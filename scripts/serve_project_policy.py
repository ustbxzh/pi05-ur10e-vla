#!/usr/bin/env python3
"""Serve a local checkpoint using the composed project config."""

from __future__ import annotations

import argparse
import logging

from pi05_ur10e.training.openpi_profile import create_train_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--default-prompt")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()

    from openpi.policies import policy as policy_module
    from openpi.policies import policy_config
    from openpi.serving.websocket_policy_server import WebsocketPolicyServer

    policy = policy_config.create_trained_policy(
        create_train_config(args.repo_id), args.checkpoint, default_prompt=args.default_prompt
    )
    metadata = policy.metadata
    if args.record:
        policy = policy_module.PolicyRecorder(policy, "policy_records")
    logging.info("serving pi05_ur10e_gamepad_lora on port %d", args.port)
    WebsocketPolicyServer(policy=policy, host="0.0.0.0", port=args.port, metadata=metadata).serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
