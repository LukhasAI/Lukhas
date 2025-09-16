#!/usr/bin/env python3
"""
T4-Compliant Batch Splitter

Splits tracked tasks from manifest into agent-specific batches following T4 principles:
- Respects agent capabilities and batch size limits
- Implements risk-based assignment
- Creates locked batch files to prevent duplication
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class BatchSplitter:
    def __init__(self, strategy_file: str):
        self.strategy = self._load_strategy(strategy_file)
        self.agents = self._initialize_agents()

    def _load_strategy(self, strategy_file: str) -> Dict[str, Any]:
        """Load allocation strategy from YAML or use defaults"""
        if strategy_file and strategy_file != "default" and Path(strategy_file).exists():
            try:
                import yaml

                with open(strategy_file, "r") as handle:
                    data = yaml.safe_load(handle) or {}
                if data:
                    return data  # ΛTAG: strategy_loader
            except Exception as strategy_error:
                print(f"⚠️ Failed to load strategy {strategy_file}: {strategy_error}")

        # Default T4 strategy if file doesn't exist
        return {
            "agent_capabilities": {
                "jules01": {"types": ["logic", "integration"], "max_batch": 25, "priorities": ["critical", "high"]},
                "jules02": {"types": ["logic", "integration"], "max_batch": 25, "priorities": ["critical", "high"]},
                "jules03": {"types": ["logic", "integration"], "max_batch": 25, "priorities": ["critical", "high"]},
                "jules04": {"types": ["logic"], "max_batch": 20, "priorities": ["critical", "high"]},
                "jules05": {"types": ["logic"], "max_batch": 20, "priorities": ["critical", "high"]},
                "jules06": {"types": ["logic"], "max_batch": 20, "priorities": ["high", "med"], "risk_flags": True},
                "jules07": {"types": ["logic"], "max_batch": 20, "priorities": ["high", "med"], "risk_flags": True},
                "jules08": {"types": ["logic"], "max_batch": 20, "priorities": ["high", "med"], "risk_flags": True},
                "jules09": {"types": ["integration"], "max_batch": 25, "priorities": ["high", "med"]},
                "jules10": {"types": ["integration"], "max_batch": 25, "priorities": ["high", "med"]},
                "codex01": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex02": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex03": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex04": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex05": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex06": {"types": ["mechanical"], "max_batch": 40, "priorities": ["high", "med", "low"]},
                "codex07": {"types": ["mechanical", "logic"], "max_batch": 30, "priorities": ["med", "low"]},
                "codex08": {"types": ["mechanical", "logic"], "max_batch": 30, "priorities": ["med", "low"]},
                "codex09": {"types": ["mechanical", "logic"], "max_batch": 30, "priorities": ["med", "low"]},
                "codex10": {"types": ["mechanical", "logic"], "max_batch": 30, "priorities": ["med", "low"]},
            },
            "priority_distribution": {
                "critical": {"jules": 0.6, "claude_paired": 0.3, "codex": 0.1},
                "high": {"jules": 0.4, "codex": 0.4, "copilot": 0.2},
                "med": {"jules": 0.2, "codex": 0.6, "copilot": 0.2},
                "low": {"jules": 0.1, "codex": 0.7, "copilot": 0.2},
            },
            "high_risk_modules": ["qi", "quantum", "crypto", "guardian", "consciousness", "identity"],
            "mechanical_keywords": ["import", "f821", "rename", "docstring", "format"],
        }

    def _initialize_agents(self) -> Dict[str, Dict[str, Any]]:
        """Initialize agent state tracking"""
        agents = {}
        for agent_id, config in self.strategy["agent_capabilities"].items():
            agents[agent_id] = {"config": config, "assigned": [], "current_batch_size": 0}
        return agents

    def split_todos(self, manifest: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Split tracked tasks into agent-specific batches"""
        todos = manifest["todos"]
        batches = {}

        # Sort tasks by priority for allocation
        priority_order = ["critical", "high", "med", "low", "unknown"]
        sorted_todos = sorted(todos, key=lambda x: priority_order.index(x.get("priority", "unknown")))

        for todo in sorted_todos:
            if todo["status"] != "open":
                continue  # Skip completed or blocked tasks

            agent = self._assign_todo_to_agent(todo)
            if agent:
                if agent not in batches:
                    batches[agent] = []
                batches[agent].append(todo)
                self.agents[agent]["assigned"].append(todo["task_id"])
                self.agents[agent]["current_batch_size"] += 1

        return batches

    def _assign_todo_to_agent(self, todo: Dict[str, Any]) -> str:
        """Assign a tracked task to the most appropriate agent"""
        priority = todo["priority"]
        todo_type = todo["est"]["type"]
        risk = todo["risk"]
        module = todo["module"]

        # Find eligible agents
        eligible_agents = []
        for agent_id, agent_state in self.agents.items():
            config = agent_state["config"]

            # Check if agent can handle this priority
            if priority not in config["priorities"]:
                continue

            # Check if agent can handle this type
            if todo_type not in config["types"]:
                continue

            # Check batch size limit
            if agent_state["current_batch_size"] >= config["max_batch"]:
                continue

            # Check risk flags for experimental agents
            if config.get("risk_flags") and risk != "high":
                continue  # Risk-flagged agents only take high-risk work

            # Check if module requires special handling
            if self._is_high_risk_module(module) and not agent_id.startswith("jules"):
                continue  # High-risk modules require Jules agents

            eligible_agents.append((agent_id, agent_state))

        if not eligible_agents:
            return None  # No agent available

        # Select agent with lowest current batch size (load balancing)
        selected_agent = min(eligible_agents, key=lambda x: x[1]["current_batch_size"])
        return selected_agent[0]

    def _is_high_risk_module(self, module: str) -> bool:
        """Check if module is high-risk requiring Jules assignment"""
        module_lower = module.lower()
        return any(risk_keyword in module_lower for risk_keyword in self.strategy["high_risk_modules"])

    def create_batch_files(self, batches: Dict[str, List[Dict[str, Any]]], output_dir: str, run_id: str):
        """Create batch files for each agent"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        batch_summary = {"run_id": run_id, "created_at": datetime.now().isoformat() + "Z", "batches": {}}

        for agent_id, todos in batches.items():
            if not todos:
                continue

            batch_id = f"BATCH-{agent_id.upper()}-{datetime.now().strftime('%Y-%m-%d')}-01"

            # Generate branch name
            agent_type = "jules" if agent_id.startswith("jules") else "codex"
            agent_num = agent_id[-2:] if len(agent_id) >= 2 else "01"
            module_hint = self._get_dominant_module(todos)
            branch_name = f"feat/{agent_type}{agent_num}/{module_hint}-batch01"

            batch_file = {
                "batch_id": batch_id,
                "agent": agent_id,
                "created_at": datetime.now().isoformat() + "Z",
                "expires_at": self._calculate_expiry(),
                "branch_name": branch_name,
                "status": "ready",
                "tasks": todos,
                "summary": {
                    "total_tasks": len(todos),
                    "by_priority": self._count_by_field(todos, "priority"),
                    "by_type": self._count_by_field(todos, ["est", "type"]),
                    "by_risk": self._count_by_field(todos, "risk"),
                },
                "dependencies": [],
                "checks": ["ruff check .", "pytest -q", "pre-commit run --all-files"],
            }

            # Write batch file
            batch_filename = f"{batch_id}.json"
            batch_filepath = output_path / batch_filename
            with open(batch_filepath, "w") as f:
                json.dump(batch_file, f, indent=2)

            batch_summary["batches"][agent_id] = {
                "batch_id": batch_id,
                "file": batch_filename,
                "tasks": len(todos),
                "branch": branch_name,
            }

            print(f"Created batch for {agent_id}: {len(todos)} tasks -> {batch_filename}")

        # Write summary
        summary_file = output_path / "batch_summary.json"
        with open(summary_file, "w") as f:
            json.dump(batch_summary, f, indent=2)

        return batch_summary

    def _get_dominant_module(self, todos: List[Dict[str, Any]]) -> str:
        """Get the most common module for branch naming"""
        module_counts = {}
        for todo in todos:
            module = todo["module"].split("/")[0]  # Take first part
            module_counts[module] = module_counts.get(module, 0) + 1

        if not module_counts:
            return "mixed"

        dominant_module = max(module_counts, key=module_counts.get)
        return dominant_module.replace(".", "-").lower()

    def _calculate_expiry(self) -> str:
        """Calculate batch expiry (72 hours from now)"""
        from datetime import timedelta

        expiry = datetime.now() + timedelta(hours=72)
        return expiry.isoformat() + "Z"

    def _count_by_field(self, todos: List[Dict[str, Any]], field) -> Dict[str, int]:
        """Count tracked tasks by a specific field"""
        counts = {}
        for todo in todos:
            if isinstance(field, list):
                # Nested field access
                value = todo
                for key in field:
                    value = value.get(key, "unknown")
            else:
                value = todo.get(field, "unknown")

            counts[value] = counts.get(value, 0) + 1
        return counts


def main():
    parser = argparse.ArgumentParser(description="Split tracked tasks into agent batches")
    parser.add_argument("--manifest", required=True, help="Input manifest file")
    parser.add_argument("--strategy", help="Allocation strategy file (optional)")
    parser.add_argument("--out", required=True, help="Output directory for batch files")

    args = parser.parse_args()

    # Load manifest
    with open(args.manifest, "r") as f:
        manifest = json.load(f)

    # Initialize splitter
    strategy_file = args.strategy if args.strategy else "default"
    splitter = BatchSplitter(strategy_file)

    # Split into batches
    print(f"Splitting {len(manifest['todos'])} tracked tasks into agent batches...")
    batches = splitter.split_todos(manifest)

    # Create batch files
    print(f"Creating batch files in {args.out}...")
    summary = splitter.create_batch_files(batches, args.out, manifest["run_id"])

    print(f"\nBatch allocation complete!")
    print(f"Created {len(summary['batches'])} batches")
    for agent_id, info in summary["batches"].items():
        print(f"  {agent_id}: {info['tasks']} tasks ({info['batch_id']})")


if __name__ == "__main__":
    main()
