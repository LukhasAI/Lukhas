#!/usr/bin/env python3
"""
Full Core Connection Report Generator
Analyze the 954 unused core_modules files for integration opportunities
"""

import ast
import json
import os
from datetime import datetime
from typing import Any, Dict, List


class FullCoreConnectionAnalyzer:
    def __init__(self, unused_files_report: str = "scripts/unused_files_report.json"):
        self.unused_files_report = unused_files_report
        self.all_unused_files = []
        self.core_unused_files = []
        self.connection_analysis = {}

        # Files to exclude (already handled or not integration candidates)
        self.exclude_patterns = {
            # Already consolidated
            "orchestrat",
            "orchestration",
            # Tools/utilities/config (lower priority)
            "fix_",
            "add_",
            "setup_",
            "generate_",
            "create_",
            "build_",
            "deploy_",
            "config",
            "settings",
            "__init__.py",
            "validator",
            "parser",
            # Documentation/meta
            "readme",
            "docs",
            "meta/",
            "template",
            "example",
            # Archive/legacy
            "legacy",
            "migrated",
            "old_",
            "deprecated",
            "archive",
            # UI/Interface (lower priority for core system)
            "streamlit",
            "dashboard",
            "gui",
            "web_",
            "ui_",
            "frontend",
        }

        # Core system categories for integration
        self.integration_categories = {
            "memory_systems": {
                "patterns": ["memory/systems/", "memory/core/", "memory/"],
                "priority": "high",
                "description": "Memory management and storage systems",
            },
            "consciousness": {
                "patterns": ["consciousness/", "awareness/", "cognitive/"],
                "priority": "high",
                "description": "Consciousness and awareness systems",
            },
            "reasoning": {
                "patterns": ["reasoning/", "logic/", "inference/", "symbolic/"],
                "priority": "high",
                "description": "Reasoning and symbolic processing",
            },
            "creativity": {
                "patterns": ["creativity/", "dream/", "expression/"],
                "priority": "high",
                "description": "Creative and dream systems",
            },
            "learning": {
                "patterns": ["learning/", "adaptive/", "meta_learning/"],
                "priority": "high",
                "description": "Learning and adaptation systems",
            },
            "identity": {
                "patterns": ["identity/", "auth/", "qr", "glyph", "vault/"],
                "priority": "medium",
                "description": "Identity and authentication",
            },
            "quantum": {
                "patterns": ["quantum/", "bio_quantum", "quantum_"],
                "priority": "medium",
                "description": "Quantum processing systems",
            },
            "bio_systems": {
                "patterns": ["bio/", "biological/", "bio_"],
                "priority": "medium",
                "description": "Bio-inspired systems",
            },
            "emotion": {
                "patterns": ["emotion/", "emotional/", "affect/"],
                "priority": "medium",
                "description": "Emotional processing",
            },
            "voice": {
                "patterns": ["voice/", "audio/", "speech/"],
                "priority": "medium",
                "description": "Voice and audio systems",
            },
            "api_services": {
                "patterns": ["api/", "service/", "endpoint/", "server/"],
                "priority": "medium",
                "description": "API and service layers",
            },
            "bridge_integration": {
                "patterns": ["bridge/", "integration/", "adapter/"],
                "priority": "high",
                "description": "System integration bridges",
            },
            "core_systems": {
                "patterns": ["core/", "system/", "infrastructure/"],
                "priority": "high",
                "description": "Core system functionality",
            },
        }

    def load_unused_files(self) -> bool:
        """Load all unused files from the categorized data"""
        try:
            with open(self.unused_files_report) as f:
                data = json.load(f)

            # Get all categorized unused files
            categorized = data.get("categorized", {})

            # Focus on core_modules (954 files) and other (315 files)
            core_modules = categorized.get("core_modules", [])
            other_files = categorized.get("other", [])

            self.all_unused_files = core_modules + other_files

            print("📊 Loaded unused files:")
            print(f"   Core modules: {len(core_modules)} files")
            print(f"   Other files: {len(other_files)} files")
            print(f"   Total to analyze: {len(self.all_unused_files)} files")

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

        # Exclude very small utility files (likely not important)
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size < 500:  # Less than 500 bytes
                    return True
        except:
            pass

        return False

    def categorize_file(self, file_path: str) -> str:
        """Categorize a file by its integration category"""
        file_path_lower = file_path.lower()

        # Check each integration category
        for category, info in self.integration_categories.items():
            for pattern in info["patterns"]:
                if pattern in file_path_lower:
                    return category

        return "uncategorized"

    def filter_integration_candidates(self) -> List[str]:
        """Filter files to focus on integration candidates"""
        print(
            f"🔍 Filtering {len(self.all_unused_files)} files for integration candidates..."
        )

        candidates = []
        excluded_count = 0
        category_counts = {}

        for file_path in self.all_unused_files:
            if self.should_exclude_file(file_path):
                excluded_count += 1
                continue

            category = self.categorize_file(file_path)
            if category != "uncategorized":
                candidates.append(file_path)
                category_counts[category] = category_counts.get(category, 0) + 1

        print("📋 Filtering results:")
        print(f"   Original files: {len(self.all_unused_files)}")
        print(f"   Excluded files: {excluded_count}")
        print(f"   Integration candidates: {len(candidates)}")
        print(f"   Categories found: {len(category_counts)}")

        # Show category breakdown
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            priority = self.integration_categories.get(category, {}).get(
                "priority", "low"
            )
            print(f"     {category:20} {count:3} files ({priority} priority)")

        self.core_unused_files = candidates
        return candidates

    def analyze_file_for_integration(self, file_path: str) -> Dict[str, Any]:
        """Analyze a file for integration opportunities"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found", "file_path": file_path}

            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Basic metrics
            lines = content.split("\\n")
            size_bytes = len(content)

            # Parse AST for structure analysis
            imports = []
            classes = []
            functions = []
            async_functions = []

            try:
                tree = ast.parse(content)

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
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.AsyncFunctionDef):
                        functions.append(node.name)
                        async_functions.append(node.name)
            except SyntaxError:
                pass

            # Analyze integration opportunities
            integration_opportunities = self._identify_integration_opportunities(
                file_path, content, imports, classes, functions
            )

            # Connection recommendations
            connection_recommendations = self._generate_connection_recommendations(
                file_path, content, imports, classes
            )

            return {
                "file_path": file_path,
                "category": self.categorize_file(file_path),
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 1),
                "lines": len(lines),
                "imports": imports[:10],  # Top 10 imports
                "classes": classes,
                "functions": functions[:10],  # Top 10 functions
                "async_functions": async_functions,
                "integration_opportunities": integration_opportunities,
                "connection_recommendations": connection_recommendations,
                "priority_score": self._calculate_priority_score(
                    file_path, content, classes, functions
                ),
            }

        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "category": self.categorize_file(file_path),
                "priority_score": 0,
            }

    def _identify_integration_opportunities(
        self,
        file_path: str,
        content: str,
        imports: List[str],
        classes: List[str],
        functions: List[str],
    ) -> List[str]:
        """Identify specific integration opportunities"""
        opportunities = []
        content_lower = content.lower()

        # Service/API integration
        if any("service" in cls.lower() for cls in classes):
            opportunities.append(
                "Contains service classes - integrate with service registry"
            )

        if any("api" in imp.lower() or "endpoint" in imp.lower() for imp in imports):
            opportunities.append(
                "Uses API modules - register endpoints with main router"
            )

        # Memory system integration
        if "memory" in file_path.lower():
            if any("manager" in cls.lower() for cls in classes):
                opportunities.append(
                    "Memory manager - connect to unified memory orchestrator"
                )
            if any(
                "store" in func.lower() or "load" in func.lower() for func in functions
            ):
                opportunities.append(
                    "Memory operations - integrate with memory persistence layer"
                )

        # Bridge/adapter integration
        if "bridge" in file_path.lower() or "adapter" in file_path.lower():
            opportunities.append("Bridge/adapter - register with integration hub")

        # Event/message system integration
        if any("event" in imp.lower() or "message" in imp.lower() for imp in imports):
            opportunities.append("Uses events/messages - connect to message bus")

        # Configuration integration
        if "config" in content_lower and any(
            "load" in func.lower() for func in functions
        ):
            opportunities.append(
                "Configuration handler - integrate with config management"
            )

        # Identity/auth integration
        if "identity" in file_path.lower() or "auth" in file_path.lower():
            opportunities.append("Identity/auth component - connect to identity hub")

        # Async/concurrent integration
        if "async def" in content:
            opportunities.append(
                "Async operations - integrate with event loop management"
            )

        # Plugin/extension integration
        if any(
            "plugin" in cls.lower() or "extension" in cls.lower() for cls in classes
        ):
            opportunities.append("Plugin/extension - register with plugin system")

        return opportunities

    def _generate_connection_recommendations(
        self, file_path: str, content: str, imports: List[str], classes: List[str]
    ) -> List[str]:
        """Generate specific connection recommendations"""
        recommendations = []
        category = self.categorize_file(file_path)

        # Category-specific recommendations
        if category == "memory_systems":
            recommendations.extend(
                [
                    "Connect to memory/core/unified_memory_orchestrator.py",
                    "Register with memory manager service registry",
                    "Add to memory system initialization sequence",
                ]
            )
        elif category == "consciousness":
            recommendations.extend(
                [
                    "Connect to consciousness/consciousness_hub.py",
                    "Register with awareness system",
                    "Integrate with cognitive architecture controller",
                ]
            )
        elif category == "reasoning":
            recommendations.extend(
                [
                    "Connect to reasoning/reasoning_engine.py",
                    "Register with symbolic processing system",
                    "Add to reasoning pipeline workflow",
                ]
            )
        elif category == "api_services":
            recommendations.extend(
                [
                    "Register endpoints with main API router",
                    "Connect to service discovery system",
                    "Add to API documentation generation",
                ]
            )
        elif category == "bridge_integration":
            recommendations.extend(
                [
                    "Register with bridge/message_bus.py",
                    "Connect to integration hub",
                    "Add to bridge initialization sequence",
                ]
            )

        # General integration patterns
        if "def main(" in content:
            recommendations.append("Has main() - create startup integration script")

        if any("init" in cls.lower() for cls in classes):
            recommendations.append("Has initialization classes - add to system startup")

        return recommendations

    def _calculate_priority_score(
        self, file_path: str, content: str, classes: List[str], functions: List[str]
    ) -> float:
        """Calculate integration priority score"""
        score = 0.0

        # Category priority bonus
        category = self.categorize_file(file_path)
        category_info = self.integration_categories.get(category, {})
        priority = category_info.get("priority", "low")

        if priority == "high":
            score += 10
        elif priority == "medium":
            score += 5

        # Size/complexity bonus
        score += min(len(content) / 1000, 5)  # Up to 5 points for size
        score += len(classes) * 2  # 2 points per class
        score += len(functions) * 0.5  # 0.5 points per function

        # Integration readiness bonus
        if "service" in content.lower():
            score += 3
        if "class" in content and "def __init__" in content:
            score += 2
        if "async def" in content:
            score += 2
        if "def main(" in content:
            score += 3

        return round(score, 1)

    def generate_full_connection_report(self) -> Dict[str, Any]:
        """Generate comprehensive connection report"""
        print(
            f"\\n📊 Analyzing {len(self.core_unused_files)} integration candidates..."
        )

        # Analyze each file
        file_analyses = {}
        category_summary = {}

        for i, file_path in enumerate(self.core_unused_files, 1):
            analysis = self.analyze_file_for_integration(file_path)
            file_analyses[file_path] = analysis

            # Update category summary
            category = analysis.get("category", "uncategorized")
            if category not in category_summary:
                category_summary[category] = {
                    "files": [],
                    "total_files": 0,
                    "total_size": 0,
                    "avg_priority": 0,
                    "integration_opportunities": set(),
                    "priority": self.integration_categories.get(category, {}).get(
                        "priority", "low"
                    ),
                }

            info = category_summary[category]
            info["files"].append(file_path)
            info["total_files"] += 1
            info["total_size"] += analysis.get("size_bytes", 0)
            info["avg_priority"] += analysis.get("priority_score", 0)

            # Collect integration opportunities
            for opp in analysis.get("integration_opportunities", []):
                info["integration_opportunities"].add(opp)

            if i % 50 == 0:
                print(f"   Analyzed {i}/{len(self.core_unused_files)} files...")

        # Finalize category summaries
        for category, info in category_summary.items():
            if info["total_files"] > 0:
                info["avg_priority"] = round(
                    info["avg_priority"] / info["total_files"], 1
                )
                info["integration_opportunities"] = list(
                    info["integration_opportunities"]
                )

        # Get top priority files
        priority_files = sorted(
            [
                analysis
                for analysis in file_analyses.values()
                if "error" not in analysis
            ],
            key=lambda x: x.get("priority_score", 0),
            reverse=True,
        )[
            :30
        ]  # Top 30 priority files

        # Create final report
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_candidates": len(self.core_unused_files),
            "categories_analyzed": len(category_summary),
            "file_analyses": file_analyses,
            "category_summary": category_summary,
            "priority_files": priority_files,
            "integration_plan": self._create_integration_plan(
                category_summary, priority_files
            ),
        }

        return report

    def _create_integration_plan(
        self, category_summary: Dict, priority_files: List
    ) -> Dict:
        """Create systematic integration plan"""
        plan = {
            "phases": [],
            "quick_wins": [],
            "major_integrations": [],
            "estimated_effort": "medium",
        }

        # Phase 1: High priority categories with most files
        high_priority_cats = [
            (cat, info)
            for cat, info in category_summary.items()
            if info["priority"] == "high" and info["total_files"] >= 5
        ]

        if high_priority_cats:
            phase1_cats = sorted(
                high_priority_cats, key=lambda x: x[1]["total_files"], reverse=True
            )[:3]
            plan["phases"].append(
                {
                    "phase": 1,
                    "focus": "High-impact categories",
                    "categories": [cat for cat, _ in phase1_cats],
                    "estimated_files": sum(
                        info["total_files"] for _, info in phase1_cats
                    ),
                    "timeframe": "1-2 weeks",
                }
            )

        # Phase 2: Medium priority categories
        medium_cats = [
            (cat, info)
            for cat, info in category_summary.items()
            if info["priority"] == "medium" and info["total_files"] >= 3
        ]

        if medium_cats:
            plan["phases"].append(
                {
                    "phase": 2,
                    "focus": "Medium-impact categories",
                    "categories": [cat for cat, _ in medium_cats],
                    "estimated_files": sum(
                        info["total_files"] for _, info in medium_cats
                    ),
                    "timeframe": "2-3 weeks",
                }
            )

        # Quick wins: High priority score files
        plan["quick_wins"] = [
            {
                "file": file_info["file_path"],
                "category": file_info["category"],
                "priority_score": file_info["priority_score"],
                "reason": "High priority score with clear integration path",
            }
            for file_info in priority_files[:10]
            if file_info.get("priority_score", 0) > 15
        ]

        # Major integrations: Categories with many files
        major_cats = [
            (cat, info)
            for cat, info in category_summary.items()
            if info["total_files"] >= 10
        ]

        plan["major_integrations"] = [
            {
                "category": cat,
                "files": info["total_files"],
                "priority": info["priority"],
                "estimated_effort": "high" if info["total_files"] > 20 else "medium",
            }
            for cat, info in major_cats
        ]

        return plan

    def save_report(self, report: Dict, filename: str = None) -> str:
        """Save the connection report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"full_core_connection_report_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        return filename

    def print_executive_summary(self, report: Dict):
        """Print executive summary of the connection analysis"""
        print(f"\\n{'='*100}")
        print("🎯 CORE UNUSED FILES CONNECTION ANALYSIS - EXECUTIVE SUMMARY")
        print(f"{'='*100}")

        print("\\n📊 Analysis Overview:")
        print(f"  Integration candidates analyzed: {report['total_candidates']}")
        print(f"  Categories identified: {report['categories_analyzed']}")
        print(f"  Analysis timestamp: {report['analysis_timestamp']}")

        print("\\n📂 Files by Integration Category:")
        category_summary = report["category_summary"]
        for category, info in sorted(
            category_summary.items(),
            key=lambda x: (x[1]["priority"] == "high", x[1]["total_files"]),
            reverse=True,
        ):
            if info["total_files"] > 0:
                priority_indicator = (
                    "🔥"
                    if info["priority"] == "high"
                    else "⚡" if info["priority"] == "medium" else "📄"
                )
                description = self.integration_categories.get(category, {}).get(
                    "description", "Other files"
                )
                print(
                    f"  {priority_indicator} {category:20} {info['total_files']:3} files ({info['total_size']/1024:6.1f} KB) [{info['priority']} priority]"
                )
                print(f"      {description}")

        print("\\n🎯 Top 15 Priority Integration Candidates:")
        for i, file_info in enumerate(report["priority_files"][:15], 1):
            print(f"  {i:2}. {file_info['file_path']}")
            print(
                f"      Category: {file_info['category']} | Priority: {file_info['priority_score']} | Size: {file_info['size_kb']} KB"
            )
            if file_info.get("connection_recommendations"):
                print(f"      → {file_info['connection_recommendations'][0]}")

        integration_plan = report["integration_plan"]
        if integration_plan["phases"]:
            print("\\n🚀 Recommended Integration Plan:")
            for phase in integration_plan["phases"]:
                print(f"  Phase {phase['phase']}: {phase['focus']}")
                print(f"    Categories: {', '.join(phase['categories'])}")
                print(
                    f"    Files: {phase['estimated_files']} | Timeframe: {phase['timeframe']}"
                )

        if integration_plan["quick_wins"]:
            print(
                f"\\n⚡ Quick Win Opportunities ({len(integration_plan['quick_wins'])} files):"
            )
            for win in integration_plan["quick_wins"][:5]:
                print(f"    • {win['file']} (score: {win['priority_score']})")

        if integration_plan["major_integrations"]:
            print("\\n🏗️  Major Integration Projects:")
            for major in integration_plan["major_integrations"]:
                print(
                    f"    • {major['category']}: {major['files']} files ({major['estimated_effort']} effort)"
                )


def main():
    analyzer = FullCoreConnectionAnalyzer()

    # Load all unused files
    if not analyzer.load_unused_files():
        return 1

    # Filter for integration candidates
    candidates = analyzer.filter_integration_candidates()
    if not candidates:
        print("❌ No integration candidates found")
        return 1

    # Generate comprehensive connection report
    report = analyzer.generate_full_connection_report()

    # Save report
    report_file = analyzer.save_report(report)
    print(f"\\n📄 Full connection report saved to: {report_file}")

    # Print executive summary
    analyzer.print_executive_summary(report)

    print("\\n✅ Full core connection analysis complete!")
    print(f"📋 Ready for systematic integration of {report['total_candidates']} files")

    return 0


if __name__ == "__main__":
    exit(main())
