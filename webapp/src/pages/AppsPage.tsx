import { motion } from "framer-motion";
import { AlertTriangle, ExternalLink, LayoutGrid } from "lucide-react";
import { useEffect, useState } from "react";
import { type FleetApp, getFleetApps } from "../lib/api";
import { useStore } from "../store";

export default function AppsPage() {
	const backendStatus = useStore((s) => s.backendStatus);
	const [apps, setApps] = useState<FleetApp[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		(async () => {
			try {
				setApps(await getFleetApps());
			} catch {
				/* offline */
			} finally {
				setLoading(false);
			}
		})();
	}, []);

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="apps-page"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-3 text-zinc-500">
					<AlertTriangle className="h-10 w-10 text-amber-500" />
					<p>Backend offline — connect MCP server to discover fleet apps</p>
				</div>
			</div>
		);
	}

	return (
		<div data-testid="apps-page" className="p-4 md:p-6 space-y-6">
			<div className="flex items-center gap-3">
				<LayoutGrid className="h-5 w-5 text-amber-500" />
				<h1 className="text-lg font-semibold text-zinc-200">Fleet apps</h1>
				<span className="text-xs text-zinc-600 bg-zinc-800 px-2 py-0.5 rounded-full">
					live discovery via /api/fleet/apps
				</span>
			</div>

			{loading && (
				<div className="flex items-center justify-center py-16">
					<motion.div
						animate={{ opacity: [0.3, 1, 0.3] }}
						transition={{ repeat: Infinity, duration: 1.5 }}
						className="text-zinc-500"
					>
						Discovering apps...
					</motion.div>
				</div>
			)}

			{!loading && apps.length === 0 && (
				<div className="text-center py-16 text-zinc-500">
					<p className="text-sm">No fleet apps discovered</p>
				</div>
			)}

			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
				{apps.map((app, i) => (
					<motion.div
						key={app.name}
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: i * 0.05 }}
						data-testid={`fleet-app-${app.name}`}
						className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
					>
						<div className="flex items-center justify-between mb-2">
							<h3 className="font-medium text-sm text-amber-400">{app.name}</h3>
							<span
								className={`text-xs flex items-center gap-1.5 ${
									app.status === "online" ? "text-green-400" : "text-zinc-500"
								}`}
							>
								<span
									className={`w-2 h-2 rounded-full ${
										app.status === "online" ? "bg-green-500" : "bg-zinc-600"
									}`}
								/>
								{app.status}
							</span>
						</div>
						<p className="text-xs text-zinc-400 mb-3">{app.role}</p>
						<a
							href={app.frontend}
							target="_blank"
							rel="noreferrer"
							className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1 transition-colors"
						>
							<ExternalLink className="h-3 w-3" />
							{app.frontend}
						</a>
					</motion.div>
				))}
			</div>
		</div>
	);
}
