from __future__ import annotations

import asyncio
import uuid
import traceback
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from models.schemas import (
    AnalyzeRequest,
    MatchAnalysis,
    HighlightClip,
    TeamContext,
    JobStatusResponse,
)
from services import reka_service, fastino_service, yutori_service


# In-memory job store
jobs: dict[str, MatchAnalysis] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    errors = settings.validate()
    if errors:
        print(f"⚠️  Configuration warnings: {errors}")
    else:
        print("✅ All API keys configured")
    yield


app = FastAPI(
    title="TactiScope API",
    description="Autonomous Sports Tactics Auto-Breakdown Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "TactiScope API"}


@app.get("/api/health/apis")
async def health_apis():
    """Test connectivity to all three external APIs."""
    reka_result, fastino_result, yutori_result = await asyncio.gather(
        reka_service.health_check(),
        fastino_service.health_check(),
        yutori_service.health_check(),
        return_exceptions=True,
    )

    def _format(name: str, result):
        if isinstance(result, Exception):
            return {"service": name, "ok": False, "error": str(result)}
        return {"service": name, **result}

    return {
        "reka": _format("reka", reka_result),
        "fastino": _format("fastino", fastino_result),
        "yutori": _format("yutori", yutori_result),
    }


@app.post("/api/analyze")
async def analyze_match(req: AnalyzeRequest):
    """Kick off the full autonomous analysis pipeline. Returns a job_id to poll."""
    errors = settings.validate()
    if errors:
        raise HTTPException(status_code=500, detail=f"Missing API keys: {errors}")

    job_id = str(uuid.uuid4())
    analysis = MatchAnalysis(
        job_id=job_id,
        status="processing",
        home_team=req.home_team,
        away_team=req.away_team,
        sport=req.sport,
    )
    jobs[job_id] = analysis

    # Run pipeline in background so we return the job_id immediately
    asyncio.create_task(_run_pipeline(job_id, req))

    return {"job_id": job_id, "status": "processing"}


@app.get("/api/analyze/{job_id}")
async def get_analysis(job_id: str):
    """Poll for analysis results."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    analysis = jobs[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=analysis.status,
        data=analysis if analysis.status in ("done", "error") else None,
    )


async def _run_pipeline(job_id: str, req: AnalyzeRequest):
    """Core autonomous pipeline: Reka → Fastino → Yutori, all in parallel where possible."""
    analysis = jobs[job_id]
    try:
        # --- Phase 1: Kick off Reka clips + Yutori research in parallel ---
        reka_task = asyncio.create_task(_reka_pipeline(req.video_url))
        yutori_task = asyncio.create_task(
            _yutori_pipeline(req.home_team, req.away_team, req.sport)
        )

        # Wait for both
        clips_raw, yutori_data = await asyncio.gather(
            reka_task, yutori_task, return_exceptions=True
        )

        # --- Process Reka results ---
        highlights = []
        if isinstance(clips_raw, Exception):
            print(f"⚠️  Reka pipeline error: {clips_raw}")
            analysis.error = f"Reka error: {str(clips_raw)}"
        elif clips_raw:
            # --- Phase 2: For each clip, run Fastino extraction ---
            fastino_tasks = []
            for clip in clips_raw:
                commentary_text = clip.get("caption", "") or clip.get("title", "")
                fastino_tasks.append(
                    _fastino_annotate(clip, commentary_text)
                )
            annotated_clips = await asyncio.gather(*fastino_tasks, return_exceptions=True)
            for result in annotated_clips:
                if isinstance(result, Exception):
                    print(f"⚠️  Fastino annotation error: {result}")
                    highlights.append(HighlightClip(title="Error annotating clip"))
                else:
                    highlights.append(result)

        # --- Process Yutori results ---
        team_context = None
        if isinstance(yutori_data, Exception):
            print(f"⚠️  Yutori pipeline error: {yutori_data}")
            if not analysis.error:
                analysis.error = f"Yutori error: {str(yutori_data)}"
        elif yutori_data:
            team_context = TeamContext(
                summary=yutori_data.get("result", "") or "",
                result_markdown=yutori_data.get("result", "") or "",
                view_url=yutori_data.get("view_url", "") or "",
            )

        # --- Phase 3: Generate briefing ---
        briefing = _generate_briefing(
            req.home_team, req.away_team, highlights, team_context, yutori_data
        )

        # --- Finalize ---
        analysis.highlights = highlights
        analysis.team_context = team_context
        analysis.briefing_markdown = briefing
        analysis.status = "done"

    except Exception as e:
        traceback.print_exc()
        analysis.status = "error"
        analysis.error = str(e)


async def _reka_pipeline(video_url: str) -> list[dict]:
    """Generate highlights from the video."""
    return await reka_service.generate_highlights(video_url)


async def _yutori_pipeline(home_team: str, away_team: str, sport: str) -> dict:
    """Research match context from the web."""
    return await yutori_service.research_match_context(home_team, away_team, sport)


async def _fastino_annotate(clip: dict, commentary_text: str) -> HighlightClip:
    """Annotate a single clip with Fastino tactical extraction."""
    highlight = HighlightClip(
        title=clip.get("title", "Untitled Clip"),
        video_url=clip.get("video_url", ""),
        caption=clip.get("caption", ""),
        hashtags=clip.get("hashtags", []),
        ai_score=clip.get("ai_score"),
    )

    if not commentary_text or len(commentary_text.strip()) < 5:
        return highlight

    try:
        # Run tactical extraction and entity extraction in parallel
        tactical_task = fastino_service.extract_tactical_info(commentary_text)
        entity_task = fastino_service.extract_entities(commentary_text)
        classify_task = fastino_service.classify_play(commentary_text)

        tactical_result, entity_result, classify_result = await asyncio.gather(
            tactical_task, entity_task, classify_task, return_exceptions=True
        )

        # Parse tactical info
        if not isinstance(tactical_result, Exception):
            result_data = tactical_result.get("result", {})
            events = result_data.get("event", [])
            if events and isinstance(events, list) and len(events) > 0:
                first_event = events[0] if isinstance(events[0], dict) else {}
                highlight.event_type = first_event.get("event_type", "")
                highlight.tactical_pattern = first_event.get("tactical_pattern", "")
                highlight.player = first_event.get("player", "")
                minute_str = first_event.get("minute", "")
                if minute_str and str(minute_str).isdigit():
                    highlight.minute = int(minute_str)

        # Parse entity info for extra player names
        if not isinstance(entity_result, Exception) and not highlight.player:
            entities = entity_result.get("result", {}).get("entities", {})
            persons = entities.get("person", [])
            if persons:
                highlight.player = persons[0]

        # Parse classification
        if not isinstance(classify_result, Exception):
            result_data = classify_result.get("result", {})
            cat = result_data.get("category", "") or result_data.get("categories", "")
            if cat and not highlight.tactical_pattern:
                highlight.tactical_pattern = cat

    except Exception as e:
        print(f"⚠️  Fastino annotation error for clip '{highlight.title}': {e}")

    return highlight


def _generate_briefing(
    home_team: str,
    away_team: str,
    highlights: list[HighlightClip],
    team_context: Optional[TeamContext],
    yutori_raw: Optional[dict],
) -> str:
    """Generate a coach's briefing markdown from all collected data."""
    lines = [
        f"# TactiScope Match Briefing: {home_team} vs {away_team}",
        "",
    ]

    # Team context from Yutori
    if team_context and team_context.result_markdown:
        lines.append("## Match Context (Web Research)")
        lines.append("")
        lines.append(team_context.result_markdown)
        lines.append("")

    # Structured data from Yutori
    if yutori_raw and not isinstance(yutori_raw, Exception):
        structured = yutori_raw.get("structured_result")
        if structured and isinstance(structured, dict):
            if structured.get("league"):
                lines.append(f"**League:** {structured['league']}")
            if structured.get("home_team_form"):
                lines.append(f"**{home_team} Form:** {structured['home_team_form']}")
            if structured.get("away_team_form"):
                lines.append(f"**{away_team} Form:** {structured['away_team_form']}")
            if structured.get("tactical_notes"):
                lines.append(f"\n**Tactical Notes:** {structured['tactical_notes']}")
            lines.append("")

    # Highlight summary
    if highlights:
        lines.append("## Key Moments Analysis")
        lines.append("")

        event_counts: dict[str, int] = {}
        pattern_counts: dict[str, int] = {}
        players_mentioned: list[str] = []

        for i, h in enumerate(highlights, 1):
            minute_str = f" ({h.minute}')" if h.minute else ""
            player_str = f" — {h.player}" if h.player else ""
            event_str = f" [{h.event_type}]" if h.event_type else ""
            pattern_str = f" ({h.tactical_pattern})" if h.tactical_pattern else ""

            lines.append(
                f"**Clip {i}: {h.title}**{minute_str}{player_str}{event_str}{pattern_str}"
            )
            if h.caption:
                lines.append(f"> {h.caption}")
            lines.append("")

            if h.event_type:
                event_counts[h.event_type] = event_counts.get(h.event_type, 0) + 1
            if h.tactical_pattern:
                pattern_counts[h.tactical_pattern] = pattern_counts.get(h.tactical_pattern, 0) + 1
            if h.player and h.player not in players_mentioned:
                players_mentioned.append(h.player)

        # Stats
        lines.append("## Match Statistics")
        lines.append("")
        if event_counts:
            lines.append("**Events:**")
            for ev, count in event_counts.items():
                lines.append(f"- {ev}: {count}")
            lines.append("")
        if pattern_counts:
            lines.append("**Tactical Patterns:**")
            for pat, count in pattern_counts.items():
                lines.append(f"- {pat}: {count}")
            lines.append("")
        if players_mentioned:
            lines.append(f"**Key Players:** {', '.join(players_mentioned)}")
            lines.append("")
    else:
        lines.append("*No highlight clips were generated for this match.*")
        lines.append("")

    lines.append("---")
    lines.append("*Generated autonomously by TactiScope using Reka Vision, Fastino GLiNER-2, and Yutori Research.*")

    return "\n".join(lines)
