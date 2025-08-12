#!/usr/bin/env python3
"""
LUKHAS AI Test Runner with Metadata Validation
Ensures all tests comply with Trinity Framework requirements
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class TestMetadataRunner:
    """Test runner with metadata validation for Trinity Framework compliance"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "trinity_framework": "⚛️🧠🛡️",
            "metadata_validation": "required",
            "tests": {},
            "summary": {},
            "validation_report": {}
        }

    def validate_test_metadata(self, test_file: Path) -> Dict[str, Any]:
        """Validate test file has proper metadata"""
        validation = {
            "file": str(test_file),
            "has_metadata": False,
            "trinity_compliant": False,
            "guardian_approved": False,
            "issues": []
        }

        try:
            with open(test_file) as f:
                content = f.read()

                # Check for metadata markers
                if "@pytest.mark.metadata" in content:
                    validation["has_metadata"] = True
                else:
                    validation["issues"].append("Missing @pytest.mark.metadata decorator")

                # Check Trinity Framework compliance
                if any(marker in content for marker in ["@pytest.mark.trinity", "trinity_framework"]):
                    validation["trinity_compliant"] = True
                else:
                    validation["issues"].append("Missing Trinity Framework markers")

                # Check Guardian approval
                if any(marker in content for marker in ["@pytest.mark.guardian", "guardian_approved"]):
                    validation["guardian_approved"] = True
                else:
                    validation["issues"].append("Missing Guardian System approval")

        except Exception as e:
            validation["issues"].append(f"Error reading file: {e}")

        return validation

    def run_tests(self, test_path: str = "tests/") -> int:
        """Run pytest with metadata validation and reporting"""
        print("🧪 LUKHAS AI Test Runner with Metadata Validation")
        print("⚛️🧠🛡️ Trinity Framework Compliance Check\n")

        # First, validate all test files
        print("📋 Validating test metadata...")
        test_files = list(Path(test_path).rglob("test_*.py"))

        for test_file in test_files:
            validation = self.validate_test_metadata(test_file)
            self.report["validation_report"][str(test_file)] = validation

            if validation["issues"]:
                print(f"⚠️  {test_file.name}: {', '.join(validation['issues'])}")
            else:
                print(f"✅ {test_file.name}: All metadata present")

        # Run pytest with JSON report
        print("\n🔬 Running tests...")
        json_report = self.results_dir / f"pytest_report_{self.timestamp}.json"
        html_report = self.results_dir / f"pytest_report_{self.timestamp}.html"

        cmd = [
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            f"--json-report-file={json_report}",
            f"--html={html_report}",
            "--self-contained-html",
            "--maxfail=10",
            "-ra"
        ]

        # Run pytest
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse results
        self.parse_pytest_output(result.stdout, result.stderr)

        # Generate final report
        self.generate_report()

        return result.returncode

    def parse_pytest_output(self, stdout: str, stderr: str):
        """Parse pytest output for test results"""
        lines = stdout.split('\n')

        # Extract summary statistics
        for line in lines:
            if "passed" in line and "failed" in line:
                # Parse summary line
                parts = line.split()
                for i, part in enumerate(parts):
                    if "passed" in part and i > 0:
                        self.report["summary"]["passed"] = int(parts[i-1])
                    if "failed" in part and i > 0:
                        self.report["summary"]["failed"] = int(parts[i-1])

            # Capture individual test results
            if "PASSED" in line or "FAILED" in line:
                test_name = line.split("::")[1] if "::" in line else line
                status = "PASSED" if "PASSED" in line else "FAILED"
                self.report["tests"][test_name] = {"status": status}

    def generate_report(self):
        """Generate comprehensive test report with metadata"""
        # Calculate statistics
        total_tests = len(self.report["tests"])
        passed = sum(1 for t in self.report["tests"].values() if t["status"] == "PASSED")
        failed = total_tests - passed

        # Metadata validation stats
        total_validated = len(self.report["validation_report"])
        fully_compliant = sum(
            1 for v in self.report["validation_report"].values()
            if not v["issues"]
        )

        # Update summary
        self.report["summary"].update({
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "metadata_compliant": fully_compliant,
            "metadata_total": total_validated,
            "compliance_rate": f"{(fully_compliant/total_validated*100):.1f}%" if total_validated > 0 else "0%"
        })

        # Save JSON report
        report_file = self.results_dir / f"test_report_{self.timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)

        # Generate markdown report
        self.generate_markdown_report()

        # Print summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        print("⚛️🧠🛡️ Trinity Framework: ACTIVE")
        print(f"📅 Timestamp: {self.report['timestamp']}")
        print(f"\n✅ Tests Passed: {passed}/{total_tests}")
        print(f"❌ Tests Failed: {failed}/{total_tests}")
        print(f"📈 Pass Rate: {self.report['summary']['pass_rate']}")
        print(f"\n📋 Metadata Compliance: {fully_compliant}/{total_validated}")
        print(f"📈 Compliance Rate: {self.report['summary']['compliance_rate']}")
        print(f"\n📁 Report saved to: {report_file}")

    def generate_markdown_report(self):
        """Generate markdown report for README"""
        md_file = self.results_dir / f"test_report_{self.timestamp}.md"

        with open(md_file, 'w') as f:
            f.write("# LUKHAS AI Test Report\n\n")
            f.write(f"**Generated**: {self.report['timestamp']}\n")
            f.write("**Trinity Framework**: ⚛️🧠🛡️ Active\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Total Tests**: {self.report['summary'].get('total_tests', 0)}\n")
            f.write(f"- **Passed**: {self.report['summary'].get('passed', 0)}\n")
            f.write(f"- **Failed**: {self.report['summary'].get('failed', 0)}\n")
            f.write(f"- **Pass Rate**: {self.report['summary'].get('pass_rate', '0%')}\n")
            f.write(f"- **Metadata Compliance**: {self.report['summary'].get('compliance_rate', '0%')}\n\n")

            f.write("## Test Results\n\n")
            f.write("| Test | Status | Metadata |\n")
            f.write("|------|--------|----------|\n")

            for test_name, result in self.report["tests"].items():
                status_icon = "✅" if result["status"] == "PASSED" else "❌"
                f.write(f"| {test_name} | {status_icon} {result['status']} | - |\n")

            f.write("\n## Metadata Validation\n\n")
            f.write("| File | Trinity | Guardian | Issues |\n")
            f.write("|------|---------|----------|--------|\n")

            for file_path, validation in self.report["validation_report"].items():
                trinity = "✅" if validation["trinity_compliant"] else "❌"
                guardian = "✅" if validation["guardian_approved"] else "❌"
                issues = len(validation["issues"])
                f.write(f"| {Path(file_path).name} | {trinity} | {guardian} | {issues} |\n")

        print(f"📝 Markdown report saved to: {md_file}")
        return md_file

if __name__ == "__main__":
    runner = TestMetadataRunner()
    exit_code = runner.run_tests()
    sys.exit(exit_code)
