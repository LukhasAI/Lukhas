import os
from pathlib import Path


def pytest_ignore_collect(path: Path, config):
    """During CI quality-gates, ignore heavy integration/e2e suites.

    This prevents import-time failures from optional integrations when
    running the fast smoke/tier1 gates.
    """
    if os.getenv("CI_QUALITY_GATES"):
        p = Path(path)
        # Skip integration and e2e test trees entirely
        parts = set(p.parts)
        if "integration" in parts or "e2e" in parts or "benchmarks" in parts:
            return True
    return False
