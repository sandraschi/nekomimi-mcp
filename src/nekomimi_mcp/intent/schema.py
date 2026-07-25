from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EasingCurve(StrEnum):
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    SNAP = "snap"
    BOUNCE = "bounce"
    CUSTOM = "custom"


class IntentToken(StrEnum):
    ATTENDING = "attending"
    CONFUSED = "confused"
    NOD = "nod"
    SHAKE = "shake"
    SULK = "sulk"
    BASHFUL = "bashful"
    AMUSED = "amused"
    SURPRISED = "surprised"
    CURIOUS = "curious"
    ALARMED = "alarmed"
    EXCITED = "excited"
    TIRED = "tired"
    ATTENTIVE_LISTEN = "attentive_listen"
    CELEBRATE = "celebrate"
    APOLOGETIC = "apologetic"
    PRESENT = "present"
    IDLE = "idle"


class MotionParams(BaseModel):
    timing_seconds: float = Field(
        default=1.0, ge=0.1, description="Duration of the gesture in seconds"
    )
    hesitation_seconds: float = Field(
        default=0.0, ge=0.0, description="Initial delay before motion starts"
    )
    hold_seconds: float = Field(default=0.0, ge=0.0, description="How long to sustain end posture")
    easing: EasingCurve = Field(
        default=EasingCurve.EASE_IN_OUT, description="Easing curve for the motion"
    )
    speed: float = Field(default=0.5, ge=0.0, le=1.0, description="Speed multiplier (0=min, 1=max)")
    intensity: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Amplitude/intensity of the gesture"
    )
    repeat_count: int = Field(
        default=1, ge=1, le=10, description="Number of repetitions for cyclic gestures"
    )
    custom_params: dict[str, float | str | bool] | None = Field(
        default=None, description="Per-renderer overrides"
    )

    model_config = ConfigDict(use_enum_values=True)


class IntentStream(BaseModel):
    tokens: list[IntentToken] = Field(description="Ordered sequence of intent tokens to execute")
    params: MotionParams = Field(
        default_factory=MotionParams, description="Default motion parameters for all tokens"
    )
    per_token_params: dict[str, MotionParams] | None = Field(
        default=None, description="Per-token parameter overrides"
    )
    loop: bool = Field(default=False, description="Whether to loop the stream")
    renderer: str | None = Field(
        default=None, description="Target renderer, or None for all registered"
    )
    model_config = ConfigDict(use_enum_values=True)
