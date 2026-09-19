import { AlertTriangle, RotateCcw, ScrollText } from "lucide-react";
import { useState } from "react";
import { API_BASE } from "../lib/api";
import { useStore } from "../store";

export default function LogsPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const [logs, setLogs] = useState<string[]>([
		`[${new Date().toISOString()}] Webapp initialized`,
		`[${new Date().toISOString()}] Connecting to backend at ${API_BASE}`,
	]);
	const [refreshing, setRefreshing] = useState(false);

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="logs-page"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-3 text-zinc-500">
					<AlertTriangle className="h-10 w-10 text-amber-500" />
					<p className="text-sm">Backend offline</p>
				</div>
			</div>
		);
	}

	return (
		<div data-testid="logs-page" className="p-4 md:p-6 space-y-4">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-3">
					<ScrollText className="h-5 w-5 text-amber-500" />
					<h1 className="text-lg font-semibold text-zinc-200">Logs</h1>
				</div>
				<button
					type="button"
					data-testid="logs-refresh"
					disabled={refreshing}
					onClick={async () => {
						setRefreshing(true);
						try {
							const [status, diag] = await Promise.all([
								fetch(`${API_BASE}/api/status`).then((r) => r.json()),
								fetch(`${API_BASE}/api/v1/diagnostics`).then((r) => r.json()),
							]);
							const ts = new Date().toISOString();
							setLogs((prev) =>
								[
									`[${ts}] status: ${status.message || status.status} (up ${status.uptime_seconds}s)`,
									`[${ts}] tools: ${(status.tools || []).length} primaries, renderers: ${(diag.renderers || []).map((r: { name: string }) => r.name).join(", ")}`,
									...prev,
								].slice(0, 100),
							);
						} catch {
							setLogs((prev) =>
								[
									`[${new Date().toISOString()}] refresh failed: backend unreachable`,
									...prev,
								].slice(0, 100),
							);
						} finally {
							setRefreshing(false);
						}
					}}
					className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors disabled:opacity-40"
				>
					<RotateCcw
						className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
					/>
				</button>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
				<div className="bg-zinc-800/50 px-4 py-2 text-xs text-zinc-500 border-b border-zinc-800">
					Event log
				</div>
				<div
					data-testid="logs-list"
					className="p-4 max-h-[60vh] overflow-y-auto font-mono text-xs space-y-1"
				>
					{logs.length === 0 ? (
						<div className="text-zinc-600 text-center py-8">No log entries</div>
					) : (
						logs.map((line, i) => (
							<div key={i} className="text-zinc-400">
								{line}
							</div>
						))
					)}
				</div>
			</div>
		</div>
	);
}
