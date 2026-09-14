"""Normalized gripper boundary independent of a vendor controller."""

from typing import Protocol


class GripperInterface(Protocol):
    def read_normalized(self) -> float: ...

    def command_normalized(self, value: float) -> None: ...

    def stop(self) -> None: ...

