interface Props { token: string; }

export default function BoomyPanel({ token }: Props) {
  const tokenEmoji: Record<string, string> = {
    attending: "normal",
    nod: "nod",
    shake: "shake head",
    sulk: "sad",
    bashful: "blush",
    amused: "giggle",
    playful: "playful",
    confused: "confused",
    retreat: "retreat",
    surprise: "surprise",
    bow: "bow",
    happy: "happy",
    sad: "cry",
    angry: "angry",
    nekomimi: "^=^",
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
      {/* Robot body SVG placeholder */}
      <svg width="200" height="200" viewBox="0 0 200 200" style={{ borderRadius: 6 }}>
        {/* Body */}
        <rect x="60" y="90" width="80" height="60" rx="10" fill="#27272a" stroke="#3f3f46" strokeWidth="2" />
        {/* Head (gimbal camera) */}
        <circle cx="100" cy="65" r="25" fill="#18181b" stroke="#52525b" strokeWidth="2" />
        {/* Lens */}
        <circle cx="100" cy="62" r="8" fill="#1a1a2e" stroke="#71717a" strokeWidth="1" />
        <circle cx="100" cy="62" r="3" fill="#f59e0b" opacity="0.8" />
        {/* LED strip */}
        <rect x="70" y="100" width="60" height="6" rx="3" fill="#f59e0b" opacity="0.7" />
        {/* Wheels */}
        <rect x="55" y="150" width="18" height="12" rx="4" fill="#3f3f46" />
        <rect x="127" y="150" width="18" height="12" rx="4" fill="#3f3f46" />
        {/* Display */}
        <rect x="75" y="110" width="50" height="20" rx="3" fill="#09090b" stroke="#3f3f46" strokeWidth="1" />
        <text x="100" y="124" textAnchor="middle" fill="#f59e0b" fontSize="12" fontFamily="monospace">
          {tokenEmoji[token] || "..."}
        </text>
      </svg>

      <div style={{ fontSize: 11, color: "#71717a", textAlign: "center" }}>
        yahboom-mcp on port 10892
      </div>

      <div style={{ fontSize: 11, color: "#52525b", textAlign: "center", maxWidth: 200 }}>
        Emits yahboom_tool calls — connect real Boomy or use mock bridge
      </div>
    </div>
  );
}
