# Onboarding — nekomimi-mcp

## What this is for

nekomimi-mcp is a substrate-independent embodiment layer for conversational NPCs. You emit **intent tokens** (nod, curious, celebrate…); every connected body — Boomy robot, VRM avatar, and more — translates them into its own motion. It does **not** include a robot, an avatar model, or an LLM: those live outside this repo and this page tells you how to get them.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | No. Everything runs locally. |
| Free tier? | Yes — Ollama, LM Studio, and all renderers are free. |
| Credit card required? | No. |
| Ongoing cost? | None for software. A Boomy robot (Yahboom Raspbot V2) costs hardware money if you want the physical body — optional. |
| Who bills? | Nobody. Optional hardware vendors bill for their own devices. |

## Prerequisites outside this repo

- **A local LLM** (pick one): [Ollama](https://ollama.com) (port 11434) or [LM Studio](https://lmstudio.ai) (port 1234) with any chat model loaded. Without one, chat runs on the offline intent matcher — intents still emit, but there is no free-form dialogue.
- **Boomy robot (optional)**: Yahboom Raspbot V2 + [yahboom-mcp](https://github.com/sandraschi/yahboom-mcp) on port 10892. Without it, the boomy renderer answers in simulated mode.
- **Resonite avatar (optional)**: Resonite + resonite-mcp on port 10979. Without it, the VRM preview in the webapp still works.

## First-timer setup steps

1. Install Ollama from https://ollama.com and pull a chat model: `ollama pull qwen3:8b` (any chat model works).
2. Start the backend: `just serve-http` (port 11128). Or double-click `start.bat`.
3. Start the webapp: `cd webapp && bun install && bun run dev` (port 11129).
4. Open Settings in the webapp — the Onboarding panel should read **Configured (ollama)**.
5. On the Dashboard, pick the `attending` token and press emit. Boomy (real or simulated) and the VRM preview respond.

See [INSTALL.md](../INSTALL.md) for packaging variants (Tauri app, MCPB bundle).

## Pitfalls

- **LM Studio server not started**: loading a model is not enough — start the local server (port 1234) in LM Studio.
- **Ollama model not pulled**: an empty model list means `ollama pull <model>` first.
- **Port 8000 (vLLM)**: the fleet treats 8000 as reserved; prefer Ollama/LM Studio unless you know why you need vLLM.
- **Boomy unreachable**: without yahboom-mcp on :10892 the boomy renderer simulates. Check the Apps page for live companion status.
- **Silent fallback**: when no provider is detected, chat answers with the offline intent matcher and says so. Check the provider indicator in the chat toolbar (`LLM: ollama` vs `offline intent matcher`).

## Sanity check

- `GET /api/llm/onboarding` returns `"configured": true` with your provider/model.
- Settings → Onboarding panel shows the green **Configured** badge.
- Chat toolbar shows `LLM: <provider>` instead of `offline intent matcher`.
- `express_intent(token="nod")` returns `"success": true`.

## Declared doubles

- **Offline intent matcher** (chat + `POST /api/chat` `mode: "local-fallback"`): keyword intent matching that also emits the matched intent. Declared in the reply payload and in the UI indicator — never presented as an LLM.
- **Mock-until-onboarded: N/A.** This UI shows no sample/fake data anywhere (no mock KPIs, no fake actors), so there are no MOCK badges to clear. Pages show live data or honest empty states. The only first-run cue is the red onboarding banner, which hides once `/api/llm/onboarding` reports configured or once dismissed.
