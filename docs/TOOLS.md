# Tool Reference — nekomimi-mcp

14 primary tools (verb-led). Historic `*_tool` names remain as deprecated
aliases (removed in 0.2.0). All tools return `success` + `message` unless noted.

## Expression

| Tool | Key params | Purpose |
|------|------------|---------|
| `express_intent` | `token`, `renderer?`, `timing_seconds?`, `speed?`, `intensity?`, `easing?`, `hold_seconds?`, `repeat?`, `hesitation?` | Express one intent token on one/all renderers |
| `play_intent_stream` | `tokens[]`, `renderer?`, `loop?` | Ordered intent sequence |
| `retreat_safely` | `check_obstacle?` | LIDAR-guarded retreat with timeout |

## Discovery

| Tool | Purpose |
|------|---------|
| `list_intents` | 17 tokens with default timing (no `success` key — `intents`/`count`/`message`) |
| `list_renderers` | 4 bodies with status (no `success` key) |
| `describe_renderer` | One renderer's capabilities |
| `preview_boomy_mapping` | Intent → Boomy actuator preview |
| `get_safety_status` | Drive guard + timeout policy state |

## Recordings

| Tool | Key params | Purpose |
|------|------------|---------|
| `list_recordings` | `limit?` (1–100) | Recorded streams (no `success` key) |
| `replay_recording` | `recording_id`, `renderers?` | Replay without live hardware |
| `export_recordings` | `path?` | JSONL export |

## Server

| Tool | Key params | Purpose |
|------|------------|---------|
| `get_status` | — | Uptime, tool/alias counts, renderer summary |
| `shutdown_server` | `confirm!`, `delay_seconds?` | Orderly exit (refuses without `confirm=True`) |
| `show_renderers_card` | — | Prefab in-chat card (no output schema — returns a UI object) |

## Prompts and resources

Prompts: `nekomimi_intent_guide`, `nekomimi_character`, `renderer_comparison(topic?)`.
Resources: `skill://nekomimi-operator` (operator SKILL.md).
