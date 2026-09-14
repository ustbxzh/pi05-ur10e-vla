"""Configurable last-mile action filter.

Defaults are examples for offline tests only and are not certified UR10e limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

from pi05_ur10e.data.ur10e_schema import (
    rot6d_to_rotation_matrix,
    rotation_matrix_to_rot6d,
    validate_vector,
)


class SafetyViolation(RuntimeError):
    pass


@dataclass(frozen=True)
class SafetyLimits:
    workspace_min: np.ndarray = field(default_factory=lambda: np.array([0.1, -0.6, 0.0], dtype=np.float32))
    workspace_max: np.ndarray = field(default_factory=lambda: np.array([0.9, 0.6, 1.0], dtype=np.float32))
    max_translation_step_m: float = 0.02
    max_rotation_step_rad: float = 0.15
    communication_timeout_s: float = 1.0

    def __post_init__(self) -> None:
        low = np.asarray(self.workspace_min, dtype=np.float32)
        high = np.asarray(self.workspace_max, dtype=np.float32)
        if low.shape != (3,) or high.shape != (3,) or np.any(low >= high):
            raise ValueError("workspace bounds must be ordered 3D vectors")
        if min(self.max_translation_step_m, self.max_rotation_step_rad, self.communication_timeout_s) <= 0:
            raise ValueError("step and timeout limits must be positive")


class SafetyFilter:
    def __init__(self, limits: SafetyLimits | None = None):
        self.limits = limits or SafetyLimits()

    def filter(
        self,
        current: np.ndarray,
        target: np.ndarray,
        *,
        now: float | None = None,
        last_communication: float | None = None,
    ) -> np.ndarray:
        current = validate_vector(current, name="current_state").astype(np.float64)
        target = validate_vector(target, name="target_action").astype(np.float64)
        if now is not None and last_communication is not None:
            age = now - last_communication
            if age < 0 or age > self.limits.communication_timeout_s:
                raise SafetyViolation(f"policy communication age {age:.3f}s exceeds timeout")

        delta = target[:3] - current[:3]
        distance = float(np.linalg.norm(delta))
        if distance > self.limits.max_translation_step_m:
            delta *= self.limits.max_translation_step_m / distance
        output = target.copy()
        output[:3] = np.clip(
            current[:3] + delta,
            np.asarray(self.limits.workspace_min),
            np.asarray(self.limits.workspace_max),
        )

        current_rotation = rot6d_to_rotation_matrix(current[3:9])
        target_rotation = rot6d_to_rotation_matrix(target[3:9])
        relative = current_rotation.T @ target_rotation
        angle = math.acos(float(np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)))
        if angle > self.limits.max_rotation_step_rad:
            axis = np.array(
                [relative[2, 1] - relative[1, 2], relative[0, 2] - relative[2, 0], relative[1, 0] - relative[0, 1]]
            )
            axis_norm = float(np.linalg.norm(axis))
            if axis_norm < 1e-8:
                raise SafetyViolation("cannot safely limit a near-pi rotation step")
            axis /= axis_norm
            relative = _axis_angle(axis, self.limits.max_rotation_step_rad)
            output[3:9] = rotation_matrix_to_rot6d(current_rotation @ relative)
        output[9] = np.clip(output[9], 0.0, 1.0)
        return output.astype(np.float32)


def _axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = axis
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + math.sin(angle) * skew + (1.0 - math.cos(angle)) * (skew @ skew)

