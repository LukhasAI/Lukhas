#!/usr/bin/env python3
"""
LUKHAS AI Tools Health Check
===========================
Comprehensive health check and validation for all tools in the LUKHAS AI ecosystem.
Validates configuration, connectivity, and operational status of all tooling components.

Usage:
    python tools/tools_health_check.py [--verbose] [--fix-issues]
"""

import asyncio
import json
import logging
import sqlite3
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ToolsHealthChecker:
    """Comprehensive health checker for LUKHAS AI tools ecosystem"""

    def __init__(self, verbose: bool = False, fix_issues: bool = False):
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.project_root = Path(__file__).resolve().parents[1]
        self.tools_dir = self.project_root / "tools"

        # Health check results
        self.results: dict[str, dict[str, any]] = {}
        self.issues_found: list[str] = []
        self.fixes_applied: list[str] = []

    def log_info(self, message: str):
        """Log info message with optional verbose output"""
        if self.verbose:
            logger.info(message)
        else:
            print(f"✓ {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        logger.warning(message)
        self.issues_found.append(message)

    def log_error(self, message: str):
        """Log error message"""
        logger.error(message)
        self.issues_found.append(message)

    def check_file_exists(self, file_path: Path, description: str) -> bool:
        """Check if a file exists"""
        if file_path.exists():
            self.log_info(f"{description}: Found at {file_path}")
            return True
        else:
            self.log_error(f"{description}: Missing at {file_path}")
            return False

    def check_directory_structure(self) -> dict[str, bool]:
        """Check tools directory structure"""
        self.log_info("Checking tools directory structure...")

        expected_dirs = [
            "testing",
            "monitoring",
            "devops",
            "dashboards",
            "devops/infrastructure",
            "devops/infrastructure/terraform",
            "devops/infrastructure/kubernetes",
            "devops/infrastructure/.github/workflows"
        ]

        results = {}
        for dir_name in expected_dirs:
            dir_path = self.tools_dir / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            results[dir_name] = exists

            if exists:
                self.log_info(f"Directory: {dir_name}")
            else:
                self.log_error(f"Missing directory: {dir_name}")
                if self.fix_issues:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied.append(f"Created directory: {dir_name}")

        return results

    def check_testing_tools(self) -> dict[str, bool]:
        """Check testing infrastructure tools"""
        self.log_info("Checking testing infrastructure...")

        results = {}
        testing_files = [
            ("test_infrastructure_monitor.py", "Test Infrastructure Monitor"),
            ("coverage_metrics_system.py", "Coverage Metrics System")
        ]

        for filename, description in testing_files:
            file_path = self.tools_dir / "testing" / filename
            results[filename] = self.check_file_exists(file_path, description)

        # Check if coverage database can be created
        try:
            db_path = self.tools_dir / "testing" / "coverage_metrics.db"
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1")
            results["database_connectivity"] = True
            self.log_info("Coverage database: Accessible")
        except Exception as e:
            results["database_connectivity"] = False
            self.log_error(f"Coverage database: Connection failed - {e}")

        return results

    def check_monitoring_tools(self) -> dict[str, bool]:
        """Check monitoring and alerting tools"""
        self.log_info("Checking monitoring and alerting system...")

        results = {}
        monitoring_files = [
            ("production_alerting_system.py", "Production Alerting System"),
            ("t4_monitoring_integration.py", "T4 Monitoring Integration"),
            ("monitoring_dashboard.py", "Monitoring Dashboard"),
            ("monitoring_config.json", "Monitoring Configuration")
        ]

        for filename, description in monitoring_files:
            file_path = self.tools_dir / "monitoring" / filename
            results[filename] = self.check_file_exists(file_path, description)

        # Check monitoring configuration validity
        config_path = self.tools_dir / "monitoring" / "monitoring_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)

                required_keys = ["evaluation_interval", "channels", "alert_rules"]
                config_valid = all(key in config for key in required_keys)

                results["config_validity"] = config_valid
                if config_valid:
                    self.log_info("Monitoring configuration: Valid structure")
                else:
                    self.log_error("Monitoring configuration: Missing required keys")

            except json.JSONDecodeError as e:
                results["config_validity"] = False
                self.log_error(f"Monitoring configuration: Invalid JSON - {e}")

        return results

    def check_devops_tools(self) -> dict[str, bool]:
        """Check DevOps and deployment tools"""
        self.log_info("Checking DevOps and deployment tools...")

        results = {}
        devops_files = [
            ("automated_deployment_pipeline.py", "Automated Deployment Pipeline"),
            ("deployment_config.json", "Deployment Configuration"),
            ("infrastructure/Dockerfile", "Docker Configuration"),
            ("infrastructure/docker-compose.yml", "Docker Compose Configuration"),
            ("infrastructure/terraform/main.tf", "Terraform Main Configuration"),
            ("infrastructure/terraform/variables.tf", "Terraform Variables"),
            ("infrastructure/terraform/outputs.tf", "Terraform Outputs"),
            ("infrastructure/kubernetes/namespace.yaml", "Kubernetes Namespaces"),
            ("infrastructure/kubernetes/configmap.yaml", "Kubernetes ConfigMaps"),
            ("infrastructure/kubernetes/deployment.yaml", "Kubernetes Deployment"),
            ("infrastructure/.github/workflows/ci-cd-pipeline.yml", "CI/CD Pipeline")
        ]

        for filename, description in devops_files:
            file_path = self.tools_dir / "devops" / filename
            results[filename] = self.check_file_exists(file_path, description)

        return results

    def check_dashboard_tools(self) -> dict[str, bool]:
        """Check dashboard and visualization tools"""
        self.log_info("Checking dashboard tools...")

        results = {}
        dashboard_files = [
            ("consciousness_drift_monitor.js", "Consciousness Drift Monitor")
        ]

        for filename, description in dashboard_files:
            file_path = self.tools_dir / "dashboards" / filename
            results[filename] = self.check_file_exists(file_path, description)

        return results

    async def check_tool_imports(self) -> dict[str, bool]:
        """Check if tools can be imported successfully"""
        self.log_info("Checking tool imports...")

        results = {}

        # Test imports
        import_tests = [
            ("tools.testing.test_infrastructure_monitor", "TestInfrastructureMonitor"),
            ("tools.testing.coverage_metrics_system", "CoverageMetricsSystem"),
            ("tools.monitoring.production_alerting_system", "ProductionAlertingSystem"),
            ("tools.monitoring.t4_monitoring_integration", "T4MonitoringIntegration"),
            ("tools.monitoring.monitoring_dashboard", "MonitoringDashboard"),
            ("tools.devops.automated_deployment_pipeline", "AutomatedDeploymentPipeline")
        ]

        for module_name, class_name in import_tests:
            try:
                # Dynamically import and check class
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                results[module_name] = True
                self.log_info(f"Import: {module_name}.{class_name}")
            except Exception as e:
                results[module_name] = False
                self.log_error(f"Import failed: {module_name}.{class_name} - {e}")

        return results

    def check_external_dependencies(self) -> dict[str, bool]:
        """Check external dependencies and optional packages"""
        self.log_info("Checking external dependencies...")

        results = {}

        # Required dependencies
        required_deps = [
            ("psutil", "System monitoring"),
            ("httpx", "HTTP client"),
            ("asyncio", "Async support")
        ]

        # Optional dependencies
        optional_deps = [
            ("fastapi", "Web dashboard"),
            ("uvicorn", "ASGI server"),
            ("datadog", "Datadog integration"),
            ("prometheus_client", "Prometheus metrics"),
            ("opentelemetry", "OpenTelemetry tracing")
        ]

        for dep_name, description in required_deps:
            try:
                __import__(dep_name)
                results[dep_name] = True
                self.log_info(f"Required dependency: {dep_name} ({description})")
            except ImportError:
                results[dep_name] = False
                self.log_error(f"Missing required dependency: {dep_name} ({description})")

        for dep_name, description in optional_deps:
            try:
                __import__(dep_name)
                results[f"optional_{dep_name}"] = True
                self.log_info(f"Optional dependency: {dep_name} ({description})")
            except ImportError:
                results[f"optional_{dep_name}"] = False
                if self.verbose:
                    self.log_warning(f"Optional dependency not available: {dep_name} ({description})")

        return results

    def check_configuration_files(self) -> dict[str, bool]:
        """Check configuration file validity"""
        self.log_info("Checking configuration files...")

        results = {}

        config_files = [
            ("monitoring/monitoring_config.json", "Monitoring Configuration"),
            ("devops/deployment_config.json", "Deployment Configuration")
        ]

        for file_path, description in config_files:
            full_path = self.tools_dir / file_path

            if full_path.exists():
                try:
                    with open(full_path) as f:
                        json.load(f)
                    results[file_path] = True
                    self.log_info(f"Configuration: {description}")
                except json.JSONDecodeError as e:
                    results[file_path] = False
                    self.log_error(f"Invalid JSON in {description}: {e}")
            else:
                results[file_path] = False
                self.log_error(f"Missing configuration: {description}")

        return results

    async def run_comprehensive_health_check(self) -> dict[str, dict[str, any]]:
        """Run comprehensive health check of all tools"""
        print("🔍 LUKHAS AI Tools Health Check")
        print("=" * 50)

        # Run all health checks
        self.results["directory_structure"] = self.check_directory_structure()
        self.results["testing_tools"] = self.check_testing_tools()
        self.results["monitoring_tools"] = self.check_monitoring_tools()
        self.results["devops_tools"] = self.check_devops_tools()
        self.results["dashboard_tools"] = self.check_dashboard_tools()
        self.results["tool_imports"] = await self.check_tool_imports()
        self.results["external_dependencies"] = self.check_external_dependencies()
        self.results["configuration_files"] = self.check_configuration_files()

        return self.results

    def generate_health_report(self) -> str:
        """Generate comprehensive health report"""
        total_checks = sum(len(category) for category in self.results.values())
        passed_checks = sum(
            sum(1 for check in category.values() if check)
            for category in self.results.values()
        )

        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        report = f"""
LUKHAS AI Tools Health Check Report
==================================

Overall Health: {success_rate:.1f}% ({passed_checks}/{total_checks} checks passed)

Category Breakdown:
"""

        for category, checks in self.results.items():
            category_passed = sum(1 for check in checks.values() if check)
            category_total = len(checks)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0

            status_icon = "✅" if category_rate == 100 else "⚠️" if category_rate > 50 else "❌"
            report += f"  {status_icon} {category.replace('_', ' ').title()}: {category_rate:.1f}% ({category_passed}/{category_total})\n"

        if self.issues_found:
            report += f"\nIssues Found ({len(self.issues_found)}):\n"
            for issue in self.issues_found[:10]:  # Show first 10 issues
                report += f"  • {issue}\n"

            if len(self.issues_found) > 10:
                report += f"  ... and {len(self.issues_found) - 10} more issues\n"

        if self.fixes_applied:
            report += f"\nFixes Applied ({len(self.fixes_applied)}):\n"
            for fix in self.fixes_applied:
                report += f"  • {fix}\n"

        report += "\nRecommendations:\n"

        if success_rate < 100:
            report += "  • Review and resolve failing checks above\n"

        if not self.results.get("external_dependencies", {}).get("optional_fastapi", False):
            report += "  • Install FastAPI for monitoring dashboard: pip install fastapi uvicorn\n"

        if not self.results.get("external_dependencies", {}).get("optional_datadog", False):
            report += "  • Install Datadog for enhanced monitoring: pip install datadog\n"

        if success_rate >= 90:
            report += "  • System is in excellent health! 🎉\n"
        elif success_rate >= 75:
            report += "  • System is in good health with minor issues to address\n"
        else:
            report += "  • System requires attention to resolve critical issues\n"

        return report

    def get_exit_code(self) -> int:
        """Get appropriate exit code based on health check results"""
        total_checks = sum(len(category) for category in self.results.values())
        passed_checks = sum(
            sum(1 for check in category.values() if check)
            for category in self.results.values()
        )

        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        if success_rate >= 95:
            return 0  # All good
        elif success_rate >= 80:
            return 1  # Minor issues
        else:
            return 2  # Major issues


async def main():
    """Main entry point for tools health check"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AI Tools Health Check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix-issues", "-f", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Run health check
    health_checker = ToolsHealthChecker(verbose=args.verbose, fix_issues=args.fix_issues)
    results = await health_checker.run_comprehensive_health_check()

    if args.json:
        # Output JSON results
        print(json.dumps(results, indent=2))
    else:
        # Output human-readable report
        report = health_checker.generate_health_report()
        print(report)

    # Exit with appropriate code
    sys.exit(health_checker.get_exit_code())


if __name__ == "__main__":
    asyncio.run(main())
