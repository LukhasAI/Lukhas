import importlib

import pytest

MODULES = [
    "core.common",
    "memory",
    "identity",
    "governance",
    "observability",
]


@pytest.mark.no_mock
@pytest.mark.parametrize("m", MODULES)
def test_imports_real(m):
    assert importlib.import_module(m)
