import importlib

import pytest

MODULES = [
"lukhas.core.common",
"lukhas.memory",
"lukhas.identity",
"lukhas.governance",
"lukhas.observability",
]


@pytest.mark.no_mock
@pytest.mark.parametrize("m", MODULES)
def test_imports_real(m):
    assert importlib.import_module(m)