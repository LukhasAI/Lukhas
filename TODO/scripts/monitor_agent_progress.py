#!/usr/bin/env python3
"""
Real-time Agent Progress Monitor for LUKHAS TODO Management

Provides live monitoring of agent progress with evidence-based validation.
Tracks completion claims against actual code changes.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class AgentProgressMonitor:
    """Monitor agent progress with evidence-based validation"""

    def __init__(self):
        self.batches_dir = Path("TODO/agent_batches")
        self.workspace_dir = Path("TODO/agent_workspaces")
        self.validation_history = []

    def get_current_todo_count(self) -> int:
        """Get current TODO count from codebase"""
        try:
            result = subprocess.run(["rg", "-c", "TODO|FIXME|HACK", "--type", "py"], capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Filter out virtual environments
                filtered_lines = [
                    line for line in lines if not any(exc in line for exc in [".venv/", "venv/", "__pycache__/"])
                ]
                return sum(int(line.split(":")[1]) for line in filtered_lines if ":" in line)

        except Exception as e:
            print(f"Error counting TODOs: {e}")

        return -1

    def load_agent_batches(self) -> List[Dict[str, Any]]:
        """Load all agent batch configurations"""
        batches = []

        if self.batches_dir.exists():
            for batch_file in self.batches_dir.glob("*.json"):
                try:
                    with open(batch_file, "r") as f:
                        batch = json.load(f)
                        batch["config_file"] = batch_file.name
                        batches.append(batch)
                except Exception as e:
                    print(f"Error loading {batch_file}: {e}")

        return sorted(batches, key=lambda x: x.get("priority", "ZZZ"))

    def check_agent_workspace(self, agent_name: str) -> Dict[str, Any]:
        """Check if agent workspace exists and get status"""
        workspace_path = self.workspace_dir / agent_name

        if not workspace_path.exists():
            return {"status": "NOT_DEPLOYED", "workspace_exists": False}

        status = {"status": "DEPLOYED", "workspace_exists": True}

        # Check for batch config
        config_file = workspace_path / "batch_config.json"
        status["config_loaded"] = config_file.exists()

        # Check for progress file
        progress_file = workspace_path / "progress.json"
        if progress_file.exists():
            try:
                with open(progress_file, "r") as f:
                    progress = json.load(f)
                    status.update(progress)
            except Exception as e:
                status["progress_error"] = str(e)

        # Check for completion markers
        completion_file = workspace_path / "completion.json"
        if completion_file.exists():
            status["status"] = "COMPLETED"
            try:
                with open(completion_file, "r") as f:
                    completion = json.load(f)
                    status.update(completion)
            except Exception as e:
                status["completion_error"] = str(e)

        return status

    def validate_completion_claims(self, agent_name: str, claimed_todos: List[str]) -> Dict[str, Any]:
        """Validate agent completion claims against actual code"""
        validation = {
            "claimed_count": len(claimed_todos),
            "verified_count": 0,
            "evidence_found": [],
            "evidence_missing": [],
            "validation_timestamp": datetime.now().isoformat(),
        }

        for todo_claim in claimed_todos:
            # Check if TODO still exists in code
            try:
                # Extract file and line info from claim
                if ":" in todo_claim:
                    file_path = todo_claim.split(":")[0]

                    # Check if file exists
                    if Path(file_path).exists():
                        # Check if TODO still present
                        result = subprocess.run(
                            ["rg", "-n", "TODO|FIXME|HACK", file_path], capture_output=True, text=True
                        )

                        if result.returncode != 0 or not result.stdout.strip():
                            # TODO not found - likely completed
                            validation["verified_count"] += 1
                            validation["evidence_found"].append(todo_claim)
                        else:
                            # TODO still exists
                            validation["evidence_missing"].append(todo_claim)
                    else:
                        # File doesn't exist - could be deleted/moved
                        validation["evidence_found"].append(f"{todo_claim} (file removed)")
                        validation["verified_count"] += 1

            except Exception as e:
                validation["evidence_missing"].append(f"{todo_claim} (validation error: {e})")

        validation["completion_rate"] = (
            validation["verified_count"] / validation["claimed_count"] if validation["claimed_count"] > 0 else 0
        )

        return validation

    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        current_todo_count = self.get_current_todo_count()
        batches = self.load_agent_batches()

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "current_todo_count": current_todo_count,
                "initial_todo_count": 956,  # From validation
                "todos_eliminated": 956 - current_todo_count if current_todo_count > 0 else 0,
            },
            "agent_status": {},
            "phase_progress": {
                "phase_1": {"total": 369, "completed": 0, "status": "PENDING"},
                "phase_2": {"total": 16, "completed": 0, "status": "PENDING"},
                "phase_3": {"total": 571, "completed": 0, "status": "PENDING"},
            },
            "summary": {},
        }

        total_assigned = 0
        total_completed = 0
        agents_deployed = 0
        agents_completed = 0

        for batch in batches:
            agent_name = batch["agent_name"]
            workspace_status = self.check_agent_workspace(agent_name)

            agent_report = {
                "batch_id": batch["batch_id"],
                "priority": batch["priority"],
                "task_count": batch["task_count"],
                "workspace_status": workspace_status,
                "completion_validation": {},
            }

            total_assigned += batch["task_count"]

            if workspace_status["status"] == "DEPLOYED":
                agents_deployed += 1
            elif workspace_status["status"] == "COMPLETED":
                agents_completed += 1

                # Validate completion claims if available
                if "completed_todos" in workspace_status:
                    validation = self.validate_completion_claims(agent_name, workspace_status["completed_todos"])
                    agent_report["completion_validation"] = validation
                    total_completed += validation["verified_count"]

            report["agent_status"][agent_name] = agent_report

        # Update phase progress
        for agent_name, agent_data in report["agent_status"].items():
            if agent_data["priority"] in ["CRITICAL", "HIGH"]:
                if agent_data["workspace_status"]["status"] == "COMPLETED":
                    report["phase_progress"]["phase_1"]["completed"] += agent_data.get("completion_validation", {}).get(
                        "verified_count", 0
                    )
            elif agent_data["priority"] == "MEDIUM":
                if agent_data["workspace_status"]["status"] == "COMPLETED":
                    report["phase_progress"]["phase_2"]["completed"] += agent_data.get("completion_validation", {}).get(
                        "verified_count", 0
                    )
            elif agent_data["priority"] == "LOW":
                if agent_data["workspace_status"]["status"] == "COMPLETED":
                    report["phase_progress"]["phase_3"]["completed"] += agent_data.get("completion_validation", {}).get(
                        "verified_count", 0
                    )

        # Determine phase status
        for phase_name, phase_data in report["phase_progress"].items():
            completion_rate = phase_data["completed"] / phase_data["total"]
            if completion_rate >= 1.0:
                phase_data["status"] = "COMPLETED"
            elif completion_rate > 0:
                phase_data["status"] = "IN_PROGRESS"
            else:
                phase_data["status"] = "PENDING"

        report["summary"] = {
            "total_batches": len(batches),
            "agents_deployed": agents_deployed,
            "agents_completed": agents_completed,
            "total_assigned_todos": total_assigned,
            "total_completed_todos": total_completed,
            "completion_rate": total_completed / total_assigned if total_assigned > 0 else 0,
            "system_todo_reduction": ((956 - current_todo_count) / 956 if current_todo_count > 0 else 0),
        }

        return report

    def print_progress_dashboard(self, report: Dict[str, Any]) -> None:
        """Print formatted progress dashboard"""
        print("🎯 LUKHAS Agent Progress Dashboard")
        print("=" * 60)
        print(f"⏰ Updated: {report['timestamp']}")

        # System status
        system = report["system_status"]
        print(f"\n📊 SYSTEM STATUS")
        print(f"┌─ Current TODOs: {system['current_todo_count']}")
        print(f"├─ TODOs Eliminated: {system['todos_eliminated']}")
        print(
            f"└─ Progress: {system['todos_eliminated']}/{system['initial_todo_count']} "
            f"({(system['todos_eliminated']/system['initial_todo_count']*100):.1f}%)"
        )

        # Phase progress
        print(f"\n🎯 PHASE PROGRESS")
        for phase_name, phase_data in report["phase_progress"].items():
            status_emoji = {"PENDING": "⏳", "IN_PROGRESS": "🔄", "COMPLETED": "✅"}
            emoji = status_emoji.get(phase_data["status"], "❓")
            completion_rate = phase_data["completed"] / phase_data["total"] * 100
            print(
                f"{emoji} {phase_name.upper()}: {phase_data['completed']}/{phase_data['total']} "
                f"({completion_rate:.1f}%) - {phase_data['status']}"
            )

        # Agent status
        print(f"\n🤖 AGENT STATUS")
        for agent_name, agent_data in report["agent_status"].items():
            status = agent_data["workspace_status"]["status"]
            status_emoji = {"NOT_DEPLOYED": "⚪", "DEPLOYED": "🔄", "COMPLETED": "✅"}
            emoji = status_emoji.get(status, "❓")

            validation = agent_data.get("completion_validation", {})
            validation_info = ""
            if validation:
                rate = validation.get("completion_rate", 0) * 100
                validation_info = f" ({validation.get('verified_count', 0)}/{validation.get('claimed_count', 0)} verified, {rate:.1f}%)"

            print(f"{emoji} {agent_name}: {status} - {agent_data['task_count']} tasks{validation_info}")

        # Summary
        summary = report["summary"]
        print(f"\n📈 SUMMARY")
        print(f"┌─ Total Batches: {summary['total_batches']}")
        print(f"├─ Agents Deployed: {summary['agents_deployed']}")
        print(f"├─ Agents Completed: {summary['agents_completed']}")
        print(f"├─ TODOs Assigned: {summary['total_assigned_todos']}")
        print(f"├─ TODOs Completed: {summary['total_completed_todos']}")
        print(f"├─ Completion Rate: {summary['completion_rate']*100:.1f}%")
        print(f"└─ System TODO Reduction: {summary['system_todo_reduction']*100:.1f}%")


def main():
    """Main monitoring function"""
    monitor = AgentProgressMonitor()

    try:
        while True:
            report = monitor.generate_progress_report()

            # Clear screen and show dashboard
            print("\033[2J\033[H")  # Clear screen
            monitor.print_progress_dashboard(report)

            # Save report
            report_file = Path("TODO/progress_reports") / f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            print(f"\n💾 Report saved: {report_file}")
            print("\n🔄 Updating every 5 minutes... (Ctrl+C to stop)")

            time.sleep(300)  # Update every 5 minutes

    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
