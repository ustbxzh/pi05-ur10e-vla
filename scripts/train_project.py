#!/usr/bin/env python3
"""Call the audited OpenPI trainer with the composed project config."""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
from pathlib import Path

from pi05_ur10e.training.openpi_profile import create_train_config


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("audited_openpi_train", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openpi-root", type=Path, required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--exp-name", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--wandb-disabled", action="store_true")
    args = parser.parse_args()
    config = dataclasses.replace(
        create_train_config(args.repo_id),
        exp_name=args.exp_name,
        resume=args.resume,
        overwrite=args.overwrite,
        wandb_enabled=not args.wandb_disabled,
    )
    _load(args.openpi_root.resolve() / "scripts" / "train.py").main(config)


if __name__ == "__main__":
    main()

