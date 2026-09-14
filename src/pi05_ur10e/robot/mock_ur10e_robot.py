"""Deterministic, hardware-free UR10e implementation for integration tests."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from pi05_ur10e.data.ur10e_schema import (
    BASE_IMAGE_KEY,
    STATE_KEY,
    WRIST_IMAGE_KEY,
    identity_state,
    validate_vector,
)


class MockUR10eRobot:
    def __init__(self, *, image_shape: tuple[int, int, int] = (64, 64, 3), home_state: np.ndarray | None = None):
        if len(image_shape) != 3 or image_shape[-1] != 3:
            raise ValueError("image_shape must be (H, W, 3)")
        self._image_shape = image_shape
        self._home_state = validate_vector(
            identity_state(position=(0.4, 0.0, 0.3), gripper=0.0) if home_state is None else home_state,
            name="home_state",
        ).copy()
        self._state = self._home_state.copy()
        self.connected = False
        self.stopped = True
        self.command_count = 0

    def connect(self) -> None:
        self.connected = True
        self.stopped = False

    def disconnect(self) -> None:
        self.stop()
        self.connected = False

    def get_observation(self) -> dict[str, Any]:
        self._ensure_connected()
        base = np.zeros(self._image_shape, dtype=np.uint8)
        wrist = np.zeros(self._image_shape, dtype=np.uint8)
        base[..., 1] = 32
        wrist[..., 2] = 32
        return {
            BASE_IMAGE_KEY: base,
            WRIST_IMAGE_KEY: wrist,
            STATE_KEY: self._state.copy(),
            "timestamp": time.monotonic(),
        }

    def command_tcp_target(self, action: np.ndarray) -> None:
        self._ensure_connected()
        self._state = validate_vector(action, name="action").copy()
        self.stopped = False
        self.command_count += 1

    def move_home(self) -> None:
        self._ensure_connected()
        self._state = self._home_state.copy()

    def stop(self) -> None:
        self.stopped = True

    @property
    def state(self) -> np.ndarray:
        return self._state.copy()

    def _ensure_connected(self) -> None:
        if not self.connected:
            raise RuntimeError("mock robot is not connected")

