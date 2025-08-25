#!/usr/bin/env python3
"""
Test Tool Executor - Verify tool execution handlers
====================================================
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from candidate.tools.tool_executor import get_tool_executor

load_dotenv()
sys.path.insert(0, str(Path.cwd()))


# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"


async def test_retrieve_knowledge():
    """Test knowledge retrieval"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}TEST: Knowledge Retrieval{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    executor = get_tool_executor()

    # Test 1: Ethical AI query
    args1 = {"query": "ethical AI principles", "k": 3}
    print(f"\n{BLUE}Query:{RESET} {args1}")
    result1 = await executor.execute("retrieve_knowledge", json.dumps(args1))
    print(f"{YELLOW}Result:{RESET}\n{result1[:300]}...")

    # Test 2: OpenAI news query
    args2 = {"query": "OpenAI announcements 2024", "k": 5}
    print(f"\n{BLUE}Query:{RESET} {args2}")
    result2 = await executor.execute("retrieve_knowledge", json.dumps(args2))
    print(f"{YELLOW}Result:{RESET}\n{result2[:300]}...")

    # Test 3: Generic query
    args3 = {"query": "quantum computing", "k": 2}
    print(f"\n{BLUE}Query:{RESET} {args3}")
    result3 = await executor.execute("retrieve_knowledge", json.dumps(args3))
    print(f"{YELLOW}Result:{RESET}\n{result3}")


async def test_open_url():
    """Test URL browsing"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}TEST: URL Browsing{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    executor = get_tool_executor()

    # Test with browsing disabled (default)
    args = {"url": "https://openai.com"}
    print(f"\n{BLUE}URL:{RESET} {args['url']}")
    print(f"Browser Enabled: {executor.browser_enabled}")
    result = await executor.execute("open_url", json.dumps(args))
    print(f"{YELLOW}Result:{RESET} {result}")

    # Test with invalid URL
    args2 = {"url": "not-a-url"}
    print(f"\n{BLUE}Invalid URL:{RESET} {args2['url']}")
    result2 = await executor.execute("open_url", json.dumps(args2))
    print(f"{YELLOW}Result:{RESET} {result2}")


async def test_schedule_task():
    """Test task scheduling"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}TEST: Task Scheduling{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    executor = get_tool_executor()

    # Schedule a task
    args = {
        "when": "tomorrow at 3pm",
        "note": "Review LUKHAS  documentation and update README",
    }
    print(f"\n{BLUE}Schedule:{RESET} {args}")
    result = await executor.execute("schedule_task", json.dumps(args))
    print(f"{YELLOW}Result:{RESET} {result}")

    # Check if file was created
    queue_dir = Path("data/scheduled_tasks")
    if queue_dir.exists():
        tasks = list(queue_dir.glob("task_*.json"))
        print(f"\n{GREEN}Scheduled tasks in queue:{RESET} {len(tasks)}")
        if tasks:
            latest = max(tasks, key=lambda p: p.stat().st_mtime)
            print(f"Latest task file: {latest.name}")


async def test_exec_code():
    """Test code execution"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}TEST: Code Execution{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    executor = get_tool_executor()

    # Test with execution disabled (default)
    args = {
        "language": "python",
        "source": "print('Hello from LUKHAS')\nresult = 2 + 2\nprint(f'Result: {result}')",
    }
    print(f"\n{BLUE}Code:{RESET} {args['language']}")
    print(f"Execution Enabled: {executor.code_exec_enabled}")
    result = await executor.execute("exec_code", json.dumps(args))
    print(f"{YELLOW}Result:{RESET} {result}")

    # Test with dangerous code
    args2 = {"language": "python", "source": "import os\nos.system('ls')"}
    print(f"\n{BLUE}Dangerous Code Test:{RESET}")
    result2 = await executor.execute("exec_code", json.dumps(args2))
    print(f"{YELLOW}Result:{RESET} {result2}")


async def test_multiple_tools():
    """Test executing multiple tools in sequence"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}TEST: Multiple Tool Execution{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    executor = get_tool_executor()

    # Simulate OpenAI tool calls
    tool_calls = [
        {
            "id": "call_abc123",
            "function": {
                "name": "retrieve_knowledge",
                "arguments": '{"query": "LUKHAS architecture", "k": 3}',
            },
        },
        {
            "id": "call_def456",
            "function": {
                "name": "schedule_task",
                "arguments": '{"when": "next week", "note": "Implement tool execution improvements"}',
            },
        },
    ]

    print(f"\n{BLUE}Executing {len(tool_calls)} tool calls:{RESET}")
    results = await executor.execute_tool_calls(tool_calls)

    for i, result in enumerate(results):
        print(f"\n{YELLOW}Tool {i+1} Result:{RESET}")
        print(f"  ID: {result['tool_call_id']}")
        print(f"  Content: {result['content'][:200]}...")

    # Show metrics
    print(f"\n{GREEN}Execution Metrics:{RESET}")
    for tool, count in executor.get_metrics().items():
        if count > 0:
            print(f"  {tool}: {count} calls")


async def main():
    """Run all tool executor tests"""
    print(f"{GREEN}🔧 LUKHAS Tool Executor Tests{RESET}")
    print("Testing tool execution handlers with safety checks\n")

    # Show configuration
    print(f"{BLUE}Configuration:{RESET}")
    print(f"  Retrieval: {os.getenv('LUKHAS_ENABLE_RETRIEVAL', 'true')}")
    print(f"  Browser: {os.getenv('LUKHAS_ENABLE_BROWSER', 'false')}")
    print(f"  Scheduler: {os.getenv('LUKHAS_ENABLE_SCHEDULER', 'true')}")
    print(f"  Code Exec: {os.getenv('LUKHAS_ENABLE_CODE_EXEC', 'false')}")

    # Run tests
    await test_retrieve_knowledge()
    await test_open_url()
    await test_schedule_task()
    await test_exec_code()
    await test_multiple_tools()

    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}✅ Tool Executor Tests Complete{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    print("\n📊 Summary:")
    print("  • Knowledge retrieval: Returns contextual stubs")
    print("  • URL browsing: Disabled by default for security")
    print("  • Task scheduling: Saves to local queue")
    print("  • Code execution: Disabled with safety checks")
    print("  • Multi-tool: Handles batched executions")


if __name__ == "__main__":
    asyncio.run(main())
