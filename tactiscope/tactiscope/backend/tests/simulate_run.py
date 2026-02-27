"""
Full simulation of the TactiScope analysis pipeline.
Tests the complete end-to-end flow using the FastAPI app.
Run with: python -m tests.simulate_run
"""
import asyncio
import sys
import json
import time
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import AnalyzeRequest
from main import _run_pipeline, jobs, MatchAnalysis


async def simulate_full_pipeline():
    print("=" * 60)
    print("  TactiScope Full Pipeline Simulation")
    print("=" * 60)

    # Use a short, clear demo video
    test_request = AnalyzeRequest(
        video_url="https://www.youtube.com/watch?v=aW2NLCrPpQk",
        home_team="Manchester City",
        away_team="Arsenal",
        sport="soccer",
    )

    job_id = "sim-test-001"
    analysis = MatchAnalysis(
        job_id=job_id,
        status="processing",
        home_team=test_request.home_team,
        away_team=test_request.away_team,
        sport=test_request.sport,
    )
    jobs[job_id] = analysis

    print(f"\n📋 Test Parameters:")
    print(f"   Video: {test_request.video_url}")
    print(f"   Match: {test_request.home_team} vs {test_request.away_team}")
    print(f"   Sport: {test_request.sport}")
    print(f"   Job ID: {job_id}")

    print("\n⏳ Running full pipeline (this may take 2-10 minutes)...")
    start = time.time()

    await _run_pipeline(job_id, test_request)

    elapsed = time.time() - start
    result = jobs[job_id]

    print(f"\n⏱️  Pipeline completed in {elapsed:.1f}s")
    print(f"   Status: {result.status}")

    if result.error:
        print(f"   ⚠️  Error: {result.error}")

    if result.highlights:
        print(f"\n🎬 Highlights ({len(result.highlights)} clips):")
        for i, clip in enumerate(result.highlights, 1):
            print(f"   Clip {i}: {clip.title}")
            print(f"     URL: {clip.video_url[:80]}..." if clip.video_url else "     URL: N/A")
            print(f"     Event: {clip.event_type or 'N/A'} | Pattern: {clip.tactical_pattern or 'N/A'}")
            print(f"     Player: {clip.player or 'N/A'} | Minute: {clip.minute or 'N/A'}")
    else:
        print("\n⚠️  No highlights generated.")

    if result.team_context:
        print(f"\n🌐 Team Context:")
        print(f"   View URL: {result.team_context.view_url}")
        preview = result.team_context.summary[:300] if result.team_context.summary else "N/A"
        print(f"   Summary preview: {preview}")
    else:
        print("\n⚠️  No team context available.")

    if result.briefing_markdown:
        print(f"\n📝 Coach's Briefing ({len(result.briefing_markdown)} chars):")
        # Print first 500 chars
        print("   " + result.briefing_markdown[:500].replace("\n", "\n   "))
        if len(result.briefing_markdown) > 500:
            print("   ...")

    # Validation
    print("\n" + "=" * 60)
    print("  SIMULATION RESULTS")
    print("=" * 60)
    checks = {
        "Pipeline completed": result.status in ("done", "error"),
        "Status is 'done'": result.status == "done",
        "Has highlights": len(result.highlights) > 0,
        "Has team context": result.team_context is not None,
        "Has briefing": len(result.briefing_markdown) > 0,
        "No critical error": result.error is None,
    }
    all_pass = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n🎉 Full simulation passed! TactiScope is demo-ready.")
    else:
        print("\n⚠️  Some checks failed. Review the output above.")

    return all_pass


if __name__ == "__main__":
    success = asyncio.run(simulate_full_pipeline())
    sys.exit(0 if success else 1)
