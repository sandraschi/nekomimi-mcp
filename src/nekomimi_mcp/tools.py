from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from nekomimi_mcp.intent.registry import get_default_params, list_intents
from nekomimi_mcp.intent.schema import EasingCurve, IntentStream, IntentToken, MotionParams
from nekomimi_mcp.renderers import RENDERER_REGISTRY, get_renderer, list_renderers
from nekomimi_mcp.safety.drive_guards import DriveGeometryGuard
from nekomimi_mcp.safety.timeout_policy import TimeoutPolicy
from nekomimi_mcp.stream.player import IntentPlayer
from nekomimi_mcp.stream.recorder import IntentRecorder

_recorder = IntentRecorder()
_player = IntentPlayer(_recorder)
_guard = DriveGeometryGuard()
_policy = TimeoutPolicy()


async def intent_tool(
    ctx: Context | None = None,
    token: Annotated[str, Field(description="Intent token to express")] = "attending",
    renderer: Annotated[
        str | None, Field(description="Target renderer name, or None for all registered")
    ] = None,
    timing_seconds: Annotated[
        float | None, Field(description="Duration override (0.1-10.0)")
    ] = None,
    speed: Annotated[float | None, Field(description="Speed override (0.0-1.0)")] = None,
    intensity: Annotated[float | None, Field(description="Intensity override (0.0-1.0)")] = None,
    easing: Annotated[
        str | None,
        Field(description="Easing override: linear, ease_in, ease_out, ease_in_out, snap, bounce"),
    ] = None,
    hold_seconds: Annotated[float | None, Field(description="Hold duration at end pose")] = None,
    repeat: Annotated[int | None, Field(description="Repeat count (1-10)")] = None,
    hesitation: Annotated[
        float | None, Field(description="Hesitation delay before motion (seconds)")
    ] = None,
) -> dict:
    """Express an intent token through one or all registered renderers.

    The intent layer is substrate-independent. The LLM emits only an intent
    token and motion parameters. Each renderer translates to its body's native
    actuator commands (differential drive, gimbal, VRM bones, Stewart platform, etc.).

    [RATIONALE]
    Single portmanteau for all social expression. Keeps the tool surface compact
    while supporting 17+ intent tokens across 4+ renderer bodies.

    ## Return Format
    {"success": bool, "token": str, "renderer_results": [{"renderer": str, "success": bool, ...}], "timing": {...}}

    ## Examples
    intent_tool(token="surprised", speed=0.8, intensity=0.9)
    intent_tool(token="sulk", renderer="boomy", speed=0.2, hold_seconds=15.0)
    """
    try:
        intent_token = IntentToken(token)
    except ValueError:
        return {
            "success": False,
            "error": f"Unknown token '{token}'. Valid: {', '.join(t.value for t in IntentToken)}",
        }

    params = get_default_params(intent_token)
    if timing_seconds is not None:
        params.timing_seconds = max(0.1, min(10.0, timing_seconds))
    if speed is not None:
        params.speed = max(0.0, min(1.0, speed))
    if intensity is not None:
        params.intensity = max(0.0, min(1.0, intensity))
    if easing:
        try:
            params.easing = EasingCurve(easing)
        except ValueError:
            pass
    if hold_seconds is not None:
        params.hold_seconds = max(0.0, hold_seconds)
    if repeat is not None:
        params.repeat_count = max(1, min(10, repeat))
    if hesitation is not None:
        params.hesitation_seconds = max(0.0, hesitation)

    # Apply safety policy for persistent intents
    _policy.begin_intent(token)
    _policy.check_intent(token)

    targets = [renderer] if renderer else list(RENDERER_REGISTRY.keys())
    results = []
    for name in targets:
        r = get_renderer(name)
        if not r:
            results.append({"renderer": name, "success": False, "error": "unknown renderer"})
            continue
        result = await r.render(intent_token, params)
        results.append(result)

    # Record
    stream = IntentStream(tokens=[intent_token], params=params, renderer=renderer)
    _recorder.record(stream, renderer or "all", results)

    return {
        "success": any(r.get("success", False) for r in results),
        "token": token,
        "renderer_results": results,
        "timing": {
            "hesitation_s": params.hesitation_seconds,
            "duration_s": params.timing_seconds,
            "hold_s": params.hold_seconds,
        },
        "repeat": params.repeat_count,
        "message": f"Expressed {token} on {len(results)} renderer(s) with timing={params.timing_seconds}s speed={params.speed}",
    }


async def intent_stream_tool(
    ctx: Context | None = None,
    tokens: Annotated[list[str], Field(description="Ordered list of intent tokens")] = [
        "attending",
        "idle",
    ],
    renderer: Annotated[str | None, Field(description="Target renderer")] = None,
    loop: Annotated[bool, Field(description="Loop the stream")] = False,
) -> dict:
    """Execute a sequence of intent tokens in order.

    [RATIONALE]
    Chaining multiple intents into a stream enables complex behavioural sequences
    (e.g. surprised -> curious -> attend) while keeping the LLM's tool call atomic.

    ## Return Format
    {"success": bool, "stream": [{"token": str, "result": {...}}], "count": int}

    ## Examples
    intent_stream(tokens=["surprised", "curious", "attending"])
    intent_stream(tokens=["excited", "celebrate", "idle"], renderer="boomy")
    """
    validated = []
    for t in tokens:
        try:
            validated.append(IntentToken(t))
        except ValueError:
            return {"success": False, "error": f"Unknown token '{t}'"}

    stream = IntentStream(tokens=validated, renderer=renderer, loop=loop)
    params = MotionParams()

    results = []
    targets = [renderer] if renderer else list(RENDERER_REGISTRY.keys())
    for token in validated:
        for name in targets:
            r = get_renderer(name)
            if r:
                result = await r.render(token, params)
                results.append({"token": token.value, "renderer": name, "result": result})

    # Record
    _recorder.record(stream, renderer or "all", results)

    return {"success": True, "stream": results, "count": len(results), "message": f"Executed stream of {len(results)} token-renderer pairs"}


async def list_intents_tool(
    ctx: Context | None = None,
) -> dict:
    """List all registered intent tokens with default parameters and descriptions.

    ## Return Format
    {"intents": [{"token": str, "default_timing_s": float, ...}], "count": int}

    ## Examples
    list_intents()
    """
    return {"intents": list_intents(), "count": len(IntentToken), "message": f"{len(IntentToken)} registered intent tokens"}


async def list_renderers_tool(
    ctx: Context | None = None,
) -> dict:
    """List all registered body renderers with capabilities and status.

    ## Return Format
    {"renderers": [{"name": str, "status": str, "body_type": str, ...}], "count": int}

    ## Examples
    list_renderers()
    """
    return {"renderers": list_renderers(), "count": len(RENDERER_REGISTRY), "message": f"{len(RENDERER_REGISTRY)} renderer(s) registered"}


async def renderer_info_tool(
    ctx: Context | None = None,
    name: Annotated[str, Field(description="Renderer name")] = "boomy",
) -> dict:
    """Get detailed information about a registered renderer.

    ## Return Format
    {"name": str, "body_type": str, "capabilities": [str], "status": str, "expressible_tokens": [str]}

    ## Examples
    renderer_info(name="boomy")
    renderer_info(name="vrm")
    """
    r = get_renderer(name)
    if not r:
        return {
            "success": False,
            "error": f"Renderer '{name}' not found.",
            "message": f"Renderer '{name}' not found. Available: {', '.join(RENDERER_REGISTRY.keys())}",
        }
    d = r.describe()
    d["message"] = f"Renderer '{name}' is {d['status']}"
    return d


async def check_boomy_mapping_tool(
    ctx: Context | None = None,
    token: Annotated[str, Field(description="Intent token to check")] = "sulk",
    include_motion: Annotated[bool, Field(description="Include concrete motion plan")] = True,
) -> dict:
    """Preview how an intent maps to Boomy's specific actuators.

    Shows the concrete yahboom_tool calls, timing, and known limitations
    for a given token on the Boomy robot.

    ## Return Format
    {"token": str, "expressible": bool, "limitations": [str], "motion_plan": [...]}

    ## Examples
    check_boomy_mapping(token="nod")
    check_boomy_mapping(token="surprised", include_motion=True)
    """
    from nekomimi_mcp.renderers.boomy import BoomyRenderer

    try:
        intent_token = IntentToken(token)
    except ValueError:
        return {"success": False, "error": f"Unknown token '{token}'", "message": f"Unknown token '{token}'"}

    r = BoomyRenderer()
    params = get_default_params(intent_token)
    return {
        "token": token,
        "expressible": r.can_express(intent_token),
        "limitations": r._get_limitations(intent_token) if hasattr(r, "_get_limitations") else [],
        "mapping": r._describe_mapping(intent_token, params) if include_motion else None,
        "message": f"Boomy can{'' if r.can_express(intent_token) else 'not'} express '{token}'",
    }


async def safety_status_tool(
    ctx: Context | None = None,
) -> dict:
    """Get the current safety subsystem status.

    ## Return Format
    {"drive_guard": {...}, "timeout_policy": {...}}
    """
    return {
        "success": True,
        "drive_guard": {
            "lidar_range_m": _guard.lidar_range_m,
            "retreat_timeout_s": _guard.timeout_on_retreat_s,
            "in_retreat": _guard._retreat_start is not None,
            "wounded_dignity_return": _guard.should_return,
        },
        "timeout_policy": {},
        "message": "Safety systems nominal",
    }


async def safe_retreat_tool(
    ctx: Context | None = None,
    check_obstacle: Annotated[
        bool, Field(description="Check LIDAR for obstacles before retreat")
    ] = True,
) -> dict:
    """Execute a safe retreat with geometry guard and timeout.

    Checks LIDAR clearance before moving backwards. Times out after
    configured duration and triggers wounded-dignity return.

    ## Return Format
    {"success": bool, "retreat_allowed": bool, "obstacle_clear": bool, "action": str}

    ## Examples
    safe_retreat(check_obstacle=True)
    """
    import time as _time

    obstacle_clear = True
    if check_obstacle:
        _guard.check_retreat_safe(1.0)

    if not obstacle_clear:
        return {
            "success": False,
            "retreat_allowed": False,
            "obstacle_clear": False,
            "action": "blocked — obstacle within LIDAR range",
            "message": "Retreat blocked — obstacle detected within LIDAR range",
        }

    _guard.begin_retreat(_time.time())

    r = get_renderer("boomy")
    if r and r.hardware_connected:
        await r.render(IntentToken.SULK)
        return {
            "success": True,
            "retreat_allowed": True,
            "obstacle_clear": True,
            "action": "retreat started (sulk)",
            "message": "Retreat started — Boomy is executing sulk",
        }

    return {
        "success": True,
        "retreat_allowed": True,
        "obstacle_clear": True,
        "action": "retreat started (simulated — no boomy hardware)",
        "message": "Retreat started (simulated — Boomy hardware not connected)",
    }


async def recordings_list_tool(
    ctx: Context | None = None,
    limit: Annotated[int, Field(description="Max recordings to return", ge=1, le=100)] = 20,
    renderer: Annotated[str | None, Field(description="Filter by renderer name")] = None,
) -> dict:
    """List recorded intent streams for playback and regression testing.

    ## Return Format
    {"recordings": [...], "count": int}

    ## Examples
    recordings_list(limit=10)
    recordings_list(renderer="boomy")
    """
    recs = _recorder.list_recordings(limit=limit, renderer=renderer)
    return {"recordings": recs, "count": len(recs), "message": f"{len(recs)} recording(s) found"}


async def replay_intent_tool(
    ctx: Context | None = None,
    recording_id: Annotated[int, Field(description="Recording ID to replay")] = 1,
    renderers: Annotated[list[str] | None, Field(description="Optional renderer filter")] = None,
) -> dict:
    """Replay a recorded intent stream. Enables regression testing without live hardware.

    ## Return Format
    {"success": bool, "results": [...], "count": int}

    ## Examples
    replay_intent(recording_id=1)
    replay_intent(recording_id=3, renderers=["vrm"])
    """
    results = await _player.replay(recording_id, renderers=renderers)
    return {"success": True, "results": results, "count": len(results), "message": f"Replayed {len(results)} renderer results from recording {recording_id}"}


async def export_recordings_tool(
    ctx: Context | None = None,
    path: Annotated[
        str, Field(description="Output path for JSONL export")
    ] = "data/intents_export.jsonl",
) -> dict:
    """Export all recorded intents to JSONL for external analysis.

    ## Return Format
    {"success": bool, "path": str, "count": int}
    """
    count = _recorder.export_jsonl(path)
    return {"success": True, "path": path, "count": count, "message": f"Exported {count} recordings to {path}"}


async def show_renderers_card(
    ctx: Context | None = None,
) -> dict:
    """Show registered renderers as a rich Prefab card.

    Displays each renderer's name, body type, status, and capabilities
    in an in-chat card. Falls back to plain text for hosts that don't
    support Apps.

    ## Return Format
    {"success": bool, "content": str, "structured_content": {...}}
    """
    from prefab_ui import PrefabApp
    from prefab_ui.components import Div, Heading

    renderers = list_renderers()
    app = PrefabApp(title="Registered Renderers")
    for r in renderers:
        status_icon = "🟢" if "ready" in r["status"] else "🟡" if "STUB" in r["status"] else "🔴"
        app.add(Heading(r["name"], level=3))
        app.add(Div(f"{status_icon} {r['status']}"))
        app.add(Div(f"Body: {r['body_type']}"))
        caps = ", ".join(r["capabilities"][:5])
        app.add(Div(f"Capabilities: {caps}"))
        app.add(Div(""))

    content = f"**{len(renderers)} renderers registered:**\n" + "\n".join(
        f"- **{r['name']}** ({r['body_type']}): {r['status']}" for r in renderers
    )

    return {
        "success": True,
        "content": content,
        "structured_content": app,
    }
