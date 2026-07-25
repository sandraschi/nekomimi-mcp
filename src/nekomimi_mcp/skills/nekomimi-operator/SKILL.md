# nekomimi-operator Skill

## Overview
You control a substrate-independent embodiment layer. Express intent tokens across robot, VRM, and humanoid bodies without knowing which body you're in.

## Intent Tokens (17)
attending, confused, nod, shake, sulk, bashful, amused, surprised, curious, alarmed, excited, tired, attentive_listen, celebrate, apologetic, present, idle

## Motion Parameters
- timing_seconds: Duration (0.1-10.0)
- speed: Speed multiplier (0.0-1.0)
- intensity: Amplitude (0.0-1.0)
- easing: linear, ease_in, ease_out, ease_in_out, snap, bounce
- hesitation: Initial delay (adds thoughtfulness)
- hold_seconds: Sustain end pose

## Available Tools
- intent_tool(token, timing_seconds, speed, intensity, ...) — primary expression
- intent_stream(tokens, ...) — sequence of intents
- list_intents() — see all tokens
- list_renderers() — see connected bodies
- renderer_info(name) — capabilities of a body

## Body Limitations
- Boomy (robot car): No head, no arms. Use shake/excited/celebrate for best effect.
- VRM: Full humanoid. All intents work.
- Reachy Mini: STUB — needs hardware.
- BHL: STUB — needs hardware.

## Best Practice
Lead with gesture: emit intent_tool BEFORE speaking. Hesitation (0.3s) reads as thoughtful.
