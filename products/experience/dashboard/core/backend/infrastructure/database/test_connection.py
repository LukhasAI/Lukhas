"""
Tests for the database connection module.
"""

from unittest.mock import AsyncMock, patch

import pytest

from products.experience.dashboard.core.backend.infrastructure.database import connection
from products.experience.dashboard.core.backend.infrastructure.database.connection import (
    close_db,
    get_db,
    init_db,
)


@pytest.fixture(autouse=True)
async def reset_db_connection():
    """Reset the database connection before and after each test."""
    connection.db_connection = None
    yield
    connection.db_connection = None


@pytest.mark.asyncio
async def test_init_db():
    """Test that the database connection is initialized correctly."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        conn = await init_db()
        assert conn["status"] == "connected"
        assert connection.db_connection is not None
        assert connection.db_connection["status"] == "connected"


@pytest.mark.asyncio
async def test_close_db():
    """Test that the database connection is closed correctly."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await init_db()
        assert connection.db_connection is not None
        await close_db()
        assert connection.db_connection is None


@pytest.mark.asyncio
async def test_get_db_without_connection():
    """Test that get_db initializes a connection if one does not exist."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        conn = await get_db()
        assert conn["status"] == "connected"
        assert connection.db_connection is not None


@pytest.mark.asyncio
async def test_get_db_with_connection():
    """Test that get_db returns the existing connection."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await init_db()
        existing_conn = connection.db_connection
        conn = await get_db()
        assert conn is existing_conn
        assert connection.db_connection is not None
