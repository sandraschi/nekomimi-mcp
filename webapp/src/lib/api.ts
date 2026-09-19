const API_BASE = "http://127.0.0.1:11128";

let _reqId = 1;

async function mcpCall(
	name: string,
	args: Record<string, unknown> = {},
): Promise<unknown> {
	const id = _reqId++;
	const r = await fetch(`${API_BASE}/mcp`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
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
	const body = await r.json();
	if (body.error) {
		throw new Error(body.error.message || "MCP error");
	}
	const text = body.result?.content?.[0]?.text;
	if (!text) return {};
	return JSON.parse(text);
}

export async function checkHealth(): Promise<boolean> {
	try {
		const r = await fetch(`${API_BASE}/mcp`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				jsonrpc: "2.0",
				id: 0,
				method: "ping",
			}),
			signal: AbortSignal.timeout(3000),
		});
		return r.ok;
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
	return mcpCall("intent_tool", {
		token,
		intensity,
		speed: speed ?? 0.5,
	});
}

export async function getRendererInfo(name: string) {
	return mcpCall("renderer_info", { name }) as Promise<Record<string, unknown>>;
}

export async function getSafetyStatus() {
	return mcpCall("safety_status") as Promise<{
		drive_guard: Record<string, unknown>;
		timeout_policy: Record<string, unknown>;
	}>;
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

export async function probeOllama() {
	try {
		const r = await fetch("http://127.0.0.1:11434/api/tags", {
			signal: AbortSignal.timeout(3000),
		});
		if (!r.ok) return { detected: false, models: [] };
		const data = await r.json();
		return {
			detected: true,
			models: (data.models || []).map((m: { name: string }) => m.name),
		};
	} catch {
		return { detected: false, models: [] };
	}
}

export async function probeLmStudio() {
	try {
		const r = await fetch("http://127.0.0.1:1234/v1/models", {
			signal: AbortSignal.timeout(3000),
		});
		if (!r.ok) return { detected: false, models: [] };
		const data = await r.json();
		return {
			detected: true,
			models: (data.data || []).map((m: { id: string }) => m.id),
		};
	} catch {
		return { detected: false, models: [] };
	}
}

export async function probeVllm() {
	try {
		const r = await fetch("http://127.0.0.1:8000/v1/models", {
			signal: AbortSignal.timeout(3000),
		});
		if (!r.ok) return { detected: false, models: [] };
		const data = await r.json();
		return {
			detected: true,
			models: (data.data || []).map((m: { id: string }) => m.id),
		};
	} catch {
		return { detected: false, models: [] };
	}
}

export { API_BASE };
