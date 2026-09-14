# π0.5 LoRA Post-Training

LoRA represents an update to selected dense weights as a product of two low-rank matrices. Base weights remain frozen while the much smaller low-rank factors are optimized, reducing trainable parameters and optimizer-state/gradient memory compared with full fine-tuning.

The audited `pi05_ur10e_lora_finetune` config sets both `paligemma_variant="gemma_2b_lora"` and `action_expert_variant="gemma_300m_lora"`. Thus LoRA-capable layers exist in both the VLM and Action Expert. `Pi0Config.get_freeze_filter()` selects language-model paths (including the `_1` Action Expert path) and then excludes paths matching `lora`, which means ordinary base parameters are frozen while LoRA parameters remain trainable. Non-language projections are not included in that freeze filter and follow the upstream optimizer partitioning.

The project profile preserves `pi05=True`, model action dimension 32, horizon 20, `pi05_base` checkpoint loader and `LeRobotURDataConfig`. Only project identity and dataset repo id change.

The data order is important:

```text
LeRobot V3 keys
→ RepackTransform
→ URInputs (physical 10D and image mapping)
→ AbsoluteTCPActionsToRelative
→ Normalize with this dataset's stats
→ resize/tokenize/pad-to-32
→ π0.5 LoRA training
```

Norm stats are part of the checkpoint data contract. Reusing statistics from another robot, coordinate range, gripper calibration or dataset would scale inputs/actions incorrectly even when all shapes match. Compute them from the exact collected repo before training and keep them with the checkpoint assets.

No training has been executed by this integration.

