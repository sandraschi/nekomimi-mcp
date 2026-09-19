# MCPB pack pipeline for nekomimi-mcp (fleet MCPB_PACKAGING_STANDARDS §2.5).
# Fresh-stage wipe+recopy src -> mcpb/src, mechanical checks, 3-4-100 verify, pack.
# Usage: pwsh -NoProfile -File scripts/mcpb-pack.ps1  (or: just mcpb-pack)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$pkg = "nekomimi_mcp"
$McpbDir = Join-Path $RepoRoot "mcpb"
$stage = Join-Path $McpbDir "src\$pkg"

function Word-Count([string]$Path) {
    (@(Get-Content -Raw $Path) -split '\s+' | Where-Object { $_ }).Count
}

Write-Host "=== mcpb-pack: fresh-stage wipe+recopy ===" -ForegroundColor Cyan

# 0. Clean sneak-in .bak twins from the source tree itself (top pollution source).
Get-ChildItem -Recurse -Path (Join-Path $RepoRoot "src") -Filter "*.bak" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path (Join-Path $RepoRoot "src") -Filter "*.bak.*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# 1. Wipe stage.
if (Test-Path (Join-Path $McpbDir "src")) {
    Remove-Item -Recurse -Force (Join-Path $McpbDir "src")
    Write-Host "  wiped mcpb/src" -ForegroundColor DarkGray
}
New-Item -ItemType Directory -Force -Path (Split-Path $stage) | Out-Null

# 2. Recopy, preserve package dir (NEVER flatten).
$src = Join-Path $RepoRoot "src\$pkg"
if (-not (Test-Path $src)) { throw "src/$pkg not found at $src" }
Copy-Item -Recurse -Force $src $stage
Write-Host "  copied src/$pkg -> mcpb/src/$pkg" -ForegroundColor Green

# 3. Strip pollution from the stage.
Get-ChildItem -Recurse -Path $stage -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $stage -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $stage -Filter "*.bak" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $stage -Filter "*.bak.*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# 4. Mirror bundle metadata into mcpb/ (manifest, prompts, docs).
foreach ($f in @("manifest.json", "README.md", "CHANGELOG.md")) {
    Copy-Item -Force (Join-Path $RepoRoot $f) (Join-Path $McpbDir $f)
}
$promptsSrc = Join-Path $RepoRoot "assets\prompts"
$promptsDst = Join-Path $McpbDir "assets\prompts"
if (Test-Path $promptsSrc) {
    New-Item -ItemType Directory -Force -Path $promptsDst | Out-Null
    Copy-Item -Force (Join-Path $promptsSrc "*") $promptsDst
}
$iconSrc = Join-Path $RepoRoot "assets\icon.png"
$iconDst = Join-Path $McpbDir "assets\icon.png"
if (Test-Path $iconSrc) {
    New-Item -ItemType Directory -Force -Path (Split-Path $iconDst) | Out-Null
    Copy-Item -Force $iconSrc $iconDst
}

# 5. .mcpbignore must exist at the PACK ROOT (mcpb/), not just repo root.
$repoIgnore = Join-Path $RepoRoot ".mcpbignore"
$mcpbIgnore = Join-Path $McpbDir ".mcpbignore"
if ((Test-Path $repoIgnore) -and (-not (Test-Path $mcpbIgnore))) {
    Copy-Item $repoIgnore $mcpbIgnore -Force
    Write-Host "  copied .mcpbignore -> mcpb/.mcpbignore" -ForegroundColor Yellow
}

# 6. Mechanical checks.
Write-Host "-> checks" -ForegroundColor Yellow
$env:PYTHONDONTWRITEBYTECODE = "1"
$check = & uv run python -c "import sys; sys.path.insert(0, 'mcpb/src'); from nekomimi_mcp.server import main; import pathlib, nekomimi_mcp.server; print(pathlib.Path(nekomimi_mcp.server.__file__).resolve())" 2>&1
Write-Host "  import origin: $check"
if ("$check" -notmatch "mcpb") { throw "Import did not resolve inside mcpb/src. Got: $check" }

$sys = Word-Count (Join-Path $RepoRoot "assets\prompts\system.md")
$user = Word-Count (Join-Path $RepoRoot "assets\prompts\user.md")
$ex = (Get-Content (Join-Path $RepoRoot "assets\prompts\examples.json") -Raw | ConvertFrom-Json).Count
Write-Host "  3-4-100: system=$sys user=$user examples=$ex"
if ($sys -lt 3000 -or $user -lt 4000 -or $ex -lt 100) {
    throw "3-4-100 FAIL: system=$sys user=$user examples=$ex (need 3000 / 4000 / 100)"
}

$pollution = Get-ChildItem -Recurse -Path $McpbDir -ErrorAction SilentlyContinue | Where-Object {
    $_.PSIsContainer -and $_.Name -eq "__pycache__"
} | Measure-Object | Select-Object -ExpandProperty Count
$pollution += @(Get-ChildItem -Recurse -Path $McpbDir -Include "*.pyc", "*.bak", "*.bak.*" -ErrorAction SilentlyContinue).Count
if ($pollution -gt 0) { throw "Pollution under mcpb/: $pollution item(s)" }
Write-Host "  pollution: clean" -ForegroundColor Green

Write-Host "=== stage verified OK ===" -ForegroundColor Green

# 7. Pack.
$manifest = Get-Content (Join-Path $RepoRoot "manifest.json") -Raw | ConvertFrom-Json
$ver = $manifest.version
$distDir = Join-Path $RepoRoot "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$out = Join-Path $distDir "nekomimi-mcp-v$ver.mcpb"
$mcpbCmd = Join-Path $env:APPDATA "npm\mcpb.cmd"
if (-not (Test-Path $mcpbCmd)) { throw "mcpb CLI not found at $mcpbCmd" }
& $mcpbCmd pack $McpbDir $out
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed" }
Write-Host "Packed: $out" -ForegroundColor Green

# 8. Delete the stage again so the next run cannot reuse it.
Remove-Item -Recurse -Force (Join-Path $McpbDir "src")
Write-Host "  stage removed post-pack" -ForegroundColor DarkGray
