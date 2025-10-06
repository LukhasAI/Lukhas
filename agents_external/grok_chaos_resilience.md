---
status: wip
type: documentation
---
# Grok — Chaos Engineering & Resilience Matrix

## Primary Task
Implement comprehensive chaos engineering with resilience validation:
- Guardian failure simulation with fail-closed behavior validation
- Network partition and infrastructure fault injection
- Memory corruption and resource exhaustion testing
- Recovery validation with SLO compliance during chaos scenarios

**Output**: artifacts/{component}_chaos_resilience_validation.json

## Specific Instructions

### Chaos Controller Implementation
```python
import asyncio
import psutil
import signal
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum

class ChaosScenario(Enum):
    GUARDIAN_PROCESS_CRASH = "guardian_process_crash"
    NETWORK_PARTITION = "network_partition"
    MEMORY_CORRUPTION = "memory_corruption"
    CPU_EXHAUSTION = "cpu_exhaustion"
    DISK_FULL = "disk_full"
    CLOCK_SKEW = "clock_skew"
    DNS_FAILURE = "dns_failure"
    DATABASE_TIMEOUT = "database_timeout"

class MATRIZChaosController:
    def __init__(self):
        self.active_scenarios = set()
        self.fail_closed_active = False
        self.chaos_metrics = {}
        self.recovery_callbacks = []

    async def execute_chaos_scenario(self, scenario: ChaosScenario,
                                   duration_seconds: int = 30) -> Dict[str, Any]:
        """Execute a specific chaos scenario with monitoring."""
        scenario_start = time.time()
        recovery_data = {'successful': False, 'time_to_recovery_ms': None}

        try:
            # Mark scenario as active
            self.active_scenarios.add(scenario)

            # Execute scenario-specific chaos
            chaos_result = await self._execute_scenario(scenario)

            # Monitor system behavior during chaos
            monitoring_task = asyncio.create_task(
                self._monitor_chaos_impact(scenario, duration_seconds)
            )

            # Wait for scenario duration
            await asyncio.sleep(duration_seconds)

            # Initiate recovery
            recovery_start = time.time()
            await self._initiate_recovery(scenario)

            # Wait for monitoring to complete
            monitoring_result = await monitoring_task

            # Validate recovery
            recovery_validation = await self._validate_recovery(scenario)
            recovery_time = (time.time() - recovery_start) * 1000

            recovery_data = {
                'successful': recovery_validation['recovered'],
                'time_to_recovery_ms': recovery_time
            }

            return {
                'scenario': scenario.value,
                'duration_seconds': duration_seconds,
                'chaos_injected': chaos_result['successful'],
                'system_impact': monitoring_result,
                'recovery': recovery_data,
                'fail_closed_triggered': self.fail_closed_active,
                'total_duration_ms': (time.time() - scenario_start) * 1000
            }

        finally:
            # Ensure cleanup
            self.active_scenarios.discard(scenario)
            await self._cleanup_scenario(scenario)

    async def _execute_scenario(self, scenario: ChaosScenario) -> Dict[str, Any]:
        """Execute the specific chaos injection."""
        if scenario == ChaosScenario.GUARDIAN_PROCESS_CRASH:
            return await self._crash_guardian_process()
        elif scenario == ChaosScenario.NETWORK_PARTITION:
            return await self._simulate_network_partition()
        elif scenario == ChaosScenario.MEMORY_CORRUPTION:
            return await self._corrupt_memory()
        elif scenario == ChaosScenario.CPU_EXHAUSTION:
            return await self._exhaust_cpu()
        elif scenario == ChaosScenario.DISK_FULL:
            return await self._fill_disk()
        elif scenario == ChaosScenario.CLOCK_SKEW:
            return await self._simulate_clock_skew()
        else:
            return {'successful': False, 'error': f'Unknown scenario: {scenario}'}

    async def _crash_guardian_process(self) -> Dict[str, Any]:
        """Simulate Guardian process crash."""
        # Find Guardian process (mock implementation)
        guardian_pid = self._find_guardian_process()

        if guardian_pid:
            try:
                # Send SIGKILL to Guardian process
                os.kill(guardian_pid, signal.SIGKILL)

                # Verify fail-closed activation
                await asyncio.sleep(1)  # Allow time for fail-closed detection
                self._activate_fail_closed("guardian_process_crashed")

                return {
                    'successful': True,
                    'guardian_pid': guardian_pid,
                    'fail_closed_activated': self.fail_closed_active
                }
            except ProcessLookupError:
                return {'successful': False, 'error': 'Guardian process not found'}
        else:
            return {'successful': False, 'error': 'Guardian process not running'}

    async def _simulate_network_partition(self) -> Dict[str, Any]:
        """Simulate network partition using iptables."""
        try:
            # Block outgoing connections to dependency services (mock)
            partition_commands = [
                "iptables -A OUTPUT -d 127.0.0.1 -p tcp --dport 5432 -j DROP",  # PostgreSQL
                "iptables -A OUTPUT -d 127.0.0.1 -p tcp --dport 6379 -j DROP",  # Redis
            ]

            for cmd in partition_commands:
                # In real implementation, would execute these commands
                # subprocess.run(cmd.split(), check=True)
                pass

            # Activate fail-closed due to dependency unavailability
            self._activate_fail_closed("network_partition")

            return {
                'successful': True,
                'partition_rules': len(partition_commands),
                'affected_services': ['postgresql', 'redis']
            }
        except Exception as e:
            return {'successful': False, 'error': str(e)}

    async def _corrupt_memory(self) -> Dict[str, Any]:
        """Simulate memory corruption by exhausting available memory."""
        try:
            # Allocate large amounts of memory rapidly
            memory_hogs = []
            target_mb = 500  # Allocate 500MB

            for _ in range(50):
                # Allocate 10MB chunks
                memory_chunk = bytearray(10 * 1024 * 1024)
                memory_hogs.append(memory_chunk)
                await asyncio.sleep(0.1)  # Brief pause between allocations

            # Monitor memory pressure
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > 85:
                self._activate_fail_closed("memory_exhaustion")

            # Store reference to prevent garbage collection
            self._memory_corruption_refs = memory_hogs

            return {
                'successful': True,
                'allocated_mb': target_mb,
                'memory_usage_percent': memory_usage
            }
        except MemoryError:
            self._activate_fail_closed("memory_exhaustion")
            return {
                'successful': True,
                'memory_exhausted': True,
                'fail_closed_triggered': True
            }

    async def _monitor_chaos_impact(self, scenario: ChaosScenario,
                                  duration: int) -> Dict[str, Any]:
        """Monitor system behavior during chaos scenario."""
        metrics = {
            'latency_samples': [],
            'error_rate_samples': [],
            'throughput_samples': [],
            'cpu_usage_samples': [],
            'memory_usage_samples': []
        }

        start_time = time.time()
        sample_interval = 0.5  # Sample every 500ms

        while time.time() - start_time < duration:
            # Collect performance metrics
            current_time = time.time()

            # Mock metric collection - in real implementation would query actual metrics
            latency = self._measure_current_latency()
            error_rate = self._measure_current_error_rate()
            throughput = self._measure_current_throughput()

            # System resource metrics
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_usage = psutil.virtual_memory().percent

            metrics['latency_samples'].append({
                'timestamp': current_time,
                'value': latency
            })
            metrics['error_rate_samples'].append({
                'timestamp': current_time,
                'value': error_rate
            })
            metrics['cpu_usage_samples'].append({
                'timestamp': current_time,
                'value': cpu_usage
            })
            metrics['memory_usage_samples'].append({
                'timestamp': current_time,
                'value': memory_usage
            })

            await asyncio.sleep(sample_interval)

        # Calculate impact statistics
        return self._calculate_chaos_impact(metrics)

    def _calculate_chaos_impact(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Calculate the impact of chaos on system performance."""
        impact_analysis = {}

        for metric_name, samples in metrics.items():
            if not samples:
                continue

            values = [s['value'] for s in samples if s['value'] is not None]
            if values:
                impact_analysis[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'samples': len(values)
                }

        # Determine overall system health
        avg_error_rate = impact_analysis.get('error_rate_samples', {}).get('avg', 0)
        avg_latency = impact_analysis.get('latency_samples', {}).get('avg', 0)

        system_health = 'healthy'
        if avg_error_rate > 0.05 or avg_latency > 500:  # 5% error rate or 500ms latency
            system_health = 'degraded'
        if avg_error_rate > 0.20 or avg_latency > 1000:  # 20% error rate or 1s latency
            system_health = 'critical'

        impact_analysis['overall_health'] = system_health
        return impact_analysis

    def _activate_fail_closed(self, reason: str):
        """Activate fail-closed mode."""
        self.fail_closed_active = True
        self.chaos_metrics['fail_closed_reason'] = reason
        self.chaos_metrics['fail_closed_activated_at'] = time.time()

        # In real implementation, would trigger actual fail-closed mechanisms
        # - Stop accepting new requests
        # - Return cached/default responses
        # - Alert operations team

    async def _validate_recovery(self, scenario: ChaosScenario) -> Dict[str, Any]:
        """Validate that the system has recovered from chaos scenario."""
        recovery_checks = {
            'service_responding': await self._check_service_health(),
            'error_rate_normal': await self._check_error_rate(),
            'latency_within_slo': await self._check_latency_slo(),
            'dependencies_available': await self._check_dependencies()
        }

        all_checks_passed = all(recovery_checks.values())

        return {
            'recovered': all_checks_passed,
            'recovery_checks': recovery_checks,
            'fail_closed_deactivated': not self.fail_closed_active
        }

    async def _check_service_health(self) -> bool:
        """Check if the service is responding to health checks."""
        # Mock health check - in real implementation would ping actual health endpoint
        try:
            await asyncio.sleep(0.1)  # Simulate network call
            return True
        except:
            return False

    def _measure_current_latency(self) -> Optional[float]:
        """Measure current request latency."""
        # Mock implementation - would measure actual request latency
        if self.fail_closed_active:
            return 50.0  # Fail-closed responses are fast
        else:
            return 100.0 + (50.0 if self.active_scenarios else 0.0)

    def _measure_current_error_rate(self) -> Optional[float]:
        """Measure current error rate."""
        # Mock implementation
        if self.fail_closed_active:
            return 0.0  # Fail-closed prevents errors
        else:
            return 0.01 + (0.10 if self.active_scenarios else 0.0)
```

### Resilience Validation Framework
```python
class ResilienceValidator:
    def __init__(self):
        self.slo_targets = {
            'max_error_rate_during_chaos': 0.05,  # 5%
            'max_latency_during_chaos_ms': 500,   # 500ms
            'recovery_time_max_ms': 30000,       # 30 seconds
            'fail_closed_activation_max_ms': 1000  # 1 second
        }

    def validate_chaos_resilience(self, chaos_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate system resilience across multiple chaos scenarios."""
        validation_results = {
            'scenarios_tested': len(chaos_results),
            'scenarios_passed': 0,
            'overall_resilient': True,
            'scenario_results': [],
            'resilience_score': 0.0
        }

        total_score = 0.0
        max_score = len(chaos_results) * 100

        for result in chaos_results:
            scenario_validation = self._validate_scenario_resilience(result)
            validation_results['scenario_results'].append(scenario_validation)

            if scenario_validation['passed']:
                validation_results['scenarios_passed'] += 1
            else:
                validation_results['overall_resilient'] = False

            total_score += scenario_validation['score']

        validation_results['resilience_score'] = (total_score / max_score) * 100 if max_score > 0 else 0

        return validation_results

    def _validate_scenario_resilience(self, chaos_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resilience for a single chaos scenario."""
        validations = []
        score = 100.0

        # Check fail-closed activation
        if chaos_result.get('fail_closed_triggered', False):
            validations.append({
                'check': 'fail_closed_triggered',
                'passed': True,
                'message': 'Fail-closed correctly activated'
            })
        else:
            validations.append({
                'check': 'fail_closed_triggered',
                'passed': False,
                'message': 'Fail-closed was not activated during chaos'
            })
            score -= 30

        # Check recovery success
        recovery_successful = chaos_result.get('recovery', {}).get('successful', False)
        if recovery_successful:
            validations.append({
                'check': 'recovery_successful',
                'passed': True,
                'message': 'System successfully recovered'
            })
        else:
            validations.append({
                'check': 'recovery_successful',
                'passed': False,
                'message': 'System failed to recover properly'
            })
            score -= 40

        # Check recovery time
        recovery_time = chaos_result.get('recovery', {}).get('time_to_recovery_ms', float('inf'))
        recovery_within_slo = recovery_time <= self.slo_targets['recovery_time_max_ms']
        if recovery_within_slo:
            validations.append({
                'check': 'recovery_time_slo',
                'passed': True,
                'message': f'Recovery time {recovery_time}ms within SLO'
            })
        else:
            validations.append({
                'check': 'recovery_time_slo',
                'passed': False,
                'message': f'Recovery time {recovery_time}ms exceeds SLO'
            })
            score -= 20

        # Check error rate during chaos
        system_impact = chaos_result.get('system_impact', {})
        error_rate = system_impact.get('error_rate_samples', {}).get('avg', 0)
        error_rate_ok = error_rate <= self.slo_targets['max_error_rate_during_chaos']
        if error_rate_ok:
            validations.append({
                'check': 'error_rate_during_chaos',
                'passed': True,
                'message': f'Error rate {error_rate:.3f} within tolerance'
            })
        else:
            validations.append({
                'check': 'error_rate_during_chaos',
                'passed': False,
                'message': f'Error rate {error_rate:.3f} exceeded tolerance'
            })
            score -= 10

        all_passed = all(v['passed'] for v in validations)

        return {
            'scenario': chaos_result.get('scenario', 'unknown'),
            'passed': all_passed,
            'score': max(0, score),
            'validations': validations
        }
```

### Performance Requirements
- Chaos injection: <1000ms setup time
- Monitoring collection: <100ms per sample
- Recovery validation: <500ms per check
- Resilience analysis: <250ms per scenario

### Testing Framework
```python
@pytest.mark.chaos
@pytest.mark.lane("integration")
async def test_guardian_crash_resilience():
    chaos_controller = MATRIZChaosController()

    result = await chaos_controller.execute_chaos_scenario(
        ChaosScenario.GUARDIAN_PROCESS_CRASH,
        duration_seconds=10
    )

    assert result['chaos_injected'] is True
    assert result['fail_closed_triggered'] is True
    assert result['recovery']['successful'] is True
    assert result['recovery']['time_to_recovery_ms'] < 30000

@pytest.mark.chaos
@pytest.mark.lane("integration")
async def test_network_partition_resilience():
    chaos_controller = MATRIZChaosController()

    result = await chaos_controller.execute_chaos_scenario(
        ChaosScenario.NETWORK_PARTITION,
        duration_seconds=15
    )

    assert result['fail_closed_triggered'] is True
    assert result['system_impact']['overall_health'] in ['healthy', 'degraded']

@pytest.mark.chaos
@pytest.mark.lane("integration")
def test_resilience_validation():
    validator = ResilienceValidator()

    mock_chaos_results = [
        {
            'scenario': 'guardian_process_crash',
            'fail_closed_triggered': True,
            'recovery': {'successful': True, 'time_to_recovery_ms': 25000},
            'system_impact': {'error_rate_samples': {'avg': 0.02}}
        }
    ]

    validation = validator.validate_chaos_resilience(mock_chaos_results)

    assert validation['overall_resilient'] is True
    assert validation['resilience_score'] > 90.0
```

### Evidence Generation
Create validation artifact with structure:
```json
{
  "component": "chaos_resilience_validation",
  "validation_timestamp": "ISO8601",
  "chaos_scenarios": {
    "scenarios_executed": 8,
    "guardian_crash_validated": true,
    "network_partition_validated": true,
    "memory_corruption_validated": true,
    "infrastructure_faults_validated": true
  },
  "fail_closed_behavior": {
    "activation_time_ms": 850,
    "triggers_validated": 8,
    "behavior_correct": true
  },
  "recovery_validation": {
    "recovery_time_p95_ms": 28500,
    "success_rate": 1.0,
    "slo_compliance": true
  },
  "resilience_metrics": {
    "overall_score": 95.5,
    "chaos_tolerance": "excellent",
    "production_ready": true
  }
}
```