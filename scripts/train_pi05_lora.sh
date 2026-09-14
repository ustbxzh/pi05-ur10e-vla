#!/usr/bin/env bash
set -euo pipefail
: "${OPENPI_ROOT:?Set OPENPI_ROOT to the audited openpi checkout}"
: "${DATASET_REPO_ID:?Set DATASET_REPO_ID to the collected LeRobot V3 repo id}"
: "${EXP_NAME:?Set EXP_NAME to a traceable experiment name}"
: "${CONFIRM_TRAINING:?Set CONFIRM_TRAINING=1 after reviewing dataset and norm stats}"
[[ "$CONFIRM_TRAINING" == "1" ]] || { echo "Training confirmation missing" >&2; exit 2; }
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The wrapper builds pi05_ur10e_gamepad_lora from the audited upstream profile.
PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
uv run --project "$OPENPI_ROOT" "$PROJECT_ROOT/scripts/train_project.py" \
  --openpi-root "$OPENPI_ROOT" \
  --repo-id "$DATASET_REPO_ID" \
  --exp-name "$EXP_NAME" \
  "$@"
