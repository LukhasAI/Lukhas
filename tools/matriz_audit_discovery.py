#!/usr/bin/env python3
"""
MATRIZ Audit Discovery Tool

Scans the codebase to discover all modules and their locations.
Produces a comprehensive inventory of modules, their paths, and contracts.
"""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List


def find_matrix_contracts(root_path: pathlib.Path) -> List[pathlib.Path]:
    """Find all matrix_*.json files in the codebase."""
    contracts = []

    # Search patterns for different areas
    search_patterns = ["matrix_*.json", "**/matrix_*.json"]

    for pattern in search_patterns:
        contracts.extend(root_path.glob(pattern))

    # Remove duplicates and sort
    unique_contracts = list(set(contracts))
    unique_contracts.sort()

    return unique_contracts


def get_module_name_from_contract(contract_path: pathlib.Path) -> str:
    """Extract module name from contract file, either from content or filename."""
    try:
        with open(contract_path, "r") as f:
            contract_data = json.load(f)

        # Check if contract specifies a canonical module name
        if "module" in contract_data:
            return contract_data["module"]

    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass

    # Fall back to filename-based naming
    filename = contract_path.name
    if filename.startswith("matrix_"):
        return filename[7:-5]  # Remove 'matrix_' prefix and '.json' suffix

    return filename[:-5]  # Just remove '.json'


def discover_module_directories(root_path: pathlib.Path) -> Dict[str, List[str]]:
    """Discover directories that contain module code."""
    module_dirs = {}

    # Key directories to scan
    scan_dirs = [
        root_path / "lukhas",
        root_path / "contracts",
        root_path / "memory",
        root_path / "core",
        root_path / "bio",
        root_path / "branding",
        root_path / "labs",
        root_path / "governance",
        root_path / "identity",
        root_path / "api",
        root_path / "tools",
        root_path / "tests",
    ]

    # Add any directory that exists
    for scan_dir in scan_dirs:
        if scan_dir.exists() and scan_dir.is_dir():
            # Use directory name as module hint
            module_name = scan_dir.name
            if module_name not in module_dirs:
                module_dirs[module_name] = []
            module_dirs[module_name].append(str(scan_dir.relative_to(root_path)))

    # Scan lukhas/ subdirectories specifically
    lukhas_dir = root_path / "lukhas"
    if lukhas_dir.exists():
        for subdir in lukhas_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                module_name = subdir.name
                if module_name not in module_dirs:
                    module_dirs[module_name] = []
                module_dirs[module_name].append(str(subdir.relative_to(root_path)))

    return module_dirs


def build_module_inventory(root_path: pathlib.Path) -> List[Dict[str, Any]]:
    """Build comprehensive module inventory."""
    inventory = []

    # Find all contracts
    contracts = find_matrix_contracts(root_path)

    # Discover module directories
    module_dirs = discover_module_directories(root_path)

    # Track modules we've seen
    seen_modules = set()

    # Process modules with contracts first
    for contract_path in contracts:
        module_name = get_module_name_from_contract(contract_path)

        if module_name in seen_modules:
            # Find existing entry and add contract
            for entry in inventory:
                if entry["module"] == module_name:
                    entry["contracts"].append(str(contract_path.relative_to(root_path)))
                    break
        else:
            # Create new entry
            module_entry = {
                "module": module_name,
                "paths": module_dirs.get(module_name, []),
                "contracts": [str(contract_path.relative_to(root_path))],
                "has_contract": True,
            }

            # Look for additional paths based on contract location
            contract_dir = contract_path.parent
            if contract_dir != root_path:
                relative_contract_dir = str(contract_dir.relative_to(root_path))
                if relative_contract_dir not in module_entry["paths"]:
                    module_entry["paths"].append(relative_contract_dir)

            inventory.append(module_entry)
            seen_modules.add(module_name)

    # Process modules without contracts
    for module_name, paths in module_dirs.items():
        if module_name not in seen_modules:
            module_entry = {"module": module_name, "paths": paths, "contracts": [], "has_contract": False}
            inventory.append(module_entry)
            seen_modules.add(module_name)

    # Sort by module name
    inventory.sort(key=lambda x: x["module"])

    return inventory


def main():
    parser = argparse.ArgumentParser(description="Discover MATRIZ modules and their locations")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: current directory)")
    parser.add_argument("--output", default="artifacts/matriz_inventory.json", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    root_path = pathlib.Path(args.root).resolve()
    output_path = pathlib.Path(args.output)

    if args.verbose:
        print(f"Scanning root path: {root_path}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build inventory
    inventory = build_module_inventory(root_path)

    # Prepare output
    output_data = {
        "timestamp": "2025-09-27T13:12:00Z",
        "root_path": str(root_path),
        "total_modules": len(inventory),
        "modules_with_contracts": len([m for m in inventory if m["has_contract"]]),
        "modules_without_contracts": len([m for m in inventory if not m["has_contract"]]),
        "modules": inventory,
    }

    # Write output
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    if args.verbose:
        print("Discovery complete:")
        print(f"  Total modules: {output_data['total_modules']}")
        print(f"  With contracts: {output_data['modules_with_contracts']}")
        print(f"  Without contracts: {output_data['modules_without_contracts']}")
        print(f"  Output written to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
