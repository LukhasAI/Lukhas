#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: generate_autotest_docs.py
# MODULE: core.generate_autotest_docs
# DESCRIPTION: Generates LukhasDoc style documentation (Markdown and JSON) for the
#              core.automatic_testing_system.py module by parsing its content.
# DEPENDENCIES: sys, os, json, re, pathlib, datetime, typing, logging
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List  # Added List

# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.core.generate_autotest_docs")
# Basic configuration for the logger if no handlers are present
if not logging.getLogger("ΛTRACE").handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - ΛTRACE: %(message)s",
    )

logger.info("ΛTRACE: Initializing generate_autotest_docs script.")


# Human-readable comment: Extracts symbolic header blocks and key information from core.common files.
# TODO: Consider using the `ast` module for more robust parsing of Python code structure.
def extract_symbolic_blocks(file_content: str) -> Dict[str, Any]:
    """
    Extracts symbolic header blocks, main docstring, class/function definitions,
    and features from the content of a LUKHAS Python file.
    Args:
        file_content (str): The string content of the Python file.
    Returns:
        Dict[str, Any]: A dictionary containing extracted information.
    """
    logger.debug("ΛTRACE: Extracting symbolic blocks from file content.")
    # Extract the main docstring (module-level)
    # Assumes it's at the beginning of the file, possibly after shebang or encoding.
    main_doc_match = re.search(
        r'^(?:#![^\n]*\n)?(?:#.*coding[=:]\s*([-\w.]+).*\n)?\s*"""([\s\S]*?)"""',
        file_content,
        re.MULTILINE,
    )
    main_docstring = main_doc_match.group(2).strip() if main_doc_match else ""
    if not main_docstring:  # Fallback for docstrings not at the very top
        main_doc_match_alt = re.search(r'"""([\s\S]*?)"""', file_content)
        main_docstring = (
            main_doc_match_alt.group(1).strip() if main_doc_match_alt else ""
        )

    logger.debug(
        f"ΛTRACE: Extracted main docstring (first 50 chars): '{main_docstring[:50]}...'"
    )

    # Extract class definitions
    classes: List[Dict[str, str]] = []
    # Regex to find 'class ClassName(PossibleBase):' or 'class ClassName:' followed by its docstring
    class_matches = re.finditer(
        r'^class\s+(\w+)(?:\([\w\s,.]*\))?:\s*"""([\s\S]*?)"""',
        file_content,
        re.MULTILINE,
    )
    for match in class_matches:
        classes.append(
            {
                "name": match.group(1),
                "docstring": match.group(2)
                .strip()
                .replace('"""', ""),  # Clean up quotes if captured
            }
        )
    logger.debug(f"ΛTRACE: Extracted {len(classes)} classes.")

    # Extract function definitions (both async and regular)
    functions: List[Dict[str, str]] = []
    # Regex to find 'def func_name(params):' or 'async def func_name(params):' followed by its docstring
    func_matches = re.finditer(
        r'^(?:async\s+)?def\s+(\w+)\([^)]*\)(?:\s*->\s*[\w\[\], .\s]+)?:\s*"""([\s\S]*?)"""',
        file_content,
        re.MULTILINE,
    )
    for match in func_matches:
        functions.append(
            {
                "name": match.group(1),
                "docstring": match.group(2)
                .strip()
                .replace('"""', ""),  # Clean up quotes
            }
        )
    logger.debug(f"ΛTRACE: Extracted {len(functions)} functions.")

    # Extract key features from the main docstring (example, adapt as needed)
    # This part is highly dependent on the specific docstring format.
    features: List[str] = []
    if main_docstring:
        # Example: looking for a section like "Core Features:"
        feature_section_match = re.search(
            r"Core Features:\s*\n((?:-\s*.*\n)+)", main_docstring, re.IGNORECASE
        )
        if feature_section_match:
            feature_lines_str = feature_section_match.group(1)
            feature_lines = [
                line.strip()[1:].strip()
                for line in feature_lines_str.split("\n")
                if line.strip().startswith("-")
            ]
            features.extend(feature_lines)
    logger.debug(f"ΛTRACE: Extracted {len(features)} features from main docstring.")

    return {
        "main_docstring": main_docstring,
        "classes": classes,
        "functions": functions,
        "features": features,
    }


# Human-readable comment: Generates LukhasDoc style documentation for a Python file.
def generate_lambda_doc(file_path: Path) -> Dict[str, Any]:
    """
    Generates LukhasDoc style documentation dictionary for a given Python file.
    Args:
        file_path (Path): Path object for the Python file to document.
    Returns:
        Dict[str, Any]: A dictionary structured for LukhasDoc.
    Raises:
        FileNotFoundError: If the specified file_path does not exist.
    """
    logger.info(f"ΛTRACE: Generating LukhasDoc for file: {file_path}")
    if not file_path.is_file():
        logger.error(f"ΛTRACE: Source file not found: {file_path}")
        raise FileNotFoundError(f"Source file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    logger.debug(f"ΛTRACE: Read {len(content)} characters from {file_path.name}.")

    blocks = extract_symbolic_blocks(content)

    # Attempt to extract version from a standard header if present
    version = "1.0.0"  # Default
    header_version_match = re.search(r"# VERSION:\s*([\w.-]+)", content, re.IGNORECASE)
    if header_version_match:
        version = header_version_match.group(1)
        logger.debug(f"ΛTRACE: Extracted version {version} from file header.")

    # Create comprehensive documentation structure
    # This structure should be consistent with LUKHAS documentation standards.
    documentation = {
        "title": f"LUKHAS AGI - Module Documentation: {file_path.stem}",
        "subtitle": blocks.get(
            "main_docstring", "Module providing core functionalities."
        ).split("\n")[
            0
        ],  # First line of main docstring
        "generated_by": "LukhasDoc - LUKHAS Symbolic Documentation Engine",
        "timestamp": datetime.now().isoformat(),
        "version": version,
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size_lines": len(content.split("\n")),
        "overview": {
            "description": blocks.get("main_docstring", "N/A"),
            # This is an example; actual design philosophy should be sourced or standardized.
            "design_philosophy": [
                "Clarity and Maintainability",
                "Robustness and Reliability",
                "Adherence to LUKHAS Standards",
            ],
            "core_capabilities": blocks.get("features", []),
        },
        "architecture": {
            "classes": blocks.get("classes", []),
            "functions": blocks.get("functions", []),
            # Key components might be manually defined or inferred if possible
            "key_components": [cls["name"] for cls in blocks.get("classes", [])],
        },
        # API Reference and Usage Examples would ideally be more detailed or standardized
        "api_reference": {
            "notes": "Refer to class and function docstrings for detailed API information."
        },
        "usage_examples": {
            "notes": "See module-specific tests or examples for usage patterns."
        },
        "symbolic_metadata": {  # Extract from standard header if possible, or use defaults
            "lukhas_signature": f"ΛTRACE: {file_path.stem} initialized",  # Example
            "symbolic_scope": f"LUKHAS AGI Core - {file_path.stem}",
            "tier_system": "Refer to file header",  # Placeholder
            "license": "PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED",  # Default
        },
    }
    logger.info(f"ΛTRACE: Documentation dictionary generated for {file_path.name}.")
    return documentation


# Human-readable comment: Exports the generated documentation data to a Markdown file.
def export_to_markdown(doc_data: Dict[str, Any], output_path: Path) -> None:
    """
    Exports documentation data to a formatted Markdown file.
    Args:
        doc_data (Dict[str, Any]): The documentation dictionary.
        output_path (Path): The path to save the Markdown file.
    """
    logger.info(f"ΛTRACE: Exporting documentation to Markdown: {output_path}")
    md_content = f"# {doc_data['title']}\n\n"
    md_content += f"> {doc_data['subtitle']}\n\n"
    md_content += f"**Generated by:** {doc_data['generated_by']}\n"
    md_content += f"**Version:** {doc_data['version']}\n"
    md_content += f"**Generated:** {doc_data['timestamp']}\n"
    md_content += (
        f"**File:** `{doc_data['file_name']}` ({doc_data['file_size_lines']} lines)\n\n"
    )
    md_content += "---\n\n"

    md_content += "## 🌟 Overview\n\n"
    md_content += f"{doc_data['overview']['description']}\n\n"
    if doc_data["overview"]["core_capabilities"]:
        md_content += "### ⚡ Core Capabilities\n\n"
        for capability in doc_data["overview"]["core_capabilities"]:
            md_content += f"- {capability}\n"
        md_content += "\n"

    md_content += "---\n\n## 🏗️ Architecture\n\n"
    if doc_data["architecture"]["classes"]:
        md_content += f"### 📚 Classes ({len(doc_data['architecture']['classes'])})\n\n"
        for cls in doc_data["architecture"]["classes"]:
            md_content += (
                f"#### `{cls['name']}`\n\n```python\n{cls['docstring']}\n```\n\n"
            )

    if doc_data["architecture"]["functions"]:
        md_content += (
            f"### 🔧 Functions ({len(doc_data['architecture']['functions'])})\n\n"
        )
        for func in doc_data["architecture"]["functions"]:
            md_content += (
                f"#### `{func['name']}()`\n\n```python\n{func['docstring']}\n```\n\n"
            )

    md_content += "---\n\n## 🔮 Symbolic Metadata (from source header if available)\n\n"
    # Attempt to pull from source file's actual footer block
    # This is a simplified extraction, real headers are more complex
    source_file_path = Path(doc_data["file_path"])
    if source_file_path.exists():
        with open(source_file_path, encoding="utf-8") as f_source:
            source_content = f_source.read()
        footer_match = re.search(
            r"# ═══════════════════════════════════════════════════════════════════════════\n# FILENAME:.*?\n(# .*?\n)*# ═══════════════════════════════════════════════════════════════════════════",
            source_content,
            re.MULTILINE | re.DOTALL,
        )
        if footer_match:
            # Extract relevant lines from the matched footer block
            footer_lines = footer_match.group(0).splitlines()
            symbolic_info_extracted = []
            keywords_to_extract = [
                "VERSION:",
                "TIER SYSTEM:",
                "ΛTRACE INTEGRATION:",
                "CAPABILITIES:",
                "LICENSE:",
            ]
            for line in footer_lines:
                if any(keyword in line for keyword in keywords_to_extract):
                    symbolic_info_extracted.append(
                        line.strip("# ").strip()
                    )  # Clean up line
            if symbolic_info_extracted:
                md_content += "```\n" + "\n".join(symbolic_info_extracted) + "\n```\n\n"
            else:
                md_content += "_Symbolic metadata block not found or keywords missing in source file footer._\n\n"

    md_content += "\n---\n\n*Documentation generated by LukhasDoc - LUKHAS Symbolic Documentation Engine*\n"
    md_content += "**ΛSIGNATURE:** This document reflects the structure and embedded comments of the source file. Accuracy depends on the source file's adherence to LUKHAS documentation standards.\n"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info(
            f"ΛTRACE: Markdown documentation successfully saved to {output_path}"
        )
    except OSError as e:
        logger.error(
            f"ΛTRACE: Failed to write Markdown file to {output_path}: {e}",
            exc_info=True,
        )


# Human-readable comment: Main function to drive the documentation generation process.
def main():
    """Generates LukhasDoc documentation for the automatic_testing_system.py."""
    logger.info("ΛTRACE: Starting main documentation generation process.")
    logger.info(
        "🚀 LukhasDoc Documentation Generator for LUKHAS Automatic Testing System"
    )
    logger.info("=" * 80)

    try:
        # Determine paths relative to this script file
        script_dir = Path(__file__).parent.resolve()  # 'core' directory
        project_root = script_dir.parent  # Parent of 'core'

        # Source file is core/automatic_testing_system.py
        source_file_path = script_dir / "automatic_testing_system.py"
        # Output directory is core/docs/
        output_dir_path = script_dir / "docs"

        logger.info(f"ΛTRACE: Source file path: {source_file_path}")
        logger.info(f"ΛTRACE: Output directory path: {output_dir_path}")

        if not source_file_path.is_file():
            logger.critical(
                f"ΛTRACE: Source file '{source_file_path}' not found. Cannot generate documentation."
            )
            logger.error(
                f"❌ ERROR: Source file '{source_file_path}' not found. Please ensure it exists."
            )
            sys.exit(1)

        output_dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ΛTRACE: Ensured output directory exists: {output_dir_path}")

        logger.info(f"📖 Analyzing source file: {source_file_path.name}")
        doc_data = generate_lambda_doc(source_file_path)
        logger.info(
            f"ΛTRACE: Documentation data generated for {source_file_path.name}."
        )

        # Export to JSON
        json_output_path = output_dir_path / f"{source_file_path.stem}_docs.json"
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        logger.info(f"ΛTRACE: JSON documentation saved to: {json_output_path}")
        logger.info(f"💾 JSON documentation saved: {json_output_path}")

        # Export to Markdown
        md_output_path = (
            output_dir_path / f"{source_file_path.stem.upper()}_DOCUMENTATION.md"
        )
        export_to_markdown(doc_data, md_output_path)
        # export_to_markdown will log success/failure
        logger.info(f"📝 Markdown documentation saved: {md_output_path}")

        logger.info("\n🎉 LukhasDoc documentation generation completed successfully!")
        logger.info(f"📂 View Markdown documentation: {md_output_path}")
        logger.info(f"📂 View JSON data: {json_output_path}")

    except FileNotFoundError as e_fnf:
        logger.critical(
            f"ΛTRACE: File not found during documentation generation: {e_fnf}",
            exc_info=True,
        )
        logger.error(f"❌ FILE NOT FOUND ERROR: {e_fnf}")
        sys.exit(1)
    except Exception as e:
        logger.critical(
            f"ΛTRACE: An unexpected error occurred during documentation generation: {e}",
            exc_info=True,
        )
        logger.error(f"❌ AN UNEXPECTED ERROR OCCURRED: {e}")
        logger.error("Traceback information logged separately")
        sys.exit(1)


# Human-readable comment: Standard execution block for when the script is run directly.
if __name__ == "__main__":
    logger.info("ΛTRACE: generate_autotest_docs.py executed as __main__.")
    main()

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: generate_autotest_docs.py
# VERSION: 1.1.0
# TIER SYSTEM: Not applicable (Documentation Generation Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Parses Python source files (specifically automatic_testing_system.py)
#               to extract docstrings, class/function definitions, and other metadata.
#               Generates documentation in JSON and Markdown formats.
# FUNCTIONS: extract_symbolic_blocks, generate_lambda_doc, export_to_markdown, main
# CLASSES: None
# DECORATORS: None
# DEPENDENCIES: sys, os, json, re, pathlib, datetime, typing, logging, traceback
# INTERFACES: Command-line execution (__main__ block).
# ERROR HANDLING: Catches FileNotFoundError and other general exceptions during execution.
#                 Logs errors and exits with a non-zero status code on failure.
# LOGGING: ΛTRACE_ENABLED for tracing script execution, file operations, and parsing steps.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   Run as a standalone Python script: python core/generate_autotest_docs.py
#   It will generate documentation for 'core/automatic_testing_system.py'
#   and place it in the 'core/docs/' directory.
# INTEGRATION NOTES: Relies on specific docstring formats and comment patterns (e.g., # VERSION:)
#                    for some metadata extraction. Regex-based parsing might need adjustments
#                    if source code style changes significantly.
# MAINTENANCE: Update regexes if Python syntax or docstring conventions change.
#              Ensure output paths and source file paths are correctly configured or derived.
#              Consider enhancing parsing robustness (e.g., using 'ast' module).
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
