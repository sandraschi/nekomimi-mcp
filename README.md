# nekomimi-mcp

Substrate-independent embodiment abstraction layer for conversational NPCs.

**One intent vocabulary. Many bodies. Zero joint angles in the LLM.**

## Architecture

```
LLM → Intent tokens → Renderer registry → Boomy (yahboom-mcp)
                                       → VRM (canonical humanoid)
                                       → Resonite (stub)
                                       → Reachy Mini (stub)
                                       → Berkeley Lite (stub)
```

Two strictly separated layers:
- **INTENT**: Abstract expressive vocabulary (nod, sulk, amused, retreat…). The LLM emits only these tokens — it never emits joint angles and never knows which body the NPC inhabits.
- **RENDER**: Per-substrate translators that convert intent + timing parameters into actuator commands. Adding a body = one renderer + one mapping table.

Motion quality (timing, easing, anticipation, hesitation) is a first-class parameter of every intent, not an afterthought per renderer.

## Tools

| Tool | Purpose |
|------|---------|
| `list_intents` | List all available intent tokens with timing metadata |
| `get_intent_definition` | Canonical timing + fallback for one token |
| `emit_intent` | Emit an intent token to all/specific renderers |
| `list_renderers` | List registered body renderers |
| `renderer_status` | Health check for one renderer |
| `stop_all` | Emergency stop — halt all renderers |
| `list_recorded_streams` | List recorded intent streams |
| `replay_stream` | Replay a recorded intent stream |
| `delete_stream` | Delete a recorded stream |
| `status` | Server status: uptime, tool count, renderer summary |
| `shutdown` | Graceful shutdown (requires confirm=True) |
| `show_renderers_card` | Renderer list as a Prefab in-chat card |

> Actual registered MCP tool names carry a `_tool` suffix
> (e.g. `intent_tool`, `list_intents_tool`, `status_tool`, `shutdown_tool`)
> plus `show_renderers_card`. See `llms-full.txt` for the full list.

## REST endpoints (HTTP mode)

`GET /health`, `GET /api/status`, `GET /api/skills` (+ `/api/skills/{name}`),
`GET /api/capabilities`, `GET /api/v1/diagnostics`, `POST /api/shutdown`.
MCP itself on `POST /mcp`.

## Renderer Status

| Renderer | Status | Backend |
|----------|--------|---------|
| Boomy | **DONE** | Delegates to yahboom-mcp via HTTP |
| VRM (canonical) | **DONE** | VRM 1.0 normalized bone poses (data-only; webapp for 3D) |
| Resonite | **STUB** | resonite-mcp API mapping needed |
| Reachy Mini | **STUB** | Hardware on order; sim via MuJoCo |
| Berkeley Lite | **STUB** | No hardware; sim via Isaac Lab |

## Usage

```bash
# Start with dual transport (HTTP + stdio)
uv run nekomimi --mode dual

# stdio only (for Claude Desktop)
uv run nekomimi --mode stdio

# Emit an intent
curl -X POST http://127.0.0.1:10700/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "emit_intent", "token": "nod", "intensity": 0.7}'
```

## Safety

- `retreat` and `sulk` both drive backward — geometry guard checks LIDAR before permitting motion
- `sulk` has a timeout and wounded-dignity return, not an open-ended state
- `stop_all` is always available from any client

## Webapp

```bash
cd webapp && npm install && npm run dev
```

Side-by-side preview: VRM canonical skeleton + Boomy telemetry + intent stream timeline.

## Intent Tokens (14)

attending, nod, shake, sulk, bashful, amused, playful, confused, retreat, surprise, bow, happy, sad, angry, nekomimi
