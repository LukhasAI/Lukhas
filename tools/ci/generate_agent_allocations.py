#!/usr/bin/env python3
"""
Generate complete agent allocation JSON files based on PLANNING_TODO.md Section 10
Direct allocation of all TODOs from manifest_clean.json to specific agents
"""

import json
from datetime import datetime
from pathlib import Path


def load_manifest(manifest_path: str):
    """Load the TODO manifest"""
    with open(manifest_path) as f:
        return json.load(f)


def categorize_todos(manifest):
    """Categorize TODOs by priority and characteristics"""
    todos_by_priority = {}
    for todo in manifest["todos"]:
        if todo.get("status") != "open":
            continue
        priority = todo.get("priority", "unknown")
        if priority not in todos_by_priority:
            todos_by_priority[priority] = []
        todos_by_priority[priority].append(todo)
    return todos_by_priority


def filter_todos_by_keywords(todos, keywords):
    """Filter TODOs by keywords in title, file, module"""
    filtered = []
    for todo in todos:
        todo_text = (todo.get("title", "") + " " + todo.get("file", "") + " " + todo.get("module", "")).lower()
        if any(keyword in todo_text for keyword in keywords):
            filtered.append(todo)
    return filtered


def filter_todos_by_type(todos, target_types):
    """Filter TODOs by estimation type (mechanical, logic, integration)"""
    filtered = []
    for todo in todos:
        todo_type = todo.get("est", {}).get("type", "logic")
        if todo_type in target_types:
            filtered.append(todo)
    return filtered


def create_agent_spec(
    agent_id, specialty, focus, priority, task_count, keywords=None, todo_types=None, risk_level="med", flagged=False
):
    """Create base agent specification"""
    return {
        "agent_id": agent_id,
        "specialty": specialty,
        "focus": focus,
        "task_count": task_count,
        "priority": priority,
        "risk_level": risk_level,
        "flagged": flagged,
        "branch_prefix": f"feat/{agent_id.lower()}/{specialty.lower().replace(' ', '-').replace('/', '-')}-batch",
        "filter_keywords": keywords or [],
        "filter_types": todo_types or [],
        "created_at": datetime.now().isoformat() + "Z",
    }


def generate_all_allocations(manifest_path: str, output_dir: str):
    """Generate all agent allocation files"""
    manifest = load_manifest(manifest_path)
    todos_by_priority = categorize_todos(manifest)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Available TODOs:")
    for priority, todos in todos_by_priority.items():
        print(f"  {priority}: {len(todos)}")

    # Agent specifications from PLANNING_TODO.md Section 10
    agent_specs = [
        # Jules agents (critical/high focus)
        create_agent_spec(
            "JULES-01",
            "Identity Core",
            "ΛTRACE persistence, audit chain linking",
            "critical",
            30,
            ["identity", "trace", "persistence", "audit", "lambd", "tier"],
            ["logic", "integration"],
            "high",
        ),
        create_agent_spec(
            "JULES-02",
            "Consent/Scopes",
            "tier boundaries, validation, history → ΛTRACE",
            "critical",
            30,
            ["consent", "scope", "tier", "boundary", "validation", "governance"],
            ["logic", "integration"],
            "high",
        ),
        create_agent_spec(
            "JULES-03",
            "SSO/Biometrics",
            "symbolic challenge, authentication flows",
            "critical",
            25,
            ["sso", "biometric", "auth", "challenge", "symbolic", "webauthn"],
            ["logic", "integration"],
            "high",
            True,
        ),
        create_agent_spec(
            "JULES-04",
            "Awareness Protocol",
            "reconciliation with ΛTIER system",
            "critical",
            25,
            ["awareness", "protocol", "consciousness", "tier", "reconcile"],
            ["logic"],
            "high",
        ),
        create_agent_spec(
            "JULES-05",
            "Guardian Ethics",
            "advanced intent + governance forwarding",
            "critical",
            25,
            ["guardian", "ethics", "intent", "governance", "safety"],
            ["logic"],
            "high",
        ),
        create_agent_spec(
            "JULES-06",
            "QRG Generator",
            "session replay scaffolding",
            "high",
            25,
            ["qrg", "generator", "session", "replay", "scaffold"],
            ["logic"],
            "med",
            True,
        ),
        create_agent_spec(
            "JULES-07",
            "Wallet/QI Bridges",
            "init placeholders, interfaces",
            "high",
            25,
            ["wallet", "qi", "bridge", "interface", "quantum"],
            ["logic"],
            "med",
            True,
        ),
        create_agent_spec(
            "JULES-08",
            "Quantum Entropy",
            "stubs + interfaces (no prod)",
            "high",
            25,
            ["quantum", "entropy", "stub", "interface"],
            ["logic"],
            "med",
            True,
        ),
        create_agent_spec(
            "JULES-09",
            "Dashboards",
            "compliance/guardian data wiring",
            "high",
            30,
            ["dashboard", "streamlit", "visualization", "compliance", "monitor"],
            ["logic"],
            "med",
        ),
        create_agent_spec(
            "JULES-10",
            "Tests/Integration",
            "integration identity imports + e2e glue",
            "high",
            30,
            ["test", "integration", "e2e", "import"],
            ["logic"],
            "med",
        ),
        # Codex agents (mechanical/med/low focus)
        create_agent_spec(
            "CODEX-01",
            "F821 Fixes",
            "undefined names and import errors",
            "mixed",
            40,
            ["f821", "undefined", "import"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-02",
            "Import Cleanup",
            "import organization and cleanup",
            "mixed",
            40,
            ["import", "cleanup"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-03",
            "Docstring Fixes",
            "docstring enforcement and formatting",
            "mixed",
            40,
            ["docstring", "documentation"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-04",
            "Rename Operations",
            "variable and function renaming",
            "mixed",
            40,
            ["rename", "variable", "refactor"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-05",
            "Lint Compliance",
            "lint error fixes and compliance",
            "mixed",
            40,
            ["lint", "compliance", "format"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-06",
            "Code Cleanup",
            "general code cleanup and organization",
            "mixed",
            40,
            ["cleanup", "organize", "structure"],
            ["mechanical"],
            "low",
        ),
        create_agent_spec(
            "CODEX-07",
            "Dashboard Widgets",
            "streamlit widget generation",
            "med",
            30,
            ["widget", "streamlit", "dashboard"],
            ["mechanical", "logic"],
            "low",
        ),
        create_agent_spec(
            "CODEX-08",
            "Template Systems",
            "template wiring and generation",
            "med",
            30,
            ["template", "generate", "stub"],
            ["mechanical", "logic"],
            "low",
        ),
        create_agent_spec(
            "CODEX-09",
            "Performance Tweaks",
            "micro-optimizations and performance",
            "med",
            30,
            ["performance", "optimize", "speed"],
            ["mechanical", "logic"],
            "low",
        ),
        create_agent_spec(
            "CODEX-10",
            "Stub Factories",
            "stub creation and factory patterns",
            "low",
            30,
            ["stub", "factory", "placeholder"],
            ["mechanical"],
            "low",
        ),
    ]

    allocated_todos = set()

    for spec in agent_specs:
        agent_file = output_path / f"{spec['agent_id']}.json"

        # Get TODOs for this agent
        if spec["priority"] == "mixed":
            # For CODEX agents, mix priorities based on type
            candidate_todos = []
            if spec["filter_types"] and "mechanical" in spec["filter_types"]:
                # Mechanical tasks from all priorities
                for priority in ["critical", "high", "med", "low"]:
                    if priority in todos_by_priority:
                        candidate_todos.extend(todos_by_priority[priority])
            else:
                # Take from med and low first for mixed
                candidate_todos = todos_by_priority.get("med", []) + todos_by_priority.get("low", [])
        else:
            candidate_todos = todos_by_priority.get(spec["priority"], [])

        # Filter by keywords if specified
        if spec["filter_keywords"]:
            filtered_todos = filter_todos_by_keywords(candidate_todos, spec["filter_keywords"])
        else:
            filtered_todos = candidate_todos

        # Filter by type if specified
        if spec["filter_types"]:
            filtered_todos = filter_todos_by_type(filtered_todos, spec["filter_types"])

        # Remove already allocated TODOs
        available_todos = [t for t in filtered_todos if t["task_id"] not in allocated_todos]

        # Take the required number of TODOs
        agent_todos = available_todos[: spec["task_count"]]

        # Mark as allocated
        for todo in agent_todos:
            allocated_todos.add(todo["task_id"])

        # Create full agent JSON
        agent_json = {
            "agent_id": spec["agent_id"],
            "specialty": spec["specialty"],
            "focus": spec["focus"],
            "task_count": len(agent_todos),
            "target_count": spec["task_count"],
            "priority": spec["priority"],
            "risk_level": spec["risk_level"],
            "flagged": spec["flagged"],
            "branch_prefix": spec["branch_prefix"],
            "implementation_guidance": {
                "key_areas": [spec["focus"]],
                "lukhas_context": {
                    "constellation_framework": get_constellation_context(spec["specialty"]),
                    "verification_required": not spec["flagged"],
                },
                "verification_requirements": get_verification_requirements(spec["specialty"]),
            },
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
                    "focus_area": spec["specialty"],
                }
                for todo in agent_todos
            ],
            "usage_instructions": {
                "how_to_start": [
                    f"1. Create branch: {spec['branch_prefix']}01",
                    f"2. Work through {len(agent_todos)} tasks systematically",
                    "3. One TaskID per commit",
                    f"4. Focus on: {spec['focus']}",
                    "5. Run checks after each task completion",
                ],
                "commit_format": f"feat({spec['specialty'].lower().split()[0]}): {{description}} ({{task_id}})",
                "checks_to_run": ["ruff check .", "pytest -q"],
            },
            "created_at": spec["created_at"],
            "source": "PLANNING_TODO.md Section 10 + manifest_clean.json",
        }

        with open(agent_file, "w") as f:
            json.dump(agent_json, f, indent=2)

        print(f"✅ Created {spec['agent_id']}: {len(agent_todos)} tasks ({spec['specialty']})")

        if len(agent_todos) < spec["task_count"]:
            print(f"   ⚠️  Only found {len(agent_todos)}/{spec['task_count']} matching tasks")

    print(f"\n📊 Total allocated: {len(allocated_todos)} TODOs across {len(agent_specs)} agents")
    total_available = sum(len(todos) for todos in todos_by_priority.values())
    print(f"📊 Remaining: {total_available - len(allocated_todos)}/{total_available} TODOs")


def get_constellation_context(specialty):
    """Get Constellation Framework context for specialty"""
    if "identity" in specialty.lower() or "auth" in specialty.lower():
        return "Focus on Identity pillar (⚛️) integration"
    elif "consciousness" in specialty.lower() or "awareness" in specialty.lower():
        return "Focus on Consciousness pillar (🧠) integration"
    elif "guardian" in specialty.lower() or "ethics" in specialty.lower():
        return "Focus on Guardian pillar (🛡️) integration"
    else:
        return "Multi-pillar integration as needed"


def get_verification_requirements(specialty):
    """Get verification requirements for specialty"""
    base_requirements = ["Unit tests covering happy/failure paths", "Integration tests if cross-module"]

    if "identity" in specialty.lower():
        base_requirements.append("ΛTRACE integration verified")
    if "guardian" in specialty.lower():
        base_requirements.append("Safety boundaries validated")
    if "dashboard" in specialty.lower():
        base_requirements.append("UI components render without errors")

    return base_requirements


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate agent allocation JSON files")
    parser.add_argument("--manifest", required=True, help="Path to manifest_clean.json")
    parser.add_argument("--output", required=True, help="Output directory for agent JSON files")

    args = parser.parse_args()
    generate_all_allocations(args.manifest, args.output)
