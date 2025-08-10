#!/usr/bin/env python3
"""
Complete Integration Tasks Generator
Create line-by-line integration tasks for ALL 600 unused core files
"""

import json
from datetime import datetime
from typing import Dict, List


def generate_complete_integration_tasks():
    """Generate detailed integration tasks for all files"""

    # Load the full connection report
    try:
        with open("full_core_connection_report_20250730_203627.json") as f:
            report = json.load(f)
    except FileNotFoundError:
        print(
            "❌ Full connection report not found. Run create_full_core_connection_report.py first."
        )
        return

    file_analyses = report["file_analyses"]
    category_summary = report["category_summary"]

    print(f"🔍 Generating integration tasks for {len(file_analyses)} files...")

    # Create comprehensive integration task list
    integration_tasks = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_files": len(file_analyses),
        "categories": len(category_summary),
        "tasks_by_category": {},
        "priority_tasks": [],
        "all_integration_tasks": [],
    }

    # Process each category
    for category, cat_info in category_summary.items():
        if category == "uncategorized":
            continue

        category_tasks = {
            "category": category,
            "priority": cat_info["priority"],
            "total_files": cat_info["total_files"],
            "integration_hub": get_integration_hub(category),
            "setup_tasks": get_category_setup_tasks(category),
            "file_tasks": [],
        }

        # Process each file in the category
        category_files = cat_info["files"]
        for file_path in category_files:
            file_analysis = file_analyses.get(file_path, {})

            if "error" in file_analysis:
                continue

            # Create specific integration task for this file
            file_task = create_file_integration_task(file_path, file_analysis, category)
            category_tasks["file_tasks"].append(file_task)

            # Add to overall task list
            integration_tasks["all_integration_tasks"].append(file_task)

            # Add to priority tasks if high priority
            if file_analysis.get("priority_score", 0) >= 50:
                integration_tasks["priority_tasks"].append(file_task)

        integration_tasks["tasks_by_category"][category] = category_tasks

    # Sort priority tasks by score
    integration_tasks["priority_tasks"].sort(
        key=lambda x: x["priority_score"], reverse=True
    )

    # Save comprehensive task list
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"complete_integration_tasks_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(integration_tasks, f, indent=2)

    print(f"✅ Complete integration tasks saved to: {filename}")

    # Generate markdown summary
    generate_markdown_summary(integration_tasks, filename.replace(".json", ".md"))

    return integration_tasks


def get_integration_hub(category: str) -> str:
    """Get the main integration hub for a category"""
    hubs = {
        "memory_systems": "memory/core/unified_memory_orchestrator.py",
        "consciousness": "consciousness/consciousness_hub.py",
        "reasoning": "reasoning/reasoning_engine.py",
        "creativity": "creativity/creative_engine.py",
        "learning": "learning/learning_hub.py",
        "identity": "identity/identity_hub.py",
        "quantum": "quantum/system_orchestrator.py",
        "bio_systems": "quantum/bio_multi_orchestrator.py",
        "voice": "voice/speech_engine.py",
        "emotion": "emotion/models.py",
        "api_services": "api/services.py",
        "bridge_integration": "bridge/message_bus.py",
        "core_systems": "core/core_hub.py",
    }
    return hubs.get(category, "core/core_hub.py")


def get_category_setup_tasks(category: str) -> List[str]:
    """Get setup tasks needed for a category"""
    setup_tasks = {
        "memory_systems": [
            "Ensure unified_memory_orchestrator.py is running",
            "Initialize memory service registry",
            "Set up memory persistence layer",
            "Configure memory event bus connections",
        ],
        "consciousness": [
            "Initialize consciousness_hub.py",
            "Set up awareness system registry",
            "Configure cognitive architecture controller",
            "Establish consciousness event loops",
        ],
        "reasoning": [
            "Initialize reasoning_engine.py",
            "Set up symbolic processing pipeline",
            "Configure logical inference system",
            "Establish reasoning event handlers",
        ],
        "creativity": [
            "Initialize creative_engine.py",
            "Set up dream system connections",
            "Configure personality system integration",
            "Establish creative expression pipelines",
        ],
        "learning": [
            "Initialize learning_hub.py",
            "Set up adaptive learning registry",
            "Configure meta-learning systems",
            "Establish learning feedback loops",
        ],
        "identity": [
            "Initialize identity_hub.py",
            "Set up authentication system",
            "Configure QR glyph system",
            "Establish identity validation pipelines",
        ],
        "bridge_integration": [
            "Initialize message_bus.py",
            "Set up integration hub registry",
            "Configure cross-system bridges",
            "Establish message routing",
        ],
        "core_systems": [
            "Initialize core_hub.py",
            "Set up system registry",
            "Configure core service discovery",
            "Establish system health monitoring",
        ],
    }
    return setup_tasks.get(
        category, ["Initialize category hub", "Set up service registry"]
    )


def create_file_integration_task(file_path: str, analysis: Dict, category: str) -> Dict:
    """Create detailed integration task for a specific file"""

    task = {
        "file_path": file_path,
        "category": category,
        "priority_score": analysis.get("priority_score", 0),
        "size_kb": analysis.get("size_kb", 0),
        "integration_steps": [],
        "connection_points": [],
        "testing_steps": [],
        "completion_criteria": [],
    }

    # Basic integration steps
    task["integration_steps"].extend(
        [
            f"1. Review {file_path} structure and functionality",
            f"2. Identify integration points with {get_integration_hub(category)}",
            "3. Create integration wrapper/adapter if needed",
            "4. Add file to system initialization sequence",
            "5. Update service registry with new component",
            "6. Configure any required dependencies",
        ]
    )

    # Add specific steps based on file analysis
    classes = analysis.get("classes", [])
    functions = analysis.get("functions", [])
    async_functions = analysis.get("async_functions", [])

    if classes:
        task["integration_steps"].append(
            f"7. Register classes: {', '.join(classes[:3])}"
        )
        task["connection_points"].extend([f"Class: {cls}" for cls in classes[:5]])

    if functions:
        task["integration_steps"].append(
            f"8. Expose key functions: {', '.join(functions[:3])}"
        )
        task["connection_points"].extend(
            [f"Function: {func}" for func in functions[:5]]
        )

    if async_functions:
        task["integration_steps"].append("9. Configure async event loop integration")

    # Add connection recommendations
    recommendations = analysis.get("connection_recommendations", [])
    for rec in recommendations[:3]:
        task["connection_points"].append(f"Recommendation: {rec}")

    # Integration opportunities
    opportunities = analysis.get("integration_opportunities", [])
    for opp in opportunities[:3]:
        task["integration_steps"].append(f"• {opp}")

    # Testing steps
    task["testing_steps"] = [
        "1. Verify file imports successfully",
        "2. Test basic functionality works",
        "3. Verify integration with hub system",
        "4. Check no conflicts with existing components",
        "5. Validate error handling and edge cases",
    ]

    # Completion criteria
    task["completion_criteria"] = [
        f"✓ {file_path} successfully imported and initialized",
        f"✓ Component registered with {get_integration_hub(category)}",
        "✓ All tests pass",
        "✓ No integration conflicts detected",
        "✓ Component appears in system health check",
    ]

    return task


def generate_markdown_summary(tasks: Dict, filename: str):
    """Generate markdown summary of all integration tasks"""

    with open(filename, "w") as f:
        f.write(
            f"""# Complete Integration Tasks Report

**Generated:** {tasks['generation_timestamp']}
**Total Files:** {tasks['total_files']}
**Categories:** {tasks['categories']}

---

## 🎯 Priority Tasks ({len(tasks['priority_tasks'])} files)

"""
        )

        # Write priority tasks
        for i, task in enumerate(tasks["priority_tasks"][:20], 1):
            f.write(
                f"""### {i}. {task['file_path']}
- **Category:** {task['category']}
- **Priority Score:** {task['priority_score']}
- **Size:** {task['size_kb']} KB

**Integration Steps:**
"""
            )
            for step in task["integration_steps"][:5]:
                f.write(f"- {step}\n")

            f.write(
                """
**Connection Points:**
"""
            )
            for point in task["connection_points"][:3]:
                f.write(f"- {point}\n")
            f.write("\n")

        f.write("\n---\n\n## 📂 Tasks by Category\n\n")

        # Write tasks by category
        for category, cat_tasks in tasks["tasks_by_category"].items():
            f.write(
                f"""### {category.title().replace('_', ' ')} ({cat_tasks['total_files']} files)

**Priority:** {cat_tasks['priority']}
**Integration Hub:** `{cat_tasks['integration_hub']}`

**Setup Tasks:**
"""
            )
            for setup_task in cat_tasks["setup_tasks"]:
                f.write(f"1. {setup_task}\n")

            f.write(f"\n**Files to Integrate ({len(cat_tasks['file_tasks'])}):**\n")

            for task in cat_tasks["file_tasks"][:10]:  # Show first 10 files
                f.write(f"- `{task['file_path']}` (score: {task['priority_score']})\n")

            if len(cat_tasks["file_tasks"]) > 10:
                f.write(f"- ... and {len(cat_tasks['file_tasks']) - 10} more files\n")

            f.write("\n")

        f.write(
            f"""
---

## 📋 Integration Summary

**Total Integration Tasks:** {len(tasks['all_integration_tasks'])}

**By Priority:**
- High Priority (50+): {len([t for t in tasks['all_integration_tasks'] if t['priority_score'] >= 50])} files
- Medium Priority (30-49): {len([t for t in tasks['all_integration_tasks'] if 30 <= t['priority_score'] < 50])} files
- Low Priority (15-29): {len([t for t in tasks['all_integration_tasks'] if 15 <= t['priority_score'] < 30])} files
- Very Low (<15): {len([t for t in tasks['all_integration_tasks'] if t['priority_score'] < 15])} files

**Next Steps:**
1. Start with Priority Tasks (highest impact)
2. Set up category integration hubs
3. Process files systematically by category
4. Test each integration thoroughly
5. Monitor system health after each integration

**Estimated Timeline:** 4-6 weeks for complete integration of all 600 files
"""
        )

    print(f"📄 Markdown summary saved to: {filename}")


def main():
    tasks = generate_complete_integration_tasks()

    if tasks:
        print("\n🎉 COMPLETE INTEGRATION TASKS GENERATED!")
        print("📊 Summary:")
        print(f"   Total files: {tasks['total_files']}")
        print(f"   Categories: {tasks['categories']}")
        print(f"   Priority tasks: {len(tasks['priority_tasks'])}")
        print(f"   Total integration tasks: {len(tasks['all_integration_tasks'])}")

        print("\n📂 Tasks by Category:")
        for category, cat_tasks in sorted(
            tasks["tasks_by_category"].items(),
            key=lambda x: x[1]["total_files"],
            reverse=True,
        ):
            priority_symbol = "🔥" if cat_tasks["priority"] == "high" else "⚡"
            print(
                f"   {priority_symbol} {category:20} {cat_tasks['total_files']:3} files"
            )

        print("\n✅ Ready for systematic integration of ALL 600 core files!")


if __name__ == "__main__":
    main()
