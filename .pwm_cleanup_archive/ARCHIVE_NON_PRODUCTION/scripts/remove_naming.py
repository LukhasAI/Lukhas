#!/usr/bin/env python3
"""
Remove LUKHAS branding from all file names
Following the new naming standard without LUKHAS references
"""

import json
import logging
import re
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LukhasNameRemover:
    """Remove LUKHAS from file names while following naming conventions"""

    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.renames = []
        self.failed = []

    def find_and_rename_all(self):
        """Find all files with LUKHAS in the name and rename them"""
        logger.info(
            f"{'DRY RUN' if self.dry_run else 'APPLYING'} - Removing LUKHAS from file names"
        )

        # Find all files with lukhas/LUKHAS/Lukhas in the name
        patterns = ["*lukhas*", "*LUKHAS*", "*Lukhas*"]

        for pattern in patterns:
            for file_path in self.root_path.rglob(pattern):
                if self._should_skip_path(file_path):
                    continue

                if file_path.is_file():
                    new_name = self._remove_lukhas_from_name(file_path.name)
                    if new_name != file_path.name:
                        self._rename_file(file_path, new_name)

        self._report_results()

    def _remove_lukhas_from_name(self, filename: str) -> str:
        """Remove LUKHAS branding and convert to appropriate naming convention"""
        # Common replacements
        replacements = {
            # Specific known files
            "lukhas_awareness_engine.py": "awareness_engine.py",
            "lukhas_awareness_engine_elevated.py": "awareness_engine_elevated.py",
            "lukhas_es_creativo_clean.py": "creative_personality_clean.py",
            "lukhas_es_creativo.py": "creative_personality.py",
            "unified_lukhasbot.py": "unified_bot.py",
            "working_lukhasbot.py": "working_bot.py",
            "lukhas_core.py": "core_system.py",
            "lukhas_orchestrator.py": "orchestrator_core.py",
            "lukhas_integration_engine.py": "integration_engine.py",
            "brain_core_bridge.py": "brain_bridge.py",
            "lukhas_cycle_phase.py": "cycle_phase.py",
            "lukhas_federated_model.py": "federated_model.py",
            "lukhas_api_client.py": "api_client.py",
            "lukhas_ai_system.py": "ai_system.py",
            "lukhas_safety_bridge.py": "safety_bridge.py",
            "lukhas_flagship_security_engine.py": "flagship_security_engine.py",
            "lukhas_trust_scorer.py": "trust_scorer.py",
            "lukhas_grpc_client.py": "grpc_client.py",
            "lukhas_neural_intelligence.py": "neural_intelligence.py",
            "lukhas_commercial_deployment.py": "commercial_deployment.py",
            "lukhas_orchestrator_emotion_engine.py": "orchestrator_emotion_engine.py",
            "lukhasdream_cli.py": "dream_cli.py",
            "lukhasctl.py": "ctl.py",
        }

        # Check direct replacements first
        lower_filename = filename.lower()
        for old_name, new_name in replacements.items():
            if lower_filename == old_name:
                # Preserve original extension and casing if different
                if filename.endswith(".py"):
                    return new_name
                else:
                    # Handle other extensions
                    ext = Path(filename).suffix
                    return Path(new_name).stem + ext

        # Generic replacement patterns
        result = filename

        # Remove LUKHAS prefix variations
        patterns = [
            (r"^LUKHAS", ""),  # LUKHAS at start
            (r"^Lukhas", ""),  # Lukhas at start
            (r"^lukhas_", ""),  # lukhas_ at start
            (r"^lukhas", ""),  # lukhas at start (no underscore)
            (r"_lukhas_", "_"),  # _lukhas_ in middle
            (r"_LUKHAS_", "_"),  # _LUKHAS_ in middle
            (r"lukhas_", ""),  # lukhas_ anywhere
            (r"LUKHAS", ""),  # LUKHAS anywhere
            (r"Lukhas", ""),  # Lukhas anywhere
        ]

        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)

        # Clean up any double underscores or leading underscores
        result = re.sub(r"__+", "_", result)
        result = re.sub(r"^_+", "", result)

        # If result is empty or just an extension, use a generic name
        if not result or result.startswith("."):
            base = "system"
            if "bot" in filename.lower():
                base = "bot"
            elif "engine" in filename.lower():
                base = "engine"
            elif "core" in filename.lower():
                base = "core"
            result = base + Path(filename).suffix

        return result

    def _rename_file(self, current_path: Path, new_name: str):
        """Rename a single file"""
        new_path = current_path.parent / new_name

        logger.info(
            f"\n{'Would rename' if self.dry_run else 'Renaming'}: {current_path.name} → {new_name}"
        )
        logger.info(f"  Path: {current_path.relative_to(self.root_path)}")

        if not self.dry_run:
            try:
                # Check if target exists
                if new_path.exists() and new_path != current_path:
                    logger.error(f"  ✗ Target already exists: {new_name}")
                    self.failed.append(
                        {
                            "file": str(current_path),
                            "reason": "Target file exists",
                            "suggested": new_name,
                        }
                    )
                    return

                # Rename file
                current_path.rename(new_path)
                logger.info("  ✓ Renamed successfully")

                self.renames.append(
                    {
                        "old_path": str(current_path),
                        "new_path": str(new_path),
                        "old_name": current_path.name,
                        "new_name": new_name,
                    }
                )

            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                self.failed.append(
                    {"file": str(current_path), "reason": str(e), "suggested": new_name}
                )

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {
            "__pycache__",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".git",
            "build",
            "dist",
            ".eggs",
            ".pytest_cache",
        }

        # Skip certain files
        skip_files = {
            "NAMING_GUIDE.md",  # Keep the naming guide
            "naming_conventions_for_lukhas.md",  # Documentation
        }

        if path.name in skip_files:
            return True

        return any(part in skip_dirs for part in path.parts)

    def _report_results(self):
        """Generate report of changes"""
        logger.info("\n" + "=" * 80)
        logger.info("RENAME COMPLETE")
        logger.info(
            f"Files {'identified' if self.dry_run else 'renamed'}: {len(self.renames)}"
        )
        logger.info(f"Failures: {len(self.failed)}")
        logger.info("=" * 80)

        if self.failed:
            logger.info("\nFailed renames:")
            for fail in self.failed:
                logger.info(f"  - {fail['file']}: {fail['reason']}")

        # Save report
        report = {
            "renames": self.renames,
            "failed": self.failed,
            "total_renamed": len(self.renames),
            "total_failed": len(self.failed),
            "dry_run": self.dry_run,
        }

        report_path = self.root_path / "lukhas_removal_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nReport saved to: {report_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove LUKHAS branding from file names"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be renamed without making changes (default)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually apply the renames"
    )

    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    root_path = Path(args.path).resolve()
    if not root_path.exists():
        logger.error(f"Path does not exist: {root_path}")
        sys.exit(1)

    remover = LukhasNameRemover(root_path, dry_run=args.dry_run)
    remover.find_and_rename_all()


if __name__ == "__main__":
    main()
