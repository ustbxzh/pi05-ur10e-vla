"""Client-side RTC state only; the mathematical guidance stays in OpenPI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, PREDICTION_HORIZON

RTCMode = Literal["off", "non_vjp", "vjp", "train_rtc"]


@dataclass(frozen=True)
class RTCRequestSnapshot:
    request_cursor: int
    request: dict | None


class RTCManager:
    def __init__(
        self,
        mode: RTCMode = "off",
        *,
        prefix_len: int = 2,
        decay_end: int | None = None,
        schedule: str = "exp",
        max_guidance_weight: float = 5.0,
    ):
        if mode not in {"off", "non_vjp", "vjp", "train_rtc"}:
            raise ValueError(f"unknown RTC mode: {mode}")
        if prefix_len <= 0 or prefix_len >= PREDICTION_HORIZON:
            raise ValueError("prefix_len must be inside the prediction horizon")
        self.mode = mode
        self.prefix_len = prefix_len
        self.decay_end = decay_end if decay_end is not None else min(prefix_len * 2, PREDICTION_HORIZON)
        self.schedule = schedule
        self.max_guidance_weight = max_guidance_weight
        self._chunk: np.ndarray | None = None
        self._cursor = 0

    @property
    def cursor(self) -> int:
        return self._cursor

    def install_initial_chunk(self, actions: np.ndarray) -> None:
        self._chunk = self._validate_chunk(actions)
        self._cursor = 0

    def advance(self, steps: int = 1) -> None:
        if self._chunk is None:
            raise RuntimeError("no chunk is installed")
        if steps < 0 or self._cursor + steps > len(self._chunk):
            raise ValueError("advance exceeds the current chunk")
        self._cursor += steps

    def build_request(self) -> RTCRequestSnapshot:
        if self.mode == "off":
            return RTCRequestSnapshot(self._cursor, None)
        if self._chunk is None:
            raise RuntimeError("RTC requires an old action chunk")
        remaining = self._chunk[self._cursor :].copy()
        if len(remaining) < self.prefix_len:
            raise RuntimeError("old chunk has fewer unexecuted actions than prefix_len")
        request: dict = {
            "mode": self.mode,
            "prev_actions_abs": remaining,
            "prefix_len": self.prefix_len,
        }
        if self.mode in {"non_vjp", "vjp"}:
            request.update(
                decay_end=self.decay_end,
                schedule=self.schedule,
                max_guidance_weight=self.max_guidance_weight,
            )
        return RTCRequestSnapshot(self._cursor, request)

    def install_replanned_chunk(self, actions: np.ndarray, snapshot: RTCRequestSnapshot) -> np.ndarray:
        chunk = self._validate_chunk(actions)
        committed = self._cursor - snapshot.request_cursor
        if committed < 0:
            raise RuntimeError("RTC cursor moved backwards")
        if self.mode != "off" and committed < self.prefix_len:
            raise RuntimeError("cannot switch before the committed RTC prefix has executed")
        if committed >= len(chunk):
            raise RuntimeError("new chunk was exhausted while inference was pending")
        self._chunk = chunk
        self._cursor = committed
        return chunk[committed:].copy()

    @staticmethod
    def _validate_chunk(actions: np.ndarray) -> np.ndarray:
        actions = np.asarray(actions)
        expected = (PREDICTION_HORIZON, ACTION_DIM)
        if actions.shape != expected or not np.all(np.isfinite(actions)):
            raise ValueError(f"RTC chunk must be finite with shape {expected}, got {actions.shape}")
        return actions.astype(np.float32, copy=True)

