"""Drive-base geometry guard.

Boomy can drive backward (retreat, sulk, bow) which on a desk
surface means a fall risk. This module checks LIDAR data via
yahboom-mcp before permitting backward motion.
"""

import logging

logger = logging.getLogger(__name__)

# Minimum clear space behind the robot in metres
MIN_REAR_CLEARANCE_M = 0.3


class SafetyVerdict:
    """Result of a geometry safety check."""

    def __init__(self, safe: bool, reason: str = ""):
        self.safe = safe
        self.reason = reason

    def __bool__(self) -> bool:
        return self.safe


async def check_retreat_path(lidar_data: dict | None) -> SafetyVerdict:
    """Check if there is enough clear space behind Boomy to retreat.

    Uses yahboom-mcp LIDAR sector data. The rear sectors are:
    back_left, back, back_right.

    If LIDAR is unavailable (no data, robot offline), defaults to
    SAFE = False with a reason. No data = no movement.
    """
    if lidar_data is None:
        return SafetyVerdict(False, "No LIDAR data — cannot verify clear path")

    rear_sectors = ["back_left", "back", "back_right"]
    for sector in rear_sectors:
        distance = lidar_data.get(sector)
        if distance is None:
            return SafetyVerdict(False, f"Missing LIDAR sector: {sector}")
        if distance < MIN_REAR_CLEARANCE_M:
            return SafetyVerdict(
                False,
                f"{sector}: {distance:.2f}m < {MIN_REAR_CLEARANCE_M}m minimum",
            )

    return SafetyVerdict(True, "Path clear")


def cower_substitute() -> dict:
    """Fallback when retreat is blocked: cower in place.

    Returns a set of substitute actions instead of driving:
    - Camera tilt full down
    - LEDs dim blue
    - Display sad face
    - Audio crouch/threat sound (if available)
    """
    return {
        "actions": [
            {"tool": "camera_set_pos", "params": {"pan": 90, "tilt": 150}},
            {"tool": "led", "params": [10, 5, 20]},
        ],
        "note": "Cower in place — retreat blocked by obstacle",
    }
