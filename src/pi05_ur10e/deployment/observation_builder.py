"""Translate BaseRobot observations into the OpenPI UR policy contract."""

from __future__ import annotations

from typing import Any

from pi05_ur10e.data.ur10e_schema import (
    BASE_IMAGE_KEY,
    PROMPT_KEY,
    STATE_KEY,
    WRIST_IMAGE_KEY,
    validate_image,
    validate_vector,
)


class ObservationBuilder:
    def __init__(self, prompt: str):
        if not prompt.strip():
            raise ValueError("prompt must be non-empty")
        self.prompt = prompt

    def build(self, robot_observation: dict[str, Any]) -> dict[str, Any]:
        return {
            BASE_IMAGE_KEY: validate_image(robot_observation[BASE_IMAGE_KEY], name=BASE_IMAGE_KEY),
            WRIST_IMAGE_KEY: validate_image(robot_observation[WRIST_IMAGE_KEY], name=WRIST_IMAGE_KEY),
            STATE_KEY: validate_vector(robot_observation[STATE_KEY], name=STATE_KEY),
            PROMPT_KEY: self.prompt,
        }

