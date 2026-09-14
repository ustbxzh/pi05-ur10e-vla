#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pi05_ur10e.data.dataset_validator import validate_lerobot_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    info = validate_lerobot_dataset(args.dataset)
    print(f"valid: {info['total_episodes']} episodes, {info['total_frames']} frames")


if __name__ == "__main__":
    main()

