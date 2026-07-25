interface Props { events: string[]; }

export default function Timeline({ events }: Props) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-3 max-h-[120px] overflow-y-auto">
      <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1.5">
        Intent Stream
      </div>
      {events.length === 0 && (
        <div className="text-xs text-zinc-600">No intents emitted yet — click a token</div>
      )}
      {events.map((ev, i) => (
        <div
          key={i}
          className="text-xs text-zinc-400 py-0.5 font-mono"
        >
          {i === 0 ? `> ${ev}` : ev}
        </div>
      ))}
    </div>
  );
}
