from __future__ import annotations

import time
from enum import StrEnum


class IntentState(StrEnum):
    IDLE = "idle"
    ACTIVE = "active"
    TIMED_OUT = "timed_out"
    RECOVERING = "recovering"


class TimeoutPolicy:
    def __init__(self, default_max_duration_s: float = 30.0):
        self._default_max = default_max_duration_s
        self._overrides: dict[str, float] = {
            "sulk": 15.0,
            "tired": 60.0,
            "surprised": 3.0,
        }
        self._states: dict[str, tuple[IntentState, float]] = {}

    def begin_intent(self, token: str) -> IntentState:
        max_dur = self._overrides.get(token, self._default_max)
        self._states[token] = (IntentState.ACTIVE, time.time() + max_dur)
        return IntentState.ACTIVE

    def check_intent(self, token: str) -> IntentState:
        entry = self._states.get(token)
        if not entry:
            return IntentState.IDLE
        state, deadline = entry
        if state == IntentState.ACTIVE and time.time() > deadline:
            self._states[token] = (IntentState.TIMED_OUT, deadline)
            return IntentState.TIMED_OUT
        return state

    def recover_intent(self, token: str) -> None:
        self._states[token] = (IntentState.RECOVERING, time.time())
        _recovery_actions: dict[str, str] = {
            "sulk": "return_to_start_position",
            "tired": "wake_cycle",
            "alarmed": "calm_down_sequence",
        }
        self._recovery_action = _recovery_actions.get(token, "reset_to_idle")

    def end_intent(self, token: str) -> None:
        self._states.pop(token, None)

    def get_recovery_action(self) -> str:
        return getattr(self, "_recovery_action", "reset_to_idle")
