#!/usr/bin/env python3
"""
LUKHAS AI Path Manager - INTEGRATED FROM ARCHIVE
=============================================

Provides standardized path constants for all scripts and applications.
Centralized path management for LUKHAS AI project structure.

Rescued from: archive/scattered_root_files/lukhas_paths.py
Integrated: 2025-09-09 into lukhas/core/filesystem/
Purpose: Eliminate hardcoded paths throughout the codebase
"""

import os
from pathlib import Path
from typing import Optional, Union


def get_project_root() -> Path:
    """
    Get the project root directory dynamically.
    Works from any location within the project structure.
    """
    # Start from current file location
    current = Path(__file__).resolve()

    # Look for project root indicators
    for parent in [current, *list(current.parents)]:
        if any(
            (parent / indicator).exists()
            for indicator in ["pyproject.toml", "README.md", "CLAUDE.md", ".git", "lukhas", "candidate", "branding"]
        ):
            return parent

    # Fallback to environment variable or current working directory
    if "LUKHAS_ROOT" in os.environ:
        return Path(os.environ["LUKHAS_ROOT"])

    return Path.cwd()


class LukhasPathManager:
    """Centralized path management for LUKHAS AI project"""

    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        self.root = Path(project_root) if project_root else get_project_root()

    # Core LUKHAS directories
    @property
    def lukhas_core(self) -> Path:
        """lukhas/ - Production-ready modules"""
        return self.root / "lukhas"

    @property
    def candidate(self) -> Path:
        """candidate/ - Development modules"""
        return self.root / "candidate"

    @property
    def branding(self) -> Path:
        """branding/ - Official LUKHAS AI branding"""
        return self.root / "branding"

    @property
    def serve(self) -> Path:
        """serve/ - API and serving infrastructure"""
        return self.root / "serve"

    @property
    def tests(self) -> Path:
        """tests/ - Test suites"""
        return self.root / "tests"

    @property
    def docs(self) -> Path:
        """docs/ - Documentation"""
        return self.root / "docs"

    @property
    def tools(self) -> Path:
        """tools/ - Development tools"""
        return self.root / "tools"

    # Configuration paths
    @property
    def config(self) -> Path:
        """config/ - Configuration files"""
        return self.root / "config"

    @property
    def config_env(self) -> Path:
        return self.config / "env"

    @property
    def config_tools(self) -> Path:
        return self.config / "tools"

    @property
    def config_project(self) -> Path:
        return self.config / "project"

    @property
    def config_node(self) -> Path:
        return self.config / "node"

    # Deployment paths
    @property
    def deployment(self) -> Path:
        return self.root / "deployment"

    @property
    def deployment_scripts(self) -> Path:
        return self.deployment / "scripts"

    @property
    def deployment_docker(self) -> Path:
        return self.deployment / "docker"

    @property
    def deployment_cloud(self) -> Path:
        return self.deployment / "cloud"

    @property
    def deployment_platforms(self) -> Path:
        return self.deployment / "platforms"

    # Asset paths
    @property
    def assets(self) -> Path:
        return self.root / "assets"

    @property
    def assets_dreams(self) -> Path:
        return self.assets / "dreams"

    @property
    def assets_ui(self) -> Path:
        return self.assets / "ui"

    @property
    def assets_docs(self) -> Path:
        return self.assets / "docs"

    # Report paths
    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def reports_api(self) -> Path:
        return self.reports / "api"

    @property
    def reports_security(self) -> Path:
        return self.reports / "security"

    @property
    def reports_deployment(self) -> Path:
        return self.reports / "deployment"

    @property
    def reports_analysis(self) -> Path:
        return self.reports / "analysis"

    # Test paths
    @property
    def tests_unit(self) -> Path:
        return self.tests / "unit"

    @property
    def tests_integration(self) -> Path:
        return self.tests / "integration"

    @property
    def tests_e2e(self) -> Path:
        return self.tests / "e2e"

    @property
    def tests_performance(self) -> Path:
        return self.tests / "performance"

    @property
    def tests_enhancements(self) -> Path:
        return self.tests / "enhancements"

    # Additional LUKHAS-specific paths
    @property
    def consciousness(self) -> Path:
        """consciousness/ - Consciousness modules"""
        return self.root / "consciousness"

    @property
    def memory(self) -> Path:
        """memory/ - Memory systems"""
        return self.root / "memory"

    @property
    def governance(self) -> Path:
        """governance/ - Guardian and ethics systems"""
        return self.root / "governance"

    @property
    def orchestration(self) -> Path:
        """orchestration/ - System orchestration"""
        return self.root / "orchestration"

    @property
    def products(self) -> Path:
        """products/ - Product implementations"""
        return self.root / "products"

    @property
    def scripts(self) -> Path:
        """scripts/ - Utility scripts"""
        return self.root / "scripts"

    @property
    def demos(self) -> Path:
        """demos/ - Demonstration code"""
        return self.root / "demos"

    @property
    def performance(self) -> Path:
        """performance/ - Performance analysis"""
        return self.root / "performance"

    # Utility methods
    def ensure_dir(self, path: Path) -> Path:
        """Ensure directory exists, create if it doesn't"""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_dream_image_path(self, filename: Optional[str] = None) -> Path:
        """Get path for dream image with optional filename"""
        base_path = self.ensure_dir(self.assets_dreams)
        if filename:
            return base_path / filename
        return base_path

    def get_test_result_path(self, test_type: str, filename: Optional[str] = None) -> Path:
        """Get path for test results based on type"""
        test_paths = {
            "api": self.reports_api,
            "security": self.reports_security,
            "performance": self.tests_performance,
            "unit": self.tests_unit,
            "integration": self.tests_integration,
            "e2e": self.tests_e2e,
        }

        base_path = self.ensure_dir(test_paths.get(test_type, self.reports_api))
        if filename:
            return base_path / filename
        return base_path

    def get_config_path(self, config_type: str, filename: Optional[str] = None) -> Path:
        """Get path for configuration files based on type"""
        config_paths = {
            "env": self.config_env,
            "tools": self.config_tools,
            "project": self.config_project,
            "node": self.config_node,
        }

        base_path = self.ensure_dir(config_paths.get(config_type, self.config_tools))
        if filename:
            return base_path / filename
        return base_path

    def get_relative_path(self, path: Union[str, Path]) -> Path:
        """Convert absolute path to relative path from project root"""
        abs_path = Path(path).resolve()
        try:
            return abs_path.relative_to(self.root.resolve())
        except ValueError:
            # Path is outside project root
            return abs_path

    def is_in_project(self, path: Union[str, Path]) -> bool:
        """Check if path is within the project structure"""
        try:
            Path(path).resolve().relative_to(self.root.resolve())
            return True
        except ValueError:
            return False

    def get_module_path(self, module_name: str, lane: str = "lukhas") -> Path:
        """Get path to a specific module in lukhas/ or candidate/"""
        if lane == "lukhas":
            return self.lukhas_core / module_name
        elif lane == "candidate":
            return self.candidate / module_name
        else:
            raise ValueError(f"Invalid lane: {lane}. Must be 'lukhas' or 'candidate'")

    def list_modules(self, lane: str = "lukhas") -> list[str]:
        """List all modules in specified lane"""
        base_path = self.get_module_path("", lane)
        if not base_path.exists():
            return []

        return [item.name for item in base_path.iterdir() if item.is_dir() and not item.name.startswith(".")]


# Global instance for easy imports
paths = LukhasPathManager()


# Legacy path mapping for migration compatibility
DEPRECATED_PATHS = {
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms": str(paths.deployment_platforms),
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/demos": str(paths.demos),
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/performance": str(paths.performance),
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security": str(paths.reports_security),
    "node_configs": str(paths.config_node),
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams": str(paths.assets_dreams),
    "meta_dashboard": str(paths.root / "dashboard" / "meta"),
}


def migrate_deprecated_path(old_path: Union[str, Path]) -> str:
    """Convert deprecated path to new path"""
    old_path_str = str(old_path)
    for old, new in DEPRECATED_PATHS.items():
        if old in old_path_str:
            return old_path_str.replace(old, new)
    return old_path_str


def get_lukhas_root() -> Path:
    """Convenience function to get project root"""
    return paths.root


def ensure_lukhas_structure() -> dict[str, bool]:
    """Ensure core LUKHAS directory structure exists"""
    results = {}
    core_dirs = [
        paths.lukhas_core,
        paths.candidate,
        paths.branding,
        paths.serve,
        paths.tests,
        paths.docs,
        paths.tools,
        paths.config,
        paths.assets,
        paths.reports,
    ]

    for directory in core_dirs:
        try:
            paths.ensure_dir(directory)
            results[str(directory.name)] = True
        except Exception:
            results[str(directory.name)] = False

    return results


if __name__ == "__main__":
    # Test the path manager
    print("LUKHAS AI Path Manager - Standard Paths:")
    print(f"Project Root: {paths.root}")
    print(f"LUKHAS Core: {paths.lukhas_core}")
    print(f"Candidate: {paths.candidate}")
    print(f"Dream Images: {paths.assets_dreams}")
    print(f"API Reports: {paths.reports_api}")
    print(f"Deployment Scripts: {paths.deployment_scripts}")
    print(f"Test Enhancements: {paths.tests_enhancements}")
    print()
    print("Available Modules:")
    print(f"  LUKHAS modules: {paths.list_modules('lukhas')}")
    print(f"  Candidate modules: {paths.list_modules('candidate')}")
    print()
    print("Directory Structure Validation:")
    structure = ensure_lukhas_structure()
    for name, exists in structure.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {name}")
