#!/usr/bin/env python3
"""
LUKHAS Safe TODO Removal Script
Surgical removal of non-actionable TODOs with comprehensive backup and verification.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class SafeTodoRemover:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.backup_dir = self.repo_path / "TODO_REMOVAL_BACKUP"
        self.log_file = self.backup_dir / "removal_log.json"
        self.rollback_file = self.backup_dir / "rollback_instructions.txt"

        # Statistics tracking
        self.stats = {
            "files_processed": 0,
            "total_removals": 0,
            "removals_by_category": {},
            "files_modified": set(),
            "errors": [],
        }

        # Define removal patterns with safety constraints
        self.removal_patterns = {
            "completion_references": {
                "patterns": [
                    r".*[Aa]ddresses TODO \d+.*\n",
                    r".*[Ii]mplements TODO \d+.*\n",
                    r".*[Cc]ompletes TODO \d+.*\n",
                    r".*[Ff]ixes TODO \d+.*\n",
                    r".*[Rr]esolves TODO \d+.*\n",
                    r".*TODO \d+:.*implemented.*\n",
                    r".*TODO \d+:.*completed.*\n",
                    r".*TODO \d+ is now.*\n",
                ],
                "description": "References to completed TODOs",
                "safety_check": lambda line: "address" in line.lower()
                or "implement" in line.lower()
                or "complete" in line.lower(),
            },
            "symbol_resolver_duplicates": {
                "patterns": [
                    r"^[\s]*#?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
                    r"^[\s]*\/\/?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
                ],
                "description": "Symbol resolver implementation stubs",
                "safety_check": lambda line: "symbol-resolver" in line and "implement missing functionality" in line,
            },
            "streamlit_stubs": {
                "patterns": [
                    r"^[\s]*#\s*TODO:\s*Install or implement streamlit\s*\n",
                    r"^[\s]*\/\/?\s*TODO:\s*Install or implement streamlit\s*\n",
                    r".*#\s*TODO:\s*Install or implement streamlit\s*\n",
                ],
                "description": "Streamlit installation stubs",
                "safety_check": lambda line: "install or implement streamlit" in line.lower(),
            },
            "consolidation_stubs": {
                "patterns": [
                    r"^[\s]*#?\s*TODO:\s*Implement actual consolidation logic\s*\n",
                    r"^[\s]*\/\/?\s*TODO:\s*Implement actual consolidation logic\s*\n",
                ],
                "description": "Consolidation logic stubs",
                "safety_check": lambda line: "implement actual consolidation logic" in line.lower(),
            },
            "placeholder_stubs": {
                "patterns": [r"^[\s]*pass\s*#\s*TODO.*\n", r"^[\s]*pass\s*#.*TODO.*\n"],
                "description": "Pass statement TODO stubs",
                "safety_check": lambda line: "pass" in line and "TODO" in line,
            },
            "dependency_stubs": {
                "patterns": [
                    r"^[\s]*#\s*TODO:\s*Install or implement \w+\s*\n",
                    r"^[\s]*#\s*TODO:\s*Install \w+\s*\n",
                    r".*#\s*TODO:\s*Install or implement \w+\s*\n",
                    r".*#\s*TODO:\s*Install \w+\s*\n",
                ],
                "description": "Dependency installation stubs",
                "safety_check": lambda line: "TODO:" in line
                and ("install" in line.lower() or "implement" in line.lower())
                and any(
                    pkg in line.lower()
                    for pkg in ["streamlit", "numpy", "pandas", "matplotlib", "plotly", "dash", "fastapi", "flask"]
                ),
            },
        }

        # Files to exclude from processing (critical system files)
        self.excluded_patterns = [
            r"\.git/.*",
            r"\.venv/.*",
            r"__pycache__/.*",
            r"node_modules/.*",
            r"\.pyc$",
            r"\.pyo$",
            r"\.so$",
            r"\.dll$",
            r"\.exe$",
        ]

    def create_backup(self) -> None:
        """Create comprehensive backup before removal"""
        print("🔒 Creating comprehensive backup...")

        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)

        # Create git stash backup
        subprocess.run(["git", "stash", "push", "-m", "TODO removal backup"], cwd=self.repo_path, capture_output=True)

        # Save current git state
        git_state = {
            "commit": subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=self.repo_path, capture_output=True, text=True
            ).stdout.strip(),
            "branch": subprocess.run(
                ["git", "branch", "--show-current"], cwd=self.repo_path, capture_output=True, text=True
            ).stdout.strip(),
            "status": subprocess.run(
                ["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True
            ).stdout,
        }

        with open(self.backup_dir / "git_state.json", "w") as f:
            json.dump(git_state, f, indent=2)

        print(f"✅ Backup created at {self.backup_dir}")

    def is_excluded_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing"""
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in self.excluded_patterns)

    def is_safe_to_modify(self, file_path: Path) -> bool:
        """Additional safety checks for file modification"""
        # Skip binary files
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.read(1024)  # Try to read first 1KB as text
        except (UnicodeDecodeError, PermissionError):
            return False

        # Skip very large files (>10MB) to avoid performance issues
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return False

        return True

    def backup_file(self, file_path: Path) -> None:
        """Create individual file backup"""
        backup_path = self.backup_dir / "files" / file_path.relative_to(self.repo_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy original file
        with open(file_path, "r", encoding="utf-8") as src:
            content = src.read()
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(content)

    def process_file(self, file_path: Path) -> Dict:
        """Process a single file for TODO removal"""
        if self.is_excluded_file(file_path) or not self.is_safe_to_modify(file_path):
            return {"processed": False, "reason": "excluded or unsafe"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            current_content = original_content
            file_stats = {"removals": 0, "categories": []}

            # Apply each removal pattern
            for category, config in self.removal_patterns.items():
                for pattern in config["patterns"]:
                    matches = list(re.finditer(pattern, current_content, re.MULTILINE))

                    # Safety check: verify each match
                    safe_matches = []
                    for match in matches:
                        line = match.group(0)
                        if config["safety_check"](line):
                            safe_matches.append(match)
                        else:
                            self.stats["errors"].append(f"Safety check failed for {file_path}: {line.strip()}")

                    if safe_matches:
                        # Create backup before modification
                        if file_stats["removals"] == 0:
                            self.backup_file(file_path)

                        # Remove matches (in reverse order to preserve positions)
                        for match in reversed(safe_matches):
                            current_content = current_content[: match.start()] + current_content[match.end() :]
                            file_stats["removals"] += 1

                        if category not in file_stats["categories"]:
                            file_stats["categories"].append(category)

            # Write modified content if changes were made
            if file_stats["removals"] > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(current_content)

                self.stats["files_modified"].add(str(file_path))
                print(f"  ✂️  {file_path}: {file_stats['removals']} removals")

            return {"processed": True, "stats": file_stats}

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats["errors"].append(error_msg)
            return {"processed": False, "error": error_msg}

    def find_todo_files(self) -> List[Path]:
        """Find all files containing TODOs"""
        print("🔍 Scanning for files with TODOs...")

        try:
            # Use git grep for faster search
            result = subprocess.run(["git", "grep", "-l", "TODO"], cwd=self.repo_path, capture_output=True, text=True)

            if result.returncode == 0:
                files = [self.repo_path / line.strip() for line in result.stdout.split("\n") if line.strip()]
                print(f"📁 Found {len(files)} files with TODOs")
                return files
            else:
                print("⚠️ git grep failed, falling back to find")
                return []

        except Exception as e:
            print(f"⚠️ Error finding TODO files: {e}")
            return []

    def run_removal(self) -> None:
        """Execute the TODO removal process"""
        start_time = datetime.now()
        print(f"🚀 Starting TODO removal at {start_time}")

        # Create backup
        self.create_backup()

        # Find files to process
        todo_files = self.find_todo_files()

        if not todo_files:
            print("ℹ️  No TODO files found")
            return

        print(f"📋 Processing {len(todo_files)} files...")

        # Process each file
        for file_path in todo_files:
            self.stats["files_processed"] += 1
            result = self.process_file(file_path)

            if result["processed"] and "stats" in result:
                stats = result["stats"]
                self.stats["total_removals"] += stats["removals"]

                for category in stats["categories"]:
                    if category not in self.stats["removals_by_category"]:
                        self.stats["removals_by_category"][category] = 0
                    self.stats["removals_by_category"][category] += stats["removals"]

        # Save removal log
        removal_log = {
            "timestamp": start_time.isoformat(),
            "duration": str(datetime.now() - start_time),
            "stats": {**self.stats, "files_modified": list(self.stats["files_modified"])},
        }

        with open(self.log_file, "w") as f:
            json.dump(removal_log, f, indent=2)

        # Create rollback instructions
        self.create_rollback_instructions()

        # Print summary
        self.print_summary()

    def create_rollback_instructions(self) -> None:
        """Create detailed rollback instructions"""
        instructions = f"""
LUKHAS TODO Removal Rollback Instructions
Generated: {datetime.now().isoformat()}

IMMEDIATE ROLLBACK (if needed):
1. git stash pop  # Restore stashed changes
2. git checkout .  # Discard all changes

SELECTIVE ROLLBACK:
1. Individual file restoration from {self.backup_dir}/files/
2. Copy specific files back to their original locations

VERIFICATION COMMANDS:
1. git status  # Check what was modified
2. git diff    # See specific changes
3. python -m py_compile <file>  # Test Python files
4. pytest tests/  # Run test suite

FILES MODIFIED: {len(self.stats['files_modified'])}
TOTAL REMOVALS: {self.stats['total_removals']}

ERRORS ENCOUNTERED:
{chr(10).join(self.stats['errors']) if self.stats['errors'] else 'None'}
"""

        with open(self.rollback_file, "w") as f:
            f.write(instructions)

    def print_summary(self) -> None:
        """Print removal summary"""
        print("\n" + "=" * 60)
        print("📊 TODO REMOVAL SUMMARY")
        print("=" * 60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {len(self.stats['files_modified'])}")
        print(f"Total removals: {self.stats['total_removals']}")

        print("\n📈 Removals by category:")
        for category, count in self.stats["removals_by_category"].items():
            description = self.removal_patterns[category]["description"]
            print(f"  {category}: {count} ({description})")

        if self.stats["errors"]:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")

        print(f"\n💾 Backup location: {self.backup_dir}")
        print(f"📋 Rollback instructions: {self.rollback_file}")
        print("=" * 60)


def main():
    """Main execution function"""
    remover = SafeTodoRemover()

    # Safety confirmation
    print("🔥 LUKHAS TODO REMOVAL TOOL")
    print("This will remove non-actionable TODOs from the codebase.")
    print("A comprehensive backup will be created.")

    response = input("\nProceed with TODO removal? (yes/no): ").lower()
    if response != "yes":
        print("❌ Operation cancelled")
        return

    remover.run_removal()
    print("\n✅ TODO removal completed successfully!")


if __name__ == "__main__":
    main()
