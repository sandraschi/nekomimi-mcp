from nekomimi_mcp.intent.schema import EasingCurve, IntentToken, MotionParams

_INTENT_DEFAULTS: dict[IntentToken, MotionParams] = {
    IntentToken.ATTENDING: MotionParams(
        timing_seconds=1.5,
        hesitation_seconds=0.1,
        hold_seconds=3.0,
        easing=EasingCurve.EASE_IN_OUT,
        speed=0.3,
        intensity=0.3,
    ),
    IntentToken.CONFUSED: MotionParams(
        timing_seconds=1.5,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.SNAP,
        speed=0.5,
        intensity=0.6,
        repeat_count=2,
    ),
    IntentToken.NOD: MotionParams(
        timing_seconds=1.2,
        hesitation_seconds=0.05,
        hold_seconds=0.0,
        easing=EasingCurve.EASE_IN_OUT,
        speed=0.4,
        intensity=0.5,
        repeat_count=2,
    ),
    IntentToken.SHAKE: MotionParams(
        timing_seconds=1.0,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.LINEAR,
        speed=0.5,
        intensity=0.6,
        repeat_count=3,
    ),
    IntentToken.SULK: MotionParams(
        timing_seconds=3.0,
        hesitation_seconds=0.3,
        hold_seconds=15.0,
        easing=EasingCurve.EASE_OUT,
        speed=0.2,
        intensity=0.7,
    ),
    IntentToken.BASHFUL: MotionParams(
        timing_seconds=1.0,
        hesitation_seconds=0.2,
        hold_seconds=2.0,
        easing=EasingCurve.EASE_OUT,
        speed=0.3,
        intensity=0.4,
    ),
    IntentToken.AMUSED: MotionParams(
        timing_seconds=1.5,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.BOUNCE,
        speed=0.6,
        intensity=0.6,
        repeat_count=2,
    ),
    IntentToken.SURPRISED: MotionParams(
        timing_seconds=0.8,
        hesitation_seconds=0.0,
        hold_seconds=1.0,
        easing=EasingCurve.SNAP,
        speed=0.8,
        intensity=0.9,
    ),
    IntentToken.CURIOUS: MotionParams(
        timing_seconds=3.0,
        hesitation_seconds=0.3,
        hold_seconds=4.0,
        easing=EasingCurve.EASE_IN,
        speed=0.2,
        intensity=0.4,
    ),
    IntentToken.ALARMED: MotionParams(
        timing_seconds=2.0,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.SNAP,
        speed=0.7,
        intensity=0.8,
    ),
    IntentToken.EXCITED: MotionParams(
        timing_seconds=2.0,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.BOUNCE,
        speed=0.7,
        intensity=0.7,
        repeat_count=3,
    ),
    IntentToken.TIRED: MotionParams(
        timing_seconds=4.0,
        hesitation_seconds=1.0,
        hold_seconds=30.0,
        easing=EasingCurve.EASE_OUT,
        speed=0.1,
        intensity=0.3,
    ),
    IntentToken.ATTENTIVE_LISTEN: MotionParams(
        timing_seconds=0.5,
        hesitation_seconds=0.0,
        hold_seconds=0.0,
        easing=EasingCurve.LINEAR,
        speed=0.1,
        intensity=0.2,
    ),
    IntentToken.CELEBRATE: MotionParams(
        timing_seconds=2.0,
        hesitation_seconds=0.0,
        hold_seconds=0.5,
        easing=EasingCurve.BOUNCE,
        speed=0.8,
        intensity=0.8,
        repeat_count=3,
    ),
    IntentToken.APOLOGETIC: MotionParams(
        timing_seconds=2.0,
        hesitation_seconds=0.5,
        hold_seconds=4.0,
        easing=EasingCurve.EASE_OUT,
        speed=0.2,
        intensity=0.5,
    ),
    IntentToken.PRESENT: MotionParams(
        timing_seconds=3.0,
        hesitation_seconds=0.2,
        hold_seconds=5.0,
        easing=EasingCurve.EASE_IN,
        speed=0.2,
        intensity=0.4,
    ),
    IntentToken.IDLE: MotionParams(
        timing_seconds=30.0,
        hesitation_seconds=0.0,
        hold_seconds=5.0,
        easing=EasingCurve.EASE_IN_OUT,
        speed=0.05,
        intensity=0.1,
    ),
}


def get_default_params(token: IntentToken) -> MotionParams:
    return _INTENT_DEFAULTS.get(token, MotionParams()).model_copy(deep=True)


def list_intents() -> list[dict]:
    return [
        {
            "token": t.value,
            "default_timing_s": round(p.timing_seconds, 1),
            "default_speed": p.speed,
            "default_intensity": p.intensity,
            "easing": p.easing.value if hasattr(p.easing, "value") else str(p.easing),
            "repeatable": p.repeat_count > 1,
            "description": _TOKEN_DESCRIPTIONS.get(t, ""),
        }
        for t, p in _INTENT_DEFAULTS.items()
    ]


_TOKEN_DESCRIPTIONS: dict[IntentToken, str] = {
    IntentToken.ATTENDING: "Orient toward target, focused attention",
    IntentToken.CONFUSED: "Uncertainty, searching, head-cocking",
    IntentToken.NOD: "Affirmative head/body dip",
    IntentToken.SHAKE: "Negative head/body sway",
    IntentToken.SULK: "Dejected retreat with timeout",
    IntentToken.BASHFUL: "Shy aversion, coy retreat",
    IntentToken.AMUSED: "Playful enjoyment, gentle bounce",
    IntentToken.SURPRISED: "Startle response, freeze",
    IntentToken.CURIOUS: "Slow approach, inspect",
    IntentToken.ALARMED: "Fear response, retreat, scan",
    IntentToken.EXCITED: "Eager enthusiasm, rapid motion",
    IntentToken.TIRED: "Low energy droop, slow blink",
    IntentToken.ATTENTIVE_LISTEN: "Frozen listening posture",
    IntentToken.CELEBRATE: "Success expression, high energy",
    IntentToken.APOLOGETIC: "Contrite retreat, submissive",
    IntentToken.PRESENT: "Offer/show object or location",
    IntentToken.IDLE: "Breathing idle, alive micro-motions",
}
