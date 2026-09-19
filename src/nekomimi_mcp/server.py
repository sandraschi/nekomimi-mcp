from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

from nekomimi_mcp.prompts import register_prompts
from nekomimi_mcp.tools import (
    OUTPUT_SCHEMAS,
    PRIMARY_TOOL_NAMES,
    check_boomy_mapping_tool,
    export_recordings_tool,
    intent_stream_tool,
    intent_tool,
    list_intents_tool,
    list_renderers_tool,
    recordings_list_tool,
    renderer_info_tool,
    replay_intent_tool,
    safe_retreat_tool,
    safety_status_tool,
    show_renderers_card,
    show_safety_card,
    show_status_card,
    shutdown_tool,
    status_tool,
)

logger = logging.getLogger("nekomimi-mcp")

MCP_PORT = int(os.environ.get("NEKOMIMI_PORT", os.environ.get("PORT", "11128")))

mcp = FastMCP(
    name="nekomimi-mcp",
    version="0.1.0",
)


_READ_ONLY = {"readOnlyHint": True}
_MUTATING = {"readOnlyHint": False}

_REGISTERED_TOOLS: list[tuple] = [
    (intent_tool, _MUTATING, {}),
    (intent_stream_tool, _MUTATING, {}),
    (list_intents_tool, _READ_ONLY, {}),
    (list_renderers_tool, _READ_ONLY, {}),
    (renderer_info_tool, _READ_ONLY, {}),
    (check_boomy_mapping_tool, _READ_ONLY, {}),
    (safety_status_tool, _READ_ONLY, {}),
    (safe_retreat_tool, _MUTATING, {}),
    (recordings_list_tool, _READ_ONLY, {}),
    (replay_intent_tool, _MUTATING, {}),
    (export_recordings_tool, _MUTATING, {}),
    (status_tool, _READ_ONLY, {}),
    (shutdown_tool, _MUTATING, {}),
    (show_renderers_card, {}, {"app": True}),
    (show_status_card, {}, {"app": True}),
    (show_safety_card, {}, {"app": True}),
]


def primary_name(fn) -> str:
    return PRIMARY_TOOL_NAMES.get(fn.__name__) or fn.__name__


def tool_names() -> list[str]:
    """Canonical verb-led tool names (what clients should call)."""
    return [primary_name(fn) for fn, _, _ in _REGISTERED_TOOLS]


def tool_aliases() -> list[str]:
    """Deprecated historic names, still registered for compatibility."""
    return [fn.__name__ for fn, _, _ in _REGISTERED_TOOLS if fn.__name__ in PRIMARY_TOOL_NAMES]


def register_tools() -> None:
    for fn, annot, extra in _REGISTERED_TOOLS:
        primary = primary_name(fn)
        schema = OUTPUT_SCHEMAS.get(fn.__name__)
        if extra.get("app"):
            mcp.tool(name=primary, app=True)(fn)
        else:
            kwargs: dict = {"annotations": annot}
            if schema:
                kwargs["output_schema"] = schema
            mcp.tool(name=primary, **kwargs)(fn)
        if fn.__name__ in PRIMARY_TOOL_NAMES:
            alias_kwargs: dict = {
                "annotations": annot,
                "description": (
                    f"Deprecated alias of {primary}. Use {primary} instead. "
                    f"{(fn.__doc__ or '').strip().splitlines()[0] if fn.__doc__ else ''}"
                ),
            }
            if schema:
                alias_kwargs["output_schema"] = schema
            mcp.tool(name=fn.__name__, **alias_kwargs)(fn)


def register_resources() -> None:
    """Expose skills as skill:// MCP resources (no SkillsDirectoryProvider in FastMCP 3.4)."""
    from pathlib import Path

    skills_dir = Path(__file__).resolve().parent / "skills"

    def _skill_reader(skill_name: str) -> str:
        doc = skills_dir / skill_name / "SKILL.md"
        if not doc.exists():
            raise FileNotFoundError(f"Skill '{skill_name}' not found")
        return doc.read_text(encoding="utf-8")

    if (skills_dir / "nekomimi-operator" / "SKILL.md").exists():

        def nekomimi_operator_skill() -> str:
            """Operator skill: intent vocabulary, motion params, body limits, best practice."""
            return _skill_reader("nekomimi-operator")

        mcp.resource(
            "skill://nekomimi-operator",
            name="nekomimi-operator",
            description="Operator skill for the nekomimi embodiment layer",
            mime_type="text/markdown",
        )(nekomimi_operator_skill)


def _gpu_info() -> dict:
    """Best-effort GPU detection for local-LLM sizing (torch, then nvidia-smi)."""
    import importlib.util
    import shutil
    import subprocess

    if importlib.util.find_spec("torch") is not None:
        try:
            torch = importlib.import_module("torch")
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                return {
                    "detected": True,
                    "source": "torch.cuda",
                    "name": torch.cuda.get_device_name(0),
                    "vram_gb": round(props.total_memory / 1e9, 1),
                }
        except Exception:
            pass
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if out.returncode == 0 and out.stdout.strip():
                name, _, _mem = out.stdout.strip().splitlines()[0].partition(",")
                return {"detected": True, "source": "nvidia-smi", "name": name.strip()}
        except Exception:
            pass
    return {"detected": False, "source": "none"}


def _register_rest_routes(app, port: int) -> None:
    """Fleet REST surface: health, status, skills, capabilities, diagnostics, shutdown.

    The webapp and fleet launcher consume these over HTTP; the MCP tools
    remain the primary agent surface on /mcp.
    """
    from pathlib import Path

    from starlette.requests import Request
    from starlette.responses import JSONResponse, PlainTextResponse, Response

    skills_dir = Path(__file__).resolve().parent / "skills"

    async def health(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "server": "nekomimi-mcp", "port": port})

    async def status(_: Request) -> JSONResponse:
        import time

        from nekomimi_mcp import tools as _tools

        uptime_s = time.time() - _tools._STARTED_AT
        return JSONResponse(
            {
                "status": "ok",
                "server": "nekomimi-mcp",
                "version": "0.1.0",
                "uptime_seconds": round(uptime_s, 1),
                "tool_count": len(tool_names()),
                "tools": tool_names(),
                "message": "nekomimi-mcp healthy",
            }
        )

    async def skills(_: Request) -> JSONResponse:
        if skills_dir.exists():
            found = sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").exists())
        else:
            found = []
        return JSONResponse(
            {
                "skills": [{"name": n, "uri": f"skill://{n}"} for n in found],
                "count": len(found),
            }
        )

    async def skill_content(request: Request) -> PlainTextResponse:
        name = request.path_params.get("name", "")
        doc = skills_dir / name / "SKILL.md"
        if not doc.exists():
            return PlainTextResponse(f"Skill '{name}' not found.", status_code=404)
        return PlainTextResponse(doc.read_text(encoding="utf-8"))

    async def capabilities(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "server": "nekomimi-mcp",
                "version": "0.1.0",
                "transports": ["stdio", "http"],
                "tools": tool_names(),
                "aliases": tool_aliases(),
                "prompts": ["nekomimi_intent_guide", "nekomimi_character", "renderer_comparison"],
                "resources": ["skill://nekomimi-operator"],
                "ports": {"backend": port, "frontend": 11129},
                "message": f"{len(tool_names())} tools over stdio + HTTP /mcp",
            }
        )

    async def diagnostics(_: Request) -> JSONResponse:
        import platform

        from nekomimi_mcp.renderers import RENDERER_REGISTRY, get_renderer

        renderers = []
        for name in RENDERER_REGISTRY.keys():
            r = get_renderer(name)
            renderers.append({"name": name, "status": r.status() if r else "missing"})
        return JSONResponse(
            {
                "server": "nekomimi-mcp",
                "version": "0.1.0",
                "python": platform.python_version(),
                "platform": platform.platform(),
                "port": port,
                "tools": tool_names(),
                "aliases": tool_aliases(),
                "renderers": renderers,
                "gpu": _gpu_info(),
                "errors": [],
            }
        )

    async def shutdown(_: Request) -> JSONResponse:
        import os
        import threading

        timer = threading.Timer(0.5, lambda: os._exit(0))
        timer.daemon = True
        timer.start()
        return JSONResponse({"success": True, "message": "nekomimi-mcp shutting down in 0.5s."})

    async def llm_discover(_: Request) -> JSONResponse:
        from nekomimi_mcp import llm as _llm

        providers = await _llm.discover_providers()
        return JSONResponse({"providers": providers, "count": len(providers)})

    async def llm_providers(_: Request) -> JSONResponse:
        from nekomimi_mcp import llm as _llm

        providers = [p for p in await _llm.discover_providers() if p["detected"]]
        return JSONResponse({"providers": providers, "count": len(providers)})

    async def llm_models(request: Request) -> JSONResponse:
        from nekomimi_mcp import llm as _llm

        provider = request.query_params.get("provider", "ollama")
        models = await _llm.list_models(provider)
        return JSONResponse({"provider": provider, "models": models, "count": len(models)})

    async def llm_onboarding(_: Request) -> JSONResponse:
        from nekomimi_mcp import llm as _llm

        return JSONResponse(await _llm.onboarding_status())

    async def llm_chat(request: Request):
        """POST /api/llm/chat — provider chat proxy. {provider, model, messages, stream?}.

        stream=true returns SSE (text/event-stream) proxied from the provider's
        OpenAI-compatible endpoint; otherwise a single JSON reply.
        """
        from starlette.responses import StreamingResponse

        from nekomimi_mcp import llm as _llm

        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"success": False, "error": "invalid JSON body", "message": "Send JSON."},
                status_code=400,
            )
        provider = body.get("provider")
        model = body.get("model")
        messages = body.get("messages", [])
        if not messages:
            return JSONResponse(
                {"success": False, "error": "messages required", "message": "messages required."},
                status_code=400,
            )
        try:
            if not provider or not model:
                discovered = await _llm.discover_providers()
                live = [p for p in discovered if p["detected"]]
                if not live:
                    raise RuntimeError("No local LLM provider detected.")
                provider = provider or live[0]["name"]
                model = model or (live[0]["models"][0] if live[0]["models"] else "")
            if body.get("stream"):
                return StreamingResponse(
                    _llm_chat_sse(provider, model, messages),
                    media_type="text/event-stream",
                )
            text = await _llm.chat_completion(provider, model, messages)
            return JSONResponse(
                {
                    "success": True,
                    "text": text,
                    "provider": provider,
                    "model": model,
                    "message": f"Answered via {provider}/{model}",
                }
            )
        except RuntimeError as e:
            return JSONResponse(
                {"success": False, "error": str(e), "message": str(e)}, status_code=409
            )

    async def chat(request: Request) -> Response:
        """POST /api/chat — skill-first chat with declared local fallback.

        Tries: skill preprompt + live provider. Falls back (mode=local-fallback)
        to the offline intent matcher that also emits the matched intent.
        stream=true returns SSE deltas instead of one JSON reply.
        """
        from starlette.responses import StreamingResponse

        from nekomimi_mcp import llm as _llm
        from nekomimi_mcp.intent.schema import IntentToken
        from nekomimi_mcp.tools import intent_tool

        try:
            body = await request.json()
        except Exception:
            body = {}
        user_text = str(body.get("message", "")).strip()
        history = body.get("history", [])
        if not user_text:
            return JSONResponse(
                {"success": False, "error": "message required", "message": "message required."},
                status_code=400,
            )
        try:
            if body.get("stream"):
                return StreamingResponse(
                    _agent_chat_sse(
                        user_text,
                        history,
                        body.get("provider"),
                        body.get("model"),
                    ),
                    media_type="text/event-stream",
                )
            result = await _llm.agent_chat(
                user_text,
                history=history,
                provider=body.get("provider"),
                model=body.get("model"),
            )
            result["success"] = True
            return JSONResponse(result)
        except RuntimeError:
            pass  # declared fallback below

        lower = user_text.lower()
        matched = next((t for t in IntentToken if t.value in lower), None)
        if matched:
            emitted = await intent_tool(token=matched.value)
            return JSONResponse(
                {
                    "success": True,
                    "mode": "local-fallback",
                    "text": f"Emitted intent **{matched.value}** (offline mode — no LLM provider detected).\n\n{emitted.get('message', '')}",
                    "token": matched.value,
                    "message": f"Emitted {matched.value} via local fallback",
                }
            )
        return JSONResponse(
            {
                "success": True,
                "mode": "local-fallback",
                "text": (
                    "No local LLM provider detected, so I am running on the offline "
                    "intent matcher. Name an intent token (e.g. 'nod', 'curious', "
                    "'celebrate') and I will emit it. Start Ollama or LM Studio for full chat."
                ),
                "message": "Local fallback response",
            }
        )

    async def fleet_apps(_: Request) -> JSONResponse:
        """GET /api/fleet/apps — this app plus companion servers (live-probed, fail-soft)."""
        import httpx

        apps = [
            {
                "name": "nekomimi-mcp",
                "role": "this server — substrate-independent embodiment layer",
                "backend": f"http://127.0.0.1:{port}",
                "frontend": "http://127.0.0.1:11129",
                "status": "online",
            }
        ]
        companions = [
            {
                "name": "yahboom-mcp",
                "role": "Boomy robot hardware bridge (Raspbot V2)",
                "health_url": "http://127.0.0.1:10892/api/v1/health",
                "frontend": "http://127.0.0.1:10893",
            },
            {
                "name": "resonite-mcp",
                "role": "Resonite VRM avatar bridge",
                "health_url": "http://127.0.0.1:10979/health",
                "frontend": "http://127.0.0.1:10978",
            },
        ]
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                for c in companions:
                    try:
                        r = await client.get(c["health_url"])
                        status = "online" if r.status_code == 200 else f"http-{r.status_code}"
                    except Exception:
                        status = "offline"
                    apps.append(
                        {
                            "name": c["name"],
                            "role": c["role"],
                            "backend": c["health_url"],
                            "frontend": c["frontend"],
                            "status": status,
                        }
                    )
        except Exception:
            pass
        return JSONResponse({"apps": apps, "count": len(apps)})

    app.add_route("/health", health, methods=["GET"])
    app.add_route("/api/status", status, methods=["GET"])
    app.add_route("/api/skills", skills, methods=["GET"])
    app.add_route("/api/skills/{name}", skill_content, methods=["GET"])
    app.add_route("/api/capabilities", capabilities, methods=["GET"])
    app.add_route("/api/v1/diagnostics", diagnostics, methods=["GET"])
    app.add_route("/api/shutdown", shutdown, methods=["POST"])
    app.add_route("/api/llm/discover", llm_discover, methods=["GET"])
    app.add_route("/api/llm/providers", llm_providers, methods=["GET"])
    app.add_route("/api/llm/models", llm_models, methods=["GET"])
    app.add_route("/api/llm/onboarding", llm_onboarding, methods=["GET"])
    app.add_route("/api/llm/chat", llm_chat, methods=["POST"])
    app.add_route("/api/chat", chat, methods=["POST"])
    app.add_route("/api/fleet/apps", fleet_apps, methods=["GET"])


async def _agent_chat_sse(
    user_text: str, history: list[dict], provider: str | None, model: str | None
):
    """SSE deltas for skill-first chat. Emits one error event when no provider is live."""
    import json

    from nekomimi_mcp import llm as _llm

    try:
        discovered = await _llm.discover_providers()
        live = [p for p in discovered if p["detected"]]
        if not live:
            raise RuntimeError("No local LLM provider detected.")
        pick = next((p for p in live if p["name"] == provider), live[0])
        use_model = model or (pick["models"][0] if pick["models"] else "")
        system = _llm.load_skill_preprompt()
        messages = (
            ([{"role": "system", "content": system}] if system else [])
            + (history or [])
            + [{"role": "user", "content": user_text}]
        )
        async for event in _llm_chat_sse(pick["name"], use_model, messages):
            yield event
    except RuntimeError as e:
        yield f"data: {json.dumps({'error': str(e), 'mode': 'local-fallback'})}\n\n"


async def _llm_chat_sse(provider: str, model: str, messages: list[dict]):
    """SSE generator: proxies the provider OpenAI-compat stream, fail-soft to a single error event."""
    import json

    import httpx

    from nekomimi_mcp import llm as _llm

    cfg = _llm.PROVIDERS.get(provider, {})
    url = cfg.get("chat_url", "")
    try:
        async with httpx.AsyncClient(timeout=_llm.CHAT_TIMEOUT_S) as client:
            async with client.stream(
                "POST", url, json={"model": model, "messages": messages, "stream": True}
            ) as r:
                if r.status_code != 200:
                    yield f"data: {json.dumps({'error': f'{provider} HTTP {r.status_code}'})}\n\n"
                    return
                async for line in r.aiter_lines():
                    if line.startswith("data:"):
                        yield f"{line}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    register_tools()
    register_resources()
    register_prompts(mcp)

    mode = "--http" in sys.argv or os.environ.get("NEKOMIMI_TRANSPORT", "stdio") == "http"
    if mode:
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware

        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                _port = int(sys.argv[i + 1])
                break
        else:
            _port = int(os.environ.get("NEKOMIMI_PORT", os.environ.get("PORT", str(MCP_PORT))))

        # Stateless HTTP: the dashboard issues single-shot tools/call POSTs
        # without an MCP session handshake; stateful mode would 400 them
        # ("Missing session ID"). Claude Desktop uses stdio and is unaffected.
        _app = mcp.http_app(stateless_http=True)
        _register_rest_routes(_app, _port)
        _app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                f"http://127.0.0.1:{_port}",
                "http://tauri.localhost",
                "https://tauri.localhost",
                "tauri://localhost",
            ],
            allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"Starting nekomimi-mcp HTTP on port {_port}")
        uvicorn.run(_app, host="127.0.0.1", port=_port, log_level="info")
    else:
        # Single-transport guard: SQLite opens at import, so stdio + HTTP must
        # never run concurrently. If the HTTP daemon owns the port, say so.
        import httpx

        try:
            r = httpx.get(f"http://127.0.0.1:{MCP_PORT}/health", timeout=2.0)
            if r.status_code == 200:
                logger.error(
                    f"HTTP daemon already owns port {MCP_PORT} — refusing stdio "
                    "(shared SQLite). Use the running daemon or stop it first."
                )
                return 2
        except Exception:
            pass
        logger.info("Starting nekomimi-mcp in stdio mode")
        mcp.run(transport="stdio")

    return 0


if __name__ == "__main__":
    sys.exit(main())
