#!/usr/bin/env python3
"""
🔍 lukhas Comprehensive Organization Scanner
Scans for naming issues, misplaced files, and organizational problems

This script identifies:
1. PascalCase files that should be snake_case
2. Empty directories
3. Misplaced .md files
4. Inconsistent naming patterns
5. Files that should be in different locations

Author: lukhas AI Enhancement Team
Date: 2025-06-05
Version: 1.0.0
"""

import re
from collections import defaultdict
from pathlib import Path


class OrganizationScanner:
    """Comprehensive scanner for organizational issues"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.Λ_path = self.workspace_root / "lukhas"

        self.issues = {
            "pascal_case_files": [],
            "mixed_case_dirs": [],
            "misplaced_md_files": [],
            "empty_directories": [],
            "inconsistent_naming": [],
            "duplicate_names": defaultdict(list),
            "large_files": [],
            "orphaned_files": [],
        }

    def scan_pascal_case_issues(self):
        """Find files using PascalCase that should use snake_case"""
        print("🔍 Scanning for PascalCase files...")

        for py_file in self.lukhas_path.rglob("*.py"):
            if py_file.stem == "__init__":
                continue

            # Check if filename is PascalCase
            if re.match(r"^[A-Z][a-zA-Z0-9]*([A-Z][a-zA-Z0-9]*)*$", py_file.stem):
                relative_path = py_file.relative_to(self.workspace_root)
                suggested_name = self._pascal_to_snake(py_file.stem)
                self.issues["pascal_case_files"].append(
                    {
                        "file": str(relative_path),
                        "current": py_file.stem,
                        "suggested": suggested_name,
                    }
                )

    def scan_directory_naming(self):
        """Find directories with naming issues"""
        print("📁 Scanning directory naming...")

        for dir_path in self.lukhas_path.rglob("*"):
            if dir_path.is_dir():
                dir_name = dir_path.name

                # Skip standard directories
                if dir_name in ["__pycache__", ".git", ".DS_Store"]:
                    continue

                # Check for mixed case in directory names
                if re.search(r"[A-Z].*[a-z]", dir_name) and "_" in dir_name:
                    self.issues["mixed_case_dirs"].append(str(dir_path.relative_to(self.workspace_root)))

                # Check if directory is empty
                try:
                    if not any(dir_path.iterdir()):
                        self.issues["empty_directories"].append(str(dir_path.relative_to(self.workspace_root)))
                except PermissionError:
                    pass

    def scan_misplaced_documentation(self):
        """Find .md files that might be misplaced"""
        print("📄 Scanning for misplaced documentation...")

        for md_file in self.lukhas_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.workspace_root)

            # Check if .md file is in core directories (suspicious)
            if "/core/" in str(relative_path) and md_file.name not in [
                "README.md",
                "ARCHITECTURE.md",
                "API.md",
            ]:
                # Additional checks for legitimate docs
                if not any(keyword in md_file.name.upper() for keyword in ["AUDIT", "ARCHITECTURE", "DESIGN", "SPEC"]):
                    self.issues["misplaced_md_files"].append(str(relative_path))

    def scan_duplicate_names(self):
        """Find files with duplicate names across different directories"""
        print("🔄 Scanning for duplicate names...")

        name_locations = defaultdict(list)

        for file_path in self.lukhas_path.rglob("*"):
            if file_path.is_file():
                name_locations[file_path.name].append(str(file_path.relative_to(self.workspace_root)))

        for name, locations in name_locations.items():
            if len(locations) > 1:
                self.issues["duplicate_names"][name] = locations

    def scan_large_files(self):
        """Find unusually large files that might need attention"""
        print("📊 Scanning for large files...")

        for file_path in self.lukhas_path.rglob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size > 1024 * 1024:  # Files larger than 1MB
                        size_mb = size / (1024 * 1024)
                        self.issues["large_files"].append(
                            {
                                "file": str(file_path.relative_to(self.workspace_root)),
                                "size_mb": round(size_mb, 2),
                            }
                        )
                except OSError:
                    pass

    def scan_orphaned_files(self):
        """Find files that might be in wrong locations"""
        print("🔍 Scanning for orphaned files...")

        # Files that might be misplaced
        suspicious_patterns = [
            (r".*test.*\.py$", "tests"),
            (r".*config.*\.py$", "config"),
            (r".*setup.*\.py$", "deployment"),
            (r".*main.*\.py$", "applications"),
            (r".*cli.*\.py$", "interface"),
        ]

        for file_path in self.lukhas_path.rglob("*.py"):
            relative_path = str(file_path.relative_to(self.workspace_root))

            for pattern, expected_category in suspicious_patterns:
                if re.search(pattern, file_path.name, re.IGNORECASE):
                    if expected_category not in relative_path:
                        self.issues["orphaned_files"].append(
                            {
                                "file": relative_path,
                                "current_location": str(file_path.parent.relative_to(self.workspace_root)),
                                "suggested_category": expected_category,
                                "reason": f"Matches pattern: {pattern}",
                            }
                        )

    def _pascal_to_snake(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        # Insert underscore before uppercase letters (except first)
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def generate_report(self) -> str:
        """Generate comprehensive organization report"""
        report = f"""
# 🔍 lukhas COMPREHENSIVE ORGANIZATION SCAN REPORT

**Generated:** {self.get_timestamp()}
**Scanner:** Comprehensive Organization Scanner v1.0.0

---

## 📊 ISSUES SUMMARY

### 🚨 Critical Issues
- **PascalCase Files:** {len(self.issues["pascal_case_files"])} files
- **Empty Directories:** {len(self.issues["empty_directories"])} directories
- **Misplaced Documentation:** {len(self.issues["misplaced_md_files"])} files

### ⚠️ Organization Issues
- **Mixed Case Directories:** {len(self.issues["mixed_case_dirs"])} directories
- **Duplicate Names:** {len(self.issues["duplicate_names"])} names
- **Large Files:** {len(self.issues["large_files"])} files
- **Orphaned Files:** {len(self.issues["orphaned_files"])} files

---

## 🔧 NAMING CONVENTION FIXES NEEDED

"""

        if self.issues["pascal_case_files"]:
            report += "### 📄 PascalCase Files (should be snake_case):\n"
            for issue in self.issues["pascal_case_files"][:10]:
                report += f"- `{issue['file']}` → `{issue['suggested']}.py`\n"
            if len(self.issues["pascal_case_files"]) > 10:
                report += f"- ... and {len(self.issues['pascal_case_files']) - 10} more\n"

        if self.issues["mixed_case_dirs"]:
            report += "\n### 📁 Mixed Case Directories:\n"
            for dir_name in self.issues["mixed_case_dirs"][:5]:
                report += f"- `{dir_name}`\n"

        report += f"""
---

## 🧹 CLEANUP OPPORTUNITIES

### 🗑️ Empty Directories ({len(self.issues["empty_directories"])})
"""

        for empty_dir in self.issues["empty_directories"][:10]:
            report += f"- `{empty_dir}`\n"

        if self.issues["misplaced_md_files"]:
            report += f"\n### 📄 Misplaced Documentation ({len(self.issues['misplaced_md_files'])})\n"
            for md_file in self.issues["misplaced_md_files"][:5]:
                report += f"- `{md_file}`\n"

        if self.issues["large_files"]:
            report += f"\n### 🐘 Large Files ({len(self.issues['large_files'])})\n"
            for large_file in sorted(self.issues["large_files"], key=lambda x: x["size_mb"], reverse=True)[:5]:
                report += f"- `{large_file['file']}` ({large_file['size_mb']} MB)\n"

        # Show some duplicate names
        if self.issues["duplicate_names"]:
            report += "\n### 🔄 Duplicate Names (showing top 5)\n"
            count = 0
            for name, locations in self.issues["duplicate_names"].items():
                if count >= 5:
                    break
                if len(locations) > 1:
                    report += f"\n**{name}:**\n"
                    for loc in locations[:3]:
                        report += f"  - `{loc}`\n"
                    if len(locations) > 3:
                        report += f"  - ... and {len(locations) - 3} more\n"
                    count += 1

        report += f"""
---

## 🎯 RECOMMENDED ACTIONS

### 1. Fix Naming Conventions
- Rename {len(self.issues["pascal_case_files"])} PascalCase files to snake_case
- Address mixed case in directory names

### 2. Clean Up Structure
- Remove {len(self.issues["empty_directories"])} empty directories
- Relocate misplaced documentation files

### 3. Review Large Files
- Check if large files should be compressed or archived
- Consider breaking down large modules

### 4. Resolve Duplicates
- Review duplicate filenames for potential conflicts
- Consolidate or rename as appropriate

---

## ✅ COMPLETION STATUS

**Organization Scan:** Complete
**Issues Identified:** {sum(len(v) if isinstance(v, list) else len(v) for v in self.issues.values())}
**Ready for:** Manual fixes and automated cleanup

"""

        return report

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def execute_scan(self) -> str:
        """Execute complete organization scan"""
        print("🚀 Starting comprehensive organization scan...")

        self.scan_pascal_case_issues()
        self.scan_directory_naming()
        self.scan_misplaced_documentation()
        self.scan_duplicate_names()
        self.scan_large_files()
        self.scan_orphaned_files()

        report = self.generate_report()

        # Save report
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = self.workspace_root / f"lukhas_ORGANIZATION_SCAN_REPORT_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📋 Report saved: {report_path}")
        return str(report_path)


def main():
    """Execute organization scan"""
    workspace_root = "/Users/A_G_I/CodexGPT_Lukhas"

    scanner = lukhasOrganizationScanner(workspace_root)
    report_path = scanner.execute_scan()

    print("\n🎉 ORGANIZATION SCAN COMPLETE!")
    print(f"📋 Report: {report_path}")

    # Print summary
    total_issues = sum(len(v) if isinstance(v, list) else len(v) for v in scanner.issues.values())
    print(f"🔍 Total Issues Found: {total_issues}")


if __name__ == "__main__":
    main()

# Λ Systems 2025 www.lukhas.ai
