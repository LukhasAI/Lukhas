#!/usr/bin/env python3
"""
Split Integration Tasks for 15 Agents
Divides 540 files equally among 15 agents with balanced workload
"""

import json
import math
from collections import defaultdict
from datetime import datetime


def load_integration_tasks():
    """Load the integration tasks from JSON"""
    with open("ESSENTIAL_REPORTS/ESSENTIAL_integration_tasks.json") as f:
        return json.load(f)


def split_tasks_for_agents(num_agents=15):
    """Split tasks equally among agents"""
    tasks = load_integration_tasks()
    all_tasks = tasks["all_integration_tasks"]

    # Sort tasks by priority score (highest first)
    sorted_tasks = sorted(all_tasks, key=lambda x: x["priority_score"], reverse=True)

    # Calculate files per agent
    total_files = len(sorted_tasks)
    files_per_agent = math.ceil(total_files / num_agents)

    print("📊 TASK DISTRIBUTION ANALYSIS")
    print(f"{'='*60}")
    print(f"Total Files: {total_files}")
    print(f"Number of Agents: {num_agents}")
    print(f"Files per Agent: ~{files_per_agent}")
    print()

    # Create agent assignments
    agent_assignments = {}

    # Round-robin assignment to balance priority files
    for i, task in enumerate(sorted_tasks):
        agent_num = (i % num_agents) + 1
        agent_key = f"Agent_{agent_num:02d}"

        if agent_key not in agent_assignments:
            agent_assignments[agent_key] = {
                "agent_number": agent_num,
                "files": [],
                "categories": defaultdict(int),
                "total_priority_score": 0,
                "high_priority_files": 0,
                "medium_priority_files": 0,
                "low_priority_files": 0,
            }

        agent_assignments[agent_key]["files"].append(task)
        agent_assignments[agent_key]["categories"][task["category"]] += 1
        agent_assignments[agent_key]["total_priority_score"] += task["priority_score"]

        # Count priority levels
        if task["priority_score"] >= 50:
            agent_assignments[agent_key]["high_priority_files"] += 1
        elif task["priority_score"] >= 30:
            agent_assignments[agent_key]["medium_priority_files"] += 1
        else:
            agent_assignments[agent_key]["low_priority_files"] += 1

    # Create summary report
    report = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_files": total_files,
        "num_agents": num_agents,
        "files_per_agent": files_per_agent,
        "agent_assignments": agent_assignments,
    }

    # Save to JSON
    with open("agent_task_assignments_15.json", "w") as f:
        json.dump(report, f, indent=2)

    # Generate markdown summary
    generate_markdown_summary(agent_assignments, total_files)

    return agent_assignments


def generate_markdown_summary(assignments, total_files):
    """Generate markdown summary of agent assignments"""

    content = f"""# 👥 TASK ASSIGNMENTS FOR 15 AGENTS

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Files:** {total_files}
**Distribution:** ~36 files per agent

---

## 📊 AGENT ASSIGNMENTS

"""

    # Sort agents by number
    for agent_key in sorted(assignments.keys()):
        agent = assignments[agent_key]
        avg_priority = agent["total_priority_score"] / len(agent["files"])

        content += f"""### 🤖 **{agent_key.replace('_', ' ')}**
**Files:** {len(agent['files'])}
**Avg Priority:** {avg_priority:.1f}
**High/Medium/Low:** {agent['high_priority_files']}/{agent['medium_priority_files']}/{agent['low_priority_files']}

**Categories:**
"""
        # Sort categories by count
        for category, count in sorted(
            agent["categories"].items(), key=lambda x: x[1], reverse=True
        ):
            content += f"- {category}: {count} files\n"

        content += "\n**Top 5 Priority Files:**\n"
        # Show top 5 files
        top_files = sorted(
            agent["files"], key=lambda x: x["priority_score"], reverse=True
        )[:5]
        for i, file in enumerate(top_files, 1):
            content += f"{i}. `{file['file_path']}` ({file['priority_score']})\n"

        content += "\n---\n\n"

    # Add summary statistics
    content += """## 📈 DISTRIBUTION STATISTICS

### **Workload Balance:**
"""

    # Calculate min/max files per agent
    file_counts = [len(agent["files"]) for agent in assignments.values()]
    min_files = min(file_counts)
    max_files = max(file_counts)

    content += f"""- Min files per agent: {min_files}
- Max files per agent: {max_files}
- Difference: {max_files - min_files} files
- Balance score: {"✅ EXCELLENT" if max_files - min_files <= 1 else "⚠️ GOOD"}

### **Priority Distribution:**
Each agent receives a balanced mix of high, medium, and low priority files through round-robin assignment.

### **Recommended Timeline:**
- **Week 1-2:** Focus on high priority files (50+ score)
- **Week 3-4:** Medium priority files (30-49 score)
- **Week 5-6:** Low priority files and testing

---

**Files saved:**
- `agent_task_assignments_15.json` - Complete assignment data
- `AGENT_ASSIGNMENTS_15.md` - This summary
"""

    # Save markdown
    with open("AGENT_ASSIGNMENTS_15.md", "w") as f:
        f.write(content)

    print("✅ Files generated:")
    print("   - agent_task_assignments_15.json")
    print("   - AGENT_ASSIGNMENTS_15.md")


def print_summary(assignments):
    """Print summary to console"""
    print("\n📋 ASSIGNMENT SUMMARY")
    print(f"{'='*60}")
    print(
        f"{'Agent':<10} {'Files':<8} {'High':<6} {'Med':<6} {'Low':<6} {'Avg Priority':<12}"
    )
    print(f"{'-'*60}")

    for agent_key in sorted(assignments.keys()):
        agent = assignments[agent_key]
        avg_priority = agent["total_priority_score"] / len(agent["files"])
        print(
            f"{agent_key:<10} {len(agent['files']):<8} {agent['high_priority_files']:<6} "
            f"{agent['medium_priority_files']:<6} {agent['low_priority_files']:<6} {avg_priority:<12.1f}"
        )


def main():
    """Main function"""
    print("🚀 Splitting integration tasks for 15 agents...")

    assignments = split_tasks_for_agents(15)
    print_summary(assignments)

    print("\n✅ Task distribution complete!")
    print("📁 Check the generated files for detailed assignments")


if __name__ == "__main__":
    main()
