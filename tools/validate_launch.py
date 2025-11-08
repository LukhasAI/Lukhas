#!/usr/bin/env python3
"""
Launch Playbook Validator

Validates launch playbook completeness, required artifacts, and cross-functional sign-offs.
Part of LUKHAS AI branding governance system (GAPS A3).

Usage:
    python3 tools/validate_launch.py [--strict] [--playbook PATH]

Examples:
    # Validate all launch playbooks
    python3 tools/validate_launch.py

    # Validate specific playbook
    python3 tools/validate_launch.py --playbook branding/governance/launch/examples/reasoning_lab_launch.md

    # Strict mode (warnings = errors)
    python3 tools/validate_launch.py --strict

Exit Codes:
    0 = All validations passed
    1 = Validation errors found
    2 = Validation warnings found (only in strict mode)

Author: @web-architect
Created: 2025-11-08
"""

import argparse
import glob
import os
import re
import sys

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


class LaunchValidator:
    """Validates launch playbooks for completeness and compliance."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.info = []
        self.playbooks_validated = 0

    def validate_playbook(self, playbook_path: str) -> bool:
        """
        Validate a single launch playbook.

        Args:
            playbook_path: Path to playbook markdown file

        Returns:
            True if validation passed, False otherwise
        """
        if not os.path.exists(playbook_path):
            self.errors.append(f"Playbook not found: {playbook_path}")
            return False

        with open(playbook_path) as f:
            content = f.read()

        playbook_name = os.path.basename(playbook_path)
        self.info.append(f"Validating {playbook_name}...")

        # Run all validation checks
        self._validate_front_matter(content, playbook_name)
        self._validate_stakeholder_map(content, playbook_name)
        self._validate_checklist_presence(content, playbook_name)
        self._validate_rollback_plan(content, playbook_name)
        self._validate_success_metrics(content, playbook_name)
        self._validate_risk_register(content, playbook_name)
        self._validate_communication_templates(content, playbook_name)
        self._validate_evidence_links(content, playbook_name)
        self._validate_sign_offs(content, playbook_name)

        self.playbooks_validated += 1
        return len(self.errors) == 0

    def _validate_front_matter(self, content: str, playbook_name: str):
        """Validate required front-matter fields."""
        required_fields = [
            ("Launch Name", r"\*\*Launch Name\*\*:\s*(.+)"),
            ("Launch Type", r"\*\*Launch Type\*\*:\s*(.+)"),
            ("Launch Date", r"\*\*Launch Date\*\*:\s*(\d{4}-\d{2}-\d{2})"),
            ("Launch Lead", r"\*\*Launch Lead\*\*:\s*(@\S+)"),
            ("Executive Sponsor", r"\*\*Executive Sponsor\*\*:\s*(@\S+)"),
            ("Status", r"\*\*Status\*\*:\s*(.+)"),
        ]

        for field_name, pattern in required_fields:
            match = re.search(pattern, content)
            if not match:
                self.errors.append(
                    f"{playbook_name}: Missing required field '{field_name}'"
                )
            elif field_name == "Launch Date":
                # Validate date format
                date_str = match.group(1)
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                    self.errors.append(
                        f"{playbook_name}: Invalid date format for '{field_name}' (expected YYYY-MM-DD)"
                    )

    def _validate_stakeholder_map(self, content: str, playbook_name: str):
        """Validate stakeholder map completeness."""
        # Check for stakeholder table
        if "## Stakeholder Map" not in content:
            self.errors.append(
                f"{playbook_name}: Missing 'Stakeholder Map' section"
            )
            return

        # Check for required roles
        required_roles = [
            "Product Lead",
            "Engineering Lead",
            "Marketing Lead",
            "Legal Lead",
            "Security Lead",
        ]

        for role in required_roles:
            if f"**{role}**" not in content:
                self.warnings.append(
                    f"{playbook_name}: Missing stakeholder role '{role}'"
                )

        # Check for RACI matrix
        if "### RACI Matrix" not in content:
            self.warnings.append(
                f"{playbook_name}: Missing RACI Matrix (recommended)"
            )

    def _validate_checklist_presence(self, content: str, playbook_name: str):
        """Validate presence of required checklists."""
        required_checklists = [
            "## Pre-Launch Checklist",
            "### Technical Readiness",
            "### Marketing Readiness",
            "### Legal/Compliance Readiness",
        ]

        for checklist in required_checklists:
            if checklist not in content:
                self.errors.append(
                    f"{playbook_name}: Missing required checklist section '{checklist}'"
                )

        # Count checkbox items
        checkbox_count = len(re.findall(r"- \[[ x]\]", content))
        if checkbox_count < 20:
            self.warnings.append(
                f"{playbook_name}: Only {checkbox_count} checklist items (recommend ≥ 20 for comprehensive launch)"
            )

    def _validate_rollback_plan(self, content: str, playbook_name: str):
        """Validate rollback procedure documentation."""
        if "## Rollback Procedures" not in content:
            self.errors.append(
                f"{playbook_name}: Missing 'Rollback Procedures' section"
            )
            return

        # Check for rollback decision criteria
        if "Rollback Decision Criteria" not in content:
            self.warnings.append(
                f"{playbook_name}: Missing 'Rollback Decision Criteria'"
            )

        # Check for rollback execution steps
        if "Rollback Execution" not in content:
            self.warnings.append(
                f"{playbook_name}: Missing 'Rollback Execution' steps"
            )

    def _validate_success_metrics(self, content: str, playbook_name: str):
        """Validate success metrics and KPI definitions."""
        if "## Success Metrics" not in content and "## Success Metrics & KPIs" not in content:
            self.errors.append(
                f"{playbook_name}: Missing 'Success Metrics & KPIs' section"
            )
            return

        # Check for metric tables
        metric_categories = ["Adoption Metrics", "Performance Metrics"]
        for category in metric_categories:
            if category not in content:
                self.warnings.append(
                    f"{playbook_name}: Missing '{category}' in success metrics"
                )

        # Validate metric format (tables with Target and Actual columns)
        if "| Metric | Target | Actual | Status |" not in content:
            self.warnings.append(
                f"{playbook_name}: Success metrics should use table format with Target/Actual/Status columns"
            )

    def _validate_risk_register(self, content: str, playbook_name: str):
        """Validate risk register presence and completeness."""
        if "## Risk Register" not in content:
            self.warnings.append(
                f"{playbook_name}: Missing 'Risk Register' section (recommended)"
            )
            return

        # Check for risk table structure
        if "| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Owner |" not in content:
            self.warnings.append(
                f"{playbook_name}: Risk register should use standardized table format"
            )

    def _validate_communication_templates(self, content: str, playbook_name: str):
        """Validate communication template presence."""
        if "## Communication Templates" not in content:
            self.warnings.append(
                f"{playbook_name}: Missing 'Communication Templates' section (recommended)"
            )
            return

        # Check for key templates
        templates = [
            "Internal Announcement",
            "External Blog Post",
        ]

        for template in templates:
            if template not in content:
                self.warnings.append(
                    f"{playbook_name}: Missing '{template}' communication template"
                )

    def _validate_evidence_links(self, content: str, playbook_name: str):
        """Validate evidence page links for claims."""
        # Check for claims in content
        claim_patterns = [
            r"\d+%",  # Percentages
            r"<\s*\d+\s*ms",  # Latencies
            r"\d+k\+",  # Counts
        ]

        has_claims = any(re.search(pattern, content) for pattern in claim_patterns)

        if has_claims:
            # Check for evidence links
            if "/release_artifacts/evidence/" not in content:
                self.warnings.append(
                    f"{playbook_name}: Contains performance claims but no evidence links found"
                )
            else:
                # Extract evidence links
                evidence_links = re.findall(
                    r"/release_artifacts/evidence/([a-z0-9-]+)\.md", content
                )
                self.info.append(
                    f"{playbook_name}: Found {len(evidence_links)} evidence link(s)"
                )

                # Check if evidence files exist
                for link in evidence_links:
                    evidence_path = f"release_artifacts/evidence/{link}.md"
                    if not os.path.exists(evidence_path):
                        self.warnings.append(
                            f"{playbook_name}: Evidence file not found: {evidence_path}"
                        )

    def _validate_sign_offs(self, content: str, playbook_name: str):
        """Validate cross-functional sign-off tracking."""
        # Check for sign-off placeholders
        if "**Sign-off**:" not in content and "Sign-Off" not in content:
            self.warnings.append(
                f"{playbook_name}: No sign-off tracking found (recommended for cross-functional alignment)"
            )

    def validate_all_playbooks(self, playbook_dir: str = "branding/governance/launch") -> bool:
        """
        Validate all launch playbooks in a directory.

        Args:
            playbook_dir: Directory containing launch playbooks

        Returns:
            True if all validations passed, False otherwise
        """
        # Find all playbook files
        playbook_files = glob.glob(f"{playbook_dir}/**/*launch*.md", recursive=True)

        if not playbook_files:
            self.warnings.append(
                f"No launch playbooks found in {playbook_dir}"
            )
            return True

        all_valid = True
        for playbook_file in playbook_files:
            # Skip template files
            if "TEMPLATE" in playbook_file.upper():
                self.info.append(f"Skipping template: {playbook_file}")
                continue

            valid = self.validate_playbook(playbook_file)
            if not valid:
                all_valid = False

        return all_valid

    def print_summary(self):
        """Print validation summary with color-coded output."""
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}Launch Playbook Validation Summary{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}\n")

        # Print info messages
        if self.info:
            for msg in self.info:
                print(f"{BLUE}ℹ{RESET}  {msg}")
            print()

        # Print warnings
        if self.warnings:
            print(f"{YELLOW}⚠  Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"{YELLOW}   - {warning}{RESET}")
            print()

        # Print errors
        if self.errors:
            print(f"{RED}✖  Errors ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"{RED}   - {error}{RESET}")
            print()

        # Summary stats
        print(f"{BLUE}{'─' * 60}{RESET}")
        print(f"Playbooks validated: {self.playbooks_validated}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        # Final verdict
        if self.errors:
            print(f"\n{RED}✖ VALIDATION FAILED{RESET}")
            return False
        elif self.warnings and self.strict:
            print(f"\n{YELLOW}⚠ VALIDATION FAILED (strict mode){RESET}")
            return False
        elif self.warnings:
            print(f"\n{YELLOW}⚠ VALIDATION PASSED (with warnings){RESET}")
            return True
        else:
            print(f"\n{GREEN}✓ VALIDATION PASSED{RESET}")
            return True


def main():
    """Main entry point for launch playbook validation."""
    parser = argparse.ArgumentParser(
        description="Validate launch playbook completeness and compliance"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail on warnings)",
    )
    parser.add_argument(
        "--playbook",
        type=str,
        help="Path to specific playbook to validate (default: validate all)",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="branding/governance/launch",
        help="Directory containing launch playbooks (default: branding/governance/launch)",
    )

    args = parser.parse_args()

    validator = LaunchValidator(strict=args.strict)

    try:
        if args.playbook:
            # Validate specific playbook
            success = validator.validate_playbook(args.playbook)
        else:
            # Validate all playbooks
            success = validator.validate_all_playbooks(args.dir)

        # Print summary
        final_success = validator.print_summary()

        # Exit with appropriate code
        if not final_success:
            if validator.errors:
                sys.exit(1)  # Errors found
            elif validator.warnings and args.strict:
                sys.exit(2)  # Warnings found (strict mode)

        sys.exit(0)

    except Exception as e:
        print(f"{RED}✖ Unexpected error: {e}{RESET}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
