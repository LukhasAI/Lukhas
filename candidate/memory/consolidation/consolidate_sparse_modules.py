#!/usr/bin/env python3
"""

#TAG:memory
#TAG:consolidation
#TAG:neuroplastic
#TAG:colony


LUKHAS Sparse Module Consolidator
Consolidates sparse modules according to the standardization plan
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

# Consolidation mapping from the plan
CONSOLIDATION_MAP = {
    "red_team": {
        "target": "security",
        "subdirectory": "red_team",
        "description": "Red team security testing",
    },
    "meta": {
        "target": "config",
        "subdirectory": "meta",
        "description": "Meta-configuration and settings",
    },
    "trace": {
        "target": "governance",
        "subdirectory": "audit_trails",
        "description": "System audit trails and tracing",
    },
}


def backup_directory(source_path: Path, backup_base: Path = Path("backups")):
    """Create backup before consolidation"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_base / f"consolidation_backup_{timestamp}" / source_path.name

    if source_path.exists():
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, backup_path)
        print(f"📦 Backed up {source_path.name} to {backup_path}")
        return backup_path
    return None


def count_files(directory: Path) -> tuple[int, list[str]]:
    """Count files and list them"""
    files = []
    for path in directory.rglob("*"):
        if path.is_file() and not path.name.startswith("."):
            files.append(str(path.relative_to(directory)))
    return len(files), files


def consolidate_module(source_name: str, base_path: Path = Path(".")):
    """Consolidate a sparse module into its target"""
    if source_name not in CONSOLIDATION_MAP:
        print(f"❌ Unknown module: {source_name}")
        return False

    config = CONSOLIDATION_MAP[source_name]
    source_path = base_path / source_name
    target_path = base_path / config["target"]
    target_subdir = target_path / config["subdirectory"]

    # Check if source exists
    if not source_path.exists():
        print(f"⚠️  Source module '{source_name}' not found at {source_path}")
        return False

    # Count files
    file_count, file_list = count_files(source_path)
    print(f"\n📊 Module: {source_name}")
    print(f"   Files: {file_count}")
    print(f"   Target: {config['target']}/{config['subdirectory']}")

    # Create backup
    backup_directory(source_path)

    # Ensure target directory exists
    target_path.mkdir(exist_ok=True)

    # Move files to target subdirectory
    if file_count > 0:
        target_subdir.mkdir(parents=True, exist_ok=True)

        # Create README in subdirectory
        readme_content = f"""# {source_name.title()} Module (Consolidated)

## Overview
{config["description"]}

## Original Location
This module was consolidated from `/{source_name}/` into `/{config["target"]}/{config["subdirectory"]}/`

## Files
"""
        for file in file_list:
            readme_content += f"- {file}\n"

        readme_path = target_subdir / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)

        # Move all files
        for item in source_path.iterdir():
            if item.is_file():
                shutil.move(str(item), str(target_subdir / item.name))
            elif item.is_dir() and not item.name.startswith("."):
                target_dir = target_subdir / item.name
                if target_dir.exists():
                    # Merge directories
                    for subitem in item.rglob("*"):
                        if subitem.is_file():
                            relative_path = subitem.relative_to(item)
                            target_file = target_dir / relative_path
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(subitem), str(target_file))
                else:
                    shutil.move(str(item), str(target_dir))

        # Remove empty source directory
        shutil.rmtree(source_path)

        print(
            f"✅ Consolidated {source_name} → {config['target']}/{config['subdirectory']}"
        )

        # Update __init__.py in target module if it exists
        init_file = target_path / "__init__.py"
        if init_file.exists():
            with open(init_file, "a") as f:
                f.write("\n")
                f.write(f"from .{config['subdirectory']} import *\n")
    else:
        print(f"⚠️  No files to consolidate in {source_name}")
        # Still remove empty directory
        if source_path.exists():
            source_path.rmdir()

    return True


def update_imports(base_path: Path = Path(".")):
    """Update imports after consolidation"""
    print("\n🔧 Updating imports...")

    updates_made = 0
    import_map = {
        "from red_team": "from security.red_team",
        "import red_team": "import security.red_team",
        "from meta": "from config.meta",
        "import meta": "import config.meta",
        "from trace": "from lukhas.governance.audit_trails",
        "import trace": "import lukhas.governance.audit_trails",
    }

    # Find Python files
    for py_file in base_path.rglob("*.py"):
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if "backup" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            original_content = content

            # Update imports
            for old_import, new_import in import_map.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    updates_made += 1

            # Write back if changed
            if content != original_content:
                py_file.write_text(content)
                print(f"   Updated: {py_file.relative_to(base_path)}")

        except Exception as e:
            print(f"   ⚠️  Error updating {py_file}: {e}")

    print(f"✅ Updated {updates_made} import statements")


def generate_consolidation_report(base_path: Path = Path(".")):
    """Generate a report of the consolidation"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "consolidations": {},
        "summary": {"modules_consolidated": 0, "files_moved": 0, "imports_updated": 0},
    }

    for source_name, config in CONSOLIDATION_MAP.items():
        target_subdir = base_path / config["target"] / config["subdirectory"]
        if target_subdir.exists():
            file_count, file_list = count_files(target_subdir)
            report["consolidations"][source_name] = {
                "target": f"{config['target']}/{config['subdirectory']}",
                "file_count": file_count,
                "files": file_list,
            }
            report["summary"]["modules_consolidated"] += 1
            report["summary"]["files_moved"] += file_count

    # Save report
    report_path = base_path / "docs" / "reports" / "consolidation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_path}")
    return report


def main():
    """Main consolidation process"""
    print(
        """
╔═══════════════════════════════════════════════════════╗
║        LUKHAS Sparse Module Consolidator v1.0         ║
║                                                       ║
║  Consolidating: red_team → security                   ║
║                 meta → config                         ║
║                 trace → governance                    ║
╚═══════════════════════════════════════════════════════╝
    """
    )

    base_path = Path(".")

    # Check current state
    print("\n📍 Current state:")
    for module in CONSOLIDATION_MAP:
        module_path = base_path / module
        if module_path.exists():
            file_count, _ = count_files(module_path)
            print(f"   {module}: {file_count} files")
        else:
            print(f"   {module}: Not found")

    # Ask for confirmation
    response = input("\n🤔 Proceed with consolidation? (y/N): ")
    if response.lower() != "y":
        print("❌ Consolidation cancelled")
        return

    # Perform consolidation
    print("\n🚀 Starting consolidation...")
    success_count = 0

    for module in CONSOLIDATION_MAP:
        if consolidate_module(module, base_path):
            success_count += 1

    # Update imports
    if success_count > 0:
        update_imports(base_path)

    # Generate report
    report = generate_consolidation_report(base_path)

    # Summary
    print("\n✅ Consolidation complete!")
    print(f"   Modules consolidated: {report['summary']['modules_consolidated']}")
    print(f"   Files moved: {report['summary']['files_moved']}")
    print("   Backups created in: backups/")

    print("\n📋 Next steps:")
    print("   1. Review the consolidation report")
    print("   2. Test the affected modules")
    print("   3. Update any documentation")
    print("   4. Remove backups when confirmed working")


if __name__ == "__main__":
    main()
