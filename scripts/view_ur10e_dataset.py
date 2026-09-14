#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pi05_ur10e.data.dataset_viewer import dataset_summary, format_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    print(format_summary(dataset_summary(args.dataset)))


if __name__ == "__main__":
    main()

