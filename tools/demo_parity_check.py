#!/usr/bin/env python3
"""
Matrix Tracks Demo-Production Parity Checker

Ensures demo scripts maintain interface compatibility with production tools.
Prevents demos from silently drifting and becoming misleading.

Validates:
- Demo scripts use same CLI arguments as production tools
- Mock outputs maintain same format as real tools
- Demo data structures match production schemas
"""

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Optional


class DemoParityChecker:
    """Check demo-production parity for Matrix Tracks examples."""

    def __init__(self):
        self.examples_dir = pathlib.Path("examples/matrix_tracks")
        self.tools_dir = pathlib.Path("tools")
        self.parity_issues = []

    def check_verification_track_parity(self) -> dict[str, Any]:
        """Check verification track demo parity."""
        print("🔮 Checking verification track parity...")

        issues = []
        prism_model_path = self.examples_dir / "verification" / "demo_memory_cascade.pm"

        # Check PRISM model exists and is syntactically valid
        if not prism_model_path.exists():
            issues.append("PRISM demo model missing: demo_memory_cascade.pm")
        else:
            # Check if PRISM is available for validation
            prism_available = self._check_tool_availability("prism", ["--version"])

            if prism_available:
                # Run PRISM syntax check
                try:
                    result = subprocess.run(
                        ["prism", "-parseonly", str(prism_model_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        issues.append(f"PRISM model syntax error: {result.stderr}")
                except subprocess.TimeoutExpired:
                    issues.append("PRISM model validation timed out")
                except Exception as e:
                    issues.append(f"PRISM model validation failed: {e}")

        # Check demo script matches production model reference
        production_model_path = pathlib.Path("models/memory/cascade.pm")
        if production_model_path.exists():
            # Compare model structure/properties
            demo_content = prism_model_path.read_text() if prism_model_path.exists() else ""
            prod_content = production_model_path.read_text()

            # Check that key properties are consistent
            demo_has_safety_prop = '"safe_operation"' in demo_content or '"no_cascade"' in demo_content
            prod_has_safety_prop = '"safe_operation"' in prod_content or '"no_cascade"' in prod_content

            if demo_has_safety_prop != prod_has_safety_prop:
                issues.append("Demo and production PRISM models have inconsistent safety properties")

        return {
            "track": "verification",
            "status": "passing" if not issues else "failing",
            "issues": issues,
            "tools_checked": ["prism"],
            "prism_available": prism_available if 'prism_available' in locals() else False
        }

    def check_provenance_track_parity(self) -> dict[str, Any]:
        """Check provenance track demo parity."""
        print("🔗 Checking provenance track parity...")

        issues = []
        demo_script = self.examples_dir / "provenance" / "generate_car.sh"
        production_tool = self.tools_dir / "generate_car.py"

        # Check demo script uses production tool correctly
        if demo_script.exists() and production_tool.exists():
            demo_content = demo_script.read_text()

            # Verify demo calls production tool with correct arguments
            if f"python3 {production_tool.relative_to('.')}" not in demo_content and \
               "python3 ../../../tools/generate_car.py" not in demo_content:
                issues.append("Demo script doesn't call production generate_car.py tool")

            # Check production tool CLI interface
            try:
                result = subprocess.run(
                    ["python3", str(production_tool), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    help_text = result.stdout
                    required_args = ["--module", "--gates", "--attestation", "--verify"]

                    for arg in required_args:
                        if arg not in help_text:
                            issues.append(f"Production tool missing expected argument: {arg}")
                        elif arg not in demo_content:
                            # Only warn if arg is used in production but not demo
                            pass  # Demo might not use all args

                else:
                    issues.append(f"Production tool help failed: {result.stderr}")

            except Exception as e:
                issues.append(f"Could not check production tool interface: {e}")

            # Check demo sample data format
            sample_run_path = self.examples_dir / "provenance" / "sample_run.json"
            if sample_run_path.exists():
                try:
                    sample_data = json.loads(sample_run_path.read_text())

                    # Check required fields match production expectations
                    required_fields = ["@context", "module", "timestamp", "gates"]
                    for field in required_fields:
                        if field not in sample_data:
                            issues.append(f"Demo sample_run.json missing required field: {field}")

                except json.JSONDecodeError as e:
                    issues.append(f"Demo sample_run.json is invalid JSON: {e}")

        else:
            if not demo_script.exists():
                issues.append("Demo generate_car.sh script missing")
            if not production_tool.exists():
                issues.append("Production generate_car.py tool missing")

        return {
            "track": "provenance",
            "status": "passing" if not issues else "failing",
            "issues": issues,
            "tools_checked": ["generate_car.py"],
            "production_tool_available": production_tool.exists()
        }

    def check_attestation_track_parity(self) -> dict[str, Any]:
        """Check attestation track demo parity."""
        print("🛡️ Checking attestation track parity...")

        issues = []
        self.examples_dir / "attestation" / "verify_evidence.sh"
        production_tool = self.tools_dir / "collect_attestation.py"

        # Check evidence JWT format matches production
        evidence_path = self.examples_dir / "attestation" / "evidence_jwt.json"
        if evidence_path.exists():
            try:
                evidence_data = json.loads(evidence_path.read_text())

                # Check JWT structure
                required_jwt_fields = ["jwt_header", "jwt_payload", "jwt_signature"]
                for field in required_jwt_fields:
                    if field not in evidence_data:
                        issues.append(f"Demo evidence JWT missing field: {field}")

                # Check payload structure matches production
                payload = evidence_data.get("jwt_payload", {})
                required_payload_fields = ["iss", "sub", "iat", "exp", "software_components", "tee_evidence"]
                for field in required_payload_fields:
                    if field not in payload:
                        issues.append(f"Demo evidence JWT payload missing field: {field}")

            except json.JSONDecodeError as e:
                issues.append(f"Demo evidence JWT is invalid JSON: {e}")

        # Check policy format matches production expectations
        policy_path = self.examples_dir / "attestation" / "verifier_policy.json"
        rats_policy_path = pathlib.Path("rats/policy-v2.1.yaml")

        if policy_path.exists() and rats_policy_path.exists():
            try:
                demo_policy = json.loads(policy_path.read_text())

                # Check demo policy has required fields
                required_policy_fields = ["version", "required_claims", "enforcement"]
                for field in required_policy_fields:
                    if field not in demo_policy:
                        issues.append(f"Demo verifier policy missing field: {field}")

            except json.JSONDecodeError as e:
                issues.append(f"Demo verifier policy is invalid JSON: {e}")

        # Check production tool compatibility
        if production_tool.exists():
            try:
                result = subprocess.run(
                    ["python3", str(production_tool), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    help_text = result.stdout
                    expected_args = ["--module", "--output", "--tee", "--pretty"]

                    for arg in expected_args:
                        if arg not in help_text:
                            issues.append(f"Production attestation tool missing expected argument: {arg}")

                else:
                    issues.append(f"Production attestation tool help failed: {result.stderr}")

            except Exception as e:
                issues.append(f"Could not check production attestation tool: {e}")

        return {
            "track": "attestation",
            "status": "passing" if not issues else "failing",
            "issues": issues,
            "tools_checked": ["collect_attestation.py"],
            "production_tool_available": production_tool.exists()
        }

    def _check_tool_availability(self, tool_name: str, version_args: list[str]) -> bool:
        """Check if external tool is available."""
        try:
            result = subprocess.run(
                [tool_name, *version_args],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def run_parity_checks(self) -> dict[str, Any]:
        """Run all parity checks and generate report."""
        print("🔍 Running Matrix Tracks demo-production parity checks...\n")

        results = {}
        results["verification"] = self.check_verification_track_parity()
        results["provenance"] = self.check_provenance_track_parity()
        results["attestation"] = self.check_attestation_track_parity()

        # Calculate overall status
        all_passing = all(result["status"] == "passing" for result in results.values())
        overall_status = "passing" if all_passing else "failing"

        # Count issues
        total_issues = sum(len(result["issues"]) for result in results.values())

        summary = {
            "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
            "overall_status": overall_status,
            "total_issues": total_issues,
            "tracks": results,
            "recommendations": self._generate_recommendations(results)
        }

        return summary

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on parity check results."""
        recommendations = []

        for track_name, track_result in results.items():
            if track_result["status"] == "failing":
                recommendations.append(f"🔧 Fix {track_name} track parity issues:")
                for issue in track_result["issues"]:
                    recommendations.append(f"   - {issue}")

        if not recommendations:
            recommendations.append("✅ All demos maintain parity with production tools")

        recommendations.append("📚 Consider adding automated parity tests to CI")
        recommendations.append("🔄 Review demo content quarterly to prevent drift")

        return recommendations

    def generate_report(self, results: dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate parity check report."""
        if not output_path:
            output_path = "reports/demo_parity_report.md"

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Generate markdown report
        content = f"""# Matrix Tracks Demo-Production Parity Report

**Generated:** {results['timestamp']}
**Overall Status:** {"✅ PASSING" if results['overall_status'] == 'passing' else "❌ FAILING"}
**Total Issues:** {results['total_issues']}

---

## 📊 Track Results

"""

        for track_name, track_result in results["tracks"].items():
            status_emoji = "✅" if track_result["status"] == "passing" else "❌"

            content += f"""### {status_emoji} {track_name.title()} Track

**Status:** {track_result['status']}
**Issues:** {len(track_result['issues'])}

"""
            if track_result['issues']:
                content += "**Issues Found:**\n"
                for issue in track_result['issues']:
                    content += f"- {issue}\n"
                content += "\n"

        content += """---

## 🎯 Recommendations

"""
        for rec in results['recommendations']:
            content += f"{rec}\n"

        content += """
---

*This report ensures Matrix Tracks demos remain accurate representations of production capabilities.*
"""

        # Write report
        with open(output_path, 'w') as f:
            f.write(content)

        # Also save JSON
        json_path = output_path.replace('.md', '.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)

        return output_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Check Matrix Tracks demo-production parity")
    parser.add_argument("--output", help="Output path for report")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only")
    parser.add_argument("--fail-on-issues", action="store_true", help="Exit 1 if any parity issues found")

    args = parser.parse_args()

    checker = DemoParityChecker()
    results = checker.run_parity_checks()

    if args.json_only:
        print(json.dumps(results, indent=2))
    else:
        report_path = checker.generate_report(results, args.output)
        print(f"\n📄 Parity report saved to: {report_path}")
        print(f"📊 Overall Status: {'✅ PASSING' if results['overall_status'] == 'passing' else '❌ FAILING'}")

        if results['total_issues'] > 0:
            print(f"\n⚠️ Found {results['total_issues']} parity issue(s):")
            for track_name, track_result in results['tracks'].items():
                for issue in track_result['issues']:
                    print(f"   - {track_name}: {issue}")

    # Exit with error if requested and issues found
    if args.fail_on_issues and results['total_issues'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
