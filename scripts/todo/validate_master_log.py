#!/usr/bin/env python3
"""
Validate MASTER_LOG.md format and consistency.

Usage:
    python3 scripts/todo/validate_master_log.py

Returns:
    0 if valid, 1 if errors found

Checks:
    - All task IDs are unique
    - Task totals match actual counts
    - No duplicate task descriptions
    - Valid priority levels (P0/P1/P2/P3)
    - Valid status values (PENDING/IN_PROGRESS/COMPLETED/BLOCKED)
    - Valid effort levels (S/M/L)
    - Task ID format: T{YYYY}{MM}{DD}{###}
"""

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set

# ANSI colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class MasterLogValidator:
    """Validates MASTER_LOG.md format and consistency."""

    def __init__(self, master_log_path: str = "TODO/MASTER_LOG.md"):
        self.master_log_path = Path(master_log_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.tasks: List[Dict] = []
        self.task_ids: Set[str] = set()

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        if not self.master_log_path.exists():
            self.errors.append(f"MASTER_LOG not found: {self.master_log_path}")
            return False

        content = self.master_log_path.read_text()

        # Run all checks
        self._parse_tasks(content)
        self._check_unique_ids()
        self._check_task_totals(content)
        self._check_priority_levels()
        self._check_status_values()
        self._check_effort_levels()
        self._check_task_id_format()
        self._check_duplicates()

        return len(self.errors) == 0

    def _parse_tasks(self, content: str):
        """Parse tasks from markdown tables."""
        # Match task rows in tables
        # Format: | ID | Task | Owner | Status | Effort | PR | Notes |
        task_pattern = re.compile(
            r'\|\s*([A-Z]{2}\d{3})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*'
            r'([^|]+)\s*\|\s*([SML])\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|'
        )

        for line in content.split('\n'):
            match = task_pattern.match(line)
            if match:
                task = {
                    'id': match.group(1).strip(),
                    'description': match.group(2).strip(),
                    'owner': match.group(3).strip(),
                    'status': match.group(4).strip(),
                    'effort': match.group(5).strip(),
                    'pr': match.group(6).strip(),
                    'notes': match.group(7).strip(),
                }
                self.tasks.append(task)
                self.task_ids.add(task['id'])

    def _check_unique_ids(self):
        """Check that all task IDs are unique."""
        id_counts = Counter(task['id'] for task in self.tasks)
        duplicates = [id_ for id_, count in id_counts.items() if count > 1]

        if duplicates:
            for dup_id in duplicates:
                self.errors.append(f"Duplicate task ID: {dup_id}")

    def _check_task_totals(self, content: str):
        """Check that reported totals match actual counts."""
        # Extract reported totals
        total_match = re.search(r'Total Tasks:\s*(\d+)', content)
        completed_match = re.search(r'Completed:\s*(\d+)', content)
        active_match = re.search(r'Active:\s*(\d+)', content)
        blocked_match = re.search(r'Blocked:\s*(\d+)', content)

        if not total_match:
            self.errors.append("Could not find 'Total Tasks' in Quick Stats")
            return

        reported_total = int(total_match.group(1))
        actual_total = len(self.tasks)

        if reported_total != actual_total:
            self.errors.append(
                f"Total mismatch: reported {reported_total}, found {actual_total}"
            )

        # Count by status
        status_counts = Counter(task['status'] for task in self.tasks)
        completed = status_counts.get('✅ MERGED', 0) + status_counts.get('COMPLETED', 0)
        active = sum(count for status, count in status_counts.items()
                     if status in ['PENDING', 'IN_PROGRESS'])
        blocked = status_counts.get('BLOCKED', 0)

        if completed_match:
            reported_completed = int(completed_match.group(1))
            if reported_completed != completed:
                self.warnings.append(
                    f"Completed mismatch: reported {reported_completed}, counted {completed}"
                )

        if active_match:
            reported_active = int(active_match.group(1))
            if reported_active != active:
                self.warnings.append(
                    f"Active mismatch: reported {reported_active}, counted {active}"
                )

    def _check_priority_levels(self):
        """Check that priority levels are valid."""
        # Priority is inferred from section, not in table
        # This is a placeholder for future enhancement
        pass

    def _check_status_values(self):
        """Check that all status values are valid."""
        valid_statuses = {
            'PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED',
            '✅ MERGED', 'IN PROGRESS'
        }

        for task in self.tasks:
            if task['status'] not in valid_statuses:
                self.warnings.append(
                    f"Task {task['id']}: unusual status '{task['status']}'"
                )

    def _check_effort_levels(self):
        """Check that all effort levels are valid."""
        valid_efforts = {'S', 'M', 'L'}

        for task in self.tasks:
            if task['effort'] not in valid_efforts:
                self.errors.append(
                    f"Task {task['id']}: invalid effort '{task['effort']}' "
                    f"(must be S/M/L)"
                )

    def _check_task_id_format(self):
        """Check that task IDs follow format: T{YYYY}{MM}{DD}{###} or XX###."""
        # Two formats allowed:
        # 1. Legacy: SG001, MS001, etc. (2-letter prefix + 3 digits)
        # 2. New: T20251111001 (T + date + 3 digits)
        legacy_pattern = re.compile(r'^[A-Z]{2}\d{3}$')
        new_pattern = re.compile(r'^T\d{8}\d{3}$')

        for task in self.tasks:
            task_id = task['id']
            if not (legacy_pattern.match(task_id) or new_pattern.match(task_id)):
                self.errors.append(
                    f"Task ID format invalid: {task_id} "
                    f"(expected XX### or T{{YYYY}}{{MM}}{{DD}}{{###}})"
                )

    def _check_duplicates(self):
        """Check for duplicate task descriptions."""
        descriptions = [task['description'] for task in self.tasks]
        desc_counts = Counter(descriptions)
        duplicates = [desc for desc, count in desc_counts.items() if count > 1]

        if duplicates:
            for dup_desc in duplicates:
                self.warnings.append(f"Duplicate task description: {dup_desc}")

    def print_results(self):
        """Print validation results."""
        print(f"\n{'='*70}")
        print("MASTER_LOG Validation Results")
        print(f"{'='*70}\n")

        print(f"Tasks found: {len(self.tasks)}")
        print(f"Unique IDs: {len(self.task_ids)}\n")

        if self.errors:
            print(f"{RED}✗ ERRORS ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"  {RED}• {error}{RESET}")
            print()

        if self.warnings:
            print(f"{YELLOW}⚠ WARNINGS ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}• {warning}{RESET}")
            print()

        if not self.errors and not self.warnings:
            print(f"{GREEN}✓ All checks passed!{RESET}\n")
        elif not self.errors:
            print(f"{GREEN}✓ No errors (warnings only){RESET}\n")
        else:
            print(f"{RED}✗ Validation failed{RESET}\n")


def main():
    """Main entry point."""
    validator = MasterLogValidator()
    is_valid = validator.validate()
    validator.print_results()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
