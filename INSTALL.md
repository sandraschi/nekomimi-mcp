# Installing nekomimi-mcp

> **First time?** Complete [docs/ONBOARDING.md](docs/ONBOARDING.md) before expecting live host calls.

## Prerequisites

Install these if you don't have them already:

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Desktop | Required host | [download](https://claude.ai/download) |
| Python 3.12+ | Backend runtime | `winget install Python.Python.3.12` |
| uv | Python package runner | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Bun | Webapp deps + dev server | `powershell -c "irm https://bun.sh/install.ps1 \| iex"` |
| Ollama **or** LM Studio | Local LLM for full chat (optional but recommended) | [ollama.com](https://ollama.com) / [lmstudio.ai](https://lmstudio.ai) |

No account, no API key, no credit card. A Boomy robot + yahboom-mcp is optional hardware.

## Option A — MCPB bundle (easiest)

1. Build: `just mcpb-pack` → `dist/nekomimi-mcp-v0.1.0.mcpb`
   (or download the release asset).
2. Claude Desktop → Settings → Extensions → drag-and-drop the `.mcpb`.
3. Restart Claude Desktop. Tools appear as `express_intent`, `list_intents`, …

## Option B — uv run (developers)

```powershell
uv sync
just serve-stdio    # for Claude Desktop stdio_then configure the command below
just serve-http     # for the webapp (port 11128)
```

Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nekomimi": {
      "command": "C:\\Users\\sandr\\.local\\bin\\uv.exe",
      "args": ["run", "python", "-m", "nekomimi_mcp.server"],
      "cwd": "D:\\Dev\\repos\\nekomimi-mcp"
    }
  }
}
```

Webapp:

```powershell
cd webapp; bun install; bun run dev   # http://127.0.0.1:11129
```

## Option C — Tauri desktop app

```powershell
.\src-tauri\build.ps1   # builds backend exe + NSIS installer
```

Install the generated `.exe` (current-user, no admin). The app spawns its
backend on port 11128 automatically and opens the dashboard.

## Option D — Source + inspect

```powershell
uv sync --group dev
just ci     # ruff + pyright + pytest + tsc + biome, must be green
just e2e    # Playwright suite (backend + preview self-hosted)
```

## Verify the install

1. Backend: `GET http://127.0.0.1:11128/health` → `{"status":"ok",…}`.
2. Webapp header dot reads **Backend Online**.
3. Settings → Onboarding panel: **Configured (ollama)** after `ollama pull qwen3:8b`.
4. Dashboard → emit `attending` → Boomy/VRM respond (simulated without hardware).

Stuck? [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) · [docs/ONBOARDING.md](docs/ONBOARDING.md).
