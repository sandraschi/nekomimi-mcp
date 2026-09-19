# nekomimi-mcp — Directory Map

## Service footprint (daemon + state)

- Backend HTTP :11128 (`GET /health`), frontend :11129. No NSSM service.
- SQLite at `src/data/intents.db` (opened at import in `tools.py` — stdio and
  HTTP modes must not run concurrently against it; there is no stdio→HTTP
  proxy, so run ONE transport at a time).
- Probe before debugging: `/health` → `/api/status` → `/api/v1/diagnostics`.
- Shutdown: `POST /api/shutdown` or `shutdown_server(confirm=True)`.
- Ports are fleet-registered (11128/11129); never change without
  `mcp-central-docs/fleet-gate/claim_ports.py`.

## src/nekomimi_mcp/

| File | Purpose |
|------|---------|
| `server.py` | FastMCP entry, dual transport, tool registration, REST routes |
| `tools.py` | 14 MCP tools (verb-led primaries + deprecated `*_tool` aliases) |
| `llm.py` | Local LLM proxy (Ollama/LM Studio/vLLM) + onboarding signal |
| `prompts.py` | 3 registered @mcp.prompt() templates |

## Key Packages

| Package | Purpose |
|---------|---------|
| `intent/` | IntentToken enum, MotionParams, IntentStream, default registry |
| `renderers/` | BaseRenderer ABC + 4 implementations (boomy, vrm, reachy_mini, bhl) |
| `stream/` | IntentRecorder (SQLite) + IntentPlayer |
| `safety/` | DriveGeometryGuard (LIDAR) + TimeoutPolicy |

## Reading Order
1. `intent/schema.py` — core data model
2. `intent/registry.py` — intent defaults
3. `renderers/base.py` — renderer abstraction
4. `renderers/boomy.py` — reference implementation
5. `tools.py` — tool definitions
6. `server.py` — entry point
