#!/usr/bin/env python3
"""
🔍 LUKHAS Corruption Analysis Tool

Analyzes the codebase to identify:
1. Files with null bytes or encoding issues
2. Severely corrupted indentation
3. Malformed f-strings
4. Files that can be salvaged vs need reconstruction

This preserves the logic and organization while identifying fixable corruption.
"""

import ast
import json
import os
from pathlib import Path
from typing import Dict


class CorruptionAnalyzer:
    def __init__(self):
        self.results = {
            "null_byte_files": [],
            "encoding_issues": [],
            "severe_indentation": [],
            "malformed_fstrings": [],
            "syntax_errors": [],
            "salvageable": [],
            "total_files": 0,
            "corrupted_files": 0,
        }

    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single file for corruption issues"""
        analysis = {"file": str(filepath), "issues": [], "severity": "clean", "salvageable": True}

        try:
            # Check for null bytes first
            with open(filepath, "rb") as f:
                raw_content = f.read()

            if b"\x00" in raw_content:
                analysis["issues"].append("null_bytes")
                analysis["severity"] = "critical"
                analysis["salvageable"] = False
                return analysis

            # Try to read as text
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                analysis["issues"].append("encoding_error")
                analysis["severity"] = "high"
                analysis["salvageable"] = False
                return analysis

            # Check for severe indentation corruption
            lines = content.split("\n")
            corrupted_indent_count = 0
            for line in lines:
                # Check for lines with excessive whitespace (corruption signature)
                if (
                    len(line) > 0
                    and line.lstrip() != line
                    and "                                                   " in line
                ):
                    corrupted_indent_count += 1

            if corrupted_indent_count > 3:  # More than 3 corrupted lines = severe
                analysis["issues"].append("severe_indentation")
                analysis["severity"] = "high"

            # Check for malformed f-strings
            if 'f"' in content or "f'" in content:
                # Common corruption patterns
                if "{{" in content and "}}" in content:
                    # Check if these are properly escaped or corrupted
                    fstring_issues = content.count("{{") + content.count("}}")
                    if fstring_issues > 10:  # Threshold for likely corruption
                        analysis["issues"].append("malformed_fstrings")
                        analysis["severity"] = "medium"

            # Try to parse as AST
            try:
                ast.parse(content)
            except SyntaxError as e:
                analysis["issues"].append(f"syntax_error: {e.msg}")
                if analysis["severity"] == "clean":
                    analysis["severity"] = "medium"

            # Determine if salvageable
            critical_issues = [i for i in analysis["issues"] if "null_bytes" in i or "encoding_error" in i]
            if critical_issues:
                analysis["salvageable"] = False

        except Exception as e:
            analysis["issues"].append(f"analysis_error: {str(e)}")
            analysis["severity"] = "unknown"
            analysis["salvageable"] = False

        return analysis

    def scan_codebase(self, root_path: str = "."):
        """Scan the entire codebase for corruption"""
        print("🔍 Starting corruption analysis...")

        # Skip these directories
        skip_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            ".venv311",
            ".cleanenv",
            "node_modules",
            ".pytest_cache",
            "build",
            "dist",
            ".egg-info",
        }

        python_files = []
        for root, dirs, files in os.walk(root_path):
            # Remove skip directories from dirs list
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        self.results["total_files"] = len(python_files)
        print(f"📁 Found {len(python_files)} Python files to analyze...")

        corrupted_count = 0
        for i, filepath in enumerate(python_files):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(python_files)} files...")

            analysis = self.analyze_file(filepath)

            if analysis["issues"]:
                corrupted_count += 1

                # Categorize by severity
                if analysis["severity"] == "critical":
                    if "null_bytes" in analysis["issues"][0]:
                        self.results["null_byte_files"].append(analysis)
                    else:
                        self.results["encoding_issues"].append(analysis)
                elif "severe_indentation" in str(analysis["issues"]):
                    self.results["severe_indentation"].append(analysis)
                elif "malformed_fstrings" in str(analysis["issues"]):
                    self.results["malformed_fstrings"].append(analysis)
                else:
                    self.results["syntax_errors"].append(analysis)

                if analysis["salvageable"]:
                    self.results["salvageable"].append(analysis)

        self.results["corrupted_files"] = corrupted_count
        print("✅ Analysis complete!")

    def generate_report(self):
        """Generate a detailed corruption report"""
        report = f"""
# 🔍 LUKHAS Corruption Analysis Report

**Generated**: {os.popen('date').read().strip()}
**Baseline**: Current main branch state

## 📊 Summary

- **Total Python Files**: {self.results['total_files']:,}
- **Corrupted Files**: {self.results['corrupted_files']:,} ({self.results['corrupted_files']/self.results['total_files']*100:.1f}%)
- **Clean Files**: {self.results['total_files'] - self.results['corrupted_files']:,}

## 🚨 Critical Issues (Unsalvageable)

### Null Byte Files: {len(self.results['null_byte_files'])}
"""

        for item in self.results["null_byte_files"][:5]:  # Show first 5
            report += f"- `{item['file']}`\n"
        if len(self.results["null_byte_files"]) > 5:
            report += f"- ... and {len(self.results['null_byte_files']) - 5} more\n"

        report += f"""
### Encoding Issues: {len(self.results['encoding_issues'])}
"""
        for item in self.results["encoding_issues"][:5]:
            report += f"- `{item['file']}`\n"
        if len(self.results["encoding_issues"]) > 5:
            report += f"- ... and {len(self.results['encoding_issues']) - 5} more\n"

        report += f"""
## ⚠️ High Priority (Salvageable with Effort)

### Severe Indentation Corruption: {len(self.results['severe_indentation'])}
"""
        for item in self.results["severe_indentation"][:5]:
            report += f"- `{item['file']}`\n"
        if len(self.results["severe_indentation"]) > 5:
            report += f"- ... and {len(self.results['severe_indentation']) - 5} more\n"

        report += f"""
### Malformed F-Strings: {len(self.results['malformed_fstrings'])}
"""
        for item in self.results["malformed_fstrings"][:5]:
            report += f"- `{item['file']}`\n"
        if len(self.results["malformed_fstrings"]) > 5:
            report += f"- ... and {len(self.results['malformed_fstrings']) - 5} more\n"

        report += f"""
## 📝 Medium Priority (Standard Syntax Issues)

### Syntax Errors: {len(self.results['syntax_errors'])}
"""
        for item in self.results["syntax_errors"][:5]:
            report += f"- `{item['file']}`: {item['issues'][0] if item['issues'] else 'unknown'}\n"
        if len(self.results["syntax_errors"]) > 5:
            report += f"- ... and {len(self.results['syntax_errors']) - 5} more\n"

        report += f"""
## 🛠️ Recommended Strategy

### Phase 0: Critical Corruption Triage
1. **Quarantine unsalvageable files** ({len(self.results['null_byte_files']) + len(self.results['encoding_issues'])} files)
2. **Manual repair of salvageable files** ({len(self.results['salvageable'])} files)
3. **Preserve logic and organization** while fixing corruption

### Phase 1: Automated Fixes (Post-Corruption Fix)
- Only attempt automated fixes after corruption is resolved
- Use targeted ruff fixes on clean files
- Incremental validation approach

### Success Metrics
- 🎯 **Target**: <100 corrupted files (currently {self.results['corrupted_files']})
- 🎯 **Target**: All critical corruption eliminated
- 🎯 **Target**: Preserve all logic, state, and organization

---
*This analysis preserves your tagged commit logic while identifying fixable issues*
"""

        return report

    def save_detailed_results(self, filename="corruption_analysis.json"):
        """Save detailed results for further analysis"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Detailed results saved to: {filename}")


if __name__ == "__main__":
    analyzer = CorruptionAnalyzer()
    analyzer.scan_codebase()

    # Generate and save report
    report = analyzer.generate_report()
    with open("CORRUPTION_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)

    analyzer.save_detailed_results()

    print("""
🎯 **Corruption Analysis Complete**

📄 **Report**: CORRUPTION_ANALYSIS_REPORT.md
📊 **Data**: corruption_analysis.json

**Next Steps**:
1. Review corruption patterns
2. Plan surgical fixes for salvageable files  
3. Quarantine unsalvageable files
4. Preserve logic/state/organization throughout
""")
