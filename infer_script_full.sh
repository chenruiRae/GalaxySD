#!/bin/bash
# This script is used to generate images using the trained model with different prompts.

export CUDA_VISIBLE_DEVICES=1
export HF_ENDPOINT=https://hf-mirror.com 

# model name and steps
name="2025-05-11-22-14-55"
model_steps=10000

# define prompt_dict
prompt_dict=(
    
    "cigar 'sdss, smooth, cigar shaped galaxy'"
    "in_between 'sdss, smooth, in-between round galaxy'"
    "compelete_round 'sdss, smooth, completely round galaxy'"
    "spiral_2_arm 'sdss, spiral galaxy, obvious bulge prominence, tightly wound spiral arms, 2 spiral arms'"
    # "edge_on 'sdss, edge-on galaxy, with rounded edge-on bulge'"
    # "merger_in-between 'sdss, smooth, in-between round galaxy, merger'"
    # "merger_spiral 'sdss, spiral galaxy, just noticeable bulge prominence, tightly wound spiral arms, 2 spiral arms, a merger'"
    # "dust_lane 'sdss, elliptical galaxy, dust lane'"
    # "ring 'sdss, ring galaxy'"

    # "hst_in_between 'hubble, smooth, in-between round galaxy'"
    # "hst_compelete_round 'hubble, smooth, something odd, completely round galaxy'"
    # "hst_spiral 'hubble, bar-shaped structure in the center of galaxy, spiral arms pattern, obvious bulge prominence'"

    # "candels_smooth 'candels, smooth, completely round'"
    # "candels_merger 'candels, smooth, in-between round, merging galaxies'"
    # "candels_spiral 'candels, features or disk-shaped, spiral arms pattern, tightly wound spiral arms, obvious bulge prominence'"
    # "candels_clump 'candels, features or disk-shaped, mostly clumpy appearance, there are five or more clumps, the clumps appear in cluster or irregular, no single brightest clump, clumps are not symmetrical, clumps are embedded'"

    # ... add more prompt key-value pairs
)

# traverse prompt_dict
for prompt_pair in "${prompt_dict[@]}"; do
    # split key and value
    IFS=' ' read -r prompt_name prompt <<<"$prompt_pair"

    command="python -m hcpdiff.visualizer \
        --cfg cfgs/infer/text2img_galaxy_full.yaml \
        exp_dir=exps/${name} \
        model_steps=${model_steps} \
        prompt=${prompt} \
        N_repeats=1 \
        output_dir=output/${name}/${prompt_name}"

    echo "Executing: $command"
    eval "$command"
done

# # optional: create a summary of the generated images by different prompts
# python create_summary.py -output_dir "output/${name}" -model_steps ${model_steps}
