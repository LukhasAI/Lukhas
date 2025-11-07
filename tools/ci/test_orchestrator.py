#!/usr/bin/env python3
"""
Test Orchestrator for LUKHAS AI - Intelligent Test Selection and Execution
Implements tiered testing strategy with risk-based test selection
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class TestTier(Enum):
    """Test execution tiers based on speed and criticality."""

    SMOKE = "smoke"  # < 30 seconds - Critical path only
    FAST = "fast"  # < 5 minutes - Unit + Tier1 integration
    STANDARD = "standard"  # < 20 minutes - Full standard suite
    ADVANCED = "advanced"  # < 45 minutes - 0.001% methodologies
    COMPREHENSIVE = "comprehensive"  # No time limit - Full coverage


@dataclass
class TestSelection:
    """Represents a selected set of tests with execution metadata."""

    tier: TestTier
    test_files: list[Path]
    test_markers: list[str]
    estimated_duration: int  # seconds
    risk_score: float
    reasoning: str


@dataclass
class TestResult:
    """Test execution result with performance and coverage data."""

    tier: TestTier
    success: bool
    duration: int
    coverage_percent: float
    failures: list[str]
    performance_data: dict[str, float]
    advanced_metrics: Optional[dict[str, any]] = None


class IntelligentTestOrchestrator:
    """Orchestrates test execution based on change analysis and risk assessment."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.test_history = self._load_test_history()

        # Test tier configurations
        self.tier_configs = {
            TestTier.SMOKE: {"timeout": 30, "markers": ["smoke", "tier1"], "max_failures": 1, "required_coverage": 0.0},
            TestTier.FAST: {
                "timeout": 300,
                "markers": ["unit", "tier1", "smoke"],
                "max_failures": 3,
                "required_coverage": 0.60,
            },
            TestTier.STANDARD: {
                "timeout": 1200,
                "markers": ["unit", "integration", "tier1"],
                "max_failures": 10,
                "required_coverage": 0.75,
            },
            TestTier.ADVANCED: {
                "timeout": 2700,
                "markers": [
                    "property_based",
                    "chaos_engineering",
                    "metamorphic",
                    "formal_verification",
                    "mutation_testing",
                    "performance_regression",
                ],
                "max_failures": 5,
                "required_coverage": 0.85,
            },
            TestTier.COMPREHENSIVE: {
                "timeout": None,
                "markers": ["all"],
                "max_failures": None,
                "required_coverage": 0.90,
            },
        }

        # Risk weights for different file types
        self.risk_weights = {
            "consciousness": 1.0,  # Highest risk
            "memory": 0.9,
            "identity": 0.9,
            "security": 0.95,
            "oauth": 0.8,
            "api": 0.7,
            "utils": 0.3,
            "tests": 0.1,
        }

    def _load_test_history(self) -> dict[str, any]:
        """Load historical test execution data for intelligent selection."""
        history_file = self.base_path / "reports" / "test_history.json"
        if history_file.exists():
            try:
                with open(history_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"executions": [], "failure_patterns": {}, "performance_trends": {}}

    def analyze_code_changes(self, base_ref: str = "origin/main") -> tuple[list[Path], float]:
        """Analyze git changes to determine test selection and risk score."""
        try:
            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_ref}...HEAD"], capture_output=True, text=True, check=True
            )

            changed_files = [
                Path(line.strip()) for line in result.stdout.splitlines() if line.strip() and line.endswith(".py")
            ]

            # Calculate risk score based on changed files
            risk_score = 0.0
            for file_path in changed_files:
                path_str = str(file_path).lower()
                for component, weight in self.risk_weights.items():
                    if component in path_str:
                        risk_score = max(risk_score, weight)
                        break
                else:
                    risk_score = max(risk_score, 0.5)  # Default risk

            return changed_files, risk_score

        except subprocess.CalledProcessError:
            # If git comparison fails, assume high risk
            print("⚠️ Could not analyze git changes, defaulting to high risk")
            return [], 1.0

    def select_tests_for_tier(self, tier: TestTier, changed_files: list[Path], risk_score: float) -> TestSelection:
        """Select appropriate tests for the given tier based on changes and risk."""
        config = self.tier_configs[tier]

        # Base test selection logic
        if tier == TestTier.SMOKE:
            test_files = self._get_smoke_tests()
            reasoning = "Critical path validation only"

        elif tier == TestTier.FAST:
            test_files = self._get_unit_tests()
            if risk_score > 0.7:
                test_files.extend(self._get_integration_tests_for_files(changed_files))
            reasoning = f"Unit tests + selective integration (risk: {risk_score:.2f})"

        elif tier == TestTier.STANDARD:
            test_files = self._get_standard_test_suite()
            reasoning = "Full standard test suite"

        elif tier == TestTier.ADVANCED:
            test_files = self._get_advanced_test_suite()
            # Focus advanced tests on changed areas if high risk
            if risk_score > 0.8:
                test_files = self._filter_advanced_tests_by_risk(test_files, changed_files)
            reasoning = f"0.001% methodologies (focused on risk areas: {risk_score:.2f})"

        else:  # COMPREHENSIVE
            test_files = self._get_all_tests()
            reasoning = "Complete test coverage"

        # Estimate duration based on history
        estimated_duration = self._estimate_duration(test_files, tier)

        return TestSelection(
            tier=tier,
            test_files=test_files,
            test_markers=config["markers"],
            estimated_duration=estimated_duration,
            risk_score=risk_score,
            reasoning=reasoning,
        )

    def _get_smoke_tests(self) -> list[Path]:
        """Get critical smoke tests that must always pass."""
        smoke_tests = []
        test_dirs = [self.base_path / "tests" / "smoke", self.base_path / "tests" / "contract"]

        for test_dir in test_dirs:
            if test_dir.exists():
                smoke_tests.extend(test_dir.glob("test_*.py"))

        return smoke_tests

    def _get_unit_tests(self) -> list[Path]:
        """Get all unit tests."""
        unit_test_dir = self.base_path / "tests" / "unit"
        if unit_test_dir.exists():
            return list(unit_test_dir.rglob("test_*.py"))
        return []

    def _get_integration_tests_for_files(self, changed_files: list[Path]) -> list[Path]:
        """Get integration tests relevant to changed files."""
        integration_tests = []
        integration_dir = self.base_path / "tests" / "integration"

        if not integration_dir.exists():
            return []

        # Map changed files to relevant integration tests
        for changed_file in changed_files:
            # Extract component name from path
            path_parts = changed_file.parts
            if "lukhas" in path_parts or "labs" in path_parts:
                try:
                    component_idx = next(i for i, part in enumerate(path_parts) if part in ["lukhas", "labs"])
                    if component_idx + 1 < len(path_parts):
                        component = path_parts[component_idx + 1]

                        # Look for integration tests for this component
                        component_tests = integration_dir.glob(f"*{component}*test*.py")
                        integration_tests.extend(component_tests)

                        # Also look in subdirectories
                        component_dir = integration_dir / component
                        if component_dir.exists():
                            integration_tests.extend(component_dir.glob("test_*.py"))
                except (StopIteration, IndexError):
                    continue

        return list(set(integration_tests))  # Remove duplicates

    def _get_standard_test_suite(self) -> list[Path]:
        """Get the standard test suite (unit + integration + contract)."""
        tests = []
        for test_type in ["unit", "integration", "contract"]:
            test_dir = self.base_path / "tests" / test_type
            if test_dir.exists():
                tests.extend(test_dir.rglob("test_*.py"))
        return tests

    def _get_advanced_test_suite(self) -> list[Path]:
        """Get the 0.001% advanced testing suite."""
        advanced_tests = []

        # Advanced test directories
        advanced_dirs = [
            self.base_path / "rl" / "tests",
            self.base_path / "tests" / "advanced",
            self.base_path / "tests" / "consciousness",
        ]

        for test_dir in advanced_dirs:
            if test_dir.exists():
                advanced_tests.extend(test_dir.glob("test_*.py"))

        return advanced_tests

    def _filter_advanced_tests_by_risk(self, test_files: list[Path], changed_files: list[Path]) -> list[Path]:
        """Filter advanced tests to focus on high-risk areas."""
        if not changed_files:
            return test_files

        # Extract components from changed files
        changed_components = set()
        for file_path in changed_files:
            path_str = str(file_path).lower()
            for component in self.risk_weights:
                if component in path_str:
                    changed_components.add(component)

        # Filter tests that target changed components
        relevant_tests = []
        for test_file in test_files:
            test_str = str(test_file).lower()
            if any(component in test_str for component in changed_components):
                relevant_tests.append(test_file)

        # Always include consciousness tests if any high-risk changes
        consciousness_tests = [t for t in test_files if "consciousness" in str(t).lower()]
        return list(set(relevant_tests + consciousness_tests))

    def _get_all_tests(self) -> list[Path]:
        """Get all available tests."""
        all_tests = []
        test_root = self.base_path / "tests"
        if test_root.exists():
            all_tests.extend(test_root.rglob("test_*.py"))

        # Include RL tests
        rl_tests = self.base_path / "rl" / "tests"
        if rl_tests.exists():
            all_tests.extend(rl_tests.glob("test_*.py"))

        return all_tests

    def _estimate_duration(self, test_files: list[Path], tier: TestTier) -> int:
        """Estimate test execution duration based on historical data."""
        # Base estimates (seconds per test file)
        base_estimates = {
            TestTier.SMOKE: 2,
            TestTier.FAST: 10,
            TestTier.STANDARD: 30,
            TestTier.ADVANCED: 120,
            TestTier.COMPREHENSIVE: 180,
        }

        base_duration = len(test_files) * base_estimates.get(tier, 60)

        # Check historical data for more accurate estimates
        for execution in self.test_history.get("executions", [])[-5:]:  # Last 5 runs
            if execution.get("tier") == tier.value:
                historical_duration = execution.get("duration", 0)
                if historical_duration > 0:
                    # Use weighted average of historical and base estimate
                    return int(0.7 * historical_duration + 0.3 * base_duration)

        return base_duration

    def execute_test_selection(self, selection: TestSelection) -> TestResult:
        """Execute the selected tests and return results."""
        print(f"🧪 Executing {selection.tier.value} tests")
        print(f"   📁 Files: {len(selection.test_files)}")
        print(f"   ⏱️  Estimated: {selection.estimated_duration}s")
        print(f"   🎯 Risk: {selection.risk_score:.2f}")
        print(f"   💭 Reasoning: {selection.reasoning}")

        start_time = time.time()

        # Build pytest command
        cmd = ["python", "-m", "pytest", "-v", "--tb=short", "--disable-warnings"]

        # Add timeout if specified
        config = self.tier_configs[selection.tier]
        if config["timeout"]:
            cmd.extend(["--timeout", str(config["timeout"])])

        # Add markers
        if selection.test_markers and selection.test_markers != ["all"]:
            marker_expr = " or ".join(selection.test_markers)
            cmd.extend(["-m", marker_expr])

        # Add coverage for standard+ tiers
        if selection.tier in [TestTier.STANDARD, TestTier.ADVANCED, TestTier.COMPREHENSIVE]:
            cmd.extend(
                [
                    "--cov=lukhas",
                    "--cov=candidate",
                    "--cov=MATRIZ",
                    "--cov-report=xml:reports/coverage.xml",
                    "--cov-report=term-missing",
                ]
            )

        # Add test files or directories
        if selection.test_files:
            cmd.extend([str(f) for f in selection.test_files])
        else:
            cmd.append("tests/")

        # Add JUnit XML output
        cmd.extend(["--junitxml=reports/junit.xml"])

        try:
            # Execute tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=config["timeout"] if config["timeout"] else None,
            )

            duration = int(time.time() - start_time)
            success = result.returncode == 0

            # Parse coverage if available
            coverage_percent = self._parse_coverage()

            # Parse failures
            failures = self._parse_failures(result.stdout, result.stderr)

            # Collect performance data for advanced tiers
            performance_data = {}
            if selection.tier in [TestTier.ADVANCED, TestTier.COMPREHENSIVE]:
                performance_data = self._collect_performance_metrics()

            test_result = TestResult(
                tier=selection.tier,
                success=success,
                duration=duration,
                coverage_percent=coverage_percent,
                failures=failures,
                performance_data=performance_data,
            )

            # Store result in history
            self._update_test_history(selection, test_result)

            return test_result

        except subprocess.TimeoutExpired:
            print(f"⏰ Test execution timed out after {config['timeout']}s")
            return TestResult(
                tier=selection.tier,
                success=False,
                duration=config["timeout"],
                coverage_percent=0.0,
                failures=[f"Test execution timed out after {config['timeout']}s"],
                performance_data={},
            )
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return TestResult(
                tier=selection.tier,
                success=False,
                duration=0,
                coverage_percent=0.0,
                failures=[str(e)],
                performance_data={},
            )

    def _parse_coverage(self) -> float:
        """Parse coverage percentage from coverage report."""
        coverage_file = self.base_path / "reports" / "coverage.xml"
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(coverage_file)
                root = tree.getroot()
                line_rate = root.attrib.get("line-rate", "0")
                return float(line_rate) * 100
            except Exception:
                pass
        return 0.0

    def _parse_failures(self, stdout: str, stderr: str) -> list[str]:
        """Parse test failures from pytest output."""
        failures = []

        # Look for FAILED indicators in stdout
        for line in stdout.split("\n"):
            if "FAILED" in line and "::" in line:
                failures.append(line.strip())

        # Check stderr for critical errors
        if stderr and "ERROR" in stderr:
            failures.append(f"STDERR: {stderr[:200]}...")

        return failures[:10]  # Limit to first 10 failures

    def _collect_performance_metrics(self) -> dict[str, float]:
        """Collect performance metrics from test execution."""
        metrics = {}

        # Check for benchmark results
        benchmark_file = self.base_path / "reports" / "benchmark.json"
        if benchmark_file.exists():
            try:
                with open(benchmark_file) as f:
                    data = json.load(f)
                if "benchmarks" in data:
                    for benchmark in data["benchmarks"]:
                        metrics[f"benchmark_{benchmark['name']}"] = benchmark["stats"]["mean"]
            except Exception:
                pass

        return metrics

    def _update_test_history(self, selection: TestSelection, result: TestResult):
        """Update test execution history for future optimization."""
        execution_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tier": selection.tier.value,
            "duration": result.duration,
            "success": result.success,
            "coverage": result.coverage_percent,
            "test_count": len(selection.test_files),
            "risk_score": selection.risk_score,
        }

        self.test_history["executions"].append(execution_record)

        # Keep only last 50 executions
        self.test_history["executions"] = self.test_history["executions"][-50:]

        # Save updated history
        history_file = self.base_path / "reports" / "test_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        with open(history_file, "w") as f:
            json.dump(self.test_history, f, indent=2)


def main():
    """Main test orchestrator entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AI Intelligent Test Orchestrator")
    parser.add_argument(
        "--tier", type=str, choices=[t.value for t in TestTier], default="fast", help="Test tier to execute"
    )
    parser.add_argument("--base-ref", default="origin/main", help="Base reference for change analysis")
    parser.add_argument("--force-all", action="store_true", help="Force execution of all tests in tier")

    args = parser.parse_args()

    orchestrator = IntelligentTestOrchestrator()
    tier = TestTier(args.tier)

    print("🎯 LUKHAS AI Intelligent Test Orchestrator")
    print("=" * 50)
    print(f"🎪 Tier: {tier.value}")
    print(f"📊 Base: {args.base_ref}")

    # Analyze changes unless forced
    if args.force_all:
        changed_files, risk_score = [], 1.0
        print("🔥 Force mode: Executing all tests")
    else:
        print("🔍 Analyzing code changes...")
        changed_files, risk_score = orchestrator.analyze_code_changes(args.base_ref)
        print(f"   📁 Changed files: {len(changed_files)}")
        print(f"   ⚠️  Risk score: {risk_score:.2f}")

    # Select tests
    print("🎯 Selecting tests for execution...")
    selection = orchestrator.select_tests_for_tier(tier, changed_files, risk_score)

    # Execute tests
    result = orchestrator.execute_test_selection(selection)

    # Report results
    print("\n📋 Test Execution Summary")
    print("-" * 30)
    print(f"✅ Success: {result.success}")
    print(f"⏱️  Duration: {result.duration}s")
    print(f"📊 Coverage: {result.coverage_percent:.1f}%")
    print(f"❌ Failures: {len(result.failures)}")

    if result.failures:
        print("\n🔴 Failures:")
        for failure in result.failures[:5]:
            print(f"   • {failure}")

    if result.performance_data:
        print("\n📈 Performance Metrics:")
        for metric, value in result.performance_data.items():
            print(f"   • {metric}: {value:.3f}s")

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
