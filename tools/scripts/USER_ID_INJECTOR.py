#!/usr/bin/env python3
"""
LUKHAS  User ID Injector
===========================
Automatically injects user ID linking into data operations, logging, and storage.
Ensures all user actions are properly tracked and audited.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


class UserIDInjector:
    """Automatically inject user_id tracking into code."""

    def __init__(self, root_path: str = ".", timezone):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / f"user_id_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'}"
        self.modifications = []

        # Patterns for data structures that should include user_id
        self.data_patterns = [
            r"(\s+)(data\s*=\s*\{)",
            r"(\s+)(result\s*=\s*\{)",
            r"(\s+)(response\s*=\s*\{)",
            r"(\s+)(log_data\s*=\s*\{)",
            r"(\s+)(record\s*=\s*\{)",
            r"(\s+)(entry\s*=\s*\{)",
            r"(\s+)(item\s*=\s*\{)",
            r"(\s+)(doc\s*=\s*\{)",
            r"(\s+)(metadata\s*=\s*\{)",
            r"(\s+)(info\s*=\s*\{)",
        ]

        # Patterns for logging calls that should include user_id
        self.log_patterns = [
            r"(logger\.info\()",
            r"(logger\.warning\()",
            r"(logger\.error\()",
            r"(logger\.debug\()",
            r"(logging\.info\()",
            r"(logging\.warning\()",
            r"(logging\.error\()",
            r"(logging\.debug\()",
        ]

        # Database/storage operations that should track users
        self.storage_patterns = [
            r"(\.save\()",
            r"(\.insert\()",
            r"(\.update\()",
            r"(\.create\()",
            r"(\.store\()",
            r"(\.write\()",
            r"(\.put\()",
            r"(db\.)",
            r"(collection\.)",
            r"(\.commit\()",
        ]

    def inject_user_tracking(self, target_modules: Optional[list[str]] = None, dry_run: bool = False):
        """Inject user ID tracking into specified modules."""
        print("🔗 LUKHAS  User ID Injector")
        print("=" * 40)

        if not dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            print(f"📁 Backup directory: {self.backup_dir}")

        target_modules = target_modules or [
            "consciousness",
            "quantum",
            "dream",
            "emotion",
            "memory",
        ]

        for module_name in target_modules:
            self._inject_module_user_tracking(module_name, dry_run)

        self._generate_report()

    def _inject_module_user_tracking(self, module_name: str, dry_run: bool):
        """Inject user tracking into a specific module."""
        module_path = self.root_path / module_name
        if not module_path.exists():
            print(f"⚠️ Module {module_name} not found")
            return

        print(f"\n🔗 Processing {module_name} module...")

        py_files = list(module_path.rglob("*.py"))
        files_modified = 0

        # Limit files for safety - focus on core files
        priority_files = [
            f
            for f in py_files
            if any(key in f.name for key in ["core", "main", "service", "manager", "processor", "engine"])
        ]

        files_to_process = priority_files[:10] if priority_files else py_files[:5]

        for py_file in files_to_process:
            if any(skip in str(py_file) for skip in ["__pycache__", "test", "backup"]):
                continue

            try:
                content = py_file.read_text()
                original_content = content

                # Check if file has functions that should track users
                if self._needs_user_tracking(content):
                    print(f"  📝 {py_file.relative_to(module_path}")

                    # Apply transformations
                    content = self._inject_data_user_ids(content)
                    content = self._inject_log_user_ids(content)
                    content = self._inject_storage_user_ids(content)
                    content = self._add_user_context_parameter(content)

                    if content != original_content:
                        if not dry_run:
                            # Backup original
                            backup_file = self.backup_dir / f"{py_file.name}_{files_modified}"
                            shutil.copy2(py_file, backup_file)

                            # Write modified content
                            py_file.write_text(content)

                        files_modified += 1
                        self.modifications.append(f"Modified {py_file.relative_to(self.root_path}")

            except Exception as e:
                print(f"❌ Error processing {py_file}: {e}")

        if files_modified > 0:
            print(f"  ✅ Modified {files_modified} files in {module_name}")
        else:
            print(f"  ℹ️ No modifications needed in {module_name}")

    def _needs_user_tracking(self, content: str) -> bool:
        """Check if file needs user ID tracking."""

        # Skip if already has user tracking
        if "user_id" in content and ("user.user_id" in content or '"user_id":' in content):
            return False

        # Check for patterns that indicate need for user tracking
        indicators = [
            r"def.*save.*\(",
            r"def.*store.*\(",
            r"def.*create.*\(",
            r"def.*process.*\(",
            r"def.*generate.*\(",
            r"logger\.",
            r"data\s*=\s*\{",
            r"result\s*=\s*\{",
            r"\.insert\(",
            r"\.update\(",
        ]

        return any(re.search(pattern, content) for pattern in indicators)

    def _inject_data_user_ids(self, content: str) -> str:
        """Add user_id to data dictionaries."""

        for pattern in self.data_patterns:
            # Add user_id as first field in dictionary
            replacement = r'\1\2\n\1    "user_id": getattr(user, "user_id", "system"),'
            content = re.sub(pattern, replacement, content)

        return content

    def _inject_log_user_ids(self, content: str) -> str:
        """Add user context to log calls."""

        # Find log calls and add user context
        lines = content.split("\n")
        modified_lines = []

        for line in lines:
            modified_line = line

            # Check if line contains logging call
            for pattern in self.log_patterns:
                if re.search(pattern, line):
                    # Add user context to log message
                    if "user_id=" not in line and 'f"' in line:
                        # f-string logs - add user_id
                        modified_line = re.sub(
                            r'(f"[^"]*)"',
                            r'\1 [user:{getattr(user, "user_id", "system")}]"',
                            line,
                        )
                    elif "user_id=" not in line and '"' in line:
                        # Regular string logs - add extra parameter
                        if line.strip().endswith(")"):
                            modified_line = line[:-1] + ', extra={"user_id": getattr(user, "user_id", "system")})'
                    break

            modified_lines.append(modified_line)

        return "\n".join(modified_lines)

    def _inject_storage_user_ids(self, content: str) -> str:
        """Add user_id to database/storage operations."""

        lines = content.split("\n")
        modified_lines = []

        for line in lines:
            modified_line = line

            # Check for storage operations
            for pattern in self.storage_patterns:
                if re.search(pattern, line) and "user_id" not in line:
                    # Try to add user_id parameter
                    if ".save(" in line:
                        modified_line = line.replace(
                            ".save()",
                            '.save(user_id=getattr(user, "user_id", "system"))',
                        )
                    elif ".insert(" in line and "{}" in line:
                        # Insert user_id into data dict
                        modified_line = re.sub(
                            r"(\{)",
                            r'\1"user_id": getattr(user, "user_id", "system"), ',
                            line,
                        )
                    break

            modified_lines.append(modified_line)

        return "\n".join(modified_lines)

    def _add_user_context_parameter(self, content: str) -> str:
        """Add user parameter to function signatures that need it."""

        lines = content.split("\n")
        modified_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for function definitions that need user context
            if re.match(r"\s*async def\s+\w+", line) or re.match(r"\s*def\s+\w+", line):
                func_line = line

                # Check if function needs user context (has user tracking calls)
                func_body_lines = []
                j = i + 1
                indent_level = len(line) - len(line.lstrip())

                # Collect function body
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == "":
                        func_body_lines.append(next_line)
                        j += 1
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level and next_line.strip():
                        break

                    func_body_lines.append(next_line)
                    j += 1

                func_body = "\n".join(func_body_lines)

                # Check if function body needs user context
                needs_user = any(
                    [
                        'getattr(user, "user_id"' in func_body,
                        "user_id" in func_body and "system" in func_body,
                        "logger." in func_body,
                        ".save(" in func_body,
                        ".insert(" in func_body,
                    ]
                )

                # Add user parameter if needed and not present
                if needs_user and "user:" not in func_line and "AuthContext" not in func_line:
                    if func_line.endswith(":"):
                        # Single line function def
                        if "()" in func_line:
                            modified_line = func_line.replace("():", '(user: Optional["AuthContext"] = None):')
                        else:
                            modified_line = func_line.replace("):", ', user: Optional["AuthContext"] = None):')
                    else:
                        # Multi-line function def
                        modified_line = func_line.replace("(", '(user: Optional["AuthContext"] = None, ')

                    modified_lines.append(modified_line)

                    # Add import if not present and this is the first function needing it
                    if "Optional" not in content:
                        import_line = "from typing import Optional"
                        if import_line not in content:
                            modified_lines.insert(-1, import_line)
                else:
                    modified_lines.append(func_line)

                # Add function body
                modified_lines.extend(func_body_lines)
                i = j
            else:
                modified_lines.append(line)
                i += 1

        return "\n".join(modified_lines)

    def _generate_report(self):
        """Generate report of user ID injections."""
        print("\n" + "=" * 40)
        print("📊 USER ID INJECTION REPORT")
        print("=" * 40)

        print(f"\n✅ Files Modified: {len(self.modifications}")
        for mod in self.modifications:
            print(f"  • {mod}")

        print("\n🔗 Injections Applied:")
        print("  • Data dictionary user_id fields")
        print("  • Log message user context")
        print("  • Storage operation user tracking")
        print("  • Function parameter user context")

        if self.backup_dir.exists():
            print(f"\n💾 Backups: {self.backup_dir}")

        print("\n📋 Manual Steps Required:")
        print("  1. Import AuthContext in modified files")
        print("  2. Pass user context through function calls")
        print("  3. Update API endpoints to provide user context")
        print("  4. Test user tracking functionality")


def main():
    import sys

    dry_run = "--dry-run" in sys.argv
    modules = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not modules:
        modules = ["consciousness", "quantum", "dream", "emotion"]

    print(f"🎯 Target modules: {', '.join(modules}")
    print(f"🧪 Dry run: {'YES' if dry_run else 'NO'}")

    if not dry_run:
        response = input("\nProceed with user ID injection? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    injector = UserIDInjector()
    injector.inject_user_tracking(modules, dry_run=dry_run)


if __name__ == "__main__":
    main()
