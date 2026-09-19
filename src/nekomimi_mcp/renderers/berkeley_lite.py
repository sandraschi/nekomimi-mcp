"""Berkeley Humanoid Lite renderer - SCHEMATIC STUB.

STUB STATUS: No hardware. Sim-only path exists (Isaac Lab + MuJoCo).
This renderer will call the Berkeley Lite UDP interface once available.

Berkeley Lite (biped, 12 DOF) constraints:
  - NO HEAD, NO FACE, NO VOICE, NO ARMS
  - Legs only - all expression is gait modulation
  - Control via UDP position targets at ~50 Hz
  - Sim: Isaac Lab 2.1.0 + MuJoCo sim2sim

The extreme constraint (legs-only expression) makes this the hardest
retargeting problem. Intent is expressed through:
  - Posture (crouch, sway, shift weight)
  - Gait (hop, bounce, step back)
  - Speed and acceleration profile
"""

import logging

from nekomimi_mcp.intent.tokens import IntentFrame, IntentToken, PhysicalityTier
from nekomimi_mcp.renderers.base import Renderer

logger = logging.getLogger(__name__)


class BerkeleyLiteRenderer(Renderer):
    """SCHEMATIC STUB - intent mapping for Berkeley Humanoid Lite (biped).

    All 12 DOF are leg joints. No upper body expression possible.
    """

    def __init__(self):
        self._available = False

    @property
    def name(self) -> str:
        return "berkeley_lite"

    @property
    def physicality_tier(self) -> PhysicalityTier:
        return PhysicalityTier.physical

    @property
    def supported_tokens(self) -> set[IntentToken]:
        return set(IntentToken)

    async def execute(self, frame: IntentFrame) -> str:
        return (
            f"STUB (Berkeley Lite): would map {frame.token.value} → "
            f"gait modulation (12 leg joints). "
            f"Sim-only: Isaac Lab 2.1.0 + MuJoCo. No hardware acquired."
        )

    async def status(self) -> dict:
        return {
            "name": self.name,
            "connected": self._available,
            "tokens": len(self.supported_tokens),
            "stub": True,
            "note": "SCHEMATIC STUB - implement UDP position streaming when hardware acquired",
        }

    async def stop(self) -> None:
        pass

    async def idle(self) -> None:
        pass
