# !/bin/bash
# This script is used to convert trained model to webui.

export CUDA_VISIBLE_DEVICES=1
export HF_ENDPOINT=https://hf-mirror.com
export HF_HOME=/home/mcr9196/.cache/huggingface/

cd /data_150T/home/mcr9196/HCP-Diffusion/

python -m hcpdiff.tools.lora_convert --to_webui \
    --lora_path  exps/2025-03-25-21-38-58/ckpts/unet-100000.safetensors \
    --lora_path_TE exps/2025-03-25-21-38-58/ckpts/text_encoder-100000.safetensors \
    --dump_path exps/2025-03-25-21-38-58/full-100000.safetensors \
    --auto_scale_alpha # The existing webui model does not have alpha automatic scaling and needs to be converted.
    

    