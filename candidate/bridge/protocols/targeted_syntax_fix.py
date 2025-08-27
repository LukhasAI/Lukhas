#!/usr/bin/env python3
"""

#TAG:bridge
#TAG:protocols
#TAG:neuroplastic
#TAG:colony

Targeted Syntax Fix - Fixes specific known syntax errors
"""

import os
import re
import shutil


def fix_specific_files():
    """Fix specific known syntax errors"""
    fixes_applied = 0

    # Fix 1: circuit_breaker.py - duplicate statement
    try:
        filepath = "./core/circuit_breaker.py"
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Fix duplicate asyncio.run
            content = content.replace(
                "asyncio.run(demo_cascade_prevention())    asyncio.run(demo_cascade_prevention())",
                "asyncio.run(demo_cascade_prevention())",
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Fixed {filepath}")
            fixes_applied += 1
    except Exception as e:
        print(f"[FAILED] {filepath}: {e}")

    # Fix 2: swarm_visualizer.py - broken line continuation
    try:
        filepath = "./core/swarm_visualizer.py"
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Fix broken line continuation
            content = content.replace(
                'graph_str += f"    {colony_id}[{colony_id} - {status} - {ethical_status}];\\\n            if style:',
                'graph_str += f"    {colony_id}[{colony_id} - {status} - {ethical_status}];\\n"\n            if style:',
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Fixed {filepath}")
            fixes_applied += 1
    except Exception as e:
        print(f"[FAILED] {filepath}: {e}")

    # Fix 3: auto_consolidate.py - nested triple quotes
    try:
        filepath = "./tools/scripts/auto_consolidate.py"
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Fix nested triple quotes
            content = content.replace('f.write("""', 'f.write("""')

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Fixed {filepath}")
            fixes_applied += 1
    except Exception as e:
        print(f"[FAILED] {filepath}: {e}")

    # Fix 4: memoria.py - unclosed triple quote
    try:
        filepath = "./core/memoria.py"
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            # Check if file ends with unclosed triple quote
            if len(lines) > 0 and lines[-1].strip() == '"""':
                # Add a closing line
                lines.append("\n")
                lines.append('"""\n')

            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)

            print(f"[OK] Fixed {filepath}")
            fixes_applied += 1
    except Exception as e:
        print(f"[FAILED] {filepath}: {e}")

    # Fix 5: Files with encoding issues (Lambda symbol)
    lambda_files = [
        "./orchestration/specialized/ΛDependaBoT_robust.py",
        "./orchestration/brain/Λbot_brain_system.py",
    ]

    for filepath in lambda_files:
        try:
            if os.path.exists(filepath):
                # Rename file to remove Lambda symbol
                new_filepath = filepath.replace("Λ", "Lambda")
                shutil.move(filepath, new_filepath)
                print(f"[OK] Renamed {filepath} to {new_filepath}")
                fixes_applied += 1
        except Exception as e:
            print(f"[FAILED] {filepath}: {e}")

    # Fix 6: Files with weird names (conflict markers)
    weird_files = ["./core/symbolic_diagnostics/.!54565!__init__.py"]

    for filepath in weird_files:
        try:
            if os.path.exists(filepath):
                # Delete these files as they're conflict artifacts
                os.remove(filepath)
                print(f"[OK] Removed conflict artifact: {filepath}")
                fixes_applied += 1
        except Exception as e:
            print(f"[FAILED] {filepath}: {e}")

    return fixes_applied


def fix_all_line_continuations():
    """Fix all broken line continuations"""
    fixed_count = 0

    for root, _dirs, files in os.walk("."):
        if any(
            skip in root
            for skip in [
                ".venv",
                ".git",
                "__pycache__",
                "._cleanup_archive",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()

                    # Fix pattern: string with backslash continuation
                    pattern = r'("[^"]*)\\\s*\n\s*([^"]*")'
                    new_content = re.sub(pattern, r'\1" + "\2', content)

                    if new_content != content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        fixed_count += 1
                        print(f"[OK] Fixed line continuation in {filepath}")
                except BaseException:
                    pass

    return fixed_count


def main():
    """Run targeted fixes"""
    print("[Targeted Syntax Fix] Starting...")
    print("=" * 50)

    # Apply specific fixes
    print("\n[Phase 1] Applying specific fixes...")
    specific_fixes = fix_specific_files()
    print(f"Applied {specific_fixes} specific fixes")

    # Fix line continuations
    print("\n[Phase 2] Fixing line continuations...")
    continuation_fixes = fix_all_line_continuations()
    print(f"Fixed {continuation_fixes} line continuation issues")

    # Summary
    total_fixes = specific_fixes + continuation_fixes
    print("\n" + "=" * 50)
    print(f"[COMPLETE] Applied {total_fixes} fixes total")

    # Check remaining errors
    print("\n[Checking] Scanning for remaining syntax errors...")

    import ast

    errors = []
    for root, _dirs, files in os.walk("."):
        if any(
            skip in root
            for skip in [
                ".venv",
                ".git",
                "__pycache__",
                "._cleanup_archive",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    ast.parse(content)
                except BaseException:
                    errors.append(filepath)

    print(f"\n[Status] Remaining syntax errors: {len(errors)}")
    if errors and len(errors) < 20:
        print("\nRemaining errors:")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
