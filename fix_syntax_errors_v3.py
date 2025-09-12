#!/usr/bin/env python3
"""
Advanced surgical syntax error fixer for LUKHAS codebase.
Handles the most common f-string and syntax issues found in the codebase.
"""

import re
import subprocess
import json


def fix_fstring_braces(content):
    """Fix f-string brace issues."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if 'f"' in line or "f'" in line:
            # Pattern 1: Fix single '}' not allowed - usually extra closing brace
            # Replace }} with } in f-strings
            if 'f"' in line and "}}" in line:
                line = re.sub(r'(f"[^"]*)}}"', r'\1}"', line)
            if "f'" in line and "}}" in line:
                line = re.sub(r"(f'[^']*)}}'", r"\1}'", line)

            # Pattern 2: Fix missing closing braces
            # Count braces in f-strings
            if 'f"' in line:
                matches = re.findall(r'f"([^"]*)"', line)
                for match in matches:
                    open_count = match.count("{")
                    close_count = match.count("}")
                    if open_count > close_count:
                        # Add missing closing braces
                        missing = open_count - close_count
                        old_pattern = f'f"{match}"'
                        new_pattern = f'f"{match}{"}" * missing}"'
                        line = line.replace(old_pattern, new_pattern)

            # Pattern 3: Fix unterminated strings
            # Look for unclosed quotes in f-strings
            if line.count('f"') % 2 == 1 and not line.rstrip().endswith('"'):
                line = line.rstrip() + '"'
            if line.count("f'") % 2 == 1 and not line.rstrip().endswith("'"):
                line = line.rstrip() + "'"

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_parentheses_issues(content):
    """Fix missing parentheses in function calls."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix missing parentheses in common patterns

        # Pattern 1: .method_name( with missing )
        if "(" in line and line.count("(") > line.count(")"):
            # Simple heuristic: add missing ) at end of line
            missing = line.count("(") - line.count(")")
            line = line.rstrip() + ")" * missing

        # Pattern 2: MongoDB-style queries
        if ".find(" in line and not line.rstrip().endswith(")"):
            if "sort=" in line or "limit=" in line:
                line = line.rstrip() + ")"

        # Pattern 3: Dictionary definitions with missing braces
        if "{" in line and line.count("{") > line.count("}"):
            missing = line.count("{") - line.count("}")
            if not line.rstrip().endswith("}"):
                line = line.rstrip() + "}" * missing

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_import_issues(content):
    """Fix import statement issues."""
    lines = content.split("\n")
    fixed_lines = []

    # Track if we already added timezone import
    has_timezone = False

    for i, line in enumerate(lines):
        # Check for existing timezone import
        if "from datetime import" in line and "timezone" in line:
            has_timezone = True

        # Fix misplaced timezone imports
        if line.strip() == "from datetime import timezone" and i > 0:
            prev_line = lines[i - 1] if i > 0 else ""
            if "(" in prev_line and ")" not in prev_line:
                # Skip this misplaced import
                continue

        # Add timezone import if needed and we see datetime usage
        if not has_timezone and "datetime.now()" in line:
            # Add timezone import before first import
            if "import" in line and "from datetime import timezone" not in fixed_lines:
                fixed_lines.append("from datetime import timezone")
                has_timezone = True

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file_advanced(filepath):
    """Advanced file fixing with multiple patterns."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Apply fixes in order
        content = fix_import_issues(content)
        content = fix_fstring_braces(content)
        content = fix_parentheses_issues(content)

        # Additional pattern fixes

        # Fix common TODO issues
        content = re.sub(r"^TODO\[.*?\]:", "# TODO:", content, flags=re.MULTILINE)

        # Fix simple syntax issues
        content = re.sub(r'(\w+)\s*=\s*f"([^"]*)"([^"]*$)', r'\1 = f"\2"\3', content, flags=re.MULTILINE)

        if content != original:
            # Validate the fix
            try:
                compile(content, filepath, "exec")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True, "Fixed successfully"
            except SyntaxError as e:
                return False, f"Still has syntax error: {e}"
            except Exception as e:
                return False, f"Compile error: {e}"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error processing: {e}"


def get_files_with_syntax_errors():
    """Get files with syntax errors, prioritized."""
    result = subprocess.run(
        [".venv/bin/ruff", "check", "--select", "E999", "--output-format=json"], capture_output=True, text=True
    )

    files = []
    try:
        errors = json.loads(result.stdout)
        file_counts = {}

        for error in errors:
            if "filename" in error:
                filename = error["filename"]
                file_counts[filename] = file_counts.get(filename, 0) + 1

        # Sort by error count (descending)
        files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        files = [f[0] for f in files]  # Extract just filenames

    except Exception as e:
        print(f"Error parsing ruff output: {e}")

    return files


def main():
    print("🔧 Advanced Surgical Syntax Error Fixer v3")
    print("=" * 50)

    # Get prioritized list of files with syntax errors
    print("Scanning for syntax errors...")
    error_files = get_files_with_syntax_errors()
    print(f"Found {len(error_files)} files with syntax errors")

    if len(error_files) == 0:
        print("No syntax errors found!")
        return

    # Show top files by error count
    print("\nTop files by error count:")
    result = subprocess.run(
        [".venv/bin/ruff", "check", "--select", "E999", "--output-format=concise"], capture_output=True, text=True
    )
    file_counts = {}
    for line in result.stdout.split("\n")[:30]:
        if ":" in line:
            filename = line.split(":")[0]
            file_counts[filename] = file_counts.get(filename, 0) + 1

    for filename, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:2d} errors: {filename}")

    print(f"\nProcessing up to 100 files...")

    fixed_count = 0
    failed_count = 0

    for i, filepath in enumerate(error_files[:100], 1):
        success, message = fix_file_advanced(filepath)

        if success:
            fixed_count += 1
            print(f"✅ [{i:3d}/{min(100, len(error_files))}] Fixed: {filepath}")
        else:
            failed_count += 1
            if "No changes needed" not in message:
                print(f"❌ [{i:3d}/{min(100, len(error_files))}] Failed: {filepath} - {message}")

    print(f"\n✨ Results:")
    print(f"   Fixed: {fixed_count} files")
    print(f"   Failed: {failed_count} files")

    # Check final status
    print(f"\n📊 Checking current error status...")
    result = subprocess.run([".venv/bin/ruff", "check", "--statistics"], capture_output=True, text=True)
    for line in result.stdout.split("\n")[:8]:
        if line.strip():
            print(f"   {line}")


if __name__ == "__main__":
    main()
