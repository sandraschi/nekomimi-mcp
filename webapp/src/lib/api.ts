const API_BASE = "http://127.0.0.1:11128";

let _reqId = 1;

/** Parse a FastMCP streamable-HTTP body: SSE `data:` frames carrying JSON-RPC. */
function parseSseJsonRpc(raw: string): unknown {
	const lines = raw.split(/\r?\n/);
	for (const line of lines) {
		const trimmed = line.trim();
		if (!trimmed.startsWith("data:")) continue;
		const payload = trimmed.slice(5).trim();
		if (!payload || payload === "[DONE]") continue;
		try {
			const parsed = JSON.parse(payload) as {
				result?: unknown;
				error?: unknown;
			};
			if (
				parsed &&
				(parsed.result !== undefined || parsed.error !== undefined)
			) {
				return parsed;
			}
		} catch {
			/* keep scanning frames */
		}
	}
	// Fallback: some transports return plain JSON.
	return JSON.parse(raw);
}

async function mcpCall(
	name: string,
	args: Record<string, unknown> = {},
): Promise<unknown> {
	const id = _reqId++;
	const r = await fetch(`${API_BASE}/mcp`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json, text/event-stream",
		},
		body: JSON.stringify({
			jsonrpc: "2.0",
			id,
			method: "tools/call",
			params: { name, arguments: args },
		}),
	});
	if (!r.ok) {
		throw new Error(`MCP call failed: HTTP ${r.status}`);
	}
	const body = (await parseSseJsonRpc(await r.text())) as {
		error?: { message?: string };
		result?: { content?: { text?: string }[] };
	};
	if (body.error) {
		throw new Error(body.error.message || "MCP error");
	}
	const text = body.result?.content?.[0]?.text;
	if (!text) return {};
	return JSON.parse(text);
}

export async function checkHealth(): Promise<boolean> {
	try {
		const r = await fetch(`${API_BASE}/health`, {
			signal: AbortSignal.timeout(3000),
		});
		if (!r.ok) return false;
		const body = await r.json();
		return body.status === "ok";
	} catch {
		return false;
	}
}

export async function listIntents() {
	return mcpCall("list_intents") as Promise<{
		intents: {
			token: string;
			default_timing_s: number;
			default_speed: number;
			default_intensity: number;
			easing: string;
			repeatable: boolean;
			description: string;
		}[];
		count: number;
	}>;
}

export async function listRenderers() {
	return mcpCall("list_renderers") as Promise<{
		renderers: {
			name: string;
			status: string;
			body_type: string;
			capabilities: string[];
		}[];
		count: number;
	}>;
}

export async function emitIntent(
	token: string,
	intensity: number,
	speed?: number,
) {
	return mcpCall("express_intent", {
		token,
		intensity,
		speed: speed ?? 0.5,
	});
}

export async function getRendererInfo(name: string) {
	return mcpCall("describe_renderer", { name }) as Promise<
		Record<string, unknown>
	>;
}

export async function getSafetyStatus() {
	return mcpCall("get_safety_status") as Promise<{
		drive_guard: Record<string, unknown>;
		timeout_policy: Record<string, unknown>;
	}>;
}

export async function listRecordings(limit = 20) {
	return mcpCall("list_recordings", { limit }) as Promise<{
		recordings: {
			id: number;
			renderer: string;
			tokens: string[];
			timestamp: number;
		}[];
		count: number;
	}>;
}

export async function replayRecording(recordingId: number) {
	return mcpCall("replay_recording", { recording_id: recordingId });
}

export async function getSkills() {
	try {
		const r = await fetch(`${API_BASE}/api/skills`);
		if (r.ok) return await r.json();
	} catch {
		/* fallback */
	}
	return { skills: [], count: 0 };
}

export async function getSkillContent(name: string): Promise<string> {
	try {
		const r = await fetch(`${API_BASE}/api/skills/${name}`);
		if (r.ok) return await r.text();
	} catch {
		/* fallback */
	}
	return "";
}

export interface LlmProviderState {
	name: string;
	port: number;
	detected: boolean;
	models: string[];
}

export async function discoverProviders(): Promise<LlmProviderState[]> {
	try {
		const r = await fetch(`${API_BASE}/api/llm/discover`, {
			signal: AbortSignal.timeout(10000),
		});
		if (!r.ok) return [];
		const data = await r.json();
		return (data.providers || []).map(
			(p: {
				name: string;
				port: number;
				detected: boolean;
				models: string[];
			}) => ({
				name: p.name,
				port: p.port,
				detected: p.detected,
				models: p.models || [],
			}),
		);
	} catch {
		return [];
	}
}

export interface OnboardingState {
	configured: boolean;
	provider: string | null;
	model: string | null;
	message: string;
}

export async function getOnboarding(): Promise<OnboardingState> {
	try {
		const r = await fetch(`${API_BASE}/api/llm/onboarding`, {
			signal: AbortSignal.timeout(10000),
		});
		if (r.ok) return (await r.json()) as OnboardingState;
	} catch {
		/* offline */
	}
	return {
		configured: false,
		provider: null,
		model: null,
		message: "Backend offline",
	};
}

export interface ChatReply {
	success: boolean;
	mode: "live" | "local-fallback";
	text: string;
	provider?: string | null;
	model?: string | null;
	token?: string;
}

export async function backendChat(
	message: string,
	history: { role: string; content: string }[] = [],
): Promise<ChatReply> {
	const r = await fetch(`${API_BASE}/api/chat`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ message, history }),
	});
	if (!r.ok) {
		throw new Error(`Chat failed: HTTP ${r.status}`);
	}
	return (await r.json()) as ChatReply;
}

export interface FleetApp {
	name: string;
	role: string;
	backend: string;
	frontend: string;
	status: string;
}

export async function getFleetApps(): Promise<FleetApp[]> {
	try {
		const r = await fetch(`${API_BASE}/api/fleet/apps`, {
			signal: AbortSignal.timeout(8000),
		});
		if (r.ok) {
			const data = await r.json();
			return data.apps || [];
		}
	} catch {
		/* offline */
	}
	return [];
}

export { API_BASE };
