# TODO[T4-AUTOFIX]: Remaining minor syntax issues - review malformed f-strings and list comprehensions
# Note: Major syntax errors were fixed in previous passes, only minor issues remain
#!/usr/bin/env python3
"""
LUKHAS Comprehensive System Status Report
=========================================
Complete analysis of all systems, tests, and health status.
Trinity Framework: ⚛️🧠🛡️

Date: August 5, 2025
Purpose: Research documentation and publishing
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemHealthAnalyzer:
    """Comprehensive system health and status analyzer"""

    def __init__(self):
        self.report_timestamp = datetime.now(timezone.utc).isoformat()
        self.base_path = Path("/Users/agi_dev/Lukhas")
        self.results = {
            "metadata": {
                "report_title": "LUKHAS Comprehensive System Status Report",
                "report_date": self.report_timestamp,
                "constellation_framework": "⚛️🧠🛡️",
                "version": "1.0",
                "purpose": "Research Documentation and Publishing",
            },
            "python_environment": {},
            "core_modules": {},
            "api_systems": {},
            "test_results": {},
            "vivox_systems": {},
            "identity_systems": {},
            "file_integrity": {},
            "performance_metrics": {},
            "issues_detected": [],
            "recommendations": [],
        }

    def run_comprehensive_analysis(self):
        """Run complete system analysis"""
        logger.info("🔍 Starting Comprehensive System Analysis")
        logger.info("=" * 60)

        # 1. Python Environment Analysis
        self.analyze_python_environment()

        # 2. Core Module Testing
        self.test_core_modules()

        # 3. API System Status
        self.check_api_systems()

        # 4. Test Suite Analysis
        self.analyze_test_results()

        # 5. VIVOX System Status
        self.check_vivox_systems()

        # 6. Identity System Status
        self.check_identity_systems()

        # 7. File Integrity Check
        self.check_file_integrity()

        # 8. Performance Analysis
        self.analyze_performance()

        # 9. Generate final report
        return self.generate_final_report()

    def analyze_python_environment(self):
        """Analyze Python environment and dependencies"""
        logger.info("🐍 Analyzing Python Environment...")

        try:
            # Python version
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            python_version = result.stdout.strip()

            # Key dependencies
            dependencies = {}
            key_packages = [
                "fastapi",
                "openai",
                "numpy",
                "pytest",
                "uvicorn",
                "pydantic",
                "requests",
                "anthropic",
                "websockets",
            ]

            for package in key_packages:
                try:
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-c",
                            f"import {package}; print({package}.__version__)",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0:
                        dependencies[package] = {
                            "version": result.stdout.strip(),
                            "status": "installed",
                        }
                    else:
                        dependencies[package] = {"version": None, "status": "not_found"}
                except Exception as e:
                    dependencies[package] = {
                        "version": None,
                        "status": f"error: {e!s}",
                    }

            self.results["python_environment"] = {
                "python_version": python_version,
                "dependencies": dependencies,
                "working_directory": str(self.base_path),
                "sys_path_entries": len(sys.path),
            }

            logger.info(f"✅ Python: {python_version}")
            logger.info(
                f"✅ Dependencies: {len([d for d in dependencies.values() if d['status'] == 'installed'])}/{len(dependencies)} installed"
            )

        except Exception as e:
            logger.error(f"❌ Python environment analysis failed: {e}")
            self.results["issues_detected"].append(f"Python environment analysis failed: {e}")

    def test_core_modules(self):
        """Test core LUKHAS modules"""
        logger.info("🧠 Testing Core Modules...")

        core_modules = {
            "lukhas_embedding": "LukhasEmbedding system",
            "symbolic_healer": "SymbolicHealer system",
            "symbolic_api": "Symbolic API system",
            "memory_chain": "Memory chain system",
            "identity_emergence": "Identity emergence system",
            "z_collapse_engine": "Z-collapse engine",
            "vivox": "VIVOX consciousness system",
        }

        module_results = {}

        for module_name, description in core_modules.items():
            try:
                # Test import
                result = subprocess.run(
                    [sys.executable, "-c", f"import {module_name}; print('SUCCESS')"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    module_results[module_name] = {
                        "status": "working",
                        "description": description,
                        "import_time": "< 10s",
                        "errors": None,
                    }
                    logger.info(f"✅ {module_name}: Working")
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    module_results[module_name] = {
                        "status": "failed",
                        "description": description,
                        "errors": error_msg,
                    }
                    logger.error(f"❌ {module_name}: Failed - {error_msg}")
                    self.results["issues_detected"].append(f"{module_name} import failed: {error_msg}")

            except Exception as e:
                module_results[module_name] = {
                    "status": "error",
                    "description": description,
                    "errors": str(e),
                }
                logger.error(f"❌ {module_name}: Error - {e}")
                self.results["issues_detected"].append(f"{module_name} test error: {e}")

        self.results["core_modules"] = module_results

        working_modules = len([m for m in module_results.values() if m["status"] == "working"])
        logger.info(f"📊 Core Modules: {working_modules}/{len(core_modules)} working")

    def check_api_systems(self):
        """Check API system status"""
        logger.info("🌐 Checking API Systems...")

        api_endpoints = {
            "symbolic_api": {
                "url": "http://localhost:8000/health",
                "description": "Main Symbolic API",
            }
        }

        api_results = {}

        for api_name, config in api_endpoints.items():
            try:
                import requests

                response = requests.get(config["url"], timeout=5)

                if response.status_code == 200:
                    api_results[api_name] = {
                        "status": "online",
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code,
                        "response_data": (
                            response.json()
                            if response.headers.get("content-type", "").startswith("application/json")
                            else response.text[:200]
                        ),
                    }
                    logger.info(f"✅ {api_name}: Online ({response.elapsed.total_seconds():.3f}s)")
                else:
                    api_results[api_name] = {
                        "status": "error",
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}",
                    }
                    logger.warning(f"⚠️ {api_name}: HTTP {response.status_code}")

            except Exception as e:
                api_results[api_name] = {"status": "offline", "error": str(e)}
                logger.warning(f"⚠️ {api_name}: Offline - {e}")

        self.results["api_systems"] = api_results

    def analyze_test_results(self):
        """Analyze pytest test results"""
        logger.info("🧪 Analyzing Test Results...")

        try:
            # Run pytest with json report
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "--tb=short",
                    "-v",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.base_path,
            )

            # Parse output
            output_lines = result.stdout.split("\n")

            # Extract summary line
            summary_line = None
            for line in reversed(output_lines):
                if "passed" in line or "failed" in line or "error" in line:
                    summary_line = line.strip()
                    break

            # Count tests
            total_tests = 0
            passed_tests = 0
            failed_tests = 0
            warnings = 0

            if summary_line:
                import re

                # Parse summary like "265 passed, 186 deselected, 2 warnings in 45.67s"
                passed_match = re.search(r"(\d+) passed", summary_line)
                failed_match = re.search(r"(\d+) failed", summary_line)
                warning_match = re.search(r"(\d+) warning", summary_line)

                if passed_match:
                    passed_tests = int(passed_match.group(1))
                if failed_match:
                    failed_tests = int(failed_match.group(1))
                if warning_match:
                    warnings = int(warning_match.group(1))

                total_tests = passed_tests + failed_tests

            self.results["test_results"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warnings": warnings,
                "success_rate": ((passed_tests / total_tests * 100) if total_tests > 0 else 0),
                "summary_line": summary_line,
                "execution_time": "< 120s",
                "exit_code": result.returncode,
            }

            logger.info(f"📊 Tests: {passed_tests} passed, {failed_tests} failed, " f"{warnings} warnings")

            if failed_tests > 0:
                self.results["issues_detected"].append(f"{failed_tests} test failures detected")

        except Exception as e:
            logger.error(f"❌ Test analysis failed: {e}")
            self.results["test_results"] = {"status": "failed", "error": str(e)}
            self.results["issues_detected"].append(f"Test execution failed: {e}")

    def check_vivox_systems(self):
        """Check VIVOX consciousness systems"""
        logger.info("🧬 Checking VIVOX Systems...")

        vivox_components = {
            "z_collapse_engine": "Z-collapse function implementation",
            "vivox.memory_expansion": "Memory expansion (ME) component",
            "vivox.moral_alignment": "Moral alignment engine (MAE)",
            "vivox.consciousness": "Consciousness interpretation layer (CIL)",
            "vivox.self_reflection": "Self-reflective memory (SRM)",
        }

        vivox_results = {}

        for component, description in vivox_components.items():
            try:
                # Test specific VIVOX component
                if component == "z_collapse_engine":
                    # Test z-collapse directly
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-c",
                            "from z_collapse_engine import ZCollapseEngine; "
                            "engine = ZCollapseEngine(); "
                            "print('Z-ENGINE SUCCESS')",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                else:
                    # Test VIVOX submodules
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-c",
                            f"import {component}; print('VIVOX SUCCESS')",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    vivox_results[component] = {
                        "status": "working",
                        "description": description,
                    }
                    logger.info(f"✅ {component}: Working")
                else:
                    vivox_results[component] = {
                        "status": "failed",
                        "description": description,
                        "error": result.stderr.strip(),
                    }
                    logger.warning(f"⚠️ {component}: Issues detected")

            except Exception as e:
                vivox_results[component] = {
                    "status": "error",
                    "description": description,
                    "error": str(e),
                }
                logger.error(f"❌ {component}: Error - {e}")

        self.results["vivox_systems"] = vivox_results

    def check_identity_systems(self):
        """Check identity and authentication systems"""
        logger.info("🛡️ Checking Identity Systems...")

        # Check identity directory structure
        identity_path = self.base_path / "identity"

        if identity_path.exists():
            identity_files = list(identity_path.rglob("*.py"))

            self.results["identity_systems"] = {
                "identity_directory": "exists",
                "python_files": len(identity_files),
                "key_components": {
                    "auth": (identity_path / "auth").exists(),
                    "api": (identity_path / "api.py").exists(),
                    "login": (identity_path / "login.py").exists(),
                    "registration": (identity_path / "registration.py").exists(),
                },
                "status": "configured",
            }
            logger.info(f"✅ Identity system: {len(identity_files)} files found")
        else:
            self.results["identity_systems"] = {
                "status": "missing",
                "error": "Identity directory not found",
            }
            logger.warning("⚠️ Identity system: Directory missing")
            self.results["issues_detected"].append("Identity directory not found")

    def check_file_integrity(self):
        """Check critical file integrity"""
        logger.info("📁 Checking File Integrity...")

        critical_files = [
            "lukhas_embedding.py",
            "symbolic_healer.py",
            "symbolic_api.py",
            "integration_config.yaml",
            "requirements.txt",
            "README.md",
            ".env",
        ]

        file_status = {}

        for filename in critical_files:
            file_path = self.base_path / filename

            if file_path.exists():
                stat = file_path.stat()
                file_status[filename] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "readable": file_path.is_file() and os.access(file_path, os.R_OK),
                }
            else:
                file_status[filename] = {"exists": False, "error": "File not found"}
                if filename != ".env":  # .env might be intentionally missing:
                    self.results["issues_detected"].append(f"Critical file missing: {filename}")

        self.results["file_integrity"] = file_status

        existing_files = len([f for f in file_status.values() if f.get("exists", False)])
        logger.info(f"📊 Critical files: {existing_files}/{len(critical_files)} present")

    def analyze_performance(self):
        """Analyze system performance metrics"""
        logger.info("⚡ Analyzing Performance...")

        try:
            # Test symbolic API performance
            start_time = time.time()
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from embedding import LukhasEmbedding; "
                    "le = LukhasEmbedding(); "
                    "result = le.evaluate_symbolic_ethics('Test message 🧠'); "
                    "print('PERFORMANCE_TEST_SUCCESS')",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            embedding_time = time.time() - start_time

            if "SUCCESS" in result.stdout:
                embedding_performance = {
                    "status": "working",
                    "execution_time": embedding_time,
                    "performance_rating": "good" if embedding_time < 5 else "slow",
                }
            else:
                embedding_performance = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }

            self.results["performance_metrics"] = {
                "lukhas_embedding": embedding_performance,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"⚡ Performance: LukhasEmbedding in {embedding_time:.2f}s")

        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {e}")
            self.results["performance_metrics"] = {"status": "failed", "error": str(e)}

    def generate_final_report(self):
        """Generate comprehensive final report"""
        logger.info("📊 Generating Final Report...")

        # Calculate overall health score
        health_score = self.calculate_health_score()

        # Generate recommendations
        self.generate_recommendations()

        # Add summary
        self.results["executive_summary"] = {
            "overall_health_score": health_score,
            "total_issues": len(self.results["issues_detected"]),
            "critical_systems_working": self.count_working_systems(),
            "api_status": (
                "online"
                if any(api.get("status") == "online" for api in self.results["api_systems"].values())
                else "offline"
            ),
            "test_success_rate": self.results["test_results"].get("success_rate", 0),
            "vivox_components_working": len(
                [v for v in self.results["vivox_systems"].values() if v.get("status") == "working"]
            ),
            "recommendation_count": len(self.results["recommendations"]),
        }

        return self.results

    def calculate_health_score(self):
        """Calculate overall system health score (0-100)"""
        score = 100

        # Deduct for failed core modules
        working_modules = len([m for m in self.results["core_modules"].values() if m.get("status") == "working"])
        total_modules = len(self.results["core_modules"])
        if total_modules > 0:
            module_score = (working_modules / total_modules) * 30
            score = score - 30 + module_score

        # Deduct for test failures
        test_success = self.results["test_results"].get("success_rate", 0)
        score = score - 20 + (test_success / 100 * 20)

        # Deduct for missing critical files
        total_files = len(self.results["file_integrity"])
        existing_files = len([f for f in self.results["file_integrity"].values() if f.get("exists", False)])
        if total_files > 0:
            file_score = (existing_files / total_files) * 20
            score = score - 20 + file_score

        # Deduct for issues
        score = max(0, score - len(self.results["issues_detected"]) * 5)

        return min(100, max(0, score))

    def count_working_systems(self):
        """Count number of working critical systems"""
        working = 0

        # Core modules
        working += len([m for m in self.results["core_modules"].values() if m.get("status") == "working"])

        # APIs
        working += len([a for a in self.results["api_systems"].values() if a.get("status") == "online"])

        # VIVOX components
        working += len([v for v in self.results["vivox_systems"].values() if v.get("status") == "working"])

        return working

    def generate_recommendations(self):
        """Generate system recommendations"""
        recommendations = []

        # Module recommendations
        failed_modules = [
            name for name, info in self.results["core_modules"].items() if info.get("status") != "working"
        ]
        if failed_modules:
            recommendations.append(f"Fix failed modules: {', '.join(failed_modules)}")

        # Test recommendations
        if self.results["test_results"].get("failed_tests", 0) > 0:
            recommendations.append("Investigate and fix failing tests")

        # API recommendations
        offline_apis = [name for name, info in self.results["api_systems"].items() if info.get("status") != "online"]
        if offline_apis:
            recommendations.append(f"Start offline APIs: {', '.join(offline_apis)}")

        # File recommendations
        missing_files = [name for name, info in self.results["file_integrity"].items() if not info.get("exists", False)]
        if missing_files:
            recommendations.append(f"Restore missing files: {', '.join(missing_files)}")

        # Performance recommendations
        if self.results["performance_metrics"].get("lukhas_embedding", {}).get("performance_rating") == "slow":
            recommendations.append("Optimize LukhasEmbedding performance")

        self.results["recommendations"] = recommendations

    def save_report(self, filename: Optional[str] = None):
        """Save the comprehensive report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/system_status_report_{timestamp}.json"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"📄 Comprehensive report saved to: {filename}")
        return filename


def main():
    """Main execution function"""
    analyzer = SystemHealthAnalyzer()

    print("🧠 LUKHAS Comprehensive System Status Report")
    print("=" * 60)
    print("Trinity Framework: ⚛️🧠🛡️")
    print("Date: August 5, 2025")
    print("=" * 60)

    # Run comprehensive analysis
    report = analyzer.run_comprehensive_analysis()

    # Save report
    report_file = analyzer.save_report()

    # Print executive summary
    summary = report["executive_summary"]
    print("\n📊 EXECUTIVE SUMMARY")
    print("=" * 60)
    print(f"Overall Health Score: {summary['overall_health_score']:.1f}/100")
    print(f"Working Systems: {summary['critical_systems_working']}")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"API Status: {summary['api_status']}")
    print(f"Test Success Rate: {summary['test_success_rate']:.1f}%")
    print(f"VIVOX Components Working: {summary['vivox_components_working']}")

    if report["issues_detected"]:
        print(f"\n⚠️ ISSUES DETECTED ({len(report['issues_detected'])})")
        for i, issue in enumerate(report["issues_detected"][:10], 1):
            print(f"  {i}. {issue}")
        if len(report["issues_detected"]) > 10:
            print(f"  ... and {len(report['issues_detected']) - 10} more")

    if report["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS ({len(report['recommendations'])})")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

    print(f"\n📄 Full report saved: {report_file}")

    return report_file


if __name__ == "__main__":
    main()
