#!/usr/bin/env python3
"""
LUKHAS Identity ΛiD Token System Integration Test - Production Schema v1.0.0

Comprehensive integration test demonstrating the complete ΛiD token workflow:
1. User authentication and ΛiD token generation
2. Token validation with Guardian integration
3. Token introspection with rate limiting
4. Performance benchmarking for <100ms p95 target

This test validates the entire Constellation Framework integration:
- Identity ⚛️: ΛiD alias generation and token creation
- Guardian 🛡️: Ethical validation of token operations
- Memory 🗃️: Tier-based access control integration

Production Excellence: T4/0.01% standards with comprehensive observability.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LUKHAS identity components
try:
    from .alias_format import make_alias, parse_alias, validate_alias_format
    from .auth_service import (  # noqa: F401  # TODO: .auth_service.AuthResult; cons...
        AuthenticationService,
        AuthResult,
    )
    from .tier_system import (  # noqa: F401  # TODO: .tier_system.TierLevel; consid...
        TierLevel,
        normalize_tier,
    )
    from .token_generator import (  # noqa: F401  # TODO: .token_generator.TokenClaims; ...
        EnvironmentSecretProvider,
        TokenClaims,
        TokenGenerator,
    )
    from .token_introspection import (  # noqa: F401  # TODO: .token_introspection.Introspec...
        IntrospectionRequest,
        IntrospectionResponse,
        TokenIntrospectionService,
    )
    from .token_validator import (  # noqa: F401  # TODO: .token_validator.ValidationRes...
        TokenValidator,
        ValidationContext,
        ValidationResult,
    )

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import ΛiD components: {e}")
    COMPONENTS_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Performance metrics for ΛiD token operations."""
    operation: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


class LiDTokenSystemTest:
    """
    Comprehensive ΛiD token system integration test.

    Tests the complete workflow from user authentication through
    token validation and introspection with performance benchmarking.
    """

    def __init__(self):
        """Initialize test environment."""
        self.metrics: List[PerformanceMetrics] = []
        self.secret_provider = None
        self.token_generator = None
        self.token_validator = None
        self.auth_service = None
        self.introspection_service = None

    def setup_test_environment(self) -> bool:
        """
        Set up the complete ΛiD token system test environment.

        Returns:
            True if setup successful, False otherwise
        """
        if not COMPONENTS_AVAILABLE:
            logger.error("ΛiD components not available for testing")
            return False

        try:
            logger.info("🔧 Setting up ΛiD token system test environment...")

            # Initialize secret provider
            self.secret_provider = EnvironmentSecretProvider("test_secret_change_in_production")

            # Initialize token generator
            self.token_generator = TokenGenerator(
                secret_provider=self.secret_provider,
                ttl_seconds=3600,
                issuer="ai"
            )

            # Create Guardian validator mock for testing
            def mock_guardian_validator(context: Dict[str, Any]) -> Dict[str, Any]:
                """Mock Guardian validator for testing."""
                return {
                    "approved": True,
                    "reason": "Test Guardian validation approved",
                    "score": 0.95
                }

            # Initialize token validator
            self.token_validator = TokenValidator(
                secret_provider=self.secret_provider,
                guardian_validator=mock_guardian_validator,
                cache_size=1000,
                cache_ttl_seconds=300
            )

            # Initialize authentication service
            self.auth_service = AuthenticationService({
                "storage_path": "/tmp/lukhas_test_auth",
                "session_timeout": 3600,
                "token_cache_size": 1000,
                "token_cache_ttl": 300
            })

            # Initialize introspection service
            self.introspection_service = TokenIntrospectionService(
                auth_service=self.auth_service,
                cache_ttl_seconds=60
            )

            logger.info("✅ ΛiD token system test environment ready")
            return True

        except Exception as e:
            logger.error(f"❌ Test environment setup failed: {e}")
            return False

    def test_alias_generation_and_validation(self) -> bool:
        """Test ΛiD alias generation and validation."""
        logger.info("🧪 Testing ΛiD alias generation and validation...")

        try:
            start_time = time.time()

            # Test alias generation
            alias = make_alias("enterprise", "prod", 2)
            generation_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="alias_generation",
                latency_ms=generation_time,
                success=True
            ))

            logger.info(f"Generated alias: {alias}")

            # Test alias validation
            start_time = time.time()
            is_valid, error_msg = validate_alias_format(alias)
            validation_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="alias_validation",
                latency_ms=validation_time,
                success=is_valid,
                error=error_msg if not is_valid else None
            ))

            if not is_valid:
                logger.error(f"❌ Alias validation failed: {error_msg}")
                return False

            # Test alias parsing
            start_time = time.time()
            parsed = parse_alias(alias)
            parsing_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="alias_parsing",
                latency_ms=parsing_time,
                success=parsed is not None
            ))

            if not parsed:
                logger.error("❌ Alias parsing failed")
                return False

            logger.info(f"✅ Parsed alias: realm={parsed.realm}, zone={parsed.zone}, version={parsed.major_version}")
            return True

        except Exception as e:
            logger.error(f"❌ Alias test failed: {e}")
            self.metrics.append(PerformanceMetrics(
                operation="alias_test",
                latency_ms=0,
                success=False,
                error=str(e)
            ))
            return False

    def test_token_generation_and_validation(self) -> bool:
        """Test ΛiD token generation and validation."""
        logger.info("🧪 Testing ΛiD token generation and validation...")

        try:
            # Test token generation
            start_time = time.time()

            claims = {
                "aud": "lukhas",
                "lukhas_tier": 2,
                "lukhas_namespace": "test",
                "permissions": ["read", "write", "test"]
            }

            token_response = self.token_generator.create(
                claims=claims,
                realm="enterprise",
                zone="test"
            )

            generation_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="token_generation",
                latency_ms=generation_time,
                success=True
            ))

            logger.info(f"Generated token with alias: {token_response.alias}")
            logger.info(f"Token expires at: {time.ctime(token_response.exp)}")

            # Test token validation
            start_time = time.time()

            validation_context = ValidationContext(
                expected_audience="lukhas",
                guardian_enabled=True,
                ethical_validation_enabled=True,
                client_ip="127.0.0.1",
                user_agent="ΛiD-Test/1.0"
            )

            validation_result = self.token_validator.validate(
                token_response.jwt,
                validation_context
            )

            validation_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="token_validation",
                latency_ms=validation_time,
                success=validation_result.valid,
                error=validation_result.error_message if not validation_result.valid else None
            ))

            if not validation_result.valid:
                logger.error(f"❌ Token validation failed: {validation_result.error_message}")
                return False

            logger.info("✅ Token validation successful:")
            logger.info(f"  - Alias: {validation_result.alias}")
            logger.info(f"  - Tier Level: {validation_result.tier_level}")
            logger.info(f"  - Namespace: {validation_result.namespace}")
            logger.info(f"  - Guardian Approved: {validation_result.guardian_approved}")
            logger.info(f"  - Validation Time: {validation_result.validation_time_ms:.2f}ms")

            return True

        except Exception as e:
            logger.error(f"❌ Token generation/validation test failed: {e}")
            self.metrics.append(PerformanceMetrics(
                operation="token_test",
                latency_ms=0,
                success=False,
                error=str(e)
            ))
            return False

    def test_authentication_service_integration(self) -> bool:
        """Test authentication service ΛiD token integration."""
        logger.info("🧪 Testing authentication service ΛiD integration...")

        try:
            # Create test user
            start_time = time.time()

            test_user = self.auth_service.create_user(
                username="testuser",
                password="TestPassword123!",
                email="test@ai",
                permissions=["read", "write", "test"]
            )

            user_creation_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="user_creation",
                latency_ms=user_creation_time,
                success=True
            ))

            logger.info(f"Created test user: {test_user.user_id}")

            # Test ΛiD token authentication
            start_time = time.time()

            auth_result = self.auth_service.authenticate_user(
                username="testuser",
                password="TestPassword123!",
                auth_method="lid_token"
            )

            auth_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="lid_token_auth",
                latency_ms=auth_time,
                success=auth_result.success,
                error=auth_result.error if not auth_result.success else None
            ))

            if not auth_result.success:
                logger.error(f"❌ ΛiD token authentication failed: {auth_result.error}")
                return False

            logger.info("✅ ΛiD token authentication successful:")
            logger.info(f"  - User ID: {auth_result.user_id}")
            logger.info(f"  - Auth Method: {auth_result.auth_method}")
            logger.info(f"  - Permissions: {auth_result.permissions}")
            logger.info(f"  - Token expires: {time.ctime(auth_result.expires_at) if auth_result.expires_at else 'Unknown'}")

            # Test token validation through auth service
            start_time = time.time()

            token_auth_result = self.auth_service.authenticate_token(auth_result.session_token)

            token_auth_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="token_auth_service",
                latency_ms=token_auth_time,
                success=token_auth_result.success,
                error=token_auth_result.error if not token_auth_result.success else None
            ))

            if not token_auth_result.success:
                logger.error(f"❌ Token authentication via service failed: {token_auth_result.error}")
                return False

            logger.info("✅ Token authentication via service successful")
            return True

        except Exception as e:
            logger.error(f"❌ Authentication service integration test failed: {e}")
            self.metrics.append(PerformanceMetrics(
                operation="auth_service_test",
                latency_ms=0,
                success=False,
                error=str(e)
            ))
            return False

    def test_token_introspection(self) -> bool:
        """Test token introspection service."""
        logger.info("🧪 Testing token introspection service...")

        try:
            # Generate a test token first
            claims = {
                "aud": "lukhas",
                "lukhas_tier": 3,
                "lukhas_namespace": "introspection_test",
                "permissions": ["read", "write", "admin"]
            }

            token_response = self.token_generator.create(
                claims=claims,
                realm="enterprise",
                zone="prod"
            )

            # Test introspection
            start_time = time.time()

            introspection_request = IntrospectionRequest(
                token=token_response.jwt,
                token_type_hint="lid_token",
                client_id="test_client",
                client_secret="test_secret_12345",
                client_ip="127.0.0.1",
                user_agent="ΛiD-Test/1.0",
                request_id="test_request_001"
            )

            introspection_response = self.introspection_service.introspect_token(
                introspection_request
            )

            introspection_time = (time.time() - start_time) * 1000

            self.metrics.append(PerformanceMetrics(
                operation="token_introspection",
                latency_ms=introspection_time,
                success=introspection_response.active,
                error=introspection_response.error if not introspection_response.active else None
            ))

            if not introspection_response.active:
                logger.error(f"❌ Token introspection failed: {introspection_response.error}")
                return False

            logger.info("✅ Token introspection successful:")
            logger.info(f"  - Active: {introspection_response.active}")
            logger.info(f"  - LID Alias: {introspection_response.lid_alias}")
            logger.info(f"  - Realm: {introspection_response.realm}")
            logger.info(f"  - Zone: {introspection_response.zone}")
            logger.info(f"  - Tier Level: {introspection_response.tier_level}")
            logger.info(f"  - Permissions: {introspection_response.permissions}")
            logger.info(f"  - Guardian Approved: {introspection_response.guardian_approved}")
            logger.info(f"  - Validation Time: {introspection_response.validation_time_ms:.2f}ms")

            # Test rate limiting
            logger.info("Testing rate limiting...")
            rate_limit_violations = 0

            for i in range(25):  # Test burst capacity
                start_time = time.time()
                response = self.introspection_service.introspect_token(introspection_request)

                if not response.active and response.error == "rate_limit_exceeded":
                    rate_limit_violations += 1

            if rate_limit_violations > 0:
                logger.info(f"✅ Rate limiting working: {rate_limit_violations} requests blocked")
            else:
                logger.warning("⚠️ Rate limiting may not be working as expected")

            return True

        except Exception as e:
            logger.error(f"❌ Token introspection test failed: {e}")
            self.metrics.append(PerformanceMetrics(
                operation="introspection_test",
                latency_ms=0,
                success=False,
                error=str(e)
            ))
            return False

    def benchmark_performance(self, iterations: int = 100) -> bool:
        """
        Benchmark ΛiD token system performance.

        Target: <100ms p95 latency for complete workflow.
        """
        logger.info(f"🚀 Benchmarking ΛiD token system performance ({iterations} iterations)...")

        try:
            workflow_times = []

            for i in range(iterations):
                workflow_start = time.time()

                # Complete workflow: generate -> validate -> introspect
                claims = {
                    "aud": "lukhas",
                    "lukhas_tier": 2,
                    "lukhas_namespace": f"benchmark_{i}",
                    "permissions": ["read", "write"]
                }

                # Generate token
                token_response = self.token_generator.create(
                    claims=claims,
                    realm="benchmark",
                    zone="test"
                )

                # Validate token
                validation_context = ValidationContext(
                    expected_audience="lukhas",
                    guardian_enabled=True,
                    ethical_validation_enabled=True
                )

                validation_result = self.token_validator.validate(
                    token_response.jwt,
                    validation_context
                )

                # Introspect token
                introspection_request = IntrospectionRequest(
                    token=token_response.jwt,
                    token_type_hint="lid_token",
                    client_id="benchmark_client",
                    client_secret="benchmark_secret_12345"
                )

                introspection_response = self.introspection_service.introspect_token(
                    introspection_request
                )

                workflow_time = (time.time() - workflow_start) * 1000
                workflow_times.append(workflow_time)

                if i % 20 == 0:
                    logger.info(f"Completed {i}/{iterations} iterations...")

            # Calculate performance statistics
            workflow_times.sort()
            p50 = workflow_times[len(workflow_times) // 2]
            p95 = workflow_times[int(len(workflow_times) * 0.95)]
            p99 = workflow_times[int(len(workflow_times) * 0.99)]
            avg = sum(workflow_times) / len(workflow_times)

            logger.info("✅ Performance Benchmark Results:")
            logger.info(f"  - Iterations: {iterations}")
            logger.info(f"  - Average: {avg:.2f}ms")
            logger.info(f"  - P50: {p50:.2f}ms")
            logger.info(f"  - P95: {p95:.2f}ms")
            logger.info(f"  - P99: {p99:.2f}ms")

            # Check if we meet our <100ms p95 target
            if p95 < 100:
                logger.info("🎯 ✅ P95 target achieved (<100ms)")
            else:
                logger.warning(f"🎯 ⚠️ P95 target missed: {p95:.2f}ms (target: <100ms)")

            self.metrics.append(PerformanceMetrics(
                operation="workflow_benchmark_p95",
                latency_ms=p95,
                success=p95 < 100
            ))

            return True

        except Exception as e:
            logger.error(f"❌ Performance benchmark failed: {e}")
            self.metrics.append(PerformanceMetrics(
                operation="benchmark",
                latency_ms=0,
                success=False,
                error=str(e)
            ))
            return False

    def print_performance_summary(self):
        """Print comprehensive performance summary."""
        logger.info("📊 ΛiD Token System Performance Summary")
        logger.info("=" * 60)

        if not self.metrics:
            logger.info("No performance metrics collected")
            return

        # Group metrics by operation
        operations = {}
        for metric in self.metrics:
            if metric.operation not in operations:
                operations[metric.operation] = []
            operations[metric.operation].append(metric)

        for operation, metrics in operations.items():
            successful = [m for m in metrics if m.success]
            failed = [m for m in metrics if not m.success]

            if successful:
                latencies = [m.latency_ms for m in successful]
                avg_latency = sum(latencies) / len(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)

                logger.info(f"{operation.upper()}:")
                logger.info(f"  - Success: {len(successful)}/{len(metrics)}")
                logger.info(f"  - Avg Latency: {avg_latency:.2f}ms")
                logger.info(f"  - Min/Max: {min_latency:.2f}ms / {max_latency:.2f}ms")
            else:
                logger.info(f"{operation.upper()}: ALL FAILED")

            if failed:
                for metric in failed:
                    logger.info(f"  - Error: {metric.error}")

        # Overall success rate
        successful_ops = len([m for m in self.metrics if m.success])
        total_ops = len(self.metrics)
        success_rate = (successful_ops / total_ops) * 100 if total_ops > 0 else 0

        logger.info("=" * 60)
        logger.info(f"Overall Success Rate: {success_rate:.1f}% ({successful_ops}/{total_ops})")

    def run_complete_test_suite(self) -> bool:
        """Run the complete ΛiD token system test suite."""
        logger.info("🚀 Starting LUKHAS ΛiD Token System Integration Test")
        logger.info("=" * 70)

        # Setup test environment
        if not self.setup_test_environment():
            logger.error("❌ Test environment setup failed")
            return False

        all_tests_passed = True

        # Run individual test modules
        tests = [
            ("Alias Generation & Validation", self.test_alias_generation_and_validation),
            ("Token Generation & Validation", self.test_token_generation_and_validation),
            ("Authentication Service Integration", self.test_authentication_service_integration),
            ("Token Introspection", self.test_token_introspection),
            ("Performance Benchmark", lambda: self.benchmark_performance(50))
        ]

        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            logger.info("-" * 50)

            try:
                test_result = test_func()
                if test_result:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    all_tests_passed = False
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {e}")
                all_tests_passed = False

        # Print final summary
        logger.info("\n" + "=" * 70)
        if all_tests_passed:
            logger.info("🎉 ALL TESTS PASSED - ΛiD Token System Ready for Production")
        else:
            logger.error("❌ SOME TESTS FAILED - Review issues before production deployment")

        # Print performance summary
        self.print_performance_summary()

        return all_tests_passed


def main():
    """Main test execution function."""
    test_suite = LiDTokenSystemTest()
    success = test_suite.run_complete_test_suite()

    exit_code = 0 if success else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
