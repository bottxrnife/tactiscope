import asyncio
import httpx
from core.config import settings


REKA_BASE = settings.REKA_BASE_URL


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-Api-Key": settings.REKA_API_KEY,
    }


async def create_clip_job(
    video_url: str,
    prompt: str = "Create short clips showing the most important plays, goals, and turnovers in this match.",
    num_generations: int = 3,
    max_duration_seconds: int = 60,
) -> str:
    """Submit a clip generation job to Reka Vision. Returns the generation ID."""
    payload = {
        "video_urls": [video_url],
        "prompt": prompt,
        "generation_config": {
            "template": "moments",
            "num_generations": num_generations,
            "min_duration_seconds": 0,
            "max_duration_seconds": max_duration_seconds,
        },
        "rendering_config": {
            "subtitles": True,
            "aspect_ratio": "16:9",
            "resolution": 720,
        },
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{REKA_BASE}/v1/clips",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["id"]


async def poll_clip_job(generation_id: str, max_wait: int = 600, interval: int = 10) -> dict:
    """Poll until the clip generation job completes. Returns the full response."""
    async with httpx.AsyncClient(timeout=30) as client:
        elapsed = 0
        while elapsed < max_wait:
            resp = await client.get(
                f"{REKA_BASE}/v1/clips/{generation_id}",
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")
            if status == "completed":
                return data
            if status == "failed":
                raise RuntimeError(f"Reka clip job failed: {data.get('error_message', 'unknown error')}")
            await asyncio.sleep(interval)
            elapsed += interval
        raise TimeoutError(f"Reka clip job {generation_id} timed out after {max_wait}s")


async def generate_highlights(video_url: str) -> list[dict]:
    """End-to-end: submit clip job, poll, return list of clip dicts."""
    gen_id = await create_clip_job(video_url)
    result = await poll_clip_job(gen_id)
    return result.get("output", [])


async def health_check() -> dict:
    """Quick connectivity test — submit a minimal request and verify auth."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{REKA_BASE}/v1/clips",
            headers=_headers(),
            json={
                "video_urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                "prompt": "test",
                "generation_config": {"template": "moments", "num_generations": 1, "max_duration_seconds": 30},
                "rendering_config": {"subtitles": False, "aspect_ratio": "16:9", "resolution": 720},
            },
        )
        if resp.status_code in (200, 201, 202):
            data = resp.json()
            return {"ok": True, "status_code": resp.status_code, "job_id": data.get("id")}
        if resp.status_code == 409:
            return {"ok": True, "status_code": 409, "detail": "Auth valid (duplicate request)"}
        return {"ok": False, "status_code": resp.status_code, "detail": resp.text}
