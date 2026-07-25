import { useState, useEffect, useCallback } from "react";
import IntentPanel from "./IntentPanel";
import VRMViewer from "./VRMViewer";
import BoomyPanel from "./BoomyPanel";
import Timeline from "./Timeline";

const API = "http://127.0.0.1:10700";

interface IntentDef {
  token: string;
  label: string;
  description: string;
  duration_ms: number;
}

export default function App() {
  const [intents, setIntents] = useState<IntentDef[]>([]);
  const [selectedToken, setSelectedToken] = useState("nod");
  const [intensity, setIntensity] = useState(0.5);
  const [timeline, setTimeline] = useState<string[]>([]);
  const [, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API}/api/v1/health`);
        setBackendOk(r.ok);
      } catch { setBackendOk(false); }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API}/api/v1/tools/execute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tool: "list_intents" }),
        });
        if (r.ok) {
          const data = await r.json();
          setIntents(data.result?.intents || data.intents || []);
        }
      } catch { /* backend offline */ }
    })();
  }, []);

  const emit = useCallback(async (token: string) => {
    try {
      await fetch(`${API}/api/v1/tools/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "emit_intent",
          token,
          intensity,
        }),
      });
      setTimeline((prev) => [`${token} @ ${intensity}`, ...prev].slice(0, 50));
    } catch { /* offline */ }
  }, [intensity]);

  return (
    <div style={{ display: "flex", height: "100vh", flexDirection: "column", background: "#09090b" }}>
      <header style={{ padding: "12px 24px", borderBottom: "1px solid #27272a", display: "flex", gap: 16, alignItems: "center" }}>
        <h1 style={{ fontSize: 16, fontWeight: 600, margin: 0, color: "#f4f4f5" }}>nekomimi-chan</h1>
        <span style={{ fontSize: 12, color: "#a1a1aa" }}>Embodiment Preview — v0.1.0</span>
      </header>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <IntentPanel
          intents={intents}
          selected={selectedToken}
          onSelect={setSelectedToken}
          intensity={intensity}
          onIntensityChange={setIntensity}
          onEmit={emit}
        />

        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: 16, gap: 16 }}>
          <div style={{ display: "flex", gap: 16, flex: 1 }}>
            <div style={{ flex: 1, background: "#18181b", borderRadius: 8, padding: 12 }}>
              <div style={{ fontSize: 11, color: "#a1a1aa", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>VRM (Canonical)</div>
              <VRMViewer token={selectedToken} intensity={intensity} />
            </div>
            <div style={{ flex: 1, background: "#18181b", borderRadius: 8, padding: 12 }}>
              <div style={{ fontSize: 11, color: "#a1a1aa", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>Boomy (yahboom-mcp)</div>
              <BoomyPanel token={selectedToken} />
            </div>
          </div>
          <Timeline events={timeline} />
        </div>
      </div>
    </div>
  );
}
