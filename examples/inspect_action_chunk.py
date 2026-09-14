"""Inspect the fixed physical/model chunk shapes."""

import numpy as np

from pi05_ur10e import ACTION_DIM, MODEL_ACTION_DIM, PREDICTION_HORIZON


physical = np.zeros((PREDICTION_HORIZON, ACTION_DIM), dtype=np.float32)
padded = np.pad(physical, ((0, 0), (0, MODEL_ACTION_DIM - ACTION_DIM)))
print({"physical": physical.shape, "model": padded.shape})

