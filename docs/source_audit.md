# Phase 1 Source Audit

Audit date: 2026-09-14. All checks were read-only and used `rg --files`, README/LICENSE inspection and `.git` discovery.

## Repository state

| Supplied archive root | Files from `rg --files` | Git metadata/status | License |
| --- | ---: | --- | --- |
| `aloha-gamepad-main/aloha-gamepad-main` | 13 | `.git` absent; dirty status cannot be determined | MIT |
| `openpi05-post-train-compat-lerobot-v3/openpi05-post-train-compat-lerobot-v3` | 144 | `.git` absent; dirty status cannot be determined | Apache-2.0 plus Gemma license |
| `robotwin_repo-main/robotwin_repo-main` | 22 | `.git` absent; dirty status cannot be determined | no license file found |

These are downloaded source snapshots rather than intact Git worktrees. The integration therefore treats every source file as user-owned/read-only.

## aloha-gamepad inventory and classification

- Root: `README.md`, `LICENSE`.
- Runtime scripts: `gamepad_teleop.py`, `lerobot_writer.py`, `eval_policy.py`, `run_eval.sh`, `view_dataset.py`, `sleep_arms.py`.
- Hardware launch: `launch/aloha_bringup.launch.py`.
- Documentation/media: `docs/index.html`, one PDF, two PNG diagrams.

Dependencies observed in source include ROS2/rclpy, ALOHA, Interbotix, sensor messages, NumPy, SciPy, modern_robotics, pyarrow, imageio, LeRobot and PyTorch. `gamepad_teleop.py` is tightly coupled to two follower arms, IK, mobile-base velocity and a `/mobile_base/joy` subscription at 50 Hz. `lerobot_writer.py` contains reusable LeRobot V3 layout logic but emits 14D joints and optional `action.base`. `eval_policy.py` loads a local LeRobot PI05Policy and directly controls ALOHA; that inference design was rejected for the new project.

## OpenPI inventory and classification

- Root/build/legal: README, Apache LICENSE, Gemma license, contributing guide, `pyproject.toml`, `uv.lock`, OpenPI commit marker and development config.
- Model core (`src/openpi/models`, `models_pytorch`): Pi0/Pi0.5 config/model, Gemma/PaliGemma components, SigLIP, tokenizers, LoRA and RTC guidance.
- Policy/transforms (`src/openpi/policies`, `transforms.py`): generic policy pipeline plus ALOHA/DROID/LIBERO/UR adapters. The UR adapter fixes physical dimension 10 and exact image keys.
- Training (`src/openpi/training`, `scripts/train*.py`, `compute_norm_stats.py`): data loaders, TrainConfig registry, weight loaders, optimizer, checkpoints, JAX/PyTorch loops and norm stats.
- Serving (`src/openpi/serving`, `scripts/serve_policy.py`): WebSocket server with optional RTC request envelope.
- Client (`packages/openpi-client`): synchronous msgpack WebSocket client, action chunk broker and runtime helpers.
- Examples: ALOHA sim/real, DROID, LIBERO, simple client and UR10e action adapter.

Verified UR path: LeRobot keys are repacked to `state`, `actions`, `prompt`; inputs apply `URInputs` then `AbsoluteTCPActionsToRelative`; outputs apply `UROutputs`. Model transforms inject prompt, resize to 224, tokenize π0.5 prompt with discrete state and pad physical 10D to model 32D. The audited LoRA config uses `pi05=True`, both Gemma variants with `_lora`, `pi05_base`, horizon 20 and policy metadata action_dim 10/execution horizon 10/frequency 20.

The supplied commit marker is `15a9616a00943ada6c20a0f158e3adb39df2ccac`.

## robotwin_repo inventory and classification

- `README.md`.
- Five experiment reports under DP, ACT, comparisons and pi0.5.
- Four pi0.5 documentation files: reproduction, hardware runbook, failure analysis, resume material.
- Six result files, two scripts and four media/figure assets.

Its README contains completed benchmark claims and hardware/result numbers. Because no license file was supplied, none of those contents or assets are migrated. Only the general document taxonomy informed newly written empty protocol templates.

## Non-destructive migration plan

1. Create only `pi05-ur10e-vla` and preserve all three snapshots.
2. Keep one editable OpenPI dependency; do not copy `src/openpi`, weights, lockfile, caches or examples.
3. Rewrite portable ALOHA ideas around BaseRobot and the 10D contract, with MIT attribution.
4. Provide mock-only executable defaults and a delegating real backend with explicit missing inputs.
5. Keep training/server entrypoints as reviewed wrappers; do not run them during integration.
6. Add original protocol templates with no populated results.
7. Validate only syntax/imports, mocks, schema, writer and static forbidden-reference searches.
