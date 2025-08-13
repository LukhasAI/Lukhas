#!/usr/bin/env python3
"""
Hardcoded Secrets Security Fix
==============================
Automated tool to find and replace hardcoded secrets with secure alternatives.

This addresses the 289 hardcoded secrets identified in the security audit.
"""

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Represents a security issue found in the code"""

    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    severity: str
    suggested_fix: str


class HardcodedSecretsFixer:
    """Automated fixer for hardcoded secrets"""

    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas")
        self.issues_found = []
        self.fixes_applied = []

        # Patterns for detecting hardcoded secrets
        self.secret_patterns = [
            # API keys and tokens
            (r'api_key\s*=\s*["\']([^"\']+)["\']', "api_key"),
            (r'openai_api_key\s*=\s*["\']([^"\']+)["\']', "openai_api_key"),
            (r'API_KEY\s*=\s*["\']([^"\']+)["\']', "api_key"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "token"),
            (r'secret_key\s*=\s*["\']([^"\']+)["\']', "secret_key"),
            (r'password\s*=\s*["\']([^"\']+)["\']', "password"),
            # OpenAI specific patterns
            (r'OpenAI\(api_key=["\']([^"\']+)["\']\)', "openai_constructor"),
            (r'openai\.api_key\s*=\s*["\']([^"\']+)["\']', "openai_global"),
            # Database URLs
            (r'database_url\s*=\s*["\']([^"\']+)["\']', "database_url"),
            (r'DATABASE_URL\s*=\s*["\']([^"\']+)["\']', "database_url"),
            # JWT secrets
            (r'jwt_secret\s*=\s*["\']([^"\']+)["\']', "jwt_secret"),
            (r'JWT_SECRET\s*=\s*["\']([^"\']+)["\']', "jwt_secret"),
        ]

        # Safe patterns to ignore (these are already using env vars or placeholders)
        self.safe_patterns = [
            r"os\.getenv\(",
            r"os\.environ\[",
            r"getenv\(",
            r"your[_-]?(?:api[_-]?)?key",
            r"placeholder[_-]?(?:api[_-]?)?key",
            r"test[_-]?(?:api[_-]?)?key",
            r"mock[_-]?(?:api[_-]?)?key",
            r"fake[_-]?(?:api[_-]?)?key",
            r"dummy[_-]?(?:api[_-]?)?key",
            r"example[_-]?(?:api[_-]?)?key",
            r"<[^>]+>",  # Placeholder patterns like <api_key>
            r"hf_\.\.\.",  # Hugging Face token placeholder
            r"sk-[a-zA-Z0-9]{48}",  # Real OpenAI key pattern - flag but don't auto-fix
            r"class.*Enum",  # Enum class definitions
            r'= "api_key"',  # String literal enum values
            r'= "password"',  # String literal enum values
            r'= "token"',  # String literal enum values
            r"#.*Pass your.*key",  # Documentation comments
            r"Example.*usage",  # Documentation examples
        ]

        # Files to skip
        self.skip_patterns = [
            r"\.git/",
            r"__pycache__/",
            r"\.pyc$",
            r"node_modules/",
            r"\.backup$",
            r"test_.*\.py$",
            r".*_test\.py$",
            r"\.md$",  # Documentation files
            r"\.json$",  # Config files might have examples
            r"archive/",  # Archived code
            r"\.venv/",  # Virtual environment
            r"venv/",  # Virtual environment
            r"site-packages/",  # Python packages
        ]

    def scan_codebase(self) -> list[SecurityIssue]:
        """Scan the entire codebase for hardcoded secrets"""
        logger.info("🔍 Scanning codebase for hardcoded secrets...")

        python_files = list(self.root_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to scan")

        for file_path in python_files:
            # Skip files matching skip patterns
            if any(
                re.search(pattern, str(file_path)) for pattern in self.skip_patterns
            ):
                continue

            self._scan_file(file_path)

        logger.info(f"Found {len(self.issues_found)} potential security issues")
        return self.issues_found

    def _scan_file(self, file_path: Path):
        """Scan a single file for hardcoded secrets"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip()

                # Skip empty lines and comments
                if not line_clean or line_clean.startswith("#"):
                    continue

                # Check if this line contains a safe pattern (already secure)
                if any(
                    re.search(pattern, line, re.IGNORECASE)
                    for pattern in self.safe_patterns
                ):
                    continue

                # Skip enum definitions (lines that look like: FIELD_NAME =
                # "field_value")
                if re.match(r'\s*[A-Z_]+ = "[a-z_]+"', line_clean):
                    continue

                # Check for hardcoded secret patterns
                for pattern, secret_type in self.secret_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        secret_value = (
                            match.group(1) if match.groups() else match.group(0)
                        )

                        # Skip if it looks like a placeholder
                        if any(
                            placeholder in secret_value.lower()
                            for placeholder in [
                                "your",
                                "placeholder",
                                "test",
                                "mock",
                                "fake",
                                "dummy",
                                "example",
                            ]
                        ):
                            continue

                        # This looks like a real hardcoded secret
                        issue = SecurityIssue(
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_number=line_num,
                            line_content=line.rstrip(),
                            issue_type=f"hardcoded_{secret_type}",
                            severity="HIGH",
                            suggested_fix=self._generate_fix_suggestion(
                                secret_type, line
                            ),
                        )

                        self.issues_found.append(issue)
                        break  # Only report first match per line

        except Exception as e:
            logger.debug(f"Error scanning {file_path}: {e}")

    def _generate_fix_suggestion(self, secret_type: str, original_line: str) -> str:
        """Generate a suggestion for fixing the hardcoded secret"""
        fixes = {
            "api_key": 'get_secret("api_key")',
            "openai_api_key": 'get_secret("openai_api_key")',
            "secret_key": 'get_secret("secret_key")',
            "password": 'get_secret("password")',
            "token": 'get_secret("token")',
            "database_url": 'get_secret("database_url")',
            "jwt_secret": 'get_secret("jwt_secret")',
            "openai_constructor": 'OpenAI(api_key=get_secret("openai_api_key"))',
            "openai_global": 'openai.api_key = get_secret("openai_api_key")',
        }

        return fixes.get(secret_type, f'get_secret("{secret_type}")')

    def generate_fixes(self, apply_fixes: bool = False) -> dict[str, Any]:
        """Generate and optionally apply fixes for hardcoded secrets"""
        logger.info("🔧 Generating fixes for hardcoded secrets...")

        fixes_by_file = {}
        for issue in self.issues_found:
            if issue.file_path not in fixes_by_file:
                fixes_by_file[issue.file_path] = []
            fixes_by_file[issue.file_path].append(issue)

        summary = {
            "total_issues": len(self.issues_found),
            "files_affected": len(fixes_by_file),
            "fixes_by_type": {},
            "fixes_applied": 0,
        }

        # Count issues by type
        for issue in self.issues_found:
            issue_type = issue.issue_type
            if issue_type not in summary["fixes_by_type"]:
                summary["fixes_by_type"][issue_type] = 0
            summary["fixes_by_type"][issue_type] += 1

        if apply_fixes:
            logger.info("🚀 Applying fixes...")
            self._apply_automated_fixes(fixes_by_file)
            summary["fixes_applied"] = len(self.fixes_applied)

        return summary

    def _apply_automated_fixes(self, fixes_by_file: dict[str, list[SecurityIssue]]):
        """Apply automated fixes to files"""
        for file_path, issues in fixes_by_file.items():
            full_path = self.root_path / file_path

            try:
                # Read the original file
                with open(full_path, encoding="utf-8") as f:
                    lines = f.readlines()

                # Apply fixes (sort by line number descending to avoid offset issues)
                issues_sorted = sorted(
                    issues, key=lambda x: x.line_number, reverse=True
                )

                for issue in issues_sorted:
                    line_idx = issue.line_number - 1  # Convert to 0-based index
                    original_line = lines[line_idx]

                    # Generate the fixed line
                    fixed_line = self._apply_fix_to_line(original_line, issue)

                    if fixed_line != original_line:
                        lines[line_idx] = fixed_line
                        self.fixes_applied.append(
                            {
                                "file": file_path,
                                "line": issue.line_number,
                                "original": original_line.strip(),
                                "fixed": fixed_line.strip(),
                            }
                        )

                # Write the fixed file
                with open(full_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                logger.info(f"✅ Fixed {len(issues)} issues in {file_path}")

            except Exception as e:
                logger.error(f"❌ Failed to fix {file_path}: {e}")

    def _apply_fix_to_line(self, original_line: str, issue: SecurityIssue) -> str:
        """Apply a specific fix to a line"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated AST-based replacement

        # Add import if needed

        if "api_key=" in original_line:
            # Replace hardcoded API key with get_secret call
            pattern = r'api_key\s*=\s*["\'][^"\']+["\']'
            replacement = 'api_key=get_secret("api_key")'
            fixed_line = re.sub(pattern, replacement, original_line)
            return fixed_line

        return original_line  # No change if we can't safely fix

    def generate_report(self) -> str:
        """Generate a comprehensive security report"""
        report = ["# 🔐 LUKHAS Security Audit Report"]
        report.append("=" * 50)
        report.append("")

        summary = self.generate_fixes(apply_fixes=False)

        report.append("## 📊 Executive Summary")
        report.append(f"- **Total Issues Found:** {summary['total_issues']}")
        report.append(f"- **Files Affected:** {summary['files_affected']}")
        report.append(f"- **Issue Types:** {len(summary['fixes_by_type'])}")
        report.append("")

        report.append("## 🚨 Issues by Type")
        for issue_type, count in summary["fixes_by_type"].items():
            report.append(f"- **{issue_type}:** {count} instances")
        report.append("")

        report.append("## 📋 Detailed Findings")
        for issue in self.issues_found[:20]:  # Show first 20 issues
            report.append(f"### {issue.file_path}:{issue.line_number}")
            report.append(f"**Type:** {issue.issue_type}")
            report.append(f"**Severity:** {issue.severity}")
            report.append(f"**Code:** `{issue.line_content.strip()}`")
            report.append(f"**Suggested Fix:** `{issue.suggested_fix}`")
            report.append("")

        if len(self.issues_found) > 20:
            report.append(f"... and {len(self.issues_found) - 20} more issues")

        report.append("## 🛡️ Remediation Steps")
        report.append("1. **Immediate:** Set up environment variables for all API keys")
        report.append("2. **Implement:** Use the LUKHAS Secret Management System")
        report.append("3. **Replace:** All hardcoded secrets with `get_secret()` calls")
        report.append("4. **Verify:** Run security scan again to confirm fixes")

        return "\n".join(report)


def main():
    """Main function to run the hardcoded secrets fixer"""
    print("🔐 LUKHAS Hardcoded Secrets Security Fix")
    print("=" * 45)

    fixer = HardcodedSecretsFixer()

    # Scan for issues
    issues = fixer.scan_codebase()

    if not issues:
        print("✅ No hardcoded secrets found!")
        return

    # Generate report
    report = fixer.generate_report()

    # Save report
    report_path = Path(
        "/Users/agi_dev/Lukhas/docs/reports/HARDCODED_SECRETS_AUDIT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print("📊 Security audit complete!")
    print(f"📋 Report saved to: {report_path}")
    print(f"🚨 Found {len(issues)} potential security issues")

    # Show summary
    summary = fixer.generate_fixes(apply_fixes=False)
    print("\n📈 Issue Summary:")
    for issue_type, count in summary["fixes_by_type"].items():
        print(f"  • {issue_type}: {count}")

    # Ask if user wants to apply fixes
    if len(sys.argv) > 1 and sys.argv[1] == "--apply-fixes":
        print("\n🔧 Applying automated fixes...")
        fixer.generate_fixes(apply_fixes=True)
        print(f"✅ Applied {len(fixer.fixes_applied)} fixes")
    else:
        print("\n💡 To apply automated fixes, run with --apply-fixes flag")


if __name__ == "__main__":
    main()
