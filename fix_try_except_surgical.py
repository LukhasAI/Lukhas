#!/usr/bin/env python3
"""
Surgical fix for malformed try/except blocks in test_core_components_comprehensive.py
"""


def fix_try_except_blocks():
    """Fix malformed try/except blocks with wrong indentation"""
    file_path = '/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/e2e/test_core_components_comprehensive.py'

    with open(file_path) as f:
        content = f.read()

    # Fix the specific pattern: try:\n<code>\nexcept Exception:\n    pass
    # where except is at wrong indentation

    # Split into lines for precise fixing
    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for malformed try/except pattern
        if ('try:' in line and
            i + 1 < len(lines) and
            'from ' in lines[i + 1] and
            i + 2 < len(lines) and
            lines[i + 2].strip() == 'except Exception:'):

            # This is a malformed try/except block
            # Keep the try line
            fixed_lines.append(line)

            # Add the import line with proper indentation
            import_line = lines[i + 1]
            if not import_line.startswith('    '):
                import_line = '    ' + import_line.lstrip()
            fixed_lines.append(import_line)

            # Fix the except line with proper indentation
            except_line = lines[i + 2]
            if except_line.strip() == 'except Exception:':
                fixed_lines.append('        except Exception:')

                # Add pass statement
                if i + 3 < len(lines) and lines[i + 3].strip() == 'pass':
                    fixed_lines.append('            pass')
                    i += 4
                else:
                    fixed_lines.append('            pass')
                    i += 3
            else:
                fixed_lines.append(line)
                i += 1

        # Handle orphaned except blocks
        elif (line.strip() == 'except Exception:' and
              i > 0 and
              not lines[i-1].strip().endswith(':')):
            # This except is orphaned, skip it
            i += 1
            # Also skip the pass if it follows
            if i < len(lines) and lines[i].strip() == 'pass':
                i += 1

        else:
            fixed_lines.append(line)
            i += 1

    # Write back the fixed content
    fixed_content = '\n'.join(fixed_lines)

    with open(file_path, 'w') as f:
        f.write(fixed_content)

    print(f"✅ Fixed try/except blocks in {file_path}")

def main():
    print("🛡️ LUKHAS AI Surgical Try/Except Fix")
    fix_try_except_blocks()
    print("✅ Complete")

if __name__ == "__main__":
    main()
