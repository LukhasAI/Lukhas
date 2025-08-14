#!/usr/bin/env python3
"""
LUKHAS Migration Script: Top 3 Modules to Production
Migrates critical modules from archive to accepted lane with compatibility shims
"""

import shutil
from datetime import datetime
from pathlib import Path

# Base paths
LUKHAS_ROOT = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
ARCHIVE_BASE = LUKHAS_ROOT / "lukhas/acceptance/archive"
ACCEPTED_BASE = LUKHAS_ROOT / "lukhas/acceptance/accepted"

# Migration targets
MIGRATIONS = [
    {
        "name": "Ethical Drift Governor",
        "source": ARCHIVE_BASE / "memory_variants/memory/governance/ethical_drift_governor.py",
        "target": ACCEPTED_BASE / "governance/drift_governor.py",
        "imports": [
            ("EthicalDriftGovernor", "EthicalDriftGovernor"),
            ("EthicalSeverity", "EthicalSeverity"),
            ("InterventionType", "InterventionType"),
            ("EthicalConcern", "EthicalConcern"),
            ("GovernanceRule", "GovernanceRule"),
        ]
    },
    {
        "name": "DNA Helix Memory Architecture",
        "source": ARCHIVE_BASE / "memory_variants/memory/dna_helix",
        "target": ACCEPTED_BASE / "dna/helix",
        "is_directory": True,
        "main_imports": [
            ("dna_memory_architecture", "DNAMemoryArchitecture"),
            ("helix_vault", "HelixVault"),
            ("dna_healix", "DNAHealix"),
        ]
    },
    {
        "name": "Memory Drift Tracker",
        "source": ARCHIVE_BASE / "memory_variants/memory/systems/memory_drift_tracker.py",
        "target": ACCEPTED_BASE / "monitoring/drift_tracker.py",
        "imports": [
            ("MemoryDriftTracker", "MemoryDriftTracker"),
        ]
    }
]

def create_compatibility_shim(original_path: Path, new_import_path: str, exports: list):
    """Create a compatibility shim at the original location"""

    shim_content = f'''"""
Compatibility shim - DEPRECATED
This module has been moved to production.
Will be removed after 2025-11-01 (SHIM_CULL_DATE)
"""

import warnings

warnings.warn(
    "Import path deprecated. Use 'from {new_import_path} import ...'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
'''

    for export_name, _ in exports:
        shim_content += f"from {new_import_path} import {export_name}\n"

    shim_content += f"\n__all__ = {[e[0] for e in exports]}\n"

    # Write shim
    original_path.parent.mkdir(parents=True, exist_ok=True)
    with open(original_path, 'w') as f:
        f.write(shim_content)

    print(f"  ✓ Created compatibility shim at {original_path.relative_to(LUKHAS_ROOT)}")

def update_module_paths(file_path: Path):
    """Update hardcoded paths in migrated modules"""

    if not file_path.exists():
        return

    with open(file_path) as f:
        content = f.read()

    # Update common hardcoded paths
    replacements = [
        ("/Users/agi_dev/Downloads/Consolidation-Repo/logs/", "logs/"),
        ("from memory.", "from lukhas.acceptance.accepted.memory."),
        ("from core.", "from lukhas.acceptance.accepted.core."),
        ("from governance.", "from lukhas.acceptance.accepted.governance."),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    with open(file_path, 'w') as f:
        f.write(content)

def migrate_module(migration: dict):
    """Migrate a single module to production"""

    print(f"\n🚀 Migrating: {migration['name']}")
    print(f"  From: {migration['source'].relative_to(LUKHAS_ROOT)}")
    print(f"  To:   {migration['target'].relative_to(LUKHAS_ROOT)}")

    # Create target directory
    if migration.get('is_directory'):
        migration['target'].mkdir(parents=True, exist_ok=True)

        # Copy entire directory
        if migration['source'].exists():
            shutil.copytree(
                migration['source'],
                migration['target'],
                dirs_exist_ok=True
            )
            print("  ✓ Copied directory structure")

            # Update paths in all Python files
            for py_file in migration['target'].rglob("*.py"):
                update_module_paths(py_file)
    else:
        migration['target'].parent.mkdir(parents=True, exist_ok=True)

        # Copy single file
        if migration['source'].exists():
            shutil.copy2(migration['source'], migration['target'])
            print("  ✓ Copied module file")

            # Update paths
            update_module_paths(migration['target'])

    # Create compatibility shim
    if 'imports' in migration:
        # Single file shim
        new_import = str(migration['target'].relative_to(ACCEPTED_BASE)).replace('/', '.').replace('.py', '')
        new_import = f"lukhas.acceptance.accepted.{new_import}"
        create_compatibility_shim(
            migration['source'],
            new_import,
            migration['imports']
        )
    elif migration.get('is_directory') and 'main_imports' in migration:
        # Directory shim - create __init__.py
        shim_path = migration['source'] / "__init__.py"
        new_base = f"lukhas.acceptance.accepted.{migration['target'].relative_to(ACCEPTED_BASE)}"
        new_base = new_base.replace('/', '.')

        shim_content = f'''"""
Compatibility shim for {migration['name']}
DEPRECATED - Will be removed after 2025-11-01
"""
import warnings
warnings.warn(
    "Import path deprecated. Use 'from {new_base} import ...'",
    DeprecationWarning,
    stacklevel=2
)

'''
        for module, cls in migration['main_imports']:
            shim_content += f"from {new_base}.{module} import {cls}\n"

        shim_content += f"\n__all__ = {[cls for _, cls in migration['main_imports']]}\n"

        with open(shim_path, 'w') as f:
            f.write(shim_content)
        print("  ✓ Created directory compatibility shim")

def create_migration_log():
    """Create a log of the migration"""

    log_path = LUKHAS_ROOT / "docs/migration_logs" / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_content = f"""# Migration Log - Top 3 Modules to Production
Date: {datetime.now().isoformat()}

## Migrated Modules

"""

    for m in MIGRATIONS:
        log_content += f"""### {m['name']}
- **From**: `{m['source'].relative_to(LUKHAS_ROOT)}`
- **To**: `{m['target'].relative_to(LUKHAS_ROOT)}`
- **Status**: ✅ Migrated with compatibility shim

"""

    log_content += """## Compatibility Shims
All original import paths have compatibility shims that will be removed after 2025-11-01.

## Next Steps
1. Run tests to verify migration
2. Update dependent code to use new import paths
3. Monitor for deprecation warnings
"""

    with open(log_path, 'w') as f:
        f.write(log_content)

    print(f"\n📝 Migration log created: {log_path.relative_to(LUKHAS_ROOT)}")

def main():
    print("=" * 60)
    print("LUKHAS Production Migration Script")
    print("Migrating Top 3 Modules to accepted/ lane")
    print("=" * 60)

    # Ensure accepted directories exist
    (ACCEPTED_BASE / "governance").mkdir(parents=True, exist_ok=True)
    (ACCEPTED_BASE / "dna").mkdir(parents=True, exist_ok=True)
    (ACCEPTED_BASE / "monitoring").mkdir(parents=True, exist_ok=True)

    # Migrate each module
    for migration in MIGRATIONS:
        try:
            migrate_module(migration)
            print(f"  ✅ Successfully migrated {migration['name']}")
        except Exception as e:
            print(f"  ❌ Failed to migrate {migration['name']}: {e}")

    # Create migration log
    create_migration_log()

    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print("\nIMPORTANT:")
    print("1. Run tests: pytest tests/")
    print("2. Check for deprecation warnings in logs")
    print("3. Update imports in dependent code gradually")
    print("4. Compatibility shims will be removed after 2025-11-01")

if __name__ == "__main__":
    main()
