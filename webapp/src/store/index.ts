import { create } from "zustand";

export interface ProviderInfo {
  name: string;
  port: number;
  base: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

interface AppState {
  backendStatus: "checking" | "connected" | "disconnected";
  setBackendStatus: (s: "checking" | "connected" | "disconnected") => void;

  selectedToken: string;
  setSelectedToken: (t: string) => void;

  intensity: number;
  setIntensity: (v: number) => void;

  timeline: string[];
  pushTimeline: (entry: string) => void;
  clearTimeline: () => void;

  detectedProviders: ProviderInfo[];
  providerStatus: Record<string, "probing" | "detected" | "not_found">;
  setProviders: (p: ProviderInfo[], s: Record<string, "probing" | "detected" | "not_found">) => void;

  llmProvider: string;
  llmModel: string;
  availableModels: string[];
  setLlmProvider: (p: string) => void;
  setLlmModel: (m: string) => void;
  setAvailableModels: (m: string[]) => void;

  chatHistory: ChatMessage[];
  addChatMessage: (m: ChatMessage) => void;
  clearChatHistory: () => void;
}

export const useStore = create<AppState>((set) => ({
  backendStatus: "checking",
  setBackendStatus: (s) => set({ backendStatus: s }),

  selectedToken: "attending",
  setSelectedToken: (t) => set({ selectedToken: t }),

  intensity: 0.5,
  setIntensity: (v) => set({ intensity: v }),

  timeline: [],
  pushTimeline: (entry) =>
    set((s) => ({ timeline: [entry, ...s.timeline].slice(0, 50) })),
  clearTimeline: () => set({ timeline: [] }),

  detectedProviders: [],
  providerStatus: {},
  setProviders: (p, s) => set({ detectedProviders: p, providerStatus: s }),

  llmProvider: localStorage.getItem("nekomimi-llm-provider") || "",
  llmModel: localStorage.getItem("nekomimi-llm-model") || "",
  availableModels: [],
  setLlmProvider: (p) => {
    localStorage.setItem("nekomimi-llm-provider", p);
    set({ llmProvider: p });
  },
  setLlmModel: (m) => {
    localStorage.setItem("nekomimi-llm-model", m);
    set({ llmModel: m });
  },
  setAvailableModels: (m) => set({ availableModels: m }),

  chatHistory: (() => {
    try {
      return JSON.parse(localStorage.getItem("nekomimi-chat-history") || "[]");
    } catch {
      return [];
    }
  })(),
  addChatMessage: (m) =>
    set((s) => {
      const next = [...s.chatHistory, m].slice(-100);
      localStorage.setItem("nekomimi-chat-history", JSON.stringify(next));
      return { chatHistory: next };
    }),
  clearChatHistory: () => {
    localStorage.removeItem("nekomimi-chat-history");
    set({ chatHistory: [] });
  },
}));
