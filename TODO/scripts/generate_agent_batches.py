#!/usr/bin/env python3
"""
Agent Task Batch Generator for LUKHAS TODO Management

Creates specific task batches for agents based on validated TODO analysis.
Generates deployment-ready configurations for Jules and Codex agents.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess


class AgentTaskGenerator:
    """Generate agent-specific task batches from validated TODO data"""

    def __init__(self, validation_report_path: str = "TODO/validation_report.json"):
        self.validation_report_path = validation_report_path
        self.report_data = self._load_validation_report()
        self.output_dir = Path("TODO/agent_batches")
        self.output_dir.mkdir(exist_ok=True)

    def _load_validation_report(self) -> Dict[str, Any]:
        """Load the validation report data"""
        with open(self.validation_report_path, "r") as f:
            return json.load(f)

    def extract_todos_by_priority(self) -> Dict[str, List[str]]:
        """Extract actual TODOs from codebase by priority"""
        priority_todos = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}

        try:
            # Get all TODOs with context
            result = subprocess.run(
                [
                    "rg",
                    "-n",
                    "TODO|FIXME|HACK",
                    "--type",
                    "py",
                    "--no-heading",
                    "--with-filename",
                    "-A",
                    "1",
                    "-B",
                    "1",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")

                # Filter and categorize
                for line in lines:
                    if not any(exclude in line for exclude in [".venv/", "venv/", "__pycache__/"]):
                        if ":" in line and any(marker in line.upper() for marker in ["TODO", "FIXME", "HACK"]):
                            # Determine priority based on content
                            line_lower = line.lower()
                            if any(
                                word in line_lower for word in ["critical", "security", "blocking", "urgent", "safety"]
                            ):
                                priority_todos["CRITICAL"].append(line)
                            elif any(
                                word in line_lower for word in ["important", "core", "framework", "agent", "test"]
                            ):
                                priority_todos["HIGH"].append(line)
                            elif any(word in line_lower for word in ["enhance", "improve", "optimize", "feature"]):
                                priority_todos["MEDIUM"].append(line)
                            else:
                                priority_todos["LOW"].append(line)

        except Exception as e:
            print(f"Error extracting TODOs: {e}")

        return priority_todos

    def generate_jules_critical_batch(self, todos: List[str]) -> Dict[str, Any]:
        """Generate Jules Critical batch configuration"""
        return {
            "agent_name": "Jules-CRITICAL",
            "batch_id": "BATCH-JULES-CRITICAL-001",
            "priority": "CRITICAL",
            "task_count": len(todos),
            "estimated_hours": 24,
            "deadline": "48 hours from assignment",
            "description": "Critical security, blocking, and safety TODOs requiring immediate attention",
            "requirements": [
                "All changes must include comprehensive tests",
                "Security validation required for all modifications",
                "Claude Code review mandatory before merge",
                "Trinity Framework compliance verification",
            ],
            "domains": [
                "Identity systems",
                "Consciousness frameworks",
                "Guardian/security systems",
                "Core infrastructure",
            ],
            "todos": todos[:9],  # Limit to 9 critical items
            "success_criteria": [
                "All critical TODOs resolved with evidence",
                "No breaking changes to existing functionality",
                "Full test coverage for all modifications",
                "Security review completed and approved",
            ],
            "risk_level": "HIGH",
            "review_required": True,
        }

    def generate_jules_high_batches(self, todos: List[str]) -> List[Dict[str, Any]]:
        """Generate Jules High Priority batch configurations"""
        # Split high priority TODOs into two batches
        batch_size = len(todos) // 2

        batch_01 = {
            "agent_name": "Jules-HIGH-01",
            "batch_id": "BATCH-JULES-HIGH-001",
            "priority": "HIGH",
            "task_count": batch_size,
            "estimated_hours": 48,
            "deadline": "72 hours from assignment",
            "description": "High priority candidate/ directory development TODOs",
            "focus_areas": ["candidate/ lane development", "core functionality", "framework integration"],
            "todos": todos[:batch_size],
            "success_criteria": [
                "Core candidate functionality stabilized",
                "Framework integration maintained",
                "All changes tested and documented",
            ],
            "risk_level": "MEDIUM-HIGH",
            "review_required": True,
        }

        batch_02 = {
            "agent_name": "Jules-HIGH-02",
            "batch_id": "BATCH-JULES-HIGH-002",
            "priority": "HIGH",
            "task_count": len(todos) - batch_size,
            "estimated_hours": 48,
            "deadline": "72 hours from assignment",
            "description": "High priority tools/, tests/, and lukhas/ integration TODOs",
            "focus_areas": ["tools automation", "testing framework", "core integration"],
            "todos": todos[batch_size:],
            "success_criteria": [
                "Testing framework fully functional",
                "Tools automation improved",
                "Core integration stable",
            ],
            "risk_level": "MEDIUM-HIGH",
            "review_required": True,
        }

        return [batch_01, batch_02]

    def generate_jules_medium_batch(self, todos: List[str]) -> Dict[str, Any]:
        """Generate Jules Medium Priority batch configuration"""
        return {
            "agent_name": "Jules-MEDIUM",
            "batch_id": "BATCH-JULES-MEDIUM-001",
            "priority": "MEDIUM",
            "task_count": len(todos),
            "estimated_hours": 36,
            "deadline": "96 hours from assignment",
            "description": "Medium priority feature enhancements and optimizations",
            "focus_areas": ["product features", "documentation improvements", "optimization"],
            "todos": todos,
            "success_criteria": ["Feature enhancements completed", "Documentation updated", "Optimization targets met"],
            "risk_level": "MEDIUM",
            "review_required": False,
        }

    def generate_codex_cleanup_batches(self, todos: List[str]) -> List[Dict[str, Any]]:
        """Generate Codex cleanup batch configurations"""
        batch_size = 100
        batches = []

        # Define cleanup targets
        cleanup_targets = [
            ("tools/", "Tools directory cleanup and automation"),
            ("quarantine/", "Legacy code triage and cleanup"),
            ("branding/products/", "Documentation and product features"),
            ("misc/", "Scattered low-priority items"),
            ("final-sweep/", "Final cleanup pass"),
            ("completion/", "Final verification and documentation"),
        ]

        for i, (target, description) in enumerate(cleanup_targets, 1):
            start_idx = (i - 1) * batch_size
            end_idx = min(start_idx + batch_size, len(todos))

            if start_idx < len(todos):
                batch_todos = todos[start_idx:end_idx]

                batches.append(
                    {
                        "agent_name": f"Codex-CLEANUP-{i:02d}",
                        "batch_id": f"BATCH-CODEX-CLEANUP-{i:03d}",
                        "priority": "LOW",
                        "task_count": len(batch_todos),
                        "estimated_hours": 24,
                        "deadline": "7 days from assignment",
                        "description": description,
                        "target": target,
                        "todos": batch_todos,
                        "automation_potential": "HIGH",
                        "success_criteria": [
                            "All assigned TODOs processed",
                            "Automated cleanup tools created where applicable",
                            "Documentation updated",
                        ],
                        "risk_level": "LOW",
                        "review_required": False,
                    }
                )

        return batches

    def generate_deployment_scripts(self, batches: List[Dict[str, Any]]) -> None:
        """Generate deployment scripts for agent batches"""

        # Create deployment directory
        deploy_dir = Path("TODO/deployments")
        deploy_dir.mkdir(exist_ok=True)

        # Generate master deployment script
        master_script = deploy_dir / "deploy_all_agents.sh"
        with open(master_script, "w") as f:
            f.write(
                """#!/bin/bash
# LUKHAS Agent Deployment Master Script
# Generated from validated TODO analysis

set -e

echo "🚀 LUKHAS Agent Deployment - Phase System"
echo "=========================================="

# Phase 1: Critical and High Priority
echo "📋 Phase 1: Deploying Critical and High Priority agents..."
./deploy_jules_critical.sh
./deploy_jules_high_01.sh
./deploy_jules_high_02.sh

echo "⏳ Waiting for Phase 1 completion before Phase 2..."
python ../scripts/wait_for_phase_completion.py --phase 1

# Phase 2: Medium Priority
echo "📋 Phase 2: Deploying Medium Priority agents..."
./deploy_jules_medium.sh

echo "⏳ Waiting for Phase 2 completion before Phase 3..."
python ../scripts/wait_for_phase_completion.py --phase 2

# Phase 3: Low Priority Cleanup
echo "📋 Phase 3: Deploying Cleanup agents..."
./deploy_codex_cleanup_all.sh

echo "✅ All agent deployments initiated!"
echo "📊 Monitor progress with: python ../scripts/monitor_all_agents.py"
"""
            )

        # Make executable
        os.chmod(master_script, 0o755)

        # Generate individual deployment scripts for each batch
        for batch in batches:
            agent_name = batch["agent_name"].lower().replace("-", "_")
            script_path = deploy_dir / f"deploy_{agent_name}.sh"

            with open(script_path, "w") as f:
                f.write(
                    f"""#!/bin/bash
# Deploy {batch['agent_name']} - {batch['description']}

echo "🤖 Deploying {batch['agent_name']}..."
echo "📋 Task Count: {batch['task_count']}"
echo "⏰ Estimated: {batch['estimated_hours']} hours"
echo "🎯 Priority: {batch['priority']}"

# Create agent workspace
mkdir -p "../agent_workspaces/{batch['agent_name']}"
cd "../agent_workspaces/{batch['agent_name']}"

# Copy batch configuration
cp "../../agent_batches/{batch['batch_id']}.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ {batch['agent_name']} deployed and ready!"
"""
                )

            os.chmod(script_path, 0o755)

    def save_agent_batches(self, batches: List[Dict[str, Any]]) -> None:
        """Save agent batch configurations to JSON files"""
        for batch in batches:
            batch_file = self.output_dir / f"{batch['batch_id']}.json"
            with open(batch_file, "w") as f:
                json.dump(batch, f, indent=2)
            print(f"📁 Saved batch: {batch_file}")

    def generate_all_batches(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all agent batch configurations"""
        print("🔍 Extracting TODOs by priority...")
        priority_todos = self.extract_todos_by_priority()

        print(f"📊 Priority Distribution:")
        for priority, todos in priority_todos.items():
            print(f"  {priority}: {len(todos)} TODOs")

        all_batches = {}

        # Generate Jules batches
        if priority_todos["CRITICAL"]:
            all_batches["jules_critical"] = [self.generate_jules_critical_batch(priority_todos["CRITICAL"])]

        if priority_todos["HIGH"]:
            all_batches["jules_high"] = self.generate_jules_high_batches(priority_todos["HIGH"])

        if priority_todos["MEDIUM"]:
            all_batches["jules_medium"] = [self.generate_jules_medium_batch(priority_todos["MEDIUM"])]

        # Generate Codex batches
        if priority_todos["LOW"]:
            all_batches["codex_cleanup"] = self.generate_codex_cleanup_batches(priority_todos["LOW"])

        # Flatten for saving and deployment
        all_batch_list = []
        for category, batches in all_batches.items():
            all_batch_list.extend(batches)

        return all_batches, all_batch_list


def main():
    """Main execution function"""
    print("🎯 LUKHAS Agent Task Batch Generator")
    print("=" * 50)

    generator = AgentTaskGenerator()

    # Generate all agent batches
    categorized_batches, all_batches = generator.generate_all_batches()

    # Save batch configurations
    print("\n💾 Saving agent batch configurations...")
    generator.save_agent_batches(all_batches)

    # Generate deployment scripts
    print("\n🚀 Generating deployment scripts...")
    generator.generate_deployment_scripts(all_batches)

    # Print summary
    print("\n📋 AGENT BATCH SUMMARY")
    print("-" * 30)

    total_tasks = 0
    for category, batches in categorized_batches.items():
        category_tasks = sum(batch["task_count"] for batch in batches)
        total_tasks += category_tasks
        print(f"📦 {category.upper()}: {len(batches)} batches, {category_tasks} tasks")

    print(f"\n🎯 TOTAL: {len(all_batches)} batches, {total_tasks} tasks")
    print(f"📁 Configurations saved to: TODO/agent_batches/")
    print(f"🚀 Deployment scripts in: TODO/deployments/")
    print(f"\n✅ Ready for agent deployment!")


if __name__ == "__main__":
    main()
