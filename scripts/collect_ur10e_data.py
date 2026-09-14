#!/usr/bin/env python3
"""Collect gamepad episodes. This checkout intentionally enables mock only."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pi05_ur10e.data.lerobot_writer import LeRobotWriter
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot
from pi05_ur10e.teleop.episode_manager import EpisodeManager
from pi05_ur10e.teleop.gamepad_mapping import GamepadMapper
from pi05_ur10e.teleop.ur10e_gamepad_teleop import PygameGamepadSource, UR10eGamepadTeleop


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--robot", choices=("mock", "ur10e"), default="mock")
    parser.add_argument("--max-steps", type=int)
    args = parser.parse_args()
    if args.robot != "mock":
        raise SystemExit("real UR10e collection is disabled until a laboratory backend is supplied and reviewed")
    writer = LeRobotWriter.create(args.output, args.repo_id)
    teleop = UR10eGamepadTeleop(
        MockUR10eRobot(),
        PygameGamepadSource(),
        GamepadMapper(),
        EpisodeManager(writer, args.task),
    )
    try:
        teleop.run(max_steps=args.max_steps)
    except KeyboardInterrupt:
        pass
    writer.finalize()


if __name__ == "__main__":
    main()

