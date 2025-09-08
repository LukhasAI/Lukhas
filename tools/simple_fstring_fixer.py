#!/usr/bin/env python3
"""
Simple, Safe F-String Pattern Fixer

Targets the two most common patterns:
1. uuid.uuid4()}.hex → uuid.uuid4().hex  
2. Double braces }} → }

Uses sed for maximum safety and speed.
"""

import subprocess


def find_and_fix_pattern(pattern_name: str, find_pattern: str, replace_pattern: str, dry_run: bool = True):
    """Find files with pattern and fix them."""

    print(f"\n🔍 Finding {pattern_name} pattern...")

    # Find files with the pattern
    find_cmd = [
        "find", ".", "-name", "*.py",
        "-not", "-path", "./.venv/*",
        "-not", "-path", "./.cleanenv/*",
        "-not", "-path", "./.venv-lock/*",
        "-not", "-path", "./products/experience/dashboard/core/backend/.venv/*",
        "-exec", "grep", "-l", find_pattern, "{}", "+"
    ]

    try:
        result = subprocess.run(find_cmd, capture_output=True, text=True, check=True)
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        if not files:
            print(f"   No files found with {pattern_name} pattern")
            return 0

        print(f"   Found {len(files)} files with {pattern_name} pattern")

        if dry_run:
            print("   Files that would be fixed:")
            for file in files[:10]:  # Show first 10
                print(f"     {file}")
            if len(files) > 10:
                print(f"     ... and {len(files) - 10} more")
            return len(files)

        # Apply fix using sed
        fixed_count = 0
        for file in files:
            try:
                # Use sed to make the replacement
                sed_cmd = ["sed", "-i.backup", f"s/{find_pattern}/{replace_pattern}/g", file]
                subprocess.run(sed_cmd, check=True)
                print(f"   ✅ Fixed: {file}")
                fixed_count += 1
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to fix {file}: {e}")

        return fixed_count

    except subprocess.CalledProcessError:
        print(f"   No files found with {pattern_name} pattern")
        return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simple f-string pattern fixer")
    parser.add_argument("--live", action="store_true", help="Apply fixes (default is dry-run)")

    args = parser.parse_args()

    print("🔧 LUKHAS Simple F-String Fixer")
    print(f"Mode: {'LIVE FIX' if args.live else 'DRY RUN'}")

    # Define the patterns to fix
    patterns = [
        (
            "uuid.hex brace mismatch",
            r"uuid\.uuid4()\.hex}",  # Find pattern for grep
            r"uuid.uuid4().hex",     # Replacement for sed
        ),
        (
            "time.time brace mismatch",
            r"time\.time()}",
            r"time.time())",
        ),
        (
            "double closing braces",
            r"}}\"",  # Look for }}" at end of f-strings
            r"}\"",
        ),
    ]

    total_files = 0
    for pattern_name, find_pattern, replace_pattern in patterns:
        count = find_and_fix_pattern(pattern_name, find_pattern, replace_pattern, dry_run=not args.live)
        total_files += count

    print(f"\n📊 Summary: {total_files} files would be processed" if not args.live else f"📊 Summary: {total_files} files fixed")

    if not args.live:
        print("\n💡 To apply fixes, run with --live flag")
        print("💡 Backup files will be created automatically (.backup extension)")


if __name__ == "__main__":
    main()
