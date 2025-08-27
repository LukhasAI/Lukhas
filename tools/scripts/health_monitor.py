#!/usr/bin/env python3
"""
LUKHAS Health Monitor - System Self-Awareness and Emergency Surgery
This is the system's consciousness about its own health
"""

import ast
import json
import os
from datetime import datetime
from pathlib import Path


class SystemHealthMonitor:
    """The system's self-awareness - monitors health and reports issues"""

    def __init__(self):
        self.health_status = {
            "overall": "CRITICAL",
            "modules": {},
            "merge_conflicts": 0,
            "syntax_errors": [],
            "broken_imports": [],
            "missing_files": [],
            "circular_dependencies": [],
            "timestamp": datetime.now().isoformat(),
        }

    def check_vital_signs(self) -> dict:
        """Check system vital signs"""
        print("🏥 Starting LUKHAS Health Check...")

        # Check for merge conflicts
        self.check_merge_conflicts()

        # Check for syntax errors
        self.check_syntax_errors()

        # Check for main entry points
        self.check_entry_points()

        # Check module health
        self.check_module_health()

        # Determine overall health
        self.diagnose_overall_health()

        return self.health_status

    def check_merge_conflicts(self):
        """Check for Git merge conflicts"""
        print("🔍 Checking for merge conflicts...")

        conflicts = []
        for root, _dirs, files in os.walk("."):
            # Skip venv and git directories
            if ".venv" in root or ".git" in root or "._cleanup_archive" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        if "<<<<<<< HEAD" in content:
                            conflict_count = content.count("<<<<<<< HEAD")
                            conflicts.append(
                                {"file": file_path, "conflicts": conflict_count}
                            )
                    except BaseException:
                        pass

        self.health_status["merge_conflicts"] = len(conflicts)
        self.health_status["conflict_files"] = conflicts

        if conflicts:
            print(f"❌ Found {len(conflicts)} files with merge conflicts!")
        else:
            print("✅ No merge conflicts found")

    def check_syntax_errors(self):
        """Check for Python syntax errors"""
        print("🔍 Checking for syntax errors...")

        errors = []
        for root, _dirs, files in os.walk("."):
            if ".venv" in root or ".git" in root or "._cleanup_archive" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        # Try to parse the file
                        ast.parse(content)
                    except SyntaxError as e:
                        errors.append(
                            {"file": file_path, "error": str(e), "line": e.lineno}
                        )
                    except Exception:
                        pass

        self.health_status["syntax_errors"] = errors

        if errors:
            print(f"❌ Found {len(errors)} files with syntax errors!")
        else:
            print("✅ No syntax errors found")

    def check_entry_points(self):
        """Check for system entry points"""
        print("🔍 Checking for entry points...")

        main_files = []
        for root, _dirs, files in os.walk("."):
            if ".venv" in root or ".git" in root or "._cleanup_archive" in root:
                continue

            if "main.py" in files:
                main_files.append(os.path.join(root, "main.py"))

        self.health_status["entry_points"] = main_files

        # Check for root main.py
        if os.path.exists("./main.py"):
            print("✅ Root main.py found")
        else:
            print("❌ No root main.py - system lacks primary entry point!")
            self.health_status["missing_files"].append("./main.py")

    def check_module_health(self):
        """Check health of each major module"""
        print("🔍 Checking module health...")

        modules = {
            "core": "Brain Stem",
            "consciousness": "Cortex",
            "memory": "Hippocampus",
            "quantum": "Quantum Processor (to be renamed QIM)",
            "emotion": "Limbic System",
            "governance": "Immune System",
            "bridge": "Peripheral Nervous",
            "orchestration": "Coordinator",
            "identity": "Identity System",
            "bio": "Biological Adaptation",
        }

        for module, description in modules.items():
            if os.path.exists(module):
                # Count Python files
                py_files = list(Path(module).rglob("*.py"))

                # Check for __init__.py
                has_init = os.path.exists(os.path.join(module, "__init__.py"))

                # Check for tests
                has_tests = os.path.exists(
                    os.path.join(module, "tests")
                ) or os.path.exists(f"tests/{module}")

                # Check for docs
                has_docs = os.path.exists(
                    os.path.join(module, "docs")
                ) or os.path.exists(os.path.join(module, "README.md"))

                self.health_status["modules"][module] = {
                    "description": description,
                    "exists": True,
                    "py_files": len(py_files),
                    "has_init": has_init,
                    "has_tests": has_tests,
                    "has_docs": has_docs,
                    "health": (
                        "HEALTHY" if has_init and len(py_files) > 0 else "UNHEALTHY"
                    ),
                }
            else:
                self.health_status["modules"][module] = {
                    "description": description,
                    "exists": False,
                    "health": "MISSING",
                }

    def diagnose_overall_health(self):
        """Determine overall system health"""

        # Critical issues
        if self.health_status["merge_conflicts"] > 0:
            self.health_status["overall"] = "CRITICAL - MERGE CONFLICTS"
        elif len(self.health_status["syntax_errors"]) > 0:
            self.health_status["overall"] = "CRITICAL - SYNTAX ERRORS"
        elif "./main.py" in self.health_status["missing_files"]:
            self.health_status["overall"] = "SEVERE - NO ENTRY POINT"
        else:
            # Check module health
            unhealthy_modules = sum(
                1
                for m in self.health_status["modules"].values()
                if m.get("health") != "HEALTHY"
            )

            if unhealthy_modules > 5:
                self.health_status["overall"] = "POOR"
            elif unhealthy_modules > 2:
                self.health_status["overall"] = "FAIR"
            elif unhealthy_modules > 0:
                self.health_status["overall"] = "GOOD"
            else:
                self.health_status["overall"] = "EXCELLENT"

    def generate_health_report(self) -> str:
        """Generate a human-readable health report"""

        report = f"""
# 🏥 LUKHAS HEALTH REPORT
Generated: {self.health_status['timestamp']}

## Overall Status: {self.health_status['overall']}

## 🚨 Critical Issues
- Merge Conflicts: {self.health_status['merge_conflicts']} files
- Syntax Errors: {len(self.health_status['syntax_errors'])} files
- Missing Entry Point: {'YES' if './main.py' in self.health_status['missing_files'] else 'NO'}

## 📊 Module Health
"""

        for module, status in self.health_status["modules"].items():
            emoji = "✅" if status.get("health") == "HEALTHY" else "❌"
            report += f"\n##"description']}\n"

            if status["exists"]:
                report += f"- Python Files: {status['py_files']}\n"
                report += f"- Has __init__.py: {'✅' if status['has_init'] else '❌'}\n"
                report += f"- Has Tests: {'✅' if status['has_tests'] else '❌'}\n"
                report += f"- Has Docs: {'✅' if status['has_docs'] else '❌'}\n"
            else:
                report += "- MODULE MISSING!\n"

        # Prescriptions
        report += "\n## 💊 Prescriptions\n"

        if self.health_status["merge_conflicts"] > 0:
            report += (
                "1. **URGENT**: Resolve merge conflicts using conflict_healer.py\n"
            )

        if len(self.health_status["syntax_errors"]) > 0:
            report += "2. **URGENT**: Fix syntax errors using syntax_doctor.py\n"

        if "./main.py" in self.health_status["missing_files"]:
            report += "3. **CRITICAL**: Create main.py entry point using bootstrap.py\n"

        report += "\n## 🔧 Next Steps\n"
        report += (
            "1. Run `python healing/emergency_surgery.py` to auto-fix critical issues\n"
        )
        report += "2. Run `python bootstrap.py` to create system startup sequence\n"
        report += "3. Run this health check again to verify improvements\n"

        return report

    def save_health_data(self):
        """Save health data for tracking"""

        # Create health_reports directory
        os.makedirs("health_reports", exist_ok=True)

        # Save JSON data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = f"health_reports/health_check_{timestamp}.json"

        with open(json_path, "w") as f:
            json.dump(self.health_status, f, indent=2, default=str)

        # Save human-readable report
        report_path = f"health_reports/health_report_{timestamp}.md"
        with open(report_path, "w") as f:
            f.write(self.generate_health_report())

        print(f"\n📋 Health report saved to: {report_path}")
        return report_path


def main():
    """Run system health check"""

    monitor = SystemHealthMonitor()

    print(
        """
╔══════════════════════════════════════════════════╗
║        LUKHAS SYSTEM HEALTH MONITOR              ║
║     "A healthy system is a happy system"         ║
╚══════════════════════════════════════════════════╝
    """
    )

    # Check vital signs
    health_status = monitor.check_vital_signs()

    # Generate and display report
    report = monitor.generate_health_report()
    print(report)

    # Save report
    monitor.save_health_data()

    # Emergency recommendations
    if health_status["overall"] in ["CRITICAL", "SEVERE"]:
        print("\n🚨 EMERGENCY PROTOCOL ACTIVATED!")
        print("The system requires immediate intervention.")
        print("Recommended actions:")
        print("1. Run: python healing/conflict_healer.py")
        print("2. Run: python healing/syntax_doctor.py")
        print("3. Run: python bootstrap.py --emergency")

    return health_status["overall"]


if __name__ == "__main__":
    main()
