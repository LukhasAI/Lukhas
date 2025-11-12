#!/usr/bin/env python3
"""
Process TODOs from TODO/inbox/ directory.

Usage:
    python3 scripts/todo/process_inbox.py [--dry-run] [--priority P1]

Process files in TODO/inbox/:
- Parse structured markdown or plain text
- Assign task IDs
- Add to MASTER_LOG.md
- Move processed files to TODO/inbox/processed/

Options:
    --dry-run: Show what would be done without making changes
    --priority: Override priority (P0/P1/P2/P3)
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class InboxProcessor:
    """Process quick-drop TODOs from inbox directory."""

    def __init__(self, inbox_path: str = "TODO/inbox", dry_run: bool = False):
        self.inbox_path = Path(inbox_path)
        self.master_log_path = Path("TODO/MASTER_LOG.md")
        self.processed_path = self.inbox_path / "processed"
        self.dry_run = dry_run

    def process_all(self, override_priority: Optional[str] = None):
        """Process all files in inbox."""
        if not self.inbox_path.exists():
            print(f"{YELLOW}Inbox directory not found: {self.inbox_path}{RESET}")
            return

        # Create processed directory
        if not self.dry_run:
            self.processed_path.mkdir(exist_ok=True)

        # Find all markdown and text files (except template and README)
        inbox_files = []
        for ext in ['*.md', '*.txt']:
            inbox_files.extend(self.inbox_path.glob(ext))

        inbox_files = [
            f for f in inbox_files
            if f.name not in ['_TEMPLATE.md', 'README.md', 'processed']
        ]

        if not inbox_files:
            print(f"{BLUE}No files to process in inbox{RESET}")
            return

        print(f"\n{BLUE}Processing {len(inbox_files)} inbox files...{RESET}\n")

        for file_path in inbox_files:
            self._process_file(file_path, override_priority)

    def _process_file(self, file_path: Path, override_priority: Optional[str]):
        """Process a single inbox file."""
        print(f"Processing: {file_path.name}")

        content = file_path.read_text()
        task = self._parse_task(content, file_path)

        if override_priority:
            task['priority'] = override_priority

        if self.dry_run:
            print(f"  {YELLOW}[DRY RUN]{RESET} Would add:")
            print(f"    ID: {task['id']}")
            print(f"    Task: {task['description']}")
            print(f"    Priority: {task['priority']}")
            print(f"    Owner: {task['owner']}")
            print(f"    Effort: {task['effort']}")
        else:
            self._add_to_master_log(task)
            self._move_to_processed(file_path)
            print(f"  {GREEN}✓{RESET} Added as {task['id']} (P{task['priority']})")

        print()

    def _parse_task(self, content: str, file_path: Path) -> Dict:
        """Parse task from file content."""
        # Try to extract structured fields
        title_match = re.search(r'#\s*TODO:?\s*(.+)', content, re.IGNORECASE)
        priority_match = re.search(r'Priority.*:\s*(P[0-3])', content, re.IGNORECASE)
        effort_match = re.search(r'Effort.*:\s*([SML])', content, re.IGNORECASE)
        owner_match = re.search(r'Owner.*:\s*(\w+)', content, re.IGNORECASE)
        source_match = re.search(r'Source.*:\s*(\w+)', content, re.IGNORECASE)

        # Extract or use defaults
        description = title_match.group(1).strip() if title_match else file_path.stem
        priority = priority_match.group(1)[1] if priority_match else '3'  # Default P3
        effort = effort_match.group(1) if effort_match else 'M'  # Default M
        owner = owner_match.group(1) if owner_match else 'human'  # Default human
        source = source_match.group(1) if source_match else 'inbox'

        # Generate task ID
        task_id = self._generate_task_id()

        return {
            'id': task_id,
            'description': description,
            'priority': priority,
            'effort': effort,
            'owner': owner,
            'source': source,
            'notes': f'From inbox: {file_path.name}',
        }

    def _generate_task_id(self) -> str:
        """Generate next task ID for today."""
        today = datetime.now()
        date_prefix = today.strftime("T%Y%m%d")

        # Read MASTER_LOG to find last ID for today
        if not self.master_log_path.exists():
            return f"{date_prefix}001"

        content = self.master_log_path.read_text()

        # Find all IDs with today's date
        pattern = re.compile(rf'{date_prefix}(\d{{3}})')
        matches = pattern.findall(content)

        if not matches:
            return f"{date_prefix}001"

        # Get highest sequential number
        highest = max(int(m) for m in matches)
        next_seq = highest + 1

        return f"{date_prefix}{next_seq:03d}"

    def _add_to_master_log(self, task: Dict):
        """Add task to MASTER_LOG.md in appropriate priority section."""
        if not self.master_log_path.exists():
            print(f"{YELLOW}MASTER_LOG not found, skipping{RESET}")
            return

        content = self.master_log_path.read_text()

        # Find the priority section
        priority_num = int(task['priority'])
        section_header = f"## Priority {priority_num}"

        # Find insertion point (after section header and table header)
        section_pattern = re.compile(
            rf'{re.escape(section_header)}.*?\n\|.*?\n\|-+\|.*?\n',
            re.DOTALL
        )
        match = section_pattern.search(content)

        if not match:
            print(f"{YELLOW}Could not find P{priority_num} section in MASTER_LOG{RESET}")
            return

        # Create task row
        task_row = (
            f"| {task['id']} | {task['description']} | {task['owner']} | "
            f"PENDING | {task['effort']} | - | {task['notes']} |\n"
        )

        # Insert task row
        insert_pos = match.end()
        new_content = content[:insert_pos] + task_row + content[insert_pos:]

        # Update totals (simplified - just increment)
        total_match = re.search(r'Total Tasks:\s*(\d+)', new_content)
        if total_match:
            current_total = int(total_match.group(1))
            new_content = new_content.replace(
                f'Total Tasks: {current_total}',
                f'Total Tasks: {current_total + 1}',
                1
            )

        self.master_log_path.write_text(new_content)

    def _move_to_processed(self, file_path: Path):
        """Move processed file to processed/ subdirectory."""
        dest_path = self.processed_path / file_path.name
        file_path.rename(dest_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process TODO inbox files')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--priority',
        choices=['P0', 'P1', 'P2', 'P3'],
        help='Override priority for all tasks'
    )

    args = parser.parse_args()

    processor = InboxProcessor(dry_run=args.dry_run)
    processor.process_all(override_priority=args.priority)


if __name__ == "__main__":
    main()
