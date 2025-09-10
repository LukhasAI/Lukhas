from lukhas_paths import paths

#!/usr/bin/env python3
"""
LUKHAS AI Path Manager
Provides standardized path constants for all scripts and applications
"""

from pathlib import Path
from typing import Optional, Union

# Get project root directory
PROJECT_ROOT = Path(__file__).parent


class LukhasPathManager:
    """Centralized path management for LUKHAS AI project"""

    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        self.root = Path(project_root) if project_root else PROJECT_ROOT

    # Configuration paths
    @property
    def config_env(self):
        return self.root / "config" / "env"

    @property
    def config_tools(self):
        return self.root / "config" / "tools"

    @property
    def config_project(self):
        return self.root / "config" / "project"

    @property
    def config_node(self):
        return self.root / "config" / "node"

    # Deployment paths
    @property
    def deployment_scripts(self):
        return self.root / "deployment" / "scripts"

    @property
    def deployment_docker(self):
        return self.root / "deployment" / "docker"

    @property
    def deployment_cloud(self):
        return self.root / "deployment" / "cloud"

    @property
    def deployment_platforms(self):
        return self.root / "deployment" / "platforms"

    # Asset paths
    @property
    def assets_dreams(self):
        return self.root / "assets" / "dreams"

    @property
    def assets_ui(self):
        return self.root / "assets" / "ui"

    @property
    def assets_docs(self):
        return self.root / "assets" / "docs"

    # Report paths
    @property
    def reports_api(self):
        return self.root / "reports" / "api"

    @property
    def reports_security(self):
        return self.root / "reports" / "security"

    @property
    def reports_deployment(self):
        return self.root / "reports" / "deployment"

    @property
    def reports_analysis(self):
        return self.root / "reports" / "analysis"

    # Test paths
    @property
    def tests_unit(self):
        return self.root / "tests" / "unit"

    @property
    def tests_integration(self):
        return self.root / "tests" / "integration"

    @property
    def tests_e2e(self):
        return self.root / "tests" / "e2e"

    @property
    def tests_performance(self):
        return self.root / "tests" / "performance"

    @property
    def tests_enhancements(self):
        return self.root / "tests" / "enhancements"

    # Development paths
    @property
    def demos(self):
        return self.root / "demos"

    @property
    def tools(self):
        return self.root / "tools"

    @property
    def performance(self):
        return self.root / "performance"

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


# Global instance for easy imports
paths = LukhasPathManager()

# Legacy path mapping for migration
DEPRECATED_PATHS = {
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms": paths.deployment_platforms,
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/demos": paths.demos,
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/performance": paths.performance,
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security": paths.reports_security,
    "node_configs": paths.config_node,
    "/Users/agi_dev/LOCAL-REPOS/Lukhas/assets/dreams": paths.assets_dreams,
    "meta_dashboard": paths.root / "dashboard" / "meta",
}


def migrate_deprecated_path(old_path):
    """Convert deprecated path to new path"""
    for old, new in DEPRECATED_PATHS.items():
        if old in str(old_path):
            return str(old_path).replace(old, str(new))
    return old_path


if __name__ == "__main__":
    # Test the path manager
    print("LUKHAS AI Path Manager - Standard Paths:")
    print(f"Dream images: {paths.assets_dreams}")
    print(f"API reports: {paths.reports_api}")
    print(f"Deployment scripts: {paths.deployment_scripts}")
    print(f"Test enhancements: {paths.tests_enhancements}")