#!/usr/bin/env python3
"""
Execute the directory reorganization plan
Moves directories into appropriate modules and archives others
"""
from consciousness.qi import qi
import streamlit as st
from datetime import timezone

import json
import os
import shutil
from datetime import datetime


class DirectoryReorganizer:
    def __init__(self):
        # Directory mappings from audit
        self.moves = {
            # Directories to move into modules
            "api": "bridge/api_legacy",
            "architectures": "core/architectures",
            "bio": "qim/bio_legacy",
            "creativity": "consciousness/creativity",
            "dream": "consciousness/dream",
            "ethics": "governance/ethics_legacy",
            "identity": "governance/identity",
            "learning": "memory/learning",
            "orchestration": "core/orchestration",
            "reasoning": "consciousness/reasoning",
            "symbolic": "core/symbolic_core",
            "voice": "bridge/voice",
        }

        # Directories to archive
        self.archive = [
            "health_reports",
            "misc",
            "quarantine",
            "security",
            "trace",
            "_context_",
        ]

        # Tool consolidation
        self.tool_moves = {
            "analysis_tools": "tools/legacy_analysis",
            "healing": "tools/healing",
        }

        self.moved_count = 0
        self.archived_count = 0
        self.errors = []

    def move_directory(self, source, target):
        """Move a directory to target location"""
        try:
            if os.path.exists(source):
                # Create target directory if needed
                os.makedirs(os.path.dirname(target), exist_ok=True)

                # Check if target exists
                if os.path.exists(target):
                    # Rename with timestamp
                    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                    target = f"{target}_{timestamp}"

                # Move directory
                shutil.move(source, target)
                print(f"  ✅ Moved {source} → {target}")
                self.moved_count += 1
                return True
            else:
                print(f"  ⚠️  Source not found: {source}")
                return False
        except Exception as e:
            self.errors.append(f"Failed to move {source}: {e!s}")
            print(f"  ❌ Error moving {source}: {e}")
            return False

    def archive_directory(self, directory):
        """Archive a directory"""
        archive_base = "archive"
        os.makedirs(archive_base, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        archive_path = f"{archive_base}/{timestamp}/{directory}"

        try:
            if os.path.exists(directory):
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                shutil.move(directory, archive_path)
                print(f"  📦 Archived {directory} → {archive_path}")
                self.archived_count += 1

                # Create archive note
                note_path = f"{archive_path}/ARCHIVE_NOTE.txt"
                with open(note_path, "w") as f:
                    f.write(f"Archived from: {directory}\n")
                    f.write(f"Archive date: {datetime.now(timezone.utc).isoformat(}\n")
                    f.write("Reason: Unclear purpose or temporary directory\n")

                return True
            else:
                print(f"  ⚠️  Directory not found: {directory}")
                return False
        except Exception as e:
            self.errors.append(f"Failed to archive {directory}: {e!s}")
            print(f"  ❌ Error archiving {directory}: {e}")
            return False

    def update_module_manifest(self, module, new_subdirs):
        """Update module manifest with new directories"""
        manifest_path = f"{module}/MODULE_MANIFEST.json"

        try:
            if os.path.exists(manifest_path):
                with open(manifest_path) as f:
                    manifest = json.load(f)

                # Add new integrated directories
                if "integrated_directories" not in manifest:
                    manifest["integrated_directories"] = []

                manifest["integrated_directories"].extend(new_subdirs)
                manifest["last_reorganization"] = datetime.now(timezone.utc).isoformat()

                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=2)

                print(f"  📝 Updated {module} manifest")
        except Exception as e:
            print(f"  ⚠️  Could not update manifest: {e}")

    def create_import_migration_guide(self):
        """Create a guide for updating imports"""
        guide = """# Import Migration Guide

After the directory reorganization, update imports as follows:

## Module Moves

### From root to core module:
```python
# OLD
from architectures import something
from orchestration import something
from symbolic import something

# NEW
from core.architectures import something
from core.orchestration import something
from core.symbolic_core import something
```

### From root to consciousness module:
```python
# OLD
from creativity import something
from dream import something
from reasoning import something

# NEW
from lukhas.consciousness.creativity import something
from lukhas.consciousness.dream import something
from lukhas.consciousness.reasoning import something
```

### From root to other modules:
```python
# OLD
from api import something
from bio import something
from ethics import something
from identity import something
from learning import something
from voice import something

# NEW
from lukhas.bridge.api_legacy import something
from lukhas.qi.bio_legacy import something
from lukhas.governance.ethics_legacy import something
from lukhas.governance.identity import something
from lukhas.memory.learning import something
from lukhas.bridge.voice import something
```

## Archived Directories

The following directories have been archived and should not be imported:
- health_reports
- misc
- quarantine
- security
- trace
- _context_

## Tools Consolidation

```python
# OLD
from analysis_tools import something
from healing import something

# NEW
from tools.legacy_analysis import something
from tools.healing import something
```

## Automated Import Update

Run this command to find all files needing import updates:
```bash
grep -r "from \\(api\\|architectures\\|bio\\|creativity\\|dream\\|ethics\\|identity\\|learning\\|orchestration\\|reasoning\\|symbolic\\|voice\\) import" . --include="*.py"
```
"""

        with open("docs/IMPORT_MIGRATION_GUIDE.md", "w") as f:
            f.write(guide)

        print("\n📋 Created import migration guide: docs/IMPORT_MIGRATION_GUIDE.md")

    def execute(self):
        """Execute the reorganization"""
        print("🚀 EXECUTING DIRECTORY REORGANIZATION")
        print("=" * 50)

        # Step 1: Move directories into modules
        print("\n📁 Moving directories into modules...")
        modules_updated = set()

        for source, target in self.moves.items():
            if self.move_directory(source, target):
                module = target.split("/")[0]
                modules_updated.add(module)

        # Update manifests
        for module in modules_updated:
            integrated = [d.split("/")[-1] for s, d in self.moves.items() if d.startswith(module)]
            self.update_module_manifest(module, integrated)

        # Step 2: Archive directories
        print("\n📦 Archiving temporary/unclear directories...")
        for directory in self.archive:
            self.archive_directory(directory)

        # Step 3: Consolidate tools
        print("\n🔧 Consolidating tool directories...")
        for source, target in self.tool_moves.items():
            self.move_directory(source, target)

        # Step 4: Create import migration guide
        self.create_import_migration_guide()

        # Summary
        print("\n" + "=" * 50)
        print("✅ REORGANIZATION COMPLETE!")
        print(f"  - Moved: {self.moved_count} directories")
        print(f"  - Archived: {self.archived_count} directories")
        print(f"  - Errors: {len(self.errors}")

        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors:
                print(f"  - {error}")

        # Create summary report
        self.create_summary_report()

    def create_summary_report(self):
        """Create reorganization summary"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "directories_moved": self.moved_count,
            "directories_archived": self.archived_count,
            "errors": self.errors,
            "moves_completed": {k: v for k, v in self.moves.items() if not os.path.exists(k)},
            "archives_completed": [d for d in self.archive if not os.path.exists(d)],
            "next_steps": [
                "Update imports using IMPORT_MIGRATION_GUIDE.md",
                "Run tests for each module",
                "Remove any remaining empty directories",
                "Update documentation",
            ],
        }

        report_path = "docs/reports/REORGANIZATION_SUMMARY.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Summary report: {report_path}")


def main():
    print("⚠️  WARNING: This will move many directories!")
    print("Current working directory:", os.getcwd())
    print("\nDirectories to be moved into modules:")
    print("  - api → bridge/api_legacy")
    print("  - architectures → core/architectures")
    print("  - bio → qim/bio_legacy")
    print("  - creativity → consciousness/creativity")
    print("  - dream → consciousness/dream")
    print("  - ethics → governance/ethics_legacy")
    print("  - identity → governance/identity")
    print("  - learning → memory/learning")
    print("  - orchestration → core/orchestration")
    print("  - reasoning → consciousness/reasoning")
    print("  - symbolic → core/symbolic_core")
    print("  - voice → bridge/voice")

    print("\nDirectories to be archived:")
    print("  - health_reports, misc, quarantine, security, trace, _context_")

    response = input("\nProceed with reorganization? (yes/no): ")

    if response.lower() == "yes":
        reorganizer = DirectoryReorganizer()
        reorganizer.execute()
    else:
        print("❌ Reorganization cancelled")


if __name__ == "__main__":
    main()
