#!/usr/bin/env python3
"""
Cleanup Command Generator - Generates bash scripts to fix codebase issues
Works with the Codebase Analyzer to create actionable cleanup commands
"""

import json
import re
from pathlib import Path


class CleanupGenerator:
    def __init__(self, analysis_file: str = "codebase_analysis.json"):
        with open(analysis_file) as f:
            self.analysis = json.load(f)

        self.commands = []
        self.safety_checks = []

    def generate_cleanup_script(self) -> str:
        """Generate a comprehensive cleanup script"""
        script_lines = [
            "#!/bin/bash",
            "# Generated cleanup script for codebase organization",
            "# Run this script from your repository root",
            "",
            "set -e  # Exit on any error",
            "",
            "echo '🧹 Starting codebase cleanup...'",
            "",
        ]

        # Add safety checks
        script_lines.extend(self._generate_safety_checks())
        script_lines.append("")

        # Generate cleanup commands by priority
        script_lines.extend(self._generate_stub_removal())
        script_lines.extend(self._generate_prefix_fixes())
        script_lines.extend(self._generate_documentation_moves())
        script_lines.extend(self._generate_file_reorganization())
        script_lines.extend(self._generate_import_fixes())

        script_lines.extend(
            [
                "",
                "echo '✅ Cleanup completed!'",
                "echo 'Remember to:'",
                "echo '  1. Test your code after these changes'",
                "echo '  2. Update any remaining import statements'",
                "echo '  3. Run your test suite if you have one'",
            ]
        )

        return "\n".join(script_lines)

    def _generate_safety_checks(self) -> list[str]:
        """Generate safety checks for the script"""
        return [
            "# Safety checks",
            "if [ ! -f 'qi/README.md' ] && [ ! -f 'README.md' ]; then",
            "  echo '❌ Error: This doesn\\'t look like your qi repository root'",
            "  echo 'Please run this script from your repository root directory'",
            "  exit 1",
            "fi",
            "",
            "echo '⚠️  This script will move and rename files in your codebase'",
            "echo 'Make sure you have committed your current changes first!'",
            "read -p 'Continue? (y/N): ' -n 1 -r",
            "echo",
            "if [[ ! $REPLY =~ ^[Yy]$ ]]; then",
            "  echo 'Cleanup cancelled.'",
            "  exit 0",
            "fi",
            "",
        ]

    def _generate_stub_removal(self) -> list[str]:
        """Generate commands to remove stub files"""
        if "stub_files" not in self.analysis["issues"]:
            return []

        lines = ["echo '🗑️  Removing stub files...'", ""]

        for issue in self.analysis["issues"]["stub_files"]:
            file_path = issue["file"]
            lines.append("")
            lines.append(f"if [ -f '{file_path}' ]; then")
            lines.append(f"  echo 'Removing {file_path}'")
            lines.append(f"  rm '{file_path}'")
            lines.append("fi")
            lines.append("")

        return lines

    def _generate_prefix_fixes(self) -> list[str]:
        """Generate commands to fix redundant prefixes"""
        if "redundant_prefixes" not in self.analysis["issues"]:
            return []

        lines = ["echo '📝 Fixing redundant prefixes...'", ""]

        for issue in self.analysis["issues"]["redundant_prefixes"]:
            old_path = issue["file"]
            new_path = self._suggest_new_name(old_path)

            if old_path != new_path:
                lines.append("")
                lines.append(f"if [ -f '{old_path}' ]; then")
                lines.append(f"  echo 'Renaming {old_path} -> {new_path}'")
                lines.append(f"  mv '{old_path}' '{new_path}'")
                lines.append("fi")
                lines.append("")

        return lines

    def _suggest_new_name(self, file_path: str) -> str:
        """Suggest a better name for a file with redundant prefixes"""
        path = Path(file_path)
        filename = path.stem

        # Remove redundant prefixes
        patterns = [
            (r"^qi_(.+)", r"\1"),
            (r"^bio_bio_(.+)", r"bio_\1"),
            (r"^symbolic_bio_(.+)", r"\1"),
            (r"^(.+)_system$", r"\1"),
            (r"^(.+)_adapter$", r"\1_adapter"),  # Keep adapter suffix
        ]

        new_filename = filename
        for pattern, replacement in patterns:
            new_filename = re.sub(pattern, replacement, new_filename)

        # Construct new path
        new_path = path.parent / f"{new_filename}{path.suffix}"
        return str(new_path)

    def _generate_documentation_moves(self) -> list[str]:
        """Generate commands to move documentation files"""
        if "documentation_in_code" not in self.analysis["issues"]:
            return []

        lines = [
            "echo '📚 Moving documentation files...'",
            "",
            "# Create docs directory if it doesn't exist",
            "mkdir -p docs",
            "",
        ]

        for issue in self.analysis["issues"]["documentation_in_code"]:
            old_path = issue["file"]
            new_path = self._suggest_doc_location(old_path)

            lines.append("")
            lines.append(f"if [ -f '{old_path}' ]; then")
            lines.append(f"  echo 'Moving {old_path} -> {new_path}'")
            lines.append(f"  mkdir -p '$(dirname \"{new_path}\")'")
            lines.append(f"  mv '{old_path}' '{new_path}'")
            lines.append("fi")
            lines.append("")

        return lines

    def _suggest_doc_location(self, file_path: str) -> str:
        """Suggest where to move a documentation file"""
        path = Path(file_path)

        # Determine which docs subdirectory based on original location
        if "bio" in str(path):
            return f"docs/bio/{path.name}"
        elif "quantum" in str(path):
            return f"docs/quantum/{path.name}"
        elif "core" in str(path):
            return f"docs/core/{path.name}"
        else:
            return f"docs/{path.name}"

    def _generate_file_reorganization(self) -> list[str]:
        """Generate commands to reorganize misplaced files"""
        if "misplaced_files" not in self.analysis["issues"]:
            return []

        lines = ["echo '📁 Reorganizing misplaced files...'", ""]

        # Group by suggested directory
        moves_by_dir = {}
        for issue in self.analysis["issues"]["misplaced_files"]:
            suggested_dir = issue["suggested_dir"]
            if suggested_dir not in moves_by_dir:
                moves_by_dir[suggested_dir] = []
            moves_by_dir[suggested_dir].append(issue)

        for target_dir, moves in moves_by_dir.items():
            lines.append("")
            lines.append(f"mkdir -p '{target_dir}'")
            lines.append("")

            for issue in moves:
                old_path = issue["file"]
                new_path = f"{target_dir}/{Path(old_path).name}"

                lines.append("")
                lines.append(f"if [ -f '{old_path}' ]; then")
                lines.append(f"  echo 'Moving {old_path} -> {new_path}'")
                lines.append(f"  mv '{old_path}' '{new_path}'")
                lines.append("fi")
                lines.append("")

        return lines

    def _generate_import_fixes(self) -> list[str]:
        """Generate commands to help fix broken imports"""
        if "broken_imports" not in self.analysis["issues"]:
            return []

        lines = [
            "echo '🔗 Checking for import issues...'",
            "echo 'Note: Import fixes may need manual attention'",
            "",
        ]

        # Create a summary of import issues
        import_issues = {}
        for issue in self.analysis["issues"]["broken_imports"]:
            file_path = issue["file"]
            import_name = issue["import"]

            if file_path not in import_issues:
                import_issues[file_path] = []
            import_issues[file_path].append(import_name)

        for file_path, imports in import_issues.items():
            lines.append(f"echo 'File {file_path} has broken imports:'")
            for imp in imports:
                lines.append(f"echo '  - {imp}'")
            lines.append("")

        lines.append("echo 'Please review and fix these imports manually after running the reorganization'")
        lines.append("")

        return lines

    def generate_verification_script(self) -> str:
        """Generate a script to verify the cleanup results"""
        lines = [
            "#!/bin/bash",
            "# Verification script to check cleanup results",
            "",
            "echo '🔍 Verifying cleanup results...'",
            "",
            "# Check for remaining problematic files",
            "echo 'Checking for remaining stub files:'",
            "find . -name '*.py' -exec grep -l 'TODO\\|placeholder\\|not implemented' {} \\; 2>/dev/null || echo 'None found ✅'",
            "",
            "echo 'Checking for redundant prefixes:'",
            "find . -name 'qi_*.py' -o -name 'bio_bio_*.py' -o -name 'symbolic_bio_*.py' 2>/dev/null || echo 'None found ✅'",
            "",
            "echo 'Checking for documentation in code directories:'",
            "find ./qi -name '*.md' -o -name '*doc*.py' -o -name '*readme*.py' 2>/dev/null || echo 'None found ✅'",
            "",
            "echo 'Verification complete!'",
        ]

        return "\n".join(lines)

    def save_scripts(self, base_path: str = "."):
        """Save the generated scripts to files"""
        base_path = Path(base_path)

        # Save cleanup script
        cleanup_script = self.generate_cleanup_script()
        cleanup_file = base_path / "cleanup_codebase.sh"
        with open(cleanup_file, "w") as f:
            f.write(cleanup_script)
        cleanup_file.chmod(0o755)  # Make executable

        # Save verification script
        verify_script = self.generate_verification_script()
        verify_file = base_path / "verify_cleanup.sh"
        with open(verify_file, "w") as f:
            f.write(verify_script)
        verify_file.chmod(0o755)  # Make executable

        print("📝 Generated scripts:")
        print(f"  Cleanup: {cleanup_file}")
        print(f"  Verification: {verify_file}")
        print("\nTo run:")
        print("  ./cleanup_codebase.sh")
        print("  ./verify_cleanup.sh")


def main():
    """Main function"""
    import sys

    analysis_file = "codebase_analysis.json"
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]

    if not Path(analysis_file).exists():
        print(f"Error: Analysis file '{analysis_file}' not found")
        print("Run the codebase analyzer first to generate the analysis file")
        sys.exit(1)

    generator = CleanupGenerator(analysis_file)
    generator.save_scripts()


if __name__ == "__main__":
    main()
