"""Exercise policy response validation without opening a socket."""

import numpy as np

from pi05_ur10e.data.ur10e_schema import ACTION_DIM, PREDICTION_HORIZON, rotation_matrix_to_rot6d
from pi05_ur10e.deployment.policy_client import WebSocketPolicyClient


class Transport:
    def get_server_metadata(self):
        return {"action_dim": ACTION_DIM, "prediction_horizon": PREDICTION_HORIZON}

    def infer(self, observation, *, rtc=None):
        chunk = np.zeros((PREDICTION_HORIZON, ACTION_DIM), dtype=np.float32)
        chunk[:, 3:9] = rotation_matrix_to_rot6d(np.eye(3))
        return {"actions": chunk}

    def reset(self):
        pass


client = WebSocketPolicyClient(transport=Transport())
print(client.infer({"prompt": "mock"})["actions"].shape)

