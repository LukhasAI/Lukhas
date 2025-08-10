#!/usr/bin/env python3
"""
Rename quantum references to more appropriate terminology.
Changes 'quantum' to 'quantum-inspired' or similar metaphors.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Replacement mappings
REPLACEMENTS = {
    # In documentation and comments
    r"quantum capabilities": "quantum-inspired capabilities",
    r"quantum processing": "quantum-inspired processing",
    r"quantum algorithms": "quantum-inspired algorithms",
    r"quantum computing": "quantum-inspired computing",
    r"quantum mechanics": "quantum-inspired mechanics",
    r"quantum state": "quantum-like state",
    r"quantum entanglement": "entanglement-like correlation",
    r"quantum superposition": "superposition-like state",
    r"quantum coherence": "coherence-inspired processing",
    r"quantum tunneling": "probabilistic exploration",
    r"quantum measurement": "probabilistic observation",
    r"Quantum capabilities": "Quantum-inspired capabilities",
    r"Quantum processing": "Quantum-inspired processing",
    r"Quantum algorithms": "Quantum-inspired algorithms",
    # In code (be more careful)
    r"QuantumProcessor": "QuantumInspiredProcessor",
    r"quantum_processor": "quantum_inspired_processor",
    r"QuantumLayer": "QuantumInspiredLayer",
    r"quantum_layer": "quantum_inspired_layer",
    r"QuantumState": "QuantumLikeState",
    r"quantum_state": "quantum_like_state",
    r"QuantumGate": "QuantumInspiredGate",
    r"quantum_gate": "quantum_inspired_gate",
    # Module/directory names (handled separately)
    r"from quantum import": "from quantum_inspired import",
    r"import quantum": "import quantum_inspired",
}

# Files to skip
SKIP_FILES = {
    "rename_quantum_references.py",  # Don't modify this script itself
}


def update_file_content(
    filepath: Path, dry_run: bool = False
) -> Tuple[bool, List[str]]:
    """Update quantum references in a file."""
    changes = []

    if filepath.name in SKIP_FILES:
        return False, []

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except:
        return False, []

    original_content = content

    # Apply replacements
    for pattern, replacement in REPLACEMENTS.items():
        if re.search(pattern, content):
            count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            changes.append(
                f"Replaced {count} instances of '{pattern}' with '{replacement}'"
            )

    # Special handling for module descriptions
    if "README" in filepath.name:
        content = re.sub(
            r"quantum[- ]inspired", "quantum-inspired", content, flags=re.IGNORECASE
        )

        # Update module descriptions
        content = re.sub(
            r"Quantum-inspired processing and algorithms",
            "Advanced probabilistic and parallel processing algorithms inspired by quantum computing principles",
            content,
        )

    if content != original_content and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, changes

    return len(changes) > 0, changes


def rename_quantum_directory(base_path: Path, dry_run: bool = False) -> bool:
    """Rename the quantum directory to quantum_inspired."""
    quantum_dir = base_path / "quantum"
    new_dir = base_path / "quantum_inspired"

    if quantum_dir.exists() and not new_dir.exists():
        if not dry_run:
            quantum_dir.rename(new_dir)
            print("✅ Renamed directory: quantum/ -> quantum_inspired/")
        else:
            print("Would rename: quantum/ -> quantum_inspired/")
        return True
    return False


def update_module_structure_dict(filepath: Path, dry_run: bool = False) -> bool:
    """Update MODULE_STRUCTURE dictionary in documentation scripts."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except:
        return False

    # Update the module structure dictionary
    if "MODULE_STRUCTURE" in content and '"quantum"' in content:
        content = re.sub(
            r'"quantum":\s*"[^"]*"',
            '"quantum_inspired": "Advanced probabilistic and parallel processing algorithms inspired by quantum computing principles"',
            content,
        )

        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        return True
    return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Rename quantum references to quantum-inspired"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed"
    )
    parser.add_argument("--path", type=str, default=".", help="Base path")
    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    print(f"Updating quantum references in: {base_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'UPDATING FILES'}")
    print("-" * 80)

    # First, rename the quantum directory
    if rename_quantum_directory(base_path, args.dry_run):
        print("Directory renamed successfully\n")

    # Update documentation scripts
    doc_scripts = [
        base_path / "scripts" / "update_documentation.py",
        base_path / "scripts" / "fix_imports.py",
    ]

    for script in doc_scripts:
        if script.exists():
            if update_module_structure_dict(script, args.dry_run):
                print(f"✅ Updated MODULE_STRUCTURE in {script.name}")

    # Find all files to update
    all_files = []
    for ext in ["*.py", "*.md", "*.txt", "*.yaml", "*.yml", "*.json"]:
        all_files.extend(base_path.rglob(ext))

    # Filter out unwanted paths
    files_to_update = [
        f
        for f in all_files
        if not any(
            skip in str(f) for skip in [".git", "__pycache__", "node_modules", ".venv"]
        )
    ]

    print(f"\nFound {len(files_to_update)} files to check...")

    modified_count = 0
    all_changes = []

    for filepath in files_to_update:
        modified, changes = update_file_content(filepath, args.dry_run)

        if modified:
            modified_count += 1
            rel_path = filepath.relative_to(base_path)
            all_changes.append((rel_path, changes))

            if len(all_changes) <= 10:  # Show first 10
                print(f"\n{rel_path}:")
                for change in changes[:3]:  # Show first 3 changes per file
                    print(f"  - {change}")
                if len(changes) > 3:
                    print(f"  - ... and {len(changes) - 3} more changes")

    if modified_count > 10:
        print(f"\n... and {modified_count - 10} more files")

    print("\n" + "=" * 80)
    print(
        f"Summary: {'Would update' if args.dry_run else 'Updated'} {modified_count} files"
    )

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")
    else:
        print(
            "\n✅ All quantum references have been updated to quantum-inspired terminology"
        )
        print("\nNext steps:")
        print("1. Update import statements: python3 scripts/fix_imports.py")
        print("2. Update documentation: python3 scripts/update_documentation.py")
        print("3. Run tests to ensure everything works")


if __name__ == "__main__":
    main()
