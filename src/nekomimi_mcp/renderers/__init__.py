from nekomimi_mcp.renderers.base import BaseRenderer, RendererCapability
from nekomimi_mcp.renderers.bhl import BHLRenderer
from nekomimi_mcp.renderers.boomy import BoomyRenderer
from nekomimi_mcp.renderers.reachy_mini import ReachyMiniRenderer
from nekomimi_mcp.renderers.vrm import VrmRenderer

RENDERER_REGISTRY: dict[str, BaseRenderer] = {}


def register_renderer(name: str, renderer: BaseRenderer) -> None:
    RENDERER_REGISTRY[name] = renderer


def get_renderer(name: str) -> BaseRenderer | None:
    return RENDERER_REGISTRY.get(name)


def list_renderers() -> list[dict]:
    return [
        {
            "name": name,
            "status": r.status(),
            "body_type": r.body_type,
            "capabilities": [c.value for c in r.capabilities],
        }
        for name, r in RENDERER_REGISTRY.items()
    ]


# Auto-register on import
register_renderer("boomy", BoomyRenderer())
register_renderer("vrm", VrmRenderer())
register_renderer("reachy_mini", ReachyMiniRenderer())
register_renderer("bhl", BHLRenderer())

__all__ = [
    "BaseRenderer",
    "RendererCapability",
    "BoomyRenderer",
    "VrmRenderer",
    "ReachyMiniRenderer",
    "BHLRenderer",
    "RENDERER_REGISTRY",
    "register_renderer",
    "get_renderer",
    "list_renderers",
]
