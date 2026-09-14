import numpy as np
import pytest

from pi05_ur10e.data.ur10e_schema import identity_state
from pi05_ur10e.robot.safety_filter import SafetyFilter, SafetyViolation


def test_translation_step_is_limited():
    current = identity_state(position=(0.4, 0.0, 0.3))
    target = current.copy()
    target[0] += 0.2
    filtered = SafetyFilter().filter(current, target)
    assert np.linalg.norm(filtered[:3] - current[:3]) <= 0.020001


def test_stale_policy_communication_is_rejected():
    state = identity_state(position=(0.4, 0.0, 0.3))
    with pytest.raises(SafetyViolation, match="timeout"):
        SafetyFilter().filter(state, state, now=2.0, last_communication=0.0)

