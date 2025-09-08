#!/usr/bin/env python3
"""
Extract comprehensive tasks from Claude_6.yml and create detailed task files for each agent
"""

import json
from datetime import datetime
from pathlib import Path

import yaml


def extract_agent_tasks(config_file="scripts/Claude_6.yml", output_dir="CLAUDE_ARMY/tasks"):
    """Extract all tasks from Claude_6.yml and create comprehensive task files"""

    # Load the YAML configuration
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Process each agent
    agents_processed = []

    for agent_key in ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5", "agent_6"]:
        if agent_key not in config:
            continue

        agent = config[agent_key]
        agent_name = agent.get("name", "unknown")

        # Create comprehensive task file
        task_file = Path(output_dir) / f"{agent_name}_tasks.md"

        with open(task_file, "w") as f:
            # Header
            f.write(f"# Tasks for {agent_name}\n\n")
            f.write(f"**Role**: {agent.get('role', 'Not specified')}\n")
            f.write(f"**Description**: {agent.get('description', 'Not specified')}\n")
            f.write(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Core Mission
            f.write("## 🎯 Core Mission\n")
            f.write(agent.get("core_mission", "No mission defined").strip() + "\n\n")

            # Personality Traits
            if "personality" in agent:
                f.write("## 🎭 Personality & Approach\n")
                for trait in agent["personality"]:
                    f.write(f"- {trait}\n")
                f.write("\n")

            # Technical Expertise
            if "technical_expertise" in agent:
                f.write("## 💻 Technical Expertise\n")
                for skill in agent["technical_expertise"]:
                    f.write(f"- {skill}\n")
                f.write("\n")

            # Current Focus Areas
            if "current_focus_areas" in agent:
                f.write("## 📌 Current Focus Areas\n")
                focus = agent["current_focus_areas"]

                for area, items in focus.items():
                    f.write(f"\n### {area.replace('_', ' ').title()}\n")

                    if isinstance(items, list):
                        for item in items:
                            f.write(f"- [ ] {item}\n")
                    elif isinstance(items, dict):
                        for key, value in items.items():
                            f.write(f"- [ ] **{key}**: {value}\n")
                f.write("\n")

            # Special sections for specific agents
            if agent_key == "agent_3" and "legacy_assessment_strategy" in agent:
                f.write("## 🔧 Legacy Assessment Strategy\n")
                strategy = agent["legacy_assessment_strategy"]
                for section, items in strategy.items():
                    f.write(f"\n### {section.replace('_', ' ').title()}\n")
                    if isinstance(items, list):
                        for item in items:
                            f.write(f"- {item}\n")
                    elif isinstance(items, dict):
                        for key, value in items.items():
                            f.write(f"- **{key}**: {value}\n")
                f.write("\n")

            if agent_key == "agent_4" and "architecture_principles" in agent:
                f.write("## 🏗️ Architecture Principles\n")
                for principle in agent["architecture_principles"]:
                    f.write(f"- {principle}\n")
                f.write("\n")

            if agent_key == "agent_5" and "user_experience_principles" in agent:
                f.write("## 🎨 User Experience Principles\n")
                for principle in agent["user_experience_principles"]:
                    f.write(f"- {principle}\n")
                f.write("\n")

                if "demo_scenario_focus" in agent:
                    f.write("## 🎬 Demo Scenario Focus\n")
                    f.write(agent["demo_scenario_focus"].strip() + "\n\n")

            if agent_key == "agent_6":
                if "repository_organization" in agent:
                    f.write("## 📁 Repository Organization\n")
                    repo_org = agent["repository_organization"]

                    if "structure_design" in repo_org:
                        f.write("\n### Structure Design\n")
                        for folder, desc in repo_org["structure_design"].items():
                            f.write(f"- **{folder}** {desc}\n")

                    if "legacy_handling" in repo_org:
                        f.write("\n### Legacy Handling\n")
                        for item in repo_org["legacy_handling"]:
                            f.write(f"- [ ] {item}\n")
                    f.write("\n")

                if "quality_metrics" in agent:
                    f.write("## 📊 Quality Metrics\n")
                    for metric in agent["quality_metrics"]:
                        f.write(f"- [ ] {metric}\n")
                    f.write("\n")

            # Collaboration Patterns
            if "collaboration_patterns" in agent:
                f.write("## 🤝 Collaboration Patterns\n")
                collab = agent["collaboration_patterns"]

                for partner, items in collab.items():
                    f.write(f"\n### {partner.replace('_', ' ').title()}\n")
                    if isinstance(items, list):
                        for item in items:
                            f.write(f"- {item}\n")
                    elif isinstance(items, dict):
                        for key, value in items.items():
                            f.write(f"- **{key}**: {value}\n")
                f.write("\n")

            # Deliverables
            if "deliverables" in agent:
                f.write("## ✅ Deliverables\n")
                for deliverable in agent["deliverables"]:
                    f.write(f"- [ ] {deliverable}\n")
                f.write("\n")

            # Add task tracking section
            f.write("## 📈 Progress Tracking\n\n")
            f.write("### Status Legend\n")
            f.write("- [ ] Not Started\n")
            f.write("- [🔄] In Progress\n")
            f.write("- [✅] Completed\n")
            f.write("- [⚠️] Blocked\n\n")

            f.write("### Notes\n")
            f.write("_Add implementation notes, blockers, and decisions here_\n\n")

            f.write("---\n")
            f.write(f"*Last Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}*\n")

        agents_processed.append({"agent": agent_key, "name": agent_name, "file": str(task_file)})
        print(f"✅ Created comprehensive task file: {task_file}")

    # Also extract coordination framework tasks
    coord_file = Path(output_dir) / "coordination_framework_tasks.md"
    with open(coord_file, "w") as f:
        f.write("# 🎭 Coordination Framework Tasks\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if "coordination_framework" in config:
            coord = config["coordination_framework"]

            # Interface Contracts
            if "interface_contracts" in coord:
                f.write("## 📜 Interface Contracts\n")
                for interface, items in coord["interface_contracts"].items():
                    f.write(f"\n### {interface.replace('_', ' ').title()}\n")
                    for item in items:
                        f.write(f"- [ ] Implement: {item}\n")
                f.write("\n")

            # Success Criteria
            if "success_criteria" in coord:
                f.write("## 🎯 Success Criteria\n")
                for category, items in coord["success_criteria"].items():
                    f.write(f"\n### {category.replace('_', ' ').title()}\n")
                    for item in items:
                        f.write(f"- [ ] {item}\n")
                f.write("\n")

        # Global Schemas
        if "global_schemas" in config:
            f.write("## 🌐 Global Schemas Implementation\n")
            schemas = config["global_schemas"]

            for schema_name, fields in schemas.items():
                f.write(f"\n### {schema_name.replace('_', ' ').title()}\n")
                f.write("```yaml\n")
                for field, desc in fields.items():
                    f.write(f"{field}: {desc}\n")
                f.write("```\n")
                f.write(f"- [ ] Implement {schema_name}\n")
                f.write(f"- [ ] Add validation for {schema_name}\n")
                f.write(f"- [ ] Create tests for {schema_name}\n")
            f.write("\n")

        # Phase 1 Completion
        if "phase_1_completion_definition" in config:
            f.write("## 🏁 Phase 1 Completion Definition\n")
            f.write(config["phase_1_completion_definition"].strip() + "\n\n")

        f.write("---\n")
        f.write(f"*Last Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}*\n")

    print(f"✅ Created coordination framework tasks: {coord_file}")

    # Create a summary JSON file for tracking
    summary_file = Path(output_dir) / "task_extraction_summary.json"
    with open(summary_file, "w") as f:
        json.dump(
            {
                "extraction_date": datetime.now(timezone.utc).isoformat(),
                "source_file": config_file,
                "agents_processed": agents_processed,
                "coordination_file": str(coord_file),
                "total_agents": len(agents_processed),
            },
            f,
            indent=2,
        )

    print(f"\n📊 Task Extraction Summary saved to: {summary_file}")

    return agents_processed


if __name__ == "__main__":
    print("🚀 Extracting comprehensive tasks from Claude_6.yml...")
    print("=" * 50)

    agents = extract_agent_tasks()

    print("\n" + "=" * 50)
    print("✨ Task extraction complete!")
    print(f"📁 Tasks created for {len(agents)} agents")
    print("\n📋 Files created:")
    for agent_info in agents:
        print(f"  - {agent_info['name']}: {agent_info['file']}")
    print("  - coordination_framework_tasks.md")
    print("\n🎯 Agents can now check their tasks in CLAUDE_ARMY/tasks/")
