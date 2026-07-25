import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BookOpen, FileText, AlertTriangle } from "lucide-react";
import { getSkills, getSkillContent } from "../lib/api";

interface SkillItem {
  name: string;
  uri?: string;
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<SkillItem[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getSkills();
        setSkills(data.skills || []);
      } catch {
        /* no skills */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!selected) {
      setContent("");
      return;
    }
    (async () => {
      const text = await getSkillContent(selected);
      setContent(text || "No content available");
    })();
  }, [selected]);

  return (
    <div data-testid="skills-page" className="p-4 md:p-6 space-y-6">
      <div className="flex items-center gap-3">
        <BookOpen className="h-5 w-5 text-amber-500" />
        <h1 className="text-lg font-semibold text-zinc-200">Skills</h1>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
            className="text-zinc-500"
          >
            Loading...
          </motion.div>
        </div>
      )}

      {!loading && skills.length === 0 && (
        <div className="text-center py-16 text-zinc-500">
          <AlertTriangle className="h-8 w-8 mx-auto mb-3 text-zinc-600" />
          <p className="text-sm">No skills registered</p>
          <p className="text-xs text-zinc-600 mt-2">
            Skills will appear here once the server registers skill resources
          </p>
        </div>
      )}

      {skills.length > 0 && (
        <div className="flex gap-6 flex-col lg:flex-row">
          <div className="w-full lg:w-56 shrink-0 space-y-1">
            {skills.map((skill) => (
              <button
                key={skill.name}
                onClick={() => setSelected(skill.name)}
                data-testid={`skill-${skill.name}`}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  selected === skill.name
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate">{skill.name}</span>
                </div>
              </button>
            ))}
          </div>

          <div className="flex-1 min-w-0">
            {selected ? (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <h2 className="text-sm font-medium text-zinc-200 mb-3 capitalize">
                  {selected.replace(/_/g, " ")}
                </h2>
                <div className="prose prose-invert prose-sm max-w-none text-zinc-300">
                  {content ? (
                    <pre className="whitespace-pre-wrap text-xs text-zinc-400 font-mono bg-zinc-800/50 p-3 rounded-lg">
                      {content}
                    </pre>
                  ) : (
                    <p className="text-zinc-500">Loading content...</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 text-zinc-500 text-sm">
                Select a skill from the list
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
