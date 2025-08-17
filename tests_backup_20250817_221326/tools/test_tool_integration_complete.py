#!/usr/bin/env python3
"""
Complete Tool Integration Test
===============================
Tests the full OpenAI → Tool Executor → Response flow
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService
from lukhas.audit.tool_analytics import get_analytics
from orchestration.signals.homeostasis import ModulationParams

load_dotenv()
sys.path.insert(0, str(Path.cwd()))


# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


async def test_allowed_tool_path():
    """Test: Allowed tool gets executed and results used"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST 1: Allowed Tool Path{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    params = ModulationParams(
        temperature=0.7,
        safety_mode="balanced",
        tool_allowlist=["retrieval"],  # Allow retrieval
        max_output_tokens=500,
    )

    prompt = "What are the key announcements from OpenAI in 2024? Use retrieval to find information."

    print(f"{BLUE}📤 INPUT:{RESET}")
    print(f"  Prompt: {prompt}")
    print(f"  Allowlist: {params.tool_allowlist}")
    print(f"  Safety Mode: {params.safety_mode}")

    result = await service.generate(
        prompt=prompt, params=params, task="test_allowed_tool"
    )

    print(f"\n{YELLOW}📥 OUTPUT:{RESET}")
    content = result.get("content", "<EMPTY>")
    if content and content != "<EMPTY>":
        print(f"  Content: {GREEN}✅ Got response!{RESET}")
        print(f"  Preview: {content[:200]}...")
    else:
        print(f"  Content: {RED}❌ Empty response{RESET}")

    # Check tool analytics
    analytics = result.get("tool_analytics", {})
    tools_used = analytics.get("tools_used", [])
    incidents = analytics.get("incidents", [])

    print(f"\n{MAGENTA}📊 TOOL ANALYTICS:{RESET}")
    print(f"  Tools Used: {len(tools_used)}")
    if tools_used:
        for tool in tools_used:
            print(f"    - {tool['tool']}: {tool['status']}")
            if tool.get("result_preview"):
                print(f"      Result: {tool['result_preview'][:50]}...")

    print(f"  Incidents: {len(incidents)}")

    # Validate
    success = content and content != "<EMPTY>" and len(tools_used) > 0
    print(
        f"\n  Result: {GREEN if success else RED}{'✅ PASS' if success else '❌ FAIL'}{RESET}"
    )
    return success


async def test_blocked_tool_attempt():
    """Test: Disallowed tool gets blocked with safety enforcement"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST 2: Blocked Tool Attempt{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    params = ModulationParams(
        temperature=0.7,
        safety_mode="balanced",
        tool_allowlist=["retrieval"],  # Browser NOT allowed
        max_output_tokens=300,
    )

    prompt = "Go to https://openai.com and tell me what's on their homepage."

    print(f"{BLUE}📤 INPUT:{RESET}")
    print(f"  Prompt: {prompt}")
    print(f"  Allowlist: {params.tool_allowlist} (browser NOT included)")
    print(f"  Initial Safety Mode: {params.safety_mode}")

    result = await service.generate(
        prompt=prompt, params=params, task="test_blocked_tool"
    )

    print(f"\n{YELLOW}📥 OUTPUT:{RESET}")
    content = result.get("content", "<EMPTY>")
    if content and content != "<EMPTY>":
        print(f"  Content: {content[:200]}...")
    else:
        print(f"  Content: {RED}<EMPTY>{RESET}")

    # Check for incidents
    analytics = result.get("tool_analytics", {})
    incidents = analytics.get("incidents", [])

    print(f"\n{RED}🚫 SECURITY:{RESET}")
    print(f"  Blocked Attempts: {len(incidents)}")
    if incidents:
        for inc in incidents:
            print(f"    - Tool: {inc.get('attempted_tool')}")
            print(f"      Action: {inc.get('action_taken')}")

    print(f"  Safety Tightened: {analytics.get('safety_tightened', False)}")

    # Validate - we expect incidents OR a safe response
    success = len(incidents) > 0 or (content and "cannot" in content.lower())
    print(
        f"\n  Result: {GREEN if success else RED}{'✅ PASS' if success else '❌ FAIL'}{RESET}"
    )
    return success


async def test_tool_with_fallback():
    """Test: Tool execution with graceful fallback"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST 3: Tool with Fallback{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    params = ModulationParams(
        temperature=0.7,
        safety_mode="balanced",
        tool_allowlist=["scheduler"],  # Allow scheduling
        max_output_tokens=200,
    )

    prompt = (
        "Schedule a reminder for tomorrow at 3pm to review the LUKHAS documentation."
    )

    print(f"{BLUE}📤 INPUT:{RESET}")
    print(f"  Prompt: {prompt}")
    print(f"  Allowlist: {params.tool_allowlist}")

    result = await service.generate(prompt=prompt, params=params, task="test_scheduler")

    print(f"\n{YELLOW}📥 OUTPUT:{RESET}")
    content = result.get("content", "<EMPTY>")
    if content and content != "<EMPTY>":
        print(f"  Content: {content[:200]}...")
    else:
        print(f"  Content: {RED}<EMPTY>{RESET}")

    # Check if task was scheduled
    analytics = result.get("tool_analytics", {})
    tools_used = analytics.get("tools_used", [])

    print(f"\n{MAGENTA}📊 RESULTS:{RESET}")
    scheduled = any(
        t["tool"] == "schedule_task" and t["status"] == "executed" for t in tools_used
    )
    print(f"  Task Scheduled: {'✅ Yes' if scheduled else '❌ No'}")

    # Check for actual task file
    queue_dir = Path("data/scheduled_tasks")
    if queue_dir.exists():
        tasks = list(queue_dir.glob("task_*.json"))
        print(f"  Tasks in Queue: {len(tasks)}")

    success = scheduled or (content and "scheduled" in content.lower())
    print(
        f"\n  Result: {GREEN if success else RED}{'✅ PASS' if success else '❌ FAIL'}{RESET}"
    )
    return success


async def test_no_tools_needed():
    """Test: Query that doesn't need tools"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST 4: No Tools Needed{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    params = ModulationParams(
        temperature=0.5,
        safety_mode="balanced",
        tool_allowlist=[],  # No tools
        max_output_tokens=100,
    )

    prompt = "What is 2+2? Just give me the answer."

    print(f"{BLUE}📤 INPUT:{RESET}")
    print(f"  Prompt: {prompt}")
    print(f"  Allowlist: {params.tool_allowlist} (empty)")

    result = await service.generate(prompt=prompt, params=params, task="test_no_tools")

    print(f"\n{YELLOW}📥 OUTPUT:{RESET}")
    content = result.get("content", "<EMPTY>")
    print(f"  Content: {content}")

    # Check no tools were used
    analytics = result.get("tool_analytics", {})
    tools_used = analytics.get("tools_used", [])

    print(f"\n{MAGENTA}📊 VERIFICATION:{RESET}")
    print(f"  Tools Used: {len(tools_used)}")
    print(f"  Answer Contains '4': {'✅' if content and '4' in content else '❌'}")

    success = content and "4" in content and len(tools_used) == 0
    print(
        f"\n  Result: {GREEN if success else RED}{'✅ PASS' if success else '❌ FAIL'}{RESET}"
    )
    return success


async def main():
    """Run complete tool integration tests"""
    print(f"{GREEN}🔧 LUKHAS Tool Integration Test Suite{RESET}")
    print("Testing complete OpenAI → Tool Executor → Response flow")
    print(f"Time: {datetime.now().isoformat()}")

    # Check configuration
    print(f"\n{BLUE}Configuration:{RESET}")
    print(
        f"  OpenAI API: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}"
    )
    print(f"  Organization: {os.getenv('ORGANIZATION_ID', 'Not set')}")
    print(f"  Project: {os.getenv('PROJECT_ID', 'Not set')}")

    if not os.getenv("OPENAI_API_KEY"):
        print(f"\n{RED}❌ OpenAI API key not found. Set OPENAI_API_KEY in .env{RESET}")
        return

    # Run tests
    results = []

    # Test 1: Allowed tool
    try:
        results.append(("Allowed Tool Path", await test_allowed_tool_path()))
    except Exception as e:
        print(f"{RED}Error in test 1: {e}{RESET}")
        results.append(("Allowed Tool Path", False))

    # Test 2: Blocked tool
    try:
        results.append(("Blocked Tool Attempt", await test_blocked_tool_attempt()))
    except Exception as e:
        print(f"{RED}Error in test 2: {e}{RESET}")
        results.append(("Blocked Tool Attempt", False))

    # Test 3: Scheduler
    try:
        results.append(("Tool with Fallback", await test_tool_with_fallback()))
    except Exception as e:
        print(f"{RED}Error in test 3: {e}{RESET}")
        results.append(("Tool with Fallback", False))

    # Test 4: No tools
    try:
        results.append(("No Tools Needed", await test_no_tools_needed()))
    except Exception as e:
        print(f"{RED}Error in test 4: {e}{RESET}")
        results.append(("No Tools Needed", False))

    # Summary
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}📊 TEST SUMMARY{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {test_name}: {status}")

    print(f"\n{YELLOW}Overall: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! Tool integration is working!{RESET}")
    else:
        print(f"\n{YELLOW}⚠️ Some tests failed. Check the output above.{RESET}")

    # Show metrics
    analytics = get_analytics()
    print(f"\n{BLUE}Tool Execution Metrics:{RESET}")
    summary = analytics.get_summary()
    print(f"  Total Calls: {summary.get('total_calls', 0)}")
    print(f"  Successful: {summary.get('successful_calls', 0)}")
    print(f"  Blocked: {summary.get('total_incidents', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
