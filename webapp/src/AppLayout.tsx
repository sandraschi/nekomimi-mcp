import { AnimatePresence, motion } from "framer-motion";
import {
	BookOpen,
	Bot,
	ChevronLeft,
	ChevronRight,
	HelpCircle,
	Inbox,
	LayoutDashboard,
	LayoutGrid,
	MessageSquare,
	ScrollText,
	Settings,
	Wrench,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { checkHealth } from "./lib/api";
import { useZoom } from "./lib/useZoom";
import { useStore } from "./store";

const NAV_ITEMS = [
	{ to: "/", label: "Dashboard", icon: LayoutDashboard },
	{ to: "/inbox", label: "Inbox", icon: Inbox },
	{ to: "/tools", label: "Tools", icon: Wrench },
	{ to: "/skills", label: "Skills", icon: BookOpen },
	{ to: "/chat", label: "Chat", icon: MessageSquare },
	{ to: "/apps", label: "Apps", icon: LayoutGrid },
	{ to: "/logs", label: "Logs", icon: ScrollText },
	{ to: "/settings", label: "Settings", icon: Settings },
	{ to: "/help", label: "Help", icon: HelpCircle },
];

const POLL_BASE_MS = 5000;
const POLL_MAX_MS = 60000;

export default function AppLayout() {
	const [collapsed, setCollapsed] = useState(false);
	const location = useLocation();
	const navigate = useNavigate();
	const backendStatus = useStore((s) => s.backendStatus);
	const setBackendStatus = useStore((s) => s.setBackendStatus);
	const { zoom, bindZoomKeys } = useZoom();
	const mainRef = useRef<HTMLElement | null>(null);
	const backoffRef = useRef(POLL_BASE_MS);

	useEffect(() => {
		bindZoomKeys(mainRef.current);
	}, [bindZoomKeys]);

	// Health poll with exponential backoff when offline (5s -> 60s max),
	// immediate re-check on success.
	useEffect(() => {
		let timer: ReturnType<typeof setTimeout>;
		let cancelled = false;
		const tick = async () => {
			if (cancelled) return;
			const ok = await checkHealth();
			if (cancelled) return;
			setBackendStatus(ok ? "connected" : "disconnected");
			backoffRef.current = ok
				? POLL_BASE_MS
				: Math.min(POLL_MAX_MS, backoffRef.current * 2);
			timer = setTimeout(tick, backoffRef.current);
		};
		tick();
		return () => {
			cancelled = true;
			clearTimeout(timer);
		};
	}, [setBackendStatus]);

	// Tauri backend-status events (native shell only; no-op on web).
	useEffect(() => {
		let unlisten: (() => void) | undefined;
		(async () => {
			try {
				const { listen } = await import("@tauri-apps/api/event");
				unlisten = await listen<string>("backend-status", (event) => {
					if (event.payload === "ready") {
						backoffRef.current = POLL_BASE_MS;
						checkHealth().then((ok) =>
							setBackendStatus(ok ? "connected" : "disconnected"),
						);
					}
				});
			} catch {
				/* not running inside Tauri */
			}
		})();
		return () => unlisten?.();
	}, [setBackendStatus]);

	// Global shortcut: Ctrl+K jumps to chat.
	useEffect(() => {
		const onKey = (e: KeyboardEvent) => {
			const target = e.target as HTMLElement | null;
			if (e.ctrlKey && (e.key === "k" || e.key === "K")) {
				if (
					target &&
					(target.tagName === "INPUT" || target.tagName === "TEXTAREA")
				) {
					return;
				}
				e.preventDefault();
				navigate("/chat");
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [navigate]);

	const statusDot =
		backendStatus === "connected"
			? "bg-green-500"
			: backendStatus === "disconnected"
				? "bg-red-500"
				: "bg-yellow-500 animate-pulse";

	return (
		<div className="flex h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
			<AnimatePresence>
				<motion.aside
					layout
					transition={{ duration: 0.2, ease: "easeInOut" }}
					className="flex flex-col bg-zinc-900 border-r border-zinc-800 overflow-hidden"
					style={{
						width: collapsed ? 56 : 220,
						minWidth: collapsed ? 56 : 220,
					}}
				>
					<div className="flex items-center justify-between px-3 h-14 border-b border-zinc-800 shrink-0">
						{!collapsed && (
							<span className="font-semibold text-sm text-amber-500 tracking-wide truncate flex items-center gap-2">
								<Bot className="h-4 w-4" />
								nekomimi
							</span>
						)}
						<button
							type="button"
							data-testid="sidebar-collapse"
							onClick={() => setCollapsed(!collapsed)}
							className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
						>
							{collapsed ? (
								<ChevronRight className="h-4 w-4" />
							) : (
								<ChevronLeft className="h-4 w-4" />
							)}
						</button>
					</div>

					<nav className="flex flex-col gap-1 p-2 flex-1 overflow-y-auto">
						{NAV_ITEMS.map((item) => {
							const active =
								item.to === "/"
									? location.pathname === "/"
									: location.pathname.startsWith(item.to);
							return (
								<NavLink
									key={item.to}
									to={item.to}
									data-testid={`nav-${item.label.toLowerCase()}`}
									className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
										active
											? "bg-amber-500/10 text-amber-400"
											: "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
									}`}
								>
									<item.icon className="h-4 w-4 shrink-0" />
									{!collapsed && <span className="truncate">{item.label}</span>}
								</NavLink>
							);
						})}
					</nav>

					{!collapsed && (
						<div className="flex items-center gap-2 px-3 py-3 border-t border-zinc-800 text-xs text-zinc-500">
							<span className={`w-2 h-2 rounded-full ${statusDot}`} />
							{backendStatus === "connected"
								? "Connected"
								: backendStatus === "disconnected"
									? "Offline"
									: "Checking..."}
						</div>
					)}
				</motion.aside>
			</AnimatePresence>

			<div className="flex flex-col flex-1 min-w-0">
				<header className="flex items-center justify-between h-14 px-4 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm shrink-0">
					<div className="flex items-center gap-3">
						<span className="text-sm font-medium text-zinc-200">
							{NAV_ITEMS.find((i) =>
								i.to === "/"
									? location.pathname === "/"
									: location.pathname.startsWith(i.to),
							)?.label || "Dashboard"}
						</span>
					</div>
					<div className="flex items-center gap-3">
						<div className="flex items-center gap-2 text-xs text-zinc-500">
							<span className={`w-2 h-2 rounded-full ${statusDot}`} />
							<span className="hidden sm:inline">
								{backendStatus === "connected"
									? "Backend Online"
									: backendStatus === "disconnected"
										? "Backend Offline"
										: "Connecting..."}
							</span>
						</div>
						<span
							data-testid="ui-zoom"
							className="text-xs text-zinc-600"
							title="UI zoom (Ctrl+scroll, Ctrl+0 resets)"
						>
							{Math.round(zoom * 100)}%
						</span>
						<span className="text-xs text-zinc-600" title="App version">
							v{__APP_VERSION__}
						</span>
					</div>
				</header>

				<main
					ref={(el) => {
						mainRef.current = el;
					}}
					className="flex-1 overflow-y-auto"
					style={{ zoom }}
				>
					<Outlet />
				</main>
			</div>
		</div>
	);
}
