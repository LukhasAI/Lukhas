#!/usr/bin/env python3
"""
Create High Priority Jules Sessions
===================================

Creates Jules sessions for remaining high-priority test tasks.
Uses our 100 sessions/day quota - we have 64 remaining today!
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

# High-priority sessions from TEST_ASSIGNMENT_REPORT.md
HIGH_PRIORITY_SESSIONS = [
    {
        "name": "TEST-002: Core Interfaces Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for core interfaces per TEST-002.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-002. Write tests for core/interfaces/ (190 files). Target 75%+ coverage. Create tests/unit/core/interfaces/test_*.py. Focus on: language processor integration, config management, adapter interfaces, base classes. Validate with: pytest tests/unit/core/interfaces/ -v --cov=core/interfaces. Report coverage metrics when done."""
    },
    {
        "name": "TEST-003: LUKHAS Identity System Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for LUKHAS identity system per TEST-003.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-003. Write tests for lukhas/identity/ (ΛiD authentication). Target 75%+ coverage. Create tests/unit/lukhas/identity/test_*.py. Focus on: WebAuthn, passkey authentication, identity integration, auth services. Validate with: pytest tests/unit/lukhas/identity/ -v --cov=lukhas/identity. Report coverage metrics."""
    },
    {
        "name": "TEST-004: LUKHAS Memory System Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for LUKHAS memory system per TEST-004.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-004. Write tests for lukhas/memory/ (fold systems). Target 75%+ coverage. Create tests/unit/lukhas/memory/test_*.py. Focus on: memory integration, fold systems, state preservation, context persistence. Validate with: pytest tests/unit/lukhas/memory/ -v --cov=lukhas/memory. Report coverage metrics."""
    },
    {
        "name": "TEST-006: Core Emotion Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for core emotion module per TEST-006.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-006. Write tests for core/emotion/. Target 60%+ coverage. Create tests/unit/core/emotion/test_*.py. Focus on: emotion processing, affective states, emotional context. Validate with: pytest tests/unit/core/emotion/ -v --cov=core/emotion. Report coverage metrics."""
    },
    {
        "name": "TEST-007: API Endpoints Integration Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive API endpoint integration tests per TEST-007.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-007. Write integration tests for all API endpoints. Target 100% endpoint coverage. Create tests/integration/api/test_*.py. Test: /health, /api/*, consciousness endpoints, MATRIZ endpoints, identity endpoints. Include: authentication, rate limiting, error handling, response validation. Validate with: pytest tests/integration/api/ -v. Report endpoint coverage metrics."""
    },
    {
        "name": "TEST-021: LUKHAS Consciousness Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for LUKHAS consciousness module per TEST-021.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me for consciousness architecture. Write tests for lukhas/consciousness/ (Constellation integration). Target 75%+ coverage. Create tests/unit/lukhas/consciousness/test_*.py. Focus on: constellation activation, consciousness integration, awareness processing. Validate with: pytest tests/unit/lukhas/consciousness/ -v --cov=lukhas/consciousness. Report coverage metrics."""
    },
    {
        "name": "TEST-022: LUKHAS Governance Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for LUKHAS governance per TEST-022.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me for governance systems. Write tests for lukhas/governance/ (Guardian, constitutional AI). Target 75%+ coverage. Create tests/unit/lukhas/governance/test_*.py. Focus on: Guardian system, constitutional AI, ethical enforcement, drift detection. Validate with: pytest tests/unit/lukhas/governance/ -v --cov=lukhas/governance. Report coverage metrics."""
    },
    {
        "name": "TEST-023: Bridge LLM Wrappers Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for bridge LLM wrappers per TEST-023.

Context: Write tests for bridge/llm_wrappers/ (OpenAI, Claude, Gemini, Jules integrations). Target 70%+ coverage. Create tests/unit/bridge/llm_wrappers/test_*.py. Focus on: API client functionality, response handling, error handling, rate limiting. Mock external API calls. Validate with: pytest tests/unit/bridge/llm_wrappers/ -v --cov=bridge/llm_wrappers. Report coverage metrics."""
    },
    {
        "name": "TEST-024: MATRIZ Cognitive Engine Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive tests for MATRIZ cognitive engine per TEST-024.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/claude.me for MATRIZ architecture. Write tests for matriz/ (symbolic DNA, node processing). Target 75%+ coverage. Create tests/unit/matriz/test_*.py. Focus on: cognitive processing, node operations, symbolic DNA, attention mechanisms. Validate MATRIZ performance targets (<250ms p95). Validate with: pytest tests/unit/matriz/ -v --cov=matriz. Report coverage metrics."""
    },
    {
        "name": "TEST-025: Core Colonies Tests Extension",
        "priority": "MEDIUM",
        "prompt": """Extend test coverage for core colonies per TEST-025.

Context: Read existing tests at tests/unit/core/test_colonies.py. Current coverage 75%. Extend to cover edge cases, error handling, multi-agent scenarios. Create additional tests in tests/unit/core/test_colonies_*.py. Target 85%+ coverage. Focus on: complex collaboration patterns, failure recovery, consensus mechanisms. Validate with: pytest tests/unit/core/ -v --cov=core/colonies. Report coverage improvement."""
    },
    {
        "name": "TEST-026: Serve API Router Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for serve API router per TEST-026.

Context: Write tests for serve/routers/ (FastAPI route handlers). Target 70%+ coverage. Create tests/unit/serve/test_routers.py. Focus on: request handling, response formatting, error handling, validation. Mock dependencies. Validate with: pytest tests/unit/serve/ -v --cov=serve/routers. Report coverage metrics."""
    },
    {
        "name": "TEST-027: Core Security Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive security tests per TEST-027.

Context: Write tests for core/security/ (encryption, keychain, auth). Target 80%+ coverage (security critical). Create tests/unit/core/security/test_*.py. Focus on: encryption/decryption, key management, auth validation, threat detection. Test edge cases and attack vectors. Validate with: pytest tests/unit/core/security/ -v --cov=core/security. Report coverage metrics."""
    },
    {
        "name": "TEST-028: Integration Cross-System Tests",
        "priority": "HIGH",
        "prompt": """Write cross-system integration tests per TEST-028.

Context: Test interactions between major systems: MATRIZ ↔ Memory, Identity ↔ API, Consciousness ↔ Orchestration. Create tests/integration/cross_system/test_*.py. Focus on: data flow, state synchronization, error propagation. Use real components (minimal mocking). Validate with: pytest tests/integration/cross_system/ -v. Report integration coverage."""
    },
    {
        "name": "TEST-029: Performance Regression Tests",
        "priority": "MEDIUM",
        "prompt": """Create performance regression test suite per TEST-029.

Context: Create tests/performance/test_regression.py. Establish performance baselines for: MATRIZ (<250ms p95), API endpoints (<100ms p50), memory operations, consciousness processing. Set up automated performance tracking. Fail if performance degrades >10%. Validate with: pytest tests/performance/test_regression.py -v. Report baseline metrics."""
    },
    {
        "name": "TEST-030: End-to-End Workflow Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive E2E workflow tests per TEST-030.

Context: Create tests/e2e/test_workflows.py. Test complete user workflows: authentication → API request → MATRIZ processing → consciousness decision → response. Include: success paths, error paths, edge cases. Use real components. Validate with: pytest tests/e2e/ -v. Report workflow coverage."""
    }
]


async def create_all_sessions():
    """Create all high-priority test sessions."""
    print("\n🚀 Creating High Priority Jules Sessions")
    print(f"📊 Creating {len(HIGH_PRIORITY_SESSIONS)} sessions")
    print(f"⏰ Remaining daily quota: ~64 sessions")
    print("=" * 70)
    print()

    created_sessions = []

    async with JulesClient() as jules:
        for i, session_def in enumerate(HIGH_PRIORITY_SESSIONS, 1):
            print(f"Creating {i}/{len(HIGH_PRIORITY_SESSIONS)}: {session_def['name']} ({session_def['priority']})")

            try:
                session = await jules.create_session(
                    prompt=session_def["prompt"],
                    source_id="sources/github/LukhasAI/Lukhas",
                    display_name=session_def["name"],
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session.get("name", "").split("/")[-1]
                session_url = f"https://jules.google.com/session/{session_id}"

                created_sessions.append({
                    "name": session_def["name"],
                    "priority": session_def["priority"],
                    "id": session_id,
                    "url": session_url
                })

                print(f"  ✅ Created: {session_url}")
                print()

            except Exception as e:
                print(f"  ❌ Failed: {e}")
                print()

    # Summary
    print("=" * 70)
    print(f"✅ Created {len(created_sessions)} sessions successfully!")
    print()

    if created_sessions:
        print("📋 Session URLs:")
        for session in created_sessions:
            priority_emoji = "🔴" if session["priority"] == "HIGH" else "🟡"
            print(f"  {priority_emoji} {session['name']}")
            print(f"     {session['url']}")
            print()

    print("Monitor progress with:")
    print("  python3 scripts/list_all_jules_sessions.py")
    print()

    return created_sessions


def main():
    """Main entry point."""
    sessions = asyncio.run(create_all_sessions())

    if len(sessions) == len(HIGH_PRIORITY_SESSIONS):
        print(f"🎉 All {len(HIGH_PRIORITY_SESSIONS)} sessions created successfully!")
        print(f"📊 Remaining daily quota: ~{64 - len(HIGH_PRIORITY_SESSIONS)} sessions")
        sys.exit(0)
    else:
        print(f"⚠️  Only {len(sessions)}/{len(HIGH_PRIORITY_SESSIONS)} sessions created")
        sys.exit(1)


if __name__ == "__main__":
    main()
