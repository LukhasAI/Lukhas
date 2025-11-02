#!/usr/bin/env python3
"""
T4/0.01% Excellence Statistical Testing Framework

Implements rigorous statistical analysis for performance validation including:
- Mann-Whitney U tests for distribution comparison
- Bootstrap confidence intervals
- Kolmogorov-Smirnov tests
- Effect size calculations
- Statistical significance validation
"""

import argparse
import json
import warnings
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import scipy.stats as stats

warnings.filterwarnings("ignore")


class StatisticalAnalyzer:
    """Comprehensive statistical analysis for audit validation."""

    def __init__(self, alpha: float = 0.01):
        """Initialize with significance level."""
        self.alpha = alpha
        self.confidence_level = 1 - alpha

    def load_audit_data(self, file_path: str) -> Dict[str, Any]:
        """Load audit data from JSON file."""
        with open(file_path, "r") as f:
            return json.load(f)

    def extract_latencies(self, audit_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Extract latency measurements from audit data."""
        return {
            "guardian": audit_data.get("guardian_latency_us", []),
            "memory": audit_data.get("memory_latency_us", []),
            "orchestrator": audit_data.get("orchestrator_latency_us", []),
            "creativity": audit_data.get("creativity_latency_us", []),
        }

    def mann_whitney_test(self, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        """Perform Mann-Whitney U test for distribution comparison."""
        if len(sample1) < 3 or len(sample2) < 3:
            return {
                "statistic": None,
                "p_value": None,
                "significant": False,
                "effect_size": None,
                "interpretation": "Insufficient data",
            }

        # Perform Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(sample1, sample2, alternative="two-sided")

        # Calculate effect size (Cliff's delta)
        effect_size = self._calculate_cliffs_delta(sample1, sample2)

        # Determine significance
        significant = p_value < self.alpha

        # Interpret effect size
        if abs(effect_size) < 0.147:
            effect_interpretation = "negligible"
        elif abs(effect_size) < 0.33:
            effect_interpretation = "small"
        elif abs(effect_size) < 0.474:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"

        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": significant,
            "effect_size": float(effect_size),
            "effect_interpretation": effect_interpretation,
            "interpretation": self._interpret_mann_whitney(p_value, effect_size),
        }

    def _calculate_cliffs_delta(self, sample1: List[float], sample2: List[float]) -> float:
        """Calculate Cliff's delta effect size."""
        n1, n2 = len(sample1), len(sample2)
        if n1 == 0 or n2 == 0:
            return 0.0

        # Count comparisons
        greater_count = 0
        total_comparisons = n1 * n2

        for x1 in sample1:
            for x2 in sample2:
                if x1 > x2:
                    greater_count += 1
                elif x1 < x2:
                    greater_count -= 1

        return greater_count / total_comparisons

    def _interpret_mann_whitney(self, p_value: float, effect_size: float) -> str:
        """Interpret Mann-Whitney test results."""
        if p_value >= self.alpha:
            return "Distributions are statistically identical (cannot reject null hypothesis)"
        else:
            direction = "first sample larger" if effect_size > 0 else "second sample larger"
            return f"Statistically significant difference detected ({direction})"

    def kolmogorov_smirnov_test(self, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        """Perform Kolmogorov-Smirnov test for distribution comparison."""
        if len(sample1) < 3 or len(sample2) < 3:
            return {"statistic": None, "p_value": None, "significant": False, "interpretation": "Insufficient data"}

        # Perform KS test
        statistic, p_value = stats.ks_2samp(sample1, sample2)

        significant = p_value < self.alpha

        interpretation = (
            "Distributions are statistically identical"
            if not significant
            else "Distributions are significantly different"
        )

        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": significant,
            "interpretation": interpretation,
        }

    def bootstrap_confidence_interval(
        self, sample: List[float], statistic_func=np.mean, n_bootstrap: int = 1000, confidence_level: float = None
    ) -> Dict[str, Any]:
        """Calculate bootstrap confidence interval."""
        if confidence_level is None:
            confidence_level = self.confidence_level

        if len(sample) < 3:
            return {
                "lower": None,
                "upper": None,
                "point_estimate": None,
                "confidence_level": confidence_level,
                "interpretation": "Insufficient data",
            }

        sample_array = np.array(sample)
        point_estimate = statistic_func(sample_array)

        # Generate bootstrap samples
        bootstrap_stats = []
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(sample_array, size=len(sample_array), replace=True)
            bootstrap_stats.append(statistic_func(bootstrap_sample))

        # Calculate confidence interval
        alpha_level = 1 - confidence_level
        lower_percentile = (alpha_level / 2) * 100
        upper_percentile = (1 - alpha_level / 2) * 100

        lower_bound = np.percentile(bootstrap_stats, lower_percentile)
        upper_bound = np.percentile(bootstrap_stats, upper_percentile)

        return {
            "lower": float(lower_bound),
            "upper": float(upper_bound),
            "point_estimate": float(point_estimate),
            "confidence_level": confidence_level,
            "bootstrap_samples": n_bootstrap,
            "interpretation": f"{confidence_level*100:.0f}% confidence interval for population parameter",
        }

    def normality_tests(self, sample: List[float]) -> Dict[str, Any]:
        """Perform normality tests on sample."""
        if len(sample) < 8:
            return {
                "shapiro_wilk": None,
                "anderson_darling": None,
                "is_normal": None,
                "interpretation": "Insufficient data for normality testing",
            }

        results = {}

        # Shapiro-Wilk test
        if len(sample) <= 5000:  # Shapiro-Wilk has sample size limit
            sw_stat, sw_p = stats.shapiro(sample)
            results["shapiro_wilk"] = {"statistic": float(sw_stat), "p_value": float(sw_p), "normal": sw_p > self.alpha}
        else:
            results["shapiro_wilk"] = None

        # Anderson-Darling test
        ad_result = stats.anderson(sample, dist="norm")
        critical_value = ad_result.critical_values[2]  # 5% significance level
        results["anderson_darling"] = {
            "statistic": float(ad_result.statistic),
            "critical_value": float(critical_value),
            "normal": ad_result.statistic < critical_value,
        }

        # Overall normality assessment
        normal_tests = [
            test["normal"]
            for test in results.values()
            if test is not None and isinstance(test, dict) and "normal" in test
        ]

        if normal_tests:
            is_normal = all(normal_tests)
            interpretation = (
                "Sample appears to be normally distributed" if is_normal else "Sample deviates from normal distribution"
            )
        else:
            is_normal = None
            interpretation = "Could not assess normality"

        results["is_normal"] = is_normal
        results["interpretation"] = interpretation

        return results

    def descriptive_statistics(self, sample: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics."""
        if not sample:
            return {"error": "Empty sample"}

        sample_array = np.array(sample)

        return {
            "count": len(sample),
            "mean": float(np.mean(sample_array)),
            "median": float(np.median(sample_array)),
            "std": float(np.std(sample_array, ddof=1)),
            "variance": float(np.var(sample_array, ddof=1)),
            "min": float(np.min(sample_array)),
            "max": float(np.max(sample_array)),
            "range": float(np.max(sample_array) - np.min(sample_array)),
            "q25": float(np.percentile(sample_array, 25)),
            "q75": float(np.percentile(sample_array, 75)),
            "iqr": float(np.percentile(sample_array, 75) - np.percentile(sample_array, 25)),
            "p95": float(np.percentile(sample_array, 95)),
            "p99": float(np.percentile(sample_array, 99)),
            "cv": float(np.std(sample_array, ddof=1) / np.mean(sample_array)) if np.mean(sample_array) > 0 else 0.0,
            "skewness": float(stats.skew(sample_array)),
            "kurtosis": float(stats.kurtosis(sample_array)),
        }

    def power_analysis(self, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        """Perform statistical power analysis."""
        if len(sample1) < 3 or len(sample2) < 3:
            return {"error": "Insufficient data for power analysis"}

        # Calculate effect size (Cohen's d)
        mean1, mean2 = np.mean(sample1), np.mean(sample2)
        std1, std2 = np.std(sample1, ddof=1), np.std(sample2, ddof=1)
        n1, n2 = len(sample1), len(sample2)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return {"error": "Zero variance - cannot calculate effect size"}

        cohens_d = abs(mean1 - mean2) / pooled_std

        # Interpret effect size
        if cohens_d < 0.2:
            effect_interpretation = "negligible"
        elif cohens_d < 0.5:
            effect_interpretation = "small"
        elif cohens_d < 0.8:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"

        return {
            "cohens_d": float(cohens_d),
            "effect_interpretation": effect_interpretation,
            "sample_size_1": n1,
            "sample_size_2": n2,
            "pooled_std": float(pooled_std),
            "interpretation": f"Effect size is {effect_interpretation} (Cohen's d = {cohens_d:.3f})",
        }

    def comprehensive_comparison(
        self, baseline_data: Dict[str, Any], comparison_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive statistical comparison."""
        baseline_latencies = self.extract_latencies(baseline_data)
        comparison_latencies = self.extract_latencies(comparison_data)

        results = {
            "baseline_info": {
                "audit_id": baseline_data.get("audit_id"),
                "environment": baseline_data.get("environment", {}).get("environment_type"),
                "samples": baseline_data.get("samples"),
            },
            "comparison_info": {
                "audit_id": comparison_data.get("audit_id"),
                "environment": comparison_data.get("environment", {}).get("environment_type"),
                "samples": comparison_data.get("samples"),
            },
            "tests": {},
        }

        # Analyze each metric
        for metric in ["guardian", "memory", "orchestrator", "creativity"]:
            baseline_sample = baseline_latencies.get(metric, [])
            comparison_sample = comparison_latencies.get(metric, [])

            if not baseline_sample or not comparison_sample:
                results["tests"][metric] = {"error": "Missing data"}
                continue

            metric_results = {
                "descriptive_baseline": self.descriptive_statistics(baseline_sample),
                "descriptive_comparison": self.descriptive_statistics(comparison_sample),
                "mann_whitney": self.mann_whitney_test(baseline_sample, comparison_sample),
                "kolmogorov_smirnov": self.kolmogorov_smirnov_test(baseline_sample, comparison_sample),
                "power_analysis": self.power_analysis(baseline_sample, comparison_sample),
                "bootstrap_ci_baseline": self.bootstrap_confidence_interval(baseline_sample),
                "bootstrap_ci_comparison": self.bootstrap_confidence_interval(comparison_sample),
                "normality_baseline": self.normality_tests(baseline_sample),
                "normality_comparison": self.normality_tests(comparison_sample),
            }

            results["tests"][metric] = metric_results

        return results

    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate human-readable summary report."""
        report_lines = []
        report_lines.append("# T4/0.01% Excellence Statistical Analysis Report")
        report_lines.append("")

        # Header information
        baseline_info = analysis_results["baseline_info"]
        comparison_info = analysis_results["comparison_info"]

        report_lines.append("## Test Configuration")
        report_lines.append(f"- **Baseline:** {baseline_info['environment']} ({baseline_info['samples']} samples)")
        report_lines.append(
            f"- **Comparison:** {comparison_info['environment']} ({comparison_info['samples']} samples)"
        )
        report_lines.append(f"- **Significance Level:** α = {self.alpha}")
        report_lines.append(f"- **Confidence Level:** {self.confidence_level*100:.0f}%")
        report_lines.append("")

        # Results summary
        report_lines.append("## Statistical Test Results")
        report_lines.append("")

        for metric, tests in analysis_results["tests"].items():
            if "error" in tests:
                report_lines.append(f"### {metric.title()} Latency")
                report_lines.append(f"❌ **Error:** {tests['error']}")
                report_lines.append("")
                continue

            mw_test = tests["mann_whitney"]
            ks_test = tests["kolmogorov_smirnov"]
            baseline_desc = tests["descriptive_baseline"]
            comparison_desc = tests["descriptive_comparison"]
            baseline_ci = tests["bootstrap_ci_baseline"]
            comparison_ci = tests["bootstrap_ci_comparison"]

            report_lines.append(f"### {metric.title()} Latency")

            # Performance summary
            baseline_p95 = baseline_desc["p95"]
            comparison_p95 = comparison_desc["p95"]
            improvement = ((baseline_p95 - comparison_p95) / baseline_p95) * 100

            report_lines.append(f"- **Baseline p95:** {baseline_p95:.1f}μs")
            report_lines.append(f"- **Comparison p95:** {comparison_p95:.1f}μs")

            if improvement > 0:
                report_lines.append(f"- **Improvement:** {improvement:.1f}% faster")
            elif improvement < 0:
                report_lines.append(f"- **Regression:** {abs(improvement):.1f}% slower")
            else:
                report_lines.append("- **Change:** No significant difference")

            # Statistical tests
            if mw_test["p_value"] is not None:
                significance = "✅ PASS" if not mw_test["significant"] else "❌ FAIL"
                report_lines.append(f"- **Mann-Whitney U:** p = {mw_test['p_value']:.6f} ({significance})")

            if ks_test["p_value"] is not None:
                significance = "✅ PASS" if not ks_test["significant"] else "❌ FAIL"
                report_lines.append(f"- **Kolmogorov-Smirnov:** p = {ks_test['p_value']:.6f} ({significance})")

            # Confidence intervals
            if baseline_ci["lower"] is not None:
                report_lines.append(f"- **Baseline CI95%:** [{baseline_ci['lower']:.1f}, {baseline_ci['upper']:.1f}]μs")
            if comparison_ci["lower"] is not None:
                report_lines.append(
                    f"- **Comparison CI95%:** [{comparison_ci['lower']:.1f}, {comparison_ci['upper']:.1f}]μs"
                )

            report_lines.append("")

        # Overall assessment
        report_lines.append("## Overall Assessment")

        all_tests_passed = True
        test_count = 0

        for metric, tests in analysis_results["tests"].items():
            if "error" not in tests:
                mw_test = tests["mann_whitney"]
                ks_test = tests["kolmogorov_smirnov"]

                if mw_test["p_value"] is not None:
                    test_count += 1
                    if mw_test["significant"]:
                        all_tests_passed = False

                if ks_test["p_value"] is not None:
                    test_count += 1
                    if ks_test["significant"]:
                        all_tests_passed = False

        if all_tests_passed and test_count > 0:
            report_lines.append("✅ **VERDICT:** Distributions are statistically identical")
            report_lines.append("🎯 **T4/0.01% COMPLIANCE:** Performance claims validated")
        else:
            report_lines.append("❌ **VERDICT:** Significant differences detected")
            report_lines.append("⚠️  **T4/0.01% COMPLIANCE:** Performance claims require investigation")

        return "\n".join(report_lines)


def main():
    """Main statistical analysis function."""
    parser = argparse.ArgumentParser(description="T4/0.01% Statistical Analysis")
    parser.add_argument("--baseline", required=True, help="Baseline audit JSON file")
    parser.add_argument("--comparison", required=True, help="Comparison audit JSON file")
    parser.add_argument("--alpha", type=float, default=0.01, help="Significance level")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--report", help="Output report markdown file")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = StatisticalAnalyzer(alpha=args.alpha)

    # Load data
    baseline_data = analyzer.load_audit_data(args.baseline)
    comparison_data = analyzer.load_audit_data(args.comparison)

    # Perform comprehensive analysis
    results = analyzer.comprehensive_comparison(baseline_data, comparison_data)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    # Generate and save report
    if args.report:
        report = analyzer.generate_summary_report(results)
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            f.write(report)

        print("📊 Statistical analysis complete")
        print(f"Results: {args.output}")
        print(f"Report: {args.report}")
    else:
        print(f"📊 Statistical analysis complete: {args.output}")

    # Print summary
    test_results = results["tests"]
    passed_tests = 0
    total_tests = 0

    for metric, tests in test_results.items():
        if "error" not in tests:
            mw_test = tests["mann_whitney"]
            if mw_test["p_value"] is not None:
                total_tests += 1
                if not mw_test["significant"]:
                    passed_tests += 1

    print(f"Statistical Tests: {passed_tests}/{total_tests} PASSED")

    if passed_tests == total_tests and total_tests > 0:
        print("🎯 T4/0.01% STATISTICAL VALIDATION: ✅ ACHIEVED")
    else:
        print("⚠️  T4/0.01% STATISTICAL VALIDATION: ❌ INVESTIGATION REQUIRED")


if __name__ == "__main__":
    main()
