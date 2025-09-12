#!/usr/bin/env python3
"""
Enhanced surgical syntax error fixer for LUKHAS codebase.
Handles more complex patterns and TODO marker issues.
"""

import re
import subprocess
import json


def fix_fstring_errors(content):
    """Fix common f-string errors."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix unclosed f-string braces
        if 'f"' in line or "f'" in line:
            # Count braces
            open_braces = line.count("{")
            close_braces = line.count("}")

            # Add missing closing braces at the end of f-strings
            if open_braces > close_braces:
                # Find f-string boundaries
                if 'f"' in line:
                    # Handle f"..." strings
                    pattern = r'f"([^"]*)"'

                    def fix_fstring(match):
                        inner = match.group(1)
                        o = inner.count("{")
                        c = inner.count("}")
                        if o > c:
                            inner += "}" * (o - c)
                        return f'f"{inner}"'

                    line = re.sub(pattern, fix_fstring, line)

                if "f'" in line:
                    # Handle f'...' strings
                    pattern = r"f'([^']*)'"

                    def fix_fstring(match):
                        inner = match.group(1)
                        o = inner.count("{")
                        c = inner.count("}")
                        if o > c:
                            inner += "}" * (o - c)
                        return f"f'{inner}'"

                    line = re.sub(pattern, fix_fstring, line)

        # Fix misplaced closing parentheses in f-strings
        line = re.sub(r"\{([^}]*)\(([^)]*)\}", r"{\1(\2)}", line)

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_todo_markers(content):
    """Fix TODO markers that break syntax."""
    # Remove TODO markers at the beginning of files
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Skip TODO markers that aren't valid Python
        if line.strip().startswith("TODO[") and ":" in line and i < 5:
            # Convert to a comment
            fixed_lines.append("# " + line)
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_import_errors(content):
    """Fix import statement errors."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fix timezone import inside parenthesized imports
        if "from datetime import timezone" in line:
            # Check if this is inside a parenthesized import
            if i > 0:
                prev_line = lines[i - 1]
                if "(" in prev_line and ")" not in prev_line:
                    # This timezone import is misplaced, skip it
                    # and add it before the problematic import
                    import_idx = max(0, i - 10)  # Look back up to 10 lines
                    for j in range(i - 1, import_idx, -1):
                        if "import" in lines[j] and "(" not in lines[j]:
                            # Found a good place to insert
                            fixed_lines.insert(len(fixed_lines) - (i - j), "from datetime import timezone")
                            break
                    i += 1
                    continue

        # Fix multi-line imports with misplaced items
        if "import (" in line:
            import_lines = [line]
            j = i + 1
            while j < len(lines) and ")" not in lines[j - 1]:
                next_line = lines[j]
                # Skip misplaced import statements
                if "from " in next_line and "import" in next_line:
                    j += 1
                    continue
                import_lines.append(next_line)
                j += 1

            # Reconstruct the import
            fixed_import = "\n".join(import_lines)
            fixed_lines.append(fixed_import)
            i = j
            continue

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Apply fixes in order
        content = fix_todo_markers(content)
        content = fix_import_errors(content)
        content = fix_fstring_errors(content)

        if content != original:
            # Test if the fixed content is valid Python
            try:
                compile(content, filepath, "exec")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except SyntaxError as e:
                # Try one more aggressive fix
                lines = content.split("\n")
                if len(lines) > e.lineno - 1:
                    problem_line = lines[e.lineno - 1]
                    # If it's a print/logger line with f-string issues, try to fix
                    if ("print(" in problem_line or "logger." in problem_line) and 'f"' in problem_line:
                        # Balance the parentheses
                        open_parens = problem_line.count("(")
                        close_parens = problem_line.count(")")
                        if open_parens > close_parens:
                            lines[e.lineno - 1] = problem_line + ")" * (open_parens - close_parens)
                            content = "\n".join(lines)
                            try:
                                compile(content, filepath, "exec")
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(content)
                                return True
                            except:
                                pass
                return False
        return False
    except Exception as e:
        return False


def get_files_with_syntax_errors():
    """Get all files with syntax errors."""
    result = subprocess.run(
        [".venv/bin/ruff", "check", "--select", "E999", "--output-format=json"], capture_output=True, text=True
    )

    files = set()
    try:
        errors = json.loads(result.stdout)
        for error in errors:
            if "filename" in error:
                files.add(error["filename"])
    except:
        pass

    return list(files)


def main():
    print("🔧 Enhanced Surgical Syntax Error Fixer v2")
    print("=" * 50)

    # Get files with syntax errors
    print("Scanning for syntax errors...")
    error_files = get_files_with_syntax_errors()
    print(f"Found {len(error_files)} files with syntax errors")

    # Prioritize certain directories
    priority_dirs = ["examples/", "candidate/qi/", "candidate/core/", "branding/"]

    # Sort files by priority
    sorted_files = []
    for pdir in priority_dirs:
        sorted_files.extend([f for f in error_files if f.startswith(pdir)])
    sorted_files.extend([f for f in error_files if f not in sorted_files])

    fixed_count = 0
    failed_files = []

    for i, filepath in enumerate(sorted_files[:200], 1):  # Process up to 200 files
        if fix_file(filepath):
            fixed_count += 1
            print(f"✅ [{i}/{len(sorted_files[:200])}] Fixed: {filepath}")
        else:
            failed_files.append(filepath)
            # print(f"❌ [{i}/{len(sorted_files[:200])}] Failed: {filepath}")

    print(f"\n✨ Successfully fixed {fixed_count} files")
    if failed_files:
        print(f"⚠️  {len(failed_files)} files couldn't be automatically fixed")

    # Check remaining errors
    print("\n📊 Checking remaining errors...")
    result = subprocess.run([".venv/bin/ruff", "check", "--statistics"], capture_output=True, text=True)

    # Parse and show improvement
    for line in result.stdout.split("\n")[:5]:
        if line.strip():
            print(f"  {line}")


if __name__ == "__main__":
    main()
