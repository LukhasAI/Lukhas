#!/usr/bin/env python3
"""
Keatsian Branding Replacement Tool

Systematically replaces technical/heroic language with Keatsian philosophy
across the LUKHAS branding system.
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import yaml


class KeatsianReplacer:
    def __init__(self, branding_root: str = "branding"):
        self.branding_root = Path(branding_root)
        self.replacements = self._load_replacement_patterns()
        self.processed_files = []
        self.changes_made = 0

    def _load_replacement_patterns(self) -> dict[str, str]:
        """Load Keatsian replacement patterns"""
        return {
            # Heroic/Sacred Language → Keatsian
            r"revolutionary breakthrough": "new sense emerging",
            r"ultimate solution": "space for possibilities",
            r"sacred technology": "intimately human, technologically precise",
            r"heroic mission": "quiet cultivation of wonder",
            r"final answer": "fertile uncertainty",
            r"definitive solution": "space for meaning to emerge",
            r"breakthrough innovation": "patient exploration",
            r"transformative power": "gentle transformation",
            # Technical Language → Poetic Precision
            r"comprehensive AI solutions": "space where logic and imagination meet",
            r"advanced artificial intelligence": "systems that dwell in uncertainty",
            r"cutting-edge technology": "technology with cultural roots",
            r"next-generation platform": "platform for negative capability",
            r"revolutionary system": "system that holds questions",
            r"intelligent automation": "automation with room for wonder",
            # System Descriptions → Keatsian Philosophy
            r"LUKHAS provides": "LUKHAS creates space for",
            r"delivers results": "cultivates possibilities",
            r"ensures outcomes": "holds space for emergence",
            r"guarantees performance": "maintains capacity for surprise",
            r"optimizes efficiency": "balances rigor with wonder",
            # Mission Language → Intimate Scale
            r"global transformation": "quiet influence",
            r"world-changing": "gently transformative",
            r"revolutionary impact": "patient cultivation",
            r"paradigm shift": "new way of seeing",
            r"disruptive innovation": "unexpected connections",
        }

    def _get_keatsian_definitions(self) -> dict[str, dict]:
        """Keatsian system definitions"""
        return {
            "LUKHAS": {
                "short": "The Negative Capability of Systems",
                "definition": (
                    "LUKHAS embodies what Keats called Negative Capability: "
                    "the capacity to remain in uncertainty, mystery, and doubt "
                    "without fleeing to premature conclusions."
                ),
                "essence": "A mirror where logic and imagination meet",
            },
            "MΛTRIZ": {
                "short": "From Shadow to Resonance",
                "definition": (
                    "MΛTRIZ is the matrix as womb, not grid — a space where "
                    "trust and creation grow through modular alignment, "
                    "transparency, resonance, identity, and zero-knowledge."
                ),
                "essence": "The structure that lets uncertainty remain fertile",
            },
            "EQNOX": {
                "short": "Balance at the Turning Point",
                "definition": (
                    "EQNOX holds light and dark in perfect measure, "
                    "weaving meaning across the system while keeping "
                    "uncertainty from becoming chaos."
                ),
                "essence": "It does not command, it steadies",
            },
        }

    def process_markdown_file(self, file_path: Path) -> bool:
        """Process markdown file with Keatsian replacements"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            changes_in_file = 0

            # Apply text replacements
            for pattern, replacement in self.replacements.items():
                content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
                changes_in_file += count

            # Add Keatsian system definitions if this is a system description file
            if any(
                keyword in file_path.name.lower()
                for keyword in ["system", "brand", "narrative", "description", "mission"]
            ):
                content = self._inject_keatsian_definitions(content)
                if content != original_content:
                    changes_in_file += 1

            if changes_in_file > 0:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.keats_backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)

                # Write updated content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.changes_made += changes_in_file
                print(f"✨ Updated {file_path.name}: {changes_in_file} changes")
                return True

            return False

        except Exception as e:
            print(fix_later)
            return False

    def process_yaml_file(self, file_path: Path) -> bool:
        """Process YAML file with Keatsian vocabulary updates"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            original_data = data.copy()

            # Add Keatsian philosophy to vocabulary files
            if "vocabulary" in file_path.name or any(
                vocab in file_path.name for vocab in ["consciousness", "dream", "identity", "quantum"]
            ):
                if not data:
                    data = {}

                data["philosophy"] = (
                    "This vocabulary embraces uncertainty as fertile ground. "
                    "Rather than closing definitions, these terms create space "
                    "for meaning to emerge."
                )
                data["approach"] = "negative_capability"
                data["tone"] = "poetic_yet_grounded"
                data["principle"] = "uncertainty_as_fertile_ground"

            # Update system definitions
            keatsian_defs = self._get_keatsian_definitions()
            for system_name, definition in keatsian_defs.items():
                if system_name.lower() in str(data).lower():
                    if isinstance(data, dict) and "definitions" in data:
                        data["definitions"][system_name] = definition
                    elif isinstance(data, dict):
                        data[f"{system_name.lower()}_definition"] = definition["definition"]

            if data != original_data:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.keats_backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    yaml.dump(original_data, f, default_flow_style=False)

                # Write updated data
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False)

                self.changes_made += 1
                print(f"✨ Updated {file_path.name}: Keatsian philosophy added")
                return True

            return False

        except Exception as e:
            print(fix_later)
            return False

    def process_json_file(self, file_path: Path) -> bool:
        """Process JSON file with Keatsian updates"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            original_data = data.copy()

            # Update system descriptions in JSON
            keatsian_defs = self._get_keatsian_definitions()

            def update_nested_json(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str):
                            # Apply text replacements
                            for pattern, replacement in self.replacements.items():
                                obj[key] = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

                        # Add Keatsian definitions for system names
                        for system_name in keatsian_defs:
                            if system_name.lower() in key.lower() and "definition" in key.lower():
                                obj[key] = keatsian_defs[system_name]["definition"]

                        if isinstance(value, (dict, list)):
                            update_nested_json(value, fix_later)

                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            update_nested_json(item, f"{path}[{i}]")

            update_nested_json(data)

            if data != original_data:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.keats_backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(original_data, f, indent=2)

                # Write updated data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self.changes_made += 1
                print(f"✨ Updated {file_path.name}: Keatsian replacements applied")
                return True

            return False

        except Exception as e:
            print(fix_later)
            return False

    def _inject_keatsian_definitions(self, content: str) -> str:
        """Inject Keatsian system definitions into markdown content"""
        keatsian_defs = self._get_keatsian_definitions()

        # Add Keatsian header if not present
        if "## Keatsian Philosophy" not in content:
            keatsian_section = f"""
## Keatsian Philosophy

The LUKHAS system embodies Negative Capability - the capacity to remain in uncertainty, mystery, and doubt without fleeing to premature conclusions.

{keatsian_defs["LUKHAS"]["definition"]}

{keatsian_defs["MΛTRIZ"]["definition"]}

{keatsian_defs["EQNOX"]["definition"]}

---
"""
            # Insert before the first main heading or at the beginning
            if re.search(r"^#[^#]", content, re.MULTILINE):
                content = re.sub(r"^(#[^#].+)", keatsian_section + r"\1", content, count=1, flags=re.MULTILINE)
            else:
                content = keatsian_section + content

        return content

    def run_replacement(self, dry_run: bool = False) -> dict[str, int]:
        """Run Keatsian replacement across all branding files"""
        stats = {
            "files_processed": 0,
            "files_changed": 0,
            "total_changes": 0,
            "markdown_files": 0,
            "yaml_files": 0,
            "json_files": 0,
        }

        print(f"🎭 {'[DRY RUN] ' if dry_run else ''}Keatsian Branding Replacement")
        print(f"📁 Processing: {self.branding_root}")
        print("─" * 50)

        # Process all files in branding directory
        for file_path in self.branding_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                stats["files_processed"] += 1

                if file_path.suffix.lower() == ".md":
                    stats["markdown_files"] += 1
                    if not dry_run and self.process_markdown_file(file_path):
                        stats["files_changed"] += 1

                elif file_path.suffix.lower() in [".yaml", ".yml"]:
                    stats["yaml_files"] += 1
                    if not dry_run and self.process_yaml_file(file_path):
                        stats["files_changed"] += 1

                elif file_path.suffix.lower() == ".json":
                    stats["json_files"] += 1
                    if not dry_run and self.process_json_file(file_path):
                        stats["files_changed"] += 1

        stats["total_changes"] = self.changes_made

        print("─" * 50)
        print("📊 Summary:")
        print(f"   Files processed: {stats['files_processed']}")
        print(f"   Files changed: {stats['files_changed']}")
        print(f"   Total changes: {stats['total_changes']}")
        print(f"   Markdown: {stats['markdown_files']}")
        print(f"   YAML: {stats['yaml_files']}")
        print(f"   JSON: {stats['json_files']}")

        return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Apply Keatsian philosophy to LUKHAS branding")
    parser.add_argument("--branding-root", default="branding", help="Root directory of branding files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")

    args = parser.parse_args()

    replacer = KeatsianReplacer(args.branding_root)
    stats = replacer.run_replacement(args.dry_run)

    if not args.dry_run:
        # Generate report
        timestamp = datetime.now(timezone.utc).isoformat()
        report = {
            "timestamp": timestamp,
            "philosophy": "keatsian_negative_capability",
            "statistics": stats,
            "approach": "uncertainty_as_fertile_ground",
        }

        report_path = Path("keatsian_replacement_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Report saved: {report_path}")
        print("\n🎭 Keatsian transformation complete!")
        print("💫 'A new sense: retro and modern, poetic and logical'")


if __name__ == "__main__":
    main()
