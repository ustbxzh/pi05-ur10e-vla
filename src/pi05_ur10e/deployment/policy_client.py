"""WebSocket-only policy transport; this module never commands a robot."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

import numpy as np

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, PREDICTION_HORIZON


class PolicyTransport(Protocol):
    def get_server_metadata(self) -> dict[str, Any]: ...

    def infer(self, observation: dict[str, Any], *, rtc: Mapping[str, Any] | None = None) -> dict[str, Any]: ...

    def reset(self) -> None: ...


class WebSocketPolicyClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        *,
        api_key: str | None = None,
        transport: PolicyTransport | None = None,
    ):
        if transport is None:
            try:
                from openpi_client.websocket_client_policy import WebsocketClientPolicy
            except ImportError as exc:
                raise ImportError("install the 'deployment' extra or the editable openpi-client package") from exc
            transport = WebsocketClientPolicy(host=host, port=port, api_key=api_key)
        self._transport = transport
        self.metadata = dict(transport.get_server_metadata())
        self._validate_metadata()

    def _validate_metadata(self) -> None:
        if int(self.metadata.get("action_dim", -1)) != ACTION_DIM:
            raise ValueError(f"server action_dim must be {ACTION_DIM}")
        if int(self.metadata.get("prediction_horizon", -1)) != PREDICTION_HORIZON:
            raise ValueError(f"server prediction_horizon must be {PREDICTION_HORIZON}")

    def infer(self, observation: dict[str, Any], *, rtc: Mapping[str, Any] | None = None) -> dict[str, Any]:
        result = self._transport.infer(observation) if rtc is None else self._transport.infer(observation, rtc=rtc)
        if "actions" not in result:
            raise ValueError("policy response does not contain 'actions'")
        actions = np.asarray(result["actions"])
        if actions.shape != (PREDICTION_HORIZON, ACTION_DIM) or not np.all(np.isfinite(actions)):
            raise ValueError(
                f"policy actions must be finite with shape ({PREDICTION_HORIZON}, {ACTION_DIM}), got {actions.shape}"
            )
        return {**result, "actions": actions.astype(np.float32, copy=False)}

    def reset(self) -> None:
        self._transport.reset()

