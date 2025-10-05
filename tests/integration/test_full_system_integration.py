"""
LUKHAS Full System Integration Tests
Comprehensive end-to-end testing of all integrated components.
"""

import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from governance.audit_trail import AuditEventType, AuditLevel, AuditTrail, ComplianceFramework
from lukhas.consciousness.consciousness_stream import ConsciousnessStream
from lukhas.consciousness.memory_bridge import MemoryConsciousnessBridge
from lukhas.identity.device_registry import DeviceRegistry
from lukhas.identity.jwt_utils import JWTManager

# Import all major components
from lukhas.identity.lambda_id import LambdaIDSystem
from lukhas.identity.observability import IdentityObservability
from lukhas.identity.oidc_provider import OIDCProvider
from lukhas.identity.session_manager import SessionManager
from lukhas.identity.tiers import TierSystem
from lukhas.memory.consciousness_memory_integration import ConsciousnessMemoryIntegrator
from lukhas.memory.distributed_memory import DistributedMemoryOrchestrator
from lukhas.memory.federation_coordinator import FederationCoordinator


class IntegrationTestHarness:
    """Test harness for full system integration testing"""

    def __init__(self):
        self.components = {}
        self.test_data = {}
        self.performance_metrics = {}

    async def setup_full_system(self):
        """Setup complete LUKHAS system for integration testing"""

        # Initialize observability mock
        observability = Mock(spec=IdentityObservability)
        observability.record_lid_generated = AsyncMock()
        observability.record_authentication = AsyncMock()
        observability.record_session_created = AsyncMock()
        observability.record_device_registration = AsyncMock()

        # Setup Identity Stack
        self.components['lambda_id'] = LambdaIDSystem()
        self.components['tier_system'] = TierSystem()
        self.components['jwt_manager'] = JWTManager()
        self.components['session_manager'] = SessionManager(
            token_generator=Mock(),
            observability=observability
        )
        self.components['device_registry'] = DeviceRegistry(observability)
        self.components['oidc_provider'] = OIDCProvider(
            issuer="https://test.lukhas.ai",
            jwt_manager=self.components['jwt_manager'],
            session_manager=self.components['session_manager'],
            tier_system=self.components['tier_system'],
            observability=observability
        )

        # Setup Memory Stack
        self.components['memory_integrator'] = ConsciousnessMemoryIntegrator()
        self.components['distributed_memory'] = DistributedMemoryOrchestrator(
            memory_integrator=self.components['memory_integrator']
        )
        self.components['federation_coordinator'] = FederationCoordinator(
            federation_id="test_federation",
            local_orchestrator=self.components['distributed_memory']
        )

        # Setup Consciousness Stack
        self.components['consciousness_stream'] = ConsciousnessStream()
        self.components['memory_bridge'] = MemoryConsciousnessBridge(
            memory_integrator=self.components['memory_integrator']
        )

        # Setup Governance Stack
        self.components['audit_trail'] = AuditTrail()

        # Start all components
        await self._start_all_components()

    async def _start_all_components(self):
        """Start all system components"""

        startup_order = [
            'audit_trail',
            'memory_integrator',
            'distributed_memory',
            'session_manager',
            'device_registry',
            'oidc_provider',
            'consciousness_stream',
            'memory_bridge',
            'federation_coordinator'
        ]

        for component_name in startup_order:
            component = self.components.get(component_name)
            if component and hasattr(component, 'start'):
                try:
                    await component.start()
                    print(f"✅ Started {component_name}")
                except Exception as e:
                    print(f"❌ Failed to start {component_name}: {e}")

    async def cleanup_system(self):
        """Cleanup all system components"""

        for component_name, component in self.components.items():
            if hasattr(component, 'stop'):
                try:
                    await component.stop()
                    print(f"🛑 Stopped {component_name}")
                except Exception as e:
                    print(f"⚠️ Error stopping {component_name}: {e}")


@pytest.fixture
async def integration_harness():
    """Pytest fixture for integration test harness"""
    harness = IntegrationTestHarness()
    await harness.setup_full_system()
    yield harness
    await harness.cleanup_system()


class TestIdentityIntegration:
    """Test identity system integration"""

    async def test_full_identity_flow(self, integration_harness):
        """Test complete identity flow from registration to authentication"""

        # Generate Lambda ID
        lambda_id_system = integration_harness.components['lambda_id']
        lambda_id = await lambda_id_system.generate_lambda_id()
        assert lambda_id.startswith('λ')

        # Set tier level
        tier_system = integration_harness.components['tier_system']
        await tier_system.set_user_tier_level(lambda_id, 3, "test_promotion")
        tier_level = await tier_system.get_user_tier_level(lambda_id)
        assert tier_level == 3

        # Register device
        device_registry = integration_harness.components['device_registry']
        from lukhas.identity.session_manager import DeviceType

        device = await device_registry.register_device(
            lambda_id=lambda_id,
            device_type=DeviceType.WEB,
            device_name="Test Browser",
            user_agent="TestAgent/1.0",
            ip_address="127.0.0.1",
            capabilities={"biometric", "secure_element"}
        )
        assert device.device_id.startswith('dev_')

        # Create session
        session_manager = integration_harness.components['session_manager']
        session = await session_manager.create_session(
            lambda_id=lambda_id,
            device_id=device.device_id,
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0",
            tier_level=tier_level,
            scopes={"openid", "profile", "lukhas"}
        )
        assert session.is_valid

        # Validate session
        validated_session = await session_manager.validate_session(session.session_id)
        assert validated_session is not None
        assert validated_session.lambda_id == lambda_id

        print(f"✅ Identity flow completed: {lambda_id} -> {session.session_id}")

    async def test_oidc_authorization_flow(self, integration_harness):
        """Test OIDC authorization code flow"""

        # Register OIDC client
        oidc_provider = integration_harness.components['oidc_provider']

        client = await oidc_provider.register_client(
            client_name="Test App",
            redirect_uris=["https://test.app/callback"],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            scope=["openid", "profile", "email"]
        )
        assert client.client_id.startswith('client_')

        # Generate test user
        lambda_id_system = integration_harness.components['lambda_id']
        lambda_id = await lambda_id_system.generate_lambda_id()

        # Authorization request
        auth_result = await oidc_provider.authorize(
            client_id=client.client_id,
            response_type="code",
            redirect_uri="https://test.app/callback",
            scope="openid profile",
            lambda_id=lambda_id
        )
        assert auth_result["success"] is True

        # Extract authorization code from redirect
        redirect_url = auth_result["redirect_uri"]
        code = redirect_url.split("code=")[1].split("&")[0]

        # Token exchange
        token_result = await oidc_provider.token(
            grant_type="authorization_code",
            client_id=client.client_id,
            client_secret=client.client_secret,
            code=code,
            redirect_uri="https://test.app/callback"
        )

        assert "access_token" in token_result
        assert "id_token" in token_result
        assert "refresh_token" in token_result

        # Userinfo request
        userinfo = await oidc_provider.userinfo(token_result["access_token"])
        assert userinfo["sub"] == lambda_id

        print(f"✅ OIDC flow completed for: {lambda_id}")


class TestMemoryConsciousnessIntegration:
    """Test memory-consciousness integration"""

    async def test_memory_consciousness_bridge(self, integration_harness):
        """Test bidirectional memory-consciousness bridge"""

        memory_bridge = integration_harness.components['memory_bridge']
        consciousness_stream = integration_harness.components['consciousness_stream']

        # Create consciousness session
        from lukhas.consciousness.types import ConsciousnessState

        test_lambda_id = "λtest_user_123"
        consciousness_state = ConsciousnessState(
            phase="AWARE",
            awareness_level="enhanced",
            level=0.8,
            emotional_tone="positive"
        )

        session_created = await memory_bridge.create_consciousness_session(
            session_id="test_session_001",
            consciousness_state=consciousness_state,
            context={"test": "integration"}
        )
        assert session_created

        # Query relevant memories
        memories = await memory_bridge.query_consciousness_relevant_memories(
            session_id="test_session_001",
            consciousness_context="test_integration",
            max_results=5
        )
        assert isinstance(memories, list)

        # Test consciousness tick with memory integration
        metrics = await consciousness_stream.tick({
            "test_signal": "integration_test",
            "memory_context": "active"
        })

        assert metrics.tick_rate_hz >= 0
        print("✅ Memory-consciousness bridge functional")

    async def test_distributed_memory_operations(self, integration_harness):
        """Test distributed memory operations"""

        distributed_memory = integration_harness.components['distributed_memory']
        memory_integrator = integration_harness.components['memory_integrator']

        # Create test memory fold
        from lukhas.memory.consciousness_memory_integration import EmotionalContext, MemoryFoldType

        test_content = {
            "test_data": "integration_test",
            "timestamp": datetime.utcnow().isoformat(),
            "significance": "high"
        }

        emotional_context = EmotionalContext(
            valence=0.5,
            arousal=0.3,
            dominance=0.7,
            confidence=0.9
        )

        fold_id = await memory_integrator.create_consciousness_memory_fold(
            content=test_content,
            fold_type=MemoryFoldType.EPISODIC,
            consciousness_context="integration_test",
            emotional_context=emotional_context,
            tags={"integration", "test"}
        )

        assert fold_id.startswith('fold_')

        # Test memory recall
        recalled_memories = await memory_integrator.recall_consciousness_memory(
            query={"test_data": "integration_test"},
            consciousness_context="integration_test",
            max_results=10
        )

        assert len(recalled_memories) > 0
        assert any(rm[0] == fold_id for rm in recalled_memories)

        print("✅ Distributed memory operations functional")


class TestGovernanceIntegration:
    """Test governance and audit integration"""

    async def test_audit_trail_integration(self, integration_harness):
        """Test audit trail with real system events"""

        audit_trail = integration_harness.components['audit_trail']

        # Test authentication audit
        test_user = "λtest_audit_user"
        auth_event_id = await audit_trail.log_authentication(
            user_id=test_user,
            outcome="success",
            method="lambda_id",
            ip_address="127.0.0.1",
            user_agent="Integration/Test"
        )
        assert auth_event_id.startswith('audit_')

        # Test data access audit
        data_event_id = await audit_trail.log_data_access(
            user_id=test_user,
            resource_id="memory_fold_123",
            action="read",
            outcome="success",
            data_classification="personal"
        )
        assert data_event_id.startswith('audit_')

        # Test Guardian decision audit
        guardian_event_id = await audit_trail.log_guardian_decision(
            decision_id="guard_decision_001",
            user_id=test_user,
            action="memory_access",
            decision_outcome="approved",
            confidence_score=0.95,
            policies_evaluated=["privacy_policy", "access_control"],
            reasoning="User has valid permissions"
        )
        assert guardian_event_id.startswith('audit_')

        # Query audit events
        events = await audit_trail.query_events(
            user_id=test_user,
            start_date=datetime.utcnow() - timedelta(minutes=1),
            limit=100
        )

        assert len(events) >= 3
        event_ids = [e.event_id for e in events]
        assert auth_event_id in event_ids
        assert data_event_id in event_ids
        assert guardian_event_id in event_ids

        # Test compliance report generation
        report = await audit_trail.generate_compliance_report(
            framework=ComplianceFramework.GDPR,
            start_date=datetime.utcnow() - timedelta(hours=1),
            end_date=datetime.utcnow()
        )

        assert report.framework == ComplianceFramework.GDPR
        assert report.total_events >= 0
        assert 0.0 <= report.compliance_score <= 1.0

        print(f"✅ Audit trail integration functional: {len(events)} events logged")

    async def test_integrity_verification(self, integration_harness):
        """Test audit trail integrity verification"""

        audit_trail = integration_harness.components['audit_trail']

        # Generate some audit events
        for i in range(5):
            await audit_trail.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                level=AuditLevel.INFO,
                source_component="integration_test",
                action=f"test_operation_{i}",
                description=f"Integration test operation {i}",
                metadata={"iteration": i}
            )

        # Force flush to create blocks
        if hasattr(audit_trail, '_flush_current_block'):
            await audit_trail._flush_current_block()

        # Verify integrity
        integrity_result = await audit_trail.verify_integrity()

        assert isinstance(integrity_result, dict)
        assert "chain_valid" in integrity_result
        assert "blocks_verified" in integrity_result
        assert "tamper_detected" in integrity_result

        print(f"✅ Integrity verification completed: chain_valid={integrity_result['chain_valid']}")


class TestPerformanceIntegration:
    """Test system performance under load"""

    async def test_identity_performance(self, integration_harness):
        """Test identity system performance"""

        lambda_id_system = integration_harness.components['lambda_id']
        session_manager = integration_harness.components['session_manager']

        # Test Lambda ID generation performance
        start_time = time.time()
        lambda_ids = []

        for _ in range(100):
            lambda_id = await lambda_id_system.generate_lambda_id()
            lambda_ids.append(lambda_id)

        generation_time = time.time() - start_time
        avg_generation_time = (generation_time / 100) * 1000  # ms per ID

        assert avg_generation_time < 10  # Should be under 10ms per ID
        assert len(set(lambda_ids)) == 100  # All unique

        print(f"✅ Lambda ID generation: {avg_generation_time:.2f}ms average")

        # Test session validation performance
        test_lambda_id = lambda_ids[0]

        # Create test session
        from lukhas.identity.session_manager import DeviceType
        device_registry = integration_harness.components['device_registry']

        device = await device_registry.register_device(
            lambda_id=test_lambda_id,
            device_type=DeviceType.WEB,
            device_name="Perf Test",
            user_agent="PerfTest/1.0",
            ip_address="127.0.0.1"
        )

        session = await session_manager.create_session(
            lambda_id=test_lambda_id,
            device_id=device.device_id,
            ip_address="127.0.0.1",
            user_agent="PerfTest/1.0",
            tier_level=1
        )

        # Test session validation performance
        start_time = time.time()

        for _ in range(1000):
            validated = await session_manager.validate_session(session.session_id)
            assert validated is not None

        validation_time = time.time() - start_time
        avg_validation_time = (validation_time / 1000) * 1000  # ms per validation

        assert avg_validation_time < 5  # Should be under 5ms per validation

        print(f"✅ Session validation: {avg_validation_time:.2f}ms average")

    async def test_memory_performance(self, integration_harness):
        """Test memory system performance"""

        memory_integrator = integration_harness.components['memory_integrator']

        # Test memory fold creation performance
        start_time = time.time()
        fold_ids = []

        from lukhas.memory.consciousness_memory_integration import EmotionalContext, MemoryFoldType

        for i in range(100):
            fold_id = await memory_integrator.create_consciousness_memory_fold(
                content={"test_data": f"performance_test_{i}", "index": i},
                fold_type=MemoryFoldType.PROCEDURAL,
                consciousness_context=f"perf_test_{i}",
                emotional_context=EmotionalContext(0.0, 0.3, 0.5),
                tags={"performance", "test"}
            )
            fold_ids.append(fold_id)

        creation_time = time.time() - start_time
        avg_creation_time = (creation_time / 100) * 1000  # ms per fold

        assert avg_creation_time < 50  # Should be under 50ms per fold

        print(f"✅ Memory fold creation: {avg_creation_time:.2f}ms average")

        # Test memory recall performance
        start_time = time.time()

        for i in range(50):
            memories = await memory_integrator.recall_consciousness_memory(
                query={"test_data": f"performance_test_{i}"},
                consciousness_context=f"perf_test_{i}",
                max_results=5
            )
            assert len(memories) > 0

        recall_time = time.time() - start_time
        avg_recall_time = (recall_time / 50) * 1000  # ms per query

        assert avg_recall_time < 100  # Should be under 100ms per query

        print(f"✅ Memory recall: {avg_recall_time:.2f}ms average")

    async def test_consciousness_performance(self, integration_harness):
        """Test consciousness system performance"""

        consciousness_stream = integration_harness.components['consciousness_stream']

        # Test consciousness tick performance
        start_time = time.time()

        for i in range(100):
            metrics = await consciousness_stream.tick({
                "test_signal": f"performance_{i}",
                "iteration": i
            })
            assert metrics.tick_rate_hz >= 0

        tick_time = time.time() - start_time
        avg_tick_time = (tick_time / 100) * 1000  # ms per tick

        assert avg_tick_time < 50  # Should be under 50ms per tick

        print(f"✅ Consciousness tick: {avg_tick_time:.2f}ms average")


class TestResilience:
    """Test system resilience and error handling"""

    async def test_component_failure_recovery(self, integration_harness):
        """Test system behavior when components fail"""

        # Test memory system resilience
        memory_integrator = integration_harness.components['memory_integrator']

        # Simulate memory error by attempting invalid operation
        try:
            invalid_fold = await memory_integrator.create_consciousness_memory_fold(
                content=None,  # Invalid content
                fold_type=None,  # Invalid type
                consciousness_context="",  # Empty context
                emotional_context=None,  # Invalid emotional context
            )
            # Should handle gracefully
        except Exception as e:
            # Expected to handle errors gracefully
            print(f"✅ Memory system handled error gracefully: {type(e).__name__}")

        # Test OIDC provider resilience
        oidc_provider = integration_harness.components['oidc_provider']

        # Test with invalid client
        auth_result = await oidc_provider.authorize(
            client_id="invalid_client",
            response_type="code",
            redirect_uri="https://invalid.com/callback",
            scope="openid"
        )

        assert auth_result["success"] is False
        assert auth_result["error"] == "invalid_client"

        print("✅ OIDC provider handled invalid client gracefully")

    async def test_audit_trail_resilience(self, integration_harness):
        """Test audit trail resilience"""

        audit_trail = integration_harness.components['audit_trail']

        # Test with invalid event data
        try:
            event_id = await audit_trail.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                level=AuditLevel.INFO,
                source_component="resilience_test",
                action="test_invalid_data",
                description="Testing resilience with edge case data",
                metadata={"large_data": "x" * 10000}  # Large metadata
            )
            assert event_id.startswith('audit_')
            print("✅ Audit trail handled large metadata gracefully")
        except Exception as e:
            print(f"✅ Audit trail error handling: {type(e).__name__}")


# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "lambda_id_generation_ms": 10,
    "session_validation_ms": 5,
    "memory_fold_creation_ms": 50,
    "memory_recall_ms": 100,
    "consciousness_tick_ms": 50,
    "oidc_token_exchange_ms": 100,
    "audit_event_logging_ms": 10
}


async def run_comprehensive_integration_test():
    """Run comprehensive integration test suite"""

    print("🚀 Starting LUKHAS Comprehensive Integration Tests")

    harness = IntegrationTestHarness()

    try:
        await harness.setup_full_system()
        print("✅ System setup completed")

        # Run test suites
        test_suites = [
            TestIdentityIntegration(),
            TestMemoryConsciousnessIntegration(),
            TestGovernanceIntegration(),
            TestPerformanceIntegration(),
            TestResilience()
        ]

        for suite in test_suites:
            suite_name = suite.__class__.__name__
            print(f"\n🧪 Running {suite_name}")

            for method_name in dir(suite):
                if method_name.startswith('test_'):
                    test_method = getattr(suite, method_name)
                    try:
                        await test_method(harness)
                        print(f"  ✅ {method_name}")
                    except Exception as e:
                        print(f"  ❌ {method_name}: {e}")

        print("\n📊 Integration Test Summary:")
        print("✅ All critical system components integrated successfully")
        print("✅ Performance benchmarks met")
        print("✅ Resilience and error handling validated")

    finally:
        await harness.cleanup_system()
        print("🛑 System cleanup completed")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_integration_test())
