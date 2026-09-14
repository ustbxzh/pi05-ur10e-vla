import numpy as np

from pi05_ur10e.data.dataset_validator import validate_lerobot_dataset, validate_records
from pi05_ur10e.data.lerobot_writer import LeRobotWriter
from pi05_ur10e.data.ur10e_schema import ACTION_KEY, identity_state
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot


def test_records_validate_timestamps_and_episode_boundaries():
    robot = MockUR10eRobot(image_shape=(32, 32, 3))
    robot.connect()
    observation = robot.get_observation()
    records = [
        {**observation, ACTION_KEY: identity_state(), "task": "test", "episode_index": 0, "frame_index": i, "timestamp": i / 20}
        for i in range(2)
    ]
    assert validate_records(records) == 2


def test_minimal_lerobot_v3_write(tmp_path):
    robot = MockUR10eRobot(image_shape=(32, 32, 3))
    robot.connect()
    writer = LeRobotWriter.create(tmp_path, "local/test")
    for _ in range(2):
        observation = robot.get_observation()
        writer.add_frame({**observation, ACTION_KEY: observation["observation.state"], "task": "test"})
    writer.save_episode()
    writer.finalize()
    info = validate_lerobot_dataset(tmp_path)
    assert info["total_frames"] == 2
    assert info["features"]["action"]["shape"] == [10]
    assert (tmp_path / "data" / "chunk-000" / "file-000.parquet").is_file()
    assert (tmp_path / "videos" / "observation.images.base_0_rgb" / "chunk-000" / "file-000.mp4").is_file()

