"""Hardware-neutral gamepad mapping extracted from the ALOHA control flow."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from pi05_ur10e.data.ur10e_schema import (
    rot6d_to_rotation_matrix,
    rotation_matrix_to_rot6d,
    validate_vector,
)


@dataclass(frozen=True)
class GamepadMappingConfig:
    deadzone: float = 0.15
    linear_speed_m_s: float = 0.10
    angular_speed_rad_s: float = 0.50
    control_frequency_hz: int = 20
    speed_min: float = 0.1
    speed_max: float = 1.0
    speed_step: float = 0.1


class GamepadMapper:
    """Map normalized stick axes to a single UR10e absolute TCP target."""

    def __init__(self, config: GamepadMappingConfig | None = None, *, speed_scale: float = 0.5):
        self.config = config or GamepadMappingConfig()
        self.speed_scale = float(np.clip(speed_scale, self.config.speed_min, self.config.speed_max))

    def adjust_speed(self, direction: int) -> float:
        self.speed_scale = float(
            np.clip(
                self.speed_scale + int(np.sign(direction)) * self.config.speed_step,
                self.config.speed_min,
                self.config.speed_max,
            )
        )
        return self.speed_scale

    def map_axes(
        self,
        state: np.ndarray,
        *,
        left_x: float = 0.0,
        left_y: float = 0.0,
        right_x: float = 0.0,
        right_y: float = 0.0,
        orientation_modifier: bool = False,
        gripper: float | None = None,
    ) -> np.ndarray:
        state = validate_vector(state, name="state")
        axes = np.array([left_x, left_y, right_x, right_y], dtype=np.float64)
        axes[np.abs(axes) < self.config.deadzone] = 0.0
        left_x, left_y, right_x, right_y = axes
        dt = 1.0 / self.config.control_frequency_hz
        target = state.astype(np.float64, copy=True)
        if orientation_modifier:
            rotation_vector = np.array([-right_y, left_y, left_x])
            angle = float(np.linalg.norm(rotation_vector)) * self.config.angular_speed_rad_s * self.speed_scale * dt
            if angle > 0:
                axis = rotation_vector / np.linalg.norm(rotation_vector)
                target[3:9] = rotation_matrix_to_rot6d(
                    rot6d_to_rotation_matrix(state[3:9]) @ _axis_angle(axis, angle)
                )
        else:
            target[:3] += (
                np.array([-left_y, left_x, -right_y]) * self.config.linear_speed_m_s * self.speed_scale * dt
            )
            roll = right_x * self.config.angular_speed_rad_s * self.speed_scale * dt
            if abs(roll) > 0:
                target[3:9] = rotation_matrix_to_rot6d(
                    rot6d_to_rotation_matrix(state[3:9]) @ _axis_angle(np.array([1.0, 0.0, 0.0]), roll)
                )
        if gripper is not None:
            target[9] = np.clip(gripper, 0.0, 1.0)
        return target.astype(np.float32)


def _axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = axis
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + math.sin(angle) * skew + (1.0 - math.cos(angle)) * (skew @ skew)
