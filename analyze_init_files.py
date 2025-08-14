#!/usr/bin/env python3
import os

empty_inits = []
meaningful_inits = []
stub_only_dirs = []

for root, dirs, files in os.walk('.'):
    # Skip hidden and special directories
    if any(part.startswith('.') for part in root.split('/')):
        continue
    if 'site-packages' in root or '__pycache__' in root:
        continue
        
    # Check if directory has __init__.py
    init_path = os.path.join(root, '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r') as f:
            content = f.read()
            # Count non-comment, non-whitespace lines
            lines = []
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    # Skip docstrings
                    if not (stripped == '"""' or stripped == "'''" or 
                           stripped.startswith('"""') or stripped.startswith("'''")):
                        lines.append(line)
            
            # Check if it's empty or just imports __version__ etc
            if len(lines) <= 1:
                empty_inits.append(init_path)
                # Check if directory ONLY has __init__.py
                other_py = [f for f in files if f.endswith('.py') and f != '__init__.py']
                subdirs = [d for d in dirs if not d.startswith('__')]
                if not other_py and not subdirs:
                    stub_only_dirs.append(root)
            else:
                meaningful_inits.append((init_path, len(lines)))

print(f"=== SUMMARY ===")
print(f"Empty/stub __init__.py files: {len(empty_inits)}")
print(f"Meaningful __init__.py files: {len(meaningful_inits)}")
print(f"Directories with ONLY stub __init__.py: {len(stub_only_dirs)}")

print(f"\n=== Sample meaningful __init__.py files ===")
for path, lines in sorted(meaningful_inits, key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {lines} code lines: {path}")

print(f"\n=== Stub-only directories (safe to remove) ===")
for d in sorted(stub_only_dirs)[:20]:
    print(f"  {d}")
if len(stub_only_dirs) > 20:
    print(f"  ... and {len(stub_only_dirs) - 20} more")
