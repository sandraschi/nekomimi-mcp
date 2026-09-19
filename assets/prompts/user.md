# nekomimi-mcp — User Guide and Tutorials

Welcome. This guide teaches you to operate nekomimi-mcp from zero to fluent:
setup, first gestures, per-body technique, sequences, recordings, chat,
troubleshooting, and migration. Keep the system prompt beside it — that is the
contract; this is the practice.

## Tutorial 1 — First contact (five minutes)

Start the backend (`just serve-http`) and open the dashboard (:11129). You
see the hero, live KPIs, the intent panel, and two previews (VRM, Boomy).
Pick `attending`, leave intensity at 0.5, press emit. Both previews respond
and the Timeline logs the expression. That is the whole loop: token in,
motion out, everywhere at once. Try `nod` with repeat 3, then `surprised` at
intensity 0.9. Notice how hesitation 0.3 makes the next response feel
considered rather than scripted.

## Tutorial 2 — Tool calls from a client

List the vocabulary: `list_intents()` returns 17 tokens with default timing,
speed, intensity, easing, and repeatability. Inspect a body:
`describe_renderer(name="boomy")` shows capabilities, status, and limits.
Express: `express_intent(token="curious", speed=0.6)`. Target one body:
`express_intent(token="celebrate", renderer="vrm")`. Every response carries
`success`, per-renderer results, timing echo, and a human `message` — show the
message to users, log the rest.

## Tutorial 3 — Sequences that read as behavior

Single tokens are words; streams are sentences. `play_intent_stream(tokens=
["surprised", "curious", "attending"])` greets novelty the way animals do:
startle, inspect, settle. `["confused", "attentive_listen", "nod"]` is active
listening. `["excited", "celebrate", "idle"]` closes a success. Keep streams
to 2–4 tokens; longer reads as fidgeting. Never stream `sulk` — persistent
intents manage their own timeout and looping them fights the safety policy.

## Tutorial 4 — Per-body technique

Boomy (robot car, no head/arms/face): think in drives, gimbal, LED, and beeps.
`shake` reads clearly (body sway). `excited` (circles) and `celebrate`
(spins) are the crowd-pleasers. `nod` is gimbal-only — degraded, avoid for
emphasis. Preview anything first: `preview_boomy_mapping(token="nod")` shows
the concrete yahboom calls plus limitations, so you never promise what the
body cannot do. LED color takes three channels; the mapping preview shows the
exact values.

VRM (full humanoid): everything works. Use the whole range — `bashful`
aversion, `present` holds, `attentive_listen` freezes. The webapp preview is
pose-only (no animation playback yet), so judge composition, not motion flow.

Reachy Mini and BHL (STUBs): no hardware path exists. They simulate so your
pipelines, recordings, and tests stay green. Say simulated, always.

## Tutorial 5 — Recordings and regression

Every expression stores to SQLite with renderer results. Open Inbox: each row
shows id, renderer, token chain, and timestamp, with Replay per row. Workflow:
develop a greeting stream against sim, replay it after every change, compare
results. `replay_recording(recording_id=3, renderers=["vrm"])` isolates one
body. `export_recordings(path="data/intents_export.jsonl")` hands history to
external analysis. Delete `src/data/intents.db` to reset history entirely.

## Tutorial 6 — Chat that gestures

With Ollama or LM Studio running, chat is skill-first: the operator skill
becomes the system prompt and the model answers through `POST /api/chat`.
Without a provider, the same endpoint falls back to the offline intent
matcher (`mode: "local-fallback"`) — it still emits matched intents, and says
so. Teach users the indicator: `LLM: ollama` means full dialogue;
`offline intent matcher` means keywords-only. Onboarding (Settings panel,
`GET /api/llm/onboarding`, red dashboard cue) walks first-timers to a working
provider. For raw provider access, `POST /api/llm/chat` proxies any
configured backend, JSON or SSE (`stream: true`).

## Tutorial 7 — Safety in practice

`retreat_safely(check_obstacle=True)` checks LIDAR before reversing and times
out into the wounded-dignity return. `get_safety_status()` shows guard state
(range, retreat flag) at any time. Persistent states (`sulk` 15s, `tired`
60s) recover by themselves — do not re-emit to extend them; start a new
expression instead. If a retreat ever looks wrong, it is always safer to emit
`idle` and re-plan than to chain more motion.

## Tutorial 8 — REST cookbook

Health: `GET /health` (launcher + dashboard dot). Status:
`GET /api/status` (uptime, tool counts). Skills: `GET /api/skills` and
`/api/skills/nekomimi-operator` (the skill text the chat uses). Capabilities:
`GET /api/capabilities` (tools, aliases, prompts, resources, ports).
Diagnostics: `GET /api/v1/diagnostics` (versions, renderers, error list).
Fleet: `GET /api/fleet/apps` (self + live companions). Shutdown:
`POST /api/shutdown` (also `shutdown_server(confirm=True)` over MCP).

## Tutorial 9 — Inbox, Apps, Logs, Settings tour

Dashboard: hero, KPIs, intent panel, VRM + Boomy previews, timeline. Inbox:
recordings with replay. Tools: all 17 tokens with timing chips. Skills: the
operator SKILL.md rendered. Chat: personalities, example prompts, export,
clear, provider indicator. Apps: live fleet discovery (green = reachable).
Logs: backend stream. Settings: connection, renderers, providers, models,
onboarding panel. Help: concepts, shortcuts (Ctrl+K chat, Ctrl+scroll zoom,
Ctrl+0 reset, Enter send).

## Example dialogues

Greeting: user "hello!" → `express_intent(token="excited")` → "Hey! Good to
see you — what's on your mind?" Thinking: user asks a hard question →
`express_intent(token="confused", hesitation_seconds=0.3)` → work, then
`attending` → answer. Apology: model error → `express_intent(token=
"apologetic")` → "My mistake — let me redo that." Success: task done →
`play_intent_stream(tokens=["excited", "celebrate", "idle"])` → summary.
Alarm: unexpected input → `express_intent(token="surprised")` → assess →
`curious` → engage, or `alarmed` + `retreat_safely()` for real hazards.

## Troubleshooting scenarios

Chat says offline matcher but Ollama runs: is the Ollama server serving
(`ollama list`)? LM Studio: is the local server toggled on (loading a model
is not serving)? Settings shows per-provider status — trust it over memory.
Boomy simulates unexpectedly: yahboom-mcp down on :10892? Apps page shows
live companion state. Tools page empty with backend online: the browser must
send `Accept: application/json, text/event-stream` (the app's client does;
raw curl needs `-H`). Port clash on 11128: the launcher clears it; manually
kill the owner. Lost history: recordings live in SQLite, not memory — check
Inbox, not chat. Slow chat: first LLM load compiles; later turns are fast.

## Migration: verb-led names (0.2.0)

Historic `*_tool` names (`intent_tool`, `list_intents_tool`, …) are deprecated
aliases. New code uses `express_intent`, `play_intent_stream`, `list_intents`,
`list_renderers`, `describe_renderer`, `preview_boomy_mapping`,
`get_safety_status`, `retreat_safely`, `list_recordings`, `replay_recording`,
`export_recordings`, `get_status`, `shutdown_server`, `show_renderers_card`.
Update saved prompts, skills, and Claude Desktop snippets; aliases vanish in
0.2.0.

## FAQ

Do I need the robot? No — sim renderers keep everything working. Do I need an
LLM? No — the offline matcher emits intents from keywords. Does it cost
money? No — all software is local and free; only optional hardware costs.
Can one call move two bodies? Yes — omit `renderer` to address all
registered bodies at once. Where is history? SQLite + Inbox page. How do I
reset? Delete the db file. Which transport for Claude Desktop? stdio. For the
webapp? HTTP :11128. Why did my stream look drunk? More than 4 tokens, or a
persistent token looped — shorten it. Why is VRM static? Pose-only preview;
positions are correct, motion playback is roadmap.

## Tutorial 10 — Ollama, step by step

Install from ollama.com (Windows installer, no admin needed). Open a
terminal: `ollama pull qwen3:8b` (about 5 GB; smaller `qwen3:4b` works on
thin machines). `ollama list` must show the model. The server is automatic —
`http://127.0.0.1:11434/api/tags` should answer. Refresh Settings: the
Ollama card turns green with your model listed; pick it in the Model
dropdown. Chat now answers live with the operator skill as its system
prompt. If the card stays grey, the Ollama app is not running — start it
from the Start menu. Corporate VPNs sometimes block loopback strangely;
disconnect to test, then add an exception.

## Tutorial 11 — LM Studio, step by step

Install LM Studio, download any chat model (Qwen, Llama, Mistral — 8B and
under for 16 GB RAM), LOAD it (sidebar), then start the server: the power
icon → Server tab → Start Server (port 1234). Loading without starting is
the number-one LM Studio pitfall — the model list stays empty until the
server runs. Refresh Settings: green card, models listed. LM Studio serves
OpenAI-compatible endpoints, so chat, history, and system preprompts work
identically to Ollama. Larger context models give better multi-turn memory;
smaller ones answer faster on reflection-heavy personalities.

## Tutorial 12 — vLLM (advanced, optional)

vLLM serves OpenAI-compatible chat on :8000 with high throughput on strong
GPUs. Note the fleet reserves port 8000 — only choose vLLM when you know you
need its batching. Serve any HF chat model with `--host 127.0.0.1 --port
8000`, confirm `/v1/models` answers, refresh Settings. Everything downstream
(chat, onboarding, provider indicator) treats it like the others. If the
port is taken, move vLLM — never move nekomimi.

## Tutorial 13 — Boomy hardware bring-up

Charge and power the Raspbot V2. Join it to your LAN (phone hotspot works for
demos). Install and start yahboom-mcp; confirm its health endpoint answers on
:10892. Set `NEKOMIMI_YAHBOOM_URL` if the robot lives elsewhere. In the
nekomimi dashboard, `describe_renderer(name="boomy")` must read connected —
if it reads simulated, the URL is wrong or yahboom-mcp is down. Calibrate:
`attending` centers the gimbal; `excited` at 0.4 sweeps LED and drive;
`curious` at low speed tests approach; `retreat_safely` with a spotter tests
reverse. Keep first sessions slow (speed ≤ 0.4) until you trust the floor.
Record a baseline stream per token — that is your hardware regression pack.

## Tutorial 14 — Easing choreography

Easing is the difference between robotic and alive. `snap` for alerts and
affirmations (`nod` + snap reads decisive). `ease_in_out` (default) for
everything social. `bounce` for `amused` and `celebrate` only — elsewhere it
reads as a glitch. `linear` for machine-like patrol motion on Boomy.
`ease_in` for approaches (`curious`), `ease_out` for settles (`attending`
after a stream). Choreograph: enter with ease_in, hold, exit with ease_out.
Never mix bounce and snap in one stream.

## Tutorial 15 — Multi-body shows

Unison beats (all bodies, renderer omitted) for hellos and finales; feature
beats (one renderer) for verses. Stagger starts 0.3–0.5s so motion overlaps.
Script example: all-`excited` (hello), vrm-`curious` (verse), boomy-`shake`
(punchline), all-`celebrate` (finale), all-`idle` (house lights). Rehearse in
sim, record the baseline, replay on hardware day. End every body on `idle` —
frozen mid-gesture reads as crashed hardware.

## Tutorial 16 — Long-running ambience

For installations, loop `["idle"]` at intensity 0.2–0.3 and inject
`attentive_listen` holds when presence is detected, `nod` on interaction.
Keep CPU trivial (one call per beat, timing ≥ 2s). Log to Timeline, export
JSONL nightly, rotate the db monthly. Never loop persistent tokens.

## Tutorial 17 — Regression workflow end to end

Record golden streams (greeting, apology, success, retreat) and note their
ids. After any server/renderer change: `replay_recording` each id, diff
`results_json` against stored, investigate diffs before shipping. Add new
goldens when adding tokens or bodies. Export JSONL into version control
alongside releases so regressions bisect cleanly.

## Tutorial 18 — JSONL analysis

Each line: `{id, renderer, tokens, params, results, timestamp}`. Count token
frequency to find overused gestures. Join timestamps to find dead hours.
Diff `params` across replays to catch default changes. Plot intensity over
time to see show arcs. The schema is stable and additive — parsers written
today keep working.

## Tutorial 19 — Alias migration runbook

Inventory: grep configs, prompts, and skills for `_tool"` and `_tool(`.
Replace per the migration table (Tutorial: migration section). Keep one
legacy client on aliases as a canary. Switch the webapp first (it is
deployed with the server), then saved Claude snippets, then skills. Verify
with `GET /api/capabilities` (aliases listed separately) and a replay of a
golden stream. Delete nothing until 0.2.0 ships.

## Tutorial 20 — Tauri app daily use

Install the NSIS build (current-user). The app spawns its backend, opens the
dashboard, and kills backend processes on upgrade/uninstall via hooks. Logs
live in the app log dir (`backend-spawn.log`). Ctrl+scroll zooms (persisted);
Ctrl+0 resets. The app is offline-capable except LLM chat, which needs your
local provider running — same onboarding, same indicator.

## Dialogue library (twenty)

Bedtime: tired at 0.3, then idle loop. Morning: excited 0.8, attending.
Meeting start: attentive_listen hold 10, nod on names. Meeting end:
celebrate 0.5, idle. Bad news: surprised, concerned attending, slow nod.
Good news: excited, celebrate. Confusion: confused + hesitation, then curious.
Thanks: bashful, nod repeat 2. Welcome: present hold 3, attending. Warning:
surprised, alarmed, retreat. Joke: amused bounce, nod. Story hook: curious
2.5s, amused. Story climax: surprised 0.9. Story end: nod, idle. Question:
attentive_listen, confused 0.3 hesitation. Answer: attending, nod.
Compliment: bashful, excited 0.5. Farewell: present, nod, idle. Emergency:
alarmed, retreat_safely, attending all-clear. First boot: attending, nod,
excited 0.6 — never sulk first.

## Extended FAQ

Which model? Any chat model; 8B is the sweet spot. Faster answers? Smaller
model, shorter history, lower intensity motion (less to wait on). Chat
remembers? History passes per request; the server keeps none (chat history
lives in browser localStorage). Two users? One transport at a time (shared
SQLite). Remote access? Loopback only by design; use Tailscale + SSH
forwarding, never expose :11128. Backup? Copy `src/data/intents.db` and
JSONL exports. Fresh start? Delete the db. Slow first reply? Model load;
watch the provider, not nekomimi. Boomy drifts? Calibrate drive speed down;
check floor traction. LED wrong color? Mappings take r,g,b — verify order in
the preview. VRM looks stiff? Pose-only preview; positions are right.
Recording failed? Disk full or db locked by a second transport — run one.
Replay differs? Renderer improved or hardware moved — that is regression
working. Alias warnings? Migrate per the table before 0.2.0. Port in use?
Launcher clears 11128/11129; kill leftovers manually. Tauri blank? Check
`backend-spawn.log`; confirm backend exe bundled. NSIS upgrade leaves
processes? Hooks kill both exes pre-install; report residuals. Offline
matcher too dumb? Install any provider — that is literally the onboarding
step. SSE confusion? Browser client parses `data:` frames (see api.ts).
Session errors? Use stateless HTTP (default) or stdio for MCP clients.

## Decision tree (chat not working)

Backend down? Start it (`just serve-http`), check `/health`. Provider
missing? Settings → install/start Ollama or LM Studio → rescan. Provider
present but chat fails? Model loaded? (LM Studio: server started?) Timeout?
First load is slow; retry once. Wrong mode? Indicator tells the truth: live
vs fallback. Still stuck? `/api/v1/diagnostics` + Troubleshooting doc, then
file an issue with the diagnostics dump.

## Glossary (user edition)

Token, stream, renderer, sim vs hardware, persistent intent, registry
defaults, recording, replay, export, guard, policy, companion, configured,
fallback, alias, capability, preprompt, onboarding cue, mock (none here —
declared N/A).

## Intent encyclopedia (usage notes per token)

attending: default opener and closer; safe anywhere, any body. confused:
thinking, ambiguity, gentle stall while you compute — pair with hesitation.
nod: agreement currency; spend freely, repeat 2–3 for warmth. shake: refusal
with finality; on BHL it is the only negation, so use it there deliberately.
sulk: dejection with a built-in exit; never loop, never stack, announce
recovery. bashful: compliments, greetings, mistakes; keep intensity low.
amused: humor response; bounce easing or it reads sarcastic. surprised:
novelty and alarm; always follow with curious or attending, never leave it
hanging. curious: the investigation token; slow speed, longer timing.
alarmed: real concern only; pairs with retreat_safely, never played for
laughs. excited: greetings and wins; high speed, watch volume on hardware.
tired: end-of-day only; self-recovers in 60s, do not poke it awake.
attentive_listen: hold while others speak; freezing mid-gesture mid-sentence
is correct here. celebrate: wins only; overuse deflates it — save for real
occasions. apologetic: errors and apologies; follow with attending to show
return. present: showing and offering; hold 3–4s so eyes land. idle: the
seams between everything; loop low and slow, never loud.

## Renderer field guide

Boomy: 30cm of charisma. Drive is differential (forward/back/turns at scaled
speeds), gimbal is pan/tilt camera, LED is r/g/b, speaker does beeps. Best
show tokens: excited circles, celebrate spins, shake sways, surprised freeze
with beep. Avoid: nod (gimbal dip, weak), present (no arms — drive-to plus
camera hold instead). Mind: battery sag slows drives (recalibrate), LED at
full white eats power, beeps carry through walls (warn neighbors).

VRM avatar: full humanoid bone set, perfect mirror of intent. Use for nuance
Boomy cannot do: bashful aversion, apologetic posture, present holds. The
webapp preview is pose-only — rehearse composition there, timing in streams.
In Resonite via resonite-mcp the same tokens drive the live avatar; latency
is network-bound, so lead gestures 0.5s early.

Reachy Mini (STUB): Stewart neck plus antennas is the whole instrument —
head-tilt reads, antenna flick reads, everything else is future. Keep
scripts to attending/curious/nod so they light up on real hardware later.

BHL (STUB): legs and posture only. shake, sulk, alarmed, tired read through
crouch, sway, and weight shift. Arms do not exist; do not choreograph them.

## Parameter masterclass

Think in three knobs: timing (room), speed (energy), intensity (size).
Ceremonial: timing up, speed down, intensity up. Snappy: timing down, speed
up, intensity mid. Intimate: everything down plus hesitation. Easing is
punctuation: snap ends sentences, bounce laughs, ease_in_out breathes.
Hold is a spotlight: 3–6s for present and attentive_listen, never for
surprised. Repeat is emphasis: 2–3 nods agree warmly; 5+ reads as malfunction
except idle loops. Hesitation is thought: 0.3 default-thought, 0.8 deep
thought, 1.5+ reads as frozen — avoid. Record every tuning session and replay
against the golden set; taste drifts, recordings do not.

## Full show scripts

Three-minute booth loop (Boomy): attending 2s, excited circle, curious
approach, shake playfully, celebrate spin, attending; repeat with ±20%
timing jitter via fresh calls (never identical loops — humans notice).
Avatar storytime (VRM): attending (hello), curious (hook), bashful
(character shy), amused (joke), surprised (twist), nod (moral), present
(goodbye hold 4), idle. Companion duet: Boomy excited while VRM holds
present; VRM nod while Boomy shakes (call-and-response); both celebrate;
both idle. Classroom 45 minutes: demo each token once on VRM with students
calling tokens; Inbox replay of the class favorites; export JSONL as the
lesson artifact.

## API cookbook expanded

List intents, pick token, describe the body, preview the mapping, emit,
record-check via list_recordings, replay on second body, export. Pre-flight
any show with get_safety_status. Gate retreats with retreat_safely and read
`action` aloud to spotters. Poll onboarding before chat features. Discover
companions before promising hardware. Capabilities at session start for
agents; skills text for prompts; diagnostics dump for bug reports. Shutdown
with confirm, verify the port frees, never taskkill the daemon.

## Advanced topics

Custom personalities: the chat page ships Assistant, Playful Companion, and
Technical Expert plus a Custom slot. Personalities shape words, never motion
— gesture tables from the system prompt apply under every personality. Write
custom prompts as constraints ("answer in three bullets", "never apologize"),
not as motion scripts; motion stays in tokens. Test a personality against
the golden streams: same tokens must fire for the same triggers regardless of
verbal style.

Multi-user patterns: one transport at a time (shared SQLite). For demos with
several operators, designate one emitter; others watch Inbox live. For
classrooms, rotate the emitter role per exercise and export per-student
JSONL slices by timestamp. Never run two backends against one db file —
second writer corrupts history silently.

Performance: intent calls are sub-100ms sim-side; hardware calls add
yahboom-mcp round-trips (tune LED/drive batching via _call_multi patterns in
custom renderers). Chat latency is provider-bound (first token slow on cold
models). Streams execute sequentially — a 4-token stream at 1.5s each is 6
seconds of show; plan accordingly. SQLite holds tens of thousands of rows
comfortably; export and rotate yearly.

Security posture: loopback-only binds, no auth (single-user box assumption),
no secrets in the repo (only host/port env), shutdown is confirm-gated but
unauthenticated — do not expose :11128 beyond localhost. If remote access is
needed, tunnel (Tailscale/SSH) rather than binding outward. The browser never
touches provider ports directly; all LLM traffic proxies through the backend
with short probe timeouts and a 120s chat ceiling.

Backup and disaster recovery: the irreplaceable artifact is
`src/data/intents.db` plus JSONL exports. Back up the db before upgrades;
restore by replacing the file while the server is stopped. Config lives in
env and fleet-start.config.ps1 — keep those in version control (they are).
Regenerable artifacts (dist/, node_modules/, .venv/) are never backed up.

Contributing intents: propose the token with three use-cases, default
timing/speed/intensity with rationale, per-body mapping notes (or STUB
honesty), three examples.json entries, one golden recording, and docs in
TOOLS.md plus the capability matrix. Contributing renderers: implement
BaseRenderer fully (render, describe, status, stop, idle_tick), register in
renderers/__init__.py, sim-respond to every token, document limits in
describe output, add Apps-page metadata if it is a companion bridge.

Roadmap (honest): VRM animation playback, Reachy Mini hardware path, BHL
hardware path, multi-user transports, cloud-provider chat option alongside
local-first default. Nothing here is promised with a date; issues track each.

Support: file issues with the `/api/v1/diagnostics` dump, the failing
recording id or JSONL slice, backend logs, and browser console output for UI
bugs. Reproduce first via Inbox replay — a replayable bug gets fixed an
order of magnitude faster than a described one.

## Appendix A — token defaults table

attending: timing 1.2, speed 0.4, intensity 0.5, ease_in_out, repeatable no.
confused: 1.8, 0.3, 0.4, ease_in_out, no. nod: 0.8, 0.6, 0.5, ease_out, yes.
shake: 1.0, 0.5, 0.6, ease_in_out, yes. sulk: persistent 15s, 0.2, 0.6,
ease_in, no. bashful: 1.4, 0.3, 0.4, ease_in_out, no. amused: 1.4, 0.6, 0.6,
bounce, yes. surprised: 0.9, 0.8, 0.9, snap, no. curious: 2.0, 0.35, 0.5,
ease_in, no. alarmed: 1.2, 0.8, 0.9, snap, no. excited: 1.2, 0.8, 0.8,
bounce, yes. tired: persistent 60s, 0.2, 0.3, ease_in, no. attentive_listen:
hold-friendly 2.0, 0.2, 0.3, linear, no. celebrate: 1.6, 0.9, 0.9, bounce,
yes. apologetic: 1.6, 0.35, 0.6, ease_in_out, no. present: hold-friendly
2.0, 0.4, 0.6, ease_in_out, no. idle: cyclic 2.0, 0.2, 0.2, ease_in_out, yes.
Overrides clamp to ranges (timing 0.1–10, speed/intensity 0–1, repeat 1–10);
out-of-range values clamp silently, unknown easings fall back to ease_in_out,
unknown tokens error with the valid list.

## Appendix B — endpoint table

GET /health (liveness). GET /api/status (uptime, inventory). GET /api/skills
(skill index). GET /api/skills/{name} (markdown or 404). GET
/api/capabilities (full contract). GET /api/v1/diagnostics (versions,
renderers, errors). POST /api/shutdown (orderly exit). GET /api/llm/discover
(all providers). GET /api/llm/providers (detected). GET /api/llm/models
(?provider=). GET /api/llm/onboarding (configured signal). POST /api/llm/chat
(provider/model/messages/stream). POST /api/chat (skill-first + fallback).
GET /api/fleet/apps (self + companions). POST /mcp (JSON-RPC tools/call with
Accept: application/json, text/event-stream; SSE data frames in reply).

## Appendix C — error catalog

Unknown token: success false, valid list in message — call list_intents.
Unknown renderer: per-renderer error entries, overall success reflects any
success — check renderer_results. Unknown skill: 404 text. Missing chat
message: 400. No provider: 409 with onboarding guidance. Shutdown without
confirm: success false refusal. Port busy: launcher clears; manual taskkill
documented. LIDAR blocked: retreat_allowed false + cower substitute. Stale
lock on db: one transport at a time. SSE parse failure: send the Accept
header. Session errors: use stateless HTTP or stdio.

## Appendix D — environment and files

NEKOMIMI_PORT (11128), NEKOMIMI_TRANSPORT (stdio), HOST (127.0.0.1),
NEKOMIMI_YAHBOOM_URL (:10892), NEKOMIMI_REACHY_HOST. Files: server.py
(entry, transports, routes), tools.py (14 tools + aliases + schemas),
llm.py (provider proxy + onboarding), prompts.py (3 prompts), intent/
(tokens, params, streams, registry), renderers/ (base + boomy/vrm/reachy/bhl),
stream/ (SQLite recorder + player), safety/ (guards + policy), skills/
(operator SKILL.md), webapp/ (9 routes), src-tauri/ (desktop shell),
assets/prompts/ (this file's home), scripts/mcpb-pack.ps1, docs/ (six
guides), tests/ (unit + REST), e2e/ (browser suite).

## Appendix E — version notes and pocket reference (0.1.0)

Emit: express_intent(token, renderer?, speed?, intensity?). Sequence:
play_intent_stream(tokens). Look up: list_intents, describe_renderer.
Preview hardware: preview_boomy_mapping. Safety: get_safety_status,
retreat_safely. History: list_recordings, replay_recording,
export_recordings. Server: get_status, shutdown_server(confirm=True), card.
Health: /health, /api/status, /api/v1/diagnostics. Chat: /api/chat (skill +
fallback), /api/llm/chat (raw proxy). Onboarding: /api/llm/onboarding,
Settings badge, red dashboard cue. Fleet: /api/fleet/apps, Apps page.
Shortcuts: Ctrl+K chat, Ctrl+scroll zoom, Ctrl+0 reset, Enter send. Ports:
11128 backend, 11129 frontend. Golden rule: gesture first, then words; sim
honestly when hardware is absent; matcher honestly when no LLM answers.

This release renamed tools to verb-led primaries with deprecated aliases,
added the REST surface (health through fleet apps), wired the backend LLM
proxy with onboarding signal, added Inbox and Apps pages, Dashboard hero and
onboarding cue, Ctrl+scroll zoom, Tauri backend-status listening with
backoff, Playwright e2e with screenshots, pyright-clean typing, 55% coverage
floor, the docs stack, and this prompt pack. Breaking in 0.2.0: alias
removal. Check CHANGELOG.md per release; replay golden recordings after every
upgrade; keep examples.json contributions coming — every new token or
renderer ships with at least three new entries here, reviewed for real
usefulness, never padded. The pack this file ships in is verified by word
count and entry count before every release, and the verification command is
printed by the pack script so anyone can re-run it independently.
Keep this guide beside the system prompt while operating; together they are
the complete nekomimi-mcp operator manual.
