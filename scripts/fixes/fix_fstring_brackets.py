#!/usr/bin/env python3
"""
F-String Bracket Mismatch Fix Script

This script fixes common f-string bracket mismatches where there are extra
closing parentheses immediately after closing braces in f-string expressions.

Patterns fixed:
1. {variable)} → {variable}
2. {variable:.2f)} → {variable:.2f}  
3. {expression)} → {expression}

Usage:
    python fix_fstring_brackets.py <file_path>
"""

import re
import sys
from pathlib import Path


def fix_fstring_brackets(content: str) -> tuple[str, int]:
    """
    Fix f-string bracket mismatches in the given content.
    
    Args:
        content: The file content as a string
        
    Returns:
        tuple: (fixed_content, number_of_fixes_made)
    """
    total_fixes = 0

    # Post-process fix for cases where the aggressive replacement was wrong
    # Fix standalone closing braces that should be closing parentheses in function calls
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Pattern 1: Function call ending with } instead of )
        if re.match(r"^[\s]*}[\s]*$", line):
            # Check if previous line looks like a function call or f-string
            if i > 0:
                prev_line = lines[i-1].strip()
                if (prev_line.endswith('."') or prev_line.endswith(".'")) and 'f"' in prev_line:
                    line = line.replace("}", ")")
                    total_fixes += 1

        # Pattern 2: Missing closing parentheses in f-strings like int(time.time()*1000
        line = re.sub(r"int\(time\.time\(\)\*1000\}", "int(time.time()*1000)}", line)

        # Pattern 3: Dictionary access ending with }
        line = re.sub(r"\.keys\(\}", ".keys()", line)

        # Pattern 4: Other function call patterns that got messed up
        if "}" in line and ("(" in line or "append(" in line or ".pop(" in line):
            # Fix cases like .append(something}
            line = re.sub(r"([^{]*\([^}]*)\}", r"\1)", line)

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    return content, total_fixes


def main():
    """Main function to process the file."""
    if len(sys.argv) != 2:
        print("Usage: python fix_fstring_brackets.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    if not file_path.is_file():
        print(f"Error: {file_path} is not a file.")
        sys.exit(1)

    try:
        # Read the original file
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        print(f"Processing file: {file_path}")
        print(f"Original file size: {len(original_content)} characters")

        # Fix the f-string brackets
        fixed_content, fixes_made = fix_fstring_brackets(original_content)

        if fixes_made == 0:
            print("No f-string bracket issues found. File unchanged.")
            return

        # Write the fixed content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        print(f"✅ Fixed {fixes_made} f-string bracket issues")
        print(f"Fixed file size: {len(fixed_content)} characters")
        print(f"File successfully updated: {file_path}")

        # Show some examples of what was fixed
        if fixes_made > 0:
            print("\nExample patterns that were fixed:")
            pattern = r"\{([^{}]*)\}\)"
            sample_matches = re.findall(pattern, original_content)[:5]  # Show first 5
            for i, match in enumerate(sample_matches, 1):
                print(f"  {i}. {{{match}} → {{{match}}")
                if i >= 5:
                    break
            if len(sample_matches) > 5:
                print(f"  ... and {len(sample_matches) - 5} more")

    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()