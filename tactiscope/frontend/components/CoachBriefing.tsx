"use client";

import { FileText, Copy, Check } from "lucide-react";
import { useState } from "react";

interface CoachBriefingProps {
  markdown: string;
}

export default function CoachBriefing({ markdown }: CoachBriefingProps) {
  const [copied, setCopied] = useState(false);

  if (!markdown) {
    return (
      <div className="text-center py-12 text-zinc-500">
        <FileText className="h-12 w-12 mx-auto mb-3 opacity-40" />
        <p className="text-sm">No briefing available yet.</p>
      </div>
    );
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderMarkdown = (md: string) => {
    const lines = md.split("\n");
    const elements: React.ReactNode[] = [];

    lines.forEach((line, i) => {
      if (line.startsWith("# ")) {
        elements.push(
          <h1 key={i} className="text-xl font-bold text-zinc-100 mt-4 mb-2">
            {line.slice(2)}
          </h1>
        );
      } else if (line.startsWith("## ")) {
        elements.push(
          <h2
            key={i}
            className="text-lg font-semibold text-emerald-400 mt-6 mb-2 border-b border-zinc-700/50 pb-1"
          >
            {line.slice(3)}
          </h2>
        );
      } else if (line.startsWith("### ")) {
        elements.push(
          <h3 key={i} className="text-base font-semibold text-zinc-200 mt-3 mb-1">
            {line.slice(4)}
          </h3>
        );
      } else if (line.startsWith("> ")) {
        elements.push(
          <blockquote
            key={i}
            className="border-l-2 border-emerald-500/40 pl-3 my-1 text-xs text-zinc-400 italic"
          >
            {line.slice(2)}
          </blockquote>
        );
      } else if (line.startsWith("- ")) {
        elements.push(
          <li key={i} className="text-sm text-zinc-300 ml-4 list-disc">
            {renderInline(line.slice(2))}
          </li>
        );
      } else if (line.startsWith("**") && line.endsWith("**")) {
        elements.push(
          <p key={i} className="text-sm font-semibold text-zinc-200 mt-2">
            {line.slice(2, -2)}
          </p>
        );
      } else if (line.startsWith("---")) {
        elements.push(
          <hr key={i} className="border-zinc-700/50 my-4" />
        );
      } else if (line.startsWith("*") && line.endsWith("*")) {
        elements.push(
          <p key={i} className="text-xs text-zinc-500 italic mt-1">
            {line.slice(1, -1)}
          </p>
        );
      } else if (line.trim() === "") {
        elements.push(<div key={i} className="h-1" />);
      } else {
        elements.push(
          <p key={i} className="text-sm text-zinc-300 leading-relaxed">
            {renderInline(line)}
          </p>
        );
      }
    });

    return elements;
  };

  const renderInline = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold text-zinc-100">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold text-zinc-100">
            Coach&apos;s Briefing
          </h2>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400 transition hover:border-zinc-600 hover:text-zinc-300"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              Copy
            </>
          )}
        </button>
      </div>

      <div className="rounded-xl border border-zinc-700/50 bg-zinc-800/30 p-5 max-h-[600px] overflow-y-auto">
        {renderMarkdown(markdown)}
      </div>
    </div>
  );
}
