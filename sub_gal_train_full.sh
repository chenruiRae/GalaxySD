#!/bin/bash
# This script is used to full fine-tuning the diffusion model.
# The customized config file is cfgs/train/galaxy/fine-tuning_sdss.yaml.

# set CUDA and Hugging Face
export CUDA_VISIBLE_DEVICES=1
export HF_ENDPOINT=https://hf-mirror.com

echo "Currently activated Conda environment: "
conda info --envs | grep '*'

# Run training command
accelerate launch -m hcpdiff.train_ac_single \
    --cf cfgs/train/examples/fine-tuning_galaxy.yaml
   