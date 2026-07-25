"""Renderer registry — manage substrate backends."""

import logging
from collections.abc import Awaitable, Callable

from nekomimi_mcp.intent.tokens import IntentFrame, PhysicalityTier
from nekomimi_mcp.renderers.base import Renderer

logger = logging.getLogger(__name__)

OnIntentCallback = Callable[[IntentFrame], Awaitable[None]]

_TIER_ORDER = [PhysicalityTier.physical, PhysicalityTier.animated, PhysicalityTier.magical]


class RendererRegistry:
    """Holds all registered renderers and dispatches frames to matching ones."""

    def __init__(self):
        self._renderers: dict[str, Renderer] = {}
        self._on_intent: list[OnIntentCallback] = []

    def register(self, renderer: Renderer) -> None:
        self._renderers[renderer.name] = renderer
        logger.info("Renderer registered: %s (tier=%s)", renderer.name, renderer.physicality_tier)

    def unregister(self, name: str) -> None:
        self._renderers.pop(name, None)
        logger.info("Renderer unregistered: %s", name)

    def get(self, name: str) -> Renderer | None:
        return self._renderers.get(name)

    def list(self) -> list[dict]:
        return [
            {
                "name": r.name,
                "tier": r.physicality_tier.value,
                "supported_tokens": sorted(t.value for t in r.supported_tokens),
            }
            for r in self._renderers.values()
        ]

    def list_by_tier(self, tier: PhysicalityTier) -> list[dict]:
        tier_idx = _TIER_ORDER.index(tier)
        return [
            {
                "name": r.name,
                "tier": r.physicality_tier.value,
                "token_count": len(r.supported_tokens),
            }
            for r in self._renderers.values()
            if _TIER_ORDER.index(r.physicality_tier) >= tier_idx
        ]

    async def dispatch(self, frame: IntentFrame, target: str | None = None) -> list[dict]:
        results = []
        renderers = (
            [self._renderers[t]]
            if target and (t := self._renderers.get(target))
            else list(self._renderers.values())
        )
        for renderer in renderers:
            # Tier check: skip renderers that can't handle this physicality tier
            if _TIER_ORDER.index(renderer.physicality_tier) < _TIER_ORDER.index(frame.physicality):
                results.append(
                    {
                        "renderer": renderer.name,
                        "status": "tier_too_low",
                        "renderer_tier": renderer.physicality_tier.value,
                        "required_tier": frame.physicality.value,
                    }
                )
                continue
            if frame.token not in renderer.supported_tokens:
                results.append({"renderer": renderer.name, "status": "unsupported"})
                continue
            try:
                msg = await renderer.execute(frame)
                results.append({"renderer": renderer.name, "status": "ok", "message": msg})
            except Exception as e:
                logger.exception("Renderer %s failed on %s", renderer.name, frame.token)
                results.append({"renderer": renderer.name, "status": "error", "error": str(e)})
        for cb in self._on_intent:
            try:
                await cb(frame)
            except Exception:
                logger.exception("Intent callback failed")
        return results

    def on_intent(self, cb: OnIntentCallback) -> None:
        self._on_intent.append(cb)

    async def stop_all(self) -> None:
        for renderer in self._renderers.values():
            try:
                await renderer.stop()
            except Exception:
                logger.exception("Failed to stop renderer %s", renderer.name)
