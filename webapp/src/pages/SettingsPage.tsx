import {
	AlertTriangle,
	CheckCircle2,
	Cpu,
	Loader2,
	Rocket,
	Server,
	Settings,
	XCircle,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
	API_BASE,
	discoverProviders,
	getOnboarding,
	type LlmProviderState,
	listRenderers,
	type OnboardingState,
} from "../lib/api";
import { useStore } from "../store";

export default function SettingsPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const llmProvider = useStore((s) => s.llmProvider);
	const setLlmProvider = useStore((s) => s.setLlmProvider);
	const llmModel = useStore((s) => s.llmModel);
	const setLlmModel = useStore((s) => s.setLlmModel);
	const availableModels = useStore((s) => s.availableModels);
	const setAvailableModels = useStore((s) => s.setAvailableModels);

	const [renderers, setRenderers] = useState<
		{ name: string; status: string; body_type: string }[]
	>([]);
	const [providers, setProviders] = useState<LlmProviderState[]>([]);
	const [onboarding, setOnboarding] = useState<OnboardingState | null>(null);
	const [probing, setProbing] = useState(true);

	useEffect(() => {
		(async () => {
			try {
				const rendererData = (await listRenderers()) as {
					renderers: { name: string; status: string; body_type: string }[];
				};
				setRenderers(rendererData.renderers || []);
			} catch {
				/* offline */
			}
		})();
	}, []);

	const probeAll = useCallback(async () => {
		setProbing(true);
		try {
			// All provider traffic goes through the backend proxy —
			// the browser never fetches provider ports directly.
			const found = await discoverProviders();
			setProviders(found);
			const detected = found.filter((p) => p.detected);
			const ob = await getOnboarding();
			setOnboarding(ob);

			const savedProvider = localStorage.getItem("nekomimi-llm-provider");
			const savedModel = localStorage.getItem("nekomimi-llm-model");
			const match =
				detected.find((d) => d.name === savedProvider) || detected[0];
			if (match) {
				setLlmProvider(match.name);
				setAvailableModels(match.models);
				if (savedModel && match.models.includes(savedModel)) {
					setLlmModel(savedModel);
				} else if (match.models.length > 0) {
					setLlmModel(match.models[0]);
				}
			}
		} catch {
			/* offline */
		} finally {
			setProbing(false);
		}
	}, [setLlmProvider, setLlmModel, setAvailableModels]);

	useEffect(() => {
		probeAll();
	}, [probeAll]);

	const handleProviderChange = async (name: string) => {
		setLlmProvider(name);
		const def = providers.find((p) => p.name === name);
		if (def) {
			setAvailableModels(def.models);
			if (def.models.length > 0) setLlmModel(def.models[0]);
		}
	};

	const detectedProviders = providers.filter((p) => p.detected);
	const providerStatus: Record<string, "probing" | "detected" | "not_found"> =
		{};
	for (const p of providers) {
		providerStatus[p.name] = probing
			? "probing"
			: p.detected
				? "detected"
				: "not_found";
	}

	return (
		<div data-testid="settings-page" className="p-4 md:p-6 space-y-6 max-w-3xl">
			<div className="flex items-center gap-3">
				<Settings className="h-5 w-5 text-amber-500" />
				<h1 className="text-lg font-semibold text-zinc-200">Settings</h1>
			</div>

			<section className="space-y-3">
				<h2 className="text-xs text-zinc-500 uppercase tracking-wider flex items-center gap-2">
					<Rocket className="h-3.5 w-3.5" />
					Onboarding
				</h2>
				<div
					data-testid="onboarding-panel"
					className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-2"
				>
					<div className="flex items-center justify-between">
						<span className="text-sm text-zinc-400">Local LLM provider</span>
						<span
							className={`text-sm flex items-center gap-1.5 ${
								onboarding?.configured ? "text-green-400" : "text-amber-400"
							}`}
						>
							{onboarding?.configured ? (
								<CheckCircle2 className="h-3.5 w-3.5" />
							) : (
								<AlertTriangle className="h-3.5 w-3.5" />
							)}
							{onboarding?.configured
								? `Configured (${onboarding.provider})`
								: "Not configured"}
						</span>
					</div>
					<p className="text-xs text-zinc-500">
						{onboarding?.message || "Checking for Ollama, LM Studio, or vLLM…"}
					</p>
					<p className="text-xs text-zinc-600">
						First time? See docs/ONBOARDING.md in the repo for setup steps,
						costs, and pitfalls.
					</p>
				</div>
			</section>

			<section className="space-y-3">
				<h2 className="text-xs text-zinc-500 uppercase tracking-wider flex items-center gap-2">
					<Server className="h-3.5 w-3.5" />
					Backend Connection
				</h2>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
					<div className="flex items-center justify-between">
						<span className="text-sm text-zinc-400">URL</span>
						<span className="text-sm text-zinc-200 font-mono">{API_BASE}</span>
					</div>
					<div className="flex items-center justify-between">
						<span className="text-sm text-zinc-400">Status</span>
						<span
							className={`text-sm flex items-center gap-1.5 ${
								backendStatus === "connected"
									? "text-green-400"
									: backendStatus === "disconnected"
										? "text-red-400"
										: "text-yellow-400"
							}`}
						>
							{backendStatus === "connected" ? (
								<CheckCircle2 className="h-3.5 w-3.5" />
							) : (
								<XCircle className="h-3.5 w-3.5" />
							)}
							{backendStatus === "connected"
								? "Connected"
								: backendStatus === "disconnected"
									? "Disconnected"
									: "Checking..."}
						</span>
					</div>
					<div className="flex items-center justify-between">
						<span className="text-sm text-zinc-400">MCP Transport</span>
						<span className="text-sm text-zinc-200 font-mono">HTTP /mcp</span>
					</div>
				</div>
			</section>

			<section className="space-y-3">
				<h2 className="text-xs text-zinc-500 uppercase tracking-wider flex items-center gap-2">
					<Cpu className="h-3.5 w-3.5" />
					Connected Renderers
				</h2>
				{renderers.length === 0 ? (
					<div className="text-sm text-zinc-500 bg-zinc-900 border border-zinc-800 rounded-xl p-4">
						No renderers connected
					</div>
				) : (
					<div className="grid gap-3">
						{renderers.map((r) => (
							<div
								key={r.name}
								className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between"
							>
								<div>
									<div className="text-sm font-medium text-zinc-200 capitalize">
										{r.name.replace(/_/g, " ")}
									</div>
									<div className="text-xs text-zinc-500 mt-0.5">
										{r.body_type}
									</div>
								</div>
								<span
									className={`text-xs flex items-center gap-1.5 ${
										r.status === "connected"
											? "text-green-400"
											: "text-zinc-500"
									}`}
								>
									<span
										className={`w-2 h-2 rounded-full ${
											r.status === "connected" ? "bg-green-500" : "bg-zinc-600"
										}`}
									/>
									{r.status}
								</span>
							</div>
						))}
					</div>
				)}
			</section>

			<section className="space-y-3">
				<h2 className="text-xs text-zinc-500 uppercase tracking-wider">
					Local LLM Providers
				</h2>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
					<div className="grid grid-cols-3 gap-2">
						{providers.map((p) => (
							<div
								key={p.name}
								className={`p-3 rounded-lg border text-sm ${
									providerStatus[p.name] === "detected"
										? "border-green-800/50 bg-green-900/10"
										: providerStatus[p.name] === "probing"
											? "border-yellow-800/50 bg-yellow-900/10"
											: "border-zinc-800 bg-zinc-800/30"
								}`}
							>
								<div className="font-medium text-zinc-300 text-xs">
									{p.name}
								</div>
								<div className="text-xs text-zinc-500">:{p.port}</div>
								<div className="mt-1">
									{providerStatus[p.name] === "probing" ? (
										<Loader2 className="h-3 w-3 text-yellow-400 animate-spin" />
									) : providerStatus[p.name] === "detected" ? (
										<span className="text-xs text-green-400 flex items-center gap-1">
											<CheckCircle2 className="h-3 w-3" /> Detected
										</span>
									) : (
										<span className="text-xs text-zinc-600">Not found</span>
									)}
								</div>
							</div>
						))}
					</div>

					{detectedProviders.length > 0 && (
						<>
							<div className="flex flex-col gap-2">
								<label
									htmlFor="llm-provider-select"
									className="text-xs text-zinc-500"
								>
									Provider
								</label>
								<select
									id="llm-provider-select"
									data-testid="llm-provider-select"
									value={llmProvider}
									onChange={(e) => handleProviderChange(e.target.value)}
									className="bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg px-3 py-2"
								>
									{detectedProviders.map((p) => (
										<option key={p.name} value={p.name}>
											{p.name}
										</option>
									))}
								</select>
							</div>
							<div className="flex flex-col gap-2">
								<label
									htmlFor="llm-model-select"
									className="text-xs text-zinc-500"
								>
									Model
								</label>
								<select
									id="llm-model-select"
									data-testid="llm-model-select"
									value={llmModel}
									onChange={(e) => setLlmModel(e.target.value)}
									className="bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg px-3 py-2"
								>
									{availableModels.map((m) => (
										<option key={m} value={m}>
											{m}
										</option>
									))}
								</select>
							</div>
						</>
					)}

					{detectedProviders.length === 0 && !probing && (
						<div className="flex items-center gap-2 text-amber-500 text-xs bg-amber-500/5 border border-amber-500/20 rounded-lg px-3 py-2">
							<AlertTriangle className="h-3.5 w-3.5 shrink-0" />
							Install Ollama or LM Studio to enable AI features
						</div>
					)}
				</div>
			</section>
		</div>
	);
}
