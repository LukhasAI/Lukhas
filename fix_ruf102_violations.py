#!/usr/bin/env python3
"""
Targeted RUF102 violation fixes for LUKHAS AI platform.
Addresses specific import formatting issues found by ruff.
"""

import os
import re
import subprocess


def run_ruff_json():
    """Get RUF102 violations as JSON"""
    try:
        result = subprocess.run(
            ['python3', '-m', 'ruff', 'check', '--select', 'RUF102', '--output-format=json', '.'],
            capture_output=True,
            text=True,
            cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
        )
        return result.stdout
    except Exception as e:
        print(f"Error running ruff: {e}")
        return ""

def fix_expected_comma_errors(file_path):
    """Fix 'Expected `,`, found name' errors by adding missing commas in imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix common import patterns missing commas
        # Pattern: from X import A B -> from X import A, B
        content = re.sub(
            r'^(\s*from\s+\S+\s+import\s+[^,\n]+?)(\s+)([A-Za-z_][A-Za-z0-9_]*)',
            r'\1,\2\3',
            content,
            flags=re.MULTILINE
        )

        # Fix multi-line imports missing commas
        # Look for import statements across multiple lines
        lines = content.split('\n')
        new_lines = []
        in_import = False

        for i, line in enumerate(lines):
            if line.strip().startswith(('from ', 'import ')) and 'import' in line:
                in_import = True
                # Check if this line should have a comma but doesn't
                if (not line.rstrip().endswith(',') and 
                    not line.rstrip().endswith(')') and
                    i + 1 < len(lines) and
                    lines[i + 1].strip() and
                    not lines[i + 1].strip().startswith(('from ', 'import ', '#', '"""', "'''"))) :

                    # Check if next line looks like a continuation
                    next_line = lines[i + 1].strip()
                    if (next_line and 
                        not next_line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except')) and
                        re.match(r'^[A-Za-z_][A-Za-z0-9_]*', next_line)):
                        line = line.rstrip() + ','

            elif in_import and line.strip() and not line.strip().startswith('#'):
                # We're in a multi-line import
                if ')' in line:
                    in_import = False
                elif not line.rstrip().endswith(',') and not line.rstrip().endswith(')'):
                    # This might need a comma
                    if (i + 1 < len(lines) and 
                        lines[i + 1].strip() and
                        re.match(r'^[A-Za-z_][A-Za-z0-9_]*', lines[i + 1].strip())):
                        line = line.rstrip() + ','
            else:
                in_import = False

            new_lines.append(line)

        content = '\n'.join(new_lines)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_colon_comma_errors(file_path):
    """Fix 'Expected `,`, found `:`' and 'Expected `:`, found `,`' errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix dict-like patterns in imports that have colon/comma confusion
        # This is trickier - let's look at the specific line patterns
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if 'import' in line and (':' in line and ',' in line):
                # This might be a malformed import - try to fix common patterns
                # Look for patterns like: from x import a: b, -> from x import a, b
                if re.search(r'import\s+[^:,]+:[^,]*,', line):
                    line = re.sub(r'(\w+):\s*(\w+),', r'\1, \2,', line)
                    line = re.sub(r'(\w+):(\w+)', r'\1, \2', line)

            new_lines.append(line)

        content = '\n'.join(new_lines)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_indentation_errors(file_path):
    """Fix indentation and try/except block issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_lines = lines[:]
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Fix incomplete try blocks
            if line.strip() == 'try:' and i + 1 < len(lines):
                new_lines.append(line)
                i += 1
                # Ensure there's at least a pass statement and except block
                if i < len(lines) and not lines[i].strip():
                    new_lines.append('    pass\n')
                    new_lines.append('except Exception:\n')
                    new_lines.append('    pass\n')
                continue

            # Fix indentation mismatches
            if line.startswith('    ') and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.endswith(':') and not prev_line.startswith('#'):
                    # This might be a continuation that should be unindented
                    if not any(lines[j].strip().endswith(':') for j in range(max(0, i-3), i)):
                        line = line.lstrip()

            new_lines.append(line)
            i += 1

        if new_lines != original_lines:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        return False

    except Exception as e:
        print(f"Error fixing indentation in {file_path}: {e}")
        return False

def main():
    """Main function to fix all RUF102 violations"""
    print("🛡️ LUKHAS AI T4 RUF102 Violation Repair")
    print("=" * 50)

    # Get current violations
    print("Scanning for RUF102 violations...")
    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')

    # Run ruff to get specific files with violations
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF102', '.'],
        capture_output=True,
        text=True
    )

    if not result.stdout:
        print("✅ No RUF102 violations found!")
        return

    # Parse violations to get file list
    violation_files = set()
    for line in result.stdout.split('\n'):
        if line and ':' in line:
            file_path = line.split(':')[0]
            if os.path.exists(file_path):
                violation_files.add(file_path)

    print(f"Found {len(violation_files)} files with RUF102 violations")

    # Fix each file
    fixed_files = 0
    for file_path in violation_files:
        print(f"Fixing: {file_path}")

        # Try different fix strategies
        fixed = False

        # Fix comma errors first
        if fix_expected_comma_errors(file_path):
            fixed = True
            print(f"  ✅ Fixed comma errors in {file_path}")

        # Fix colon/comma confusion
        if fix_colon_comma_errors(file_path):
            fixed = True
            print(f"  ✅ Fixed colon/comma errors in {file_path}")

        # Fix indentation issues
        if fix_indentation_errors(file_path):
            fixed = True
            print(f"  ✅ Fixed indentation in {file_path}")

        if fixed:
            fixed_files += 1

    print(f"\n🎯 Fixed {fixed_files} files")

    # Check remaining violations
    print("\nChecking remaining violations...")
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF102', '.'],
        capture_output=True,
        text=True
    )

    if result.stdout:
        violations = len([line for line in result.stdout.split('\n') if line.strip() and ':' in line])
        print(f"⚠️  {violations} RUF102 violations remaining")
        print("\nRemaining issues:")
        print(result.stdout)
    else:
        print("🎉 All RUF102 violations eliminated!")

if __name__ == "__main__":
    main()