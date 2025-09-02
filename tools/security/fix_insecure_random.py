#!/usr/bin/env python3
"""
LUKHAS AI - tools/security/fix_insecure_random.py

Small, robust script to find and replace insecure uses of Python's
`random` module with a secure random wrapper located at
`lukhas.security.secure_random`.

This file is intentionally conservative: it performs text-based checks
and replacements and logs counts of files and fixes applied. Designed to
be run from the repository root or via CI tooling.
"""

import re
import sys
from pathlib import Path
from typing import Union

# Make repository root importable when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class InsecureRandomFixer:
    """Automated fixer for insecure random module usage."""

    def __init__(self, root_dir: Union[Path, str]):
        self.root_dir = Path(root_dir)
        self.fixes_applied = 0
        self.files_processed = 0

        # Patterns to consider insecure
        self.security_critical_patterns = [
            r"random\.random\(\)",
            r"random\.randint\(",
            r"random\.randrange\(",
            r"random\.choice\(",
            r"random\.choices\(",
            r"random\.sample\(",
            r"random\.shuffle\(",
            r"random\.uniform\(",
            r"random\.gauss\(",
            r"random\.normalvariate\(",
        ]

        # Directories considered higher priority for security fixes
        self.critical_dirs = [
            "governance",
            "security",
            "identity",
            "auth",
            "crypto",
            "privacy",
            "entropy",
            "symbolic",
            "guardian",
            "compliance",
        ]

        # Files/paths to skip
        self.skip_patterns = [
            r"\.venv",
            r"__pycache__",
            r"node_modules",
            r"\.git",
            r"venv",
            r"build",
            r"dist",
            r"\.egg-info",
            r"site-packages",
            r"test.*\.py$",
        ]

    def should_skip_file(self, file_path: Path) -> bool:
        file_str = str(file_path)
        return any(re.search(p, file_str) for p in self.skip_patterns)

    def is_security_critical(self, file_path: Path) -> bool:
        file_str = str(file_path).lower()
        return any(d in file_str for d in self.critical_dirs)

    def analyze_file(self, file_path: Path) -> tuple[list[str], bool]:
        """Return (issues, is_critical) found in file_path."""
        try:
            with open(file_path, encoding="utf-8") as fh:
                content = fh.read()

            issues: list[str] = []
            if re.search(r"^import random\s*$", content, re.MULTILINE):
                issues.append("Uses 'import random'")
            if re.search(r"^from random import", content, re.MULTILINE):
                issues.append("Uses 'from random import'")

            # collect pattern matches
            issues.extend(f"Uses {p}" for p in self.security_critical_patterns if re.search(p, content))

            return issues, self.is_security_critical(file_path)
        except Exception as exc:  # pragma: no cover - best effort script
            print(f"Error analyzing {file_path}: {exc}")
            return [], False

    def fix_file(self, file_path: Path) -> bool:
        """Apply conservative textual replacements and write the file if changed."""
        try:
            with open(file_path, encoding="utf-8") as fh:
                original = fh.read()

            content = original
            fixes = 0

            # Replace top-level `import random` with secure wrapper import
            if re.search(r"^import random\s*$", content, re.MULTILINE):
                replacement = (
                    "# SECURITY FIX: Replaced insecure random with secure random\n"
                    "from lukhas.security import secure_random"
                )
                content = re.sub(r"^import random\s*$", replacement, content, flags=re.MULTILINE)
                fixes += 1

            # Replace `from random import X` with direct secure_random imports
            content = re.sub(
                r"^from random import (.+)$",
                r"# SECURITY FIX: Replaced insecure random imports\nfrom lukhas.security.secure_random import \1",
                content,
                flags=re.MULTILINE,
            )

            replacements = {
                r"random\.random\(\)": "secure_random.random()",
                r"random\.randint\(": "secure_random.randint(",
                r"random\.randrange\(": "secure_random.randrange(",
                r"random\.choice\(": "secure_random.choice(",
                r"random\.choices\(": "secure_random.choices(",
                r"random\.sample\(": "secure_random.sample(",
                r"random\.shuffle\(": "secure_random.shuffle(",
                r"random\.uniform\(": "secure_random.uniform(",
                r"random\.gauss\(": "secure_random.gauss(",
                r"random\.normalvariate\(": "secure_random.normalvariate(",
            }

            for pat, repl in replacements.items():
                if re.search(pat, content):
                    content = re.sub(pat, repl, content)
                    fixes += 1

            if fixes > 0 and content != original:
                with open(file_path, "w", encoding="utf-8") as fh:
                    fh.write(content)
                self.fixes_applied += fixes
                print(f"✅ Fixed {fixes} issues in {file_path}")
                return True
            return False
        except Exception as exc:  # pragma: no cover
            print(f"❌ Error fixing {file_path}: {exc}")
            return False

    def scan_directory(self) -> dict[str, list[tuple[Path, list[str], bool]]]:
        results: dict[str, list[tuple[Path, list[str], bool]]] = {"critical": [], "normal": []}
        for file_path in self.root_dir.rglob("*.py"):
            if self.should_skip_file(file_path):
                continue
            issues, is_critical = self.analyze_file(file_path)
            if issues:
                category = "critical" if is_critical else "normal"
                results[category].append((file_path, issues, is_critical))
        return results

    def fix_all_files(self) -> None:
        print("🔍 Scanning for insecure random usage...")
        results = self.scan_directory()
        total_files = len(results["critical"]) + len(results["normal"])
        if total_files == 0:
            print("✅ No insecure random usage found!")
            return

        print(f"\n🚨 Found {total_files} files with insecure random usage:")
        print(f"   📍 {len(results['critical'])} security-critical files")
        print(f"   📍 {len(results['normal'])} normal files")

        print("\n🛡️ Fixing CRITICAL security files first:")
        for file_path, issues, _ in results["critical"]:
            print(f"\n🚨 CRITICAL: {file_path}")
            for issue in issues:
                print(f"   - {issue}")
            self.fix_file(file_path)
            self.files_processed += 1

        print(f"\n📝 Fixing remaining {len(results['normal'])} files:")
        for file_path, issues, _ in results["normal"]:
            print(f"\n📁 {file_path}")
            for issue in issues:
                print(f"   - {issue}")
            self.fix_file(file_path)
            self.files_processed += 1

        print("\n✅ SECURITY FIX COMPLETE!")
        print(f"   📊 Files processed: {self.files_processed}")
        print(f"   🔧 Total fixes applied: {self.fixes_applied}")

    def generate_report(self) -> str:
        results = self.scan_directory()
        report = f"""
# LUKHAS AI - Insecure Random Usage Security Report
Generated: {Path(__file__).name}

## Summary
- **Total files scanned**: {len(list(self.root_dir.rglob("*.py")))}
- **Files with insecure random usage**: {len(results["critical"]) + len(results["normal"]) }
- **Security-critical files**: {len(results["critical"]) }
- **Normal files**: {len(results["normal"]) }

## Security-Critical Files (Priority 1)
"""
        for file_path, issues, _ in results["critical"]:
            report += f"\n### 🚨 {file_path}\n"
            for issue in issues:
                report += f"- {issue}\n"

        report += "\n## Normal Files (Priority 2)\n"
        for file_path, issues, _ in results["normal"]:
            report += f"\n### 📁 {file_path}\n"
            for issue in issues:
                report += f"- {issue}\n"
        return report


def main() -> None:
    root_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent
    fixer = InsecureRandomFixer(root_dir)
    if "--report-only" in sys.argv:
        report = fixer.generate_report()
        print(report)
        report_file = Path(root_dir) / "docs" / "security" / "insecure_random_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"\n📄 Report saved to: {report_file}")
    else:
        fixer.fix_all_files()


if __name__ == "__main__":
    main()
