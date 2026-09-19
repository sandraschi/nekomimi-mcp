import { motion } from "framer-motion";
import {
	AlertTriangle,
	Bot,
	Download,
	Eraser,
	Send,
	Sparkles,
	User,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { emitIntent, listIntents } from "../lib/api";
import { useStore } from "../store";

const PERSONALITIES = [
	{
		id: "assistant",
		label: "Assistant",
		prompt: "You are a helpful assistant for the nekomimi embodiment system.",
	},
	{
		id: "playful",
		label: "Playful Companion",
		prompt:
			"You are a playful cat-eared companion. Respond with warmth, playfulness, and occasional cat-like mannerisms.",
	},
	{
		id: "expert",
		label: "Technical Expert",
		prompt:
			"You are a technical expert in robotics and embodiment systems. Be precise and informative.",
	},
	{
		id: "custom",
		label: "Custom",
		prompt: "",
	},
];

const EXAMPLE_PROMPTS = [
	{ text: "Show me what intents are available", category: "Discover" },
	{ text: "Try the nod intent", category: "Intents" },
	{ text: "Emit a surprised expression", category: "Intents" },
	{ text: "List all connected renderers", category: "Status" },
	{ text: "What can the Boomy robot express?", category: "Boomy" },
	{ text: "Run a playful sequence", category: "Intents" },
];

export default function ChatPage() {
	const chatHistory = useStore((s) => s.chatHistory);
	const addChatMessage = useStore((s) => s.addChatMessage);
	const clearChatHistory = useStore((s) => s.clearChatHistory);
	const backendStatus = useStore((s) => s.backendStatus);

	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [personality, setPersonality] = useState(() => {
		return localStorage.getItem("nekomimi-chat-personality") || "assistant";
	});
	const [intentTokens, setIntentTokens] = useState<string[]>([]);
	const scrollRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		localStorage.setItem("nekomimi-chat-personality", personality);
	}, [personality]);

	useEffect(() => {
		(async () => {
			try {
				const data = (await listIntents()) as { intents: { token: string }[] };
				setIntentTokens(data.intents.map((i) => i.token));
			} catch {
				/* offline */
			}
		})();
	}, []);

	useEffect(() => {
		scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
	}, [chatHistory]);

	const personalityPrompt =
		PERSONALITIES.find((p) => p.id === personality)?.prompt || "";

	const handleSend = useCallback(async () => {
		const text = input.trim();
		if (!text || loading) return;
		setInput("");
		addChatMessage({
			role: "user",
			content: text,
			ts: new Date().toISOString(),
		});
		setLoading(true);

		try {
			const lower = text.toLowerCase().trim();
			const matchedToken = intentTokens.find((t) => lower.includes(t));

			if (matchedToken) {
				const result = await emitIntent(matchedToken, 0.5);
				const msg =
					`Emitted intent: **${matchedToken}**\n\n` +
						(result as { message?: string }).message ||
					JSON.stringify(result, null, 2);
				addChatMessage({
					role: "assistant",
					content: msg,
					ts: new Date().toISOString(),
				});
			} else if (lower.includes("renderer") || lower.includes("hardware")) {
				const ildata = (await listIntents()) as { count: number };
				addChatMessage({
					role: "assistant",
					content:
						`There are **${ildata.count}** intent tokens registered.\n\n` +
						`Available tokens: ${intentTokens.join(", ")}.\n\nSay something like "try the nod intent" to emit one.`,
					ts: new Date().toISOString(),
				});
			} else {
				addChatMessage({
					role: "assistant",
					content:
						`${personalityPrompt}\n\nI can help you explore the nekomimi embodiment system. ` +
						`Try one of the example prompts above, or ask about available intents and renderers.`,
					ts: new Date().toISOString(),
				});
			}
		} catch (e) {
			addChatMessage({
				role: "assistant",
				content: `Error: ${e instanceof Error ? e.message : "Failed to process request"}`,
				ts: new Date().toISOString(),
			});
		} finally {
			setLoading(false);
		}
	}, [input, loading, intentTokens, personalityPrompt, addChatMessage]);

	const handleExport = () => {
		if (chatHistory.length === 0) return;
		const lines = chatHistory.map(
			(m) =>
				`[${m.ts || "?"}] ${m.role === "user" ? "User" : "Assistant"}: ${m.content}`,
		);
		const blob = new Blob([lines.join("\n\n")], { type: "text/plain" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `nekomimi-chat-${Date.now()}.txt`;
		a.click();
		URL.revokeObjectURL(url);
	};

	if (backendStatus === "disconnected") {
		return (
			<div
				data-testid="chat-page"
				className="flex items-center justify-center h-full"
			>
				<div className="flex flex-col items-center gap-3 text-zinc-500">
					<AlertTriangle className="h-10 w-10 text-amber-500" />
					<p>Backend offline</p>
				</div>
			</div>
		);
	}

	return (
		<div data-testid="chat-page" className="flex flex-col h-full bg-zinc-950">
			<div
				data-testid="chat-controls"
				className="flex items-center gap-3 px-4 py-2 border-b border-zinc-800 bg-zinc-900/50 shrink-0"
			>
				<select
					data-testid="personality-select"
					value={personality}
					onChange={(e) => setPersonality(e.target.value)}
					className="bg-zinc-800 text-zinc-200 text-xs border border-zinc-700 rounded-md px-2 py-1.5"
				>
					{PERSONALITIES.map((p) => (
						<option key={p.id} value={p.id}>
							{p.label}
						</option>
					))}
				</select>

				<div className="flex-1" />

				<button
					type="button"
					data-testid="chat-export"
					onClick={handleExport}
					disabled={chatHistory.length === 0}
					className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
				>
					<Download className="h-4 w-4" />
				</button>
				<button
					type="button"
					data-testid="chat-clear"
					onClick={clearChatHistory}
					disabled={chatHistory.length === 0}
					className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
				>
					<Eraser className="h-4 w-4" />
				</button>
			</div>

			<div
				ref={scrollRef}
				data-testid="chat-messages"
				className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
			>
				{chatHistory.length === 0 && (
					<div className="flex flex-col items-center justify-center h-full text-center py-16">
						<Bot className="h-12 w-12 text-zinc-700 mb-4" />
						<p className="text-zinc-400 text-sm mb-6">
							Ask me about nekomimi intents and renderers
						</p>
						<div
							data-testid="example-prompts"
							className="flex flex-wrap gap-2 justify-center max-w-md"
						>
							{EXAMPLE_PROMPTS.map((ex) => (
								<button
									type="button"
									key={ex.text}
									onClick={() => setInput(ex.text)}
									className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors border border-zinc-700/50"
								>
									<Sparkles className="h-3 w-3 text-amber-500" />
									{ex.text}
								</button>
							))}
						</div>
					</div>
				)}

				{chatHistory.map((msg, i) => (
					<motion.div
						key={i}
						initial={{ opacity: 0, y: 8 }}
						animate={{ opacity: 1, y: 0 }}
						className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
					>
						{msg.role === "assistant" && (
							<div className="w-7 h-7 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0 mt-1">
								<Bot className="h-4 w-4 text-amber-400" />
							</div>
						)}
						<div
							className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm ${
								msg.role === "user"
									? "bg-amber-500/15 text-zinc-200 border border-amber-500/20"
									: "bg-zinc-800/70 text-zinc-300 border border-zinc-700/50"
							}`}
						>
							<div className="whitespace-pre-wrap">{msg.content}</div>
						</div>
						{msg.role === "user" && (
							<div className="w-7 h-7 rounded-full bg-zinc-700 flex items-center justify-center shrink-0 mt-1">
								<User className="h-4 w-4 text-zinc-300" />
							</div>
						)}
					</motion.div>
				))}

				{loading && (
					<div className="flex items-center gap-3 text-zinc-500 text-sm px-2">
						<motion.div
							animate={{ opacity: [0.3, 1, 0.3] }}
							transition={{ repeat: Infinity, duration: 1.2 }}
						>
							Thinking...
						</motion.div>
					</div>
				)}
			</div>

			<div className="p-4 border-t border-zinc-800 bg-zinc-900/50 shrink-0">
				<div className="flex gap-3 max-w-4xl mx-auto">
					<input
						data-testid="chat-input"
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === "Enter" && !e.shiftKey) {
								e.preventDefault();
								handleSend();
							}
						}}
						placeholder="Type a message or intent token..."
						className="flex-1 bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-amber-500/50 transition-colors"
					/>
					<button
						type="button"
						data-testid="chat-send"
						onClick={handleSend}
						disabled={!input.trim() || loading}
						className="px-4 py-2.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-400 rounded-xl text-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
					>
						<Send className="h-4 w-4" />
					</button>
				</div>
			</div>
		</div>
	);
}
