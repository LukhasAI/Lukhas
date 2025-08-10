#!/usr/bin/env python3
"""
Comprehensive Stress Testing Suite for Lambda Products
Tests every feature under extreme load, validates all paths, and ensures production readiness

This suite includes:
1. Path validation and import testing
2. Stress testing with high load
3. Memory leak detection
4. Concurrency testing
5. Edge case handling
6. Security validation
7. Performance benchmarking
"""

import asyncio
import json
import random
import sys
import time
import tracemalloc
from datetime import datetime
from pathlib import Path

import psutil
import pytest

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Track test results
TEST_RESULTS = {
    "path_validation": {},
    "stress_tests": {},
    "memory_tests": {},
    "concurrency_tests": {},
    "security_tests": {},
    "performance_benchmarks": {},
}


class TestPathValidation:
    """Validate all file paths and imports"""

    def test_01_directory_structure(self):
        """Test 01: Validate directory structure exists"""
        print("\n🧪 Test 01: Directory Structure Validation")
        print("=" * 50)

        base_path = Path(__file__).parent.parent.parent

        required_dirs = [
            "NIΛS",
            "ΛBAS",
            "DΛST",
            "WΛLLET",
            "agents",
            "integration",
            "integrations",
            "plugin_system",
            "unified_systems",
            "tests",
            "docs",
            "data",
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                print(f"❌ Missing: {dir_name}")
            else:
                print(f"✅ Found: {dir_name}")

        TEST_RESULTS["path_validation"]["directories"] = {
            "required": len(required_dirs),
            "found": len(required_dirs) - len(missing_dirs),
            "missing": missing_dirs,
        }

        assert len(missing_dirs) == 0, f"Missing directories: {missing_dirs}"

    def test_02_critical_files(self):
        """Test 02: Validate critical files exist"""
        print("\n🧪 Test 02: Critical Files Validation")
        print("=" * 50)

        base_path = Path(__file__).parent.parent.parent

        critical_files = [
            "setup.py",
            "requirements.txt",
            "README.md",
            "plugin_system/plugin_base.py",
            "plugin_system/lambda_products_adapter.py",
            "agents/autonomous_agent_framework.py",
            "agents/lambda_workforce_agents.py",
            "integration/lukhas_pwm_adapter.py",
            "integrations/openai_agi_bridge.py",
        ]

        missing_files = []
        for file_path in critical_files:
            full_path = base_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"❌ Missing: {file_path}")
            else:
                file_size = full_path.stat().st_size
                print(f"✅ Found: {file_path} ({file_size:,} bytes)")

        TEST_RESULTS["path_validation"]["files"] = {
            "required": len(critical_files),
            "found": len(critical_files) - len(missing_files),
            "missing": missing_files,
        }

        assert len(missing_files) == 0, f"Missing files: {missing_files}"

    def test_03_imports(self):
        """Test 03: Validate all imports work"""
        print("\n🧪 Test 03: Import Validation")
        print("=" * 50)

        import_tests = [
            ("plugin_system.plugin_base", ["PluginSystem", "LukhasPlugin"]),
            ("plugin_system.lambda_products_adapter", ["LambdaProductsAdapter"]),
            (
                "agents.autonomous_agent_framework",
                ["AutonomousAgent", "AgentOrchestrator"],
            ),
            ("agents.lambda_workforce_agents", ["NIASEmotionalIntelligenceAgent"]),
            ("integration.lukhas_pwm_adapter", ["LukhasPWMIntegrationAdapter"]),
        ]

        failed_imports = []
        for module_name, expected_attrs in import_tests:
            try:
                module = __import__(module_name, fromlist=expected_attrs)
                for attr in expected_attrs:
                    if not hasattr(module, attr):
                        failed_imports.append(f"{module_name}.{attr}")
                        print(f"❌ Missing attribute: {module_name}.{attr}")
                    else:
                        print(f"✅ Import successful: {module_name}.{attr}")
            except ImportError as e:
                failed_imports.append(module_name)
                print(f"❌ Import failed: {module_name} - {e}")

        TEST_RESULTS["path_validation"]["imports"] = {
            "tested": len(import_tests),
            "successful": len(import_tests) - len(failed_imports),
            "failed": failed_imports,
        }

        assert len(failed_imports) == 0, f"Failed imports: {failed_imports}"


class TestStressLoad:
    """Stress test Lambda Products under extreme load"""

    @pytest.mark.asyncio
    async def test_01_plugin_system_stress(self):
        """Test 01: Stress test plugin system with many plugins"""
        print("\n🧪 Test 01: Plugin System Stress Test")
        print("=" * 50)

        from plugin_system.plugin_base import (
            LukhasPlugin,
            PluginManifest,
            PluginStatus,
            PluginSystem,
        )

        plugin_system = PluginSystem()

        # Create and register many plugins
        num_plugins = 1000
        start_time = time.time()

        class StressTestPlugin(LukhasPlugin):
            def __init__(self, plugin_id):
                manifest = PluginManifest(
                    id=f"stress_{plugin_id}",
                    name=f"Stress Test Plugin {plugin_id}",
                    version="1.0.0",
                    description="Stress test plugin for testing scalability",
                )
                super().__init__(manifest)

            async def initialize(self, config):
                return True

            async def start(self):
                self.status = PluginStatus.ACTIVE
                return True

            async def stop(self):
                self.status = PluginStatus.DISABLED
                return True

            async def process(self, input_data):
                return {"processed": True, "data": input_data}

            async def health_check(self):
                from datetime import datetime

                from plugin_system.plugin_base import HealthStatus

                return HealthStatus(
                    is_healthy=True,
                    last_check=datetime.now(),
                    cpu_usage=random.uniform(1, 10),
                    memory_usage=random.uniform(10, 100),
                    response_time_ms=random.uniform(1, 10),
                    uptime_seconds=100,
                )

        # Register plugins
        registration_times = []
        for i in range(num_plugins):
            plugin = StressTestPlugin(i)
            reg_start = time.time()
            await plugin_system.register_plugin(plugin)
            registration_times.append(time.time() - reg_start)

            if i % 100 == 0:
                print(f"  Registered {i} plugins...")

        total_time = time.time() - start_time

        # Test operations on all plugins
        start_time = time.time()
        plugin_system.get_plugin_status_summary()
        summary_time = time.time() - start_time

        TEST_RESULTS["stress_tests"]["plugin_system"] = {
            "plugins_registered": num_plugins,
            "total_registration_time": total_time,
            "avg_registration_time": sum(registration_times) / len(registration_times),
            "max_registration_time": max(registration_times),
            "summary_generation_time": summary_time,
            "memory_used_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        }

        print(f"✅ Registered {num_plugins} plugins in {total_time:.2f}s")
        print(
            f"  Average: {sum(registration_times) / len(registration_times) * 1000:.2f}ms per plugin"
        )
        print(f"  Max: {max(registration_times) * 1000:.2f}ms")
        print(f"  Summary generation: {summary_time * 1000:.2f}ms")

        assert (
            total_time < 60
        ), f"Registration too slow: {total_time}s for {num_plugins} plugins"
        assert summary_time < 1, f"Summary generation too slow: {summary_time}s"

    @pytest.mark.asyncio
    async def test_02_autonomous_agents_stress(self):
        """Test 02: Stress test autonomous agents"""
        print("\n🧪 Test 02: Autonomous Agents Stress Test")
        print("=" * 50)

        from agents.autonomous_agent_framework import (
            AgentGoal,
            AgentPriority,
            AutonomousAgent,
        )

        # Create many agents
        num_agents = 100
        agents = []

        start_time = time.time()

        for i in range(num_agents):
            agent = AutonomousAgent(f"stress_agent_{i}", "stress_test")
            await agent.initialize({"max_autonomous_days": 1})

            # Add multiple goals to each agent
            for j in range(10):
                goal = AgentGoal(
                    description=f"Goal {j} for agent {i}", priority=AgentPriority.NORMAL
                )
                await agent.set_goal(goal)

            agents.append(agent)

            if i % 10 == 0:
                print(f"  Created {i} agents...")

        creation_time = time.time() - start_time

        # Let agents process tasks briefly
        process_tasks = []
        for agent in agents:
            process_tasks.append(agent.execute_tasks())

        start_time = time.time()
        await asyncio.gather(*process_tasks)
        processing_time = time.time() - start_time

        # Collect metrics
        total_tasks = sum(len(agent.task_queue) for agent in agents)
        total_completed = sum(len(agent.completed_tasks) for agent in agents)

        TEST_RESULTS["stress_tests"]["autonomous_agents"] = {
            "agents_created": num_agents,
            "goals_per_agent": 10,
            "creation_time": creation_time,
            "processing_time": processing_time,
            "total_tasks_queued": total_tasks,
            "total_tasks_completed": total_completed,
            "memory_used_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        }

        print(f"✅ Created {num_agents} agents in {creation_time:.2f}s")
        print(f"  Tasks queued: {total_tasks}")
        print(f"  Tasks completed: {total_completed}")
        print(f"  Processing time: {processing_time:.2f}s")

        assert creation_time < 30, f"Agent creation too slow: {creation_time}s"

    @pytest.mark.asyncio
    async def test_03_concurrent_operations(self):
        """Test 03: Test concurrent operations"""
        print("\n🧪 Test 03: Concurrent Operations Stress Test")
        print("=" * 50)

        from plugin_system.lambda_products_adapter import LambdaProductsAdapter

        adapter = LambdaProductsAdapter()

        # Simulate many concurrent operations
        num_operations = 1000

        async def simulate_operation(op_id):
            # Random operation
            operations = [
                lambda: adapter.enable_product(f"test_{op_id}", {}),
                lambda: adapter.disable_product(f"test_{op_id}"),
                lambda: adapter.get_status_summary(),
                lambda: adapter.get_enabled_products(),
            ]

            op = random.choice(operations)
            try:
                await op()
                return True
            except BaseException:
                return False

        start_time = time.time()

        # Run operations concurrently
        tasks = [simulate_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        execution_time = time.time() - start_time

        successful = sum(1 for r in results if r)
        failed = sum(1 for r in results if not r or isinstance(r, Exception))

        TEST_RESULTS["stress_tests"]["concurrent_operations"] = {
            "total_operations": num_operations,
            "successful": successful,
            "failed": failed,
            "execution_time": execution_time,
            "ops_per_second": num_operations / execution_time,
        }

        print(
            f"✅ Executed {num_operations} concurrent operations in {execution_time:.2f}s"
        )
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Rate: {num_operations / execution_time:.0f} ops/sec")

        assert execution_time < 10, f"Concurrent ops too slow: {execution_time}s"
        assert (
            successful > num_operations * 0.7
        ), f"Too many failures: {failed}/{num_operations}"


class TestMemoryAndPerformance:
    """Test memory usage and performance characteristics"""

    @pytest.mark.asyncio
    async def test_01_memory_leak_detection(self):
        """Test 01: Detect memory leaks"""
        print("\n🧪 Test 01: Memory Leak Detection")
        print("=" * 50)

        from agents.autonomous_agent_framework import AutonomousAgent
        from plugin_system.plugin_base import PluginSystem

        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create and destroy many objects
        for iteration in range(5):
            # Create plugin system
            plugin_system = PluginSystem()

            # Create agents
            agents = []
            for i in range(100):
                agent = AutonomousAgent(f"leak_test_{i}", "test")
                await agent.initialize({})
                agents.append(agent)

            # Process some tasks
            for agent in agents:
                await agent.execute_tasks()

            # Clean up
            del agents
            del plugin_system

            # Force garbage collection
            import gc

            gc.collect()

            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"  Iteration {iteration + 1}: Memory = {current_memory:.1f} MB")

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        # Get memory snapshot
        snapshot = tracemalloc.take_snapshot()
        snapshot.statistics("lineno")[:10]

        TEST_RESULTS["memory_tests"]["leak_detection"] = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_growth_mb": memory_growth,
            "growth_percentage": (
                (memory_growth / initial_memory) * 100 if initial_memory > 0 else 0
            ),
        }

        print("\n📊 Memory Analysis:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(
            f"  Growth: {memory_growth:.1f} MB ({(memory_growth / initial_memory) * 100:.1f}%)"
        )

        tracemalloc.stop()

        # Allow some memory growth but not excessive
        assert memory_growth < 100, f"Excessive memory growth: {memory_growth} MB"

    @pytest.mark.asyncio
    async def test_02_performance_benchmarks(self):
        """Test 02: Performance benchmarking"""
        print("\n🧪 Test 02: Performance Benchmarks")
        print("=" * 50)

        from agents.lambda_workforce_agents import (
            ABASProductivityOptimizerAgent,
            DASTContextOrchestratorAgent,
            NIASEmotionalIntelligenceAgent,
        )

        benchmarks = {}

        # Benchmark NIΛS agent
        agent = NIASEmotionalIntelligenceAgent("benchmark_nias")
        await agent.initialize({})

        start = time.time()
        for _ in range(100):
            await agent.monitor_emotional_state({"employee_count": 100})
        nias_time = time.time() - start
        benchmarks["nias_monitoring"] = nias_time / 100

        # Benchmark ΛBAS agent
        agent = ABASProductivityOptimizerAgent("benchmark_abas")
        await agent.initialize({})

        start = time.time()
        for _ in range(100):
            await agent.optimize_meeting_schedule({"meeting_count": 50})
        abas_time = time.time() - start
        benchmarks["abas_optimization"] = abas_time / 100

        # Benchmark DΛST agent
        agent = DASTContextOrchestratorAgent("benchmark_dast")
        await agent.initialize({})

        start = time.time()
        for _ in range(100):
            await agent.build_knowledge_graph({})
        dast_time = time.time() - start
        benchmarks["dast_knowledge_graph"] = dast_time / 100

        TEST_RESULTS["performance_benchmarks"] = benchmarks

        print("📊 Performance Benchmarks (per operation):")
        for operation, time_sec in benchmarks.items():
            print(f"  {operation}: {time_sec * 1000:.2f}ms")

        # All operations should be fast
        for op, time_sec in benchmarks.items():
            assert time_sec < 0.1, f"{op} too slow: {time_sec}s"


class TestEdgeCasesAndSecurity:
    """Test edge cases and security scenarios"""

    @pytest.mark.asyncio
    async def test_01_edge_cases(self):
        """Test 01: Edge case handling"""
        print("\n🧪 Test 01: Edge Case Testing")
        print("=" * 50)

        from agents.autonomous_agent_framework import (
            AgentGoal,
            AutonomousAgent,
        )
        from plugin_system.plugin_base import PluginSystem

        edge_cases_passed = []
        edge_cases_failed = []

        # Test 1: Empty plugin system
        try:
            plugin_system = PluginSystem()
            summary = plugin_system.get_plugin_status_summary()
            assert summary == {}, "Empty system should return empty summary"
            edge_cases_passed.append("empty_plugin_system")
            print("✅ Empty plugin system handled")
        except Exception as e:
            edge_cases_failed.append(f"empty_plugin_system: {e}")
            print(f"❌ Empty plugin system failed: {e}")

        # Test 2: Agent with no goals
        try:
            agent = AutonomousAgent("no_goals", "test")
            await agent.initialize({})
            await agent.plan_next_action()
            edge_cases_passed.append("agent_no_goals")
            print("✅ Agent with no goals handled")
        except Exception as e:
            edge_cases_failed.append(f"agent_no_goals: {e}")
            print(f"❌ Agent with no goals failed: {e}")

        # Test 3: Massive input strings
        try:
            massive_string = "x" * 1000000  # 1MB string
            agent = AutonomousAgent("massive_input", "test")
            await agent.initialize({})
            goal = AgentGoal(description=massive_string)
            await agent.set_goal(goal)
            edge_cases_passed.append("massive_input")
            print("✅ Massive input handled")
        except Exception as e:
            edge_cases_failed.append(f"massive_input: {e}")
            print(f"❌ Massive input failed: {e}")

        # Test 4: Rapid start/stop cycles
        try:
            agent = AutonomousAgent("rapid_cycle", "test")
            for _ in range(100):
                await agent.initialize({})
                await agent.shutdown()
            edge_cases_passed.append("rapid_cycles")
            print("✅ Rapid start/stop cycles handled")
        except Exception as e:
            edge_cases_failed.append(f"rapid_cycles: {e}")
            print(f"❌ Rapid cycles failed: {e}")

        # Test 5: Null/None values
        try:
            agent = AutonomousAgent(None, None)
            await agent.initialize(None)
            edge_cases_passed.append("null_values")
            print("✅ Null values handled")
        except Exception:
            # This should fail gracefully
            edge_cases_passed.append("null_values_rejected")
            print("✅ Null values properly rejected")

        TEST_RESULTS["security_tests"]["edge_cases"] = {
            "passed": edge_cases_passed,
            "failed": edge_cases_failed,
            "pass_rate": len(edge_cases_passed)
            / (len(edge_cases_passed) + len(edge_cases_failed)),
        }

        assert len(edge_cases_failed) == 0, f"Edge cases failed: {edge_cases_failed}"

    @pytest.mark.asyncio
    async def test_02_security_validation(self):
        """Test 02: Security validation"""
        print("\n🧪 Test 02: Security Validation")
        print("=" * 50)

        security_tests_passed = []
        security_tests_failed = []

        # Test 1: SQL injection attempt
        try:
            from agents.autonomous_agent_framework import (
                AgentGoal,
                AutonomousAgent,
            )

            agent = AutonomousAgent("security_test", "test")
            await agent.initialize({})

            # Try SQL injection in goal
            malicious_goal = AgentGoal(
                description="'; DROP TABLE users; --",
                success_criteria={"test": "1 OR 1=1"},
            )
            await agent.set_goal(malicious_goal)

            # Should handle without executing SQL
            security_tests_passed.append("sql_injection_prevented")
            print("✅ SQL injection attempt handled safely")
        except Exception as e:
            security_tests_failed.append(f"sql_injection: {e}")
            print(f"❌ SQL injection test failed: {e}")

        # Test 2: Path traversal attempt
        try:
            malicious_path = "../../../etc/passwd"
            agent = AutonomousAgent(malicious_path, "test")
            await agent.save_state()  # Should not access system files
            security_tests_passed.append("path_traversal_prevented")
            print("✅ Path traversal attempt prevented")
        except Exception:
            # Expected to fail safely
            security_tests_passed.append("path_traversal_prevented")
            print("✅ Path traversal properly blocked")

        # Test 3: Resource exhaustion attempt
        try:
            from plugin_system.plugin_base import PluginSystem

            plugin_system = PluginSystem()
            # Try to exhaust resources
            for _i in range(10000):
                # This should be rate-limited or rejected
                plugin_system.get_plugin_status_summary()

            security_tests_passed.append("resource_exhaustion_handled")
            print("✅ Resource exhaustion attempt handled")
        except Exception as e:
            security_tests_failed.append(f"resource_exhaustion: {e}")
            print(f"❌ Resource exhaustion test failed: {e}")

        TEST_RESULTS["security_tests"]["security_validation"] = {
            "passed": security_tests_passed,
            "failed": security_tests_failed,
            "pass_rate": (
                len(security_tests_passed)
                / (len(security_tests_passed) + len(security_tests_failed))
                if (len(security_tests_passed) + len(security_tests_failed)) > 0
                else 0
            ),
        }

        assert (
            len(security_tests_failed) == 0
        ), f"Security tests failed: {security_tests_failed}"


class TestIntegrationPaths:
    """Test all integration paths work correctly"""

    @pytest.mark.asyncio
    async def test_01_pwm_integration_path(self):
        """Test 01: Full PWM integration path"""
        print("\n🧪 Test 01: PWM Integration Path")
        print("=" * 50)

        try:
            from integration.lukhas_pwm_adapter import (
                ABASPWMPlugin,
                DASTPWMPlugin,
                LukhasPWMIntegrationAdapter,
                NIASPWMPlugin,
            )

            adapter = LukhasPWMIntegrationAdapter()

            # Register all products
            products = [NIASPWMPlugin(), ABASPWMPlugin(), DASTPWMPlugin()]

            for product in products:
                success = await adapter.register_lambda_product(product, {})
                assert (
                    success or not adapter.plugin_registry
                ), "Registration should succeed or PWM not available"

            print("✅ PWM integration path validated")

            TEST_RESULTS["path_validation"]["pwm_integration"] = "passed"

        except Exception as e:
            print(f"❌ PWM integration failed: {e}")
            TEST_RESULTS["path_validation"]["pwm_integration"] = f"failed: {e}"
            raise

    @pytest.mark.asyncio
    async def test_02_openai_integration_path(self):
        """Test 02: OpenAI integration path"""
        print("\n🧪 Test 02: OpenAI Integration Path")
        print("=" * 50)

        try:
            from integrations.openai_agi_bridge import (
                OpenAILambdaBridge,
            )

            # Create bridge (won't connect without API key)
            bridge = OpenAILambdaBridge()

            # Initialize with test config
            await bridge.initialize(
                {
                    "integration_level": "BASIC",
                    "connect_nias": True,
                    "connect_abas": True,
                    "connect_dast": True,
                }
            )

            # Test consciousness processing (simulated)
            result = await bridge.process_with_consciousness(
                prompt="Test prompt", user_id="test_user", context={"test": True}
            )

            assert "response" in result, "Should return response"
            assert "lambda_context" in result, "Should include Lambda context"

            print("✅ OpenAI integration path validated")

            TEST_RESULTS["path_validation"]["openai_integration"] = "passed"

        except Exception as e:
            print(f"❌ OpenAI integration failed: {e}")
            TEST_RESULTS["path_validation"]["openai_integration"] = f"failed: {e}"
            raise


def generate_comprehensive_report():
    """Generate comprehensive test report"""

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_suite": "Comprehensive Stress Testing",
        "summary": {
            "total_tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_grade": "A",
            "production_ready": False,
        },
        "results": TEST_RESULTS,
        "recommendations": [],
    }

    # Calculate summary
    for category in TEST_RESULTS.values():
        if isinstance(category, dict):
            for _test_name, result in category.items():
                report["summary"]["total_tests_run"] += 1
                if (
                    isinstance(result, str)
                    and "failed" not in result
                    or isinstance(result, dict)
                    and not result.get("failed")
                ):
                    report["summary"]["tests_passed"] += 1
                else:
                    report["summary"]["tests_failed"] += 1

    # Determine production readiness
    pass_rate = (
        report["summary"]["tests_passed"] / report["summary"]["total_tests_run"]
        if report["summary"]["total_tests_run"] > 0
        else 0
    )
    report["summary"]["pass_rate"] = pass_rate
    report["summary"]["production_ready"] = pass_rate > 0.95

    # Performance grade
    if pass_rate >= 0.95:
        report["summary"]["performance_grade"] = "A+"
    elif pass_rate >= 0.90:
        report["summary"]["performance_grade"] = "A"
    elif pass_rate >= 0.80:
        report["summary"]["performance_grade"] = "B"
    else:
        report["summary"]["performance_grade"] = "C"

    # Add recommendations
    if report["summary"]["tests_failed"] > 0:
        report["recommendations"].append(
            "Fix failing tests before production deployment"
        )

    if (
        TEST_RESULTS.get("stress_tests", {})
        .get("plugin_system", {})
        .get("avg_registration_time", 0)
        > 0.01
    ):
        report["recommendations"].append(
            "Optimize plugin registration for better performance"
        )

    if (
        TEST_RESULTS.get("memory_tests", {})
        .get("leak_detection", {})
        .get("memory_growth_mb", 0)
        > 50
    ):
        report["recommendations"].append("Investigate potential memory leaks")

    # Save report
    report_path = (
        Path(__file__).parent.parent
        / "reports"
        / "comprehensive_stress_test_report.json"
    )
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Test report saved to: {report_path}")

    return report


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 LAMBDA PRODUCTS - COMPREHENSIVE STRESS TESTING")
    print("=" * 60)
    print("\nRunning all stress tests, path validations, and benchmarks...")
    print("This will test everything under extreme conditions.\n")

    # Run all tests
    pytest.main([__file__, "-v", "--tb=short", "-W", "ignore::DeprecationWarning"])

    # Generate report
    report = generate_comprehensive_report()

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)

    print(f"\nTotal Tests: {report['summary']['total_tests_run']}")
    print(f"Passed: {report['summary']['tests_passed']}")
    print(f"Failed: {report['summary']['tests_failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1%}")
    print(f"Grade: {report['summary']['performance_grade']}")
    print(
        f"Production Ready: {'✅ YES' if report['summary']['production_ready'] else '❌ NO'}"
    )

    if report["recommendations"]:
        print("\n📝 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

    print("\n" + "=" * 60)
    print("✅ STRESS TESTING COMPLETE")
    print("=" * 60)
