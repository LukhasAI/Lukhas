#!/usr/bin/env python3
"""
Interactive file mapping tool for Jules's batch.
Run this and paste the file mappings from screenshots.
"""
import json
from pathlib import Path

JULES_DOWNLOAD = Path("/Users/agi_dev/Downloads/BATCH-JULES-2025-10-08-01")

def main():
    print("🗺️  Jules File Mapping Tool")
    print("=" * 60)
    print("\nPaste file mappings in format: filename → target/path")
    print("Or: filename,target/path")
    print("Press Ctrl+D (or Ctrl+Z on Windows) when done\n")

    mappings = {}

    try:
        while True:
            line = input().strip()
            if not line:
                continue

            # Parse different formats
            if "→" in line:
                parts = line.split("→")
            elif "," in line:
                parts = line.split(",")
            elif "\t" in line:
                parts = line.split("\t")
            else:
                print(f"⚠️  Couldn't parse: {line}")
                continue

            if len(parts) != 2:
                print(f"⚠️  Invalid format: {line}")
                continue

            source = parts[0].strip()
            target = parts[1].strip()

            # Verify source file exists
            source_path = JULES_DOWNLOAD / source
            if not source_path.exists():
                print(f"⚠️  File not found: {source}")
                continue

            mappings[source] = target
            print(f"✅ Mapped: {source} → {target}")

    except EOFError:
        pass

    # Save mappings
    output_file = Path(".lukhas_runs/2025-10-08/jules_file_mappings.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(mappings, f, indent=2)

    print(f"\n💾 Saved {len(mappings)} mappings to: {output_file}")
    print("\nMappings:")
    for source, target in sorted(mappings.items()):
        print(f"  {source:40} → {target}")

if __name__ == "__main__":
    main()
