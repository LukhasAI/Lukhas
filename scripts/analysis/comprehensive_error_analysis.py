#!/usr/bin/env python3
"""
🔬 COMPREHENSIVE ERROR ANALYSIS
Deep analysis of all syntax errors across the entire codebase
"""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class ComprehensiveErrorAnalyzer:
    """Comprehensive analysis of all syntax errors"""

    def __init__(self):
        self.total_files = 0
        self.syntax_errors = 0
        self.valid_files = 0
        self.error_patterns = defaultdict(list)
        self.blocking_chains = defaultdict(list)

    def analyze_single_file(self, file_path: str) -> dict:
        """Analyze a single file for syntax errors"""
        result = {
            "file": file_path,
            "valid": False,
            "error": None,
            "error_line": None,
            "error_type": None,
            "is_f_string": False,
            "blocking_level": 0
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            ast.parse(content)
            result["valid"] = True
            self.valid_files += 1

        except SyntaxError as e:
            result["error"] = str(e).replace(str(file_path), "FILE")[:100]
            result["error_line"] = e.lineno
            result["is_f_string"] = "f-string" in str(e)

            # Classify error types
            error_str = str(e).lower()
            if "f-string" in error_str:
                if "closing parenthesis" in error_str:
                    result["error_type"] = "f-string-parenthesis"
                elif "unmatched" in error_str:
                    result["error_type"] = "f-string-unmatched"
                else:
                    result["error_type"] = "f-string-other"
            elif "invalid syntax" in error_str:
                result["error_type"] = "invalid-syntax"
            else:
                result["error_type"] = "other-syntax"

            # Determine blocking level
            if file_path.startswith("lukhas/"):
                result["blocking_level"] = 3  # High blocking
            elif file_path.endswith("__init__.py"):
                result["blocking_level"] = 2  # Medium blocking
            elif any(x in file_path for x in ["core", "governance", "memory", "consciousness"]):
                result["blocking_level"] = 2
            else:
                result["blocking_level"] = 1  # Low blocking

            self.syntax_errors += 1
            self.error_patterns[result["error_type"]].append(file_path)

        except Exception as e:
            result["error"] = f"Read error: {str(e}[:50]}"
            result["error_type"] = "read-error"

        return result

    def get_all_python_files(self) -> list[str]:
        """Get all Python files in the codebase"""

        # Priority patterns - files that matter most
        priority_patterns = [
            "lukhas/**/*.py",
            "*.py",
            "candidate/**/*.py",
            "governance/**/*.py",
            "core/**/*.py",
            "orchestration/**/*.py",
            "bridge/**/*.py",
        ]

        all_files = set()
        for pattern in priority_patterns:
            matches = list(Path(".").glob(pattern))
            all_files.update([str(f) for f in matches if f.suffix == ".py"])

        return sorted(list(all_files))

    def run_comprehensive_analysis(self) -> dict:
        """Run comprehensive analysis of all Python files"""
        print("🔬 COMPREHENSIVE ERROR ANALYSIS")
        print("=" * 60)
        print("Deep analysis of all syntax errors across the entire codebase")
        print()

        python_files = self.get_all_python_files()
        self.total_files = len(python_files)

        print(f"Analyzing {self.total_files} Python files...")
        print()

        results = []
        critical_blockers = []

        for i, file_path in enumerate(python_files):
            if os.path.exists(file_path):
                result = self.analyze_single_file(file_path)
                results.append(result)

                # Track critical blockers
                if not result["valid"] and result["blocking_level"] >= 2:
                    critical_blockers.append(result)

                # Progress indicator
                if (i + 1) % 100 == 0:
                    print(f"Progress: {i + 1}/{self.total_files} files analyzed")

        # Analysis summary
        analysis = {
            "total_files": self.total_files,
            "valid_files": self.valid_files,
            "syntax_errors": self.syntax_errors,
            "error_rate": (self.syntax_errors / self.total_files) * 100 if self.total_files > 0 else 0,
            "success_rate": (self.valid_files / self.total_files) * 100 if self.total_files > 0 else 0,
            "error_patterns": dict(self.error_patterns),
            "critical_blockers": critical_blockers,
            "results": results
        }

        self.print_analysis_results(analysis)
        return analysis

    def print_analysis_results(self, analysis: dict):
        """Print comprehensive analysis results"""
        print()
        print("🔬 COMPREHENSIVE ANALYSIS RESULTS:")
        print("=" * 50)
        print(f"Total Python files: {analysis['total_files']}")
        print(f"Valid files: {analysis['valid_files']}")
        print(f"Files with syntax errors: {analysis['syntax_errors']}")
        print(f"Success rate: {analysis['success_rate']:.1f}%")
        print(f"Error rate: {analysis['error_rate']:.1f}%")

        print()
        print("🔍 ERROR TYPE BREAKDOWN:")
        print("-" * 30)
        for error_type, files in analysis["error_patterns"].items():
            print(f"  {error_type}: {len(files)} files")
            if len(files) <= 5:
                for file_path in files[:5]:
                    print(f"    • {file_path}")
            else:
                for file_path in files[:3]:
                    print(f"    • {file_path}")
                print(f"    • ... and {len(files} - 3} more")

        print()
        print("🚨 CRITICAL BLOCKERS (Blocking Level 2+):")
        print("-" * 40)
        critical_blockers = analysis["critical_blockers"]
        blocking_by_level = defaultdict(list)

        for blocker in critical_blockers:
            blocking_by_level[blocker["blocking_level"]].append(blocker)

        for level in sorted(blocking_by_level.keys(), reverse=True):
            blockers = blocking_by_level[level][:10]  # Show top 10 per level
            level_name = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}[level]
            print(f"  {level_name} Priority ({len(blocking_by_level[level])} total):")

            for blocker in blockers:
                error_short = blocker["error"][:50] + "..." if len(blocker["error"]) > 50 else blocker["error"]
                print(f"    • {blocker['file']} (line {blocker['error_line']}): {error_short}")

        print()
        print("💡 STRATEGIC RECOMMENDATIONS:")
        print("-" * 30)

        f_string_errors = sum(len(files) for error_type, files in analysis["error_patterns"].items()
                             if "f-string" in error_type)

        if f_string_errors > analysis["syntax_errors"] * 0.7:
            print("  • F-string errors dominate - focused f-string fixing strategy recommended")

        high_priority_blockers = len(blocking_by_level[3])
        if high_priority_blockers > 0:
            print(f"  • {high_priority_blockers} HIGH priority blockers in lukhas/ namespace")
            print("  • Focus on lukhas/ files first for maximum functional impact")

        if analysis["success_rate"] < 50:
            print("  • Low success rate - systematic approach needed")
            print("  • Consider file-by-file surgical fixes with validation")
        else:
            print(f"  • {analysis['success_rate']:.1f}% success rate - targeted fixes may be sufficient")


def main():
    """Run comprehensive error analysis"""
    analyzer = ComprehensiveErrorAnalyzer()
    analysis = analyzer.run_comprehensive_analysis()

    # Save results for future analysis
    with open("comprehensive_error_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print("\n📊 Detailed results saved to: comprehensive_error_analysis.json")


if __name__ == "__main__":
    main()
