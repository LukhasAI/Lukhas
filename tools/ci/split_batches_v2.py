#!/usr/bin/env python3
"""
T4-Compliant Batch Splitter v2.0
PLANNING_TODO.md Section 10 Implementation

Splits tracked tasks from manifest into agent-specific batches following exact PLANNING_TODO.md specification:
- Implements concrete allocation starter (Section 10)
- Uses allocation_rules.yaml for agent capabilities
- Respects T4 principles: skepticism, evidence, atomic discipline
"""

import argparse
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class T4BatchSplitter:
    def __init__(self, rules_file: str = "rules/allocation_rules.yaml"):
        self.rules = self._load_rules(rules_file)
        self.agents = self._initialize_agents()
        self.assigned_tasks = set()

    def _load_rules(self, rules_file: str) -> Dict[str, Any]:
        """Load allocation rules from YAML file"""
        try:
            with open(rules_file, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to basic rules if file doesn't exist
            return self._get_default_rules()

    def _get_default_rules(self) -> Dict[str, Any]:
        """Default allocation rules matching PLANNING_TODO.md Section 10"""
        return {
            "agents": {
                "jules01": {
                    "domain": "Identity Core",
                    "capabilities": ["identity", "trace", "persistence"],
                    "batch_size": 25,
                    "priorities": ["critical", "high"],
                    "risk_level": "high",
                },
                "codex01": {
                    "domain": "F821 Fixes",
                    "capabilities": ["f821", "undefined", "import"],
                    "batch_size": 30,
                    "priorities": ["critical", "high", "med", "low"],
                    "risk_level": "low",
                },
            }
        }

    def _initialize_agents(self) -> Dict[str, Dict[str, Any]]:
        """Initialize agent state tracking"""
        agents = {}
        for agent_id, config in self.rules["agents"].items():
            agents[agent_id] = {
                "config": config,
                "assigned": [],
                "current_batch_size": 0,
                "batch_id": f"BATCH-{agent_id.upper()}-{datetime.now().strftime('%Y-%m-%d')}-01",
            }
        return agents

    def split_todos(self, manifest: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Split tracked tasks into agent-specific batches following PLANNING_TODO.md Section 10."""
        todos = manifest["todos"]
        batches = {}

        print(f"Splitting {len(todos)} tracked tasks into agent batches...")

        # Sort by priority: critical > high > med > low
        priority_order = ["critical", "high", "med", "low", "unknown"]
        sorted_todos = sorted(todos, key=lambda x: priority_order.index(x.get("priority", "unknown")))

        # Process by priority groups as specified in Section 10
        for todo in sorted_todos:
            if todo["status"] != "open":
                continue

            agent = self._assign_todo_to_agent(todo)
            if agent and todo["task_id"] not in self.assigned_tasks:
                if agent not in batches:
                    batches[agent] = []

                batches[agent].append(todo)
                self.agents[agent]["assigned"].append(todo["task_id"])
                self.agents[agent]["current_batch_size"] += 1
                self.assigned_tasks.add(todo["task_id"])

        return batches

    def _assign_todo_to_agent(self, todo: Dict[str, Any]) -> Optional[str]:
        """Assign a tracked task to an agent following PLANNING_TODO.md allocation rules."""
        priority = todo["priority"]
        module = todo["module"]
        todo_type = todo["est"]["type"]
        risk = todo["risk"]

        # Apply priority distribution rules from Section 10
        if priority == "critical":
            # Critical: 60% Jules, 30% Claude-paired Jules, 10% Codex (only mechanical)
            if todo_type == "mechanical":
                agent = self._find_available_agent(
                    ["codex01", "codex02", "codex03", "codex04", "codex05", "codex06"], todo
                )
            else:
                agent = self._find_available_agent(["jules01", "jules02", "jules03", "jules04", "jules05"], todo)
        elif priority == "high":
            # High: 40% Jules, 40% Codex, 20% Copilot
            if todo_type == "mechanical":
                agent = self._find_available_agent(
                    ["codex01", "codex02", "codex03", "codex04", "codex05", "codex06"], todo
                )
            else:
                agent = self._find_available_agent(
                    ["jules01", "jules02", "jules03", "jules04", "jules05", "jules09", "jules10"], todo
                )
        else:
            # Med/Low: 20% Jules, 60% Codex, 20% Copilot
            if todo_type == "mechanical":
                agent = self._find_available_agent(
                    [
                        "codex01",
                        "codex02",
                        "codex03",
                        "codex04",
                        "codex05",
                        "codex06",
                        "codex07",
                        "codex08",
                        "codex09",
                        "codex10",
                    ],
                    todo,
                )
            else:
                agent = self._find_available_agent(["jules09", "jules10"], todo)

        # Apply specific module mappings from PLANNING_TODO.md Section 10
        if not agent:
            agent = self._assign_by_domain(todo)

        return agent

    def _assign_by_domain(self, todo: Dict[str, Any]) -> Optional[str]:
        """Assign based on domain expertise as specified in PLANNING_TODO.md Section 10."""
        module = todo["module"].lower()

        # Jules-01: Identity core (ΛTRACE persistence; audit chain linking)
        if any(keyword in module for keyword in ["identity", "trace", "audit"]):
            return self._find_available_agent(["jules01"], todo)

        # Jules-02: Consent/Scopes (tier boundaries, validation, history → ΛTRACE)
        if any(keyword in module for keyword in ["consent", "governance", "tier", "scope"]):
            return self._find_available_agent(["jules02"], todo)

        # Jules-03: SSO/biometrics/symbolic challenge (gated, mocked)
        if any(keyword in module for keyword in ["sso", "auth", "bridge", "biometric"]):
            return self._find_available_agent(["jules03"], todo)

        # Jules-04: Awareness protocol reconciliation with ΛTIER
        if any(keyword in module for keyword in ["consciousness", "awareness", "tier"]):
            return self._find_available_agent(["jules04"], todo)

        # Jules-05: Guardian ethics advanced intent + governance forwarding
        if any(keyword in module for keyword in ["guardian", "ethics", "governance"]):
            return self._find_available_agent(["jules05"], todo)

        # Jules-06: QRG generator & session replay scaffolding
        if any(keyword in module for keyword in ["qrg", "quantum", "replay"]):
            return self._find_available_agent(["jules06"], todo)

        # Jules-07: Wallet/QI bridges (init placeholders, interfaces)
        if any(keyword in module for keyword in ["wallet", "qi", "bridge"]):
            return self._find_available_agent(["jules07"], todo)

        # Jules-08: Quantum entropy stubs + interfaces (no prod)
        if any(keyword in module for keyword in ["quantum", "entropy", "qi"]):
            return self._find_available_agent(["jules08"], todo)

        # Jules-09: Compliance/Guardian dashboards (data wiring)
        if any(keyword in module for keyword in ["dashboard", "compliance", "visual"]):
            return self._find_available_agent(["jules09"], todo)

        # Jules-10: Tests: integration identity imports + e2e glue
        if any(keyword in module for keyword in ["test", "integration", "e2e"]):
            return self._find_available_agent(["jules10"], todo)

        # Codex agents for mechanical tasks
        if todo["est"]["type"] == "mechanical":
            return self._find_available_agent(["codex01", "codex02", "codex03", "codex04", "codex05", "codex06"], todo)

        # Default fallback
        return self._find_available_agent(list(self.agents.keys()), todo)

    def _find_available_agent(self, agent_candidates: List[str], todo: Dict[str, Any]) -> Optional[str]:
        """Find available agent from candidates with capacity"""
        for agent_id in agent_candidates:
            if agent_id not in self.agents:
                continue

            agent_state = self.agents[agent_id]
            config = agent_state["config"]

            # Check batch capacity
            max_batch = config.get("batch_size", 25)
            if agent_state["current_batch_size"] >= max_batch:
                continue

            # Check priority compatibility
            priorities = config.get("priorities", ["critical", "high", "med", "low"])
            if todo["priority"] not in priorities:
                continue

            # Check risk compatibility
            if config.get("risk_level") == "low" and todo["risk"] == "high":
                continue

            return agent_id

        return None

    def create_batch_files(self, batches: Dict[str, List[Dict[str, Any]]], output_dir: str):
        """Create batch files with proper T4 structure"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Creating batch files in {output_dir}...")

        for agent_id, tasks in batches.items():
            if not tasks:
                continue

            agent_config = self.agents[agent_id]["config"]
            batch_data = {
                "batch_id": self.agents[agent_id]["batch_id"],
                "agent": agent_id,
                "created_at": datetime.now().isoformat() + "Z",
                "expires_at": (datetime.now() + timedelta(hours=72)).isoformat() + "Z",
                "branch_name": f"feat/{agent_id}/{agent_config.get('domain', 'general').lower().replace(' ', '-').replace('/', '-')}-batch01",
                "status": "ready",
                "tasks": tasks,
                "meta": {
                    "domain": agent_config.get("domain", "General"),
                    "description": agent_config.get("description", ""),
                    "risk_level": agent_config.get("risk_level", "medium"),
                    "requires_review": agent_config.get("requires_review", False),
                    "feature_flags_required": agent_config.get("feature_flags_required", False),
                    "experimental": agent_config.get("experimental", False),
                    "total_tasks": len(tasks),
                },
            }

            batch_filename = f"{self.agents[agent_id]['batch_id']}.json"
            batch_file = output_path / batch_filename

            with open(batch_file, "w") as f:
                json.dump(batch_data, f, indent=2)

            print(f"Created batch for {agent_id}: {len(tasks)} tasks -> {batch_filename}")


def main():
    parser = argparse.ArgumentParser(description="T4-Compliant Batch Splitter v2.0")
    parser.add_argument("--manifest", required=True, help="Manifest JSON file")
    parser.add_argument("--rules", default="rules/allocation_rules.yaml", help="Allocation rules YAML file")
    parser.add_argument("--out", required=True, help="Output directory for batch files")

    args = parser.parse_args()

    # Load manifest
    with open(args.manifest, "r") as f:
        manifest = json.load(f)

    # Create splitter and process
    splitter = T4BatchSplitter(args.rules)
    batches = splitter.split_todos(manifest)
    splitter.create_batch_files(batches, args.out)

    # Summary
    print(f"\nBatch allocation complete!")
    print(f"Created {len(batches)} batches")
    for agent_id, tasks in batches.items():
        batch_id = splitter.agents[agent_id]["batch_id"]
        domain = splitter.agents[agent_id]["config"].get("domain", "General")
        print(f"  {agent_id}: {len(tasks)} tasks ({batch_id}) - {domain}")


if __name__ == "__main__":
    main()
