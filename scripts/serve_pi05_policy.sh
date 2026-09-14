#!/usr/bin/env bash
set -euo pipefail
: "${OPENPI_ROOT:?Set OPENPI_ROOT to the audited openpi checkout}"
: "${CHECKPOINT_DIR:?Set CHECKPOINT_DIR to a local, verified checkpoint directory}"
: "${DATASET_REPO_ID:?Set DATASET_REPO_ID to the checkpoint's dataset repo id}"
PORT="${PORT:-8000}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
uv run --project "$OPENPI_ROOT" "$PROJECT_ROOT/scripts/serve_project_policy.py" \
  --port "$PORT" \
  --repo-id "$DATASET_REPO_ID" \
  --checkpoint "$CHECKPOINT_DIR"

