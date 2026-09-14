"""Interruptible, replaceable action-chunk execution at a fixed frequency."""

from __future__ import annotations

import threading
import time
from typing import Callable

import numpy as np

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, CONTROL_FREQUENCY_HZ, EXECUTION_HORIZON
from pi05_ur10e.robot.base_robot import BaseRobot
from pi05_ur10e.robot.safety_filter import SafetyFilter


class ActionChunkExecutor:
    def __init__(
        self,
        robot: BaseRobot,
        safety_filter: SafetyFilter,
        *,
        execution_horizon: int = EXECUTION_HORIZON,
        control_frequency_hz: int = CONTROL_FREQUENCY_HZ,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        if execution_horizon <= 0 or control_frequency_hz <= 0:
            raise ValueError("execution horizon and frequency must be positive")
        self.robot = robot
        self.safety_filter = safety_filter
        self.execution_horizon = execution_horizon
        self.control_frequency_hz = control_frequency_hz
        self._clock = clock
        self._sleeper = sleeper
        self._lock = threading.Lock()
        self._chunk: np.ndarray | None = None
        self._generation = 0
        self._interrupted = False

    def replace_chunk(self, actions: np.ndarray) -> int:
        actions = np.asarray(actions)
        if actions.ndim != 2 or actions.shape[1] != ACTION_DIM or not np.all(np.isfinite(actions)):
            raise ValueError(f"action chunk must be finite with shape (steps, {ACTION_DIM}), got {actions.shape}")
        if actions.shape[0] < self.execution_horizon:
            raise ValueError(f"action chunk must contain at least {self.execution_horizon} steps")
        with self._lock:
            self._chunk = actions.astype(np.float32, copy=True)
            self._generation += 1
            self._interrupted = False
            return self._generation

    def interrupt(self) -> None:
        with self._lock:
            self._interrupted = True
        self.robot.stop()

    def execute(self, *, last_communication: float | None = None) -> int:
        with self._lock:
            if self._chunk is None:
                raise RuntimeError("no action chunk loaded")
            generation = self._generation
            chunk = self._chunk[: self.execution_horizon].copy()
        period = 1.0 / self.control_frequency_hz
        executed = 0
        try:
            for target in chunk:
                started = self._clock()
                with self._lock:
                    if self._interrupted or generation != self._generation:
                        break
                current = self.robot.get_observation()["observation.state"]
                safe = self.safety_filter.filter(
                    current,
                    target,
                    now=started,
                    last_communication=last_communication,
                )
                self.robot.command_tcp_target(safe)
                executed += 1
                self._sleeper(max(0.0, period - (self._clock() - started)))
        except Exception:
            self.robot.stop()
            raise
        return executed

