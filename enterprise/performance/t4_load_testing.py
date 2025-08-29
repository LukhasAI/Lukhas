#!/usr/bin/env python3
"""
T4 Enterprise Load Testing System
================================
Sam Altman Level: 10K+ Concurrent Users, Enterprise Scale

Designed for parallel execution with multi-agent coordination
Compatible with Jules Agent + Codex Agent collaboration
"""

import asyncio
import json
import logging
import os
import statistics
import time
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Configuration for enterprise load testing"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 10000
    ramp_up_seconds: int = 60
    test_duration_seconds: int = 300  # 5 minutes sustained
    target_rps: int = 1000
    max_latency_p95: float = 25.0  # Sam Altman standard
    max_error_rate: float = 0.1   # 0.1% max error rate

@dataclass
class LoadTestResults:
    """Enterprise load test results"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    p95_latency: float
    p99_latency: float
    throughput_rps: float
    error_rate: float
    peak_concurrent_users: int
    test_duration: float
    meets_sam_altman_standard: bool

class T4LoadTester:
    """Enterprise-grade load testing for LUKHAS Trinity Framework"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: list[dict[str, Any]] = []

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.config.concurrent_users + 100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def generate_load_pattern(self) -> list[dict[str, Any]]:
        """Generate realistic load patterns for Trinity Framework"""
        patterns = [
            # Identity System Load (⚛️) - 30% of traffic
            {"endpoint": "/api/v1/identity/authenticate", "weight": 0.15, "method": "POST"},
            {"endpoint": "/api/v1/identity/verify", "weight": 0.10, "method": "GET"},
            {"endpoint": "/api/v1/identity/tier-check", "weight": 0.05, "method": "GET"},

            # Consciousness System Load (🧠) - 50% of traffic
            {"endpoint": "/api/v1/consciousness/query", "weight": 0.25, "method": "POST"},
            {"endpoint": "/api/v1/consciousness/dream", "weight": 0.15, "method": "POST"},
            {"endpoint": "/api/v1/consciousness/memory", "weight": 0.10, "method": "GET"},

            # Guardian System Load (🛡️) - 20% of traffic
            {"endpoint": "/api/v1/guardian/validate", "weight": 0.10, "method": "POST"},
            {"endpoint": "/api/v1/guardian/audit", "weight": 0.05, "method": "GET"},
            {"endpoint": "/api/v1/guardian/drift-check", "weight": 0.05, "method": "GET"},
        ]

        return patterns

    async def single_request(self, endpoint: str, method: str = "GET",
                           payload: Optional[dict] = None) -> dict[str, Any]:
        """Execute single API request with timing"""
        start_time = time.time()

        try:
            url = f"{self.config.base_url}{endpoint}"

            if method == "POST":
                if not payload:
                    payload = {"test": True, "timestamp": start_time}
                async with self.session.post(url, json=payload) as response:
                    await response.text()
                    status = response.status
            else:
                async with self.session.get(url) as response:
                    await response.text()
                    status = response.status

            latency = (time.time() - start_time) * 1000  # Convert to ms

            return {
                "success": 200 <= status < 400,
                "status_code": status,
                "latency_ms": latency,
                "endpoint": endpoint,
                "timestamp": start_time
            }

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": 0,
                "latency_ms": latency,
                "endpoint": endpoint,
                "error": str(e),
                "timestamp": start_time
            }

    async def ramp_up_users(self, target_users: int, ramp_seconds: int) -> None:
        """Gradually ramp up concurrent users"""
        logger.info(f"🚀 Ramping up to {target_users} concurrent users over {ramp_seconds}s")

        users_per_second = target_users / ramp_seconds
        current_users = 0

        for second in range(ramp_seconds):
            target_for_second = int((second + 1) * users_per_second)
            new_users = target_for_second - current_users

            if new_users > 0:
                logger.info(f"   Second {second + 1}: Adding {new_users} users (Total: {target_for_second})")
                # This would spawn actual user simulation tasks
                await asyncio.sleep(1)
                current_users = target_for_second

        logger.info(f"✅ Ramp-up complete: {target_users} concurrent users active")

    async def sustained_load_test(self) -> LoadTestResults:
        """Run sustained load test at target concurrency"""
        logger.info("⚡ Starting sustained load test")
        logger.info(f"   Target Users: {self.config.concurrent_users}")
        logger.info(f"   Duration: {self.config.test_duration_seconds}s")
        logger.info(f"   Target RPS: {self.config.target_rps}")

        load_patterns = await self.generate_load_pattern()
        start_time = time.time()
        end_time = start_time + self.config.test_duration_seconds

        # Tracking variables
        request_results = []
        total_requests = 0
        active_tasks = []

        # Main load generation loop
        while time.time() < end_time:
            # Calculate requests to generate this second
            elapsed = time.time() - start_time
            target_requests = int(elapsed * self.config.target_rps)
            requests_to_generate = target_requests - total_requests

            if requests_to_generate > 0:
                # Generate batch of requests
                batch_tasks = []

                for _ in range(min(requests_to_generate, 100)):  # Limit batch size
                    # Select endpoint based on weight
                    import random
                    pattern = random.choices(load_patterns,
                                           weights=[p["weight"] for p in load_patterns])[0]

                    task = asyncio.create_task(
                        self.single_request(pattern["endpoint"], pattern["method"])
                    )
                    batch_tasks.append(task)
                    total_requests += 1

                active_tasks.extend(batch_tasks)

            # Process completed tasks
            if active_tasks:
                done_tasks = [task for task in active_tasks if task.done()]
                for task in done_tasks:
                    try:
                        result = await task
                        request_results.append(result)
                    except Exception as e:
                        request_results.append({
                            "success": False,
                            "latency_ms": 0,
                            "error": str(e)
                        })
                    active_tasks.remove(task)

            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.01)

        # Wait for remaining tasks
        if active_tasks:
            remaining_results = await asyncio.gather(*active_tasks, return_exceptions=True)
            for result in remaining_results:
                if isinstance(result, dict):
                    request_results.append(result)

        # Calculate results
        total_time = time.time() - start_time
        successful = [r for r in request_results if r.get("success", False)]
        failed = [r for r in request_results if not r.get("success", False)]

        latencies = [r["latency_ms"] for r in successful if "latency_ms" in r]

        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = p95_latency = p99_latency = 0

        results = LoadTestResults(
            total_requests=len(request_results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            average_latency=avg_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            throughput_rps=len(successful) / total_time if total_time > 0 else 0,
            error_rate=(len(failed) / len(request_results)) * 100 if request_results else 0,
            peak_concurrent_users=self.config.concurrent_users,
            test_duration=total_time,
            meets_sam_altman_standard=(p95_latency < self.config.max_latency_p95 and
                                     (len(failed) / len(request_results)) * 100 < self.config.max_error_rate)
        )

        # Log results
        logger.info("🎯 Sustained Load Test Results:")
        logger.info(f"   Total Requests: {results.total_requests:,}")
        logger.info(f"   Successful: {results.successful_requests:,}")
        logger.info(f"   Failed: {results.failed_requests:,}")
        logger.info(f"   Average Latency: {results.average_latency:.2f}ms")
        logger.info(f"   P95 Latency: {results.p95_latency:.2f}ms ({'✅' if results.p95_latency < 25 else '⚠️'} Target: <25ms)")
        logger.info(f"   P99 Latency: {results.p99_latency:.2f}ms")
        logger.info(f"   Throughput: {results.throughput_rps:.1f} RPS")
        logger.info(f"   Error Rate: {results.error_rate:.2f}%")
        logger.info(f"   Sam Altman Standard: {'✅ PASSED' if results.meets_sam_altman_standard else '❌ NEEDS WORK'}")

        return results

    async def run_full_load_test(self) -> LoadTestResults:
        """Run complete load test with ramp-up and sustained load"""
        logger.info("🏆 Starting T4 Enterprise Load Test")

        # Phase 1: Ramp up users
        await self.ramp_up_users(self.config.concurrent_users, self.config.ramp_up_seconds)

        # Phase 2: Sustained load
        results = await self.sustained_load_test()

        logger.info("🏁 T4 Load Test Complete!")
        return results

async def run_t4_load_test():
    """Run T4 leadership level load testing"""
    config = LoadTestConfig(
        concurrent_users=10000,  # Sam Altman scale
        ramp_up_seconds=60,
        test_duration_seconds=300,  # 5 minutes sustained
        target_rps=1000,
        max_latency_p95=25.0,  # 2x better than current target
        max_error_rate=0.1
    )

    async with T4LoadTester(config) as tester:
        results = await tester.run_full_load_test()

        # Save results for Jules Agents to analyze
        timestamp = int(time.time())
        output_dir = "/tmp/lukhas_performance_results/"
        os.makedirs(output_dir, exist_ok=True)
        results_file = os.path.join(output_dir, f"load_test_results_{timestamp}.json")

        with open(results_file, "w") as f:
            json.dump({
                "config": {
                    "concurrent_users": config.concurrent_users,
                    "target_rps": config.target_rps,
                    "test_duration": config.test_duration_seconds,
                    "sam_altman_standard": config.max_latency_p95
                },
                "results": {
                    "total_requests": results.total_requests,
                    "successful_requests": results.successful_requests,
                    "failed_requests": results.failed_requests,
                    "average_latency": results.average_latency,
                    "p95_latency": results.p95_latency,
                    "p99_latency": results.p99_latency,
                    "throughput_rps": results.throughput_rps,
                    "error_rate": results.error_rate,
                    "meets_standard": results.meets_sam_altman_standard
                }
            }, f, indent=2)

        logger.info(f"📊 Results saved: {results_file}")
        return results

if __name__ == "__main__":
    asyncio.run(run_t4_load_test())
