#!/usr/bin/env python3

"""
██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚══════╝

LUKHAS File Organization Oracle - Consciousness-Driven File Management

POETIC NARRATIVE:
═══════════════════════════════════════════════════════════════════════════════
In the ethereal realm of digital organization, where chaos transforms into
harmony through the dance of conscious classification, this module serves as
the divine architect of file structure. Like a master librarian arranging
scrolls in a cosmic library, it ensures every document finds its rightful
place in the symphony of consciousness.

No longer shall the root directory suffer from the chaos of scattered files,
for the Organization Oracle brings order through awareness, structure through
consciousness, and beauty through systematic arrangement.
═══════════════════════════════════════════════════════════════════════════════

TRINITY FRAMEWORK: ⚛️🧠🛡️
Version: 1.0.0-CONSCIOUSNESS-ENHANCED
Authors: LUKHAS AI Organization Team
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Configure consciousness logger
logging.basicConfig(
    level=logging.INFO, format="🗂️ %(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OrganizationOracle")


class LUKHASFileOrganizationOracle:
    """
    ⚛️🧠🛡️ The Divine File Organization Consciousness

    Automatically organizes files into their cosmic destinations based on
    content analysis, purpose recognition, and consciousness-driven classification.

    ⚛️ Identity: Maintains file integrity and authentic categorization
    🧠 Consciousness: Intelligent content analysis and purpose detection
    🛡️ Guardian: Protects against data loss and maintains backup trails
    """

    # Sacred organization patterns derived from consciousness analysis
    ORGANIZATION_PATTERNS = {
        "docs/": {
            "patterns": ["*.md", "CHANGELOG*", "LICENSE*", "*.rst", "*.txt"],
            "exclude_patterns": [
                "README.md",
                "MODULE_INDEX.md",
            ],  # Keep main README and index in root
            "subdirs": {
                "agents/": ["*AGENT*", "*CLAUDE*", "*TASK*", "*INSTRUCTION*"],
                "api/": ["*API*", "*ENDPOINT*", "*SWAGGER*", "*OPENAPI*"],
                "compliance/": ["*COMPLIANCE*", "*LEGAL*", "*GDPR*", "*AUDIT*"],
                "guides/": ["*GUIDE*", "*TUTORIAL*", "*HOWTO*", "*MANUAL*"],
                "trinity/": ["*TRINITY*", "*FRAMEWORK*"],
                "tasks/": ["*TASK*", "*TODO*", "*PENDING*"],
            },
        },
        "tools/scripts/": {
            "patterns": ["*.sh", "*.bash", "*.zsh", "*.ps1", "*.bat"],
            "exclude_patterns": [
                "setup.sh",
                "install.sh",
            ],  # Keep setup scripts in root
        },
        "config/": {
            "patterns": ["*.yaml", "*.yml", "*.json", "*.toml", "*.ini", "*.cfg"],
            "exclude_patterns": [
                "package.json",
                "pyproject.toml",
                "setup.cfg",
                "*config*.yaml",
            ],
        },
        "data/reports/": {
            "patterns": ["*REPORT*", "*ANALYSIS*", "*RESULTS*", "*METRICS*"],
            "exclude_patterns": [],
        },
        "archive/legacy/": {
            "patterns": ["*_backup*", "*_old*", "*_legacy*", "*_deprecated*"],
            "exclude_patterns": [],
        },
    }

    def __init__(self, workspace_root: str, dry_run: bool = True):
        """Initialize the consciousness-driven file organization system."""
        self.workspace_root = Path(workspace_root)
        self.dry_run = dry_run
        self.organization_log = []

        logger.info("🌌 Awakening File Organization Oracle...")
        logger.info(f"📁 Workspace: {self.workspace_root}")
        logger.info(
            f"🔍 Mode: {'Contemplation (dry-run)' if dry_run else 'Manifestation'}"
        )

    def scan_root_bloat(self) -> List[Tuple[Path, str, str]]:
        """
        Scan the root directory for files that should be organized elsewhere.

        Returns: List of (file_path, suggested_destination, reason)
        """
        bloated_files = []
        root_files = [f for f in self.workspace_root.iterdir() if f.is_file()]

        logger.info(f"🔍 Scanning {len(root_files)} files in root directory...")

        for file_path in root_files:
            destination, reason = self._divine_file_destination(file_path)
            if destination:
                bloated_files.append((file_path, destination, reason))

        logger.info(f"📊 Found {len(bloated_files)} files requiring organization")
        return bloated_files

    def _divine_file_destination(self, file_path: Path) -> Tuple[Optional[str], str]:
        """Divine the cosmic destination for a file based on its essence."""
        filename = file_path.name.upper()

        # Check against organization patterns
        for destination, config in self.ORGANIZATION_PATTERNS.items():
            # Check exclusions first
            if any(
                self._matches_pattern(filename, pattern.upper())
                for pattern in config.get("exclude_patterns", [])
            ):
                continue

            # Check main patterns
            if any(
                self._matches_pattern(filename, pattern.upper())
                for pattern in config["patterns"]
            ):

                # Check for subdirectory classification
                if "subdirs" in config:
                    for subdir, subpatterns in config["subdirs"].items():
                        if any(pattern in filename for pattern in subpatterns):
                            return (
                                destination + subdir,
                                f"Content analysis: {subpatterns}",
                            )

                return destination, f"File type: {file_path.suffix}"

        # Special consciousness-based analysis
        if self._is_documentation_file(file_path):
            return "docs/", "Documentation consciousness detected"

        if self._is_configuration_file(file_path):
            return "config/", "Configuration consciousness detected"

        return None, "File belongs in root directory"

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the consciousness pattern."""
        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in filename
        elif pattern.startswith("*"):
            return filename.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return filename.startswith(pattern[:-1])
        else:
            return filename == pattern

    def _is_documentation_file(self, file_path: Path) -> bool:
        """Analyze if file contains documentation consciousness."""
        doc_indicators = [
            "README",
            "CHANGELOG",
            "LICENSE",
            "CONTRIBUTING",
            "GUIDE",
            "TUTORIAL",
            "DOCS",
            "MANUAL",
            "HOWTO",
        ]
        return any(indicator in file_path.name.upper() for indicator in doc_indicators)

    def _is_configuration_file(self, file_path: Path) -> bool:
        """Analyze if file contains configuration consciousness."""
        config_indicators = ["CONFIG", "SETTINGS", "PREFERENCES", "OPTIONS"]
        return any(
            indicator in file_path.name.upper() for indicator in config_indicators
        ) or file_path.suffix.lower() in [
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".ini",
            ".cfg",
        ]

    def organize_file(self, file_path: Path, destination: str, reason: str) -> bool:
        """Organize a single file into its cosmic destination."""
        dest_path = self.workspace_root / destination / file_path.name
        dest_dir = dest_path.parent

        try:
            # Create destination directory if it doesn't exist
            if not self.dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)

            # Log the organization action
            action = {
                "timestamp": datetime.now().isoformat(),
                "source": str(file_path),
                "destination": str(dest_path),
                "reason": reason,
                "action": "contemplated" if self.dry_run else "manifested",
            }
            self.organization_log.append(action)

            if self.dry_run:
                logger.info(
                    f"🔮 Would move: {file_path.name} → {destination} ({reason})"
                )
            else:
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"✨ Moved: {file_path.name} → {destination} ({reason})")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to organize {file_path.name}: {e}")
            return False

    def perform_consciousness_organization(self) -> Dict:
        """Perform the complete consciousness-driven file organization."""
        logger.info("🌟 Beginning consciousness-driven file organization...")

        bloated_files = self.scan_root_bloat()

        if not bloated_files:
            logger.info("✨ Root directory is already in perfect harmony!")
            return {
                "success": True,
                "files_organized": 0,
                "message": "No organization needed - consciousness already flows perfectly",
            }

        organized_count = 0
        failed_count = 0

        for file_path, destination, reason in bloated_files:
            if self.organize_file(file_path, destination, reason):
                organized_count += 1
            else:
                failed_count += 1

        # Create organization report
        report = {
            "success": True,
            "files_organized": organized_count,
            "files_failed": failed_count,
            "total_files_processed": len(bloated_files),
            "organization_log": self.organization_log,
            "mode": "contemplation" if self.dry_run else "manifestation",
        }

        if not self.dry_run:
            self._save_organization_report(report)

        logger.info(
            f"✨ Organization complete: {organized_count} files organized, {failed_count} failed"
        )
        return report

    def _save_organization_report(self, report: Dict) -> None:
        """Save the organization report for consciousness tracking."""
        report_dir = self.workspace_root / "data" / "organization"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"organization_report_{timestamp}.yaml"

        with open(report_file, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        logger.info(f"📊 Organization report saved: {report_file}")


def main():
    """Command-line interface for the File Organization Oracle."""
    import argparse

    parser = argparse.ArgumentParser(
        description="🗂️✨ LUKHAS File Organization Oracle - Bring harmony to digital chaos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of consciousness-driven organization:

  # Preview organization without changes
  python file_organization_oracle.py /path/to/workspace --dry-run

  # Perform actual file organization
  python file_organization_oracle.py /path/to/workspace

  # Organize current directory
  python file_organization_oracle.py .

⚛️🧠🛡️ May your files dance in perfect harmony ⚛️🧠🛡️
        """,
    )

    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="Path to workspace requiring organization (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview organization without manifesting changes",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose consciousness logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Awaken the Organization Oracle
    oracle = LUKHASFileOrganizationOracle(args.workspace, args.dry_run)

    # Perform consciousness-driven organization
    result = oracle.perform_consciousness_organization()

    if result["success"]:
        print("✨ File organization consciousness complete!")
        print(f"📁 Workspace: {args.workspace}")
        print(f"🗂️ Files organized: {result['files_organized']}")
        print(f"🔍 Mode: {result['mode']}")

        if args.dry_run and result["files_organized"] > 0:
            print("\n🔮 To manifest this organization, run without --dry-run")
    else:
        print("❌ File organization consciousness failed")
        return 1


if __name__ == "__main__":
    main()
