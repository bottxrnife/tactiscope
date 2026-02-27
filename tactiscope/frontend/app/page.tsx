"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Crosshair, Activity, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import MatchForm from "@/components/MatchForm";
import HighlightList from "@/components/HighlightList";
import CoachBriefing from "@/components/CoachBriefing";
import TeamContext from "@/components/TeamContext";
import {
  submitAnalysis,
  pollAnalysis,
  type AnalyzeRequest,
  type MatchAnalysis,
} from "@/lib/api";

type AppStatus = "idle" | "submitting" | "processing" | "done" | "error";

export default function Home() {
  const [status, setStatus] = useState<AppStatus>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<MatchAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    pollRef.current = null;
    timerRef.current = null;
  }, []);

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const startPolling = useCallback(
    (id: string) => {
      setElapsed(0);
      timerRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);

      pollRef.current = setInterval(async () => {
        try {
          const res = await pollAnalysis(id);
          if (res.status === "done" || res.status === "error") {
            stopPolling();
            setAnalysis(res.data);
            setStatus(res.status === "done" ? "done" : "error");
            if (res.data?.error) setError(res.data.error);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 5000);
    },
    [stopPolling]
  );

  const handleSubmit = async (data: AnalyzeRequest) => {
    setStatus("submitting");
    setError(null);
    setAnalysis(null);
    setJobId(null);

    try {
      const res = await submitAnalysis(data);
      setJobId(res.job_id);
      setStatus("processing");
      startPolling(res.job_id);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to submit analysis");
    }
  };

  const formatElapsed = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return m > 0 ? `${m}m ${sec}s` : `${sec}s`;
  };

  const activeTab =
    status === "done" && analysis
      ? "results"
      : "input";

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-600/20 p-2">
              <Crosshair className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-zinc-100 tracking-tight">
                TactiScope
              </h1>
              <p className="text-[11px] text-zinc-500">
                Autonomous Sports Tactics Breakdown
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {status === "processing" && (
              <div className="flex items-center gap-2 rounded-full border border-yellow-500/30 bg-yellow-500/10 px-3 py-1.5">
                <Loader2 className="h-3 w-3 animate-spin text-yellow-400" />
                <span className="text-xs text-yellow-300">
                  Analyzing... {formatElapsed(elapsed)}
                </span>
              </div>
            )}
            {status === "done" && (
              <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5">
                <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                <span className="text-xs text-emerald-300">
                  Done in {formatElapsed(elapsed)}
                </span>
              </div>
            )}
            {status === "error" && (
              <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1.5">
                <AlertCircle className="h-3 w-3 text-red-400" />
                <span className="text-xs text-red-300">Error</span>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <Activity className="h-3 w-3 text-emerald-500" />
              <span className="text-[11px] text-zinc-500">3 AI Agents</span>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {activeTab === "input" && (
          <div className="grid gap-8 lg:grid-cols-[400px_1fr]">
            {/* Input Panel */}
            <div className="space-y-6">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
                <h2 className="text-sm font-semibold text-zinc-300 mb-4 flex items-center gap-2">
                  <Crosshair className="h-4 w-4 text-emerald-400" />
                  Match Input
                </h2>
                <MatchForm
                  onSubmit={handleSubmit}
                  isLoading={status === "submitting" || status === "processing"}
                />
              </div>

              {error && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-red-300">
                        Analysis Error
                      </p>
                      <p className="text-xs text-red-400/80 mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Pipeline Status */}
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
              <h2 className="text-sm font-semibold text-zinc-300 mb-6">
                AI Pipeline
              </h2>
              <div className="space-y-4">
                {[
                  {
                    name: "Reka Vision",
                    desc: "Generates highlight clips from match video",
                    icon: "🎬",
                  },
                  {
                    name: "Fastino GLiNER-2",
                    desc: "Extracts tactical patterns & events from commentary",
                    icon: "🧠",
                  },
                  {
                    name: "Yutori Research",
                    desc: "Scouts team form & league context from the web",
                    icon: "🌐",
                  },
                ].map((agent) => (
                  <div
                    key={agent.name}
                    className="flex items-center gap-4 rounded-xl border border-zinc-700/40 bg-zinc-800/30 p-4"
                  >
                    <span className="text-2xl">{agent.icon}</span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-zinc-200">
                        {agent.name}
                      </p>
                      <p className="text-xs text-zinc-500">{agent.desc}</p>
                    </div>
                    {status === "processing" && (
                      <Loader2 className="h-4 w-4 animate-spin text-yellow-400" />
                    )}
                    {status === "done" && (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    )}
                  </div>
                ))}
              </div>

              {status === "idle" && (
                <div className="mt-8 text-center">
                  <p className="text-sm text-zinc-500">
                    Submit a match to start the autonomous analysis pipeline.
                  </p>
                </div>
              )}

              {status === "processing" && (
                <div className="mt-8 text-center">
                  <div className="inline-flex items-center gap-2 rounded-full border border-zinc-700 bg-zinc-800 px-4 py-2">
                    <Loader2 className="h-4 w-4 animate-spin text-emerald-400" />
                    <span className="text-sm text-zinc-300">
                      Pipeline running autonomously...
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 mt-3">
                    Job ID: {jobId}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "results" && analysis && (
          <div className="space-y-8">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-zinc-100">
                  {analysis.home_team} vs {analysis.away_team}
                </h2>
                <p className="text-sm text-zinc-500 mt-1">
                  Analysis complete • {analysis.highlights.length} highlights
                </p>
              </div>
              <button
                onClick={() => {
                  setStatus("idle");
                  setAnalysis(null);
                  setJobId(null);
                  setError(null);
                  setElapsed(0);
                }}
                className="rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition hover:border-zinc-600 hover:text-zinc-100"
              >
                New Analysis
              </button>
            </div>

            {/* Results Grid */}
            <div className="grid gap-8 lg:grid-cols-2">
              <div className="space-y-8">
                <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
                  <HighlightList highlights={analysis.highlights} />
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
                  <TeamContext context={analysis.team_context} />
                </div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
                <CoachBriefing markdown={analysis.briefing_markdown} />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
