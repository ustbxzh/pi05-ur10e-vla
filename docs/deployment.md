# Deployment

## Process boundary

```text
Robot process                              GPU process
BaseRobot → ObservationBuilder ─WebSocket→ OpenPI Policy Server
    ↑                                      π0.5 LoRA checkpoint
    └─ Executor ← SafetyFilter ← absolute ← relative (20,10) chunk
```

The server response is physical 10D but relative TCP action representation because `AbsoluteTCPActionsToRelative` is part of the input transforms and `UROutputs` only removes model padding. `action_adapter.py` composes each relative pose with the observation's absolute pose before commands reach the safety layer.

The executor validates rank/dimension/finiteness, takes the first 10 steps, runs at 20 Hz, stops on exceptions, and observes interrupt/chunk-generation changes. The safety filter rejects stale communications and invalid numbers, clips translation step/workspace/gripper, and limits rotation step. Supplied limits are mock examples only.

## Required hardware information

Before implementing a ROS2 backend, provide exact state and Cartesian command APIs, base/tool frames, camera streams, gripper calibration, home target, safety limits, QoS, controller lifecycle and emergency-stop behavior. These must be validated on the laboratory system; no topic/controller names are assumed here.

