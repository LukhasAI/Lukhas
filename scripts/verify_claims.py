#!/usr/bin/env python3
"""
Module: verify_claims.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
T4/0.01% Excellence Claims Verification Script

Validates performance measurements against published T4/0.01% excellence claims.
Provides automated verification with tolerance checking and detailed reporting.
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ClaimTarget:
    """Performance claim target with tolerance."""
    component: str
    metric: str
    target_value: float
    unit: str
    tolerance_percent: float
    description: str


@dataclass
class VerificationResult:
    """Result of a single claim verification."""
    claim: ClaimTarget
    measured_value: Optional[float]
    within_tolerance: bool
    deviation_percent: float
    status: str  # "PASS", "FAIL", "MISSING"
    details: str


class ClaimsVerifier:
    """Comprehensive T4/0.01% claims verification framework."""

    def __init__(self, tolerance_percent: float = 10.0):
        """Initialize with default tolerance."""
        self.tolerance_percent = tolerance_percent
        self.t4_claims = self._load_t4_claims()

    def _load_t4_claims(self) -> List[ClaimTarget]:
        """Load T4/0.01% performance claims."""
        return [
            ClaimTarget(
                component="guardian",
                metric="p95_latency_us",
                target_value=168.0,
                unit="μs",
                tolerance_percent=self.tolerance_percent,
                description="Guardian E2E response time (p95)"
            ),
            ClaimTarget(
                component="memory",
                metric="p95_latency_us",
                target_value=178.0,
                unit="μs",
                tolerance_percent=self.tolerance_percent,
                description="Memory event creation time (p95)"
            ),
            ClaimTarget(
                component="orchestrator",
                metric="p95_latency_us",
                target_value=54000.0,  # 54ms in microseconds
                unit="μs",
                tolerance_percent=self.tolerance_percent,
                description="Orchestrator health check time (p95)"
            ),
            ClaimTarget(
                component="creativity",
                metric="p95_latency_us",
                target_value=50000.0,  # 50ms in microseconds
                unit="μs",
                tolerance_percent=25.0,  # More tolerance for new component
                description="Creativity engine processing time (p95)"
            ),
            # Additional performance claims
            ClaimTarget(
                component="guardian",
                metric="mean_latency_us",
                target_value=150.0,
                unit="μs",
                tolerance_percent=15.0,
                description="Guardian E2E mean response time"
            ),
            ClaimTarget(
                component="memory",
                metric="mean_latency_us",
                target_value=160.0,
                unit="μs",
                tolerance_percent=15.0,
                description="Memory event creation mean time"
            )
        ]

    def load_baseline_data(self, baseline_file: str) -> Dict[str, Any]:
        """Load baseline audit data from file."""
        baseline_path = Path(baseline_file)

        if baseline_path.suffix.lower() == '.md':
            # Parse from markdown audit report
            return self._parse_markdown_claims(baseline_path)
        else:
            # Load from JSON
            with open(baseline_path, 'r') as f:
                return json.load(f)

    def _parse_markdown_claims(self, md_file: Path) -> Dict[str, Any]:
        """Parse claims from markdown audit report."""
        with open(md_file, 'r') as f:
            content = f.read()

        # Extract performance claims using regex
        claims_data = {}

        # Pattern to match performance claims like "Guardian E2E: 168.18μs"
        pattern = r'(\w+)\s+E2E:\s*([0-9,.]+)μs'
        matches = re.findall(pattern, content, re.IGNORECASE)

        for component, value_str in matches:
            # Clean value string and convert to float
            value = float(value_str.replace(',', ''))

            component_lower = component.lower()
            if component_lower not in claims_data:
                claims_data[component_lower] = {}

            claims_data[component_lower]['p95_latency_us'] = value

        return claims_data

    def load_results_data(self, results_file: str) -> Dict[str, Any]:
        """Load measurement results from file."""
        with open(results_file, 'r') as f:
            return json.load(f)

    def extract_measurement_value(
        self,
        results_data: Dict[str, Any],
        claim: ClaimTarget
    ) -> Optional[float]:
        """Extract measurement value for a specific claim."""

        # Map component names to result data structure
        component_mapping = {
            "guardian": "guardian_stats",
            "memory": "memory_stats",
            "orchestrator": "orchestrator_stats",
            "creativity": "creativity_stats"
        }

        # Map metric names
        metric_mapping = {
            "p95_latency_us": "p95",
            "mean_latency_us": "mean"
        }

        component_key = component_mapping.get(claim.component)
        metric_key = metric_mapping.get(claim.metric)

        if not component_key or not metric_key:
            return None

        # Navigate through data structure
        component_data = results_data.get(component_key)
        if not component_data:
            return None

        return component_data.get(metric_key)

    def verify_claim(
        self,
        claim: ClaimTarget,
        measured_value: Optional[float]
    ) -> VerificationResult:
        """Verify a single performance claim."""

        if measured_value is None:
            return VerificationResult(
                claim=claim,
                measured_value=None,
                within_tolerance=False,
                deviation_percent=0.0,
                status="MISSING",
                details="Measurement data not found"
            )

        # Calculate tolerance bounds
        tolerance_amount = claim.target_value * (claim.tolerance_percent / 100.0)
        lower_bound = claim.target_value - tolerance_amount
        upper_bound = claim.target_value + tolerance_amount

        # Check if within tolerance
        within_tolerance = lower_bound <= measured_value <= upper_bound

        # Calculate deviation percentage
        deviation_percent = abs(measured_value - claim.target_value) / claim.target_value * 100.0

        # Determine status
        if within_tolerance:
            status = "PASS"
            details = f"Within ±{claim.tolerance_percent}% tolerance"
        else:
            status = "FAIL"
            if measured_value > upper_bound:
                details = f"Exceeds target by {deviation_percent:.1f}%"
            else:
                details = f"Below target by {deviation_percent:.1f}%"

        return VerificationResult(
            claim=claim,
            measured_value=measured_value,
            within_tolerance=within_tolerance,
            deviation_percent=deviation_percent,
            status=status,
            details=details
        )

    def verify_all_claims(
        self,
        baseline_data: Dict[str, Any],
        results_data: Dict[str, Any]
    ) -> List[VerificationResult]:
        """Verify all T4/0.01% performance claims."""

        verification_results = []

        for claim in self.t4_claims:
            # First try to get baseline target if available
            baseline_value = self.extract_measurement_value(baseline_data, claim)
            if baseline_value is not None:
                # Update claim target to baseline if it exists
                claim.target_value = baseline_value

            # Extract measured value
            measured_value = self.extract_measurement_value(results_data, claim)

            # Verify claim
            result = self.verify_claim(claim, measured_value)
            verification_results.append(result)

        return verification_results

    def generate_verification_report(
        self,
        verification_results: List[VerificationResult],
        baseline_file: str,
        results_file: str
    ) -> str:
        """Generate comprehensive verification report."""

        report_lines = []
        report_lines.append("# T4/0.01% Excellence Claims Verification Report")
        report_lines.append("")

        # Header information
        report_lines.append("## Verification Configuration")
        report_lines.append(f"- **Baseline Claims:** {baseline_file}")
        report_lines.append(f"- **Results Data:** {results_file}")
        report_lines.append(f"- **Default Tolerance:** ±{self.tolerance_percent}%")
        report_lines.append("")

        # Summary statistics
        total_claims = len(verification_results)
        passed_claims = sum(1 for r in verification_results if r.status == "PASS")
        failed_claims = sum(1 for r in verification_results if r.status == "FAIL")
        missing_claims = sum(1 for r in verification_results if r.status == "MISSING")

        report_lines.append("## Verification Summary")
        report_lines.append(f"- **Total Claims:** {total_claims}")
        report_lines.append(f"- **Passed:** {passed_claims}")
        report_lines.append(f"- **Failed:** {failed_claims}")
        report_lines.append(f"- **Missing Data:** {missing_claims}")
        report_lines.append("")

        # Overall verdict
        if failed_claims == 0 and missing_claims == 0:
            verdict = "✅ ALL CLAIMS VERIFIED"
            compliance = "🎯 T4/0.01% COMPLIANCE: ACHIEVED"
        elif failed_claims == 0 and missing_claims > 0:
            verdict = "⚠️  PARTIAL VERIFICATION (missing data)"
            compliance = "🔍 T4/0.01% COMPLIANCE: REQUIRES INVESTIGATION"
        else:
            verdict = "❌ CLAIMS VERIFICATION FAILED"
            compliance = "🚫 T4/0.01% COMPLIANCE: NOT ACHIEVED"

        report_lines.append(f"**VERDICT:** {verdict}")
        report_lines.append(f"**COMPLIANCE:** {compliance}")
        report_lines.append("")

        # Detailed results
        report_lines.append("## Detailed Verification Results")
        report_lines.append("")

        for result in verification_results:
            claim = result.claim
            status_icon = {"PASS": "✅", "FAIL": "❌", "MISSING": "⚠️"}[result.status]

            report_lines.append(f"### {claim.component.title()} - {claim.description}")
            report_lines.append(f"- **Target:** {claim.target_value:.1f}{claim.unit}")

            if result.measured_value is not None:
                report_lines.append(f"- **Measured:** {result.measured_value:.1f}{claim.unit}")
                report_lines.append(f"- **Deviation:** {result.deviation_percent:.1f}%")
            else:
                report_lines.append("- **Measured:** N/A")

            report_lines.append(f"- **Tolerance:** ±{claim.tolerance_percent}%")
            report_lines.append(f"- **Status:** {status_icon} {result.status}")
            report_lines.append(f"- **Details:** {result.details}")
            report_lines.append("")

        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")

        if failed_claims > 0:
            report_lines.append("### Performance Issues Detected")
            for result in verification_results:
                if result.status == "FAIL":
                    report_lines.append(f"- **{result.claim.component.title()}:** {result.details}")
            report_lines.append("")
            report_lines.append("**Action Required:** Investigate and optimize underperforming components")
            report_lines.append("")

        if missing_claims > 0:
            report_lines.append("### Missing Measurements")
            for result in verification_results:
                if result.status == "MISSING":
                    report_lines.append(f"- **{result.claim.component.title()}:** {result.claim.description}")
            report_lines.append("")
            report_lines.append("**Action Required:** Complete measurement collection for all components")
            report_lines.append("")

        if failed_claims == 0 and missing_claims == 0:
            report_lines.append("✅ **All claims verified successfully**")
            report_lines.append("🚀 **System ready for T4/0.01% excellence certification**")

        return "\n".join(report_lines)

    def export_verification_json(
        self,
        verification_results: List[VerificationResult],
        baseline_file: str,
        results_file: str
    ) -> Dict[str, Any]:
        """Export verification results as JSON."""

        # Convert results to serializable format
        results_data = []
        for result in verification_results:
            results_data.append({
                "claim": {
                    "component": result.claim.component,
                    "metric": result.claim.metric,
                    "target_value": result.claim.target_value,
                    "unit": result.claim.unit,
                    "tolerance_percent": result.claim.tolerance_percent,
                    "description": result.claim.description
                },
                "measured_value": result.measured_value,
                "within_tolerance": result.within_tolerance,
                "deviation_percent": result.deviation_percent,
                "status": result.status,
                "details": result.details
            })

        # Summary statistics
        total_claims = len(verification_results)
        passed_claims = sum(1 for r in verification_results if r.status == "PASS")
        failed_claims = sum(1 for r in verification_results if r.status == "FAIL")
        missing_claims = sum(1 for r in verification_results if r.status == "MISSING")

        return {
            "verification_metadata": {
                "baseline_file": baseline_file,
                "results_file": results_file,
                "default_tolerance_percent": self.tolerance_percent,
                "verification_timestamp": Path(__file__).stat().st_mtime
            },
            "summary": {
                "total_claims": total_claims,
                "passed_claims": passed_claims,
                "failed_claims": failed_claims,
                "missing_claims": missing_claims,
                "success_rate": passed_claims / total_claims if total_claims > 0 else 0.0,
                "overall_status": "PASS" if failed_claims == 0 and missing_claims == 0 else "FAIL"
            },
            "verification_results": results_data
        }


def main():
    """Main claims verification function."""
    parser = argparse.ArgumentParser(description="T4/0.01% Excellence Claims Verification")
    parser.add_argument("--baseline", required=True, help="Baseline claims file (JSON or MD)")
    parser.add_argument("--results", required=True, help="Results measurement file (JSON)")
    parser.add_argument("--tolerance", type=float, default=10.0, help="Tolerance percentage")
    parser.add_argument("--report", help="Output verification report (Markdown)")
    parser.add_argument("--output", help="Output verification data (JSON)")

    args = parser.parse_args()

    # Initialize verifier
    verifier = ClaimsVerifier(tolerance_percent=args.tolerance)

    # Load data
    try:
        baseline_data = verifier.load_baseline_data(args.baseline)
        results_data = verifier.load_results_data(args.results)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return 1

    # Perform verification
    verification_results = verifier.verify_all_claims(baseline_data, results_data)

    # Generate and save report
    if args.report:
        report = verifier.generate_verification_report(
            verification_results, args.baseline, args.results
        )

        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"📄 Verification report saved: {args.report}")

    # Export JSON data
    if args.output:
        verification_data = verifier.export_verification_json(
            verification_results, args.baseline, args.results
        )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(verification_data, f, indent=2, sort_keys=True)

        print(f"📊 Verification data saved: {args.output}")

    # Print summary
    total_claims = len(verification_results)
    passed_claims = sum(1 for r in verification_results if r.status == "PASS")
    failed_claims = sum(1 for r in verification_results if r.status == "FAIL")
    missing_claims = sum(1 for r in verification_results if r.status == "MISSING")

    print("\n🎯 Claims Verification Summary:")
    print(f"Total Claims: {total_claims}")
    print(f"Passed: {passed_claims}")
    print(f"Failed: {failed_claims}")
    print(f"Missing: {missing_claims}")

    # Print individual results
    for result in verification_results:
        status_icon = {"PASS": "✅", "FAIL": "❌", "MISSING": "⚠️"}[result.status]
        component = result.claim.component.title()
        value = f"{result.measured_value:.1f}μs" if result.measured_value else "N/A"
        target = f"{result.claim.target_value:.1f}μs"

        print(f"{status_icon} {component}: {value} vs {target} target ({result.status})")

    # Overall verdict
    if failed_claims == 0 and missing_claims == 0:
        print("\n✅ T4/0.01% CLAIMS VERIFICATION: PASSED")
        print("🎯 All performance claims validated within tolerance")
        return 0
    elif failed_claims == 0:
        print("\n⚠️  T4/0.01% CLAIMS VERIFICATION: INCOMPLETE")
        print("🔍 Some measurement data missing - manual review required")
        return 2
    else:
        print("\n❌ T4/0.01% CLAIMS VERIFICATION: FAILED")
        print("🚫 Performance claims not met - optimization required")
        return 1


if __name__ == "__main__":
    exit(main())
