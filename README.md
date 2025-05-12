# GalaxySD

### Git and create environment

```
git clone https://github.com/chenruiRae/GalaxySD.git
cd GalaxySD
```

```
conda create -n galaxysd
conda activate galaxysd
pip install -r requirements.txt
```
Now you have set up the workspace and could fine-tune a GalaxySD model.

### Customize configurations

For example, full fine-tuning training configurations are in `GalaxySD/cfgs/train/examples/fine-tuning_galaxy.yaml`. You could customize it before using. The parameters that must be modified to ensure the pipeline run well and corresponding descriptions in `fine-tuning_galaxy.yaml` are in the following table.

| Training Parameter             | Description                                | Example                   |
|--------------------|-------------------------------------|--------------------------|
| `pretrained_model_name_or_path` | Pretrained model name in hugging-face / downloaded local path                | `stable-diffusion-v1-5/stable-diffusion-v1-5` |
| `img_root`    | image path                              | a folder of `.jpg` files.                 |
| `caption_file`       | caption path                        | a folder of `.txt` files whose filenames are same as corresponding images.             |
| `resume` | Continue the previous training by filling this part or start a new training by set it to null                |                       |

By setting these and the rest parameters in configuration, you could start full fine-tuning.

Before inference, you must modify the inference configurations in `GalaxySD/cfgs/infer/text2img_galaxy_full.yaml`.

| Inference Parameter             | Description                                | Example                   |
|--------------------|-------------------------------------|--------------------------|
| `pretrained_model` | Pretrained model name in hugging-face / downloaded local path                | `stable-diffusion-v1-5/stable-diffusion-v1-5` |
| `condition`    | Control the generation                              | `type: i2i`<br>`image: 'galaxy_cond.jpg'`            |

### Get started

#### Training
```
bash ./sub_gal_train_full.sh
```
#### Inference
Fill model name and steps and give prompts in `infer_script_full.sh`.
```
bash ./infer_script_full.sh
```
If you wanna view a summary of generation, 

