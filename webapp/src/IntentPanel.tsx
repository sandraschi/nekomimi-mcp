interface Props {
  intents: { token: string; label: string; description: string }[];
  selected: string;
  onSelect: (t: string) => void;
  intensity: number;
  onIntensityChange: (v: number) => void;
  onEmit: (t: string) => void;
}

export default function IntentPanel({ intents, selected, onSelect, intensity, onIntensityChange, onEmit }: Props) {
  return (
    <div style={{ width: 260, borderRight: "1px solid #27272a", padding: 16, display: "flex", flexDirection: "column", gap: 12, overflowY: "auto" }}>
      <div style={{ fontSize: 11, color: "#a1a1aa", textTransform: "uppercase", letterSpacing: 1 }}>Intent Tokens</div>

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <span style={{ fontSize: 12, color: "#d4d4d8" }}>Intensity</span>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={intensity}
          onChange={(e) => onIntensityChange(parseFloat(e.target.value))}
          style={{ flex: 1 }}
        />
        <span style={{ fontSize: 12, color: "#a1a1aa", width: 30, textAlign: "right" }}>{intensity.toFixed(1)}</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {intents.map((it) => (
          <button
            key={it.token}
            onClick={() => { onSelect(it.token); onEmit(it.token); }}
            style={{
              textAlign: "left",
              padding: "8px 12px",
              border: `1px solid ${selected === it.token ? "#f59e0b" : "#27272a"}`,
              borderRadius: 6,
              background: selected === it.token ? "#1c1917" : "transparent",
              color: selected === it.token ? "#fbbf24" : "#d4d4d8",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            <div style={{ fontWeight: 500 }}>{it.label || it.token}</div>
            <div style={{ fontSize: 11, color: "#71717a" }}>{it.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
