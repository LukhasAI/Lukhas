#!/usr/bin/env python3
"""
🔍 lukhas Post-Consolidation Audit System
Comprehensive audit of remaining components in core and core_systems after consolidation

This script will:
1. Scan ALL remaining files in core/ and core_systems/
2. Categorize every single component (classified and unclassified)
3. Generate detailed reports of what remains
4. Identify potential missed consolidation opportunities
5. Provide recommendations for final cleanup

Author: lukhas AI Enhancement Team
Date: 2025-06-05
Version: 1.0.0
"""
from datetime import timezone

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class PostConsolidationAuditor:
    """Comprehensive lukhasuditor for post-consolidation workspace analysis"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.audit_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Directories to audit
        self.audit_directories = [
            "core",
            "core_systems",
            "src/core",
            "modules/src/core",
            "test_glossary_workspace/core",
        ]

        # Known consolidation categories (from original plan)
        self.known_categories = {
            "bio": ["bio_core", "BIO_SYMBOLIC", "bio_symbolic", "bio", "oscillator"],
            "quantum": ["qi_core", "quantum", "qi_processing"],
            "brain": ["brain", "neural", "cognitive", "consciousness"],
            "memory": ["memory", "memory_learning", "memory_systems"],
            "voice": ["voice", "voice_systems", "speech", "audio"],
            "interface": ["interface", "ui", "web", "mobile", "video"],
            "integration": ["integration", "unified", "orchestrator"],
            "enhancement": ["enhancement", "optimization", "cognitive_enhancement"],
            "learning": ["learning", "meta_learning", "adaptive", "ml"],
            "security": ["security", "auth", "encryption", "ssl"],
            "network": ["network", "communication", "protocol"],
            "data": ["data", "storage", "database", "persistence"],
            "api": ["api", "rest", "graphql", "endpoints"],
            "config": ["config", "settings", "environment"],
            "utils": ["utils", "helpers", "common", "shared"],
            "tests": ["test", "tests", "testing", "spec"],
            "docs": ["docs", "documentation", "readme"],
            "deployment": ["deploy", "deployment", "docker", "k8s"],
            "monitoring": ["monitoring", "metrics", "logging", "observability"],
        }

        # File type classifications
        self.file_types = {
            "python": [".py"],
            "javascript": [".js", ".ts", ".jsx", ".tsx"],
            "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"],
            "documentation": [".md", ".txt", ".rst", ".asciidoc"],
            "data": [".csv", ".xml", ".sql", ".db"],
            "web": [".html", ".css", ".scss", ".less"],
            "shell": [".sh", ".bash", ".zsh", ".fish"],
            "other": [],  # Will be populated with unknown extensions
        }

    def perform_comprehensive_audit(self) -> dict[str, Any]:
        """Perform comprehensive audit of remaining components"""

        print("🔍 Starting Comprehensive Post-Consolidation Audit...")

        audit_results = {
            "audit_metadata": {
                "timestamp": self.audit_timestamp,
                "workspace_root": str(self.workspace_root),
                "audit_directories": self.audit_directories,
            },
            "directory_analysis": {},
            "file_analysis": {},
            "categorization_report": {},
            "unclassified_components": {},
            "consolidation_recommendations": [],
            "summary_statistics": {},
            "detailed_inventory": {},
        }

        # Scan each target directory
        for directory in self.audit_directories:
            dir_path = self.workspace_root / directory
            if dir_path.exists():
                print(f"📁 Auditing: {directory}")
                audit_results["directory_analysis"][directory] = self._audit_directory(dir_path)
            else:
                audit_results["directory_analysis"][directory] = {"status": "NOT_FOUND"}

        # Perform comprehensive file analysis
        audit_results["file_analysis"] = self._analyze_all_files(audit_results["directory_analysis"])

        # Categorize all components
        audit_results["categorization_report"] = self._categorize_components(audit_results["file_analysis"])

        # Identify unclassified components
        audit_results["unclassified_components"] = self._identify_unclassified(audit_results["categorization_report"])

        # Generate recommendations
        audit_results["consolidation_recommendations"] = self._generate_recommendations(audit_results)

        # Calculate summary statistics
        audit_results["summary_statistics"] = self._calculate_statistics(audit_results)

        # Create detailed inventory
        audit_results["detailed_inventory"] = self._create_detailed_inventory(audit_results)

        return audit_results

    def _audit_directory(self, directory: Path) -> dict[str, Any]:
        """Audit a single directory comprehensively"""

        analysis = {
            "path": str(directory),
            "exists": directory.exists(),
            "total_files": 0,
            "total_directories": 0,
            "file_tree": {},
            "file_details": [],
            "subdirectories": [],
            "file_sizes": {},
            "file_types_found": set(),
            "largest_files": [],
            "recently_modified": [],
        }

        if not directory.exists():
            return analysis

        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                relative_path = root_path.relative_to(directory)

                # Count directories
                analysis["total_directories"] += len(dirs)
                analysis["subdirectories"].extend([str(relative_path / d) for d in dirs])

                # Process files
                for file in files:
                    file_path = root_path / file
                    relative_file_path = file_path.relative_to(directory)

                    try:
                        file_stat = file_path.stat()
                        file_size = file_stat.st_size
                        file_modified = datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc)
                        file_ext = file_path.suffix.lower()

                        file_details = {
                            "path": str(relative_file_path),
                            "full_path": str(file_path),
                            "size": file_size,
                            "modified": file_modified.isoformat(),
                            "extension": file_ext,
                            "type": self._classify_file_type(file_ext),
                        }

                        analysis["file_details"].append(file_details)
                        analysis["file_sizes"][str(relative_file_path)] = file_size
                        analysis["file_types_found"].add(file_ext)

                        # Track largest files (top 10)
                        analysis["largest_files"].append((str(relative_file_path), file_size))

                        # Track recently modified files
                        if (datetime.now(timezone.utc) - file_modified).days <= 7:
                            analysis["recently_modified"].append(
                                {
                                    "path": str(relative_file_path),
                                    "modified": file_modified.isoformat(),
                                }
                            )

                        analysis["total_files"] += 1

                    except (OSError, PermissionError) as e:
                        print(f"⚠️  Warning: Could not access {file_path}: {e}")

            # Sort and limit largest files
            analysis["largest_files"] = sorted(analysis["largest_files"], key=lambda x: x[1], reverse=True)[:10]
            analysis["file_types_found"] = list(analysis["file_types_found"])

        except Exception as e:
            analysis["error"] = str(e)
            print(f"❌ Error auditing {directory}: {e}")

        return analysis

    def _classify_file_type(self, extension: str) -> str:
        """Classify file type based on extension"""
        for file_type, extensions in self.file_types.items():
            if extension in extensions:
                return file_type

        # Add to "other" category if not found
        if extension not in self.file_types["other"]:
            self.file_types["other"].append(extension)

        return "other"

    def _analyze_all_files(self, directory_analysis: dict[str, Any]) -> dict[str, Any]:
        """Analyze all files across directories"""

        file_analysis = {
            "total_files_found": 0,
            "files_by_type": defaultdict(int),
            "files_by_category": defaultdict(list),
            "duplicate_analysis": {},
            "size_analysis": {},
            "all_files": [],
        }

        all_files = []

        # Collect all files
        for dir_name, dir_data in directory_analysis.items():
            if dir_data.get("file_details"):
                for file_detail in dir_data["file_details"]:
                    file_detail["source_directory"] = dir_name
                    all_files.append(file_detail)

        file_analysis["all_files"] = all_files
        file_analysis["total_files_found"] = len(all_files)

        # Analyze by type
        for file_detail in all_files:
            file_type = file_detail["type"]
            file_analysis["files_by_type"][file_type] += 1

        # Find potential duplicates by name
        file_names = defaultdict(list)
        for file_detail in all_files:
            file_name = Path(file_detail["path"]).name
            file_names[file_name].append(file_detail)

        # Identify duplicates
        for file_name, file_list in file_names.items():
            if len(file_list) > 1:
                file_analysis["duplicate_analysis"][file_name] = file_list

        # Size analysis
        total_size = sum(f["size"] for f in all_files)
        file_analysis["size_analysis"] = {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_file_size": (round(total_size / len(all_files), 2) if all_files else 0),
            "largest_file": (max(all_files, key=lambda x: x["size"]) if all_files else None),
        }

        return file_analysis

    def _categorize_components(self, file_analysis: dict[str, Any]) -> dict[str, Any]:
        """Categorize all components based on known categories"""

        categorization = {
            "categorized": defaultdict(list),
            "unclassified": [],
            "category_statistics": {},
            "classification_confidence": {},
        }

        for file_detail in file_analysis["all_files"]:
            file_path = file_detail["path"].lower()
            file_name = Path(file_detail["path"]).name.lower()

            # Try to classify based on path and name
            classified = False
            confidence_scores = {}

            for category, keywords in self.known_categories.items():
                confidence = 0

                # Check keywords in path
                for keyword in keywords:
                    if keyword.lower() in file_path:
                        confidence += 2
                    if keyword.lower() in file_name:
                        confidence += 1

                if confidence > 0:
                    confidence_scores[category] = confidence

            # Assign to highest confidence category
            if confidence_scores:
                best_category = max(confidence_scores, key=confidence_scores.get)
                best_confidence = confidence_scores[best_category]

                categorization["categorized"][best_category].append(file_detail)
                categorization["classification_confidence"][file_detail["full_path"]] = {
                    "category": best_category,
                    "confidence": best_confidence,
                    "all_scores": confidence_scores,
                }
                classified = True

            if not classified:
                categorization["unclassified"].append(file_detail)

        # Calculate category statistics
        for category, files in categorization["categorized"].items():
            categorization["category_statistics"][category] = {
                "file_count": len(files),
                "total_size": sum(f["size"] for f in files),
                "file_types": list({f["type"] for f in files}),
            }

        return categorization

    def _identify_unclassified(self, categorization_report: dict[str, Any]) -> dict[str, Any]:
        """Identify and analyze unclassified components"""

        unclassified_analysis = {
            "total_unclassified": len(categorization_report["unclassified"]),
            "unclassified_files": categorization_report["unclassified"],
            "unclassified_patterns": defaultdict(list),
            "potential_new_categories": {},
            "recommendations": [],
        }

        # Analyze patterns in unclassified files
        for file_detail in categorization_report["unclassified"]:
            file_path = Path(file_detail["path"])

            # Group by parent directory
            parent_dir = str(file_path.parent) if file_path.parent != Path(".") else "root"
            unclassified_analysis["unclassified_patterns"][parent_dir].append(file_detail)

            # Look for potential category indicators
            path_parts = file_path.parts
            for part in path_parts:
                if len(part) > 3 and part.isalpha():  # Potential category name
                    if part not in unclassified_analysis["potential_new_categories"]:
                        unclassified_analysis["potential_new_categories"][part] = []
                    unclassified_analysis["potential_new_categories"][part].append(file_detail)

        # Generate recommendations for unclassified items
        for pattern, files in unclassified_analysis["unclassified_patterns"].items():
            if len(files) > 1:
                unclassified_analysis["recommendations"].append(
                    {
                        "type": "pattern_consolidation",
                        "pattern": pattern,
                        "file_count": len(files),
                        "suggestion": f"Consider creating category for pattern: {pattern}",
                    }
                )

        return unclassified_analysis

    def _generate_recommendations(self, audit_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate consolidation recommendations"""

        recommendations = []

        # Recommendation 1: Move remaining files
        total_remaining = audit_results["summary_statistics"].get("total_files_remaining", 0)
        if total_remaining > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "type": "consolidation",
                    "title": "Consolidate Remaining Files",
                    "description": f"Found {total_remaining} files still in core directories",
                    "action": "Move all categorized files to appropriate lukhas/ subdirectories",
                }
            )

        # Recommendation 2: Handle unclassified files
        unclassified_count = len(audit_results["unclassified_components"]["unclassified_files"])
        if unclassified_count > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "type": "classification",
                    "title": "Classify Unidentified Components",
                    "description": f"Found {unclassified_count} unclassified files requiring manual review",
                    "action": "Review and categorize unclassified files manually",
                }
            )

        # Recommendation 3: Handle duplicates
        duplicate_count = len(audit_results["file_analysis"]["duplicate_analysis"])
        if duplicate_count > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "type": "deduplication",
                    "title": "Resolve Duplicate Files",
                    "description": f"Found {duplicate_count} potential duplicate file names",
                    "action": "Review and merge or remove duplicate files",
                }
            )

        # Recommendation 4: Clean up empty directories
        recommendations.append(
            {
                "priority": "LOW",
                "type": "cleanup",
                "title": "Remove Empty Directories",
                "description": "Remove empty core directories after consolidation",
                "action": "Safe removal of empty directory structures",
            }
        )

        return recommendations

    def _calculate_statistics(self, audit_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate comprehensive statistics"""

        stats = {
            "total_files_remaining": 0,
            "total_size_remaining_mb": 0,
            "files_by_directory": {},
            "files_by_type": {},
            "files_by_category": {},
            "consolidation_progress": {},
        }

        # Calculate totals
        for dir_name, dir_data in audit_results["directory_analysis"].items():
            if dir_data.get("total_files"):
                stats["files_by_directory"][dir_name] = dir_data["total_files"]
                stats["total_files_remaining"] += dir_data["total_files"]

        # File type distribution
        if audit_results["file_analysis"].get("files_by_type"):
            stats["files_by_type"] = dict(audit_results["file_analysis"]["files_by_type"])

        # Category distribution
        if audit_results["categorization_report"].get("category_statistics"):
            for category, cat_stats in audit_results["categorization_report"]["category_statistics"].items():
                stats["files_by_category"][category] = cat_stats["file_count"]

        # Size calculations
        if audit_results["file_analysis"].get("size_analysis"):
            size_mb = audit_results["file_analysis"]["size_analysis"].get("total_size_mb", 0)
            stats["total_size_remaining_mb"] = size_mb

        return stats

    def _create_detailed_inventory(self, audit_results: dict[str, Any]) -> dict[str, Any]:
        """Create detailed inventory of all components"""

        inventory = {
            "inventory_by_category": {},
            "inventory_by_directory": {},
            "inventory_by_type": {},
            "high_priority_items": [],
            "consolidation_candidates": [],
        }

        # Organize by category
        if audit_results["categorization_report"].get("categorized"):
            for category, files in audit_results["categorization_report"]["categorized"].items():
                inventory["inventory_by_category"][category] = [
                    {
                        "path": f["path"],
                        "size": f["size"],
                        "type": f["type"],
                        "source_dir": f["source_directory"],
                    }
                    for f in files
                ]

        # Add unclassified to inventory
        if audit_results["unclassified_components"].get("unclassified_files"):
            inventory["inventory_by_category"]["UNCLASSIFIED"] = [
                {
                    "path": f["path"],
                    "size": f["size"],
                    "type": f["type"],
                    "source_dir": f["source_directory"],
                }
                for f in audit_results["unclassified_components"]["unclassified_files"]
            ]

        # Identify high priority consolidation items
        for category, files in inventory["inventory_by_category"].items():
            if len(files) > 5:  # Categories with many files
                inventory["high_priority_items"].append(
                    {
                        "category": category,
                        "file_count": len(files),
                        "priority": "HIGH" if len(files) > 10 else "MEDIUM",
                    }
                )

        return inventory

    def generate_comprehensive_report(self, audit_results: dict[str, Any]) -> str:
        """Generate comprehensive audit report"""

        report = f"""
# 🔍 lukhas Post-Consolidation Comprehensive Audit Report

**Generated:** {audit_results["audit_metadata"]["timestamp"]}
**Workspace:** {audit_results["audit_metadata"]["workspace_root"]}

---

## 📋 EXECUTIVE SUMMARY

### **Audit Overview**
"""

        stats = audit_results["summary_statistics"]
        report += f"""
- **Total Files Remaining:** {stats.get("total_files_remaining", 0)}
- **Total Size Remaining:** {stats.get("total_size_remaining_mb", 0):.2f} MB
- **Directories Audited:** {len(audit_results["audit_metadata"]["audit_directories"])}
- **Categorized Files:** {sum(stats.get("files_by_category", {}).values())}
- **Unclassified Files:** {len(audit_results["unclassified_components"]["unclassified_files"])}

"""

        # Directory Analysis
        report += """
---

## 📁 DIRECTORY ANALYSIS

"""

        for dir_name, dir_data in audit_results["directory_analysis"].items():
            if dir_data.get("exists"):
                report += f"""
### **{dir_name}/**
- **Status:** ✅ EXISTS
- **Files:** {dir_data.get("total_files", 0)}
- **Directories:** {dir_data.get("total_directories", 0)}
- **File Types:** {", ".join(dir_data.get("file_types_found", []))}
- **Recently Modified:** {len(dir_data.get("recently_modified", []))} files
"""
            else:
                report += f"""
### **{dir_name}/**
- **Status:** ❌ NOT FOUND
"""

        # Categorization Report
        report += """
---

## 🏷️ CATEGORIZATION REPORT

### **Categorized Components:**
"""

        for category, cat_stats in audit_results["categorization_report"].get("category_statistics", {}).items():
            report += f"""
- **{category.upper()}:** {cat_stats["file_count"]} files ({cat_stats["total_size"]} bytes)
  - File types: {", ".join(cat_stats["file_types"])}
"""

        # Unclassified Components
        unclassified = audit_results["unclassified_components"]
        report += f"""

### **UNCLASSIFIED COMPONENTS:** {unclassified["total_unclassified"]} files

#### **Unclassified by Pattern:**
"""

        for pattern, files in unclassified.get("unclassified_patterns", {}).items():
            report += f"""
- **{pattern}:** {len(files)} files
"""

        # Potential New Categories
        if unclassified.get("potential_new_categories"):
            report += """

#### **Potential New Categories:**
"""
            for category, files in unclassified["potential_new_categories"].items():
                if len(files) > 1:
                    report += f"- **{category}:** {len(files)} files\n"

        # File Analysis
        report += """
---

## 📊 FILE ANALYSIS

### **File Type Distribution:**
"""

        for file_type, count in audit_results["file_analysis"].get("files_by_type", {}).items():
            report += f"- **{file_type}:** {count} files\n"

        # Duplicates
        duplicates = audit_results["file_analysis"].get("duplicate_analysis", {})
        if duplicates:
            report += f"""

### **Potential Duplicates:** {len(duplicates)} sets found

"""
            for file_name, file_list in list(duplicates.items())[:5]:  # Show first 5
                report += f"""
#### **{file_name}**
"""
                for file_detail in file_list:
                    report += f"- {file_detail['source_directory']}/{file_detail['path']}\n"

        # Recommendations
        report += """
---

## 🚀 CONSOLIDATION RECOMMENDATIONS

"""

        for i, rec in enumerate(audit_results["consolidation_recommendations"], 1):
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
            report += f"""
### **{i}. {rec["title"]}** {priority_emoji}
- **Priority:** {rec["priority"]}
- **Type:** {rec["type"]}
- **Description:** {rec["description"]}
- **Action:** {rec["action"]}

"""

        # Detailed Inventory
        report += """
---

## 📝 DETAILED INVENTORY

### **High Priority Consolidation Candidates:**
"""

        for item in audit_results["detailed_inventory"].get("high_priority_items", []):
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡"}.get(item["priority"], "⚪")
            report += f"""
- **{item["category"]}:** {item["file_count"]} files {priority_emoji}
"""

        # Complete File Listing
        report += """

### **Complete File Inventory by Category:**
"""

        for category, files in audit_results["detailed_inventory"].get("inventory_by_category", {}).items():
            if files:
                report += f"""

#### **{category.upper()}** ({len(files)} files)
"""
                for file_info in files[:10]:  # Show first 10 per category
                    report += f"- `{file_info['source_dir']}/{file_info['path']}` ({file_info['size']} bytes)\n"

                if len(files) > 10:
                    report += f"- ... and {len(files) - 10} more files\n"

        # Conclusion
        total_remaining = stats.get("total_files_remaining", 0)
        if total_remaining == 0:
            report += """
---

## 🎉 CONCLUSION

✅ **CONSOLIDATION COMPLETE!** All core components have been successfully consolidated into the lukhas/ directory structure.

**Next Steps:**
1. Verify modular structure integrity
2. Update import statements if needed
3. Run comprehensive tests
4. Remove empty core directories

"""
        else:
            report += f"""
---

## 🎯 CONCLUSION

⚠️ **CONSOLIDATION INCOMPLETE** - {total_remaining} files remain in core directories.

**Immediate Actions Required:**
1. Review unclassified components
2. Complete file categorization
3. Execute remaining consolidation steps
4. Verify system functionality

"""

        report += f"""
---

*lukhas Post-Consolidation Audit Report*
*Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return report

    def save_audit_results(self, audit_results: dict[str, Any]):
        """Save comprehensive audit results"""

        # Save JSON data
        json_path = self.workspace_root / f"post_consolidation_audit_{self.audit_timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(audit_results, f, indent=2, default=str)

        # Save detailed report
        report = self.generate_comprehensive_report(audit_results)
        report_path = self.workspace_root / f"POST_CONSOLIDATION_AUDIT_REPORT_{self.audit_timestamp}.md"
        with open(report_path, "w") as f:
            f.write(report)

        print("📄 Audit results saved:")
        print(f"   JSON: {json_path}")
        print(f"   Report: {report_path}")

        return json_path, report_path


def main():
    """Run comprehensive post-consolidation audit"""

    workspace_root = "/Users/A_G_I/CodexGPT_Lukhas"

    print("🔍 lukhas Post-Consolidation Comprehensive Audit")
    print("=" * 60)

    lukhasuditor = PostConsolidationAuditor(workspace_root)
    audit_results = lukhasuditor.perform_comprehensive_audit()

    # Save results
    json_path, report_path = lukhasuditor.save_audit_results(audit_results)

    # Display summary
    print("\n" + "=" * 60)
    print("🎯 AUDIT SUMMARY")
    print("=" * 60)

    stats = audit_results["summary_statistics"]
    print(f"📁 Total Files Remaining: {stats.get('total_files_remaining', 0)}")
    print(f"📊 Total Size: {stats.get('total_size_remaining_mb', 0):.2f} MB")
    print(f"🏷️  Categorized Files: {sum(stats.get('files_by_category', {}).values())}")
    print(f"❓ Unclassified Files: {len(audit_results['unclassified_components']['unclassified_files'])}")
    print(f"🔄 Recommendations: {len(audit_results['consolidation_recommendations'])}")

    # Show top recommendations
    print("\n🚀 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(audit_results["consolidation_recommendations"][:3], 1):
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
        print(f"   {i}. {rec['title']} {priority_emoji}")

    print(f"\n📄 Complete report available at: {report_path}")

    return audit_results


if __name__ == "__main__":
    main()

# Λ Systems 2025 www.ai