import { HelpCircle, BrainCircuit, Cpu, MessageSquare, Wrench, BookOpen } from "lucide-react";

const SECTIONS = [
  {
    icon: BrainCircuit,
    title: "Intent Tokens",
    content:
      "Intent tokens are substrate-independent social expressions. The LLM emits only an intent token and motion parameters. Each renderer translates these to its body's native actuator commands (differential drive, gimbal, VRM bones, etc.).\n\nTokens include: attending, nod, shake, sulk, bashful, amused, surprised, curious, alarmed, excited, tired, attentive_listen, celebrate, apologetic, present, idle, confused.",
  },
  {
    icon: Cpu,
    title: "Renderers",
    content:
      "Renderers are body implementations that translate intent tokens into actual motion/expression. Currently supported:\n\n- **boomy**: Yahboom robot with differential drive, gimbal camera, LED strip, speaker\n- **vrm**: Canonical cat-eared 3D avatar (Three.js preview)\n- **reachy_mini**: Reachy Mini robot arm\n- **bhl**: BHL (placeholder renderer)\n\nEach renderer can express a subset of intent tokens depending on its physical capabilities.",
  },
  {
    icon: MessageSquare,
    title: "Chat & Commands",
    content:
      "The Chat page uses MCP tools as its backend. Type an intent token name (e.g., 'nod', 'sulk', 'surprised') and the system will call the intent_tool to express it through connected renderers.\n\nYou can also ask about available tools and renderers.",
  },
  {
    icon: Wrench,
    title: "Tools",
    content:
      "The Tools page lists all registered intent tokens with their default parameters (timing, speed, intensity, easing curve). Each tool maps a social intent to motion parameters.\n\nPortmanteau pattern: The intent_tool consolidates all expression operations into a single MCP tool with a 'token' discriminator.",
  },
  {
    icon: BookOpen,
    title: "Skills",
    content:
      "Skills provide structured guidance on how to use the nekomimi-mcp server. When the server registers skill resources (via FastMCP SkillsDirectoryProvider), they appear on the Skills page.\n\nSkills can be loaded as chat personalities to give the LLM context-aware instructions.",
  },
];

export default function HelpPage() {
  return (
    <div data-testid="help-page" className="p-4 md:p-6 space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <HelpCircle className="h-5 w-5 text-amber-500" />
        <h1 className="text-lg font-semibold text-zinc-200">Help</h1>
      </div>

      <p className="text-sm text-zinc-400 leading-relaxed">
        nekomimi-mcp is a substrate-independent embodiment system. It bridges
        social intent tokens to multiple body renderers (VRM avatar, Boomy robot,
        Reachy Mini, BHL). The webapp provides a dashboard to preview and emit
        intents, explore tools, and configure the system.
      </p>

      <div className="space-y-4">
        {SECTIONS.map((section) => (
          <div
            key={section.title}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-3">
              <section.icon className="h-5 w-5 text-amber-500" />
              <h2 className="text-sm font-medium text-zinc-200">
                {section.title}
              </h2>
            </div>
            <div className="text-sm text-zinc-400 leading-relaxed whitespace-pre-line">
              {section.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
