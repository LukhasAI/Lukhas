#!/usr/bin/env python3
"""
LUKHAS AI API Performance Benchmark Suite
=========================================

Comprehensive API performance testing to validate claimed throughput rates.
Tests HTTP/REST, WebSocket, and GraphQL performance under various loads.
"""

import asyncio
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import aiohttp


class APIPerformanceBenchmark:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "test_start": time.time(),
            "test_scenarios": [],
            "performance_metrics": {},
        }

    async def test_rest_api_throughput(
        self, concurrent_requests: int = 100, total_requests: int = 10000
    ):
        """Test REST API throughput performance"""
        print(
            f"🌐 Testing REST API Throughput - {concurrent_requests} concurrent, {total_requests} total"
        )

        start_time = time.time()
        response_times = []
        successful_requests = 0

        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(concurrent_requests)

            async def make_request():
                nonlocal successful_requests
                async with semaphore:
                    request_start = time.time()
                    try:
                        async with session.get(
                            f"{self.base_url}/api/health"
                        ) as response:
                            if response.status == 200:
                                successful_requests += 1
                            request_time = (time.time() - request_start) * 1000
                            response_times.append(request_time)
                    except Exception as e:
                        print(f"Request failed: {e}")

            # Execute all requests
            tasks = [make_request() for _ in range(total_requests)]
            await asyncio.gather(*tasks)

        total_time = time.time() - start_time
        throughput = successful_requests / total_time

        result = {
            "test": "rest_api_throughput",
            "concurrent_requests": concurrent_requests,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "total_time_seconds": total_time,
            "throughput_req_per_sec": throughput,
            "avg_response_time_ms": (
                statistics.mean(response_times) if response_times else 0
            ),
            "median_response_time_ms": (
                statistics.median(response_times) if response_times else 0
            ),
            "p95_response_time_ms": (
                sorted(response_times)[int(len(response_times) * 0.95)]
                if response_times
                else 0
            ),
            "success_rate": (successful_requests / total_requests) * 100,
        }

        self.results["test_scenarios"].append(result)

        print(f"   ✅ Throughput: {throughput:.0f} req/s")
        print(f'   📊 Success Rate: {result["success_rate"]:.1f}%')
        print(f'   ⚡ Avg Response: {result["avg_response_time_ms"]:.1f}ms')

        return throughput >= 800  # Target: 842 req/s claimed

    async def test_websocket_performance(
        self, concurrent_connections: int = 50, messages_per_connection: int = 1000
    ):
        """Test WebSocket real-time performance"""
        print(
            f"🔄 Testing WebSocket Performance - {concurrent_connections} connections, {messages_per_connection} msgs each"
        )

        start_time = time.time()
        total_messages = 0

        async def websocket_client():
            nonlocal total_messages
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect("ws://localhost:8001/ws") as ws:
                        for i in range(messages_per_connection):
                            await ws.send_str(
                                json.dumps({"id": i, "data": "test_message"})
                            )
                            response = await ws.receive()
                            if response.type == aiohttp.WSMsgType.TEXT:
                                total_messages += 1
            except Exception as e:
                print(f"WebSocket error: {e}")

        # Run concurrent WebSocket connections
        tasks = [websocket_client() for _ in range(concurrent_connections)]
        await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time
        throughput = total_messages / total_time

        result = {
            "test": "websocket_performance",
            "concurrent_connections": concurrent_connections,
            "messages_per_connection": messages_per_connection,
            "total_messages_sent": concurrent_connections * messages_per_connection,
            "total_messages_received": total_messages,
            "total_time_seconds": total_time,
            "throughput_msg_per_sec": throughput,
            "message_success_rate": (
                total_messages / (concurrent_connections * messages_per_connection)
            )
            * 100,
        }

        self.results["test_scenarios"].append(result)

        print(f"   ✅ Throughput: {throughput:.0f} msg/s")
        print(f'   📊 Success Rate: {result["message_success_rate"]:.1f}%')

        return throughput >= 5000  # Target: High-frequency messaging

    def test_concurrent_user_simulation(
        self, max_users: int = 1000, ramp_up_time: int = 60
    ):
        """Simulate real user load with gradual ramp-up"""
        print(
            f"👥 Testing Concurrent User Load - {max_users} users, {ramp_up_time}s ramp-up"
        )

        start_time = time.time()
        user_response_times = []
        successful_sessions = 0

        def simulate_user_session():
            nonlocal successful_sessions
            session_start = time.time()
            try:
                # Simulate typical user workflow
                import requests

                # Login simulation
                response = requests.get(f"{self.base_url}/api/auth/check", timeout=10)
                if response.status_code == 200:
                    # API calls simulation
                    for _ in range(5):  # 5 API calls per user session
                        requests.get(f"{self.base_url}/api/data", timeout=5)
                        time.sleep(0.1)  # Small delay between calls

                    successful_sessions += 1
                    session_time = (time.time() - session_start) * 1000
                    user_response_times.append(session_time)

            except Exception as e:
                print(f"User session failed: {e}")

        # Gradual ramp-up of users
        with ThreadPoolExecutor(max_workers=max_users) as executor:
            futures = []
            for i in range(max_users):
                future = executor.submit(simulate_user_session)
                futures.append(future)
                if i < max_users - 1:
                    time.sleep(ramp_up_time / max_users)  # Gradual ramp-up

            # Wait for all user sessions to complete
            for future in futures:
                future.result()

        total_time = time.time() - start_time

        result = {
            "test": "concurrent_user_simulation",
            "max_concurrent_users": max_users,
            "ramp_up_time_seconds": ramp_up_time,
            "successful_sessions": successful_sessions,
            "total_time_seconds": total_time,
            "avg_session_time_ms": (
                statistics.mean(user_response_times) if user_response_times else 0
            ),
            "user_success_rate": (successful_sessions / max_users) * 100,
            "users_per_second": successful_sessions / total_time,
        }

        self.results["test_scenarios"].append(result)

        print(f"   ✅ Successful Sessions: {successful_sessions}/{max_users}")
        print(f'   📊 Success Rate: {result["user_success_rate"]:.1f}%')
        print(f'   ⚡ Avg Session Time: {result["avg_session_time_ms"]:.1f}ms')

        return result["user_success_rate"] >= 95  # Target: 95% success rate

    async def run_full_api_benchmark_suite(self):
        """Run complete API performance benchmark suite"""
        print("🚀 Starting LUKHAS AI API Performance Benchmark Suite...\n")

        test_results = []

        # Test 1: REST API Throughput
        try:
            result1 = await self.test_rest_api_throughput(
                concurrent_requests=100, total_requests=50000
            )
            test_results.append(result1)
        except Exception as e:
            print(f"❌ REST API test failed: {e}")
            test_results.append(False)

        # Test 2: WebSocket Performance
        try:
            result2 = await self.test_websocket_performance(
                concurrent_connections=100, messages_per_connection=500
            )
            test_results.append(result2)
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            test_results.append(False)

        # Test 3: Concurrent User Load
        try:
            result3 = self.test_concurrent_user_simulation(
                max_users=1000, ramp_up_time=30
            )
            test_results.append(result3)
        except Exception as e:
            print(f"❌ User load test failed: {e}")
            test_results.append(False)

        # Calculate overall results
        self.results["test_end"] = time.time()
        self.results["total_duration"] = (
            self.results["test_end"] - self.results["test_start"]
        )
        self.results["tests_passed"] = sum(test_results)
        self.results["total_tests"] = len(test_results)
        self.results["success_rate"] = (
            self.results["tests_passed"] / self.results["total_tests"]
        ) * 100

        # Performance metrics summary
        if self.results["test_scenarios"]:
            self.results["performance_metrics"] = {
                "peak_throughput_req_per_sec": max(
                    [
                        s.get("throughput_req_per_sec", 0)
                        for s in self.results["test_scenarios"]
                    ]
                ),
                "peak_msg_throughput": max(
                    [
                        s.get("throughput_msg_per_sec", 0)
                        for s in self.results["test_scenarios"]
                    ]
                ),
                "avg_response_time_ms": statistics.mean(
                    [
                        s.get("avg_response_time_ms", 0)
                        for s in self.results["test_scenarios"]
                        if s.get("avg_response_time_ms", 0) > 0
                    ]
                ),
                "overall_success_rate": statistics.mean(
                    [
                        s.get("success_rate", 0)
                        for s in self.results["test_scenarios"]
                        if "success_rate" in s
                    ]
                ),
            }

        print(f'\n{"="*70}')
        print("📊 LUKHAS AI API PERFORMANCE BENCHMARK RESULTS")
        print(f'{"="*70}')
        print(
            f'🎯 Tests Passed: {self.results["tests_passed"]}/{self.results["total_tests"]}'
        )
        print(f'📈 Overall Success Rate: {self.results["success_rate"]:.1f}%')
        print(f'⏱️  Total Duration: {self.results["total_duration"]:.1f} seconds')

        if "performance_metrics" in self.results:
            metrics = self.results["performance_metrics"]
            print("\n🚀 Performance Metrics:")
            print(
                f'   📊 Peak Throughput: {metrics["peak_throughput_req_per_sec"]:.0f} req/s'
            )
            print(
                f'   💬 Peak Message Rate: {metrics["peak_msg_throughput"]:.0f} msg/s'
            )
            print(f'   ⚡ Avg Response Time: {metrics["avg_response_time_ms"]:.1f}ms')
            print(f'   ✅ Overall Success: {metrics["overall_success_rate"]:.1f}%')

        # Save results
        results_file = f'/Users/agi_dev/Downloads/Consolidation-Repo/benchmarks/results/api_performance_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {results_file}")

        # Final assessment
        if self.results["success_rate"] >= 90:
            print("\n🏆 LUKHAS AI API PERFORMANCE: EXCELLENT")
            print("✅ API performance meets enterprise standards")
            print("🚀 Ready for high-load production deployment")
        elif self.results["success_rate"] >= 70:
            print("\n⭐ LUKHAS AI API PERFORMANCE: GOOD")
            print("✅ API performance acceptable for most use cases")
            print("🔧 Some optimization opportunities identified")
        else:
            print("\n⚠️  LUKHAS AI API PERFORMANCE: NEEDS IMPROVEMENT")
            print("❌ API performance below production standards")
            print("🛠️  Significant optimization required")

        return self.results["success_rate"] >= 70


async def main():
    """Run API performance benchmark suite"""
    benchmark = APIPerformanceBenchmark()
    success = await benchmark.run_full_api_benchmark_suite()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
    success = asyncio.run(main())
    exit(0 if success else 1)
