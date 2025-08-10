#!/usr/bin/env python3
"""
Chaos Engineering Tests
Test system resilience under failure conditions
"""

import asyncio
import logging
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChaosScenario:
    """Chaos test scenario definition"""

    name: str
    description: str
    failure_type: str
    affected_components: List[str]
    duration_seconds: float
    recovery_expected: bool
    severity: str  # low, medium, high, critical


class TestChaosEngineering:
    """Chaos engineering test suite"""

    @pytest.fixture
    def chaos_scenarios(self):
        """Define chaos scenarios to test"""
        return [
            ChaosScenario(
                name="hub_failure",
                description="Random hub becomes unresponsive",
                failure_type="unresponsive",
                affected_components=["memory_hub"],
                duration_seconds=5.0,
                recovery_expected=True,
                severity="high",
            ),
            ChaosScenario(
                name="bridge_network_partition",
                description="Bridge loses network connectivity",
                failure_type="network_partition",
                affected_components=["core_consciousness_bridge"],
                duration_seconds=3.0,
                recovery_expected=True,
                severity="medium",
            ),
            ChaosScenario(
                name="cascading_failure",
                description="Multiple component failures cascade",
                failure_type="cascading",
                affected_components=[
                    "quantum_hub",
                    "consciousness_hub",
                    "quantum_consciousness_bridge",
                ],
                duration_seconds=10.0,
                recovery_expected=True,
                severity="critical",
            ),
            ChaosScenario(
                name="memory_exhaustion",
                description="System runs out of memory",
                failure_type="resource_exhaustion",
                affected_components=["memory_manager"],
                duration_seconds=5.0,
                recovery_expected=True,
                severity="high",
            ),
            ChaosScenario(
                name="service_discovery_failure",
                description="Service discovery becomes unavailable",
                failure_type="service_unavailable",
                affected_components=["service_discovery"],
                duration_seconds=7.0,
                recovery_expected=True,
                severity="high",
            ),
        ]

    @pytest.fixture
    async def resilient_system(self):
        """Mock system with resilience features"""

        class ResilientSystem:
            def __init__(self):
                self.components = {
                    "core_hub": {"status": "healthy", "retries": 0},
                    "memory_hub": {"status": "healthy", "retries": 0},
                    "consciousness_hub": {"status": "healthy", "retries": 0},
                    "quantum_hub": {"status": "healthy", "retries": 0},
                    "safety_hub": {"status": "healthy", "retries": 0},
                    "core_consciousness_bridge": {"status": "connected", "retries": 0},
                    "quantum_consciousness_bridge": {
                        "status": "connected",
                        "retries": 0,
                    },
                    "service_discovery": {"status": "available", "retries": 0},
                    "memory_manager": {"status": "healthy", "memory_used": 0.5},
                }
                self.circuit_breakers = {}
                self.failover_enabled = True
                self.max_retries = 3
                self.retry_delay = 0.5
                self.chaos_active = {}

            async def inject_failure(
                self, component: str, failure_type: str, duration: float
            ):
                """Inject a failure into a component"""
                logger.info(
                    f"💥 Injecting {failure_type} failure in {component} for {duration}s"
                )

                self.chaos_active[component] = {
                    "type": failure_type,
                    "start_time": time.time(),
                    "duration": duration,
                }

                # Apply failure
                if failure_type == "unresponsive":
                    self.components[component]["status"] = "unresponsive"
                elif failure_type == "network_partition":
                    self.components[component]["status"] = "disconnected"
                elif failure_type == "resource_exhaustion":
                    if component == "memory_manager":
                        self.components[component]["memory_used"] = 0.95
                elif failure_type == "service_unavailable":
                    self.components[component]["status"] = "unavailable"

                # Schedule recovery
                asyncio.create_task(self._recover_component(component, duration))

            async def _recover_component(self, component: str, after_seconds: float):
                """Recover component after specified duration"""
                await asyncio.sleep(after_seconds)

                logger.info(f"🔧 Recovering {component}")

                # Restore component
                if component.endswith("_hub"):
                    self.components[component]["status"] = "healthy"
                elif component.endswith("_bridge"):
                    self.components[component]["status"] = "connected"
                elif component == "service_discovery":
                    self.components[component]["status"] = "available"
                elif component == "memory_manager":
                    self.components[component]["memory_used"] = 0.5

                # Clear chaos marker
                if component in self.chaos_active:
                    del self.chaos_active[component]

            async def call_component(
                self, component: str, operation: str
            ) -> Dict[str, Any]:
                """Call a component with resilience logic"""
                # Check if component is in chaos
                if component in self.chaos_active:
                    chaos = self.chaos_active[component]
                    if time.time() - chaos["start_time"] < chaos["duration"]:
                        # Component is failing
                        if chaos["type"] == "unresponsive":
                            await asyncio.sleep(30)  # Timeout simulation
                            raise TimeoutError(f"{component} is unresponsive")
                        elif chaos["type"] in ["network_partition", "disconnected"]:
                            raise ConnectionError(f"{component} is unreachable")
                        elif chaos["type"] == "resource_exhaustion":
                            raise MemoryError(f"{component} out of resources")
                        elif chaos["type"] == "service_unavailable":
                            raise RuntimeError(f"{component} is unavailable")

                # Check circuit breaker
                if self._is_circuit_open(component):
                    raise RuntimeError(f"Circuit breaker open for {component}")

                # Normal operation
                comp_info = self.components.get(component, {})
                if comp_info.get("status") in ["healthy", "connected", "available"]:
                    return {
                        "result": "success",
                        "component": component,
                        "operation": operation,
                    }
                else:
                    raise RuntimeError(
                        f"{component} is {comp_info.get('status', 'unknown')}"
                    )

            async def call_with_retry(
                self, component: str, operation: str
            ) -> Optional[Dict[str, Any]]:
                """Call component with retry logic"""
                for attempt in range(self.max_retries):
                    try:
                        result = await self.call_component(component, operation)
                        # Reset retry counter on success
                        self.components[component]["retries"] = 0
                        self._close_circuit(component)
                        return result
                    except Exception as e:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {component}: {e}"
                        )
                        self.components[component]["retries"] += 1

                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                        else:
                            # Open circuit breaker after max retries
                            self._open_circuit(component)

                            # Try failover if enabled
                            if self.failover_enabled:
                                return await self._failover(component, operation)
                            raise

                return None

            async def _failover(
                self, failed_component: str, operation: str
            ) -> Optional[Dict[str, Any]]:
                """Attempt failover to alternative component"""
                logger.info(f"🔄 Attempting failover for {failed_component}")

                # Define failover mappings
                failovers = {
                    "memory_hub": "memory_manager",
                    "consciousness_hub": "quantum_hub",
                    "service_discovery": "core_hub",  # Core can provide basic discovery
                }

                alternative = failovers.get(failed_component)
                if alternative and alternative in self.components:
                    try:
                        result = await self.call_component(alternative, operation)
                        result["failover"] = True
                        result["original_component"] = failed_component
                        return result
                    except Exception as e:
                        logger.error(f"Failover to {alternative} also failed: {e}")

                return None

            def _is_circuit_open(self, component: str) -> bool:
                """Check if circuit breaker is open"""
                breaker = self.circuit_breakers.get(component, {})
                if breaker.get("state") == "open":
                    # Check if cool-down period has passed
                    if time.time() - breaker["opened_at"] > 10:  # 10 second cool-down
                        self._close_circuit(component)
                        return False
                    return True
                return False

            def _open_circuit(self, component: str):
                """Open circuit breaker for component"""
                logger.warning(f"⚡ Opening circuit breaker for {component}")
                self.circuit_breakers[component] = {
                    "state": "open",
                    "opened_at": time.time(),
                }

            def _close_circuit(self, component: str):
                """Close circuit breaker for component"""
                if component in self.circuit_breakers:
                    logger.info(f"✅ Closing circuit breaker for {component}")
                    self.circuit_breakers[component]["state"] = "closed"

            async def health_check(self) -> Dict[str, Any]:
                """System-wide health check"""
                healthy_components = sum(
                    1
                    for c in self.components.values()
                    if c.get("status") in ["healthy", "connected", "available"]
                )
                total_components = len(self.components)

                health_percentage = (healthy_components / total_components) * 100

                return {
                    "overall_health": health_percentage,
                    "healthy_components": healthy_components,
                    "total_components": total_components,
                    "status": "healthy" if health_percentage > 80 else "degraded",
                    "chaos_active": len(self.chaos_active) > 0,
                    "open_circuits": sum(
                        1
                        for cb in self.circuit_breakers.values()
                        if cb.get("state") == "open"
                    ),
                }

        return ResilientSystem()

    @pytest.mark.asyncio
    async def test_single_component_failure(self, resilient_system, chaos_scenarios):
        """Test system behavior with single component failure"""
        scenario = chaos_scenarios[0]  # hub_failure

        # Baseline - system should be healthy
        health = await resilient_system.health_check()
        assert health["status"] == "healthy"
        assert health["overall_health"] == 100

        # Inject failure
        await resilient_system.inject_failure(
            scenario.affected_components[0],
            scenario.failure_type,
            scenario.duration_seconds,
        )

        # System should be degraded
        health = await resilient_system.health_check()
        assert health["chaos_active"] == True

        # Try to use failed component
        try:
            result = await resilient_system.call_with_retry(
                scenario.affected_components[0], "test_operation"
            )
            # Should either succeed with failover or fail
            if result:
                assert result.get("failover") == True
        except Exception as e:
            # Expected during failure
            assert scenario.failure_type in str(e).lower()

        # Wait for recovery
        await asyncio.sleep(scenario.duration_seconds + 1)

        # System should recover
        health = await resilient_system.health_check()
        assert health["status"] == "healthy"
        assert health["chaos_active"] == False

    @pytest.mark.asyncio
    async def test_cascading_failure(self, resilient_system, chaos_scenarios):
        """Test system behavior under cascading failures"""
        scenario = next(s for s in chaos_scenarios if s.name == "cascading_failure")

        # Inject multiple failures
        tasks = []
        for i, component in enumerate(scenario.affected_components):
            # Stagger failures to simulate cascade
            delay = i * 0.5
            task = asyncio.create_task(
                self._delayed_failure_injection(
                    resilient_system,
                    component,
                    scenario.failure_type,
                    scenario.duration_seconds,
                    delay,
                )
            )
            tasks.append(task)

        # Wait for all failures to be injected
        await asyncio.gather(*tasks)

        # System should be severely degraded
        health = await resilient_system.health_check()
        assert health["overall_health"] < 80
        assert health["status"] == "degraded"

        # Try operations on various components
        results = []
        for component in ["core_hub", "memory_hub", "safety_hub"]:
            try:
                result = await resilient_system.call_with_retry(component, "test_op")
                results.append((component, "success", result))
            except Exception as e:
                results.append((component, "failed", str(e)))

        # Some components should still work
        successful = [r for r in results if r[1] == "success"]
        assert len(successful) > 0, "System should maintain partial functionality"

        # Wait for recovery
        await asyncio.sleep(scenario.duration_seconds + 2)

        # System should recover
        health = await resilient_system.health_check()
        assert health["overall_health"] > 80

    async def _delayed_failure_injection(
        self, system, component, failure_type, duration, delay
    ):
        """Helper to inject failure after delay"""
        await asyncio.sleep(delay)
        await system.inject_failure(component, failure_type, duration)

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, resilient_system):
        """Test circuit breaker protection"""
        component = "memory_hub"

        # Inject permanent failure
        await resilient_system.inject_failure(component, "unresponsive", 60)

        # First call should retry and eventually open circuit
        with pytest.raises(Exception):
            await resilient_system.call_with_retry(component, "test")

        # Circuit should be open
        assert resilient_system._is_circuit_open(component)

        # Immediate retry should fail fast due to open circuit
        start = time.time()
        with pytest.raises(RuntimeError) as exc_info:
            await resilient_system.call_component(component, "test")
        duration = time.time() - start

        assert "Circuit breaker open" in str(exc_info.value)
        assert duration < 1.0  # Should fail fast, not timeout

    @pytest.mark.asyncio
    async def test_failover_mechanism(self, resilient_system):
        """Test failover to alternative components"""
        # Enable failover
        resilient_system.failover_enabled = True

        # Fail memory_hub
        await resilient_system.inject_failure("memory_hub", "unresponsive", 5)

        # Call should failover to memory_manager
        result = await resilient_system.call_with_retry("memory_hub", "store_data")

        assert result is not None
        assert result["failover"] == True
        assert result["original_component"] == "memory_hub"
        assert result["component"] == "memory_manager"

    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(
        self, resilient_system, chaos_scenarios
    ):
        """Test recovery from resource exhaustion"""
        scenario = next(
            s for s in chaos_scenarios if s.failure_type == "resource_exhaustion"
        )

        # Check initial memory usage
        initial_memory = resilient_system.components["memory_manager"]["memory_used"]
        assert initial_memory < 0.8

        # Inject memory exhaustion
        await resilient_system.inject_failure(
            "memory_manager", "resource_exhaustion", scenario.duration_seconds
        )

        # Memory should be exhausted
        assert resilient_system.components["memory_manager"]["memory_used"] > 0.9

        # Operations should fail
        with pytest.raises(MemoryError):
            await resilient_system.call_component("memory_manager", "allocate")

        # Wait for recovery
        await asyncio.sleep(scenario.duration_seconds + 1)

        # Memory should be restored
        assert resilient_system.components["memory_manager"]["memory_used"] < 0.8

        # Operations should succeed again
        result = await resilient_system.call_component("memory_manager", "allocate")
        assert result["result"] == "success"

    @pytest.mark.asyncio
    async def test_chaos_under_load(self, resilient_system):
        """Test system behavior under load with chaos"""

        # Generate load
        async def generate_load(duration: float):
            end_time = time.time() + duration
            operations = 0
            errors = 0

            while time.time() < end_time:
                component = random.choice(list(resilient_system.components.keys()))
                try:
                    await resilient_system.call_with_retry(component, "load_test")
                    operations += 1
                except Exception:
                    errors += 1

                await asyncio.sleep(0.01)  # 100 ops/sec target

            return operations, errors

        # Start load generation
        load_task = asyncio.create_task(generate_load(10))  # 10 seconds

        # Inject random failures during load
        await asyncio.sleep(2)
        await resilient_system.inject_failure("core_hub", "unresponsive", 2)

        await asyncio.sleep(2)
        await resilient_system.inject_failure(
            "service_discovery", "service_unavailable", 2
        )

        await asyncio.sleep(2)
        await resilient_system.inject_failure(
            "consciousness_hub", "network_partition", 2
        )

        # Wait for load test to complete
        operations, errors = await load_task

        # Calculate success rate
        success_rate = (
            (operations / (operations + errors)) * 100 if operations + errors > 0 else 0
        )

        logger.info(
            f"Load test completed: {operations} ops, {errors} errors, {success_rate:.1f}% success"
        )

        # System should maintain reasonable success rate despite chaos
        assert success_rate > 60, f"Success rate {success_rate}% too low under chaos"

        # System should be healthy after chaos
        health = await resilient_system.health_check()
        assert health["status"] == "healthy"

    def generate_chaos_report(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Generate chaos engineering report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "scenarios_tested": len(test_results),
                "passed": sum(1 for r in test_results if r["passed"]),
                "failed": sum(1 for r in test_results if not r["passed"]),
                "recovery_rate": sum(
                    1 for r in test_results if r.get("recovered", False)
                )
                / len(test_results)
                * 100,
            },
            "resilience_metrics": {
                "mttr": self._calculate_mttr(test_results),  # Mean Time To Recovery
                "availability": self._calculate_availability(test_results),
                "failure_tolerance": self._calculate_failure_tolerance(test_results),
            },
            "recommendations": self._generate_chaos_recommendations(test_results),
            "test_results": test_results,
        }

    def _calculate_mttr(self, results: List[Dict]) -> float:
        """Calculate Mean Time To Recovery"""
        recovery_times = [r["recovery_time"] for r in results if "recovery_time" in r]
        return sum(recovery_times) / len(recovery_times) if recovery_times else 0

    def _calculate_availability(self, results: List[Dict]) -> float:
        """Calculate system availability during chaos"""
        total_time = sum(r.get("duration", 0) for r in results)
        downtime = sum(r.get("downtime", 0) for r in results)
        return ((total_time - downtime) / total_time * 100) if total_time > 0 else 0

    def _calculate_failure_tolerance(self, results: List[Dict]) -> str:
        """Assess failure tolerance level"""
        recovery_rate = sum(1 for r in results if r.get("recovered", False)) / len(
            results
        )

        if recovery_rate >= 0.95:
            return "Excellent"
        elif recovery_rate >= 0.80:
            return "Good"
        elif recovery_rate >= 0.60:
            return "Fair"
        else:
            return "Poor"

    def _generate_chaos_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate recommendations from chaos testing"""
        recommendations = []

        # Check recovery times
        slow_recoveries = [r for r in results if r.get("recovery_time", 0) > 10]
        if slow_recoveries:
            recommendations.append(
                f"Improve recovery time for {len(slow_recoveries)} scenarios"
            )

        # Check circuit breaker effectiveness
        circuit_breaker_issues = [
            r for r in results if r.get("circuit_breaker_failed", False)
        ]
        if circuit_breaker_issues:
            recommendations.append("Review circuit breaker thresholds and timing")

        # Check failover success
        failover_failures = [
            r
            for r in results
            if r.get("failover_attempted", False)
            and not r.get("failover_successful", False)
        ]
        if failover_failures:
            recommendations.append(
                "Improve failover mechanisms for critical components"
            )

        if not recommendations:
            recommendations.append("System shows good resilience to chaos scenarios")

        return recommendations


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
