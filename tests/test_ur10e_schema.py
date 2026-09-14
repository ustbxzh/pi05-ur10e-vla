import numpy as np
import pytest

from pi05_ur10e.data.ur10e_schema import ContractError, identity_state, rot6d_to_rotation_matrix, validate_vector


def test_identity_state_is_valid_10d_float32():
    state = validate_vector(identity_state(), name="state")
    assert state.shape == (10,)
    assert state.dtype == np.float32
    np.testing.assert_allclose(rot6d_to_rotation_matrix(state[3:9]), np.eye(3), atol=1e-6)


def test_parallel_rot6d_is_rejected():
    state = identity_state()
    state[3:9] = [1, 0, 0, 2, 0, 0]
    with pytest.raises(ContractError, match="parallel"):
        validate_vector(state, name="state")


def test_gripper_range_is_enforced():
    state = identity_state(gripper=1.1)
    with pytest.raises(ContractError, match="gripper"):
        validate_vector(state, name="state")

