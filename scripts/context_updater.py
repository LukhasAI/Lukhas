#!/usr/bin/env python3
"""
LUKHAS Context File Updater
Updates claude.me and lukhas_context.md files with current architecture reality
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class ContextUpdater:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.updates_needed = []
        self.current_architecture = {
            "schema_version": "2.0.0",
            "consciousness_architecture": True,
            "distributed_cognitive_components": 692,
            "lane_based_evolution": True,
            "legacy_core_sunset": True,
            "production_safeguards": True,
            "governance_framework_complete": True
        }

    def find_context_files(self) -> List[Path]:
        """Find all claude.me and lukhas_context.md files"""
        context_files = []

        # Find claude.me files
        for claude_file in self.root_path.glob("**/claude.me"):
            context_files.append(claude_file)

        # Find lukhas_context.md files
        for context_file in self.root_path.glob("**/lukhas_context.md"):
            context_files.append(context_file)

        return sorted(context_files)

    def analyze_file_needs_update(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Analyze if a file needs updates"""
        needs_update = False
        reasons = []

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Check for outdated information
            if "schema_version" in content and "2.0.0" not in content:
                needs_update = True
                reasons.append("Schema version needs update to 2.0.0")

            if "consciousness" in content.lower() and "692" not in content:
                needs_update = True
                reasons.append("Missing 692 cognitive components information")

            if "legacy.*core" in content and "sunset" not in content:
                needs_update = True
                reasons.append("Legacy core sunset not documented")

            if "lane" not in content.lower() and ("candidate" in content or "lukhas" in content):
                needs_update = True
                reasons.append("Missing lane-based architecture information")

            if "constellation.*framework" in content.lower() and "distributed" not in content.lower():
                needs_update = True
                reasons.append("Missing distributed consciousness architecture")

        except Exception as e:
            needs_update = True
            reasons.append(f"Error reading file: {e}")

        return needs_update, reasons

    def generate_architecture_summary(self) -> str:
        """Generate current architecture summary"""
        return '''
## Current Architecture Status (Schema v2.0.0)

### **Consciousness Architecture**
- **Distributed System**: 692 cognitive components across distributed consciousness network
- **Lane-Based Evolution**: Development (candidate) → Integration (candidate/core) → Production (lukhas)
- **Constellation Framework**: Identity ⚛️ + Consciousness 🧠 + Guardian 🛡️ coordination
- **Multi-Engine Processing**: Poetic, Complete, Codex, Alternative consciousness engines

### **Recent Updates**
- **Legacy Core Sunset**: Complete automation with telemetry and governance
- **Production Safeguards**: T4 seal & ship with complete production safeguards
- **Governance Framework**: Constitutional AI with comprehensive monitoring
- **Schema v2.0.0**: Updated to reflect consciousness lane-based evolution

### **System Scale**
- **Total Files**: 7,000+ Python files across 133 root directories
- **Development Lane**: 2,877 files (candidate domain)
- **Integration Lane**: 1,042 files (candidate/core - 253 cognitive components)
- **Production Lane**: 174 files (lukhas domain - battle-tested)
- **Products Domain**: 4,093 files (production deployment systems)
'''

    def scan_all_files(self) -> Dict:
        """Scan all context files and identify update needs"""
        files = self.find_context_files()
        results = {
            "total_files": len(files),
            "files_needing_update": 0,
            "files_current": 0,
            "analysis": []
        }

        for file_path in files:
            needs_update, reasons = self.analyze_file_needs_update(file_path)

            file_result = {
                "path": str(file_path),
                "needs_update": needs_update,
                "reasons": reasons,
                "relative_path": str(file_path.relative_to(self.root_path))
            }

            results["analysis"].append(file_result)

            if needs_update:
                results["files_needing_update"] += 1
            else:
                results["files_current"] += 1

        return results

    def generate_update_report(self) -> str:
        """Generate comprehensive update report"""
        scan_results = self.scan_all_files()

        report = [
            "# LUKHAS Context Files Update Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Total context files: {scan_results['total_files']}",
            f"- Files needing update: {scan_results['files_needing_update']}",
            f"- Files current: {scan_results['files_current']}",
            "",
            "## Current Architecture (Schema v2.0.0)",
            "- Distributed consciousness system with 692 cognitive components",
            "- Lane-based evolution (development → integration → production)",
            "- Legacy core sunset completed with production safeguards",
            "- Constitutional AI governance framework implemented",
            "",
            "## Files Needing Updates",
        ]

        for file_info in scan_results["analysis"]:
            if file_info["needs_update"]:
                report.append(f"### {file_info['relative_path']}")
                for reason in file_info["reasons"]:
                    report.append(f"- {reason}")
                report.append("")

        report.extend([
            "## Recommended Actions",
            "1. Update schema references to v2.0.0",
            "2. Add 692 cognitive components information",
            "3. Document lane-based evolution architecture",
            "4. Include legacy core sunset status",
            "5. Add distributed consciousness architecture details",
            "",
            "## Architecture Summary for Updates",
            self.generate_architecture_summary()
        ])

        return "\\n".join(report)


if __name__ == "__main__":
    updater = ContextUpdater("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    print("=== LUKHAS Context Files Update Analysis ===\\n")

    report = updater.generate_update_report()
    print(report)

    # Save report
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/temp_context_update_report.md", "w") as f:
        f.write(report)
