#!/usr/bin/env python3

"""
AI - Import Path Fixer

Copyright (c) 2025 AI Development Team
All rights reserved.

This file is part of the AI system, an artificial intelligence
platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This tool automatically fixes broken import paths by finding actual module
locations, updating import statements, creating missing service modules, and
fixing common import patterns.
"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportPathAnalyzer:
    """Analyzes and maps import paths to actual file locations."""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.module_registry = {}  # actual_path -> module_info
        self.import_failures = []
        self.fixes_applied = []

    def build_module_registry(self):
        """Build registry of all actual Python modules."""
        logger.info("Building module registry...")

        for py_file in self.root_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue

            try:
                # Get module path relative to root
                rel_path = py_file.relative_to(self.root_path)
                module_path = str(rel_path).replace("/", ".").replace(".py", "")

                # Skip if it's a broken symlink
                if not py_file.exists():
                    continue

                # Store module info
                self.module_registry[module_path] = {
                    "file_path": py_file,
                    "module_path": module_path,
                    "directory": py_file.parent,
                    "name": py_file.stem,
                }

            except Exception as e:
                logger.debug(f"Skipping {py_file}: {e}")

        logger.info(f"Found {len(self.module_registry)} valid modules")

    def find_best_match(self, broken_import: str) -> Optional[str]:
        """Find the best matching module for a broken import."""

        # Direct match first
        if broken_import in self.module_registry:
            return broken_import

        # Remove 'lukhas.' prefix if present for matching
        clean_import = broken_import.replace("lukhas.", "")

        # Look for exact matches without lukhas prefix
        if clean_import in self.module_registry:
            return clean_import

        # Split import into parts for fuzzy matching
        import_parts = clean_import.split(".")

        best_match = None
        best_score = 0

        for module_path in self.module_registry:
            module_parts = module_path.split(".")

            # Calculate match score
            score = 0

            # Exact part matches
            for part in import_parts:
                if part in module_parts:
                    score += 2

            # End match bonus (file name match)
            if import_parts[-1] == module_parts[-1]:
                score += 5

            # Directory structure match
            if len(import_parts) > 1 and len(module_parts) > 1:
                if import_parts[-2] == module_parts[-2]:  # Parent directory match
                    score += 3

            # Substring matches
            for i_part in import_parts:
                for m_part in module_parts:
                    if i_part in m_part or m_part in i_part:
                        score += 1

            if score > best_score:
                best_score = score
                best_match = module_path

        # Only return if we have a decent match
        if best_score >= 3:
            return best_match

        return None

    def create_missing_service_modules(self) -> List[str]:
        """Create missing service layer modules."""

        # Common service patterns that are missing
        service_patterns = [
            "creativity.creativity_service",
            "learning.learning_service",
            "memory.memory_service",
            "ethics.ethics_service",
            "quantum.quantum_service",
            "trace.drift_metrics",
            "core.symbolic.symbolic_drift_tracker",
        ]

        created_services = []

        for service_pattern in service_patterns:
            if service_pattern not in self.module_registry:
                # Create the service module
                service_parts = service_pattern.split(".")
                service_dir = self.root_path / "/".join(service_parts[:-1])
                service_file = service_dir / f"{service_parts[-1]}.py"

                # Create directory if it doesn't exist
                service_dir.mkdir(parents=True, exist_ok=True)

                # Generate service module content
                service_content = self.generate_service_module(service_pattern)

                try:
                    with open(service_file, "w") as f:
                        f.write(service_content)

                    created_services.append(service_pattern)
                    logger.info(f"Created service module: {service_file}")

                    # Add to registry
                    self.module_registry[service_pattern] = {
                        "file_path": service_file,
                        "module_path": service_pattern,
                        "directory": service_dir,
                        "name": service_parts[-1],
                    }

                except Exception as e:
                    logger.error(f"Failed to create {service_file}: {e}")

        return created_services

    def generate_service_module(self, service_pattern: str) -> str:
        """Generate a basic service module."""

        parts = service_pattern.split(".")
        service_name = parts[-1].replace("_", " ").title().replace(" ", "")
        subsystem = parts[0].title()

        return f'''"""
AI System - {service_name}
Path: {'/'.join(parts)}.py
Generated: 2025-07-24
Author: AI Team (Auto-generated)

{subsystem} service layer for AI system.
This module provides service interfaces for {parts[0]} subsystem operations.

Tags: [SERVICE, {subsystem.upper()}, GENERATED]
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure module logger
logger = logging.getLogger(__name__)

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "{service_pattern}"

class {service_name}:
    """
    {subsystem} service for AI system.

    Provides centralized interface for {parts[0]} operations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize {service_name}."""
        self.config = config or {{}}
        self.logger = logging.getLogger(f"ai.{{MODULE_NAME}}")
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize the service."""
        try:
            # Service initialization logic here
            self.initialized = True
            self.logger.info(f"{service_name} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {service_name}: {{e}}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {{
            "service": MODULE_NAME,
            "version": MODULE_VERSION,
            "initialized": self.initialized,
            "timestamp": datetime.now().isoformat()
        }}

# Default service instance
default_service = {service_name}()

def get_service() -> {service_name}:
    """Get default service instance."""
    return default_service

# Service interface functions
def initialize_service(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize the {parts[0]} service."""
    if config:
        global default_service
        default_service = {service_name}(config)
    return default_service.initialize()

def get_service_status() -> Dict[str, Any]:
    """Get {parts[0]} service status."""
    return default_service.get_status()

# Module exports
__all__ = [
    '{service_name}',
    'default_service',
    'get_service',
    'initialize_service',
    'get_service_status'
]

"""
AI System Module Footer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Module: {service_pattern}
Status: AUTO-GENERATED SERVICE LAYER
Compliance: AI Standards v1.0
Generated: 2025-07-24

Key Capabilities:
- Service initialization and management
- Status monitoring and health checks
- Configuration management
- Logging and error handling

Dependencies: Core AI modules
Integration: Part of {subsystem} subsystem
Validation: ✅ Template compliant

For technical documentation: docs/{parts[0]}/
For service API: See class {service_name}
For integration: Import as 'from {service_pattern} import get_service'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Copyright (c) 2025 AI Research. All rights reserved.
"""
'''


class ImportFixer:
    """Main import path fixing engine."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.analyzer = ImportPathAnalyzer(self.root_path)
        self.fixes_applied = []
        self.dry_run = True

    def fix_imports_in_file(self, file_path: Path, fixes: Dict[str, str]) -> bool:
        """Fix import statements in a single file."""

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            changes_made = False

            # Fix each broken import
            for broken_import, fixed_import in fixes.items():
                # Pattern for 'from X import Y' statements
                from_pattern = rf"from\s+{re.escape(broken_import)}\s+import"
                from_replacement = f"from {fixed_import} import"

                if re.search(from_pattern, content):
                    content = re.sub(from_pattern, from_replacement, content)
                    changes_made = True
                    logger.info(
                        f"Fixed 'from {broken_import} import' -> 'from {fixed_import} import'"
                    )

                # Pattern for 'import X' statements
                import_pattern = rf"import\s+{re.escape(broken_import)}(?=\s|$|,)"
                import_replacement = f"import {fixed_import}"

                if re.search(import_pattern, content):
                    content = re.sub(import_pattern, import_replacement, content)
                    changes_made = True
                    logger.info(
                        f"Fixed 'import {broken_import}' -> 'import {fixed_import}'"
                    )

            # Write back if changes made and not dry run
            if changes_made and not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "fixes": fixes,
                        "changes_count": len(fixes),
                    }
                )

            return changes_made

        except Exception as e:
            logger.error(f"Error fixing imports in {file_path}: {e}")
            return False

    def run_import_fixes(self, dry_run: bool = True) -> Dict[str, Any]:
        """Run comprehensive import fixing."""

        self.dry_run = dry_run
        logger.info(f"Starting import fixes (dry_run={dry_run})...")

        # Build module registry
        self.analyzer.build_module_registry()

        # Create missing service modules first
        if not dry_run:
            created_services = self.analyzer.create_missing_service_modules()
            logger.info(f"Created {len(created_services)} service modules")

        # Load broken imports from validation results
        try:
            with open(self.root_path.parent / "path_validation_results.json") as f:
                validation_data = json.load(f)

            broken_imports = validation_data.get("path_validation", {}).get(
                "missing_modules", []
            )

        except FileNotFoundError:
            logger.error(
                "path_validation_results.json not found. Run path validator first."
            )
            return {"error": "validation results not found"}

        # Group broken imports by file
        fixes_by_file = defaultdict(dict)
        fixed_count = 0
        unfixed_count = 0

        for broken_import_info in broken_imports:
            module = broken_import_info["module"]
            missing_import = broken_import_info["missing_import"]

            # Find best match for the broken import
            best_match = self.analyzer.find_best_match(missing_import)

            if best_match:
                # Convert module path to file path
                module_file = self.root_path / (module.replace(".", "/") + ".py")

                if module_file.exists():
                    fixes_by_file[module_file][missing_import] = best_match
                    fixed_count += 1
                else:
                    unfixed_count += 1
            else:
                unfixed_count += 1
                logger.warning(f"No match found for {missing_import}")

        # Apply fixes to each file
        files_modified = 0
        for file_path, fixes in fixes_by_file.items():
            if self.fix_imports_in_file(file_path, fixes):
                files_modified += 1

        results = {
            "dry_run": dry_run,
            "total_broken_imports": len(broken_imports),
            "fixed_imports": fixed_count,
            "unfixed_imports": unfixed_count,
            "files_modified": files_modified,
            "success_rate": (
                f"{fixed_count/(fixed_count+unfixed_count)*100:.1f}%"
                if (fixed_count + unfixed_count) > 0
                else "0%"
            ),
            "fixes_applied": self.fixes_applied,
        }

        return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix broken import paths in LUKHAS")
    parser.add_argument("--root", default=".", help="Root directory to fix")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview fixes without applying"
    )
    parser.add_argument("--apply", action="store_true", help="Apply fixes to files")
    parser.add_argument("--output", help="Save results to JSON file")

    args = parser.parse_args()

    fixer = ImportFixer(args.root)

    # Run fixes
    dry_run = not args.apply
    results = fixer.run_import_fixes(dry_run=dry_run)

    # Print summary
    print("🔧 Import Path Fixer Results")
    print("=" * 40)
    print(f"Mode: {'DRY RUN' if results.get('dry_run') else 'APPLIED'}")
    print(f"Total Broken Imports: {results.get('total_broken_imports', 0)}")
    print(f"Fixed: {results.get('fixed_imports', 0)} ✅")
    print(f"Unfixed: {results.get('unfixed_imports', 0)} ❌")
    print(f"Files Modified: {results.get('files_modified', 0)}")
    print(f"Success Rate: {results.get('success_rate', '0%')}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to {args.output}")

    if dry_run:
        print("\n💡 Run with --apply to make actual changes")


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 AI. All rights reserved.
║   Licensed under the AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
