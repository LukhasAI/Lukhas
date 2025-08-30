"""
Core Introspection Module - Phase 3C

# ΛLOCKED: Core introspection logic – symbolic-aware module scanner
# LUKHAS_TAG: introspection_core
# PURPOSE: Analyze modules for symbolic tags, drift scores, and emotional deltas

This module provides introspective analysis capabilities for the AGI system,
enabling symbolic state reporting and module health monitoring.
"""

import ast
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModuleIntrospector:
    """
    Symbolic-aware module introspection system

    # LUKHAS_TAG: introspection_engine
    # ΔdriftScore: drift_monitoring_enabled
    """

    def __init__(self, base_path: str = None):
        """Initialize introspector with base repository path"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.symbolic_tags = {
            "LUKHAS_TAG": r"#\s*LUKHAS_TAG:\s*([^\n]+)",
            "ΛLOCKED": r"#\s*ΛLOCKED:\s*([^\n]+)",
            "ΔdriftScore": r"#\s*ΔdriftScore:\s*([^\n]+)",
            "EMO_DELTA": r"#\s*EMO_DELTA:\s*([^\n]+)",
            "affect_trace": r"#\s*affect_trace:\s*([^\n]+)",
            "mood_infusion": r"#\s*mood_infusion:\s*([^\n]+)",
            "INTROSPECTION_POINT": r"#\s*INTROSPECTION_POINT:\s*([^\n]+)",
            "RECURSION_CONTROL": r"#\s*RECURSION_CONTROL:\s*([^\n]+)",
        }

    def analyze_module(self, module_path: str) -> dict[str, Any]:
        """
        Analyze a Python module for symbolic tags and introspective metadata

        Args:
            module_path: Path to the Python module to analyze

        Returns:
            Dictionary containing module analysis results
        """
        analysis = {
            "module_path": module_path,
            "timestamp": datetime.now().isoformat(),
            "symbolic_tags": {},
            "functions": [],
            "classes": [],
            "imports": [],
            "symbolic_state": "unknown",
            "drift_indicators": [],
            "emotional_deltas": [],
            "locked_status": False,
            "introspection_points": [],
            "recursion_controls": [],
        }

        try:
            # Read module content
            with open(module_path, encoding="utf-8") as f:
                content = f.read()

            # Extract symbolic tags
            for tag_name, pattern in self.symbolic_tags.items():
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    analysis["symbolic_tags"][tag_name] = matches

            # Process specific tag types
            self._process_special_tags(analysis, content)

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, analysis)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {module_path}: {e}")
                analysis["syntax_error"] = str(e)

        except Exception as e:
            logger.error(f"Error analyzing {module_path}: {e}")
            analysis["error"] = str(e)

        return analysis

    def _process_special_tags(self, analysis: dict, content: str):
        """Process special symbolic tags for introspection"""

        # Check for locked status
        if "ΛLOCKED" in analysis["symbolic_tags"]:
            analysis["locked_status"] = True

        # Extract drift indicators
        if "ΔdriftScore" in analysis["symbolic_tags"]:
            analysis["drift_indicators"] = analysis["symbolic_tags"]["ΔdriftScore"]

        # Extract emotional deltas
        for emo_tag in ["EMO_DELTA", "affect_trace", "mood_infusion"]:
            if emo_tag in analysis["symbolic_tags"]:
                analysis["emotional_deltas"].extend(analysis["symbolic_tags"][emo_tag])

        # Extract introspection points
        if "INTROSPECTION_POINT" in analysis["symbolic_tags"]:
            analysis["introspection_points"] = analysis["symbolic_tags"]["INTROSPECTION_POINT"]

        # Extract recursion controls
        if "RECURSION_CONTROL" in analysis["symbolic_tags"]:
            analysis["recursion_controls"] = analysis["symbolic_tags"]["RECURSION_CONTROL"]

    def _analyze_ast(self, tree: ast.AST, analysis: dict):
        """Analyze AST structure for functions, classes, and imports"""

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            self._get_decorator_name(dec) for dec in node.decorator_list
                        ],
                    }
                )
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [self._get_base_name(base) for base in node.bases],
                        "decorators": [
                            self._get_decorator_name(dec) for dec in node.decorator_list
                        ],
                    }
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append(
                        {
                            "type": "import",
                            "name": alias.name,
                            "asname": alias.asname,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    analysis["imports"].append(
                        {
                            "type": "from_import",
                            "module": node.module,
                            "name": alias.name,
                            "asname": alias.asname,
                        }
                    )

    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return str(decorator)

    def _get_base_name(self, base) -> str:
        """Extract base class name from AST node"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        return str(base)

    def report_symbolic_state(self, module_summary: dict) -> str:
        """
        Generate a symbolic state report from module analysis

        Args:
            module_summary: Dictionary from analyze_module()

        Returns:
            Formatted string report of symbolic state
        """

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("SYMBOLIC STATE REPORT")
        report_lines.append(f"Module: {module_summary['module_path']}")
        report_lines.append(f"Timestamp: {module_summary['timestamp']}")
        report_lines.append("=" * 60)

        # Locked status
        if module_summary["locked_status"]:
            report_lines.append("🔒 STATUS: LOCKED MODULE")
            if "ΛLOCKED" in module_summary["symbolic_tags"]:
                report_lines.append(f"   Reason: {module_summary['symbolic_tags']['ΛLOCKED'][0]}")
        else:
            report_lines.append("🔓 STATUS: UNLOCKED MODULE")

        # Symbolic tags summary
        if module_summary["symbolic_tags"]:
            report_lines.append("\n📋 SYMBOLIC TAGS:")
            for tag_name, values in module_summary["symbolic_tags"].items():
                report_lines.append(f"   {tag_name}: {values}")

        # Drift indicators
        if module_summary["drift_indicators"]:
            report_lines.append("\n📊 DRIFT INDICATORS:")
            for indicator in module_summary["drift_indicators"]:
                report_lines.append(f"   • {indicator}")

        # Emotional deltas
        if module_summary["emotional_deltas"]:
            report_lines.append("\n💭 EMOTIONAL DELTAS:")
            for delta in module_summary["emotional_deltas"]:
                report_lines.append(f"   • {delta}")

        # Introspection points
        if module_summary["introspection_points"]:
            report_lines.append("\n🔍 INTROSPECTION POINTS:")
            for point in module_summary["introspection_points"]:
                report_lines.append(f"   • {point}")

        # Structure summary
        report_lines.append("\n🏗️ STRUCTURE:")
        report_lines.append(f"   Functions: {len(module_summary['functions'])}")
        report_lines.append(f"   Classes: {len(module_summary['classes'])}")
        report_lines.append(f"   Imports: {len(module_summary['imports'])}")

        # Function details
        if module_summary["functions"]:
            report_lines.append("\n📦 FUNCTIONS:")
            for func in module_summary["functions"][:5]:  # Show first 5
                report_lines.append(f"   • {func['name']}() [line {func['line']}]")
            if len(module_summary["functions"]) > 5:
                report_lines.append(f"   ... and {len(module_summary['functions']) - 5} more")

        # Class details
        if module_summary["classes"]:
            report_lines.append("\n🏛️ CLASSES:")
            for cls in module_summary["classes"][:5]:  # Show first 5
                report_lines.append(f"   • {cls['name']} [line {cls['line']}]")
            if len(module_summary["classes"]) > 5:
                report_lines.append(f"   ... and {len(module_summary['classes']) - 5} more")

        # Error reporting
        if "error" in module_summary:
            report_lines.append(f"\n❌ ERROR: {module_summary['error']}")
        elif "syntax_error" in module_summary:
            report_lines.append(f"\n⚠️ SYNTAX ERROR: {module_summary['syntax_error']}")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)


# Convenience functions for direct use


def analyze_module(module_path: str) -> dict[str, Any]:
    """Analyze a single module - convenience function"""
    introspector = ModuleIntrospector()
    return introspector.analyze_module(module_path)


def report_symbolic_state(module_summary: dict) -> str:
    """Generate symbolic state report - convenience function"""
    introspector = ModuleIntrospector()
    return introspector.report_symbolic_state(module_summary)


# CLI scaffold for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Module Introspection Tool")
    parser.add_argument("module_path", help="Path to Python module to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Analyze module
    analysis = analyze_module(args.module_path)

    if args.json:
        logger.info(json.dumps(analysis, indent=2))
    else:
        logger.info(report_symbolic_state(analysis))
