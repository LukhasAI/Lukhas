#!/usr/bin/env python3
"""
Analyze core module isolation (excluding .venv)
"""

import json

# Load the connectivity report
with open("module_connectivity_report.json") as f:
    data = json.load(f)

# Filter out .venv modules
isolated_core_modules = {}
total_isolated_core = 0

for directory, modules in data["isolated_modules"]["by_directory"].items():
    if not directory.startswith(".venv"):
        isolated_core_modules[directory] = modules
        total_isolated_core += len(modules)

# Sort by number of isolated modules
sorted_dirs = sorted(
    isolated_core_modules.items(), key=lambda x: len(x[1]), reverse=True
)

print("=" * 60)
print("CORE MODULE ISOLATION ANALYSIS")
print("(Excluding .venv directories)")
print("=" * 60)

print(
    f"\nTotal Core Modules: {data['summary']['total_modules'] - sum(len(m) for d, m in data['isolated_modules']['by_directory'].items() if d.startswith('.venv'))}"
)
print(f"Isolated Core Modules: {total_isolated_core}")
print(
    f"Core Isolation Rate: {(total_isolated_core / (data['summary']['total_modules'] - sum(len(m) for d, m in data['isolated_modules']['by_directory'].items() if d.startswith('.venv'))) * 100):.1f}%"
)

print("\n\nMost Isolated Directories:")
print("-" * 60)

for directory, modules in sorted_dirs[:20]:
    print(f"\n{directory or 'root'}/ - {len(modules)} isolated modules")
    # Show first 5 modules
    for module in modules[:5]:
        print(f"  - {module}")
    if len(modules) > 5:
        print(f"  ... and {len(modules) - 5} more")

print("\n\nKey Isolated System Modules:")
print("-" * 60)

# Identify key system modules that are isolated
key_systems = [
    "core",
    "consciousness",
    "quantum",
    "memory",
    "identity",
    "ethics",
    "learning",
]
for system in key_systems:
    system_isolated = []
    for directory, modules in isolated_core_modules.items():
        for module in modules:
            if module.startswith(system):
                system_isolated.append(module)

    if system_isolated:
        print(f"\n{system.upper()} System - {len(system_isolated)} isolated modules:")
        for module in system_isolated[:10]:
            print(f"  - {module}")
        if len(system_isolated) > 10:
            print(f"  ... and {len(system_isolated) - 10} more")

# Save core-only report
core_report = {
    "total_core_modules": data["summary"]["total_modules"]
    - sum(
        len(m)
        for d, m in data["isolated_modules"]["by_directory"].items()
        if d.startswith(".venv")
    ),
    "isolated_core_modules": total_isolated_core,
    "core_isolation_rate": (
        total_isolated_core
        / (
            data["summary"]["total_modules"]
            - sum(
                len(m)
                for d, m in data["isolated_modules"]["by_directory"].items()
                if d.startswith(".venv")
            )
        )
        * 100
    ),
    "isolated_by_directory": isolated_core_modules,
    "top_hubs": data["top_hubs"],
}

with open("core_isolation_report.json", "w") as f:
    json.dump(core_report, f, indent=2)

print("\n\nReport saved to: core_isolation_report.json")
print("=" * 60)
