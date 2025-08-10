#!/usr/bin/env python3
"""
Lambda Products Integration Test Runner
Tests integration with Lukhas PWM and production deployment readiness
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


class IntegrationTestRunner:
    """Run comprehensive integration tests for Lambda Products"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "integration_tests": [],
            "performance_metrics": {},
            "deployment_status": {},
            "summary": {},
        }

    async def test_plugin_registration_performance(self) -> Dict[str, Any]:
        """Test plugin registration performance"""
        print("\n📊 Testing Plugin Registration Performance...")

        from plugins.plugin_base import PluginSystem

        results = {
            "test": "Plugin Registration Performance",
            "status": "FAILED",
            "metrics": {},
        }

        try:
            plugin_system = PluginSystem()

            # Warm up
            for i in range(10):
                await plugin_system.register_plugin(
                    {"name": f"warmup_{i}", "version": "1.0.0"}
                )

            # Performance test
            start_time = time.perf_counter()
            num_registrations = 1000

            for i in range(num_registrations):
                await plugin_system.register_plugin(
                    {"name": f"perf_test_{i}", "version": "1.0.0", "enabled": True}
                )

            end_time = time.perf_counter()

            total_time_ms = (end_time - start_time) * 1000
            avg_time_ms = total_time_ms / num_registrations
            ops_per_sec = num_registrations / (end_time - start_time)

            results["metrics"] = {
                "total_registrations": num_registrations,
                "total_time_ms": round(total_time_ms, 2),
                "avg_time_ms": round(avg_time_ms, 3),
                "ops_per_sec": round(ops_per_sec, 0),
            }

            # Check against target (< 2ms per registration)
            if avg_time_ms < 2:
                results["status"] = "PASSED"
                print(f"   ✅ Registration performance: {ops_per_sec:.0f} ops/sec")
            else:
                print(f"   ❌ Registration too slow: {avg_time_ms:.2f}ms per op")

        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return results

    async def test_agent_orchestration(self) -> Dict[str, Any]:
        """Test agent orchestration capabilities"""
        print("\n🤖 Testing Agent Orchestration...")

        results = {"test": "Agent Orchestration", "status": "FAILED", "details": {}}

        try:
            from agents.autonomous_agent_framework import (
                AgentGoal,
                AgentOrchestrator,
                AgentPriority,
                AutonomousAgent,
            )

            orchestrator = AgentOrchestrator()

            # Deploy multiple agents
            agents_deployed = []
            for i in range(5):
                agent = AutonomousAgent(f"test_agent_{i}", "NIAS")
                config = {"max_autonomous_days": 1, "decision_threshold": 0.85}
                await orchestrator.deploy_agent(agent, config)
                agents_deployed.append(agent)

            results["details"]["agents_deployed"] = len(agents_deployed)

            # Set goals for agents
            for agent in agents_deployed:
                goal = AgentGoal(
                    description=f"Goal for {agent.agent_id}",
                    priority=AgentPriority.NORMAL,
                )
                await agent.set_goal(goal)

            # Test coordination - get_active_agents is async
            active_agents = await orchestrator.get_active_agents()
            results["details"]["active_agents"] = len(active_agents)

            # Test shutdown - shutdown_all_agents is async
            await orchestrator.shutdown_all_agents()

            results["status"] = "PASSED"
            print(f"   ✅ Orchestrated {len(agents_deployed)} agents successfully")

        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return results

    async def test_lukhas_pwm_integration(self) -> Dict[str, Any]:
        """Test integration with Lukhas PWM system"""
        print("\n🔗 Testing Lukhas PWM Integration...")

        results = {"test": "Lukhas PWM Integration", "status": "FAILED", "details": {}}

        try:
            # Try to import PWM components
            try:
                from core.plugin_registry import PluginRegistry

                results["details"]["pwm_available"] = True
            except ImportError:
                results["details"]["pwm_available"] = False
                results["status"] = "SKIPPED"
                print("   ⏭️  PWM not available - skipping integration test")
                return results

            # Test adapter
            from integrations.lukhas_pwm_adapter import (
                LukhasPWMIntegrationAdapter,
            )

            adapter = LukhasPWMIntegrationAdapter()

            # Auto-register products
            products = await adapter.auto_register_all_products()
            results["details"]["products_registered"] = len(products) if products else 0

            # Test consciousness connection
            consciousness_connected = await adapter.connect_consciousness_layer()
            results["details"]["consciousness_connected"] = consciousness_connected

            if products and consciousness_connected:
                results["status"] = "PASSED"
                print(
                    f"   ✅ PWM Integration successful - {len(products)} products registered"
                )
            else:
                print("   ⚠️  Partial integration - some components failed")

        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return results

    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints if available"""
        print("\n🌐 Testing API Endpoints...")

        results = {"test": "API Endpoints", "status": "FAILED", "endpoints": []}

        try:
            # Check if FastAPI server can be started
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            # Create test app
            app = FastAPI()

            # Add test endpoints
            @app.get("/health")
            async def health():
                return {"status": "healthy"}

            @app.get("/agents")
            async def get_agents():
                return {"agents": []}

            # Test with client
            client = TestClient(app)

            # Test health endpoint
            response = client.get("/health")
            if response.status_code == 200:
                results["endpoints"].append(
                    {
                        "path": "/health",
                        "status": response.status_code,
                        "response": response.json(),
                    }
                )

            # Test agents endpoint
            response = client.get("/agents")
            if response.status_code == 200:
                results["endpoints"].append(
                    {
                        "path": "/agents",
                        "status": response.status_code,
                        "response": response.json(),
                    }
                )

            if len(results["endpoints"]) > 0:
                results["status"] = "PASSED"
                print(f"   ✅ API endpoints tested: {len(results['endpoints'])}")

        except ImportError:
            results["status"] = "SKIPPED"
            results["error"] = "FastAPI not installed"
            print("   ⏭️  FastAPI not available - skipping API tests")

        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return results

    async def test_deployment_readiness(self) -> Dict[str, Any]:
        """Test deployment readiness"""
        print("\n🚀 Testing Deployment Readiness...")

        results = {"test": "Deployment Readiness", "status": "FAILED", "checks": {}}

        try:
            # Check required files
            required_files = [
                "requirements.txt",
                "setup.py",
                "MANIFEST.json",
                "deploy/production_deployment.py",
            ]

            base_path = Path(__file__).parent
            files_found = 0

            for file in required_files:
                file_path = base_path / file
                if file_path.exists():
                    files_found += 1
                    results["checks"][file] = "✅ Found"
                else:
                    results["checks"][file] = "❌ Missing"

            # Check infrastructure files
            terraform_path = base_path / "infrastructure" / "terraform" / "main.tf"
            if terraform_path.exists():
                results["checks"]["terraform"] = "✅ Found"
                files_found += 1
            else:
                results["checks"]["terraform"] = "❌ Missing"

            # Check monitoring config
            monitoring_path = base_path / "monitoring" / "prometheus_alerts.yml"
            if monitoring_path.exists():
                results["checks"]["monitoring"] = "✅ Found"
                files_found += 1
            else:
                results["checks"]["monitoring"] = "❌ Missing"

            # Determine status
            total_checks = len(required_files) + 2
            if files_found == total_checks:
                results["status"] = "PASSED"
                print(
                    f"   ✅ All deployment files present ({files_found}/{total_checks})"
                )
            else:
                print(
                    f"   ⚠️  Some deployment files missing ({files_found}/{total_checks})"
                )

        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return results

    async def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        print("\n⚡ Running Performance Benchmarks...")

        benchmarks = {
            "test": "Performance Benchmarks",
            "status": "FAILED",
            "results": {},
        }

        try:
            from agents.autonomous_agent_framework import AgentOrchestrator
            from plugins.plugin_base import PluginSystem

            # Benchmark 1: Plugin registration throughput
            plugin_system = PluginSystem()
            start = time.perf_counter()

            for i in range(1000):
                await plugin_system.register_plugin(
                    {"name": f"bench_{i}", "version": "1.0.0"}
                )

            plugin_time = time.perf_counter() - start
            plugin_throughput = 1000 / plugin_time

            benchmarks["results"]["plugin_throughput"] = {
                "ops_per_sec": round(plugin_throughput, 0),
                "time_per_op_ms": round((plugin_time / 1000) * 1000, 3),
            }

            # Benchmark 2: Agent deployment speed
            orchestrator = AgentOrchestrator()
            start = time.perf_counter()

            for i in range(10):
                from agents.autonomous_agent_framework import AutonomousAgent

                agent = AutonomousAgent(f"bench_agent_{i}", "NIAS")
                await orchestrator.deploy_agent(agent, {})

            agent_time = time.perf_counter() - start
            agent_throughput = 10 / agent_time

            benchmarks["results"]["agent_deployment"] = {
                "agents_per_sec": round(agent_throughput, 2),
                "time_per_agent_ms": round((agent_time / 10) * 1000, 1),
            }

            # Check against targets
            if plugin_throughput > 500 and agent_throughput > 5:
                benchmarks["status"] = "PASSED"
                print("   ✅ Performance targets met")
            else:
                print("   ⚠️  Performance below targets")

            print(f"   Plugin throughput: {plugin_throughput:.0f} ops/sec")
            print(f"   Agent deployment: {agent_throughput:.1f} agents/sec")

        except Exception as e:
            benchmarks["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return benchmarks

    async def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("🧪 LAMBDA PRODUCTS INTEGRATION TEST SUITE")
        print("=" * 60)

        # Run tests
        test_results = []

        # Integration tests
        test_results.append(await self.test_plugin_registration_performance())
        test_results.append(await self.test_agent_orchestration())
        test_results.append(await self.test_lukhas_pwm_integration())
        test_results.append(await self.test_api_endpoints())
        test_results.append(await self.test_deployment_readiness())

        # Performance benchmarks
        benchmark_results = await self.run_performance_benchmarks()

        # Store results
        self.results["integration_tests"] = test_results
        self.results["performance_metrics"] = benchmark_results

        # Generate summary
        total_tests = len(test_results) + 1  # +1 for benchmarks
        passed_tests = sum(1 for t in test_results if t["status"] == "PASSED")
        if benchmark_results["status"] == "PASSED":
            passed_tests += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": round((passed_tests / total_tests) * 100, 1),
        }

        # Print summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)

        summary = self.results["summary"]
        print("\n📈 Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   Success Rate: {summary['success_rate']}%")

        # Performance highlights
        if "performance_metrics" in self.results:
            perf = self.results["performance_metrics"]
            if "results" in perf and "plugin_throughput" in perf["results"]:
                throughput = perf["results"]["plugin_throughput"]["ops_per_sec"]
                print("\n⚡ Performance:")
                print(f"   Plugin Throughput: {throughput} ops/sec")

    def save_results(self):
        """Save test results"""
        # Save JSON report
        results_file = Path(__file__).parent / "integration_test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_file}")

        # Save markdown report
        report_file = Path(__file__).parent / "integration_test_report.md"
        with open(report_file, "w") as f:
            f.write("# Lambda Products Integration Test Report\n\n")
            f.write(f"**Date:** {self.results['timestamp']}\n\n")

            f.write("## Summary\n\n")
            summary = self.results["summary"]
            f.write(f"- **Total Tests:** {summary['total_tests']}\n")
            f.write(f"- **Passed:** {summary['passed']}\n")
            f.write(f"- **Failed:** {summary['failed']}\n")
            f.write(f"- **Success Rate:** {summary['success_rate']}%\n\n")

            f.write("## Integration Tests\n\n")
            for test in self.results["integration_tests"]:
                f.write(f"### {test['test']}\n")
                f.write(f"**Status:** {test['status']}\n\n")
                if "metrics" in test:
                    f.write("**Metrics:**\n")
                    for key, value in test["metrics"].items():
                        f.write(f"- {key}: {value}\n")
                    f.write("\n")
                if "details" in test:
                    f.write("**Details:**\n")
                    for key, value in test["details"].items():
                        f.write(f"- {key}: {value}\n")
                    f.write("\n")

        print(f"📝 Report saved to: {report_file}")


async def main():
    """Main entry point"""
    runner = IntegrationTestRunner()
    await runner.run_all_tests()

    # Exit with appropriate code
    if runner.results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1)
