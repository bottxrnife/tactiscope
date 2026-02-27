import httpx
from core.config import settings


FASTINO_BASE = settings.FASTINO_BASE_URL


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": settings.FASTINO_API_KEY,
    }


TACTICAL_SCHEMA = {
    "event": [
        "minute::str::Minute of the event",
        "team::str::Team name involved",
        "player::str::Player name involved",
        "event_type::str::Type of event (goal, shot, turnover, foul, assist, save, tackle)",
        "tactical_pattern::str::Tactical pattern (counter_attack, set_piece, high_press, low_block, transition, build_up)",
    ]
}

ENTITY_LABELS = ["person", "team", "location", "event", "time"]


async def extract_tactical_info(text: str) -> dict:
    """Extract structured tactical JSON from a commentary snippet."""
    payload = {
        "task": "extract_json",
        "text": text,
        "schema": TACTICAL_SCHEMA,
        "threshold": 0.4,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{FASTINO_BASE}/gliner-2",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def extract_entities(text: str) -> dict:
    """Extract named entities (players, teams, etc.) from text."""
    payload = {
        "task": "extract_entities",
        "text": text,
        "schema": ENTITY_LABELS,
        "threshold": 0.5,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{FASTINO_BASE}/gliner-2",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def classify_play(text: str) -> dict:
    """Classify a play description as offensive or defensive."""
    payload = {
        "task": "classify_text",
        "text": text,
        "schema": {
            "categories": [
                "offensive_play",
                "defensive_play",
                "transition",
                "set_piece",
                "neutral",
            ]
        },
        "threshold": 0.3,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{FASTINO_BASE}/gliner-2",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def health_check() -> dict:
    """Quick connectivity + auth test with a minimal extraction call."""
    payload = {
        "task": "extract_entities",
        "text": "Messi scored a goal in the 90th minute against Real Madrid.",
        "schema": ["person", "team", "time"],
        "threshold": 0.5,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{FASTINO_BASE}/gliner-2",
            headers=_headers(),
            json=payload,
        )
        if resp.status_code == 200:
            return {"ok": True, "status_code": 200, "result": resp.json()}
        return {"ok": False, "status_code": resp.status_code, "detail": resp.text}
