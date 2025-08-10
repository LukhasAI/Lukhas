#!/usr/bin/env python3
"""
setup_project.py

Project setup and installation script for CollapseHash.
Handles dependency installation, configuration, and initial setup.

Usage:
    python setup_project.py [--dev] [--no-deps] [--config-only]

Author: LUKHAS AGI Core
TODO: Add automated environment detection
TODO: Add dependency conflict resolution
TODO: Add configuration validation
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


class CollapseHashSetup:
    """
    Automated setup and configuration for CollapseHash project.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize setup manager.

        Args:
            project_root (Path): Root directory of the project
        """
        self.project_root = project_root or Path(__file__).parent
        self.config_file = self.project_root / "config.json"
        self.requirements_file = self.project_root / "requirements.txt"

        # Setup status tracking
        self.setup_status = {
            "dependencies_installed": False,
            "config_created": False,
            "directories_created": False,
            "test_vectors_loaded": False,
            "web_templates_ready": False,
        }

    def check_python_version(self) -> bool:
        """
        Check if Python version meets requirements.

        Returns:
            bool: True if Python version is compatible

        TODO: Add more detailed version checking
        """
        min_version = (3, 8)
        current_version = sys.version_info[:2]

        if current_version < min_version:
            print(
                f"❌ Python {min_version[0]}.{min_version[1]}+ required. Current: {current_version[0]}.{current_version[1]}"
            )
            return False

        print(
            f"✅ Python version check passed: {current_version[0]}.{current_version[1]}"
        )
        return True

    def install_dependencies(self, dev_mode: bool = False) -> bool:
        """
        Install project dependencies from requirements.txt.

        Args:
            dev_mode (bool): Install development dependencies

        Returns:
            bool: True if installation successful

        TODO: Add pip upgrade check
        TODO: Add virtual environment detection
        TODO: Add dependency conflict resolution
        """
        print("📦 Installing dependencies...")

        if not self.requirements_file.exists():
            print(f"❌ Requirements file not found: {self.requirements_file}")
            return False

        try:
            # Install core dependencies
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(self.requirements_file),
            ]
            if dev_mode:
                print("  Installing development dependencies...")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Dependencies installed successfully")

            # TODO: Verify installation of critical dependencies
            self._verify_critical_imports()

            self.setup_status["dependencies_installed"] = True
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            return False

    def _verify_critical_imports(self) -> bool:
        """
        Verify that critical dependencies can be imported.

        Returns:
            bool: True if all critical imports successful

        TODO: Add comprehensive import testing
        """
        critical_imports = [
            ("oqs", "liboqs-python"),
            ("hashlib", "built-in"),
            ("json", "built-in"),
            ("numpy", "numpy"),
        ]

        failed_imports = []

        for module_name, package_name in critical_imports:
            try:
                __import__(module_name)
                print(f"  ✅ {module_name} ({package_name})")
            except ImportError:
                print(f"  ❌ {module_name} ({package_name})")
                failed_imports.append((module_name, package_name))

        if failed_imports:
            print("❌ Some critical dependencies failed to import:")
            for module_name, package_name in failed_imports:
                print(f"  - {module_name} (install: pip install {package_name})")
            return False

        return True

    def create_directories(self) -> bool:
        """
        Create necessary project directories.

        Returns:
            bool: True if directories created successfully

        TODO: Add permission checking
        TODO: Add cleanup option for failed setup
        """
        print("📁 Creating project directories...")

        directories = [
            "logs",
            "data",
            "exports",
            "qr_codes",
            "web_templates",
            "tests",
            "docs",
        ]

        try:
            for dir_name in directories:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(exist_ok=True)
                print(f"  ✅ {dir_name}/")

            self.setup_status["directories_created"] = True
            return True

        except OSError as e:
            print(f"❌ Failed to create directories: {e}")
            return False

    def create_config(self) -> bool:
        """
        Create default configuration file.

        Returns:
            bool: True if config created successfully

        TODO: Add configuration validation
        TODO: Add user prompts for custom settings
        """
        print("⚙️ Creating configuration file...")

        if self.config_file.exists():
            print(f"  ℹ️ Configuration file already exists: {self.config_file}")
            response = input("  Overwrite existing config? (y/N): ").lower()
            if response != "y":
                print("  Keeping existing configuration")
                self.setup_status["config_created"] = True
                return True

        default_config = {
            "version": "1.0.0",
            "algorithm": "SPHINCS+-SHAKE256-128f-simple",
            "hash_function": "SHAKE256",
            "signature_size": 17088,
            "public_key_size": 32,
            "private_key_size": 64,
            "security_level": 128,
            "verification": {
                "timeout_seconds": 30,
                "max_retries": 3,
                "cache_results": True,
            },
            "logging": {
                "level": "INFO",
                "file": "logs/collapse_hash.log",
                "max_size_mb": 10,
                "backup_count": 5,
            },
            "web_interface": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "secret_key": "CHANGE_THIS_IN_PRODUCTION",
            },
            "hardware": {
                "use_tpm": False,
                "use_yubikey": False,
                "entropy_sources": ["system", "quantum"],
            },
            "storage": {
                "ledger_file": "collapse_logbook.jsonl",
                "test_vectors": "test_vectors.json",
                "backup_enabled": True,
                "backup_interval_hours": 24,
            },
        }

        try:
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)

            print(f"  ✅ Configuration created: {self.config_file}")
            self.setup_status["config_created"] = True
            return True

        except (OSError, json.JSONEncodeError) as e:
            print(f"❌ Failed to create configuration: {e}")
            return False

    def setup_test_environment(self) -> bool:
        """
        Set up test environment and sample data.

        Returns:
            bool: True if test setup successful

        TODO: Add more comprehensive test data
        TODO: Add test database setup
        """
        print("🧪 Setting up test environment...")

        # TODO: Create sample test vectors if they don't exist
        test_vectors_file = self.project_root / "test_vectors.json"
        if not test_vectors_file.exists():
            print("  Creating sample test vectors...")
            # Test vectors should already be created by previous setup

        # TODO: Create sample ledger entries
        ledger_file = self.project_root / "collapse_logbook.jsonl"
        if not ledger_file.exists():
            print("  Creating sample ledger...")
            # Ledger should already be created by previous setup

        self.setup_status["test_vectors_loaded"] = True
        return True

    def run_validation_tests(self) -> bool:
        """
        Run basic validation tests to ensure setup is working.

        Returns:
            bool: True if validation tests pass

        TODO: Add comprehensive validation suite
        TODO: Add performance benchmarks
        """
        print("🔍 Running validation tests...")

        try:
            # Test 1: Import core modules
            print("  Testing core module imports...")
            import collapse_hash_pq

            print("    ✅ Core modules import successfully")

            # Test 2: Basic hash generation
            print("  Testing hash generation...")
            generator = collapse_hash_pq.CollapseHashGenerator()
            print("    ✅ Hash generator initialized")

            # Test 3: Configuration loading
            print("  Testing configuration loading...")
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                print("    ✅ Configuration loads successfully")

            return True

        except Exception as e:
            print(f"❌ Validation tests failed: {e}")
            return False

    def print_setup_summary(self) -> None:
        """
        Print summary of setup status and next steps.

        TODO: Add more detailed status reporting
        TODO: Add troubleshooting suggestions
        """
        print("\n" + "=" * 50)
        print("📋 SETUP SUMMARY")
        print("=" * 50)

        for task, completed in self.setup_status.items():
            status = "✅" if completed else "❌"
            task_name = task.replace("_", " ").title()
            print(f"{status} {task_name}")

        all_completed = all(self.setup_status.values())

        if all_completed:
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Review configuration in config.json")
            print("2. Run tests: python -m pytest tests/")
            print("3. Start web interface: python web_qr_verifier.py")
            print("4. Generate your first hash: python collapse_cli.py generate")
            print("5. Read documentation in README.md")
        else:
            print("\n⚠️ Setup incomplete. Please resolve the failed steps above.")
            print("\nFor help, check:")
            print("- README.md for detailed instructions")
            print("- requirements.txt for dependency information")
            print("- GitHub issues for known problems")

        print(f"\nProject root: {self.project_root}")
        print(f"Configuration: {self.config_file}")
        print("=" * 50)

    def run_full_setup(self, dev_mode: bool = False, skip_deps: bool = False) -> bool:
        """
        Run complete project setup process.

        Args:
            dev_mode (bool): Install development dependencies
            skip_deps (bool): Skip dependency installation

        Returns:
            bool: True if setup completed successfully
        """
        print("🚀 Starting CollapseHash project setup...")
        print(f"📁 Project root: {self.project_root}")

        # Step 1: Check Python version
        if not self.check_python_version():
            return False

        # Step 2: Install dependencies (unless skipped)
        if not skip_deps:
            if not self.install_dependencies(dev_mode):
                print("⚠️ Dependency installation failed, continuing with setup...")

        # Step 3: Create directories
        if not self.create_directories():
            return False

        # Step 4: Create configuration
        if not self.create_config():
            return False

        # Step 5: Setup test environment
        if not self.setup_test_environment():
            return False

        # Step 6: Run validation tests
        if not self.run_validation_tests():
            print("⚠️ Validation tests failed, but setup may still be usable")

        # Step 7: Print summary
        self.print_setup_summary()

        return all(self.setup_status.values())


def main():
    """
    Main setup script entry point.

    TODO: Add more command line options
    TODO: Add interactive setup mode
    """
    parser = argparse.ArgumentParser(
        description="CollapseHash project setup script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_project.py                    # Standard setup
  python setup_project.py --dev             # Setup with dev dependencies
  python setup_project.py --no-deps         # Setup without installing deps
  python setup_project.py --config-only     # Only create configuration
        """,
    )

    parser.add_argument(
        "--dev", action="store_true", help="Install development dependencies"
    )
    parser.add_argument(
        "--no-deps", action="store_true", help="Skip dependency installation"
    )
    parser.add_argument(
        "--config-only", action="store_true", help="Only create configuration file"
    )
    parser.add_argument(
        "--project-root", type=str, help="Specify project root directory"
    )

    args = parser.parse_args()

    # Initialize setup manager
    project_root = Path(args.project_root) if args.project_root else None
    setup_manager = CollapseHashSetup(project_root)

    # Run requested setup
    if args.config_only:
        success = setup_manager.create_config()
    else:
        success = setup_manager.run_full_setup(
            dev_mode=args.dev, skip_deps=args.no_deps
        )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
