# 🌌 GalaxySD
We fine-tuned sd-1.5 specialized for galaxy image generation by galaxy images with annoted morphological description based on [GZ2](https://arxiv.org/abs/1308.3496v2). The galaxy morphological description dataset in natural language insteal of vote fractions will release soon. 

Our project [HOMEPAGE](https://galaxysd-webpage.streamlit.app/).

### 🧠 Arcitecture

Schematic diagram of our model and downstream tasks in our paper.

![schema](schema.png)

### 🛠️ Git and create environment

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

### ⚙️ Customize configurations

For example, full fine-tuning training configurations are in `GalaxySD/cfgs/train/examples/fine-tuning_galaxy.yaml`. You could customize it before using. The parameters that must be modified to ensure the pipeline run well and corresponding descriptions in `fine-tuning_galaxy.yaml` are in the following table. The fine-tuning tool we used is [HCP-Diffusion](https://github.com/IrisRainbowNeko/HCP-Diffusion).

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

### 🚀 Get started

#### Training
```
bash ./sub_gal_train_full.sh
```
#### Inference
Fill model name and steps and give prompts in `infer_script_full.sh`. You could use the model weights in 🤗[HF](https://huggingface.co/CosmosDream/GalaxySD).
```
bash ./infer_script_full.sh
```
If you wanna view a summary of generation, uncomment the last line of `infer_script_full.sh` and keep the prompts in `create_summary.py` consistent with those in inference script.

### 📄 Citation
```
@misc{ma2025aidreamunseengalaxies,
      title={Can AI Dream of Unseen Galaxies? Conditional Diffusion Model for Galaxy Morphology Augmentation}, 
      author={Chenrui Ma and Zechang Sun and Tao Jing and Zheng Cai and Yuan-Sen Ting and Song Huang and Mingyu Li},
      year={2025},
      eprint={2506.16233},
      archivePrefix={arXiv},
      primaryClass={astro-ph.GA},
      url={https://arxiv.org/abs/2506.16233}, 
}
```


### 🔗 Project Resources
- 🏠 [Homepage](https://galaxysd-webpage.streamlit.app/)
- 🤗 [GalaxySD Model Weights](https://huggingface.co/CosmosDream/GalaxySD)
- 🛠️ [Trained Galaxy Embedding Tool](https://huggingface.co/CosmosDream/GalaxyEmb)
- 🗂️ [Training Dataset](https://zenodo.org/records/15669465)
- 📊 [A Contributed Catalog](https://zenodo.org/records/15636756)



