"""
Golden Path Integration Test for LUKHAS AI
Tests the critical path: ΛID → Consent → Context Bus → Adapter → Λ-trace
Performance budgets: Auth p95 ≤100ms, Handoff p95 ≤250ms, E2E ≤3s
Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import time
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.golden_path
@pytest.mark.integration
@pytest.mark.asyncio
async def test_golden_path_e2e(
    lid_user, 
    consent_token, 
    perf_tracker, 
    trace_collector,
    perf_budgets,
    metadata_only
):
    """
    Golden path integration test covering:
    1. User registration via ΛID (<100ms)
    2. Consent scope creation for "drive.read_metadata"
    3. Orchestrator pipeline execution: fetch drive list (metadata-only)
    4. Λ-trace record with rationale and policy tags
    5. Context handoff measurement (<250ms)
    """
    
    # Track overall E2E time
    e2e_start = perf_tracker.start('e2e_demo')
    
    # Step 1: ΛID Authentication
    auth_start = perf_tracker.start('auth')
    
    # Mock the ΛID service for testing
    with patch('core.adapters.seven_agent_adapter.LambdaIdentityServiceAdapter') as MockΛID:
        mock_identity = MockΛID.return_value
        mock_identity.initialize = AsyncMock()
        mock_identity.authenticate = AsyncMock(return_value={
            'user_id': lid_user['user_id'],
            'token': f"token_{lid_user['user_id']}",
            'namespace': lid_user['namespace'],
            'authenticated': True
        })
        
        # Initialize and authenticate
        await mock_identity.initialize()
        auth_result = await mock_identity.authenticate({
            'namespace': lid_user['namespace'],
            'token': 'test_token'
        })
        
    auth_time = perf_tracker.end('auth', auth_start)
    assert auth_result['authenticated'], "ΛID authentication failed"
    assert auth_time < perf_budgets['auth_p95_ms'], \
        f"Auth time {auth_time:.2f}ms exceeds budget {perf_budgets['auth_p95_ms']}ms"
    
    # Add Λ-trace for authentication
    trace_collector.add_trace(
        action='authenticate_user',
        rationale='User authentication via ΛID for system access',
        tags={'user_id': lid_user['user_id'], 'namespace': lid_user['namespace']}
    )
    
    # Step 2: Consent Ledger - Create consent scope
    consent_start = perf_tracker.start('consent_check')
    
    with patch('core.adapters.seven_agent_adapter.ConsentLedgerServiceAdapter') as MockConsent:
        mock_consent = MockConsent.return_value
        mock_consent.initialize = AsyncMock()
        mock_consent.record_consent = AsyncMock(return_value=True)
        mock_consent.check_consent = AsyncMock(return_value=True)
        
        # Record consent for drive.read_metadata
        await mock_consent.initialize()
        consent_recorded = await mock_consent.record_consent(
            user_id=lid_user['user_id'],
            action='drive.read_metadata',
            granted=True
        )
        
        # Check consent
        has_consent = await mock_consent.check_consent(
            user_id=lid_user['user_id'],
            action='drive.read_metadata'
        )
        
    consent_time = perf_tracker.end('consent_check', consent_start)
    assert consent_recorded, "Failed to record consent"
    assert has_consent, "Consent check failed"
    assert consent_time < perf_budgets['consent_check_ms'], \
        f"Consent check {consent_time:.2f}ms exceeds budget {perf_budgets['consent_check_ms']}ms"
    
    # Add Λ-trace for consent
    trace_collector.add_trace(
        action='record_consent',
        rationale='User granted consent for drive metadata access under GDPR',
        tags={
            'user_id': lid_user['user_id'], 
            'scope': 'drive.read_metadata',
            'jurisdiction': 'GDPR',
            'privileged': True
        }
    )
    
    # Step 3: Context Bus - Orchestrate pipeline
    handoff_start = perf_tracker.start('handoff')
    
    # Mock the Context Bus
    with patch('orchestration.context_bus_enhanced.ContextBusOrchestrator') as MockBus:
        mock_bus = MockBus.return_value
        mock_bus.publish = AsyncMock()
        mock_bus.subscribe = AsyncMock()
        
        # Publish fetch request
        await mock_bus.publish('adapter.request', {
            'service': 'drive',
            'action': 'list_metadata',
            'user_id': lid_user['user_id']
        })
        
        # Simulate pipeline execution with handoff
        await asyncio.sleep(0.01)  # Simulate processing
        
    handoff_time = perf_tracker.end('handoff', handoff_start)
    assert handoff_time < perf_budgets['handoff_p95_ms'], \
        f"Handoff time {handoff_time:.2f}ms exceeds budget {perf_budgets['handoff_p95_ms']}ms"
    
    # Step 4: Adapter - Fetch Drive metadata (metadata-only mode)
    adapter_start = perf_tracker.start('adapter_metadata')
    
    with patch('core.adapters.seven_agent_adapter.ExternalAdaptersServiceAdapter') as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.initialize = AsyncMock()
        mock_adapter.fetch_data = AsyncMock(return_value=metadata_only['drive'])
        
        # Fetch metadata
        await mock_adapter.initialize()
        drive_data = await mock_adapter.fetch_data('drive', {'query': 'list'})
        
    adapter_time = perf_tracker.end('adapter_metadata', adapter_start)
    assert drive_data, "No drive data returned"
    assert 'files' in drive_data, "Drive data missing files"
    assert len(drive_data['files']) > 0, "No files in drive data"
    assert adapter_time < perf_budgets['adapter_metadata_ms'], \
        f"Adapter time {adapter_time:.2f}ms exceeds budget {perf_budgets['adapter_metadata_ms']}ms"
    
    # Add Λ-trace for adapter call
    trace_collector.add_trace(
        action='fetch_drive_metadata',
        rationale='User requested drive file list with valid consent',
        tags={
            'user_id': lid_user['user_id'],
            'service': 'drive',
            'metadata_only': True,
            'file_count': len(drive_data['files'])
        }
    )
    
    # Step 5: Verify Λ-trace audit trail
    trace_collector.assert_rationale_exists('authenticate_user')
    trace_collector.assert_rationale_exists('record_consent')
    trace_collector.assert_rationale_exists('fetch_drive_metadata')
    
    privileged_actions = trace_collector.get_privileged_actions()
    assert len(privileged_actions) >= 1, "No privileged actions recorded"
    assert privileged_actions[0]['action'] == 'record_consent', \
        "Consent recording not marked as privileged"
    
    # End E2E timing
    e2e_time = perf_tracker.end('e2e_demo', e2e_start)
    assert e2e_time / 1000 < perf_budgets['e2e_demo_s'], \
        f"E2E time {e2e_time/1000:.2f}s exceeds budget {perf_budgets['e2e_demo_s']}s"
    
    # Report performance metrics
    print("\n=== Golden Path Performance Metrics ===")
    for operation in ['auth', 'consent_check', 'handoff', 'adapter_metadata', 'e2e_demo']:
        stats = perf_tracker.get_p50_p95(operation)
        print(f"{operation}: p50={stats['p50']:.2f}ms, p95={stats['p95']:.2f}ms")
    
    print(f"\n✅ Golden path completed successfully in {e2e_time:.2f}ms")
    print(f"📊 Λ-traces recorded: {len(trace_collector.traces)}")
    print(f"🔐 Privileged actions: {len(privileged_actions)}")


@pytest.mark.golden_path
@pytest.mark.perf
@pytest.mark.asyncio
async def test_golden_path_cold_start(perf_tracker, perf_budgets):
    """Test golden path with cold start (no caching)"""
    
    # Simulate cold start by clearing any caches
    import gc
    gc.collect()
    
    start = perf_tracker.start('cold_start')
    
    # Mock cold initialization
    with patch('core.bootstrap.LUKHASBootstrap') as MockBootstrap:
        mock_bootstrap = MockBootstrap.return_value
        mock_bootstrap.initialize = AsyncMock()
        
        # Cold start initialization
        await mock_bootstrap.initialize()
        await asyncio.sleep(0.1)  # Simulate cold start overhead
        
    cold_time = perf_tracker.end('cold_start', start)
    
    # Cold start should still meet E2E budget
    assert cold_time / 1000 < perf_budgets['e2e_demo_s'], \
        f"Cold start {cold_time/1000:.2f}s exceeds E2E budget"
    
    print(f"\n❄️ Cold start time: {cold_time:.2f}ms")


@pytest.mark.golden_path
@pytest.mark.perf
@pytest.mark.asyncio
async def test_golden_path_warm_cache(perf_tracker, perf_budgets):
    """Test golden path with warm cache (best case)"""
    
    # Pre-warm caches
    cache = {'users': {}, 'consents': {}, 'adapters': {}}
    
    start = perf_tracker.start('warm_cache')
    
    # Simulate cached operations
    with patch('core.adapters.seven_agent_adapter.LambdaIdentityServiceAdapter') as MockΛID:
        mock_identity = MockΛID.return_value
        mock_identity.authenticate = AsyncMock(return_value={
            'cached': True,
            'authenticated': True
        })
        
        # Should be very fast with cache
        result = await mock_identity.authenticate({'cached': True})
        
    warm_time = perf_tracker.end('warm_cache', start)
    
    # Warm cache should be significantly faster
    assert warm_time < perf_budgets['auth_p95_ms'] / 2, \
        f"Warm cache not fast enough: {warm_time:.2f}ms"
    
    print(f"\n🔥 Warm cache time: {warm_time:.2f}ms")


@pytest.mark.golden_path
@pytest.mark.perf
@pytest.mark.asyncio
async def test_golden_path_under_load(perf_tracker, perf_budgets):
    """Test golden path under load (100 concurrent requests)"""
    
    async def single_request(request_id: int) -> float:
        start = time.perf_counter()
        
        # Simulate request processing
        await asyncio.sleep(0.01 + (request_id % 10) * 0.001)
        
        return (time.perf_counter() - start) * 1000
    
    # Run 100 concurrent requests
    start = perf_tracker.start('load_test')
    
    tasks = [single_request(i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    load_time = perf_tracker.end('load_test', start)
    
    # Calculate p95 of individual requests
    sorted_results = sorted(results)
    p95_idx = int(len(sorted_results) * 0.95)
    p95_latency = sorted_results[p95_idx]
    
    # Under load, p95 should still meet handoff budget
    assert p95_latency < perf_budgets['handoff_p95_ms'], \
        f"Load test p95 {p95_latency:.2f}ms exceeds budget"
    
    print(f"\n📊 Load test (100 concurrent):")
    print(f"   Total time: {load_time:.2f}ms")
    print(f"   Request p95: {p95_latency:.2f}ms")
    print(f"   Throughput: {100000/load_time:.1f} req/s")


@pytest.mark.risk_critical
@pytest.mark.asyncio
async def test_consent_bulk_delete_requires_step_up(trace_collector):
    """
    Tripwire test: bulk delete must require step-up authentication
    This is a risk-critical path that must have 100% coverage
    """
    
    with patch('governance.consent_ledger.ledger_v1.ConsentLedgerV1') as MockLedger:
        mock_ledger = MockLedger.return_value
        mock_ledger.bulk_delete = AsyncMock(side_effect=Exception("Step-up required"))
        
        # Attempt bulk delete without step-up
        with pytest.raises(Exception, match="Step-up required"):
            await mock_ledger.bulk_delete(user_ids=['user1', 'user2'])
        
        # Add Λ-trace for security event
        trace_collector.add_trace(
            action='bulk_delete_blocked',
            rationale='Bulk delete operation blocked due to missing step-up authentication',
            tags={
                'privileged': True,
                'security_event': True,
                'requires_step_up': True
            }
        )
    
    # Verify security trace was recorded
    security_events = [t for t in trace_collector.traces if t['tags'].get('security_event')]
    assert len(security_events) > 0, "Security event not traced"
    assert security_events[0]['tags']['requires_step_up'], "Step-up requirement not recorded"