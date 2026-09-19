# Development — nekomimi-mcp

## Setup

```powershell
uv sync --group dev        # or: just sync + just bootstrap
cd webapp; bun install     # frontend deps
```

## Daily commands (`justfile`)

| Recipe | What |
|--------|------|
| `just serve-stdio` / `just serve-http` | Run the server (stdio / :11128) |
| `just test` | pytest |
| `just lint` / `just fix` / `just fmt` | ruff |
| `just ci` | Full local gate: ruff + format-check + **pyright** + pytest (+coverage floor 55) + `tsc` + `biome:ci` |
| `just e2e` / `just cua-webapp-test` | Playwright suite (spins up backend + preview itself) |
| `just mcpb-pack` / `just mcpb-validate` | MCPB bundle via `scripts/mcpb-pack.ps1` |
| `just bootstrap` | dev sync + pre-commit install + web deps |

## Tests

- `tests/test_imports.py` — package structure.
- `tests/test_assfix_regressions.py` — recorder enum-coercion crash, LLM fail-soft, tool renames.
- `tests/test_rest_routes.py` — REST surface via in-process TestClient (no network).
- Coverage floor: **55%** (`--cov-fail-under=55`). Keep it green; raise, never lower.
- `webapp/e2e/nekomimi.spec.ts` — 7 Playwright specs incl. README screenshots.

## Pre-commit

`.pre-commit-config.yaml` runs ruff, ruff-format, the Biome webapp hook
(`scripts/pre-commit-biome.ps1`), whitespace/yaml hygiene. Install once:
`uv run pre-commit install`. The hook blocks commits that fail any gate.

## Declared doubles (testing)

Per TESTING_GUIDE: the only test double is the **offline intent matcher**
(`POST /api/chat` `mode: "local-fallback"` and the Chat page fallback) — it is
named in every payload and in the UI indicator. No mocked KPIs, no fake
providers, no stubbed HTTP in tests (companion probes are fail-soft by design).

## Onboarding

Not N/A: this repo has wrappee hardware (Boomy robot) and benefits from a
local LLM account-free install. See [ONBOARDING.md](ONBOARDING.md). The
`configured` signal is `GET /api/llm/onboarding`.
