"""Composable single-arm teleoperation loop; input and robot are injected."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Protocol

from pi05_ur10e.data.ur10e_schema import ACTION_KEY, STATE_KEY
from pi05_ur10e.robot.base_robot import BaseRobot
from pi05_ur10e.teleop.episode_manager import EpisodeManager
from pi05_ur10e.teleop.gamepad_mapping import GamepadMapper


@dataclass(frozen=True)
class GamepadSample:
    left_x: float = 0.0
    left_y: float = 0.0
    right_x: float = 0.0
    right_y: float = 0.0
    orientation_modifier: bool = False
    gripper: float | None = None
    start_stop: bool = False
    discard: bool = False
    exit: bool = False
    speed_direction: int = 0


class GamepadSource(Protocol):
    def read(self) -> GamepadSample: ...


class PygameGamepadSource:
    """Poll a standard PS-style controller without importing ROS2.

    Axis/button indices are configurable because operating systems expose
    controllers differently. Defaults mirror the audited ALOHA mapping.
    """

    def __init__(self, *, device_index: int = 0, axis_map: dict[str, int] | None = None, button_map: dict[str, int] | None = None):
        try:
            import pygame
        except ImportError as exc:
            raise ImportError("pygame is required for physical gamepad input") from exc
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() <= device_index:
            raise RuntimeError(f"no gamepad found at index {device_index}")
        self._pygame = pygame
        self._joystick = pygame.joystick.Joystick(device_index)
        self._joystick.init()
        self._axis = axis_map or {
            "left_x": 0,
            "left_y": 1,
            "right_x": 3,
            "right_y": 4,
            "r2": 5,
            "dpad_y": 7,
        }
        self._button = button_map or {"close": 0, "start_stop": 1, "open": 2, "discard": 3, "exit": 10}
        self._gripper = 0.0

    def read(self) -> GamepadSample:
        self._pygame.event.pump()
        if self._pressed("open"):
            self._gripper = 0.0
        if self._pressed("close"):
            self._gripper = 1.0
        return GamepadSample(
            left_x=self._joystick.get_axis(self._axis["left_x"]),
            left_y=self._joystick.get_axis(self._axis["left_y"]),
            right_x=self._joystick.get_axis(self._axis["right_x"]),
            right_y=self._joystick.get_axis(self._axis["right_y"]),
            orientation_modifier=self._joystick.get_axis(self._axis["r2"]) > 0.5,
            gripper=self._gripper,
            start_stop=self._pressed("start_stop"),
            discard=self._pressed("discard"),
            exit=self._pressed("exit"),
            speed_direction=int(-self._joystick.get_axis(self._axis["dpad_y"])),
        )

    def _pressed(self, name: str) -> bool:
        index = self._button[name]
        return index < self._joystick.get_numbuttons() and bool(self._joystick.get_button(index))


class UR10eGamepadTeleop:
    def __init__(self, robot: BaseRobot, source: GamepadSource, mapper: GamepadMapper, episodes: EpisodeManager):
        self.robot = robot
        self.source = source
        self.mapper = mapper
        self.episodes = episodes

    def run(self, *, max_steps: int | None = None) -> None:
        period = 1.0 / self.mapper.config.control_frequency_hz
        self.robot.connect()
        previous_start_stop = False
        previous_speed_direction = 0
        try:
            step = 0
            while max_steps is None or step < max_steps:
                started = time.monotonic()
                gamepad = self.source.read()
                if gamepad.exit:
                    break
                if gamepad.start_stop and not previous_start_stop:
                    if self.episodes.state.value == "idle":
                        self.episodes.start()
                    else:
                        self.episodes.finish()
                previous_start_stop = gamepad.start_stop
                if gamepad.speed_direction and not previous_speed_direction:
                    self.mapper.adjust_speed(gamepad.speed_direction)
                previous_speed_direction = gamepad.speed_direction
                if gamepad.discard:
                    self.episodes.discard()
                observation = self.robot.get_observation()
                action = self.mapper.map_axes(
                    observation[STATE_KEY],
                    left_x=gamepad.left_x,
                    left_y=gamepad.left_y,
                    right_x=gamepad.right_x,
                    right_y=gamepad.right_y,
                    orientation_modifier=gamepad.orientation_modifier,
                    gripper=gamepad.gripper,
                )
                self.robot.command_tcp_target(action)
                self.episodes.record({**observation, ACTION_KEY: action})
                step += 1
                time.sleep(max(0.0, period - (time.monotonic() - started)))
        finally:
            self.robot.stop()
            self.robot.disconnect()
