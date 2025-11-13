#!/usr/bin/env python3
"""
Complete TODO Allocation - Simple Direct Assignment
Allocates ALL TODOs from manifest_clean.json to agents with no filtering
"""

import json
from datetime import datetime
from pathlib import Path


def load_and_allocate_all_todos(manifest_path: str, output_dir: str):
    """Load manifest and allocate ALL TODOs to agents"""

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Get all open TODOs sorted by priority
    open_todos = [todo for todo in manifest["todos"] if todo.get("status") == "open"]

    critical_todos = [t for t in open_todos if t.get("priority") == "critical"]
    high_todos = [t for t in open_todos if t.get("priority") == "high"]
    med_todos = [t for t in open_todos if t.get("priority") == "med"]
    low_todos = [t for t in open_todos if t.get("priority") == "low"]
    unknown_todos = [t for t in open_todos if t.get("priority") == "unknown"]

    print("Available TODOs:")
    print(f"  Critical: {len(critical_todos)}")
    print(f"  High: {len(high_todos)}")
    print(f"  Med: {len(med_todos)}")
    print(f"  Low: {len(low_todos)}")
    print(f"  Unknown: {len(unknown_todos)}")
    print(f"  Total: {len(open_todos)}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Simple allocation plan based on PLANNING_TODO.md
    allocations = [
        # JULES agents - critical and high priority
        (
            "JULES-01",
            "Identity Core",
            "ΛTRACE persistence, audit chain linking",
            critical_todos[0:30],
            "critical",
            "high",
        ),
        (
            "JULES-02",
            "Consent/Scopes",
            "tier boundaries, validation, history",
            critical_todos[30:60],
            "critical",
            "high",
        ),
        (
            "JULES-03",
            "SSO/Biometrics",
            "authentication flows, symbolic challenge",
            critical_todos[60:85],
            "critical",
            "high",
        ),
        ("JULES-04", "Awareness Protocol", "ΛTIER system reconciliation", critical_todos[85:110], "critical", "high"),
        ("JULES-05", "Guardian Ethics", "advanced intent + governance", critical_todos[110:135], "critical", "high"),
        ("JULES-06", "QRG Generator", "session replay scaffolding", high_todos[0:30], "high", "med"),
        ("JULES-07", "Wallet/QI Bridges", "interfaces and placeholders", high_todos[30:60], "high", "med"),
        ("JULES-08", "Quantum Entropy", "stubs + interfaces", high_todos[60:90], "high", "med"),
        ("JULES-09", "Dashboards", "compliance/guardian wiring", high_todos[90:120], "high", "med"),
        ("JULES-10", "Tests/Integration", "e2e glue and imports", high_todos[120:150], "high", "med"),
        # CODEX agents - remaining high, med, low
        ("CODEX-01", "High Priority Batch 1", "high priority mechanical fixes", high_todos[150:190], "high", "low"),
        ("CODEX-02", "High Priority Batch 2", "high priority logic tasks", high_todos[190:230], "high", "low"),
        ("CODEX-03", "High Priority Batch 3", "high priority integration", high_todos[230:270], "high", "low"),
        ("CODEX-04", "High Priority Batch 4", "high priority cleanup", high_todos[270:310], "high", "low"),
        ("CODEX-05", "High Priority Batch 5", "high priority remaining", high_todos[310:350], "high", "low"),
        ("CODEX-06", "High Priority Batch 6", "high priority final", high_todos[350:390], "high", "low"),
        ("CODEX-07", "Medium Priority Batch 1", "medium priority tasks", med_todos[0:40], "med", "low"),
        ("CODEX-08", "Medium Priority Batch 2", "medium priority tasks", med_todos[40:80], "med", "low"),
        ("CODEX-09", "Medium Priority Batch 3", "medium priority tasks", med_todos[80:120], "med", "low"),
        ("CODEX-10", "Low Priority Batch", "low priority cleanup", low_todos[0:40], "low", "low"),
    ]

    total_allocated = 0

    for agent_id, specialty, focus, todos, priority, risk in allocations:
        if not todos:  # Skip if no TODOs available for this slice
            continue

        agent_json = {
            "agent_id": agent_id,
            "specialty": specialty,
            "focus": focus,
            "task_count": len(todos),
            "priority": priority,
            "risk_level": risk,
            "branch_prefix": f"feat/{agent_id.lower()}/{specialty.lower().replace(' ', '-')}-batch",
            "tasks": [
                {
                    "task_id": todo["task_id"],
                    "priority": todo["priority"],
                    "title": todo["title"],
                    "file": todo["file"],
                    "module": todo["module"],
                    "constellation": todo["constellation"],
                    "line_hint": todo.get("line_hint"),
                    "risk": todo["risk"],
                    "type": todo["est"]["type"],
                    "size": todo["est"]["size"],
                    "evidence": todo.get("evidence", {}),
                }
                for todo in todos
            ],
            "usage_instructions": {
                "how_to_start": [
                    f"1. Create branch: {agent_id.lower()}-batch-$(date +%m%d)",
                    f"2. Work through {len(todos)} tasks systematically",
                    "3. One TaskID per commit",
                    f"4. Focus: {focus}",
                    "5. Run checks: ruff check . && pytest -q",
                ],
                "commit_format": f"feat({specialty.split()[0].lower()}): {{description}} ({{task_id}})",
            },
            "created_at": datetime.now().isoformat() + "Z",
            "source": "Direct allocation from manifest_clean.json",
        }

        agent_file = output_path / f"{agent_id}.json"
        with open(agent_file, "w") as f:
            json.dump(agent_json, f, indent=2)

        print(f"✅ {agent_id}: {len(todos)} tasks ({specialty})")
        total_allocated += len(todos)

    # Handle remaining TODOs
    all_allocated_ids = set()
    for _, _, _, todos, _, _ in allocations:
        for todo in todos:
            all_allocated_ids.add(todo["task_id"])

    remaining_todos = [t for t in open_todos if t["task_id"] not in all_allocated_ids]

    print(f"\n📊 Total allocated: {total_allocated} TODOs")
    print(f"📊 Remaining: {len(remaining_todos)} TODOs")

    if remaining_todos:
        # Create additional batches for remaining TODOs
        remaining_batches = []
        batch_size = 40
        for i in range(0, len(remaining_todos), batch_size):
            batch_todos = remaining_todos[i : i + batch_size]
            batch_num = i // batch_size + 1
            remaining_batches.append(
                (
                    f"REMAINING-{batch_num:02d}",
                    f"Remaining Batch {batch_num}",
                    "unallocated TODOs",
                    batch_todos,
                    "mixed",
                    "low",
                )
            )

        print(f"📋 Created {len(remaining_batches)} additional batches for remaining TODOs")

        for agent_id, specialty, focus, todos, priority, risk in remaining_batches:
            agent_json = {
                "agent_id": agent_id,
                "specialty": specialty,
                "focus": focus,
                "task_count": len(todos),
                "priority": priority,
                "risk_level": risk,
                "branch_prefix": f"feat/{agent_id.lower()}/remaining-batch",
                "tasks": [
                    {
                        "task_id": todo["task_id"],
                        "priority": todo["priority"],
                        "title": todo["title"],
                        "file": todo["file"],
                        "module": todo["module"],
                        "constellation": todo["constellation"],
                        "line_hint": todo.get("line_hint"),
                        "risk": todo["risk"],
                        "type": todo["est"]["type"],
                        "size": todo["est"]["size"],
                        "evidence": todo.get("evidence", {}),
                    }
                    for todo in todos
                ],
                "usage_instructions": {
                    "how_to_start": [
                        f"1. Create branch: {agent_id.lower()}-$(date +%m%d)",
                        f"2. Work through {len(todos)} remaining tasks",
                        "3. One TaskID per commit",
                        "4. Mixed priority cleanup",
                        "5. Run checks: ruff check . && pytest -q",
                    ],
                    "commit_format": "feat(cleanup): {description} ({task_id})",
                },
                "created_at": datetime.now().isoformat() + "Z",
                "source": "Remaining unallocated TODOs",
            }

            agent_file = output_path / f"{agent_id}.json"
            with open(agent_file, "w") as f:
                json.dump(agent_json, f, indent=2)

            print(f"✅ {agent_id}: {len(todos)} remaining tasks")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Complete TODO allocation")
    parser.add_argument("--manifest", required=True, help="Path to manifest_clean.json")
    parser.add_argument("--output", required=True, help="Output directory")

    args = parser.parse_args()
    load_and_allocate_all_todos(args.manifest, args.output)
