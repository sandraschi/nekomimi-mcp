"""Resonite renderer - delegates to resonite-mcp via HTTP.

STUB STATUS: This renderer has the interface defined but the
actual calls to resonite-mcp are not yet implemented. The
resonite-mcp HTTP API surface needs to be mapped first.
"""

import logging

from nekomimi_mcp.intent.tokens import IntentFrame, IntentToken, PhysicalityTier
from nekomimi_mcp.renderers.base import Renderer

logger = logging.getLogger(__name__)


class ResoniteRenderer(Renderer):
    """STUB - delegates intent tokens to resonite-mcp for VRM avatar in Resonite.

    Will translate intent tokens to VRM bone poses via the Resonite
    avatar's constraint system. Resonite avatars use VRM 1.0 compatible
    bone mappings when using the VRM avatar import path.
    """

    def __init__(self):
        self._connected = False

    @property
    def name(self) -> str:
        return "resonite"

    @property
    def physicality_tier(self) -> PhysicalityTier:
        return PhysicalityTier.animated

    @property
    def supported_tokens(self) -> set[IntentToken]:
        return set(IntentToken)

    async def execute(self, frame: IntentFrame) -> str:
        logger.warning("ResoniteRenderer.execute: STUB - no resonite-mcp calls implemented")
        return f"STUB: would execute {frame.token.value} on Resonite avatar"

    async def status(self) -> dict:
        return {
            "name": self.name,
            "connected": self._connected,
            "tokens": len(self.supported_tokens),
            "stub": True,
            "note": "STUB - implement HTTP calls to resonite-mcp",
        }

    async def stop(self) -> None:
        logger.warning("ResoniteRenderer.stop: STUB")

    async def idle(self) -> None:
        logger.warning("ResoniteRenderer.idle: STUB")
