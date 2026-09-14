# π0.5 Architecture in the Audited OpenPI Checkout

This document describes the supplied OpenPI code, especially `models/pi0.py`, `models/pi0_config.py`, `training/config.py` and `policies/ur_policy.py`.

## Prefix

`URInputs` maps the two dataset images into model names `base_0_rgb` and `left_wrist_0_rgb`; it creates a zero `right_wrist_0_rgb` with a false image mask. The model transform resizes to 224×224 and tokenizes the prompt. For π0.5, `discrete_state_input` defaults true, so state is encoded through prompt tokenization rather than the continuous state token used by π0. `Pi0.embed_prefix` sends each image through the SigLIP image encoder and the text/discrete-state tokens through the PaliGemma language embedding, concatenating them with full prefix attention.

## Suffix and model roles

The action suffix contains one token per noisy action step. `action_in_proj` maps 32D actions into the Action Expert width. In π0.5, timestep embeddings pass through a two-layer MLP and condition the Action Expert through adaptive RMS normalization (`adarms`); there is no separate continuous state token in `embed_suffix`.

PaliGemma supplies visual/language contextual representations and the shared transformer interface. The smaller Action Expert processes action/timestep suffix tokens and `action_out_proj` maps its output back to action velocity. Images/language do not attend to future action tokens; the suffix attends to the prefix and follows the configured action-token attention pattern.

## Flow matching

Training samples Gaussian noise and a beta-distributed time, constructs `x_t = t*noise + (1-t)*actions`, and uses target velocity `u_t = noise - actions`. The network predicts velocity `v_t`; loss is mean squared error over action dimensions. Sampling starts from noise and integrates the predicted vector field over denoising steps to form a 20-step chunk.

## Why physical 10D becomes model 32D

The UR contract is 10D, but audited `Pi0Config` uses `action_dim=32`. `PadStatesAndActions` zero-pads state/action after UR conversion and before the model. `UROutputs` returns only the leading 10 physical dimensions. Padding preserves the base model tensor architecture and checkpoint compatibility; it is not an extra set of robot controls.

