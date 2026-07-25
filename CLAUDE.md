# nekomimi-mcp — Agent Guide

## Overview
Substrate-independent embodiment layer for conversational NPCs.
Express intent tokens across robot, VRM, and humanoid bodies.

## Entry Points
- `uv run python -m nekomimi_mcp.server` — stdio mode
- `uv run python -m nekomimi_mcp.server --http --port 11128` — HTTP mode
- `just serve-stdio` / `just serve-http`

## Key Files
- `src/nekomimi_mcp/server.py` — FastMCP entry point
- `src/nekomimi_mcp/tools.py` — 11 MCP tool definitions
- `src/nekomimi_mcp/intent/schema.py` — IntentToken, MotionParams, IntentStream
- `src/nekomimi_mcp/intent/registry.py` — Intent defaults with timing
- `src/nekomimi_mcp/renderers/` — Boomy (real), VRM (preview), Reachy Mini (STUB), BHL (STUB)
- `src/nekomimi_mcp/stream/` — SQLite recorder + player
- `src/nekomimi_mcp/safety/` — Drive geometry guard + timeout policy

## Standards
- FastMCP 3.4.4 portmanteau pattern with Annotated params
- Responses: structured dicts with `success`, `message`, domain fields
- Dual transport: stdio (Claude Desktop) + HTTP (port 11128)
- See mcp-central-docs for fleet-wide standards
