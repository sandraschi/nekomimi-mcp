"""Canonical intent definitions with default timing, physicality tier, and fallback notes."""

from nekomimi_mcp.intent.tokens import IntentTiming, IntentToken, PhysicalityTier, TimingCurve


class IntentDefinition:
    """Metadata, tier, and canonical timing for one intent token."""

    def __init__(
        self,
        token: IntentToken,
        label: str,
        description: str,
        tier: PhysicalityTier = PhysicalityTier.physical,
        canonical_timing: IntentTiming | None = None,
        fallback_note: str = "",
    ):
        self.token = token
        self.label = label
        self.description = description
        self.tier = tier
        self.canonical_timing = canonical_timing or IntentTiming()
        self.fallback_note = fallback_note


LEXICON: dict[IntentToken, IntentDefinition] = {
    IntentToken.attending: IntentDefinition(
        token=IntentToken.attending,
        label="Attending",
        description="Neutral attentive idle posture. Default state between gestures.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            attack_ms=300, sustain_ms=0, decay_ms=0, attack_easing=TimingCurve.ease_out
        ),
        fallback_note="Continuous idle micro-bobbing; not a discrete gesture.",
    ),
    IntentToken.nod: IntentDefinition(
        token=IntentToken.nod,
        label="Nod",
        description="Affirmation, greeting, agreement. Head dips and returns.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=80, attack_ms=150, sustain_ms=200, decay_ms=300
        ),
        fallback_note="Low-DOF: use body yaw oscillation.",
    ),
    IntentToken.shake: IntentDefinition(
        token=IntentToken.shake,
        label="Shake",
        description="Negation, disbelief. Side-to-side head motion.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=80, attack_ms=300, sustain_ms=120, decay_ms=250
        ),
        fallback_note="Repeat loop. Pan-limited: scale step to available range.",
    ),
    IntentToken.sulk: IntentDefinition(
        token=IntentToken.sulk,
        label="Sulk",
        description="Withdrawal, displeasure. Slow retreat with head down.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=500, sustain_ms=2000, decay_ms=300
        ),
        fallback_note="SAFETY: check geometry before backward drive. No path = cower in place.",
    ),
    IntentToken.bashful: IntentDefinition(
        token=IntentToken.bashful,
        label="Bashful",
        description="Embarrassment, coyness. Head turns away and drops.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=150, attack_ms=200, sustain_ms=800, decay_ms=300
        ),
        fallback_note="Turn head away + warm LED. No face: LED color carries emotion.",
    ),
    IntentToken.amused: IntentDefinition(
        token=IntentToken.amused,
        label="Amused",
        description="Light enjoyment, giggle. Small head bobs.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=50, attack_ms=100, sustain_ms=100, decay_ms=240
        ),
        fallback_note="Series of small rapid bobs (giggle pattern), not one large motion.",
    ),
    IntentToken.playful: IntentDefinition(
        token=IntentToken.playful,
        label="Playful",
        description="Invitation, teasing. Energy, spin, bright lights.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=300, sustain_ms=200, decay_ms=200
        ),
    ),
    IntentToken.confused: IntentDefinition(
        token=IntentToken.confused,
        label="Confused",
        description="Uncertainty. Head tilt alternating with look-around.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=100,
            attack_ms=200,
            sustain_ms=400,
            decay_ms=200,
            anticipation_easing=TimingCurve.ease_in,
        ),
    ),
    IntentToken.retreat: IntentDefinition(
        token=IntentToken.retreat,
        label="Retreat",
        description="Fear, defensive withdrawal. Drive backward, head down.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=50, attack_ms=400, sustain_ms=1000, decay_ms=200
        ),
        fallback_note="SAFETY: LIDAR geometry check mandatory. No path = cower in place.",
    ),
    IntentToken.surprise: IntentDefinition(
        token=IntentToken.surprise,
        label="Surprise",
        description="Startle reaction. Sudden upward jerk, brief forward lurch.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=0,
            attack_ms=50,
            sustain_ms=400,
            decay_ms=500,
            attack_easing=TimingCurve.abrupt,
        ),
        fallback_note="Abrupt onset with zero anticipation is the key expressive parameter.",
    ),
    IntentToken.bow: IntentDefinition(
        token=IntentToken.bow,
        label="Bow",
        description="Deep respect, apology. Forward lean with head lowered.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=600, sustain_ms=1000, decay_ms=500
        ),
        fallback_note="Camera tilt full down + short backward drive as proxy.",
    ),
    IntentToken.happy: IntentDefinition(
        token=IntentToken.happy,
        label="Happy",
        description="Joy, positive engagement. Forward lean, bright energy.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=80, attack_ms=200, sustain_ms=400, decay_ms=300
        ),
    ),
    IntentToken.sad: IntentDefinition(
        token=IntentToken.sad,
        label="Sad",
        description="Low energy, disappointment. Head droop, dim.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=300,
            attack_ms=500,
            sustain_ms=1500,
            decay_ms=400,
            anticipation_easing=TimingCurve.ease_in,
        ),
    ),
    IntentToken.angry: IntentDefinition(
        token=IntentToken.angry,
        label="Angry",
        description="Frustration, threat. Forward lunge, red display.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=150, sustain_ms=500, decay_ms=200
        ),
    ),
    IntentToken.nekomimi: IntentDefinition(
        token=IntentToken.nekomimi,
        label="Nekomimi",
        description="Catgirl pose — head tilt, ear flick, playful 'nya' energy.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=80, attack_ms=150, sustain_ms=400, decay_ms=200
        ),
        fallback_note="Tilt gimbal + warm LED + display '^=^'. VRM: head tilt + ear anim.",
    ),
    # ── Anime / V-tuber reaction gestures ──────────────────────────
    IntentToken.wave: IntentDefinition(
        token=IntentToken.wave,
        label="Wave",
        description="Greeting at a distance. Raise hand and wag side to side.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=200, sustain_ms=600, decay_ms=300
        ),
        fallback_note="No arm: tilt gimbal side to side + LED brighten as greeting proxy.",
    ),
    IntentToken.point: IntentDefinition(
        token=IntentToken.point,
        label="Point",
        description="Indicate direction or object. Arm extends with index finger.",
        tier=PhysicalityTier.physical,
        canonical_timing=IntentTiming(
            anticipation_ms=150, attack_ms=250, sustain_ms=800, decay_ms=300
        ),
        fallback_note="No arm: turn camera gimbal toward target + forward lean.",
    ),
    IntentToken.clap: IntentDefinition(
        token=IntentToken.clap,
        label="Clap",
        description="Applause, excitement. Hands brought together repeatedly.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=50, attack_ms=100, sustain_ms=60, decay_ms=100
        ),
        fallback_note="No hands: camera bob + LED flash burst + short drive forward.",
    ),
    IntentToken.wink: IntentDefinition(
        token=IntentToken.wink,
        label="Wink",
        description="Playful one-eye closure. Conspiratorial or flirtatious.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=50, attack_ms=80, sustain_ms=200, decay_ms=100
        ),
        fallback_note="No eyelids: LED flicker on one side + camera tilt.",
    ),
    IntentToken.blush: IntentDefinition(
        token=IntentToken.blush,
        label="Blush",
        description="Embarrassment or affection. Warm cheeks, averted gaze.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=300, sustain_ms=1500, decay_ms=500
        ),
        fallback_note="Deep pink LED + camera look away + tilt down.",
    ),
    IntentToken.dizzy: IntentDefinition(
        token=IntentToken.dizzy,
        label="Dizzy",
        description="Overwhelmed, spinning sensation. Wobble, spiral eyes.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=0, attack_ms=200, sustain_ms=1200, decay_ms=400
        ),
        fallback_note="Continuous slow spin + camera wobble in all axes.",
    ),
    IntentToken.sweatdrop: IntentDefinition(
        token=IntentToken.sweatdrop,
        label="Sweatdrop",
        description="Embarrassed or exasperated reaction. Single sweat bead.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=100, sustain_ms=600, decay_ms=200
        ),
        fallback_note="Display text '汗' + camera tilt + dim cool LED.",
    ),
    IntentToken.glare: IntentDefinition(
        token=IntentToken.glare,
        label="Glare",
        description="Cold stare of disapproval. Half-lidded eyes, no blink.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=100, sustain_ms=2000, decay_ms=200
        ),
        fallback_note="Camera dead centre + red dim LED + stop all idle movement.",
    ),
    IntentToken.pout: IntentDefinition(
        token=IntentToken.pout,
        label="Pout",
        description="Childish displeasure. Protruded lower lip, averted gaze.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=150, attack_ms=200, sustain_ms=1200, decay_ms=300
        ),
        fallback_note="Camera tilt down + turn away slightly + blue LED.",
    ),
    IntentToken.smug: IntentDefinition(
        token=IntentToken.smug,
        label="Smug",
        description="Self-satisfied superiority. Half-smile, raised brow.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=200, sustain_ms=1000, decay_ms=300
        ),
        fallback_note="Camera tilt up + slight turn + warm gold LED.",
    ),
    IntentToken.facepalm: IntentDefinition(
        token=IntentToken.facepalm,
        label="Facepalm",
        description="Dismay at someone's foolishness. Hand meets face.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=80, attack_ms=150, sustain_ms=800, decay_ms=200
        ),
        fallback_note="No arms: camera tilt abruptly down + hold + sigh audio.",
    ),
    IntentToken.shrug: IntentDefinition(
        token=IntentToken.shrug,
        label="Shrug",
        description="I don't know / what can you do. Shoulders lift, palms up.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=250, sustain_ms=600, decay_ms=300
        ),
        fallback_note="Camera tilt + pan alternating + LED pattern for '?'.",
    ),
    IntentToken.gasp: IntentDefinition(
        token=IntentToken.gasp,
        label="Gasp",
        description="Sharp intake of breath in surprise or shock.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=0,
            attack_ms=60,
            sustain_ms=500,
            decay_ms=400,
            attack_easing=TimingCurve.abrupt,
        ),
        fallback_note="Camera jerk up + sudden bright LED + pause.",
    ),
    IntentToken.sigh: IntentDefinition(
        token=IntentToken.sigh,
        label="Sigh",
        description="Resignation or relief. Long exhalation, shoulders drop.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=300, sustain_ms=800, decay_ms=400
        ),
        fallback_note="Slow camera drop + dim + long pause.",
    ),
    IntentToken.stretch: IntentDefinition(
        token=IntentToken.stretch,
        label="Stretch",
        description="Post-idle or waking. Arms up, back arches.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=500, sustain_ms=400, decay_ms=300
        ),
        fallback_note="Camera tilt up + forward lurch + bright warm LED.",
    ),
    IntentToken.twirl_hair: IntentDefinition(
        token=IntentToken.twirl_hair,
        label="Twirl Hair",
        description="Flirtatious or idle hair play. Finger wraps around lock.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=400, sustain_ms=800, decay_ms=300
        ),
        fallback_note="No hair: small gimbal circle + pink LED.",
    ),
    # ── Idol / performance ─────────────────────────────────────────
    IntentToken.idol_pose: IntentDefinition(
        token=IntentToken.idol_pose,
        label="Idol Pose",
        description="Signature idol stance: one hand up, peace sign, sparkle.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=200, sustain_ms=1200, decay_ms=300
        ),
        fallback_note="Camera tilt + bright LED + forward drive stop.",
    ),
    IntentToken.heart_hands: IntentDefinition(
        token=IntentToken.heart_hands,
        label="Heart Hands",
        description="Make a heart shape with fingers above head. K-pop idol staple.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=150, attack_ms=300, sustain_ms=1000, decay_ms=400
        ),
        fallback_note="Display heart + warm pink LED + camera bob.",
    ),
    IntentToken.blow_kiss: IntentDefinition(
        token=IntentToken.blow_kiss,
        label="Blow Kiss",
        description="Blow a kiss toward audience. Hand to mouth, then outward.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=300, sustain_ms=500, decay_ms=200
        ),
        fallback_note="Camera tilt + LED heart blink + forward lurch.",
    ),
    IntentToken.curtsy: IntentDefinition(
        token=IntentToken.curtsy,
        label="Curtsy",
        description="Formal feminine bow. One leg back, deep knee bend.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=400, sustain_ms=800, decay_ms=400
        ),
        fallback_note="Deep camera tilt + backward drive + dim respectful LED.",
    ),
    IntentToken.flourish: IntentDefinition(
        token=IntentToken.flourish,
        label="Flourish",
        description="Dramatic hand or cape motion. Showy, theatrical.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=200, sustain_ms=300, decay_ms=200
        ),
        fallback_note="Quick spin + LED trail effect (fast blink sequence).",
    ),
    IntentToken.spin: IntentDefinition(
        token=IntentToken.spin,
        label="Spin",
        description="Full-body rotation. Joyful or dramatic turn.",
        tier=PhysicalityTier.animated,
        canonical_timing=IntentTiming(
            anticipation_ms=50, attack_ms=600, sustain_ms=200, decay_ms=200
        ),
        fallback_note="Continuous turn_left at high angular speed.",
    ),
    IntentToken.jazz_hands: IntentDefinition(
        token=IntentToken.jazz_hands,
        label="Jazz Hands",
        description="Ta-da! Both hands open, fingers splayed, dramatic reveal.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=150, sustain_ms=800, decay_ms=300
        ),
        fallback_note="Camera up + bright gold LED burst + display '★'.",
    ),
    # ── Magical / physically impossible ─────────────────────────────
    IntentToken.shapeshift: IntentDefinition(
        token=IntentToken.shapeshift,
        label="Shapeshift",
        description="Transform physical form into a different creature or object.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=300, attack_ms=800, sustain_ms=500, decay_ms=400
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite only. Flash LED + restart display.",
    ),
    IntentToken.transform: IntentDefinition(
        token=IntentToken.transform,
        label="Transform",
        description="Magical girl / sentai henshin sequence. Sparkle swirl + new outfit.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=500, attack_ms=1500, sustain_ms=1000, decay_ms=500
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite only. LED strobe + spin.",
    ),
    IntentToken.sparkle: IntentDefinition(
        token=IntentToken.sparkle,
        label="Sparkle",
        description="Shimmering magical particle effect. Eyes light up.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=0, attack_ms=100, sustain_ms=800, decay_ms=300
        ),
        fallback_note="LED rapid twinkle + camera slight bob.",
    ),
    IntentToken.vanish: IntentDefinition(
        token=IntentToken.vanish,
        label="Vanish",
        description="Disappear in a puff of smoke or light. Poof.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=100, attack_ms=200, sustain_ms=100, decay_ms=0
        ),
        fallback_note="LED off + audio pop + camera drop. No actual disappearance.",
    ),
    IntentToken.appear: IntentDefinition(
        token=IntentToken.appear,
        label="Appear",
        description="Materialise from nothing. Reverse of vanish.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=0, attack_ms=100, sustain_ms=300, decay_ms=100
        ),
        fallback_note="LED on suddenly + camera up + display '!'.",
    ),
    IntentToken.leap: IntentDefinition(
        token=IntentToken.leap,
        label="Leap",
        description="Jump high into the air. 3m vertical. Defies gravity.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=150, attack_ms=200, sustain_ms=400, decay_ms=200
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite. Boomy: jerk up + LED.",
    ),
    IntentToken.float: IntentDefinition(
        token=IntentToken.float,
        label="Float",
        description="Hover gently above the ground. Levitation.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=500, sustain_ms=2000, decay_ms=500
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite only. Boomy: tilt up + blue glow LED.",
    ),
    IntentToken.shrink: IntentDefinition(
        token=IntentToken.shrink,
        label="Shrink",
        description="Become smaller. Scale down to a fraction of normal size.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=600, sustain_ms=300, decay_ms=200
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite only. Boomy: retreat + tilt down.",
    ),
    IntentToken.grow: IntentDefinition(
        token=IntentToken.grow,
        label="Grow",
        description="Become larger. Towering presence.",
        tier=PhysicalityTier.magical,
        canonical_timing=IntentTiming(
            anticipation_ms=200, attack_ms=600, sustain_ms=500, decay_ms=200
        ),
        fallback_note="PHYSICAL UNAVAILABLE. VRM/Resonite only. Boomy: forward + tilt up.",
    ),
}
