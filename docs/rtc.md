# Real-Time Chunking (RTC)

Independently predicted action chunks can disagree at their boundary because each inference starts from a new observation/noise realization and has no obligation to preserve the old plan. RTC constrains part of the new chunk using actions from the old chunk that were still unexecuted when inference began.

The client `RTCManager` snapshots `old_chunk[cursor:]` as absolute `prev_actions_abs` and sends it with `prefix_len`. The upstream UR input transforms apply the same absolute-to-relative conversion, normalization and 32D padding used for ordinary actions. The OpenPI policy validates the request and builds fixed sampler inputs.

- `off`: no RTC envelope.
- `non_vjp`: uses upstream prefix weights/guidance without the VJP path.
- `vjp`: selects the sampler's VJP-based guidance path.
- `train_rtc`: requires a checkpoint trained with action-prefix conditioning and rejects inference-guidance-only parameters.

`prefix_len` should cover actions committed while the WebSocket inference is pending. A larger value tolerates more latency but constrains more of the new plan. When inference returns, the client skips the number of prefix steps already submitted since the snapshot; it refuses to switch before the promised prefix was committed.

The OpenPI source owns schedules, weights, VJP calculations and denoising. This project only owns client cursor/state. The robot client must still schedule commands because a policy server produces trajectories, not ROS2 deadlines. Python threads, WebSockets and a normal OS do not provide bounded industrial real-time behavior; this implementation is a research integration, not a safety PLC.

