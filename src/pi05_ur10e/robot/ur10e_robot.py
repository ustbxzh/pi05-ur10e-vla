"""Delegating boundary for a future laboratory-specific UR10e ROS2 backend."""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np

from pi05_ur10e.data.ur10e_schema import validate_vector


class HardwareIntegrationRequired(RuntimeError):
    pass


class UR10eBackend(Protocol):
    """Adapter contract to implement once real ROS2 interfaces are known."""

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def read_observation(self) -> dict[str, Any]: ...

    def send_tcp_target(self, action: np.ndarray) -> None: ...

    def move_home(self) -> None: ...

    def stop(self) -> None: ...


class UR10eRobot:
    """BaseRobot implementation that never invents ROS2 topic/controller names.

    TODO(hardware): supply a tested ``UR10eBackend`` using the laboratory's
    controller, state source, camera streams, gripper driver, frames and QoS.
    """

    def __init__(self, backend: UR10eBackend | None = None):
        self._backend = backend

    def _require_backend(self) -> UR10eBackend:
        if self._backend is None:
            raise HardwareIntegrationRequired(
                "real UR10e backend is not configured; provide laboratory ROS2 interfaces explicitly"
            )
        return self._backend

    def connect(self) -> None:
        self._require_backend().connect()

    def disconnect(self) -> None:
        self._require_backend().disconnect()

    def get_observation(self) -> dict[str, Any]:
        return self._require_backend().read_observation()

    def command_tcp_target(self, action: np.ndarray) -> None:
        self._require_backend().send_tcp_target(validate_vector(action, name="action"))

    def move_home(self) -> None:
        self._require_backend().move_home()

    def stop(self) -> None:
        self._require_backend().stop()

