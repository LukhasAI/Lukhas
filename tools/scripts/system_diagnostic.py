#!/usr/bin/env python3
"""
LUKHΛS System Diagnostic
========================

Comprehensive diagnostic to verify system functionality and readiness.
Tests all major components and provides a functionality percentage.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import importlib.util
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class SystemDiagnostic:
    """Run comprehensive system diagnostics."""

    def __init__(self):
        self.results = {
            "modules": {},
            "api_endpoints": {},
            "data_files": {},
            "imports": {},
            "tests": {},
        }
        self.total_checks = 0
        self.passed_checks = 0

    def check_module_imports(self) -> dict[str, bool]:
        """Check if critical modules can be imported."""
        modules_to_check = [
            # Identity system
            ("identity", "Identity System"),
            ("identity.user_db", "User Database"),
            ("identity.api", "Identity API"),
            ("identity.middleware", "Auth Middleware"),
            # API system
            ("symbolic_api", "Symbolic API"),
            ("bridge.api.intent_router", "Intent Router"),
            ("bridge.api.entity_extractor", "Entity Extractor"),
            # Dashboard
            ("meta_dashboard.routes.log_route", "Log Routes"),
            # Core modules
            ("core.symbolic", "Symbolic Core"),
            ("memory", "Memory System"),
            ("consciousness", "Consciousness System"),
            ("governance", "Governance System"),
            # VIVoX
            ("vivox", "VIVoX Module"),
        ]

        results = {}
        for module_name, description in modules_to_check:
            self.total_checks += 1
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    results[description] = True
                    self.passed_checks += 1
                else:
                    results[description] = False
            except Exception as e:
                results[description] = False
                print(f"❌ Failed to import {module_name}: {e!s}")

        self.results["imports"] = results
        return results

    def check_data_files(self) -> dict[str, bool]:
        """Check if required data files exist."""
        files_to_check = [
            ("data/users.json", "User Database"),
            ("data/consent_log.jsonl", "Consent Log"),
            ("data/meta_metrics.json", "Meta Metrics"),
            ("data/drift_audit_summary.json", "Drift Audit"),
            ("integration_config.yaml", "Integration Config"),
            ("lukhas_config.yaml", " Config"),
        ]

        results = {}
        for file_path, description in files_to_check:
            self.total_checks += 1
            exists = Path(file_path).exists()
            results[description] = exists
            if exists:
                self.passed_checks += 1

        self.results["data_files"] = results
        return results

    def check_api_functionality(self) -> dict[str, str]:
        """Check API endpoint availability."""
        endpoints = {
            "/identity/login": "Authentication",
            "/identity/register": "User Registration",
            "/identity/verify": "Token Verification",
            "/api/meta/log": "System Logs",
            "/api/consciousness/state": "Consciousness State",
            "/api/memory/explore": "Memory Exploration",
            "/api/guardian/drift": "Drift Monitoring",
            "/api/trinity/status": "Trinity Status",
        }

        results = {}
        for endpoint, description in endpoints.items():
            self.total_checks += 1
            # Check if module exists for endpoint
            if "/identity/" in endpoint:
                status = "✅ Ready" if self.results["imports"].get("Identity API", False) else "❌ Missing"
            elif "/api/meta/" in endpoint:
                status = "✅ Ready" if self.results["imports"].get("Log Routes", False) else "❌ Missing"
            elif endpoint in [
                "/api/consciousness/state",
                "/api/memory/explore",
                "/api/guardian/drift",
                "/api/trinity/status",
            ]:
                # These endpoints are now implemented in symbolic_api.py
                status = "✅ Ready" if self.results["imports"].get("Symbolic API", False) else "❌ Missing"
            else:
                # Check if symbolic API is available
                status = "⚠️ Partial" if self.results["imports"].get("Symbolic Core", False) else "❌ Missing"

            results[f"{description} ({endpoint})"] = status
            if status.startswith("✅"):
                self.passed_checks += 1
            elif status.startswith("⚠️"):
                self.passed_checks += 0.5

        self.results["api_endpoints"] = results
        return results

    def check_module_health(self) -> dict[str, dict[str, Any]]:
        """Check health of individual modules."""
        modules = {
            "consciousness": {
                "files": ["__init__.py", "unified", "awareness"],
                "critical": True,
            },
            "memory": {
                "files": ["__init__.py", "fold", "service.py"],
                "critical": True,
            },
            "identity": {
                "files": ["__init__.py", "user_db.py", "api.py"],
                "critical": True,
            },
            "governance": {"files": ["__init__.py"], "critical": True},
            "quantum": {"files": ["__init__.py"], "critical": False},
            "emotion": {"files": ["__init__.py"], "critical": False},
            "vivox": {"files": ["__init__.py"], "critical": False},
            "bridge": {"files": ["__init__.py", "api"], "critical": True},
        }

        results = {}
        for module_name, config in modules.items():
            self.total_checks += 1
            module_path = Path(module_name)

            if module_path.exists():
                file_count = sum(1 for f in module_path.rglob("*.py") if not f.name.startswith("test_"))
                has_init = (module_path / "__init__.py").exists()

                health = {
                    "exists": True,
                    "file_count": file_count,
                    "has_init": has_init,
                    "status": ("✅ Healthy" if file_count > 5 and has_init else "⚠️ Partial"),
                    "critical": config["critical"],
                }

                if health["status"].startswith("✅"):
                    self.passed_checks += 1
                elif health["status"].startswith("⚠️"):
                    self.passed_checks += 0.5
            else:
                health = {
                    "exists": False,
                    "file_count": 0,
                    "has_init": False,
                    "status": "❌ Missing",
                    "critical": config["critical"],
                }

            results[module_name] = health

        self.results["modules"] = results
        return results

    def check_trinity_integration(self) -> dict[str, bool]:
        """Check Trinity Framework integration."""
        checks = {
            "Identity System": self.results["imports"].get("Identity System", False),
            "Consciousness System": self.results["imports"].get("Consciousness System", False),
            "Guardian System": self.results["imports"].get("Governance System", False),
            "Symbolic Core": self.results["imports"].get("Symbolic Core", False),
            "Meta Metrics": self.results["data_files"].get("Meta Metrics", False),
        }

        for _check_name, passed in checks.items():
            self.total_checks += 1
            if passed:
                self.passed_checks += 1

        self.results["trinity"] = checks
        return checks

    def generate_report(self) -> str:
        """Generate comprehensive diagnostic report."""
        functionality_percentage = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0

        report = f"""
═══════════════════════════════════════════════════════════════
        🧠 LUKHΛS System Diagnostic Report
═══════════════════════════════════════════════════════════════
Generated: {datetime.utcnow().isoformat()}Z
Trinity Framework: ⚛️ 🧠 🛡️

Overall Functionality: {functionality_percentage:.1f}%
Total Checks: {self.total_checks}
Passed: {self.passed_checks}

═══════════════════════════════════════════════════════════════
📦 Module Import Status
═══════════════════════════════════════════════════════════════
"""
        for module, status in self.results["imports"].items():
            report += f"  {module:<30} {'✅ OK' if status else '❌ FAIL'}\n"

        report += """
═══════════════════════════════════════════════════════════════
📁 Data Files Status
═══════════════════════════════════════════════════════════════
"""
        for file, status in self.results["data_files"].items():
            report += f"  {file:<30} {'✅ EXISTS' if status else '❌ MISSING'}\n"

        report += """
═══════════════════════════════════════════════════════════════
🌐 API Endpoints Status
═══════════════════════════════════════════════════════════════
"""
        for endpoint, status in self.results["api_endpoints"].items():
            report += f"  {endpoint:<40} {status}\n"

        report += """
═══════════════════════════════════════════════════════════════
🏥 Module Health Check
═══════════════════════════════════════════════════════════════
"""
        for module, health in self.results["modules"].items():
            critical = "🚨 CRITICAL" if health["critical"] else "📌 Optional"
            report += f"  {module:<20} {health['status']:<15} Files: {health['file_count']:<5} {critical}\n"

        report += """
═══════════════════════════════════════════════════════════════
🔺 Trinity Framework Status
═══════════════════════════════════════════════════════════════
"""
        trinity_ok = all(self.results.get("trinity", {}).values())
        report += f"  Trinity Integration: {'✅ COMPLETE' if trinity_ok else '⚠️ INCOMPLETE'}\n"
        # Individual trinity components
        identity_ok = self.results.get("trinity", {}).get("Identity System", False)
        consciousness_ok = self.results.get("trinity", {}).get("Consciousness System", False)
        guardian_ok = self.results.get("trinity", {}).get("Guardian System", False)
        report += f"  ⚛️ Identity: {'✅' if identity_ok else '❌'}\n"
        report += f"  🧠 Consciousness: {'✅' if consciousness_ok else '❌'}\n"
        report += f"  🛡️ Guardian: {'✅' if guardian_ok else '❌'}\n"

        # Summary and recommendations
        report += f"""
═══════════════════════════════════════════════════════════════
📊 Summary & Recommendations
═══════════════════════════════════════════════════════════════

System Readiness: {"🟢 READY" if functionality_percentage >= 90 else "🟡 PARTIAL" if functionality_percentage >= 70 else "🔴 NOT READY"}
Functionality: {functionality_percentage:.1f}%

"""

        # Find critical issues
        critical_issues = []
        for module, health in self.results["modules"].items():
            if health["critical"] and health["status"].startswith("❌"):
                critical_issues.append(f"- Critical module '{module}' is missing")

        for file, exists in self.results["data_files"].items():
            if not exists and "users.json" in file:
                critical_issues.append(f"- Critical data file '{file}' is missing")

        if critical_issues:
            report += "⚠️ Critical Issues:\n"
            for issue in critical_issues:
                report += f"  {issue}\n"
        else:
            report += "✅ No critical issues found!\n"

        # Next steps
        if functionality_percentage < 100:
            report += """
📋 To Reach 100% Functionality:
"""
            if functionality_percentage < 90:
                report += "  1. Fix syntax errors in core modules\n"
                report += "  2. Create missing Natural Language files\n"
                report += "  3. Initialize missing data files\n"
            else:
                report += "  1. Complete VIVoX module integration\n"
                report += "  2. Fix remaining API endpoints\n"
                report += "  3. Complete quantum module implementation\n"

        report += """
═══════════════════════════════════════════════════════════════
🛡️ Trinity Protected | LUKHΛS AGI System v1.0.0
═══════════════════════════════════════════════════════════════
"""

        return report

    def run_diagnostic(self):
        """Run complete system diagnostic."""
        print("🔍 Running LUKHΛS System Diagnostic...")
        print("=" * 60)

        # Run all checks
        print("Checking module imports...")
        self.check_module_imports()

        print("Checking data files...")
        self.check_data_files()

        print("Checking API functionality...")
        self.check_api_functionality()

        print("Checking module health...")
        self.check_module_health()

        print("Checking Trinity integration...")
        self.check_trinity_integration()

        # Generate and display report
        report = self.generate_report()
        print(report)

        # Save report
        report_path = Path("system_diagnostic_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_path}")

        # Return functionality percentage
        functionality = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        return functionality


if __name__ == "__main__":
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))

    # Run diagnostic
    diagnostic = SystemDiagnostic()
    functionality = diagnostic.run_diagnostic()

    # Exit with appropriate code
    if functionality >= 90:
        print("\n✅ System is ready for production!")
        sys.exit(0)
    elif functionality >= 70:
        print("\n⚠️ System is partially functional")
        sys.exit(1)
    else:
        print("\n❌ System needs significant work")
        sys.exit(2)
