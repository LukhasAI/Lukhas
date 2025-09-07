#!/usr/bin/env python3
"""
LUKHAS AI Path Migration Script
Updates all scripts to use the new directory structure
"""
import re
from pathlib import Path

# Import the path manager
from lukhas_paths import paths


class PathMigrator:
    """Migrates scripts to use new directory paths"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.migration_log = []

        # Path mappings for common patterns
        self.path_mappings = {
            # Direct old -> new mappings
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams"': f'"{paths.assets_dreams}"',
            r"'/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams'": f"'{paths.assets_dreams}'",
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security"': f'"{paths.reports_security}"',
            r"'/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security'": f"'{paths.reports_security}'",
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms"': f'"{paths.deployment_platforms}"',
            r"'/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms'": f"'{paths.deployment_platforms}'",
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/demos"': f'"{paths.demos}"',
            r"'/Users/agi_dev/LOCAL-REPOS/Lukhas/demos'": f"'{paths.demos}'",
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/performance"': f'"{paths.performance}"',
            r"'/Users/agi_dev/LOCAL-REPOS/Lukhas/performance'": f"'{paths.performance}'",
            # Path construction patterns
            r'Path\("/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams"\)': f'Path("{paths.assets_dreams}")',
            r'Path\("/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security"\)': f'Path("{paths.reports_security}")',
            r'Path\("/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms"\)': f'Path("{paths.deployment_platforms}")',
            r'Path\("/Users/agi_dev/LOCAL-REPOS/Lukhas/demos"\)': f'Path("{paths.demos}")',
            r'Path\("/Users/agi_dev/LOCAL-REPOS/Lukhas/performance"\)': f'Path("{paths.performance}")',
            # Complex path operations
            r'project_root / "/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams"': "paths.assets_dreams",
            r'project_root / "/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security"': "paths.reports_security",
            r'project_root / "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms"': "paths.deployment_platforms",
            r'project_root / "/Users/agi_dev/LOCAL-REPOS/Lukhas/demos"': "paths.demos",
            r'project_root / "/Users/agi_dev/LOCAL-REPOS/Lukhas/performance"': "paths.performance",
            # File path patterns
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams/': f'"{paths.assets_dreams}/',
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security/': f'"{paths.reports_security}/',
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms/': f'"{paths.deployment_platforms}/',
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/demos/': f'"{paths.demos}/',
            r'"/Users/agi_dev/LOCAL-REPOS/Lukhas/performance/': f'"{paths.performance}/',
        }

    def find_python_files(self) -> list[Path]:
        """Find all Python files that might need updating"""
        python_files = []

        # Search in key directories
        search_dirs = [
            "scripts",
            "branding",
            "tools",
            "lambda_products",
            "tests",
            "api",
            "candidate",
            ".",  # Root directory
        ]

        for search_dir in search_dirs:
            dir_path = self.project_root / search_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    # Skip __pycache__ and other build directories
                    if "__pycache__" not in str(py_file) and ".venv" not in str(py_file):
                        python_files.append(py_file)

        return python_files

    def needs_migration(self, file_path: Path) -> bool:
        """Check if file contains deprecated paths"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for any deprecated path patterns
            deprecated_patterns = [
                "/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams",
                "/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security",
                "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms",
                "/Users/agi_dev/LOCAL-REPOS/Lukhas/demos",
                "perf/",
                "node_configs",
            ]

            return any(pattern in content for pattern in deprecated_patterns)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return False

    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file to use new paths"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Apply all path mappings
            updated_content = original_content
            changes_made = []

            for old_pattern, new_replacement in self.path_mappings.items():
                if re.search(old_pattern, updated_content):
                    updated_content = re.sub(old_pattern, new_replacement, updated_content)
                    changes_made.append(f"{old_pattern} -> {new_replacement}")

            # If changes were made, write the file and add import
            if changes_made:
                # Add import for paths at the top if needed
                if "paths." in updated_content and "from lukhas_paths import paths" not in updated_content:
                    # Find the last import statement or add after initial comments
                    lines = updated_content.split("\n")
                    insert_line = 0

                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        insert_line = i + 1
                    elif line.strip() and not line.startswith("# ") and not line.startswith('"""'):
                        break

                lines.insert(insert_line, "from lukhas_paths import paths")
                updated_content = "\n".join(lines)
                changes_made.append("Added lukhas_paths import")  # Write the updated file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

                self.migration_log.append({"file": str(file_path), "changes": changes_made})

                print(f"✅ Updated {file_path}")
                for change in changes_made:
                    print(f"    - {change}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error migrating {file_path}: {e}")
            return False

    def run_migration(self):
        """Run the complete path migration"""
        print("🚀 Starting LUKHAS AI Path Migration")
        print("=" * 50)

        # Find all Python files
        python_files = self.find_python_files()
        print(f"📂 Found {len(python_files)} Python files")

        # Filter files that need migration
        files_to_migrate = [f for f in python_files if self.needs_migration(f)]
        print(f"🔄 {len(files_to_migrate)} files need path updates")

        if not files_to_migrate:
            print("✅ No files need migration!")
            return

        # Migrate each file
        migrated_count = 0
        for file_path in files_to_migrate:
            if self.migrate_file(file_path):
                migrated_count += 1

        print("\n" + "=" * 50)
        print("✅ Migration complete!")
        print(f"📊 {migrated_count}/{len(files_to_migrate)} files updated")

        # Save migration log
        if self.migration_log:
            log_path = self.project_root / "reports" / "deployment" / "path_migration_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            import json

            with open(log_path, "w") as f:
                json.dump(self.migration_log, f, indent=2)

            print(f"📋 Migration log saved to {log_path}")


if __name__ == "__main__":
    migrator = PathMigrator()
    migrator.run_migration()
