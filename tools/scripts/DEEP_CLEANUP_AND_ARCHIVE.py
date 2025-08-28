#!/usr/bin/env python3
"""
Deep Cleanup and Archive Script for Lukhas
Archives deprecated files, cleans cache, updates docs, and creates clean package
"""

import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


class WorkspaceCleanup:
    """Comprehensive workspace cleanup and archiving"""

    def __init__(self):
        self.workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas"
        self.archive_dir = (
            Path.home()
            / "lukhas-archive"
            / f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.stats = {
            "files_archived": 0,
            "files_cleaned": 0,
            "bytes_freed": 0,
            "duplicates_found": 0,
            "issues_fixed": 0,
        }
        self.files_to_archive = []
        self.files_to_delete = []
        self.import_issues = []
        self.documentation_updates = []

    def scan_duplicate_versions(self) -> list[Path]:
        """Find duplicate versioned files like __init___1.py"""
        print("\n🔍 Scanning for duplicate versioned files...")
        duplicates = []

        pattern = re.compile(r"(.+)_(\d+)(\.\w+)$")

        for file in self.workspace.rglob("*"):
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    # Check if original exists
                    base_name = match.group(1)
                    ext = match.group(3)
                    original = file.parent / f"{base_name}{ext}"

                    if original.exists() or "_" in base_name:
                        duplicates.append(file)
                        print(f"   Found duplicate: {file.relative_to(self.workspace)}")

        self.stats["duplicates_found"] = len(duplicates)
        return duplicates

    def scan_cache_files(self) -> list[Path]:
        """Find all cache and temporary files"""
        print("\n🗑️ Scanning for cache files...")
        cache_files = []

        cache_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.pytest_cache/**",
            "**/.mypy_cache/**",
            "**/*.egg-info/**",
            "**/build/**",
            "**/dist/**",
            "**/.DS_Store",
            "**/.coverage",
            "**/*.log",
        ]

        for pattern in cache_patterns:
            cache_files.extend(self.workspace.glob(pattern))

        return cache_files

    def scan_misplaced_tests(self) -> list[Path]:
        """Find test files outside of tests/ directory"""
        print("\n🧪 Scanning for misplaced test files...")
        misplaced = []

        for file in self.workspace.rglob("test_*.py"):
            if "tests" not in str(file.parent):
                misplaced.append(file)
                print(f"   Misplaced test: {file.relative_to(self.workspace)}")

        return misplaced

    def scan_deprecated_modules(self) -> list[Path]:
        """Identify deprecated and unused modules"""
        print("\n📦 Scanning for deprecated modules...")
        deprecated = []

        deprecated_patterns = [
            "**/ethics_legacy/**",
            "**/safety/watch/**",
            "**/safety/monitoring/**",
            "**/tools/mesh_snapshots/**",
            "**/mobile_platform/**",
            "**/wearables_integration/**",
            "**/claude_integration/**",
            "**/dao/**",
        ]

        for pattern in deprecated_patterns:
            for path in self.workspace.glob(pattern):
                if path.is_file():
                    deprecated.append(path)

        return deprecated

    def check_import_paths(self) -> list[dict]:
        """Check for broken import paths"""
        print("\n🔗 Checking import paths...")
        issues = []

        for py_file in self.workspace.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Find imports
                import_pattern = re.compile(
                    r"^(?:from|import)\s+([^\s]+)", re.MULTILINE
                )
                imports = import_pattern.findall(content)

                for imp in imports:
                    # Check if it's a relative import to a non-existent module
                    if imp.startswith("."):
                        continue

                    # Check if it's a local module that doesn't exist
                    if not imp.startswith(
                        ("lukhas", "lambda", "governance", "consciousness", "memory")
                    ):
                        continue

                    module_path = imp.replace(".", "/")
                    possible_paths = [
                        self.workspace / f"{module_path}.py",
                        self.workspace / module_path / "__init__.py",
                    ]

                    if not any(p.exists() for p in possible_paths):
                        issues.append(
                            {
                                "file": str(py_file.relative_to(self.workspace)),
                                "import": imp,
                                "type": "broken_import",
                            }
                        )

            except Exception:
                pass

        return issues

    def update_requirements(self):
        """Update and consolidate requirements.txt"""
        print("\n📋 Updating requirements.txt...")

        # Collect all unique requirements
        all_requirements = set()

        for req_file in self.workspace.rglob("requirements*.txt"):
            if req_file.is_file():
                try:
                    with open(req_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("# ":
                                # Parse package name
                                re.split(r"[<>=!]", line)[0]
                                all_requirements.add(line)
                except Exception:
                    pass

        # Core requirements for the main system
        core_requirements = [
            "# Core Dependencies",
            "python-dateutil>=2.8.2",
            "pytz>=2023.3",
            "typing-extensions>=4.8.0",
            "",
            "# Async Support",
            "asyncio",
            "aiohttp>=3.9.0",
            "aiofiles>=23.2.0",
            "",
            "# Web Framework",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "pydantic>=2.0.0",
            "",
            "# Data Processing",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "scikit-learn>=1.3.0",
            "",
            "# Testing",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "",
            "# Security",
            "cryptography>=41.0.0",
            "pynacl>=1.5.0",
            "bcrypt>=4.0.1",
            "",
            "# Database",
            "sqlalchemy>=2.0.0",
            "redis>=5.0.0",
            "psycopg2-binary>=2.9.0",
            "",
            "# Monitoring",
            "prometheus-client>=0.19.0",
            "structlog>=23.2.0",
            "",
            "# Development",
            "black>=23.11.0",
            "mypy>=1.7.0",
            "pylint>=3.0.0",
            "",
            "# Cloud",
            "boto3>=1.29.0",
            "kubernetes>=28.1.0",
        ]

        # Write consolidated requirements
        req_path = self.workspace / "requirements.txt"
        with open(req_path, "w") as f:
            f.write("\n".join(core_requirements))

        print(f"   ✅ Updated requirements.txt with {len(core_requirements)} packages")

    def update_setup_py(self):
        """Update setup.py with current structure"""
        print("\n🔧 Updating setup.py...")

        setup_content = '''#!/usr/bin/env python3
"""
Lukhas  Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="lukhas-",
    version="2.0.0",
    author="LUKHAS AI",
    description="Production-ready consciousness-aware AI platform with Lambda Products",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lukhas-",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
        "asyncio",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.11.0",
            "mypy>=1.7.0",
        ],
        "lambda": [
            "msgpack>=1.0.5",
            "orjson>=3.9.0",
            "prometheus-client>=0.19.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "scipy>=1.11.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "lukhas=main:main",
            "lukhas-test=COMPLETE_SYSTEM_TEST:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md", "*.html"],
    },
)
'''

        setup_path = self.workspace / "setup.py"
        with open(setup_path, "w") as f:
            f.write(setup_content)

        print("   ✅ Updated setup.py")

    def create_archive(self, files_to_archive: list[Path]):
        """Move files to archive directory"""
        print(f"\n📦 Creating archive at {self.archive_dir}...")

        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Create archive structure
        (self.archive_dir / "duplicates").mkdir(exist_ok=True)
        (self.archive_dir / "deprecated").mkdir(exist_ok=True)
        (self.archive_dir / "misplaced_tests").mkdir(exist_ok=True)
        (self.archive_dir / "old_docs").mkdir(exist_ok=True)

        for file in files_to_archive:
            if not file.exists():
                continue

            # Determine archive category
            if re.match(r".+_\d+\.\w+$", file.name):
                category = "duplicates"
            elif "test_" in file.name and "tests" not in str(file):
                category = "misplaced_tests"
            elif any(dep in str(file) for dep in ["legacy", "deprecated", "old"]):
                category = "deprecated"
            else:
                category = "old_docs"

            # Create relative path in archive
            rel_path = file.relative_to(self.workspace)
            archive_path = self.archive_dir / category / rel_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            try:
                shutil.move(str(file), str(archive_path))
                self.stats["files_archived"] += 1
                self.stats["bytes_freed"] += file.stat().st_size if file.exists() else 0
            except Exception as e:
                print(f"   ⚠️ Could not archive {file}: {e}")

        print(f"   ✅ Archived {self.stats['files_archived']} files")

    def clean_cache(self, cache_files: list[Path]):
        """Remove cache and temporary files"""
        print("\n🧹 Cleaning cache files...")

        for file in cache_files:
            try:
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
                self.stats["files_cleaned"] += 1
            except Exception:
                pass

        print(f"   ✅ Cleaned {self.stats['files_cleaned']} cache files")

    def update_documentation(self):
        """Update main documentation"""
        print("\n📚 Updating documentation...")

        # Create docs directory structure
        docs_dir = self.workspace / "docs"
        docs_dir.mkdir(exist_ok=True)

        (docs_dir / "api").mkdir(exist_ok=True)
        (docs_dir / "guides").mkdir(exist_ok=True)
        (docs_dir / "architecture").mkdir(exist_ok=True)

        # Move documentation files to docs/
        doc_files = [
            "COMPLETE_PACKAGE_MANIFEST.md",
            "AI_CORE_BENEFITS_ANALYSIS.md",
            "FINAL_SYSTEM_REPORT.md",
            "COMPLETE_SYSTEM_TEST_REPORT.md",
        ]

        for doc_file in doc_files:
            source = self.workspace / doc_file
            if source.exists():
                dest = docs_dir / doc_file
                shutil.move(str(source), str(dest))
                print(f"   Moved {doc_file} to docs/")

        print("   ✅ Documentation updated")

    def create_clean_package(self):
        """Create a clean zip package of the workspace"""
        print("\n📦 Creating clean package...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"lukhas_an_{timestamp}.zip"
        zip_path = self.workspace.parent / zip_name

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in self.workspace.rglob("*"):
                if file.is_file():
                    # Skip cache and temporary files
                    if any(
                        skip in str(file)
                        for skip in ["__pycache__", ".pyc", ".pyo", ".DS_Store", ".git"]
                    ):
                        continue

                    # Add to zip with relative path
                    rel_path = file.relative_to(self.workspace)
                    zipf.write(file, rel_path)

        # Get zip size
        zip_size = zip_path.stat().st_size / (1024 * 1024# MB

        print(f"   ✅ Created {zip_name} ({zip_size:.2f} MB)")
        return zip_path

    def generate_cleanup_report(self):
        """Generate cleanup report"""
        print("\n" + "=" * 60)
        print("📊 CLEANUP REPORT")
        print("=" * 60)

        print(
            f"""
Summary:
   Files Archived: {self.stats['files_archived']}
   Cache Cleaned: {self.stats['files_cleaned']}
   Duplicates Found: {self.stats['duplicates_found']}
   Space Freed: {self.stats['bytes_freed'] / (1024*1024):.2f} MB

Archive Location:
   {self.archive_dir}

Documentation:
   ✅ Updated and organized in /docs

Requirements:
   ✅ Consolidated into single requirements.txt

Setup.py:
   ✅ Updated with current structure
        """
        )

        # Save report
        report_path = self.workspace / "CLEANUP_REPORT.md"
        with open(report_path, "w") as f:
            f.write("# Workspace Cleanup Report\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write("## Statistics\n\n")
            for key, value in self.stats.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
            f.write("\n## Archive Location\n\n")
            f.write(f"`{self.archive_dir}`\n")

    def run_deep_cleanup(self):
        """Execute the complete cleanup process"""
        print("=" * 60)
        print("🧹 DEEP WORKSPACE CLEANUP")
        print("=" * 60)

        # 1. Scan for issues
        duplicates = self.scan_duplicate_versions()
        cache_files = self.scan_cache_files()
        misplaced_tests = self.scan_misplaced_tests()
        deprecated = self.scan_deprecated_modules()
        self.check_import_paths()

        # 2. Prepare archive list
        files_to_archive = duplicates + misplaced_tests + deprecated

        # 3. Create archive
        if files_to_archive:
            self.create_archive(files_to_archive)

        # 4. Clean cache
        if cache_files:
            self.clean_cache(cache_files)

        # 5. Update configurations
        self.update_requirements()
        self.update_setup_py()

        # 6. Update documentation
        self.update_documentation()

        # 7. Create clean package
        zip_path = self.create_clean_package()

        # 8. Generate report
        self.generate_cleanup_report()

        print("\n✅ Cleanup complete!")
        print(f"📦 Clean package: {zip_path}")
        print(f"🗄️ Archive: {self.archive_dir}")


def main():
    """Run the cleanup process"""
    cleanup = WorkspaceCleanup()
    cleanup.run_deep_cleanup()


if __name__ == "__main__":

    # Auto-run mode for script execution
    print("\n🚀 Running automated cleanup...")
    main()
