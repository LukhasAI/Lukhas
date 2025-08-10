#!/usr/bin/env python3
"""
LUKHAS AI Task Tracker - Simple CLI tool for managing master task list
Helps update task status, add new tasks, and generate progress reports.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict


class TaskTracker:
    """Simple task management for MASTER_TASK_TRACKER.md"""

    def __init__(self, tracker_file: str = "MASTER_TASK_TRACKER.md"):
        self.tracker_file = Path(tracker_file)
        self.tasks = {}

    def load_tasks(self) -> Dict:
        """Parse tasks from markdown file"""
        if not self.tracker_file.exists():
            return {}

        content = self.tracker_file.read_text()
        tasks = {}

        # Find all task items: - [ ] or - [x]
        task_pattern = r"^- \[([ x])\] \*\*(.*?)\*\* - (.*?)$"

        for match in re.finditer(task_pattern, content, re.MULTILINE):
            completed = match.group(1) == "x"
            title = match.group(2).strip()
            description = match.group(3).strip()

            task_id = self._generate_task_id(title)
            tasks[task_id] = {
                "title": title,
                "description": description,
                "completed": completed,
                "line_text": match.group(0),
            }

        return tasks

    def _generate_task_id(self, title: str) -> str:
        """Generate consistent task ID from title"""
        return re.sub(r"[^a-zA-Z0-9]", "_", title.lower())[:50]

    def mark_complete(self, task_id: str) -> bool:
        """Mark a task as complete"""
        tasks = self.load_tasks()
        if task_id not in tasks:
            print(f"Task '{task_id}' not found")
            return False

        # Update the markdown file
        content = self.tracker_file.read_text()
        old_line = tasks[task_id]["line_text"]
        new_line = old_line.replace("- [ ]", "- [x]")

        updated_content = content.replace(old_line, new_line)
        self.tracker_file.write_text(updated_content)

        print(f"✅ Marked complete: {tasks[task_id]['title']}")
        return True

    def add_task(
        self,
        title: str,
        description: str,
        section: str = "IMMEDIATE HIGH-PRIORITY TASKS",
    ) -> bool:
        """Add a new task to the tracker"""
        content = self.tracker_file.read_text()

        # Find the section to add to
        section_pattern = f"## 🔥 \\*\\*{section}\\*\\*"
        if section not in content:
            print(f"Section '{section}' not found")
            return False

        # Add new task after the section header
        new_task = f"- [ ] **{title}** - {description}\n  - **Status**: Not started\n  - **Priority**: High\n"

        # Insert after first occurrence of bullet points in the section
        lines = content.split("\n")
        insert_index = -1

        for i, line in enumerate(lines):
            if section_pattern in line:
                # Find first bullet point after this section
                for j in range(i, len(lines)):
                    if lines[j].strip().startswith("- [ ]") or lines[
                        j
                    ].strip().startswith("- [x]"):
                        insert_index = j
                        break
                break

        if insert_index > -1:
            lines.insert(insert_index, new_task.strip())
            updated_content = "\n".join(lines)
            self.tracker_file.write_text(updated_content)
            print(f"✅ Added task: {title}")
            return True

        print(f"Could not find insertion point in section '{section}'")
        return False

    def list_tasks(self, show_completed: bool = False) -> None:
        """List all tasks with their status"""
        tasks = self.load_tasks()

        if not tasks:
            print("No tasks found")
            return

        print(f"\n📋 **Task Summary** ({len(tasks)} total tasks)")
        print("=" * 50)

        completed_count = sum(1 for t in tasks.values() if t["completed"])
        pending_count = len(tasks) - completed_count

        print(f"✅ Completed: {completed_count}")
        print(f"⏳ Pending: {pending_count}")
        print(f"📊 Progress: {(completed_count/len(tasks)*100):.1f}%")
        print()

        for task_id, task in tasks.items():
            if not show_completed and task["completed"]:
                continue

            status = "✅" if task["completed"] else "⏳"
            print(f"{status} {task['title']}")
            print(f"   {task['description']}")
            print(f"   ID: {task_id}")
            print()

    def generate_progress_report(self) -> str:
        """Generate a progress report"""
        tasks = self.load_tasks()

        if not tasks:
            return "No tasks to report on."

        completed_count = sum(1 for t in tasks.values() if t["completed"])
        total_count = len(tasks)
        progress_pct = (completed_count / total_count * 100) if total_count > 0 else 0

        report = f"""
# 📊 Task Progress Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tasks**: {total_count}
- **Completed**: {completed_count}
- **Pending**: {total_count - completed_count}
- **Progress**: {progress_pct:.1f}%

## Recent Completions
"""

        completed_tasks = [t for t in tasks.values() if t["completed"]]
        for task in completed_tasks[-5:]:  # Last 5 completed
            report += f"- ✅ {task['title']}\n"

        report += "\n## Next Priority Tasks\n"
        pending_tasks = [t for t in tasks.values() if not t["completed"]]
        for task in pending_tasks[:10]:  # Next 10 pending
            report += f"- ⏳ {task['title']}\n"

        return report


def main():
    """CLI interface for task tracker"""
    import sys

    tracker = TaskTracker()

    if len(sys.argv) < 2:
        print("Usage: python task_tracker.py [list|complete|add|report]")
        return

    command = sys.argv[1]

    if command == "list":
        show_completed = "--all" in sys.argv
        tracker.list_tasks(show_completed=show_completed)

    elif command == "complete":
        if len(sys.argv) < 3:
            print("Usage: python task_tracker.py complete <task_id>")
            return
        task_id = sys.argv[2]
        tracker.mark_complete(task_id)

    elif command == "add":
        if len(sys.argv) < 4:
            print("Usage: python task_tracker.py add '<title>' '<description>'")
            return
        title = sys.argv[2]
        description = sys.argv[3]
        tracker.add_task(title, description)

    elif command == "report":
        report = tracker.generate_progress_report()
        print(report)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, complete, add, report")


if __name__ == "__main__":
    main()
    main()
