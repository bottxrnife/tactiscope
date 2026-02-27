from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    video_url: str = Field(..., description="YouTube or video URL to analyze")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    sport: str = Field(default="soccer", description="Sport type")


class HighlightClip(BaseModel):
    title: str = ""
    video_url: str = ""
    caption: str = ""
    hashtags: list[str] = []
    ai_score: Optional[int] = None
    event_type: str = ""
    tactical_pattern: str = ""
    player: str = ""
    minute: Optional[int] = None


class TeamContext(BaseModel):
    summary: str = ""
    result_markdown: str = ""
    view_url: str = ""


class MatchAnalysis(BaseModel):
    job_id: str
    status: str = "processing"
    home_team: str = ""
    away_team: str = ""
    sport: str = "soccer"
    highlights: list[HighlightClip] = []
    team_context: Optional[TeamContext] = None
    briefing_markdown: str = ""
    error: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    data: Optional[MatchAnalysis] = None
