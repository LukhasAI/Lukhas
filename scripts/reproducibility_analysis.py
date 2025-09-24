#!/usr/bin/env python3
"""
T4/0.01% Excellence Reproducibility Analysis

Analyzes reproducibility across multiple independent benchmark runs.
Calculates consistency metrics, variance analysis, and reproducibility scores.
"""

import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class ReproducibilityAnalyzer:
    """Comprehensive reproducibility analysis for audit validation."""

    def __init__(self, target_reproducibility: float = 0.80):
        """Initialize with target reproducibility threshold."""
        self.target_reproducibility = target_reproducibility

    def load_multiple_audits(self, file_patterns: List[str]) -> List[Dict[str, Any]]:
        """Load multiple audit result files."""
        audit_data = []

        for pattern in file_patterns:
            file_path = Path(pattern)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    audit_data.append(json.load(f))
            else:
                # Handle glob patterns
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file():
                        with open(file_path, 'r') as f:
                            audit_data.append(json.load(f))

        return audit_data

    def extract_performance_matrices(self, audit_results: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Extract performance data as matrices for analysis."""
        matrices = {
            "guardian_p95": [],
            "memory_p95": [],
            "orchestrator_p95": [],
            "creativity_p95": [],
            "guardian_mean": [],
            "memory_mean": [],
            "orchestrator_mean": [],
            "creativity_mean": []
        }

        for audit in audit_results:
            # Extract p95 latencies
            matrices["guardian_p95"].append(audit.get("guardian_stats", {}).get("p95", np.nan))
            matrices["memory_p95"].append(audit.get("memory_stats", {}).get("p95", np.nan))
            matrices["orchestrator_p95"].append(audit.get("orchestrator_stats", {}).get("p95", np.nan))
            matrices["creativity_p95"].append(audit.get("creativity_stats", {}).get("p95", np.nan))

            # Extract mean latencies
            matrices["guardian_mean"].append(audit.get("guardian_stats", {}).get("mean", np.nan))
            matrices["memory_mean"].append(audit.get("memory_stats", {}).get("mean", np.nan))
            matrices["orchestrator_mean"].append(audit.get("orchestrator_stats", {}).get("mean", np.nan))
            matrices["creativity_mean"].append(audit.get("creativity_stats", {}).get("mean", np.nan))

        # Convert to numpy arrays and remove NaN values
        for key in matrices:
            array = np.array(matrices[key])
            matrices[key] = array[~np.isnan(array)]

        return matrices

    def calculate_reproducibility_metrics(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate reproducibility metrics for a set of values."""
        if len(values) < 2:
            return {
                "reproducibility_score": 0.0,
                "coefficient_of_variation": float('inf'),
                "relative_std": float('inf'),
                "consistency_score": 0.0,
                "interpretation": "Insufficient data"
            }

        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)

        # Coefficient of variation
        cv = std_val / mean_val if mean_val > 0 else float('inf')

        # Relative standard deviation (percentage)
        relative_std = cv * 100

        # Reproducibility score (inversely related to CV)
        # Score of 1.0 means CV = 0%, score of 0.0 means CV >= 20%
        reproducibility_score = max(0.0, 1.0 - (cv / 0.20))

        # Consistency score based on how many values fall within ±10% of mean
        tolerance = 0.10
        within_tolerance = np.sum(np.abs(values - mean_val) <= tolerance * mean_val)
        consistency_score = within_tolerance / len(values)

        # Interpretation
        if cv < 0.05:
            interpretation = "Excellent reproducibility"
        elif cv < 0.10:
            interpretation = "Good reproducibility"
        elif cv < 0.15:
            interpretation = "Acceptable reproducibility"
        elif cv < 0.20:
            interpretation = "Poor reproducibility"
        else:
            interpretation = "Unacceptable reproducibility"

        return {
            "reproducibility_score": float(reproducibility_score),
            "coefficient_of_variation": float(cv),
            "relative_std": float(relative_std),
            "consistency_score": float(consistency_score),
            "interpretation": interpretation,
            "mean": float(mean_val),
            "std": float(std_val),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "range": float(np.max(values) - np.min(values)),
            "count": len(values)
        }

    def cross_run_variance_analysis(self, matrices: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Analyze variance across multiple runs."""
        results = {}

        for metric, values in matrices.items():
            if len(values) < 2:
                results[metric] = {"error": "Insufficient data"}
                continue

            # Calculate basic variance metrics
            variance_metrics = self.calculate_reproducibility_metrics(values)

            # Add additional variance analysis
            variance_metrics.update({
                "variance": float(np.var(values, ddof=1)),
                "interquartile_range": float(np.percentile(values, 75) - np.percentile(values, 25)),
                "median_absolute_deviation": float(np.median(np.abs(values - np.median(values)))),
                "min_max_ratio": float(np.min(values) / np.max(values)) if np.max(values) > 0 else 0.0
            })

            results[metric] = variance_metrics

        return results

    def detect_outliers(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        if len(values) < 4:
            return {"method": "insufficient_data", "outliers": [], "outlier_count": 0}

        # IQR method
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        iqr_outliers = []
        for i, val in enumerate(values):
            if val < lower_bound or val > upper_bound:
                iqr_outliers.append({"index": i, "value": float(val), "method": "iqr"})

        # Z-score method (modified Z-score using MAD)
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        modified_z_scores = 0.6745 * (values - median) / mad if mad > 0 else np.zeros_like(values)

        zscore_outliers = []
        for i, z_score in enumerate(modified_z_scores):
            if abs(z_score) > 3.5:  # Threshold for modified Z-score
                zscore_outliers.append({"index": i, "value": float(values[i]), "z_score": float(z_score), "method": "zscore"})

        # Combine outliers
        all_outliers = iqr_outliers + zscore_outliers

        return {
            "iqr_outliers": iqr_outliers,
            "zscore_outliers": zscore_outliers,
            "all_outliers": all_outliers,
            "outlier_count": len(set(o["index"] for o in all_outliers)),
            "outlier_percentage": len(set(o["index"] for o in all_outliers)) / len(values) * 100
        }

    def environment_consistency_analysis(self, audit_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consistency across different environments."""
        environments = {}

        # Group results by environment
        for audit in audit_results:
            env_type = audit.get("environment", {}).get("environment_type", "unknown")
            if env_type not in environments:
                environments[env_type] = []
            environments[env_type].append(audit)

        # Analyze each environment
        env_analysis = {}
        for env_type, env_audits in environments.items():
            if len(env_audits) < 2:
                env_analysis[env_type] = {"error": "Insufficient data for analysis"}
                continue

            env_matrices = self.extract_performance_matrices(env_audits)
            env_variance = self.cross_run_variance_analysis(env_matrices)

            env_analysis[env_type] = {
                "audit_count": len(env_audits),
                "variance_analysis": env_variance,
                "average_reproducibility": np.mean([
                    metrics.get("reproducibility_score", 0.0)
                    for metrics in env_variance.values()
                    if "error" not in metrics
                ])
            }

        return env_analysis

    def generate_reproducibility_matrix(self, matrices: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Generate comprehensive reproducibility matrix."""
        # Overall variance analysis
        variance_analysis = self.cross_run_variance_analysis(matrices)

        # Calculate overall reproducibility score
        reproducibility_scores = [
            metrics.get("reproducibility_score", 0.0)
            for metrics in variance_analysis.values()
            if "error" not in metrics
        ]

        overall_reproducibility = np.mean(reproducibility_scores) if reproducibility_scores else 0.0

        # Identify metrics that meet/fail reproducibility targets
        passing_metrics = []
        failing_metrics = []

        for metric, analysis in variance_analysis.items():
            if "error" not in analysis:
                score = analysis.get("reproducibility_score", 0.0)
                if score >= self.target_reproducibility:
                    passing_metrics.append(metric)
                else:
                    failing_metrics.append(metric)

        # Reproducibility classification
        if overall_reproducibility >= 0.90:
            classification = "excellent"
        elif overall_reproducibility >= 0.80:
            classification = "good"
        elif overall_reproducibility >= 0.70:
            classification = "acceptable"
        elif overall_reproducibility >= 0.50:
            classification = "poor"
        else:
            classification = "unacceptable"

        return {
            "overall_reproducibility_score": float(overall_reproducibility),
            "target_reproducibility": self.target_reproducibility,
            "classification": classification,
            "passing_metrics": passing_metrics,
            "failing_metrics": failing_metrics,
            "metric_analysis": variance_analysis,
            "meets_target": overall_reproducibility >= self.target_reproducibility,
            "recommendation": self._generate_reproducibility_recommendation(
                overall_reproducibility, failing_metrics
            )
        }

    def _generate_reproducibility_recommendation(
        self,
        score: float,
        failing_metrics: List[str]
    ) -> str:
        """Generate reproducibility improvement recommendations."""
        if score >= self.target_reproducibility:
            return "Reproducibility targets met. System ready for production."

        recommendations = []

        if score < 0.50:
            recommendations.append("Critical: Fundamental reproducibility issues detected")
            recommendations.append("- Review test environment stability")
            recommendations.append("- Implement deterministic seeding")
            recommendations.append("- Validate measurement methodology")

        if failing_metrics:
            recommendations.append(f"Address variability in: {', '.join(failing_metrics)}")

        if score < 0.70:
            recommendations.append("- Increase sample sizes for more stable measurements")
            recommendations.append("- Control for external system load")
            recommendations.append("- Review hardware consistency requirements")

        return "; ".join(recommendations) if recommendations else "No specific recommendations"

    def generate_visualizations(self, matrices: Dict[str, np.ndarray], output_dir: str):
        """Generate reproducibility visualizations."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # 1. Box plots for each metric
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('T4/0.01% Reproducibility Analysis - Performance Distribution', fontsize=16)

        metrics = ["guardian_p95", "memory_p95", "orchestrator_p95", "creativity_p95"]
        titles = ["Guardian p95 (μs)", "Memory p95 (μs)", "Orchestrator p95 (μs)", "Creativity p95 (μs)"]

        for i, (metric, title) in enumerate(zip(metrics, titles)):
            row, col = i // 2, i % 2
            ax = axes[row, col]

            if len(matrices[metric]) > 0:
                ax.boxplot(matrices[metric], patch_artist=True)
                ax.set_title(title)
                ax.set_ylabel('Latency (μs)')
                ax.grid(True, alpha=0.3)

                # Add statistics
                mean_val = np.mean(matrices[metric])
                cv = np.std(matrices[metric]) / mean_val * 100
                ax.text(0.02, 0.98, f'CV: {cv:.1f}%', transform=ax.transAxes,
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat'))
            else:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title + " (No Data)")

        plt.tight_layout()
        plt.savefig(output_path / "reproducibility_boxplots.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Reproducibility scores heatmap
        fig, ax = plt.subplots(figsize=(12, 8))

        # Prepare data for heatmap
        variance_analysis = self.cross_run_variance_analysis(matrices)
        heatmap_data = []
        labels = []

        for metric, analysis in variance_analysis.items():
            if "error" not in analysis:
                heatmap_data.append([
                    analysis["reproducibility_score"],
                    analysis["consistency_score"],
                    1.0 - min(analysis["coefficient_of_variation"] / 0.20, 1.0)  # Normalized CV
                ])
                labels.append(metric.replace("_", " ").title())

        if heatmap_data:
            heatmap_array = np.array(heatmap_data)
            sns.heatmap(heatmap_array,
                       xticklabels=["Reproducibility Score", "Consistency Score", "CV Score"],
                       yticklabels=labels,
                       annot=True, fmt='.3f', cmap='RdYlGn',
                       vmin=0, vmax=1, ax=ax)

            ax.set_title('T4/0.01% Reproducibility Metrics Heatmap', fontsize=14)
            plt.tight_layout()
            plt.savefig(output_path / "reproducibility_heatmap.png", dpi=300, bbox_inches='tight')

        plt.close()

        # 3. Trend analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('T4/0.01% Reproducibility - Run-to-Run Variation', fontsize=16)

        for i, (metric, title) in enumerate(zip(metrics, titles)):
            row, col = i // 2, i % 2
            ax = axes[row, col]

            if len(matrices[metric]) > 0:
                run_numbers = range(1, len(matrices[metric]) + 1)
                ax.plot(run_numbers, matrices[metric], 'o-', linewidth=2, markersize=6)
                ax.set_title(title)
                ax.set_xlabel('Run Number')
                ax.set_ylabel('Latency (μs)')
                ax.grid(True, alpha=0.3)

                # Add trend line
                if len(matrices[metric]) > 2:
                    z = np.polyfit(run_numbers, matrices[metric], 1)
                    p = np.poly1d(z)
                    ax.plot(run_numbers, p(run_numbers), '--', alpha=0.7, color='red')

            else:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title + " (No Data)")

        plt.tight_layout()
        plt.savefig(output_path / "reproducibility_trends.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📊 Visualizations saved to {output_path}/")

    def generate_comprehensive_report(
        self,
        audit_results: List[Dict[str, Any]],
        reproducibility_matrix: Dict[str, Any]
    ) -> str:
        """Generate comprehensive reproducibility report."""
        report_lines = []
        report_lines.append("# T4/0.01% Excellence Reproducibility Analysis Report")
        report_lines.append("")

        # Executive summary
        score = reproducibility_matrix["overall_reproducibility_score"]
        classification = reproducibility_matrix["classification"]
        meets_target = reproducibility_matrix["meets_target"]

        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"- **Overall Reproducibility Score:** {score:.3f}")
        report_lines.append(f"- **Target Threshold:** {reproducibility_matrix['target_reproducibility']:.3f}")
        report_lines.append(f"- **Classification:** {classification.title()}")

        status = "✅ PASS" if meets_target else "❌ FAIL"
        report_lines.append(f"- **T4/0.01% Compliance:** {status}")
        report_lines.append("")

        # Test configuration
        report_lines.append("## Test Configuration")
        report_lines.append("")
        report_lines.append(f"- **Total Audit Runs:** {len(audit_results)}")

        # Environment breakdown
        environments = set()
        for audit in audit_results:
            env_type = audit.get("environment", {}).get("environment_type", "unknown")
            environments.add(env_type)

        report_lines.append(f"- **Environments Tested:** {', '.join(sorted(environments))}")
        report_lines.append("")

        # Detailed metrics analysis
        report_lines.append("## Detailed Metrics Analysis")
        report_lines.append("")

        metric_analysis = reproducibility_matrix["metric_analysis"]
        for metric, analysis in metric_analysis.items():
            if "error" in analysis:
                continue

            metric_name = metric.replace("_", " ").title()
            report_lines.append(f"### {metric_name}")

            score = analysis["reproducibility_score"]
            cv = analysis["coefficient_of_variation"] * 100
            consistency = analysis["consistency_score"] * 100

            status = "✅ PASS" if score >= reproducibility_matrix["target_reproducibility"] else "❌ FAIL"

            report_lines.append(f"- **Reproducibility Score:** {score:.3f} ({status})")
            report_lines.append(f"- **Coefficient of Variation:** {cv:.2f}%")
            report_lines.append(f"- **Consistency Score:** {consistency:.1f}%")
            report_lines.append(f"- **Mean Latency:** {analysis['mean']:.1f}μs")
            report_lines.append(f"- **Standard Deviation:** {analysis['std']:.2f}μs")
            report_lines.append(f"- **Range:** {analysis['range']:.1f}μs ({analysis['min']:.1f} - {analysis['max']:.1f})")
            report_lines.append(f"- **Assessment:** {analysis['interpretation']}")
            report_lines.append("")

        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        recommendation = reproducibility_matrix["recommendation"]
        if recommendation:
            for rec in recommendation.split(";"):
                report_lines.append(f"- {rec.strip()}")
        else:
            report_lines.append("- No specific recommendations")

        report_lines.append("")

        # Final verdict
        report_lines.append("## Final Verdict")
        report_lines.append("")

        if meets_target:
            report_lines.append("✅ **REPRODUCIBILITY VALIDATION:** PASSED")
            report_lines.append("🎯 **T4/0.01% COMPLIANCE:** System demonstrates acceptable reproducibility")
            report_lines.append("🚀 **RECOMMENDATION:** Approved for production deployment")
        else:
            report_lines.append("❌ **REPRODUCIBILITY VALIDATION:** FAILED")
            report_lines.append("⚠️  **T4/0.01% COMPLIANCE:** Reproducibility below acceptable threshold")
            report_lines.append("🔧 **RECOMMENDATION:** Address reproducibility issues before deployment")

        return "\n".join(report_lines)


def main():
    """Main reproducibility analysis function."""
    parser = argparse.ArgumentParser(description="T4/0.01% Reproducibility Analysis")
    parser.add_argument("--data", nargs="+", required=True, help="Audit result JSON files or patterns")
    parser.add_argument("--output", required=True, help="Output analysis JSON file")
    parser.add_argument("--report", help="Output report markdown file")
    parser.add_argument("--visualizations", help="Output directory for visualizations")
    parser.add_argument("--target-reproducibility", type=float, default=0.80,
                       help="Target reproducibility threshold")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = ReproducibilityAnalyzer(target_reproducibility=args.target_reproducibility)

    # Load audit data
    audit_results = analyzer.load_multiple_audits(args.data)

    if len(audit_results) < 2:
        print("❌ Error: At least 2 audit results required for reproducibility analysis")
        return 1

    print(f"📊 Analyzing reproducibility across {len(audit_results)} audit runs")

    # Extract performance matrices
    matrices = analyzer.extract_performance_matrices(audit_results)

    # Generate reproducibility matrix
    reproducibility_matrix = analyzer.generate_reproducibility_matrix(matrices)

    # Environment consistency analysis
    env_consistency = analyzer.environment_consistency_analysis(audit_results)

    # Compile final results
    final_results = {
        "reproducibility_matrix": reproducibility_matrix,
        "environment_consistency": env_consistency,
        "audit_summary": {
            "total_audits": len(audit_results),
            "environments": list(set(
                audit.get("environment", {}).get("environment_type", "unknown")
                for audit in audit_results
            )),
            "analysis_timestamp": Path().absolute().name  # Use current dir as timestamp
        }
    }

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(final_results, f, indent=2, sort_keys=True)

    # Generate report
    if args.report:
        report = analyzer.generate_comprehensive_report(audit_results, reproducibility_matrix)
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"📄 Report saved: {args.report}")

    # Generate visualizations
    if args.visualizations:
        analyzer.generate_visualizations(matrices, args.visualizations)

    # Print summary
    score = reproducibility_matrix["overall_reproducibility_score"]
    meets_target = reproducibility_matrix["meets_target"]

    print(f"\n🎯 Reproducibility Analysis Complete")
    print(f"Overall Score: {score:.3f}")
    print(f"Target: {args.target_reproducibility:.3f}")

    status = "✅ PASSED" if meets_target else "❌ FAILED"
    print(f"T4/0.01% Compliance: {status}")

    print(f"Results: {args.output}")

    return 0 if meets_target else 1


if __name__ == "__main__":
    exit(main())