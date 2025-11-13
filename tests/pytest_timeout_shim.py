from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register a noop timeout ini option when pytest-timeout is absent."""
    parser.addini(
        "timeout",
        "Pytest-timeout compatibility shim (no-op in Codex test runs)",
        default="0",
    )
