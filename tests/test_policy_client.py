import numpy as np

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, PREDICTION_HORIZON, identity_state
from pi05_ur10e.deployment.policy_client import WebSocketPolicyClient


class MockTransport:
    def get_server_metadata(self):
        return {"action_dim": ACTION_DIM, "prediction_horizon": PREDICTION_HORIZON}

    def infer(self, observation, *, rtc=None):
        return {"actions": np.repeat(identity_state()[None, :], PREDICTION_HORIZON, axis=0)}

    def reset(self):
        pass


def test_mock_transport_response_is_validated():
    client = WebSocketPolicyClient(transport=MockTransport())
    assert client.infer({"prompt": "test"})["actions"].shape == (20, 10)

