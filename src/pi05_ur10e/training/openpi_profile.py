"""Build the named project profile without forking OpenPI's source tree."""

from __future__ import annotations

import dataclasses

PROJECT_CONFIG_NAME = "pi05_ur10e_gamepad_lora"
UPSTREAM_CONFIG_NAME = "pi05_ur10e_lora_finetune"


def create_train_config(repo_id: str):
    """Return an upstream TrainConfig with only project identity/data changed."""
    if not repo_id.strip():
        raise ValueError("repo_id must be non-empty")
    try:
        from openpi.training import config as openpi_config
    except ImportError as exc:
        raise ImportError("the editable OpenPI dependency is required for training configuration") from exc
    base = openpi_config.get_config(UPSTREAM_CONFIG_NAME)
    data = dataclasses.replace(base.data, repo_id=repo_id)
    result = dataclasses.replace(base, name=PROJECT_CONFIG_NAME, project_name="pi05-ur10e-vla", data=data)
    metadata = result.policy_metadata or {}
    invariant_ok = (
        result.model.action_dim == 32
        and result.model.action_horizon == 20
        and result.model.pi05
        and result.model.paligemma_variant == "gemma_2b_lora"
        and result.model.action_expert_variant == "gemma_300m_lora"
        and getattr(result.weight_loader, "params_path", "").endswith("/pi05_base/params")
        and type(result.data).__name__ == "LeRobotURDataConfig"
        and metadata.get("action_dim") == 10
        and metadata.get("prediction_horizon") == 20
        and metadata.get("execution_horizon") == 10
        and metadata.get("control_frequency_hz") == 20
    )
    if not invariant_ok:
        raise RuntimeError("audited upstream UR10e model contract changed")
    return result
