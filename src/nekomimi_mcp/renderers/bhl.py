from __future__ import annotations

from nekomimi_mcp.intent.schema import IntentToken, MotionParams
from nekomimi_mcp.renderers.base import BaseRenderer, RendererCapability

# BHL arm joint target positions (degrees) for each intent.
# Joints: shoulder_pitch/roll/yaw, elbow_pitch/yaw (5 per arm)
# Legs not specified here - gait is controlled separately.

_BHL_ARM_POSES: dict[str, dict] = {
    "attending": {
        "left_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
    },
    "confused": {
        "left_arm": {
            "shoulder_pitch": -30,
            "shoulder_roll": 20,
            "shoulder_yaw": 0,
            "elbow_pitch": -45,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": -5,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
    },
    "sulk": {
        "left_arm": {
            "shoulder_pitch": 30,
            "shoulder_roll": 15,
            "shoulder_yaw": 0,
            "elbow_pitch": -90,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": 30,
            "shoulder_roll": -15,
            "shoulder_yaw": 0,
            "elbow_pitch": -90,
            "elbow_yaw": 0,
        },
    },
    "surprised": {
        "left_arm": {
            "shoulder_pitch": -45,
            "shoulder_roll": -10,
            "shoulder_yaw": 0,
            "elbow_pitch": -30,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -45,
            "shoulder_roll": 10,
            "shoulder_yaw": 0,
            "elbow_pitch": -30,
            "elbow_yaw": 0,
        },
    },
    "excited": {
        "left_arm": {
            "shoulder_pitch": -80,
            "shoulder_roll": -10,
            "shoulder_yaw": 0,
            "elbow_pitch": -45,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -80,
            "shoulder_roll": 10,
            "shoulder_yaw": 0,
            "elbow_pitch": -45,
            "elbow_yaw": 0,
        },
    },
    "celebrate": {
        "left_arm": {
            "shoulder_pitch": -90,
            "shoulder_roll": -30,
            "shoulder_yaw": 0,
            "elbow_pitch": -90,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -90,
            "shoulder_roll": 30,
            "shoulder_yaw": 0,
            "elbow_pitch": -90,
            "elbow_yaw": 0,
        },
    },
    "present": {
        "left_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -30,
            "shoulder_roll": -20,
            "shoulder_yaw": 10,
            "elbow_pitch": -20,
            "elbow_yaw": 0,
        },
    },
    "apologetic": {
        "left_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": 0,
            "elbow_yaw": 0,
        },
    },
    "tired": {
        "left_arm": {
            "shoulder_pitch": 15,
            "shoulder_roll": -5,
            "shoulder_yaw": 0,
            "elbow_pitch": -30,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": 15,
            "shoulder_roll": 5,
            "shoulder_yaw": 0,
            "elbow_pitch": -30,
            "elbow_yaw": 0,
        },
    },
    "idle": {
        "left_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": -5,
            "elbow_yaw": 0,
        },
        "right_arm": {
            "shoulder_pitch": -10,
            "shoulder_roll": 0,
            "shoulder_yaw": 0,
            "elbow_pitch": -5,
            "elbow_yaw": 0,
        },
    },
}


class BHLRenderer(BaseRenderer):
    body_type = "humanoid_biped"
    hardware_connected = False
    capabilities = [
        RendererCapability.HUMAN_LEGS,
        RendererCapability.ARMS,
        RendererCapability.HUMANOID_FULL,
    ]

    def status(self) -> str:
        return "STUB - requires BHL hardware or Isaac Lab sim"

    def can_express(self, token: IntentToken) -> bool:
        return token.value in _BHL_ARM_POSES

    async def stop(self) -> dict:
        return {"success": True, "renderer": "bhl", "action": "all_zero"}

    async def render(
        self, token: IntentToken, params: MotionParams | None = None, target: dict | None = None
    ) -> dict:
        pose = _BHL_ARM_POSES.get(token.value)
        if not pose:
            return {
                "success": False,
                "error": f"no BHL pose for {token.value}",
                "token": token.value,
            }
        return {
            "success": True,
            "token": token.value,
            "renderer": "bhl",
            "joint_targets": pose,
            "params": params.model_dump() if params else None,
            "joint_count": sum(len(v) for v in pose.values()),
            "simulated": True,
            "note": "STUB - requires BHL hardware or Isaac Lab sim. No neck/face expression available.",
        }
