#!/usr/bin/env python3
"""
Validate which imports are actually broken vs external libraries
"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealBrokenImportValidator:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.truly_broken = defaultdict(list)
        self.external_imports = defaultdict(int)

        # Common Python standard library modules
        self.stdlib_modules = {
            "argparse",
            "ast",
            "asyncio",
            "base64",
            "binascii",
            "collections",
            "contextlib",
            "copy",
            "csv",
            "datetime",
            "email",
            "enum",
            "functools",
            "gc",
            "gzip",
            "hashlib",
            "heapq",
            "http",
            "importlib",
            "inspect",
            "io",
            "itertools",
            "json",
            "logging",
            "math",
            "multiprocessing",
            "os",
            "pathlib",
            "pickle",
            "platform",
            "queue",
            "re",
            "random",
            "secrets",
            "shutil",
            "signal",
            "socket",
            "sqlite3",
            "ssl",
            "statistics",
            "string",
            "struct",
            "subprocess",
            "sys",
            "tempfile",
            "threading",
            "time",
            "traceback",
            "typing",
            "unicodedata",
            "unittest",
            "urllib",
            "uuid",
            "warnings",
            "weakref",
            "xml",
            "zlib",
        }

        # Common third-party packages
        self.third_party = {
            "numpy",
            "pandas",
            "matplotlib",
            "scipy",
            "sklearn",
            "torch",
            "tensorflow",
            "keras",
            "cv2",
            "PIL",
            "requests",
            "urllib3",
            "beautifulsoup4",
            "scrapy",
            "flask",
            "django",
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "pymongo",
            "redis",
            "celery",
            "pytest",
            "nose",
            "mock",
            "faker",
            "factory_boy",
            "hypothesis",
            "black",
            "flake8",
            "pylint",
            "mypy",
            "isort",
            "autopep8",
            "yapf",
            "jupyter",
            "ipython",
            "notebook",
            "nbconvert",
            "jupyterlab",
            "click",
            "typer",
            "rich",
            "tqdm",
            "colorama",
            "termcolor",
            "yaml",
            "toml",
            "configparser",
            "python-dotenv",
            "environs",
            "cryptography",
            "bcrypt",
            "passlib",
            "jwt",
            "pyjwt",
            "boto3",
            "google-cloud",
            "azure",
            "kubernetes",
            "docker",
            "structlog",
            "loguru",
            "sentry-sdk",
            "datadog",
            "prometheus_client",
            "openai",
            "anthropic",
            "transformers",
            "langchain",
            "chromadb",
            "websockets",
            "aiohttp",
            "httpx",
            "grpc",
            "graphql",
            "psutil",
            "watchdog",
            "schedule",
            "apscheduler",
            "qrcode",
            "pillow",
            "opencv-python",
            "scikit-image",
            "networkx",
            "graphviz",
            "pydot",
            "pygraphviz",
            "setuptools",
            "wheel",
            "pip",
            "poetry",
            "pipenv",
            "typing_extensions",
            "attrs",
            "cattrs",
            "orjson",
            "ujson",
            "rapidjson",
            "msgpack",
            "qiskit",
            "cirq",
            "pennylane",
            "strawberryfields",
            "dotenv",
            "python-decouple",
            "dynaconf",
            "elevenlabs",
            "cohere",
            "pinecone",
        }

    def validate(self):
        """Validate broken imports"""
        logger.info("Validating broken imports (excluding external libraries)...")

        # First, build an index of all available internal modules
        self._build_module_index()

        # Then check imports
        self._check_imports()

        # Generate report
        self._generate_report()

    def _build_module_index(self):
        """Build index of all internal modules"""
        self.internal_modules = set()

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            # Add module path
            relative = py_file.relative_to(self.root_path)
            module_parts = list(relative.parts[:-1]) + [relative.stem]
            module_path = ".".join(module_parts)
            self.internal_modules.add(module_path)

            # Also add parent modules
            for i in range(1, len(module_parts)):
                parent = ".".join(module_parts[:i])
                self.internal_modules.add(parent)

    def _check_imports(self):
        """Check all imports"""
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                relative_path = str(py_file.relative_to(self.root_path))

                # Find all imports
                import_patterns = [
                    (r"^import\s+([\w.]+)(?:\s+as\s+\w+)?$", "import"),
                    (r"^from\s+([\w.]+)\s+import", "from"),
                ]

                for pattern, import_type in import_patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        module = match.group(1)
                        base_module = module.split(".")[0]

                        # Check if it's standard library
                        if base_module in self.stdlib_modules:
                            continue

                        # Check if it's known third-party
                        if base_module in self.third_party:
                            self.external_imports[base_module] += 1
                            continue

                        # Check if it's __future__
                        if base_module == "__future__":
                            continue

                        # Check if it's internal
                        if (
                            module in self.internal_modules
                            or base_module in self.internal_modules
                        ):
                            continue

                        # Check if module exists as file
                        module_file = module.replace(".", "/") + ".py"
                        module_dir = module.replace(".", "/")

                        if (self.root_path / module_file).exists() or (
                            self.root_path / module_dir
                        ).exists():
                            continue

                        # This is truly broken
                        line_no = content[: match.start()].count("\n") + 1
                        self.truly_broken[relative_path].append(
                            {
                                "module": module,
                                "type": import_type,
                                "line": line_no,
                                "statement": match.group(0).strip(),
                            }
                        )

            except Exception as e:
                logger.debug(f"Error checking {py_file}: {e}")

    def _generate_report(self):
        """Generate validation report"""
        total_broken = sum(len(imports) for imports in self.truly_broken.values())

        logger.info("\nValidation complete!")
        logger.info(f"Truly broken imports: {total_broken}")
        logger.info(f"Files with broken imports: {len(self.truly_broken)}")

        # Show most common external imports
        logger.info("\nMost common external libraries detected:")
        for lib, count in sorted(
            self.external_imports.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            logger.info(f"  {lib}: {count} imports")

        # Show examples of truly broken imports
        if self.truly_broken:
            logger.info("\nExamples of truly broken imports:")
            examples_shown = 0
            for file_path, imports in list(self.truly_broken.items())[:5]:
                for imp in imports[:2]:
                    logger.info(f"  {file_path}:{imp['line']}")
                    logger.info(f"    {imp['statement']}")
                    examples_shown += 1
                    if examples_shown >= 10:
                        break
                if examples_shown >= 10:
                    break

        # Save detailed report
        report = {
            "summary": {
                "truly_broken_imports": total_broken,
                "files_affected": len(self.truly_broken),
                "external_libraries_found": len(self.external_imports),
            },
            "external_libraries": dict(self.external_imports),
            "truly_broken": {
                path: imports for path, imports in list(self.truly_broken.items())[:50]
            },
        }

        output_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "validated_broken_imports.json"
        )
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nDetailed report saved to: {output_path}")

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "env",
            "build",
            "dist",
            "node_modules",
            ".pytest_cache",
            "visualizations",
            "analysis_output",
            "scripts",
        }

        return any(part in skip_dirs for part in path.parts)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate truly broken imports")
    parser.add_argument("path", nargs="?", default=".", help="Root path")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    validator = RealBrokenImportValidator(root_path)
    validator.validate()


if __name__ == "__main__":
    main()
