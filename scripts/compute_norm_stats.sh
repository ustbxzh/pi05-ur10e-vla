#!/usr/bin/env bash
set -euo pipefail
: "${OPENPI_ROOT:?Set OPENPI_ROOT to the audited openpi checkout}"
: "${DATASET_REPO_ID:?Set DATASET_REPO_ID to the collected LeRobot V3 repo id}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
uv run --project "$OPENPI_ROOT" "$PROJECT_ROOT/scripts/compute_project_norm_stats.py" \
  --repo-id "$DATASET_REPO_ID" \
  --openpi-root "$OPENPI_ROOT"
