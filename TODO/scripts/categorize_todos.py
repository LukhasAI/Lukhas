#!/usr/bin/env python3
"""
categorize_todos.py - Categorize LUKHAS TODOs by priority
Processes the extracted TODO list and sorts into CRITICAL/HIGH/MED/LOW
"""

import re
from collections import defaultdict
from pathlib import Path


def load_exclusions():
    """Load standardized exclusions and get clean TODO list"""
    import subprocess

    # Use our clean search to get accurate TODO list
    cmd = """
    cd /Users/agi_dev/LOCAL-REPOS/Lukhas
    source tools/search/standardized_exclusions.sh
    clean_grep "TODO" --include="*.py" -n
    """

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable="/bin/bash")
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def classify_priority(todo_line, file_path, context=""):
    """Classify TODO priority based on content and location"""
    todo_lower = todo_line.lower()
    file_lower = file_path.lower()

    # CRITICAL: Security, safety, blocking issues
    critical_keywords = [
        "security",
        "vulnerability",
        "critical",
        "urgent",
        "blocking",
        "corrupted",
        "failed",
        "broken",
        "error",
        "exception",
        "crash",
        "deadlock",
        "race condition",
        "data loss",
        "memory leak",
        "infinite loop",
        "guardian",
        "safety",
    ]

    critical_modules = [
        "security",
        "identity",
        "auth",
        "guardian",
        "consciousness/core",
        "api/auth",
        "crypto",
        "validation",
    ]

    # HIGH: Core functionality, Trinity Framework, agent coordination
    high_keywords = [
        "core",
        "important",
        "trinity",
        "consciousness",
        "identity",
        "memory",
        "integration",
        "api",
        "performance",
        "optimize",
        "agent",
        "coordinator",
        "essential",
        "required",
        "needed",
        "framework",
        "architecture",
    ]

    high_modules = [
        "core/",
        "api/",
        "consciousness/",
        "identity/",
        "memory/",
        "lukhas/",
        "orchestration/",
        "coordination",
    ]

    # MED: Features, enhancements, documentation
    med_keywords = [
        "enhance",
        "improve",
        "feature",
        "document",
        "refactor",
        "cleanup",
        "optimize",
        "better",
        "upgrade",
        "modernize",
        "extend",
    ]

    # LOW: Minor cleanup, style, nice-to-have
    low_keywords = [
        "style",
        "cosmetic",
        "minor",
        "cleanup",
        "format",
        "comment",
        "nice to have",
        "optional",
        "later",
        "future",
        "consider",
    ]

    # Check for T4 annotations (these are often important)
    if "t4-" in todo_lower or "[t4" in todo_lower:
        if any(kw in todo_lower for kw in critical_keywords):
            return "CRITICAL"
        elif "unused-import" in todo_lower or "document or remove" in todo_lower:
            return "MED"  # Import cleanup is medium priority
        else:
            return "HIGH"  # T4 framework items are generally high priority

    # Check for specialist assignments (agent coordination)
    if "specialist]" in todo_lower or "agent]" in todo_lower:
        return "HIGH"

    # Critical checks
    if any(kw in todo_lower for kw in critical_keywords):
        return "CRITICAL"

    if any(module in file_lower for module in critical_modules):
        return "CRITICAL"

    # High priority checks
    if any(kw in todo_lower for kw in high_keywords):
        return "HIGH"

    if any(module in file_lower for module in high_modules):
        return "HIGH"

    # Medium priority checks
    if any(kw in todo_lower for kw in med_keywords):
        return "MED"

    # Low priority checks
    if any(kw in todo_lower for kw in low_keywords):
        return "LOW"

    # Default based on module location
    if "candidate/" in file_lower:
        return "MED"  # Candidate modules are generally medium priority
    elif "tools/" in file_lower or "tests/" in file_lower:
        return "LOW"  # Tools and tests are generally lower priority
    elif "products/" in file_lower:
        return "HIGH"  # Products are user-facing, higher priority
    else:
        return "MED"  # Default to medium


def extract_todo_context(line):
    """Extract TODO text and context from grep line"""
    # Format: ./path/file.py:line_number:content
    parts = line.split(":", 2)
    if len(parts) < 3:
        return "", "", ""

    file_path = parts[0]
    line_num = parts[1]
    content = parts[2]

    # Extract just the TODO part
    todo_match = re.search(r"TODO[^:]*:?\s*(.+)", content, re.IGNORECASE)
    todo_text = todo_match.group(1).strip() if todo_match else content.strip()

    return file_path, line_num, todo_text


def categorize_todos():
    """Main function to categorize all TODOs"""
    print("🔍 Loading TODOs with clean search...")
    todo_lines = load_exclusions()

    if not todo_lines or (len(todo_lines) == 1 and not todo_lines[0]):
        print("❌ No TODOs found!")
        return

    print(f"📊 Processing {len(todo_lines)} TODO entries...")

    categories = {"CRITICAL": [], "HIGH": [], "MED": [], "LOW": []}

    for line in todo_lines:
        if not line.strip():
            continue

        file_path, line_num, todo_text = extract_todo_context(line)
        if not todo_text:
            continue

        priority = classify_priority(todo_text, file_path)

        categories[priority].append({"file": file_path, "line": line_num, "text": todo_text, "full_line": line})

    # Summary
    total = sum(len(todos) for todos in categories.values())
    print(f"\n📋 TODO Categorization Results:")
    print(f"  🚨 CRITICAL: {len(categories['CRITICAL'])}")
    print(f"  ⭐ HIGH: {len(categories['HIGH'])}")
    print(f"  📋 MED: {len(categories['MED'])}")
    print(f"  🔧 LOW: {len(categories['LOW'])}")
    print(f"  📊 TOTAL: {total}")

    return categories


def generate_priority_files(categories):
    """Generate markdown files for each priority level"""
    base_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas/TODO")

    priority_info = {
        "CRITICAL": {"emoji": "🚨", "description": "Security, consciousness safety, blocking issues"},
        "HIGH": {"emoji": "⭐", "description": "Core functionality, Trinity Framework, agent coordination"},
        "MED": {"emoji": "📋", "description": "Feature enhancements, optimization, documentation"},
        "LOW": {"emoji": "🔧", "description": "Cleanup, refactoring, nice-to-have features"},
    }

    for priority, todos in categories.items():
        if not todos:
            continue

        info = priority_info[priority]
        filename = f"{priority.lower()}_todos.md"
        filepath = base_path / priority / filename

        # Group by module for better organization
        by_module = defaultdict(list)
        for todo in todos:
            module = todo["file"].split("/")[1] if "/" in todo["file"] else "root"
            by_module[module].append(todo)

        with open(filepath, "w") as f:
            f.write(f"# {info['emoji']} {priority} Priority TODOs\n\n")
            f.write(f"**{info['description']}**\n\n")
            f.write(f"**Count**: {len(todos)} TODOs\n")
            f.write(f"**Last Updated**: September 12, 2025\n\n")

            f.write("## 📊 Summary by Module\n\n")
            for module in sorted(by_module.keys()):
                f.write(f"- **{module}**: {len(by_module[module])} TODOs\n")

            f.write("\n---\n\n")

            for module in sorted(by_module.keys()):
                module_todos = by_module[module]
                f.write(f"## 📁 {module.title()} Module ({len(module_todos)} TODOs)\n\n")

                for i, todo in enumerate(module_todos, 1):
                    f.write(f"### {i}. {todo['text'][:80]}{'...' if len(todo['text']) > 80 else ''}\n\n")
                    f.write(f"- **File**: `{todo['file']}:{todo['line']}`\n")
                    f.write(f"- **Priority**: {priority}\n")
                    f.write(f"- **Status**: Open\n")

                    # Determine Trinity aspect
                    text_lower = todo["text"].lower()
                    if any(word in text_lower for word in ["identity", "auth", "id"]):
                        f.write(f"- **Trinity Aspect**: ⚛️ Identity\n")
                    elif any(word in text_lower for word in ["consciousness", "memory", "cognitive"]):
                        f.write(f"- **Trinity Aspect**: 🧠 Consciousness\n")
                    elif any(word in text_lower for word in ["security", "guardian", "safety"]):
                        f.write(f"- **Trinity Aspect**: 🛡️ Guardian\n")

                    f.write(f"\n**TODO Text:**\n```\n{todo['text']}\n```\n\n")
                    f.write("---\n\n")

        print(f"✅ Generated {filepath}")


if __name__ == "__main__":
    print("🎯 LUKHAS TODO Categorization System")
    print("=" * 50)

    categories = categorize_todos()
    if categories:
        print("\n📝 Generating priority files...")
        generate_priority_files(categories)
        print("\n✅ TODO categorization complete!")
        print("📂 Check TODO/CRITICAL/, TODO/HIGH/, TODO/MED/, TODO/LOW/ directories")
    else:
        print("❌ No TODOs to categorize")
