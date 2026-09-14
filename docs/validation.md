# Validation Report

Validation is offline only; no model, dataset or robot connection was used.

## Passed

- Python compile check for `src`, `scripts`, `examples`.
- Import of all 29 `pi05_ur10e` modules with optional heavy dependencies kept lazy.
- 15 pytest cases covering mock robot, 10D state/action, Rot6D rejection, gripper range, deadzone/mapping, observation keys, WebSocket response boundary, safety limits/timeouts, action chunk shape/execution, LeRobot V3 minimal writer and RTC state.
- Mock rollout: one chunk, 10 submitted steps.
- Git for Windows Bash parsed all three shell entrypoints with `bash -n`.
- Runtime source search: no Interbotix, Mobile ALOHA, `action.base`, bimanual 14D or mobile-base references.
- Result-claim search: no copied RoboTwin success rate/checkpoint/hardware claims.
- Source snapshot file counts remain 13 / 144 / 22.

## Not passed / not available

- Full OpenPI profile import: the current lightweight Python environment lacks `etils`; no large training dependency was installed. Static source audit confirms the composed fields, but profile execution must be checked inside the upstream `uv` environment.
- Training, checkpoint loading, server networking, ROS2 and real UR10e checks: intentionally not executed.
