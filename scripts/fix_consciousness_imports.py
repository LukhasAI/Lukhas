#!/usr/bin/env python3
"""
Systematically fix test imports for consciousness modules.

Transforms imports from:
  - consciousness.* → labs.consciousness.*
"""

import re
import sys
from pathlib import Path

# Files to fix (from the grep results)
TEST_FILES = [
    "tests/unit/candidate/consciousness/dream/test_dream_feedback_controller.py",
    "tests/benchmarks/test_mesh.py",
    "tests/soak/test_guardian_matriz_throughput.py",
    "tests/matriz/test_e2e_perf.py",
    "tests/consciousness/test_lukhas_reflection_engine.py",
    "tests/consciousness/test_advanced_cognitive_features.py",
    "tests/consciousness/simulation/test_simulation_lane.py",
    "tests/consciousness/test_reflection_engine.py",
    "tests/consciousness/test_creativity_engine.py",
    "tests/consciousness/test_guardian_integration.py",
    "tests/integration/test_orchestrator_matriz_roundtrip.py",
    "tests/integration/test_matriz_complete_thought_loop.py",
    "tests/integration/test_full_system_integration.py",
    "tests/cognitive/stress/test_cognitive_load_infrastructure.py",
    "tests/cognitive/property_based/test_reasoning_edge_cases.py",
    "tests/cognitive/test_comprehensive_coverage.py",
    "tests/unit/dream/test_evolution.py",
    "tests/unit/dream/test_resonance.py",
    "tests/unit/dream/test_noise.py",
    "tests/unit/dream/expand/test_archetypes.py",
    "tests/unit/dream/expand/test_sentinel.py",
    "tests/unit/dream/expand/test_atlas.py",
    "tests/unit/dream/expand/test_replay.py",
    "tests/unit/dream/expand/test_mediation.py",
    "tests/unit/test_awareness_protocol.py",
    "tests/unit/consciousness/test_core_integrator_access_tier.py",
    "tests/unit/consciousness/test_ethical_drift_sentinel.py",
    "tests/unit/consciousness/test_awareness_log_synchronizer.py",
    "tests/unit/consciousness/test_circuit_breakers.py",
]


def fix_imports_in_file(file_path: Path) -> tuple[bool, list[str]]:
    """
    Fix consciousness imports in a single file.

    Returns:
        (success, changes) - success flag and list of changes made
    """
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    try:
        content = file_path.read_text()
        original_content = content
        changes = []

        # Pattern 1: from consciousness.X import Y
        pattern1 = r'^(\s*)from consciousness\.([^\s]+) import (.+)$'
        def replace1(match):
            indent = match.group(1)
            module_path = match.group(2)
            imports = match.group(3)
            new_line = f"{indent}from labs.consciousness.{module_path} import {imports}"
            changes.append(f"  {match.group(0).strip()} → {new_line.strip()}")
            return new_line

        content = re.sub(pattern1, replace1, content, flags=re.MULTILINE)

        # Pattern 2: import consciousness.X
        pattern2 = r'^(\s*)import consciousness\.([^\s]+)$'
        def replace2(match):
            indent = match.group(1)
            module_path = match.group(2)
            new_line = f"{indent}import labs.consciousness.{module_path}"
            changes.append(f"  {match.group(0).strip()} → {new_line.strip()}")
            return new_line

        content = re.sub(pattern2, replace2, content, flags=re.MULTILINE)

        # Pattern 3: Special case for mock paths like 'consciousness.reflection_engine.tracer'
        pattern3 = r"'consciousness\.([^']+)'"
        def replace3(match):
            module_path = match.group(1)
            new_text = f"'labs.consciousness.{module_path}'"
            if new_text != f"'consciousness.{module_path}'":
                changes.append(f"  'consciousness.{module_path}' → {new_text}")
            return new_text

        content = re.sub(pattern3, replace3, content)

        if content != original_content:
            file_path.write_text(content)
            return True, changes
        else:
            return True, ["No changes needed"]

    except Exception as e:
        return False, [f"Error: {e}"]


def main():
    """Fix all test files with consciousness import issues."""
    repo_root = Path(__file__).parent.parent

    print("🔧 Fixing consciousness imports in test files...")
    print(f"Repository root: {repo_root}\n")

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for test_file in TEST_FILES:
        file_path = repo_root / test_file
        print(f"\n📝 Processing: {test_file}")

        success, changes = fix_imports_in_file(file_path)

        if success:
            if changes and changes[0] != "No changes needed":
                print("✅ Fixed imports:")
                for change in changes:
                    print(change)
                success_count += 1
            else:
                print("⏭️  No changes needed")
                skipped_count += 1
        else:
            print(f"❌ Failed:")
            for msg in changes:
                print(f"  {msg}")
            failed_count += 1

    print("\n" + "="*70)
    print(f"📊 Summary:")
    print(f"  ✅ Successfully fixed: {success_count}")
    print(f"  ⏭️  Skipped (no changes): {skipped_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📁 Total files: {len(TEST_FILES)}")

    if failed_count > 0:
        sys.exit(1)

    print("\n🎉 All imports fixed successfully!")


if __name__ == "__main__":
    main()
