import numpy as np
import pytest

from pi05_ur10e.data.ur10e_schema import PREDICTION_HORIZON, identity_state
from pi05_ur10e.deployment.rtc_manager import RTCManager


def _chunk():
    return np.repeat(identity_state()[None, :], PREDICTION_HORIZON, axis=0)


def test_rtc_request_uses_unexecuted_absolute_suffix_and_skips_committed_prefix():
    manager = RTCManager("non_vjp", prefix_len=2)
    manager.install_initial_chunk(_chunk())
    manager.advance(10)
    snapshot = manager.build_request()
    assert snapshot.request["prev_actions_abs"].shape == (10, 10)
    manager.advance(2)
    remaining = manager.install_replanned_chunk(_chunk(), snapshot)
    assert remaining.shape == (18, 10)


def test_rtc_cannot_switch_before_prefix_committed():
    manager = RTCManager("vjp", prefix_len=2)
    manager.install_initial_chunk(_chunk())
    snapshot = manager.build_request()
    with pytest.raises(RuntimeError, match="committed"):
        manager.install_replanned_chunk(_chunk(), snapshot)

