#!/usr/bin/env python3
"""
Core Module Import Testing - Test all 344 core modules for import capability

This script systematically tests every Python module in the core directory
to determine which are functional, which have errors, and what dependencies exist.
"""

import importlib.util
import sys
import time
import traceback
from pathlib import Path
from typing import List, Tuple


def test_module_import(module_path: Path) -> Tuple[bool, str, List[str]]:
    """
    Test if a module can be imported successfully

    Returns:
        (success, error_message, dependencies)
    """
    try:
        # Create module spec
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        if spec is None:
            return False, "Could not create module spec", []

        # Create and load module
        module = importlib.util.module_from_spec(spec)

        # Add core directory to path for relative imports
        core_path = str(module_path.parent.parent / "core")
        if core_path not in sys.path:
            sys.path.insert(0, core_path)

        spec.loader.exec_module(module)

        # Try to identify dependencies by checking imports
        dependencies = []
        try:
            module_content = module_path.read_text()
            lines = module_content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    dependencies.append(line)
        except:
            pass

        return True, "Success", dependencies

    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        return False, error_msg, []


def analyze_core_modules():
    """Analyze all core modules and generate status report"""

    print("🔍 **Core Module Import Analysis**")
    print("Testing all 344 Python modules in /core/ directory...")
    print("=" * 60)

    core_dir = Path("core")
    if not core_dir.exists():
        print("❌ Core directory not found!")
        return

    # Find all Python files
    py_files = list(core_dir.rglob("*.py"))
    total_files = len(py_files)

    print(f"📊 Found {total_files} Python files")
    print()

    # Test each module
    results = {
        "working": [],
        "broken": [],
        "dependencies": {},
        "categories": {
            "actor_system": [],
            "colonies": [],
            "integration": [],
            "symbolic": [],
            "networking": [],
            "monitoring": [],
            "other": [],
        },
    }

    success_count = 0

    for i, py_file in enumerate(py_files):
        print(
            f"Testing [{i+1}/{total_files}] {py_file.relative_to(core_dir)}", end="..."
        )

        success, error, deps = test_module_import(py_file)

        if success:
            print(" ✅")
            results["working"].append(str(py_file.relative_to(core_dir)))
            success_count += 1
        else:
            print(" ❌")
            results["broken"].append(
                {"file": str(py_file.relative_to(core_dir)), "error": error}
            )

        results["dependencies"][str(py_file.relative_to(core_dir))] = deps

        # Categorize module
        file_str = str(py_file).lower()
        if "actor" in file_str or "event" in file_str:
            results["categories"]["actor_system"].append(
                str(py_file.relative_to(core_dir))
            )
        elif "colon" in file_str:
            results["categories"]["colonies"].append(str(py_file.relative_to(core_dir)))
        elif "integrat" in file_str or "hub" in file_str:
            results["categories"]["integration"].append(
                str(py_file.relative_to(core_dir))
            )
        elif "symbolic" in file_str or "contract" in file_str:
            results["categories"]["symbolic"].append(str(py_file.relative_to(core_dir)))
        elif "net" in file_str or "client" in file_str:
            results["categories"]["networking"].append(
                str(py_file.relative_to(core_dir))
            )
        elif "monitor" in file_str or "trace" in file_str:
            results["categories"]["monitoring"].append(
                str(py_file.relative_to(core_dir))
            )
        else:
            results["categories"]["other"].append(str(py_file.relative_to(core_dir)))

    # Generate report
    print()
    print("=" * 60)
    print("📊 **CORE MODULE ANALYSIS RESULTS**")
    print("=" * 60)

    success_rate = (success_count / total_files * 100) if total_files > 0 else 0

    print(
        f"✅ **Working Modules**: {success_count}/{total_files} ({success_rate:.1f}%)"
    )
    print(f"❌ **Broken Modules**: {len(results['broken'])}")
    print()

    print("📋 **Working Modules by Category:**")
    for category, modules in results["categories"].items():
        working_in_category = [m for m in modules if m in results["working"]]
        if working_in_category:
            print(
                f"  🟢 {category.replace('_', ' ').title()}: {len(working_in_category)} modules"
            )
            for module in working_in_category[:3]:  # Show first 3
                print(f"    - {module}")
            if len(working_in_category) > 3:
                print(f"    ... and {len(working_in_category) - 3} more")
        print()

    print("🔧 **Common Error Patterns:**")
    error_patterns = {}
    for broken in results["broken"]:
        error_type = (
            broken["error"].split(":")[0]
            if ":" in broken["error"]
            else broken["error"][:50]
        )
        error_patterns[error_type] = error_patterns.get(error_type, 0) + 1

    for error, count in sorted(
        error_patterns.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"  ❌ {error}: {count} modules")

    print()
    print("🎯 **Immediate Actionable Modules:**")
    print("These modules imported successfully and are ready for testing:")

    priority_modules = [
        "minimal_actor.py",
        "event_bus.py",
        "task_manager.py",
        "swarm.py",
        "integration_hub.py",
        "integrated_system.py",
    ]

    for module in priority_modules:
        if module in results["working"]:
            print(f"  ✅ {module} - Ready for activation testing")
        else:
            # Find the broken entry
            broken_entry = next(
                (b for b in results["broken"] if module in b["file"]), None
            )
            if broken_entry:
                print(f"  ❌ {module} - Error: {broken_entry['error'][:60]}...")
            else:
                print(f"  ⚠️ {module} - Not found")

    print()
    print("🚀 **Next Steps:**")
    print("1. Focus on working modules for immediate activation")
    print("2. Fix common error patterns in broken modules")
    print("3. Test functionality of priority working modules")
    print("4. Document dependencies and integration points")

    # Save detailed results
    import json

    with open("core_module_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Detailed results saved to core_module_analysis.json")

    return results


def main():
    """Run core module analysis"""
    start_time = time.time()

    print("🎯 **LUKHAS AI Core Module Analysis**")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        results = analyze_core_modules()

        elapsed = time.time() - start_time
        print(f"\n⏱️ Analysis completed in {elapsed:.2f} seconds")

        return results

    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
    main()
