#!/usr/bin/env python3
"""
Trinity to Constellation Framework Migration Script

Systematically migrates 14k+ Trinity references to Constellation across the entire codebase.
Handles imports, class names, function names, documentation, and configuration files.
"""

import logging
import os
import re
from pathlib import Path
from typing import List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TrinityToConstellationMigrator:
    """Handles systematic migration from Trinity to Constellation Framework"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'replacements_made': 0,
            'errors': []
        }

        # Core migration patterns - order matters for proper replacement
        self.patterns = [
            # Framework names (case sensitive)
            (r'\bTrinity Framework\b', 'Constellation Framework'),
            (r'\bTRINITY FRAMEWORK\b', 'CONSTELLATION FRAMEWORK'),
            (r'\btrinity framework\b', 'constellation framework'),

            # Class names and modules
            (r'\bTrinityFramework\b', 'ConstellationFramework'),
            (r'\bTrinityEngine\b', 'ConstellationEngine'),
            (r'\bTrinityCore\b', 'ConstellationCore'),
            (r'\bTrinitySystem\b', 'ConstellationSystem'),
            (r'\bTrinityManager\b', 'ConstellationManager'),
            (r'\bTrinityService\b', 'ConstellationService'),
            (r'\bTrinityController\b', 'ConstellationController'),
            (r'\bTrinityOrchestrator\b', 'ConstellationOrchestrator'),
            (r'\bTrinityMonitor\b', 'ConstellationMonitor'),
            (r'\bTrinityHandler\b', 'ConstellationHandler'),
            (r'\bTrinityProcessor\b', 'ConstellationProcessor'),
            (r'\bTrinityValidator\b', 'ConstellationValidator'),
            (r'\bTrinityAdapter\b', 'ConstellationAdapter'),
            (r'\bTrinityBridge\b', 'ConstellationBridge'),
            (r'\bTrinityIntegrator\b', 'ConstellationIntegrator'),

            # Variable and function names (camelCase and snake_case)
            (r'\btrinityFramework\b', 'constellationFramework'),
            (r'\btrinityEngine\b', 'constellationEngine'),
            (r'\btrinityCore\b', 'constellationCore'),
            (r'\btrinitySystem\b', 'constellationSystem'),
            (r'\btrinityManager\b', 'constellationManager'),
            (r'\btrinityService\b', 'constellationService'),
            (r'\btrinityController\b', 'constellationController'),
            (r'\btrinityOrchestrator\b', 'constellationOrchestrator'),
            (r'\btrinityMonitor\b', 'constellationMonitor'),
            (r'\btrinityHandler\b', 'constellationHandler'),
            (r'\btrinityProcessor\b', 'constellationProcessor'),
            (r'\btrinityValidator\b', 'constellationValidator'),
            (r'\btrinityAdapter\b', 'constellationAdapter'),
            (r'\btrinityBridge\b', 'constellationBridge'),
            (r'\btrinityIntegrator\b', 'constellationIntegrator'),

            # Snake case versions
            (r'\btrinity_framework\b', 'constellation_framework'),
            (r'\btrinity_engine\b', 'constellation_engine'),
            (r'\btrinity_core\b', 'constellation_core'),
            (r'\btrinity_system\b', 'constellation_system'),
            (r'\btrinity_manager\b', 'constellation_manager'),
            (r'\btrinity_service\b', 'constellation_service'),
            (r'\btrinity_controller\b', 'constellation_controller'),
            (r'\btrinity_orchestrator\b', 'constellation_orchestrator'),
            (r'\btrinity_monitor\b', 'constellation_monitor'),
            (r'\btrinity_handler\b', 'constellation_handler'),
            (r'\btrinity_processor\b', 'constellation_processor'),
            (r'\btrinity_validator\b', 'constellation_validator'),
            (r'\btrinity_adapter\b', 'constellation_adapter'),
            (r'\btrinity_bridge\b', 'constellation_bridge'),
            (r'\btrinity_integrator\b', 'constellation_integrator'),

            # Configuration keys and constants
            (r'\bTRINITY_FRAMEWORK\b', 'CONSTELLATION_FRAMEWORK'),
            (r'\bTRINITY_ENGINE\b', 'CONSTELLATION_ENGINE'),
            (r'\bTRINITY_CORE\b', 'CONSTELLATION_CORE'),
            (r'\bTRINITY_SYSTEM\b', 'CONSTELLATION_SYSTEM'),
            (r'\bTRINITY_ENABLED\b', 'CONSTELLATION_ENABLED'),
            (r'\bTRINITY_CONFIG\b', 'CONSTELLATION_CONFIG'),
            (r'\bUSE_TRINITY\b', 'USE_CONSTELLATION'),
            (r'\bENABLE_TRINITY\b', 'ENABLE_CONSTELLATION'),

            # File and directory references
            (r'\btrinity/', 'constellation/'),
            (r'\btrinity\.', 'constellation.'),
            (r'\btrinity-', 'constellation-'),
            (r'\btrinity_', 'constellation_'),

            # Documentation and comments
            (r'\btrinity\b', 'constellation'),  # Generic trinity to constellation
            (r'\bTrinity\b', 'Constellation'),  # Generic Trinity to Constellation
            (r'\bTRINITY\b', 'CONSTELLATION'),  # Generic TRINITY to CONSTELLATION
        ]

        # Files to exclude from migration
        self.excluded_files = {
            '.git',
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            'venv',
            '.venv',
            'env',
            '.env',
            'reports',
            '.claude',
        }

        # File extensions to process
        self.target_extensions = {
            '.py', '.md', '.yml', '.yaml', '.json', '.txt', '.sh', '.js', '.ts',
            '.html', '.css', '.xml', '.cfg', '.conf', '.ini', '.toml'
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed for migration"""
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            return False

        # Skip excluded directories
        for part in file_path.parts:
            if part in self.excluded_files:
                return False

        # Only process target file types
        if file_path.suffix not in self.target_extensions:
            return False

        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Test read
        except (UnicodeDecodeError, UnicodeError, FileNotFoundError):
            return False

        return True

    def migrate_file(self, file_path: Path) -> Tuple[bool, int]:
        """Migrate Trinity references in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            modified_content = original_content
            replacements_count = 0

            # Apply all migration patterns
            for pattern, replacement in self.patterns:
                new_content, count = re.subn(pattern, replacement, modified_content)
                modified_content = new_content
                replacements_count += count

            # Write back if modifications were made
            if replacements_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)

                logger.info(f"✅ {file_path}: {replacements_count} replacements")
                return True, replacements_count

            return False, 0

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False, 0

    def scan_directory(self, directory: Path) -> List[Path]:
        """Recursively scan directory for files to process"""
        files_to_process = []

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_files]

            for file_name in files:
                file_path = Path(root) / file_name
                if self.should_process_file(file_path):
                    files_to_process.append(file_path)

        return files_to_process

    def preview_changes(self, file_path: Path) -> List[Tuple[str, str, str]]:
        """Preview changes that would be made to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            changes = []
            for pattern, replacement in self.patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)

                    line = content[line_start:line_end]
                    changes.append((pattern, replacement, line.strip()))

            return changes

        except Exception as e:
            logger.error(f"Error previewing {file_path}: {str(e)}")
            return []

    def generate_report(self) -> str:
        """Generate migration report"""
        report = [
            "# Trinity to Constellation Migration Report",
            f"**Generated**: {self.get_timestamp()}",
            "",
            "## Summary",
            f"- Files processed: {self.stats['files_processed']}",
            f"- Files modified: {self.stats['files_modified']}",
            f"- Total replacements: {self.stats['replacements_made']}",
            f"- Errors: {len(self.stats['errors'])}",
            "",
        ]

        if self.stats['errors']:
            report.extend([
                "## Errors",
                "",
            ])
            for error in self.stats['errors']:
                report.append(f"- {error}")
            report.append("")

        report.extend([
            "## Migration Patterns Applied",
            "",
            "| Pattern | Replacement |",
            "|---------|-------------|",
        ])

        for pattern, replacement in self.patterns[:10]:  # Show first 10 patterns
            report.append(f"| `{pattern}` | `{replacement}` |")

        if len(self.patterns) > 10:
            report.append(f"| ... and {len(self.patterns) - 10} more patterns | |")

        return '\n'.join(report)

    def get_timestamp(self) -> str:
        """Get current timestamp for reporting"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_migration(self, dry_run: bool = False) -> None:
        """Run the complete migration process"""
        logger.info(f"🚀 Starting Trinity to Constellation migration (dry_run={dry_run})")
        logger.info(f"📁 Root path: {self.root_path}")

        # Scan for files to process
        files_to_process = self.scan_directory(self.root_path)
        logger.info(f"📄 Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            self.stats['files_processed'] += 1

            if dry_run:
                changes = self.preview_changes(file_path)
                if changes:
                    logger.info(f"📋 {file_path}: {len(changes)} potential changes")
                    for pattern, replacement, line in changes[:3]:  # Show first 3
                        logger.info(f"   - Line: {line}")
                        logger.info(f"     {pattern} -> {replacement}")
            else:
                modified, count = self.migrate_file(file_path)
                if modified:
                    self.stats['files_modified'] += 1
                    self.stats['replacements_made'] += count

        # Generate and save report
        report = self.generate_report()
        report_path = self.root_path / "migration_trinity_to_constellation_report.md"

        if not dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📊 Report saved to: {report_path}")

        logger.info("✅ Migration complete!")
        logger.info(f"📈 Summary: {self.stats['files_modified']}/{self.stats['files_processed']} files modified, {self.stats['replacements_made']} replacements")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate Trinity references to Constellation Framework")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--path", default=".", help="Root path to process (default: current directory)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    migrator = TrinityToConstellationMigrator(args.path)
    migrator.run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
