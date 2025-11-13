#!/usr/bin/env python3
"""
E402 Import Organization Analysis & Strategy
============================================

Analyzes E402 violations to categorize them by complexity and develop
a targeted fixing strategy for LUKHAS codebase.
"""

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

def get_e402_violations() -> List[Tuple[str, int]]:
    """Get all E402 violations with file paths and line numbers."""
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", "--select", "E402", "--no-fix", "."],
            capture_output=True, text=True, cwd="."
        )

        violations = []
        lines = result.stdout.split('\n')

        for line in lines:
            if '-->' in line:
                # Extract file and line number
                match = re.search(r'-->\s+([^:]+):(\d+):', line)
                if match:
                    file_path, line_num = match.groups()
                    violations.append((file_path.strip(), int(line_num)))

        return violations

    except Exception as e:
        print(f"Error getting E402 violations: {e}")
        return []

def analyze_file_patterns(violations: List[Tuple[str, int]]) -> Dict[str, List[int]]:
    """Group violations by file."""
    file_violations = defaultdict(list)

    for file_path, line_num in violations:
        file_violations[file_path].append(line_num)

    # Sort line numbers for each file
    for file_path in file_violations:
        file_violations[file_path].sort()

    return dict(file_violations)

def categorize_files(file_violations: Dict[str, List[int]]) -> Dict[str, List[str]]:
    """Categorize files by potential complexity for fixing."""
    categories = {
        "simple": [],      # Likely just docstring/comment issues
        "moderate": [],    # Multiple imports, may need careful reordering
        "complex": [],     # Many violations, likely conditional/dynamic imports
        "test_files": [],  # Test files which may have special import patterns
    }

    for file_path, line_nums in file_violations.items():
        violation_count = len(line_nums)

        # Categorize by file type and violation count
        if "test_" in file_path or "/tests/" in file_path:
            categories["test_files"].append(file_path)
        elif violation_count <= 3:
            categories["simple"].append(file_path)
        elif violation_count <= 10:
            categories["moderate"].append(file_path)
        else:
            categories["complex"].append(file_path)

    return categories

def analyze_import_context(file_path: str, line_nums: List[int]) -> Dict[str, any]:
    """Analyze why imports are not at top of file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}

        lines = path.read_text().splitlines()
        analysis = {
            "docstring_lines": 0,
            "comment_lines": 0,
            "code_before_imports": False,
            "conditional_imports": False,
            "sys_path_modifications": False,
            "first_violation_context": "",
        }

        # Check lines before first violation
        if line_nums:
            first_violation = line_nums[0] - 1  # Convert to 0-based

            for i in range(min(first_violation, len(lines))):
                line = lines[i].strip()

                if line.startswith('"""') or line.startswith("'''"):
                    analysis["docstring_lines"] += 1
                elif line.startswith("#"):
                    analysis["comment_lines"] += 1
                elif line and not line.startswith(("import", "from")):
                    analysis["code_before_imports"] = True

                # Check for sys.path modifications
                if "sys.path" in line:
                    analysis["sys_path_modifications"] = True

            # Get context around first violation
            start = max(0, first_violation - 2)
            end = min(len(lines), first_violation + 3)
            analysis["first_violation_context"] = "\n".join(lines[start:end])

        # Check for conditional imports in violation lines
        for line_num in line_nums:
            if line_num <= len(lines):
                line = lines[line_num - 1]
                if any(keyword in line for keyword in ["if ", "try:", "except", "def ", "class "]):
                    analysis["conditional_imports"] = True
                    break

        return analysis

    except Exception as e:
        return {"error": str(e)}

def generate_fix_strategy(categories: Dict[str, List[str]], file_violations: Dict[str, List[int]]) -> None:
    """Generate fixing strategy based on analysis."""

    print("🔍 E402 Import Organization Analysis")
    print("=" * 50)

    total_files = sum(len(files) for files in categories.values())
    total_violations = sum(len(violations) for violations in file_violations.values())

    print(f"📊 Total: {total_violations} violations across {total_files} files\n")

    # Category breakdown
    for category, files in categories.items():
        if files:
            print(f"📁 {category.upper()}: {len(files)} files")
            for file_path in files[:5]:  # Show first 5 files
                violation_count = len(file_violations[file_path])
                print(f"   • {file_path} ({violation_count} violations)")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
            print()

    # Detailed analysis of a few sample files
    print("🔬 Sample File Analysis:")
    print("-" * 30)

    for category in ["simple", "moderate"]:
        if categories[category]:
            sample_file = categories[category][0]
            violations = file_violations[sample_file]
            analysis = analyze_import_context(sample_file, violations)

            print(f"\n📄 {sample_file} ({category}):")
            print(f"   Violations: {len(violations)} at lines {violations}")
            print(f"   Docstring lines: {analysis.get('docstring_lines', 0)}")
            print(f"   Comment lines: {analysis.get('comment_lines', 0)}")
            print(f"   Code before imports: {analysis.get('code_before_imports', False)}")
            print(f"   Conditional imports: {analysis.get('conditional_imports', False)}")
            print(f"   Sys.path modifications: {analysis.get('sys_path_modifications', False)}")

            if analysis.get('first_violation_context'):
                print(f"   Context around first violation:")
                for line in analysis['first_violation_context'].split('\n'):
                    print(f"      {line}")

    print("\n🎯 Recommended Fixing Strategy:")
    print("-" * 35)

    print("1. PHASE 1 (SIMPLE): Fix files with docstring/comment issues")
    print(f"   Target: {len(categories['simple'])} files")
    print("   Approach: Move imports after docstring/comments to top")

    print("\n2. PHASE 2 (MODERATE): Fix multi-import reordering")
    print(f"   Target: {len(categories['moderate'])} files") 
    print("   Approach: Careful import reordering, validate functionality")

    print("\n3. PHASE 3 (COMPLEX): Handle conditional/dynamic imports")
    print(f"   Target: {len(categories['complex'])} files")
    print("   Approach: Case-by-case analysis, may need restructuring")

    print("\n4. PHASE 4 (TESTS): Fix test file import patterns")
    print(f"   Target: {len(categories['test_files'])} files")
    print("   Approach: Respect test setup patterns, move when safe")

if __name__ == "__main__":
    print("🚀 Starting E402 Analysis...")

    violations = get_e402_violations()
    if not violations:
        print("✅ No E402 violations found!")
        sys.exit(0)

    file_violations = analyze_file_patterns(violations)
    categories = categorize_files(file_violations)

    generate_fix_strategy(categories, file_violations)

    print(f"\n📝 Analysis complete! Ready to start Phase 1 with {len(categories['simple'])} simple files.")