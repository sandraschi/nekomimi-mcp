import { motion } from "framer-motion";
import {
	Activity,
	AlertTriangle,
	BrainCircuit,
	Cpu,
	Rocket,
	X,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import BoomyPanel from "../components/BoomyPanel";
import IntentPanel from "../components/IntentPanel";
import Timeline from "../components/Timeline";
import VRMViewer from "../components/VRMViewer";
import {
	emitIntent,
	getOnboarding,
	listIntents,
	listRenderers,
} from "../lib/api";
import { useStore } from "../store";

const ONBOARDING_DISMISS_KEY = "nekomimi-onboarding-dismissed";

export default function DashboardPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const selectedToken = useStore((s) => s.selectedToken);
	const setSelectedToken = useStore((s) => s.setSelectedToken);
	const intensity = useStore((s) => s.intensity);
	const setIntensity = useStore((s) => s.setIntensity);
	const pushTimeline = useStore((s) => s.pushTimeline);
	const timeline = useStore((s) => s.timeline);

	const [intents, setIntents] = useState<
		{ token: string; label?: string; description: string }[]
	>([]);
	const [renderers, setRenderers] = useState<
		{ name: string; status: string; body_type: string }[]
	>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [onboarded, setOnboarded] = useState(true);
	const [ctaDismissed, setCtaDismissed] = useState(() => {
		try {
			return localStorage.getItem(ONBOARDING_DISMISS_KEY) === "1";
		} catch {
			return false;
		}
	});

	useEffect(() => {
		(async () => {
			try {
				const ob = await getOnboarding();
				setOnboarded(ob.configured);
			} catch {
				/* offline: keep CTA hidden until backend answers */
			}
		})();
	}, []);

	useEffect(() => {
		(async () => {
			try {
				const [intentData, rendererData] = await Promise.all([
					listIntents(),
					listRenderers(),
				]);
				setIntents(
					(
						intentData as { intents: { token: string; description: string }[] }
					).intents.map((i) => ({
						token: i.token,
						label: i.token.charAt(0).toUpperCase() + i.token.slice(1),
						description: i.description,
					})),
				);
				setRenderers(
					(
						rendererData as {
							renderers: { name: string; status: string; body_type: string }[];
						}
					).renderers,
				);
			} catch {
				setError("Failed to load data from backend");
			} finally {
				setLoading(false);
			}
		})();
	}, []);

	const emit = useCallback(
		async (token: string) => {
			try {
				await emitIntent(token, intensity);
				pushTimeline(`${token} @ ${intensity.toFixed(1)} — ok`);
			} catch {
				pushTimeline(`${token} @ ${intensity.toFixed(1)} — failed`);
			}
		},
		[intensity, pushTimeline],
	);

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="dashboard"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-4 text-zinc-500">
					<AlertTriangle className="h-12 w-12 text-amber-500" />
					<p className="text-lg">Backend offline</p>
					<p className="text-sm text-zinc-600">
						Start the MCP server on port 11128
					</p>
				</div>
			</div>
		);
	}

	if (loading) {
		return (
			<div
				data-testid="dashboard"
				className="flex items-center justify-center h-full"
			>
				<motion.div
					animate={{ opacity: [0.3, 1, 0.3] }}
					transition={{ repeat: Infinity, duration: 1.5 }}
					className="text-zinc-500"
				>
					Loading...
				</motion.div>
			</div>
		);
	}

	return (
		<div data-testid="dashboard" className="p-4 md:p-6 space-y-6">
			{error && (
				<div className="bg-red-900/20 border border-red-800/50 rounded-lg px-4 py-3 text-sm text-red-400">
					{error}
				</div>
			)}

			<div
				data-testid="dashboard-hero"
				className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 md:p-6"
			>
				<h1 className="text-xl font-semibold text-zinc-100">
					Nekomimi embodiment layer
				</h1>
				<p className="text-sm text-zinc-400 mt-1 max-w-2xl">
					One intent vocabulary, many bodies. Emit an expressive intent token
					below and every connected renderer — Boomy robot, VRM avatar, and more
					— translates it into its own motion.
				</p>
				<p className="text-sm text-zinc-500 mt-2">
					Quick start: pick a token on the left, tune intensity, press emit.
					Status:{" "}
					<span
						className={
							backendStatus === "connected" ? "text-green-400" : "text-red-400"
						}
					>
						{backendStatus === "connected"
							? "backend connected"
							: "backend offline — start it with `just serve-http`"}
					</span>
				</p>
			</div>

			{!onboarded && !ctaDismissed && backendStatus === "connected" && (
				<div
					data-testid="onboarding-cue"
					className="flex items-center gap-4 bg-red-950/60 border-2 border-red-600 rounded-xl p-4 md:p-5"
				>
					<Rocket className="h-8 w-8 text-red-400 shrink-0" />
					<div className="flex-1 min-w-0">
						<div className="text-sm font-semibold text-red-200">
							Complete onboarding — connect a local LLM
						</div>
						<div className="text-xs text-red-300/80 mt-0.5">
							Chat runs on the offline intent matcher until Ollama, LM Studio,
							or vLLM is reachable. See docs/ONBOARDING.md.
						</div>
					</div>
					<Link
						to="/settings"
						data-testid="onboarding-cta"
						className="shrink-0 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-sm font-medium transition-colors"
					>
						Open Settings
					</Link>
					<button
						type="button"
						aria-label="Dismiss onboarding cue"
						onClick={() => {
							try {
								localStorage.setItem(ONBOARDING_DISMISS_KEY, "1");
							} catch {
								/* no storage */
							}
							setCtaDismissed(true);
						}}
						className="shrink-0 p-1.5 rounded-md text-red-400/70 hover:text-red-200 hover:bg-red-900/50 transition-colors"
					>
						<X className="h-4 w-4" />
					</button>
				</div>
			)}

			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
				<motion.div
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					data-testid="kpi-backend"
					className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
				>
					<div className="flex items-center gap-3">
						<Activity className="h-8 w-8 text-amber-500" />
						<div>
							<div className="text-xs text-zinc-500 uppercase tracking-wider">
								Backend
							</div>
							<div className="text-lg font-semibold mt-0.5">
								{backendStatus === "connected" ? "Online" : "Offline"}
							</div>
						</div>
					</div>
				</motion.div>

				<motion.div
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 0.1 }}
					data-testid="kpi-renderers"
					className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
				>
					<div className="flex items-center gap-3">
						<Cpu className="h-8 w-8 text-blue-500" />
						<div>
							<div className="text-xs text-zinc-500 uppercase tracking-wider">
								Renderers
							</div>
							<div className="text-lg font-semibold mt-0.5">
								{renderers.length}
							</div>
							<div className="text-xs text-zinc-600 mt-0.5">
								{renderers.map((r) => r.name).join(", ") || "None"}
							</div>
						</div>
					</div>
				</motion.div>

				<motion.div
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 0.2 }}
					data-testid="kpi-intents"
					className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
				>
					<div className="flex items-center gap-3">
						<BrainCircuit className="h-8 w-8 text-purple-500" />
						<div>
							<div className="text-xs text-zinc-500 uppercase tracking-wider">
								Intents
							</div>
							<div className="text-lg font-semibold mt-0.5">
								{intents.length}
							</div>
							<div className="text-xs text-zinc-600 mt-0.5">
								Tokens registered
							</div>
						</div>
					</div>
				</motion.div>

				{renderers.map((r, i) => (
					<motion.div
						key={r.name}
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.3 + i * 0.1 }}
						data-testid={`kpi-${r.name}`}
						className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
					>
						<div className="flex items-center gap-3">
							<div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center text-xs font-bold text-zinc-400 uppercase">
								{r.name.slice(0, 2)}
							</div>
							<div>
								<div className="text-xs text-zinc-500 uppercase tracking-wider">
									{r.name}
								</div>
								<div className="text-lg font-semibold mt-0.5 capitalize">
									{r.status}
								</div>
								<div className="text-xs text-zinc-600 mt-0.5">
									{r.body_type}
								</div>
							</div>
						</div>
					</motion.div>
				))}
			</div>

			<div className="flex gap-4 flex-col lg:flex-row">
				<div className="w-full lg:w-72 shrink-0">
					<IntentPanel
						intents={intents}
						selected={selectedToken}
						onSelect={setSelectedToken}
						intensity={intensity}
						onIntensityChange={setIntensity}
						onEmit={emit}
					/>
				</div>

				<div className="flex-1 flex flex-col gap-4">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
							<div className="text-xs text-zinc-500 uppercase tracking-wider mb-3">
								VRM (Canonical)
							</div>
							<VRMViewer token={selectedToken} intensity={intensity} />
						</div>
						<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
							<div className="text-xs text-zinc-500 uppercase tracking-wider mb-3">
								Boomy (yahboom-mcp)
							</div>
							<BoomyPanel token={selectedToken} />
						</div>
					</div>

					<Timeline events={timeline} />
				</div>
			</div>
		</div>
	);
}
