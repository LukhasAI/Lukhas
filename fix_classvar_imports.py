#!/usr/bin/env python3
"""Fix missing ClassVar imports in files using ClassVar annotations."""
import glob
import re

files_missing_import = []

for filepath in glob.glob("**/*.py", recursive=True):
    if "__pycache__" in filepath or ".pyc" in filepath:
        continue
    if filepath.startswith(".venv/") or filepath.startswith("venv/"):
        continue

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        if "ClassVar[" in content:
            # Check if ClassVar is imported
            has_import = bool(re.search(r'from typing import.*\bClassVar\b', content))

            if not has_import:
                # Check if there's a typing import we can modify
                typing_import_match = re.search(r'from typing import ([^\n]+)', content)

                if typing_import_match:
                    old_import = typing_import_match.group(0)
                    imports = typing_import_match.group(1)

                    # Add ClassVar to the import list
                    if '(' in imports:
                        # Multi-line import - insert at beginning
                        new_import = old_import.replace('from typing import', 'from typing import ClassVar,')
                    else:
                        # Single line import - add ClassVar in alphabetical position
                        import_list = [i.strip() for i in imports.split(',')]
                        if 'ClassVar' not in import_list:
                            import_list.append('ClassVar')
                            import_list.sort()
                            new_import = f"from typing import {', '.join(import_list)}"

                    # Replace the import
                    new_content = content.replace(old_import, new_import, 1)

                    with open(filepath, 'w') as f:
                        f.write(new_content)

                    files_missing_import.append(filepath)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(f"Fixed ClassVar imports in {len(files_missing_import)} files")
for f in files_missing_import[:20]:
    print(f"  ✓ {f}")

if len(files_missing_import) > 20:
    print(f"  ... and {len(files_missing_import) - 20} more files")
