import { motion } from "framer-motion";
import { AlertTriangle, Clock, Gauge, Repeat, Wrench } from "lucide-react";
import { useEffect, useState } from "react";
import { listIntents } from "../lib/api";
import { useStore } from "../store";

interface IntentDef {
	token: string;
	default_timing_s: number;
	default_speed: number;
	default_intensity: number;
	easing: string;
	repeatable: boolean;
	description: string;
}

export default function ToolsPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const [intents, setIntents] = useState<IntentDef[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		(async () => {
			try {
				const data = (await listIntents()) as {
					intents: IntentDef[];
					count: number;
				};
				setIntents(data.intents);
			} catch {
				setError("Could not fetch tools from backend");
			} finally {
				setLoading(false);
			}
		})();
	}, []);

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="tools-page"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-3 text-zinc-500">
					<AlertTriangle className="h-10 w-10 text-amber-500" />
					<p>Backend offline — connect MCP server to see tools</p>
				</div>
			</div>
		);
	}

	if (loading) {
		return (
			<div
				data-testid="tools-page"
				className="flex items-center justify-center h-full"
			>
				<motion.div
					animate={{ opacity: [0.3, 1, 0.3] }}
					transition={{ repeat: Infinity, duration: 1.5 }}
					className="text-zinc-500"
				>
					Loading tools...
				</motion.div>
			</div>
		);
	}

	return (
		<div data-testid="tools-page" className="p-4 md:p-6 space-y-6">
			<div className="flex items-center gap-3">
				<Wrench className="h-5 w-5 text-amber-500" />
				<h1 className="text-lg font-semibold text-zinc-200">Intent Tools</h1>
				<span className="text-xs text-zinc-600 bg-zinc-800 px-2 py-0.5 rounded-full">
					{intents.length} registered
				</span>
			</div>

			{error && (
				<div className="bg-red-900/20 border border-red-800/50 rounded-lg px-4 py-3 text-sm text-red-400">
					{error}
				</div>
			)}

			{intents.length === 0 && !error && (
				<div className="text-center py-16 text-zinc-500">
					No intent tools registered
				</div>
			)}

			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
				{intents.map((intent, i) => (
					<motion.div
						key={intent.token}
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: i * 0.04 }}
						data-testid={`tool-card-${intent.token}`}
						className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors"
					>
						<div className="flex items-center justify-between mb-2">
							<h3 className="font-medium text-sm text-amber-400 capitalize">
								{intent.token.replace(/_/g, " ")}
							</h3>
							{intent.repeatable && (
								<Repeat className="h-3 w-3 text-zinc-500" />
							)}
						</div>
						<p className="text-xs text-zinc-400 mb-3 line-clamp-2">
							{intent.description || "No description"}
						</p>
						<div className="flex flex-wrap gap-2 text-xs text-zinc-500">
							<span className="flex items-center gap-1 bg-zinc-800 px-2 py-1 rounded">
								<Clock className="h-3 w-3" />
								{intent.default_timing_s}s
							</span>
							<span className="flex items-center gap-1 bg-zinc-800 px-2 py-1 rounded">
								<Gauge className="h-3 w-3" />
								{intent.default_speed.toFixed(1)}
							</span>
							<span className="bg-zinc-800 px-2 py-1 rounded capitalize">
								{intent.easing.replace(/_/g, " ")}
							</span>
							<span className="bg-zinc-800 px-2 py-1 rounded">
								int:{intent.default_intensity.toFixed(1)}
							</span>
						</div>
					</motion.div>
				))}
			</div>
		</div>
	);
}
