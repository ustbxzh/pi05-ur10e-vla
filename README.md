# pi05-ur10e-vla

## Project Overview

本项目是“基于游戏手柄遥操作示教的 UR10e 数据采集、π0.5 LoRA 后训练与 Policy Server 闭环部署”的源码级系统集成。它把机器人、数采、训练/推理和评测分成明确边界；当前实现可在 MockUR10eRobot 上离线验证，但没有宣称完成真实训练或真机部署。

## Motivation

来源项目分别覆盖 ALOHA 手柄数采、OpenPI 模型训练和实验记录。直接拼接会留下双臂 14D/UR10e 10D、50/20 Hz、本地推理/WebSocket 推理等冲突。本项目以一个固定契约贯穿全链路，并只把 OpenPI 保留为唯一外部模型实现。

## End-to-End Pipeline

```text
Gamepad Teleoperation
→ UR10e Cartesian Control
→ LeRobot V3 Demonstration Dataset
→ pi05_base
→ LoRA Post-Training
→ OpenPI Policy Server
→ UR10e ROS2 Client
→ Action Chunk Execution
→ RTC
→ Evaluation and Failure Analysis
```

代码层对应四层：

1. `robot`：BaseRobot、Mock、未来 ROS2 backend、相机/夹爪边界、安全过滤。
2. `teleop` + `data`：手柄映射、Episode 生命周期、LeRobot V3 writer/validator/viewer。
3. `training` + `deployment`：OpenPI 配置组合、WebSocket 客户端、动作适配、chunk executor、RTC。
4. `evaluation` + `docs` + `experiments`：可追溯记录、协议模板和诚实的项目材料。

## Repository Structure

```text
configs/                 固定契约、硬件待配置项、部署设置
src/pi05_ur10e/
  robot/                 唯一机器人抽象与安全层
  teleop/                单 UR10e 手柄遥操作与 Episode 状态机
  data/                  LeRobot V3 schema、writer、validator、viewer
  training/              外部 OpenPI 配置组合
  deployment/            WebSocket、动作适配、chunk、RTC、rollout
  evaluation/            episode/failure 记录与指标
scripts/                 数采、验证、训练、serve、rollout 入口
examples/                只使用 mock 的小例子
tests/                   离线单元与最小集成测试
docs/                    架构、训练、部署、复现与失败分析
experiments/             尚未执行的实验协议模板
results/                 结果落盘规范（当前无结果）
```

OpenPI 不复制到 `src/openpi`。`pyproject.toml` 的 editable source 指向同级已审计的 `openpi05-post-train-compat-lerobot-v3`，从而避免两个 OpenPI 副本。详见 [MIGRATION_MAP.md](MIGRATION_MAP.md)。

## Unified UR10e Data Contract

物理 `state` 和 `action` 均为 float32 `[10]`：

```text
[x, y, z, rot6d_1, rot6d_2, rot6d_3, rot6d_4, rot6d_5, rot6d_6, gripper]
```

- `state`：base frame 下当前绝对 TCP 状态。
- 数据集 `action`：base frame 下绝对 TCP 目标。
- 图像：RGB `uint8[H,W,3]`，键为 `base_0_rgb`、`left_wrist_0_rgb` 的完整 observation 路径。
- task：每个 Episode 一个非空字符串；部署时映射为 `prompt`。
- 频率 20 Hz，prediction horizon 20，execution horizon 10。
- OpenPI `AbsoluteTCPActionsToRelative` 在训练/推理变换边界使用当前 state 将动作变为 TCP-frame relative；随后 state/action 从物理 10D 零填充到模型 32D。服务端 `UROutputs` 截回 10D，客户端再转为绝对目标。

常量只定义于 `data/ur10e_schema.py`，配置副本用于人类可读检查。

## Data Collection

```bash
python scripts/collect_ur10e_data.py ./data/my_task \
  --repo-id my_org/ur10e_gamepad_demonstrations \
  --task "pick the object" --robot mock
python scripts/validate_ur10e_dataset.py ./data/my_task
```

当前命令只允许 mock。物理手柄通过延迟导入的 pygame source 读取；Circle 开始/结束、Square 丢弃、X/Triangle 控制夹爪的语义来自 ALOHA 通用交互，但不包含双臂、Interbotix 或移动底盘。

## π0.5 LoRA Post-Training

`pi05_ur10e.training.openpi_profile.create_train_config(repo_id)` 生成命名配置 `pi05_ur10e_gamepad_lora`。它从真实上游 `pi05_ur10e_lora_finetune` dataclass 组合，只替换 name、project name 和 repo_id，并检查 π0.5、32D、20-step 不变量。训练 shell 使用同一上游 CLI profile 加等价覆盖，因为上游注册表不支持外部注册。

运行前先计算并检查当前数据的 norm stats；不得借用不匹配数据集的统计量。脚本不会在本仓库验证阶段执行，也不会自动下载模型。

## Policy Server Deployment

GPU 端运行上游 `serve_policy.py`；机器人端只使用 OpenPI WebSocket client。`policy_client.py` 不接触机器人；`rollout.py` 才组合 observation、网络响应、相对到绝对转换、安全过滤和执行器。

`scripts/run_ur10e_rollout.py` 默认且当前只允许 mock。真实 UR10e 模式在实验室 backend、帧、controller、相机、夹爪和安全限制确定前主动退出。

## Action Chunk and RTC

普通路径每次验证 `(20,10)` chunk，只执行前 10 步。Executor 支持中断和用新 generation 替换旧 chunk。RTC 默认 `off`；启用时 `RTCManager` 只管理旧 chunk、游标、`prev_actions_abs`、`prefix_len` 与已提交 prefix 的跳过，数学 guidance 继续由 OpenPI 的 sampler 处理。

## Current Status

| Status | Scope |
| --- | --- |
| Implemented | 分层接口、10D schema、writer、WebSocket 边界、安全过滤、chunk/RTC 状态管理、文档模板 |
| Mock-validated | Mock observation/action、schema/Rot6D、writer 最小样本、observation keys、chunk 执行、RTC 游标 |
| Requires real hardware | ROS2 backend、坐标帧、controller、相机、夹爪、急停与限位验证 |
| Requires training | 当前 UR10e 数据 norm stats、LoRA checkpoint、服务端元数据实测 |
| Planned | 真机数采、闭环 rollout、RTC 对照实验、失败分析 |

## Planned Hardware Integration

需要用户提供并在实验室审批：ROS2 发行版与工作区、状态接口、笛卡尔 controller/action 接口、base/tool frame、两路 RGB stream 与编码、夹爪归一化映射、home target、workspace/速度/加速度/jerk 限制、急停/保护停机恢复、QoS 与 watchdog 行为。项目没有猜测这些名称或数值。

## Third-Party Attribution

- `aloha-gamepad`（MIT）：手柄交互、Episode、writer/viewer 的设计来源；重写后去除 ALOHA 硬件耦合。
- Physical Intelligence OpenPI（Apache-2.0）：唯一模型/训练/serve/client/RTC 实现，以 editable dependency 使用。
- `robotwin_repo`：未发现许可证，仅参考信息分类，未复制正文、结果、数字或媒体。

完整说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## Limitations

没有执行训练、下载 checkpoint、连接机器人或运行物理控制。默认安全值只用于 mock 示例，不是 UR10e 安全认证参数。LeRobot writer 是针对本项目固定契约的小实现，投入大规模采集前仍应以目标 LeRobot 版本做兼容性回归。RTC 客户端是普通操作系统上的时序状态机，不是工业实时调度器。

