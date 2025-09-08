#!/usr/bin/env python3
"""
Comprehensive F-String Bracket Fix Script

This script systematically fixes all f-string bracket issues in a file.
It handles cases where parentheses are mismatched in f-string expressions.
"""

import re
import sys
from pathlib import Path


def comprehensive_fstring_fix(content: str) -> tuple[str, int]:
    """
    Comprehensively fix f-string bracket mismatches.
    
    Args:
        content: The file content as a string
        
    Returns:
        tuple: (fixed_content, number_of_fixes_made)
    """
    total_fixes = 0

    # Phase 1: Fix f-strings with unmatched closing parentheses
    # Pattern: {something) instead of {something}
    # This matches expressions inside {} that have extra ) at the end
    pattern1 = r"\{([^{}]*)\)"
    matches1 = re.findall(pattern1, content)
    if matches1:
        content = re.sub(pattern1, r"{\1}", content)
        total_fixes += len(matches1)

    # Phase 2: Fix function calls where } was used instead of )
    # Look for lines that end with } but should end with )
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        original_line = line

        # Fix standalone } that should be )
        if re.match(r"^\s*\}\s*$", line):
            if i > 0:
                prev_line = lines[i-1].strip()
                # If previous line looks like a function call or f-string ending
                if ("logger." in prev_line or 'f"' in prev_line or "print(" in prev_line) and (prev_line.endswith('."') or prev_line.endswith(".'") or prev_line.endswith(",")):
                    line = line.replace("}", ")")
                    total_fixes += 1

        # Fix dictionary/list access patterns
        line = re.sub(r"\.keys\(\}", ".keys()", line)
        line = re.sub(r"\.append\(([^}]*)\}", r".append(\1)", line)
        line = re.sub(r"\.pop\(([^}]*)\}", r".pop(\1)", line)

        # Fix function argument patterns
        if "self.config." in line and "}" in line and "(" in line:
            line = re.sub(r"self\.config\.([^}]*)\}", r"self.config.\1)", line)

        # Fix list/dict comprehensions
        line = re.sub(r"len\(([^}]*)\}", r"len(\1)", line)

        if line != original_line:
            total_fixes += 1

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Phase 3: Fix specific patterns we see in the errors
    # Fix unmatched ) in f-strings by balancing braces
    fstring_fixes = [
        # Fix cases where there's an extra ) inside f-string expressions
        (r'f"([^"]*\{[^}]*)\)"', r'f"\1}"'),
        (r"f'([^']*\{[^}]*)\)'", r"f'\1}'"),

        # Fix missing ) in function calls within f-strings
        (r"\{int\(time\.time\(\)\*1000\}", r"{int(time.time()*1000)}"),
        (r"\{([^{}]*)\.[^}]*\}", lambda m: "{" + m.group(1) + "}"),
    ]

    for pattern, replacement in fstring_fixes:
        if isinstance(replacement, str):
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                total_fixes += content.count(pattern)
                content = new_content
        else:
            # For lambda replacements, count manually
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                total_fixes += len(matches)

    return content, total_fixes


def main():
    """Main function to process the file."""
    if len(sys.argv) != 2:
        print("Usage: python comprehensive_fstring_fix.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    try:
        # Read the original file
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        print(f"Processing file: {file_path}")

        # Apply comprehensive fixes
        fixed_content, fixes_made = comprehensive_fstring_fix(original_content)

        if fixes_made == 0:
            print("No additional f-string issues found. File unchanged.")
            return

        # Write the fixed content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        print(f"✅ Applied {fixes_made} comprehensive f-string fixes")
        print(f"File successfully updated: {file_path}")

    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
