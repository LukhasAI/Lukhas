#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE LUKHAS CORE AUDITOR
Complete audit of ALL components remaining in core directories across the workspace

This script provides the COMPLETE answer to: "What components remain in core directories?"

Features:
- Scans ALL core directories comprehensively
- Categorizes every single file and component
- Identifies unclassified/unknown components
- Provides detailed statistics and recommendations
- Generates comprehensive reports

Author: LUKHAS AI Enhancement Team
Date: 2025-09-12
Version: 2.1.0 - Fixed syntax and import issues
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveCoreAuditor:
    """Complete audit system for all core components in LUKHAS workspace"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.audit_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # ALL possible core directories to audit
        self.core_directories = [
            "core",
            "core_systems",
            "src/core",
            "modules/src/core",
            "test_glossary_workspace/core",
            "legacy_core",
            "old_core",
            "backup_core",
        ]

        # Comprehensive category mapping with keywords
        self.component_categories = {
            "consciousness": [
                "consciousness", "aware", "cognitive", "neural", "lukhas.memory",
                "dream", "emotion", "perception", "recognition", "learning"
            ],
            "symbolic_systems": [
                "symbolic", "glyph", "token", "semantic", "meaning",
                "representation", "encoding", "interpretation"
            ],
            "orchestration": [
                "orchestrat", "coordinator", "dispatcher", "scheduler",
                "workflow", "pipeline", "process", "execution"
            ],
            "identity_auth": [
                "identity", "auth", "user", "access", "permission",
                "tier", "role", "security", "login", "session"
            ],
            "api_interfaces": [
                "api", "endpoint", "route", "handler", "request",
                "response", "middleware", "service", "client"
            ],
            "data_persistence": [
                "database", "storage", "persistence", "repository",
                "model", "entity", "migration", "schema"
            ],
            "quantum_bio": [
                "quantum", "bio", "physics", "algorithm", "computation",
                "simulation", "modeling", "optimization"
            ],
            "testing_validation": [
                "test", "spec", "validation", "verification", "check",
                "assert", "mock", "fixture", "scenario"
            ],
            "utilities_helpers": [
                "util", "helper", "common", "shared", "library",
                "tool", "function", "decorator", "mixin"
            ],
            "configuration": [
                "config", "setting", "environment", "parameter",
                "option", "preference", "initialization"
            ]
        }

        # Initialize results
        self.audit_results = {
            "directories_found": [],
            "categorized_components": defaultdict(list),
            "unclassified_components": [],
            "statistics": defaultdict(int),
            "recommendations": [],
            "audit_metadata": {
                "timestamp": self.audit_timestamp,
                "workspace_root": str(self.workspace_root),
                "total_files_scanned": 0,
                "total_directories_scanned": 0
            }
        }

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Execute complete audit of all core directories"""
        logger.info("🔍 Starting comprehensive core audit...")

        # 1. Discover all core directories
        self._discover_core_directories()

        # 2. Scan and categorize all components
        self._scan_and_categorize_components()

        # 3. Analyze unclassified components
        self._analyze_unclassified_components()

        # 4. Generate statistics
        self._generate_statistics()

        # 5. Generate recommendations
        self._generate_recommendations()

        # 6. Save results
        self._save_audit_results()

        logger.info("✅ Comprehensive audit complete!")
        return self.audit_results

    def _discover_core_directories(self):
        """Discover all existing core directories"""
        logger.info("📁 Discovering core directories...")

        found_directories = []

        for core_dir in self.core_directories:
            dir_path = self.workspace_root / core_dir
            if dir_path.exists() and dir_path.is_dir():
                found_directories.append({
                    "path": str(dir_path),
                    "relative_path": core_dir,
                    "file_count": len(list(dir_path.rglob("*.*"))),
                    "python_files": len(list(dir_path.rglob("*.py"))),
                    "subdirectories": len([d for d in dir_path.iterdir() if d.is_dir()])
                })

        self.audit_results["directories_found"] = found_directories
        self.audit_results["statistics"]["directories_found"] = len(found_directories)

        logger.info(f"   Found {len(found_directories)} core directories")

    def _scan_and_categorize_components(self):
        """Scan all files and categorize them"""
        logger.info("📝 Scanning and categorizing components...")

        total_files = 0

        for dir_info in self.audit_results["directories_found"]:
            dir_path = Path(dir_info["path"])

            # Scan all Python files in this directory
            for py_file in dir_path.rglob("*.py"):
                if self._should_skip_file(py_file):
                    continue

                total_files += 1
                file_info = self._analyze_file(py_file)

                # Categorize based on content analysis
                category = self._categorize_component(file_info)

                if category:
                    self.audit_results["categorized_components"][category].append(file_info)
                else:
                    self.audit_results["unclassified_components"].append(file_info)

        self.audit_results["audit_metadata"]["total_files_scanned"] = total_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "backup",
            "archive"
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for categorization"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.workspace_root)),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "line_count": len(content.split("\n")),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "imports": self._extract_imports(content),
                "classes": self._extract_classes(content),
                "functions": self._extract_functions(content),
                "keywords_found": self._find_keywords(content.lower())
            }

        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.workspace_root)),
                "file_name": file_path.name,
                "error": str(e)
            }

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from file content"""
        import re
        imports = []

        # Find import statements
        import_patterns = [
            r"^import\s+([^\s]+)",
            r"^from\s+([^\s]+)\s+import"
        ]

        for line in content.split("\n"):
            for pattern in import_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    imports.append(match.group(1))

        return imports

    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from file content"""
        import re
        classes = []

        for match in re.finditer(r"^class\s+(\w+)", content, re.MULTILINE):
            classes.append(match.group(1))

        return classes

    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from file content"""
        import re
        functions = []

        for match in re.finditer(r"^def\s+(\w+)", content, re.MULTILINE):
            functions.append(match.group(1))

        return functions

    def _find_keywords(self, content: str) -> Dict[str, List[str]]:
        """Find category keywords in content"""
        found_keywords = defaultdict(list)

        for category, keywords in self.component_categories.items():
            for keyword in keywords:
                if keyword in content:
                    found_keywords[category].append(keyword)

        return dict(found_keywords)

    def _categorize_component(self, file_info: Dict[str, Any]) -> Optional[str]:
        """Categorize a component based on analysis"""
        if "error" in file_info:
            return None

        keywords_found = file_info.get("keywords_found", {})
        file_path = file_info.get("relative_path", "").lower()

        # Score each category
        category_scores = defaultdict(int)

        for category, keywords in keywords_found.items():
            category_scores[category] += len(keywords) * 2

        # Add path-based scoring
        for category, keywords in self.component_categories.items():
            for keyword in keywords:
                if keyword in file_path:
                    category_scores[category] += 1

        # Return highest scoring category if score > 0
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        return None

    def _analyze_unclassified_components(self):
        """Analyze unclassified components for patterns"""
        logger.info("🔍 Analyzing unclassified components...")

        unclassified = self.audit_results["unclassified_components"]

        # Group by directory
        by_directory = defaultdict(list)
        for component in unclassified:
            if "error" not in component:
                dir_path = Path(component["relative_path"]).parent
                by_directory[str(dir_path)].append(component)

        # Add analysis to recommendations
        if by_directory:
            self.audit_results["recommendations"].append({
                "type": "unclassified_analysis",
                "description": f"Found {len(unclassified)} unclassified components",
                "details": dict(by_directory)
            })

    def _generate_statistics(self):
        """Generate comprehensive statistics"""
        logger.info("📊 Generating statistics...")

        stats = self.audit_results["statistics"]

        # File counts by category
        for category, components in self.audit_results["categorized_components"].items():
            stats[f"{category}_count"] = len(components)

        stats["unclassified_count"] = len(self.audit_results["unclassified_components"])
        stats["total_categorized"] = sum(len(comps) for comps in self.audit_results["categorized_components"].values())

        # Calculate percentages
        total_files = stats["total_categorized"] + stats["unclassified_count"]
        if total_files > 0:
            stats["categorization_percentage"] = (stats["total_categorized"] / total_files) * 100

    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        logger.info("💡 Generating recommendations...")

        recommendations = self.audit_results["recommendations"]
        stats = self.audit_results["statistics"]

        # High-level recommendations
        if stats.get("consciousness_count", 0) > 0:
            recommendations.append({
                "type": "consciousness_components",
                "priority": "high",
                "description": f"Found {stats['consciousness_count']} consciousness components",
                "action": "Review for core consciousness functionality"
            })

        if stats.get("symbolic_systems_count", 0) > 0:
            recommendations.append({
                "type": "symbolic_systems",
                "priority": "high",
                "description": f"Found {stats['symbolic_systems_count']} symbolic system components",
                "action": "Ensure symbolic processing is properly integrated"
            })

        if stats.get("unclassified_count", 0) > 10:
            recommendations.append({
                "type": "unclassified_components",
                "priority": "medium",
                "description": f"{stats['unclassified_count']} components need classification",
                "action": "Manual review and categorization needed"
            })

    def _save_audit_results(self):
        """Save audit results to files"""
        logger.info("💾 Saving audit results...")

        # Save JSON report
        json_file = self.workspace_root / f"comprehensive_core_audit_{self.audit_timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(self.audit_results, f, indent=2, default=str)

        # Save human-readable report
        report_file = self.workspace_root / f"comprehensive_core_audit_{self.audit_timestamp}.md"
        self._generate_markdown_report(report_file)

        logger.info(f"   JSON report: {json_file}")
        logger.info(f"   Markdown report: {report_file}")

    def _generate_markdown_report(self, report_file: Path):
        """Generate human-readable markdown report"""
        with open(report_file, "w") as f:
            f.write("# 🔍 Comprehensive LUKHAS Core Audit Report\n\n")
            f.write(f"**Generated:** {self.audit_timestamp}\n")
            f.write(f"**Workspace:** {self.workspace_root}\n\n")

            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            stats = self.audit_results["statistics"]
            f.write(f"- **Directories Found:** {stats.get('directories_found', 0)}\n")
            f.write(f"- **Files Scanned:** {stats.get('total_files_scanned', 0)}\n")
            f.write(f"- **Categorized Components:** {stats.get('total_categorized', 0)}\n")
            f.write(f"- **Unclassified Components:** {stats.get('unclassified_count', 0)}\n")
            if stats.get("categorization_percentage"):
                f.write(f"- **Categorization Success:** {stats['categorization_percentage']:.1f}%\n")
            f.write("\n")

            # Component Categories
            f.write("## 🏗️ Component Categories\n\n")
            for category, components in self.audit_results["categorized_components"].items():
                f.write(f"### {category.replace('_', ' ').title()} ({len(components)} files)\n")
                for component in components[:5]:  # Show first 5
                    f.write(f"- `{component.get('relative_path', 'N/A')}`\n")
                if len(components) > 5:
                    f.write(f"- *... and {len(components) - 5} more files*\n")
                f.write("\n")

            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            for rec in self.audit_results["recommendations"]:
                priority = rec.get("priority", "medium").upper()
                f.write(f"### {priority}: {rec.get('description', 'N/A')}\n")
                f.write(f"**Action:** {rec.get('action', 'Review needed')}\n\n")


def main():
    """Main execution function"""
    print("🔍 LUKHAS Comprehensive Core Auditor")
    print("=" * 50)

    # Get workspace root
    workspace_root = Path.cwd()
    print(f"📁 Workspace: {workspace_root}")

    # Run audit
    auditor = ComprehensiveCoreAuditor(str(workspace_root))
    results = auditor.run_comprehensive_audit()

    # Display summary
    print("\n📊 Audit Summary:")
    stats = results["statistics"]
    print(f"   Directories found: {stats.get('directories_found', 0)}")
    print(f"   Files scanned: {stats.get('total_files_scanned', 0)}")
    print(f"   Categorized: {stats.get('total_categorized', 0)}")
    print(f"   Unclassified: {stats.get('unclassified_count', 0)}")

    if stats.get("categorization_percentage"):
        print(f"   Success rate: {stats['categorization_percentage']:.1f}%")

    print(f"\n📋 Reports generated with timestamp: {auditor.audit_timestamp}")
    print("✅ Comprehensive audit complete!")


if __name__ == "__main__":
    main()
