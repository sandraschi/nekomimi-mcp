"""assfix 2026-09-19 regression tests: recorder enum-coercion crash, LLM fail-soft, tool renames."""

import asyncio

from nekomimi_mcp.intent.schema import IntentStream, IntentToken
from nekomimi_mcp.stream.recorder import IntentRecorder


def test_record_with_coerced_tokens(tmp_path):
    """IntentStream coerces StrEnum to str; record() must not crash (was AttributeError)."""
    rec = IntentRecorder(db_path=str(tmp_path / "t.db"))
    stream = IntentStream(tokens=[IntentToken("nod")])
    assert all(isinstance(t, str) for t in stream.tokens)  # documents the coercion
    rid = rec.record(stream, "all", [{"renderer": "vrm", "success": True}])
    assert rid > 0
    recs = rec.list_recordings()
    assert len(recs) == 1
    assert recs[0]["tokens"] == ["nod"]


def test_record_accepts_enum_members(tmp_path):
    from nekomimi_mcp.stream.recorder import _token_str

    assert _token_str(IntentToken.NOD) == "nod"
    assert _token_str("nod") == "nod"


def test_llm_probe_fail_soft():
    from nekomimi_mcp.llm import onboarding_status, probe_provider

    probed = asyncio.run(probe_provider("definitely-not-a-provider"))
    assert probed["detected"] is False
    status = asyncio.run(onboarding_status())
    assert set(status) >= {"configured", "provider", "model", "providers", "message"}
    assert isinstance(status["configured"], bool)


def test_skill_preprompt_loads_or_empty():
    from nekomimi_mcp.llm import load_skill_preprompt

    text = load_skill_preprompt()
    assert isinstance(text, str)
    assert load_skill_preprompt("no-such-skill") == ""


def test_primary_tool_names():
    from nekomimi_mcp.server import tool_aliases, tool_names

    names = tool_names()
    assert "express_intent" in names
    assert "list_intents" in names
    assert "shutdown_server" in names
    assert "show_status_card" in names
    assert "show_safety_card" in names
    assert len(names) == 16
    assert "intent_tool" not in names
    assert "intent_tool" in tool_aliases()
    assert len(tool_aliases()) == 13
