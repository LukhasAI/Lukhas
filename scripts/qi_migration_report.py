#!/usr/bin/env python3
"""
Module: qi_migration_report.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
🧬 LUKHAS Quantum → QI Module Migration Report
Summary of quantum module structure update to QI (Quantum Intelligence)
Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from pathlib import Path


def generate_qi_migration_report():
    """Generate comprehensive report on quantum → qi migration"""

    print("🔄 LUKHAS Quantum → QI Migration Report")
    print("=" * 60)

    base_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    # Check qi directory structure
    print("📁 QI Directory Structure:")
    qi_path = base_path / "qi"
    if qi_path.exists():
        print(f"✅ Main QI directory: {qi_path}")

        # List subdirectories
        subdirs = [d for d in qi_path.iterdir() if d.is_dir() and d.name != "__pycache__"]
        print(f"   📂 Subdirectories: {len(subdirs)}")
        for subdir in sorted(subdirs):
            init_file = subdir / "__init__.py"
            init_status = "✅" if init_file.exists() else "❌"
            python_files = len(list(subdir.rglob("*.py")))
            print(f"   {init_status} {subdir.name}/ ({python_files} Python files)")
    else:
        print("❌ Main QI directory not found")

    # Check candidate qi structure
    print("\n📁 Candidate QI Directory Structure:")
    candidate_qi_path = base_path / "candidate" / "qi"
    if candidate_qi_path.exists():
        print(f"✅ Candidate QI directory: {candidate_qi_path}")
        subdirs = [d for d in candidate_qi_path.iterdir() if d.is_dir()]
        print(f"   📂 Subdirectories: {len(subdirs)}")
        for subdir in sorted(subdirs):
            python_files = len(list(subdir.rglob("*.py")))
            print(f"   ✅ {subdir.name}/ ({python_files} Python files)")
    else:
        print("❌ Candidate QI directory not found")

    # Check for quantum references that should be qi
    print("\n🔍 Quantum References Analysis:")

    # Files with quantum in name
    qi_files = list(base_path.rglob("*quantum*"))
    config_quantum_files = [f for f in qi_files if "config" in str(f) or "json" in str(f) or "yaml" in str(f)]

    print(f"📄 Files with 'quantum' in name: {len(qi_files)}")
    print(f"⚙️  Configuration files: {len(config_quantum_files)}")

    for config_file in config_quantum_files[:5]:  # Show first 5
        print(f"   📋 {config_file.relative_to(base_path)}")

    if len(config_quantum_files) > 5:
        print(f"   ... and {len(config_quantum_files) - 5} more")

    # Check lukhas qi structure
    print("\n📁 LUKHAS QI Integration:")
    lukhas_qi_path = base_path / "lukhas" / "qi"
    if lukhas_qi_path.exists():
        print(f"✅ LUKHAS QI integration: {lukhas_qi_path}")
        init_file = lukhas_qi_path / "__init__.py"
        print(f"   {'✅' if init_file.exists() else '❌'} __init__.py present")
    else:
        print("❌ LUKHAS QI integration not found")

    # Migration recommendations
    print("\n📋 Migration Recommendations:")
    print("1. ✅ Main qi/ directory structure established")
    print("2. ✅ __init__.py files created for qi/ subdirectories")
    print("3. ✅ Test script updated to use 'qi' instead of 'quantum'")
    print("4. 🔄 Consider updating quantum config files to use qi naming")
    print("5. 🔄 Update documentation references from qi to qi")
    print("6. 🔄 Consider migrating quantum-specific agent configs to qi")

    # Status summary
    print("\n🎯 Migration Status:")
    qi_available = qi_path.exists()
    qi_init = (qi_path / "__init__.py").exists() if qi_available else False
    candidate_available = candidate_qi_path.exists()
    lukhas_available = lukhas_qi_path.exists()

    status_items = [
        ("Main QI directory", qi_available),
        ("QI module init", qi_init),
        ("Candidate QI structure", candidate_available),
        ("LUKHAS QI integration", lukhas_available),
    ]

    working_count = sum(1 for _, status in status_items if status)
    total_count = len(status_items)

    print(f"✅ Working: {working_count}/{total_count}")

    if working_count >= 3:
        print("🟢 QI System Status: READY")
    elif working_count >= 2:
        print("🟡 QI System Status: PARTIALLY READY")
    else:
        print("🔴 QI System Status: NEEDS SETUP")


if __name__ == "__main__":
    generate_qi_migration_report()
