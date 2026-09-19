interface IntentDef {
	token: string;
	label?: string;
	description: string;
}

interface Props {
	intents: IntentDef[];
	selected: string;
	onSelect: (t: string) => void;
	intensity: number;
	onIntensityChange: (v: number) => void;
	onEmit: (t: string) => void;
}

export default function IntentPanel({
	intents,
	selected,
	onSelect,
	intensity,
	onIntensityChange,
	onEmit,
}: Props) {
	return (
		<div className="flex flex-col gap-3 overflow-y-auto">
			<div className="text-xs text-zinc-500 uppercase tracking-wider">
				Intent Tokens
			</div>

			<div className="flex items-center gap-2">
				<span className="text-xs text-zinc-400 shrink-0">Intensity</span>
				<input
					type="range"
					min="0"
					max="1"
					step="0.1"
					value={intensity}
					onChange={(e) => onIntensityChange(parseFloat(e.target.value))}
					className="flex-1 accent-amber-500"
				/>
				<span className="text-xs text-zinc-500 w-8 text-right">
					{intensity.toFixed(1)}
				</span>
			</div>

			<div className="flex flex-col gap-1">
				{intents.map((it) => (
					<button
						type="button"
						key={it.token}
						onClick={() => {
							onSelect(it.token);
							onEmit(it.token);
						}}
						data-testid={`intent-${it.token}`}
						className={`text-left px-3 py-2 rounded-md text-sm transition-colors ${
							selected === it.token
								? "bg-amber-500/10 border border-amber-500/30 text-amber-400"
								: "bg-transparent border border-zinc-800 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
						}`}
					>
						<div className="font-medium capitalize">
							{it.label || it.token.replace(/_/g, " ")}
						</div>
						<div className="text-xs text-zinc-600 mt-0.5 line-clamp-1">
							{it.description}
						</div>
					</button>
				))}
				{intents.length === 0 && (
					<div className="text-xs text-zinc-600 py-4 text-center">
						No intents loaded
					</div>
				)}
			</div>
		</div>
	);
}
