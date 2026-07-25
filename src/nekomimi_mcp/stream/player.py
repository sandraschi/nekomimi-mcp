from __future__ import annotations

from nekomimi_mcp.intent.schema import IntentToken, MotionParams
from nekomimi_mcp.stream.recorder import IntentRecorder

INTENT_DELAY_BETWEEN = 0.3  # seconds between tokens in a recorded stream


class IntentPlayer:
    def __init__(self, recorder: IntentRecorder):
        self._recorder = recorder

    async def replay(self, recording_id: int, renderers: list | None = None) -> list[dict]:
        from nekomimi_mcp.renderers import RENDERER_REGISTRY

        rec = self._recorder.get_recording(recording_id)
        if not rec:
            return [{"success": False, "error": f"recording {recording_id} not found"}]

        tokens = [IntentToken(t) for t in rec["tokens"]]
        params = MotionParams(**rec["params"])
        target_renderer = rec["renderer"]

        results = []
        targets = (
            [target_renderer]
            if target_renderer and target_renderer != "all"
            else list(RENDERER_REGISTRY.keys())
        )
        if renderers:
            targets = [t for t in targets if t in renderers]

        for token in tokens:
            for name in targets:
                r = RENDERER_REGISTRY.get(name)
                if r and r.hardware_connected:
                    result = await r.render(token, params)
                    results.append(result)
        return results
