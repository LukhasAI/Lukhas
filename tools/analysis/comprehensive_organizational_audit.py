#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE ORGANIZATIONAL AUDIT
====================================

Performs a thorough analysis of the lukhas workspace to identify
all organizational debt and structural issues that prevent
commercial deployment readiness.
"""

import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class OrganizationalAuditor:
    """Comprehensive organizational debt analyzer."""

    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

        # Define what should NOT be in production-ready structure
        self.problematic_patterns = {
            "legacy_files": [
                "Claude_Tasks.md",
                "agent_task.md",
                "TODO.md",
                "NOTES.md",
                "temp.py",
                "test.py",
                "debug.py",
                "old_*.py",
                "backup_*.py",
                "*.tmp",
                "*.bak",
                "*.old",
                "*_old.*",
                "*_backup.*",
            ],
            "development_artifacts": [
                ".DS_Store",
                "Thumbs.db",
                "*.pyc",
                "*.pyo",
                "__pycache__",
                "*.log",
                "*.swp",
                "*.swo",
                "*~",
                ".pytest_cache",
            ],
            "misplaced_content": [
                "dream*",
                "voice*",
                "memory*",
                "bio*",
                "identity*",
                "governance*",
            ],
            "wrong_locations": {
                "task_files": ["Claude_Tasks.md", "agent_task.md"],
                "test_files": ["test_*.py", "*_test.py"],
                "config_files": ["config.py", "settings.py", "*.json", "*.yaml"],
                "documentation": ["*.md", "*.rst", "*.txt"],
            },
        }

        # Define expected commercial structure
        self.expected_structure = {
            "lukhas/": ["core/", "modules/", "plugins/", "api/", "tests/"],
            "documentation/": ["api/", "user/", "developer/", "deployment/"],
            "scripts/": ["deployment/", "maintenance/", "development/"],
            "tests/": ["unit/", "integration/", "system/", "performance/"],
            "config/": ["production/", "development/", "testing/"],
        }

    def audit_workspace(self) -> dict[str, Any]:
        """Perform comprehensive organizational audit."""
        logger.info("🔍 Starting comprehensive organizational audit...")

        # Scan all files and directories
        self._scan_file_structure()
        self._identify_misplaced_files()
        self._check_module_organization()
        self._analyze_naming_conventions()
        self._check_documentation_structure()
        self._identify_duplicate_functionality()
        self._assess_commercial_readiness()

        return self._generate_audit_report()

    def _scan_file_structure(self):
        """Scan entire file structure for issues."""
        logger.info("📂 Scanning file structure...")

        for root, dirs, files in os.walk(self.workspace):
            # Skip virtual environment
            if ".venv" in root:
                continue

            root_path = Path(root)
            relative_path = root_path.relative_to(self.workspace)

            # Check directory structure
            self._check_directory_issues(relative_path, dirs)

            # Check files in this directory
            for file in files:
                file_path = root_path / file
                self._check_file_issues(file_path)

    def _check_directory_issues(self, path: Path, subdirs: list[str]):
        """Check for directory structure issues."""
        path_str = str(path)

        # Check for empty directories
        dir_path = self.workspace / path
        if dir_path.exists() and not any(dir_path.iterdir()):
            self.issues["empty_directories"].append(str(path))

        # Check for poorly named directories
        if any(char in path_str for char in ["_backup", "_old", "_temp", "_test"]):
            self.issues["poorly_named_directories"].append(str(path))

        # Check for nested redundancy
        if len(path.parts) > 6:  # Too deeply nested
            self.issues["excessive_nesting"].append(str(path))

    def _check_file_issues(self, file_path: Path):
        """Check individual file for issues."""
        filename = file_path.name
        relative_path = file_path.relative_to(self.workspace)

        # Check for legacy/temporary files
        for pattern in self.problematic_patterns["legacy_files"]:
            if self._matches_pattern(filename, pattern):
                self.issues["legacy_files"].append(str(relative_path))

        # Check for development artifacts
        for pattern in self.problematic_patterns["development_artifacts"]:
            if self._matches_pattern(filename, pattern):
                self.issues["development_artifacts"].append(str(relative_path))

        # Check for misplaced files based on content
        self._check_content_placement(file_path, relative_path)

    def _check_content_placement(self, file_path: Path, relative_path: Path):
        """Check if file content matches its location."""
        try:
            if file_path.suffix == ".py":
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check for test files not in test directories
                if (
                    "def test_" in content or "import pytest" in content or "import unittest" in content
                ) and "test" not in str(relative_path):
                    self.issues["misplaced_tests"].append(str(relative_path))

                # Check for configuration files not in config directories
                if (
                    "CONFIG" in content or "SETTINGS" in content or "configuration" in content.lower()
                ) and "config" not in str(relative_path):
                    self.issues["misplaced_configs"].append(str(relative_path))

            elif file_path.suffix == ".md":
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check for task/todo files in wrong locations
                if any(keyword in content.lower() for keyword in ["todo", "task", "claude", "agent"]) and (
                    "memory" in str(relative_path) or "core" in str(relative_path)
                ):
                    self.issues["misplaced_task_files"].append(str(relative_path))

        except Exception as e:
            self.issues["unreadable_files"].append(f"{relative_path}: {e}")

    def _identify_misplaced_files(self):
        """Identify files in wrong directories."""
        logger.info("🔍 Identifying misplaced files...")

        # Find dream-related files outside dream modules
        dream_files = list(self.workspace.glob("**/dream*"))
        for file in dream_files:
            relative_path = file.relative_to(self.workspace)
            if "dream" not in str(relative_path.parent) and "lukhas/core/dream" not in str(relative_path):
                self.issues["misplaced_dream_files"].append(str(relative_path))

        # Find voice-related files outside voice modules
        voice_files = list(self.workspace.glob("**/voice*"))
        for file in voice_files:
            relative_path = file.relative_to(self.workspace)
            if "voice" not in str(relative_path.parent) and "lukhas/core/voice" not in str(relative_path):
                self.issues["misplaced_voice_files"].append(str(relative_path))

        # Find memory-related files outside memory modules
        memory_files = list(self.workspace.glob("**/memory*"))
        for file in memory_files:
            relative_path = file.relative_to(self.workspace)
            if "memory" not in str(relative_path.parent) and "lukhas/core/memory" not in str(relative_path):
                self.issues["misplaced_memory_files"].append(str(relative_path))

    def _check_module_organization(self):
        """Check modular organization quality."""
        logger.info("🧩 Checking module organization...")

        Λ_core = self.workspace / "lukhas" / "core"
        if Λ_core.exists():
            for module_dir in Λ_core.iterdir():
                if module_dir.is_dir():
                    self._analyze_module_structure(module_dir)

    def _analyze_module_structure(self, module_path: Path):
        """Analyze individual module structure."""
        module_name = module_path.name
        expected_files = ["__init__.py", "core.py"]

        # Check for required files
        for required_file in expected_files:
            if not (module_path / required_file).exists():
                self.issues["incomplete_modules"].append(f"{module_name}: missing {required_file}")

        # Check for foreign files
        for file in module_path.glob("*"):
            if (  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_analysis_comprehensive_organizational_audit_py_L234"}
                file.is_file() and file.name not in expected_files and not file.name.endswith(".py")
            ) and file.suffix in [".md", ".txt", ".json"]:
                # Check if it belongs here
                if module_name.lower() not in file.name.lower():
                    self.issues["foreign_files_in_modules"].append(str(file.relative_to(self.workspace)))

    def _analyze_naming_conventions(self):
        """Check naming convention consistency."""
        logger.info("📝 Analyzing naming conventions...")

        # Check for inconsistent naming patterns
        all_python_files = list(self.workspace.glob("**/*.py"))

        naming_patterns = defaultdict(list)
        for file in all_python_files:
            if ".venv" in str(file):
                continue

            filename = file.stem
            if "_" in filename:
                naming_patterns["snake_case"].append(str(file.relative_to(self.workspace)))
            elif any(c.isupper() for c in filename[1:]):
                naming_patterns["camelCase"].append(str(file.relative_to(self.workspace)))
            else:
                naming_patterns["lowercase"].append(str(file.relative_to(self.workspace)))

        # Report inconsistencies if multiple patterns are heavily used
        if len(naming_patterns) > 1:
            self.issues["inconsistent_naming"] = dict(naming_patterns)

    def _check_documentation_structure(self):
        """Check documentation organization."""
        logger.info("📚 Checking documentation structure...")

        # Find all markdown files
        md_files = list(self.workspace.glob("**/*.md"))

        for md_file in md_files:
            if ".venv" in str(md_file):
                continue

            relative_path = md_file.relative_to(self.workspace)

            # Check if documentation is properly organized
            if "documentation" not in str(relative_path) and "docs" not in str(relative_path):  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_analysis_comprehensive_organizational_audit_py_L279"}
                # Check if it's a legitimate README or module doc
                if md_file.name.lower() not in [
                    "readme.md",
                    "license.md",
                    "changelog.md",
                ]:
                    self.issues["misplaced_documentation"].append(str(relative_path))

    def _identify_duplicate_functionality(self):
        """Identify potential duplicate functionality."""
        logger.info("🔍 Identifying duplicate functionality...")

        # Look for similar file names
        python_files = list(self.workspace.glob("**/*.py"))
        file_stems = defaultdict(list)

        for file in python_files:
            if ".venv" in str(file):
                continue
            stem = file.stem.lower()
            file_stems[stem].append(str(file.relative_to(self.workspace)))

        # Report files with same names in different locations
        for stem, files in file_stems.items():
            if len(files) > 1:
                self.issues["duplicate_filenames"].append({stem: files})

    def _assess_commercial_readiness(self):
        """Assess overall commercial readiness."""
        logger.info("💼 Assessing commercial readiness...")

        # Check for required commercial structure
        required_dirs = ["lukhas/", "tests/", "documentation/", "scripts/"]
        for req_dir in required_dirs:
            if not (self.workspace / req_dir).exists():
                self.issues["missing_required_directories"].append(req_dir)

        # Check for production-ready configuration
        config_files = list(self.workspace.glob("**/config*.py")) + list(self.workspace.glob("**/config*.json"))
        if not config_files:
            self.issues["missing_configuration"].append("No configuration files found")

        # Check for proper testing structure
        test_dirs = list(self.workspace.glob("**/tests/"))
        if not test_dirs:
            self.issues["missing_test_structure"].append("No dedicated test directories found")

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a glob pattern."""
        import fnmatch

        return fnmatch.fnmatch(filename.lower(), pattern.lower())

    def _generate_audit_report(self) -> dict[str, Any]:
        """Generate comprehensive audit report."""
        logger.info("📊 Generating audit report...")

        # Calculate severity scores
        total_issues = sum(len(issues) for issues in self.issues.values())
        critical_issues = len(
            self.issues.get("misplaced_task_files", [])
            + self.issues.get("misplaced_tests", [])
            + self.issues.get("incomplete_modules", [])
        )

        severity = "LOW"
        if critical_issues > 10:
            severity = "CRITICAL"
        elif critical_issues > 5:
            severity = "HIGH"
        elif total_issues > 20:
            severity = "MEDIUM"

        report = {
            "audit_timestamp": "2025-06-05",
            "total_issues_found": total_issues,
            "critical_issues": critical_issues,
            "severity_level": severity,
            "commercial_readiness": ("NOT READY" if severity in ["CRITICAL", "HIGH"] else "NEEDS CLEANUP"),
            "issues_by_category": dict(self.issues),
            "recommendations": self._generate_recommendations(),
            "cleanup_priority": self._prioritize_cleanup(),
        }

        # Save detailed report
        report_path = self.workspace / "COMPREHENSIVE_ORGANIZATIONAL_AUDIT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate human-readable summary
        self._generate_readable_summary(report)

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if self.issues.get("misplaced_task_files"):
            recommendations.append(
                "URGENT: Move all task/agent files to a dedicated 'planning/' or 'docs/internal/' directory"
            )

        if self.issues.get("misplaced_tests"):
            recommendations.append("CRITICAL: Relocate all test files to proper 'tests/' directory structure")

        if self.issues.get("incomplete_modules"):
            recommendations.append("HIGH: Complete all module structures with required files")

        if self.issues.get("empty_directories"):
            recommendations.append("CLEANUP: Remove all empty directories")

        if self.issues.get("legacy_files"):
            recommendations.append("CLEANUP: Remove or archive all legacy/temporary files")

        recommendations.append("STRUCTURE: Implement proper modular organization before commercial deployment")
        recommendations.append("TESTING: Establish comprehensive test directory structure")
        recommendations.append("CONFIG: Create production-ready configuration management")

        return recommendations

    def _prioritize_cleanup(self) -> list[str]:
        """Prioritize cleanup tasks."""
        priority = []

        # Critical priorities
        if self.issues.get("misplaced_task_files"):
            priority.append("1. CRITICAL: Relocate task/planning files")

        if self.issues.get("misplaced_tests"):
            priority.append("2. CRITICAL: Organize test structure")

        if self.issues.get("incomplete_modules"):
            priority.append("3. HIGH: Complete module implementations")

        # Medium priorities
        if self.issues.get("misplaced_dream_files") or self.issues.get("misplaced_voice_files"):
            priority.append("4. MEDIUM: Relocate domain-specific files")

        if self.issues.get("empty_directories"):
            priority.append("5. MEDIUM: Remove empty directories")

        # Low priorities
        if self.issues.get("legacy_files"):
            priority.append("6. LOW: Clean up legacy files")

        return priority

    def _generate_readable_summary(self, report: dict[str, Any]):
        """Generate human-readable summary."""
        summary = f"""
🔍 lukhas WORKSPACE ORGANIZATIONAL AUDIT
======================================
Audit Date: {report["audit_timestamp"]}
Total Issues: {report["total_issues_found"]}
Critical Issues: {report["critical_issues"]}
Severity Level: {report["severity_level"]}
Commercial Readiness: {report["commercial_readiness"]}

📊 ISSUES BY CATEGORY:
"""

        for category, issues in report["issues_by_category"].items():
            if issues:
                issue_list = list(issues) if isinstance(issues, dict) else issues
                summary += f"\n🔸 {category.replace('_', ' ').title()}: {len(issue_list)} issues\n"
                for issue in issue_list[:5]:  # Show first 5
                    summary += f"   - {issue}\n"
                if len(issue_list) > 5:
                    summary += f"   ... and {len(issue_list) - 5} more\n"

        summary += "\n💡 RECOMMENDATIONS:\n"
        for i, rec in enumerate(report["recommendations"], 1):
            summary += f"{i}. {rec}\n"

        summary += "\n🎯 CLEANUP PRIORITY:\n"
        for priority in report["cleanup_priority"]:
            summary += f"{priority}\n"

        summary += f"""
⚠️  COMMERCIAL DEPLOYMENT READINESS: {report["commercial_readiness"]}

Next Steps:
1. Address critical issues immediately
2. Implement proper modular structure
3. Create comprehensive test organization
4. Establish production configuration
5. Re-run audit to verify improvements
"""

        # Save readable summary
        summary_path = self.workspace / "ORGANIZATIONAL_AUDIT_SUMMARY.md"
        with open(summary_path, "w") as f:
            f.write(summary)

        print(summary)


if __name__ == "__main__":
    Λuditor = OrganizationalAuditor("/Users/A_G_I/CodexGPT_Lukhas")
    audit_results = Λuditor.audit_workspace()

    print("\n🎯 AUDIT COMPLETE!")
    print(f"Total Issues: {audit_results['total_issues_found']}")
    print(f"Severity: {audit_results['severity_level']}")
    print(f"Commercial Readiness: {audit_results['commercial_readiness']}")

# Λ Systems 2025 www.ai
