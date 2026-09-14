"""Episode state machine shared by interactive and mock collection."""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol


class EpisodeWriter(Protocol):
    def add_frame(self, sample: dict[str, Any]) -> None: ...

    def save_episode(self, task: str | None = None) -> None: ...

    def discard_episode(self) -> None: ...


class EpisodeState(Enum):
    IDLE = "idle"
    RECORDING = "recording"


class EpisodeManager:
    def __init__(self, writer: EpisodeWriter, task: str):
        if not task.strip():
            raise ValueError("task must be non-empty")
        self.writer = writer
        self.task = task
        self.state = EpisodeState.IDLE
        self.frame_count = 0

    def start(self) -> None:
        if self.state is EpisodeState.RECORDING:
            raise RuntimeError("episode is already recording")
        self.state = EpisodeState.RECORDING
        self.frame_count = 0

    def record(self, frame: dict[str, Any]) -> None:
        if self.state is not EpisodeState.RECORDING:
            return
        self.writer.add_frame({**frame, "task": self.task})
        self.frame_count += 1

    def finish(self) -> int:
        if self.state is not EpisodeState.RECORDING:
            raise RuntimeError("no active episode")
        count = self.frame_count
        self.writer.save_episode(self.task)
        self.state = EpisodeState.IDLE
        self.frame_count = 0
        return count

    def discard(self) -> int:
        count = self.frame_count
        self.writer.discard_episode()
        self.state = EpisodeState.IDLE
        self.frame_count = 0
        return count

