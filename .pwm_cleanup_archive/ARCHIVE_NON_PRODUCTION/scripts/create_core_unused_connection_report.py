#!/usr/bin/env python3
"""
Core Unused Files Connection Report Generator
Filter unused files to focus on core system files that need integration
"""

import ast
import json
import os
from datetime import datetime
from typing import Any, Dict, List


class CoreUnusedConnectionAnalyzer:
    def __init__(self, unused_files_report: str = "scripts/unused_files_report.json"):
        self.unused_files_report = unused_files_report
        self.unused_files = []
        self.core_unused_files = []
        self.connection_analysis = {}

        # Files to exclude (already handled or not core system files)
        self.exclude_patterns = {
            # Already consolidated
            "orchestrat",
            "orchestration",
            # Test/Demo/Benchmark files
            "test",
            "tests",
            "benchmark",
            "benchmarks",
            "demo",
            "example",
            "examples",
            # Tool/Utility files
            "tools",
            "scripts",
            "devtools",
            "cli",
            # Documentation/Config
            "docs",
            "doc",
            "readme",
            "config",
            "__init__.py",
            # Build/Deploy
            "build",
            "dist",
            "deploy",
            "migration",
            "migrations",
            # Specific exclude patterns
            "fix_",
            "add_",
            "regenerate_",
            "setup_",
            "meta/",
            ".vscode/",
            # Interface/UI (lower priority)
            "interface",
            "ui",
            "gui",
            "streamlit",
            "web_",
            "dashboard",
            # Archive/Legacy
            "archive",
            "legacy",
            "migrated",
            "old_",
            "deprecated",
        }

        # Core system categories we want to focus on
        self.core_categories = {
            "consciousness": "Consciousness and awareness systems",
            "memory": "Memory management and storage",
            "reasoning": "Reasoning and logic systems",
            "creativity": "Creative and dream systems",
            "learning": "Learning and adaptation",
            "quantum": "Quantum processing systems",
            "symbolic": "Symbolic processing",
            "identity": "Identity and authentication",
            "ethics": "Ethics and governance",
            "bio": "Bio-inspired systems",
            "emotion": "Emotional processing",
            "voice": "Voice and audio processing",
            "bridge": "Integration bridges",
            "core": "Core system functionality",
            "api": "API and service layers",
        }

    def load_unused_files(self) -> bool:
        """Load unused files from report"""
        try:
            with open(self.unused_files_report) as f:
                data = json.load(f)

            self.unused_files = data.get("unused_list", [])
            print(f"📊 Loaded {len(self.unused_files)} unused files from report")
            return True

        except Exception as e:
            print(f"❌ Error loading unused files report: {e}")
            return False

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from core analysis"""
        file_path_lower = file_path.lower()

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in file_path_lower:
                return True

        # Exclude files that are clearly utilities or generated
        if any(
            keyword in file_path_lower
            for keyword in [
                "generator",
                "builder",
                "compiler",
                "parser",
                "validator",
                "formatter",
                "converter",
                "migrator",
                "installer",
            ]
        ):
            return True

        return False

    def categorize_core_file(self, file_path: str) -> str:
        """Categorize a core file by its primary function"""
        file_path_lower = file_path.lower()

        # Check each core category
        for category, description in self.core_categories.items():
            if category in file_path_lower:
                return category

        # Special case mappings
        if "neural" in file_path_lower or "neuro" in file_path_lower:
            return "reasoning"
        elif "dream" in file_path_lower:
            return "creativity"
        elif (
            "glyph" in file_path_lower
            or "qr" in file_path_lower
            or "vault" in file_path_lower
            or "security" in file_path_lower
        ):
            return "identity"
        elif "meta" in file_path_lower and "learning" in file_path_lower:
            return "learning"
        elif (
            "colony" in file_path_lower
            or "swarm" in file_path_lower
            or "trace" in file_path_lower
            or "log" in file_path_lower
        ):
            return "core"

        return "other"

    def filter_core_unused_files(self) -> List[str]:
        """Filter unused files to focus on core system files"""
        print(
            f"🔍 Filtering {len(self.unused_files)} unused files for core system files..."
        )

        core_files = []
        excluded_count = 0

        for file_path in self.unused_files:
            if self.should_exclude_file(file_path):
                excluded_count += 1
                continue

            # Only include files that are in core categories
            category = self.categorize_core_file(file_path)
            if category != "other":
                core_files.append(file_path)

        print("📋 Filtered results:")
        print(f"   Original unused files: {len(self.unused_files)}")
        print(f"   Excluded files: {excluded_count}")
        print(f"   Core system files: {len(core_files)}")

        self.core_unused_files = core_files
        return core_files

    def analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze a file's imports and potential connections"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}

            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST to extract imports and structure
            tree = ast.parse(content)

            imports = []
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            imports.append(f"{node.module}.{name.name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only top-level functions
                    functions.append(node.name)

            # Find potential connection points
            connection_hints = self._find_connection_hints(content, file_path)

            return {
                "file_path": file_path,
                "size_bytes": len(content),
                "lines": len(content.split("\n")),
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "connection_hints": connection_hints,
                "category": self.categorize_core_file(file_path),
            }

        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "category": self.categorize_core_file(file_path),
            }

    def _find_connection_hints(self, content: str, file_path: str) -> List[str]:
        """Find hints about how this file should be connected"""
        hints = []
        content_lower = content.lower()

        # Look for integration patterns
        if "def main(" in content:
            hints.append("Has main() function - may be executable entry point")

        if "class" in content and "service" in content_lower:
            hints.append("Contains service class - may need service registration")

        if "async def" in content:
            hints.append("Contains async functions - may need event loop integration")

        if "from bridge" in content or "import bridge" in content:
            hints.append("Uses bridge modules - may need bridge registration")

        if "message_bus" in content_lower or "event_bus" in content_lower:
            hints.append("Uses message/event bus - may need bus connection")

        if "config" in content_lower and (
            "load" in content_lower or "read" in content_lower
        ):
            hints.append("Handles configuration - may need config system integration")

        if "api" in file_path.lower() and (
            "router" in content_lower or "endpoint" in content_lower
        ):
            hints.append("Contains API endpoints - may need router registration")

        if "memory" in file_path.lower() and (
            "store" in content_lower or "cache" in content_lower
        ):
            hints.append(
                "Memory system component - may need memory manager integration"
            )

        if "identity" in file_path.lower() and (
            "auth" in content_lower or "user" in content_lower
        ):
            hints.append("Identity component - may need identity system integration")

        # Look for specific integration keywords
        integration_keywords = [
            "register",
            "initialize",
            "setup",
            "connect",
            "bind",
            "attach",
            "plugin",
            "extension",
            "module",
            "component",
            "service",
        ]

        for keyword in integration_keywords:
            if keyword in content_lower:
                hints.append(f'Contains "{keyword}" - may need integration setup')
                break

        return hints

    def generate_connection_report(self) -> Dict[str, Any]:
        """Generate comprehensive connection report for core unused files"""
        print(
            f"\\n📊 Generating connection analysis for {len(self.core_unused_files)} core files..."
        )

        # Analyze each core file
        file_analyses = {}
        category_summary = {}

        for i, file_path in enumerate(self.core_unused_files, 1):
            analysis = self.analyze_file_dependencies(file_path)
            file_analyses[file_path] = analysis

            # Update category summary
            category = analysis.get("category", "other")
            if category not in category_summary:
                category_summary[category] = {
                    "count": 0,
                    "files": [],
                    "total_size": 0,
                    "common_imports": set(),
                    "connection_opportunities": [],
                }

            category_summary[category]["count"] += 1
            category_summary[category]["files"].append(file_path)
            category_summary[category]["total_size"] += analysis.get("size_bytes", 0)

            # Track common imports
            for imp in analysis.get("imports", []):
                category_summary[category]["common_imports"].add(imp)

            if i % 10 == 0:
                print(f"   Analyzed {i}/{len(self.core_unused_files)} files...")

        # Generate connection opportunities by category
        for category, info in category_summary.items():
            opportunities = self._generate_category_connection_opportunities(
                category, info
            )
            info["connection_opportunities"] = opportunities
            info["common_imports"] = list(info["common_imports"])

        # Create final report
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_unused_files": len(self.unused_files),
            "core_unused_files": len(self.core_unused_files),
            "categories_found": len(category_summary),
            "file_analyses": file_analyses,
            "category_summary": category_summary,
            "integration_recommendations": self._generate_integration_recommendations(
                category_summary
            ),
            "priority_files": self._identify_priority_files(file_analyses),
        }

        return report

    def _generate_category_connection_opportunities(
        self, category: str, info: Dict
    ) -> List[str]:
        """Generate connection opportunities for a category"""
        opportunities = []

        if category == "memory":
            opportunities.extend(
                [
                    "Integrate with unified memory orchestrator",
                    "Connect to memory manager service registry",
                    "Add to memory system initialization sequence",
                ]
            )
        elif category == "consciousness":
            opportunities.extend(
                [
                    "Connect to consciousness hub",
                    "Register with awareness system",
                    "Integrate with cognitive architecture",
                ]
            )
        elif category == "reasoning":
            opportunities.extend(
                [
                    "Connect to reasoning engine",
                    "Register with symbolic processing system",
                    "Add to logical inference pipeline",
                ]
            )
        elif category == "creativity":
            opportunities.extend(
                [
                    "Integrate with creative expression engine",
                    "Connect to dream system",
                    "Register with personality system",
                ]
            )
        elif category == "identity":
            opportunities.extend(
                [
                    "Connect to identity hub",
                    "Register with authentication system",
                    "Integrate with QR glyph system",
                ]
            )
        elif category == "api":
            opportunities.extend(
                [
                    "Register API endpoints with main router",
                    "Connect to service discovery",
                    "Add to API documentation system",
                ]
            )
        else:
            opportunities.append(f"Integrate with {category} system hub")

        return opportunities

    def _generate_integration_recommendations(
        self, category_summary: Dict
    ) -> List[str]:
        """Generate overall integration recommendations"""
        recommendations = []

        # High-impact categories
        high_impact = [
            (cat, info) for cat, info in category_summary.items() if info["count"] >= 5
        ]

        if high_impact:
            recommendations.append(
                f"HIGH PRIORITY: Focus on {len(high_impact)} categories with 5+ files each"
            )
            for cat, info in sorted(
                high_impact, key=lambda x: x[1]["count"], reverse=True
            ):
                recommendations.append(
                    f"  - {cat}: {info['count']} files ({info['total_size']/1024:.1f} KB)"
                )

        # Common integration patterns
        all_imports = set()
        for info in category_summary.values():
            all_imports.update(info.get("common_imports", []))

        if "bridge" in str(all_imports):
            recommendations.append(
                "INTEGRATION: Many files use bridge modules - create bridge registry"
            )

        if "service" in str(all_imports):
            recommendations.append(
                "INTEGRATION: Many files are services - create service discovery system"
            )

        recommendations.append(
            f"TOTAL IMPACT: {len(self.core_unused_files)} core files need integration"
        )

        return recommendations

    def _identify_priority_files(self, file_analyses: Dict) -> List[Dict]:
        """Identify highest priority files for integration"""
        priority_files = []

        for file_path, analysis in file_analyses.items():
            if "error" in analysis:
                continue

            # Calculate priority score
            score = 0

            # Size bonus (larger files likely more important)
            score += min(analysis.get("size_bytes", 0) / 1000, 10)

            # Class/function bonus
            score += len(analysis.get("classes", [])) * 2
            score += len(analysis.get("functions", []))

            # Connection hints bonus
            score += len(analysis.get("connection_hints", [])) * 3

            # Category bonus
            category = analysis.get("category", "other")
            if category in ["memory", "consciousness", "reasoning", "core"]:
                score += 5
            elif category in ["creativity", "identity", "api"]:
                score += 3

            priority_files.append(
                {
                    "file_path": file_path,
                    "category": category,
                    "priority_score": round(score, 1),
                    "size_kb": round(analysis.get("size_bytes", 0) / 1024, 1),
                    "classes": len(analysis.get("classes", [])),
                    "functions": len(analysis.get("functions", [])),
                    "connection_hints": analysis.get("connection_hints", [])[
                        :3
                    ],  # Top 3 hints
                }
            )

        # Sort by priority score
        priority_files.sort(key=lambda x: x["priority_score"], reverse=True)

        return priority_files[:20]  # Top 20 priority files

    def save_report(self, report: Dict, filename: str = None) -> str:
        """Save connection report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"core_unused_connection_report_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        return filename

    def print_summary(self, report: Dict):
        """Print connection report summary"""
        print(f"\\n{'='*80}")
        print("🔍 CORE UNUSED FILES CONNECTION ANALYSIS")
        print(f"{'='*80}")

        print("\\n📊 Summary:")
        print(f"  Total unused files: {report['total_unused_files']}")
        print(f"  Core system files: {report['core_unused_files']}")
        print(f"  Categories found: {report['categories_found']}")

        print("\\n📂 Files by Category:")
        category_summary = report["category_summary"]
        for category, info in sorted(
            category_summary.items(), key=lambda x: x[1]["count"], reverse=True
        ):
            if info["count"] > 0:
                description = self.core_categories.get(category, "Other files")
                print(
                    f"  {category:15} {info['count']:3} files ({info['total_size']/1024:6.1f} KB) - {description}"
                )

        print("\\n🎯 Top 10 Priority Files:")
        for i, file_info in enumerate(report["priority_files"][:10], 1):
            print(f"  {i:2}. {file_info['file_path']}")
            print(
                f"      Category: {file_info['category']} | Priority: {file_info['priority_score']} | Size: {file_info['size_kb']} KB"
            )
            if file_info["connection_hints"]:
                print(f"      Hints: {', '.join(file_info['connection_hints'])}")

        print("\\n💡 Integration Recommendations:")
        for i, rec in enumerate(report["integration_recommendations"], 1):
            print(f"  {i}. {rec}")


def main():
    analyzer = CoreUnusedConnectionAnalyzer()

    # Load and filter unused files
    if not analyzer.load_unused_files():
        return 1

    core_files = analyzer.filter_core_unused_files()
    if not core_files:
        print("❌ No core unused files found to analyze")
        return 1

    # Generate connection report
    report = analyzer.generate_connection_report()

    # Save report
    report_file = analyzer.save_report(report)
    print(f"\\n📄 Connection report saved to: {report_file}")

    # Print summary
    analyzer.print_summary(report)

    print("\\n✅ Core unused files connection analysis complete!")
    print("📋 Next steps:")
    print("   1. Review priority files for immediate integration")
    print("   2. Create integration scripts for high-impact categories")
    print(f"   3. Focus on {report['categories_found']} categories systematically")

    return 0


if __name__ == "__main__":
    exit(main())
