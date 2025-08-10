#!/usr/bin/env python3

"""
██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

@lukhas/HEADER_FOOTER_TEMPLATE.py

**MODULE TITLE: API Systems Comprehensive Benchmark**

============================

**DESCRIPTION**

REAL TESTS ONLY - Connects to actual LUKHAS API systems.
NO MOCK IMPLEMENTATIONS - Tests real response times, real failures, real throughput.

Tests: FastAPI endpoints, authentication, memory API, colony API, real load testing

VERSION: 1.0.0
CREATED: 2025-07-31
AUTHORS: LUKHAS Benchmark Team

Copyright (c) 2025 LUKHAS AI. All rights reserved.
Licensed under the LUKHAS Enterprise License.

For documentation and support: https://lukhas.ai/docs
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealAPISystemBenchmark:
    """REAL API system benchmark - NO MOCKS ALLOWED"""

    def __init__(self):
        self.results = {
            "benchmark_id": f"REAL_api_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "system": "api_systems",
            "test_type": "REAL_ONLY",
            "mock_mode": False,  # NEVER TRUE
            "tests": {},
            "summary": {},
            "import_status": {},
        }

        # ATTEMPT REAL IMPORTS - NO FALLBACKS TO MOCKS
        self.memory_api = None
        self.colony_api = None
        self.fastapi_app = None
        self.memory_system = None

        self._initialize_real_systems()

    def _initialize_real_systems(self):
        """Initialize REAL API systems - fail if not available"""
        print("🌐 Attempting to connect to REAL LUKHAS API systems...")

        # Try to import real FastAPI memory endpoints
        try:
            from api.memory import memory_system
            from api.memory import router as memory_router

            self.memory_api = memory_router
            self.memory_system = memory_system
            self.results["import_status"]["memory_api"] = "SUCCESS"
            print("  ✅ Memory API router loaded successfully")
        except Exception as e:
            self.results["import_status"]["memory_api"] = f"FAILED: {str(e)}"
            print(f"  ❌ Memory API failed: {e}")

        # Try to import real colony endpoints
        try:
            from api.colony_endpoints import router as colony_router

            self.colony_api = colony_router
            self.results["import_status"]["colony_api"] = "SUCCESS"
            print("  ✅ Colony API router loaded successfully")
        except Exception as e:
            self.results["import_status"]["colony_api"] = f"FAILED: {str(e)}"
            print(f"  ❌ Colony API failed: {e}")

        # Try to import core swarm system for colony operations
        try:
            from core.swarm import SwarmHub

            self.swarm_hub = SwarmHub()
            self.results["import_status"]["swarm_hub"] = "SUCCESS"
            print("  ✅ SwarmHub loaded successfully")
        except Exception as e:
            self.results["import_status"]["swarm_hub"] = f"FAILED: {str(e)}"
            print(f"  ❌ SwarmHub failed: {e}")

        # Try to create FastAPI test app
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            self.fastapi_app = FastAPI()
            if self.memory_api:
                self.fastapi_app.include_router(self.memory_api)
            if self.colony_api:
                self.fastapi_app.include_router(self.colony_api)

            self.test_client = TestClient(self.fastapi_app)
            self.results["import_status"]["fastapi_app"] = "SUCCESS"
            print("  ✅ FastAPI test application created successfully")
        except Exception as e:
            self.results["import_status"]["fastapi_app"] = f"FAILED: {str(e)}"
            print(f"  ❌ FastAPI test app failed: {e}")

        # Count successful imports
        successful_imports = sum(
            1
            for status in self.results["import_status"].values()
            if status == "SUCCESS"
        )
        total_imports = len(self.results["import_status"])

        print(
            f"📊 Real system status: {successful_imports}/{total_imports} API components loaded"
        )

        if successful_imports == 0:
            print("🚨 CRITICAL: NO REAL API SYSTEMS AVAILABLE")
            return False

        return True

    async def test_real_memory_api_performance(self) -> Dict[str, Any]:
        """Test REAL memory API endpoint performance"""
        print("🧠 Testing REAL Memory API Performance...")

        if not self.memory_api or not self.test_client:
            return {
                "error": "NO_REAL_MEMORY_API_AVAILABLE",
                "message": "Cannot test memory API - no real memory system loaded",
                "real_test": False,
            }

        memory_api_tests = [
            {
                "endpoint": "/memory/health",
                "method": "GET",
                "expected_status": 200,
                "test_name": "health_check",
            },
            {
                "endpoint": "/memory/statistics",
                "method": "GET",
                "expected_status": 200,
                "test_name": "statistics",
            },
            {
                "endpoint": "/memory/create",
                "method": "POST",
                "data": {
                    "emotion": "curiosity",
                    "context_snippet": "Testing real memory API performance benchmark",
                    "user_id": "benchmark_test_user",
                    "metadata": {
                        "test": True,
                        "benchmark_id": self.results["benchmark_id"],
                    },
                },
                "expected_status": 200,
                "test_name": "create_memory",
            },
            {
                "endpoint": "/memory/recall",
                "method": "POST",
                "data": {"user_id": "benchmark_test_user", "user_tier": 5, "limit": 10},
                "expected_status": 200,
                "test_name": "recall_memories",
            },
            {
                "endpoint": "/memory/enhanced-recall",
                "method": "POST",
                "data": {
                    "user_id": "benchmark_test_user",
                    "target_emotion": "curiosity",
                    "user_tier": 5,
                    "emotion_threshold": 0.3,
                    "max_results": 5,
                },
                "expected_status": 200,
                "test_name": "enhanced_recall",
            },
        ]

        results = {
            "real_test": True,
            "total_tests": len(memory_api_tests),
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "endpoint_results": {},
            "real_api_errors": [],
        }

        for test in memory_api_tests:
            endpoint = test["endpoint"]
            method = test["method"]
            data = test.get("data")
            expected_status = test["expected_status"]
            test_name = test["test_name"]

            print(f"  🧪 Testing {test_name}: {method} {endpoint}")

            start_time = time.time()

            try:
                # Call REAL FastAPI endpoint
                if method == "GET":
                    response = self.test_client.get(endpoint)
                elif method == "POST":
                    response = self.test_client.post(endpoint, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                results["response_times"].append(response_time)

                # Check response
                status_code = response.status_code
                success = status_code == expected_status

                if success:
                    results["successful_requests"] += 1
                    # Try to parse JSON response
                    try:
                        response_data = response.json()
                        data_status = response_data.get("status", "unknown")
                    except:
                        response_data = {"raw": response.text}
                        data_status = "non_json"

                    results["endpoint_results"][test_name] = {
                        "status_code": status_code,
                        "response_time_ms": response_time,
                        "success": True,
                        "data_status": data_status,
                        "response_size": len(response.text),
                    }

                    print(
                        f"    ✅ Success: {status_code} status, {response_time:.1f}ms, {data_status}"
                    )
                else:
                    results["failed_requests"] += 1
                    error_msg = f"Expected {expected_status}, got {status_code}"
                    results["real_api_errors"].append(f"{test_name}: {error_msg}")

                    results["endpoint_results"][test_name] = {
                        "status_code": status_code,
                        "response_time_ms": response_time,
                        "success": False,
                        "error": error_msg,
                        "response_text": response.text[:200],  # First 200 chars
                    }

                    print(f"    ❌ Failed: {error_msg}, {response_time:.1f}ms")

            except Exception as e:
                results["failed_requests"] += 1
                results["real_api_errors"].append(f"{test_name}: Exception - {str(e)}")
                print(f"    ❌ Exception: {str(e)}")

        # Calculate REAL metrics
        results["success_rate"] = (
            results["successful_requests"] / results["total_tests"]
        )
        if results["response_times"]:
            results["average_response_time_ms"] = sum(results["response_times"]) / len(
                results["response_times"]
            )
            results["min_response_time_ms"] = min(results["response_times"])
            results["max_response_time_ms"] = max(results["response_times"])
            results["p95_response_time_ms"] = sorted(results["response_times"])[
                int(0.95 * len(results["response_times"]))
            ]

        print(
            f"📊 REAL Memory API: {results['success_rate']:.1%} success, {results.get('average_response_time_ms', 0):.1f}ms avg"
        )

        return results

    async def test_real_colony_api_performance(self) -> Dict[str, Any]:
        """Test REAL colony API endpoint performance"""
        print("🏭 Testing REAL Colony API Performance...")

        if not self.colony_api or not self.test_client:
            return {
                "error": "NO_REAL_COLONY_API_AVAILABLE",
                "message": "Cannot test colony API - no real colony system loaded",
                "real_test": False,
            }

        colony_api_tests = [
            {
                "endpoint": "/colonies/spawn",
                "method": "POST",
                "data": {
                    "colony_type": "reasoning",
                    "size": 5,
                    "capabilities": ["logic", "inference"],
                    "config": {"timeout": 30.0},
                },
                "expected_status": 200,
                "test_name": "spawn_colony",
            }
        ]

        results = {
            "real_test": True,
            "total_tests": len(colony_api_tests),
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "colony_operations": {},
            "real_colony_errors": [],
            "spawned_colonies": [],
        }

        for test in colony_api_tests:
            endpoint = test["endpoint"]
            method = test["method"]
            data = test.get("data")
            expected_status = test["expected_status"]
            test_name = test["test_name"]

            print(f"  🧪 Testing {test_name}: {method} {endpoint}")

            start_time = time.time()

            try:
                # Call REAL colony API endpoint
                if method == "POST":
                    response = self.test_client.post(endpoint, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                results["response_times"].append(response_time)

                # Check response
                status_code = response.status_code
                success = status_code == expected_status

                if success:
                    results["successful_requests"] += 1
                    # Try to parse colony response
                    try:
                        response_data = response.json()
                        colony_id = response_data.get("colony_id")
                        if colony_id:
                            results["spawned_colonies"].append(colony_id)
                    except:
                        response_data = {"raw": response.text}

                    results["colony_operations"][test_name] = {
                        "status_code": status_code,
                        "response_time_ms": response_time,
                        "success": True,
                        "colony_spawned": (
                            colony_id is not None if "colony_id" in locals() else False
                        ),
                    }

                    print(
                        f"    ✅ Success: {status_code} status, {response_time:.1f}ms"
                    )
                else:
                    results["failed_requests"] += 1
                    error_msg = f"Expected {expected_status}, got {status_code}"
                    results["real_colony_errors"].append(f"{test_name}: {error_msg}")

                    results["colony_operations"][test_name] = {
                        "status_code": status_code,
                        "response_time_ms": response_time,
                        "success": False,
                        "error": error_msg,
                        "response_text": response.text[:200],
                    }

                    print(f"    ❌ Failed: {error_msg}, {response_time:.1f}ms")

            except Exception as e:
                results["failed_requests"] += 1
                results["real_colony_errors"].append(
                    f"{test_name}: Exception - {str(e)}"
                )
                print(f"    ❌ Exception: {str(e)}")

        # Test colony termination if we spawned any
        for colony_id in results["spawned_colonies"]:
            print(f"  🧪 Testing colony termination: {colony_id}")
            start_time = time.time()

            try:
                response = self.test_client.delete(f"/colonies/{colony_id}")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                if response.status_code == 200:
                    print(
                        f"    ✅ Colony {colony_id} terminated: {response_time:.1f}ms"
                    )
                else:
                    print(
                        f"    ⚠️ Colony {colony_id} termination issue: {response.status_code}"
                    )

            except Exception as e:
                print(f"    ❌ Colony {colony_id} termination failed: {e}")

        # Calculate REAL metrics
        results["success_rate"] = (
            results["successful_requests"] / results["total_tests"]
        )
        if results["response_times"]:
            results["average_response_time_ms"] = sum(results["response_times"]) / len(
                results["response_times"]
            )
            results["colonies_successfully_spawned"] = len(results["spawned_colonies"])

        print(
            f"📊 REAL Colony API: {results['success_rate']:.1%} success, {results.get('average_response_time_ms', 0):.1f}ms avg"
        )

        return results

    async def test_real_concurrent_api_load(self) -> Dict[str, Any]:
        """Test REAL API performance under concurrent load"""
        print("🔄 Testing REAL Concurrent API Load...")

        if not self.memory_api or not self.test_client:
            return {
                "error": "NO_REAL_API_AVAILABLE",
                "message": "Cannot test concurrent load - no real API systems loaded",
                "real_test": False,
            }

        load_tests = [
            {"concurrent_requests": 10, "endpoint": "/memory/health", "method": "GET"},
            {
                "concurrent_requests": 20,
                "endpoint": "/memory/statistics",
                "method": "GET",
            },
            {
                "concurrent_requests": 15,
                "endpoint": "/memory/recall",
                "method": "POST",
                "data": {"user_id": "load_test_user", "user_tier": 5, "limit": 5},
            },
        ]

        results = {
            "real_test": True,
            "total_load_tests": len(load_tests),
            "successful_load_tests": 0,
            "failed_load_tests": 0,
            "load_results": {},
            "max_successful_concurrent": 0,
            "total_requests_processed": 0,
        }

        for test in load_tests:
            concurrent_requests = test["concurrent_requests"]
            endpoint = test["endpoint"]
            method = test["method"]
            data = test.get("data")

            print(
                f"  🧪 Load testing {concurrent_requests} concurrent {method} {endpoint}..."
            )

            start_time = time.time()
            successful_requests = 0
            failed_requests = 0
            response_times = []

            async def make_request():
                """Make a single API request"""
                req_start = time.time()
                try:
                    if method == "GET":
                        response = self.test_client.get(endpoint)
                    elif method == "POST":
                        response = self.test_client.post(endpoint, json=data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    req_end = time.time()
                    req_time = (req_end - req_start) * 1000

                    if response.status_code == 200:
                        return {
                            "success": True,
                            "time": req_time,
                            "status": response.status_code,
                        }
                    else:
                        return {
                            "success": False,
                            "time": req_time,
                            "status": response.status_code,
                        }

                except Exception as e:
                    req_end = time.time()
                    req_time = (req_end - req_start) * 1000
                    return {"success": False, "time": req_time, "error": str(e)}

            # Execute concurrent requests using asyncio
            try:
                tasks = [make_request() for _ in range(concurrent_requests)]
                request_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in request_results:
                    if isinstance(result, Exception):
                        failed_requests += 1
                    elif result.get("success", False):
                        successful_requests += 1
                        response_times.append(result["time"])
                    else:
                        failed_requests += 1
                        response_times.append(result["time"])

                end_time = time.time()
                total_time = end_time - start_time

                # Calculate metrics
                success_rate = successful_requests / concurrent_requests
                throughput = concurrent_requests / total_time
                avg_response_time = (
                    sum(response_times) / len(response_times) if response_times else 0
                )

                results["load_results"][f"{concurrent_requests}_concurrent"] = {
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests,
                    "success_rate": success_rate,
                    "throughput_rps": throughput,
                    "average_response_time_ms": avg_response_time,
                    "total_time_seconds": total_time,
                }

                results["total_requests_processed"] += concurrent_requests

                # Check if load test was successful (>90% success rate)
                if success_rate >= 0.9:
                    results["successful_load_tests"] += 1
                    results["max_successful_concurrent"] = max(
                        results["max_successful_concurrent"], concurrent_requests
                    )
                    status = "✅"
                else:
                    results["failed_load_tests"] += 1
                    status = "❌"

                print(
                    f"  {status} {concurrent_requests} concurrent: {success_rate:.1%} success, {throughput:.1f} RPS, {avg_response_time:.1f}ms avg"
                )

            except Exception as e:
                results["failed_load_tests"] += 1
                results["load_results"][f"{concurrent_requests}_concurrent"] = {
                    "error": str(e),
                    "success_rate": 0,
                }
                print(
                    f"  ❌ {concurrent_requests} concurrent: Load test failed - {str(e)}"
                )

        print(
            f"📊 REAL Concurrent Load: {results['max_successful_concurrent']} max concurrent, {results['total_requests_processed']} total processed"
        )

        return results

    async def test_real_error_handling(self) -> Dict[str, Any]:
        """Test REAL API error handling and recovery"""
        print("🚨 Testing REAL API Error Handling...")

        if not self.test_client:
            return {
                "error": "NO_REAL_API_CLIENT_AVAILABLE",
                "message": "Cannot test error handling - no real API client available",
                "real_test": False,
            }

        error_tests = [
            {
                "endpoint": "/memory/nonexistent",
                "method": "GET",
                "expected_status": 404,
                "test_name": "invalid_endpoint",
            },
            {
                "endpoint": "/memory/create",
                "method": "POST",
                "data": {"invalid": "data"},  # Missing required fields
                "expected_status": 422,  # FastAPI validation error
                "test_name": "invalid_request_data",
            },
            {
                "endpoint": "/memory/recall",
                "method": "POST",
                "data": {
                    "user_id": "test",
                    "user_tier": 10,  # Invalid tier (should be 0-5)
                    "limit": 5,
                },
                "expected_status": 422,  # FastAPI validation error
                "test_name": "invalid_parameter_range",
            },
            {
                "endpoint": "/colonies/nonexistent_colony_id",
                "method": "DELETE",
                "expected_status": 404,
                "test_name": "nonexistent_colony",
            },
        ]

        results = {
            "real_test": True,
            "total_error_tests": len(error_tests),
            "correct_error_handling": 0,
            "incorrect_error_handling": 0,
            "error_test_results": {},
            "real_error_responses": [],
        }

        for test in error_tests:
            endpoint = test["endpoint"]
            method = test["method"]
            data = test.get("data")
            expected_status = test["expected_status"]
            test_name = test["test_name"]

            print(
                f"  🧪 Testing {test_name}: expecting {expected_status} from {method} {endpoint}"
            )

            start_time = time.time()

            try:
                # Call REAL API endpoint expecting error
                if method == "GET":
                    response = self.test_client.get(endpoint)
                elif method == "POST":
                    response = self.test_client.post(endpoint, json=data)
                elif method == "DELETE":
                    response = self.test_client.delete(endpoint)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                # Check if we got the expected error status
                actual_status = response.status_code
                correct_handling = actual_status == expected_status

                if correct_handling:
                    results["correct_error_handling"] += 1
                    status = "✅"
                else:
                    results["incorrect_error_handling"] += 1
                    status = "❌"

                # Try to parse error response
                try:
                    error_response = response.json()
                    error_detail = error_response.get("detail", "No detail")
                except:
                    error_detail = response.text[:100]

                results["error_test_results"][test_name] = {
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                    "correct_handling": correct_handling,
                    "response_time_ms": response_time,
                    "error_detail": error_detail,
                }

                print(
                    f"    {status} Expected {expected_status}, got {actual_status}: {error_detail[:50]}"
                )

            except Exception as e:
                results["incorrect_error_handling"] += 1
                results["real_error_responses"].append(
                    f"{test_name}: Exception - {str(e)}"
                )
                print(f"    ❌ Exception during error test: {str(e)}")

        # Calculate error handling accuracy
        results["error_handling_accuracy"] = (
            results["correct_error_handling"] / results["total_error_tests"]
        )

        print(
            f"📊 REAL Error Handling: {results['error_handling_accuracy']:.1%} accuracy, {results['correct_error_handling']}/{results['total_error_tests']} correct"
        )

        return results

    async def run_real_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run REAL comprehensive API system benchmark - NO MOCKS"""
        print("🚀 REAL API SYSTEMS COMPREHENSIVE BENCHMARK")
        print("=" * 80)
        print("⚠️  INVESTOR MODE: REAL TESTS ONLY - NO MOCK DATA")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Mock Mode: {self.results['mock_mode']} (NEVER TRUE)")
        print()

        # Check if we have any real systems
        successful_imports = sum(
            1
            for status in self.results["import_status"].values()
            if status == "SUCCESS"
        )
        if successful_imports == 0:
            error_result = {
                "error": "NO_REAL_SYSTEMS_AVAILABLE",
                "message": "Cannot run investor-grade benchmarks without real API systems",
                "import_failures": self.results["import_status"],
                "recommendation": "Fix import dependencies and deploy real API systems before investor presentation",
            }
            self.results["critical_error"] = error_result
            print("🚨 CRITICAL ERROR: No real API systems available for testing")
            return self.results

        # Run REAL tests only
        real_test_functions = [
            ("real_memory_api_performance", self.test_real_memory_api_performance),
            ("real_colony_api_performance", self.test_real_colony_api_performance),
            ("real_concurrent_api_load", self.test_real_concurrent_api_load),
            ("real_error_handling", self.test_real_error_handling),
        ]

        for test_name, test_func in real_test_functions:
            print(f"\n🧪 Running REAL {test_name.replace('_', ' ').title()}...")
            print("-" * 60)

            try:
                test_result = await test_func()
                self.results["tests"][test_name] = test_result

                if test_result.get("real_test", False):
                    print(f"✅ REAL {test_name} completed")
                else:
                    print(f"❌ {test_name} skipped - no real system available")

            except Exception as e:
                error_result = {
                    "error": str(e),
                    "real_test": False,
                    "timestamp": datetime.now().isoformat(),
                }
                self.results["tests"][test_name] = error_result
                print(f"❌ REAL {test_name} failed: {str(e)}")

        # Generate REAL summary
        self._generate_real_summary()

        # Save REAL results
        self._save_real_results()

        print("\n🎉 REAL API SYSTEMS BENCHMARK COMPLETE!")
        print("=" * 80)
        self._print_real_summary()

        return self.results

    def _generate_real_summary(self):
        """Generate summary of REAL test results"""
        tests = self.results["tests"]
        real_tests = [test for test in tests.values() if test.get("real_test", False)]

        summary = {
            "total_attempted_tests": len(tests),
            "real_tests_executed": len(real_tests),
            "mock_tests_executed": 0,  # NEVER ALLOWED
            "import_success_rate": sum(
                1
                for status in self.results["import_status"].values()
                if status == "SUCCESS"
            )
            / len(self.results["import_status"]),
            "overall_system_health": (
                "CRITICAL"
                if len(real_tests) == 0
                else "DEGRADED" if len(real_tests) < 3 else "HEALTHY"
            ),
            "investor_ready": len(real_tests) >= 2,
            "key_metrics": {},
        }

        # Extract real metrics
        for test_name, test_data in tests.items():
            if test_data.get("real_test", False):
                if "success_rate" in test_data:
                    summary["key_metrics"][f"{test_name}_success_rate"] = test_data[
                        "success_rate"
                    ]
                if "average_response_time_ms" in test_data:
                    summary["key_metrics"][f"{test_name}_latency_ms"] = test_data[
                        "average_response_time_ms"
                    ]
                if "error_handling_accuracy" in test_data:
                    summary["key_metrics"][f"{test_name}_accuracy"] = test_data[
                        "error_handling_accuracy"
                    ]
                if "max_successful_concurrent" in test_data:
                    summary["key_metrics"][f"{test_name}_max_concurrent"] = test_data[
                        "max_successful_concurrent"
                    ]

        self.results["summary"] = summary

    def _print_real_summary(self):
        """Print REAL test summary for investors"""
        summary = self.results["summary"]

        print(f"📊 System Health: {summary['overall_system_health']}")
        print(f"🏭 Import Success: {summary['import_success_rate']:.1%}")
        print(
            f"🧪 Real Tests: {summary['real_tests_executed']}/{summary['total_attempted_tests']}"
        )
        print(
            f"💼 Investor Ready: {'✅ YES' if summary['investor_ready'] else '❌ NO'}"
        )

        if summary["key_metrics"]:
            print("\n🔑 Real Performance Metrics:")
            for metric, value in summary["key_metrics"].items():
                if "success_rate" in metric or "accuracy" in metric:
                    print(f"   📈 {metric}: {value:.1%}")
                elif "latency" in metric:
                    print(f"   ⚡ {metric}: {value:.1f}ms")
                elif "concurrent" in metric:
                    print(f"   🔄 {metric}: {value}")

        if not summary["investor_ready"]:
            print("\n🚨 NOT READY FOR INVESTORS:")
            print("   - Fix import failures in API systems")
            print("   - Deploy missing FastAPI components")
            print("   - Ensure all real tests pass before presentation")

    def _save_real_results(self):
        """Save REAL benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"REAL_api_system_benchmark_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 REAL Results saved to: {filename}")


async def main():
    """Run REAL API system benchmark - NO MOCKS ALLOWED"""
    print("⚠️  STARTING REAL API BENCHMARK - Mock tests prohibited for investors")

    benchmark = RealAPISystemBenchmark()
    results = await benchmark.run_real_comprehensive_benchmark()

    return results


if __name__ == "__main__":
    asyncio.run(main())
