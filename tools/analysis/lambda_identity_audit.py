#!/usr/bin/env python3
"""
ΛiD Identity System Audit
========================
Comprehensive audit of the LUKHAS identity system for open-source readiness.
"""
import ast
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class LambdaIDSystemAudit:
    """Audits the ΛiD identity system for security and functionality"""

    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas")
        self.identity_modules = []
        self.security_issues = []
        self.functionality_map = {}
        self.dependencies = defaultdict(set)

    def audit_identity_system(self) -> dict[str, Any]:
        """Run comprehensive audit of ΛiD system"""
        logger.info("🔍 Auditing ΛiD Identity System...")

        # Find all identity-related modules
        self._discover_identity_modules()

        # Analyze functionality
        self._analyze_functionality()

        # Security audit
        self._security_audit()

        # Dependency analysis
        self._analyze_dependencies()

        # Generate recommendations
        report = self._generate_audit_report()

        # Save report
        report_path = self.root_path / "docs" / "reports" / "LAMBDA_ID_AUDIT_REPORT.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self._print_summary(report)
        return report

    def _discover_identity_modules(self):
        """Discover all identity-related modules"""
        logger.info("\n🔎 Discovering identity modules...")

        # Core identity module
        identity_dir = self.root_path / "identity"
        if identity_dir.exists():
            for py_file in identity_dir.rglob("*.py"):
                self.identity_modules.append(py_file)

        # Core identity in core/
        core_identity_dir = self.root_path / "core" / "identity"
        if core_identity_dir.exists():
            for py_file in core_identity_dir.rglob("*.py"):
                self.identity_modules.append(py_file)

        # Search for identity-related files
        for py_file in self.root_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read().lower()

                identity_keywords = [
                    "λid",
                    "lambda_id",
                    "identity",
                    "auth",
                    "login",
                    "user_control",
                ]
                if any(keyword in content for keyword in identity_keywords):
                    if py_file not in self.identity_modules:
                        self.identity_modules.append(py_file)

            except Exception:
                pass

        logger.info(f"   Found {len(self.identity_modules)} identity-related modules")

    def _analyze_functionality(self):
        """Analyze functionality of identity modules"""
        logger.info("\n🔧 Analyzing functionality...")

        functionality_categories = {
            "authentication": ["login", "authenticate", "verify"],
            "authorization": ["authorize", "permission", "access", "tier"],
            "user_management": ["user", "profile", "account"],
            "data_control": ["privacy", "control", "sovereignty"],
            "security": ["encrypt", "hash", "secure", "crypto"],
            "audit": ["audit", "log", "track", "monitor"],
        }

        for module_path in self.identity_modules:
            try:
                with open(module_path, encoding="utf-8") as f:
                    content = f.read()

                relative_path = module_path.relative_to(self.root_path)
                module_functions = []

                # Parse AST to find functions and classes
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            module_functions.append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            module_functions.append(f"class_{node.name}")
                except BaseException:
                    pass

                # Categorize functionality
                module_categories = set()
                content_lower = content.lower()

                for category, keywords in functionality_categories.items():
                    if any(keyword in content_lower for keyword in keywords):
                        module_categories.add(category)

                self.functionality_map[str(relative_path)] = {
                    "categories": list(module_categories),
                    "functions": module_functions,
                    "size_lines": len(content.split("\n")),
                    "has_classes": any(f.startswith("class_") for f in module_functions),
                }

            except Exception as e:
                logger.warning(f"   Error analyzing {module_path}: {e}")

        # Analyze coverage
        total_categories = len(functionality_categories)
        covered_categories = set()
        for module_data in self.functionality_map.values():
            covered_categories.update(module_data["categories"])

        coverage = len(covered_categories) / total_categories * 100
        logger.info(f"   Functionality coverage: {coverage:.1f}% ({len(covered_categories)}/{total_categories})")

    def _security_audit(self):
        """Perform security audit"""
        logger.info("\n🔒 Performing security audit...")

        security_patterns = {
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            "weak_crypto": [r"md5\(", r"sha1\(", r"DES\(", r"RC4\("],
            "insecure_practices": [
                r"eval\(",
                r"exec\(",
                r"pickle\.loads",
                r"subprocess\.shell=True",
            ],
            "missing_validation": [
                r"request\.(form|args|json).*without.*validation",
                r"user_input.*without.*sanitization",
            ],
        }

        for module_path in self.identity_modules:
            try:
                with open(module_path, encoding="utf-8") as f:
                    content = f.read()

                relative_path = module_path.relative_to(self.root_path)

                for issue_type, patterns in security_patterns.items():
                    import re

                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            self.security_issues.append(
                                {
                                    "file": str(relative_path),
                                    "line": line_num,
                                    "issue_type": issue_type,
                                    "pattern": pattern,
                                    "severity": self._get_severity(issue_type),
                                }
                            )

            except Exception:
                pass

        logger.info(f"   Found {len(self.security_issues)} potential security issues")

    def _get_severity(self, issue_type: str) -> str:
        """Get severity level for security issue"""
        severity_map = {
            "hardcoded_secrets": "HIGH",
            "weak_crypto": "HIGH",
            "insecure_practices": "MEDIUM",
            "missing_validation": "MEDIUM",
        }
        return severity_map.get(issue_type, "LOW")

    def _analyze_dependencies(self):
        """Analyze dependencies between identity modules"""
        logger.info("\n🔗 Analyzing dependencies...")

        for module_path in self.identity_modules:
            try:
                with open(module_path, encoding="utf-8") as f:
                    content = f.read()

                relative_path = str(module_path.relative_to(self.root_path))

                # Find imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module:
                                # Check if importing from another identity module
                                if any(identity_part in node.module for identity_part in ["identity", "auth"]):
                                    self.dependencies[relative_path].add(node.module)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if any(identity_part in alias.name for identity_part in ["identity", "auth"]):
                                    self.dependencies[relative_path].add(alias.name)
                except BaseException:
                    pass

            except Exception:
                pass

        logger.info(f"   Analyzed dependencies for {len(self.dependencies)} modules")

    def _generate_audit_report(self) -> dict[str, Any]:
        """Generate comprehensive audit report"""

        # Calculate metrics
        total_modules = len(self.identity_modules)
        total_functions = sum(len(data["functions"]) for data in self.functionality_map.values())
        total_lines = sum(data["size_lines"] for data in self.functionality_map.values())

        high_severity_issues = [issue for issue in self.security_issues if issue["severity"] == "HIGH"]
        [issue for issue in self.security_issues if issue["severity"] == "MEDIUM"]

        # Generate recommendations
        recommendations = []

        if high_severity_issues:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Security",
                    "issue": f"{len(high_severity_issues)} high-severity security issues found",
                    "action": "Review and fix hardcoded secrets and weak cryptography before open-source release",
                }
            )

        if "authentication" not in [cat for data in self.functionality_map.values() for cat in data["categories"]]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Functionality",
                    "issue": "Authentication functionality not clearly identified",
                    "action": "Implement or clearly document authentication mechanisms",
                }
            )

        if total_lines < 1000:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Implementation",
                    "issue": "Identity system appears minimal",
                    "action": "Consider expanding core identity features for production readiness",
                }
            )

        # Open-source readiness checklist
        readiness_checklist = {
            "security_audit_complete": len(high_severity_issues) == 0,
            "documentation_exists": False,  # Will be updated after doc creation
            "no_hardcoded_secrets": not any(
                issue["issue_type"] == "hardcoded_secrets" for issue in self.security_issues
            ),
            "clear_api_definition": "authentication"
            in [cat for data in self.functionality_map.values() for cat in data["categories"]],
            "license_compatible": True,  # Assume compatible
            "test_coverage": False,  # Will need separate analysis
        }

        readiness_score = sum(readiness_checklist.values()) / len(readiness_checklist) * 100

        # Convert sets to lists for JSON serialization
        serializable_dependencies = {}
        for module, deps in self.dependencies.items():
            serializable_dependencies[module] = list(deps)

        return {
            "audit_timestamp": "2025-08-03T17:00:00Z",
            "summary": {
                "total_modules": total_modules,
                "total_functions": total_functions,
                "total_lines": total_lines,
                "security_issues": len(self.security_issues),
                "high_severity_issues": len(high_severity_issues),
                "readiness_score": readiness_score,
            },
            "functionality_analysis": self.functionality_map,
            "security_issues": self.security_issues[:20],  # Top 20 issues
            "dependencies": serializable_dependencies,
            "recommendations": recommendations,
            "readiness_checklist": readiness_checklist,
            "next_steps": [
                "Fix all high-severity security issues",
                "Create comprehensive ΛiD documentation",
                "Implement test coverage for identity modules",
                "Create developer API documentation",
                "Design user onboarding flow",
            ],
        }

    def _print_summary(self, report: dict[str, Any]):
        """Print audit summary"""
        print("\n" + "=" * 80)
        print("🔐 ΛiD IDENTITY SYSTEM AUDIT SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print("\n📊 System Overview:")
        print(f"   Modules analyzed: {summary['total_modules']}")
        print(f"   Functions found: {summary['total_functions']}")
        print(f"   Total code lines: {summary['total_lines']:,}")
        print(f"   Security issues: {summary['security_issues']} ({summary['high_severity_issues']} high severity)")
        print(f"   Open-source readiness: {summary['readiness_score']:.1f}%")

        if report["security_issues"]:
            print("\n⚠️  Top Security Issues:")
            for issue in report["security_issues"][:5]:
                print(f"   [{issue['severity']}] {issue['issue_type']} in {issue['file']}:{issue['line']}")

        print("\n💡 Key Recommendations:")
        for rec in report["recommendations"][:3]:
            print(f"   [{rec['priority']}] {rec['issue']}")
            print(f"   → {rec['action']}")

        print("\n📁 Full report: docs/reports/LAMBDA_ID_AUDIT_REPORT.json")
        print("=" * 80)


def main():
    """Run ΛiD identity system audit"""
    auditor = LambdaIDSystemAudit()
    auditor.audit_identity_system()


if __name__ == "__main__":
    main()
