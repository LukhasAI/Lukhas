"""Minimal pytest-asyncio stub to satisfy configuration in offline environments."""

# ΛTAG: test_stub

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover
    group = parser.getgroup("asyncio")
    group.addoption("--asyncio-mode", action="store", dest="asyncio_mode")
    parser.addini("asyncio_mode", "Asyncio mode", default="auto")
    parser.addini(
        "asyncio_default_fixture_loop_scope",
        "Asyncio fixture loop scope",
        default="function",
    )
    parser.addini(
        "asyncio_default_test_loop_scope",
        "Asyncio test loop scope",
        default="function",
    )


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover
    config.asyncio_mode = config.getini("asyncio_mode")
