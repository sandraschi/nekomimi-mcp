interface Props { events: string[]; }

export default function Timeline({ events }: Props) {
  return (
    <div style={{ background: "#18181b", borderRadius: 8, padding: 12, maxHeight: 120, overflowY: "auto" }}>
      <div style={{ fontSize: 11, color: "#a1a1aa", marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>
        Intent Stream
      </div>
      {events.length === 0 && (
        <div style={{ fontSize: 12, color: "#52525b" }}>No intents emitted yet — click a token</div>
      )}
      {events.map((ev, i) => (
        <div key={i} style={{ fontSize: 12, color: "#d4d4d8", padding: "2px 0", fontFamily: "monospace" }}>
          {i === 0 ? `> ${ev}` : ev}
        </div>
      ))}
    </div>
  );
}
