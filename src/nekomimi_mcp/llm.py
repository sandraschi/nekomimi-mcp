"""Local LLM provider proxy (Ollama / LM Studio / vLLM).

All browser traffic goes through the backend — the webapp must never fetch
provider ports directly (fleet glom-on rule). Every probe is fail-soft with a
short timeout; every chat call fails with a declared error, never a hang.

Onboarding "configured" means: at least one local provider answers.
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_S = 3.0
CHAT_TIMEOUT_S = 120.0

PROVIDERS: dict[str, dict] = {
    "ollama": {
        "port": 11434,
        "models_url": "http://127.0.0.1:11434/api/tags",
        "chat_url": "http://127.0.0.1:11434/v1/chat/completions",
    },
    "lmstudio": {
        "port": 1234,
        "models_url": "http://127.0.0.1:1234/v1/models",
        "chat_url": "http://127.0.0.1:1234/v1/chat/completions",
    },
    "vllm": {
        "port": 8000,
        "models_url": "http://127.0.0.1:8000/v1/models",
        "chat_url": "http://127.0.0.1:8000/v1/chat/completions",
    },
}


def _model_names(provider: str, data: dict) -> list[str]:
    try:
        if provider == "ollama":
            return [m["name"] for m in data.get("models", []) if m.get("name")]
        return [m["id"] for m in data.get("data", []) if m.get("id")]
    except (AttributeError, TypeError):
        return []


async def probe_provider(name: str) -> dict:
    """Probe one provider. Never raises — returns detected=False on any failure."""
    cfg = PROVIDERS.get(name)
    if not cfg:
        return {"name": name, "detected": False, "models": [], "port": 0}
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT_S) as client:
            r = await client.get(cfg["models_url"])
            if r.status_code != 200:
                return {"name": name, "detected": False, "models": [], "port": cfg["port"]}
            return {
                "name": name,
                "detected": True,
                "models": _model_names(name, r.json()),
                "port": cfg["port"],
            }
    except Exception as e:
        logger.debug(f"LLM probe {name} failed: {e}")
        return {"name": name, "detected": False, "models": [], "port": cfg["port"]}


async def discover_providers() -> list[dict]:
    """Probe all known providers. Always returns a list, never raises."""
    out = []
    for name in PROVIDERS:
        out.append(await probe_provider(name))
    return out


async def list_models(provider: str) -> list[str]:
    result = await probe_provider(provider)
    return result["models"]


async def chat_completion(
    provider: str,
    model: str,
    messages: list[dict],
    timeout_s: float = CHAT_TIMEOUT_S,
) -> str:
    """OpenAI-compatible chat completion via the named provider. Raises RuntimeError on failure."""
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise RuntimeError(f"Unknown provider '{provider}'. Known: {', '.join(PROVIDERS)}")
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.post(
                cfg["chat_url"],
                json={"model": model, "messages": messages, "stream": False},
            )
            if r.status_code != 200:
                raise RuntimeError(f"{provider} HTTP {r.status_code}: {r.text[:200]}")
            data = r.json()
            return str(data["choices"][0]["message"]["content"])
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"{provider} chat failed: {e}") from e


def load_skill_preprompt(skill_name: str = "nekomimi-operator") -> str:
    """Load a skill SKILL.md as a system preprompt. Returns '' when absent (declared fallback)."""
    doc = Path(__file__).resolve().parent / "skills" / skill_name / "SKILL.md"
    if not doc.exists():
        return ""
    return doc.read_text(encoding="utf-8")


async def agent_chat(
    user_text: str,
    history: list[dict] | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> dict:
    """Skill-first chat: skill SKILL.md becomes the system prompt, then the
    first configured provider answers. Raises RuntimeError when no provider
    is configured (caller falls back to the local intent matcher)."""
    discovered = await discover_providers()
    live = [p for p in discovered if p["detected"]]
    if not live:
        raise RuntimeError("No local LLM provider detected. Start Ollama or LM Studio, then retry.")

    pick = next((p for p in live if p["name"] == provider), live[0])
    use_model = model or (pick["models"][0] if pick["models"] else "")
    if not use_model:
        raise RuntimeError(f"Provider '{pick['name']}' has no models loaded.")

    system = load_skill_preprompt()
    messages = (
        ([{"role": "system", "content": system}] if system else [])
        + (history or [])
        + [{"role": "user", "content": user_text}]
    )
    text = await chat_completion(pick["name"], use_model, messages)
    return {
        "text": text,
        "mode": "live",
        "provider": pick["name"],
        "model": use_model,
        "skill_used": bool(system),
        "message": f"Answered via {pick['name']}/{use_model}",
    }


async def onboarding_status() -> dict:
    """Sanity-check shape for onboarding: configured + which provider/model."""
    discovered = await discover_providers()
    live = [p for p in discovered if p["detected"]]
    first = live[0] if live else None
    return {
        "configured": bool(live),
        "provider": first["name"] if first else None,
        "model": (first["models"][0] if first and first["models"] else None),
        "providers": discovered,
        "message": (
            f"Onboarded via {first['name']}"
            if first
            else "Not onboarded: no local LLM provider detected"
        ),
    }
