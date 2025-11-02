"""Minimal async test to verify pytest-asyncio works."""

import pytest

# Enable asyncio mode for this module
pytestmark = pytest.mark.asyncio


async def test_simple_async():
    """Simple async test."""
    import asyncio

    await asyncio.sleep(0.001)
    assert True
