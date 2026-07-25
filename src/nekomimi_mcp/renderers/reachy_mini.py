from __future__ import annotations

from nekomimi_mcp.intent.schema import IntentToken, MotionParams
from nekomimi_mcp.renderers.base import BaseRenderer, RendererCapability

_REACHY_MAPPING: dict[str, dict] = {
    "attending": {
        "head": {"roll": 0, "pitch": 0, "yaw": 0, "x": 0, "y": 0, "z": 0},
        "antennas": [0, 0],
        "body_yaw": 0,
    },
    "confused": {
        "head": {"roll": 10, "pitch": 0, "yaw": 15, "x": 0, "y": 0, "z": 5},
        "antennas": [0, 45],
        "body_yaw": 10,
    },
    "nod": {
        "head": {"roll": 0, "pitch": -15, "yaw": 0, "x": 0, "y": 0, "z": -5},
        "antennas": [0, 0],
        "body_yaw": 0,
    },
    "shake": {
        "head": {"roll": 0, "pitch": 0, "yaw": 25, "x": 0, "y": 0, "z": 0},
        "antennas": [0, 0],
        "body_yaw": 10,
    },
    "sulk": {
        "head": {"roll": -10, "pitch": -20, "yaw": 0, "x": 0, "y": 0, "z": 5},
        "antennas": [-40, -40],
        "body_yaw": -20,
    },
    "bashful": {
        "head": {"roll": -5, "pitch": -10, "yaw": 15, "x": 0, "y": 0, "z": 3},
        "antennas": [0, 20],
        "body_yaw": -15,
    },
    "amused": {
        "head": {"roll": 8, "pitch": 0, "yaw": 12, "x": 0, "y": 0, "z": -3},
        "antennas": [30, 30],
        "body_yaw": 5,
    },
    "surprised": {
        "head": {"roll": 0, "pitch": 10, "yaw": 0, "x": 0, "y": 0, "z": 10},
        "antennas": [90, 90],
        "body_yaw": 0,
    },
    "curious": {
        "head": {"roll": 15, "pitch": -5, "yaw": 15, "x": 0, "y": 0, "z": -5},
        "antennas": [20, 20],
        "body_yaw": 15,
    },
    "alarmed": {
        "head": {"roll": 0, "pitch": -15, "yaw": 0, "x": 0, "y": 0, "z": 15},
        "antennas": [-30, -30],
        "body_yaw": 180,
    },
    "excited": {
        "head": {"roll": 8, "pitch": 0, "yaw": 20, "x": 0, "y": 0, "z": -3},
        "antennas": [60, 60],
        "body_yaw": 20,
    },
    "tired": {
        "head": {"roll": 0, "pitch": -25, "yaw": 0, "x": 0, "y": 0, "z": 10},
        "antennas": [-50, -50],
        "body_yaw": 0,
    },
    "attentive_listen": {
        "head": {"roll": 0, "pitch": -2, "yaw": 0, "x": 0, "y": 0, "z": -5},
        "antennas": [15, 15],
        "body_yaw": 0,
    },
    "celebrate": {
        "head": {"roll": 15, "pitch": 0, "yaw": 30, "x": 0, "y": 0, "z": -10},
        "antennas": [90, 90],
        "body_yaw": 30,
    },
    "apologetic": {
        "head": {"roll": -10, "pitch": -25, "yaw": 0, "x": 0, "y": 0, "z": 8},
        "antennas": [-40, -40],
        "body_yaw": -10,
    },
    "present": {
        "head": {"roll": 0, "pitch": -8, "yaw": 0, "x": 0, "y": 0, "z": -5},
        "antennas": [30, 30],
        "body_yaw": 0,
    },
    "idle": {
        "head": {"roll": 0, "pitch": 0, "yaw": 0, "x": 0, "y": 0, "z": 0},
        "antennas": [0, 0],
        "body_yaw": 0,
    },
}


class ReachyMiniRenderer(BaseRenderer):
    body_type = "stewart_platform_desktop"
    hardware_connected = False
    capabilities = [
        RendererCapability.STEWART_PLATFORM,
        RendererCapability.ANTENNAS,
        RendererCapability.BODY_YAW,
        RendererCapability.SPEAKER,
    ]

    def status(self) -> str:
        return "STUB — no hardware, sim not connected"

    def can_express(self, token: IntentToken) -> bool:
        return token.value in _REACHY_MAPPING

    async def stop(self) -> dict:
        return {"success": True, "renderer": "reachy_mini", "action": "reset"}

    async def render(
        self, token: IntentToken, params: MotionParams | None = None, target: dict | None = None
    ) -> dict:
        mapping = _REACHY_MAPPING.get(token.value)
        if not mapping:
            return {
                "success": False,
                "error": f"no mapping for {token.value}",
                "token": token.value,
            }
        return {
            "success": True,
            "token": token.value,
            "renderer": "reachy_mini",
            "mapping": mapping,
            "params": params.model_dump() if params else None,
            "simulated": True,
            "note": "STUB — requires Reachy Mini hardware or MuJoCo sim",
        }
