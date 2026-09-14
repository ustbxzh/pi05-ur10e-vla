"""Shared robot abstraction used by collection and deployment."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class BaseRobot(Protocol):
    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def get_observation(self) -> dict[str, Any]: ...

    def command_tcp_target(self, action: np.ndarray) -> None: ...

    def move_home(self) -> None: ...

    def stop(self) -> None: ...

