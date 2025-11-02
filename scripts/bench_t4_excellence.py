#!/usr/bin/env python3
"""T4/0.01% Excellence Performance Validation Suite
================================================

Unassailable performance validation with complete statistical rigor,
chaos engineering, and tamper-evident proof generation.
"""

import hashlib
import json
import logging
import os
import pickle
import platform
import signal
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

import psutil

# Suppress verbose logging
logging.getLogger().setLevel(logging.CRITICAL)

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bench_core import (
    PerformanceBenchmark,  # - requires sys.path manipulation before import
)
from preflight_check import (
    PreflightValidator,  # - requires sys.path manipulation before import
)


class ChaosCleanupManager:
    """Idempotent chaos cleanup with signal trap handling"""

    def __init__(self):
        self.active_chaos = []
        self.cleanup_handlers = []
        self.original_handlers = {}
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful cleanup"""
        signals_to_handle = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, 'SIGHUP'):
            signals_to_handle.append(signal.SIGHUP)

        for sig in signals_to_handle:
            self.original_handlers[sig] = signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle signals by cleaning up chaos and exiting"""
        print(f"\n🛑 Received signal {signum}, cleaning up chaos...")
        self.cleanup_all()
        # Restore original handler and re-raise
        if signum in self.original_handlers:
            signal.signal(signum, self.original_handlers[signum])
        os.kill(os.getpid(), signum)

    def register_cleanup(self, cleanup_func, description: str = ""):
        """Register a cleanup function"""
        self.cleanup_handlers.append((cleanup_func, description))

    def cleanup_all(self):
        """Execute all cleanup handlers idempotently"""
        for cleanup_func, description in reversed(self.cleanup_handlers):
            try:
                if description:
                    print(f"  🧹 Cleaning up: {description}")
                cleanup_func()
            except Exception as e:
                print(f"  ⚠️  Cleanup failed for {description}: {e}")

        self.cleanup_handlers.clear()
        self.active_chaos.clear()

    def restore_signal_handlers(self):
        """Restore original signal handlers"""
        for sig, handler in self.original_handlers.items():
            signal.signal(sig, handler)


@contextmanager
def chaos_context(chaos_type: str, **kwargs):
    """Context manager for safe chaos engineering with automatic cleanup"""
    cleanup_mgr = ChaosCleanupManager()
    chaos_resources = {}

    try:
        print(f"🌪️  Starting {chaos_type} chaos...")

        if chaos_type == "cpu_spike":
            # CPU contention chaos
            stop_flag = threading.Event()
            threads = []

            def cpu_burner():
                while not stop_flag.is_set():
                    _ = sum(i**2 for i in range(1000))

            cpu_count = kwargs.get('cpu_count', psutil.cpu_count())
            for _ in range(cpu_count):
                t = threading.Thread(target=cpu_burner, daemon=True)
                t.start()
                threads.append(t)

            chaos_resources['threads'] = threads
            chaos_resources['stop_flag'] = stop_flag

            def cleanup_cpu():
                stop_flag.set()
                for t in threads:
                    t.join(timeout=1)
                print(f"    Stopped {len(threads)} CPU burner threads")

            cleanup_mgr.register_cleanup(cleanup_cpu, f"CPU spike ({len(threads)} threads)")

        elif chaos_type == "memory_pressure":
            # Memory pressure chaos
            memory_hogs = []
            block_size = kwargs.get('block_size_mb', 100) * 1024 * 1024
            num_blocks = kwargs.get('num_blocks', 10)

            for i in range(num_blocks):
                try:
                    block = bytearray(block_size)
                    memory_hogs.append(block)
                except MemoryError:
                    print(f"    Memory allocation failed at block {i}")
                    break

            chaos_resources['memory_hogs'] = memory_hogs

            def cleanup_memory():
                memory_hogs.clear()
                print(f"    Released {num_blocks} memory blocks ({block_size // (1024*1024)}MB each)")

            cleanup_mgr.register_cleanup(cleanup_memory, f"Memory pressure ({len(memory_hogs)} blocks)")

        elif chaos_type == "network_delay":
            # Network latency simulation (placeholder for future implementation)
            print("    Network delay chaos (simulated)")

            def cleanup_network():
                print("    Network delay cleanup (simulated)")

            cleanup_mgr.register_cleanup(cleanup_network, "Network delay")

        else:
            raise ValueError(f"Unknown chaos type: {chaos_type}")

        print(f"    ✅ {chaos_type} chaos active")
        yield chaos_resources

    except Exception as e:
        print(f"    ❌ Chaos setup failed: {e}")
        raise
    finally:
        cleanup_mgr.cleanup_all()
        cleanup_mgr.restore_signal_handlers()
        print(f"    🧹 {chaos_type} chaos cleaned up")


class E2EPromotionGate:
    """E2E-only promotion gates for SLA compliance validation"""

    # Define valid E2E metric patterns
    E2E_METRIC_PATTERNS = {
        'guardian_e2e', 'memory_e2e', 'orchestrator_e2e',
        'api_e2e', 'workflow_e2e', 'integration_e2e'
    }

    # Define forbidden unit test patterns
    UNIT_METRIC_PATTERNS = {
        'guardian_unit', 'memory_unit', 'orchestrator_unit',
        'api_unit', 'workflow_unit', 'integration_unit'
    }

    SLA_THRESHOLDS = {
        'guardian_e2e': 100000,    # 100ms in μs
        'memory_e2e': 1000,       # 1ms in μs
        'orchestrator_e2e': 250000, # 250ms in μs
        'api_e2e': 500000,        # 500ms in μs
        'workflow_e2e': 1000000,   # 1s in μs
        'integration_e2e': 2000000 # 2s in μs
    }

    def __init__(self):
        self.violations = []
        self.validations = []

    def validate_metric_eligibility(self, metric_name: str, distribution: 'PerformanceDistribution') -> bool:
        """Validate that metric is eligible for SLA evaluation"""
        is_e2e = any(pattern in metric_name.lower() for pattern in self.E2E_METRIC_PATTERNS)
        is_unit = any(pattern in metric_name.lower() for pattern in self.UNIT_METRIC_PATTERNS)

        validation = {
            'metric': metric_name,
            'is_e2e_eligible': is_e2e,
            'is_unit_test': is_unit,
            'samples': distribution.samples,
            'p95_us': distribution.p95,
            'status': 'unknown'
        }

        if is_unit:
            validation['status'] = 'REJECTED'
            validation['reason'] = 'Unit test metrics not allowed for SLA validation'
            self.violations.append(f"Metric '{metric_name}' rejected: Unit test metrics forbidden for SLA compliance")
            self.validations.append(validation)
            return False

        elif is_e2e:
            if distribution.samples < 1000:
                validation['status'] = 'REJECTED'
                validation['reason'] = f'Insufficient samples: {distribution.samples} < 1000'
                self.violations.append(f"Metric '{metric_name}' rejected: Insufficient E2E samples ({distribution.samples})")
                self.validations.append(validation)
                return False
            else:
                validation['status'] = 'ACCEPTED'
                validation['reason'] = f'Valid E2E metric with {distribution.samples} samples'
                self.validations.append(validation)
                return True

        else:
            validation['status'] = 'REJECTED'
            validation['reason'] = 'Metric name does not match E2E patterns'
            self.violations.append(f"Metric '{metric_name}' rejected: Not recognized as E2E metric")
            self.validations.append(validation)
            return False

    def validate_sla_compliance(self, results: Dict[str, 'PerformanceDistribution']) -> Dict[str, bool]:
        """Validate SLA compliance using only E2E metrics"""
        print("🚪 Running E2E-only promotion gate validation...")

        self.violations.clear()
        self.validations.clear()
        sla_compliance = {}

        # First, validate all metrics for eligibility
        eligible_metrics = {}
        for metric_name, distribution in results.items():
            if self.validate_metric_eligibility(metric_name, distribution):
                eligible_metrics[metric_name] = distribution
                print(f"  ✅ {metric_name}: Eligible for SLA validation ({distribution.samples} samples)")
            else:
                print(f"  ❌ {metric_name}: Rejected for SLA validation")

        # Then, check SLA compliance for eligible metrics
        for metric_name, distribution in eligible_metrics.items():
            if metric_name in self.SLA_THRESHOLDS:
                threshold = self.SLA_THRESHOLDS[metric_name]
                compliant = distribution.p95 < threshold
                sla_compliance[metric_name] = compliant

                margin = ((threshold - distribution.p95) / threshold) * 100 if compliant else 0
                status = "✅ PASS" if compliant else "❌ FAIL"

                print(f"  {status} {metric_name}: {distribution.p95:.2f}μs < {threshold}μs "
                      f"({margin:.1f}% margin)" if compliant else
                      f"({distribution.p95 - threshold:.2f}μs over)")

            else:
                print(f"  ⚠️  {metric_name}: No SLA threshold defined")

        # Report violations
        if self.violations:
            print(f"\n🚨 E2E Promotion Gate Violations ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  • {violation}")

        # Summary
        total_eligible = len(eligible_metrics)
        total_checked = len(sla_compliance)
        passed_sla = sum(sla_compliance.values())

        print("\n📊 E2E Promotion Gate Summary:")
        print(f"  • Metrics evaluated: {len(results)}")
        print(f"  • E2E eligible: {total_eligible}")
        print(f"  • SLA thresholds defined: {total_checked}")
        print(f"  • SLA compliance passed: {passed_sla}/{total_checked}")

        if len(self.violations) == 0 and passed_sla == total_checked and total_checked > 0:
            print("  🎉 All E2E promotion gates passed!")
        else:
            print("  ❌ Promotion gate failures detected")

        return sla_compliance

    def generate_promotion_report(self) -> Dict[str, Any]:
        """Generate detailed promotion gate report"""
        return {
            'gate_type': 'e2e_only',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'validations': self.validations,
            'violations': self.violations,
            'sla_thresholds': self.SLA_THRESHOLDS,
            'summary': {
                'total_validations': len(self.validations),
                'accepted_metrics': len([v for v in self.validations if v['status'] == 'ACCEPTED']),
                'rejected_metrics': len([v for v in self.validations if v['status'] == 'REJECTED']),
                'violation_count': len(self.violations)
            }
        }


class PowerThermalTelemetry:
    """Power and thermal telemetry capture for detecting throttling"""

    def __init__(self):
        self.baseline_readings = {}
        self.benchmark_readings = []
        self.throttling_detected = False
        self.frequency_variance = 0.0

    def capture_baseline(self):
        """Capture baseline power/thermal readings"""
        print("⚡ Capturing baseline power/thermal telemetry...")

        reading = self._take_reading("baseline")
        self.baseline_readings = reading

        print(f"  📊 Baseline CPU frequency: {reading.get('cpu_freq_mhz', 'N/A')} MHz")
        print(f"  🌡️  Baseline CPU temperature: {reading.get('cpu_temp_c', 'N/A')}°C")

    def _take_reading(self, label: str = "") -> Dict[str, Any]:
        """Take a comprehensive power/thermal reading"""
        reading = {
            'timestamp': time.time(),
            'label': label
        }

        try:
            # CPU frequency readings
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                reading['cpu_freq_mhz'] = cpu_freq.current
                reading['cpu_freq_min'] = cpu_freq.min
                reading['cpu_freq_max'] = cpu_freq.max
            else:
                reading['cpu_freq_mhz'] = None

            # Per-core frequency (Linux only)
            if platform.system() == "Linux":
                try:
                    per_core_freq = psutil.cpu_freq(percpu=True)
                    if per_core_freq:
                        freqs = [f.current for f in per_core_freq if f.current]
                        if freqs:
                            reading['cpu_freq_per_core'] = freqs
                            reading['cpu_freq_variance'] = max(freqs) - min(freqs)
                except Exception as e:
                    logger.debug(f"Expected optional failure: {e}")
                    pass

            # CPU temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    cpu_temps = []
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            for entry in entries:
                                if entry.current:
                                    cpu_temps.append(entry.current)

                    if cpu_temps:
                        reading['cpu_temp_c'] = sum(cpu_temps) / len(cpu_temps)
                        reading['cpu_temp_max'] = max(cpu_temps)
                        reading['cpu_temp_cores'] = cpu_temps
            except Exception:
                reading['cpu_temp_c'] = None

            # Power consumption (Linux only)
            if platform.system() == "Linux":
                try:
                    # Try to read power consumption from /sys/class/power_supply/
                    power_paths = [
                        "/sys/class/power_supply/BAT0/power_now",
                        "/sys/class/power_supply/BAT1/power_now"
                    ]

                    for path in power_paths:
                        if Path(path).exists():
                            with open(path) as f:
                                power_uw = int(f.read().strip())
                                reading['battery_power_w'] = power_uw / 1000000  # Convert μW to W
                            break
                except Exception as e:
                    logger.debug(f"Expected optional failure: {e}")
                    pass

            # CPU load averages
            load_avg = psutil.getloadavg()
            reading['load_1min'] = load_avg[0]
            reading['load_5min'] = load_avg[1]
            reading['load_15min'] = load_avg[2]

            # Memory pressure
            memory = psutil.virtual_memory()
            reading['memory_percent'] = memory.percent
            reading['memory_available_gb'] = memory.available / (1024**3)

        except Exception as e:
            reading['error'] = str(e)

        return reading

    def monitor_during_benchmark(self, interval_seconds: float = 0.5):
        """Start monitoring power/thermal during benchmark"""
        self.benchmark_readings = []
        self.monitoring = True

        def monitor_thread():
            while getattr(self, 'monitoring', False):
                reading = self._take_reading("benchmark")
                self.benchmark_readings.append(reading)
                time.sleep(interval_seconds)

        import threading
        self.monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring and analyze results"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)

        self._analyze_readings()

    def _analyze_readings(self):
        """Analyze readings for throttling and frequency scaling"""
        if not self.benchmark_readings:
            return

        print("⚡ Analyzing power/thermal telemetry...")

        # Analyze frequency stability
        freqs = [r.get('cpu_freq_mhz') for r in self.benchmark_readings if r.get('cpu_freq_mhz')]
        if freqs and len(freqs) > 1:
            freq_mean = sum(freqs) / len(freqs)
            freq_variance = sum((f - freq_mean) ** 2 for f in freqs) / len(freqs)
            freq_coefficient_of_variation = (freq_variance ** 0.5) / freq_mean * 100

            self.frequency_variance = freq_coefficient_of_variation

            if freq_coefficient_of_variation > 5:  # More than 5% CV indicates instability
                self.throttling_detected = True
                print(f"  🚨 CPU frequency instability detected: {freq_coefficient_of_variation:.1f}% CV")
            else:
                print(f"  ✅ CPU frequency stable: {freq_coefficient_of_variation:.1f}% CV")

            print(f"  📊 Frequency range: {min(freqs):.0f} - {max(freqs):.0f} MHz (mean: {freq_mean:.0f})")

        # Analyze temperature stability
        temps = [r.get('cpu_temp_c') for r in self.benchmark_readings if r.get('cpu_temp_c')]
        if temps and len(temps) > 1:
            temp_mean = sum(temps) / len(temps)
            temp_max = max(temps)
            temp_range = max(temps) - min(temps)

            if temp_max > 85:  # High temperature threshold
                self.throttling_detected = True
                print(f"  🌡️  High CPU temperature detected: {temp_max:.1f}°C max")
            elif temp_range > 10:  # Large temperature swings
                print(f"  ⚠️  CPU temperature variation: {temp_range:.1f}°C range")
            else:
                print(f"  ✅ CPU temperature stable: {temp_mean:.1f}°C ± {temp_range:.1f}°C")

        # Analyze load stability
        loads = [r.get('load_1min') for r in self.benchmark_readings if r.get('load_1min')]
        if loads:
            load_mean = sum(loads) / len(loads)
            load_max = max(loads)
            cpu_count = psutil.cpu_count()

            if load_max > cpu_count * 0.8:  # High load threshold
                print(f"  ⚠️  High system load detected: {load_max:.2f} (>{cpu_count * 0.8:.1f})")
            else:
                print(f"  ✅ System load acceptable: {load_mean:.2f} average")

    def generate_telemetry_report(self) -> Dict[str, Any]:
        """Generate comprehensive telemetry report"""
        report = {
            'telemetry_version': '1.0.0',
            'capture_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'baseline': self.baseline_readings,
            'benchmark_samples': len(self.benchmark_readings),
            'analysis': {
                'throttling_detected': self.throttling_detected,
                'frequency_variance_percent': self.frequency_variance,
                'monitoring_duration_seconds': 0
            }
        }

        if self.benchmark_readings:
            first_reading = min(r['timestamp'] for r in self.benchmark_readings)
            last_reading = max(r['timestamp'] for r in self.benchmark_readings)
            report['analysis']['monitoring_duration_seconds'] = last_reading - first_reading

            # Add statistical summaries
            freqs = [r.get('cpu_freq_mhz') for r in self.benchmark_readings if r.get('cpu_freq_mhz')]
            if freqs:
                report['analysis']['frequency_stats'] = {
                    'min_mhz': min(freqs),
                    'max_mhz': max(freqs),
                    'mean_mhz': sum(freqs) / len(freqs),
                    'samples': len(freqs)
                }

            temps = [r.get('cpu_temp_c') for r in self.benchmark_readings if r.get('cpu_temp_c')]
            if temps:
                report['analysis']['temperature_stats'] = {
                    'min_c': min(temps),
                    'max_c': max(temps),
                    'mean_c': sum(temps) / len(temps),
                    'samples': len(temps)
                }

        report['raw_readings'] = self.benchmark_readings[:100]  # Limit to first 100 readings

        return report

    @contextmanager
    def monitor_benchmark(self, name: str = "benchmark"):
        """Context manager for monitoring a benchmark"""
        print(f"⚡ Starting power/thermal monitoring for: {name}")
        self.capture_baseline()

        try:
            self.monitor_during_benchmark()
            yield self
        finally:
            self.stop_monitoring()

            if self.throttling_detected:
                print("  ⚠️  Performance may be affected by power/thermal constraints")
            else:
                print("  ✅ No significant power/thermal issues detected")


class SLOBurnRateDrill:
    """SLO burn-rate drill for testing monitoring and alerting"""

    def __init__(self):
        self.drill_results = {}
        self.synthetic_latencies = []
        self.slo_violations = []

    def generate_synthetic_traffic(self, target_function, baseline_latency: float,
                                 duration_seconds: int = 30,
                                 requests_per_second: int = 100) -> Dict[str, Any]:
        """Generate synthetic traffic to test SLO burn-rate monitoring"""
        print("🚀 Starting SLO burn-rate drill...")
        print(f"  📊 Target: {requests_per_second} RPS for {duration_seconds}s")
        print(f"  🎯 Baseline latency: {baseline_latency:.2f}μs")

        self.synthetic_latencies = []
        self.slo_violations = []
        start_time = time.time()
        request_interval = 1.0 / requests_per_second

        # Define SLO thresholds based on baseline
        slo_thresholds = {
            'p50_threshold': baseline_latency * 2,   # 2x baseline for p50
            'p95_threshold': baseline_latency * 5,   # 5x baseline for p95
            'p99_threshold': baseline_latency * 10   # 10x baseline for p99
        }

        print(f"  📏 SLO thresholds: p50<{slo_thresholds['p50_threshold']:.1f}μs, "
              f"p95<{slo_thresholds['p95_threshold']:.1f}μs, p99<{slo_thresholds['p99_threshold']:.1f}μs")

        total_requests = duration_seconds * requests_per_second
        violation_windows = []
        current_window = []
        window_size = requests_per_second  # 1-second windows

        try:
            for request_id in range(total_requests):
                request_start = time.time()

                # Execute request
                t0 = time.perf_counter_ns()
                target_function()
                t1 = time.perf_counter_ns()
                latency_us = (t1 - t0) / 1000

                self.synthetic_latencies.append({
                    'request_id': request_id,
                    'timestamp': request_start,
                    'latency_us': latency_us,
                    'elapsed_seconds': request_start - start_time
                })

                current_window.append(latency_us)

                # Process window when full
                if len(current_window) >= window_size:
                    window_violations = self._analyze_window(current_window, slo_thresholds, request_id)
                    if window_violations:
                        violation_windows.append({
                            'window_start_request': request_id - window_size + 1,
                            'window_end_request': request_id,
                            'violations': window_violations
                        })

                    current_window = []

                # Progress reporting
                if request_id % (requests_per_second * 5) == 0 and request_id > 0:
                    elapsed = time.time() - start_time
                    progress = (request_id / total_requests) * 100
                    print(f"    📈 Progress: {progress:.1f}% ({request_id}/{total_requests} requests, {elapsed:.1f}s)")

                # Rate limiting
                elapsed = time.time() - request_start
                sleep_time = max(0, request_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("    ⚠️  Drill interrupted by user")

        # Analyze final window
        if current_window:
            window_violations = self._analyze_window(current_window, slo_thresholds, len(self.synthetic_latencies))
            if window_violations:
                violation_windows.append({
                    'window_start_request': len(self.synthetic_latencies) - len(current_window),
                    'window_end_request': len(self.synthetic_latencies) - 1,
                    'violations': window_violations
                })

        # Calculate overall statistics
        all_latencies = [r['latency_us'] for r in self.synthetic_latencies]
        if all_latencies:
            result = self._calculate_drill_results(all_latencies, slo_thresholds, violation_windows, duration_seconds)
        else:
            result = {'error': 'No requests completed'}

        return result

    def _analyze_window(self, window_latencies: List[float], slo_thresholds: Dict[str, float],
                       request_id: int) -> List[Dict[str, Any]]:
        """Analyze a window of latencies for SLO violations"""
        violations = []

        if len(window_latencies) < 10:  # Need minimum samples
            return violations

        sorted_latencies = sorted(window_latencies)
        n = len(sorted_latencies)

        # Calculate percentiles
        p50 = sorted_latencies[int(n * 0.5)]
        p95 = sorted_latencies[int(n * 0.95)]
        p99 = sorted_latencies[int(n * 0.99)]

        # Check for violations
        if p50 > slo_thresholds['p50_threshold']:
            violations.append({
                'type': 'p50_violation',
                'actual': p50,
                'threshold': slo_thresholds['p50_threshold'],
                'severity': 'high'
            })

        if p95 > slo_thresholds['p95_threshold']:
            violations.append({
                'type': 'p95_violation',
                'actual': p95,
                'threshold': slo_thresholds['p95_threshold'],
                'severity': 'critical'
            })

        if p99 > slo_thresholds['p99_threshold']:
            violations.append({
                'type': 'p99_violation',
                'actual': p99,
                'threshold': slo_thresholds['p99_threshold'],
                'severity': 'critical'
            })

        return violations

    def _calculate_drill_results(self, all_latencies: List[float], slo_thresholds: Dict[str, float],
                               violation_windows: List[Dict], duration_seconds: int) -> Dict[str, Any]:
        """Calculate comprehensive drill results"""
        if not all_latencies:
            return {'error': 'No latency data'}

        sorted_latencies = sorted(all_latencies)
        n = len(sorted_latencies)

        # Overall statistics
        stats = {
            'total_requests': n,
            'duration_seconds': duration_seconds,
            'average_rps': n / duration_seconds if duration_seconds > 0 else 0,
            'p50_us': sorted_latencies[int(n * 0.5)],
            'p95_us': sorted_latencies[int(n * 0.95)],
            'p99_us': sorted_latencies[int(n * 0.99)],
            'min_us': min(sorted_latencies),
            'max_us': max(sorted_latencies),
            'mean_us': sum(sorted_latencies) / n
        }

        # SLO compliance
        slo_compliance = {
            'p50_compliant': stats['p50_us'] <= slo_thresholds['p50_threshold'],
            'p95_compliant': stats['p95_us'] <= slo_thresholds['p95_threshold'],
            'p99_compliant': stats['p99_us'] <= slo_thresholds['p99_threshold']
        }

        # Violation analysis
        violation_summary = {
            'total_violation_windows': len(violation_windows),
            'violation_types': {},
            'max_violation_severity': 'none'
        }

        for window in violation_windows:
            for violation in window['violations']:
                vtype = violation['type']
                violation_summary['violation_types'][vtype] = violation_summary['violation_types'].get(vtype, 0) + 1

                if violation['severity'] == 'critical':
                    violation_summary['max_violation_severity'] = 'critical'
                elif violation['severity'] == 'high' and violation_summary['max_violation_severity'] == 'none':
                    violation_summary['max_violation_severity'] = 'high'

        # Burn rate calculation
        burn_rate = self._calculate_burn_rate(violation_windows, duration_seconds)

        result = {
            'drill_type': 'slo_burn_rate',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'statistics': stats,
            'slo_thresholds': slo_thresholds,
            'slo_compliance': slo_compliance,
            'violations': violation_summary,
            'burn_rate': burn_rate,
            'violation_windows': violation_windows[:10],  # Keep first 10 windows
            'overall_status': 'PASS' if all(slo_compliance.values()) else 'FAIL'
        }

        return result

    def _calculate_burn_rate(self, violation_windows: List[Dict], duration_seconds: int) -> Dict[str, Any]:
        """Calculate SLO burn rate metrics"""
        if duration_seconds <= 0:
            return {'error': 'Invalid duration'}

        # Calculate violation percentage
        violation_time = len(violation_windows)  # Each window is ~1 second
        violation_percentage = (violation_time / duration_seconds) * 100

        # Define burn rate thresholds
        burn_rate_thresholds = {
            'low': 1,      # 1% violation rate
            'medium': 5,   # 5% violation rate
            'high': 10,    # 10% violation rate
            'critical': 25 # 25% violation rate
        }

        # Determine severity
        if violation_percentage >= burn_rate_thresholds['critical']:
            severity = 'critical'
        elif violation_percentage >= burn_rate_thresholds['high']:
            severity = 'high'
        elif violation_percentage >= burn_rate_thresholds['medium']:
            severity = 'medium'
        elif violation_percentage >= burn_rate_thresholds['low']:
            severity = 'low'
        else:
            severity = 'none'

        return {
            'violation_percentage': violation_percentage,
            'violation_windows_count': len(violation_windows),
            'total_windows': duration_seconds,
            'severity': severity,
            'thresholds': burn_rate_thresholds
        }

    def run_comprehensive_drill(self, target_function, baseline_latency: float) -> Dict[str, Any]:
        """Run comprehensive SLO burn-rate drill with multiple scenarios"""
        print("🎯 Running comprehensive SLO burn-rate drill...")

        scenarios = [
            {'name': 'normal_load', 'rps': 50, 'duration': 20},
            {'name': 'high_load', 'rps': 200, 'duration': 15},
            {'name': 'burst_load', 'rps': 500, 'duration': 10}
        ]

        drill_results = {}

        for scenario in scenarios:
            print(f"\n📊 Scenario: {scenario['name']}")

            try:
                result = self.generate_synthetic_traffic(
                    target_function,
                    baseline_latency,
                    duration_seconds=scenario['duration'],
                    requests_per_second=scenario['rps']
                )
                drill_results[scenario['name']] = result

                # Print scenario summary
                if 'statistics' in result:
                    stats = result['statistics']
                    compliance = result['slo_compliance']
                    burn_rate = result['burn_rate']

                    print(f"    📈 Results: {stats['total_requests']} requests, "
                          f"p95={stats['p95_us']:.1f}μs")
                    print(f"    🎯 SLO compliance: "
                          f"p50={'✅' if compliance['p50_compliant'] else '❌'} "
                          f"p95={'✅' if compliance['p95_compliant'] else '❌'} "
                          f"p99={'✅' if compliance['p99_compliant'] else '❌'}")
                    print(f"    🔥 Burn rate: {burn_rate['violation_percentage']:.1f}% ({burn_rate['severity']})")

            except Exception as e:
                print(f"    ❌ Scenario failed: {e}")
                drill_results[scenario['name']] = {'error': str(e)}

        # Overall assessment
        passed_scenarios = sum(1 for r in drill_results.values()
                             if r.get('overall_status') == 'PASS')
        total_scenarios = len(scenarios)

        print(f"\n🎉 Drill Summary: {passed_scenarios}/{total_scenarios} scenarios passed")

        return {
            'comprehensive_drill': True,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'scenarios': drill_results,
            'summary': {
                'total_scenarios': total_scenarios,
                'passed_scenarios': passed_scenarios,
                'overall_success': passed_scenarios == total_scenarios
            }
        }


@dataclass
class PerformanceDistribution:
    """Complete performance distribution with all percentiles"""
    name: str
    samples: int
    p25: float
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float
    p999: float
    mean: float
    stdev: float
    cv: float  # Coefficient of variation
    min: float
    max: float
    iqr: float  # Interquartile range
    mad: float  # Median absolute deviation
    histogram: List[Tuple[float, int]] = field(default_factory=list)
    raw_samples: List[float] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Complete validation result with proof"""
    timestamp: str
    environment: Dict[str, Any]
    distributions: Dict[str, PerformanceDistribution]
    sla_compliance: Dict[str, bool]
    chaos_results: Dict[str, Any]
    reproducibility: Dict[str, float]
    telemetry_report: Dict[str, Any]
    merkle_root: str
    previous_hash: str
    evidence_hash: str


class T4ExcellenceValidator:
    """Unassailable T4/0.01% performance validator"""

    def __init__(self):
        self.bench = PerformanceBenchmark()
        self.results = {}
        self.chaos_results = {}
        self.telemetry = PowerThermalTelemetry()
        self.merkle_chain = []
        self.artifacts_dir = Path("artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)

    def capture_full_environment(self) -> Dict[str, Any]:
        """Capture complete environment for reproducibility"""
        cpu_info = psutil.cpu_freq()
        mem_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        # Capture Python dependencies
        deps = {}
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'freeze'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if '==' in line:
                    name, version = line.split('==')
                    deps[name] = version
        except Exception:
            deps = {"error": "Could not capture dependencies"}

        return {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python": platform.python_version(),
                "python_compiler": platform.python_compiler(),
            },
            "hardware": {
                "cpu_count": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_freq_current": cpu_info.current if cpu_info else None,
                "cpu_freq_min": cpu_info.min if cpu_info else None,
                "cpu_freq_max": cpu_info.max if cpu_info else None,
                "memory_total_gb": mem_info.total / (1024**3),
                "memory_available_gb": mem_info.available / (1024**3),
                "disk_total_gb": disk_info.total / (1024**3),
                "disk_free_gb": disk_info.free / (1024**3),
            },
            "environment": {
                "pythonhashseed": os.environ.get('PYTHONHASHSEED', 'not_set'),
                "lukhas_mode": os.environ.get('LUKHAS_MODE', 'not_set'),
                "pythondontwritebytecode": os.environ.get('PYTHONDONTWRITEBYTECODE', 'not_set'),
                "path": os.environ.get('PATH', '').split(':')[:3],  # First 3 paths only
            },
            "dependencies": deps,
            "process": {
                "pid": os.getpid(),
                "nice": os.nice(0),
                "cwd": os.getcwd(),
            }
        }

    def calculate_distribution(self, samples: List[float], name: str) -> PerformanceDistribution:
        """Calculate complete distribution statistics"""
        if not samples:
            return PerformanceDistribution(
                name=name, samples=0, p25=0, p50=0, p75=0, p90=0,
                p95=0, p99=0, p999=0, mean=0, stdev=0, cv=0,
                min=0, max=0, iqr=0, mad=0
            )

        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        def percentile(p):
            idx = p * (n - 1)
            lower = int(idx)
            upper = min(lower + 1, n - 1)
            weight = idx - lower
            return sorted_samples[lower] * (1 - weight) + sorted_samples[upper] * weight

        p25 = percentile(0.25)
        p50 = percentile(0.50)
        p75 = percentile(0.75)
        p90 = percentile(0.90)
        p95 = percentile(0.95)
        p99 = percentile(0.99)
        p999 = percentile(0.999)

        mean = statistics.mean(samples)
        stdev = statistics.stdev(samples) if n > 1 else 0
        cv = (stdev / mean * 100) if mean > 0 else 0

        # Calculate MAD (Median Absolute Deviation)
        deviations = [abs(x - p50) for x in samples]
        mad = percentile(0.50) if deviations else 0

        # Create histogram (10 bins)
        hist_bins = 10
        hist_min = min(samples)
        hist_max = max(samples)
        bin_width = (hist_max - hist_min) / hist_bins if hist_max > hist_min else 1

        histogram = []
        for i in range(hist_bins):
            bin_start = hist_min + i * bin_width
            bin_end = hist_min + (i + 1) * bin_width
            count = sum(1 for s in samples if bin_start <= s < bin_end)
            histogram.append((bin_start, count))

        return PerformanceDistribution(
            name=name,
            samples=n,
            p25=p25, p50=p50, p75=p75,
            p90=p90, p95=p95, p99=p99, p999=p999,
            mean=mean, stdev=stdev, cv=cv,
            min=min(samples), max=max(samples),
            iqr=p75 - p25,
            mad=mad,
            histogram=histogram,
            raw_samples=sorted_samples[:100]  # Keep first 100 for verification
        )

    def run_benchmark_with_distribution(self, func, name: str,
                                       warmup: int = 100,
                                       samples: int = 5000) -> PerformanceDistribution:
        """Run benchmark and return full distribution with telemetry monitoring"""
        print(f"🔬 Benchmarking {name}...")

        # Start telemetry monitoring for this benchmark
        with self.telemetry.monitor_benchmark(name):
            # Warmup
            for _ in range(warmup):
                func()

            # Collection
            latencies_us = []
            for i in range(samples):
                if i % 1000 == 0 and i > 0:
                    print(f"    Progress: {i}/{samples}")

                t0 = time.perf_counter_ns()
                func()
                t1 = time.perf_counter_ns()
                latencies_us.append((t1 - t0) / 1000)  # Convert to microseconds

        dist = self.calculate_distribution(latencies_us, name)
        print(f"    ✅ p50={dist.p50:.2f}μs, p95={dist.p95:.2f}μs, p99={dist.p99:.2f}μs (CV={dist.cv:.1f}%)")

        # Check for telemetry warnings
        if self.telemetry.throttling_detected:
            print("    ⚠️  Power/thermal constraints detected - results may be affected")

        self.results[name] = dist
        return dist

    def run_chaos_test(self, func, name: str, chaos_type: str = "cpu_spike") -> Dict[str, Any]:
        """Run benchmark under chaos conditions with idempotent cleanup"""
        print(f"🌪️  Chaos test: {name} with {chaos_type}")

        baseline_samples = []
        chaos_samples = []

        # Baseline (no chaos)
        print("    📊 Collecting baseline samples...")
        for _ in range(100):
            t0 = time.perf_counter_ns()
            func()
            t1 = time.perf_counter_ns()
            baseline_samples.append((t1 - t0) / 1000)

        # Run under chaos with automatic cleanup
        print("    🌪️  Applying chaos conditions...")
        try:
            with chaos_context(chaos_type):
                # Allow chaos to stabilize
                time.sleep(0.1)

                # Collect samples under chaos
                for i in range(100):
                    if i % 25 == 0:
                        print(f"      Progress: {i}/100 chaos samples")

                    t0 = time.perf_counter_ns()
                    func()
                    t1 = time.perf_counter_ns()
                    chaos_samples.append((t1 - t0) / 1000)

        except Exception as e:
            print(f"    ❌ Chaos test failed: {e}")
            # Return a failed result
            return {
                "chaos_type": chaos_type,
                "baseline_p95": 0,
                "chaos_p95": 0,
                "degradation_pct": float('inf'),
                "resilient": False,
                "error": str(e)
            }

        # Calculate results
        baseline_p95 = sorted(baseline_samples)[int(len(baseline_samples) * 0.95)]
        chaos_p95 = sorted(chaos_samples)[int(len(chaos_samples) * 0.95)]
        degradation = ((chaos_p95 - baseline_p95) / baseline_p95) * 100 if baseline_p95 > 0 else 0

        result = {
            "chaos_type": chaos_type,
            "baseline_p95": baseline_p95,
            "chaos_p95": chaos_p95,
            "degradation_pct": degradation,
            "resilient": degradation < 50,  # Less than 50% degradation = resilient
            "samples": {
                "baseline": len(baseline_samples),
                "chaos": len(chaos_samples)
            }
        }

        print("    📈 Results:")
        print(f"      Baseline p95: {baseline_p95:.2f}μs")
        print(f"      Chaos p95: {chaos_p95:.2f}μs")
        print(f"      Degradation: {degradation:.1f}%")
        print(f"      Resilient: {'✅ Yes' if result['resilient'] else '❌ No'}")

        self.chaos_results[name] = result
        return result

    def test_reproducibility(self, func, name: str, runs: int = 5) -> Dict[str, float]:
        """Test reproducibility across multiple runs"""
        print(f"🔄 Testing reproducibility: {name} ({runs} runs)")

        run_results = []
        for run in range(runs):
            samples = []
            for _ in range(100):
                t0 = time.perf_counter_ns()
                func()
                t1 = time.perf_counter_ns()
                samples.append((t1 - t0) / 1000)

            p95 = sorted(samples)[int(len(samples) * 0.95)]
            run_results.append(p95)
            print(f"    Run {run+1}: p95={p95:.2f}μs")

        mean_p95 = statistics.mean(run_results)
        stdev_p95 = statistics.stdev(run_results) if len(run_results) > 1 else 0
        cv_p95 = (stdev_p95 / mean_p95 * 100) if mean_p95 > 0 else 0

        # Calculate how many runs are within ±5% of mean
        within_5pct = sum(1 for r in run_results if abs(r - mean_p95) / mean_p95 <= 0.05)
        reproducibility_rate = (within_5pct / runs) * 100

        result = {
            "runs": runs,
            "mean_p95": mean_p95,
            "stdev_p95": stdev_p95,
            "cv_pct": cv_p95,
            "reproducibility_rate": reproducibility_rate,
            "all_results": run_results
        }

        print(f"    Mean p95: {mean_p95:.2f}μs (CV={cv_p95:.1f}%)")
        print(f"    Reproducibility: {reproducibility_rate:.0f}% within ±5% of mean")

        return result

    def generate_merkle_proof(self) -> str:
        """Generate Merkle tree proof for tamper evidence"""
        # Get previous hash or genesis
        previous_hash = self.merkle_chain[-1] if self.merkle_chain else "genesis"

        # Serialize current results
        data = {
            "timestamp": time.time(),
            "results": {k: asdict(v) for k, v in self.results.items()},
            "chaos": self.chaos_results,
            "previous": previous_hash
        }

        # Calculate hash
        data_str = json.dumps(data, sort_keys=True)
        current_hash = hashlib.sha256(data_str.encode()).hexdigest()

        # Add to chain
        self.merkle_chain.append(current_hash)

        return current_hash

    def generate_comprehensive_report(self) -> ValidationResult:
        """Generate comprehensive validation report"""
        env = self.capture_full_environment()

        # Use E2E-only promotion gate for SLA compliance validation
        promotion_gate = E2EPromotionGate()
        sla_compliance = promotion_gate.validate_sla_compliance(self.results)

        # Save promotion gate report
        promotion_report = promotion_gate.generate_promotion_report()
        promotion_report_path = self.artifacts_dir / f"promotion_gate_{int(time.time())}.json"
        with open(promotion_report_path, 'w') as f:
            json.dump(promotion_report, f, indent=2)

        # Generate and save telemetry report
        telemetry_report = self.telemetry.generate_telemetry_report()
        telemetry_report_path = self.artifacts_dir / f"telemetry_{int(time.time())}.json"
        with open(telemetry_report_path, 'w') as f:
            json.dump(telemetry_report, f, indent=2)

        merkle_root = self.generate_merkle_proof()

        result = ValidationResult(
            timestamp=env["timestamp"],
            environment=env,
            distributions=dict(self.results.items()),
            sla_compliance=sla_compliance,
            chaos_results=self.chaos_results,
            reproducibility={},
            telemetry_report=telemetry_report,
            merkle_root=merkle_root,
            previous_hash=self.merkle_chain[-2] if len(self.merkle_chain) > 1 else "genesis",
            evidence_hash=""
        )

        # Calculate evidence hash
        evidence_str = json.dumps(asdict(result), sort_keys=True, default=str)
        result.evidence_hash = hashlib.sha256(evidence_str.encode()).hexdigest()

        return result

    def save_artifacts(self, result: ValidationResult):
        """Save all artifacts for audit trail"""
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())

        # Save JSON report
        report_path = self.artifacts_dir / f"t4_validation_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)

        # Save raw distributions (pickle for complete data)
        dist_path = self.artifacts_dir / f"distributions_{timestamp}.pkl"
        with open(dist_path, 'wb') as f:
            pickle.dump(self.results, f)

        # Save merkle chain
        merkle_path = self.artifacts_dir / f"merkle_chain_{timestamp}.json"
        with open(merkle_path, 'w') as f:
            json.dump({
                "chain": self.merkle_chain,
                "current_root": result.merkle_root,
                "evidence_hash": result.evidence_hash
            }, f, indent=2)

        print("\n📁 Artifacts saved:")
        print(f"  • Report: {report_path}")
        print(f"  • Distributions: {dist_path}")
        print(f"  • Merkle chain: {merkle_path}")
        print(f"  🔒 Evidence hash: {result.evidence_hash[:16]}...")


def run_t4_excellence_validation():
    """Run complete T4/0.01% excellence validation"""
    print("="*80)
    print("🚀 T4/0.01% EXCELLENCE VALIDATION - UNASSAILABLE PROOF")
    print("="*80)

    validator = T4ExcellenceValidator()

    # Import components
    from governance.guardian_system import GuardianSystem
    from memory.memory_event import MemoryEventFactory

    guardian = GuardianSystem()
    memory_factory = MemoryEventFactory()

    # 1. BASELINE BENCHMARKS
    print("\n📊 BASELINE PERFORMANCE MEASUREMENTS")
    print("-"*60)

    # Guardian tests
    validator.run_benchmark_with_distribution(
        lambda: guardian.validate_safety({"test": "data"}),
        "guardian_unit", warmup=500, samples=10000
    )

    temp_dir = tempfile.mkdtemp()
    def guardian_e2e():
        response = guardian.validate_safety({"test": "data"})
        log_file = Path(temp_dir) / f"log_{time.time_ns()}.json"
        with open(log_file, 'w') as f:
            json.dump(response, f)
        with open(log_file) as f:
            verified = json.load(f)
        log_file.unlink()
        return verified

    validator.run_benchmark_with_distribution(
        guardian_e2e, "guardian_e2e", warmup=100, samples=2000
    )

    # Memory tests
    validator.run_benchmark_with_distribution(
        lambda: memory_factory.create({"test": "data"}, {"affect_delta": 0.5}),
        "memory_unit", warmup=500, samples=10000
    )

    def memory_e2e():
        event = memory_factory.create({"test": "data"}, {"affect_delta": 0.5})
        event_file = Path(temp_dir) / f"event_{time.time_ns()}.json"
        with open(event_file, 'w') as f:
            json.dump({"data": event.data, "metadata": event.metadata}, f)
        with open(event_file) as f:
            verified = json.load(f)
        event_file.unlink()
        return verified

    validator.run_benchmark_with_distribution(
        memory_e2e, "memory_e2e", warmup=100, samples=2000
    )

    # 2. CHAOS ENGINEERING
    print("\n🌪️  CHAOS ENGINEERING TESTS")
    print("-"*60)

    validator.run_chaos_test(
        lambda: guardian.validate_safety({"test": "data"}),
        "guardian_chaos_cpu", chaos_type="cpu_spike"
    )

    validator.run_chaos_test(
        lambda: memory_factory.create({"test": "data"}, {"affect_delta": 0.5}),
        "memory_chaos_memory", chaos_type="memory_pressure"
    )

    # 3. REPRODUCIBILITY TESTS
    print("\n🔄 REPRODUCIBILITY VALIDATION")
    print("-"*60)

    repro_guardian = validator.test_reproducibility(
        lambda: guardian.validate_safety({"test": "data"}),
        "guardian_reproducibility", runs=5
    )

    repro_memory = validator.test_reproducibility(
        lambda: memory_factory.create({"test": "data"}, {"affect_delta": 0.5}),
        "memory_reproducibility", runs=5
    )

    # 4. GENERATE REPORT
    print("\n📝 GENERATING VALIDATION REPORT")
    print("-"*60)

    result = validator.generate_comprehensive_report()
    result.reproducibility = {
        "guardian": repro_guardian,
        "memory": repro_memory
    }

    # 5. SAVE ARTIFACTS
    validator.save_artifacts(result)

    # 6. FINAL VALIDATION SUMMARY
    print("\n"+"="*80)
    print("📊 T4/0.01% EXCELLENCE VALIDATION SUMMARY")
    print("="*80)

    print("\n🎯 Performance Distributions (all percentiles in μs):")
    print("-"*80)
    print(f"{'Component':<20} {'p50':<10} {'p95':<10} {'p99':<10} {'p99.9':<10} {'CV%':<8} {'Status'}")
    print("-"*80)

    for name, dist in validator.results.items():
        if "e2e" in name:
            status = "✅" if any(name.startswith(k) and v
                                for k, v in result.sla_compliance.items()) else "❌"
            print(f"{name:<20} {dist.p50:<10.2f} {dist.p95:<10.2f} "
                  f"{dist.p99:<10.2f} {dist.p999:<10.2f} {dist.cv:<8.1f} {status}")

    print("\n🌪️  Chaos Resilience:")
    for name, chaos in validator.chaos_results.items():
        print(f"  {name}: {'✅ Resilient' if chaos['resilient'] else '❌ Not resilient'} "
              f"(degradation: {chaos['degradation_pct']:.1f}%)")

    print("\n🔄 Reproducibility:")
    print(f"  Guardian: {repro_guardian['reproducibility_rate']:.0f}% within ±5%")
    print(f"  Memory: {repro_memory['reproducibility_rate']:.0f}% within ±5%")

    print("\n🔒 Tamper Evidence:")
    print(f"  Merkle root: {result.merkle_root[:16]}...")
    print(f"  Evidence hash: {result.evidence_hash[:16]}...")
    print(f"  Chain length: {len(validator.merkle_chain)} blocks")

    # Check overall pass
    all_sla_pass = all(result.sla_compliance.values())
    chaos_resilient = all(c['resilient'] for c in validator.chaos_results.values())
    reproducible = (repro_guardian['reproducibility_rate'] >= 80 and
                   repro_memory['reproducibility_rate'] >= 80)

    print("\n"+"="*80)
    if all_sla_pass and chaos_resilient and reproducible:
        print("🏆 T4/0.01% EXCELLENCE: VALIDATED WITH UNASSAILABLE PROOF ✅")
    else:
        print("⚠️  T4/0.01% EXCELLENCE: PARTIAL (see failures above)")
    print("="*80)

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    return 0 if (all_sla_pass and chaos_resilient and reproducible) else 1


def main():
    """Main entry point"""
    # Set environment for maximum reproducibility
    os.environ['PYTHONHASHSEED'] = '0'
    os.environ['LUKHAS_MODE'] = 'release'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    try:
        # Run preflight validation gate first
        audit_run_id = os.getenv("AUDIT_RUN_ID", f"excellence_{int(time.time())}")
        os.environ['AUDIT_RUN_ID'] = audit_run_id

        print("🔍 Running T4/0.01% Excellence Preflight Validation...")
        validator = PreflightValidator(audit_run_id)
        preflight_passed = validator.run_all_validations()

        # Generate preflight report
        preflight_path = Path("artifacts") / f"preflight_{audit_run_id}.json"
        validator.generate_report(preflight_path)

        if not preflight_passed:
            print(f"\n❌ Preflight validation failed ({len(validator.violations)} violations)")
            print("   Environment not ready for T4/0.01% excellence audit")
            return 3

        print("\n✅ Preflight validation passed - proceeding with performance audit")
        return run_t4_excellence_validation()
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
