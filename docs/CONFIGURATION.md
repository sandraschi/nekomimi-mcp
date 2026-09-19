# Configuration — nekomimi-mcp

All configuration is environment variables. Defaults target a single-user Windows box.

## Backend

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEKOMIMI_PORT` | `11128` | HTTP mode port (also honors `PORT` for Tauri) |
| `NEKOMIMI_TRANSPORT` | `stdio` | `stdio` for Claude Desktop, `http` for the webapp |
| `HOST` | `127.0.0.1` | Bind address (Tauri passes this; loopback only) |
| `NEKOMIMI_YAHBOOM_URL` | `http://127.0.0.1:10892` | yahboom-mcp base URL for the Boomy renderer |
| `NEKOMIMI_REACHY_HOST` | `127.0.0.1` | Reachy Mini host (when hardware exists) |

## Ports (fleet-registered)

| Port | Use |
|------|-----|
| 11128 | Backend: FastMCP stdio + HTTP (`/mcp`), REST (`/health`, `/api/*`) |
| 11129 | Frontend: Vite dev / preview |

## Fleet launcher

`fleet-start.config.ps1` is the source of truth for `start.ps1`:

- `BackendPort = 11128`, `FrontendPort = 11129`, `HealthPath = '/health'`
- Backend `module-serve`: `python -m nekomimi_mcp.server --http --port 11128`
- Frontend `vite-npm` in `webapp/`

## Webapp

No build-time config. The backend URL is `API_BASE` in `webapp/src/lib/api.ts`
(`http://127.0.0.1:11128`). UI zoom persists in `localStorage` (`nekomimi-ui-zoom`);
chat personality, history, and LLM selection persist under `nekomimi-*` keys.
