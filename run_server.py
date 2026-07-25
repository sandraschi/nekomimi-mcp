"""PyInstaller entry point — starts the HTTP/uvicorn server."""
import os
import sys

sys.path.insert(0, "src")

import uvicorn

port = int(os.getenv("PORT", "10700"))
host = os.getenv("HOST", "127.0.0.1")

# Overwrite sys.argv to prevent PyInstaller from passing frozen args
sys.argv = ["run_server.py", "--mode", "http", "--host", host, "--port", str(port)]

from nekomimi_mcp.server import main

main()
