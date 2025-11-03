#!/usr/bin/env python3
"""
Find gaps between bridge modules and actual labs/* modules.
Identifies modules that exist in labs/* but aren't exposed in bridge __init__.py files.
"""
import re
from pathlib import Path

ROOT = Path(".")
LABS_DIR = ROOT / "labs"

def find_bridge_gaps():
    """Find modules in labs/* that aren't bridged."""
    gaps = []

    # Find all Python modules in labs/
    for py_file in LABS_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Convert file path to module path
        rel_path = py_file.relative_to(LABS_DIR)
        module_parts = list(rel_path.parent.parts) + [rel_path.stem]
        labs_module = "labs." + ".".join(module_parts)
        bridge_module = ".".join(module_parts)

        # Check if corresponding bridge exists
        bridge_init = ROOT / rel_path.parent / "__init__.py"

        if bridge_init.exists():
            content = bridge_init.read_text()
            module_name = rel_path.stem

            # Check if module is mentioned in bridge
            if f'"{module_name}"' not in content and f"'{module_name}'" not in content:
                gaps.append({
                    "labs_file": str(py_file),
                    "labs_module": labs_module,
                    "bridge_module": bridge_module,
                    "bridge_init": str(bridge_init),
                    "module_name": module_name
                })

    return gaps

def main():
    gaps = find_bridge_gaps()

    print(f"Found {len(gaps)} modules in labs/* without bridge exposure:\n")

    # Group by bridge directory
    by_bridge = {}
    for gap in gaps:
        bridge_dir = str(Path(gap["bridge_init"]).parent)
        if bridge_dir not in by_bridge:
            by_bridge[bridge_dir] = []
        by_bridge[bridge_dir].append(gap)

    for bridge_dir, modules in sorted(by_bridge.items()):
        print(f"\n{bridge_dir}/ needs these modules:")
        for mod in modules:
            print(f"  - {mod['module_name']}")

    # Write gaps to file
    output = ROOT / "release_artifacts" / "matriz_readiness_v1" / "discovery" / "bridge_gaps.txt"
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w") as f:
        for gap in gaps:
            f.write(f"{gap['bridge_module']}.{gap['module_name']}\n")

    print(f"\n\nWrote {len(gaps)} gaps to {output}")

if __name__ == "__main__":
    main()
