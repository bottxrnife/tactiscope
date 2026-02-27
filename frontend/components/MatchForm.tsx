"use client";

import { useState } from "react";
import { Play, Loader2, Video } from "lucide-react";
import { cn } from "@/lib/utils";

interface MatchFormProps {
  onSubmit: (data: {
    video_url: string;
    home_team: string;
    away_team: string;
    sport: string;
  }) => void;
  isLoading: boolean;
}

export default function MatchForm({ onSubmit, isLoading }: MatchFormProps) {
  const [videoUrl, setVideoUrl] = useState("");
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [sport, setSport] = useState("soccer");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!videoUrl || !homeTeam || !awayTeam) return;
    onSubmit({
      video_url: videoUrl,
      home_team: homeTeam,
      away_team: awayTeam,
      sport,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-zinc-300">
          Match Video URL
        </label>
        <div className="relative">
          <Video className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
          <input
            type="url"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800/50 py-2.5 pl-10 pr-4 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            required
            disabled={isLoading}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-zinc-300">
            Home Team
          </label>
          <input
            type="text"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
            placeholder="e.g. Manchester City"
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800/50 py-2.5 px-4 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            required
            disabled={isLoading}
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-zinc-300">
            Away Team
          </label>
          <input
            type="text"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
            placeholder="e.g. Arsenal"
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800/50 py-2.5 px-4 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            required
            disabled={isLoading}
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-zinc-300">Sport</label>
        <select
          value={sport}
          onChange={(e) => setSport(e.target.value)}
          className="w-full rounded-lg border border-zinc-700 bg-zinc-800/50 py-2.5 px-4 text-sm text-zinc-100 outline-none transition focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          disabled={isLoading}
        >
          <option value="soccer">Soccer / Football</option>
          <option value="basketball">Basketball</option>
          <option value="american_football">American Football</option>
          <option value="tennis">Tennis</option>
          <option value="cricket">Cricket</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={isLoading || !videoUrl || !homeTeam || !awayTeam}
        className={cn(
          "w-full flex items-center justify-center gap-2 rounded-lg py-3 px-6 text-sm font-semibold transition-all",
          isLoading
            ? "bg-zinc-700 text-zinc-400 cursor-not-allowed"
            : "bg-emerald-600 text-white hover:bg-emerald-500 active:scale-[0.98]"
        )}
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing Match...
          </>
        ) : (
          <>
            <Play className="h-4 w-4" />
            Analyze Match
          </>
        )}
      </button>
    </form>
  );
}
