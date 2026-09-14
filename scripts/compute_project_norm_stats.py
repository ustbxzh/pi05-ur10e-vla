#!/usr/bin/env python3
"""Run upstream norm-stat computation with the external project profile."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from pi05_ur10e.training.openpi_profile import create_train_config


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("audited_openpi_compute_norm_stats", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openpi-root", type=Path, required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args()
    config = create_train_config(args.repo_id)
    from openpi.training import config as openpi_config

    openpi_config._CONFIGS_DICT[config.name] = config
    upstream = _load(args.openpi_root.resolve() / "scripts" / "compute_norm_stats.py")
    upstream.main(config.name, args.max_frames)


if __name__ == "__main__":
    main()

