"""Convert upstream relative TCP chunks back to absolute base-frame targets."""

from __future__ import annotations

import numpy as np

from pi05_ur10e.data.ur10e_schema import (
    ACTION_DIM,
    rot6d_to_rotation_matrix,
    rotation_matrix_to_rot6d,
    validate_vector,
)


def relative_actions_to_absolute(state: np.ndarray, actions: np.ndarray) -> np.ndarray:
    state = validate_vector(state, name="state").astype(np.float64)
    action_array = np.asarray(actions)
    if action_array.ndim != 2 or action_array.shape[1] != ACTION_DIM or not np.all(np.isfinite(action_array)):
        raise ValueError(f"relative actions must have shape (steps, {ACTION_DIM}) and finite values")
    current_position = state[:3]
    current_rotation = rot6d_to_rotation_matrix(state[3:9])
    absolute = action_array.astype(np.float64, copy=True)
    for index, relative in enumerate(action_array):
        relative_rotation = rot6d_to_rotation_matrix(relative[3:9])
        absolute[index, :3] = current_position + current_rotation @ relative[:3]
        absolute[index, 3:9] = rotation_matrix_to_rot6d(current_rotation @ relative_rotation)
        absolute[index, 9] = relative[9]
    return absolute.astype(np.float32)

