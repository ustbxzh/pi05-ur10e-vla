# Data Collection

## Contract

Each input to `LeRobotWriter.add_frame` contains both RGB uint8 images, the current absolute 10D state, the absolute 10D target action and a task string. Shape, finite values, decodable Rot6D and normalized gripper are checked before buffering. Episodes cannot mix task strings. Writer frequency is fixed at 20 Hz.

## Interaction flow

The pygame source polls a PS-style controller. Axes are configurable to accommodate OS mappings. The default semantic mapping retains the audited ALOHA interaction: stick deadzone, speed scale, translation/rotation modifier, open/close, start/stop, discard and exit. It does not contain arm selection or base motion.

Collection starts with `--robot mock`. The real mode is disabled until the ROS2 backend and safety configuration are reviewed. On Ctrl+C or exception, the loop calls stop and disconnect. An active unsaved episode causes writer finalization to fail instead of silently creating partial metadata.

## LeRobot V3 output

One episode produces one data parquet and one MP4 per image feature. Global metadata contains info, tasks, episode ranges and numeric stats. Images are RGB on input; unlike the source ALOHA writer, no implicit BGR-to-RGB conversion occurs.

