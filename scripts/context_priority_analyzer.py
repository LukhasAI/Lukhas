#!/usr/bin/env python3
"""
LUKHAS Context File Priority Analyzer
Analyzes and prioritizes context file updates based on criticality
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
import json


class ContextPriorityAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)

        # Define priority levels based on architectural importance
        self.priority_mapping = {
            # CRITICAL - Core system understanding
            "claude.me": 100,
            "lukhas_context.md": 100,

            # HIGH - Lane definitions
            "lukhas/claude.me": 90,
            "lukhas/lukhas_context.md": 90,
            "candidate/claude.me": 90,
            "candidate/lukhas_context.md": 90,
            "candidate/core/claude.me": 90,
            "candidate/core/lukhas_context.md": 90,

            # HIGH - Consciousness core
            "candidate/consciousness/claude.me": 85,
            "candidate/consciousness/lukhas_context.md": 85,
            "lukhas/consciousness/claude.me": 85,
            "lukhas/consciousness/lukhas_context.md": 85,
            "candidate/aka_qualia/claude.me": 85,
            "candidate/aka_qualia/lukhas_context.md": 85,

            # MEDIUM-HIGH - Core components
            "candidate/core/orchestration/claude.me": 80,
            "candidate/core/orchestration/lukhas_context.md": 80,
            "candidate/core/interfaces/claude.me": 75,
            "candidate/core/interfaces/lukhas_context.md": 75,
            "candidate/core/symbolic/claude.me": 75,
            "candidate/core/symbolic/lukhas_context.md": 75,

            # MEDIUM - Constellation Framework components
            "lukhas/identity/claude.me": 70,
            "lukhas/identity/lukhas_context.md": 70,
            "lukhas/memory/claude.me": 70,
            "lukhas/memory/lukhas_context.md": 70,
            "lukhas/governance/claude.me": 70,
            "lukhas/governance/lukhas_context.md": 70,

            # MEDIUM-LOW - Development components
            "candidate/identity/claude.me": 60,
            "candidate/memory/claude.me": 60,
            "candidate/governance/claude.me": 60,
            "candidate/bridge/claude.me": 60,

            # LOW - Specialized components
            "matriz/claude.me": 50,
            "products/claude.me": 50,
            "ethics/claude.me": 50,
            "quantum/claude.me": 40,
            "tools/claude.me": 40,
            "bio/claude.me": 40
        }

    def calculate_file_priority(self, file_path: Path) -> int:
        """Calculate priority score for a file"""
        relative_path = str(file_path.relative_to(self.root_path))

        # Check exact matches first
        if relative_path in self.priority_mapping:
            return self.priority_mapping[relative_path]

        # Check pattern matches
        score = 30  # Default score

        # Boost for critical paths
        if file_path.name in ["claude.me", "lukhas_context.md"]:
            if "lukhas/" in relative_path or "candidate/" in relative_path:
                score += 40
            elif "consciousness" in relative_path:
                score += 35
            elif "core/" in relative_path:
                score += 30
            else:
                score += 20

        # Boost for depth (shallower = more important)
        depth = len(file_path.parts) - len(self.root_path.parts)
        if depth <= 2:
            score += 20
        elif depth <= 3:
            score += 10

        return min(score, 100)

    def analyze_update_impact(self, file_path: Path) -> Dict:
        """Analyze the impact of updating a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""

        impact = {
            "file_size": len(content),
            "mentions_consciousness": "consciousness" in content.lower(),
            "mentions_trinity": "constellation" in content.lower(),
            "mentions_candidate": "candidate" in content,
            "mentions_lukhas": "lukhas" in content,
            "has_architecture_section": "architecture" in content.lower(),
            "has_overview_section": "overview" in content.lower(),
            "estimated_ai_reads": 0  # How often AIs might read this
        }

        # Estimate AI read frequency based on location
        relative_path = str(file_path.relative_to(self.root_path))
        if relative_path in ["claude.me", "lukhas_context.md"]:
            impact["estimated_ai_reads"] = 100
        elif "/claude.me" in relative_path or "/lukhas_context.md" in relative_path:
            depth = len(file_path.parts) - len(self.root_path.parts)
            impact["estimated_ai_reads"] = max(10, 80 - (depth * 15))

        return impact

    def create_update_plan(self) -> Dict:
        """Create prioritized update plan"""
        context_files = []

        # Find all context files
        for claude_file in self.root_path.glob("**/claude.me"):
            context_files.append(claude_file)
        for context_file in self.root_path.glob("**/lukhas_context.md"):
            context_files.append(context_file)

        # Analyze each file
        file_analysis = []
        for file_path in context_files:
            priority = self.calculate_file_priority(file_path)
            impact = self.analyze_update_impact(file_path)

            file_analysis.append({
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(self.root_path)),
                "priority_score": priority,
                "impact_analysis": impact,
                "update_urgency": self.calculate_urgency(priority, impact)
            })

        # Sort by priority
        file_analysis.sort(key=lambda x: (x["priority_score"], x["impact_analysis"]["estimated_ai_reads"]), reverse=True)

        # Group into batches
        batches = {
            "critical_immediate": [f for f in file_analysis if f["priority_score"] >= 90],
            "high_priority": [f for f in file_analysis if 75 <= f["priority_score"] < 90],
            "medium_priority": [f for f in file_analysis if 60 <= f["priority_score"] < 75],
            "low_priority": [f for f in file_analysis if f["priority_score"] < 60]
        }

        return {
            "total_files": len(file_analysis),
            "batches": batches,
            "recommended_sequence": self.create_update_sequence(batches)
        }

    def calculate_urgency(self, priority: int, impact: Dict) -> str:
        """Calculate update urgency"""
        if priority >= 90 and impact["estimated_ai_reads"] > 50:
            return "IMMEDIATE"
        elif priority >= 80:
            return "HIGH"
        elif priority >= 60:
            return "MEDIUM"
        else:
            return "LOW"

    def create_update_sequence(self, batches: Dict) -> List[Dict]:
        """Create recommended update sequence"""
        sequence = []

        # Phase 1: Critical files first
        if batches["critical_immediate"]:
            sequence.append({
                "phase": "1_critical",
                "description": "Update core system context files",
                "files": [f["relative_path"] for f in batches["critical_immediate"]],
                "estimated_time": "30-45 minutes",
                "risk": "HIGH - These define core system understanding"
            })

        # Phase 2: High priority lane definitions
        if batches["high_priority"]:
            sequence.append({
                "phase": "2_lanes",
                "description": "Update lane-specific context files",
                "files": [f["relative_path"] for f in batches["high_priority"]],
                "estimated_time": "45-60 minutes",
                "risk": "MEDIUM - Lane understanding critical for development"
            })

        # Phase 3: Medium priority components
        if batches["medium_priority"]:
            sequence.append({
                "phase": "3_components",
                "description": "Update component-specific context files",
                "files": [f["relative_path"] for f in batches["medium_priority"]],
                "estimated_time": "30-45 minutes",
                "risk": "LOW - Component-specific documentation"
            })

        # Phase 4: Remaining files
        if batches["low_priority"]:
            sequence.append({
                "phase": "4_remaining",
                "description": "Update remaining context files",
                "files": [f["relative_path"] for f in batches["low_priority"]],
                "estimated_time": "60+ minutes",
                "risk": "MINIMAL - Nice to have updates"
            })

        return sequence


if __name__ == "__main__":
    analyzer = ContextPriorityAnalyzer("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    print("=== LUKHAS Context Update Priority Analysis ===\\n")

    plan = analyzer.create_update_plan()

    print(f"Total context files: {plan['total_files']}\\n")

    for batch_name, files in plan['batches'].items():
        if files:
            print(f"{batch_name.upper().replace('_', ' ')}: {len(files)} files")
            for file_info in files[:3]:  # Show first 3
                print(f"  - {file_info['relative_path']} (priority: {file_info['priority_score']})")
            if len(files) > 3:
                print(f"  - ... and {len(files)-3} more")
            print()

    print("RECOMMENDED UPDATE SEQUENCE:")
    for phase in plan['recommended_sequence']:
        print(f"\\n{phase['phase'].upper()}: {phase['description']}")
        print(f"Time: {phase['estimated_time']}")
        print(f"Risk: {phase['risk']}")
        print(f"Files ({len(phase['files'])}):")
        for file_path in phase['files'][:5]:  # Show first 5
            print(f"  - {file_path}")
        if len(phase['files']) > 5:
            print(f"  - ... and {len(phase['files'])-5} more")

    # Save detailed plan
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/temp_update_priority_plan.json", "w") as f:
        json.dump(plan, f, indent=2)