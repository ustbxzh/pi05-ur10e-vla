"""Create a two-frame hardware-free LeRobot V3 dataset."""

from pathlib import Path
import tempfile

from pi05_ur10e.data.lerobot_writer import LeRobotWriter
from pi05_ur10e.data.ur10e_schema import ACTION_KEY
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot


robot = MockUR10eRobot(image_shape=(32, 32, 3))
robot.connect()
with tempfile.TemporaryDirectory() as directory:
    writer = LeRobotWriter.create(Path(directory), "local/mock_ur10e")
    for _ in range(2):
        observation = robot.get_observation()
        writer.add_frame({**observation, ACTION_KEY: observation["observation.state"], "task": "mock task"})
    writer.save_episode()
    writer.finalize()
    print(directory)
robot.disconnect()

