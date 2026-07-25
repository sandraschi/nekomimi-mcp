import { useState, useEffect } from "react";
import { getRendererInfo } from "../lib/api";

interface Props { token: string; }

const TOKEN_LABELS: Record<string, string> = {
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

export default function BoomyPanel({ token }: Props) {
  const [info, setInfo] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getRendererInfo("boomy");
        setInfo(data);
      } catch {
        setInfo(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const label = TOKEN_LABELS[token] || "...";
  const status = info?.status as string | undefined;
  const connected = status === "connected";

  return (
    <div className="flex flex-col items-center gap-3">
      <svg
        width="200"
        height="200"
        viewBox="0 0 200 200"
        className="rounded-lg"
      >
        <rect x="60" y="90" width="80" height="60" rx="10" fill="#27272a" stroke="#3f3f46" strokeWidth="2" />
        <circle cx="100" cy="65" r="25" fill="#18181b" stroke="#52525b" strokeWidth="2" />
        <circle cx="100" cy="62" r="8" fill="#1a1a2e" stroke="#71717a" strokeWidth="1" />
        <circle cx="100" cy="62" r="3" fill="#f59e0b" opacity="0.8" />
        <rect x="70" y="100" width="60" height="6" rx="3" fill="#f59e0b" opacity="0.7" />
        <rect x="55" y="150" width="18" height="12" rx="4" fill="#3f3f46" />
        <rect x="127" y="150" width="18" height="12" rx="4" fill="#3f3f46" />
        <rect x="75" y="110" width="50" height="20" rx="3" fill="#09090b" stroke="#3f3f46" strokeWidth="1" />
        <text x="100" y="124" textAnchor="middle" fill="#f59e0b" fontSize="12" fontFamily="monospace">
          {label}
        </text>
      </svg>

      {loading ? (
        <div className="text-xs text-zinc-600">Loading Boomy status...</div>
      ) : connected ? (
        <div className="text-xs text-green-400 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Boomy connected
        </div>
      ) : (
        <div className="text-xs text-zinc-500 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
          Boomy not connected
        </div>
      )}

      <div className="text-xs text-zinc-600 text-center max-w-[200px]">
        {connected
          ? "Emits yahboom_tool calls via nekomimi intent layer"
          : "Connect real Boomy or use mock bridge on port 10892"}
      </div>
    </div>
  );
}
