#!/usr/bin/env python3
"""
Check licenses of Python dependencies.

Scans installed packages and reports license compliance.
Outputs report to docs/audits/licenses.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import json
from typing import Dict, List, Set

# Approved open-source licenses
APPROVED_LICENSES: Set[str] = {
    "MIT",
    "MIT License",
    "Apache-2.0",
    "Apache Software License",
    "Apache License 2.0",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "BSD License",
    "ISC",
    "ISC License (ISCL)",
    "Python Software Foundation License",
    "PSF",
    "Public Domain",
    "The Unlicense",
    "Mozilla Public License 2.0 (MPL 2.0)",
    "MPL-2.0",
}


def get_package_licenses() -> List[Dict[str, str]]:
    """
    Get licenses for all installed packages using pip-licenses.
    
    Returns:
        List of dicts with keys: Name, Version, License
    """
    try:
        # Install pip-licenses if not available
        subprocess.run(
            [sys.executable, "-m", "pip", "show", "pip-licenses"],
            capture_output=True,
            check=False
        )

        # Run pip-licenses
        result = subprocess.run(
            [sys.executable, "-m", "pip_licenses", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to run pip-licenses: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse pip-licenses output: {e}")
        sys.exit(1)


def check_license_compliance(packages: List[Dict[str, str]]) -> tuple[List[Dict], List[Dict]]:
    """
    Check packages for license compliance.
    
    Returns:
        tuple: (approved_packages, violations)
    """
    approved = []
    violations = []

    for pkg in packages:
        license_name = pkg.get("License", "UNKNOWN")

        # Check if license is approved
        if license_name in APPROVED_LICENSES or license_name == "UNKNOWN":
            approved.append(pkg)
        else:
            violations.append(pkg)

    return approved, violations


def generate_report(packages: List[Dict], violations: List[Dict], output_path: Path):
    """Generate markdown report of license compliance."""

    total = len(packages)
    violation_count = len(violations)
    approved_count = total - violation_count

    lines = [
        "# License Compliance Report",
        "",
        f"**Generated**: {Path.cwd()}",
        f"**Total Packages**: {total}",
        f"**Approved**: {approved_count}",
        f"**Violations**: {violation_count}",
        "",
    ]

    if violations:
        lines.extend([
            "## ⚠️ License Violations",
            "",
            "The following packages have licenses that require review:",
            "",
            "| Package | Version | License |",
            "|---------|---------|---------|",
        ])

        for pkg in sorted(violations, key=lambda p: p["Name"]):
            name = pkg["Name"]
            version = pkg["Version"]
            license_name = pkg["License"]
            lines.append(f"| {name} | {version} | {license_name} |")

        lines.extend([
            "",
            "### Actions Required",
            "",
            "1. **Review each license** to determine compatibility",
            "2. **Replace packages** with unapproved licenses if possible",
            "3. **Document exceptions** in `.license-exceptions.json`",
            "4. **Seek legal review** if unsure about compatibility",
            "",
        ])
    else:
        lines.extend([
            "## ✅ All Licenses Approved",
            "",
            "All installed packages use approved open-source licenses.",
            "",
        ])

    # Add approved licenses section
    lines.extend([
        "## Approved Licenses",
        "",
        "The following licenses are automatically approved:",
        "",
    ])

    for license_name in sorted(APPROVED_LICENSES):
        lines.append(f"- {license_name}")

    lines.extend([
        "",
        "## Package Summary (Sample)",
        "",
        "| Package | Version | License |",
        "|---------|---------|---------|",
    ])

    # Show sample of approved packages
    for pkg in sorted(packages[:25], key=lambda p: p["Name"]):
        name = pkg["Name"]
        version = pkg["Version"]
        license_name = pkg["License"]
        lines.append(f"| {name} | {version} | {license_name} |")

    if len(packages) > 25:
        lines.append(f"| ... | ... | *({len(packages) - 25} more packages)* |")

    lines.append("")

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Check Python package license compliance"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/audits/licenses.md"),
        help="Output file path (default: docs/audits/licenses.md)"
    )
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit with code 1 if violations found"
    )

    args = parser.parse_args()

    print("[licenses] Scanning installed packages...")

    # Get all package licenses
    packages = get_package_licenses()
    print(f"[licenses] Found {len(packages)} installed packages")

    # Check compliance
    approved, violations = check_license_compliance(packages)

    # Generate report
    print(f"[licenses] Generating report to {args.out}...")
    generate_report(packages, violations, args.out)

    # Print summary
    print()
    print(f"[licenses] ✅ Approved: {len(approved)}")

    if violations:
        print(f"[licenses] ⚠️  Violations: {len(violations)}")
        print()
        print("Packages with unapproved licenses:")
        for pkg in violations:
            print(f"  - {pkg['Name']} {pkg['Version']}: {pkg['License']}")
        print()
        print(f"[licenses] Report written to: {args.out}")

        if args.fail_on_violation:
            return 1
    else:
        print("[licenses] ✅ No license violations found")
        print(f"[licenses] Report written to: {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
