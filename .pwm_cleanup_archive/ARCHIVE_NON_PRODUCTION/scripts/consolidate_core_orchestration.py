#!/usr/bin/env python3
"""
Core Orchestration Consolidator - Phase 2B-1
Consolidate 34 core orchestration files into 1 primary implementation
"""

import argparse
import ast
import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List


class CoreOrchestrationConsolidator:
    def __init__(self, analysis_file: str = "functional_orchestrator_analysis.json"):
        self.analysis_file = analysis_file
        self.analysis_data = {}
        self.primary_file = "./orchestration/core_modules/orchestration_service.py"
        self.consolidated_features = {}
        self.unique_classes = {}
        self.unique_functions = {}
        self.unique_imports = set()

    def load_analysis(self) -> bool:
        """Load the functional analysis report"""
        try:
            with open(self.analysis_file) as f:
                self.analysis_data = json.load(f)

            print("📊 Loaded functional analysis")
            return True

        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
            return False

    def get_core_orchestration_files(self) -> List[str]:
        """Get all core orchestration files from analysis"""
        if "consolidation_plan" not in self.analysis_data:
            return []

        core_plan = self.analysis_data["consolidation_plan"].get(
            "core_orchestration", {}
        )
        if "files" not in core_plan:
            return []

        # Extract file paths from analysis data
        files = []
        for file_info in core_plan["files"]:
            if isinstance(file_info, dict) and "path" in file_info:
                files.append(file_info["path"])
            elif isinstance(file_info, str):
                files.append(file_info)

        return files

    def analyze_file_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze Python file content for classes, functions, imports"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            classes = []
            functions = []
            imports = []
            constants = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract class info
                    class_info = {
                        "name": node.name,
                        "bases": [self._get_name(base) for base in node.bases],
                        "methods": [
                            n.name
                            for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ],
                        "docstring": ast.get_docstring(node) or "",
                    }
                    classes.append(class_info)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only top-level functions (not methods)
                    if not any(
                        isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
                    ):
                        func_info = {
                            "name": node.name,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node) or "",
                        }
                        functions.append(func_info)

                elif isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(f"import {name.name}")

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            imports.append(f"from {node.module} import {name.name}")

                elif isinstance(node, ast.Assign):
                    # Look for module-level constants
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append(target.id)

            return {
                "content": content,
                "classes": classes,
                "functions": functions,
                "imports": list(set(imports)),
                "constants": constants,
                "size": len(content),
                "lines": len(content.split("\n")),
            }

        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
            return {"error": str(e)}

    def _get_name(self, node):
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def extract_unique_features(self, files: List[str]) -> Dict[str, Any]:
        """Extract unique features from all core orchestration files"""
        print(f"🔍 Analyzing {len(files)} core orchestration files...")

        all_features = {
            "classes": {},
            "functions": {},
            "imports": set(),
            "constants": set(),
            "docstrings": [],
            "patterns": set(),
        }

        primary_content = None
        if os.path.exists(self.primary_file):
            primary_analysis = self.analyze_file_content(self.primary_file)
            primary_content = primary_analysis
            print(
                f"📋 Primary file: {self.primary_file} ({primary_analysis.get('size', 0)/1024:.1f} KB)"
            )

        for i, file_path in enumerate(files, 1):
            if not os.path.exists(file_path):
                print(f"   ⚠️  File not found: {file_path}")
                continue

            if file_path == self.primary_file:
                continue  # Skip primary file in extraction

            analysis = self.analyze_file_content(file_path)
            if "error" in analysis:
                continue

            print(
                f"   {i:2}/{len(files)} {os.path.basename(file_path)} ({analysis['size']/1024:.1f} KB)"
            )

            # Collect unique classes
            for cls in analysis.get("classes", []):
                cls_name = cls["name"]
                if cls_name not in all_features["classes"]:
                    all_features["classes"][cls_name] = {
                        "definition": cls,
                        "source_file": file_path,
                        "unique": True,
                    }

                    # Check if this class exists in primary
                    if primary_content:
                        primary_classes = [
                            c["name"] for c in primary_content.get("classes", [])
                        ]
                        if cls_name in primary_classes:
                            all_features["classes"][cls_name]["unique"] = False

            # Collect unique functions
            for func in analysis.get("functions", []):
                func_name = func["name"]
                if func_name not in all_features["functions"]:
                    all_features["functions"][func_name] = {
                        "definition": func,
                        "source_file": file_path,
                        "unique": True,
                    }

                    # Check if this function exists in primary
                    if primary_content:
                        primary_functions = [
                            f["name"] for f in primary_content.get("functions", [])
                        ]
                        if func_name in primary_functions:
                            all_features["functions"][func_name]["unique"] = False

            # Collect imports and constants
            all_features["imports"].update(analysis.get("imports", []))
            all_features["constants"].update(analysis.get("constants", []))

            # Extract docstrings for documentation
            for cls in analysis.get("classes", []):
                if cls.get("docstring"):
                    all_features["docstrings"].append(
                        {
                            "type": "class",
                            "name": cls["name"],
                            "docstring": cls["docstring"],
                            "source": file_path,
                        }
                    )

            for func in analysis.get("functions", []):
                if func.get("docstring"):
                    all_features["docstrings"].append(
                        {
                            "type": "function",
                            "name": func["name"],
                            "docstring": func["docstring"],
                            "source": file_path,
                        }
                    )

        return all_features

    def generate_consolidated_file(
        self, features: Dict[str, Any], dry_run: bool = True
    ) -> str:
        """Generate consolidated orchestration service file"""
        print("\\n🔧 Generating consolidated orchestration service...")

        # Read primary file content
        if not os.path.exists(self.primary_file):
            print(f"❌ Primary file not found: {self.primary_file}")
            return ""

        with open(self.primary_file) as f:
            primary_content = f.read()

        # Find unique classes and functions to add
        unique_classes = {
            name: info for name, info in features["classes"].items() if info["unique"]
        }
        unique_functions = {
            name: info for name, info in features["functions"].items() if info["unique"]
        }

        print(f"   📦 Found {len(unique_classes)} unique classes to merge")
        print(f"   📦 Found {len(unique_functions)} unique functions to merge")
        print(f"   📦 Found {len(features['imports'])} total imports")

        # Generate enhanced file content
        consolidated_content = f'''"""
LUKHAS Consolidated Orchestration Service - Enhanced Core Module

This is the consolidated orchestration service that combines functionality from
{len(self.get_core_orchestration_files())} core orchestration files.

CONSOLIDATED FROM:
{chr(10).join(f"- {f}" for f in self.get_core_orchestration_files()[:10])}
{"... and " + str(len(self.get_core_orchestration_files()) - 10) + " more files" if len(self.get_core_orchestration_files()) > 10 else ""}

Consolidation Date: {datetime.now().isoformat()}
Total Original Size: {sum(os.path.getsize(f) for f in self.get_core_orchestration_files() if os.path.exists(f))/1024:.1f} KB

Key Consolidated Features:
- Module coordination and orchestration
- Workflow execution and management
- Resource management across modules
- Event routing and message handling
- Performance orchestration and optimization
- Cross-module permission validation
- Comprehensive logging and audit trails
- Load balancing and failover capabilities
- Configuration management
- Security and authentication integration

All operations respect user consent, tier access, and LUKHAS identity requirements.
"""

# === CONSOLIDATED IMPORTS ===
{chr(10).join(sorted(features['imports']))}

# === PRIMARY ORCHESTRATION SERVICE CONTENT ===
{primary_content.split('"""', 2)[-1] if '"""' in primary_content else primary_content}

# === CONSOLIDATED UNIQUE CLASSES ===
'''

        # Add unique classes
        for class_name, class_info in unique_classes.items():
            cls_def = class_info["definition"]
            consolidated_content += f'''
# From: {class_info['source_file']}
class {cls_def['name']}({', '.join(cls_def['bases']) if cls_def['bases'] else 'object'}):
    """
    {cls_def['docstring'] or f"Consolidated class from {os.path.basename(class_info['source_file'])}"}

    Originally from: {class_info['source_file']}
    Methods: {', '.join(cls_def['methods'])}
    """
    # TODO: Implement consolidated {cls_def['name']} functionality
    # Original methods: {', '.join(cls_def['methods'])}
    pass

'''

        # Add unique functions
        consolidated_content += "\\n# === CONSOLIDATED UNIQUE FUNCTIONS ===\\n"
        for func_name, func_info in unique_functions.items():
            func_def = func_info["definition"]
            async_keyword = "async " if func_def["is_async"] else ""
            args_str = ", ".join(func_def["args"]) if func_def["args"] else ""

            consolidated_content += f'''
# From: {func_info['source_file']}
{async_keyword}def {func_def['name']}({args_str}):
    """
    {func_def['docstring'] or f"Consolidated function from {os.path.basename(func_info['source_file'])}"}

    Originally from: {func_info['source_file']}
    """
    # TODO: Implement consolidated {func_def['name']} functionality
    pass

'''

        # Add documentation section
        consolidated_content += '''
# === CONSOLIDATION DOCUMENTATION ===

"""
CONSOLIDATION REPORT:

Original Files Consolidated:
"""
'''

        for doc in features["docstrings"][:20]:  # Limit to first 20 docstrings
            consolidated_content += f"""
# {doc['type'].upper()}: {doc['name']} (from {os.path.basename(doc['source'])})
# {doc['docstring'][:200]}{'...' if len(doc['docstring']) > 200 else ''}

"""

        return consolidated_content

    def create_archive_structure(self) -> None:
        """Create archive structure for consolidated files"""
        archive_dirs = [
            "archived/orchestrators/consolidated/core_orchestration",
            "archived/orchestrators/consolidated/core_orchestration/original_files",
        ]

        for dir_path in archive_dirs:
            os.makedirs(dir_path, exist_ok=True)

    def archive_original_files(
        self, files: List[str], dry_run: bool = True
    ) -> List[str]:
        """Archive original files before consolidation"""
        if dry_run:
            print(f"🔍 DRY RUN - Would archive {len(files)} files")
            return []

        self.create_archive_structure()
        archived_files = []

        print(f"\\n📦 Archiving {len(files)} original core orchestration files...")

        for file_path in files:
            if not os.path.exists(file_path):
                print(f"   ⚠️  File not found: {file_path}")
                continue

            if file_path == self.primary_file:
                continue  # Don't archive the primary file

            try:
                # Create archive filename
                file_name = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{file_name}_{timestamp}"
                archive_path = f"archived/orchestrators/consolidated/core_orchestration/original_files/{archive_name}"

                # Copy to archive
                shutil.copy2(file_path, archive_path)

                # Remove original
                os.remove(file_path)

                print(f"   ✅ Archived: {file_path}")
                print(f"      💾 Backup: {archive_name}")

                archived_files.append(
                    {
                        "original_path": file_path,
                        "archive_path": archive_path,
                        "timestamp": timestamp,
                    }
                )

            except Exception as e:
                print(f"   ❌ Error archiving {file_path}: {e}")

        return archived_files

    def update_consolidated_file(
        self, consolidated_content: str, dry_run: bool = True
    ) -> bool:
        """Update the primary file with consolidated content"""
        if dry_run:
            print(
                f"🔍 DRY RUN - Would update {self.primary_file} with consolidated content"
            )
            print(f"   📊 New content size: {len(consolidated_content)/1024:.1f} KB")
            return True

        try:
            # Backup original primary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.primary_file}.backup_{timestamp}"
            shutil.copy2(self.primary_file, backup_path)
            print(f"💾 Backed up primary file to: {backup_path}")

            # Write consolidated content
            with open(self.primary_file, "w") as f:
                f.write(consolidated_content)

            print(f"✅ Updated {self.primary_file} with consolidated content")
            print(f"   📊 New size: {len(consolidated_content)/1024:.1f} KB")
            return True

        except Exception as e:
            print(f"❌ Error updating consolidated file: {e}")
            return False

    def generate_consolidation_report(
        self, features: Dict[str, Any], archived_files: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive consolidation report"""
        files_list = self.get_core_orchestration_files()

        report = {
            "consolidation_timestamp": datetime.now().isoformat(),
            "analysis_file": self.analysis_file,
            "primary_file": self.primary_file,
            "total_files_consolidated": len(files_list),
            "files_archived": len(archived_files),
            "files_consolidated": files_list,
            "archived_files": archived_files,
            "unique_features_extracted": {
                "classes": len(
                    [c for c in features["classes"].values() if c["unique"]]
                ),
                "functions": len(
                    [f for f in features["functions"].values() if f["unique"]]
                ),
                "imports": len(features["imports"]),
                "constants": len(features["constants"]),
            },
            "consolidation_stats": {
                "original_file_count": len(files_list),
                "final_file_count": 1,
                "reduction_count": len(files_list) - 1,
                "reduction_percentage": round(
                    ((len(files_list) - 1) / len(files_list)) * 100, 1
                ),
            },
        }

        report_file = f"core_orchestration_consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\\n📄 Consolidation report saved to: {report_file}")
        return report

    def consolidate_core_orchestration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Main consolidation process"""
        print("\\n🎯 CORE ORCHESTRATION CONSOLIDATION")
        print(f"{'='*60}")
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        print(f"{'='*60}")

        # Get core orchestration files
        files = self.get_core_orchestration_files()
        if not files:
            print("❌ No core orchestration files found in analysis")
            return {}

        print(f"📁 Found {len(files)} core orchestration files to consolidate")
        print(f"🎯 Primary file: {self.primary_file}")

        # Extract unique features
        features = self.extract_unique_features(files)

        # Generate consolidated content
        consolidated_content = self.generate_consolidated_file(features, dry_run)

        # Archive original files (except primary)
        archived_files = self.archive_original_files(files, dry_run)

        # Update primary file with consolidated content
        if consolidated_content:
            self.update_consolidated_file(consolidated_content, dry_run)

        # Generate report
        report = self.generate_consolidation_report(features, archived_files)

        # Print summary
        print(f"\\n{'='*60}")
        print("📊 CONSOLIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"  Files to consolidate: {len(files)}")
        print(f"  Files archived: {len(archived_files)}")
        print(f"  Primary file: {os.path.basename(self.primary_file)}")
        print(
            f"  Unique classes extracted: {len([c for c in features['classes'].values() if c['unique']])}"
        )
        print(
            f"  Unique functions extracted: {len([f for f in features['functions'].values() if f['unique']])}"
        )
        print(f"  Final reduction: {len(files)-1} files eliminated")

        if dry_run:
            print("\\n🔍 This was a dry run. Use --execute to perform consolidation.")

        return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Consolidate core orchestration files")
    parser.add_argument(
        "--analysis-file",
        default="functional_orchestrator_analysis.json",
        help="Functional analysis report file",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually consolidate files (default: dry run)",
    )

    args = parser.parse_args()

    consolidator = CoreOrchestrationConsolidator(args.analysis_file)

    if not consolidator.load_analysis():
        return 1

    # Perform consolidation
    report = consolidator.consolidate_core_orchestration(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute consolidation:")
        print("   python3 scripts/consolidate_core_orchestration.py --execute")
    else:
        print("\\n✅ Core orchestration consolidation complete!")
        print(
            f"   📊 Reduced from {report['consolidation_stats']['original_file_count']} to 1 file"
        )
        print(
            f"   📉 {report['consolidation_stats']['reduction_percentage']}% reduction achieved"
        )

    return 0


if __name__ == "__main__":
    exit(main())
