#!/usr/bin/env python3
"""
Identify critical unused files that might be important
"""

import json
from pathlib import Path


def main():
    # Load the unused files report
    report_path = Path(__file__).parent / "unused_files_report.json"
    with open(report_path) as f:
        data = json.load(f)

    # Define critical patterns
    critical_patterns = {
        "Main Entry Points": [
            "main.py",
            "app.py",
            "server.py",
            "api.py",
            "cli.py",
            "run.py",
        ],
        "Core Infrastructure": [
            "core_hub.py",
            "integration_hub.py",
            "message_hub.py",
            "orchestrator.py",
            "coordinator.py",
            "manager.py",
        ],
        "Identity System": [
            "identity_hub.py",
            "id_manager.py",
            "lukhas",
            "auth",
            "qrg",
        ],
        "Golden Trio Components": [
            "dast.py",
            "abas.py",
            "nias.py",
            "dast_",
            "abas_",
            "nias_",
        ],
        "Memory Systems": ["memory_hub.py", "memory_manager.py", "unified_memory"],
        "Quantum/Bio Integration": [
            "quantum_hub.py",
            "bio_hub.py",
            "quantum_consciousness",
            "bio_symbolic",
        ],
        "API/Controllers": ["controllers.py", "endpoints.py", "services.py", "api_"],
        "Reasoning/Ethics": [
            "reasoning_engine.py",
            "ethical_reasoning",
            "decision_node",
        ],
    }

    print("=" * 80)
    print("CRITICAL UNUSED FILES ANALYSIS")
    print("=" * 80)
    print(f"Total unused files: {len(data['unused_files'])}\n")

    critical_findings = {}

    for category, patterns in critical_patterns.items():
        matches = []
        for file_info in data["unused_files"]:
            path = file_info["path"].lower()
            filename = Path(file_info["path"]).name.lower()

            for pattern in patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in filename or pattern_lower in path:
                    matches.append(file_info)
                    break

        if matches:
            critical_findings[category] = matches

    # Display findings
    for category, files in critical_findings.items():
        print(f"\n{category} ({len(files)} unused files):")
        print("-" * 60)

        # Sort by size
        sorted_files = sorted(files, key=lambda x: x["size_bytes"], reverse=True)

        for file_info in sorted_files[:10]:
            print(f"  📁 {file_info['path']}")
            print(f"     Size: {file_info['size_human']}")

            # Check if it's a large file (potential important code)
            if file_info["size_bytes"] > 10000:
                print("     ⚠️  Large file - may contain significant implementation")

    # Find potential duplicate implementations
    print("\n" + "=" * 80)
    print("POTENTIAL DUPLICATE IMPLEMENTATIONS:")
    print("=" * 80)

    duplicates = {
        "Orchestrators": [],
        "Hubs": [],
        "Managers": [],
        "Engines": [],
        "Bridges": [],
    }

    for file_info in data["unused_files"]:
        filename = Path(file_info["path"]).name.lower()

        if "orchestrator" in filename:
            duplicates["Orchestrators"].append(file_info)
        elif "hub" in filename and "github" not in filename:
            duplicates["Hubs"].append(file_info)
        elif "manager" in filename:
            duplicates["Managers"].append(file_info)
        elif "engine" in filename:
            duplicates["Engines"].append(file_info)
        elif "bridge" in filename:
            duplicates["Bridges"].append(file_info)

    for category, files in duplicates.items():
        if len(files) > 5:  # Only show if there are many duplicates
            print(f"\n{category}: {len(files)} unused implementations")
            print("Sample files:")
            for f in sorted(files, key=lambda x: x["size_bytes"], reverse=True)[:5]:
                print(f"  - {f['path']} ({f['size_human']})")

    # Identify large unused files that might be important
    print("\n" + "=" * 80)
    print("LARGEST UNUSED FILES (may contain important code):")
    print("=" * 80)

    large_files = [f for f in data["unused_files"] if f["size_bytes"] > 50000]
    large_files.sort(key=lambda x: x["size_bytes"], reverse=True)

    for i, file_info in enumerate(large_files[:20]):
        print(f"{i+1}. {file_info['path']}")
        print(f"   Size: {file_info['size_human']}")

        # Add context about what it might be
        path_lower = file_info["path"].lower()
        if "test" in path_lower:
            print("   Type: Test file")
        elif "example" in path_lower or "demo" in path_lower:
            print("   Type: Example/Demo")
        elif "backup" in path_lower or "old" in path_lower:
            print("   Type: Possibly old/backup")
        else:
            print("   Type: ⚠️  Potentially important implementation")


if __name__ == "__main__":
    main()
