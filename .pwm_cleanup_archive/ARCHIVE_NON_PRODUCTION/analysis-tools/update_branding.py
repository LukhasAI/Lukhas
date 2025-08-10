#!/usr/bin/env python3
"""
Safe Branding Update Script
Updates old Lucas/lucas branding to LUKHAS/lukhas
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class BrandingUpdater:
    """Safely updates branding from Lucas to LUKHAS"""

    def __init__(self, repo_path: str, dry_run: bool = True):
        self.repo_path = Path(repo_path)
        self.dry_run = dry_run
        self.backup_dir = (
            self.repo_path
            / f".branding_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.changes_made = []

        # Branding mappings - order matters for proper replacement
        self.branding_map = [
            # Exact case mappings
            ("LUCAS", "LUKHAS"),
            ("Lucas", "LUKHAS"),
            ("lucas", "lukhas"),
            ("LucAS", "LUKHAS"),
            ("Lucλs", "LUKHAS"),
            ("LUCΛS", "LUKHAS"),
            # URL/path safe versions
            ("lucas-ai", "lukhas-ai"),
            ("Lucas-AI", "LUKHAS-AI"),
            ("LUCAS_AI", "LUKHAS_AI"),
            ("lucas_ai", "lukhas_ai"),
        ]

        # Patterns to check but NOT replace (for safety)
        self.exclude_patterns = [
            r"\.git/",
            r"\.venv/",
            r"__pycache__",
            r"\.pyc$",
            r"\.backup",
            r"node_modules/",
        ]

    def load_files_to_update(self, file_list_path: str) -> List[str]:
        """Load list of files that need branding updates"""
        with open(file_list_path) as f:
            data = json.load(f)

        files = []
        if "branding_updates" in data:
            files = [item["file"] for item in data["branding_updates"]]
        elif "branding" in data:
            files = [item["file"] for item in data["branding"]]

        # Filter out excluded patterns
        filtered_files = []
        for file_path in files:
            if not any(
                re.search(pattern, file_path) for pattern in self.exclude_patterns
            ):
                full_path = self.repo_path / file_path
                if full_path.exists() and full_path.is_file():
                    filtered_files.append(file_path)

        return filtered_files

    def backup_file(self, file_path: str):
        """Create backup of file before modification"""
        if not self.dry_run:
            full_path = self.repo_path / file_path
            backup_path = self.backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(full_path, backup_path)

    def update_file_content(self, file_path: str) -> Tuple[bool, List[str]]:
        """Update branding in file content"""
        full_path = self.repo_path / file_path

        try:
            with open(full_path, encoding="utf-8") as f:
                original_content = f.read()

            updated_content = original_content
            changes = []

            # Apply branding replacements
            for old_brand, new_brand in self.branding_map:
                if old_brand in updated_content:
                    # Count occurrences
                    count = updated_content.count(old_brand)
                    updated_content = updated_content.replace(old_brand, new_brand)
                    changes.append(f"{old_brand} → {new_brand} ({count} occurrences)")

            if updated_content != original_content:
                if not self.dry_run:
                    self.backup_file(file_path)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(updated_content)

                return True, changes

            return False, []

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return False, []

    def update_filename_if_needed(self, file_path: str) -> Optional[str]:
        """Check if filename itself needs branding update"""
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        new_filename = filename
        for old_brand, new_brand in self.branding_map:
            if old_brand in filename:
                new_filename = new_filename.replace(old_brand, new_brand)

        if new_filename != filename:
            new_path = (
                os.path.join(directory, new_filename) if directory else new_filename
            )
            return new_path
        return None

    def process_files(self, files: List[str]):
        """Process all files for branding updates"""
        print(f"\n{'🧪 DRY RUN MODE' if self.dry_run else '🚀 UPDATING FILES'}")
        print("=" * 70)

        total_files = len(files)
        files_updated = 0
        total_changes = 0

        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{total_files}] Processing: {file_path}")

            # Update file content
            updated, changes = self.update_file_content(file_path)

            if updated:
                files_updated += 1
                total_changes += len(changes)
                print("  ✅ Content updated:")
                for change in changes:
                    print(f"     - {change}")
                self.changes_made.append({"file": file_path, "changes": changes})

            # Check if filename needs update
            new_filename = self.update_filename_if_needed(file_path)
            if new_filename:
                print(
                    f"  📝 Filename change needed: {os.path.basename(file_path)} → {os.path.basename(new_filename)}"
                )
                if not self.dry_run:
                    full_old_path = self.repo_path / file_path
                    full_new_path = self.repo_path / new_filename
                    full_old_path.rename(full_new_path)
                    print("  ✅ File renamed")

        # Summary
        print("\n" + "=" * 70)
        print("📊 BRANDING UPDATE SUMMARY")
        print("=" * 70)
        print(f"Total files processed: {total_files}")
        print(f"Files with updates: {files_updated}")
        print(f"Total branding changes: {total_changes}")

        if self.dry_run:
            print("\n⚠️  DRY RUN - No files were actually modified")
            print("Run with --execute to apply changes")
        else:
            print("\n✅ Updates applied successfully")
            print(f"Backup created at: {self.backup_dir}")

    def save_report(self, output_file: str = "branding_update_report.json"):
        """Save detailed report of changes"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "dry_run" if self.dry_run else "executed",
            "backup_dir": str(self.backup_dir) if not self.dry_run else None,
            "summary": {
                "files_processed": len(self.changes_made),
                "total_changes": sum(len(c["changes"]) for c in self.changes_made),
            },
            "detailed_changes": self.changes_made,
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Update branding from Lucas/lucas to LUKHAS/lukhas"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("file_list", help="JSON file with list of files to update")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform updates (default is dry run)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="branding_update_report.json",
        help="Output file for detailed report",
    )

    args = parser.parse_args()

    print("🎨 LUKHAS Branding Updater")
    print("Converting: Lucas/lucas → LUKHAS/lukhas")

    updater = BrandingUpdater(args.repo_path, dry_run=not args.execute)

    # Load files to update
    files = updater.load_files_to_update(args.file_list)
    print(f"\n📋 Found {len(files)} files to process")

    if files:
        # Process files
        updater.process_files(files)

        # Save report
        updater.save_report(args.output)
    else:
        print("❌ No valid files found to update")


if __name__ == "__main__":
    main()
