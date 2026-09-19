# Changelog

## Unreleased (2026-09-19 fix-all)

- BREAKING (compat kept): verb-led primary tool names (`express_intent`,
  `play_intent_stream`, `list_intents`, `list_renderers`, `describe_renderer`,
  `preview_boomy_mapping`, `get_safety_status`, `retreat_safely`,
  `list_recordings`, `replay_recording`, `export_recordings`, `get_status`,
  `shutdown_server`); historic `*_tool` names are deprecated aliases (gone in 0.2.0)
- Fixed: recorder crash on every `express_intent` (StrEnum coerced to str);
  dead `berkeley_lite`/`resonite` stub modules removed (unimportable, unregistered)
- Fixed: Boomy `led` calls dropped the blue channel (`_call` arity);
  Prefab card crashed (`app.add` does not exist — context-manager API now)
- Fixed: webapp MCP client never worked (406 without Accept; SSE unparsed);
  Tailwind plugin missing (unstyled UI); stateless HTTP enabled for dashboard
- New: backend LLM proxy (`/api/llm/*`), skill-first `POST /api/chat` + SSE,
  `/api/fleet/apps`, `skill://nekomimi-operator` resource, output schemas
- New: Inbox + Apps pages, Dashboard hero + onboarding cue, useZoom,
  Tauri listen + backoff, Ctrl+K, provider indicator, backend-backed Settings
- Quality: pyright clean, coverage 59% (floor 55), Playwright e2e 7/7,
  fleet CI + `just ci` green, pre-commit operational
- Docs: `docs/` stack (incl. ONBOARDING), README rewrite, INSTALL.md, screenshots
- Packaging: icon, 3-4-100 prompts (3004/4006/100), manifest.json, fresh-stage pack

## Unreleased (2026-09-19 assfix)

- 14 MCP tools: added `status_tool` and `shutdown_tool` (confirm-gated)
- New REST surface in HTTP mode: `/health`, `/api/status`, `/api/skills`,
  `/api/capabilities`, `/api/v1/diagnostics`, `POST /api/shutdown`
- Fixed `run_server.py`: correct port default (11128) and `--http --port` argv;
  server honors `PORT`/`HOST` env (Tauri backend)
- `fleet-start.config.ps1`: real ports (11128/11129) + module-serve backend
- Webapp: Biome 2.x wired (`biome:ci`, `check` scripts), lint + a11y clean,
  Dashboard hero section, Settings reads backend URL from API_BASE
- Session context: `.claude-plugin/plugin.json`, Copilot instructions,
  OpenCode + Antigravity skills
- Hygiene: `.gitattributes` (LF), `.mcpbignore`, `.gitignore` patterns,
  Biome pre-commit hook, `just fmt`, bootstrap installs web deps
- glama.json version + tool list; llms-full port + endpoint docs

## 0.1.0 (2026-07-25)

- Initial scaffold: intent layer with 17 tokens and motion parameters
- Boomy renderer (HTTP proxy to yahboom-mcp)
- VRM renderer (canonical bone pose keyframes)
- Reachy Mini renderer (STUB)
- BHL renderer (STUB)
- Stream recorder/player (SQLite + JSONL)
- Safety guards (drive geometry, timeout policy)
- 11 MCP tools
- 3 FastMCP prompts
- Preview webapp (React + Three.js VRM viewer)
