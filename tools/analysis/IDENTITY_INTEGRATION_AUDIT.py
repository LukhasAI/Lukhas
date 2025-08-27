#!/usr/bin/env python3
"""
LUKHAS  Identity Integration Audit
======================================
Comprehensive analysis of identity module integration across the codebase.
Checks tier-based access control, login enforcement, and user ID linking.
"""

import json
import re
from pathlib import Path

# Key modules that should have tier-based access control
PROTECTED_MODULES = {
    "consciousness": "T3",  # Requires T3 or above
    "dream": "T3",  # Requires T3 or above
    "emotion": "T3",  # Requires T3 or above
    "quantum": "T4",  # Requires T4 or above
    "governance": "T5",  # Requires T5 (Guardian)
    "api": "T2",  # Requires T2 for API access
}

# API endpoint patterns that should be protected
API_PATTERNS = [
    r"@app\.(get|post|put|delete|patch)",
    r"@router\.(get|post|put|delete|patch)",
    r"async def.*\(.*\):",
]

# Identity import patterns
IDENTITY_PATTERNS = [
    r"from identity",
    r"import.*identity",
    r"AccessTier",
    r"IdentityCore",
    r"get_current_user",
    r"require_t\d",
    r"require_tier",
    r"require_permission",
    r"AuthContext",
]

# Tier enforcement patterns
ENFORCEMENT_PATTERNS = [
    r"Depends\(get_current_user\)",
    r"Depends\(require_t\d",
    r"@require_tier",
    r"@require_permission",
    r"has_permission\(",
    r"is_tier_or_above\(",
    r"check_permission\(",
]


class IdentityAudit:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = []
        self.stats = {
            "total_modules": 0,
            "protected_modules": 0,
            "unprotected_modules": 0,
            "api_endpoints": 0,
            "protected_endpoints": 0,
            "unprotected_endpoints": 0,
            "files_with_identity": 0,
            "files_without_identity": 0,
        }
        self.module_report = {}

    def audit(self):
        """Run complete identity integration audit."""
        print("🔍 LUKHAS  Identity Integration Audit")
        print("=" * 60)

        # 1. Check protected modules
        self._audit_protected_modules()

        # 2. Check API endpoints
        self._audit_api_endpoints()

        # 3. Check user ID linking
        self._audit_user_linking()

        # 4. Generate report
        self._generate_report()

    def _audit_protected_modules(self):
        """Check if protected modules enforce tier access."""
        print("\n📁 Auditing Protected Modules...")

        for module_name, required_tier in PROTECTED_MODULES.items():
            module_path = self.root_path / module_name
            if not module_path.exists():
                continue

            self.stats["total_modules"] += 1
            module_info = {
                "name": module_name,
                "required_tier": required_tier,
                "files_checked": 0,
                "files_protected": 0,
                "files_unprotected": 0,
                "unprotected_files": [],
            }

            # Check all Python files in module
            for py_file in module_path.rglob("*.py"):
                if any(
                    skip in str(py_file)
                    for skip in ["__pycache__", "test", "backup", "archive"]
                ):
                    continue

                module_info["files_checked"] += 1

                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for identity imports
                has_identity = any(
                    re.search(pattern, content) for pattern in IDENTITY_PATTERNS
                )

                # Check for enforcement
                has_enforcement = any(
                    re.search(pattern, content) for pattern in ENFORCEMENT_PATTERNS
                )

                if has_enforcement:
                    module_info["files_protected"] += 1
                else:
                    module_info["files_unprotected"] += 1
                    if not has_identity:
                        module_info["unprotected_files"].append(
                            str(py_file.relative_to(self.root_path))
                        )

            if module_info["files_protected"] > 0:
                self.stats["protected_modules"] += 1
            else:
                self.stats["unprotected_modules"] += 1

            self.module_report[module_name] = module_info

            # Report module status
            protection_rate = (
                module_info["files_protected"] / module_info["files_checked"] * 100
                if module_info["files_checked"] > 0
                else 0
            )

            status = (
                "✅" if protection_rate > 50 else "⚠️" if protection_rate > 0 else "❌"
            )
            print(
                f"  {status} {module_name}: {protection_rate:.1f}% protected ({module_info['files_protected']}/{module_info['files_checked']} files)"
            )

    def _audit_api_endpoints(self):
        """Check if API endpoints are protected."""
        print("\n🌐 Auditing API Endpoints...")

        api_path = self.root_path / "api"
        if not api_path.exists():
            print("  ⚠️ API directory not found")
            return

        for py_file in api_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ["__pycache__", "test", "backup"]):
                continue

            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Find all endpoints
            endpoints = []
            for pattern in API_PATTERNS:
                endpoints.extend(re.findall(pattern, content))

            if not endpoints:
                continue

            # Check if file has identity protection
            any(
                re.search(pattern, content) for pattern in IDENTITY_PATTERNS
            )
            has_enforcement = any(
                re.search(pattern, content) for pattern in ENFORCEMENT_PATTERNS
            )

            self.stats["api_endpoints"] += len(endpoints)

            if has_enforcement:
                self.stats["protected_endpoints"] += len(endpoints)
                status = "✅"
            else:
                self.stats["unprotected_endpoints"] += len(endpoints)
                status = "❌"
                self.issues.append(
                    f"Unprotected API file: {py_file.relative_to(self.root_path)}"
                )

            print(f"  {status} {py_file.name}: {len(endpoints)} endpoints")

    def _audit_user_linking(self):
        """Check if modules properly link to user IDs."""
        print("\n🔗 Auditing User ID Linking...")

        user_patterns = [
            r"user_id",
            r"user\.id",
            r"user\.user_id",
            r"current_user",
            r"auth_context",
            r"AuthContext",
        ]

        modules_with_user_linking = []
        modules_without_user_linking = []

        for module_dir in self.root_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("."):
                continue

            if module_dir.name in ["tests", "docs", "tools", "__pycache__"]:
                continue

            has_user_linking = False

            for py_file in module_dir.rglob("*.py"):
                if any(
                    skip in str(py_file) for skip in ["__pycache__", "test", "backup"]
                ):
                    continue

                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if any(re.search(pattern, content) for pattern in user_patterns):
                    has_user_linking = True
                    break

            if has_user_linking:
                modules_with_user_linking.append(module_dir.name)
            else:
                modules_without_user_linking.append(module_dir.name)

        print(f"  ✅ Modules with user linking: {len(modules_with_user_linking)}")
        print(f"  ❌ Modules without user linking: {len(modules_without_user_linking)}")

        # Show critical modules without user linking
        critical_without_linking = [
            m for m in modules_without_user_linking if m in PROTECTED_MODULES
        ]

        if critical_without_linking:
            print("\n  ⚠️ Critical modules without user linking:")
            for module in critical_without_linking:
                print(f"    - {module}")
                self.issues.append(f"Critical module without user linking: {module}")

    def _generate_report(self):
        """Generate comprehensive audit report."""
        print("\n" + "=" * 60)
        print("📊 IDENTITY INTEGRATION AUDIT REPORT")
        print("=" * 60)

        # Overall statistics
        print("\n📈 Overall Statistics:")
        print(
            f"  • Protected Modules: {self.stats['protected_modules']}/{self.stats['total_modules']}"
        )
        print(
            f"  • Protected API Endpoints: {self.stats['protected_endpoints']}/{self.stats['api_endpoints']}"
        )

        # Module breakdown
        print("\n🔐 Module Protection Status:")
        for module_name, info in self.module_report.items():
            if info["files_unprotected"] > 0:
                print(f"\n  {module_name} (Tier {info['required_tier']} Required):")
                print(f"    • Protected: {info['files_protected']} files")
                print(f"    • Unprotected: {info['files_unprotected']} files")
                if info["unprotected_files"][:5]:  # Show first 5
                    print("    • Sample unprotected files:")
                    for file in info["unprotected_files"][:5]:
                        print(f"      - {file}")

        # Critical Issues
        if self.issues:
            print("\n⚠️ Critical Issues Found:")
            for issue in self.issues[:10]:  # Show first 10
                print(f"  • {issue}")

        # Recommendations
        print("\n💡 Recommendations:")

        if self.stats["unprotected_endpoints"] > 0:
            print("  1. Add authentication to all API endpoints using:")
            print("     from identity import get_current_user, AuthContext")
            print(
                "     async def endpoint(user: AuthContext = Depends(get_current_user)):"
            )

        if self.stats["unprotected_modules"] > 0:
            print("\n  2. Protect sensitive modules with tier checks:")
            print("     from identity import require_tier, require_permission")
            print("     @require_tier('T3')  # For consciousness, dream, emotion")
            print("     @require_tier('T4')  # For quantum")
            print("     @require_tier('T5')  # For governance")

        print("\n  3. Link user IDs in all data operations:")
        print("     data['user_id'] = user.user_id")
        print("     audit_log(user_id=user.user_id, action='...')")

        # Save report
        report_path = self.root_path / "identity_audit_report.json"
        report_data = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "statistics": self.stats,
            "module_report": self.module_report,
            "issues": self.issues,
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Full report saved to: {report_path}")

        # Final verdict
        protection_score = (
            (self.stats["protected_modules"] / max(self.stats["total_modules"], 1))
            * 0.4
            + (self.stats["protected_endpoints"] / max(self.stats["api_endpoints"], 1))
            * 0.6
        ) * 100

        print("\n" + "=" * 60)
        if protection_score > 80:
            print(f"✅ IDENTITY INTEGRATION: GOOD ({protection_score:.1f}%)")
        elif protection_score > 50:
            print(
                f"⚠️ IDENTITY INTEGRATION: NEEDS IMPROVEMENT ({protection_score:.1f}%)"
            )
        else:
            print(f"❌ IDENTITY INTEGRATION: CRITICAL ({protection_score:.1f}%)")
        print("=" * 60)


if __name__ == "__main__":
    auditor = IdentityAudit()
    auditor.audit()
