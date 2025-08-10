import asyncio
import importlib

import pytest


def test_main_ethics():
    pytest.importorskip("structlog")
    module = importlib.import_module("reasoning.ethical_reasoning_system")
    assert hasattr(module, "main_ethics_test")
    # Run the example test function to ensure it executes without error
    asyncio.run(module.main_ethics_test())
