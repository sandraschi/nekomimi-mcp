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
)

logger = logging.getLogger("nekomimi-mcp")

MCP_PORT = int(os.environ.get("NEKOMIMI_PORT", "11128"))

mcp = FastMCP(
    name="nekomimi-mcp",
    version="0.1.0",
)


def register_tools() -> None:
    mcp.tool(annotations={"readOnlyHint": False})(intent_tool)
    mcp.tool(annotations={"readOnlyHint": False})(intent_stream_tool)
    mcp.tool(annotations={"readOnlyHint": True})(list_intents_tool)
    mcp.tool(annotations={"readOnlyHint": True})(list_renderers_tool)
    mcp.tool(annotations={"readOnlyHint": True})(renderer_info_tool)
    mcp.tool(annotations={"readOnlyHint": True})(check_boomy_mapping_tool)
    mcp.tool(annotations={"readOnlyHint": True})(safety_status_tool)
    mcp.tool(annotations={"readOnlyHint": False})(safe_retreat_tool)
    mcp.tool(annotations={"readOnlyHint": True})(recordings_list_tool)
    mcp.tool(annotations={"readOnlyHint": False})(replay_intent_tool)
    mcp.tool(annotations={"readOnlyHint": False})(export_recordings_tool)
    mcp.tool(app=True)(show_renderers_card)


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
            _port = int(os.environ.get("NEKOMIMI_PORT", str(MCP_PORT)))

        _app = mcp.http_app()
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
