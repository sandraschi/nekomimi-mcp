set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

set shell := ["powershell.exe", "-NoProfile", "-Command"]

_uv := "C:\\Users\\sandr\\.local\\bin\\uv.exe"
_bun := "C:\\Users\\sandr\\.bun\\bin\\bun.exe"
_ruff := "C:\\Users\\sandr\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\ruff.exe"
_just := "C:\\Users\\sandr\\.local\\bin\\just.exe"
_mcpb := "C:\\Users\\sandr\\AppData\\Roaming\\npm\\mcpb.cmd"

# Show all recipes
default:
    @{{_just}} --list

# MCP
serve: serve-stdio

serve-stdio:
    {{_uv}} run python -m nekomimi_mcp.server

serve-http:
    $env:NEKOMIMI_TRANSPORT = "http"
    {{_uv}} run python -m nekomimi_mcp.server --http --port 11128

lint:
    {{_ruff}} check src/
    {{_ruff}} format src/ --check

fix:
    {{_ruff}} check --fix src/
    {{_ruff}} format src/

fmt:
    {{_ruff}} format src/

sync:
    {{_uv}} sync

mcpb-pack:
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/mcpb-pack.ps1

mcpb-validate:
    & {{_mcpb}} validate .

test:
    {{_uv}} run pytest tests/ -v

# Full local quality gate (mirrors .github/workflows/ci.yml)
ci:
    {{_uv}} run ruff check src/ tests/
    {{_uv}} run ruff format src/ tests/ --check
    {{_uv}} run pyright src/
    {{_uv}} run pytest tests/ -q
    Set-Location webapp; {{_bun}} run check
    Set-Location webapp; {{_bun}} run biome:ci
    Write-Host "CI green." -ForegroundColor Green

# Playwright e2e (spins up backend :11128 + preview :11129 itself)
e2e:
    Set-Location webapp; {{_bun}} x playwright test

# CUA webapp test (browser-driven pre-Tauri pass)
cua-webapp-test: e2e

# Release certification: full gate + e2e + bundle validation
certify: ci e2e
    {{_uv}} run python -c "import json; d=json.load(open('assets/prompts/examples.json')); s=open('assets/prompts/system.md').read().split(); u=open('assets/prompts/user.md').read().split(); assert len(d)>=100 and len(s)>=3000 and len(u)>=4000, 'MCPB 3-4-100 FAIL'; print(f'certify OK: {len(s)}/{len(u)}/{len(d)}'))"
    Write-Host "Certified." -ForegroundColor Green

# Bootstrap: install dev deps + pre-commit hook + web deps
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Set-Location webapp; {{_bun}} install --frozen-lockfile
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
