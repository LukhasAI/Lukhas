#!/usr/bin/env python3
"""
LUKHAS Comprehensive System Status Report
=========================================
Complete system diagnostic and status report
Date: August 5, 2025
Trinity Framework: ⚛️🧠🛡️
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LUKHASSystemDiagnostic:
    """Comprehensive LUKHAS system diagnostic tool"""

    def __init__(self):
        self.report_timestamp = datetime.now(timezone.utc).isoformat()
        self.base_path = Path("/Users/agi_dev/Lukhas")
        self.results = {
            "metadata": {
                "report_title": "LUKHAS Comprehensive System Status Report",
                "report_date": self.report_timestamp,
                "trinity_framework": "⚛️🧠🛡️",
                "version": "1.0",
                "purpose": "System Health & Research Documentation",
            },
            "python_environment": {},
            "core_modules": {},
            "api_endpoints": {},
            "test_results": {},
            "file_structure": {},
            "api_credentials": {},
            "system_issues": [],
            "recommendations": [],
        }

    def check_python_environment(self):
        """Check Python environment and dependencies"""
        logger.info("🐍 Checking Python Environment...")

        try:
            # Python version
            python_version = sys.version

            # Key dependencies
            dependencies = [
                "fastapi",
                "uvicorn",
                "openai",
                "anthropic",
                "pydantic",
                "pytest",
                "numpy",
                "requests",
                "python-dotenv",
                "pathlib",
            ]

            installed_packages = {}
            missing_packages = []

            for package in dependencies:
                try:
                    __import__(package.replace("-", "_"))
                    # Get version if possible
                    try:
                        mod = __import__(package.replace("-", "_"))
                        version = getattr(mod, "__version__", "unknown")
                        installed_packages[package] = version
                    except BaseException:
                        installed_packages[package] = "installed"
                except ImportError:
                    missing_packages.append(package)

            self.results["python_environment"] = {
                "python_version": python_version,
                "installed_packages": installed_packages,
                "missing_packages": missing_packages,
                "status": "healthy" if not missing_packages else "issues",
            }

        except Exception as e:
            self.results["python_environment"] = {"status": "error", "error": str(e)}

    def check_core_modules(self):
        """Test core LUKHAS modules"""
        logger.info("🧠 Testing Core LUKHAS Modules...")

        modules_to_test = [
            ("lukhas_embedding", "LukhasEmbedding"),
            ("symbolic_healer", "SymbolicHealer"),
            ("symbolic_api", None),
            ("memory_chain", "SymbolicMemoryManager"),
            ("memory_fold_tracker", "MemoryFoldTracker"),
            ("gpt_integration_layer", "GPTIntegrationLayer"),
            ("persona_similarity_engine", "PersonaSimilarityEngine"),
            ("vivox", None),
            ("z_collapse_engine", "ZCollapseEngine"),
        ]

        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name)
                if class_name:
                    cls = getattr(module, class_name)
                    # Try to instantiate
                    cls()
                    status = "✅ Working"
                else:
                    status = "✅ Imports"

                self.results["core_modules"][module_name] = {
                    "status": "working",
                    "class": class_name,
                    "note": status,
                }

            except Exception as e:
                self.results["core_modules"][module_name] = {
                    "status": "error",
                    "class": class_name,
                    "error": str(e),
                }

    def check_api_credentials(self):
        """Check API credential availability"""
        logger.info("🔑 Checking API Credentials...")

        # Load environment variables
        from dotenv import load_dotenv

        load_dotenv()

        api_keys = {
            "OpenAI": os.getenv("OPENAI_API_KEY"),
            "Google": os.getenv("GOOGLE_API_KEY"),
            "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "Perplexity": os.getenv("PERPLEXITY_API_KEY"),
        }

        for provider, key in api_keys.items():
            if key:
                self.results["api_credentials"][provider] = {
                    "status": "✅ Available",
                    "key_preview": f"{key[:10]}..." if len(key) > 10 else "short_key",
                }
            else:
                self.results["api_credentials"][provider] = {
                    "status": "❌ Missing",
                    "key_preview": None,
                }

    def test_api_endpoints(self):
        """Test API endpoints"""
        logger.info("🌐 Testing API Endpoints...")

        import requests

        # Test symbolic API
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.results["api_endpoints"]["symbolic_api"] = {
                    "status": "✅ Running",
                    "port": 8000,
                    "response": response.json(),
                }
            else:
                self.results["api_endpoints"]["symbolic_api"] = {
                    "status": "❌ Error",
                    "port": 8000,
                    "error": f"HTTP {response.status_code}",
                }
        except Exception as e:
            self.results["api_endpoints"]["symbolic_api"] = {
                "status": "❌ Not Running",
                "port": 8000,
                "error": str(e),
            }

    def run_test_suite(self):
        """Run abbreviated test suite"""
        logger.info("🧪 Running Test Suite...")

        try:
            # Run specific health tests
            test_commands = [
                ("Health Tests",
                 ["python3", "-m", "pytest", "tests/", "-k", "test_health",
                  "--tb=short", "-q",],),
                ("Module Imports",
                 ["python3", "-c",
                  "import embedding, symbolic_healer, vivox; print('Core imports OK')",],),
                ("API Test",
                 ["python3", "-c",
                  "import requests; r=requests.get('http://localhost:8000/health'); print(f'API: {r.status_code}')",],),]

            for test_name, command in test_commands:
                try:
                    result = subprocess.run(
                        command, capture_output=True, text=True, timeout=30
                    )

                    self.results["test_results"][test_name] = {
                        "status": (
                            "✅ Passed" if result.returncode == 0 else "❌ Failed"
                        ),
                        "return_code": result.returncode,
                        "stdout": result.stdout[:500],  # Limit output
                        "stderr": result.stderr[:500] if result.stderr else None,
                    }

                except subprocess.TimeoutExpired:
                    self.results["test_results"][test_name] = {
                        "status": "⏰ Timeout",
                        "error": "Test timed out after 30 seconds",
                    }
                except Exception as e:
                    self.results["test_results"][test_name] = {
                        "status": "❌ Error",
                        "error": str(e),
                    }

        except Exception as e:
            self.results["test_results"]["error"] = str(e)

    def analyze_file_structure(self):
        """Analyze key file structure"""
        logger.info("📁 Analyzing File Structure...")

        key_files = [
            "README.md",
            "requirements.txt",
            "integration_config.yaml",
            "lukhas_embedding.py",
            "symbolic_healer.py",
            "symbolic_api.py",
            "z_collapse_engine.py",
            ".env",
            "multi_model_drift_audit.py",
        ]

        key_directories = [
            "vivox/",
            "core/",
            "identity/",
            "memory/",
            "api/",
            "tests/",
            "data/",
            "quantum/",
        ]

        file_status = {}
        for file_path in key_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                stat = full_path.stat()
                file_status[file_path] = {
                    "status": "✅ Exists",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            else:
                file_status[file_path] = {"status": "❌ Missing"}

        dir_status = {}
        for dir_path in key_directories:
            full_path = self.base_path / dir_path
            if full_path.exists() and full_path.is_dir():
                file_count = len(list(full_path.rglob("*")))
                dir_status[dir_path] = {"status": "✅ Exists", "file_count": file_count}
            else:
                dir_status[dir_path] = {"status": "❌ Missing"}

        self.results["file_structure"] = {
            "files": file_status,
            "directories": dir_status,
        }

    def identify_issues(self):
        """Identify and categorize system issues"""
        logger.info("🔍 Identifying System Issues...")

        issues = []
        recommendations = []

        # Check Python environment
        if self.results["python_environment"]["status"] == "error":
            issues.append(
                {
                    "category": "critical",
                    "component": "python_environment",
                    "issue": "Python environment check failed",
                    "impact": "System cannot run",
                }
            )
        elif self.results["python_environment"]["missing_packages"]:
            issues.append({
                "category": "warning", 
                "component": "python_environment",
                "issue": f"Missing packages: {', '.join(self.results['python_environment']['missing_packages'])}",
                "impact": "Some features may not work"
            })
            recommendations.append("Install missing packages with pip install")

        # Check core modules
        failed_modules = [
            name
            for name, data in self.results["core_modules"].items():
            if data["status"] == "error":
        ]
        if failed_modules:
            issues.append(
                {
                    "category": "critical",
                    "component": "core_modules",
                    "issue": f"Failed modules: {', '.join(failed_modules)}",
                    "impact": "Core functionality broken",
                }
            )
            recommendations.append("Fix module import errors and dependencies")

        # Check API credentials
        missing_apis = [
            name
            for name, data in self.results["api_credentials"].items():
            if data["status"] == "❌ Missing":
        ]
        if missing_apis:
            issues.append(
                {
                    "category": "warning",
                    "component": "api_credentials",
                    "issue": f"Missing API keys: {', '.join(missing_apis)}",
                    "impact": "Limited model testing capability",
                }
            )
            recommendations.append("Add missing API keys to .env file")

        # Check API endpoints
        if self.results["api_endpoints"]["symbolic_api"]["status"] != "✅ Running":
            issues.append(
                {
                    "category": "warning",
                    "component": "api_endpoints",
                    "issue": "Symbolic API not running",
                    "impact": "API functionality unavailable",
                }
            )
            recommendations.append("Start symbolic API with: python3 symbolic_api.py")

        # Check test results
        failed_tests = [
            name
            for name, data in self.results["test_results"].items():
            if data.get("status", "").startswith("❌"):
        ]
        if failed_tests:
            issues.append(
                {
                    "category": "warning",
                    "component": "tests",
                    "issue": f"Failed tests: {', '.join(failed_tests)}",
                    "impact": "Quality assurance issues",
                }
            )
            recommendations.append("Investigate and fix failing tests")

        self.results["system_issues"] = issues
        self.results["recommendations"] = recommendations

    def generate_summary(self):
        """Generate executive summary"""
        logger.info("📊 Generating Summary...")

        total_modules = len(self.results["core_modules"])
        working_modules = len(
            [
                m
                for m in self.results["core_modules"].values():
                if m["status"] == "working":
            ]
        )
        module_health = (
            (working_modules / total_modules * 100) if total_modules > 0 else 0
        )

        total_apis = len(self.results["api_credentials"])
        available_apis = len(
            [
                a
                for a in self.results["api_credentials"].values():
                if a["status"] == "✅ Available":
            ]
        )
        api_coverage = (available_apis / total_apis * 100) if total_apis > 0 else 0

        critical_issues = len(
            [i for i in self.results["system_issues"] if i["category"] == "critical"]
        )
        warning_issues = len(
            [i for i in self.results["system_issues"] if i["category"] == "warning"]
        )

        overall_health = "Healthy" if critical_issues == 0 else "Critical Issues"
        if critical_issues == 0 and warning_issues > 0:
            overall_health = "Minor Issues"

        self.results["executive_summary"] = {
            "overall_health": overall_health,
            "module_health_percentage": round(module_health, 1),
            "api_coverage_percentage": round(api_coverage, 1),
            "total_modules_tested": total_modules,
            "working_modules": working_modules,
            "available_apis": available_apis,
            "total_apis": total_apis,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "total_recommendations": len(self.results["recommendations"]),
        }

    def run_comprehensive_diagnostic(self):
        """Run complete system diagnostic"""
        logger.info("🚀 Starting LUKHAS Comprehensive System Diagnostic")
        logger.info("=" * 60)

        try:
            self.check_python_environment()
            self.check_core_modules()
            self.check_api_credentials()
            self.test_api_endpoints()
            self.run_test_suite()
            self.analyze_file_structure()
            self.identify_issues()
            self.generate_summary()

            logger.info("✅ Diagnostic complete!")
            return self.results

        except Exception as e:
            logger.error(f"❌ Diagnostic failed: {e}")
            self.results["diagnostic_error"] = str(e)
            return self.results

    def save_report(self, filename: str = None):
        """Save comprehensive report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/comprehensive_system_report_{timestamp}.json"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"📄 System report saved to: {filename}")
        return filename

    def print_summary(self):
        """Print summary to console"""
        summary = self.results.get("executive_summary", {})

        print("\n" + "=" * 60)
        print("🧠 LUKHAS COMPREHENSIVE SYSTEM STATUS REPORT")
        print("=" * 60)
        print(f"📅 Date: {self.report_timestamp}")
        print(f"🏥 Overall Health: {summary.get('overall_health', 'Unknown')}")
        print(
            f"🧬 Module Health: {summary.get('module_health_percentage',}
                                            0)} % ({summary.get('working_modules', 0)} / {summary.get('total_modules_tested', 0)})"
        )
        print(
            f"🔑 API Coverage: {summary.get('api_coverage_percentage', 0)}% ({summary.get('available_apis', 0)}/{summary.get('total_apis', 0)})"
        )
        print(f"🚨 Critical Issues: {summary.get('critical_issues', 0)}")
        print(f"⚠️  Warning Issues: {summary.get('warning_issues', 0)}")
        print(f"💡 Recommendations: {summary.get('total_recommendations', 0)}")

        if self.results["system_issues"]:
            print("\n🔍 KEY ISSUES:")
            for issue in self.results["system_issues"]:
                icon = "🚨" if issue["category"] == "critical" else "⚠️"
                print(f"   {icon} {issue['component']}: {issue['issue']}")

        if self.results["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")

        print("=" * 60)


def main():
    """Main execution function"""
    diagnostic = LUKHASSystemDiagnostic()

    # Run comprehensive diagnostic
    results = diagnostic.run_comprehensive_diagnostic()

    # Save report
    report_file = diagnostic.save_report()

    # Print summary
    diagnostic.print_summary()

    return report_file, results


if __name__ == "__main__":
    main()
