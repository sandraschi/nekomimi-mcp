import { motion } from "framer-motion";
import { AlertTriangle, Clock, Inbox, Play } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { listRecordings, replayRecording } from "../lib/api";
import { useStore } from "../store";

interface Recording {
	id: number;
	renderer: string;
	tokens: string[];
	timestamp: number;
}

export default function InboxPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const pushTimeline = useStore((s) => s.pushTimeline);
	const [recordings, setRecordings] = useState<Recording[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [replaying, setReplaying] = useState<number | null>(null);

	const load = useCallback(async () => {
		setLoading(true);
		setError("");
		try {
			const data = (await listRecordings(50)) as {
				recordings: Recording[];
			};
			setRecordings(data.recordings || []);
		} catch {
			setError("Could not fetch recordings from backend");
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		load();
	}, [load]);

	const replay = useCallback(
		async (id: number) => {
			setReplaying(id);
			try {
				await replayRecording(id);
				pushTimeline(`replay recording #${id} — ok`);
			} catch {
				pushTimeline(`replay recording #${id} — failed`);
			} finally {
				setReplaying(null);
			}
		},
		[pushTimeline],
	);

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="inbox-page"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-3 text-zinc-500">
					<AlertTriangle className="h-10 w-10 text-amber-500" />
					<p>Backend offline — connect MCP server to see recordings</p>
				</div>
			</div>
		);
	}

	return (
		<div data-testid="inbox-page" className="p-4 md:p-6 space-y-6">
			<div className="flex items-center gap-3">
				<Inbox className="h-5 w-5 text-amber-500" />
				<h1 className="text-lg font-semibold text-zinc-200">
					Recorded intent streams
				</h1>
				<span className="text-xs text-zinc-600 bg-zinc-800 px-2 py-0.5 rounded-full">
					{recordings.length} stored
				</span>
			</div>

			{error && (
				<div className="bg-red-900/20 border border-red-800/50 rounded-lg px-4 py-3 text-sm text-red-400">
					{error}
				</div>
			)}

			{loading && (
				<div className="flex items-center justify-center py-16">
					<motion.div
						animate={{ opacity: [0.3, 1, 0.3] }}
						transition={{ repeat: Infinity, duration: 1.5 }}
						className="text-zinc-500"
					>
						Loading recordings...
					</motion.div>
				</div>
			)}

			{!loading && recordings.length === 0 && !error && (
				<div className="text-center py-16 text-zinc-500">
					<Inbox className="h-8 w-8 mx-auto mb-3 text-zinc-600" />
					<p className="text-sm">No intent streams recorded yet</p>
					<p className="text-xs text-zinc-600 mt-2">
						Emit intents from the Dashboard — every expression is stored here
						for replay and regression testing
					</p>
				</div>
			)}

			<div className="grid gap-3">
				{recordings.map((rec, i) => (
					<motion.div
						key={rec.id}
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: i * 0.03 }}
						data-testid={`recording-${rec.id}`}
						className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-4"
					>
						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 flex-wrap">
								<span className="text-sm font-medium text-zinc-200">
									#{rec.id}
								</span>
								<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-full">
									{rec.renderer}
								</span>
								<span className="text-xs text-zinc-500 flex items-center gap-1">
									<Clock className="h-3 w-3" />
									{new Date(rec.timestamp * 1000).toLocaleString()}
								</span>
							</div>
							<div className="text-xs text-amber-400/90 mt-1.5 font-mono truncate">
								{(rec.tokens || []).join(" → ") || "(empty)"}
							</div>
						</div>
						<button
							type="button"
							data-testid={`replay-${rec.id}`}
							onClick={() => replay(rec.id)}
							disabled={replaying === rec.id}
							className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-400 text-xs transition-colors disabled:opacity-40 shrink-0"
						>
							<Play className="h-3.5 w-3.5" />
							{replaying === rec.id ? "Replaying…" : "Replay"}
						</button>
					</motion.div>
				))}
			</div>
		</div>
	);
}
