import numpy as np

from pi05_ur10e.data.ur10e_schema import identity_state
from pi05_ur10e.teleop.gamepad_mapping import GamepadMapper, GamepadMappingConfig


def test_deadzone_produces_no_translation():
    mapper = GamepadMapper(GamepadMappingConfig(deadzone=0.2))
    state = identity_state(position=(0.4, 0.0, 0.3))
    target = mapper.map_axes(state, left_x=0.1, left_y=0.1, right_y=0.1)
    np.testing.assert_allclose(target, state)


def test_translation_mapping_is_single_ur10e_10d():
    mapper = GamepadMapper(GamepadMappingConfig(control_frequency_hz=20), speed_scale=1.0)
    state = identity_state(position=(0.4, 0.0, 0.3))
    target = mapper.map_axes(state, left_y=-1.0)
    assert target.shape == (10,)
    assert target[0] > state[0]

