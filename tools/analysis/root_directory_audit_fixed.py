#!/usr/bin/env python3
"""
LUKHAS  Root Directory Audit and Reorganization Plan
Analyzes all root directories and creates a comprehensive reorganization plan
"""
import json
import os
from datetime import datetime, timezone

import streamlit as st

from consciousness.qi import qi


class RootDirectoryAuditor:
    def __init__(self):
        # Define our 7 core modules
        self.core_modules = [
            "core",
            "consciousness",
            "memory",
            "qim",
            "emotion",
            "governance",
            "bridge",
        ]

        # Define what should stay at root
        self.essential_root = [
            ".git",
            ".github",
            ".venv",
            "docs",
            "tests",
            "tools",
            "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms",
            ".gitignore",
            "README.md",
            "LICENSE",
            "requirements.txt",
            "main.py",
            "CLAUDE.md",
            ".env.example",
        ]

        # Categorize directories
        self.categories = {
            "core_modules": [],
            "should_be_submodules": [],
            "tools_and_utils": [],
            "documentation": [],
            "testing": [],
            "deployment": [],
            "archive_candidates": [],
            "unknown_purpose": [],
        }

        self.directory_analysis = {}

    def analyze_root(self):
        """Analyze all root-level directories"""
        root_items = os.listdir(".")
        directories = [d for d in root_items if os.path.isdir(d) and not d.startswith(".")]

        print(f"📊 Found {len(directories)} directories at root level")

        for directory in sorted(directories):
            self.analyze_directory(directory)

        return self.generate_reorganization_plan()

    def analyze_directory(self, directory):
        """Analyze a single directory"""
        analysis = {
            "name": directory,
            "size": self.get_directory_size(directory),
            "file_count": self.count_files(directory),
            "has_init": os.path.exists(os.path.join(directory, "__init__.py")),
            "has_readme": os.path.exists(os.path.join(directory, "README.md")),
            "has_tests": self.has_tests(directory),
            "suggested_action": "",
            "suggested_location": "",
            "reason": "",
        }

        # Categorize based on name and content
        if directory in self.core_modules:
            self.categories["core_modules"].append(directory)
            analysis["suggested_action"] = "ENHANCE"
            analysis["reason"] = "Core module - needs docs, tests, examples"

        elif directory in [
            "api",
            "architectures",
            "bio",
            "creativity",
            "dream",
            "ethics",
            "identity",
            "learning",
            "orchestration",
            "reasoning",
            "symbolic",
            "voice",
        ]:
            self.categories["should_be_submodules"].append(directory)
            analysis["suggested_action"] = "MERGE"
            analysis["suggested_location"] = self.suggest_module_for_directory(directory)
            analysis["reason"] = f"Should be part of {analysis['suggested_location']} module"

        elif directory in ["tools", "analysis_tools", "healing"]:
            self.categories["tools_and_utils"].append(directory)
            analysis["suggested_action"] = "CONSOLIDATE"
            analysis["suggested_location"] = "tools/"
            analysis["reason"] = "Utility/tool - consolidate into tools/"

        elif directory in [
            "docs",
            "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms",
            "config",
        ]:
            self.categories["documentation"].append(directory)
            analysis["suggested_action"] = "KEEP"
            analysis["reason"] = "Essential root directory"

        elif directory in ["tests", "red_team", "compliance"]:
            self.categories["testing"].append(directory)
            analysis["suggested_action"] = "REORGANIZE"
            analysis["suggested_location"] = "tests/"
            analysis["reason"] = "Testing related - consolidate into tests/"

        elif directory in [
            "misc",
            "trace",
            "_context_",
            "security",
            "health_reports",
            "quarantine",
        ]:
            self.categories["archive_candidates"].append(directory)
            analysis["suggested_action"] = "ARCHIVE"
            analysis["reason"] = "Unclear purpose or temporary - candidate for archival"

        else:
            self.categories["unknown_purpose"].append(directory)
            analysis["suggested_action"] = "REVIEW"
            analysis["reason"] = "Unknown purpose - needs manual review"

        self.directory_analysis[directory] = analysis

    def suggest_module_for_directory(self, directory):
        """Suggest which core module a directory should belong to"""
        mappings = {
            "api": "bridge",
            "architectures": "core",
            "bio": "qim",
            "creativity": "consciousness",
            "dream": "consciousness",
            "ethics": "governance",
            "identity": "governance",
            "learning": "memory",
            "orchestration": "core",
            "reasoning": "consciousness",
            "symbolic": "core",
            "voice": "bridge",
        }
        return mappings.get(directory, "core")

    def get_directory_size(self, directory):
        """Get size of directory in MB"""
        total_size = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except BaseException:
            pass
        return round(total_size / 1024 / 1024, 2)

    def count_files(self, directory):
        """Count Python files in directory"""
        count = 0
        try:
            for _root, _dirs, files in os.walk(directory):
                count += sum(1 for f in files if f.endswith(".py"))
        except BaseException:
            pass
        return count

    def has_tests(self, directory):
        """Check if directory has tests"""
        test_dir = os.path.join(directory, "tests")
        if os.path.exists(test_dir):
            return True

        # Check for test files
        try:
            for _root, _dirs, files in os.walk(directory):
                if any(f.startswith("test_") and f.endswith(".py") for f in files):
                    return True
        except BaseException:
            pass
        return False

    def generate_reorganization_plan(self):
        """Generate comprehensive reorganization plan"""
        plan = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_directories": len(self.directory_analysis),
                "core_modules": len(self.categories["core_modules"]),
                "to_merge": len(self.categories["should_be_submodules"]),
                "to_archive": len(self.categories["archive_candidates"]),
                "to_review": len(self.categories["unknown_purpose"]),
            },
            "categories": self.categories,
            "detailed_analysis": self.directory_analysis,
            "actions": self.create_action_plan(),
        }

        return plan

    def create_action_plan(self):
        """Create detailed action plan"""
        actions = []

        # 1. Enhance core modules
        for module in self.categories["core_modules"]:
            actions.append(
                {
                    "priority": 1,
                    "action": "ENHANCE_MODULE",
                    "target": module,
                    "tasks": [
                        f"Create {module}/README.md with module documentation",
                        f"Create {module}/tests/ with comprehensive test suite",
                        f"Create {module}/examples/ with usage examples",
                        f"Create {module}/docs/ with API documentation",
                        f"Add {module}/.gitignore for module-specific ignores",
                        f"Create {module}/Makefile for module-specific commands",
                        "Ensure all submodules have __init__.py",
                        "Add module-specific requirements.txt if needed",
                    ],
                }
            )

        # 2. Merge directories into modules
        for directory in self.categories["should_be_submodules"]:
            target_module = self.suggest_module_for_directory(directory)
            actions.append(
                {
                    "priority": 2,
                    "action": "MERGE_INTO_MODULE",
                    "source": directory,
                    "target": f"{target_module}/{directory}/",
                    "tasks": [
                        f"Move all files from {directory}/ to {target_module}/{directory}/",
                        f"Update all imports referencing {directory}",
                        f"Add {directory} to {target_module}/MODULE_MANIFEST.json",
                        "Create integration tests",
                    ],
                }
            )

        # 3. Consolidate tools
        for tool_dir in self.categories["tools_and_utils"]:
            if tool_dir != "tools":
                actions.append(
                    {
                        "priority": 3,
                        "action": "CONSOLIDATE_TOOLS",
                        "source": tool_dir,
                        "target": "tools/",
                        "tasks": [
                            f"Move {tool_dir}/* to tools/{tool_dir}/",
                            "Update any references",
                            "Remove empty directory",
                        ],
                    }
                )

        # 4. Archive candidates
        for directory in self.categories["archive_candidates"]:
            actions.append(
                {
                    "priority": 4,
                    "action": "ARCHIVE",
                    "source": directory,
                    "target": "archive/",
                    "tasks": [
                        f"Review {directory} for any valuable content",
                        "Document purpose in archive/README.md",
                        f"Move to archive/{directory}/",
                        "Update .gitignore to exclude if large",
                    ],
                }
            )

        return actions


def main():
    print("🔍 LUKHAS  ROOT DIRECTORY AUDIT")
    print("=" * 50)

    auditor = RootDirectoryAuditor()
    plan = auditor.analyze_root()

    # Save plan
    plan_path = "docs/planning/_ROOT_REORGANIZATION_PLAN.json"
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    with open(plan_path, "w") as f:
        json.dump(plan, f, indent=2)

    print(f"\n📋 Reorganization plan saved to: {plan_path}")

    # Display summary
    print("\n📊 ROOT DIRECTORY AUDIT SUMMARY")
    print("=" * 50)

    print(f"\nTotal directories at root: {plan['summary']['total_directories']}")
    print(f"Core modules (to enhance): {plan['summary']['core_modules']}")
    print(f"Should be submodules: {plan['summary']['to_merge']}")
    print(f"Archive candidates: {plan['summary']['to_archive']}")
    print(f"Need review: {plan['summary']['to_review']}")

    # Show categories
    for category, directories in plan["categories"].items():
        if directories:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for directory in directories:
                analysis = plan["detailed_analysis"][directory]
                print(f"  - {directory}: {analysis['file_count']} files, {analysis['size']}MB")
                print(f"    Action: {analysis['suggested_action']} - {analysis['reason']}")

    # Create enhancement tasks
    print("\n📝 MODULE ENHANCEMENT TASKS:")
    print("=" * 50)

    for module in auditor.categories["core_modules"]:
        print(f"\n{module.upper()} Module Enhancement:")
        print("1. Create comprehensive README.md")
        print("2. Set up test infrastructure")
        print("3. Add examples directory")
        print("4. Create API documentation")
        print("5. Add Makefile for common tasks")
        print("6. Ensure all submodules are properly initialized")

    print("\n🎯 REORGANIZATION PRIORITIES:")
    print("1. IMMEDIATE: Enhance 7 core modules to be self-sufficient")
    print("2. HIGH: Merge 12 directories into appropriate modules")
    print("3. MEDIUM: Consolidate tools and utilities")
    print("4. LOW: Archive unclear/temporary directories")

    # Count total files to be moved
    total_files_to_move = 0
    for directory in plan["categories"]["should_be_submodules"]:
        total_files_to_move += plan["detailed_analysis"][directory]["file_count"]

    print(f"\n📦 Total Python files to reorganize: {total_files_to_move}")


if __name__ == "__main__":
    main()
