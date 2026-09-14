from pi05_ur10e.deployment.observation_builder import ObservationBuilder
from pi05_ur10e.robot.mock_ur10e_robot import MockUR10eRobot


def test_openpi_observation_keys():
    robot = MockUR10eRobot()
    robot.connect()
    built = ObservationBuilder("pick the object").build(robot.get_observation())
    assert set(built) == {
        "observation.images.base_0_rgb",
        "observation.images.left_wrist_0_rgb",
        "observation.state",
        "prompt",
    }

