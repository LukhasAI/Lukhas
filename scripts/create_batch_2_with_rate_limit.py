#!/usr/bin/env python3
"""Create 10 more Jules sessions - Batch 2 with rate limiting."""

import asyncio
import sys

sys.path.insert(0, '/Users/agi_dev/LOCAL-REPOS/Lukhas')

from bridge.llm_wrappers.jules_wrapper import JulesClient

# Task definitions
BATCH_2_TASKS = [
    {
        "name": "[IDENTITY] Complete test coverage for lukhas/identity/",
        "prompt": """# Task: Comprehensive Test Coverage for lukhas/identity/

## 🎯 Goal
Achieve 90%+ test coverage for the entire lukhas/identity/ module including:
- lid_manager.py (ΛiD system core)
- auth_service.py (authentication)
- credential_store.py (credential management)
- session_manager.py (session handling)

## 📚 LUKHAS Context
- Lane: lukhas/ (production lane)
- Import Rules: Can import from core/, matriz/, universal_language/
- Constellation Star: ⚛️ Identity (authentication, ΛiD, secure access)

## ✅ Requirements
1. Unit tests for all public methods
2. Integration tests for auth flows
3. Mock external dependencies (Redis, secrets)
4. Test edge cases and error handling
5. Security testing (token validation, injection prevention)

## 📝 Test Files
Create/enhance:
- tests/unit/lukhas/identity/test_lid_manager.py
- tests/unit/lukhas/identity/test_auth_service.py
- tests/unit/lukhas/identity/test_credential_store.py
- tests/unit/lukhas/identity/test_session_manager.py
- tests/integration/lukhas/identity/test_auth_flows.py

## 🎯 Acceptance
- [ ] 90%+ coverage for lukhas/identity/
- [ ] All critical auth paths tested
- [ ] Security edge cases covered
- [ ] Async tests properly structured
"""
    },
    {
        "name": "[MATRIZ] Performance & load tests for cognitive pipeline",
        "prompt": """# Task: MATRIZ Pipeline Performance & Load Tests

## 🎯 Goal
Create comprehensive performance tests for the MATRIZ cognitive pipeline to verify:
- <250ms p95 latency target
- <100MB memory footprint
- 50+ ops/sec throughput
- Concurrent request handling

## 📚 LUKHAS Context
- Module: matriz/ (MATRIZ cognitive engine)
- Components: Memory-Attention-Thought-Risk-Intent-Action processing
- Performance Targets: Critical system SLOs

## ✅ Requirements
1. Latency benchmarks for each pipeline stage
2. Memory profiling during processing
3. Throughput tests with concurrent loads
4. Resource leak detection
5. Performance regression tests

## 📝 Test File
Create:
- tests/performance/matriz/test_pipeline_performance.py
- tests/load/matriz/test_concurrent_processing.py

## 🎯 Acceptance
- [ ] Performance tests verify all SLO targets
- [ ] Load tests handle 100+ concurrent requests
- [ ] Memory profiling shows <100MB usage
- [ ] Benchmark baseline established
"""
    },
    {
        "name": "[GUARDIAN] Comprehensive contract enforcement tests",
        "prompt": """# Task: Guardian Constitutional AI Contract Tests

## 🎯 Goal
Create comprehensive tests for the Guardian system's contract enforcement:
- Contract parsing and validation
- Ethical violation detection
- Multi-contract priority handling
- Audit trail generation

## 📚 LUKHAS Context
- Module: lukhas/governance/guardian/
- Constellation Star: 🛡️ Guardian (constitutional AI, ethical enforcement)
- Critical: Production safety system

## ✅ Requirements
1. Test all 5 default contracts (harm, manipulation, autonomy, transparency, accountability)
2. Custom contract creation and validation
3. Conflict resolution between contracts
4. Audit trail completeness
5. Performance (contract checks <10ms)

## 📝 Test Files
Create/enhance:
- tests/unit/lukhas/governance/guardian/test_contract_engine.py
- tests/unit/lukhas/governance/guardian/test_violation_detector.py
- tests/integration/lukhas/governance/guardian/test_multi_contract.py

## 🎯 Acceptance
- [ ] 90%+ coverage for guardian/
- [ ] All default contracts tested
- [ ] Conflict resolution verified
- [ ] Performance targets met
"""
    },
    {
        "name": "[MEMORY] Comprehensive memory system test coverage",
        "prompt": """# Task: Comprehensive Memory System Test Coverage

## 🎯 Goal
Achieve 85%+ coverage for lukhas/memory/ including:
- memory_manager.py (core memory operations)
- recall_engine.py (retrieval)
- consolidation.py (memory strengthening)
- forgetting_engine.py (decay)

## 📚 LUKHAS Context
- Module: lukhas/memory/
- Constellation Star: ✦ Memory (persistent state, context preservation)
- SLO: <100ms recall latency

## ✅ Requirements
1. Unit tests for all memory operations (store, recall, update, forget)
2. Integration tests for full memory lifecycle
3. Performance tests for recall SLO
4. Concurrent access tests
5. Memory capacity limits

## 📝 Test Files
Create/enhance:
- tests/unit/lukhas/memory/test_memory_manager.py
- tests/unit/lukhas/memory/test_recall_engine.py
- tests/unit/lukhas/memory/test_consolidation.py
- tests/unit/lukhas/memory/test_forgetting.py
- tests/integration/lukhas/memory/test_memory_lifecycle.py

## 🎯 Acceptance
- [ ] 85%+ coverage for lukhas/memory/
- [ ] <100ms recall verified
- [ ] Concurrent access safe
- [ ] Memory limits tested
"""
    },
    {
        "name": "[SECURITY] API security hardening & penetration tests",
        "prompt": """# Task: API Security Hardening & Penetration Tests

## 🎯 Goal
Create security-focused tests for lukhas/api/:
- Authentication bypass attempts
- Authorization boundary tests
- Input validation (XSS, SQL injection, command injection)
- Rate limiting enforcement
- CORS policy validation

## 📚 LUKHAS Context
- Module: lukhas/api/ (public API surface)
- Critical: External attack surface
- Lane: Production (lukhas/)

## ✅ Requirements
1. Authentication/authorization edge cases
2. Input sanitization tests (OWASP Top 10)
3. Rate limiting effectiveness
4. CORS misconfiguration tests
5. Token manipulation attempts
6. Mass assignment vulnerabilities

## 📝 Test Files
Create:
- tests/security/api/test_authentication_bypass.py
- tests/security/api/test_input_validation.py
- tests/security/api/test_authorization_boundaries.py
- tests/security/api/test_rate_limiting.py

## 🎯 Acceptance
- [ ] All OWASP Top 10 categories tested
- [ ] No authentication bypass possible
- [ ] Input sanitization verified
- [ ] Rate limits enforced
"""
    },
    {
        "name": "[DOCS] Documentation completeness audit & enhancement",
        "prompt": """# Task: Documentation Completeness Audit & Enhancement

## 🎯 Goal
Audit and enhance documentation for all Constellation Stars:
- Architecture decision records (ADRs)
- API endpoint documentation
- Integration guides
- Security best practices
- Performance tuning guides

## 📚 LUKHAS Context
- Focus: docs/ directory and inline docstrings
- Audience: External developers integrating with LUKHAS
- Standard: Every public API must have complete docs

## ✅ Requirements
1. Audit docs/ for missing/outdated content
2. Generate API reference from OpenAPI spec
3. Create integration quickstart guides
4. Document security considerations
5. Add performance tuning guide
6. Update README files

## 📝 Documentation Files
Create/enhance:
- docs/api/reference.md (complete API docs)
- docs/integration/quickstart.md
- docs/security/best_practices.md
- docs/performance/tuning_guide.md
- docs/architecture/constellation_framework.md

## 🎯 Acceptance
- [ ] All public APIs documented
- [ ] Integration guides complete
- [ ] Security docs comprehensive
- [ ] Performance guidance clear
"""
    },
    {
        "name": "[CI/CD] GitHub Actions workflow optimization",
        "prompt": """# Task: GitHub Actions Workflow Optimization

## 🎯 Goal
Optimize .github/workflows/ for faster CI/CD:
- Parallel job execution
- Caching strategies
- Conditional execution
- Matrix builds optimization
- Artifact retention policies

## 📚 LUKHAS Context
- Focus: .github/workflows/ (127 workflow files)
- Objective: 30-40% CI minutes reduction
- Reference: docs/CI_OPTIMIZATION_FINDINGS_2025-11-10.md

## ✅ Requirements
1. Add concurrency controls to prevent duplicate runs
2. Implement path filters (only run affected workflows)
3. Optimize caching (pip, npm, docker layers)
4. Matrix build parallelization
5. Reduce artifact retention (7 days → 1 day for temp)
6. Fast-fail strategies

## 📝 Target Workflows
Optimize high-frequency workflows:
- .github/workflows/ci.yml
- .github/workflows/tests.yml
- .github/workflows/coverage-gates.yml
- .github/workflows/lint.yml

## 🎯 Acceptance
- [ ] 30%+ reduction in CI minutes
- [ ] Concurrency controls added
- [ ] Path filters implemented
- [ ] Caching optimized
"""
    },
    {
        "name": "[OBSERVABILITY] Grafana dashboard creation",
        "prompt": """# Task: Create Grafana Observability Dashboards

## 🎯 Goal
Create comprehensive Grafana dashboards for LUKHAS observability:
- System health (CPU, memory, disk)
- MATRIZ pipeline metrics (latency, throughput)
- API performance (request rate, error rate, latency)
- Memory system metrics (recall latency, hit rate)
- Guardian system metrics (contract violations)

## 📚 LUKHAS Context
- Module: lukhas/observability/
- Stack: Prometheus + Grafana
- Dashboards: JSON format in lukhas/observability/dashboards/

## ✅ Requirements
1. System overview dashboard (high-level health)
2. MATRIZ pipeline dashboard (detailed cognitive metrics)
3. API performance dashboard (request/error/latency)
4. Memory system dashboard (recall performance)
5. Guardian compliance dashboard (contract metrics)
6. Alerting rules for SLO violations

## 📝 Dashboard Files
Create:
- lukhas/observability/dashboards/system_overview.json
- lukhas/observability/dashboards/matriz_pipeline.json
- lukhas/observability/dashboards/api_performance.json
- lukhas/observability/dashboards/memory_system.json
- lukhas/observability/dashboards/guardian_compliance.json

## 🎯 Acceptance
- [ ] All 5 dashboards created
- [ ] Prometheus metrics defined
- [ ] Alerting rules configured
- [ ] Documentation complete
"""
    },
    {
        "name": "[ASYNC] Async/await consistency audit & fixes",
        "prompt": """# Task: Async/Await Consistency Audit & Fixes

## 🎯 Goal
Audit and fix async/await usage across LUKHAS:
- Missing await keywords (sync calls on async functions)
- Blocking operations in async contexts
- Proper async context manager usage
- asyncio.gather() optimization opportunities

## 📚 LUKHAS Context
- System-wide audit (lukhas/, matriz/, core/)
- Critical: main.py async architecture
- Performance impact: blocking calls hurt throughput

## ✅ Requirements
1. Scan for missing await keywords
2. Identify blocking I/O in async contexts
3. Convert sync file operations to aiofiles
4. Replace time.sleep() with asyncio.sleep()
5. Optimize sequential async calls with gather()
6. Fix async context manager usage

## 📝 Audit Scope
- lukhas/**/*.py (production code)
- matriz/**/*.py (cognitive engine)
- core/**/*.py (integration components)

## 🎯 Acceptance
- [ ] All missing awaits fixed
- [ ] No blocking I/O in async contexts
- [ ] Optimization opportunities applied
- [ ] Test suite remains green
"""
    },
    {
        "name": "[TYPES] Type annotation completeness & mypy strict",
        "prompt": """# Task: Type Annotation Completeness & mypy Strict Mode

## 🎯 Goal
Achieve full type annotation coverage and enable mypy strict mode:
- Add type hints to all function signatures
- Annotate complex data structures
- Fix mypy errors in strict mode
- Add py.typed marker

## 📚 LUKHAS Context
- System-wide (lukhas/, matriz/, core/)
- Tool: mypy with strict configuration
- Target: 100% typed functions

## ✅ Requirements
1. Add type hints to all function signatures
2. Annotate class attributes
3. Type generic collections (List[str] not list)
4. Fix mypy --strict errors
5. Add py.typed to all packages
6. Update pyproject.toml with strict mypy config

## 📝 Scope
Priority files (highest traffic):
- lukhas/core/**/*.py
- lukhas/identity/**/*.py
- lukhas/memory/**/*.py
- matriz/**/*.py

## 🎯 Acceptance
- [ ] mypy --strict passes
- [ ] 90%+ functions fully typed
- [ ] py.typed markers added
- [ ] Tests remain green
"""
    },
]

async def create_with_rate_limit():
    """Create sessions with 60s delay between each to avoid rate limits."""

    async with JulesClient() as jules:
        # Get source ID
        sources = await jules.list_sources()
        source_id = None
        for source in sources:
            display_name = getattr(source, 'display_name', '') or ''
            if 'Lukhas' in display_name or 'Lukhas' in source.name:
                source_id = source.name
                break

        if not source_id:
            print("❌ Could not find Lukhas source")
            return

        print(f"✅ Found source: {source_id}\n")
        print("Creating Batch 2: 10 High-Value Sessions (60s delay between)")
        print("="*60)
        print("⏰ This will take ~10 minutes to complete")
        print("")

        sessions = []

        for i, task in enumerate(BATCH_2_TASKS, 1):
            try:
                print(f"[{i}/10] Creating: {task['name']}")
                session = await jules.create_session(
                    prompt=task['prompt'],
                    source_id=source_id,
                    automation_mode="AUTO_CREATE_PR",
                    display_name=task['name']
                )
                print(f"✅ Created: {session.get('name')}")
                sessions.append(session)

                if i < len(BATCH_2_TASKS):
                    print("⏳ Waiting 60 seconds before next session...")
                    await asyncio.sleep(60)
                    print("")

            except Exception as e:
                print(f"❌ Error creating session {i}: {e}")
                print("⏸️  Waiting 120 seconds before retry...")
                await asyncio.sleep(120)

        print("\n" + "="*60)
        print(f"✅ Batch 2 Complete: {len(sessions)}/10 Sessions Created")
        return sessions

if __name__ == "__main__":
    asyncio.run(create_with_rate_limit())
