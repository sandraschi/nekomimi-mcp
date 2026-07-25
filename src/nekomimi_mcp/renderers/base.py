from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from nekomimi_mcp.intent.schema import IntentToken, MotionParams


class RendererCapability(StrEnum):
    DRIVE_BASE = "drive_base"
    PTZ_GIMBAL = "ptz_gimbal"
    HEAD_PITCH = "head_pitch"
    HEAD_YAW = "head_yaw"
    HEAD_ROLL = "head_roll"
    HEAD_TRANSLATE = "head_translate"
    STEWART_PLATFORM = "stewart_platform"
    ARMS = "arms"
    HANDS = "hands"
    ANTENNAS = "antennas"
    FACE_DISPLAY = "face_display"
    LEDS = "leds"
    SPEAKER = "speaker"
    BODY_YAW = "body_yaw"
    HUMAN_LEGS = "human_legs"
    HUMANOID_FULL = "humanoid_full"
    GAZE = "gaze"
    IDLE_BREATHING = "idle_breathing"


class BaseRenderer(ABC):
    body_type: str = "unknown"
    capabilities: list[RendererCapability] = []
    hardware_connected: bool = False

    @abstractmethod
    async def render(
        self, token: IntentToken, params: MotionParams | None = None, target: dict | None = None
    ) -> dict: ...

    @abstractmethod
    async def stop(self) -> dict: ...

    @abstractmethod
    def status(self) -> str: ...

    @abstractmethod
    def can_express(self, token: IntentToken) -> bool: ...

    async def idle_tick(self) -> dict | None:
        return None

    async def render_stream(
        self, tokens: list[IntentToken], params: MotionParams | None = None
    ) -> list[dict]:
        results = []
        for token in tokens:
            result = await self.render(token, params)
            results.append(result)
        return results

    def describe(self) -> dict:
        return {
            "name": self.__class__.__name__,
            "body_type": self.body_type,
            "hardware_connected": self.hardware_connected,
            "capabilities": [c.value for c in self.capabilities],
            "status": self.status(),
            "expressible_tokens": [t.value for t in IntentToken if self.can_express(t)],
        }
