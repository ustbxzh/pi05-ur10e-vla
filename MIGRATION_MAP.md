# Migration Map

## Integration decision

目标目录是在三个下载归档旁新建的独立项目。来源目录没有 `.git`，没有任何内容被删除、覆盖或重命名。OpenPI 选择“单一外部 editable dependency”方案：新项目没有 `src/openpi`，也不会同时依赖复制版与外部版。

## Source-to-target map

| Source | Audited functionality | Target | Treatment |
| --- | --- | --- | --- |
| `aloha-gamepad/.../scripts/gamepad_teleop.py` | PS4 axes/buttons、deadzone、speed、Episode 控制、50 Hz loop | `teleop/gamepad_mapping.py`, `teleop/ur10e_gamepad_teleop.py`, `teleop/episode_manager.py` | MIT 思路/结构改写为单 UR10e、20 Hz、BaseRobot；未迁移 Interbotix、左右臂、底盘、IK 常量、ALOHA pose/topic |
| `aloha-gamepad/.../scripts/lerobot_writer.py` | LeRobot V3 parquet/video/metadata、frame buffer | `data/lerobot_writer.py` | MIT 来源注明；缩减为固定 10D、两相机、RGB、20 Hz，并在写前验证 |
| `aloha-gamepad/.../scripts/view_dataset.py` | summary 与只读查看 | `data/dataset_viewer.py`, `scripts/view_ur10e_dataset.py` | 保留通用 summary，移除左右臂/底盘绘图假设 |
| `aloha-gamepad/.../scripts/eval_policy.py` | rollout loop、Ctrl+C、频率控制 | `deployment/rollout.py`, `action_chunk_executor.py` | 改为 WebSocket client；删除本地 `PI05Policy.from_pretrained` 与真机 ALOHA 初始化 |
| `aloha-gamepad/.../scripts/run_eval.sh` | 环境/入口包装 | `scripts/serve_pi05_policy.sh`, `scripts/run_ur10e_rollout.py` | 不保留机器专属路径、conda 名和 Interbotix PYTHONPATH |
| `aloha-gamepad/.../launch/` | ALOHA 双臂、底盘、camera launch | 无运行时代码 | 完全隔离；真实 UR ROS2 launch 必须等待实验室信息 |
| `openpi/.../src/openpi/policies/ur_policy.py` | `UR_ACTION_DIM=10`, Rot6D, URInputs/UROutputs, absolute-relative transforms | editable dependency + `data/ur10e_schema.py` + `deployment/action_adapter.py` | 模型侧不重写；客户端只实现物理边界的对偶转换/验证 |
| `openpi/.../src/openpi/training/config.py` | LeRobotURDataConfig、LoRA UR configs、metadata | `training/openpi_profile.py`, shell wrappers | 组合上游配置，不修改其静态注册表 |
| `openpi/.../src/openpi/models/` | π0/π0.5、PaliGemma、Action Expert、flow matching、LoRA、RTC sampler | editable dependency | 不复制、不重写 |
| `openpi/.../src/openpi/serving/` and `packages/openpi-client` | WebSocket server/client 与 RTC envelope | `deployment/policy_client.py` | 延迟导入并只负责通信 |
| `robotwin_repo` | experiments/results/docs 的分层表达 | `experiments/`, `results/`, selected `docs/` | 仅参考分类；模板为重新撰写且全部标记未执行 |

## Data interfaces

数采到训练：writer 输出两个 RGB video key、绝对 10D state/action 与 task metadata；`LeRobotURDataConfig` repack 为 `state/actions/prompt`，先调用 `URInputs` 和 `AbsoluteTCPActionsToRelative`，再 normalization、resize/tokenize、pad-to-32。

checkpoint 到执行：OpenPI checkpoint → upstream policy server → WebSocket response `(20,10)` relative chunk → `relative_actions_to_absolute` → SafetyFilter → Executor 前 10 步 → BaseRobot。

## Intentional structure difference

需求示意树含 `src/openpi/`。本项目省略它，因为真实上游是一个完整的 144 文件 Python workspace（含 client package 与脚本），选择性复制会破坏导入关系，整体复制又会制造分叉。`pyproject.toml` 明确指向工作区中的已审计上游路径；部署到其他机器时应检出 `OPENPI_COMMIT.txt` 记录的版本并更新 editable path。

