"""Orchestration boundary for policy transport and robot control."""

from __future__ import annotations

import time

from pi05_ur10e.deployment.action_adapter import relative_actions_to_absolute
from pi05_ur10e.deployment.action_chunk_executor import ActionChunkExecutor
from pi05_ur10e.deployment.observation_builder import ObservationBuilder
from pi05_ur10e.deployment.policy_client import WebSocketPolicyClient
from pi05_ur10e.robot.base_robot import BaseRobot


class RolloutRunner:
    def __init__(
        self,
        robot: BaseRobot,
        builder: ObservationBuilder,
        policy: WebSocketPolicyClient,
        executor: ActionChunkExecutor,
    ):
        self.robot = robot
        self.builder = builder
        self.policy = policy
        self.executor = executor

    def run(self, *, chunks: int) -> int:
        if chunks <= 0:
            raise ValueError("chunks must be positive")
        executed = 0
        self.robot.connect()
        try:
            for _ in range(chunks):
                raw = self.robot.get_observation()
                observation = self.builder.build(raw)
                result = self.policy.infer(observation)
                received_at = time.monotonic()
                absolute = relative_actions_to_absolute(observation["observation.state"], result["actions"])
                self.executor.replace_chunk(absolute)
                executed += self.executor.execute(last_communication=received_at)
        finally:
            self.robot.stop()
            self.robot.disconnect()
            self.policy.reset()
        return executed

