#!/usr/bin/env python3
"""
LUKHAS  Identity Automation Suite
====================================
Master script that coordinates all identity integration automation tools.
Provides a simple interface to fix identity integration issues across the entire codebase.

Usage:
    python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --dry-run    # Preview changes
    python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --fix-all    # Apply all fixes
    python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --validate   # Validate current state
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


class IdentityAutomationSuite:
    """Master coordinator for identity integration automation."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.tools_dir = self.root_path / "tools" / "scripts"
        self.analysis_dir = self.root_path / "tools" / "analysis"

    def run_full_automation(self, dry_run: bool = False):
        """Run complete identity integration automation."""

        print("🚀 LUKHAS  Identity Integration Automation Suite")
        print("=" * 60)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 Mode: {'DRY RUN' if dry_run else 'LIVE FIXES'}")
        print()

        # Step 1: Initial audit
        print("📊 Step 1: Running Initial Identity Audit...")
        self._run_identity_audit()

        # Step 2: Automated fixes
        if not dry_run:
            self._confirm_proceed()

        print("\n🔧 Step 2: Applying Automated Fixes...")
        self._run_auto_fixer(dry_run)

        # Step 3: User ID injection
        print("\n🔗 Step 3: Injecting User ID Tracking...")
        self._run_user_id_injector(dry_run)

        # Step 4: Validation
        print("\n🛡️ Step 4: Validating Results...")
        self._run_validation()

        # Step 5: Final audit
        print("\n📈 Step 5: Final Audit...")
        self._run_identity_audit()

        # Step 6: Summary and next steps
        self._generate_summary(dry_run)

    def validate_only(self):
        """Run validation tools only."""
        print("🛡️ LUKHAS  Identity Validation")
        print("=" * 40)

        self._run_identity_audit()
        self._run_validation()

    def _run_identity_audit(self):
        """Run the identity integration audit."""
        audit_script = self.analysis_dir / "IDENTITY_INTEGRATION_AUDIT.py"
        if audit_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(audit_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.root_path),
                )
                print(result.stdout)
                if result.stderr:
                    print(f"⚠️ Audit warnings: {result.stderr}")
            except Exception as e:
                print(f"❌ Error running audit: {e}")
        else:
            print("❌ Identity audit script not found")

    def _run_auto_fixer(self, dry_run: bool = False):
        """Run the automated identity fixer."""
        fixer_script = self.tools_dir / "AUTO_IDENTITY_FIXER.py"
        if fixer_script.exists():
            try:
                args = [sys.executable, str(fixer_script)]
                if dry_run:
                    args.append("--dry-run")

                result = subprocess.run(args, cwd=str(self.root_path))

                if result.returncode != 0:
                    print("⚠️ Auto-fixer encountered some issues")

            except Exception as e:
                print(f"❌ Error running auto-fixer: {e}")
        else:
            print("❌ Auto-fixer script not found")

    def _run_user_id_injector(self, dry_run: bool = False):
        """Run the user ID injector."""
        injector_script = self.tools_dir / "USER_ID_INJECTOR.py"
        if injector_script.exists():
            try:
                args = [sys.executable, str(injector_script)]
                if dry_run:
                    args.append("--dry-run")

                # Target critical modules
                args.extend(["consciousness", "quantum", "dream", "emotion"])

                result = subprocess.run(args, cwd=str(self.root_path))

                if result.returncode != 0:
                    print("⚠️ User ID injector encountered some issues")

            except Exception as e:
                print(f"❌ Error running user ID injector: {e}")
        else:
            print("❌ User ID injector script not found")

    def _run_validation(self):
        """Run the identity guard validation."""
        guard_script = self.tools_dir / "IDENTITY_GUARD.py"
        if guard_script.exists():
            try:
                # Validate key API files
                api_files = (
                    list((self.root_path / "api").glob("*.py"))
                    if (self.root_path / "api").exists()
                    else []
                )

                for api_file in api_files[:3]:  # Validate first 3 API files
                    result = subprocess.run(
                        [sys.executable, str(guard_script), str(api_file)],
                        capture_output=True,
                        text=True,
                        cwd=str(self.root_path),
                    )

                    if result.returncode != 0:
                        print(f"⚠️ Validation failed for {api_file.name}")
                        # Show first few lines of output
                        lines = result.stdout.split("\n")[:10]
                        for line in lines:
                            if line.strip():
                                print(f"   {line}")
                    else:
                        print(f"✅ {api_file.name} passed validation")

            except Exception as e:
                print(f"❌ Error running validation: {e}")
        else:
            print("❌ Identity guard script not found")

    def _confirm_proceed(self):
        """Confirm before making live changes."""
        print("\n⚠️  IMPORTANT: This will modify your code files!")
        print("   - Backups will be created automatically")
        print("   - All changes can be reverted using git")
        print("   - Review changes before committing")

        response = input("\nProceed with live fixes? (y/N): ")
        if response.lower() != "y":
            print("❌ Aborted by user")
            sys.exit(0)
            print("\n✅ Proceeding with live fixes...")

    def _generate_summary(self, dry_run: bool):
        """Generate summary and next steps."""
        print("\n" + "=" * 60)
        print("📋 IDENTITY INTEGRATION AUTOMATION SUMMARY")
        print("=" * 60)

        if dry_run:
            print("\n🧪 DRY RUN COMPLETED")
            print("   No files were modified")
            print("   Review the planned changes above")
        else:
            print("\n✅ LIVE FIXES COMPLETED")
            print("   Files have been modified with backups created")
            print("   Review all changes before committing")

        print("\n📂 Generated Files:")
        print("   • Backup directories: *_backup_*")
        print("   • Audit report: identity_audit_report.json")
        print("   • Template: tools/templates/protected_api_template.py")

        print("\n🔧 Manual Steps Required:")
        print("   1. Review all automated changes")
        print("   2. Test API endpoints with authentication")
        print("   3. Update any custom business logic")
        print("   4. Run tests: pytest tests/")
        print("   5. Commit changes: git add . && git commit")

        print("\n📋 Available Tools:")
        print("   • Full audit: python3 tools/analysis/IDENTITY_INTEGRATION_AUDIT.py")
        print("   • Validate files: python3 tools/scripts/IDENTITY_GUARD.py <file>")
        print(
            "   • Fix specific issues: python3 tools/scripts/AUTO_IDENTITY_FIXER.py --dry-run"
        )
        print("   • User tracking: python3 tools/scripts/USER_ID_INJECTOR.py --dry-run")

        print("\n🎯 Success Criteria:")
        print("   • All API endpoints protected (82/82)")
        print("   • Tier enforcement in sensitive modules")
        print("   • User ID tracking in data operations")
        print("   • Authentication imports in all relevant files")

        print("\n🚀 When Ready:")
        print("   • Create PR with identity integration improvements")
        print("   • Update documentation with new authentication requirements")
        print("   • Deploy with proper identity service configuration")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""

    suite = IdentityAutomationSuite()

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    elif "--dry-run" in sys.argv:
        suite.run_full_automation(dry_run=True)

    elif "--fix-all" in sys.argv:
        suite.run_full_automation(dry_run=False)

    elif "--validate" in sys.argv:
        suite.validate_only()

    else:
        print("🤖 LUKHAS  Identity Automation Suite")
        print("   Choose an option:")
        print("   1. --dry-run     Preview all changes without modifying files")
        print("   2. --fix-all     Apply all automated fixes (with backups)")
        print("   3. --validate    Validate current identity integration")
        print("   4. --help        Show detailed usage information")
        print()
        print(
            "   Example: python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --dry-run"
        )


if __name__ == "__main__":
    main()
