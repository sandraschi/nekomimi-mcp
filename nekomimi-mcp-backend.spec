# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — produce nekomimi-mcp-backend.exe for Tauri NSIS embedding.
# Fleet standard: strip=False, upx=False, noarchive=True (see tauri_nsis_building.md).
# Usage (from repo root):
#   uv run pyinstaller nekomimi-mcp-backend.spec --distpath dist --clean --noconfirm

block_cipher = None

a = Analysis(
    ["src/nekomimi_mcp/__main__.py"],
    pathex=["src"],
    binaries=[],
    nekomimi_mcps=[("src/nekomimi_mcp", "nekomimi_mcp")],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "h11",
        "beartype",
        "websockets",
        "sqlite3",
        "_strptime",
        "_datetime",
        "cachetools",
        "pytz",
        "jsonschema",
        "joserfc",
        "joserfc.jwk",
        "joserfc.jwt",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "setuptools", "pip", "wheel", "test", "tests", "unittest", "_distutils_hack"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
# Strip .dist-info but preserve metanekomimi_mcp for packages that need it at runtime
_keep_dist = ["fastmcp-", "fastmcp_slim-", "mcp-", "prefab_ui-", "opentelemetry-", "email_validator-"]
_saved = [
    e
    for e in a.nekomimi_mcps
    if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and ".dist-info" in str(e[0])
]
for _list in [a.nekomimi_mcps, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and ".dist-info" in str(e[0]))]
a.nekomimi_mcps.extend(_saved)
SKIP = [
    "torch",
    "playwright",
    "bitsandbytes",
    "llvmlite",
    "pyarrow",
    "pymupdf",
    "grpc",
    "numba",
    "Cython",
    "google",
    "azure",
    "boto3",
    "botocore",
    "matplotlib",
    "PIL",
    "pandas",
    "scipy",
    "sklearn",
    "onnxruntime",
]
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure, a.zipped_nekomimi_mcp, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.nekomimi_mcps,
    [],
    name="nekomimi-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
