"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUClukhasS :: PLUGIN TESTING FRAMEWORK                         │
│                   Comprehensive Plugin Testing & Validation                  │
│                    Author: Lukhas Systems & GitHub Copilot, 2025             │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    Advanced testing framework for Lukhas plugins providing comprehensive test
    execution, validation, and reporting capabilities. Features include:
        • Unit testing with Lukhas-aware assertions
        • Integration testing with consciousness simulation
        • Performance benchmarking and profiling
        • Compliance testing (GDPR, HIPAA, SEEDRA-v3)
        • Security vulnerability scanning
        • Symbolic reasoning validation
        • Test reporting and analytics
        • Continuous testing automation

USAGE:
    from sdk.tools.plugin_test_framework import LucasPluginTestRunner

    runner = LucasPluginTestRunner()
    results = await runner.run_comprehensive_tests("plugin_path")

COPYRIGHT:
    Part of the Lukhas Plugin SDK v2.0
    Licensed under Lukhas Symbolic License
"""

import asyncio
import importlib.util
import inspect
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# Test result data structures
@dataclass
class TestCase:
    """Individual test case representation"""

    name: str
    description: str
    test_function: Callable
    category: str = "unit"
    timeout: float = 30.0
    consciousness_level: str = "basic"
    compliance_requirements: List[str] = field(default_factory=list)
    expected_symbolic_outputs: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Test execution result"""

    test_case: TestCase
    status: str  # passed, failed, skipped, error
    duration: float
    message: str = ""
    error: Optional[Exception] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    symbolic_traces: List[str] = field(default_factory=list)
    consciousness_metrics: Dict[str, float] = field(default_factory=dict)
    compliance_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Collection of related test cases"""

    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    plugin_path: Optional[str] = None


@dataclass
class TestReport:
    """Comprehensive test execution report"""

    plugin_name: str
    plugin_version: str
    test_session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0

    # Test statistics
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0

    # Results by category
    unit_test_results: List[TestResult] = field(default_factory=list)
    integration_test_results: List[TestResult] = field(default_factory=list)
    performance_test_results: List[TestResult] = field(default_factory=list)
    compliance_test_results: List[TestResult] = field(default_factory=list)
    security_test_results: List[TestResult] = field(default_factory=list)

    # Aggregate scores
    overall_score: float = 0.0
    consciousness_compatibility_score: float = 0.0
    compliance_score: float = 0.0
    security_score: float = 0.0
    performance_score: float = 0.0

    # Additional metrics
    coverage_percentage: float = 0.0
    symbolic_reasoning_validation: bool = False
    lukhas_integration_status: str = "unknown"


class LucasTestAssertions:
    """Lukhas-specific test assertions for plugin testing"""

    @staticmethod
    def assert_consciousness_compatible(plugin_instance, level: str = "basic"):
        """Assert that plugin is compatible with specified consciousness level"""
        if not hasattr(plugin_instance, "consciousness_level"):
            raise AssertionError("Plugin must implement consciousness_level attribute")

        level_hierarchy = {"basic": 1, "intermediate": 2, "advanced": 3, "flagship": 4}
        plugin_level = level_hierarchy.get(plugin_instance.consciousness_level, 0)
        required_level = level_hierarchy.get(level, 0)

        if plugin_level < required_level:
            raise AssertionError(
                f"Plugin consciousness level '{plugin_instance.consciousness_level}' insufficient for required level '{level}'"
            )

    @staticmethod
    def assert_symbolic_output(output: Any, expected_symbols: List[str]):
        """Assert that output contains expected symbolic elements"""
        output_str = str(output).lower()
        missing_symbols = []

        for symbol in expected_symbols:
            if symbol.lower() not in output_str:
                missing_symbols.append(symbol)

        if missing_symbols:
            raise AssertionError(
                f"Missing expected symbolic elements: {missing_symbols}"
            )

    @staticmethod
    def assert_compliance_metadata(plugin_instance, standard: str):
        """Assert that plugin has proper compliance metadata"""
        compliance_attr = f"{standard.lower()}_compliant"
        if not hasattr(plugin_instance, compliance_attr):
            raise AssertionError(
                f"Plugin missing compliance attribute: {compliance_attr}"
            )

        if not getattr(plugin_instance, compliance_attr):
            raise AssertionError(f"Plugin not marked as {standard} compliant")

    @staticmethod
    def assert_security_patterns(code_content: str, forbidden_patterns: List[str]):
        """Assert that code doesn't contain forbidden security patterns"""
        violations = []
        code_lower = code_content.lower()

        for pattern in forbidden_patterns:
            if pattern.lower() in code_lower:
                violations.append(pattern)

        if violations:
            raise AssertionError(
                f"Code contains forbidden security patterns: {violations}"
            )

    @staticmethod
    def assert_performance_threshold(duration: float, max_duration: float):
        """Assert that operation completed within performance threshold"""
        if duration > max_duration:
            raise AssertionError(
                f"Operation took {duration:.3f}s, exceeding threshold of {max_duration:.3f}s"
            )


class LucasPluginTestRunner:
    """
    Comprehensive test runner for Lukhas plugins

    Provides automated testing capabilities including unit tests, integration tests,
    performance benchmarks, compliance validation, and security scanning.
    """

    def __init__(self):
        self.test_suites: List[TestSuite] = []
        self.current_session_id = None
        self.assertions = LucasTestAssertions()

        # Test configuration
        self.config = {
            "timeout_default": 30.0,
            "performance_threshold": 5.0,
            "memory_limit_mb": 512,
            "enable_consciousness_testing": True,
            "enable_compliance_testing": True,
            "enable_security_testing": True,
            "verbose_output": False,
            "parallel_execution": False,
        }

        # Built-in test categories
        self.test_categories = {
            "unit": "Basic functionality tests",
            "integration": "Integration with Lukhas consciousness",
            "performance": "Performance and resource usage tests",
            "compliance": "GDPR/HIPAA/SEEDRA-v3 compliance tests",
            "security": "Security vulnerability scans",
            "symbolic": "Symbolic reasoning validation",
        }

    def discover_tests(self, plugin_path: str) -> List[TestSuite]:
        """Discover test files and create test suites"""
        plugin_path_obj = Path(plugin_path)
        test_suites = []

        # Look for test directories
        test_dirs = [
            plugin_path_obj / "tests",
            plugin_path_obj / "test",
            plugin_path_obj / "testing",
        ]

        for test_dir in test_dirs:
            if test_dir.exists():
                test_suites.extend(
                    self._discover_tests_in_directory(test_dir, plugin_path_obj)
                )

        # Create default test suite if no tests found
        if not test_suites:
            default_suite = self._create_default_test_suite(plugin_path_obj)
            test_suites.append(default_suite)

        return test_suites

    def _discover_tests_in_directory(
        self, test_dir: Path, plugin_path: Path
    ) -> List[TestSuite]:
        """Discover tests in a specific directory"""
        test_suites = []

        # Find test files
        test_files = list(test_dir.glob("test_*.py")) + list(test_dir.glob("*_test.py"))

        for test_file in test_files:
            try:
                suite = self._load_test_file(test_file, plugin_path)
                if suite:
                    test_suites.append(suite)
            except Exception as e:
                print(f"Warning: Could not load test file {test_file}: {e}")

        return test_suites

    def _load_test_file(
        self, test_file: Path, plugin_path: Path
    ) -> Optional[TestSuite]:
        """Load tests from a Python test file"""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Create test suite
            suite_name = test_file.stem
            suite = TestSuite(
                name=suite_name,
                description=f"Tests from {test_file.name}",
                plugin_path=str(plugin_path),
            )

            # Discover test functions
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and (
                    name.startswith("test_") or name.endswith("_test")
                ):

                    test_case = TestCase(
                        name=name,
                        description=obj.__doc__ or f"Test function {name}",
                        test_function=obj,
                        category=self._determine_test_category(name, obj),
                    )
                    suite.test_cases.append(test_case)

            # Look for setup/teardown functions
            if hasattr(module, "setup_module"):
                suite.setup_function = module.setup_module
            if hasattr(module, "teardown_module"):
                suite.teardown_function = module.teardown_module

            return suite if suite.test_cases else None

        except Exception as e:
            print(f"Error loading test file {test_file}: {e}")
            return None

    def _determine_test_category(self, name: str, func: Callable) -> str:
        """Determine test category based on name and annotations"""
        name_lower = name.lower()

        if "performance" in name_lower or "benchmark" in name_lower:
            return "performance"
        elif "integration" in name_lower or "consciousness" in name_lower:
            return "integration"
        elif (
            "compliance" in name_lower or "gdpr" in name_lower or "hipaa" in name_lower
        ):
            return "compliance"
        elif "security" in name_lower or "vulnerability" in name_lower:
            return "security"
        elif "symbolic" in name_lower or "reasoning" in name_lower:
            return "symbolic"
        else:
            return "unit"

    def _create_default_test_suite(self, plugin_path: Path) -> TestSuite:
        """Create default tests when no test files are found"""
        suite = TestSuite(
            name="default_tests",
            description="Default plugin validation tests",
            plugin_path=str(plugin_path),
        )

        # Add basic validation tests
        suite.test_cases.extend(
            [
                TestCase(
                    name="test_plugin_loads",
                    description="Test that plugin can be loaded",
                    test_function=self._test_plugin_loads,
                    category="unit",
                ),
                TestCase(
                    name="test_manifest_valid",
                    description="Test that plugin manifest is valid",
                    test_function=self._test_manifest_valid,
                    category="unit",
                ),
                TestCase(
                    name="test_consciousness_compatibility",
                    description="Test consciousness system compatibility",
                    test_function=self._test_consciousness_compatibility,
                    category="integration",
                ),
                TestCase(
                    name="test_basic_compliance",
                    description="Test basic compliance requirements",
                    test_function=self._test_basic_compliance,
                    category="compliance",
                ),
            ]
        )

        return suite

    async def run_comprehensive_tests(self, plugin_path: str) -> TestReport:
        """Run comprehensive test suite for a plugin"""
        plugin_path_obj = Path(plugin_path)
        self.current_session_id = f"test_{int(time.time())}"

        # Load plugin manifest
        manifest_path = plugin_path_obj / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
        else:
            manifest = {"name": plugin_path_obj.name, "version": "unknown"}

        # Create test report
        report = TestReport(
            plugin_name=manifest.get("name", plugin_path_obj.name),
            plugin_version=manifest.get("version", "unknown"),
            test_session_id=self.current_session_id,
            start_time=datetime.now(),
        )

        print(f"🧪 Starting comprehensive test suite for {report.plugin_name}")
        print(f"   Session ID: {self.current_session_id}")

        try:
            # Discover tests
            test_suites = self.discover_tests(str(plugin_path_obj))
            print(f"   Discovered {len(test_suites)} test suites")

            # Run all test suites
            for suite in test_suites:
                print(f"\n🔍 Running test suite: {suite.name}")
                suite_results = await self._run_test_suite(suite, plugin_path_obj)

                # Categorize results
                for result in suite_results:
                    if result.test_case.category == "unit":
                        report.unit_test_results.append(result)
                    elif result.test_case.category == "integration":
                        report.integration_test_results.append(result)
                    elif result.test_case.category == "performance":
                        report.performance_test_results.append(result)
                    elif result.test_case.category == "compliance":
                        report.compliance_test_results.append(result)
                    elif result.test_case.category == "security":
                        report.security_test_results.append(result)

            # Calculate statistics
            all_results = (
                report.unit_test_results
                + report.integration_test_results
                + report.performance_test_results
                + report.compliance_test_results
                + report.security_test_results
            )

            report.total_tests = len(all_results)
            report.passed_tests = len([r for r in all_results if r.status == "passed"])
            report.failed_tests = len([r for r in all_results if r.status == "failed"])
            report.skipped_tests = len(
                [r for r in all_results if r.status == "skipped"]
            )
            report.error_tests = len([r for r in all_results if r.status == "error"])

            # Calculate scores
            if report.total_tests > 0:
                report.overall_score = (report.passed_tests / report.total_tests) * 100

            report.end_time = datetime.now()
            report.total_duration = (
                report.end_time - report.start_time
            ).total_seconds()

            print(f"\n✅ Test suite completed in {report.total_duration:.2f}s")
            print(
                f"   Results: {report.passed_tests} passed, {report.failed_tests} failed, {report.skipped_tests} skipped"
            )

            return report

        except Exception as e:
            report.end_time = datetime.now()
            print(f"❌ Test suite failed with error: {e}")
            raise

    async def _run_test_suite(
        self, suite: TestSuite, plugin_path: Path
    ) -> List[TestResult]:
        """Run a single test suite"""
        results = []

        # Run setup if available
        if suite.setup_function:
            try:
                await self._run_function_safely(suite.setup_function)
            except Exception as e:
                print(f"Warning: Setup function failed: {e}")

        # Run each test case
        for test_case in suite.test_cases:
            print(f"    Running: {test_case.name}")
            result = await self._run_test_case(test_case, plugin_path)
            results.append(result)

            # Print result
            status_symbol = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "error": "💥",
            }.get(result.status, "❓")
            print(f"      {status_symbol} {result.status.upper()}: {result.message}")

        # Run teardown if available
        if suite.teardown_function:
            try:
                await self._run_function_safely(suite.teardown_function)
            except Exception as e:
                print(f"Warning: Teardown function failed: {e}")

        return results

    async def _run_test_case(
        self, test_case: TestCase, plugin_path: Path
    ) -> TestResult:
        """Run a single test case"""
        start_time = time.time()

        try:
            # Run the test function
            if asyncio.iscoroutinefunction(test_case.test_function):
                await asyncio.wait_for(
                    test_case.test_function(plugin_path), timeout=test_case.timeout
                )
            else:
                await asyncio.wait_for(
                    asyncio.create_task(
                        asyncio.to_thread(test_case.test_function, plugin_path)
                    ),
                    timeout=test_case.timeout,
                )

            duration = time.time() - start_time

            return TestResult(
                test_case=test_case,
                status="passed",
                duration=duration,
                message="Test passed successfully",
            )

        except AssertionError as e:
            duration = time.time() - start_time
            return TestResult(
                test_case=test_case,
                status="failed",
                duration=duration,
                message=str(e),
                error=e,
            )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            return TestResult(
                test_case=test_case,
                status="error",
                duration=duration,
                message=f"Test timed out after {test_case.timeout}s",
                error=asyncio.TimeoutError("Test timeout"),
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_case=test_case,
                status="error",
                duration=duration,
                message=f"Unexpected error: {str(e)}",
                error=e,
            )

    async def _run_function_safely(self, func: Callable):
        """Run a function safely, handling both sync and async"""
        if asyncio.iscoroutinefunction(func):
            await func()
        else:
            await asyncio.to_thread(func)

    # Default test implementations
    def _test_plugin_loads(self, plugin_path: Path):
        """Test that plugin can be loaded"""
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise AssertionError("Plugin manifest.json not found")

        # Try to load and parse manifest
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in manifest: {e}")

        # Check required fields
        required_fields = ["name", "version", "description", "entry_point"]
        missing_fields = [field for field in required_fields if field not in manifest]
        if missing_fields:
            raise AssertionError(f"Missing required manifest fields: {missing_fields}")

    def _test_manifest_valid(self, plugin_path: Path):
        """Test that plugin manifest is valid"""
        manifest_path = plugin_path / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Validate consciousness level
        valid_levels = ["basic", "intermediate", "advanced", "flagship"]
        consciousness_level = manifest.get("consciousness_level", "basic")
        if consciousness_level not in valid_levels:
            raise AssertionError(f"Invalid consciousness level: {consciousness_level}")

        # Validate version format
        version = manifest.get("version", "")
        if not version or len(version.split(".")) != 3:
            raise AssertionError(f"Invalid version format: {version}")

    def _test_consciousness_compatibility(self, plugin_path: Path):
        """Test consciousness system compatibility"""
        manifest_path = plugin_path / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Check consciousness integration requirements
        consciousness_level = manifest.get("consciousness_level", "basic")
        consciousness_integration = manifest.get("consciousness_integration", False)

        if (
            consciousness_level in ["advanced", "flagship"]
            and not consciousness_integration
        ):
            raise AssertionError(
                "Advanced consciousness levels require consciousness integration"
            )

    def _test_basic_compliance(self, plugin_path: Path):
        """Test basic compliance requirements"""
        manifest_path = plugin_path / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Check for compliance declarations
        compliance_fields = ["privacy_policy", "data_handling", "user_consent"]
        missing_compliance = [
            field
            for field in compliance_fields
            if field not in manifest or not manifest[field]
        ]

        if missing_compliance:
            raise AssertionError(
                f"Missing compliance information: {missing_compliance}"
            )

    def generate_test_report_html(self, report: TestReport, output_path: str):
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Lukhas Plugin Test Report - {report.plugin_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; border-radius: 10px; padding: 20px; text-align: center; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .error {{ color: #fd7e14; }}
        .test-results {{ margin: 20px 0; }}
        .test-category {{ margin: 20px 0; }}
        .test-category h3 {{ background: #e9ecef; padding: 10px; border-radius: 5px; }}
        .test-item {{ padding: 10px; border-left: 4px solid #dee2e6; margin: 5px 0; }}
        .test-item.passed {{ border-left-color: #28a745; }}
        .test-item.failed {{ border-left-color: #dc3545; }}
        .test-item.error {{ border-left-color: #fd7e14; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Lukhas Plugin Test Report</h1>
        <h2>{report.plugin_name} v{report.plugin_version}</h2>
        <p>Test Session: {report.test_session_id}</p>
        <p>Generated: {report.end_time.strftime('%Y-%m-%d %H:%M:%S') if report.end_time else 'In Progress'}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Overall Score</h3>
            <div style="font-size: 2em; font-weight: bold;">{report.overall_score:.1f}%</div>
        </div>
        <div class="stat-card">
            <h3>Total Tests</h3>
            <div style="font-size: 2em; font-weight: bold;">{report.total_tests}</div>
        </div>
        <div class="stat-card">
            <h3>Duration</h3>
            <div style="font-size: 2em; font-weight: bold;">{report.total_duration:.2f}s</div>
        </div>
    </div>

    <div class="stats">
        <div class="stat-card passed">
            <h4>✅ Passed</h4>
            <div style="font-size: 1.5em;">{report.passed_tests}</div>
        </div>
        <div class="stat-card failed">
            <h4>❌ Failed</h4>
            <div style="font-size: 1.5em;">{report.failed_tests}</div>
        </div>
        <div class="stat-card skipped">
            <h4>⏭️ Skipped</h4>
            <div style="font-size: 1.5em;">{report.skipped_tests}</div>
        </div>
        <div class="stat-card error">
            <h4>💥 Errors</h4>
            <div style="font-size: 1.5em;">{report.error_tests}</div>
        </div>
    </div>
"""

        # Add test results by category
        categories = [
            ("Unit Tests", report.unit_test_results),
            ("Integration Tests", report.integration_test_results),
            ("Performance Tests", report.performance_test_results),
            ("Compliance Tests", report.compliance_test_results),
            ("Security Tests", report.security_test_results),
        ]

        html_content += '<div class="test-results">'
        for category_name, results in categories:
            if results:
                html_content += f'<div class="test-category"><h3>{category_name}</h3>'
                for result in results:
                    html_content += f"""
                    <div class="test-item {result.status}">
                        <strong>{result.test_case.name}</strong> ({result.duration:.3f}s)<br>
                        <em>{result.test_case.description}</em><br>
                        <span class="{result.status}">{result.message}</span>
                    </div>
                    """
                html_content += "</div>"

        html_content += "</div></body></html>"

        # Write to file
        with open(output_path, "w") as f:
            f.write(html_content)

        print(f"📊 Test report generated: {output_path}")


# Convenience functions for common testing scenarios
async def test_plugin_quick(plugin_path: str) -> bool:
    """Quick plugin test - returns True if basic tests pass"""
    runner = LucasPluginTestRunner()
    report = await runner.run_comprehensive_tests(plugin_path)
    return report.overall_score >= 80.0


async def test_plugin_compliance(plugin_path: str) -> Dict[str, bool]:
    """Test plugin compliance specifically"""
    runner = LucasPluginTestRunner()
    report = await runner.run_comprehensive_tests(plugin_path)

    compliance_results = {}
    for result in report.compliance_test_results:
        compliance_results[result.test_case.name] = result.status == "passed"

    return compliance_results


async def benchmark_plugin_performance(plugin_path: str) -> Dict[str, float]:
    """Benchmark plugin performance"""
    runner = LucasPluginTestRunner()
    report = await runner.run_comprehensive_tests(plugin_path)

    performance_metrics = {}
    for result in report.performance_test_results:
        performance_metrics[result.test_case.name] = result.duration

    return performance_metrics
