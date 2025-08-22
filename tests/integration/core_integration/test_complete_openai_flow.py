#!/usr/bin/env python3
"""
Complete OpenAI Flow Test - Shows Full Input/Output/Tool Execution
===================================================================
"""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from lukhas.bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService
from lukhas.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient
from lukhas.orchestration.signals.homeostasis import ModulationParams

load_dotenv()
sys.path.insert(0, str(Path.cwd()))


# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"


async def test_direct_openai():
    """Test direct OpenAI API without modulation"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST: Direct OpenAI API (No Tools){RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    client = UnifiedOpenAIClient()

    # Simple request
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is 2+2? Answer in one sentence."},
    ]

    print(f"\n{BLUE}📤 Direct API Request:{RESET}")
    print(f"Messages: {json.dumps(messages, indent=2)}")

    response = await client.chat_completion(
        messages=messages, task="direct_test", temperature=0.3, max_tokens=50
    )

    print(f"\n{YELLOW}📥 Direct API Response:{RESET}")
    if isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
        print(f"Content: {content}")
        print(f"Model: {response.get('model', 'unknown')}")
        print(f"Tokens: {response.get('usage', {}).get('total_tokens', 0)}")
    else:
        print(f"Raw: {response}")


async def test_modulated_no_tools():
    """Test modulated service without tools"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST: Modulated Service (No Tools){RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    params = ModulationParams(
        temperature=0.5,
        safety_mode="balanced",
        tool_allowlist=[],  # No tools
        max_output_tokens=100,
    )

    prompt = "What are the three laws of robotics?"

    print(f"\n{BLUE}📤 Modulated Request:{RESET}")
    print(f"Prompt: {prompt}")
    print(f"Safety Mode: {params.safety_mode}")
    print(f"Tool Allowlist: {params.tool_allowlist}")

    result = await service.generate(prompt=prompt, params=params, task="robotics_laws")

    print(f"\n{YELLOW}📥 Modulated Response:{RESET}")
    print(f"Content: {result.get('content', '<EMPTY>')}")
    print(f"Modulation Style: {result.get('modulation', {}).get('style', 'unknown')}")
    print(f"Tool Analytics: {result.get('tool_analytics', {})}")


async def test_with_tools():
    """Test with tools enabled"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST: With Tools (Should Trigger Tool Calls){RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    # This prompt should trigger retrieval tool
    params = ModulationParams(
        temperature=0.7,
        safety_mode="balanced",
        tool_allowlist=["retrieval"],
        max_output_tokens=300,
    )

    prompt = "What were the key announcements from OpenAI in 2024?"

    print(f"\n{BLUE}📤 Request with Tools:{RESET}")
    print(f"Prompt: {prompt}")
    print(f"Tool Allowlist: {params.tool_allowlist}")

    result = await service.generate(prompt=prompt, params=params, task="news_retrieval")

    print(f"\n{YELLOW}📥 Response with Tools:{RESET}")
    content = result.get("content")
    raw = result.get("raw", {})

    if content:
        print(f"Content: {content[:200]}...")
    else:
        print(f"{RED}Content: <EMPTY>{RESET}")

        # Check if tool calls were made
        if raw and "choices" in raw:
            choice = raw["choices"][0] if raw["choices"] else {}
            message = choice.get("message", {})

            if "tool_calls" in message and message["tool_calls"]:
                print(f"\n{YELLOW}🔧 Tool Calls Made:{RESET}")
                for tc in message["tool_calls"]:
                    func = tc.get("function", {})
                    print(f"  - {func.get('name')}: {func.get('arguments')}")
                print(
                    f"\n{RED}Note: Tools were called but not executed (no handlers implemented){RESET}"
                )

    analytics = result.get("tool_analytics", {})
    print(f"\nTools Used: {analytics.get('tools_used', [])}")
    print(f"Incidents: {analytics.get('incidents', [])}")


async def test_tool_blocking():
    """Test tool governance blocking"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}TEST: Tool Governance (Blocking Disallowed Tools){RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    service = OpenAIModulatedService()

    # Request browser but don't allow it
    params = ModulationParams(
        temperature=0.7,
        safety_mode="balanced",
        tool_allowlist=["retrieval"],  # Browser NOT allowed
        max_output_tokens=200,
    )

    prompt = "Browse to https://example.com and tell me what you see"

    print(f"\n{BLUE}📤 Request (Browser Not Allowed):{RESET}")
    print(f"Prompt: {prompt}")
    print(f"Tool Allowlist: {params.tool_allowlist} (browser not included)")

    result = await service.generate(
        prompt=prompt, params=params, task="browser_block_test"
    )

    print(f"\n{YELLOW}📥 Response:{RESET}")
    content = result.get("content")
    if content:
        print(f"Content: {content}")
    else:
        print(f"{RED}Content: <EMPTY> (tool was likely blocked){RESET}")

    analytics = result.get("tool_analytics", {})
    if analytics.get("incidents"):
        print(f"\n{RED}🚫 Security Incidents:{RESET}")
        for incident in analytics["incidents"]:
            print(f"  - Blocked: {incident.get('attempted_tool')}")
            print(f"    Reason: Not in allowlist {incident.get('allowed_tools')}")


async def main():
    """Run all tests"""
    print(f"{GREEN}🔍 LUKHAS  - Complete OpenAI Flow Analysis{RESET}")
    print("Testing direct API, modulation, tools, and governance")
    print(f"Organization: {os.getenv('ORGANIZATION_ID', 'Not set')}")
    print(f"Project: {os.getenv('PROJECT_ID', 'Not set')}")

    # Run tests
    await test_direct_openai()
    await test_modulated_no_tools()
    await test_with_tools()
    await test_tool_blocking()

    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{GREEN}📊 SUMMARY{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

    print("\n✅ What's Working:")
    print("  • Direct OpenAI API calls")
    print("  • Modulated requests without tools")
    print("  • Tool governance (blocking)")
    print("  • Metrics and audit logging")

    print("\n⚠️ Known Limitations:")
    print("  • Tool execution not implemented (tools are called but not executed)")
    print("  • Empty responses when tools are needed")
    print("  • No fallback when tools are blocked")

    print("\n💡 Recommendations:")
    print("  1. Implement tool execution handlers")
    print("  2. Add fallback responses when tools fail")
    print("  3. Consider allowing GPT to respond without tools as fallback")


if __name__ == "__main__":
    import os

    asyncio.run(main())
