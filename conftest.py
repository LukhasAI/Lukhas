# conftest.py (repo root)
# Ensure the alias hook + ledger is installed before *any* test import anywhere.
import pathlib
import sys

# Make sure tests/ is on sys.path so we can import its conftest utilities
tests_dir = pathlib.Path(__file__).parent / "tests"
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

# Import side-effect: installs the lukhas.* → canonical alias hook V2
import tests.conftest  # noqa: F401
