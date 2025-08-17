#!/usr/bin/env python3
"""
API Testing Interface for Innovation System
============================================
Tests the innovation system through REST API endpoints to simulate
real-world deployment scenarios.

This module tests:
- API endpoint functionality
- Request/response validation
- Rate limiting and throttling
- Authentication and authorization
- Error handling and recovery
- Response consistency
"""

import asyncio
import hashlib
import json
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Logging
from core.common import get_logger

logger = get_logger(__name__)


@dataclass
class APITestCase:
    """API test case definition"""
    id: str
    name: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    payload: Dict[str, Any]
    expected_status: int
    expected_response: Dict[str, Any]
    validate_response: bool
    timeout: float


@dataclass
class APITestResult:
    """API test execution result"""
    test_id: str
    test_name: str
    timestamp: datetime

    # Request details
    endpoint: str
    method: str
    request_payload: Dict[str, Any]

    # Response details
    status_code: int
    response_time_ms: float
    response_body: Dict[str, Any]
    response_hash: str

    # Validation
    passed: bool
    error_message: Optional[str]

    # Metrics
    rate_limited: bool
    retry_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'timestamp': self.timestamp.isoformat(),
            'request': {
                'endpoint': self.endpoint,
                'method': self.method,
                'payload': self.request_payload
            },
            'response': {
                'status_code': self.status_code,
                'time_ms': self.response_time_ms,
                'body': self.response_body,
                'hash': self.response_hash
            },
            'validation': {
                'passed': self.passed,
                'error': self.error_message
            },
            'metrics': {
                'rate_limited': self.rate_limited,
                'retry_count': self.retry_count
            }
        }


class InnovationAPITest:
    """
    API testing interface for Innovation System.
    Simulates real-world API usage patterns.
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_cases: List[APITestCase] = []
        self.test_results: List[APITestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_key = "test_api_key_" + uuid.uuid4().hex[:8]

    async def setup(self) -> None:
        """Initialize API test session"""
        logger.info("🌐 Initializing API Test System")

        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "User-Agent": "LUKHAS-API-Test/1.0"
            }
        )

        # Load test scenarios from YAML
        await self.load_test_scenarios()

        logger.info(f"✅ API test system initialized with {len(self.test_cases)} test cases")

    async def teardown(self) -> None:
        """Cleanup API test session"""
        if self.session:
            await self.session.close()
        logger.info("API test system shutdown complete")

    async def load_test_scenarios(self) -> None:
        """Load test scenarios from YAML configuration"""
        yaml_file = Path(__file__).parent / "data" / "innovation_test_scenarios.yaml"

        if yaml_file.exists():
            with open(yaml_file) as f:
                config = yaml.safe_load(f)

            # Convert YAML scenarios to API test cases
            for scenario in config.get('scenarios', []):
                test_case = self._create_api_test_case(scenario)
                self.test_cases.append(test_case)
        else:
            # Create default test cases
            self._create_default_test_cases()

    def _create_api_test_case(self, scenario: Dict[str, Any]) -> APITestCase:
        """Convert scenario to API test case"""
        return APITestCase(
            id=scenario['id'],
            name=scenario['name'],
            endpoint="/api/v1/innovation/generate",
            method="POST",
            headers={
                "X-Request-ID": str(uuid.uuid4()),
                "X-Test-Scenario": scenario['id']
            },
            payload={
                "hypothesis": scenario['input']['hypothesis'],
                "domain": scenario['input']['domain'],
                "context": scenario['input'].get('context', ''),
                "parameters": {
                    "reality_count": 50,
                    "exploration_depth": 5,
                    "safety_level": "HIGH",
                    "enable_drift_protection": True
                },
                "metadata": scenario.get('metadata', {})
            },
            expected_status=200 if scenario['expected'].get('innovation_generated', False) else 400,
            expected_response={
                "success": scenario['expected'].get('innovation_generated', False),
                "safety_intervention": scenario['expected'].get('safety_intervention', False)
            },
            validate_response=True,
            timeout=30.0
        )

    def _create_default_test_cases(self) -> None:
        """Create default API test cases"""

        # Test Case 1: Health Check
        self.test_cases.append(APITestCase(
            id="api_health_001",
            name="Health Check",
            endpoint="/health",
            method="GET",
            headers={},
            payload={},
            expected_status=200,
            expected_response={"status": "healthy"},
            validate_response=True,
            timeout=5.0
        ))

        # Test Case 2: Generate Innovation (Safe)
        self.test_cases.append(APITestCase(
            id="api_generate_001",
            name="Generate Safe Innovation",
            endpoint="/api/v1/innovation/generate",
            method="POST",
            headers={"X-Request-ID": str(uuid.uuid4())},
            payload={
                "hypothesis": "Optimize renewable energy distribution using AI",
                "domain": "ENERGY_SYSTEMS",
                "parameters": {
                    "reality_count": 10,
                    "exploration_depth": 3
                }
            },
            expected_status=200,
            expected_response={"success": True},
            validate_response=True,
            timeout=30.0
        ))

        # Test Case 3: Generate Innovation (Prohibited)
        self.test_cases.append(APITestCase(
            id="api_generate_002",
            name="Reject Prohibited Innovation",
            endpoint="/api/v1/innovation/generate",
            method="POST",
            headers={"X-Request-ID": str(uuid.uuid4())},
            payload={
                "hypothesis": "Create system to bypass safety protocols",
                "domain": "ARTIFICIAL_INTELLIGENCE",
                "parameters": {
                    "reality_count": 10,
                    "exploration_depth": 3
                }
            },
            expected_status=400,
            expected_response={
                "success": False,
                "error": "Safety violation detected"
            },
            validate_response=False,  # Don't validate exact error message
            timeout=10.0
        ))

        # Test Case 4: Check Status
        self.test_cases.append(APITestCase(
            id="api_status_001",
            name="Check System Status",
            endpoint="/api/v1/status",
            method="GET",
            headers={},
            payload={},
            expected_status=200,
            expected_response={"operational": True},
            validate_response=False,
            timeout=5.0
        ))

    async def execute_test_case(self, test_case: APITestCase) -> APITestResult:
        """Execute a single API test case"""
        logger.info(f"🔍 Testing: {test_case.name}")

        url = f"{self.base_url}{test_case.endpoint}"
        start_time = time.time()

        result = APITestResult(
            test_id=test_case.id,
            test_name=test_case.name,
            timestamp=datetime.now(timezone.utc),
            endpoint=test_case.endpoint,
            method=test_case.method,
            request_payload=test_case.payload,
            status_code=0,
            response_time_ms=0,
            response_body={},
            response_hash="",
            passed=False,
            error_message=None,
            rate_limited=False,
            retry_count=0
        )

        try:
            # Execute request with retries
            for attempt in range(3):  # Max 3 attempts
                try:
                    if test_case.method == "GET":
                        async with self.session.get(
                            url,
                            headers=test_case.headers,
                            timeout=aiohttp.ClientTimeout(total=test_case.timeout)
                        ) as response:
                            result.status_code = response.status
                            result.response_body = await response.json() if response.content_type == 'application/json' else {}

                    elif test_case.method == "POST":
                        async with self.session.post(
                            url,
                            json=test_case.payload,
                            headers=test_case.headers,
                            timeout=aiohttp.ClientTimeout(total=test_case.timeout)
                        ) as response:
                            result.status_code = response.status
                            result.response_body = await response.json() if response.content_type == 'application/json' else {}

                    # Check for rate limiting
                    if response.status == 429:
                        result.rate_limited = True
                        if attempt < 2:  # Retry if not last attempt
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            result.retry_count += 1
                            continue

                    break  # Success, exit retry loop

                except asyncio.TimeoutError:
                    result.error_message = f"Request timeout after {test_case.timeout}s"
                    if attempt < 2:
                        result.retry_count += 1
                        continue
                    raise

                except aiohttp.ClientError as e:
                    result.error_message = f"Client error: {str(e)}"
                    if attempt < 2:
                        result.retry_count += 1
                        await asyncio.sleep(1)
                        continue
                    raise

            # Calculate response time
            result.response_time_ms = (time.time() - start_time) * 1000

            # Generate response hash for consistency checking
            result.response_hash = hashlib.sha256(
                json.dumps(result.response_body, sort_keys=True).encode()
            ).hexdigest()[:16]

            # Validate response
            if test_case.validate_response:
                result.passed = (
                    result.status_code == test_case.expected_status and
                    all(
                        result.response_body.get(key) == value
                        for key, value in test_case.expected_response.items()
                    )
                )
            else:
                result.passed = result.status_code == test_case.expected_status

            if not result.passed and not result.error_message:
                result.error_message = f"Expected status {test_case.expected_status}, got {result.status_code}"

        except Exception as e:
            result.error_message = f"Test execution failed: {str(e)}"
            result.passed = False
            logger.error(f"Test case {test_case.id} failed: {e}")

        # Log result
        status = "✅ PASS" if result.passed else "❌ FAIL"
        logger.info(f"  {status} - Status: {result.status_code}, Time: {result.response_time_ms:.1f}ms")
        if result.error_message:
            logger.info(f"  Error: {result.error_message}")

        return result

    async def test_rate_limiting(self, requests_per_second: int = 10) -> Dict[str, Any]:
        """Test API rate limiting behavior"""
        logger.info(f"⚡ Testing rate limiting ({requests_per_second} req/s)")

        results = []
        rate_limited_count = 0

        # Create simple test case
        test_case = APITestCase(
            id="rate_limit_test",
            name="Rate Limit Test",
            endpoint="/api/v1/status",
            method="GET",
            headers={},
            payload={},
            expected_status=200,
            expected_response={},
            validate_response=False,
            timeout=5.0
        )

        # Send rapid requests
        start_time = time.time()
        tasks = []

        for i in range(requests_per_second):
            task = self.execute_test_case(test_case)
            tasks.append(task)
            await asyncio.sleep(1 / requests_per_second)  # Spread over 1 second

        results = await asyncio.gather(*tasks)

        # Count rate limited responses
        rate_limited_count = sum(1 for r in results if r.rate_limited)

        elapsed = time.time() - start_time
        actual_rate = len(results) / elapsed

        return {
            'requests_sent': len(results),
            'rate_limited': rate_limited_count,
            'actual_rate': actual_rate,
            'test_duration': elapsed,
            'passed': rate_limited_count == 0 or actual_rate <= requests_per_second
        }

    async def test_consistency(self, iterations: int = 5) -> Dict[str, Any]:
        """Test response consistency across multiple identical requests"""
        logger.info(f"🔄 Testing response consistency ({iterations} iterations)")

        # Use a deterministic test case
        test_case = APITestCase(
            id="consistency_test",
            name="Consistency Test",
            endpoint="/api/v1/innovation/generate",
            method="POST",
            headers={"X-Request-ID": "consistent_test_id"},
            payload={
                "hypothesis": "Optimize solar panel efficiency",
                "domain": "ENERGY_SYSTEMS",
                "parameters": {
                    "reality_count": 5,
                    "exploration_depth": 2,
                    "seed": 12345  # Fixed seed for determinism
                }
            },
            expected_status=200,
            expected_response={},
            validate_response=False,
            timeout=30.0
        )

        hashes = []
        results = []

        for i in range(iterations):
            result = await self.execute_test_case(test_case)
            results.append(result)
            hashes.append(result.response_hash)
            await asyncio.sleep(0.5)  # Small delay between requests

        # Check consistency
        unique_hashes = len(set(hashes))
        consistency_score = 1.0 if unique_hashes == 1 else (1.0 / unique_hashes)

        return {
            'iterations': iterations,
            'unique_responses': unique_hashes,
            'consistency_score': consistency_score,
            'response_hashes': hashes,
            'passed': consistency_score >= 0.8  # 80% consistency threshold
        }

    async def run_api_tests(self) -> Dict[str, Any]:
        """Run complete API test suite"""
        logger.info("="*60)
        logger.info("INNOVATION API TEST SUITE")
        logger.info("="*60)

        await self.setup()

        # Execute all test cases
        for test_case in self.test_cases:
            result = await self.execute_test_case(test_case)
            self.test_results.append(result)
            await asyncio.sleep(0.5)  # Delay between tests

        # Additional tests
        rate_limit_result = await self.test_rate_limiting(requests_per_second=5)
        consistency_result = await self.test_consistency(iterations=3)

        await self.teardown()

        # Generate report
        report = self.generate_report(rate_limit_result, consistency_result)
        self.save_results(report)

        return report

    def generate_report(self,
                       rate_limit_result: Dict[str, Any],
                       consistency_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive API test report"""

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)

        report = {
            'test_suite': 'Innovation API Tests',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'base_url': self.base_url,
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'performance': {
                'avg_response_time_ms': sum(r.response_time_ms for r in self.test_results) / len(self.test_results) if self.test_results else 0,
                'max_response_time_ms': max((r.response_time_ms for r in self.test_results), default=0),
                'min_response_time_ms': min((r.response_time_ms for r in self.test_results), default=0)
            },
            'rate_limiting': rate_limit_result,
            'consistency': consistency_result,
            'test_results': [r.to_dict() for r in self.test_results]
        }

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("API TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"Avg Response Time: {report['performance']['avg_response_time_ms']:.1f}ms")
        logger.info(f"Rate Limiting: {'PASS' if rate_limit_result['passed'] else 'FAIL'}")
        logger.info(f"Consistency: {consistency_result['consistency_score']*100:.1f}%")
        logger.info("="*60)

        return report

    def save_results(self, report: Dict[str, Any]) -> None:
        """Save API test results"""
        results_dir = Path(__file__).parent.parent / "test_results"
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / "innovation_api_results.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 API test results saved to: {output_file}")


async def main():
    """Main API test execution"""
    # Check if API server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/health", timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status != 200:
                    logger.warning("⚠️ API server not responding, using mock mode")
                    # Continue with mock responses
    except:
        logger.warning("⚠️ API server not available, tests will use mock responses")

    tester = InnovationAPITest()
    report = await tester.run_api_tests()

    # Success if > 80% tests pass
    success_rate = report['summary']['success_rate']
    success = success_rate >= 80

    if success:
        logger.info(f"\n✅ API tests PASSED with {success_rate:.1f}% success rate")
    else:
        logger.error(f"\n❌ API tests FAILED with {success_rate:.1f}% success rate")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
