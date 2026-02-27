"use client";

import { Film, Clock, User, Zap, Tag } from "lucide-react";
import { cn } from "@/lib/utils";
import type { HighlightClip } from "@/lib/api";

interface HighlightListProps {
  highlights: HighlightClip[];
}

const patternColors: Record<string, string> = {
  counter_attack: "bg-red-500/20 text-red-300 border-red-500/30",
  "counter attack": "bg-red-500/20 text-red-300 border-red-500/30",
  set_piece: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  "set piece": "bg-blue-500/20 text-blue-300 border-blue-500/30",
  high_press: "bg-orange-500/20 text-orange-300 border-orange-500/30",
  "high press": "bg-orange-500/20 text-orange-300 border-orange-500/30",
  low_block: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  transition: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  build_up: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
  "build up": "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
  offensive_play: "bg-green-500/20 text-green-300 border-green-500/30",
  defensive_play: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
  neutral: "bg-zinc-500/20 text-zinc-300 border-zinc-500/30",
};

const eventIcons: Record<string, string> = {
  goal: "⚽",
  shot: "🎯",
  turnover: "🔄",
  foul: "🟨",
  assist: "🅰️",
  save: "🧤",
  tackle: "🦵",
};

export default function HighlightList({ highlights }: HighlightListProps) {
  if (!highlights || highlights.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-500">
        <Film className="h-12 w-12 mx-auto mb-3 opacity-40" />
        <p className="text-sm">No highlights generated yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Film className="h-5 w-5 text-emerald-400" />
        <h2 className="text-lg font-semibold text-zinc-100">
          Highlights ({highlights.length} clips)
        </h2>
      </div>

      {highlights.map((clip, i) => (
        <div
          key={i}
          className="rounded-xl border border-zinc-700/50 bg-zinc-800/40 p-4 transition hover:border-zinc-600"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-sm font-semibold text-zinc-100 truncate">
                  {eventIcons[clip.event_type] || "🎬"} {clip.title || `Clip ${i + 1}`}
                </h3>
                {clip.minute && (
                  <span className="flex items-center gap-1 text-xs text-zinc-400">
                    <Clock className="h-3 w-3" />
                    {clip.minute}&apos;
                  </span>
                )}
              </div>

              {clip.caption && (
                <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed line-clamp-2">
                  {clip.caption}
                </p>
              )}

              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {clip.player && (
                  <span className="inline-flex items-center gap-1 rounded-full border border-zinc-600 bg-zinc-700/50 px-2.5 py-0.5 text-xs text-zinc-300">
                    <User className="h-3 w-3" />
                    {clip.player}
                  </span>
                )}
                {clip.event_type && (
                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs text-emerald-300">
                    <Zap className="h-3 w-3" />
                    {clip.event_type}
                  </span>
                )}
                {clip.tactical_pattern && (
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs",
                      patternColors[clip.tactical_pattern] ||
                        "bg-zinc-500/20 text-zinc-300 border-zinc-500/30"
                    )}
                  >
                    <Tag className="h-3 w-3" />
                    {clip.tactical_pattern.replace(/_/g, " ")}
                  </span>
                )}
                {clip.ai_score !== null && clip.ai_score !== undefined && (
                  <span className="text-xs text-zinc-500">
                    Score: {clip.ai_score}
                  </span>
                )}
              </div>

              {clip.hashtags && clip.hashtags.length > 0 && (
                <div className="mt-2 flex gap-1.5 flex-wrap">
                  {clip.hashtags.map((tag, j) => (
                    <span
                      key={j}
                      className="text-[10px] text-emerald-400/70"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {clip.video_url && (
              <a
                href={clip.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="shrink-0 rounded-lg bg-emerald-600/20 p-2 text-emerald-400 transition hover:bg-emerald-600/30"
                title="Watch clip"
              >
                <Film className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
