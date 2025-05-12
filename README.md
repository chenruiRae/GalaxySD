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

| parameter             | description                                | example                   |
|--------------------|-------------------------------------|--------------------------|
| `pretrained_model_name_or_path` | Pretrained model name in hugging-face / downloaded local path                | `stable-diffusion-v1-5/stable-diffusion-v1-5` |
| `img_root`    | image path                              | a folder of `.jpg` files.                 |
| `caption_file`       | caption path                        | a folder of `.txt` files whose filenames are same as corresponding images.             |
| `resume` | Continue the previous training by filling this part or start a new training by set it to null                |                       |

By setting these and the rest parameters in configuration, you could start full fine-tuning.

### Get started

#### Training
```
bash ./sub_gal_train_full
```
#### Inference

