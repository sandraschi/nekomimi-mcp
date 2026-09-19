from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

from nekomimi_mcp.prompts import register_prompts
from nekomimi_mcp.tools import (
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
]


def tool_names() -> list[str]:
    return [fn.__name__ for fn, _, _ in _REGISTERED_TOOLS]


def register_tools() -> None:
    for fn, annot, extra in _REGISTERED_TOOLS:
        if extra.get("app"):
            mcp.tool(app=True)(fn)
        else:
            mcp.tool(annotations=annot)(fn)


def _register_rest_routes(app, port: int) -> None:
    """Fleet REST surface: health, status, skills, capabilities, diagnostics, shutdown.

    The webapp and fleet launcher consume these over HTTP; the MCP tools
    remain the primary agent surface on /mcp.
    """
    from pathlib import Path

    from starlette.requests import Request
    from starlette.responses import JSONResponse, PlainTextResponse

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
                "prompts": ["nekomimi_intent_guide", "nekomimi_character", "renderer_comparison"],
                "resources": [],
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
                "renderers": renderers,
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

    app.add_route("/health", health, methods=["GET"])
    app.add_route("/api/status", status, methods=["GET"])
    app.add_route("/api/skills", skills, methods=["GET"])
    app.add_route("/api/skills/{name}", skill_content, methods=["GET"])
    app.add_route("/api/capabilities", capabilities, methods=["GET"])
    app.add_route("/api/v1/diagnostics", diagnostics, methods=["GET"])
    app.add_route("/api/shutdown", shutdown, methods=["POST"])


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    register_tools()
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

        _app = mcp.http_app()
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
        logger.info("Starting nekomimi-mcp in stdio mode")
        mcp.run(transport="stdio")

    return 0


if __name__ == "__main__":
    sys.exit(main())
