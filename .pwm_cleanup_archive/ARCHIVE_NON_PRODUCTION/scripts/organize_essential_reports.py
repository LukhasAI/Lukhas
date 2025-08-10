#!/usr/bin/env python3
"""
Organize Essential Reports for Agents
Keep only the critical reports and move/remove obsolete ones
"""

import os
import shutil
from datetime import datetime


def organize_essential_reports():
    """Organize and keep only essential reports"""

    # Essential reports to keep (these are what agents need)
    essential_reports = {
        # Core integration tasks - THE MAIN DELIVERABLE
        "complete_integration_tasks_20250730_203853.json": {
            "new_name": "ESSENTIAL_integration_tasks.json",
            "description": "600 core files with line-by-line integration tasks",
        },
        "complete_integration_tasks_20250730_203853.md": {
            "new_name": "ESSENTIAL_integration_tasks.md",
            "description": "Human-readable integration tasks summary",
        },
        # Full connection analysis - REFERENCE DATA
        "full_core_connection_report_20250730_203627.json": {
            "new_name": "ESSENTIAL_connection_analysis.json",
            "description": "Complete analysis of 600 files with connection opportunities",
        },
        # Orchestrator consolidation results - COMPLETED WORK
        "analysis-tools/ORCHESTRATOR_CONSOLIDATION_PROGRESS_REPORT.md": {
            "new_name": "ESSENTIAL_orchestrator_consolidation_complete.md",
            "description": "Orchestrator consolidation results (82→11 files, 86% reduction)",
        },
        # Original unused files data - SOURCE DATA
        "scripts/unused_files_report.json": {
            "new_name": "ESSENTIAL_unused_files_source.json",
            "description": "Original unused files analysis (1,332 total unused files)",
        },
    }

    # Create essential reports directory
    os.makedirs("ESSENTIAL_REPORTS", exist_ok=True)

    print("📁 Organizing essential reports...")

    # Copy essential reports to new directory
    for old_path, info in essential_reports.items():
        if os.path.exists(old_path):
            new_path = f"ESSENTIAL_REPORTS/{info['new_name']}"
            shutil.copy2(old_path, new_path)
            print(f"✅ Kept: {info['new_name']} - {info['description']}")
        else:
            print(f"⚠️  Missing: {old_path}")

    # Create README for agents
    create_agent_readme()

    # List reports to archive/remove
    obsolete_reports = [
        "core_unused_connection_report_20250730_203414.json",
        "core_orchestration_consolidation_report_20250730_202214.json",
        "core_orchestration_consolidation_report_20250730_202227.json",
        "functional_orchestrator_analysis.json",
        "orchestrator_analysis_report.json",
        "orchestrator_archive_report_20250730_201931.json",
    ]

    print("\n📦 Moving obsolete reports to archive...")
    os.makedirs("archived/obsolete_reports", exist_ok=True)

    for report in obsolete_reports:
        if os.path.exists(report):
            shutil.move(report, f"archived/obsolete_reports/{report}")
            print(f"📦 Archived: {report}")

    print("\n✅ Essential reports organized!")
    return True


def create_agent_readme():
    """Create README for agents explaining the essential reports"""

    readme_content = f"""# 🎯 ESSENTIAL REPORTS FOR AGENTS

**Generated:** {datetime.now().isoformat()}

This directory contains the **5 essential reports** needed for system integration work. All other reports have been archived to avoid confusion.

---

## 📋 ESSENTIAL REPORTS OVERVIEW

### 1. **INTEGRATION TASKS** (PRIMARY DELIVERABLE)
- **`ESSENTIAL_integration_tasks.json`** - Complete integration tasks for 600 core files
- **`ESSENTIAL_integration_tasks.md`** - Human-readable integration tasks summary

**What this contains:**
- **600 core unused files** with specific integration instructions
- **Line-by-line integration steps** for each file
- **Connection points, testing steps, completion criteria**
- **Organized by category and priority**

**Agent Usage:**
```bash
# View integration tasks
cat ESSENTIAL_REPORTS/ESSENTIAL_integration_tasks.md

# Get specific file integration task
python3 -c "
import json
with open('ESSENTIAL_REPORTS/ESSENTIAL_integration_tasks.json', 'r') as f:
    tasks = json.load(f)

# Find specific file task
file_path = 'memory/systems/memory_planning.py'
for task in tasks['all_integration_tasks']:
    if task['file_path'] == file_path:
        print(f'Integration steps for {{file_path}}:')
        for step in task['integration_steps']:
            print(f'  - {{step}}')
        break
"
```

### 2. **CONNECTION ANALYSIS** (REFERENCE DATA)
- **`ESSENTIAL_connection_analysis.json`** - Complete analysis of 600 files

**What this contains:**
- **Detailed analysis** of each file (imports, classes, functions)
- **Integration opportunities** for each file
- **Priority scores** and categorization
- **Category summaries** with integration hubs

### 3. **ORCHESTRATOR CONSOLIDATION** (COMPLETED WORK)
- **`ESSENTIAL_orchestrator_consolidation_complete.md`** - Consolidation results

**What this contains:**
- **Results:** 82 orchestrator files → 11 files (86% reduction)
- **What was consolidated:** Core, bio, memory, brain, specialized systems
- **Remaining files:** List of 11 orchestrator files kept
- **Impact:** Dramatically cleaner orchestrator architecture

### 4. **UNUSED FILES SOURCE** (ORIGINAL DATA)
- **`ESSENTIAL_unused_files_source.json`** - Original unused files data

**What this contains:**
- **1,332 total unused files** from original analysis
- **Categorized breakdown:** core_modules (954), tests (24), tools (19), etc.
- **Source data** for integration task generation

---

## 🎯 AGENT WORKFLOW

### **For Integration Tasks:**
1. Start with **`ESSENTIAL_integration_tasks.md`** for overview
2. Use **`ESSENTIAL_integration_tasks.json`** for specific file tasks
3. Focus on **priority files first** (scores 50+)
4. Work **category by category** for systematic integration

### **Priority Integration Order:**
1. **🔥 High Priority Categories** (351 files):
   - Memory Systems (101 files)
   - Core Systems (64 files)
   - Reasoning (60 files)
   - Creativity (52 files)
   - Learning (35 files)
   - Consciousness (21 files)
   - Bridge Integration (18 files)

2. **⚡ Medium Priority Categories** (189 files):
   - Identity (107 files)
   - Quantum (39 files)
   - Voice (23 files)
   - API Services (8 files)
   - Bio Systems (7 files)
   - Emotion (5 files)

### **Example Integration Task:**
```json
{{
  "file_path": "memory/systems/memory_planning.py",
  "category": "memory_systems",
  "priority_score": 83.0,
  "integration_steps": [
    "1. Review memory/systems/memory_planning.py structure and functionality",
    "2. Identify integration points with memory/core/unified_memory_orchestrator.py",
    "3. Create integration wrapper/adapter if needed",
    "4. Add file to system initialization sequence",
    "5. Update service registry with new component"
  ],
  "connection_points": [
    "Class: LiveRange",
    "Class: LiveRanges",
    "Class: AllocationTreeNode"
  ],
  "testing_steps": [
    "1. Verify file imports successfully",
    "2. Test basic functionality works",
    "3. Verify integration with hub system"
  ],
  "completion_criteria": [
    "✓ memory/systems/memory_planning.py successfully imported",
    "✓ Component registered with memory/core/unified_memory_orchestrator.py",
    "✓ All tests pass"
  ]
}}
```

---

## 📊 INTEGRATION STATUS

**Current State:**
- **✅ Orchestrator Consolidation:** COMPLETE (82→11 files, 86% reduction)
- **🔄 Core File Integration:** READY (600 files with detailed tasks)
- **📋 Integration Tasks:** GENERATED (line-by-line instructions)

**Next Steps:**
1. Agents work through integration tasks systematically
2. Start with highest priority files (90+ scores)
3. Focus on high-impact categories first
4. Test each integration thoroughly
5. Monitor system health during integration

**Estimated Timeline:** 4-6 weeks for complete integration of all 600 files

---

## 🚫 ARCHIVED REPORTS

All other reports have been moved to `archived/obsolete_reports/` to avoid confusion:
- Intermediate analysis reports
- Draft consolidation reports
- Development/debug reports
- Duplicate reports

**Only use the 5 ESSENTIAL reports in this directory.**

---

**Status:** Ready for systematic integration execution ✅
"""

    with open("ESSENTIAL_REPORTS/README_FOR_AGENTS.md", "w") as f:
        f.write(readme_content)

    print("📄 Created README_FOR_AGENTS.md")


def main():
    organize_essential_reports()


if __name__ == "__main__":
    main()
