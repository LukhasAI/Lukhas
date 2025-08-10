#!/usr/bin/env python3
"""
Task Migration Tool - Consolidate scattered TODOs into MASTER_TASK_TRACKER.md

This script helps migrate tasks from various TODO files into the unified tracker,
marking what's been consolidated to avoid duplication.
"""

import re
from pathlib import Path
from typing import List, Tuple


def extract_tasks_from_reality_todo() -> List[Tuple[str, str, str]]:
    """Extract pending tasks from REALITY_TODO.md"""
    file_path = Path("docs/reports/REALITY_TODO.md")
    if not file_path.exists():
        return []

    content = file_path.read_text()
    tasks = []

    # Look for TODO sections that aren't marked as completed
    todo_pattern = (
        r"## TODO (\d+)\n\n- 🔮 Original Thought: `(.+?)`\n- ✅ Task: (.+?)\n"
    )

    for match in re.finditer(todo_pattern, content, re.DOTALL):
        todo_num = match.group(1)
        thought = match.group(2)
        task_desc = match.group(3)

        # Check if this section shows completion
        section_end = content.find(f"## TODO {int(todo_num) + 1}", match.end())
        if section_end == -1:
            section_end = len(content)

        section_content = content[match.start() : section_end]

        # Skip if marked as completed/implemented
        if any(
            marker in section_content.lower()
            for marker in ["✅ fully implemented", "production ready", "completed"]
        ):
            continue

        tasks.append((todo_num, thought, task_desc))

    return tasks


def extract_tasks_from_dev_checklist() -> List[Tuple[str, str]]:
    """Extract pending tasks from DEVELOPMENT_CHECKLIST.md"""
    file_path = Path("DEVELOPMENT_CHECKLIST.md")
    if not file_path.exists():
        return []

    content = file_path.read_text()
    tasks = []

    # Find unchecked tasks
    task_pattern = r"- \[ \] \*\*(.*?)\*\* - (.*?)(?=\n|$)"

    for match in re.finditer(task_pattern, content):
        title = match.group(1).strip()
        description = match.group(2).strip()
        tasks.append((title, description))

    return tasks


def extract_tasks_from_ethics_todo() -> List[Tuple[str, str]]:
    """Extract pending tasks from ethics/TODO.md"""
    file_path = Path("ethics/TODO.md")
    if not file_path.exists():
        return []

    content = file_path.read_text()
    tasks = []

    # Find unchecked tasks
    task_pattern = r"- \[ \] (.*?)(?=\n|$)"

    for match in re.finditer(task_pattern, content):
        task_desc = match.group(1).strip()
        # Create title from first few words
        title = " ".join(task_desc.split()[:4])
        tasks.append((title, task_desc))

    return tasks


def extract_code_todos() -> List[Tuple[str, str, str]]:
    """Extract TODO comments from code files"""
    todos = []

    for py_file in Path(".").rglob("*.py"):
        try:
            content = py_file.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if "# TODO" in line.upper() or "# FIXME" in line.upper():
                    todo_text = line.strip()
                    # Remove comment prefix and clean up
                    todo_text = re.sub(
                        r"^#\s*(TODO|FIXME):?\s*", "", todo_text, flags=re.IGNORECASE
                    )

                    title = " ".join(todo_text.split()[:5])
                    location = f"{py_file}:{i+1}"

                    todos.append((title, todo_text, location))
        except:
            # Skip files that can't be read
            continue

    return todos


def generate_migration_summary():
    """Generate a summary of tasks to be migrated"""
    print("🔍 **Task Migration Analysis**")
    print("=" * 50)

    # Extract from various sources
    reality_tasks = extract_tasks_from_reality_todo()
    dev_tasks = extract_tasks_from_dev_checklist()
    ethics_tasks = extract_tasks_from_ethics_todo()
    code_todos = extract_code_todos()

    print("\n📊 **Sources Found:**")
    print(f"- REALITY_TODO.md: {len(reality_tasks)} pending tasks")
    print(f"- DEVELOPMENT_CHECKLIST.md: {len(dev_tasks)} tasks")
    print(f"- ethics/TODO.md: {len(ethics_tasks)} tasks")
    print(f"- Code TODOs: {len(code_todos)} comments")

    total_tasks = (
        len(reality_tasks) + len(dev_tasks) + len(ethics_tasks) + len(code_todos)
    )
    print(f"\n🎯 **Total Tasks to Consolidate**: {total_tasks}")

    print("\n📋 **High-Priority Code TODOs:**")
    priority_keywords = ["auth", "security", "performance", "integration", "tier"]

    priority_todos = [
        todo
        for todo in code_todos
        if any(keyword in todo[1].lower() for keyword in priority_keywords)
    ]

    for title, desc, location in priority_todos[:10]:
        print(f"- {title}")
        print(f"  📍 {location}")
        print(f"  📝 {desc}")
        print()

    print("\n✅ **Migration Status:**")
    print("- ✅ MASTER_TASK_TRACKER.md created")
    print("- ⏳ Task migration needed")
    print("- ⏳ Source file consolidation pending")

    return {
        "reality_tasks": reality_tasks,
        "dev_tasks": dev_tasks,
        "ethics_tasks": ethics_tasks,
        "code_todos": code_todos,
        "total": total_tasks,
    }


def create_archive_marker(file_path: str):
    """Create a marker file indicating this TODO source has been consolidated"""
    marker_content = f"""# 🏗️ CONSOLIDATED

This TODO file has been consolidated into MASTER_TASK_TRACKER.md as of {Path().absolute()}/MASTER_TASK_TRACKER.md

**Date Consolidated**: {Path().ctime()}
**Status**: ✅ Migrated to unified task tracker

## Original File Preserved
The original content is preserved below for reference, but all active task
tracking should now use MASTER_TASK_TRACKER.md

---

"""

    original_file = Path(file_path)
    if original_file.exists():
        original_content = original_file.read_text()
        consolidated_content = marker_content + original_content

        # Create backup
        backup_file = original_file.with_suffix(original_file.suffix + ".backup")
        backup_file.write_text(original_content)

        # Update original with consolidated marker
        original_file.write_text(consolidated_content)

        print(f"✅ Marked {file_path} as consolidated (backup created)")


def main():
    """Run task migration analysis"""
    print("🎯 **LUKHAS AI Task Consolidation Tool**")
    print("Analyzing scattered TODO files for migration to MASTER_TASK_TRACKER.md")
    print()

    # Check if master tracker exists
    master_tracker = Path("MASTER_TASK_TRACKER.md")
    if not master_tracker.exists():
        print("❌ MASTER_TASK_TRACKER.md not found!")
        print("Please create the master tracker first.")
        return

    print("✅ MASTER_TASK_TRACKER.md found")
    print()

    # Analyze tasks
    summary = generate_migration_summary()

    print("\n🎯 **Next Steps:**")
    print("1. Review the analysis above")
    print("2. Manually migrate high-priority tasks to MASTER_TASK_TRACKER.md")
    print("3. Run this script with --consolidate to mark source files")
    print("4. Use tools/task_tracker.py for ongoing task management")

    # Optionally mark files as consolidated
    import sys

    if "--consolidate" in sys.argv:
        print("\n🏗️ **Marking source files as consolidated...**")
        create_archive_marker("docs/reports/REALITY_TODO.md")
        create_archive_marker("DEVELOPMENT_CHECKLIST.md")
        create_archive_marker("ethics/TODO.md")
        print("✅ Source files marked as consolidated")


if __name__ == "__main__":
    main()
    main()
