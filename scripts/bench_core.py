#!/usr/bin/env python3
"""
T4/0.01% Performance Validation Framework
=========================================

Rigorous, statistically sound performance measurement with
tamper-evident proof generation.
"""

import json
import time
import statistics
import platform
import psutil
import hashlib
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np


@dataclass
class BenchmarkResult:
    """Structured benchmark result with statistical metadata"""
    name: str
    type: str  # 'unit' or 'e2e'
    samples: int
    warmup: int
    latencies_ns: List[int]
    p50_us: float
    p95_us: float
    p99_us: float
    mean_us: float
    stdev_us: float
    ci95_lower_us: float
    ci95_upper_us: float
    min_us: float
    max_us: float
    throughput_per_sec: float
    environment: Dict[str, Any]
    timestamp: str
    sha256: str = ""

    def calculate_sha(self) -> str:
        """Calculate SHA256 of result for tamper evidence"""
        data = json.dumps({
            'name': self.name,
            'samples': self.samples,
            'p95_us': self.p95_us,
            'latencies_hash': hashlib.sha256(
                str(self.latencies_ns).encode()
            ).hexdigest()[:16]
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class PerformanceBenchmark:
    """Rigorous performance benchmarking framework"""

    def __init__(self):
        self.results = []
        self.environment = self._capture_environment()

    def _capture_environment(self) -> Dict[str, Any]:
        """Capture runtime environment for reproducibility"""
        cpu_freq = psutil.cpu_freq()
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq_current': cpu_freq.current if cpu_freq else None,
            'cpu_freq_max': cpu_freq.max if cpu_freq else None,
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'pythonhashseed': os.environ.get('PYTHONHASHSEED', 'random'),
            'lukhas_mode': os.environ.get('LUKHAS_MODE', 'debug'),
            'timestamp': time.time(),
            'hostname': platform.node()
        }

    def percentile(self, data: List[float], p: float) -> float:
        """Calculate percentile with proper interpolation"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        n = len(sorted_data)
        idx = p * (n - 1)
        lower = int(idx)
        upper = min(lower + 1, n - 1)
        weight = idx - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight

    def bootstrap_ci(self, data: List[float], n_bootstrap: int = 1000,
                    confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for p95"""
        if len(data) < 10:
            return (min(data), max(data)) if data else (0.0, 0.0)

        p95_estimates = []
        n = len(data)

        for _ in range(n_bootstrap):
            # Resample with replacement
            resample = [data[np.random.randint(0, n)] for _ in range(n)]
            p95_estimates.append(self.percentile(resample, 0.95))

        # Calculate confidence interval
        alpha = 1 - confidence
        lower_percentile = alpha / 2
        upper_percentile = 1 - alpha / 2

        ci_lower = self.percentile(p95_estimates, lower_percentile)
        ci_upper = self.percentile(p95_estimates, upper_percentile)

        return ci_lower, ci_upper

    def benchmark_function(self, func, name: str, benchmark_type: str = 'unit',
                         warmup: int = 100, samples: int = 2000) -> BenchmarkResult:
        """Benchmark a function with statistical rigor"""
        print(f"🔬 Benchmarking {name} ({benchmark_type})...")

        # Warmup phase
        print(f"  Warming up ({warmup} iterations)...")
        for _ in range(warmup):
            func()

        # Collection phase
        print(f"  Collecting ({samples} samples)...")
        latencies_ns = []

        # Force GC before measurement
        import gc
        gc.collect()
        gc.disable()  # Disable GC during measurement

        try:
            for i in range(samples):
                if i % 500 == 0 and i > 0:
                    print(f"    Progress: {i}/{samples}")

                t0 = time.perf_counter_ns()
                func()
                t1 = time.perf_counter_ns()
                latencies_ns.append(t1 - t0)

        finally:
            gc.enable()  # Re-enable GC

        # Convert to microseconds
        latencies_us = [lat / 1000 for lat in latencies_ns]

        # Calculate statistics
        p50 = self.percentile(latencies_us, 0.50)
        p95 = self.percentile(latencies_us, 0.95)
        p99 = self.percentile(latencies_us, 0.99)
        mean = statistics.mean(latencies_us)
        stdev = statistics.stdev(latencies_us) if len(latencies_us) > 1 else 0.0
        ci_lower, ci_upper = self.bootstrap_ci(latencies_us)

        # Calculate throughput
        total_time_sec = sum(latencies_ns) / 1e9
        throughput = samples / total_time_sec if total_time_sec > 0 else 0

        result = BenchmarkResult(
            name=name,
            type=benchmark_type,
            samples=samples,
            warmup=warmup,
            latencies_ns=latencies_ns[:100],  # Store first 100 for reference
            p50_us=p50,
            p95_us=p95,
            p99_us=p99,
            mean_us=mean,
            stdev_us=stdev,
            ci95_lower_us=ci_lower,
            ci95_upper_us=ci_upper,
            min_us=min(latencies_us),
            max_us=max(latencies_us),
            throughput_per_sec=throughput,
            environment=self.environment,
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        )

        result.sha256 = result.calculate_sha()
        self.results.append(result)

        print(f"  ✅ Complete: p95={p95:.2f}μs [{ci_lower:.2f}-{ci_upper:.2f}] CI95%")

        return result

    def benchmark_throughput(self, func, name: str, duration_sec: int = 10) -> Dict[str, Any]:
        """Benchmark throughput with steady-state verification"""
        print(f"🚀 Throughput benchmark {name} ({duration_sec}s)...")

        operations = 0
        start_time = time.perf_counter()
        checkpoint_times = []
        checkpoint_ops = []

        # Collect checkpoints every second
        next_checkpoint = start_time + 1.0

        while time.perf_counter() - start_time < duration_sec:
            func()
            operations += 1

            current_time = time.perf_counter()
            if current_time >= next_checkpoint:
                elapsed = current_time - start_time
                checkpoint_times.append(elapsed)
                checkpoint_ops.append(operations)
                print(f"    {elapsed:.0f}s: {operations} ops ({operations/elapsed:.0f} ops/sec)")
                next_checkpoint += 1.0

        end_time = time.perf_counter()
        total_duration = end_time - start_time
        throughput = operations / total_duration

        # Calculate throughput variance (steady-state check)
        interval_throughputs = []
        for i in range(1, len(checkpoint_ops)):
            interval_ops = checkpoint_ops[i] - checkpoint_ops[i-1]
            interval_throughputs.append(interval_ops)  # ops per second

        throughput_stdev = statistics.stdev(interval_throughputs) if len(interval_throughputs) > 1 else 0
        throughput_cv = throughput_stdev / statistics.mean(interval_throughputs) if interval_throughputs else 0

        result = {
            'name': name,
            'type': 'throughput',
            'duration_sec': total_duration,
            'total_operations': operations,
            'throughput_ops_per_sec': throughput,
            'throughput_stdev': throughput_stdev,
            'throughput_cv': throughput_cv,  # Coefficient of variation (lower is more steady)
            'steady_state': throughput_cv < 0.1,  # <10% variation = steady
            'checkpoints': list(zip(checkpoint_times, checkpoint_ops)),
            'environment': self.environment,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

        print(f"  ✅ Complete: {throughput:.0f} ops/sec (CV={throughput_cv:.2%})")

        return result

    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        report = {
            'version': '1.0.0',
            'environment': self.environment,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'benchmarks': []
        }

        print("\n" + "="*80)
        print("📊 PERFORMANCE VALIDATION REPORT")
        print("="*80)

        # Separate unit and E2E results
        unit_results = [r for r in self.results if r.type == 'unit']
        e2e_results = [r for r in self.results if r.type == 'e2e']

        if unit_results:
            print("\n🔬 UNIT/MOCK BENCHMARKS (in-process, no IO)")
            print("-"*60)
            print(f"{'Component':<30} {'P50':<10} {'P95':<15} {'P99':<10} {'N':<8} {'Status'}")
            print("-"*60)

            for r in unit_results:
                ci_range = f"[{r.ci95_lower_us:.1f}-{r.ci95_upper_us:.1f}]"
                status = "✅" if r.p95_us < 100 else "⚠️"
                print(f"{r.name:<30} {r.p50_us:<10.2f} {r.p95_us:.2f} {ci_range:<15} {r.p99_us:<10.2f} {r.samples:<8} {status}")

                report['benchmarks'].append({
                    'name': r.name,
                    'type': r.type,
                    'metrics': asdict(r),
                    'sha256': r.sha256
                })

        if e2e_results:
            print("\n🌐 END-TO-END BENCHMARKS (real IO/network)")
            print("-"*60)
            print(f"{'Component':<30} {'P50':<10} {'P95 [CI95%]':<20} {'P99':<10} {'N':<8} {'Status'}")
            print("-"*60)

            for r in e2e_results:
                ci_range = f"{r.p95_us:.1f} [{r.ci95_lower_us:.1f}-{r.ci95_upper_us:.1f}]"
                status = self._get_sla_status(r.name, r.p95_us)
                print(f"{r.name:<30} {r.p50_us:<10.2f} {ci_range:<20} {r.p99_us:<10.2f} {r.samples:<8} {status}")

                report['benchmarks'].append({
                    'name': r.name,
                    'type': r.type,
                    'metrics': asdict(r),
                    'sha256': r.sha256
                })

        # Calculate report hash
        report['report_sha256'] = hashlib.sha256(
            json.dumps(report['benchmarks'], sort_keys=True).encode()
        ).hexdigest()

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Report saved to: {output_file}")

        print(f"\n🔒 Report SHA256: {report['report_sha256'][:16]}...")

        return report

    def _get_sla_status(self, name: str, p95_us: float) -> str:
        """Determine SLA compliance status"""
        sla_thresholds = {
            'guardian': 100000,  # 100ms
            'memory': 100,       # 100μs
            'orchestrator': 250000,  # 250ms
        }

        for key, threshold in sla_thresholds.items():
            if key in name.lower():
                return "✅" if p95_us < threshold else "❌"
        return "✅"

    def validate_sla(self, sla_requirements: Dict[str, float]) -> bool:
        """Validate results against SLA requirements"""
        print("\n⚖️  SLA VALIDATION")
        print("-"*60)

        all_pass = True

        for name, max_p95_us in sla_requirements.items():
            matching = [r for r in self.results if name in r.name.lower()]

            if not matching:
                print(f"⚠️  {name}: No results found")
                continue

            # Use E2E if available, otherwise unit
            e2e = [r for r in matching if r.type == 'e2e']
            result = e2e[0] if e2e else matching[0]

            passed = result.p95_us <= max_p95_us
            all_pass = all_pass and passed

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{name:<25} Required: <{max_p95_us:>8.1f}μs   "
                  f"Actual: {result.p95_us:>8.1f}μs   {status}")

        return all_pass


def main():
    """Example usage"""
    bench = PerformanceBenchmark()

    # Example: Benchmark a simple function
    def example_func():
        time.sleep(0.00001)  # Simulate 10μs operation

    # Run benchmark
    result = bench.benchmark_function(
        example_func,
        name="example_operation",
        benchmark_type="unit",
        warmup=50,
        samples=1000
    )

    # Generate report
    bench.generate_report("benchmark_results.json")

    # Validate SLAs
    sla_requirements = {
        "example": 100.0  # 100μs max
    }

    if bench.validate_sla(sla_requirements):
        print("\n✅ All SLAs passed!")
        return 0
    else:
        print("\n❌ Some SLAs failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())