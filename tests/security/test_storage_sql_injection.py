#!/usr/bin/env python3
"""
Security Test Suite for SQL Injection Vulnerabilities in SQLiteMetadataStore

This test suite focuses on verifying that the SQLiteMetadataStore is not
vulnerable to SQL injection attacks. It uses a variety of malicious inputs
to probe all data access methods and ensures that the application layer
correctly uses parameterized queries.

# ΛTAG: security_testing, sql_injection, storage_testing
"""

import asyncio
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from storage.distributed_storage import (
    DataClassification,
    SQLiteMetadataStore,
    StorageObject,
    StoragePolicy,
)

# A collection of common SQL injection payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "'; DROP TABLE storage_objects; --",
    "' UNION SELECT null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null --",
    "test_key' OR 1=1; --",
    "test_key' UNION ALL SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17 --",
    "test_key' AND 1=0; --",
    "test_key'; SELECT sql FROM sqlite_master; --"
]

class TestSQLiteMetadataStoreSQLInjection:
    """
    Test suite for SQL injection vulnerabilities in SQLiteMetadataStore.
    """

    @pytest.fixture
    def db_path(self):
        """Creates a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as fp:
            yield Path(fp.name)

    @pytest.fixture
    def metadata_store(self, db_path):
        """Initializes a SQLiteMetadataStore instance with a temporary database."""
        store = SQLiteMetadataStore(str(db_path))
        return store

    @pytest.fixture
    def sample_object(self):
        """Creates a sample StorageObject for testing."""
        return StorageObject(
            object_id="test-obj-123",
            key="safe/key/test.txt",
            size_bytes=1024,
            content_type="text/plain",
            content_hash="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            classification=DataClassification.INTERNAL,
            storage_policy=StoragePolicy.HOT,
            tags={"safe", "test"},
        )

    @pytest.mark.asyncio
    async def test_store_and_retrieve_sample_object(self, metadata_store, sample_object):
        """Verify that a valid object can be stored and retrieved."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        retrieved_obj = await metadata_store.get_object(sample_object.key)

        # Assert
        assert retrieved_obj is not None
        assert retrieved_obj.key == sample_object.key
        assert retrieved_obj.object_id == sample_object.object_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_get_object_injection(self, metadata_store, sample_object, payload):
        """Test for SQL injection in the get_object method."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        retrieved_obj = await metadata_store.get_object(payload)

        # Assert
        # The query should return None because no object with the malicious key exists.
        # If it returns anything else, it might be a sign of a successful injection.
        assert retrieved_obj is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_list_objects_injection_prefix(self, metadata_store, sample_object, payload):
        """Test for SQL injection in the list_objects method via the prefix parameter."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        objects = await metadata_store.list_objects(prefix=payload)

        # Assert
        # The query should return an empty list because no keys match the malicious prefix.
        assert len(objects) == 0

    @pytest.mark.asyncio
    async def test_list_objects_wildcard_safety(self, metadata_store, sample_object):
        """Ensure that wildcards in the prefix are treated as literals."""
        # Arrange
        await metadata_store.store_object(sample_object)
        # Create an object with a literal '%' in the key
        like_obj = sample_object
        like_obj.key = "safe/key/100%.txt"
        like_obj.object_id = "like-obj-456"
        await metadata_store.store_object(like_obj)

        # Act
        # The LIKE operator should match the literal '%' and not treat it as a wildcard
        objects = await metadata_store.list_objects(prefix="safe/key/100%")

        # Assert
        assert len(objects) == 1
        assert objects[0].key == "safe/key/100%.txt"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_update_access_stats_injection(self, metadata_store, sample_object, payload):
        """Test for SQL injection in the update_access_stats method."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        # This operation should not raise an error and should not modify other rows.
        await metadata_store.update_access_stats(payload)

        # Assert
        # Verify that the original, safe object was not modified.
        retrieved_obj = await metadata_store.get_object(sample_object.key)
        assert retrieved_obj.access_count == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_get_lifecycle_candidates_injection(self, metadata_store, sample_object, payload):
        """Test for SQL injection in the get_lifecycle_candidates method."""
        # This method's parameters are not directly from user input, but we test for safety nonetheless.
        # Arrange
        await metadata_store.store_object(sample_object)
        # We need to manipulate the payload to match the expected data type.
        # This is more of a defense-in-depth test.
        malicious_stage = StoragePolicy.HOT
        try:
            # If the payload can be cast to a StoragePolicy, use it
            malicious_stage = StoragePolicy(payload)
        except (ValueError, TypeError):
            # Otherwise, we can't proceed with this specific payload
            pass

        # Act
        candidates = await metadata_store.get_lifecycle_candidates(malicious_stage, datetime.now())

        # Assert
        # If the malicious_stage was a valid enum, it might return the sample object.
        # Otherwise, it should return an empty list. No error should be raised.
        if malicious_stage == StoragePolicy.HOT:
            assert len(candidates) <= 1
        else:
            assert len(candidates) == 0

    @pytest.mark.asyncio
    async def test_parameterized_queries_are_used(self, db_path, sample_object):
        """
        Verify that the underlying sqlite3.Connection.execute method is always
        called with parameters, never with a formatted raw SQL string.
        """
        # Arrange
        store = SQLiteMetadataStore(str(db_path))
        await store.store_object(sample_object)

        # Mock the connection's execute method
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None

            # Act
            await store.get_object("some/key")
            await store.list_objects(prefix="some/prefix")
            await store.update_access_stats("some/key")

            # Assert
            # Check every call to execute
            for call in mock_conn.execute.call_args_list:
                # The second argument should always be a tuple of parameters
                assert len(call.args) > 1, f"execute called without parameters: {call}"
                assert isinstance(call.args[1], tuple) or isinstance(call.args[1], list), \
                    f"execute called with non-tuple/list parameters: {call}"
                # Ensure the SQL string itself doesn't contain the values, which would indicate interpolation
                assert "some/key" not in call.args[0]
                assert "some/prefix" not in call.args[0]

    @pytest.mark.asyncio
    async def test_get_object_with_special_characters(self, metadata_store, sample_object):
        """Test retrieving an object with various special characters in its key."""
        # Arrange
        special_key = "key with spaces, 'quotes', \"double quotes\", and %percent%"
        sample_object.key = special_key
        sample_object.object_id = "special-char-obj"
        await metadata_store.store_object(sample_object)

        # Act
        retrieved_obj = await metadata_store.get_object(special_key)

        # Assert
        assert retrieved_obj is not None
        assert retrieved_obj.key == special_key

    @pytest.mark.asyncio
    async def test_get_object_with_unicode_characters(self, metadata_store, sample_object):
        """Test retrieving an object with Unicode characters in its key."""
        # Arrange
        unicode_key = "キー/세금/ειδικός/عام"
        sample_object.key = unicode_key
        sample_object.object_id = "unicode-obj"
        await metadata_store.store_object(sample_object)

        # Act
        retrieved_obj = await metadata_store.get_object(unicode_key)

        # Assert
        assert retrieved_obj is not None
        assert retrieved_obj.key == unicode_key

    @pytest.mark.asyncio
    async def test_get_object_with_empty_string_key(self, metadata_store):
        """Test that querying for an empty string key is handled safely."""
        # Act
        retrieved_obj = await metadata_store.get_object("")

        # Assert
        assert retrieved_obj is None

    @pytest.mark.asyncio
    async def test_list_objects_with_empty_prefix(self, metadata_store, sample_object):
        """Test listing objects with an empty prefix, which should return all objects."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        objects = await metadata_store.list_objects(prefix="")

        # Assert
        assert len(objects) == 1
        assert objects[0].key == sample_object.key

    @pytest.mark.asyncio
    async def test_no_rows_affected_by_failed_update(self, metadata_store, sample_object):
        """Ensure an update with a non-existent key doesn't affect other rows."""
        # Arrange
        await metadata_store.store_object(sample_object)

        # Act
        await metadata_store.update_access_stats("non-existent-key' OR 1=1; --")

        # Assert
        # The access count of the original object should remain unchanged.
        retrieved_obj = await metadata_store.get_object(sample_object.key)
        assert retrieved_obj is not None
        assert retrieved_obj.access_count == 0
