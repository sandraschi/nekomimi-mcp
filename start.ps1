param([switch]$HTTP, [switch]$NoBrowser)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSCommandPath
$Port = if ($HTTP) { 11130 } else { $null }

# Port zombie clearing
if ($HTTP) {
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

$env:NEKOMIMI_PORT = "$Port"
$env:NEKOMIMI_TRANSPORT = if ($HTTP) { "http" } else { "stdio" }

Write-Host "Starting nekomimi-mcp ($($env:NEKOMIMI_TRANSPORT) mode)..." -ForegroundColor Cyan
if ($HTTP) {
    Write-Host "  MCP SSE: http://127.0.0.1:$Port/mcp" -ForegroundColor Yellow
}
uv run python -m nekomimi_mcp.server
