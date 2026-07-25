from __future__ import annotations

import json

from nekomimi_mcp.intent.schema import IntentToken, MotionParams
from nekomimi_mcp.renderers.base import BaseRenderer, RendererCapability

# Canonical VRM 1.0 bone pose keyframes for each intent token.
# Units are local Euler rotations (degrees) on the VRM normalized humanoid bone set.
# Only bones that move are specified — others inherit from neutral T-pose.

_VRM_POSES: dict[str, dict[str, dict[str, float]]] = {
    "attending": {
        "head": {"x": 0, "y": 0, "z": 0},
        "neck": {"x": 0, "y": 0, "z": 0},
        "upper_chest": {"x": 0, "y": 0, "z": 0},
    },
    "confused": {
        "head": {"x": -5, "y": 10, "z": 15},
        "left_upper_arm": {"x": -20, "y": 10, "z": 0},
        "right_upper_arm": {"x": -10, "y": -5, "z": 0},
    },
    "nod": {
        "head": {"x": -20, "y": 0, "z": 0},
        "neck": {"x": -10, "y": 0, "z": 0},
    },
    "shake": {
        "head": {"x": 0, "y": 25, "z": 0},
    },
    "sulk": {
        "head": {"x": -10, "y": -15, "z": 5},
        "neck": {"x": -15, "y": -10, "z": 0},
        "upper_chest": {"x": -5, "y": -10, "z": 0},
        "left_upper_arm": {"x": 10, "y": -10, "z": 0},
        "right_upper_arm": {"x": 10, "y": 10, "z": 0},
    },
    "bashful": {
        "head": {"x": -5, "y": 15, "z": 8},
        "left_upper_arm": {"x": 20, "y": -15, "z": 0},
        "right_upper_arm": {"x": 20, "y": 15, "z": 0},
    },
    "amused": {
        "head": {"x": 5, "y": 0, "z": 10},
        "upper_chest": {"x": 5, "y": 0, "z": 0},
    },
    "surprised": {
        "head": {"x": 10, "y": 0, "z": 0},
        "neck": {"x": 15, "y": 0, "z": 0},
        "left_upper_arm": {"x": -45, "y": -20, "z": 0},
        "right_upper_arm": {"x": -45, "y": 20, "z": 0},
        "left_lower_arm": {"x": -30, "y": 0, "z": 0},
        "right_lower_arm": {"x": -30, "y": 0, "z": 0},
    },
    "curious": {
        "head": {"x": -5, "y": 20, "z": 15},
        "neck": {"x": -5, "y": 15, "z": 0},
        "upper_chest": {"x": -5, "y": 5, "z": 0},
    },
    "alarmed": {
        "head": {"x": -15, "y": 0, "z": 0},
        "neck": {"x": -10, "y": 0, "z": 0},
        "upper_chest": {"x": -10, "y": 0, "z": 0},
        "left_upper_arm": {"x": 10, "y": -30, "z": 0},
        "right_upper_arm": {"x": 10, "y": 30, "z": 0},
        "left_lower_arm": {"x": -20, "y": 0, "z": 0},
        "right_lower_arm": {"x": -20, "y": 0, "z": 0},
    },
    "excited": {
        "head": {"x": 5, "y": 0, "z": 0},
        "left_upper_arm": {"x": -80, "y": -10, "z": 0},
        "right_upper_arm": {"x": -80, "y": 10, "z": 0},
        "left_lower_arm": {"x": -45, "y": 0, "z": 0},
        "right_lower_arm": {"x": -45, "y": 0, "z": 0},
    },
    "tired": {
        "head": {"x": -15, "y": 0, "z": 5},
        "neck": {"x": -10, "y": 0, "z": 0},
        "upper_chest": {"x": -10, "y": 0, "z": 0},
        "left_upper_arm": {"x": 15, "y": -5, "z": 0},
        "right_upper_arm": {"x": 15, "y": 5, "z": 0},
    },
    "attentive_listen": {
        "head": {"x": -5, "y": 0, "z": 0},
        "neck": {"x": -3, "y": 0, "z": 0},
    },
    "celebrate": {
        "head": {"x": 10, "y": 0, "z": 0},
        "left_upper_arm": {"x": -90, "y": -30, "z": 0},
        "right_upper_arm": {"x": -90, "y": 30, "z": 0},
        "left_lower_arm": {"x": -90, "y": 0, "z": 0},
        "right_lower_arm": {"x": -90, "y": 0, "z": 0},
    },
    "apologetic": {
        "head": {"x": -25, "y": -5, "z": 0},
        "neck": {"x": -20, "y": 0, "z": 0},
        "upper_chest": {"x": -15, "y": 0, "z": 0},
        "left_upper_arm": {"x": 30, "y": -10, "z": 0},
        "right_upper_arm": {"x": 30, "y": 10, "z": 0},
    },
    "present": {
        "head": {"x": -5, "y": 0, "z": 0},
        "neck": {"x": -3, "y": 0, "z": 0},
        "right_upper_arm": {"x": -30, "y": -20, "z": 10},
        "right_lower_arm": {"x": -20, "y": 0, "z": 0},
    },
    "idle": {
        "head": {"x": 0, "y": 0, "z": 0},
    },
}


class VrmRenderer(BaseRenderer):
    body_type = "vrm_humanoid"
    hardware_connected = False
    capabilities = [
        RendererCapability.HUMANOID_FULL,
        RendererCapability.HEAD_PITCH,
        RendererCapability.HEAD_YAW,
        RendererCapability.HEAD_ROLL,
        RendererCapability.ARMS,
        RendererCapability.GAZE,
        RendererCapability.IDLE_BREATHING,
    ]

    def __init__(self):
        self._poses = _VRM_POSES

    def status(self) -> str:
        return "available (no hardware — preview only)"

    def can_express(self, token: IntentToken) -> bool:
        return token in self._poses

    async def stop(self) -> dict:
        return {"success": True, "renderer": "vrm", "action": "reset_to_neutral"}

    async def render(
        self, token: IntentToken, params: MotionParams | None = None, target: dict | None = None
    ) -> dict:
        pose = self._poses.get(token.value)
        if not pose:
            return {
                "success": False,
                "error": f"no VRM pose for {token.value}",
                "token": token.value,
            }
        return {
            "success": True,
            "token": token.value,
            "renderer": "vrm",
            "pose": pose,
            "params": params.model_dump() if params else None,
            "bone_count": len(pose),
        }

    def describe(self) -> dict:
        d = super().describe()
        d["pose_count"] = len(self._poses)
        d["poses"] = {
            k: {"bone_count": len(v), "bones": list(v.keys())} for k, v in self._poses.items()
        }
        return d


_VRM_POSE_JSON = json.dumps(_VRM_POSES, indent=2)
