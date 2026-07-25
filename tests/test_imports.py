"""Basic import and structure tests for nekomimi-mcp."""

from nekomimi_mcp.intent.registry import list_intents
from nekomimi_mcp.intent.schema import EasingCurve, IntentToken, MotionParams
from nekomimi_mcp.renderers import list_renderers
from nekomimi_mcp.renderers.vrm import VrmRenderer
from nekomimi_mcp.safety.drive_guards import DriveGeometryGuard
from nekomimi_mcp.safety.timeout_policy import TimeoutPolicy


def test_intents_exist():
    intents = list_intents()
    assert len(intents) == len(IntentToken)
    assert intents[0]["token"] == "attending"


def test_renderers_registered():
    renderers = list_renderers()
    assert len(renderers) >= 4
    names = [r["name"] for r in renderers]
    assert "boomy" in names
    assert "vrm" in names


def test_motion_params_defaults():
    p = MotionParams()
    assert p.timing_seconds == 1.0
    assert p.speed == 0.5
    assert p.intensity == 0.5
    assert p.easing == EasingCurve.EASE_IN_OUT


def test_easing_curve_values():
    assert EasingCurve.LINEAR.value == "linear"
    assert EasingCurve.BOUNCE.value == "bounce"


def test_intent_token_count():
    assert len(IntentToken) == 17


def test_drive_guard():
    g = DriveGeometryGuard()
    assert not g.check_retreat_safe(0.3)
    assert g.check_retreat_safe(1.0)
    assert not g.should_return


def test_timeout_policy():
    p = TimeoutPolicy()
    p.begin_intent("sulk")


def test_vrm_renderer():
    v = VrmRenderer()
    assert v.can_express(IntentToken.NOD)
    assert v.can_express(IntentToken.SULK)
