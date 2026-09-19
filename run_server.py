"""PyInstaller entry point — starts the HTTP/uvicorn server."""

import os
import sys

sys.path.insert(0, "src")


def _main() -> int:
    from nekomimi_mcp.server import main

    port = int(os.getenv("PORT", os.getenv("NEKOMIMI_PORT", "11128")))
    host = os.getenv("HOST", "127.0.0.1")

    # Overwrite sys.argv to prevent PyInstaller from passing frozen args.
    # Must match server.py main(): it looks for "--http" and "--port <n>".
    sys.argv = ["run_server.py", "--http", "--port", str(port), "--host", host]

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
