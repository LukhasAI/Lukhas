#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - SECURITY FIX: INSECURE RANDOM USAGE
║ Automated script to replace insecure random module usage with secure alternatives
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: fix_insecure_random.py  
║ Path: tools/security/fix_insecure_random.py
║ Version: 1.0.0 | Created: 2025-09-01
║ Authors: LUKHAS AI Security Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ This script systematically replaces insecure usage of Python's random module
║ with cryptographically secure alternatives from lukhas.security.secure_random.
║ It identifies and fixes security vulnerabilities in random number generation
║ across the LUKHAS AI codebase.
║
║ CRITICAL SECURITY ISSUE: Python's random module uses a deterministic
║ Mersenne Twister algorithm that is NOT suitable for security purposes.
║ This script replaces it with secrets-based cryptographically secure random.
╚═══════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add lukhas to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class InsecureRandomFixer:
    """Automated fixer for insecure random module usage"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.fixes_applied = 0
        self.files_processed = 0
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

        # Critical directories that should be prioritized
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
            "compliance"
        ]

        # Files to skip (known to be safe or external dependencies)
        self.skip_patterns = [
            r"\.venv.*",
            r"__pycache__",
            r"node_modules",
            r"\.git",
            r"venv",
            r"build",
            r"dist",
            r"\.egg-info",
            r"site-packages",
            r"test.*\.py$",  # Skip test files for now as they may use random for non-security purposes
        ]

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in self.skip_patterns)

    def is_security_critical(self, file_path: Path) -> bool:
        """Check if file is in a security-critical directory"""
        file_str = str(file_path).lower()
        return any(critical_dir in file_str for critical_dir in self.critical_dirs)

    def analyze_file(self, file_path: Path) -> Tuple[List[str], bool]:
        """Analyze file for insecure random usage"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            issues = []

            # Check for import random
            if re.search(r"^import random\s*$", content, re.MULTILINE):
                issues.append("Uses 'import random'")

            if re.search(r"^from random import", content, re.MULTILINE):
                issues.append("Uses 'from random import'")

            # Check for random function calls
            for pattern in self.security_critical_patterns:
                if re.search(pattern, content):
                    issues.append(f"Uses {pattern}")

            is_critical = self.is_security_critical(file_path)
            return issues, is_critical

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return [], False

    def fix_file(self, file_path: Path) -> bool:
        """Fix insecure random usage in a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            content = original_content
            fixes_made = 0

            # Replace import statements
            if re.search(r"^import random\s*$", content, re.MULTILINE):
                content = re.sub(
                    r"^import random\s*$",
                    "# SECURITY FIX: Replaced insecure random with secure random\nfrom lukhas.security import secure_random",
                    content,
                    flags=re.MULTILINE
                )
                fixes_made += 1

            # Replace from random import statements
            content = re.sub(
                r"^from random import (.+)$",
                r"# SECURITY FIX: Replaced insecure random imports\nfrom lukhas.security.secure_random import \1",
                content,
                flags=re.MULTILINE
            )

            # Replace random function calls
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

            for pattern, replacement in replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes_made += 1

            # Write back if changes were made
            if content != original_content and fixes_made > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes_applied += fixes_made
                print(f"✅ Fixed {fixes_made} issues in {file_path}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False

    def scan_directory(self) -> Dict[str, List[Tuple[Path, List[str], bool]]]:
        """Scan directory for Python files with insecure random usage"""
        results = {
            "critical": [],
            "normal": []
        }

        for file_path in self.root_dir.rglob("*.py"):
            if self.should_skip_file(file_path):
                continue

            issues, is_critical = self.analyze_file(file_path)
            if issues:
                category = "critical" if is_critical else "normal"
                results[category].append((file_path, issues, is_critical))

        return results

    def fix_all_files(self) -> None:
        """Fix all files with insecure random usage"""
        print("🔍 Scanning for insecure random usage...")
        results = self.scan_directory()

        total_files = len(results["critical"]) + len(results["normal"])
        if total_files == 0:
            print("✅ No insecure random usage found!")
            return

        print(f"\n🚨 Found {total_files} files with insecure random usage:")
        print(f"   📍 {len(results['critical'])} security-critical files")
        print(f"   📍 {len(results['normal'])} normal files")

        # Fix critical files first
        print("\n🛡️ Fixing CRITICAL security files first:")
        for file_path, issues, _ in results["critical"]:
            print(f"\n🚨 CRITICAL: {file_path}")
            for issue in issues:
                print(f"   - {issue}")
            self.fix_file(file_path)
            self.files_processed += 1

        # Then fix normal files
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
        """Generate a security fix report"""
        results = self.scan_directory()

        report = f"""
# LUKHAS AI - Insecure Random Usage Security Report
Generated: {Path(__file__).name}

## Summary
- **Total files scanned**: {len(list(self.root_dir.rglob('*.py')))}
- **Files with insecure random usage**: {len(results['critical']) + len(results['normal'])}
- **Security-critical files**: {len(results['critical'])}
- **Normal files**: {len(results['normal'])}

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


def main():
    """Main function"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        # Default to LUKHAS root directory
        root_dir = Path(__file__).parent.parent.parent

    fixer = InsecureRandomFixer(root_dir)

    if "--report-only" in sys.argv:
        report = fixer.generate_report()
        print(report)

        # Save report to file
        report_file = Path(root_dir) / "docs" / "security" / "insecure_random_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_file}")
    else:
        fixer.fix_all_files()


if __name__ == "__main__":
    main()
