#!/usr/bin/env python3
"""
LUKHAS AI Branding Structure Analyzer
Analyzes current branding directory for overlaps, gaps, orphaned components
Provides elite organizational recommendations
"""
import time
import streamlit as st

import ast
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ComponentAnalysis:
    """Analysis of a branding component"""

    name: str
    path: str
    type: str  # class, function, module, directory
    dependencies: set[str]
    dependents: set[str]
    functionality: list[str]
    is_orphaned: bool
    overlaps_with: list[str]
    elite_score: float


class BrandingStructureAnalyzer:
    """
    Analyzes LUKHAS AI branding structure for elite organization
    Identifies overlaps, gaps, orphaned components, automation opportunities
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.components = {}
        self.dependencies = defaultdict(set)
        self.functionalities = defaultdict(list)

    def analyze_complete_structure(self) -> dict[str, Any]:
        """Complete analysis of branding structure"""
        print("🔍 Analyzing LUKHAS AI Branding Structure...")

        # Phase 1: Directory structure analysis
        directory_analysis = self._analyze_directory_structure()

        # Phase 2: Code analysis
        code_analysis = self._analyze_code_components()

        # Phase 3: Dependency mapping
        dependency_analysis = self._analyze_dependencies()

        # Phase 4: Overlap detection
        overlap_analysis = self._detect_overlaps()

        # Phase 5: Elite gaps identification
        gaps_analysis = self._identify_elite_gaps()

        # Phase 6: Automation opportunities
        automation_analysis = self._identify_automation_opportunities()

        return {
            "directory_structure": directory_analysis,
            "code_components": code_analysis,
            "dependencies": dependency_analysis,
            "overlaps": overlap_analysis,
            "elite_gaps": gaps_analysis,
            "automation_opportunities": automation_analysis,
            "recommendations": self._generate_elite_recommendations(),
        }

    def _analyze_directory_structure(self) -> dict[str, Any]:
        """Analyze directory structure and empty directories"""
        print("📁 Analyzing directory structure...")

        directories = {}
        empty_dirs = []

        for root, dirs, files in os.walk(self.base_path):
            rel_path = Path(root).relative_to(self.base_path)

            # Check if directory is empty or only has __init__.py
            meaningful_files = [f for f in files if f != "__init__.py" and not f.startswith(".")]

            if not meaningful_files and not dirs:
                empty_dirs.append(str(rel_path))
            else:
                directories[str(rel_path)] = {
                    "files": len(files),
                    "subdirs": len(dirs),
                    "python_files": len([f for f in files if f.endswith(".py")]),
                    "config_files": len([f for f in files if f.endswith((".yaml", ".yml", ".json"))]),
                    "doc_files": len([f for f in files if f.endswith(".md")]),
                }

        return {
            "total_directories": len(directories),
            "empty_directories": empty_dirs,
            "directory_details": directories,
        }

    def _analyze_code_components(self) -> dict[str, Any]:
        """Analyze Python code components"""
        print("🐍 Analyzing code components...")

        classes = {}
        functions = {}
        modules = {}

        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to extract classes and functions
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes[node.name] = {
                            "file": str(py_file.relative_to(self.base_path)),
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                            "docstring": ast.get_docstring(node) or "",
                        }
                    elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                        # Only top-level functions
                        if isinstance(getattr(node, "parent", None), ast.Module):
                            functions[node.name] = {
                                "file": str(py_file.relative_to(self.base_path)),
                                "docstring": ast.get_docstring(node) or "",
                            }

                # Module-level analysis
                modules[str(py_file.relative_to(self.base_path))] = {
                    "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    "lines": len(content.splitlines()),
                    "imports": len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
                }

            except Exception as e:
                print(f"⚠️  Could not parse {py_file}: {e}")

        return {"classes": classes, "functions": functions, "modules": modules}

    def _analyze_dependencies(self) -> dict[str, Any]:
        """Analyze component dependencies"""
        print("🔗 Analyzing dependencies...")

        dependencies = defaultdict(set)

        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Find imports
                tree = ast.parse(content)
                file_key = str(py_file.relative_to(self.base_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies[file_key].add(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        dependencies[file_key].add(node.module)

            except Exception:
                continue

        return dict(dependencies)

    def _detect_overlaps(self) -> dict[str, Any]:
        """Detect overlapping functionality"""
        print("🔍 Detecting overlaps...")

        overlaps = []

        # Common functionality patterns to check for overlaps
        patterns = {
            "voice_coherence": ["voice", "coherence", "tone"],
            "content_generation": ["content", "generate", "create"],
            "validation": ["validate", "check", "verify"],
            "orchestration": ["orchestrate", "coordinate", "manage"],
            "database": ["db", "database", "storage"],
            "trinity": ["trinity", "framework", "⚛️", "🧠", "🛡️"],
        }

        # Find files that might have overlapping functionality
        for category, keywords in patterns.items():
            matching_files = []

            for py_file in self.base_path.rglob("*.py"):
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in keywords):
                    matching_files.append(str(py_file.relative_to(self.base_path)))

            if len(matching_files) > 1:
                overlaps.append(
                    {
                        "category": category,
                        "files": matching_files,
                        "overlap_score": len(matching_files),
                    }
                )

        return overlaps

    def _identify_elite_gaps(self) -> list[str]:
        """Identify missing elite capabilities"""
        print("🎯 Identifying elite gaps...")

        elite_requirements = [
            "automated_self_healing",
            "real_time_monitoring",
            "adaptive_brand_evolution",
            "social_media_automation",
            "competitive_intelligence",
            "brand_sentiment_tracking",
            "automated_content_optimization",
            "cross_platform_orchestration",
            "predictive_brand_analytics",
            "autonomous_crisis_management",
            "multi_language_brand_adaptation",
            "brand_performance_optimization",
            "automated_compliance_checking",
            "dynamic_voice_adjustment",
            "intelligent_content_routing",
        ]

        # Check which capabilities are missing
        gaps = []

        for capability in elite_requirements:
            found = False
            for py_file in self.base_path.rglob("*.py"):
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    if capability.replace("_", " ") in content or capability in content:
                        found = True
                        break

            if not found:
                gaps.append(capability)

        return gaps

    def _identify_automation_opportunities(self) -> list[dict[str, Any]]:
        """Identify automation opportunities"""
        print("🤖 Identifying automation opportunities...")

        opportunities = [
            {
                "name": "Automated Voice Coherence Optimization",
                "description": "Self-optimizing voice coherence based on performance metrics",
                "impact": "high",
                "complexity": "medium",
            },
            {
                "name": "Dynamic Brand Adaptation",
                "description": "Automatically adapt brand messaging based on audience response",
                "impact": "high",
                "complexity": "high",
            },
            {
                "name": "Social Media Auto-Orchestration",
                "description": "Automated social media content generation and posting",
                "impact": "medium",
                "complexity": "medium",
            },
            {
                "name": "Self-Healing Brand Consistency",
                "description": "Automatically detect and fix brand inconsistencies",
                "impact": "high",
                "complexity": "low",
            },
            {
                "name": "Predictive Content Performance",
                "description": "Predict content performance before publishing",
                "impact": "medium",
                "complexity": "high",
            },
        ]

        return opportunities

    def _generate_elite_recommendations(self) -> dict[str, Any]:
        """Generate elite organizational recommendations"""
        print("💎 Generating elite recommendations...")

        return {
            "structural_improvements": [
                "Consolidate overlapping voice coherence tools",
                "Create unified automation layer",
                "Implement self-healing architecture",
                "Add predictive analytics module",
            ],
            "naming_conventions": [
                'Remove "unified" from all file names',
                "Use action-based naming (optimizer, orchestrator, guardian)",
                "Consistent elite terminology across modules",
            ],
            "architecture_changes": [
                "Separate core engines from utilities",
                "Create automation layer above all components",
                "Implement event-driven architecture",
                "Add monitoring and analytics layer",
            ],
            "elite_additions": [
                "Social media automation engine",
                "Predictive brand analytics",
                "Automated crisis management",
                "Cross-platform orchestration",
            ],
        }

    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        analysis = self.analyze_complete_structure()

        report = f"""# 🔍 LUKHAS AI Branding Structure Analysis

## 📊 Current State Overview

**Total Directories**: {analysis["directory_structure"]["total_directories"]}
**Empty Directories**: {len(analysis["directory_structure"]["empty_directories"])}
**Python Classes**: {len(analysis["code_components"]["classes"])}
**Python Functions**: {len(analysis["code_components"]["functions"])}
**Python Modules**: {len(analysis["code_components"]["modules"])}

## 🗂️ Empty Directories (Candidates for Removal)
{chr(10).join(f"- {d}" for d in analysis["directory_structure"]["empty_directories"])}

## 🔄 Overlapping Functionality
"""

        for overlap in analysis["overlaps"]:
            report += f"""
### {overlap["category"].title()}
**Files with overlap**: {overlap["overlap_score"]}
{chr(10).join(f"- {f}" for f in overlap["files"])}
"""

        report += f"""
## ❌ Elite Gaps (Missing Capabilities)
{chr(10).join(f"- {gap.replace('_', ' ').title()}" for gap in analysis["elite_gaps"])}

## 🤖 Automation Opportunities
"""

        for opp in analysis["automation_opportunities"]:
            report += f"""
### {opp["name"]}
**Impact**: {opp["impact"]} | **Complexity**: {opp["complexity"]}
{opp["description"]}
"""

        report += f"""
## 💎 Elite Recommendations

### Structural Improvements
{chr(10).join(f"- {rec}" for rec in analysis["recommendations"]["structural_improvements"])}

### Naming Conventions
{chr(10).join(f"- {rec}" for rec in analysis["recommendations"]["naming_conventions"])}

### Architecture Changes
{chr(10).join(f"- {rec}" for rec in analysis["recommendations"]["architecture_changes"])}

### Elite Additions
{chr(10).join(f"- {rec}" for rec in analysis["recommendations"]["elite_additions"])}

---

*Analysis powered by LUKHAS AI Elite Organizational Intelligence*
"""

        return report


if __name__ == "__main__":
    analyzer = BrandingStructureAnalyzer()
    report = analyzer.generate_analysis_report()
    print(report)

    # Save report
    with open(analyzer.base_path / "BRANDING_STRUCTURE_ANALYSIS.md", "w") as f:
        f.write(report)

    print("\n📊 Analysis complete! Report saved to BRANDING_STRUCTURE_ANALYSIS.md")
