# conftest.py (repo root)
# Ensure the alias hook + ledger is installed before *any* test import anywhere.
import pathlib
import sys

# CRITICAL: Add repo root to sys.path so packages like bridge/, qi/, etc. are importable
repo_root = pathlib.Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import side-effect: installs the lukhas.* → canonical alias hook V2
# Import using full module path to avoid adding tests/ to sys.path
import importlib.util
spec = importlib.util.spec_from_file_location("tests_conftest", repo_root / "tests" / "conftest.py")
if spec and spec.loader:
    tests_conftest = importlib.util.module_from_spec(spec)
    sys.modules["tests_conftest"] = tests_conftest
    spec.loader.exec_module(tests_conftest)
