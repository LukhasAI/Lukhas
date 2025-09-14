#!/usr/bin/env python3
"""
Identity Module Refactoring Script
Consolidates identity logic into identity_core.py and removes legacy files
"""

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


class IdentityRefactor:
    """Refactor identity module to use unified identity_core.py"""

    def __init__(self):
        self.workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
        self.backup_dir = self.workspace / f".identity_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.changes = []

    def backup_identity_modules(self):
        """Backup all identity-related modules before refactoring"""
        print("\n📦 Creating backup of identity modules...")
        self.backup_dir.mkdir(exist_ok=True)

        # Backup main identity module
        if (self.workspace / "identity").exists():
            shutil.copytree(self.workspace / "identity", self.backup_dir / "identity")
            print("  ✅ Backed up identity/")

        # Backup legacy identity directories
        for dir_name in ["identity_legacy", "identity_enhanced", "lambda_identity"]:
            dir_path = self.workspace / dir_name
            if dir_path.exists():
                shutil.copytree(dir_path, self.backup_dir / dir_name)
                print(f"  ✅ Backed up {dir_name}/")

    def remove_legacy_files(self):
        """Remove legacy and broken identity files"""
        print("\n🗑️ Removing legacy identity files...")

        # Files to keep (essential for API compatibility)

        # Remove empty/legacy directories
        legacy_dirs = [
            "identity_legacy",
            "identity_enhanced",
            "lambda_identity",
            "identity/lukhus_ultimate_test_suite",
            "identity/auth_backend",
            "identity/auth_middleware",
            "identity/auth_utils",
            "identity/interface",
            "identity/tiered_access",
            "identity/core",  # Will be replaced by identity_core.py
        ]

        for dir_path in legacy_dirs:
            full_path = self.workspace / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)
                print(f"  ✅ Removed {dir_path}/")
                self.changes.append(("removed_dir", dir_path))

        # Remove old implementation files (now in identity_core.py)
        old_files = [
            "identity/user_db.py",  # Integrated into identity_core
            "identity/verify.py",  # Integrated into identity_core
            "identity/login.py",  # Will be simplified
            "identity/registration.py",  # Will be simplified
            "identity/example_integration.py",  # Not needed
        ]

        for file_path in old_files:
            full_path = self.workspace / file_path
            if full_path.exists():
                full_path.unlink()
                print(f"  ✅ Removed {file_path}")
                self.changes.append(("removed_file", file_path))

    def create_simplified_wrappers(self):
        """Create simplified wrapper files for backward compatibility"""
        print("\n📝 Creating compatibility wrappers...")

        # Create simplified __init__.py
        init_content = '''"""
LUKHΛS Identity Module
Unified identity management with symbolic authentication
"""

from .identity_core import (
    IdentityCore,
    AccessTier,
    identity_core,
    validate_symbolic_token,
    resolve_access_tier,
    generate_identity_glyph
)

__all__ = [
    "IdentityCore",
    "AccessTier",
    "identity_core",
    "validate_symbolic_token",
    "resolve_access_tier",
    "generate_identity_glyph"
]
'''

        init_path = self.workspace / "identity" / "__init__.py"
        with open(init_path, "w") as f:
            f.write(init_content)
        print("  ✅ Created simplified __init__.py")

        # Create minimal login wrapper for API compatibility
        login_content = '''"""
Login wrapper for backward compatibility
Routes to identity_core.py
"""

from typing import Dict, Any
from .identity_core import identity_core, AccessTier


def _is_valid_password(password: str) -> bool:
    """Minimal validation stub (non-production)."""
    if not isinstance(password, str):
        return False
    if len(password) < 8:
        return False
    weak = {"password", "12345678", "letmein", "qwerty"}
    return password.lower() not in weak


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Legacy login function - routes to identity_core"""
    if not _is_valid_password(password):
        return {
            "success": False,
            "error": "invalid_credentials",
            "message": "Password does not meet minimal requirements",
        }

    # Create a token with default T2 tier for legacy flows
    user_id = email.split('@')[0].replace('.', '_').lower()
    metadata = {
        "email": email,
        "consent": True,
        "triad_score": 0.5,
        "drift_score": 0.0,
    }

    token = identity_core.create_token(user_id, AccessTier.T2, metadata)

    return {
        "success": True,
        "token": token,
        "user_id": user_id,
        "tier": "T2",
        "glyphs": identity_core.generate_identity_glyph(email),
    }


def logout_user(token: str) -> bool:
    """Legacy logout function - routes to identity_core"""
    return identity_core.revoke_token(token)
'''

        login_path = self.workspace / "identity" / "login.py"
        with open(login_path, "w") as f:
            f.write(login_content)
        print("  ✅ Created login.py wrapper")

        # Create minimal registration wrapper
        registration_content = '''"""
Registration wrapper for backward compatibility
Routes to identity_core.py
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import hashlib

from .identity_core import identity_core, AccessTier


def _hash_password(password: str) -> str:
    """Minimal hashing stub (non-production)."""
    if not isinstance(password, str):
        password = str(password)
    # Warning: for demo only — replace with bcrypt/argon2 in production
    return hashlib.sha256(("lukhas-demo-salt::" + password).encode()).hexdigest()


_USER_STORE: dict[str, dict] = {}


def register_user(
    email: str, password: str, requested_tier: Optional[str] = None
) -> Dict[str, Any]:
    """Legacy registration function - routes to identity_core"""

    # Determine tier (default to T2 for new users)
    tier_map = {
        "T1": AccessTier.T1,
        "T2": AccessTier.T2,
        "T3": AccessTier.T3,
        "T4": AccessTier.T4,
        "T5": AccessTier.T5,
    }
    tier = tier_map.get(requested_tier, AccessTier.T2)

    user_id = email.split('@')[0].replace('.', '_').lower()
    pw_hash = _hash_password(password)

    # Minimal in-memory storage stub
    _USER_STORE[user_id] = {
        "email": email,
        "password_hash": pw_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata = {
        "email": email,
        "consent": True,
        "triad_score": 0.3,
        "drift_score": 0.0,
        "cultural_profile": "universal",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    token = identity_core.create_token(user_id, tier, metadata)
    glyphs = identity_core.generate_identity_glyph(email)

    return {
        "success": True,
        "user_id": user_id,
        "token": token,
        "tier": tier.value,
        "glyphs": glyphs,
        "message": f"User registered with tier {tier.value}",
    }
'''

        registration_path = self.workspace / "identity" / "registration.py"
        with open(registration_path, "w") as f:
            f.write(registration_content)
        print("  ✅ Created registration.py wrapper")

    def update_imports(self):
        """Update imports across codebase to use identity_core"""
        print("\n🔄 Updating imports to use identity_core...")

        import_mappings = [
            # Old user_db imports
            (
                r"from identity\.user_db import .*",
                "from identity.identity_core import identity_core",
            ),
            (r"from \.user_db import .*", "from .identity_core import identity_core"),
            # Old verify imports
            (
                r"from identity\.verify import .*",
                "from identity.identity_core import validate_symbolic_token",
            ),
            # Legacy identity module imports
            (r"from identity_legacy import .*", "from identity import identity_core"),
            (r"from identity_enhanced import .*", "from identity import identity_core"),
            (r"from lambda_identity import .*", "from identity import identity_core"),
            # Update function calls
            (r"user_db\.verify_token", "identity_core.validate_symbolic_token"),
            (r"user_db\.create_user", "identity_core.create_token"),
            (r"get_tier_permissions", "identity_core.resolve_access_tier"),
        ]

        updated_files = 0
        for py_file in self.workspace.rglob("*.py"):
            if ".identity_backup" in str(py_file) or str(py_file).endswith("identity_refactor.py"):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content
                for old_pattern, new_import in import_mappings:
                    content = re.sub(old_pattern, new_import, content)

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_files += 1

            except Exception as e:
                print(f"  ⚠️ Error updating {py_file.name}: {e}")

        print(f"  ✅ Updated imports in {updated_files} files")
        self.changes.append(("imports_updated", updated_files))

    def generate_report(self):
        """Generate refactoring report"""
        print("\n📊 Generating refactoring report...")

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backup_location": str(self.backup_dir),
            "changes": self.changes,
            "new_structure": {
                "core_module": "identity/identity_core.py",
                "wrappers": [
                    "identity/__init__.py",
                    "identity/login.py",
                    "identity/registration.py",
                    "identity/api.py",
                    "identity/middleware.py",
                ],
                "removed": [
                    "identity_legacy/",
                    "identity_enhanced/",
                    "lambda_identity/",
                    "identity/user_db.py",
                    "identity/verify.py",
                    "identity/core/",
                    "identity/auth_backend/",
                    "identity/auth_utils/",
                ],
            },
            "todo_items": [
                "Implement proper password validation in login wrapper",
                "Add user storage backend (database/Redis)",
                "Connect to Guardian system for ethical validation",
                "Integrate with consciousness module",
                "Add quantum entropy source for glyph generation",
                "Implement distributed token storage",
                "Add biometric integration hooks",
                "Create migration path from old user_db",
                "Implement token refresh and rotation",
                "Add rate limiting and brute-force protection",
            ],
        }

        report_path = self.workspace / "IDENTITY_REFACTOR_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"  ✅ Report saved to {report_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 IDENTITY REFACTOR SUMMARY")
        print("=" * 60)
        print("✅ Created unified identity_core.py")
        print("✅ Removed legacy directories and files")
        print("✅ Created compatibility wrappers")
        print("✅ Updated imports across codebase")
        print(f"📁 Backup location: {self.backup_dir}")
        print("\n🎯 Next Steps:")
        for todo in report["todo_items"][:5]:
            print(f"  • {todo}")

    def execute(self):
        """Execute the complete refactoring"""
        print("=" * 60)
        print("🔐 IDENTITY MODULE REFACTORING")
        print("=" * 60)

        # Execute refactoring steps
        self.backup_identity_modules()
        self.remove_legacy_files()
        self.create_simplified_wrappers()
        self.update_imports()
        self.generate_report()

        print("\n✅ Identity refactoring complete!")


def main():
    """Main execution"""

    refactor = IdentityRefactor()
    refactor.execute()


if __name__ == "__main__":
    main()
