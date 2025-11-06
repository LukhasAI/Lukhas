#!/usr/bin/env python3
"""
Create Jules Test Sessions (TEST-014 onwards)
=============================================

Automatically creates 7 new Jules sessions for test assignments.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# Session definitions
SESSIONS = [
    {
        "name": "TEST-014: Smoke Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke. Report coverage metrics when done."""
    },
    {
        "name": "TEST-015: Performance Tests",
        "priority": "HIGH",
        "prompt": """Write comprehensive performance tests per TEST-015.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v. Report metrics when done."""
    },
    {
        "name": "TEST-016: Candidate Consciousness Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for candidate/consciousness/ per TEST-016.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules in candidate/consciousness/, target 50%+ coverage (lighter coverage for experimental code), focus on core consciousness processing functions, validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness. Report coverage metrics."""
    },
    {
        "name": "TEST-017: Candidate Bio Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for candidate/bio/ per TEST-017.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules in candidate/bio/, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio. Report coverage metrics."""
    },
    {
        "name": "TEST-018: Candidate Quantum Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for candidate/quantum/ per TEST-018.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms in candidate/quantum/, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum. Report coverage metrics."""
    },
    {
        "name": "TEST-019: Labs Memory Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for labs/memory/ per TEST-019.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes in labs/memory/, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory. Report coverage metrics."""
    },
    {
        "name": "TEST-020: Labs Governance Tests",
        "priority": "MEDIUM",
        "prompt": """Write tests for labs/governance/ per TEST-020.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules in labs/governance/, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance. Report coverage metrics."""
    }
]


async def create_all_sessions():
    """Create all test sessions."""
    print("🚀 Creating Jules Test Sessions (TEST-014 through TEST-020)")
    print("=" * 70)
    print()

    created_sessions = []

    async with JulesClient() as jules:
        for i, session_def in enumerate(SESSIONS, 1):
            print(f"Creating {i}/7: {session_def['name']} ({session_def['priority']})")

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

    if len(sessions) == 7:
        print("🎉 All 7 sessions created successfully!")
        sys.exit(0)
    else:
        print(f"⚠️  Only {len(sessions)}/7 sessions created")
        sys.exit(1)


if __name__ == "__main__":
    main()
