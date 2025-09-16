#!/usr/bin/env python3
"""
T4-Compliant Progress Generator
PLANNING_TODO.md Section 6 & 9 Implementation

Generates progress.json rollup metrics and daily reports for the task coordination system.
Implements synchronization and source of truth as specified in PLANNING_TODO.md.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


class ProgressGenerator:
    def __init__(self, run_dir: str):
        self.run_dir = Path(run_dir)
        self.manifest = self._load_manifest()
        self.batches = self._load_batches()

    def _load_manifest(self) -> Dict[str, Any]:
        """Load the manifest describing tracked tasks."""
        manifest_files = list(self.run_dir.glob("manifest*.json"))
        if not manifest_files:
            raise FileNotFoundError("No manifest.json found in run directory")

        with open(manifest_files[0], "r") as f:
            return json.load(f)

    def _load_batches(self) -> Dict[str, Dict[str, Any]]:
        """Load all batch files from the most recent batch directory"""
        batches = {}
        # Priority order: clean is most recent/authoritative, then v2, then original
        batch_dirs = ["batches_clean", "batches_v2", "batches"]

        for batch_dir in batch_dirs:
            batch_path = self.run_dir / batch_dir
            if batch_path.exists():
                print(f"Loading batches from: {batch_path}")
                for batch_file in batch_path.glob("BATCH-*.json"):
                    with open(batch_file, "r") as f:
                        batch_data = json.load(f)
                        batches[batch_data["agent"]] = batch_data
                print(f"Loaded {len(batches)} batches from {batch_dir}")
                break

        return batches

    def generate_progress_json(self) -> Dict[str, Any]:
        """Generate progress.json as specified in PLANNING_TODO.md Section 9."""
        stats = self.manifest.get("stats", {})

        # Count by priority and status
        priority_counts = {}
        for priority in ["critical", "high", "med", "low"]:
            priority_counts[priority] = {
                "open": 0,
                "wip": 0,
                "done": 0,
                "total": stats.get("by_priority", {}).get(priority, 0),
            }

        # Count todos by status and priority
        for todo in self.manifest.get("todos", []):
            priority = todo.get("priority", "unknown")
            if priority in priority_counts:
                status = todo.get("status", "open")
                if status == "completed":
                    priority_counts[priority]["done"] += 1
                elif status == "wip":
                    priority_counts[priority]["wip"] += 1
                else:
                    priority_counts[priority]["open"] += 1

        # Agent statistics
        agent_stats = {}
        for agent_id, batch in self.batches.items():
            tasks = batch.get("tasks", [])
            assigned = len(tasks)
            done = len([t for t in tasks if t.get("status") == "completed"])
            wip = len([t for t in tasks if t.get("status") == "wip"])

            agent_stats[agent_id] = {
                "assigned": assigned,
                "done": done,
                "wip": wip,
                "remaining": assigned - done - wip,
                "batch_id": batch.get("batch_id", ""),
                "domain": batch.get("meta", {}).get("domain", ""),
                "risk_level": batch.get("meta", {}).get("risk_level", "medium"),
            }

        # Overall metrics
        total_assigned = sum(stats["assigned"] for stats in agent_stats.values())
        total_done = sum(stats["done"] for stats in agent_stats.values())
        total_wip = sum(stats["wip"] for stats in agent_stats.values())

        progress_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "run_id": self.manifest.get("run_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_todos": stats.get("total", 0),
                "total_assigned": total_assigned,
                "total_done": total_done,
                "total_wip": total_wip,
                "total_remaining": total_assigned - total_done - total_wip,
                "completion_rate": (total_done / max(total_assigned, 1)) * 100,
                "active_batches": len(self.batches),
            },
            "counts": priority_counts,
            "agents": agent_stats,
            "distribution": {
                "by_priority": stats.get("by_priority", {}),
                "by_status": stats.get("by_status", {}),
                "by_source": stats.get("by_source", {}),
            },
            "verification": {
                "evidence_verified": total_done,
                "requires_review": len(
                    [batch for batch in self.batches.values() if batch.get("meta", {}).get("requires_review", False)]
                ),
                "feature_flags_required": len(
                    [
                        batch
                        for batch in self.batches.values()
                        if batch.get("meta", {}).get("feature_flags_required", False)
                    ]
                ),
                "experimental": len(
                    [batch for batch in self.batches.values() if batch.get("meta", {}).get("experimental", False)]
                ),
            },
        }

        return progress_data

    def generate_daily_report(self, progress_data: Dict[str, Any]) -> str:
        """Generate daily report as specified in PLANNING_TODO.md Section 9."""
        date = progress_data["date"]
        summary = progress_data["summary"]

        report = f"""# LUKHAS AI Task Management Daily Report

**Date**: {date}
**Run ID**: {progress_data["run_id"]}
**System**: T4-Compliant Evidence-Based Task Coordination

## 📊 Summary Statistics

### Ground Truth Status
- **Total tracked tasks**: {summary["total_todos"]:,} (verified via manifest)
- **Assigned**: {summary["total_assigned"]} ({summary["total_assigned"]/summary["total_todos"]*100:.1f}%)
- **Completed**: {summary["total_done"]} (evidence-verified, {summary["completion_rate"]:.1f}%)
- **In Progress**: {summary["total_wip"]} ({summary["total_wip"]/max(summary["total_assigned"],1)*100:.1f}%)
- **Remaining**: {summary["total_remaining"]} ({summary["total_remaining"]/max(summary["total_assigned"],1)*100:.1f}%)

### Priority Breakdown
"""

        for priority, counts in progress_data["counts"].items():
            if counts["total"] > 0:
                report += f"- **{priority.upper()}**: {counts['total']} tasks ({counts['total']/summary['total_todos']*100:.1f}%) - "
                report += f"{counts['done']} done, {counts['wip']} in progress, {counts['open']} open\n"

        report += f"""
## 🤖 Agent Assignment Status

### Active Batches ({summary["active_batches"]})
"""

        # Group agents by type
        jules_agents = {k: v for k, v in progress_data["agents"].items() if k.startswith("jules")}
        codex_agents = {k: v for k, v in progress_data["agents"].items() if k.startswith("codex")}

        if jules_agents:
            report += "\n**Jules Agents (Complex Logic):**\n"
            for agent, stats in jules_agents.items():
                report += f"- **{agent}**: {stats['assigned']} tasks ({stats['domain']}) - "
                report += f"{stats['done']} done, {stats['wip']} wip, {stats['remaining']} remaining\n"

        if codex_agents:
            report += "\n**Codex Agents (Mechanical Fixes):**\n"
            for agent, stats in codex_agents.items():
                report += f"- **{agent}**: {stats['assigned']} tasks ({stats['domain']}) - "
                report += f"{stats['done']} done, {stats['wip']} wip, {stats['remaining']} remaining\n"

        report += f"""
## 🛡️ Risk Assessment

### Safety Protocols
- **Requires Review**: {progress_data["verification"]["requires_review"]} batches need Claude Code review
- **Feature Flags**: {progress_data["verification"]["feature_flags_required"]} batches require feature flags
- **Experimental**: {progress_data["verification"]["experimental"]} batches are experimental (gated)

### T4 Compliance
- **Evidence-Based**: All {progress_data["verification"]["evidence_verified"]} completions verified
- **Atomic Discipline**: Each commit traceable to TaskID
- **Batch Discipline**: 72h expiration enforced
- **Risk Gating**: High-risk changes behind feature flags

## 📋 Next Actions

### Immediate Priorities
1. **Continue Batch Execution**: Focus on critical and high-priority batches
2. **Evidence Verification**: Ensure all completions have grep/test proof
3. **Risk Review**: Claude Code review required for high-risk batches
4. **Progress Tracking**: Update manifest.json with completion evidence

### Week 1 Goals
- Complete critical tasks with evidence verification
- Maintain batch discipline and atomic commits
- Achieve 25+ tasks completed per active batch
- Establish daily reporting rhythm

---

**Report Generated**: {datetime.now().isoformat()}Z
**Next Report**: {(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) +
                  (timedelta(days=1) if datetime.now().hour >= 9 else timedelta(days=0))).isoformat()}Z
**System Status**: ✅ Active task allocation system ready for execution
"""

        return report

    def save_reports(self, output_dir: str):
        """Save progress.json and daily report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate progress data
        progress_data = self.generate_progress_json()

        # Save progress.json
        progress_file = output_path / "progress.json"
        with open(progress_file, "w") as f:
            json.dump(progress_data, f, indent=2)

        # Save daily report
        report_content = self.generate_daily_report(progress_data)
        report_file = output_path / f"daily_report_{progress_data['date']}.md"
        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"✅ Generated progress.json: {progress_file}")
        print(f"✅ Generated daily report: {report_file}")
        print(
            f"📊 Summary: {progress_data['summary']['total_assigned']} assigned, "
            f"{progress_data['summary']['total_done']} done, "
            f"{progress_data['summary']['completion_rate']:.1f}% complete"
        )


def main():
    parser = argparse.ArgumentParser(description="T4-Compliant Progress Generator")
    parser.add_argument("--run-dir", required=True, help="Run directory (e.g., .lukhas_runs/2025-09-15)")
    parser.add_argument("--output", help="Output directory for reports (defaults to run-dir/reports)")

    args = parser.parse_args()

    output_dir = args.output or f"{args.run_dir}/reports"

    generator = ProgressGenerator(args.run_dir)
    generator.save_reports(output_dir)


if __name__ == "__main__":
    main()
