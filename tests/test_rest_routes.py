"""REST surface tests (in-process TestClient, no network, no live providers)."""

from starlette.testclient import TestClient

from nekomimi_mcp.prompts import register_prompts
from nekomimi_mcp.server import (
    _register_rest_routes,
    mcp,
    register_resources,
    register_tools,
)

register_tools()
register_resources()
register_prompts(mcp)
_app = mcp.http_app(stateless_http=True)
_register_rest_routes(_app, 11128)
client = TestClient(_app, raise_server_exceptions=False)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status_lists_primary_tools():
    body = client.get("/api/status").json()
    assert "express_intent" in body["tools"]
    assert "intent_tool" not in body["tools"]
    assert body["tool_count"] == len(body["tools"])


def test_skills_and_content():
    body = client.get("/api/skills").json()
    assert body["count"] >= 1
    assert body["skills"][0]["uri"] == "skill://nekomimi-operator"
    r = client.get("/api/skills/nekomimi-operator")
    assert r.status_code == 200
    assert "Intent Tokens" in r.text
    assert client.get("/api/skills/nope").status_code == 404


def test_capabilities_and_diagnostics():
    caps = client.get("/api/capabilities").json()
    assert "skill://nekomimi-operator" in caps["resources"]
    assert "express_intent" in caps["tools"]
    diag = client.get("/api/v1/diagnostics").json()
    assert len(diag["renderers"]) == 4
    assert diag["errors"] == []


def test_llm_endpoints_fail_soft():
    disc = client.get("/api/llm/discover").json()
    assert disc["count"] == 3
    assert {p["name"] for p in disc["providers"]} == {"ollama", "lmstudio", "vllm"}
    ob = client.get("/api/llm/onboarding").json()
    assert isinstance(ob["configured"], bool)
    assert "message" in ob
    models = client.get("/api/llm/models?provider=ollama").json()
    assert models["provider"] == "ollama"
    assert isinstance(models["models"], list)


def test_chat_fallback_emits_intent():
    r = client.post("/api/chat", json={"message": "please do a nod"})
    body = r.json()
    assert r.status_code == 200
    assert body["mode"] == "local-fallback"
    assert body["token"] == "nod"


def test_chat_fallback_guidance():
    body = client.post("/api/chat", json={"message": "hello xyzzy"}).json()
    assert body["mode"] == "local-fallback"
    assert "Ollama" in body["text"]


def test_chat_requires_message():
    assert client.post("/api/chat", json={"message": "  "}).status_code == 400


def test_fleet_apps_lists_self():
    body = client.get("/api/fleet/apps").json()
    assert body["count"] >= 1
    assert body["apps"][0]["name"] == "nekomimi-mcp"
    assert body["apps"][0]["status"] == "online"
