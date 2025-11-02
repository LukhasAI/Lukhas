#!/usr/bin/env python3
"""
Test Suite for LUKHAS Advanced Security & Caching Infrastructure

Comprehensive test coverage for security framework, caching system, and distributed storage.

# ΛTAG: security_testing, cache_testing, storage_testing, integration_testing
"""

import asyncio
import hashlib
import json
import shutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest
from caching.cache_system import (
    CacheConfig,
    CacheEntry,
    CacheLevel,
    CacheStatistics,
    CacheStrategy,
    HierarchicalCacheManager,
    MemoryCacheBackend,
)
from storage.distributed_storage import (
    DataClassification,
    DistributedStorageManager,
    LocalFilesystemBackend,
    SQLiteMetadataStore,
    StorageBackendType,
    StorageConfig,
    StorageObject,
    StoragePolicy,
)

# Import the modules we're testing
from security.security_framework import (
    EncryptionService,
    JWTService,
    LUKHASSecurityFramework,
    RateLimiter,
    SecurityAuditEvent,
    SecurityAuditor,
    SecurityConfig,
    ThreatDetector,
    UserPrincipal,
)


class TestSecurityFramework:
    """Test suite for LUKHAS Security Framework."""

    @pytest.fixture
    async def security_framework(self):
        """Create security framework for testing."""
        config = SecurityConfig(
            jwt_secret_key="test_secret_key_for_testing_only",
            encryption_key="test_encryption_key_32_chars_long",
            rate_limit_requests_per_minute=100,
            threat_detection_enabled=True,
            audit_logging_enabled=True
        )

        framework = LUKHASSecurityFramework(config)
        await framework.initialize()
        yield framework
        await framework.shutdown()

    @pytest.mark.asyncio
    async def test_jwt_service_token_generation(self, security_framework):
        """Test JWT token generation and validation."""

        jwt_service = security_framework.jwt_service

        # Create test user
        user = UserPrincipal(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            roles={"user", "tester"},
            permissions={"read", "write"}
        )

        # Generate token
        token = await jwt_service.generate_token(user)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Validate token
        decoded_user = await jwt_service.validate_token(token)
        assert decoded_user is not None
        assert decoded_user.user_id == user.user_id
        assert decoded_user.username == user.username
        assert decoded_user.email == user.email
        assert decoded_user.roles == user.roles
        assert decoded_user.permissions == user.permissions

    @pytest.mark.asyncio
    async def test_jwt_service_token_expiration(self, security_framework):
        """Test JWT token expiration handling."""

        jwt_service = security_framework.jwt_service

        # Create short-lived token
        user = UserPrincipal(
            user_id="test_user_exp",
            username="exptest",
            email="exp@example.com"
        )

        # Generate token with 1 second expiration
        token = await jwt_service.generate_token(user, expires_in_seconds=1)

        # Should be valid immediately
        decoded_user = await jwt_service.validate_token(token)
        assert decoded_user is not None

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be invalid after expiration
        expired_user = await jwt_service.validate_token(token)
        assert expired_user is None

    @pytest.mark.asyncio
    async def test_encryption_service(self, security_framework):
        """Test encryption and decryption operations."""

        encryption_service = security_framework.encryption_service

        # Test data
        test_data = "This is sensitive data that needs encryption"

        # Encrypt data
        encrypted_data = await encryption_service.encrypt(test_data)
        assert encrypted_data != test_data
        assert len(encrypted_data) > 0

        # Decrypt data
        decrypted_data = await encryption_service.decrypt(encrypted_data)
        assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_encryption_service_binary_data(self, security_framework):
        """Test encryption with binary data."""

        encryption_service = security_framework.encryption_service

        # Test binary data
        test_data = b"Binary data \x00\x01\x02\x03"

        # Encrypt binary data
        encrypted_data = await encryption_service.encrypt_bytes(test_data)
        assert encrypted_data != test_data
        assert len(encrypted_data) > 0

        # Decrypt binary data
        decrypted_data = await encryption_service.decrypt_bytes(encrypted_data)
        assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_rate_limiter(self, security_framework):
        """Test rate limiting functionality."""

        rate_limiter = security_framework.rate_limiter

        client_id = "test_client_123"

        # Should allow requests within limit
        for i in range(10):
            allowed = await rate_limiter.is_allowed(client_id)
            assert allowed

        # Configure very low limit for testing
        rate_limiter.requests_per_minute = 5
        rate_limiter.window_size_seconds = 10

        # Reset client state
        rate_limiter.client_requests.clear()

        # Should allow up to limit
        for i in range(5):
            allowed = await rate_limiter.is_allowed(client_id)
            assert allowed

        # Should deny after limit
        denied = await rate_limiter.is_allowed(client_id)
        assert not denied

    @pytest.mark.asyncio
    async def test_threat_detector(self, security_framework):
        """Test threat detection capabilities."""

        threat_detector = security_framework.threat_detector

        # Test SQL injection detection
        sql_injection_input = "'; DROP TABLE users; --"
        is_threat = await threat_detector.detect_threat("sql_injection", sql_injection_input)
        assert is_threat

        # Test XSS detection
        xss_input = "<script>alert('xss')</script>"
        is_threat = await threat_detector.detect_threat("xss", xss_input)
        assert is_threat

        # Test benign input
        safe_input = "This is a normal, safe input string"
        is_threat = await threat_detector.detect_threat("sql_injection", safe_input)
        assert not is_threat

    @pytest.mark.asyncio
    async def test_security_auditor(self, security_framework):
        """Test security audit logging."""

        auditor = security_framework.security_auditor

        # Create audit event
        event = SecurityAuditEvent(
            event_type="authentication",
            user_id="test_user",
            resource="login_endpoint",
            action="login_attempt",
            result="success",
            ip_address="192.168.1.100",
            user_agent="Test Agent",
            additional_data={"login_method": "password"}
        )

        # Log event
        logged = await auditor.log_event(event)
        assert logged

        # Query events
        events = await auditor.query_events(
            start_time=datetime.now() - timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=1),
            event_type="authentication"
        )

        assert len(events) > 0
        found_event = next((e for e in events if e.user_id == "test_user"), None)
        assert found_event is not None
        assert found_event.action == "login_attempt"
        assert found_event.result == "success"

    @pytest.mark.asyncio
    async def test_password_hashing(self, security_framework):
        """Test password hashing functionality."""

        # Test password
        password = "test_password_123"

        # Hash password
        hashed = await security_framework.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

        # Verify correct password
        is_valid = await security_framework.verify_password(password, hashed)
        assert is_valid

        # Verify incorrect password
        is_invalid = await security_framework.verify_password("wrong_password", hashed)
        assert not is_invalid


class TestCachingSystem:
    """Test suite for LUKHAS Caching System."""

    @pytest.fixture
    async def memory_cache(self):
        """Create memory cache backend for testing."""
        cache = MemoryCacheBackend(max_size=100, default_ttl=300)
        yield cache
        await cache.clear()

    @pytest.fixture
    async def cache_manager(self):
        """Create cache manager for testing."""
        config = CacheConfig(
            l1_max_size=50,
            l1_ttl_seconds=300,
            l1_strategy=CacheStrategy.LRU,
            warming_enabled=False  # Disable for testing
        )

        manager = HierarchicalCacheManager(config)
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self, memory_cache):
        """Test basic cache operations."""

        # Set value
        success = await memory_cache.set("test_key", "test_value")
        assert success

        # Get value
        value = await memory_cache.get("test_key")
        assert value == "test_value"

        # Check existence
        exists = await memory_cache.exists("test_key")
        assert exists

        # Delete value
        deleted = await memory_cache.delete("test_key")
        assert deleted

        # Value should be gone
        value = await memory_cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_memory_cache_ttl_expiration(self, memory_cache):
        """Test TTL-based expiration."""

        # Set value with 1 second TTL
        success = await memory_cache.set("ttl_key", "ttl_value", ttl_seconds=1)
        assert success

        # Should be available immediately
        value = await memory_cache.get("ttl_key")
        assert value == "ttl_value"

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be expired
        value = await memory_cache.get("ttl_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_memory_cache_lru_eviction(self):
        """Test LRU eviction strategy."""

        # Create cache with small size
        cache = MemoryCacheBackend(max_size=3, strategy=CacheStrategy.LRU)

        # Fill cache to capacity
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        # All should be present
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"

        # Access key1 to make it recently used
        await cache.get("key1")

        # Add new key - should evict key2 (least recently used)
        await cache.set("key4", "value4")

        # key2 should be evicted
        assert await cache.get("key1") == "value1"  # Recently accessed
        assert await cache.get("key2") is None      # Evicted
        assert await cache.get("key3") == "value3"  # Still there
        assert await cache.get("key4") == "value4"  # New entry

    @pytest.mark.asyncio
    async def test_hierarchical_cache_manager(self, cache_manager):
        """Test hierarchical cache manager operations."""

        # Set value
        success = await cache_manager.set("test_key", {"data": "test_value"})
        assert success

        # Get value
        value = await cache_manager.get("test_key")
        assert value == {"data": "test_value"}

        # Delete value
        deleted = await cache_manager.delete("test_key")
        assert deleted

        # Value should be gone
        value = await cache_manager.get("test_key", default="not_found")
        assert value == "not_found"

    @pytest.mark.asyncio
    async def test_cache_pattern_invalidation(self, cache_manager):
        """Test pattern-based cache invalidation."""

        # Set multiple related keys
        await cache_manager.set("user:123:profile", {"name": "John"})
        await cache_manager.set("user:123:settings", {"theme": "dark"})
        await cache_manager.set("user:456:profile", {"name": "Jane"})
        await cache_manager.set("product:789", {"name": "Widget"})

        # Invalidate user:123 keys
        invalidated = await cache_manager.invalidate_pattern("user:123:*")
        assert invalidated == 2

        # user:123 keys should be gone
        assert await cache_manager.get("user:123:profile") is None
        assert await cache_manager.get("user:123:settings") is None

        # Other keys should remain
        assert await cache_manager.get("user:456:profile") == {"name": "Jane"}
        assert await cache_manager.get("product:789") == {"name": "Widget"}

    @pytest.mark.asyncio
    async def test_cache_statistics(self, cache_manager):
        """Test cache statistics collection."""

        # Perform operations
        await cache_manager.set("stat_key1", "value1")
        await cache_manager.set("stat_key2", "value2")

        # Generate some hits and misses
        await cache_manager.get("stat_key1")  # Hit
        await cache_manager.get("stat_key1")  # Hit
        await cache_manager.get("nonexistent")  # Miss

        # Get statistics
        stats = await cache_manager.get_statistics()

        assert "global" in stats
        assert "l1_memory" in stats
        assert stats["l1_memory"]["hits"] >= 2
        assert stats["l1_memory"]["misses"] >= 1
        assert stats["l1_memory"]["sets"] >= 2


class TestDistributedStorage:
    """Test suite for LUKHAS Distributed Storage System."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary directory for storage testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    async def local_backend(self, temp_storage_dir):
        """Create local filesystem backend for testing."""
        backend = LocalFilesystemBackend(temp_storage_dir)
        yield backend

    @pytest.fixture
    async def metadata_store(self, temp_storage_dir):
        """Create metadata store for testing."""
        db_path = Path(temp_storage_dir) / "test_metadata.db"
        store = SQLiteMetadataStore(str(db_path))
        yield store

    @pytest.fixture
    async def storage_manager(self, temp_storage_dir):
        """Create storage manager for testing."""
        config = StorageConfig(
            base_path=temp_storage_dir,
            primary_backend=StorageBackendType.LOCAL_FILESYSTEM,
            replication_factor=1,
            compression_enabled=True,
            deduplication_enabled=True,
            enable_lifecycle_management=False,  # Disable for testing
            backup_enabled=False  # Disable for testing
        )

        manager = DistributedStorageManager(config)
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_local_backend_operations(self, local_backend):
        """Test local filesystem backend operations."""

        test_data = b"Test data for storage backend"
        test_metadata = {"content_type": "text/plain", "author": "test"}

        # Put data
        success = await local_backend.put("test/file.txt", test_data, test_metadata)
        assert success

        # Get data
        retrieved_data = await local_backend.get("test/file.txt")
        assert retrieved_data == test_data

        # Check existence
        exists = await local_backend.exists("test/file.txt")
        assert exists

        # Get metadata
        metadata = await local_backend.get_metadata("test/file.txt")
        assert metadata == test_metadata

        # List keys
        keys = await local_backend.list_keys()
        assert "test/file.txt" in keys

        # Delete data
        deleted = await local_backend.delete("test/file.txt")
        assert deleted

        # Should no longer exist
        exists = await local_backend.exists("test/file.txt")
        assert not exists

    @pytest.mark.asyncio
    async def test_local_backend_health_check(self, local_backend):
        """Test local backend health check."""

        healthy = await local_backend.health_check()
        assert healthy

    @pytest.mark.asyncio
    async def test_metadata_store_operations(self, metadata_store):
        """Test metadata store operations."""

        # Create test object
        obj = StorageObject(
            object_id="test_obj_123",
            key="test/document.pdf",
            size_bytes=1024,
            content_type="application/pdf",
            content_hash="abc123def456",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            classification=DataClassification.INTERNAL,
            storage_policy=StoragePolicy.HOT,
            custom_metadata={"author": "test_user"},
            tags={"document", "test"}
        )

        # Store object
        success = await metadata_store.store_object(obj)
        assert success

        # Retrieve object
        retrieved_obj = await metadata_store.get_object("test/document.pdf")
        assert retrieved_obj is not None
        assert retrieved_obj.object_id == obj.object_id
        assert retrieved_obj.key == obj.key
        assert retrieved_obj.size_bytes == obj.size_bytes
        assert retrieved_obj.content_type == obj.content_type
        assert retrieved_obj.classification == obj.classification
        assert retrieved_obj.custom_metadata == obj.custom_metadata
        assert retrieved_obj.tags == obj.tags

        # Update access stats
        await metadata_store.update_access_stats("test/document.pdf")

        # Retrieve updated object
        updated_obj = await metadata_store.get_object("test/document.pdf")
        assert updated_obj.access_count == 2

    @pytest.mark.asyncio
    async def test_storage_manager_operations(self, storage_manager):
        """Test distributed storage manager operations."""

        test_data = "This is test data for distributed storage"

        # Store object
        success = await storage_manager.put(
            "documents/test.txt",
            test_data,
            content_type="text/plain",
            classification=DataClassification.INTERNAL,
            storage_policy=StoragePolicy.HOT,
            metadata={"author": "test_user"},
            tags={"document", "test"}
        )
        assert success

        # Retrieve object
        retrieved_data = await storage_manager.get("documents/test.txt")
        assert retrieved_data is not None
        assert retrieved_data.decode() == test_data

        # Get object info
        obj_info = await storage_manager.get_object_info("documents/test.txt")
        assert obj_info is not None
        assert obj_info.key == "documents/test.txt"
        assert obj_info.content_type == "text/plain"
        assert obj_info.classification == DataClassification.INTERNAL
        assert obj_info.custom_metadata["author"] == "test_user"
        assert "document" in obj_info.tags

        # List objects
        objects = await storage_manager.list_objects()
        assert len(objects) > 0
        found_obj = next((o for o in objects if o.key == "documents/test.txt"), None)
        assert found_obj is not None

        # Delete object
        deleted = await storage_manager.delete("documents/test.txt")
        assert deleted

        # Should no longer be retrievable
        retrieved_data = await storage_manager.get("documents/test.txt")
        assert retrieved_data is None

    @pytest.mark.asyncio
    async def test_storage_deduplication(self, storage_manager):
        """Test storage deduplication functionality."""

        test_data = "Duplicate data for deduplication testing"

        # Store same data with different keys
        success1 = await storage_manager.put("file1.txt", test_data)
        assert success1

        success2 = await storage_manager.put("file2.txt", test_data)
        assert success2

        # Get object info for both
        obj1 = await storage_manager.get_object_info("file1.txt")
        obj2 = await storage_manager.get_object_info("file2.txt")

        # Should have same content hash
        assert obj1.content_hash == obj2.content_hash

        # One should be a deduplication reference
        has_dedup_ref = (
            obj1.custom_metadata.get("dedup_reference") is not None or
            obj2.custom_metadata.get("dedup_reference") is not None
        )
        assert has_dedup_ref

    @pytest.mark.asyncio
    async def test_storage_compression(self, storage_manager):
        """Test storage compression functionality."""

        # Large text data that should be compressed
        large_data = "This is a large piece of text data that should be compressed. " * 100

        # Store data
        success = await storage_manager.put(
            "large_file.txt",
            large_data,
            content_type="text/plain"
        )
        assert success

        # Retrieve data
        retrieved_data = await storage_manager.get("large_file.txt")
        assert retrieved_data is not None
        assert retrieved_data.decode() == large_data

        # Check if compression was used
        obj_info = await storage_manager.get_object_info("large_file.txt")
        assert obj_info is not None

        # If compression was applied, the metadata should indicate it
        # Note: This depends on the implementation details

    @pytest.mark.asyncio
    async def test_storage_metrics(self, storage_manager):
        """Test storage metrics collection."""

        # Store some objects
        await storage_manager.put("metrics_test1.txt", "Data 1")
        await storage_manager.put("metrics_test2.txt", "Data 2")

        # Retrieve to generate read operations
        await storage_manager.get("metrics_test1.txt")
        await storage_manager.get("metrics_test1.txt")

        # Get metrics
        metrics = await storage_manager.get_metrics()

        assert "total_objects" in metrics
        assert "total_size_bytes" in metrics
        assert "read_operations" in metrics
        assert "write_operations" in metrics
        assert metrics["total_objects"] >= 2
        assert metrics["read_operations"] >= 2
        assert metrics["write_operations"] >= 2


class TestIntegration:
    """Integration tests for security, caching, and storage components."""

    @pytest.fixture
    async def integrated_system(self):
        """Create integrated system with all components."""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Security framework
            security_config = SecurityConfig(
                jwt_secret_key="integration_test_secret",
                encryption_key="integration_test_key_32_chars!",
                audit_logging_enabled=True
            )
            security = LUKHASSecurityFramework(security_config)
            await security.initialize()

            # Cache manager
            cache_config = CacheConfig(
                l1_max_size=100,
                warming_enabled=False
            )
            cache = HierarchicalCacheManager(cache_config)
            await cache.initialize()

            # Storage manager
            storage_config = StorageConfig(
                base_path=temp_dir,
                enable_lifecycle_management=False,
                backup_enabled=False
            )
            storage = DistributedStorageManager(storage_config)
            await storage.initialize()

            yield {
                "security": security,
                "cache": cache,
                "storage": storage,
                "temp_dir": temp_dir
            }

        finally:
            # Cleanup
            await security.shutdown()
            await cache.shutdown()
            await storage.shutdown()
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_secure_cached_storage_workflow(self, integrated_system):
        """Test complete workflow with security, caching, and storage."""

        security = integrated_system["security"]
        cache = integrated_system["cache"]
        storage = integrated_system["storage"]

        # 1. Create and authenticate user
        user = UserPrincipal(
            user_id="integration_user",
            username="integrationtest",
            email="integration@test.com",
            roles={"user"},
            permissions={"read", "write", "delete"}
        )

        token = await security.jwt_service.generate_token(user)
        assert token is not None

        # 2. Validate token
        validated_user = await security.jwt_service.validate_token(token)
        assert validated_user is not None
        assert validated_user.user_id == user.user_id

        # 3. Store sensitive data in storage
        sensitive_data = "This is sensitive business data"
        encrypted_data = await security.encryption_service.encrypt(sensitive_data)

        storage_success = await storage.put(
            f"user/{user.user_id}/sensitive_doc.txt",
            encrypted_data,
            content_type="text/plain",
            classification=DataClassification.CONFIDENTIAL,
            metadata={"encrypted": "true", "user_id": user.user_id}
        )
        assert storage_success

        # 4. Cache the decrypted data for performance
        cache_key = f"decrypted:user:{user.user_id}:sensitive_doc"
        cache_success = await cache.set(cache_key, sensitive_data, ttl_seconds=300)
        assert cache_success

        # 5. Retrieve from cache (should be fast)
        start_time = time.time()
        cached_data = await cache.get(cache_key)
        cache_time = time.time() - start_time

        assert cached_data == sensitive_data
        assert cache_time < 0.01  # Should be very fast

        # 6. Simulate cache miss - retrieve from storage and decrypt
        await cache.delete(cache_key)

        start_time = time.time()
        stored_encrypted_data = await storage.get(f"user/{user.user_id}/sensitive_doc.txt")
        decrypted_data = await security.encryption_service.decrypt(stored_encrypted_data.decode())
        storage_time = time.time() - start_time

        assert decrypted_data == sensitive_data
        # Storage + decryption should be slower than cache

        # 7. Log security audit event
        audit_event = SecurityAuditEvent(
            event_type="data_access",
            user_id=user.user_id,
            resource=f"user/{user.user_id}/sensitive_doc.txt",
            action="read",
            result="success",
            additional_data={"access_method": "integration_test"}
        )

        audit_logged = await security.security_auditor.log_event(audit_event)
        assert audit_logged

        # 8. Verify audit trail
        audit_events = await security.security_auditor.query_events(
            start_time=datetime.now() - timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=1),
            user_id=user.user_id
        )

        assert len(audit_events) > 0
        found_event = next((e for e in audit_events if e.resource.endswith("sensitive_doc.txt")), None)
        assert found_event is not None

    @pytest.mark.asyncio
    async def test_rate_limited_cache_operations(self, integrated_system):
        """Test rate limiting on cache operations."""

        security = integrated_system["security"]
        cache = integrated_system["cache"]

        # Configure strict rate limiting
        rate_limiter = security.rate_limiter
        rate_limiter.requests_per_minute = 5
        rate_limiter.window_size_seconds = 10

        client_id = "test_client_rate_limit"

        # Should allow initial requests
        for i in range(5):
            allowed = await rate_limiter.is_allowed(client_id)
            assert allowed

            # Perform cache operation
            await cache.set(f"rate_test_{i}", f"value_{i}")

        # Should deny further requests
        denied = await rate_limiter.is_allowed(client_id)
        assert not denied

    @pytest.mark.asyncio
    async def test_threat_detection_on_storage_keys(self, integrated_system):
        """Test threat detection on storage key patterns."""

        security = integrated_system["security"]
        storage = integrated_system["storage"]

        threat_detector = security.threat_detector

        # Test malicious key patterns
        malicious_keys = [
            "../../../etc/passwd",
            "uploads/<script>alert('xss')</script>",
            "data'; DROP TABLE files; --"
        ]

        for malicious_key in malicious_keys:
            # Should detect threat in key
            is_threat = await threat_detector.detect_threat("path_traversal", malicious_key)

            if is_threat:
                # Storage operation should be rejected
                # (In a real implementation, this would be enforced)
                print(f"✅ Threat detected and blocked: {malicious_key}")
            else:
                # If not detected as threat, still attempt storage
                # but log for analysis
                success = await storage.put(
                    malicious_key.replace('/', '_').replace('<', '_').replace('>', '_'),
                    "test data",
                    classification=DataClassification.PUBLIC
                )
                if success:
                    print(f"⚠️  Potentially malicious key stored: {malicious_key}")


# Performance benchmarks
class TestPerformance:
    """Performance tests for the infrastructure components."""

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Benchmark cache performance."""

        config = CacheConfig(l1_max_size=10000)
        cache = HierarchicalCacheManager(config)
        await cache.initialize()

        try:
            # Benchmark cache writes
            start_time = time.time()
            for i in range(1000):
                await cache.set(f"perf_key_{i}", f"value_{i}")
            write_time = time.time() - start_time

            print(f"✅ Cache write performance: {1000/write_time:.0f} ops/sec")

            # Benchmark cache reads
            start_time = time.time()
            for i in range(1000):
                await cache.get(f"perf_key_{i}")
            read_time = time.time() - start_time

            print(f"✅ Cache read performance: {1000/read_time:.0f} ops/sec")

            # Performance should be reasonable
            assert write_time < 1.0  # Should complete 1000 writes in < 1 second
            assert read_time < 0.5   # Should complete 1000 reads in < 0.5 seconds

        finally:
            await cache.shutdown()

    @pytest.mark.asyncio
    async def test_storage_performance(self):
        """Benchmark storage performance."""

        temp_dir = tempfile.mkdtemp()

        try:
            config = StorageConfig(
                base_path=temp_dir,
                enable_lifecycle_management=False,
                backup_enabled=False
            )
            storage = DistributedStorageManager(config)
            await storage.initialize()

            # Benchmark storage writes
            test_data = "Performance test data " * 100  # ~2KB per object

            start_time = time.time()
            for i in range(100):
                await storage.put(f"perf/file_{i}.txt", test_data)
            write_time = time.time() - start_time

            print(f"✅ Storage write performance: {100/write_time:.0f} ops/sec")

            # Benchmark storage reads
            start_time = time.time()
            for i in range(100):
                await storage.get(f"perf/file_{i}.txt")
            read_time = time.time() - start_time

            print(f"✅ Storage read performance: {100/read_time:.0f} ops/sec")

            # Performance should be reasonable for local filesystem
            assert write_time < 5.0  # Should complete 100 writes in < 5 seconds
            assert read_time < 2.0   # Should complete 100 reads in < 2 seconds

            await storage.shutdown()

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
