# System Architecture

```text
GamepadSource ─→ GamepadMapper ─→ BaseRobot.command_tcp_target
                                  │
BaseRobot.get_observation ─→ EpisodeManager ─→ LeRobotWriter ─→ LeRobot V3
                                  │
                                  └→ validator ─→ OpenPI training profile

BaseRobot ─→ ObservationBuilder ─→ WebSocketPolicyClient ─→ GPU Policy Server
   ↑                                                        │
   └─ ActionChunkExecutor ← SafetyFilter ← absolute adapter ←┘
                                      ↑
                                RTCManager state
```

`BaseRobot` is the only robot dependency used by both collection and rollout. The policy client is transport-only; it cannot issue motion. The executor knows robot timing but not model internals. This separation makes mock tests meaningful and keeps future ROS2 code inside one backend.

`UR10eRobot` delegates to an injected laboratory backend. Without one, every hardware operation raises `HardwareIntegrationRequired`; this is intentional fail-closed behavior.

