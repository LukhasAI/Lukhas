#!/usr/bin/env python3
"""
Specialized Batch Creator for UNALLOCATED_TODO_GROUPS.md Implementation
Creates targeted agent batches for specific task groups based on domain expertise.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


class SpecializedBatchCreator:
    def __init__(self, manifest_file: str):
        """Initialize with manifest and identify unallocated task entries."""
        self.manifest = self._load_manifest(manifest_file)
        self.unallocated_todos = self._find_unallocated_todos()

        # Specialized agent definitions from UNALLOCATED_TODO_GROUPS.md
        self.agent_specs = {
            "jules11": {
                "domain": "CRITICAL-CORE-INFRASTRUCTURE",
                "focus": "Core system initialization, critical imports, undefined name fixes",
                "capabilities": ["F821", "imports", "core", "system", "initialization"],
                "batch_size": 35,
                "priority": ["critical"],
                "risk_level": "high",
            },
            "jules12": {
                "domain": "CRITICAL-CONSCIOUSNESS-CORE",
                "focus": "Consciousness system critical paths, AkaQualia core issues",
                "capabilities": ["consciousness", "akaqualia", "awareness", "memory", "states"],
                "batch_size": 35,
                "priority": ["critical"],
                "risk_level": "critical",
            },
            "jules13": {
                "domain": "CRITICAL-IDENTITY-AUTH",
                "focus": "Identity system, authentication, Lambda ID critical issues",
                "capabilities": ["identity", "auth", "lambda", "webauthn", "namespace"],
                "batch_size": 35,
                "priority": ["critical"],
                "risk_level": "critical",
            },
            "codex11": {
                "domain": "HIGH-API-INTEGRATION",
                "focus": "API implementations, service integrations, external connections",
                "capabilities": ["api", "integration", "service", "rest", "graphql"],
                "batch_size": 35,
                "priority": ["high"],
                "risk_level": "medium",
            },
            "codex12": {
                "domain": "MEDIUM-REFACTORING",
                "focus": "Code refactoring, structure improvements, maintainability",
                "capabilities": ["refactor", "structure", "cleanup", "maintainability"],
                "batch_size": 35,
                "priority": ["med"],
                "risk_level": "low",
            },
        }

    def _load_manifest(self, manifest_file: str) -> dict[str, Any]:
        """Load the task manifest."""
        with open(manifest_file) as f:
            return json.load(f)

    def _find_unallocated_todos(self) -> list[dict[str, Any]]:
        """Find tasks that aren't assigned to any existing batch."""
        # For now, return all open tasks as we're creating new specialized batches
        # In a real implementation, this would check against existing batch allocations
        return [todo for todo in self.manifest["todos"] if todo.get("status") == "open"]

    def _score_todo_for_agent(self, todo: dict[str, Any], agent_spec: dict[str, Any]) -> int:
        """Score how well a task matches an agent's capabilities."""
        score = 0
        todo_text = (todo.get("title", "") + " " + todo.get("file", "") + " " + todo.get("module", "")).lower()

        # Priority match (high weight)
        if todo.get("priority") in agent_spec["priority"]:
            score += 10

        # Capability keyword matching
        for capability in agent_spec["capabilities"]:
            if capability.lower() in todo_text:
                score += 5

        # Module/domain matching
        if agent_spec["domain"] == "CRITICAL-CORE-INFRASTRUCTURE":
            if any(keyword in todo_text for keyword in ["import", "f821", "undefined", "core", "init"]):
                score += 8
        elif agent_spec["domain"] == "CRITICAL-CONSCIOUSNESS-CORE":
            if any(keyword in todo_text for keyword in ["consciousness", "aka", "qualia", "memory", "dream"]):
                score += 8
        elif agent_spec["domain"] == "CRITICAL-IDENTITY-AUTH":
            if any(keyword in todo_text for keyword in ["identity", "auth", "lambda", "webauthn", "oauth"]):
                score += 8
        elif agent_spec["domain"] == "HIGH-API-INTEGRATION":
            if any(keyword in todo_text for keyword in ["api", "integration", "service", "adapter", "bridge"]):
                score += 6
        elif agent_spec['domain'] == 'MEDIUM-REFACTORING' and any(keyword in todo_text for keyword in ['refactor', 'cleanup', 'structure', 'organize']):
            score += 4

        return score

    def create_batch(self, agent_id: str, output_dir: str) -> Optional[dict[str, Any]]:
        """Create a specialized batch for the given agent"""
        if agent_id not in self.agent_specs:
            print(f"Unknown agent: {agent_id}")
            return None

        agent_spec = self.agent_specs[agent_id]

        # Score all unallocated tasks for this agent
        scored_todos = []
        for todo in self.unallocated_todos:
            score = self._score_todo_for_agent(todo, agent_spec)
            if score > 0:  # Only include tasks with some match
                scored_todos.append((score, todo))

        # Sort by score (descending) and take top batch_size
        scored_todos.sort(key=lambda x: x[0], reverse=True)
        selected_todos = [todo for score, todo in scored_todos[: agent_spec["batch_size"]]]

        if not selected_todos:
            print(f"No suitable tasks found for {agent_id}")
            return None

        # Create batch structure
        batch = {
            "batch_id": f"BATCH-{agent_id.upper()}-2025-09-15-01",
            "agent": agent_id,
            "created_at": datetime.now().isoformat() + "Z",
            "expires_at": (datetime.now() + timedelta(days=3)).isoformat() + "Z",
            "branch_name": f"feat/{agent_id}/{agent_spec['domain'].lower().replace('-', '_')}",
            "status": "ready",
            "tasks": selected_todos,
            "summary": {
                "total_tasks": len(selected_todos),
                "by_priority": self._count_by_priority(selected_todos),
                "by_type": self._count_by_type(selected_todos),
                "by_risk": self._count_by_risk(selected_todos),
            },
            "meta": {
                "domain": agent_spec["domain"],
                "focus": agent_spec["focus"],
                "risk_level": agent_spec["risk_level"],
                "specialization": "domain_expert",
            },
            "dependencies": [],
            "checks": ["ruff check .", "pytest -q", "pre-commit run --all-files"],
        }

        # Save batch file
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        batch_file = output_path / f"{batch['batch_id']}.json"

        with open(batch_file, "w") as f:
            json.dump(batch, f, indent=2)

        print(f"✅ Created {agent_id}: {len(selected_todos)} tasks -> {batch_file}")
        print(f"   Domain: {agent_spec['domain']}")
        print(f"   Focus: {agent_spec['focus']}")

        return batch

    def _count_by_priority(self, todos: list[dict[str, Any]]) -> dict[str, int]:
        """Count tasks by priority."""
        counts = {}
        for todo in todos:
            priority = todo.get("priority", "unknown")
            counts[priority] = counts.get(priority, 0) + 1
        return counts

    def _count_by_type(self, todos: list[dict[str, Any]]) -> dict[str, int]:
        """Count tasks by type."""
        counts = {}
        for todo in todos:
            todo_type = todo.get("est", {}).get("type", "unknown")
            counts[todo_type] = counts.get(todo_type, 0) + 1
        return counts

    def _count_by_risk(self, todos: list[dict[str, Any]]) -> dict[str, int]:
        """Count tasks by risk level."""
        counts = {}
        for todo in todos:
            risk = todo.get("risk", "unknown")
            counts[risk] = counts.get(risk, 0) + 1
        return counts

    def create_all_batches(self, output_dir: str):
        """Create all specialized agent batches"""
        created_batches = []

        for agent_id in self.agent_specs:
            batch = self.create_batch(agent_id, output_dir)
            if batch:
                created_batches.append(batch)

        print("\n🎯 Specialized batch creation complete!")
        print(f"   Created {len(created_batches)} specialized agent batches")
        print(f"   Total tasks allocated: {sum(batch['summary']['total_tasks'] for batch in created_batches)}")

        return created_batches


def main():
    parser = argparse.ArgumentParser(description="Create specialized agent batches")
    parser.add_argument("--manifest", required=True, help="Manifest JSON file")
    parser.add_argument("--output", required=True, help="Output directory for batch files")
    parser.add_argument("--agent", help="Create batch for specific agent only")

    args = parser.parse_args()

    creator = SpecializedBatchCreator(args.manifest)

    if args.agent:
        creator.create_batch(args.agent, args.output)
    else:
        creator.create_all_batches(args.output)


if __name__ == "__main__":
    main()
