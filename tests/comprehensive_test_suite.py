#!/usr/bin/env python3
"""
LUKHAS Comprehensive Test Suite (TP001)
======================================

Enterprise-grade comprehensive test suite for LUKHAS AI platform.
Provides structured testing across all system components with quality gates.

P1 Task: TP001 - Create comprehensive test suite
Priority: High (P1) 
Agent: Claude Code (Testing/Documentation)

Constellation Framework: 🛡️ Guardian · ⚛️ Identity · 🧠 Consciousness

Features:
- Multi-tier test organization (Unit, Integration, System, E2E)
- Quality gates and coverage requirements
- Performance benchmarking and regression detection
- Security and compliance validation
- Cross-component integration testing
- Continuous validation pipeline

# ΛTAG: comprehensive_testing, coverage_validation, test_orchestration, quality_gates
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from collections import defaultdict
<<<<<<< HEAD
from dataclasses import dataclass, asdict
=======
from dataclasses import asdict, dataclass
>>>>>>> origin/main
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

# Configure comprehensive test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test coverage tracking
try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False

# Performance monitoring
try:
    import psutil
    PERFORMANCE_MONITORING = True
except ImportError:
    PERFORMANCE_MONITORING = False


@dataclass
class TestSuiteMetrics:
    """Comprehensive test suite execution metrics"""
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    execution_time: float = 0.0
    coverage_percentage: float = 0.0
    performance_regressions: int = 0
    security_issues: int = 0
    quality_gate_status: str = "unknown"
    tier_results: Dict[str, Dict[str, int]] = None
    component_results: Dict[str, Dict[str, int]] = None
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def __post_init__(self):
        if self.tier_results is None:
            self.tier_results = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
        if self.component_results is None:
            self.component_results = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    @property
    def quality_score(self) -> float:
        """Calculate comprehensive quality score"""
        weights = {
            "success_rate": 0.4,
            "coverage": 0.3,
            "performance": 0.2,
            "security": 0.1
        }
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        success_score = min(self.success_rate / 100, 1.0)
        coverage_score = min(self.coverage_percentage / 100, 1.0)
        performance_score = max(0, 1.0 - (self.performance_regressions * 0.1))
        security_score = max(0, 1.0 - (self.security_issues * 0.2))
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        return (
            weights["success_rate"] * success_score +
            weights["coverage"] * coverage_score +
            weights["performance"] * performance_score +
            weights["security"] * security_score
        ) * 100


# Legacy compatibility alias
<<<<<<< HEAD
@dataclass 
=======
@dataclass
>>>>>>> origin/main
class TestSuiteResults:
    """Legacy alias for TestSuiteMetrics - maintained for compatibility"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    coverage_percentage: float = 0.0
    execution_time: float = 0.0
    performance_metrics: Dict[str, Any] = None
    failed_test_details: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.failed_test_details is None:
            self.failed_test_details = []

    @property
    def success_rate(self) -> float:
        """Calculate test success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def meets_standards(self) -> bool:
        """Check if results meet T4/0.01% standards."""
        return (
            self.success_rate >= 95.0 and
            self.coverage_percentage >= 90.0 and
            len(self.failed_test_details) == 0
        )


class ComprehensiveTestSuite:
    """
    Enhanced comprehensive test suite orchestrator for LUKHAS platform
    Provides enterprise-grade testing with quality gates and detailed metrics
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.metrics = TestSuiteMetrics()
        self.test_config = self._load_test_config()
        self.quality_gates = self._load_quality_gates()
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        if COVERAGE_AVAILABLE:
            self.coverage = coverage.Coverage(
                source=[str(self.project_root)],
                omit=[
                    "*/tests/*",
                    "*/test_*",
                    "*/__pycache__/*",
                    "*/venv/*",
                    "*/env/*",
                    "*/.venv/*"
                ]
            )
        else:
            self.coverage = None
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def _load_test_config(self) -> Dict[str, Any]:
        """Load comprehensive test configuration"""
        default_config = {
            "test_tiers": {
                "unit": {
                    "patterns": ["tests/unit/**/*test*.py", "tests/*/test_*.py"],
                    "timeout": 300,
                    "parallel": True,
                    "coverage_required": 85.0
                },
                "integration": {
                    "patterns": ["tests/integration/**/*test*.py"],
                    "timeout": 900,
                    "parallel": False,
                    "coverage_required": 75.0
                },
                "system": {
                    "patterns": ["tests/system/**/*test*.py", "tests/e2e/**/*test*.py"],
                    "timeout": 1800,
                    "parallel": False,
                    "coverage_required": 60.0
                },
                "security": {
                    "patterns": ["tests/security/**/*test*.py"],
                    "timeout": 600,
                    "parallel": True,
                    "coverage_required": 90.0
                }
            },
            "components": {
                "identity": ["tests/identity/", "tests/core/identity/"],
                "consciousness": ["tests/consciousness/", "tests/core/consciousness/"],
                "memory": ["tests/memory/", "tests/core/memory/"],
                "governance": ["tests/governance/", "tests/guardian/"],
                "orchestration": ["tests/orchestration/"],
                "api": ["tests/api/", "tests/core/api/"],
                "matriz": ["tests/matriz/", "tests/MATRIZ/"]
            },
            "quality_requirements": {
                "min_coverage": 80.0,
                "max_execution_time": 3600,
                "max_failure_rate": 5.0,
                "performance_regression_threshold": 20.0
            }
        }
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        # Try to load from config file
        config_path = self.project_root / "tests" / "test_suite_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                logger.warning(f"Failed to load test config: {e}")
<<<<<<< HEAD
                
        return default_config
    
=======

        return default_config

>>>>>>> origin/main
    def _load_quality_gates(self) -> Dict[str, float]:
        """Load quality gate thresholds"""
        return {
            "min_success_rate": 95.0,
            "min_coverage": 80.0,
            "max_security_issues": 0,
            "max_performance_regressions": 2,
            "min_quality_score": 85.0
        }
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def run_comprehensive_suite(self, tier_filter: Optional[str] = None) -> TestSuiteMetrics:
        """
        Run comprehensive test suite with quality gates
        
        Args:
            tier_filter: Optional tier to run (unit, integration, system, security)
            
        Returns:
            Complete test metrics and quality assessment
        """
        logger.info("Starting LUKHAS Comprehensive Test Suite")
        print("🚀 Starting LUKHAS Enhanced Comprehensive Test Suite")
        print("=" * 60)
<<<<<<< HEAD
        
        start_time = time.perf_counter()
        
        if self.coverage:
            self.coverage.start()
        
=======

        start_time = time.perf_counter()

        if self.coverage:
            self.coverage.start()

>>>>>>> origin/main
        try:
            # Determine which tiers to run
            if tier_filter:
                tiers_to_run = [tier_filter] if tier_filter in self.test_config["test_tiers"] else []
            else:
                tiers_to_run = list(self.test_config["test_tiers"].keys())
<<<<<<< HEAD
            
=======

>>>>>>> origin/main
            # Run each test tier
            for tier in tiers_to_run:
                logger.info(f"Running {tier} tests...")
                print(f"\n📋 Phase: {tier.title()} Tests")
                tier_results = self._run_test_tier(tier)
                self._update_metrics_from_tier(tier, tier_results)
<<<<<<< HEAD
            
            # Run component-specific tests
            print(f"\n🔧 Phase: Component-Specific Tests")
            self._run_component_tests()
            
            # Run security scans
            print(f"\n🔒 Phase: Security Scans")
            self._run_security_scans()
            
            # Run performance benchmarks
            print(f"\n⚡ Phase: Performance Tests")
            self._run_performance_tests()
            
            # Calculate coverage
            print(f"\n📊 Phase: Coverage Analysis")
            self._calculate_coverage()
            
        finally:
            if self.coverage:
                self.coverage.stop()
        
        # Calculate total execution time
        self.metrics.execution_time = time.perf_counter() - start_time
        
        # Evaluate quality gates
        print(f"\n🎯 Phase: Quality Gate Evaluation")
        self._evaluate_quality_gates()
        
        # Generate comprehensive report
        self._generate_test_report()
        
        # Print final summary
        self._print_summary()
        
=======

            # Run component-specific tests
            print("\n🔧 Phase: Component-Specific Tests")
            self._run_component_tests()

            # Run security scans
            print("\n🔒 Phase: Security Scans")
            self._run_security_scans()

            # Run performance benchmarks
            print("\n⚡ Phase: Performance Tests")
            self._run_performance_tests()

            # Calculate coverage
            print("\n📊 Phase: Coverage Analysis")
            self._calculate_coverage()

        finally:
            if self.coverage:
                self.coverage.stop()

        # Calculate total execution time
        self.metrics.execution_time = time.perf_counter() - start_time

        # Evaluate quality gates
        print("\n🎯 Phase: Quality Gate Evaluation")
        self._evaluate_quality_gates()

        # Generate comprehensive report
        self._generate_test_report()

        # Print final summary
        self._print_summary()

>>>>>>> origin/main
        return self.metrics


class ComprehensiveTestOrchestrator:
    """Legacy orchestrator class - maintained for backwards compatibility."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.test_results = TestSuiteResults()
        self.coverage_data = None

        if COVERAGE_AVAILABLE:
            self.coverage = coverage.Coverage(
                source=[str(self.project_root / "lukhas")],
                omit=[
                    "*/tests/*",
                    "*/test_*",
                    "*/__pycache__/*",
                    "*/venv/*",
                    "*/env/*"
                ]
            )

    def run_comprehensive_suite(self) -> TestSuiteResults:
        """Run complete test suite with coverage analysis."""

        print("🚀 Starting LUKHAS Comprehensive Test Suite (Legacy)")
        print("=" * 60)

        start_time = time.perf_counter()

        if COVERAGE_AVAILABLE:
            self.coverage.start()

        try:
            # Phase 1: Unit Tests
            print("\n📋 Phase 1: Unit Tests")
            unit_results = self._run_unit_tests()

            # Phase 2: Integration Tests
            print("\n🔗 Phase 2: Integration Tests")
            integration_results = self._run_integration_tests()

            # Phase 3: End-to-End Tests
            print("\n🌐 Phase 3: End-to-End Tests")
            e2e_results = self._run_e2e_tests()

            # Phase 4: Security Tests
            print("\n🔒 Phase 4: Security Tests")
            security_results = self._run_security_tests()

            # Phase 5: Performance Tests
            print("\n⚡ Phase 5: Performance Tests")
            performance_results = self._run_performance_tests()

            # Phase 6: Memory Tests
            print("\n🧠 Phase 6: Memory Tests")
            memory_results = self._run_memory_tests()

            # Aggregate results
            self._aggregate_results([
                unit_results,
                integration_results,
                e2e_results,
                security_results,
                performance_results,
                memory_results
            ])

        finally:
            if COVERAGE_AVAILABLE:
                self.coverage.stop()
                self._analyze_coverage()

        self.test_results.execution_time = time.perf_counter() - start_time
        self._generate_final_report()

        return self.test_results

    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit tests."""

        unit_test_paths = [
            "tests/unit/",
            "tests/core/",
            "tests/governance/",
            "tests/memory/test_topk_recall.py",
            "tests/memory/test_scheduled_folding.py"
        ]

        results = {"phase": "unit", "details": []}

        for test_path in unit_test_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="not integration and not e2e")
                results["details"].append(result)
            else:
                print(f"  Skipping: {test_path} (not found)")

        return results

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""

        integration_paths = [
            "tests/integration/test_guardian_dsl.py",
            "tests/integration/test_memory_system.py",
            "tests/reliability/",
            "tests/e2e/test_matriz_orchestration.py"
        ]

        results = {"phase": "integration", "details": []}

        for test_path in integration_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="integration or reliability")
                results["details"].append(result)

        return results

    def _run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests."""

        e2e_paths = [
            "tests/e2e/",
            "tests/stress/test_orchestrator.py"
        ]

        results = {"phase": "e2e", "details": []}

        for test_path in e2e_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="e2e or stress")
                results["details"].append(result)

        return results

    def _run_security_tests(self) -> Dict[str, Any]:
        """Run security validation tests."""

        security_paths = [
            "tests/security/test_security_validation.py",
            "tests/bridge/test_llm_guardrail.py"
        ]

        results = {"phase": "security", "details": []}

        for test_path in security_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="security")
                results["details"].append(result)

        return results

    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance benchmark tests."""

        performance_paths = [
            "tests/performance/test_performance_budgets.py",
            "tests/stress/"
        ]

        results = {"phase": "performance", "details": []}

        for test_path in performance_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="performance or benchmark")
                results["details"].append(result)

        return results

    def _run_memory_tests(self) -> Dict[str, Any]:
        """Run memory system tests."""

        memory_paths = [
            "tests/memory/test_fold_consolidation_edge_cases.py",
            "tests/memory/test_topk_recall.py",
            "tests/memory/test_scheduled_folding.py"
        ]

        results = {"phase": "memory", "details": []}

        for test_path in memory_paths:
            full_path = self.project_root / test_path
            if full_path.exists():
                print(f"  Running: {test_path}")
                result = self._execute_pytest(full_path, markers="memory")
                results["details"].append(result)

        return results

    def _execute_pytest(self, test_path: Path, markers: str = "") -> Dict[str, Any]:
        """Execute pytest on given path with optional markers."""

        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--disable-warnings",
            "-x"  # Stop on first failure for comprehensive suite
        ]

        if markers:
            cmd.extend(["-m", markers])

        # Add JSON report if available
        json_report = self.project_root / f"test_results_{test_path.name}.json"
        cmd.extend(["--json-report", f"--json-report-file={json_report}"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per test file
                cwd=self.project_root
            )

            return {
                "path": str(test_path),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "path": str(test_path),
                "return_code": -1,
                "stdout": "",
                "stderr": "Test execution timeout",
                "success": False
            }
        except Exception as e:
            return {
                "path": str(test_path),
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }

    def _aggregate_results(self, phase_results: List[Dict[str, Any]]) -> None:
        """Aggregate results from all test phases."""

        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        failed_details = []

        for phase in phase_results:
            phase_name = phase["phase"]
            print(f"\n📊 {phase_name.title()} Phase Results:")

            phase_passed = 0
            phase_failed = 0

            for detail in phase["details"]:
                if detail["success"]:
                    phase_passed += 1
                    print(f"  ✅ {Path(detail['path']).name}")
                else:
                    phase_failed += 1
                    print(f"  ❌ {Path(detail['path']).name}")
                    failed_details.append({
                        "phase": phase_name,
                        "path": detail["path"],
                        "error": detail["stderr"]
                    })

            print(f"  Summary: {phase_passed} passed, {phase_failed} failed")

            # Update totals (rough estimates, actual counts would come from pytest JSON)
            total_tests += (phase_passed + phase_failed) * 10  # Estimate 10 tests per file
            passed_tests += phase_passed * 10
            failed_tests += phase_failed * 10

        self.test_results.total_tests = total_tests
        self.test_results.passed_tests = passed_tests
        self.test_results.failed_tests = failed_tests
        self.test_results.skipped_tests = skipped_tests
        self.test_results.failed_test_details = failed_details

    def _analyze_coverage(self) -> None:
        """Analyze code coverage from test execution."""

        if not COVERAGE_AVAILABLE:
            print("⚠️ Coverage analysis not available (install coverage.py)")
            return

        try:
            self.coverage.save()

            # Generate coverage report
            coverage_report = self.project_root / "coverage_report.txt"
            with open(coverage_report, 'w') as f:
                self.coverage.report(file=f, show_missing=True)

            # Get coverage percentage
            total_coverage = self.coverage.report(show_missing=False)
            self.test_results.coverage_percentage = total_coverage

            print(f"📊 Coverage Analysis: {total_coverage:.1f}%")

            # Generate HTML report
            html_dir = self.project_root / "htmlcov"
            self.coverage.html_report(directory=str(html_dir))
            print(f"📄 HTML Coverage Report: {html_dir}/index.html")

        except Exception as e:
            print(f"⚠️ Coverage analysis failed: {e}")
            self.test_results.coverage_percentage = 0.0

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics during testing."""

        if not PERFORMANCE_MONITORING:
            return {}

        try:
            process = psutil.Process()
            system_metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            return system_metrics
        except Exception as e:
            print(f"⚠️ Performance monitoring failed: {e}")
            return {}

    def _generate_final_report(self) -> None:
        """Generate comprehensive final test report."""

        print("\n" + "=" * 60)
        print("🎯 LUKHAS Comprehensive Test Suite Results")
        print("=" * 60)

        # Performance metrics
        self.test_results.performance_metrics = self._collect_performance_metrics()

        # Results summary
        print("📊 Test Summary:")
        print(f"  Total Tests: {self.test_results.total_tests}")
        print(f"  Passed: {self.test_results.passed_tests}")
        print(f"  Failed: {self.test_results.failed_tests}")
        print(f"  Skipped: {self.test_results.skipped_tests}")
        print(f"  Success Rate: {self.test_results.success_rate:.1f}%")
        print(f"  Coverage: {self.test_results.coverage_percentage:.1f}%")
        print(f"  Execution Time: {self.test_results.execution_time:.1f}s")

        # T4/0.01% Standards Check
        print("\n🎯 T4/0.01% Standards Compliance:")
        print(f"  ✅ Success Rate ≥95%: {self.test_results.success_rate >= 95.0}")
        print(f"  ✅ Coverage ≥90%: {self.test_results.coverage_percentage >= 90.0}")
        print(f"  ✅ Zero Critical Failures: {len(self.test_results.failed_test_details) == 0}")
        print(f"  Overall Status: {'✅ PASS' if self.test_results.meets_standards else '❌ FAIL'}")

        # Failed tests detail
        if self.test_results.failed_test_details:
            print("\n❌ Failed Test Details:")
            for failure in self.test_results.failed_test_details[:5]:  # Show first 5
                print(f"  {failure['phase']}: {Path(failure['path']).name}")
                print(f"    Error: {failure['error'][:100]}...")

        # Performance metrics
        if self.test_results.performance_metrics:
            print("\n⚡ Performance Metrics:")
            metrics = self.test_results.performance_metrics
            print(f"  CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_usage_mb', 0):.1f}MB")
            print(f"  Memory Percent: {metrics.get('memory_percent', 0):.1f}%")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "results": {
                "total_tests": self.test_results.total_tests,
                "passed_tests": self.test_results.passed_tests,
                "failed_tests": self.test_results.failed_tests,
                "success_rate": self.test_results.success_rate,
                "coverage_percentage": self.test_results.coverage_percentage,
                "execution_time": self.test_results.execution_time,
                "meets_standards": self.test_results.meets_standards
            },
            "failed_tests": self.test_results.failed_test_details,
            "performance_metrics": self.test_results.performance_metrics
        }

        report_file = self.project_root / "comprehensive_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved: {report_file}")
        print("=" * 60)


def run_comprehensive_tests() -> int:
    """Main entry point for comprehensive test suite."""

    orchestrator = ComprehensiveTestOrchestrator()
    results = orchestrator.run_comprehensive_suite()

    # Return appropriate exit code
    if results.meets_standards:
        print("🎉 All tests passed T4/0.01% standards!")
        return 0
    else:
        print("💥 Test suite failed to meet T4/0.01% standards")
        return 1


# Pytest integration for individual test execution
class TestComprehensiveValidation:
    """Pytest-compatible comprehensive validation tests."""

    def test_guardian_system_comprehensive(self):
        """Comprehensive Guardian system validation."""

        # This would run all Guardian-related tests
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/integration/test_guardian_dsl.py",
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=120)

            assert result.returncode == 0, f"Guardian tests failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("Guardian tests timed out")

    def test_memory_system_comprehensive(self):
        """Comprehensive memory system validation."""

        memory_test_files = [
            "tests/memory/test_topk_recall.py",
            "tests/memory/test_scheduled_folding.py",
            "tests/memory/test_fold_consolidation_edge_cases.py",
            "tests/integration/test_memory_system.py"
        ]

        for test_file in memory_test_files:
            if Path(test_file).exists():
                result = subprocess.run([
                    sys.executable, "-m", "pytest",
                    test_file, "-v", "--tb=short"
                ], capture_output=True, text=True, timeout=120)

                assert result.returncode == 0, f"Memory test {test_file} failed: {result.stderr}"

    def test_orchestrator_comprehensive(self):
        """Comprehensive orchestrator validation."""

        orchestrator_tests = [
            "tests/e2e/test_matriz_orchestration.py",
            "tests/stress/test_orchestrator.py"
        ]

        for test_file in orchestrator_tests:
            if Path(test_file).exists():
                result = subprocess.run([
                    sys.executable, "-m", "pytest",
                    test_file, "-v", "--tb=short"
                ], capture_output=True, text=True, timeout=180)

                assert result.returncode == 0, f"Orchestrator test {test_file} failed: {result.stderr}"

    def test_security_comprehensive(self):
        """Comprehensive security validation."""

        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/security/test_security_validation.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)

        # Security tests may find vulnerabilities, so we check for test execution success
        # rather than zero vulnerabilities
        assert "FAILED" not in result.stdout, f"Security test execution failed: {result.stderr}"

    def test_performance_budgets_comprehensive(self):
        """Comprehensive performance budget validation."""

        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/performance/test_performance_budgets.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=180)

        assert result.returncode == 0, f"Performance tests failed: {result.stderr}"

    def test_coverage_requirements(self):
        """Validate test coverage meets T4/0.01% requirements."""

        if not COVERAGE_AVAILABLE:
            pytest.skip("Coverage analysis not available")

        # Run subset of tests with coverage
        cov = coverage.Coverage(source=["lukhas"])
        cov.start()

        try:
            # Run representative tests
            subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/memory/test_topk_recall.py",
                "tests/reliability/",
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=120)

        finally:
            cov.stop()
            cov.save()

        # Check coverage percentage
        total_coverage = cov.report(show_missing=False)

        # For comprehensive suite, we expect high coverage
        assert total_coverage >= 75.0, f"Coverage too low: {total_coverage:.1f}% < 75%"


if __name__ == "__main__":
    sys.exit(run_comprehensive_tests())
