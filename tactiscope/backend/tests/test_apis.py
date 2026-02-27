"""
API Sanity Tests for TactiScope.
Tests connectivity and authentication for all three external APIs.
Run with: python -m tests.test_apis
"""
import asyncio
import sys
import json
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.config import settings
from services import reka_service, fastino_service, yutori_service


async def test_reka():
    print("\n" + "=" * 60)
    print("🎬 Testing Reka Vision API...")
    print("=" * 60)
    try:
        result = await reka_service.health_check()
        print(f"  Status Code: {result.get('status_code')}")
        print(f"  OK: {result.get('ok')}")
        if result.get("ok"):
            print(f"  Job ID: {result.get('job_id')}")
            print("  ✅ Reka Vision API: CONNECTED & AUTHENTICATED")
        else:
            print(f"  Detail: {result.get('detail', '')[:200]}")
            print("  ❌ Reka Vision API: FAILED")
        return result.get("ok", False)
    except Exception as e:
        print(f"  ❌ Reka Vision API ERROR: {e}")
        return False


async def test_fastino():
    print("\n" + "=" * 60)
    print("🧠 Testing Fastino GLiNER-2 API...")
    print("=" * 60)
    try:
        result = await fastino_service.health_check()
        print(f"  Status Code: {result.get('status_code')}")
        print(f"  OK: {result.get('ok')}")
        if result.get("ok"):
            print(f"  Result: {json.dumps(result.get('result', {}), indent=2)[:300]}")
            print("  ✅ Fastino GLiNER-2 API: CONNECTED & AUTHENTICATED")
        else:
            print(f"  Detail: {result.get('detail', '')[:200]}")
            print("  ❌ Fastino GLiNER-2 API: FAILED")
        return result.get("ok", False)
    except Exception as e:
        print(f"  ❌ Fastino GLiNER-2 API ERROR: {e}")
        return False


async def test_yutori():
    print("\n" + "=" * 60)
    print("🌐 Testing Yutori Research API...")
    print("=" * 60)
    try:
        result = await yutori_service.health_check()
        print(f"  Status Code: {result.get('status_code')}")
        print(f"  OK: {result.get('ok')}")
        if result.get("ok"):
            print(f"  Detail: {json.dumps(result.get('detail', {}), indent=2)[:200]}")
            print("  ✅ Yutori Research API: CONNECTED & AUTHENTICATED")
        else:
            print(f"  Detail: {result.get('detail', '')[:200]}")
            print("  ❌ Yutori Research API: FAILED")
        return result.get("ok", False)
    except Exception as e:
        print(f"  ❌ Yutori Research API ERROR: {e}")
        return False


async def test_fastino_extraction():
    print("\n" + "=" * 60)
    print("🧠 Testing Fastino Tactical Extraction...")
    print("=" * 60)
    try:
        text = "In the 67th minute, Smith scores a brilliant goal after a quick counter attack down the right wing."
        result = await fastino_service.extract_tactical_info(text)
        print(f"  Result: {json.dumps(result, indent=2)[:500]}")
        print("  ✅ Fastino Tactical Extraction: WORKING")
        return True
    except Exception as e:
        print(f"  ❌ Fastino Tactical Extraction ERROR: {e}")
        return False


async def test_fastino_classify():
    print("\n" + "=" * 60)
    print("🧠 Testing Fastino Play Classification...")
    print("=" * 60)
    try:
        text = "The team pressed high up the pitch forcing a turnover in the opponent's half."
        result = await fastino_service.classify_play(text)
        print(f"  Result: {json.dumps(result, indent=2)[:500]}")
        print("  ✅ Fastino Classification: WORKING")
        return True
    except Exception as e:
        print(f"  ❌ Fastino Classification ERROR: {e}")
        return False


async def main():
    print("=" * 60)
    print("  TactiScope API Sanity Tests")
    print("=" * 60)

    # Check config
    errors = settings.validate()
    if errors:
        print(f"\n❌ Configuration errors: {errors}")
        print("Please check your .env file")
        sys.exit(1)
    print("\n✅ All API keys are configured in .env")

    # Run all tests
    results = {}
    results["reka"] = await test_reka()
    results["fastino"] = await test_fastino()
    results["yutori"] = await test_yutori()
    results["fastino_extraction"] = await test_fastino_extraction()
    results["fastino_classify"] = await test_fastino_classify()

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n🎉 All API tests passed! TactiScope is ready.")
    else:
        print("\n⚠️  Some tests failed. Check API keys and network connectivity.")
    
    return all_pass


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
