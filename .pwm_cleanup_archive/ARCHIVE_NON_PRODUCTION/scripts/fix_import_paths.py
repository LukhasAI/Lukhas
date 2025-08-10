#!/usr/bin/env python3
"""
Fix relative import issues in core modules
"""

import os
import re

# List of files with relative import issues
FILES_TO_FIX = [
    "core/integrated_system.py",
    "core/actor_supervision_integration.py",
    "core/config_manager.py",
    "core/event_replayer.py",
    "core/consistency_manager.py",
    "core/demo_coordination.py",
    "core/test_event_replay_snapshot_simple.py",
    "core/audit_observer.py",
    "core/collaborative_tools.py",
    "core/context_analyzer.py",
    "core/coordination_agent.py",
    "core/coordination_v2.py",
    "core/direct_ai_router.py",
    "core/main.py",
    "core/plugin_loader.py",
    "core/real_config.py",
    "core/supervision.py",
    "core/test_enhanced_swarm.py",
    "core/test_event_bus.py",
    "core/test_event_sourcing.py",
    "core/test_swarm.py",
]

# Pattern to match relative imports
RELATIVE_IMPORT_PATTERN = re.compile(r"^from\s+\.([\w.]+)\s+import", re.MULTILINE)


def fix_relative_imports(file_path):
    """Fix relative imports in a Python file"""

    # Read the file
    with open(file_path) as f:
        content = f.read()

    # Track if we made changes
    original_content = content

    # Fix relative imports
    # Replace "from .module import" with "from core.module import"
    content = RELATIVE_IMPORT_PATTERN.sub(r"from core.\1 import", content)

    # Also fix "from .. import" patterns
    content = re.sub(
        r"^from\s+\.\.\s+import", "from core import", content, flags=re.MULTILINE
    )
    content = re.sub(
        r"^from\s+\.\.([\w.]+)\s+import", r"from \1 import", content, flags=re.MULTILINE
    )

    # If we made changes, write the file back
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def fix_no_module_imports(file_path):
    """Fix 'No module named core' errors"""

    # Read the file
    with open(file_path) as f:
        content = f.read()

    # Track if we made changes
    original_content = content

    # Fix imports like "from core import" when we're already in core
    # These should be relative imports or direct module imports
    content = re.sub(
        r"^from\s+core\s+import\s+([\w_]+)",
        r"from .\1 import \1",
        content,
        flags=re.MULTILINE,
    )

    # Fix imports like "from core.module import"
    # If we're in core/, these can be simplified
    content = re.sub(
        r"^from\s+core\.([\w_]+)\s+import",
        r"from .\1 import",
        content,
        flags=re.MULTILINE,
    )

    # If we made changes, write the file back
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    """Main function to fix import issues"""

    print("🔧 Fixing Import Path Issues")
    print("=" * 50)

    fixed_count = 0

    # Fix relative import issues
    print("\n📝 Fixing relative imports...")
    for file_path in FILES_TO_FIX:
        if os.path.exists(file_path):
            if fix_relative_imports(file_path):
                print(f"   ✅ Fixed: {file_path}")
                fixed_count += 1
            else:
                print(f"   ℹ️ No changes needed: {file_path}")
        else:
            print(f"   ⚠️ File not found: {file_path}")

    # Fix "No module named 'core'" issues
    print("\n📝 Fixing 'No module named core' errors...")
    no_module_files = [
        "core/swarm.py",
        "core/resource_scheduler.py",
        "core/resource_optimization_integration.py",
    ]

    for file_path in no_module_files:
        if os.path.exists(file_path):
            if fix_no_module_imports(file_path):
                print(f"   ✅ Fixed: {file_path}")
                fixed_count += 1
            else:
                print(f"   ℹ️ No changes needed: {file_path}")
        else:
            print(f"   ⚠️ File not found: {file_path}")

    # Fix the test_module issue in __init__.py
    init_file = "core/__init__.py"
    if os.path.exists(init_file):
        print(f"\n📝 Fixing {init_file}...")
        with open(init_file) as f:
            content = f.read()

        # Remove or comment out the test_module import
        content = re.sub(
            r"^from\s+test_module\s+import.*$",
            "# from test_module import ...  # Removed: module not found",
            content,
            flags=re.MULTILINE,
        )

        with open(init_file, "w") as f:
            f.write(content)
        print(f"   ✅ Fixed: {init_file}")
        fixed_count += 1

    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   - Files fixed: {fixed_count}")
    print(f"   - Total files checked: {len(FILES_TO_FIX) + len(no_module_files) + 1}")

    print("\n✅ Import path fixes complete!")
    print("   Next step: Run the module analyzer again to verify fixes")


if __name__ == "__main__":
    main()
