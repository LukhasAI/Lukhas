#!/usr/bin/env python3
"""
LUKHAS Codebase Hygiene - Automated Rename Execution
Performs high-stakes naming cleanup before commercial rollout
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


class CodebaseHygieneExecutor:
    """Execute comprehensive codebase naming cleanup"""

    def __init__(self):
        self.workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
        self.backup_dir = (
            self.workspace
            / f".hygiene_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.changes_log = []
        self.import_updates = {}

        # Define rename mappings
        self.directory_renames = {
            "dreams": "dreams",
            "governance_extended": "governance_extended",
            "personality": "personality",
            "ethics_guard": "ethics_guard",
            "awareness_protocol": "awareness_protocol",
            "brain_core": "brain_core",
            "identity_legacy": "identity_legacy",
            "identity_legacy_enhanced": "identity_enhanced",
            "lambda_identity": "lambda_identity",
            "next_gen": "next_gen",
            "orb": "orb",
            "demo_suite": "demo_suite",
            "dna_link": "dna_link",
            "config_legacy": "config_legacy",
            "data_legacy": "data_legacy",
        }

        self.file_renames = {
            "tools/analysis/_OPERATIONAL_SUMMARY.py": "tools/analysis/operational_summary.py",
            "tools/analysis/_FUNCTIONAL_ANALYSIS.py": "tools/analysis/functional_analysis.py",
            "tools/analysis/_WORKSPACE_STATUS_ANALYSIS.py": "tools/analysis/workspace_status.py",
            "tools/analysis/_SECURITY_COMPLIANCE_GAP_ANALYSIS.py": "tools/analysis/security_gap_analysis.py",
            "tools/analysis/_TARGETED_IMPORT_FIXER.py": "tools/analysis/import_fixer.py",
            "tools/analysis/_CIRCULAR_DEPENDENCY_ANALYSIS.py": "tools/analysis/circular_dependency_analysis.py",
            "tools/analysis/_ROOT_DIRECTORY_AUDIT.py": "tools/analysis/root_directory_audit.py",
            "tools/analysis/_IMPORT_SUCCESS_SUMMARY.py": "tools/analysis/import_success_summary.py",
            "tools/analysis/_STREAMLINE_ANALYZER.py": "tools/analysis/streamline_analyzer.py",
            "tools/analysis/_CURRENT_CONNECTIVITY_ANALYSIS.py": "tools/analysis/connectivity_analysis.py",
            "core/orchestration/lukhas_orchestrator.py": "core/orchestration/main_orchestrator.py",
            "tools/legacy_analysis": "tools/deprecated",
        }

    def create_backup(self):
        """Create backup of directories to be renamed"""
        print(f"\n📦 Creating backup at {self.backup_dir}")
        self.backup_dir.mkdir(exist_ok=True)

        # Backup directories
        for old_name in self.directory_renames:
            old_path = self.workspace / old_name
            if old_path.exists():
                backup_path = self.backup_dir / old_name
                print(f"  Backing up: {old_name}")
                shutil.copytree(old_path, backup_path)

        # Backup files
        for old_file in self.file_renames:
            old_path = self.workspace / old_file
            if old_path.exists():
                backup_path = self.backup_dir / old_file
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Backing up: {old_file}")
                if old_path.is_dir():
                    shutil.copytree(old_path, backup_path)
                else:
                    shutil.copy2(old_path, backup_path)

    def execute_directory_renames(self):
        """Execute directory renames"""
        print("\n📁 Executing directory renames...")

        for old_name, new_name in self.directory_renames.items():
            old_path = self.workspace / old_name
            new_path = self.workspace / new_name

            if old_path.exists():
                if new_path.exists():
                    print(f"  ⚠️  Target exists, merging: {old_name} → {new_name}")
                    # Merge contents instead of replacing
                    self._merge_directories(old_path, new_path)
                    shutil.rmtree(old_path)
                else:
                    print(f"  ✅ Renaming: {old_name} → {new_name}")
                    shutil.move(str(old_path), str(new_path))

                self.changes_log.append(
                    {
                        "type": "directory",
                        "old": old_name,
                        "new": new_name,
                        "status": "success",
                    }
                )

                # Track import updates needed
                self.import_updates[old_name] = new_name
            else:
                print(f"  ⏭️  Skip (not found): {old_name}")

    def execute_file_renames(self):
        """Execute file renames"""
        print("\n📄 Executing file renames...")

        for old_file, new_file in self.file_renames.items():
            old_path = self.workspace / old_file
            new_path = self.workspace / new_file

            if old_path.exists():
                if old_path.is_dir():
                    # Handle directory rename in file_renames
                    if new_path.exists():
                        print(f"  ⚠️  Target exists: {old_file}")
                    else:
                        print(f"  ✅ Renaming directory: {old_file} → {new_file}")
                        shutil.move(str(old_path), str(new_path))
                else:
                    # Regular file rename
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ Renaming: {old_file} → {new_file}")
                    shutil.move(str(old_path), str(new_path))

                self.changes_log.append(
                    {
                        "type": "file",
                        "old": old_file,
                        "new": new_file,
                        "status": "success",
                    }
                )
            else:
                print(f"  ⏭️  Skip (not found): {old_file}")

    def _merge_directories(self, source: Path, target: Path):
        """Merge source directory into target"""
        for item in source.iterdir():
            target_item = target / item.name
            if item.is_dir():
                target_item.mkdir(exist_ok=True)
                self._merge_directories(item, target_item)
            else:
                if not target_item.exists():
                    shutil.copy2(item, target_item)

    def update_imports(self):
        """Update imports across all Python files"""
        print("\n🔄 Updating imports across codebase...")

        import_patterns = []
        for old_name, new_name in self.import_updates.items():
            # Create regex patterns for different import styles
            import_patterns.extend(
                [
                    (f"from {old_name}", f"from {new_name}"),
                    (f"import {old_name}", f"import {new_name}"),
                    (f'"{old_name}', f'"{new_name}'),
                    (f"'{old_name}", f"'{new_name}"),
                ]
            )

        # Update imports in all Python files
        updated_files = 0
        for py_file in self.workspace.rglob("*.py"):
            if ".hygiene_backup" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                for old_pattern, new_pattern in import_patterns:
                    content = content.replace(old_pattern, new_pattern)

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_files += 1

            except Exception as e:
                print(f"  ⚠️  Error updating {py_file}: {e}")

        print(f"  ✅ Updated imports in {updated_files} files")

    def consolidate_sparse_modules(self):
        """Consolidate single-purpose files into cohesive modules"""
        print("\n🔀 Consolidating sparse modules...")

        # Example: Consolidate governance_extended subdirectories
        gov_extended = self.workspace / "governance_extended"
        if gov_extended.exists():
            consolidated_content = []
            consolidated_content.append('"""')
            consolidated_content.append("Consolidated Governance Extended Module")
            consolidated_content.append(
                "Combines audit_logger, compliance_hooks, and policy_manager"
            )
            consolidated_content.append('"""')
            consolidated_content.append("")

            for subdir in ["audit_logger", "compliance_hooks", "policy_manager"]:
                subdir_path = gov_extended / subdir
                if subdir_path.exists():
                    init_file = subdir_path / "__init__.py"
                    if init_file.exists():
                        with open(init_file) as f:
                            content = f.read()
                            if content.strip():
                                consolidated_content.append(f"# --- {subdir} ---")
                                consolidated_content.append(content)
                                consolidated_content.append("")

            # Write consolidated module
            if len(consolidated_content) > 5:
                consolidated_file = gov_extended.parent / "governance_extended.py"
                with open(consolidated_file, "w") as f:
                    f.write("\n".join(consolidated_content))
                print("  ✅ Created consolidated: governance_extended.py")

    def generate_report(self):
        """Generate hygiene report"""
        print("\n📊 Generating hygiene report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "changes": self.changes_log,
            "summary": {
                "directories_renamed": len(
                    [c for c in self.changes_log if c["type"] == "directory"]
                ),
                "files_renamed": len(
                    [c for c in self.changes_log if c["type"] == "file"]
                ),
                "total_changes": len(self.changes_log),
            },
        }

        report_path = self.workspace / "CODEBASE_HYGIENE_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"  ✅ Report saved to: {report_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 HYGIENE SUMMARY")
        print("=" * 60)
        print(f"Directories renamed: {report['summary']['directories_renamed']}")
        print(f"Files renamed: {report['summary']['files_renamed']}")
        print(f"Total changes: {report['summary']['total_changes']}")
        print(f"Backup location: {self.backup_dir}")

    def execute(self):
        """Execute the complete hygiene process"""
        print("=" * 60)
        print("🧹 LUKHAS CODEBASE HYGIENE EXECUTION")
        print("=" * 60)

        # Create backup
        self.create_backup()

        # Execute renames
        self.execute_directory_renames()
        self.execute_file_renames()

        # Update imports
        self.update_imports()

        # Consolidate modules
        self.consolidate_sparse_modules()

        # Generate report
        self.generate_report()

        print("\n✅ Codebase hygiene complete!")
        print("🔍 Please run tests to verify functionality")


def main():
    """Main execution"""
    executor = CodebaseHygieneExecutor()

    print("\n⚠️  This will rename files and directories across the codebase.")
    print("A backup will be created, but please ensure you have committed all changes.")

    # Auto-execute for automation
    print("\n🚀 Starting automated hygiene process...")
    executor.execute()


if __name__ == "__main__":
    main()
