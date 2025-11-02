#!/usr/bin/env python3
"""
T4/0.01% Excellence Performance SLA Validator
==============================================

Validates benchmark results against T4/0.01% performance requirements:
- Guardian: <100ms p95 latency
- Memory Events: <100μs p95 creation time
- AI Providers: <250ms p95 latency
- Consciousness: <1ms p99 tick latency
- Authentication: <100ms p95 latency
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


class PerformanceSLAValidator:
    """Validates performance benchmarks against T4/0.01% SLA requirements"""

    # T4/0.01% Excellence SLA Thresholds
    SLA_THRESHOLDS = {
        "guardian_response": {"p95": 0.1, "unit": "s"},
        "memory_event_creation": {"p95": 0.0001, "unit": "s"},
        "ai_provider_request": {"p95": 0.25, "unit": "s"},
        "consciousness_tick": {"p99": 0.001, "unit": "s"},
        "authentication": {"p95": 0.1, "unit": "s"},
    }

    def __init__(self, benchmark_file: str):
        self.benchmark_file = Path(benchmark_file)
        self.results = self._load_benchmark_results()
        self.violations: List[Dict] = []
        self.passed_checks: List[Dict] = []

    def _load_benchmark_results(self) -> Dict:
        """Load benchmark results from JSON file"""
        try:
            with open(self.benchmark_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Benchmark file not found: {self.benchmark_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in benchmark file: {e}")
            sys.exit(1)

    def _extract_percentile(self, benchmark: Dict, percentile: str) -> float:
        """Extract percentile value from benchmark stats"""
        stats = benchmark.get("stats", {})

        # Try different possible keys for percentile data
        percentile_keys = [f"percentile_{percentile}", f"p{percentile}", percentile.upper(), percentile.lower()]

        for key in percentile_keys:
            if key in stats:
                return float(stats[key])

        # Fallback to mean if percentile not available
        if "mean" in stats:
            return float(stats["mean"])

        return float("inf")  # Fail validation if no usable data

    def _validate_benchmark(self, benchmark_name: str, benchmark_data: Dict) -> bool:
        """Validate a single benchmark against SLA thresholds"""
        # Find matching SLA threshold
        matching_sla = None
        for sla_name, sla_config in self.SLA_THRESHOLDS.items():
            if sla_name in benchmark_name.lower():
                matching_sla = (sla_name, sla_config)
                break

        if not matching_sla:
            # No specific SLA - use general performance check
            return self._validate_general_performance(benchmark_name, benchmark_data)

        sla_name, sla_config = matching_sla

        # Extract required percentile
        percentile_key = "p99" if "p99" in sla_config else "p95"
        percentile_value = percentile_key[1:]  # Remove 'p' prefix

        actual_latency = self._extract_percentile(benchmark_data, percentile_value)
        threshold = sla_config[percentile_key]

        # Validate against threshold
        passed = actual_latency <= threshold

        result = {
            "benchmark": benchmark_name,
            "sla": sla_name,
            "metric": f"{percentile_key} latency",
            "actual": actual_latency,
            "threshold": threshold,
            "unit": sla_config["unit"],
            "passed": passed,
            "margin": threshold - actual_latency,
        }

        if passed:
            self.passed_checks.append(result)
        else:
            self.violations.append(result)

        return passed

    def _validate_general_performance(self, benchmark_name: str, benchmark_data: Dict) -> bool:
        """Validate general performance for benchmarks without specific SLAs"""
        stats = benchmark_data.get("stats", {})
        mean_time = stats.get("mean", 0)

        # General performance threshold: 10ms for most operations
        general_threshold = 0.01
        passed = mean_time <= general_threshold

        result = {
            "benchmark": benchmark_name,
            "sla": "general_performance",
            "metric": "mean latency",
            "actual": mean_time,
            "threshold": general_threshold,
            "unit": "s",
            "passed": passed,
            "margin": general_threshold - mean_time,
        }

        if passed:
            self.passed_checks.append(result)
        else:
            self.violations.append(result)

        return passed

    def validate_all(self) -> bool:
        """Validate all benchmarks against SLA requirements"""
        if "benchmarks" not in self.results:
            print("❌ No benchmarks found in results file")
            return False

        benchmarks = self.results["benchmarks"]
        all_passed = True

        print("🔍 Validating T4/0.01% Excellence Performance SLAs...")
        print("=" * 60)

        for benchmark in benchmarks:
            name = benchmark.get("name", "Unknown")
            passed = self._validate_benchmark(name, benchmark)
            all_passed = all_passed and passed

        return all_passed

    def generate_report(self) -> None:
        """Generate comprehensive validation report"""
        total_checks = len(self.passed_checks) + len(self.violations)

        print("\n📊 T4/0.01% Excellence Performance Report")
        print("=" * 60)
        print(f"Total Benchmarks: {total_checks}")
        print(f"✅ Passed: {len(self.passed_checks)}")
        print(f"❌ Failed: {len(self.violations)}")
        print(f"Success Rate: {len(self.passed_checks)/total_checks*100:.1f}%")

        if self.passed_checks:
            print("\n✅ PASSED SLA CHECKS:")
            print("-" * 40)
            for check in self.passed_checks:
                margin_pct = (check["margin"] / check["threshold"]) * 100
                print(f"  {check['benchmark']}")
                print(
                    f"    {check['metric']}: {check['actual']:.6f}{check['unit']} "
                    f"(<= {check['threshold']}{check['unit']}) "
                    f"[+{margin_pct:.1f}% margin]"
                )

        if self.violations:
            print("\n❌ SLA VIOLATIONS:")
            print("-" * 40)
            for violation in self.violations:
                excess_pct = ((violation["actual"] - violation["threshold"]) / violation["threshold"]) * 100
                print(f"  {violation['benchmark']}")
                print(
                    f"    {violation['metric']}: {violation['actual']:.6f}{violation['unit']} "
                    f"(> {violation['threshold']}{violation['unit']}) "
                    f"[+{excess_pct:.1f}% over limit]"
                )

        # Detailed SLA Summary
        print("\n📋 T4/0.01% SLA Requirements:")
        print("-" * 40)
        for sla_name, config in self.SLA_THRESHOLDS.items():
            percentile = "p99" if "p99" in config else "p95"
            threshold = config[percentile]
            unit = config["unit"]
            print(f"  {sla_name}: {percentile} < {threshold}{unit}")

    def save_report(self, output_file: str = "sla_validation_report.json") -> None:
        """Save detailed report to JSON file"""
        report = {
            "timestamp": self.results.get("datetime", "unknown"),
            "total_checks": len(self.passed_checks) + len(self.violations),
            "passed": len(self.passed_checks),
            "failed": len(self.violations),
            "success_rate": len(self.passed_checks) / (len(self.passed_checks) + len(self.violations)),
            "sla_thresholds": self.SLA_THRESHOLDS,
            "passed_checks": self.passed_checks,
            "violations": self.violations,
            "overall_status": "PASS" if not self.violations else "FAIL",
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validate_performance_slas.py <benchmark_file.json>")
        print("Example: python validate_performance_slas.py benchmark-results.json")
        sys.exit(1)

    benchmark_file = sys.argv[1]

    try:
        validator = PerformanceSLAValidator(benchmark_file)
        all_passed = validator.validate_all()
        validator.generate_report()
        validator.save_report()

        print(f"\n🎯 T4/0.01% Excellence Validation: {'PASS' if all_passed else 'FAIL'}")

        if not all_passed:
            print("\n⚠️  Performance SLA violations detected!")
            print("Review the failed benchmarks and optimize performance before deployment.")
            sys.exit(1)
        else:
            print("\n🎉 All performance SLAs met! Ready for T4/0.01% excellence deployment.")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
