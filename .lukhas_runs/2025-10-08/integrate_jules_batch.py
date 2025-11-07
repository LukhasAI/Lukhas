#!/usr/bin/env python3
"""
Jules Batch Integration Script
Safely maps and integrates recovered Jules files into the repository.
"""
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

# Repository root
REPO_ROOT = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
JULES_DOWNLOAD = Path("/Users/agi_dev/Downloads/BATCH-JULES-2025-10-08-01")

# File mapping rules based on BATCH-JULES-2025-10-08-01.json tasks
FILE_MAPPING = {
    # API implementation files
    "openai_modulated_service.py": "candidate/bridge/llm_wrappers/openai_modulated_service.py",

    # Governance files
    "auth_glyph_registry.py": "candidate/governance/auth_glyph_registry.py",

    # Adapter files (candidate/bridge/adapters or matriz/adapters)
    "bio_adapter.py": "matriz/adapters/bio_adapter.py",
    "bridge_adapter.py": "matriz/adapters/bridge_adapter.py",
    "compliance_adapter.py": "matriz/adapters/compliance_adapter.py",
    "consciousness_adapter.py": "matriz/adapters/consciousness_adapter.py",
    "contradiction_adapter.py": "matriz/adapters/contradiction_adapter.py",
    "creative_adapter.py": "matriz/adapters/creative_adapter.py",
    "emotion_adapter.py": "matriz/adapters/emotion_adapter.py",
    "governance_adapter.py": "matriz/adapters/governance_adapter.py",
    "identity_adapter.py": "matriz/adapters/identity_adapter.py",
    "memory_adapter.py": "matriz/adapters/memory_adapter.py",
    "orchestration_adapter.py": "matriz/adapters/orchestration_adapter.py",

    # Core files
    "fold_engine.py": "candidate/memory/fold_system/fold_engine.py",
    "cloud_consolidation.py": "candidate/core/cloud_consolidation.py",

    # Test files
    "test_adapters_integration.py": "tests/integration/matriz/test_adapters_integration.py",
    "test_adapters_unit.py": "tests/unit/matriz/test_adapters_unit.py",
    "test_crypto_hygiene.py": "tests/security/test_crypto_hygiene.py",
    "conftest.py": "tests/conftest.py",  # May need to merge with existing

    # __init__ files (need context to determine which module)
    "__init__.py": "matriz/adapters/__init__.py",
    "__init__-2.py": "candidate/bridge/api/__init__.py",
    "__init__-3.py": "candidate/governance/ethics/__init__.py",
    "__init__-4.py": "candidate/governance/security/__init__.py",
    "__init__-5.py": "candidate/governance/policy/__init__.py",
    "__init__-6.py": "candidate/governance/consent/__init__.py",

    # Documentation
    "api.md": "docs/examples/api.md",
    "architecture.md": "docs/examples/architecture.md",
    "troubleshooting.md": "docs/examples/troubleshooting.md",
    "lukhas_context.md": "matriz/adapters/lukhas_context.md",
    "README-2.md": "candidate/bridge/api/README.md",
    "README-3.md": "candidate/governance/ethics/README.md",
    "README-4.md": "candidate/governance/security/README.md",
    "README-5.md": "candidate/governance/policy/README.md",

    # Empty/placeholder files (skip these)
    "MATRIX_V3_README.md": None,
    "MATRIX_V3_SLIDES.md": None,
}


def analyze_files() -> tuple[list[str], list[str], list[str]]:
    """Analyze downloaded files and categorize them."""
    found_files = list(JULES_DOWNLOAD.glob("*"))

    mapped = []
    unmapped = []
    skipped = []

    for file_path in found_files:
        if file_path.is_dir():
            continue

        filename = file_path.name

        if filename in FILE_MAPPING:
            target = FILE_MAPPING[filename]
            if target is None:
                skipped.append(filename)
            else:
                mapped.append((filename, target))
        else:
            unmapped.append(filename)

    return mapped, unmapped, skipped


def check_conflicts(mapped_files: list[tuple[str, str]]) -> list[tuple[str, str, bool]]:
    """Check which target files already exist."""
    conflicts = []

    for source_name, target_rel_path in mapped_files:
        target_path = REPO_ROOT / target_rel_path
        exists = target_path.exists()
        conflicts.append((source_name, target_rel_path, exists))

    return conflicts


def create_backup(target_path: Path) -> Path:
    """Create backup of existing file."""
    backup_dir = REPO_ROOT / ".lukhas_runs/2025-10-08/backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    rel_path = target_path.relative_to(REPO_ROOT)
    backup_path = backup_dir / f"{rel_path.as_posix().replace('/', '_')}.bak"

    if target_path.exists():
        shutil.copy2(target_path, backup_path)
        print(f"  📦 Backed up: {rel_path} → {backup_path.name}")

    return backup_path


def integrate_file(source_name: str, target_rel_path: str, force: bool = False) -> bool:
    """Integrate a single file."""
    source_path = JULES_DOWNLOAD / source_name
    target_path = REPO_ROOT / target_rel_path

    # Create parent directory if needed
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing file
    if target_path.exists():
        create_backup(target_path)
        if not force:
            print(f"  ⚠️  File exists: {target_rel_path} (use --force to overwrite)")
            return False

    # Copy file
    shutil.copy2(source_path, target_path)
    print(f"  ✅ Integrated: {source_name} → {target_rel_path}")

    return True


def run_verification() -> tuple[bool, str]:
    """Run basic verification checks."""
    checks = []

    # Check imports
    print("\n🔍 Running verification checks...")

    try:
        result = subprocess.run(
            ["python", "-c", "import lukhas"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        import_ok = result.returncode == 0
        checks.append(("Import check", import_ok, result.stderr if not import_ok else ""))
    except Exception as e:
        checks.append(("Import check", False, str(e)))

    # Check ruff
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--quiet"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        ruff_ok = result.returncode == 0
        error_count = result.stdout.count("\n") if not ruff_ok else 0
        checks.append(("Ruff linting", ruff_ok, f"{error_count} errors" if not ruff_ok else ""))
    except Exception as e:
        checks.append(("Ruff linting", False, str(e)))

    # Print results
    all_ok = all(ok for _, ok, _ in checks)
    report = "\nVerification Results:\n"
    for check_name, ok, msg in checks:
        status = "✅" if ok else "❌"
        report += f"{status} {check_name}: {msg if msg else 'PASS'}\n"

    return all_ok, report


def main():
    """Main integration workflow."""
    print("🚀 Jules Batch Integration Script")
    print("=" * 60)

    # Analyze files
    print("\n📂 Analyzing recovered files...")
    mapped, unmapped, skipped = analyze_files()

    print(f"\nFound {len(mapped)} mapped files")
    print(f"Found {len(unmapped)} unmapped files")
    print(f"Found {len(skipped)} files to skip")

    if unmapped:
        print("\n⚠️  Unmapped files:")
        for name in unmapped:
            print(f"  - {name}")

    # Check conflicts
    print("\n🔍 Checking for conflicts...")
    conflicts = check_conflicts(mapped)

    existing_count = sum(1 for _, _, exists in conflicts if exists)
    new_count = len(mapped) - existing_count

    print(f"  {existing_count} files will be UPDATED (backups created)")
    print(f"  {new_count} files will be CREATED")

    # Show what will happen
    print("\n📋 Integration Plan:")
    for source_name, target_rel_path, exists in conflicts:
        action = "UPDATE" if exists else "CREATE"
        print(f"  {action:8} {source_name:30} → {target_rel_path}")

    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input("Proceed with integration? [y/N]: ").strip().lower()

    if response != 'y':
        print("❌ Integration cancelled")
        return

    # Integrate files
    print("\n🔧 Integrating files...")
    success_count = 0

    for source_name, target_rel_path in mapped:
        if integrate_file(source_name, target_rel_path, force=True):
            success_count += 1

    print(f"\n✅ Integrated {success_count}/{len(mapped)} files")

    # Run verification
    verification_ok, report = run_verification()
    print(report)

    if verification_ok:
        print("\n✅ All verification checks passed!")
        print("\nNext steps:")
        print("  1. Review changes: git status")
        print("  2. Run full tests: pytest tests/ -v")
        print("  3. Check lane boundaries: make lane-guard")
        print("  4. Create commit following T4 standard")
    else:
        print("\n⚠️  Some verification checks failed")
        print("Review the errors above before committing")

    print("\n💾 Backups saved to: .lukhas_runs/2025-10-08/backups/")


if __name__ == "__main__":
    main()
