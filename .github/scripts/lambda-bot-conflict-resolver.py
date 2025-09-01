#!/usr/bin/env python3
"""
ΛBot Intelligent Conflict Resolution Script
# ΛTAG: conflict-resolution, lambda-bot
"""

import argparse
import subprocess
import sys
from pathlib import Path


def resolve_documentation_conflicts(file_path):
    """Resolve conflicts in documentation files intelligently."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Remove conflict markers and merge intelligently
        lines = content.split("\n")
        resolved_lines = []
        in_conflict = False
        our_lines = []
        their_lines = []

        for line in lines:
            if line.startswith("<<<<<<< "):
                in_conflict = True
                our_lines = []
                their_lines = []
            elif line.startswith("======="):
                # Switch to their section
                pass
            elif line.startswith(">>>>>>> "):
                in_conflict = False

                # Intelligent merge logic
                if any("ΛTAG" in line_item or "ΛORIGIN" in line_item for line_item in our_lines + their_lines):
                    # Keep symbolic tags from both
                    resolved_lines.extend(our_lines)
                    resolved_lines.extend([line_item for line_item in their_lines if line_item not in our_lines])
                elif any(
                    "security" in line_item.lower() or "vulnerability" in line_item.lower() for line_item in our_lines
                ):
                    # Keep security-related content
                    resolved_lines.extend(our_lines)
                else:
                    # Default: keep ours
                    resolved_lines.extend(our_lines)
            elif in_conflict:
                if "=======" not in line:
                    if not their_lines:  # Still in our section
                        our_lines.append(line)
                    else:  # In their section
                        their_lines.append(line)
            else:
                resolved_lines.append(line)

        # Write resolved content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(resolved_lines))

        print(f"✅ Resolved conflicts in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error resolving {file_path}: {e}")
        return False


def resolve_python_conflicts(file_path):
    """Resolve conflicts in Python files intelligently."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Remove conflict markers and merge Python code intelligently
        lines = content.split("\n")
        resolved_lines = []
        in_conflict = False
        our_lines = []
        their_lines = []

        for line in lines:
            if line.startswith("<<<<<<< "):
                in_conflict = True
                our_lines = []
                their_lines = []
            elif line.startswith("======="):
                pass
            elif line.startswith(">>>>>>> "):
                in_conflict = False

                # Python-specific merge logic
                if any("import" in line_item for line_item in our_lines + their_lines):
                    # Merge imports uniquely
                    all_imports = set(our_lines + their_lines)
                    resolved_lines.extend(sorted(all_imports))
                elif any("# ΛTAG" in line_item or "# ΛORIGIN" in line_item for line_item in our_lines + their_lines):
                    # Keep symbolic headers
                    resolved_lines.extend(our_lines)
                    resolved_lines.extend([line_item for line_item in their_lines if line_item not in our_lines])
                else:
                    # Default: keep our version
                    resolved_lines.extend(our_lines)
            elif in_conflict:
                if not their_lines:
                    our_lines.append(line)
                else:
                    their_lines.append(line)
            else:
                resolved_lines.append(line)

        # Write resolved content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(resolved_lines))

        print(f"✅ Resolved Python conflicts in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error resolving {file_path}: {e}")
        return False


def resolve_file_conflicts(file_path):
    """Resolve conflicts in a file based on its type."""
    file_path = Path(file_path)

    if file_path.suffix == ".py":
        return resolve_python_conflicts(file_path)
    elif file_path.suffix in [".md", ".txt"] or "README" in file_path.name:
        return resolve_documentation_conflicts(file_path)
    else:
        # Default: keep HEAD version
        try:
            subprocess.run(["git", "checkout", "--ours", str(file_path)], check=True)
            subprocess.run(["git", "add", str(file_path)], check=True)
            print(f"✅ Resolved {file_path} using HEAD version")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error resolving {file_path}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="ΛBot Intelligent Conflict Resolution")
    parser.add_argument("files", nargs="+", help="Files to resolve conflicts in")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    success_count = 0
    total_files = len(args.files)

    for file_path in args.files:
        if args.dry_run:
            print(f"Would resolve conflicts in: {file_path}")
            continue

        if resolve_file_conflicts(file_path):
            success_count += 1

    if not args.dry_run:
        print(f"\n🎯 Resolution Summary: {success_count}/{total_files} files resolved successfully")

        if success_count == total_files:
            print("✅ All conflicts resolved successfully!")
            sys.exit(0)
        else:
            print("⚠️ Some conflicts could not be resolved automatically")
            sys.exit(1)


if __name__ == "__main__":
    main()
