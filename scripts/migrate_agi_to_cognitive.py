#!/usr/bin/env python3
"""
AGI to Cognitive Migration Script

Systematically migrates 33k+ AGI references to Cognitive across the entire codebase.
Handles class names, function names, documentation, and configuration files while
preserving technical accuracy and semantic meaning.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AGIToCognitiveMigrator:
    """Handles systematic migration from AGI to Cognitive terminology"""

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
            # Full AGI context replacements (more specific first)
            (r'\bAGI System\b', 'Cognitive AI System'),
            (r'\bAGI Framework\b', 'Cognitive AI Framework'),
            (r'\bAGI Architecture\b', 'Cognitive Architecture'),
            (r'\bAGI Development\b', 'Cognitive AI Development'),
            (r'\bAGI Research\b', 'Cognitive AI Research'),
            (r'\bAGI Platform\b', 'Cognitive AI Platform'),
            (r'\bAGI Technology\b', 'Cognitive Technology'),
            (r'\bAGI Implementation\b', 'Cognitive Implementation'),
            (r'\bAGI Core\b', 'Cognitive Core'),
            (r'\bAGI Engine\b', 'Cognitive Engine'),
            (r'\bAGI Model\b', 'Cognitive Model'),
            (r'\bAGI Intelligence\b', 'Cognitive Intelligence'),
            (r'\bAGI Processing\b', 'Cognitive Processing'),
            (r'\bAGI Capabilities\b', 'Cognitive Capabilities'),
            (r'\bAGI Features\b', 'Cognitive Features'),
            (r'\bAGI Components\b', 'Cognitive Components'),
            (r'\bAGI Modules\b', 'Cognitive Modules'),
            (r'\bAGI Services\b', 'Cognitive Services'),
            (r'\bAGI Operations\b', 'Cognitive Operations'),
            (r'\bAGI Orchestration\b', 'Cognitive Orchestration'),
            (r'\bAGI Management\b', 'Cognitive Management'),
            (r'\bAGI Coordination\b', 'Cognitive Coordination'),
            (r'\bAGI Integration\b', 'Cognitive Integration'),
            (r'\bAGI Enhancement\b', 'Cognitive Enhancement'),

            # Artificial General Intelligence full term
            (r'\bArtificial General Intelligence\b', 'Cognitive Artificial Intelligence'),
            (r'\bGeneral AI\b', 'Cognitive AI'),
            (r'\bGeneral Intelligence\b', 'Cognitive Intelligence'),

            # Class names and modules (preserve technical accuracy)
            (r'\bAGIEngine\b', 'CognitiveEngine'),
            (r'\bAGICore\b', 'CognitiveCore'),
            (r'\bAGISystem\b', 'CognitiveSystem'),
            (r'\bAGIManager\b', 'CognitiveManager'),
            (r'\bAGIService\b', 'CognitiveService'),
            (r'\bAGIController\b', 'CognitiveController'),
            (r'\bAGIOrchestrator\b', 'CognitiveOrchestrator'),
            (r'\bAGIMonitor\b', 'CognitiveMonitor'),
            (r'\bAGIHandler\b', 'CognitiveHandler'),
            (r'\bAGIProcessor\b', 'CognitiveProcessor'),
            (r'\bAGIValidator\b', 'CognitiveValidator'),
            (r'\bAGIAdapter\b', 'CognitiveAdapter'),
            (r'\bAGIBridge\b', 'CognitiveBridge'),
            (r'\bAGIIntegrator\b', 'CognitiveIntegrator'),
            (r'\bAGIFramework\b', 'CognitiveFramework'),
            (r'\bAGIArchitecture\b', 'CognitiveArchitecture'),
            (r'\bAGIComponent\b', 'CognitiveComponent'),
            (r'\bAGIModule\b', 'CognitiveModule'),
            (r'\bAGINode\b', 'CognitiveNode'),

            # Variable and function names (camelCase)
            (r'\bagiEngine\b', 'cognitiveEngine'),
            (r'\bagiCore\b', 'cognitiveCore'),
            (r'\bagiSystem\b', 'cognitiveSystem'),
            (r'\bagiManager\b', 'cognitiveManager'),
            (r'\bagiService\b', 'cognitiveService'),
            (r'\bagiController\b', 'cognitiveController'),
            (r'\bagiOrchestrator\b', 'cognitiveOrchestrator'),
            (r'\bagiMonitor\b', 'cognitiveMonitor'),
            (r'\bagiHandler\b', 'cognitiveHandler'),
            (r'\bagiProcessor\b', 'cognitiveProcessor'),
            (r'\bagiValidator\b', 'cognitiveValidator'),
            (r'\bagiAdapter\b', 'cognitiveAdapter'),
            (r'\bagiBridge\b', 'cognitiveBridge'),
            (r'\bagiIntegrator\b', 'cognitiveIntegrator'),
            (r'\bagiFramework\b', 'cognitiveFramework'),
            (r'\bagiArchitecture\b', 'cognitiveArchitecture'),
            (r'\bagiComponent\b', 'cognitiveComponent'),
            (r'\bagiModule\b', 'cognitiveModule'),
            (r'\bagiNode\b', 'cognitiveNode'),

            # Snake case versions
            (r'\bagi_engine\b', 'cognitive_engine'),
            (r'\bagi_core\b', 'cognitive_core'),
            (r'\bagi_system\b', 'cognitive_system'),
            (r'\bagi_manager\b', 'cognitive_manager'),
            (r'\bagi_service\b', 'cognitive_service'),
            (r'\bagi_controller\b', 'cognitive_controller'),
            (r'\bagi_orchestrator\b', 'cognitive_orchestrator'),
            (r'\bagi_monitor\b', 'cognitive_monitor'),
            (r'\bagi_handler\b', 'cognitive_handler'),
            (r'\bagi_processor\b', 'cognitive_processor'),
            (r'\bagi_validator\b', 'cognitive_validator'),
            (r'\bagi_adapter\b', 'cognitive_adapter'),
            (r'\bagi_bridge\b', 'cognitive_bridge'),
            (r'\bagi_integrator\b', 'cognitive_integrator'),
            (r'\bagi_framework\b', 'cognitive_framework'),
            (r'\bagi_architecture\b', 'cognitive_architecture'),
            (r'\bagi_component\b', 'cognitive_component'),
            (r'\bagi_module\b', 'cognitive_module'),
            (r'\bagi_node\b', 'cognitive_node'),

            # Configuration keys and constants
            (r'\bAGI_ENGINE\b', 'COGNITIVE_ENGINE'),
            (r'\bAGI_CORE\b', 'COGNITIVE_CORE'),
            (r'\bAGI_SYSTEM\b', 'COGNITIVE_SYSTEM'),
            (r'\bAGI_ENABLED\b', 'COGNITIVE_ENABLED'),
            (r'\bAGI_CONFIG\b', 'COGNITIVE_CONFIG'),
            (r'\bUSE_AGI\b', 'USE_COGNITIVE'),
            (r'\bENABLE_AGI\b', 'ENABLE_COGNITIVE'),
            (r'\bAGI_MODE\b', 'COGNITIVE_MODE'),
            (r'\bAGI_LEVEL\b', 'COGNITIVE_LEVEL'),

            # File and directory references
            (r'\bagi/', 'cognitive/'),
            (r'\bagi\.', 'cognitive.'),
            (r'\bagi-', 'cognitive-'),
            (r'\bagi_', 'cognitive_'),

            # Documentation and comments - more careful with context
            (r'\bGeneral AI capabilities\b', 'Cognitive AI capabilities'),
            (r'\bGeneral AI features\b', 'Cognitive AI features'),
            (r'\bGeneral AI systems\b', 'Cognitive AI systems'),
            (r'\badvanced AGI\b', 'advanced cognitive AI'),
            (r'\benterprise AGI\b', 'enterprise cognitive AI'),
            (r'\bAGI deployment\b', 'cognitive AI deployment'),
            (r'\bAGI scaling\b', 'cognitive AI scaling'),

            # Generic AGI replacements (last to avoid conflicts)
            (r'\bAGI\b', 'Cognitive AI'),  # Generic AGI to Cognitive AI
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
            with open(file_path, encoding='utf-8') as f:
                f.read(1024)  # Test read
        except (UnicodeDecodeError, UnicodeError, FileNotFoundError):
            return False

        return True

    def migrate_file(self, file_path: Path) -> Tuple[bool, int]:
        """Migrate AGI references in a single file"""
        try:
            with open(file_path, encoding='utf-8') as f:
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
            error_msg = f"Error processing {file_path}: {e!s}"
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

    def generate_report(self) -> str:
        """Generate migration report"""
        report = [
            "# AGI to Cognitive Migration Report",
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

        for pattern, replacement in self.patterns[:15]:  # Show first 15 patterns
            report.append(f"| `{pattern}` | `{replacement}` |")

        if len(self.patterns) > 15:
            report.append(f"| ... and {len(self.patterns) - 15} more patterns | |")

        return '\n'.join(report)

    def get_timestamp(self) -> str:
        """Get current timestamp for reporting"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_migration(self, dry_run: bool = False) -> None:
        """Run the complete migration process"""
        logger.info(f"🚀 Starting AGI to Cognitive migration (dry_run={dry_run})")
        logger.info(f"📁 Root path: {self.root_path}")

        # Scan for files to process
        files_to_process = self.scan_directory(self.root_path)
        logger.info(f"📄 Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            self.stats['files_processed'] += 1

            if dry_run:
                # Just count potential changes
                try:
                    with open(file_path, encoding='utf-8') as f:
                        content = f.read()

                    total_matches = 0
                    for pattern, _replacement in self.patterns:
                        matches = len(re.findall(pattern, content))
                        total_matches += matches

                    if total_matches > 0:
                        logger.info(f"📋 {file_path}: {total_matches} potential changes")

                except Exception as e:
                    logger.error(f"Error previewing {file_path}: {e!s}")
            else:
                modified, count = self.migrate_file(file_path)
                if modified:
                    self.stats['files_modified'] += 1
                    self.stats['replacements_made'] += count

        # Generate and save report
        if not dry_run:
            report = self.generate_report()
            report_path = self.root_path / "migration_agi_to_cognitive_report.md"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📊 Report saved to: {report_path}")

        logger.info("✅ Migration complete!")
        logger.info(f"📈 Summary: {self.stats['files_modified']}/{self.stats['files_processed']} files modified, {self.stats['replacements_made']} replacements")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate AGI references to Cognitive terminology")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--path", default=".", help="Root path to process (default: current directory)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    migrator = AGIToCognitiveMigrator(args.path)
    migrator.run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
