# Troubleshooting — nekomimi-mcp

## Backend

**`GET /api/llm/onboarding` says `configured: false`**
Start Ollama (`ollama serve`, `ollama pull <model>`) or LM Studio's local
server. The Settings page mirrors this state.

**Chat answers with the offline matcher**
No provider detected — see above. The chat toolbar shows
`offline intent matcher` instead of `LLM: <provider>`.

**`Missing session ID` (HTTP 400 on `/mcp`)**
The server runs stateless HTTP; stateful MCP clients that require a session
handshake must use stdio mode instead. Browser clients must send
`Accept: application/json, text/event-stream` and parse SSE `data:` frames
(see `webapp/src/lib/api.ts` `parseSseJsonRpc`).

**`406 Not Acceptable` on `/mcp`**
Same cause: send the Accept header above.

**Port 11128 in use**
`start.ps1` clears it via the fleet engine; manually:
`Get-NetTCPConnection -LocalPort 11128 | % { taskkill /F /PID $_.OwningProcess }`.

## Webapp

**Unstyled page (raw HTML)**
The Tailwind v4 Vite plugin must be in `vite.config.ts` (`tailwindcss()`).
Fixed 2026-09-19; if styles vanish again, check the plugin list first.

**Backend offline dot**
Poll uses exponential backoff (5s → 60s). Force a re-check by reloading;
Tauri builds also listen for `backend-status` events.

**UI too small/large**
Ctrl+scroll zooms (persisted), Ctrl+0 resets. Percentage shows in the header.

## Packaging

**`mcpb pack` ships stale code**
Never pack by hand — `just mcpb-pack` wipes `mcpb/src` and recopies
`src/nekomimi_mcp` first, then verifies 3-4-100 counts and the import origin.

**Tauri backend missing at runtime**
`src-tauri` embeds `resources/nekomimi-mcp-backend.exe` built by
`src-tauri/build.ps1` (PyInstaller from the project venv — never `uv run
pyinstaller`). Check `backend-spawn.log` in the app log dir.

## Diagnostics

- `GET /health`, `/api/status`, `/api/v1/diagnostics` — liveness to full dump.
- `POST /api/shutdown` / `shutdown_server(confirm=True)` — orderly exit.
- `data/intents.db` — SQLite recordings (delete to reset history).
