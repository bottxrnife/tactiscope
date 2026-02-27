"use client";

import { Globe, ExternalLink } from "lucide-react";
import type { TeamContext as TeamContextType } from "@/lib/api";

interface TeamContextProps {
  context: TeamContextType | null;
}

export default function TeamContext({ context }: TeamContextProps) {
  if (!context) {
    return (
      <div className="text-center py-12 text-zinc-500">
        <Globe className="h-12 w-12 mx-auto mb-3 opacity-40" />
        <p className="text-sm">No team context available yet.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Globe className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold text-zinc-100">
            Team Context (Web Research)
          </h2>
        </div>
        {context.view_url && (
          <a
            href={context.view_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400 transition hover:border-zinc-600 hover:text-zinc-300"
          >
            <ExternalLink className="h-3 w-3" />
            Full Report
          </a>
        )}
      </div>

      <div className="rounded-xl border border-zinc-700/50 bg-zinc-800/30 p-5 max-h-[500px] overflow-y-auto">
        {context.summary ? (
          <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {context.summary}
          </div>
        ) : context.result_markdown ? (
          <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {context.result_markdown}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">
            Research completed but no summary available.
          </p>
        )}
      </div>
    </div>
  );
}
