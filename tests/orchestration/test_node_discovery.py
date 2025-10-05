# tests/orchestration/test_node_discovery.py
import importlib
import sys

import pytest


@pytest.mark.skipif("candidate" not in sys.modules and not any(m.startswith("candidate") for m in sys.modules),
                    reason="candidate package not present in test env")
def test_discovery_smoke():
    # If the candidate package is present, just ensure discover doesn't crash.
    loader = importlib.import_module("candidate.core.orchestration.loader")
    count = loader.discover_nodes(root_package="candidate")
    assert isinstance(count, int)
    assert count >= 0
