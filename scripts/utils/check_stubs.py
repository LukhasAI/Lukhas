#!/usr/bin/env python3
import os

# Get all stub directories
stub_dirs = []
for dir_name in os.listdir("."):
    if os.path.isdir(dir_name) and not dir_name.startswith("."):
        dir_path = os.path.join(dir_name, "__init__.py")
        if os.path.exists(dir_path):
            # Check if only __init__.py exists
            files = [f for f in os.listdir(dir_name) if not f.startswith(".")]
            if len(files) == 1 and files[0] == "__init__.py":
                # Check if it's a stub (small file)
                with open(dir_path) as f:
                    lines = len(f.readlines())
                    if lines < 10:  # Small stub file
                        stub_dirs.append(dir_name)

print(f"Found {len(stub_dirs)} stub directories")

# Check for imports
import_found = {}
for stub in sorted(stub_dirs):
    # Search for imports of this module
    import_patterns = [
        f"from {stub}",
        f"import {stub}",
        f"'{stub}'",
        f'"{stub}"',
    ]

    found = False
    for root, dirs, files in os.walk("."):
        # Skip hidden and archive directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != stub]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path) as f:
                        content = f.read()
                        for pattern in import_patterns:
                            if pattern in content:
                                found = True
                                if stub not in import_found:
                                    import_found[stub] = []
                                import_found[stub].append(file_path)
                                break
                    if found:
                        break
                except:
                    pass
        if found:
            break

# Report results
print("\n=== IMPORTED STUBS (DO NOT REMOVE) ===")
for stub in sorted(import_found.keys()):
    print(f"  {stub}: imported in {len(import_found[stub])} file(s)")

print("\n=== SAFE TO REMOVE (NOT IMPORTED) ===")
safe_to_remove = [s for s in stub_dirs if s not in import_found]
for stub in sorted(safe_to_remove):
    print(f"  {stub}")

print(f"\nTotal safe to remove: {len(safe_to_remove)}")
