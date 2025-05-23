"""
cfg_net_tools.py
====================
    :Name:        creat model and plugin from config
    :Author:      Dong Ziyi
    :Affiliation: HCP Lab, SYSU
    :Created:     10/03/2023
    :Licence:     Apache-2.0
"""
import warnings
from typing import Dict, List, Tuple, Union, Any

import re
import torch
from torch import nn

from .utils import net_path_join
from hcpdiff.models import LoraBlock, LoraGroup, lora_layer_map
from hcpdiff.models.plugin import SinglePluginBlock, MultiPluginBlock, PluginBlock, PluginGroup, PatchPluginBlock
from hcpdiff.ckpt_manager import auto_manager
from .net_utils import split_module_name
from hcpdiff.tools.convert_old_lora import convert_state

def get_class_match_layer(class_name, block:nn.Module):
    if type(block).__name__==class_name:
        return ['']
    else:
        return ['.'+name for name, layer in block.named_modules() if type(layer).__name__==class_name]

def get_match_layers(layers, all_layers, return_metas=False) -> Union[List[str], List[Dict[str, Any]]]:
    res=[]
    for name in layers:
        metas = name.split(':')

        use_re = False
        pre_hook = False
        cls_filter = None
        for meta in metas[:-1]:
            if meta=='re':
                use_re=True
            elif meta=='pre_hook':
                pre_hook=True
            elif meta.startswith('cls('):
                cls_filter=meta[4:-1]

        name = metas[-1]
        if use_re:
            pattern = re.compile(name)
            match_layers = filter(lambda x: pattern.match(x) != None, all_layers.keys())
        else:
            match_layers = [name]

        if cls_filter is not None:
            match_layers_new = []
            for layer in match_layers:
                match_layers_new.extend([layer + x for x in get_class_match_layer(name[1], all_layers[layer])])
            match_layers = match_layers_new

        for layer in match_layers:
            if return_metas:
                res.append({'layer': layer, 'pre_hook': pre_hook})
            else:
                res.append(layer)

    # Remove duplicates and keep the original order
    if return_metas:
        layer_set=set()
        res_unique = []
        for item in res:
            if item['layer'] not in layer_set:
                layer_set.add(item['layer'])
                res_unique.append(item)
        return res_unique
    else:
        return sorted(set(res), key=res.index)

def get_lora_rank_and_cls(lora_state):
    if 'layer.lora_down.weight' in lora_state: # old format
        warnings.warn("The old lora format is deprecated.", DeprecationWarning)
        rank = lora_state['layer.lora_down.weight'].shape[0]
        lora_layer_cls = lora_layer_map['lora']
        return lora_layer_cls, rank, True
    elif 'layer.W_down' in lora_state:
        rank = lora_state['layer.W_down'].shape[0]
        lora_layer_cls = lora_layer_map['lora']
        return lora_layer_cls, rank, False
    else:
        raise ValueError('Unknown lora format.')

def make_hcpdiff(model, cfg_model, cfg_lora, default_lr=1e-5) -> Tuple[List[Dict], Union[LoraGroup, Tuple[LoraGroup, LoraGroup]]]:
    named_modules = {k:v for k,v in model.named_modules()}

    train_params=[]
    all_lora_blocks={}
    all_lora_blocks_neg={}

    if cfg_model is not None:
        for item in cfg_model:
            params_group = []
            for layer_name in get_match_layers(item.layers, named_modules):
                layer = named_modules[layer_name]
                layer.requires_grad_(True)
                layer.train()
                params_group.extend(list(LoraBlock.extract_param_without_lora(layer).values()))
            train_params.append({'params':list(set(params_group)), 'lr':getattr(item, 'lr', default_lr)})

    if cfg_lora is not None:
        for lora_id, item in enumerate(cfg_lora):
            params_group = []
            for layer_name in get_match_layers(item.layers, named_modules):
                parent_name, host_name = split_module_name(layer_name)
                layer = named_modules[layer_name]
                arg_dict = {k:v for k,v in item.items() if k!='layers'}
                lora_block_dict = lora_layer_map[arg_dict.get('type', 'lora')].wrap_model(lora_id, layer, parent_block=named_modules[parent_name], host_name=host_name, **arg_dict)

                for k,v in lora_block_dict.items():
                    block_path = net_path_join(layer_name, k)
                    all_lora_blocks[block_path] = v
                    v.requires_grad_(True)
                    v.train()
                    params_group.extend(v.parameters())

            train_params.append({'params': params_group, 'lr':getattr(item, 'lr', default_lr)})

    if len(all_lora_blocks_neg)>0:
        return train_params, (LoraGroup(all_lora_blocks), LoraGroup(all_lora_blocks_neg))
    else:
        return train_params, LoraGroup(all_lora_blocks)

def make_plugin(model, cfg_plugin, default_lr=1e-5) -> Tuple[List, Dict[str, PluginGroup]]:
    train_params=[]
    all_plugin_group={}

    if cfg_plugin is None:
        return train_params, all_plugin_group

    named_modules = {k: v for k, v in model.named_modules()}

    # builder: functools.partial
    for plugin_name, builder in cfg_plugin.items():
        all_plugin_blocks={}

        lr = builder.keywords.pop('lr') if 'lr' in builder.keywords else default_lr
        train_plugin = builder.keywords.pop('train') if 'train' in builder.keywords else True
        plugin_class = getattr(builder.func, '__self__', builder.func) # support static or class method

        params_group = []
        if issubclass(plugin_class, MultiPluginBlock):
            from_layers = [{**item, 'layer':named_modules[item['layer']]} for item in get_match_layers(builder.keywords.pop('from_layers'), named_modules, return_metas=True)]
            to_layers = [{**item, 'layer':named_modules[item['layer']]} for item in get_match_layers(builder.keywords.pop('to_layers'), named_modules, return_metas=True)]

            layer = builder(name=plugin_name, host_model=model, from_layers=from_layers, to_layers=to_layers)
            if train_plugin:
                layer.train()
                params = layer.get_trainable_parameters()
                for p in params:
                    p.requires_grad_(True)
                    params_group.append(p)
            else:
                layer.requires_grad_(False)
                layer.eval()
            all_plugin_blocks[''] = layer
        elif issubclass(plugin_class, SinglePluginBlock):
            layers_name = builder.keywords.pop('layers')
            for layer_name in get_match_layers(layers_name, named_modules):
                blocks = builder(name=plugin_name, host_model=model, host=named_modules[layer_name])
                if not isinstance(blocks, dict):
                    blocks={'':blocks}

                for k,v in blocks.items():
                    all_plugin_blocks[net_path_join(layer_name, k)] = v
                    if train_plugin:
                        v.train()
                        params = v.get_trainable_parameters()
                        for p in params:
                            p.requires_grad_(True)
                            params_group.append(p)
                    else:
                        v.requires_grad_(False)
                        v.eval()
        elif issubclass(plugin_class, PluginBlock):
            from_layer = get_match_layers(builder.keywords.pop('from_layer'), named_modules, return_metas=True)
            to_layer = get_match_layers(builder.keywords.pop('to_layer'), named_modules, return_metas=True)

            for from_layer_meta, to_layer_meta in zip(from_layer, to_layer):
                from_layer_name=from_layer_meta['layer']
                from_layer_meta['layer']=named_modules[from_layer_name]
                to_layer_meta['layer']=named_modules[to_layer_meta['layer']]
                layer = builder(name=plugin_name, host_model=model, from_layer=from_layer_meta, to_layer=to_layer_meta)
                if train_plugin:
                    layer.train()
                    params = layer.get_trainable_parameters()
                    for p in params:
                        p.requires_grad_(True)
                        params_group.append(p)
                else:
                    layer.requires_grad_(False)
                    layer.eval()
                all_plugin_blocks[from_layer_name] = layer
        elif issubclass(plugin_class, PatchPluginBlock):
            layers_name = builder.keywords.pop('layers')
            for layer_name in get_match_layers(layers_name, named_modules):
                parent_name, host_name = split_module_name(layer_name)
                layers = builder(name=plugin_name, host_model=model, host=named_modules[layer_name],
                                parent_block=named_modules[parent_name], host_name=host_name)
                if not isinstance(layers, dict):
                    layers={'':layers}

                for k,v in layers.items():
                    all_plugin_blocks[net_path_join(layer_name, k)] = v
                    if train_plugin:
                        v.train()
                        params = v.get_trainable_parameters()
                        for p in params:
                            p.requires_grad_(True)
                            params_group.append(p)
                    else:
                        v.requires_grad_(False)
                        v.eval()
        else:
            raise NotImplementedError(f'Unknown plugin {plugin_class}')
        if train_plugin:
            train_params.append({'params':params_group, 'lr':lr})
        all_plugin_group[plugin_name] = PluginGroup(all_plugin_blocks)
    return train_params, all_plugin_group

class HCPModelLoader:
    def __init__(self, host):
        self.host = host
        self.named_modules = {k:v for k, v in host.named_modules()}
        self.named_params = {k:v for k, v in host.named_parameters()}

    @torch.no_grad()
    def load_part(self, cfg, base_model_alpha=0.0, load_ema=False):
        if cfg is None:
            return
        for item in cfg:
            # print(f"item:{item}")

            # print(f"item path:{item.path}") # item path:None/ckpts/unet-1000.safetensors

            part_state = auto_manager(item.path).load_ckpt(item.path, map_location='cpu')['base_ema' if load_ema else 'base']
            layers = item.get('layers', 'all')
            if layers == 'all':
                for k, v in part_state.items():
                    self.named_params[k].data = base_model_alpha * self.named_params[k].data + item.alpha * v
            else:
                match_blocks = get_match_layers(layers, self.named_modules)
                state_add = {k:v for blk in match_blocks for k,v in part_state.items() if k.startswith(blk)}
                for k, v in state_add.items():
                    self.named_params[k].data = base_model_alpha * self.named_params[k].data + item.alpha * v

    @torch.no_grad()
    def load_lora(self, cfg, base_model_alpha=1.0, load_ema=False):
        if cfg is None:
            return

        all_lora_blocks = {}
        for lora_id, item in enumerate(cfg):
            lora_state = auto_manager(item.path).load_ckpt(item.path, map_location='cpu')['lora_ema' if load_ema else 'lora']
            lora_block_state = {}
            # get all layers in the lora_state
            for name, p in lora_state.items():
                # lora_block. is the old format
                prefix, block_name = name.split('.___.' if name.rfind('lora_block.')==-1 else '.lora_block.', 1)
                if prefix not in lora_block_state:
                    lora_block_state[prefix] = {}
                lora_block_state[prefix][block_name] = p
            # get selected layers
            layers = item.get('layers', 'all')
            if layers != 'all':
                match_blocks = get_match_layers(layers, self.named_modules)
                lora_state_new = {}
                for k, v in lora_block_state.items():
                    for mk in match_blocks:
                        if k.startswith(mk):
                            lora_state_new[k]=v
                            break
                lora_block_state = lora_state_new
            # add lora to host and load weights
            for layer_name, lora_state in lora_block_state.items():
                parent_name, host_name = split_module_name(layer_name)
                lora_layer_cls, rank, old_format = get_lora_rank_and_cls(lora_state)
                if 'alpha' in lora_state:
                    del lora_state['alpha']

                if old_format:
                    lora_state = convert_state(lora_state)

                lora_block = lora_layer_cls.wrap_layer(lora_id, self.named_modules[layer_name], rank=rank, dropout=getattr(item, 'dropout', 0.0),
                                                        alpha=getattr(item, 'alpha', 1.0), bias='layer.bias' in lora_state, alpha_auto_scale=getattr(item, 'alpha_auto_scale', True),
                                                        parent_block=self.named_modules[parent_name], host_name=host_name)
                all_lora_blocks[f'{layer_name}.{lora_block.name}'] = lora_block
                lora_block.load_state_dict(lora_state, strict=False)
                lora_block.to(self.host.device)
        return LoraGroup(all_lora_blocks)

    @torch.no_grad()
    def load_plugin(self, cfg, load_ema=False):
        if cfg is None:
            return

        for name, item in cfg.items():
            plugin_state = auto_manager(item.path).load_ckpt(item.path, map_location='cpu')['plugin_ema' if load_ema else 'plugin']
            layers = item.get('layers', 'all')
            if layers != 'all':
                match_blocks = get_match_layers(layers, self.named_modules)
                plugin_state = {k:v for blk in match_blocks for k, v in plugin_state.items() if k.startswith(blk)}
            plugin_key_set = set([k.split('___', 1)[0]+name for k in plugin_state.keys()])
            plugin_state = {k.replace('___', name):v for k, v in plugin_state.items()}  # replace placeholder to target plugin name
            self.host.load_state_dict(plugin_state, strict=False)
            if 'layers' in item:
                del item.layers
            del item.path
            if hasattr(self.host, name):  # MultiPluginBlock
                getattr(self.host, name).set_hyper_params(**item)
            else:
                for plugin_key in plugin_key_set:
                    self.named_modules[plugin_key].set_hyper_params(**item)

    def load_all(self, cfg_merge, load_ema=False):
        self.load_part(cfg_merge.get('part', []), base_model_alpha=cfg_merge.get('base_model_alpha', 0.0), load_ema=load_ema)
        lora_group = self.load_lora(cfg_merge.get('lora', []), base_model_alpha=cfg_merge.get('base_model_alpha', 1.0), load_ema=load_ema)
        self.load_plugin(cfg_merge.get('plugin', {}), load_ema=load_ema)
        return lora_group