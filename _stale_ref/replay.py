"""Intent Stream Player — replay a recorded intent stream from CLI."""
import argparse
import asyncio
import sys

sys.path.insert(0, "src")

from nekomimi_mcp.intent.stream import get_stream
from nekomimi_mcp.renderers.registry import RendererRegistry
from nekomimi_mcp.renderers.vrm import VRMRenderer


async def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a recorded intent stream")
    parser.add_argument("stream_name", help="Name of the recorded stream")
    args = parser.parse_args()

    registry = RendererRegistry()
    registry.register(VRMRenderer())

    frames = get_stream(args.stream_name)
    if not frames:
        print(f"Stream not found: {args.stream_name}")
        return

    print(f"Replaying {len(frames)} frames from '{args.stream_name}'")
    for i, frame in enumerate(frames):
        print(f"  [{i}] {frame.token.value} (intensity={frame.intensity})")
        results = await registry.dispatch(frame)
        for r in results:
            print(f"       → {r['renderer']}: {r['status']}")


if __name__ == "__main__":
    asyncio.run(main())
