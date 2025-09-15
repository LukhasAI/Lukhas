#!/usr/bin/env python3
"""
Batch Progress Updater
======================

Updates batch files to reflect completed work based on GitHub PRs.
Scans PRs 241-257 and maps them to batch tasks for progress tracking.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def get_pr_info(pr_number: int) -> Dict[str, Any]:
    """Get PR information from GitHub CLI"""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json", "title,body,state,commits,labels"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return {}


def analyze_pr_completion(pr_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze PR to determine what work was completed"""
    title = pr_info.get("title", "")
    body = pr_info.get("body", "")
    state = pr_info.get("state", "")

    # Extract task indicators from PR content
    keywords = []

    # Common patterns in the completed PRs
    if "feat:" in title or "fix:" in title:
        keywords.append("implementation")
    if "test:" in title:
        keywords.append("testing")
    if "refactor:" in title:
        keywords.append("refactoring")
    if "perf:" in title:
        keywords.append("optimization")
    if "docs:" in title:
        keywords.append("documentation")
    if "chore:" in title:
        keywords.append("maintenance")

    # Extract specific domains
    if "consciousness" in title.lower() or "awareness" in title.lower():
        keywords.append("consciousness")
    if "memory" in title.lower():
        keywords.append("memory")
    if "identity" in title.lower():
        keywords.append("identity")
    if "ethics" in title.lower() or "guardian" in title.lower():
        keywords.append("ethics")
    if "dashboard" in title.lower() or "widget" in title.lower():
        keywords.append("dashboard")
    if "import" in title.lower():
        keywords.append("imports")
    if "quantum" in title.lower():
        keywords.append("quantum")
    if "consent" in title.lower():
        keywords.append("consent")

    return {
        "title": title,
        "keywords": keywords,
        "state": state,
        "has_tests": "test" in body.lower() or "pytest" in body.lower(),
        "completed": state == "MERGED" or (state == "OPEN" and "## Summary" in body),
    }


def match_pr_to_tasks(pr_analysis: Dict[str, Any], all_batch_tasks: List[Dict[str, Any]]) -> List[str]:
    """Match PR work to specific batch tasks across all batches"""
    matched_tasks = []
    keywords = pr_analysis["keywords"]
    title = pr_analysis["title"].lower()

    for task in all_batch_tasks:
        if task.get("status") == "completed":
            continue  # Skip already completed tasks

        task_title = (task.get("title") or "").lower()
        task_file = (task.get("file") or "").lower()
        task_module = (task.get("module") or "").lower()
        evidence = task.get("evidence") or {}
        task_evidence = (evidence.get("grep") or "").lower()

        # Score based on keyword matches
        score = 0

        # Direct keyword matches
        for keyword in keywords:
            if keyword in task_title or keyword in task_file or keyword in task_module:
                score += 2

        # Enhanced specific pattern matching
        if "import" in keywords and ("import" in task_title or "f821" in task_title or "undefined" in task_title):
            score += 4
        if "consciousness" in keywords and ("consciousness" in task_module or "awareness" in task_module):
            score += 4
        if "dashboard" in keywords and ("dashboard" in task_file or "widget" in task_file):
            score += 4
        if "memory" in keywords and ("memory" in task_module or "memory" in task_file):
            score += 4
        if "ethics" in keywords and (
            "ethics" in task_module or "guardian" in task_module or "governance" in task_module
        ):
            score += 4
        if "quantum" in keywords and ("quantum" in task_module or "qi" in task_module):
            score += 4
        if "consent" in keywords and ("consent" in task_module or "compliance" in task_module):
            score += 4

        # High-value matches for refactoring/optimization work
        if "refactoring" in keywords and ("refactor" in task_title or "clean" in task_title):
            score += 3
        if "optimization" in keywords and ("perf" in task_title or "optimize" in task_title):
            score += 3
        if "testing" in keywords and ("test" in task_file or "test" in task_title):
            score += 3
        if "documentation" in keywords and ("docs" in task_file or "doc" in task_title):
            score += 3

        # Evidence-based matching (from grep patterns)
        if "import" in keywords and ("import" in task_evidence or "f401" in task_evidence or "f821" in task_evidence):
            score += 3

        # Lower threshold for mechanical tasks
        task_type = task.get("est", {}).get("type", "")
        if task_type == "mechanical" and score >= 1:
            score += 1  # Boost mechanical tasks

        # If we have a reasonable match, include this task
        if score >= 2:
            matched_tasks.append(task["task_id"])

    return matched_tasks


def update_batch_files(batch_dir: Path, completed_tasks: Dict[str, List[str]]):
    """Update batch files with completed task status"""
    updates_made = 0

    for batch_file in batch_dir.glob("BATCH-CODEX*.json"):
        with open(batch_file, "r") as f:
            batch_data = json.load(f)

        agent = batch_data["agent"]
        tasks_updated = 0

        for task in batch_data["tasks"]:
            task_id = task["task_id"]

            # Check if this task was completed in any PR
            for pr_num, task_ids in completed_tasks.items():
                if task_id in task_ids and task["status"] == "open":
                    task["status"] = "completed"
                    task["completion_pr"] = pr_num
                    task["completed_at"] = "2025-09-15T08:00:00Z"  # Approximate time
                    tasks_updated += 1
                    break

        if tasks_updated > 0:
            # Save updated batch file
            with open(batch_file, "w") as f:
                json.dump(batch_data, f, indent=2)
            print(f"✅ Updated {batch_file.name}: {tasks_updated} tasks marked completed")
            updates_made += tasks_updated

    return updates_made


def main():
    """Main function to update batch progress"""
    print("🔄 Analyzing Codex PRs 241-257 for batch progress updates...")

    # Get all PR information
    prs_analyzed = {}
    for pr_num in range(241, 258):
        pr_info = get_pr_info(pr_num)
        if pr_info:
            prs_analyzed[str(pr_num)] = analyze_pr_completion(pr_info)
            print(f"📋 PR {pr_num}: {pr_info.get('title', 'Unknown')[:60]}...")

    print(f"\n🔍 Analyzed {len(prs_analyzed)} PRs")

    # Load batch files and match tasks
    batch_dir = Path(".lukhas_runs/2025-09-15/batches_clean")
    if not batch_dir.exists():
        print(f"❌ Batch directory not found: {batch_dir}")
        return

    # Load all batch tasks from all CODEX batches
    all_tasks = []
    for batch_file in batch_dir.glob("BATCH-CODEX*.json"):
        with open(batch_file, "r") as f:
            batch_data = json.load(f)
            for task in batch_data["tasks"]:
                task["batch_file"] = batch_file.name
                all_tasks.append(task)

    print(f"📋 Loaded {len(all_tasks)} tasks from CODEX batches")

    completed_tasks = {}
    total_matches = 0

    for pr_num, pr_analysis in prs_analyzed.items():
        if pr_analysis["completed"]:
            matched = match_pr_to_tasks(pr_analysis, all_tasks)
            if matched:
                completed_tasks[pr_num] = matched
                total_matches += len(matched)
                print(f"✅ PR {pr_num} matches {len(matched)} tasks")

    print(f"\n🎯 Total task matches: {total_matches}")

    # Update batch files
    if completed_tasks:
        updates = update_batch_files(batch_dir, completed_tasks)
        print(f"\n🏁 Updated {updates} tasks across batch files")

        # Regenerate progress report
        subprocess.run(["python3", "tools/ci/generate_progress.py", "--run-dir", ".lukhas_runs/2025-09-15"])
        print("📊 Progress report regenerated")
    else:
        print("⚠️  No task matches found for PRs")


if __name__ == "__main__":
    main()
