# nekomimi-mcp — Directory Map

## src/nekomimi_mcp/

| File | Purpose |
|------|---------|
| `server.py` | FastMCP entry, dual transport, tool registration |
| `tools.py` | 11 MCP tools: intent, stream, renderer registry, safety, recordings |
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
