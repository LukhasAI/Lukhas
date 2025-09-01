# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: meta_learning_recovery.py
# MODULE: learning.meta_learning_recovery
# DESCRIPTION: Tool for recovering Meta Learning and Adaptive AI components from
#              a LUKHAS backup directory, converting them to the LUKHAS format.
# DEPENDENCIES: os, shutil, pathlib, datetime, json, typing, structlog
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ΛORIGIN_AGENT: Jules-04
# ΛTASK_ID: 171-176
# ΛCOMMIT_WINDOW: pre-audit
# ΛAPPROVED_BY: Human Overseer (GRDM)
# ΛUDIT: Standardized header/footer, added comments, normalized logger,
# applied ΛTAGs. Corrected class name.

#!/usr/bin/env python3
"""
lukhasMetaLearningRecovery.py - Recovery tool for Meta Learning and Adaptive AI components

This tool specifically targets the Meta Learning and Adaptive AI systems
from the LUKHAS backup directory.
"""

import ast
import json
import os
from collections import defaultdict
from datetime import datetime  # Use datetime directly
from pathlib import Path
from typing import Any, Optional  # Added Any, Optional

# ΛTRACE: Initialize logger for learning phase (or recovery tool context)


# # MetaLearningRecovery class
# ΛEXPOSE: Main class for the recovery tool.
class MetaLearningRecovery:
    """
    Tool for recovering Meta Learning and Adaptive AI components from backups
    and integrating them into the LUKHAS workspace.
    """

    # # Initialization
    def __init__(self):
        # ΛNOTE: Hardcoded paths are specific to a particular environment.
        # ΛCAUTION: Hardcoded paths like /Users/A_G_I/ make this script not portable.
        self.workspace_root = Path(os.getcwd())  # Changed to current working directory for portability within repo
        self.recovery_log: list[dict[str, Any]] = []  # Type hint

        # ΛNOTE: Source path for recovery.
        # ΛCAUTION: This path is absolute and system-specific.
        self.meta_learning_source = "/Users/A_G_I/Archive/old_git_repos/Library/Mobile Documents/com~apple~CloudDocs/LUKHAS_BACKUP_20250530/LUKHAS/CORE/Adaptative_AGI/Meta_Learning"
        # ΛSEED: Target mapping defines where recovered components are placed,
        # seeding the new structure.
        self.target_mapping = {
            "meta_learning": "core/meta_learning",
            "adaptive_agi": "core/adaptive_agi",
            "learning": "brain/learning",  # Potentially learning/ within current context
            "adaptation": "brain/adaptation",
            "intelligence": "core/intelligence",
            "cognitive": "brain/cognitive",
        }
        # ΛTRACE: MetaLearningRecovery initialized
        logger.info(
            "meta_learning_recovery_initialized",
            workspace_root=str(self.workspace_root),
            source=self.meta_learning_source,
        )

    # # Explore the Meta Learning backup directory structure
    # ΛEXPOSE: Method to scan and categorize files in the backup source.
    def explore_meta_learning_directory(self) -> dict[str, Any]:  # Type hint for return
        """Explore the Meta Learning directory structure"""
        # ΛTRACE: Exploring meta-learning directory
        logger.info(
            "explore_meta_learning_directory_start",
            source_path=self.meta_learning_source,
        )
        exploration_result: dict[str, Any] = {  # Type hint
            "source_path": self.meta_learning_source,
            "exists": False,
            "total_files": 0,
            "python_files": 0,
            "directories": [],
            "files": [],
            "meta_learning_components": [],
            "adaptive_components": [],
            "learning_components": [],
        }

        source_path_obj = Path(self.meta_learning_source)  # Use Path object
        if not source_path_obj.exists():
            logger.error("meta_learning_source_not_found", path=self.meta_learning_source)
            # print(f"❌ Meta Learning source not found: {self.meta_learning_source}")
            # # Replaced with logger
            return exploration_result

        exploration_result["exists"] = True
        logger.info("exploring_meta_learning_directory", path=self.meta_learning_source)
        # print(f"🔍 Exploring Meta Learning directory:
        # {self.meta_learning_source}") # Replaced

        try:
            for root, dirs, files in os.walk(self.meta_learning_source):
                root_path = Path(root)  # Use Path object
                exploration_result["directories"].extend([str(root_path / d) for d in dirs])
                for file_name in files:  # Renamed file to file_name
                    file_path = root_path / file_name
                    rel_path = str(file_path.relative_to(source_path_obj))
                    exploration_result["total_files"] += 1
                    exploration_result["files"].append(rel_path)

                    if file_name.endswith(".py"):
                        exploration_result["python_files"] += 1
                        file_lower = file_name.lower()
                        # ΛNOTE: Categorization based on keywords in filenames.
                        if any(term in file_lower for term in ["meta_learning", "metalearning", "meta"]):
                            exploration_result["meta_learning_components"].append(rel_path)
                        elif any(term in file_lower for term in ["adaptive", "adaptation", "adapt"]):
                            exploration_result["adaptive_components"].append(rel_path)
                        elif any(term in file_lower for term in ["learning", "learn", "train"]):
                            exploration_result["learning_components"].append(rel_path)
                        logger.debug("python_file_found_for_recovery", path=rel_path)
                        # print(f"   📄 Found: {rel_path}") # Replaced
        except Exception as e:
            logger.error("error_exploring_directory_meta_recovery", error=str(e), exc_info=True)
            # print(f"❌ Error exploring directory: {e}") # Replaced

        logger.info(
            "exploration_complete_meta_recovery",
            total_files=exploration_result["total_files"],
            py_files=exploration_result["python_files"],
        )
        # print statements replaced by logging above or not necessary for agent
        return exploration_result

    # # Convert filename and content to LUKHAS format
    def convert_to_lukhas_format(
        self, filename: str, content: Optional[str] = None
    ) -> tuple[str, Optional[str]]:  # Added Optional, type hint
        """Convert filename and content to lukhas format"""
        # ΛNOTE: Renames files and potentially class names within content to 'lukhas' prefix and PascalCase.
        # ΛCAUTION: String replacement for class names can be brittle. AST modification would be safer.
        # ΛTRACE: Converting to LUKHAS format
        logger.debug("convert_to_lukhas_format_start", original_filename=filename)
        new_filename, new_content = filename, content
        if filename.endswith(".py"):
            base_name = filename[:-3]  # More robust than replace
            if not base_name.lower().startswith("lukhas"):  # Check case-insensitively
                # Special handling for known component types
                if "meta_learning" in base_name.lower():
                    new_pascal_name = (
                        f"MetaLearning{base_name.lower().replace('meta_learning', '').replace('_', '').title()}"
                    )
                elif "adaptive" in base_name.lower():
                    new_pascal_name = f"Adaptive{base_name.lower().replace('adaptive', '').replace('_', '').title()}"
                elif "learning" in base_name.lower():
                    new_pascal_name = f"Learning{base_name.lower().replace('learning', '').replace('_', '').title()}"
                else:
                    new_pascal_name = "".join(word.capitalize() for word in base_name.split("_"))
                new_filename = f"lukhas{new_pascal_name}.py"

            if content:  # Process content only if provided
                new_content_lines = []
                for line in content.splitlines():
                    stripped_line = line.strip()
                    if stripped_line.startswith("class ") and "lukhas" not in stripped_line.lower():
                        # Attempt to extract class name more robustly
                        try:
                            class_name_match = ast.parse(line).body[0]  # type: ignore
                            if isinstance(class_name_match, ast.ClassDef):
                                old_class_name = class_name_match.name
                                if not old_class_name.lower().startswith("lukhas"):
                                    # Similar special handling for class names
                                    if "meta_learning" in old_class_name.lower():
                                        new_pascal_class = f"MetaLearning{old_class_name.lower().replace('meta_learning', '').replace('_', '').title()}"
                                    elif "adaptive" in old_class_name.lower():
                                        new_pascal_class = f"Adaptive{old_class_name.lower().replace('adaptive', '').replace('_', '').title()}"
                                    else:
                                        new_pascal_class = "".join(
                                            word.capitalize() for word in old_class_name.split("_")
                                        )
                                    new_lukhas_class_name = f"lukhas{new_pascal_class}"
                                    line = line.replace(
                                        f"class {old_class_name}",
                                        f"class {new_lukhas_class_name}",
                                    )
                                    logger.debug(
                                        "class_name_converted_lukhas_format",
                                        old=old_class_name,
                                        new=new_lukhas_class_name,
                                    )
                        except SyntaxError:
                            logger.warn(
                                "syntax_error_parsing_class_line_lukhas_format",
                                line_content=line,
                            )  # Could not parse, leave as is
                    new_content_lines.append(line)
                new_content = "\n".join(new_content_lines)
        # ΛTRACE: LUKHAS format conversion result
        logger.debug(
            "convert_to_lukhas_format_end",
            new_filename=new_filename,
            content_changed=content != new_content,
        )
        return new_filename, new_content

    # # Determine the appropriate target directory for a component
    def determine_target_directory(self, file_path_str: str) -> str:  # Renamed file_path to file_path_str
        """Determine the appropriate target directory for a component"""
        # ΛNOTE: Uses keywords in file path to map to target directories.
        # ΛTRACE: Determining target directory
        logger.debug("determine_target_directory_start", file_path=file_path_str)
        file_lower = file_path_str.lower()
        for keyword, target_key in [
            ("meta_learning", "meta_learning"),
            ("metalearning", "meta_learning"),
            ("adaptive", "adaptive_agi"),
            ("adaptation", "adaptive_agi"),
            ("learning", "learning"),
            ("learn", "learning"),  # "learning" keyword maps to "brain/learning"
            ("cognitive", "cognitive"),
            ("cognition", "cognitive"),
            ("intelligence", "intelligence"),
            ("intelligent", "intelligence"),
        ]:
            if keyword in file_lower:
                # ΛTRACE: Target directory determined
                logger.debug(
                    "target_directory_determined",
                    keyword=keyword,
                    target_key=self.target_mapping[target_key],
                )
                return self.target_mapping[target_key]
        # ΛTRACE: Default target directory used
        logger.debug(
            "default_target_directory_used",
            default_key=self.target_mapping["meta_learning"],
        )
        return self.target_mapping["meta_learning"]

    # # Recover all Meta Learning components based on exploration results
    # ΛEXPOSE: Main method to perform the recovery of components.
    def recover_meta_learning_components(self, exploration_result: dict[str, Any]) -> dict[str, Any]:  # Type hints
        """Recover all Meta Learning components"""
        # ΛDREAM_LOOP: If this recovery process learns or adapts over time (e.g., improving categorization), it's a learning loop.
        # ΛTRACE: Recovering meta-learning components
        logger.info("recover_meta_learning_components_start")
        recovery_result: dict[str, Any] = {  # Type hint
            "timestamp": datetime.now().isoformat(),
            "source_directory": self.meta_learning_source,
            "components_processed": 0,
            "components_successful": 0,
            "total_files_recovered": 0,
            "files_recovered": [],
            "errors": [],
        }

        if not exploration_result.get("exists"):  # Use .get for safety
            recovery_result["errors"].append("Source directory does not exist for recovery")
            logger.error(
                "source_directory_not_exist_for_recovery",
                path=self.meta_learning_source,
            )
            return recovery_result

        logger.info("starting_meta_learning_component_recovery_process")
        # print("\n🚀 Starting Meta Learning Component Recovery...") # Replaced

        for file_rel_path in exploration_result.get("files", []):  # Use .get
            if not file_rel_path.endswith(".py"):
                continue

            source_file_path = Path(self.meta_learning_source) / file_rel_path  # Use Path object
            recovery_result["components_processed"] += 1
            try:
                with open(source_file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                filename = source_file_path.name
                new_filename, new_content = self.convert_to_lukhas_format(filename, content)

                target_dir_key = self.determine_target_directory(file_rel_path)
                # Ensure target path is relative to workspace_root for consistency
                relative_target_dir = Path(
                    self.target_mapping.get(target_dir_key, self.target_mapping["meta_learning"])
                )  # Use .get

                # Handle subdirectories from original path
                original_subdir = Path(file_rel_path).parent
                final_target_dir = self.workspace_root / relative_target_dir / original_subdir
                final_target_dir.mkdir(parents=True, exist_ok=True)

                target_path = final_target_dir / new_filename
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(new_content or "")  # Ensure new_content is not None

                recovery_result["files_recovered"].append(
                    {
                        "original": file_rel_path,
                        "new_filename": new_filename,
                        "target_path": str(target_path),
                        "target_category": target_dir_key,  # Use target_dir_key
                        "size": len(content),
                    }
                )
                recovery_result["components_successful"] += 1
                recovery_result["total_files_recovered"] += 1
                logger.info(
                    "file_recovered_successfully",
                    original=file_rel_path,
                    new_name=new_filename,
                    target=str(target_path),
                )
                # print(f"✅ Recovered: {file_rel_path} → {new_filename}") # Replaced
                # print(f"   Target: {target_path}") # Replaced
            except Exception as e:
                error_msg = f"Failed to recover {file_rel_path}: {e!s}"
                recovery_result["errors"].append(error_msg)
                logger.error(
                    "file_recovery_failed",
                    file=file_rel_path,
                    error=error_msg,
                    exc_info=True,
                )
                # print(f"❌ {error_msg}") # Replaced
        # ΛTRACE: Meta-learning components recovery finished
        logger.info(
            "recover_meta_learning_components_end",
            processed=recovery_result["components_processed"],
            successful=recovery_result["components_successful"],
        )
        return recovery_result

    # # Execute complete Meta Learning recovery operation
    # ΛEXPOSE: Main entry point to run the entire recovery process.
    def execute_recovery(self) -> dict[str, Any]:  # Type hint
        """Execute complete Meta Learning recovery operation"""
        # ΛTRACE: Executing full recovery
        logger.info("execute_full_recovery_start")
        # print("🚀 Starting Meta Learning & Adaptive AI Component Recovery...") # Replaced
        # print("=" * 70) # Replaced

        exploration_result = self.explore_meta_learning_directory()
        if not exploration_result.get("exists"):  # Use .get
            logger.critical(
                "cannot_proceed_recovery_source_dir_not_found",
                path=self.meta_learning_source,
            )
            # print("❌ Cannot proceed - source directory not found") # Replaced
            return {
                "error": "Source directory not found",
                "exploration": exploration_result,
                "recovery": {},
            }  # Return exploration too

        recovery_result = self.recover_meta_learning_components(exploration_result)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")  # Renamed timestamp to timestamp_str
        # Renamed report_file
        report_filename = f"lukhasMetaLearning_Recovery_Report_{timestamp_str}.json"
        report_path = self.workspace_root / report_filename  # Use Path object

        complete_report = {
            "exploration": exploration_result,
            "recovery": recovery_result,
        }
        try:
            with open(report_path, "w") as f:
                json.dump(complete_report, f, indent=2, default=str)  # Added default=str for non-serializable
            logger.info("recovery_report_saved", path=str(report_path))
        except Exception as e:
            logger.error(
                "failed_to_save_recovery_report",
                path=str(report_path),
                error=str(e),
                exc_info=True,
            )

        # Summary logging
        logger.info(
            "meta_learning_recovery_summary",
            source=self.meta_learning_source,
            processed=recovery_result["components_processed"],
            successful=recovery_result["components_successful"],
            errors=len(recovery_result["errors"]),
            report_file=str(report_path),
        )

        if recovery_result.get("files_recovered"):  # Use .get
            target_counts: dict[str, int] = defaultdict(int)  # Use defaultdict
            for file_info in recovery_result["files_recovered"]:
                target_counts[file_info["target_category"]] += 1
            logger.info("components_by_category_summary", counts=dict(target_counts))  # Convert to dict for logging
        # print statements replaced by logging
        # ΛTRACE: Full recovery execution finished
        logger.info("execute_full_recovery_end")
        return complete_report


# # Main function for script execution
def main():
    """Main execution function for the recovery script."""
    # ΛTRACE: main function called for recovery script
    logger.info("meta_learning_recovery_script_main_start")
    recovery_tool = MetaLearningRecovery()  # Corrected class name
    results = recovery_tool.execute_recovery()

    if (
        "error" not in results and results.get("recovery", {}).get("components_successful", 0) > 0
    ):  # Check nested dicts carefully
        logger.info(
            "meta_learning_recovery_script_success",
            recovered_files=results["recovery"]["total_files_recovered"],
        )
        # print statements for CLI users, agent doesn't need them
    else:
        logger.warn(
            "meta_learning_recovery_script_no_components_recovered",
            error=results.get("error"),
        )
    # ΛTRACE: main function finished
    logger.info("meta_learning_recovery_script_main_end")


if __name__ == "__main__":
    # ΛNOTE: Standard Python entry point.
    main()

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: meta_learning_recovery.py
# VERSION: 1.1 (Jules-04 update)
# TIER SYSTEM: Tool / Utility
# ΛTRACE INTEGRATION: ENABLED (structlog)
# CAPABILITIES: Explores backup directories, converts filenames and class names to LUKHAS format,
#               recovers components to specified target directories, generates recovery reports.
# FUNCTIONS: MetaLearningRecovery (class with methods), main
# CLASSES: MetaLearningRecovery
# DECORATORS: None
# DEPENDENCIES: os, pathlib, datetime, json, typing, structlog, ast (for class name conversion)
# INTERFACES: `MetaLearningRecovery.execute_recovery()`
# ERROR HANDLING: Logs errors during file operations and exploration. Returns error dict on critical failure.
# LOGGING: ΛTRACE_ENABLED via structlog, bound with tag="meta_learning_recovery".
# AUTHENTICATION: N/A (File system operations)
# HOW TO USE:
#   Instantiate `MetaLearningRecovery()` and call `execute_recovery()`.
#   Ensure the `meta_learning_source` path in `__init__` points to the correct backup location.
#   Workspace root is currently set to CWD, adjust if necessary.
# INTEGRATION NOTES: Highly dependent on specific backup directory structures and file naming conventions.
#                    Filename and class name conversion logic is rule-based and might need refinement.
#                    Hardcoded paths should ideally be configurable.
# MAINTENANCE: Update path configurations if backup locations change.
#              Refine filename/classname conversion rules if new patterns emerge.
#              Consider making paths configurable via arguments or a config file.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
