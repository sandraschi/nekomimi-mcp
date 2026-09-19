# Architecture — nekomimi-mcp

## Layers

```
LLM / user  →  INTENT layer (tokens + MotionParams)  →  RENDER layer (per-body translators)
```

The LLM emits **only** intent tokens (`express_intent`) — never joint angles,
never body-specific commands. Each renderer translates to its body's native
actuators: differential drive + gimbal (Boomy), VRM bone poses (VRM avatar),
Stewart platform (Reachy Mini, STUB), biped posture (BHL, STUB).

## Processes and transports

| Surface | How |
|---------|-----|
| Claude Desktop | stdio (`python -m nekomimi_mcp.server`) |
| Webapp / Tauri | HTTP :11128 — MCP on `POST /mcp` (stateless), REST on `/health` + `/api/*` |
| Webapp UI | Vite :11129 (dev) or Tauri webview (bundled `dist/`) |

Stateless HTTP is deliberate: the dashboard issues single-shot `tools/call`
POSTs without an MCP session handshake (stateful mode 400s them).

## Data flow

- Every `express_intent` / `play_intent_stream` call is recorded to SQLite
  (`src/data/intents.db` via `IntentRecorder`) for replay and regression
  testing (`list_recordings`, `replay_recording`, Inbox page).
- `POST /api/chat`: skill preprompt (`skills/nekomimi-operator/SKILL.md` as
  system message) + first configured local provider (Ollama/LM Studio/vLLM);
  falls back to the offline intent matcher, which also emits.
- `GET /api/fleet/apps`: self + live-probed companions (yahboom-mcp :10892,
  resonite-mcp :10979), fail-soft.

## Safety

- `DriveGeometryGuard`: LIDAR clearance before retreat (`retreat_safely`).
- `TimeoutPolicy`: persistent intents auto-terminate (sulk 15s, tired 60s).

## Ports

Backend :11128, frontend :11129 (adjacent pair, fleet-registered). No other
ports are bound. Probes to :11434/:1234/:8000/:10892/:10979 are outbound
client connections from the backend, never binds.
