#!/usr/bin/env python3
"""
Test Report Generator for LUKHAS Test Suite
Generates KNOWN_ISSUES.md and TEST_STATUS.md from pytest results
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class TestReportGenerator:
    def __init__(self, test_dir: Path = Path("tests")):
        self.test_dir = test_dir
        self.results = {}
        self.known_issues = []

    def run_tests(self) -> dict:
        """Run pytest and collect results in JSON format"""
        print("🔍 Running test suite...")

        cmd = [
            "pytest",
            str(self.test_dir),
            "--json-report",
            "--json-report-file=test_results.json",
            "--tb=short",
            "--disable-warnings",
            "-q",
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Load JSON results
            with open("test_results.json") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not run tests with JSON output: {e}")
            return self._run_simple_tests()

    def _run_simple_tests(self) -> dict:
        """Fallback: Run tests with simple output parsing"""
        cmd = [
            "pytest",
            str(self.test_dir),
            "--tb=no",
            "-v",
            "--co",
        ]  # Collect only for quick analysis

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse output
        lines = result.stdout.split("\n")
        tests = []
        for line in lines:
            if "::" in line and "test_" in line:
                tests.append(line.strip())

        return {
            "summary": {"total": len(tests), "passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "tests": [{"nodeid": t} for t in tests],
        }

    def parse_failures(self, results: dict) -> list[dict]:
        """Extract failure information from test results"""
        failures = []

        for test in results.get("tests", []):
            if test.get("outcome") in ["failed", "error"]:
                failure = {
                    "test_path": test.get("nodeid", "").split("::")[0],
                    "test_name": "::".join(test.get("nodeid", "").split("::")[1:]),
                    "outcome": test.get("outcome"),
                    "error": self._extract_error(test),
                    "duration": test.get("duration", 0),
                }
                failures.append(failure)

        return failures

    def _extract_error(self, test: dict) -> str:
        """Extract error message from test result"""
        if "call" in test and "longrepr" in test["call"]:
            return str(test["call"]["longrepr"])[:200]
        return "Error details not available"

    def categorize_issue(self, failure: dict) -> tuple[str, str]:
        """Categorize issue by priority and type"""
        test_path = failure["test_path"]

        # Priority mapping
        if "compliance" in test_path or "consent" in test_path:
            priority = "P1"
        elif "ethics" in test_path or "governance" in test_path:
            priority = "P2"
        elif "integration" in test_path:
            priority = "P1" if "mcp" in test_path else "P2"
        else:
            priority = "P3"

        # Type mapping
        if "integration" in test_path:
            issue_type = "integration"
        elif "unit" in test_path:
            issue_type = "unit-test"
        elif "e2e" in test_path:
            issue_type = "e2e-test"
        else:
            issue_type = "test"

        return priority, issue_type

    def generate_known_issues(self, failures: list[dict]) -> str:
        """Generate KNOWN_ISSUES.md content"""

        issues = []
        for i, failure in enumerate(failures, 1):
            priority, issue_type = self.categorize_issue(failure)

            issue = f"""
### ISSUE-{i:03d}: {failure["test_name"].replace("::", " - ")}
**Component:** `{failure["test_path"]}`
**Status:** 🔴 Open
**Priority:** {priority}
**Labels:** `{issue_type}`, `auto-generated`

**Error:**
```
{failure["error"]}
```

**Next Steps:**
1. Investigate root cause
2. Implement fix
3. Update test if needed

---
"""
            issues.append(issue)

        return "\n".join(issues)

    def generate_status_dashboard(self, results: dict) -> str:
        """Generate TEST_STATUS.md content"""

        summary = results.get("summary", {})

        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0) + summary.get("errors", 0)
        skipped = summary.get("skipped", 0)

        pass_rate = (passed / total * 100) if total > 0 else 0

        status = f"""# LUKHAS Test Suite Status Dashboard

> Auto-generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 📊 Overall Health

```
Total Tests:     {total}
Passing:         {passed}  {"█" * int(pass_rate / 5)}{"░" * (20 - int(pass_rate / 5))} {pass_rate:.1f}%
Failing:         {failed}  {"█" * int(failed * 20 / max(total, 1))}{"░" * (20 - int(failed * 20 / max(total, 1)))} {failed / max(total, 1) * 100:.1f}%
Skipped:         {skipped}  {"█" * int(skipped * 20 / max(total, 1))}{"░" * (20 - int(skipped * 20 / max(total, 1)))} {skipped / max(total, 1) * 100:.1f}%
```

## Test Results by Category

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | {passed} | {pass_rate:.1f}% |
| ❌ Failed | {failed} | {failed / max(total, 1) * 100:.1f}% |
| ⚠️ Skipped | {skipped} | {skipped / max(total, 1) * 100:.1f}% |

## Recent Test Run

- **Duration:** {results.get("duration", "N/A")}s
- **Platform:** {sys.platform}
- **Python:** {sys.version.split()[0]}
- **Timestamp:** {datetime.now().isoformat()}
"""
        return status

    def write_reports(self):
        """Generate and write all report files"""
        print("📊 Generating test reports...")

        # Run tests and get results
        results = self.run_tests()
        failures = self.parse_failures(results)

        # Generate reports
        if failures:
            issues_content = self.generate_known_issues(failures)
            with open(self.test_dir / "KNOWN_ISSUES_AUTO.md", "w") as f:
                f.write("# Auto-Generated Known Issues\n\n")
                f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write(issues_content)
            print(f"✅ Generated KNOWN_ISSUES_AUTO.md with {len(failures)} issues")

        status_content = self.generate_status_dashboard(results)
        with open(self.test_dir / "TEST_STATUS_AUTO.md", "w") as f:
            f.write(status_content)
        print("✅ Generated TEST_STATUS_AUTO.md")

        # Summary
        summary = results.get("summary", {})
        print("\n📈 Test Summary:")
        print(f"   Total: {summary.get('total', 0)}")
        print(f"   Passed: {summary.get('passed', 0)}")
        print(f"   Failed: {summary.get('failed', 0)}")
        print(f"   Errors: {summary.get('errors', 0)}")
        print(f"   Skipped: {summary.get('skipped', 0)}")


if __name__ == "__main__":
    generator = TestReportGenerator()
    generator.write_reports()
