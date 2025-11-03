#!/usr/bin/env python3
"""
T4 Quality Gate Validator for LUKHAS AI Multi-Agent Coordination
================================================================

Comprehensive validation system that ensures all T4 agent contributions
meet the Demis Hassabis standard for rigorous testing and quality assurance.

This validator runs:
- Security vulnerability scanning
- Acceptance gate validation
- Comprehensive test suite execution
- Performance benchmarking
- Quality metrics calculation
- Audit compliance verification

Usage:
    python tools/t4_quality_gate_validator.py [--mode={full|security|audit}]

Author: LUKHAS AI Testing & DevOps Specialist (Agent #3)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
RESULTS_DIR = REPO_ROOT / "out" / "t4_validation"
AUDIT_DIR = REPO_ROOT / "audit"


class T4QualityGateValidator:
    """T4 Quality Gate Validator implementing Demis Hassabis standards."""

    def __init__(self, mode: str = "full"):
        self.mode = mode
        self.start_time = datetime.now(timezone.utc)
        self.results = {
            "metadata": {
                "validator_version": "1.0.0",
                "validation_mode": mode,
                "start_time": self.start_time.isoformat(),
                "agent": "Agent #3 - Testing & DevOps Specialist",
                "standard": "Demis Hassabis (Rigorous Validation)}",
            },
            "quality_gates": {},
            "test_execution": {},
            "security_validation": {},
            "performance_metrics": {},
            "audit_compliance": {},
            "overall_status": "PENDING",
        }

        # Ensure output directories exist
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    def run_command(self, command: list[str], description: str) -> tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr."""
        print(f"🔧 {description}...")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=600,  # 10 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out after 600 seconds"
        except Exception as e:
            return False, "", str(e)

    def validate_environment_setup(self) -> bool:
        """Validate that environment is properly configured for testing."""
        print("🌍 Validating environment setup...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 11):
            print(f"❌ Python version {python_version} < 3.11")
            return False

        # Check required files exist
        required_files = [
            "pytest.ini",
            "requirements.txt",
            "requirements-test.txt",
            "tools/acceptance_gate_ast.py",
        ]

        for file_path in required_files:
            if not (REPO_ROOT / file_path).exists():
                print(f"❌ Required file missing: {file_path}")
                return False

        # Check pytest is available
        success, _, _ = self.run_command(["python", "-m", "pytest", "--version"], "Check pytest availability")
        if not success:
            print("❌ pytest not available")
            return False

        print("✅ Environment setup validated")
        return True

    def run_acceptance_gate_validation(self) -> bool:
        """Run AST-based acceptance gate validation."""
        print("🛡️ Running acceptance gate validation...")

        success, stdout, stderr = self.run_command(
            ["python", "tools/acceptance_gate_ast.py"], "AST-based acceptance gate scan"
        )

        # Check if audit report was generated
        audit_report_path = AUDIT_DIR / "acceptance_gate_audit.json"
        if audit_report_path.exists():
            with open(audit_report_path) as f:
                audit_data = json.load(f)
                self.results["audit_compliance"]["acceptance_gate"] = audit_data

        if success:
            print("✅ Acceptance gate validation PASSED")
        else:
            print("❌ Acceptance gate validation FAILED")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

        return success

    def run_security_validation(self) -> bool:
        """Run comprehensive security validation."""
        print("🔒 Running security validation...")

        # Run security-focused tests
        success, _stdout, _stderr = self.run_command(
            [
                "python",
                "-m",
                "pytest",
                "tests/test_comprehensive_security_validation.py",
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={RESULTS_DIR / 'security-report.json'}",
            ],
            "Security validation tests",
        )

        # Parse security test results
        security_report_path = RESULTS_DIR / "security-report.json"
        if security_report_path.exists():
            with open(security_report_path) as f:
                security_data = json.load(f)
                self.results["security_validation"]["test_results"] = security_data

        # Run authentication tests
        auth_success, _, _ = self.run_command(
            ["python", "-m", "pytest", "tests/security/", "-v", "--tb=short"],
            "Authentication security tests",
        )

        overall_success = success and auth_success

        if overall_success:
            print("✅ Security validation PASSED")
        else:
            print("❌ Security validation FAILED")

        return overall_success

    def run_comprehensive_test_suite(self) -> bool:
        """Run the comprehensive test suite."""
        print("🧪 Running comprehensive test suite...")

        # Run all tests with coverage
        success, _stdout, stderr = self.run_command(
            [
                "python",
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--cov=lukhas",
                "--cov=candidate",
                "--cov=tools",
                "--cov-report=json:" + str(RESULTS_DIR / "coverage.json"),
                "--cov-report=html:" + str(RESULTS_DIR / "coverage-html"),
                "--json-report",
                f"--json-report-file={RESULTS_DIR / 'test-report.json'}",
            ],
            "Comprehensive test suite",
        )

        # Parse test results
        test_report_path = RESULTS_DIR / "test-report.json"
        if test_report_path.exists():
            with open(test_report_path) as f:
                test_data = json.load(f)
                self.results["test_execution"]["comprehensive_results"] = test_data

        # Parse coverage results
        coverage_report_path = RESULTS_DIR / "coverage.json"
        if coverage_report_path.exists():
            with open(coverage_report_path) as f:
                coverage_data = json.load(f)
                self.results["test_execution"]["coverage_results"] = coverage_data

        if success:
            print("✅ Comprehensive test suite PASSED")
        else:
            print("❌ Comprehensive test suite FAILED")
            print(f"stderr: {stderr}")

        return success

    def run_performance_benchmarks(self) -> bool:
        """Run performance benchmarks."""
        print("⚡ Running performance benchmarks...")

        # Run performance tests if they exist
        perf_test_files = list(REPO_ROOT.glob("tests/**/test_*performance*.py"))

        if not perf_test_files:
            print("ℹ️  No performance tests found, skipping...")
            return True

        success, _stdout, _stderr = self.run_command(
            [
                "python",
                "-m",
                "pytest",
                "--benchmark-only",
                "--benchmark-json=" + str(RESULTS_DIR / "benchmark-report.json"),
            ]
            + [str(f) for f in perf_test_files],
            "Performance benchmarks",
        )

        if success:
            print("✅ Performance benchmarks PASSED")
        else:
            print("❌ Performance benchmarks FAILED")

        return success

    def calculate_quality_metrics(self) -> dict:
        """Calculate comprehensive quality metrics."""
        print("📊 Calculating quality metrics...")

        metrics = {
            "test_metrics": {},
            "security_metrics": {},
            "coverage_metrics": {},
            "quality_scores": {},
        }

        # Test execution metrics
        if "comprehensive_results" in self.results["test_execution"]:
            test_data = self.results["test_execution"]["comprehensive_results"]
            summary = test_data.get("summary", {})

            total_tests = summary.get("total", 0)
            passed_tests = summary.get("passed", 0)
            failed_tests = summary.get("failed", 0)

            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            metrics["test_metrics"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate_percentage": round(pass_rate, 2),
            }

        # Coverage metrics
        if "coverage_results" in self.results["test_execution"]:
            coverage_data = self.results["test_execution"]["coverage_results"]
            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

            metrics["coverage_metrics"] = {"total_coverage_percentage": round(total_coverage, 2)}

        # Security metrics
        if "test_results" in self.results["security_validation"]:
            security_data = self.results["security_validation"]["test_results"]
            security_summary = security_data.get("summary", {})

            security_total = security_summary.get("total", 0)
            security_passed = security_summary.get("passed", 0)
            security_failed = security_summary.get("failed", 0)

            security_pass_rate = (security_passed / security_total * 100) if security_total > 0 else 0

            metrics["security_metrics"] = {
                "total_security_tests": security_total,
                "security_tests_passed": security_passed,
                "security_tests_failed": security_failed,
                "security_pass_rate_percentage": round(security_pass_rate, 2),
            }

        # Quality scores (T4 standards)
        test_score = min(metrics["test_metrics"].get("pass_rate_percentage", 0) / 95 * 100, 100)
        coverage_score = min(metrics["coverage_metrics"].get("total_coverage_percentage", 0) / 95 * 100, 100)
        security_score = min(metrics["security_metrics"].get("security_pass_rate_percentage", 0) / 95 * 100, 100)

        overall_score = (test_score + coverage_score + security_score) / 3

        metrics["quality_scores"] = {
            "test_quality_score": round(test_score, 2),
            "coverage_quality_score": round(coverage_score, 2),
            "security_quality_score": round(security_score, 2),
            "overall_quality_score": round(overall_score, 2),
        }

        return metrics

    def evaluate_quality_gates(self, metrics: dict) -> bool:
        """Evaluate T4 quality gates."""
        print("🎯 Evaluating T4 quality gates...")

        gates = {
            "test_pass_rate": {
                "target": 95.0,
                "actual": metrics["test_metrics"].get("pass_rate_percentage", 0),
                "status": "PENDING",
            },
            "test_coverage": {
                "target": 95.0,
                "actual": metrics["coverage_metrics"].get("total_coverage_percentage", 0),
                "status": "PENDING",
            },
            "security_compliance": {
                "target": 0,  # Zero security test failures
                "actual": metrics["security_metrics"].get("security_tests_failed", 0),
                "status": "PENDING",
            },
            "minimum_test_count": {
                "target": 30,
                "actual": metrics["test_metrics"].get("total_tests", 0),
                "status": "PENDING",
            },
        }

        all_gates_passed = True

        for gate_name, gate_data in gates.items():
            if gate_name == "security_compliance":
                # For security, we want actual <= target (zero failures)
                passed = gate_data["actual"] <= gate_data["target"]
            else:
                # For others, we want actual >= target
                passed = gate_data["actual"] >= gate_data["target"]

            gate_data["status"] = "PASSED" if passed else "FAILED"

            if passed:
                print(
                    f"✅ {gate_name}: {gate_data['actual']} {'<=' if gate_name == 'security_compliance' else '>='} {gate_data['target']}"
                )
            else:
                print(
                    f"❌ {gate_name}: {gate_data['actual']} {'>' if gate_name == 'security_compliance' else '<'} {gate_data['target']}"
                )
                all_gates_passed = False

        self.results["quality_gates"] = gates
        return all_gates_passed

    def generate_final_report(self, metrics: dict, gates_passed: bool) -> None:
        """Generate final validation report."""
        print("📋 Generating final validation report...")

        self.results["performance_metrics"] = metrics
        self.results["overall_status"] = "PASSED" if gates_passed else "FAILED"
        self.results["metadata"]["end_time"] = datetime.now(timezone.utc).isoformat()
        self.results["metadata"]["duration_seconds"] = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        # Save comprehensive report
        report_path = RESULTS_DIR / f"t4_validation_report_{int(time.time())}.json"
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_path = RESULTS_DIR / "t4_validation_summary.json"
        summary = {
            "timestamp": self.results["metadata"]["end_time"],
            "status": self.results["overall_status"],
            "quality_scores": metrics.get("quality_scores", {}),
            "quality_gates": {k: v["status"] for k, v in self.results["quality_gates"].items()},
            "test_summary": metrics.get("test_metrics", {}),
            "security_summary": metrics.get("security_metrics", {}),
            "coverage_summary": metrics.get("coverage_metrics", {}),
        }

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"📊 Comprehensive report: {report_path}")
        print(f"📋 Summary report: {summary_path}")

    def run_validation(self) -> bool:
        """Run the complete T4 quality gate validation."""
        print("=" * 80)
        print("🚀 T4 Quality Gate Validator")
        print("   Agent #3 - Testing & DevOps Specialist")
        print("   Standard: Demis Hassabis (Rigorous Validation)")
        print(f"   Mode: {self.mode}")
        print("=" * 80)

        try:
            # Step 1: Environment validation
            if not self.validate_environment_setup():
                print("❌ Environment validation failed")
                return False

            # Step 2: Acceptance gate validation
            if self.mode in ["full", "audit"] and not self.run_acceptance_gate_validation():
                print("❌ Acceptance gate validation failed")
                if self.mode == "audit":
                    return False

            # Step 3: Security validation
            if self.mode in ["full", "security"] and not self.run_security_validation():
                print("❌ Security validation failed")
                # Continue for now, as we expect some security issues during audit

            # Step 4: Comprehensive test suite
            if self.mode in ["full"] and not self.run_comprehensive_test_suite():
                print("❌ Comprehensive test suite failed")
                # Continue to generate metrics

            # Step 5: Performance benchmarks
            if self.mode in ["full"]:
                self.run_performance_benchmarks()  # Non-blocking

            # Step 6: Calculate metrics and evaluate gates
            metrics = self.calculate_quality_metrics()
            gates_passed = self.evaluate_quality_gates(metrics)

            # Step 7: Generate final report
            self.generate_final_report(metrics, gates_passed)

            # Final status
            if gates_passed:
                print("\n🎉 T4 QUALITY GATE VALIDATION PASSED")
                print(
                    f"   Overall Quality Score: {metrics.get('quality_scores', {}).get('overall_quality_score', 0):.2f}/100"
                )
                return True
            else:
                print("\n❌ T4 QUALITY GATE VALIDATION FAILED")
                print("   Review failed quality gates above")
                return False

        except Exception as e:
            print(f"\n💥 Validation failed with exception: {e}")
            self.results["overall_status"] = "ERROR"
            self.results["error"] = str(e)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="T4 Quality Gate Validator")
    parser.add_argument(
        "--mode",
        choices=["full", "security", "audit"],
        default="full",
        help="Validation mode (default: full)",
    )

    args = parser.parse_args()

    validator = T4QualityGateValidator(mode=args.mode)
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
