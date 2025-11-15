#!/usr/bin/env python3
"""
Create 4 high-priority Jules sessions for test improvements
Following successful Python 3.9 type annotation fixes
"""
import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def create_priority_sessions():
    """Create 4 high-priority Jules sessions"""

    async with JulesClient() as jules:
        # Get source ID for Lukhas repo
        sources = await jules.list_sources()
        lukhas_source = None
        for source in sources:
            # Check both repository_url and source name pattern
            if "LukhasAI/Lukhas" in (source.repository_url or "") or \
               "LukhasAI/Lukhas" in source.name:
                lukhas_source = source.name
                break

        if not lukhas_source:
            print("❌ Lukhas source not found")
            print(f"Available sources: {[s.name for s in sources]}")
            return

        print(f"✅ Using source: {lukhas_source}\n")

        sessions = []

        # Session 1: Test coverage for new bridge modules
        print("Creating Session 1: Test coverage for new bridge modules...")
        session1 = await jules.create_session(
            prompt="""Create comprehensive unit tests for the 4 new bridge modules we just created:

1. consciousness/enhanced_thought_engine.py
2. identity/auth_service.py
3. memory/sync.py
4. orchestration/externalized_orchestrator.py

Requirements:
- Test successful imports from lukhas_website.lukhas.* paths
- Test fallback behavior when imports fail
- Mock the underlying modules to test bridge isolation
- Add tests to tests/unit/bridges/ directory
- Use pytest fixtures for consistent setup
- Target 90%+ coverage for each bridge

Context: These are bridge modules that provide import compatibility. They should gracefully handle import failures and provide clear error messages.""",
            source_id=lukhas_source,
            automation_mode="AUTO_CREATE_PR"
        )
        sessions.append(("Bridge Module Tests", session1))
        print(f"✅ Session 1 created: {session1.get('name', 'unknown') if isinstance(session1, dict) else getattr(session1, 'name', 'unknown')}\n")

        # Session 2: Fix remaining test collection errors
        print("Creating Session 2: Fix remaining test collection errors...")
        session2 = await jules.create_session(
            prompt="""Fix the remaining test collection errors in the test suite. Currently we have ~100 test files with import/module errors.

Priority modules with errors:
1. tests/benchmarks/test_mesh.py - DreamMesh import issue
2. tests/candidate/qi/test_qi_entanglement.py - qi.qi_entanglement module not found
3. tests/consciousness/test_advanced_cognitive_features.py - InferenceRequest import
4. tests/consciousness/test_c1_consciousness_components.py - AutoConsciousness import
5. tests/consciousness/test_reflection_engine.py - candidate.consciousness import

For each error:
- Investigate the correct module location
- Create bridge modules if needed (follow pattern from consciousness/enhanced_thought_engine.py)
- Update import paths to use lukhas_website.lukhas.* pattern
- Verify tests can be collected without errors

DO NOT mock or stub - use real module paths. Reference recently merged PR #1527 for patterns.""",
            source_id=lukhas_source,
            automation_mode="AUTO_CREATE_PR"
        )
        sessions.append(("Fix Collection Errors", session2))
        print(f"✅ Session 2 created: {session2.get('name', 'unknown') if isinstance(session2, dict) else getattr(session2, 'name', 'unknown')}\n")

        # Session 3: Increase test coverage for recently fixed modules
        print("Creating Session 3: Increase coverage for fixed modules...")
        session3 = await jules.create_session(
            prompt="""Increase test coverage for the 3 modules we recently fixed for Python 3.9 compatibility:

1. labs/consciousness/reflection/self_reflection_engine.py
   - Add tests for ReflectionReport, ContextProvider protocol
   - Test coherence tracking and anomaly detection
   - Target 75%+ coverage

2. labs/consciousness/dream/expand/evolution.py
   - Add tests for StrategyGenome mutations and crossover
   - Test evolution cycles and fitness evaluation
   - Target 75%+ coverage

3. cognitive_core/reasoning/deep_inference_engine/__init__.py
   - Test fallback import mechanisms
   - Verify __getattr__ doesn't recurse
   - Target 90%+ coverage (it's a bridge)

Use pytest, pytest-asyncio for async tests. Add tests to tests/unit/labs/ and tests/unit/cognitive_core/ directories.""",
            source_id=lukhas_source,
            automation_mode="AUTO_CREATE_PR"
        )
        sessions.append(("Coverage Improvements", session3))
        print(f"✅ Session 3 created: {session3.get('name', 'unknown') if isinstance(session3, dict) else getattr(session3, 'name', 'unknown')}\n")

        # Session 4: Python 3.9 type annotation audit
        print("Creating Session 4: Python 3.9 type annotation audit...")
        session4 = await jules.create_session(
            prompt="""Audit the entire codebase for remaining Python 3.10+ type annotations that break Python 3.9 compatibility.

Search for patterns:
1. Union syntax with `|` operator: `str | None`, `dict[str, Any] | None`
2. Built-in generic types: `dict[`, `list[`, `set[`, `tuple[`
3. Missing typing imports: `Optional`, `Dict`, `List`, `Set`, `Tuple`, `Union`

Replace with Python 3.9 compatible versions:
- `str | None` → `Optional[str]`
- `dict[str, Any]` → `Dict[str, Any]`
- `list[str]` → `List[str]`

Focus on:
- lukhas_website/lukhas/**/*.py files
- labs/**/*.py files
- Any file that imports from typing but uses | syntax

Create a comprehensive PR fixing all instances. Reference PR #1527 for the pattern we successfully used.""",
            source_id=lukhas_source,
            automation_mode="AUTO_CREATE_PR"
        )
        sessions.append(("Type Annotation Audit", session4))
        print(f"✅ Session 4 created: {session4.get('name', 'unknown') if isinstance(session4, dict) else getattr(session4, 'name', 'unknown')}\n")

        # Summary
        print("\n" + "="*60)
        print("📊 JULES SESSION CREATION SUMMARY")
        print("="*60)
        for i, (title, session) in enumerate(sessions, 1):
            if isinstance(session, dict):
                state = session.get('state', 'UNKNOWN')
                name = session.get('name', 'unknown')
            else:
                state = getattr(session, 'state', 'UNKNOWN')
                name = getattr(session, 'name', 'unknown')
            print(f"{i}. {title}")
            print(f"   State: {state}")
            print(f"   ID: {name}")
            print()

        print("✅ All 4 high-priority Jules sessions created successfully!")
        print("\nNext steps:")
        print("1. Monitor sessions: python3 scripts/list_all_jules_sessions.py")
        print("2. Check for waiting plans: python3 scripts/get_jules_session_activities.py")
        print("3. Respond to Jules questions: python3 scripts/send_jules_message.py <session_id> '<message>'")


if __name__ == "__main__":
    asyncio.run(create_priority_sessions())
