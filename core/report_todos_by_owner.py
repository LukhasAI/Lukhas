#!/usr/bin/env python3
"""
Finds all TODO comments in the codebase and generates a report grouped by file
and the owner specified in the nearest lukhas_context.md file.

Usage:
    python scripts/report_todos_by_owner.py > docs/audits/todo_report.md
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from functools import lru_cache


def parse_frontmatter(content: str) -> dict:
    """Parses YAML frontmatter from a markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}


@lru_cache(maxsize=128)
def find_owner(start_path: Path, repo_root: Path) -> str:
    """
    Finds the owner from the nearest lukhas_context.md file by searching
    upwards from the start_path.
    """
    current_dir = start_path.parent
    while current_dir != repo_root.parent and current_dir.is_dir():
        context_file = current_dir / "lukhas_context.md"
        if context_file.exists():
            content = context_file.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(content)
            if "owner" in frontmatter and frontmatter["owner"]:
                return str(frontmatter["owner"])
        if current_dir == repo_root:
            break
        current_dir = current_dir.parent
    return "N/A"


def find_todos(repo_root: Path) -> dict:
    """Finds all TODOs and groups them by owner and file."""
    todos_by_owner = defaultdict(lambda: defaultdict(list))
    
    # Regex to find TODO comments, case-insensitive
    todo_regex = re.compile(r".*TODO:(.*)", re.IGNORECASE)

    # Define files/dirs to ignore
    exclude_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"}
    exclude_extensions = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".ico"}

    for current_path, dirs, files in os.walk(repo_root):
        # Modify dirs in-place to prune traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in files:
            file_path = Path(current_path) / filename
            if file_path.suffix in exclude_extensions:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_todos = []
                    for i, line in enumerate(f, 1):
                        match = todo_regex.match(line)
                        if match:
                            file_todos.append({
                                "line": i,
                                "text": match.group(1).strip()
                            })
                
                if file_todos:
                    owner = find_owner(file_path, repo_root)
                    relative_path = file_path.relative_to(repo_root)
                    todos_by_owner[owner][str(relative_path)] = file_todos

            except Exception:
                # Ignore files that can't be read (e.g., binary files)
                continue

    return todos_by_owner


def main():
    """Main function to generate the TODO report."""
    repo_root = Path(__file__).parent.parent
    all_todos = find_todos(repo_root)

    print("# TODO Report by Owner")
    print("\nThis report lists all `TODO:` comments found in the codebase, grouped by the owner defined in the nearest `lukhas_context.md` file.")

    total_todos = 0
    sorted_owners = sorted(all_todos.keys())

    for owner in sorted_owners:
        owner_todos = all_todos[owner]
        owner_total = sum(len(items) for items in owner_todos.values())
        total_todos += owner_total
        print(f"\n## Owner: {owner} ({owner_total} TODOs)")
        
        sorted_files = sorted(owner_todos.keys())
        for file_path in sorted_files:
            todos = owner_todos[file_path]
            print(f"\n### `{file_path}` ({len(todos)} TODOs)")
            print("```")
            for todo in todos:
                print(f"L{todo['line']}: {todo['text']}")
            print("```")

    print("\n---\n")
    print(f"**Summary: Found {total_todos} TODOs across {len(sorted_owners)} owners.**")


if __name__ == "__main__":
    main()