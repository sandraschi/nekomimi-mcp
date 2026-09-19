# Changelog

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
