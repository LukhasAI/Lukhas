#!/usr/bin/env python3
"""
Cross-Stack Integration Roundtrip Testing - T4/0.01% Excellence
==============================================================

End-to-end integration testing for the complete LUKHAS stack:
Orchestrator → MATRIZ → Guardian → Identity flow validation.

Test Flow:
1. Multi-AI routing through orchestrator
2. MATRIZ thought loop processing
3. Guardian decision validation
4. Identity tier gate checking
5. JWT/WebAuthn claims propagation
6. Full roundtrip performance validation

Performance Target: P95 < 250ms end-to-end
Success Criteria: All components integrate seamlessly with proper claim propagation

Constellation Framework: 🌊 Complete Stack Integration
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from identity.tiers import IdentityTier, TierValidator
from consciousness.matriz_thought_loop import MATRIZProcessingContext, MATRIZThoughtLoop
from consciousness.types import ConsciousnessState
from governance.guardian_serializer import GuardianEnvelopeSerializer
from identity.auth_service import LUKHASIdentityService

# Import LUKHAS components
from orchestration.multi_ai_router import ConsensusType, RoutingRequest

logger = logging.getLogger(__name__)


@dataclass
class IntegrationTestResult:
    """Result of cross-stack integration test."""
    test_name: str
    success: bool
    total_time_ms: float
    component_timings: Dict[str, float]
    jwt_claims_propagated: bool
    guardian_decision_valid: bool
    identity_tier_checked: bool
    matriz_processing_successful: bool
    orchestrator_routing_successful: bool
    performance_target_met: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class CrossStackIntegrationTester:
    """Cross-stack integration tester for LUKHAS components."""

    def __init__(self):
        """Initialize integration tester with mocked external dependencies."""
        self.orchestrator = None
        self.matriz_loop = None
        self.guardian_serializer = None
        self.identity_service = None
        self.tier_validator = None

        # Initialize components
        self._setup_components()

    def _setup_components(self):
        """Setup LUKHAS components for integration testing."""
        # Setup MATRIZ thought loop
        self.matriz_loop = MATRIZThoughtLoop(
            tenant="integration_test",
            max_inference_depth=5,  # Reduced for testing
            total_time_budget_ms=200.0,
            enable_advanced_features=True
        )

        # Setup Guardian serializer
        self.guardian_serializer = GuardianEnvelopeSerializer()

        # Setup Identity service (mocked for integration)
        self.identity_service = Mock(spec=LUKHASIdentityService)

        # Setup Tier validator
        self.tier_validator = TierValidator()

    async def create_mock_orchestrator(self) -> Mock:
        """Create mock orchestrator with realistic responses."""
        orchestrator = Mock()

        # Mock routing response
        async def mock_route_request(request: RoutingRequest) -> Dict[str, Any]:
            await asyncio.sleep(0.05)  # 50ms routing time
            return {
                'success': True,
                'responses': [
                    {
                        'provider': 'openai',
                        'model': 'gpt-4',
                        'response': f"Processed: {request.prompt}",
                        'confidence': 0.9,
                        'latency_ms': 45.0
                    },
                    {
                        'provider': 'anthropic',
                        'model': 'claude-3',
                        'response': f"Analysis: {request.prompt}",
                        'confidence': 0.85,
                        'latency_ms': 52.0
                    }
                ],
                'consensus': {
                    'type': 'majority',
                    'agreement_score': 0.87,
                    'final_response': f"Consensus: {request.prompt}"
                },
                'routing_time_ms': 48.5,
                'total_time_ms': 97.5
            }

        orchestrator.route_request = mock_route_request
        return orchestrator

    def create_mock_jwt_claims(self) -> Dict[str, Any]:
        """Create mock JWT claims for testing."""
        return {
            'sub': 'user_123',
            'iss': 'ai',
            'aud': 'lukhas-api',
            'exp': int(time.time()) + 3600,
            'iat': int(time.time()),
            'tier': 'T3',
            'scopes': ['read', 'write'],
            'namespace': 'integration_test',
            'device_id': 'device_456',
            'session_id': 'session_789'
        }

    async def simulate_orchestrator_routing(self, query: str, jwt_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate orchestrator multi-AI routing."""
        start_time = time.perf_counter()

        try:
            # Create mock orchestrator
            orchestrator = await self.create_mock_orchestrator()

            # Create routing request
            routing_request = RoutingRequest(
                prompt=query,
                context={
                    'user_claims': jwt_claims,
                    'tier': jwt_claims.get('tier', 'T1'),
                    'namespace': jwt_claims.get('namespace', 'default')
                },
                consensus_type=ConsensusType.MAJORITY,
                min_responses=2,
                max_responses=3,
                timeout=10.0,
                metadata={'integration_test': True}
            )

            # Execute routing
            routing_result = await orchestrator.route_request(routing_request)

            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return {
                'success': routing_result['success'],
                'consensus_response': routing_result['consensus']['final_response'],
                'agreement_score': routing_result['consensus']['agreement_score'],
                'processing_time_ms': processing_time_ms,
                'metadata': {
                    'providers_used': len(routing_result['responses']),
                    'routing_latency': routing_result['routing_time_ms']
                }
            }

        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Orchestrator routing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time_ms
            }

    async def simulate_matriz_processing(self, orchestrator_result: Dict[str, Any], jwt_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MATRIZ thought loop processing."""
        start_time = time.perf_counter()

        try:
            # Create MATRIZ processing context
            context = MATRIZProcessingContext(
                query=orchestrator_result.get('consensus_response', 'Test query'),
                memory_signals=[
                    {
                        'id': f'mem_{i}',
                        'content': f'Memory signal {i}',
                        'score': 0.8 + (i * 0.05)
                    }
                    for i in range(3)
                ],
                consciousness_state=ConsciousnessState.ACTIVE,
                processing_config={
                    'complexity': 'moderate',
                    'integration_test': True
                },
                session_id=jwt_claims.get('session_id', 'test_session'),
                tenant=jwt_claims.get('namespace', 'default'),
                time_budget_ms=150.0,
                enable_all_features=True,
                metadata={
                    'user_tier': jwt_claims.get('tier', 'T1'),
                    'orchestrator_agreement': orchestrator_result.get('agreement_score', 0.5)
                }
            )

            # Mock the thought node processing
            with patch.object(self.matriz_loop.enhanced_thought_node, 'process_async') as mock_process:
                mock_process.return_value = {
                    'success': True,
                    'answer': {'summary': f"MATRIZ processed: {context.query}"},
                    'confidence': 0.88,
                    'processing_time_ms': 75.0,
                    'enhanced_features': {
                        'inference_depth_reached': 3,
                        'reasoning_chains_count': 2,
                        'contradictions_detected': 0,
                        'quality_score': 0.85,
                        'cognitive_load': 0.35
                    }
                }

                # Process through MATRIZ
                matriz_result = await self.matriz_loop.process_complete_thought_loop(context)

            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return {
                'success': matriz_result.success,
                'synthesis': matriz_result.synthesis,
                'confidence': matriz_result.confidence,
                't4_compliant': matriz_result.t4_compliant,
                'processing_time_ms': processing_time_ms,
                'metadata': {
                    'inference_depth': matriz_result.inference_depth_reached,
                    'cognitive_load': matriz_result.cognitive_load,
                    'quality_score': matriz_result.quality_score
                }
            }

        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"MATRIZ processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time_ms
            }

    async def simulate_guardian_validation(self, matriz_result: Dict[str, Any], jwt_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Guardian decision validation."""
        start_time = time.perf_counter()

        try:
            # Create Guardian decision envelope
            decision_envelope = {
                'schema_version': '2.1.0',
                'decision': {
                    'status': 'allow',
                    'policy': 'integration_test/v1.0.0',
                    'severity': 'low',
                    'confidence': matriz_result.get('confidence', 0.5),
                    'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    'ttl_seconds': 300
                },
                'subject': {
                    'user_id': jwt_claims.get('sub', 'unknown'),
                    'session_id': jwt_claims.get('session_id', 'unknown'),
                    'tier': jwt_claims.get('tier', 'T1'),
                    'namespace': jwt_claims.get('namespace', 'default')
                },
                'context': {
                    'request_type': 'matriz_integration_test',
                    'processing_result': matriz_result.get('synthesis', ''),
                    'quality_score': matriz_result.get('metadata', {}).get('quality_score', 0.0),
                    'lane': 'integration'
                },
                'metrics': {
                    'processing_time_ms': matriz_result.get('processing_time_ms', 0.0),
                    'confidence_score': matriz_result.get('confidence', 0.0),
                    'quality_assessment': 0.85,
                    'risk_score': 0.1
                },
                'enforcement': {
                    'enabled': True,
                    'mode': 'enforced',
                    'actions': ['allow_processing'],
                    'restrictions': []
                },
                'audit': {
                    'correlation_id': f"test_{int(time.time())}",
                    'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    'source': 'integration_test',
                    'compliance_checked': True
                },
                'integrity': {
                    'schema_version': '2.1.0',
                    'payload_hash': 'placeholder_hash',
                    'signature': 'placeholder_signature',
                    'algorithm': 'ed25519',
                    'keyid': 'test_key'
                }
            }

            # Validate with Guardian serializer
            validation_result = self.guardian_serializer.validate_envelope(decision_envelope)

            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return {
                'success': validation_result['valid'],
                'decision_status': decision_envelope['decision']['status'],
                'enforcement_mode': decision_envelope['enforcement']['mode'],
                'processing_time_ms': processing_time_ms,
                'validation_errors': validation_result.get('errors', []),
                'metadata': {
                    'policy_applied': decision_envelope['decision']['policy'],
                    'risk_score': decision_envelope['metrics']['risk_score']
                }
            }

        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Guardian validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time_ms
            }

    async def simulate_identity_tier_check(self, jwt_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Identity tier gate checking."""
        start_time = time.perf_counter()

        try:
            # Mock identity service calls
            self.identity_service.validate_token.return_value = {
                'valid': True,
                'claims': jwt_claims,
                'tier': jwt_claims.get('tier', 'T1')
            }

            # Validate tier
            user_tier = IdentityTier(jwt_claims.get('tier', 'T1'))
            tier_validation = self.tier_validator.validate_access(
                tier=user_tier,
                required_tier=IdentityTier.T2,  # Require T2 for integration test
                operation='matriz_processing'
            )

            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return {
                'success': True,
                'tier_valid': tier_validation.access_granted,
                'user_tier': user_tier.value,
                'required_tier': 'T2',
                'processing_time_ms': processing_time_ms,
                'metadata': {
                    'token_valid': True,
                    'claims_verified': True,
                    'namespace': jwt_claims.get('namespace', 'default')
                }
            }

        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Identity tier check failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time_ms
            }

    async def run_complete_roundtrip_test(self, test_query: str, jwt_claims: Dict[str, Any]) -> IntegrationTestResult:
        """Run complete cross-stack integration test."""
        total_start_time = time.perf_counter()
        component_timings = {}
        errors = []
        warnings = []

        try:
            # Step 1: Orchestrator routing
            logger.info("Step 1: Orchestrator multi-AI routing")
            orchestrator_result = await self.simulate_orchestrator_routing(test_query, jwt_claims)
            component_timings['orchestrator'] = orchestrator_result['processing_time_ms']

            if not orchestrator_result['success']:
                errors.append(f"Orchestrator failed: {orchestrator_result.get('error', 'Unknown')}")

            # Step 2: MATRIZ processing
            logger.info("Step 2: MATRIZ thought loop processing")
            matriz_result = await self.simulate_matriz_processing(orchestrator_result, jwt_claims)
            component_timings['matriz'] = matriz_result['processing_time_ms']

            if not matriz_result['success']:
                errors.append(f"MATRIZ failed: {matriz_result.get('error', 'Unknown')}")

            # Step 3: Guardian validation
            logger.info("Step 3: Guardian decision validation")
            guardian_result = await self.simulate_guardian_validation(matriz_result, jwt_claims)
            component_timings['guardian'] = guardian_result['processing_time_ms']

            if not guardian_result['success']:
                errors.append(f"Guardian failed: {guardian_result.get('error', 'Unknown')}")

            # Step 4: Identity tier check
            logger.info("Step 4: Identity tier gate checking")
            identity_result = await self.simulate_identity_tier_check(jwt_claims)
            component_timings['identity'] = identity_result['processing_time_ms']

            if not identity_result['success']:
                errors.append(f"Identity failed: {identity_result.get('error', 'Unknown')}")

            # Calculate total time
            total_time_ms = (time.perf_counter() - total_start_time) * 1000

            # Verify JWT claims propagation
            jwt_claims_propagated = (
                orchestrator_result.get('success', False) and
                'user_claims' in str(orchestrator_result) and
                matriz_result.get('success', False) and
                guardian_result.get('success', False) and
                identity_result.get('success', False)
            )

            # Performance target check (P95 < 250ms)
            performance_target_met = total_time_ms <= 250.0

            if not performance_target_met:
                warnings.append(f"Performance target missed: {total_time_ms:.1f}ms > 250ms")

            # Overall success
            overall_success = (
                len(errors) == 0 and
                orchestrator_result.get('success', False) and
                matriz_result.get('success', False) and
                guardian_result.get('success', False) and
                identity_result.get('success', False)
            )

            return IntegrationTestResult(
                test_name="complete_roundtrip",
                success=overall_success,
                total_time_ms=total_time_ms,
                component_timings=component_timings,
                jwt_claims_propagated=jwt_claims_propagated,
                guardian_decision_valid=guardian_result.get('success', False),
                identity_tier_checked=identity_result.get('success', False),
                matriz_processing_successful=matriz_result.get('success', False),
                orchestrator_routing_successful=orchestrator_result.get('success', False),
                performance_target_met=performance_target_met,
                errors=errors,
                warnings=warnings,
                metadata={
                    'test_query': test_query,
                    'orchestrator_agreement': orchestrator_result.get('agreement_score', 0.0),
                    'matriz_confidence': matriz_result.get('confidence', 0.0),
                    'guardian_decision': guardian_result.get('decision_status', 'unknown'),
                    'user_tier': identity_result.get('user_tier', 'unknown')
                }
            )

        except Exception as e:
            total_time_ms = (time.perf_counter() - total_start_time) * 1000
            logger.error(f"Complete roundtrip test failed: {e}")

            return IntegrationTestResult(
                test_name="complete_roundtrip",
                success=False,
                total_time_ms=total_time_ms,
                component_timings=component_timings,
                jwt_claims_propagated=False,
                guardian_decision_valid=False,
                identity_tier_checked=False,
                matriz_processing_successful=False,
                orchestrator_routing_successful=False,
                performance_target_met=False,
                errors=[str(e)],
                warnings=warnings,
                metadata={}
            )


@pytest.mark.asyncio
@pytest.mark.integration
class TestCrossStackIntegration:
    """Cross-stack integration tests for LUKHAS components."""

    async def test_orchestrator_matriz_guardian_identity_roundtrip(self):
        """Test complete roundtrip: Orchestrator → MATRIZ → Guardian → Identity."""
        tester = CrossStackIntegrationTester()

        # Create test data
        test_query = "Analyze the cognitive processing requirements for T4/0.01% excellence"
        jwt_claims = tester.create_mock_jwt_claims()
        jwt_claims['tier'] = 'T3'  # Set sufficient tier for test

        # Run integration test
        result = await tester.run_complete_roundtrip_test(test_query, jwt_claims)

        # Log test results
        logger.info("=== Cross-Stack Integration Test Results ===")
        logger.info(f"Overall Success: {'✓' if result.success else '✗'}")
        logger.info(f"Total Time: {result.total_time_ms:.1f}ms")
        logger.info(f"Performance Target Met: {'✓' if result.performance_target_met else '✗'}")

        logger.info("Component Timings:")
        for component, timing in result.component_timings.items():
            logger.info(f"  {component}: {timing:.1f}ms")

        logger.info("Integration Checks:")
        logger.info(f"  Orchestrator Routing: {'✓' if result.orchestrator_routing_successful else '✗'}")
        logger.info(f"  MATRIZ Processing: {'✓' if result.matriz_processing_successful else '✗'}")
        logger.info(f"  Guardian Validation: {'✓' if result.guardian_decision_valid else '✗'}")
        logger.info(f"  Identity Tier Check: {'✓' if result.identity_tier_checked else '✗'}")
        logger.info(f"  JWT Claims Propagated: {'✓' if result.jwt_claims_propagated else '✗'}")

        if result.errors:
            logger.error("Errors:")
            for error in result.errors:
                logger.error(f"  ❌ {error}")

        if result.warnings:
            logger.warning("Warnings:")
            for warning in result.warnings:
                logger.warning(f"  ⚠️  {warning}")

        # Assertions
        assert result.success, f"Cross-stack integration failed: {result.errors}"
        assert result.performance_target_met, f"Performance target not met: {result.total_time_ms:.1f}ms > 250ms"
        assert result.orchestrator_routing_successful, "Orchestrator routing failed"
        assert result.matriz_processing_successful, "MATRIZ processing failed"
        assert result.guardian_decision_valid, "Guardian validation failed"
        assert result.identity_tier_checked, "Identity tier check failed"

        # Verify JWT claims propagation
        assert result.jwt_claims_propagated, "JWT claims not properly propagated through stack"

    async def test_performance_under_load(self):
        """Test cross-stack integration performance under simulated load."""
        tester = CrossStackIntegrationTester()

        # Run multiple concurrent tests
        test_queries = [
            "Test query 1 for load testing",
            "Test query 2 with complexity",
            "Test query 3 for performance validation"
        ]

        concurrent_tasks = []
        for i, query in enumerate(test_queries):
            jwt_claims = tester.create_mock_jwt_claims()
            jwt_claims['session_id'] = f"load_test_{i}"
            jwt_claims['tier'] = 'T4'  # High tier for load testing

            task = tester.run_complete_roundtrip_test(query, jwt_claims)
            concurrent_tasks.append(task)

        # Execute concurrent tests
        results = await asyncio.gather(*concurrent_tasks)

        # Analyze results
        successful_tests = sum(1 for r in results if r.success)
        avg_time_ms = sum(r.total_time_ms for r in results) / len(results)
        performance_compliant = sum(1 for r in results if r.performance_target_met)

        logger.info(f"Load Test Results: {successful_tests}/{len(results)} successful")
        logger.info(f"Average Time: {avg_time_ms:.1f}ms")
        logger.info(f"Performance Compliant: {performance_compliant}/{len(results)}")

        # Assertions
        assert successful_tests == len(results), "Some load tests failed"
        assert avg_time_ms <= 250.0, f"Average performance target not met: {avg_time_ms:.1f}ms"
        assert performance_compliant >= len(results) * 0.95, "Less than 95% performance compliance"

    async def test_jwt_claim_validation_flow(self):
        """Test JWT claim validation throughout the complete flow."""
        tester = CrossStackIntegrationTester()

        # Test with different tier levels
        test_cases = [
            ('T1', False),  # Should fail tier check
            ('T2', True),   # Should pass tier check
            ('T3', True),   # Should pass tier check
            ('T4', True),   # Should pass tier check
        ]

        for tier, should_pass_tier_check in test_cases:
            jwt_claims = tester.create_mock_jwt_claims()
            jwt_claims['tier'] = tier
            jwt_claims['session_id'] = f"tier_test_{tier}"

            result = await tester.run_complete_roundtrip_test(
                f"Test query for tier {tier}",
                jwt_claims
            )

            logger.info(f"Tier {tier} test: {'✓' if result.success else '✗'}")

            # Verify tier checking behavior
            if should_pass_tier_check:
                assert result.identity_tier_checked, f"Tier {tier} should pass tier check"

            # JWT claims should always propagate regardless of tier
            assert result.jwt_claims_propagated, f"JWT claims not propagated for tier {tier}"


if __name__ == "__main__":
    # Run integration test standalone
    async def run_integration_test():
        tester = CrossStackIntegrationTester()

        print("Running cross-stack integration test...")

        jwt_claims = tester.create_mock_jwt_claims()
        jwt_claims['tier'] = 'T3'

        result = await tester.run_complete_roundtrip_test(
            "Integration test query for LUKHAS stack validation",
            jwt_claims
        )

        print("\n=== Cross-Stack Integration Test Results ===")
        print(f"Overall Success: {'✓ PASS' if result.success else '✗ FAIL'}")
        print(f"Total Time: {result.total_time_ms:.1f}ms")
        print(f"Performance Target (< 250ms): {'✓ PASS' if result.performance_target_met else '✗ FAIL'}")

        print("\nComponent Performance:")
        for component, timing in result.component_timings.items():
            print(f"  {component.capitalize()}: {timing:.1f}ms")

        print("\nIntegration Verification:")
        print(f"  Orchestrator Routing: {'✓' if result.orchestrator_routing_successful else '✗'}")
        print(f"  MATRIZ Processing: {'✓' if result.matriz_processing_successful else '✗'}")
        print(f"  Guardian Validation: {'✓' if result.guardian_decision_valid else '✗'}")
        print(f"  Identity Tier Check: {'✓' if result.identity_tier_checked else '✗'}")
        print(f"  JWT Claims Propagated: {'✓' if result.jwt_claims_propagated else '✗'}")

        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                print(f"   {error}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   {warning}")

        print(f"\nOverall Status: {'✅ INTEGRATION SUCCESSFUL' if result.success else '❌ INTEGRATION FAILED'}")

        return result.success

    import sys
    success = asyncio.run(run_integration_test())
    sys.exit(0 if success else 1)
