import asyncio
import httpx
from core.config import settings


YUTORI_BASE = settings.YUTORI_BASE_URL


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": settings.YUTORI_API_KEY,
    }


async def create_research_task(home_team: str, away_team: str, sport: str = "soccer") -> dict:
    """Launch a Yutori Research task to gather team/league context."""
    query = (
        f"Provide a detailed scouting and match context summary for the {sport} match between "
        f"{home_team} and {away_team}. Include: current league standings, recent form (last 5 matches), "
        f"key players to watch, head-to-head record, tactical tendencies, and any injury news. "
        f"Format the response as a structured briefing."
    )
    output_schema = {
        "type": "object",
        "properties": {
            "league": {"type": "string", "description": "League or competition name"},
            "home_team_form": {"type": "string", "description": "Recent form of home team"},
            "away_team_form": {"type": "string", "description": "Recent form of away team"},
            "key_players_home": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key players for home team",
            },
            "key_players_away": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key players for away team",
            },
            "head_to_head": {"type": "string", "description": "Head to head summary"},
            "tactical_notes": {"type": "string", "description": "Tactical observations"},
            "summary": {"type": "string", "description": "Overall match preview summary"},
        },
    }
    payload = {
        "query": query,
        "user_timezone": "America/Los_Angeles",
        "output_schema": output_schema,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{YUTORI_BASE}/v1/research/tasks",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def get_research_status(task_id: str) -> dict:
    """Get the current status and results of a Yutori Research task."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{YUTORI_BASE}/v1/research/tasks/{task_id}",
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def poll_research_task(task_id: str, max_wait: int = 600, interval: int = 10) -> dict:
    """Poll Yutori until the research task succeeds or fails."""
    elapsed = 0
    while elapsed < max_wait:
        data = await get_research_status(task_id)
        status = data.get("status", "")
        if status in ("succeeded", "completed", "done"):
            return data
        if status in ("failed", "error"):
            raise RuntimeError(f"Yutori research task failed: {data}")
        await asyncio.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"Yutori research task {task_id} timed out after {max_wait}s")


async def research_match_context(home_team: str, away_team: str, sport: str = "soccer") -> dict:
    """End-to-end: create research task, poll, return results."""
    task_data = await create_research_task(home_team, away_team, sport)
    task_id = task_data["task_id"]
    result = await poll_research_task(task_id)
    return result


async def health_check() -> dict:
    """Quick connectivity + auth test by hitting the Yutori health endpoint."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{YUTORI_BASE}/v1/health",
            headers=_headers(),
        )
        if resp.status_code == 200:
            return {"ok": True, "status_code": 200, "detail": resp.json()}
        return {"ok": False, "status_code": resp.status_code, "detail": resp.text}
