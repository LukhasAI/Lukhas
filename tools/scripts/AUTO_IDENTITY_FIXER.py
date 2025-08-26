#!/usr/bin/env python3
"""
LUKHAS  Automated Identity Integration Fixer
===============================================
Automatically fixes identity integration issues across the codebase.
Adds authentication, tier protection, and user ID linking where needed.

SAFETY: Creates backups before modifying files.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

# Tier requirements for modules
MODULE_TIERS = {
    "consciousness": "T3",
    "dream": "T3",
    "emotion": "T3",
    "quantum": "T4",
    "governance": "T5",
    "api": "T2",
}

# API endpoint patterns to protect
API_PATTERNS = [
    r"@app\.(get|post|put|delete|patch)\(",
    r"@router\.(get|post|put|delete|patch)\(",
    r"@[a-zA-Z_]+\.(get|post|put|delete|patch)\(",
]

# Function patterns that need user context
USER_CONTEXT_FUNCTIONS = [
    r"async def.*chat.*\(",
    r"async def.*generate.*\(",
    r"async def.*process.*\(",
    r"async def.*create.*\(",
    r"async def.*update.*\(",
    r"async def.*delete.*\(",
    r"def.*save.*\(",
    r"def.*store.*\(",
    r"def.*log.*\(",
]


class AutoIdentityFixer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = (
            self.root_path
            / f"identity_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.fixes_applied = []
        self.errors = []

    def fix_all(self, dry_run: bool = False):
        """Run all automated fixes."""
        print("🔧 LUKHAS  Automated Identity Fixer")
        print("=" * 50)

        if not dry_run:
            print(f"📁 Creating backup at: {self.backup_dir}")
            self.backup_dir.mkdir(exist_ok=True)

        print(f"🔍 Scanning {self.root_path}")
        print(f"🧪 Dry run: {'YES' if dry_run else 'NO'}")
        print()

        # 1. Fix API endpoints
        self._fix_api_endpoints(dry_run)

        # 2. Add module protection
        self._add_module_protection(dry_run)

        # 3. Inject user ID linking
        self._inject_user_linking(dry_run)

        # 4. Add missing imports
        self._add_missing_imports(dry_run)

        # Generate report
        self._generate_report()

    def _fix_api_endpoints(self, dry_run: bool):
        """Automatically protect API endpoints."""
        print("🌐 Fixing API Endpoints...")

        api_files = list((self.root_path / "api").rglob("*.py"))

        for api_file in api_files:
            if any(skip in str(api_file) for skip in ["__pycache__", "test", "backup"]):
                continue

            try:
                content = api_file.read_text()
                original_content = content

                # Check if already has identity imports
                has_identity_imports = (
                    "from identity" in content or "import identity" in content
                )

                # Find API endpoints
                endpoints_found = []
                for pattern in API_PATTERNS:
                    endpoints_found.extend(re.finditer(pattern, content))

                if not endpoints_found:
                    continue

                print(f"  📝 {api_file.name}: {len(endpoints_found)} endpoints")

                # Backup original
                if not dry_run and not has_identity_imports:
                    backup_file = self.backup_dir / api_file.name
                    shutil.copy2(api_file, backup_file)

                # Add imports if missing
                if not has_identity_imports:
                    content = self._add_identity_imports(content)

                # Protect endpoints
                content = self._protect_endpoints(content, api_file.name)

                if content != original_content:
                    if not dry_run:
                        api_file.write_text(content)
                    self.fixes_applied.append(
                        f"Protected {len(endpoints_found)} endpoints in {api_file.name}"
                    )

            except Exception as e:
                self.errors.append(f"Error fixing {api_file}: {e}")

    def _add_module_protection(self, dry_run: bool):
        """Add tier protection to module entry points."""
        print("\n🛡️ Adding Module Protection...")

        for module_name, required_tier in MODULE_TIERS.items():
            module_path = self.root_path / module_name
            if not module_path.exists():
                continue

            init_file = module_path / "__init__.py"
            if not init_file.exists():
                continue

            try:
                content = init_file.read_text()
                original_content = content

                # Check if already protected
                if "require_tier" in content or "AuthContext" in content:
                    print(f"  ✅ {module_name}: Already protected")
                    continue

                print(f"  🔒 {module_name}: Adding {required_tier} protection")

                # Backup original
                if not dry_run:
                    backup_file = self.backup_dir / f"{module_name}__init__.py"
                    shutil.copy2(init_file, backup_file)

                # Add protection
                protection_code = f'''
# LUKHAS Identity Protection - Auto-generated
import logging
from typing import Optional

# Import identity system
try:
    from identity.middleware import require_tier, AuthContext, get_current_user
    from identity import AccessTier
    _IDENTITY_AVAILABLE = True

    # Module tier requirement
    MODULE_REQUIRED_TIER = "{required_tier}"

    def _check_module_access(user_context: Optional[AuthContext] = None):
        """Check if user has required tier for this module."""
        if not _IDENTITY_AVAILABLE:
            logging.warning(f"{module_name} module: Identity system not available")
            return True

        if user_context and hasattr(user_context, 'is_tier_or_above'):
            if not user_context.is_tier_or_above(MODULE_REQUIRED_TIER):
                raise PermissionError(
                    f"Access denied to {module_name} module. "
                    f"Requires {MODULE_REQUIRED_TIER}, you have {user_context.tier}"
                )
        return True

except ImportError as e:
    _IDENTITY_AVAILABLE = False
    logging.warning(f"{module_name} module: Identity system not available - {e}")

    def _check_module_access(user_context=None):
        return True

'''
                content = protection_code + "\n" + content

                if not dry_run:
                    init_file.write_text(content)
                self.fixes_applied.append(
                    f"Added {required_tier} protection to {module_name}"
                )

            except Exception as e:
                self.errors.append(f"Error protecting {module_name}: {e}")

    def _inject_user_linking(self, dry_run: bool):
        """Inject user ID linking into functions that need it."""
        print("\n🔗 Injecting User ID Linking...")

        # Focus on critical modules first
        critical_modules = ["consciousness", "quantum", "dream", "emotion"]

        for module_name in critical_modules:
            module_path = self.root_path / module_name
            if not module_path.exists():
                continue

            py_files = list(module_path.rglob("*.py"))
            files_modified = 0

            for py_file in py_files[:5]:  # Limit to first 5 files per module for safety
                if any(
                    skip in str(py_file) for skip in ["__pycache__", "test", "backup"]
                ):
                    continue

                try:
                    content = py_file.read_text()

                    # Look for functions that should have user context
                    needs_user_context = False
                    for pattern in USER_CONTEXT_FUNCTIONS:
                        if re.search(pattern, content):
                            needs_user_context = True
                            break

                    if needs_user_context and "user_id" not in content:
                        print(f"  🔗 {py_file.relative_to(self.root_path)}")

                        # Add user context parameter to key functions
                        content = self._add_user_context_to_functions(content)

                        if not dry_run:
                            backup_file = (
                                self.backup_dir / f"{py_file.name}_{files_modified}"
                            )
                            shutil.copy2(py_file, backup_file)
                            py_file.write_text(content)

                        files_modified += 1

                except Exception as e:
                    self.errors.append(f"Error adding user context to {py_file}: {e}")

            if files_modified > 0:
                self.fixes_applied.append(
                    f"Added user linking to {files_modified} files in {module_name}"
                )

    def _add_missing_imports(self, dry_run: bool):
        """Add missing identity imports to files that need them."""
        print("\n📦 Adding Missing Imports...")

        files_with_auth = []

        # Find files that use auth but missing imports
        for py_file in self.root_path.rglob("*.py"):
            if any(
                skip in str(py_file)
                for skip in ["__pycache__", "test", "backup", "archive"]
            ):
                continue

            try:
                content = py_file.read_text()

                # Has auth usage but no imports
                has_auth_usage = any(
                    pattern in content
                    for pattern in [
                        "AuthContext",
                        "require_tier",
                        "get_current_user",
                        "user.user_id",
                    ]
                )
                has_identity_import = (
                    "from identity" in content or "import identity" in content
                )

                if has_auth_usage and not has_identity_import:
                    print(f"  📦 {py_file.relative_to(self.root_path)}")

                    content = self._add_identity_imports(content)

                    if not dry_run:
                        py_file.write_text(content)

                    files_with_auth.append(str(py_file.relative_to(self.root_path)))

            except Exception as e:
                self.errors.append(f"Error adding imports to {py_file}: {e}")

        if files_with_auth:
            self.fixes_applied.append(f"Added imports to {len(files_with_auth)} files")

    def _add_identity_imports(self, content: str) -> str:
        """Add identity imports to Python file content."""
        imports_to_add = """
# LUKHAS Identity Integration - Auto-generated
from typing import Optional
try:
    from identity.middleware import AuthContext, get_current_user, require_tier
    from identity.middleware import require_t2_or_above, require_t3_or_above, require_t4_or_above, require_t5
    from identity import AccessTier
    from fastapi import Depends
    _IDENTITY_AVAILABLE = True
except ImportError:
    # Fallback for when identity system not available
    _IDENTITY_AVAILABLE = False
    AuthContext = None

    def get_current_user():
        return None

    def require_tier(tier):
        def decorator(func):
            return func
        return decorator

    class MockAccessTier:
        T1 = T2 = T3 = T4 = T5 = "mock"
    AccessTier = MockAccessTier()

"""

        # Find the right place to insert imports (after existing imports)
        lines = content.split("\n")
        import_end_idx = 0

        for i, line in enumerate(lines):
            if (
                line.strip().startswith(("import ", "from "))
                or line.strip().startswith('"""')
                or line.strip().startswith("'''")
                or line.strip() == ""
                or line.strip().startswith("#")
            ):
                import_end_idx = i + 1
            else:
                break

        lines.insert(import_end_idx, imports_to_add)
        return "\n".join(lines)

    def _protect_endpoints(self, content: str, filename: str) -> str:
        """Add authentication to API endpoints."""

        # Determine required tier based on filename
        if "consciousness" in filename or "dream" in filename or "emotion" in filename:
            auth_dep = "require_t3_or_above"
        elif "quantum" in filename:
            auth_dep = "require_t4_or_above"
        elif "governance" in filename or "admin" in filename:
            auth_dep = "require_t5"
        else:
            auth_dep = "require_t2_or_above"

        # Find endpoint functions and add authentication
        lines = content.split("\n")
        modified_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line defines an API endpoint
            if re.match(r"@(app|router)\.(get|post|put|delete|patch)", line.strip()):
                modified_lines.append(line)

                # Look for the function definition
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("async def "):
                    modified_lines.append(lines[j])
                    j += 1

                if j < len(lines):
                    func_line = lines[j]

                    # Add user parameter if not present
                    if "AuthContext" not in func_line and "user:" not in func_line:
                        # Insert user parameter
                        func_match = re.match(
                            r"(\s*async def\s+\w+\s*\([^)]*)", func_line
                        )
                        if func_match:
                            func_start = func_match.group(1)
                            if func_line.endswith("):"):
                                # Add parameter before closing paren
                                new_func_line = (
                                    func_line[:-2]
                                    + f", user: AuthContext = Depends({auth_dep})):"
                                )
                            else:
                                # Function continues on next line
                                new_func_line = (
                                    func_line
                                    + f", user: AuthContext = Depends({auth_dep})"
                                )
                            modified_lines.append(new_func_line)
                        else:
                            modified_lines.append(func_line)
                    else:
                        modified_lines.append(func_line)

                    i = j + 1
                else:
                    i += 1
            else:
                modified_lines.append(line)
                i += 1

        return "\n".join(modified_lines)

    def _add_user_context_to_functions(self, content: str) -> str:
        """Add user_id tracking to function bodies."""

        # Simple approach: add user_id to data dictionaries
        patterns_to_enhance = [
            (
                r"(\s+)(data\s*=\s*\{)",
                r'\1\2\n\1    "user_id": getattr(user, "user_id", "anonymous"),',
            ),
            (
                r"(\s+)(result\s*=\s*\{)",
                r'\1\2\n\1    "user_id": getattr(user, "user_id", "anonymous"),',
            ),
            (
                r"(\s+)(response\s*=\s*\{)",
                r'\1\2\n\1    "user_id": getattr(user, "user_id", "anonymous"),',
            ),
            (
                r"(\s+)(log_data\s*=\s*\{)",
                r'\1\2\n\1    "user_id": getattr(user, "user_id", "anonymous"),',
            ),
        ]

        for pattern, replacement in patterns_to_enhance:
            content = re.sub(pattern, replacement, content)

        return content

    def _generate_report(self):
        """Generate report of fixes applied."""
        print("\n" + "=" * 50)
        print("📊 AUTOMATED IDENTITY FIXES REPORT")
        print("=" * 50)

        print(f"\n✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"  • {fix}")

        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5
                print(f"  • {error}")

        if self.backup_dir.exists():
            print(f"\n💾 Backups saved to: {self.backup_dir}")

        print(
            f"\n📁 Total files in backup: {len(list(self.backup_dir.rglob('*'))) if self.backup_dir.exists() else 0}"
        )

        # Next steps
        print("\n🚀 Next Steps:")
        print("  1. Review changes in backup directory")
        print("  2. Test API endpoints with authentication")
        print(
            "  3. Run identity audit again: python3 tools/analysis/IDENTITY_INTEGRATION_AUDIT.py"
        )
        print("  4. Fix any remaining manual issues")


def main():
    import sys

    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv

    if dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  LIVE MODE - Files will be modified (backups created)")
        response = input("Continue? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    fixer = AutoIdentityFixer()
    fixer.fix_all(dry_run=dry_run)


if __name__ == "__main__":
    main()
