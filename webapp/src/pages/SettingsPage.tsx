import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  Server,
  Cpu,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { useStore } from "../store";
import { listRenderers, probeOllama, probeLmStudio, probeVllm } from "../lib/api";

const PROVIDER_DEFS = [
  { name: "Ollama", port: 11434, probe: probeOllama },
  { name: "LM Studio", port: 1234, probe: probeLmStudio },
  { name: "vLLM", port: 8000, probe: probeVllm },
];

export default function SettingsPage() {
  const backendStatus = useStore((s) => s.backendStatus);
  const detectedProviders = useStore((s) => s.detectedProviders);
  const setProviders = useStore((s) => s.setProviders);
  const providerStatus = useStore((s) => s.providerStatus);
  const llmProvider = useStore((s) => s.llmProvider);
  const setLlmProvider = useStore((s) => s.setLlmProvider);
  const llmModel = useStore((s) => s.llmModel);
  const setLlmModel = useStore((s) => s.setLlmModel);
  const availableModels = useStore((s) => s.availableModels);
  const setAvailableModels = useStore((s) => s.setAvailableModels);

  const [renderers, setRenderers] = useState<
    { name: string; status: string; body_type: string }[]
  >([]);
  const [probing, setProbing] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const rendererData = (await listRenderers()) as {
          renderers: { name: string; status: string; body_type: string }[];
        };
        setRenderers(rendererData.renderers || []);
      } catch {
        /* offline */
      }
    })();
  }, []);

  const probeAll = useCallback(async () => {
    setProbing(true);
    const statuses: Record<string, "probing" | "detected" | "not_found"> = {};
    const detected: { name: string; port: number; base: string }[] = [];
    const results = await Promise.all(
      PROVIDER_DEFS.map(async (p) => {
        statuses[p.name] = "probing";
        const r = await p.probe();
        statuses[p.name] = r.detected ? "detected" : "not_found";
        if (r.detected) {
          detected.push({ name: p.name, port: p.port, base: "http://127.0.0.1" });
        }
        return { name: p.name, models: r.models };
      })
    );
    setProviders(detected, statuses);
    setProbing(false);

    const savedProvider = localStorage.getItem("nekomimi-llm-provider");
    const savedModel = localStorage.getItem("nekomimi-llm-model");
    if (savedProvider && detected.find((d) => d.name === savedProvider)) {
      setLlmProvider(savedProvider);
      const p = results.find((r) => r.name === savedProvider);
      if (p) {
        setAvailableModels(p.models);
        if (savedModel && p.models.includes(savedModel)) {
          setLlmModel(savedModel);
        } else if (p.models.length > 0) {
          setLlmModel(p.models[0]);
        }
      }
    } else if (detected.length > 0) {
      setLlmProvider(detected[0].name);
      const p = results.find((r) => r.name === detected[0].name);
      if (p) {
        setAvailableModels(p.models);
        if (p.models.length > 0) setLlmModel(p.models[0]);
      }
    }
  }, [setProviders, setLlmProvider, setLlmModel, setAvailableModels]);

  useEffect(() => {
    probeAll();
  }, [probeAll]);

  const handleProviderChange = async (name: string) => {
    setLlmProvider(name);
    const def = PROVIDER_DEFS.find((p) => p.name === name);
    if (def) {
      const r = await def.probe();
      setAvailableModels(r.models);
      if (r.models.length > 0) setLlmModel(r.models[0]);
    }
  };

  return (
    <div data-testid="settings-page" className="p-4 md:p-6 space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <Settings className="h-5 w-5 text-amber-500" />
        <h1 className="text-lg font-semibold text-zinc-200">Settings</h1>
      </div>

      <section className="space-y-3">
        <h2 className="text-xs text-zinc-500 uppercase tracking-wider flex items-center gap-2">
          <Server className="h-3.5 w-3.5" />
          Backend Connection
        </h2>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">URL</span>
            <span className="text-sm text-zinc-200 font-mono">
              http://127.0.0.1:11128
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">Status</span>
            <span
              className={`text-sm flex items-center gap-1.5 ${
                backendStatus === "connected"
                  ? "text-green-400"
                  : backendStatus === "disconnected"
                    ? "text-red-400"
                    : "text-yellow-400"
              }`}
            >
              {backendStatus === "connected" ? (
                <CheckCircle2 className="h-3.5 w-3.5" />
              ) : (
                <XCircle className="h-3.5 w-3.5" />
              )}
              {backendStatus === "connected"
                ? "Connected"
                : backendStatus === "disconnected"
                  ? "Disconnected"
                  : "Checking..."}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-400">MCP Transport</span>
            <span className="text-sm text-zinc-200 font-mono">HTTP /mcp</span>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xs text-zinc-500 uppercase tracking-wider flex items-center gap-2">
          <Cpu className="h-3.5 w-3.5" />
          Connected Renderers
        </h2>
        {renderers.length === 0 ? (
          <div className="text-sm text-zinc-500 bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            No renderers connected
          </div>
        ) : (
          <div className="grid gap-3">
            {renderers.map((r) => (
              <div
                key={r.name}
                className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between"
              >
                <div>
                  <div className="text-sm font-medium text-zinc-200 capitalize">
                    {r.name.replace(/_/g, " ")}
                  </div>
                  <div className="text-xs text-zinc-500 mt-0.5">{r.body_type}</div>
                </div>
                <span
                  className={`text-xs flex items-center gap-1.5 ${
                    r.status === "connected" ? "text-green-400" : "text-zinc-500"
                  }`}
                >
                  <span
                    className={`w-2 h-2 rounded-full ${
                      r.status === "connected" ? "bg-green-500" : "bg-zinc-600"
                    }`}
                  />
                  {r.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-xs text-zinc-500 uppercase tracking-wider">
          Local LLM Providers
        </h2>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
          <div className="grid grid-cols-3 gap-2">
            {PROVIDER_DEFS.map((p) => (
              <div
                key={p.name}
                className={`p-3 rounded-lg border text-sm ${
                  providerStatus[p.name] === "detected"
                    ? "border-green-800/50 bg-green-900/10"
                    : providerStatus[p.name] === "probing"
                      ? "border-yellow-800/50 bg-yellow-900/10"
                      : "border-zinc-800 bg-zinc-800/30"
                }`}
              >
                <div className="font-medium text-zinc-300 text-xs">{p.name}</div>
                <div className="text-xs text-zinc-500">:{p.port}</div>
                <div className="mt-1">
                  {providerStatus[p.name] === "probing" ? (
                    <Loader2 className="h-3 w-3 text-yellow-400 animate-spin" />
                  ) : providerStatus[p.name] === "detected" ? (
                    <span className="text-xs text-green-400 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Detected
                    </span>
                  ) : (
                    <span className="text-xs text-zinc-600">Not found</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {detectedProviders.length > 0 && (
            <>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-zinc-500">Provider</label>
                <select
                  data-testid="llm-provider-select"
                  value={llmProvider}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  className="bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg px-3 py-2"
                >
                  {detectedProviders.map((p) => (
                    <option key={p.name} value={p.name}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-zinc-500">Model</label>
                <select
                  data-testid="llm-model-select"
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg px-3 py-2"
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {detectedProviders.length === 0 && !probing && (
            <div className="flex items-center gap-2 text-amber-500 text-xs bg-amber-500/5 border border-amber-500/20 rounded-lg px-3 py-2">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
              Install Ollama or LM Studio to enable AI features
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
