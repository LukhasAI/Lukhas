#!/usr/bin/env python3
"""
LUKHAS Automated File Organizer
================================
Keeps the root directory clean by automatically organizing files
according to predefined rules.
"""

import argparse
import json
import logging
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class FileOrganizer:
    """Automated file organization system for LUKHAS"""

    def __init__(self, root_path: Optional[Path] = None, config_file: str = ".file-organization.yaml"):
        self.root_path = root_path or Path.cwd()
        self.config_file = self.root_path / config_file
        self.config = self.load_config()
        self.dry_run = False
        self.moves_log = []
        self.stats = defaultdict(int)

    def load_config(self) -> dict:
        """Load organization configuration"""
        if not self.config_file.exists():
            logger.error(f"Configuration file {self.config_file} not found")
            return {}

        with open(self.config_file) as f:
            return yaml.safe_load(f)

    def ensure_directories(self):
        """Create required directories"""
        for dir_path in self.config.get("ensure_directories", []):
            full_path = self.root_path / dir_path
            if not full_path.exists():
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {dir_path}")

    def should_keep_in_root(self, filename: str) -> bool:
        """Check if file should stay in root"""
        keep_list = self.config.get("keep_in_root", [])
        return filename in keep_list

    def find_destination(self, filename: str) -> Optional[tuple[str, str]]:
        """Find destination for a file based on rules"""
        rules = self.config.get("organization_rules", [])

        for rule in rules:
            pattern = rule.get("pattern")
            if pattern and re.match(pattern, filename):
                return rule.get("destination"), rule.get("description")

        return None, None

    def move_file(self, source: Path, destination: Path, description: str):
        """Move a file to its destination"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would move: {source.name} → {destination}")
            self.moves_log.append(
                {
                    "file": source.name,
                    "from": str(source.parent),
                    "to": str(destination),
                    "description": description,
                    "dry_run": True,
                }
            )
            return True

        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(source), str(destination))

            logger.info(f"✅ Moved: {source.name} → {destination}")

            self.moves_log.append(
                {
                    "file": source.name,
                    "from": str(source.parent),
                    "to": str(destination),
                    "description": description,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to move {source.name}: {e}")
            return False

    def clean_root(self, interactive: bool = False):
        """Clean root directory according to rules"""
        logger.info("🧹 Starting root directory organization...")

        # Ensure required directories exist
        self.ensure_directories()

        # Get all files in root
        root_files = [f for f in self.root_path.iterdir() if f.is_file()]

        logger.info(f"📊 Found {len(root_files)} files in root directory")

        moved_count = 0
        kept_count = 0
        reviewed_count = 0

        for file_path in root_files:
            filename = file_path.name

            # Skip hidden files (except specific ones)
            if filename.startswith(".") and not filename.endswith(".backup"):
                continue

            # Check if should keep in root
            if self.should_keep_in_root(filename):
                kept_count += 1
                logger.debug(f"📌 Keeping in root: {filename}")
                continue

            # Check special cases
            special = self.config.get("special_cases", {})
            review_patterns = special.get("review_before_move", [])

            needs_review = False
            for pattern in review_patterns:
                if re.match(pattern.replace("*", ".*"), filename):
                    needs_review = True
                    break

            if needs_review and interactive:
                response = input(f"❓ Review: {filename} - Move? (y/n/s[kip]): ").lower()
                if response == "n":
                    kept_count += 1
                    continue
                elif response == "s":
                    reviewed_count += 1
                    continue

            # Find destination based on rules
            destination_dir, description = self.find_destination(filename)

            if destination_dir:
                destination = self.root_path / destination_dir / filename
                if self.move_file(file_path, destination, description):
                    moved_count += 1
                    self.stats[destination_dir] += 1
            else:
                logger.debug(f"⚠️ No rule for: {filename}")

        # Log summary
        logger.info("\n📊 Organization Summary:")
        logger.info(f"  ✅ Moved: {moved_count} files")
        logger.info(f"  📌 Kept in root: {kept_count} files")
        logger.info(f"  👀 Reviewed: {reviewed_count} files")

        if self.stats:
            logger.info("\n📁 Files by destination:")
            for dest, count in sorted(self.stats.items()):
                logger.info(f"  {dest}: {count} files")

    def cleanup_old_files(self):
        """Clean up old files based on age rules"""
        archive_rules = self.config.get("cleanup", {}).get("archive_after_days", {})

        for pattern, days in archive_rules.items():
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            pattern_regex = pattern.replace("*", ".*")

            for file_path in self.root_path.rglob("*"):
                if file_path.is_file() and re.match(pattern_regex, file_path.name):
                    # Check file age
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        archive_path = self.root_path / "archive" / "aged" / file_path.name
                        logger.info(
                            f"📦 Archiving old file: {file_path.name} (age: {(datetime.now(timezone.utc) - mtime}.days} days)"
                        )
                        if not self.dry_run:
                            archive_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(archive_path))

    def delete_unwanted_files(self):
        """Delete unwanted file types"""
        delete_patterns = self.config.get("cleanup", {}).get("delete_patterns", [])

        deleted_count = 0
        for pattern in delete_patterns:
            pattern_regex = pattern.replace("*", ".*")

            for file_path in self.root_path.rglob("*"):
                if file_path.is_file() and re.match(pattern_regex, file_path.name):
                    logger.info(f"🗑️ Deleting: {file_path}")
                    if not self.dry_run:
                        file_path.unlink()
                    deleted_count += 1

        if deleted_count > 0:
            logger.info(f"🗑️ Deleted {deleted_count} unwanted files")

    def generate_report(self):
        """Generate organization report"""
        if not self.config.get("reporting", {}).get("generate_summary", True):
            return

        report_path = self.root_path / "docs" / "organization_summary.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = [
            "# File Organization Report",
            f"\nGenerated: {datetime.now(timezone.utc).isoformat()}",
            "\n## Summary",
            f"- Total files moved: {sum(self.stats.values()}",
            f"- Dry run: {self.dry_run}",
            "\n## Moves by Destination\n",
        ]

        for dest, count in sorted(self.stats.items()):
            report.append(f"- `{dest}`: {count} files")

        if self.moves_log:
            report.append("\n## Recent Moves\n")
            for move in self.moves_log[-20:]:  # Last 20 moves
                report.append(f"- `{move['file']}` → `{move['to']}`")

        report_content = "\n".join(report)

        if not self.dry_run:
            with open(report_path, "w") as f:
                f.write(report_content)
            logger.info(f"📄 Report saved to: {report_path}")

        # Save detailed log
        log_path = self.root_path / ".file_organization_log.json"
        if not self.dry_run:
            existing_log = []
            if log_path.exists():
                with open(log_path) as f:
                    existing_log = json.load(f)

            existing_log.extend(self.moves_log)

            # Keep only last 1000 entries
            existing_log = existing_log[-1000:]

            with open(log_path, "w") as f:
                json.dump(existing_log, f, indent=2)

    def suggest_new_rules(self):
        """Suggest new organization rules based on unmatched files"""
        unmatched = []

        for file_path in self.root_path.iterdir():
            if file_path.is_file():
                filename = file_path.name

                if not self.should_keep_in_root(filename):
                    dest, _ = self.find_destination(filename)
                    if not dest:
                        unmatched.append(filename)

        if unmatched:
            logger.info(f"\n💡 Suggested new rules for {len(unmatched)} unmatched files:")

            # Group by patterns
            suggestions = defaultdict(list)

            for filename in unmatched:
                # Extract patterns
                if filename.endswith(".md"):
                    if "_" in filename:
                        prefix = filename.split("_")[0]
                        suggestions[f"^{prefix}_.*\\.md$"].append(filename)
                    else:
                        suggestions["^.*\\.md$"].append(filename)
                else:
                    ext = Path(filename).suffix
                    if ext:
                        suggestions[f".*\\{ext}$"].append(filename)

            for pattern, files in suggestions.items():
                if len(files) >= 2:  # Only suggest if pattern matches multiple files
                    logger.info(f"\n  Pattern: `{pattern}`")
                    logger.info(f"  Matches: {', '.join(files[:3])}")
                    logger.info("  Suggested destination: docs/uncategorized/")

    def watch_mode(self, interval: int = 60):
        """Watch mode - continuously organize files"""
        import time

        logger.info(f"👁️ Starting watch mode (interval: {interval}s)")

        try:
            while True:
                self.clean_root()
                self.cleanup_old_files()
                self.generate_report()

                logger.info(f"💤 Sleeping for {interval} seconds...")
                time.sleep(interval)

                # Reload config in case it changed
                self.config = self.load_config()

        except KeyboardInterrupt:
            logger.info("⏹️ Watch mode stopped")

    def restore_file(self, filename: str):
        """Restore a moved file back to root"""
        log_path = self.root_path / ".file_organization_log.json"

        if not log_path.exists():
            logger.error("No move history found")
            return

        with open(log_path) as f:
            log = json.load(f)

        # Find the file in history
        for entry in reversed(log):
            if entry.get("file") == filename:
                source = Path(entry["to"])
                destination = self.root_path / filename

                if source.exists():
                    shutil.move(str(source), str(destination))
                    logger.info(f"✅ Restored {filename} to root")
                    return
                else:
                    logger.error(f"File not found at {source}")
                    return

        logger.error(f"No history found for {filename}")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="LUKHAS File Organizer")
    parser.add_argument(
        "command",
        choices=["organize", "cleanup", "suggest", "watch", "restore", "report"],
        help="Command to execute",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--interactive", action="store_true", help="Ask before moving special files")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds (default: 300)")
    parser.add_argument("--file", help="File to restore (for restore command)")
    parser.add_argument("--config", default=".file-organization.yaml", help="Configuration file path")

    args = parser.parse_args()

    # Initialize organizer
    organizer = FileOrganizer(config_file=args.config)
    organizer.dry_run = args.dry_run

    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")

    if args.command == "organize":
        # Organize root directory
        organizer.clean_root(interactive=args.interactive)
        organizer.generate_report()

    elif args.command == "cleanup":
        # Clean up old and unwanted files
        organizer.cleanup_old_files()
        organizer.delete_unwanted_files()

    elif args.command == "suggest":
        # Suggest new rules
        organizer.suggest_new_rules()

    elif args.command == "watch":
        # Watch mode
        organizer.watch_mode(interval=args.interval)

    elif args.command == "restore":
        # Restore a file
        if not args.file:
            logger.error("Please specify a file to restore with --file")
            sys.exit(1)
        organizer.restore_file(args.file)

    elif args.command == "report":
        # Generate report only
        organizer.generate_report()


if __name__ == "__main__":
    main()
