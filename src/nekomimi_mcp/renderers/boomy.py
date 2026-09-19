from __future__ import annotations

import os

import httpx

from nekomimi_mcp.intent.schema import IntentToken, MotionParams
from nekomimi_mcp.renderers.base import BaseRenderer, RendererCapability

_YAHBOOM_BASE = os.environ.get("NEKOMIMI_YAHBOOM_URL", "http://127.0.0.1:10892")
_MCP_ENDPOINT = f"{_YAHBOOM_BASE}/mcp"


class BoomyRenderer(BaseRenderer):
    body_type = "differential_drive_ptz"
    hardware_connected = False
    capabilities = [
        RendererCapability.DRIVE_BASE,
        RendererCapability.PTZ_GIMBAL,
        RendererCapability.LEDS,
        RendererCapability.SPEAKER,
        RendererCapability.FACE_DISPLAY,
    ]

    # Gimbal position tracking
    _pan: int = 90
    _tilt: int = 90
    _gimbal_engaged: bool = False
    _led_r: int = 0
    _led_g: int = 0
    _led_b: int = 0

    def __init__(self):
        self._client = httpx.AsyncClient(base_url=_YAHBOOM_BASE, timeout=5.0)
        self.hardware_connected = self._probe()

    def _probe(self) -> bool:
        try:
            import httpx

            r = httpx.get(f"{_YAHBOOM_BASE}/api/v1/health", timeout=2.0)
            return r.status_code == 200
        except Exception:
            return False

    def status(self) -> str:
        if not self.hardware_connected:
            return "unavailable (yahboom-mcp not reachable)"
        return "ready"

    def can_express(self, token: IntentToken) -> bool:
        _unsupported = {
            IntentToken.NOD,
            IntentToken.BASHFUL,
            IntentToken.SURPRISED,
            IntentToken.ALARMED,
            IntentToken.CURIOUS,
            IntentToken.APOLOGETIC,
        }
        return token not in _unsupported

    async def stop(self) -> dict:
        return await self._call("stop_all")

    async def idle_tick(self) -> dict | None:
        return await self._render_boomy(IntentToken.IDLE, MotionParams())

    async def render(
        self, token: IntentToken, params: MotionParams | None = None, target: dict | None = None
    ) -> dict:
        return await self._render_boomy(token, params or MotionParams())

    async def _call(
        self,
        operation: str,
        param1: float | str | None = None,
        param2: float | str | None = None,
        param3: float | str | None = None,
    ) -> dict:
        try:
            r = await self._client.post(
                _MCP_ENDPOINT,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "yahboom_tool",
                        "arguments": {
                            "operation": operation,
                            "param1": param1,
                            "param2": param2,
                            "param3": param3,
                        },
                    },
                },
                timeout=5.0,
            )
            if r.status_code == 200:
                return {"success": True, "operation": operation}
            return {"success": False, "error": f"HTTP {r.status_code}", "operation": operation}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "operation": operation}
        except httpx.ConnectError:
            self.hardware_connected = False
            return {"success": False, "error": "yahboom-mcp unreachable", "operation": operation}

    async def _call_multi(
        self, calls: list[tuple[str, float | str | None, float | str | None]]
    ) -> list[dict]:
        results = []
        for op, p1, p2 in calls:
            results.append(await self._call(op, p1, p2))
        return results

    async def _render_boomy(self, token: IntentToken, params: MotionParams) -> dict:
        if not self.hardware_connected:
            return {
                "success": False,
                "error": "hardware not connected",
                "token": token.value,
                "simulated": True,
                "mapping": self._describe_mapping(token, params),
            }

        s = params.speed
        intensity = params.intensity

        _pan_step = int(30 * intensity)
        _tilt_step = int(20 * intensity)
        _drive_speed = max(0.05, s * 0.4)

        match token:
            case IntentToken.ATTENDING:
                calls = [
                    ("camera_set_pos", 90, 90),
                    ("forward", _drive_speed * 0.5, None),
                ]
                await self._call_multi(calls)

            case IntentToken.CONFUSED:
                for _ in range(int(params.repeat_count)):
                    await self._call("turn_left", _drive_speed * 0.5, None)
                    await self._call("turn_right", _drive_speed * 0.5, None)
                    await self._call("camera_left", _pan_step, None)
                    await self._call("camera_right", _pan_step, None)
                await self._call("camera_set_pos", 90, 90)
                await self._call("led", 128, 64, 0)
                await self._call("play_beep", None, None)

            case IntentToken.NOD:
                # Severely degraded - gimbal tilt only
                for _ in range(int(params.repeat_count)):
                    await self._call("camera_up", _tilt_step, None)
                    await self._call("camera_down", _tilt_step, None)

            case IntentToken.SHAKE:
                for _ in range(int(params.repeat_count)):
                    await self._call("turn_left", _drive_speed * 0.5, None)
                    await self._call("turn_right", _drive_speed * 0.5, None)
                    await self._call("camera_left", _pan_step, None)
                    await self._call("camera_right", _pan_step, None)

            case IntentToken.SULK:
                await self._call("camera_set_pos", 110, 150)
                await self._call("backward", _drive_speed * 0.3, None)
                await self._call("led", 0, 0, 32)
                # Wait via sleep - hold duration is policy-managed outside

            case IntentToken.BASHFUL:
                # Degraded - no head-tilt possible, use gimbal aversion
                await self._call("camera_set_pos", 120, 110)
                await self._call("turn_left", _drive_speed * 0.3, None)
                await self._call("led", 64, 16, 32)

            case IntentToken.AMUSED:
                for _ in range(int(params.repeat_count)):
                    await self._call("forward", _drive_speed * 0.3, None)
                    await self._call("backward", _drive_speed * 0.3, None)
                await self._call("camera_up", _tilt_step // 2, None)
                await self._call("camera_down", _tilt_step // 2, None)
                await self._call("light_effect", 2, None)

            case IntentToken.SURPRISED:
                await self._call("stop", None, None)
                await self._call("backward", _drive_speed * 0.5, None)
                await self._call("camera_set_pos", 90, 45)
                await self._call("led", 255, 255, 255)
                await self._call("play_beep", None, None)

            case IntentToken.CURIOUS:
                await self._call("forward", _drive_speed * 0.3, None)
                await self._call("camera_set_pos", 90, 80)
                await self._call("led", 32, 24, 8)

            case IntentToken.ALARMED:
                await self._call("backward", _drive_speed * 0.6, None)
                await self._call("camera_set_pos", 0, 90)
                await self._call("camera_set_pos", 180, 90)
                await self._call("camera_set_pos", 90, 90)
                await self._call("led", 255, 0, 0)

            case IntentToken.EXCITED:
                for _ in range(int(params.repeat_count)):
                    await self._call("turn_left", _drive_speed * 0.6, None)
                    await self._call("turn_right", _drive_speed * 0.6, None)
                await self._call("camera_up", _tilt_step, None)
                await self._call("camera_down", _tilt_step, None)
                await self._call("light_effect", 5, None)

            case IntentToken.TIRED:
                await self._call("camera_set_pos", 100, 140)
                await self._call("led", 4, 4, 4)

            case IntentToken.ATTENTIVE_LISTEN:
                await self._call("stop", None, None)
                await self._call("camera_set_pos", 90, 85)
                await self._call("led", 16, 16, 16)

            case IntentToken.CELEBRATE:
                for _ in range(int(params.repeat_count)):
                    await self._call("forward", _drive_speed * 0.4, None)
                    await self._call("backward", _drive_speed * 0.4, None)
                await self._call("light_effect", 3, None)
                await self._call("camera_up", _tilt_step, None)
                await self._call("camera_down", _tilt_step, None)

            case IntentToken.APOLOGETIC:
                await self._call("backward", _drive_speed * 0.2, None)
                await self._call("camera_set_pos", 100, 140)
                await self._call("led", 32, 16, 0)
                await self._call("play_beep", None, None)

            case IntentToken.PRESENT:
                await self._call("forward", _drive_speed * 0.3, None)
                await self._call("camera_set_pos", 90, 100)
                await self._call("led", 64, 48, 16)

            case IntentToken.IDLE:
                # Micro-cycle: slow gimbal drift + periodic micro-turn
                _cycle_pan = 85 + int(10 * (hash(str(token)) % 2 - 0.5) * 2)
                await self._call("camera_set_pos", _cycle_pan, (88 + _cycle_pan) % 5 + 88)
                await self._call("led", 4, 2, 0)

        return {"success": True, "token": token.value, "renderer": "boomy"}

    def _describe_mapping(self, token: IntentToken, params: MotionParams) -> dict:
        return {
            "token": token.value,
            "timing_s": params.timing_seconds,
            "speed": params.speed,
            "intensity": params.intensity,
            "easing": params.easing.value,
            "repeat_count": params.repeat_count,
            "limitations": self._get_limitations(token),
        }

    @staticmethod
    def _get_limitations(token: IntentToken) -> list[str]:
        limits = {
            IntentToken.NOD: [
                "gimbal-only nod (no head pitch DOF)",
                "visual effect is camera nod, not head nod",
            ],
            IntentToken.CURIOUS: ["no head-tilt (no roll axis on gimbal)"],
            IntentToken.BASHFUL: ["no head-tilt, no face-blush"],
            IntentToken.SURPRISED: ["no leg jump", "no face expression"],
            IntentToken.ALARMED: ["no arms to recoil"],
            IntentToken.APOLOGETIC: ["no head-bow posture"],
        }
        return limits.get(token, [])
