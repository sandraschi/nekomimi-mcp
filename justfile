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
    $v = & {{_uv}} run python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d['project']['version'])"
    & {{_mcpb}} pack . "dist/nekomimi-mcp-v$v.mcpb"

mcpb-validate:
    & {{_mcpb}} validate .

test:
    {{_uv}} run pytest tests/ -v

# Bootstrap: install dev deps + pre-commit hook + web deps
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Set-Location webapp; {{_bun}} install --frozen-lockfile
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
