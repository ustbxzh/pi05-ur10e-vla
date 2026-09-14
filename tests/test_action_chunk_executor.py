import numpy as np
import pytest

from pi05_ur10e.data.ur10e_schema import PREDICTION_HORIZON, identity_state
from pi05_ur10e.deployment.action_chunk_executor import ActionChunkExecutor
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot
from pi05_ur10e.robot.safety_filter import SafetyFilter


def test_executes_only_execution_horizon_without_sleeping():
    robot = MockUR10eRobot()
    robot.connect()
    chunk = np.repeat(identity_state(position=(0.4, 0.0, 0.3))[None, :], PREDICTION_HORIZON, axis=0)
    executor = ActionChunkExecutor(robot, SafetyFilter(), clock=lambda: 1.0, sleeper=lambda _: None)
    executor.replace_chunk(chunk)
    assert executor.execute(last_communication=1.0) == 10
    assert robot.command_count == 10


def test_rejects_bad_chunk_shape():
    robot = MockUR10eRobot()
    executor = ActionChunkExecutor(robot, SafetyFilter())
    with pytest.raises(ValueError, match="shape"):
        executor.replace_chunk(np.zeros((20, 9), dtype=np.float32))

