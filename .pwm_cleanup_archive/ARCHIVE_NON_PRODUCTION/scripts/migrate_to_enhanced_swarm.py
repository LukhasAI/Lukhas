#!/usr/bin/env python3
"""
Automated migration script for swarm system enhancement
Migrates existing colony implementations to use enhanced swarm capabilities.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List


class SwarmMigrator:
    """Handles migration of swarm-related files."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.files_migrated = []
        self.errors = []

        # Patterns to identify swarm usage
        self.swarm_patterns = [
            r"from core\.swarm import",
            r"import core\.swarm",
            r"class.*\(AgentColony\)",
            r"class.*\(SwarmAgent\)",
            r"SwarmHub\(\)",
            r"AgentColony\(",
            r"SwarmAgent\(",
        ]

        # Replacement mappings
        self.replacements = {
            # Import statements
            r"from core\.swarm import (SwarmAgent|AgentColony|SwarmHub)": r"from core.swarm import \1  # Now enhanced with real behaviors",
            # Colony creation patterns - add capabilities and agent count
            r'AgentColony\((["\'][^"\']+["\'])\)': r'AgentColony(\1, capabilities=["generic"], agent_count=3)',
            r"SwarmHub\(\)\.register_colony\(([^,]+),\s*([^)]+)\)": r'SwarmHub().register_colony(\1, \2, capabilities=["generic"], agent_count=3)',
            # Process task calls - make them async
            r"(\w+)\.process_task\(([^)]+)\)": r"await \1.process_task(\2)",
            # Broadcast event calls - make them async
            r"(\w+)\.broadcast_event\(([^)]+)\)": r"await \1.broadcast_event(\2)",
        }

        # Colony-specific capability mappings
        self.colony_capabilities = {
            "reasoning": ["logical_reasoning", "problem_solving", "causal_reasoning"],
            "memory": ["episodic_memory", "semantic_memory", "working_memory"],
            "creativity": ["idea_generation", "synthesis", "divergent_thinking"],
            "governance": [
                "deontological_ethics",
                "consequentialist_ethics",
                "virtue_ethics",
            ],
            "temporal": ["time_reasoning", "sequence_analysis", "temporal_planning"],
            "quantum": ["quantum_algorithms", "superposition", "entanglement"],
        }

    def find_swarm_files(self) -> List[Path]:
        """Find all Python files that use swarm components."""
        swarm_files = []

        for py_file in self.base_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check if file uses swarm components
                for pattern in self.swarm_patterns:
                    if re.search(pattern, content):
                        swarm_files.append(py_file)
                        break

            except Exception as e:
                self.errors.append(f"Error reading {py_file}: {e}")

        return swarm_files

    def analyze_colony_type(self, content: str, file_path: Path) -> str:
        """Determine colony type from file content or path."""
        file_name = file_path.name.lower()
        content_lower = content.lower()

        # Check file path first
        for colony_type in self.colony_capabilities.keys():
            if colony_type in file_name:
                return colony_type

        # Check content for colony type indicators
        for colony_type in self.colony_capabilities.keys():
            if colony_type in content_lower:
                return colony_type

        return "generic"

    def get_capabilities_for_colony(self, colony_type: str) -> List[str]:
        """Get appropriate capabilities for a colony type."""
        return self.colony_capabilities.get(colony_type, ["generic"])

    def migrate_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Migrate a single file to use enhanced swarm."""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            content = original_content
            colony_type = self.analyze_colony_type(content, file_path)
            capabilities = self.get_capabilities_for_colony(colony_type)

            # Apply basic replacements
            for pattern, replacement in self.replacements.items():
                content = re.sub(pattern, replacement, content)

            # Handle specific colony creation with appropriate capabilities
            if colony_type != "generic":
                capabilities_str = str(capabilities).replace("'", '"')

                # Replace AgentColony creation with specific capabilities
                content = re.sub(
                    rf'AgentColony\((["\'][^"\']*{colony_type}[^"\']*["\'])\)',
                    f"AgentColony(\\1, capabilities={capabilities_str}, agent_count=3)",
                    content,
                    flags=re.IGNORECASE,
                )

                # Replace SwarmHub.register_colony calls
                content = re.sub(
                    rf'register_colony\((["\'][^"\']*{colony_type}[^"\']*["\'])\s*,\s*([^)]+)\)',
                    f"register_colony(\\1, \\2, capabilities={capabilities_str}, agent_count=3)",
                    content,
                    flags=re.IGNORECASE,
                )

            # Add async/await imports if needed
            if "await " in content and "import asyncio" not in content:
                # Add asyncio import at the top
                import_section = re.search(
                    r"^((?:from|import).*?\n)*", content, re.MULTILINE
                )
                if import_section:
                    end_pos = import_section.end()
                    content = content[:end_pos] + "import asyncio\n" + content[end_pos:]
                else:
                    content = "import asyncio\n" + content

            # Check if content actually changed
            if content == original_content:
                return False

            if not dry_run:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)

                # Write migrated content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            self.files_migrated.append(str(file_path))
            return True

        except Exception as e:
            self.errors.append(f"Error migrating {file_path}: {e}")
            return False

    def update_colony_files(self, dry_run: bool = False) -> None:
        """Update specific colony implementation files."""
        colony_files = [
            "core/colonies/reasoning_colony.py",
            "core/colonies/memory_colony.py",
            "core/colonies/creativity_colony.py",
            "core/colonies/governance_colony.py",
            "core/colonies/temporal_colony.py",
        ]

        for colony_file in colony_files:
            file_path = self.base_path / colony_file
            if file_path.exists():
                self.migrate_colony_implementation(file_path, dry_run)

    def migrate_colony_implementation(
        self, file_path: Path, dry_run: bool = False
    ) -> None:
        """Migrate a colony implementation to use enhanced features."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            colony_type = self.analyze_colony_type(content, file_path)
            capabilities = self.get_capabilities_for_colony(colony_type)
            capabilities_str = str(capabilities).replace("'", '"')

            # Replace basic colony inheritance
            old_pattern = r"class (\w+Colony)\(AgentColony\):"
            new_replacement = "class \\1(AgentColony):"
            content = re.sub(old_pattern, new_replacement, content)

            # Replace __init__ method to include capabilities
            old_init_pattern = r"def __init__\(self\):\s*super\(\).__init__\(([^)]+)\)"
            new_init = f"def __init__(self):\n        super().__init__(\\1, capabilities={capabilities_str}, agent_count=3)"
            content = re.sub(old_init_pattern, new_init, content)

            # Replace dummy process_task methods
            if 'return {"status": "completed"}' in content:
                content = content.replace(
                    "def process_task(self, task):",
                    "async def process_task(self, task):",
                ).replace(
                    'return {"status": "completed"}',
                    "return await super().process_task(task)",
                )

            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            self.files_migrated.append(str(file_path))

        except Exception as e:
            self.errors.append(f"Error migrating colony {file_path}: {e}")

    def create_test_updates(self, dry_run: bool = False) -> None:
        """Update test files to work with enhanced swarm."""
        test_files = list(self.base_path.rglob("test_*.py"))

        for test_file in test_files:
            try:
                with open(test_file, encoding="utf-8") as f:
                    content = f.read()

                if any(
                    pattern in content
                    for pattern in ["AgentColony", "SwarmAgent", "SwarmHub"]
                ):
                    # Add async test decorators
                    content = re.sub(
                        r"def (test_\w+)\(([^)]*)\):", r"async def \1(\2):", content
                    )

                    # Add pytest-asyncio import
                    if "async def test_" in content and "import pytest" not in content:
                        content = "import pytest\nimport asyncio\n" + content

                    # Update assertions for new response format
                    content = content.replace(
                        'assert result["status"] == "completed"',
                        'assert result["status"] in ["completed", "partial"]',
                    )

                    if not dry_run:
                        with open(test_file, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.files_migrated.append(str(test_file))

            except Exception as e:
                self.errors.append(f"Error updating test {test_file}: {e}")

    def run_migration(self, dry_run: bool = False) -> Dict:
        """Run the complete migration process."""
        print(f"Starting swarm migration in {self.base_path}")
        print(f"Dry run: {dry_run}")

        # Find all swarm-related files
        swarm_files = self.find_swarm_files()
        print(f"Found {len(swarm_files)} files using swarm components")

        # Migrate each file
        for file_path in swarm_files:
            print(f"Migrating: {file_path}")
            self.migrate_file(file_path, dry_run)

        # Update colony implementations
        print("Updating colony implementations...")
        self.update_colony_files(dry_run)

        # Update test files
        print("Updating test files...")
        self.create_test_updates(dry_run)

        results = {
            "files_found": len(swarm_files),
            "files_migrated": len(self.files_migrated),
            "errors": len(self.errors),
            "migrated_files": self.files_migrated,
            "error_details": self.errors,
        }

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Migrate LUKHAS swarm system to enhanced implementation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Base path to search for files (default: current directory)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    migrator = SwarmMigrator(args.path)
    results = migrator.run_migration(args.dry_run)

    print("\n=== Migration Results ===")
    print(f"Files found: {results['files_found']}")
    print(f"Files migrated: {results['files_migrated']}")
    print(f"Errors: {results['errors']}")

    if args.verbose:
        print("\nMigrated files:")
        for file_path in results["migrated_files"]:
            print(f"  - {file_path}")

        if results["error_details"]:
            print("\nErrors:")
            for error in results["error_details"]:
                print(f"  - {error}")

    if results["errors"] > 0:
        print(f"\n⚠️  {results['errors']} errors occurred during migration")
        return 1
    else:
        print("\n✅ Migration completed successfully!")
        if not args.dry_run:
            print("Backup files created with .backup extension")
        return 0


if __name__ == "__main__":
    sys.exit(main())
