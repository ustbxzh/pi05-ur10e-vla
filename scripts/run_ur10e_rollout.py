#!/usr/bin/env python3
"""Offline rollout smoke test. Real hardware remains intentionally disabled."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, PREDICTION_HORIZON, rotation_matrix_to_rot6d
from pi05_ur10e.deployment.action_chunk_executor import ActionChunkExecutor
from pi05_ur10e.deployment.observation_builder import ObservationBuilder
from pi05_ur10e.deployment.policy_client import WebSocketPolicyClient
from pi05_ur10e.deployment.rollout import RolloutRunner
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot
from pi05_ur10e.robot.safety_filter import SafetyFilter


class MockTransport:
    def get_server_metadata(self):
        return {"action_dim": ACTION_DIM, "prediction_horizon": PREDICTION_HORIZON}

    def infer(self, observation, *, rtc=None):
        actions = np.zeros((PREDICTION_HORIZON, ACTION_DIM), dtype=np.float32)
        actions[:, 3:9] = rotation_matrix_to_rot6d(np.eye(3))
        actions[:, 9] = observation["observation.state"][9]
        return {"actions": actions}

    def reset(self):
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", type=int, default=1)
    parser.add_argument("--robot", choices=("mock", "ur10e"), default="mock")
    args = parser.parse_args()
    if args.robot != "mock":
        raise SystemExit("real UR10e rollout is disabled until the laboratory backend and limits are supplied")
    robot = MockUR10eRobot()
    client = WebSocketPolicyClient(transport=MockTransport())
    executor = ActionChunkExecutor(robot, SafetyFilter())
    count = RolloutRunner(robot, ObservationBuilder("mock task"), client, executor).run(chunks=args.chunks)
    print(f"mock-validated {count} action steps")


if __name__ == "__main__":
    main()

