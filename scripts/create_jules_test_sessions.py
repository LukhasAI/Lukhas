#!/usr/bin/env python3
"""
Create Jules Sessions for Test Creation
========================================

Batch creates Jules sessions to write comprehensive tests for recently
created LUKHAS components.

This script uses our FREE Jules API quota (100 sessions/day) to automate
test creation instead of burning Anthropic API credits.

Usage:
    python3 scripts/create_jules_test_sessions.py
    python3 scripts/create_jules_test_sessions.py --dry-run
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# Test tasks to create
TEST_TASKS = [
    {
        "name": "Redis Queue Tests",
        "file": "bridge/queue/redis_queue.py",
        "test_path": "tests/unit/bridge/queue/test_redis_queue.py",
        "prompt": """Create comprehensive tests for bridge/queue/redis_queue.py

The file implements a Redis-based priority queue with:
- Task model with Pydantic validation
- TaskPriority enum (CRITICAL, HIGH, MEDIUM, LOW)
- TaskType constants (architectural_violation, todo_comment, bug_fix, etc.)
- RedisTaskQueue async context manager with:
  - enqueue(task) - atomic priority insertion (ZADD)
  - dequeue(timeout) - blocking priority pop (BZPOPMIN)
  - get_queue_size() - count pending tasks
  - close() - cleanup

Requirements:
- 100% test coverage
- Test all priority levels (1=CRITICAL to 4=LOW)
- Test atomic operations (concurrent enqueue/dequeue)
- Test timeout behavior
- Test async context manager lifecycle
- Mock Redis client (don't require actual Redis server)
- Use pytest-asyncio for async tests
- Follow LUKHAS test patterns from tests/unit/

Save to: tests/unit/bridge/queue/test_redis_queue.py""",
    },
    {
        "name": "Codex Wrapper Tests",
        "file": "bridge/llm_wrappers/codex_wrapper.py",
        "test_path": "tests/unit/bridge/llm_wrappers/test_codex_wrapper.py",
        "prompt": """Create comprehensive tests for bridge/llm_wrappers/codex_wrapper.py

The file implements OpenAI Codex API wrapper with:
- CodexConfig (Pydantic model for configuration)
- CodexResponse (Pydantic model for responses)
- CodexClient async context manager with methods:
  - complete(prompt) - code generation
  - fix_code(code, error) - bug fixing
  - refactor(code, instructions) - refactoring
  - explain(code, detail_level) - code explanation
  - document(code, style) - add docstrings

Requirements:
- 100% test coverage
- Mock aiohttp client (no real API calls)
- Test API key loading (keychain → env variable fallback)
- Test retry logic (429, 500 errors)
- Test timeout handling
- Test all methods (complete, fix_code, refactor, explain, document)
- Test async context manager lifecycle
- Test PEP 585/604 modern type hints
- Use pytest-asyncio for async tests
- Follow LUKHAS test patterns from tests/unit/bridge/llm_wrappers/

Save to: tests/unit/bridge/llm_wrappers/test_codex_wrapper.py""",
    },
    {
        "name": "AI Webhook Receiver Tests",
        "file": "scripts/ai_webhook_receiver.py",
        "test_path": "tests/unit/scripts/test_ai_webhook_receiver.py",
        "prompt": """Create comprehensive tests for scripts/ai_webhook_receiver.py

The file implements FastAPI webhook receiver with:
- WebhookPayload (Pydantic model)
- map_status_to_priority() - status → TaskPriority mapping
- /webhook/ai-status endpoint - receives AI agent status updates
- /health endpoint - health check

Key functionality:
- Receives AI status updates (success, error, warning, info)
- Maps to TaskPriority (error=HIGH, warning=MEDIUM, info=LOW)
- Enqueues Task to Redis priority queue
- Handles agent types (jules, codex, gemini, ollama)
- Extracts PR number from context

Requirements:
- 100% test coverage
- Use FastAPI TestClient (no real server)
- Mock RedisTaskQueue
- Test all status levels (success, error, warning, info)
- Test priority mapping logic
- Test PR number extraction
- Test invalid payloads
- Test health endpoint
- Use pytest-asyncio for async tests
- Follow LUKHAS test patterns from tests/unit/

Save to: tests/unit/scripts/test_ai_webhook_receiver.py""",
    },
    {
        "name": "AI Task Router Tests",
        "file": "scripts/ai_task_router.py",
        "test_path": "tests/unit/scripts/test_ai_task_router.py",
        "prompt": """Create comprehensive tests for scripts/ai_task_router.py

The file implements AI task routing daemon with:
- AITaskRouter class with methods:
  - start() - daemon startup
  - _run_event_loop() - main blocking dequeue loop
  - _route_task(task) - route to appropriate agent
  - _handle_jules_task(task) - Jules integration
  - _handle_codex_task(task) - Codex integration
  - _handle_gemini_task(task) - Gemini placeholder
  - _handle_ollama_task(task) - Ollama placeholder
  - shutdown() - graceful shutdown
  - cleanup() - resource cleanup

Key functionality:
- Blocking dequeue from Redis (BZPOPMIN with 5s timeout)
- Routes tasks to Jules, Codex, Gemini, Ollama
- Handles errors with retry logic
- Tracks task_count and error_count metrics
- Graceful shutdown on SIGTERM/SIGINT

Requirements:
- 100% test coverage
- Mock RedisTaskQueue, JulesClient, CodexClient
- Test routing logic (jules, codex, gemini, ollama)
- Test task type handling (bug_fix, refactoring, documentation)
- Test graceful shutdown
- Test error handling and retries
- Test metrics tracking
- Use pytest-asyncio for async tests
- Follow LUKHAS test patterns from tests/unit/

Save to: tests/unit/scripts/test_ai_task_router.py""",
    },
]


async def create_test_sessions(dry_run: bool = False):
    """Create Jules sessions for all test tasks."""
    print("🧪 Creating Jules Test Sessions")
    print("=" * 60)
    print(f"Tasks to create: {len(TEST_TASKS)}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    if dry_run:
        print("DRY RUN - Would create the following sessions:")
        for i, task in enumerate(TEST_TASKS, 1):
            print(f"\n{i}. {task['name']}")
            print(f"   File: {task['file']}")
            print(f"   Test: {task['test_path']}")
            print(f"   Prompt: {task['prompt'][:100]}...")
        print("\nRun without --dry-run to create sessions.")
        return

    async with JulesClient() as jules:
        created_sessions = []
        failed_sessions = []

        for i, task in enumerate(TEST_TASKS, 1):
            print(f"\n[{i}/{len(TEST_TASKS)}] Creating session: {task['name']}")
            print(f"   File: {task['file']}")
            print(f"   Test: {task['test_path']}")

            try:
                session = await jules.create_session(
                    prompt=task["prompt"],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"  # Auto-create PR when done
                )

                session_id = session.get("name", "unknown")
                session_url = f"https://jules.app/{session_id}"

                print(f"   ✅ Created: {session_url}")
                created_sessions.append({
                    "task": task["name"],
                    "session_id": session_id,
                    "url": session_url
                })

            except Exception as e:
                print(f"   ❌ Failed: {e}")
                failed_sessions.append({
                    "task": task["name"],
                    "error": str(e)
                })

        # Summary
        print("\n" + "=" * 60)
        print("📊 SESSION CREATION SUMMARY")
        print("=" * 60)
        print(f"Total tasks: {len(TEST_TASKS)}")
        print(f"Created: {len(created_sessions)}")
        print(f"Failed: {len(failed_sessions)}")

        if created_sessions:
            print("\n✅ Created Sessions:")
            for session in created_sessions:
                print(f"  - {session['task']}")
                print(f"    {session['url']}")

        if failed_sessions:
            print("\n❌ Failed Sessions:")
            for session in failed_sessions:
                print(f"  - {session['task']}: {session['error']}")

        print("\n🎯 Next Steps:")
        print("1. Monitor sessions: python3 scripts/list_all_jules_sessions.py")
        print("2. Approve plans when ready (or Jules will auto-execute)")
        print("3. Review PRs when Jules creates them")
        print("4. Merge after CI passes")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create Jules sessions for test creation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating sessions"
    )

    args = parser.parse_args()
    await create_test_sessions(dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
