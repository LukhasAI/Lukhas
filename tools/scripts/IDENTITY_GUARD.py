#!/usr/bin/env python3
"""
LUKHAS  Identity Guard
=========================
Pre-commit hook and validation tool to ensure new code follows identity integration standards.
Prevents unprotected API endpoints and missing user tracking from being committed.
"""

import re
import sys
from pathlib import Path


class IdentityGuard:
    """Validate identity integration in code changes."""

    def __init__(self):
        self.violations = []
        self.warnings = []

    def validate_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """Validate a single file for identity compliance."""

        if not file_path.exists() or file_path.suffix != ".py":
            return True, []

        content = file_path.read_text()
        file_violations = []

        # Check API endpoints
        if self._is_api_file(file_path):
            file_violations.extend(self._check_api_protection(content, file_path))

        # Check sensitive modules
        if self._is_sensitive_module(file_path):
            file_violations.extend(self._check_module_protection(content, file_path))

        # Check data operations
        file_violations.extend(self._check_user_tracking(content, file_path))

        return len(file_violations) == 0, file_violations

    def _is_api_file(self, file_path: Path) -> bool:
        """Check if file contains API endpoints."""
        return (
            "api" in str(file_path)
            or file_path.name.endswith("_api.py")
            or "router" in file_path.name.lower()
            or "endpoint" in file_path.name.lower()
        )

    def _is_sensitive_module(self, file_path: Path) -> bool:
        """Check if file is in a sensitive module requiring tier protection."""
        sensitive_dirs = ["consciousness", "quantum", "dream", "emotion", "governance"]
        return any(sens_dir in str(file_path) for sens_dir in sensitive_dirs)

    def _check_api_protection(self, content: str, file_path: Path) -> list[str]:
        """Check API endpoints for proper authentication."""
        violations = []

        # Find API endpoint decorators
        endpoint_patterns = [
            r"@app\.(get|post|put|delete|patch)\(",
            r"@router\.(get|post|put|delete|patch)\(",
            r"@[a-zA-Z_]+\.(get|post|put|delete|patch)\(",
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines):
            for pattern in endpoint_patterns:
                if re.search(pattern, line):
                    # Found an endpoint, check next few lines for function def
                    func_def_found = False
                    has_auth = False

                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j]

                        if re.match(r"\s*async def\s+\w+", next_line) or re.match(
                            r"\s*def\s+\w+", next_line
                        ):
                            func_def_found = True

                            # Check if function has authentication
                            if any(
                                auth_pattern in next_line
                                for auth_pattern in [
                                    "AuthContext",
                                    "get_current_user",
                                    "require_t",
                                    "Depends",
                                ]
                            ):
                                has_auth = True
                                break

                    if func_def_found and not has_auth:
                        violations.append(
                            f"❌ UNPROTECTED API ENDPOINT at {file_path}:{i+1}\n"
                            f"   Endpoint: {line.strip()}\n"
                            f"   Required: Add 'user: AuthContext = Depends(require_tX_or_above)'\n"
                        )

        return violations

    def _check_module_protection(self, content: str, file_path: Path) -> list[str]:
        """Check sensitive modules for tier protection."""
        violations = []

        # Determine required tier based on module
        module_tiers = {
            "consciousness": "T3",
            "dream": "T3",
            "emotion": "T3",
            "quantum": "T4",
            "governance": "T5",
        }

        required_tier = None
        for module, tier in module_tiers.items():
            if module in str(file_path):
                required_tier = tier
                break

        if required_tier:
            # Check for identity imports
            has_identity_import = any(
                pattern in content
                for pattern in [
                    "from identity",
                    "import identity",
                    "AuthContext",
                    "require_tier",
                ]
            )

            # Check for public functions that should be protected
            public_functions = re.findall(
                r"^\s*(async\s+)?def\s+([a-zA-Z_]\w*)", content, re.MULTILINE
            )
            unprotected_functions = [
                func
                for _, func in public_functions
                if not func.startswith("_") and func not in ["main", "__init__"]
            ]

            if unprotected_functions and not has_identity_import:
                violations.append(
                    f"⚠️ SENSITIVE MODULE WITHOUT IDENTITY at {file_path}\n"
                    f"   Module requires tier: {required_tier}\n"
                    f"   Public functions: {', '.join(unprotected_functions[:3])}{'...' if len(unprotected_functions) > 3 else ''}\n"
                    f"   Required: Add identity imports and tier checks\n"
                )

        return violations

    def _check_user_tracking(self, content: str, file_path: Path) -> list[str]:
        """Check for proper user ID tracking in data operations."""
        violations = []

        # Look for data operations that should track users
        data_operations = [
            r"\.save\(",
            r"\.insert\(",
            r"\.create\(",
            r"\.update\(",
            r"data\s*=\s*\{",
            r"result\s*=\s*\{",
            r"log_data\s*=\s*\{",
        ]

        has_user_tracking = "user_id" in content or "user.user_id" in content

        if not has_user_tracking:
            for pattern in data_operations:
                if re.search(pattern, content):
                    clean_pattern = pattern.replace("\\\\", "\\")
                    violations.append(
                        f"⚠️ DATA OPERATION WITHOUT USER TRACKING at {file_path}\n"
                        f"   Found: {clean_pattern}\n"
                        f"   Required: Add user_id to data operations\n"
                        f"   Example: data['user_id'] = user.user_id\n"
                    )
                    break  # Only report once per file

        return violations

    def validate_changes(self, changed_files: list[str] = None) -> bool:
        """Validate changed files for identity compliance."""

        if changed_files is None:
            # Get changed files from git
            import subprocess

            try:
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    capture_output=True,
                    text=True,
                    cwd=".",
                )
                changed_files = (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
            except:
                print("⚠️ Could not get git changes, validating all API files")
                changed_files = []

        if not changed_files:
            # Fallback: check critical API files
            api_dir = Path(".") / "api"
            if api_dir.exists():
                changed_files = [str(f) for f in api_dir.glob("*.py")]

        print("🛡️ LUKHAS Identity Guard - Validating Changes")
        print("=" * 50)

        all_valid = True

        for file_path_str in changed_files:
            if not file_path_str or not file_path_str.endswith(".py"):
                continue

            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            is_valid, violations = self.validate_file(file_path)

            if not is_valid:
                all_valid = False
                print(f"\n📁 {file_path}")
                for violation in violations:
                    print(f"   {violation}")

        if all_valid:
            print("✅ All files pass identity validation!")
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ IDENTITY VALIDATION FAILED")
            print("=" * 50)
            print("\n🔧 Quick Fixes:")
            print(
                "  • API endpoints: Add 'user: AuthContext = Depends(require_t3_or_above)'"
            )
            print(
                "  • Imports: Add 'from identity.middleware import AuthContext, require_t3_or_above'"
            )
            print("  • User tracking: Add 'data[\"user_id\"] = user.user_id'")
            print("\n🔨 Automated fix: python3 tools/scripts/AUTO_IDENTITY_FIXER.py")
            print("📖 Template: tools/templates/protected_api_template.py")
            return False


def main():
    """Main entry point for pre-commit hook."""

    guard = IdentityGuard()

    # Check if running as pre-commit hook
    if "--pre-commit" in sys.argv:
        # Get staged files
        is_valid = guard.validate_changes()
        sys.exit(0 if is_valid else 1)
    else:
        # Manual validation mode
        files = sys.argv[1:] if len(sys.argv) > 1 else None
        is_valid = guard.validate_changes(files)

        if is_valid:
            print("\n🚀 Ready to commit!")
        else:
            print("\n⚠️ Fix violations before committing")
            print(
                "💡 Run automated fixer: python3 tools/scripts/AUTO_IDENTITY_FIXER.py"
            )


if __name__ == "__main__":
    main()
