"""Camera boundary; concrete ROS2 topics must be supplied by the laboratory."""

from typing import Protocol

import numpy as np


class CameraInterface(Protocol):
    def connect(self) -> None: ...

    def read_rgb(self) -> np.ndarray: ...

    def disconnect(self) -> None: ...

