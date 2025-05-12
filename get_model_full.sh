# !/bin/bash
# This script is used to convert trained model (TE and Unet) to full model.

export CUDA_VISIBLE_DEVICES=1
export HF_ENDPOINT=https://hf-mirror.com

# model name and steps
name="2025-03-25-21-38-58"
model_steps=100000

python -m hcpdiff.visualizer \
        --cfg cfgs/train/galaxy/save_model.yaml \
        exp_dir=exps/${name} \
        model_steps=${model_steps}