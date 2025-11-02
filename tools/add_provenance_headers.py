#!/usr/bin/env python3
"""
Add provenance headers to generated scaffold files.
Helps track template versions and edit policies.
"""

import pathlib
import subprocess
import sys
from typing import Dict


class ProvenanceHeadersAdder:
    def __init__(self):
        self.git_commit = self._get_git_commit()
        self.scaffold_version = "1.0"
        self.template_version = "v1"

        # File type mappings to comment styles
        self.comment_styles = {
            ".yaml": "#",
            ".yml": "#",
            ".py": "#",
            ".md": "<!--",
            ".json": "//",  # Note: JSON doesn't support comments, but some parsers allow //
        }

        # Files that should be marked as editable vs regenerated
        self.editable_files = {
            "README.md",  # Humans can edit READMEs
            "api.md",  # Documentation is editable
            "architecture.md",
            "troubleshooting.md",
        }

    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def create_header(self, file_path: pathlib.Path, file_type: str) -> str:
        """Create provenance header for a file."""
        comment_char = self.comment_styles.get(file_type, "#")
        is_editable = file_path.name in self.editable_files

        if file_type == ".md":
            header = f"""<!--
@generated LUKHAS scaffold v{self.scaffold_version}
template_id: module.scaffold/{self.template_version}
template_commit: {self.git_commit}
do_not_edit: {str(not is_editable).lower()}
human_editable: {str(is_editable).lower()}
-->

"""
        else:
            header = f"""{comment_char} @generated LUKHAS scaffold v{self.scaffold_version}
{comment_char} template_id: module.scaffold/{self.template_version}
{comment_char} template_commit: {self.git_commit}
{comment_char} do_not_edit: {str(not is_editable).lower()}
{comment_char} human_editable: {str(is_editable).lower()}
{comment_char}
"""

        return header

    def has_provenance_header(self, file_path: pathlib.Path) -> bool:
        """Check if file already has a provenance header."""
        try:
            with open(file_path, "r") as f:
                first_lines = f.read(500)  # Check first 500 chars
                return "@generated LUKHAS scaffold" in first_lines
        except Exception:
            return False

    def add_header_to_file(self, file_path: pathlib.Path) -> bool:
        """Add provenance header to a file."""
        if self.has_provenance_header(file_path):
            return False  # Already has header

        file_type = file_path.suffix.lower()
        if file_type not in self.comment_styles:
            return False  # Unsupported file type

        try:
            # Read current content
            with open(file_path, "r") as f:
                content = f.read()

            # Create header
            header = self.create_header(file_path, file_type)

            # Write header + content
            with open(file_path, "w") as f:
                f.write(header + content)

            return True

        except Exception as e:
            print(f"❌ Failed to add header to {file_path}: {e}")
            return False

    def process_module_directory(self, module_path: pathlib.Path) -> Dict[str, int]:
        """Process all scaffold files in a module directory."""
        results = {"processed": 0, "skipped": 0, "errors": 0}

        # Target directories and their key files
        target_patterns = ["config/*.yaml", "config/*.yml", "docs/*.md", "tests/*.py", "assets/*.md"]

        for pattern in target_patterns:
            for file_path in module_path.glob(pattern):
                if file_path.is_file():
                    if self.add_header_to_file(file_path):
                        results["processed"] += 1
                    else:
                        results["skipped"] += 1

        return results


def main():
    """Main function to add provenance headers."""
    adder = ProvenanceHeadersAdder()

    # Find all module directories
    root_path = pathlib.Path(".")
    module_dirs = []

    for item in root_path.iterdir():
        if item.is_dir() and not item.name.startswith(".") and (item / "config").exists():
            module_dirs.append(item)

    if not module_dirs:
        print("No module directories found")
        return 0

    print(f"🏷️  Adding provenance headers to {len(module_dirs)} modules...")

    total_processed = 0
    total_skipped = 0

    for module_dir in sorted(module_dirs):
        results = adder.process_module_directory(module_dir)
        total_processed += results["processed"]
        total_skipped += results["skipped"]

        if results["processed"] > 0:
            print(f"✅ {module_dir.name}: +{results['processed']} headers")
        elif results["skipped"] > 0:
            print(f"⏭️  {module_dir.name}: {results['skipped']} already have headers")

    print("\n📊 Summary:")
    print(f"   Headers added: {total_processed}")
    print(f"   Files skipped: {total_skipped}")
    print(f"   Total modules: {len(module_dirs)}")

    if total_processed > 0:
        print(f"\n✨ Added provenance tracking to {total_processed} generated files")
        print("   Use tools/sync_scaffold.py to update from templates")

    return 0


if __name__ == "__main__":
    sys.exit(main())
