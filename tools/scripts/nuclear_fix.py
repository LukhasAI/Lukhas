#!/usr/bin/env python3
"""
NUCLEAR FIX - The most aggressive fix possible
This WILL modify your code significantly!
"""
import re
import subprocess
from pathlib import Path


def nuclear_fix_file(filepath: Path):
    """Apply nuclear-level fixes to a single file"""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original_content = content

        # Fix common issues with regex
        # 1. Remove trailing whitespace
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

        # 2. Fix line length by adding backslashes
        lines = content.split("\n")
        fixed_lines = []
        for line in lines:
            if len(line) > 88 and not line.strip().startswith("#"):
                # Try to break at commas, operators, or spaces
                if "," in line[70:88]:
                    idx = line.rfind(",", 70, 88) + 1
                    fixed_lines.append(line[:idx])
                    fixed_lines.append("    " + line[idx:].strip())
                elif " = " in line[70:88]:
                    idx = line.rfind(" = ", 70, 88) + 3
                    fixed_lines.append(line[:idx] + "\\")
                    fixed_lines.append("    " + line[idx:].strip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        content = "\n".join(fixed_lines)

        # 3. Fix missing blank lines around functions/classes
        content = re.sub(r"(\n)(\s*)(class\s+\w+)", r"\n\n\2\3", content)
        content = re.sub(r"(\n)(\s*)(def\s+\w+)", r"\n\n\2\3", content)
        content = re.sub(r"(\n\n\n+)", r"\n\n", content)  # Remove excessive blank lines

        # 4. Fix bare except
        content = re.sub(r"except:\s*$", "except Exception:", content, flags=re.MULTILINE)

        # 5. Remove unused imports (aggressive)
        import_lines = []
        other_lines = []
        imports_done = False

        for line in content.split("\n"):
            if not imports_done and (line.startswith("import ") or line.startswith("from ")):
                # Check if this import is used
                if "import " in line:
                    module = re.search(r"import\s+(\w+)", line)
                    if module:
                        module_name = module.group(1)
                        # Check if used in the rest of the file
                        rest_of_file = "\n".join(other_lines)
                        if module_name in rest_of_file or "__all__" in rest_of_file:
                            import_lines.append(line)
                    else:
                        import_lines.append(line)
                else:
                    import_lines.append(line)  # Keep all from imports for safety
            else:
                if line and not line.startswith("# "):
                    imports_done = True
                other_lines.append(line)

        # Only write if we made changes
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")
        return False
    return False


def main():
    """Nuclear fix for the entire codebase"""
    print("☢️ NUCLEAR FIX MODE ☢️")
    print("=" * 60)
    print("This is the most aggressive fix possible!")
    print("=" * 60)

    # Target directories with most issues
    target_dirs = ["core", "bridge", "tools"]

    total_fixed = 0

    for target_dir in target_dirs:
        if not Path(target_dir).exists():
            continue

        print(f"\n☢️ Nuclear fixing {target_dir}...")

        # Find all Python files
        py_files = list(Path(target_dir).rglob("*.py"))

        # Process each file
        for py_file in py_files:
            if nuclear_fix_file(py_file):
                total_fixed += 1
                if total_fixed % 50 == 0:
                    print(f"  Fixed {total_fixed} files...")

        # Now run standard tools on the directory
        print(f"  Running standard tools on {target_dir}...")

        # autopep8 with maximum aggression
        subprocess.run(
            [
                "autopep8",
                "--in-place",
                "--recursive",
                "--aggressive",
                "--aggressive",
                "--aggressive",  # Triple aggressive!
                "--max-line-length",
                "88",
                "--experimental",  # Use experimental fixes
                target_dir,
            ],
            capture_output=True,
            timeout=120,
        )

        # Black
        subprocess.run(
            [
                "black",
                "--line-length",
                "88",
                "--target-version",
                "py39",
                "--quiet",
                "--fast",
                target_dir,
            ],
            capture_output=True,
            timeout=120,
        )

        # isort
        subprocess.run(
            [
                "isort",
                "--profile",
                "black",
                "--line-length",
                "88",
                "--force-single-line",
                "--force-alphabetical-sort-within-sections",
                "--quiet",
                "--recursive",
                target_dir,
            ],
            capture_output=True,
            timeout=120,
        )

    print(f"\n☢️ Nuclear fix complete! Modified {total_fixed} files")

    # Final check
    print("\n📊 Final issue count:")
    for target_dir in target_dirs:
        if Path(target_dir).exists():
            result = subprocess.run(
                [
                    "flake8",
                    target_dir,
                    "--count",
                    "--exit-zero",
                    "--max-line-length=88",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            count = result.stdout.strip().split("\n")[-1]
            print(f"  {target_dir}: {count} issues")


if __name__ == "__main__":
    import sys

    response = input("\n⚠️ NUCLEAR MODE: This will DRASTICALLY change your code! Continue? (yes/no): ")
    if response.lower() == "yes":
        main()
    else:
        print("Aborted.")
        sys.exit(0)