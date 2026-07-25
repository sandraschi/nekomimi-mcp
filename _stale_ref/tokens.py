from enum import StrEnum

from pydantic import BaseModel, Field


class IntentToken(StrEnum):
    # Base expressions
    attending = "attending"
    nod = "nod"
    shake = "shake"
    sulk = "sulk"
    bashful = "bashful"
    amused = "amused"
    playful = "playful"
    confused = "confused"
    retreat = "retreat"
    surprise = "surprise"
    bow = "bow"
    happy = "happy"
    sad = "sad"
    angry = "angry"
    nekomimi = "nekomimi"

    # Anime / V-tuber reaction gestures
    wave = "wave"
    point = "point"
    clap = "clap"
    wink = "wink"
    blush = "blush"
    dizzy = "dizzy"
    sweatdrop = "sweatdrop"
    glare = "glare"
    pout = "pout"
    smug = "smug"
    facepalm = "facepalm"
    shrug = "shrug"
    gasp = "gasp"
    sigh = "sigh"
    stretch = "stretch"
    twirl_hair = "twirl_hair"

    # Idol / performance
    idol_pose = "idol_pose"
    heart_hands = "heart_hands"
    blow_kiss = "blow_kiss"
    curtsy = "curtsy"
    flourish = "flourish"
    spin = "spin"
    jazz_hands = "jazz_hands"

    # Magical / physically impossible
    shapeshift = "shapeshift"
    transform = "transform"
    sparkle = "sparkle"
    vanish = "vanish"
    appear = "appear"
    leap = "leap"
    float = "float"
    shrink = "shrink"
    grow = "grow"


class PhysicalityTier(StrEnum):
    """What kind of physical reality a renderer or token demands.

    Tokens at tier N should only dispatch to renderers that support tier >= N.
    """

    physical = "physical"
    """Real-world feasible: walk, nod, wave. All renderers."""

    animated = "animated"
    """Humanly unrealistic but visually plausible: spin, float, sparkle.
    Requires at least a simulated or 3D renderer."""

    magical = "magical"
    """Defies physics entirely: shapeshift, vanish, grow.
    Only full 3D / VRM renderers can express these."""


class TimingCurve(StrEnum):
    ease_out = "ease_out"
    ease_in = "ease_in"
    ease_in_out = "ease_in_out"
    linear = "linear"
    abrupt = "abrupt"
    hold = "hold"
    bounce = "bounce"


class MotionPhase(BaseModel):
    duration_ms: int = Field(ge=0, description="Duration of this phase in ms")
    easing: TimingCurve = TimingCurve.ease_in_out
    description: str = ""


class IntentTiming(BaseModel):
    anticipation_ms: int = 0
    attack_ms: int = 300
    sustain_ms: int = 500
    decay_ms: int = 300
    anticipation_easing: TimingCurve = TimingCurve.ease_in
    attack_easing: TimingCurve = TimingCurve.ease_out
    sustain_easing: TimingCurve = TimingCurve.hold
    decay_easing: TimingCurve = TimingCurve.ease_out

    @property
    def total_ms(self) -> int:
        return self.anticipation_ms + self.attack_ms + self.sustain_ms + self.decay_ms


class IntentFrame(BaseModel):
    token: IntentToken
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    timing: IntentTiming = Field(default_factory=IntentTiming)
    repeats: int = Field(default=1, ge=1, le=10)
    physicality: PhysicalityTier = PhysicalityTier.physical
    metadata: dict = Field(default_factory=dict)


class ChoreographyStep(BaseModel):
    token: IntentToken
    beat: float = Field(ge=0.0, description="Time in seconds from start of phrase")
    duration: float = Field(default=1.0, ge=0.1, description="Duration in seconds")
    intensity: float = 0.5


class Choreography(BaseModel):
    name: str
    steps: list[ChoreographyStep]
    bpm: float = 120
    loop: bool = False


class IntentStreamEvent(BaseModel):
    frame: IntentFrame
    renderer_name: str
    status: str = "pending"
    error: str | None = None
