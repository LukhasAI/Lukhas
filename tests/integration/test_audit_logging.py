"""Integration tests for audit logging system.

Tests SOC 2 compliance, event storage, querying, and retention policies.
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from lukhas.governance.audit import (
    AuditConfig,
    AuditEvent,
    AuditEventType,
    AuditLogger,
    FileAuditStorage,
    InMemoryAuditStorage,
)
from lukhas.governance.audit.config import get_default_config, get_development_config, get_testing_config


class TestAuditEvent:
    """Test AuditEvent dataclass and serialization."""

    def test_event_creation(self):
        """Test creating a basic audit event."""
        event = AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_abc",
            ip_address="203.0.113.1",
            action="User login",
            success=True,
        )

        assert event.event_type == AuditEventType.LOGIN_SUCCESS
        assert event.user_id == "user_abc"
        assert event.ip_address == "203.0.113.1"
        assert event.success is True
        assert event.event_id  # UUID generated
        assert event.timestamp > 0  # Timestamp generated

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = AuditEvent(
            event_type=AuditEventType.DATA_READ,
            user_id="user_abc",
            resource_type="feedback_card",
            resource_id="card_123",
        )

        data = event.to_dict()

        assert data["event_type"] == "data.read"
        assert data["user_id"] == "user_abc"
        assert data["resource_type"] == "feedback_card"
        assert data["resource_id"] == "card_123"
        assert "event_id" in data
        assert "timestamp" in data

    def test_event_to_json(self):
        """Test converting event to JSON string."""
        event = AuditEvent(
            event_type=AuditEventType.DATA_CREATE,
            user_id="user_abc",
            action="Create feedback card",
        )

        json_str = event.to_json()
        data = json.loads(json_str)

        assert data["event_type"] == "data.create"
        assert data["user_id"] == "user_abc"
        assert data["action"] == "Create feedback card"

    def test_event_with_metadata(self):
        """Test event with additional metadata."""
        event = AuditEvent(
            event_type=AuditEventType.CONFIG_CHANGE,
            user_id="admin_abc",
            action="Update rate limit configuration",
            metadata={
                "old_value": 100,
                "new_value": 200,
                "config_key": "rate_limit.tier_0.requests"
            }
        )

        assert event.metadata["old_value"] == 100
        assert event.metadata["new_value"] == 200
        assert event.metadata["config_key"] == "rate_limit.tier_0.requests"


class TestInMemoryAuditStorage:
    """Test in-memory audit storage backend."""

    def test_store_and_retrieve_events(self):
        """Test storing and retrieving audit events."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events
        event1 = AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_abc",
            ip_address="203.0.113.1",
        )
        event2 = AuditEvent(
            event_type=AuditEventType.DATA_READ,
            user_id="user_abc",
            resource_type="feedback_card",
            resource_id="card_123",
        )

        storage.store_event(event1)
        storage.store_event(event2)

        # Retrieve all events
        events = storage.get_events()
        assert len(events) == 2
        assert events[0].event_id == event2.event_id  # Most recent first
        assert events[1].event_id == event1.event_id

    def test_filter_by_user_id(self):
        """Test filtering events by user ID."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events for different users
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_abc",
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_xyz",
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            user_id="user_abc",
        ))

        # Filter by user_id
        user_abc_events = storage.get_events(user_id="user_abc")
        assert len(user_abc_events) == 2
        assert all(e.user_id == "user_abc" for e in user_abc_events)

        user_xyz_events = storage.get_events(user_id="user_xyz")
        assert len(user_xyz_events) == 1
        assert user_xyz_events[0].user_id == "user_xyz"

    def test_filter_by_event_type(self):
        """Test filtering events by event type."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events of different types
        storage.store_event(AuditEvent(event_type=AuditEventType.LOGIN_SUCCESS))
        storage.store_event(AuditEvent(event_type=AuditEventType.LOGIN_FAILURE))
        storage.store_event(AuditEvent(event_type=AuditEventType.DATA_READ))
        storage.store_event(AuditEvent(event_type=AuditEventType.DATA_CREATE))

        # Filter by event type
        login_events = storage.get_events(
            event_types=[AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE]
        )
        assert len(login_events) == 2
        assert all(e.event_type in [AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE]
                   for e in login_events)

        data_events = storage.get_events(
            event_types=[AuditEventType.DATA_READ, AuditEventType.DATA_CREATE]
        )
        assert len(data_events) == 2

    def test_filter_by_time_range(self):
        """Test filtering events by time range."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events at different times
        now = time.time()
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now - 3600,  # 1 hour ago
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            timestamp=now - 1800,  # 30 minutes ago
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_CREATE,
            timestamp=now,  # Now
        ))

        # Filter by time range (last 45 minutes)
        recent_events = storage.get_events(start_time=now - 2700)
        assert len(recent_events) == 2

        # Filter by time range (last 2 hours)
        all_recent_events = storage.get_events(start_time=now - 7200)
        assert len(all_recent_events) == 3

    def test_filter_by_resource(self):
        """Test filtering events by resource type and ID."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events for different resources
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            resource_type="feedback_card",
            resource_id="card_123",
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_UPDATE,
            resource_type="feedback_card",
            resource_id="card_123",
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            resource_type="trace",
            resource_id="trace_456",
        ))

        # Filter by resource type
        feedback_events = storage.get_events(resource_type="feedback_card")
        assert len(feedback_events) == 2
        assert all(e.resource_type == "feedback_card" for e in feedback_events)

        # Filter by resource ID
        card_events = storage.get_events(resource_id="card_123")
        assert len(card_events) == 2
        assert all(e.resource_id == "card_123" for e in card_events)

        # Filter by both
        specific_events = storage.get_events(
            resource_type="feedback_card",
            resource_id="card_123"
        )
        assert len(specific_events) == 2

    def test_filter_by_success_status(self):
        """Test filtering events by success status."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store successful and failed events
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            success=True,
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_FAILURE,
            success=False,
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            success=True,
        ))

        # Filter by success status
        successful_events = storage.get_events(success=True)
        assert len(successful_events) == 2
        assert all(e.success is True for e in successful_events)

        failed_events = storage.get_events(success=False)
        assert len(failed_events) == 1
        assert failed_events[0].success is False

    def test_result_limit(self):
        """Test limiting number of results."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store many events
        for i in range(100):
            storage.store_event(AuditEvent(
                event_type=AuditEventType.DATA_READ,
                user_id=f"user_{i}",
            ))

        # Get limited results
        events = storage.get_events(limit=10)
        assert len(events) == 10

        # Get all results
        all_events = storage.get_events(limit=1000)
        assert len(all_events) == 100

    def test_cleanup_old_events(self):
        """Test removing old events."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store events at different times
        now = time.time()
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now - 86400,  # 1 day ago
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now - 7200,  # 2 hours ago
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now,  # Now
        ))

        # Clean up events older than 3 hours
        cutoff_time = now - 10800
        removed_count = storage.cleanup_old_events(cutoff_time)

        assert removed_count == 1
        remaining_events = storage.get_events()
        assert len(remaining_events) == 2

    def test_get_statistics(self):
        """Test getting audit log statistics."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config)

        # Store various events
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            success=True,
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_FAILURE,
            success=False,
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            success=True,
        ))
        storage.store_event(AuditEvent(
            event_type=AuditEventType.DATA_READ,
            success=True,
        ))

        stats = storage.get_statistics()

        assert stats["total_events"] == 4
        assert stats["filtered_events"] == 4
        assert stats["success_count"] == 3
        assert stats["failure_count"] == 1
        assert stats["success_rate"] == 0.75
        assert stats["storage_type"] == "in_memory"
        assert "data.read" in stats["event_type_counts"]
        assert stats["event_type_counts"]["data.read"] == 2

    def test_max_events_limit(self):
        """Test that storage respects max_events limit."""
        config = get_testing_config()
        storage = InMemoryAuditStorage(config, max_events=10)

        # Store more than max_events
        for i in range(20):
            storage.store_event(AuditEvent(
                event_type=AuditEventType.DATA_READ,
                user_id=f"user_{i}",
            ))

        # Should only keep last 10 events
        events = storage.get_events(limit=1000)
        assert len(events) == 10


class TestFileAuditStorage:
    """Test file-based audit storage backend."""

    def test_store_and_retrieve_events(self):
        """Test storing and retrieving events from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.jsonl"
            config = AuditConfig(log_file_path=log_file)
            storage = FileAuditStorage(config)

            # Store events
            event1 = AuditEvent(
                event_type=AuditEventType.LOGIN_SUCCESS,
                user_id="user_abc",
            )
            event2 = AuditEvent(
                event_type=AuditEventType.DATA_READ,
                user_id="user_abc",
            )

            storage.store_event(event1)
            storage.store_event(event2)

            # Retrieve events
            events = storage.get_events()
            assert len(events) == 2
            assert events[0].event_id == event2.event_id  # Most recent first

    def test_file_persistence(self):
        """Test that events persist across storage instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.jsonl"
            config = AuditConfig(log_file_path=log_file)

            # Store events in first instance
            storage1 = FileAuditStorage(config)
            storage1.store_event(AuditEvent(
                event_type=AuditEventType.LOGIN_SUCCESS,
                user_id="user_abc",
            ))

            # Retrieve events in second instance
            storage2 = FileAuditStorage(config)
            events = storage2.get_events()

            assert len(events) == 1
            assert events[0].user_id == "user_abc"

    def test_file_rotation(self):
        """Test log file rotation when size limit exceeded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.jsonl"
            config = AuditConfig(
                log_file_path=log_file,
                max_file_size_mb=0.001,  # Very small limit for testing
                max_backup_count=2,
            )
            storage = FileAuditStorage(config)

            # Store many events to trigger rotation
            for i in range(100):
                storage.store_event(AuditEvent(
                    event_type=AuditEventType.DATA_READ,
                    user_id=f"user_{i}",
                    metadata={"large_data": "x" * 1000}  # Make events larger
                ))

            # Check that backup files were created
            backup_files = list(Path(tmpdir).glob("audit.*.jsonl"))
            assert len(backup_files) > 0

    def test_cleanup_old_events(self):
        """Test removing old events from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.jsonl"
            config = AuditConfig(log_file_path=log_file)
            storage = FileAuditStorage(config)

            # Store events at different times
            now = time.time()
            storage.store_event(AuditEvent(
                event_type=AuditEventType.LOGIN_SUCCESS,
                timestamp=now - 86400,  # 1 day ago
            ))
            storage.store_event(AuditEvent(
                event_type=AuditEventType.LOGIN_SUCCESS,
                timestamp=now,  # Now
            ))

            # Clean up old events
            cutoff_time = now - 7200  # 2 hours ago
            removed_count = storage.cleanup_old_events(cutoff_time)

            assert removed_count == 1

            # Verify only recent event remains
            events = storage.get_events()
            assert len(events) == 1
            assert events[0].timestamp >= cutoff_time

    def test_get_statistics(self):
        """Test getting statistics from file storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.jsonl"
            config = AuditConfig(log_file_path=log_file)
            storage = FileAuditStorage(config)

            # Store events
            storage.store_event(AuditEvent(
                event_type=AuditEventType.LOGIN_SUCCESS,
                success=True,
            ))
            storage.store_event(AuditEvent(
                event_type=AuditEventType.LOGIN_FAILURE,
                success=False,
            ))

            stats = storage.get_statistics()

            assert stats["total_events"] == 2
            assert stats["success_count"] == 1
            assert stats["failure_count"] == 1
            assert stats["storage_type"] == "file"
            assert stats["log_file"] == str(log_file)
            assert stats["file_size_bytes"] > 0


class TestAuditLogger:
    """Test high-level audit logger."""

    def test_log_authentication_event(self):
        """Test logging authentication events."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        logger.log_authentication_event(
            user_id="user_abc",
            event_type=AuditEventType.LOGIN_SUCCESS,
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0 ...",
            success=True,
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.LOGIN_SUCCESS
        assert events[0].user_id == "user_abc"
        assert events[0].ip_address == "203.0.113.1"
        assert events[0].success is True

    def test_log_data_access_event(self):
        """Test logging data access events."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        logger.log_data_access_event(
            user_id="user_abc",
            event_type=AuditEventType.DATA_READ,
            resource_type="feedback_card",
            resource_id="card_123",
            ip_address="203.0.113.1",
            success=True,
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.DATA_READ
        assert events[0].resource_type == "feedback_card"
        assert events[0].resource_id == "card_123"

    def test_log_security_event(self):
        """Test logging security events."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        logger.log_security_event(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            user_id="user_abc",
            ip_address="203.0.113.1",
            success=False,
            error_message="Rate limit exceeded",
            metadata={"limit": 100, "window": 3600}
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.RATE_LIMIT_EXCEEDED
        assert events[0].success is False
        assert events[0].metadata["limit"] == 100

    def test_log_admin_action(self):
        """Test logging administrative actions."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        logger.log_admin_action(
            user_id="admin_abc",
            event_type=AuditEventType.CONFIG_CHANGE,
            action="Updated rate limit configuration",
            resource_type="configuration",
            resource_id="rate_limit.tier_0",
            success=True,
            metadata={"old_value": 100, "new_value": 200}
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.CONFIG_CHANGE
        assert events[0].action == "Updated rate limit configuration"

    def test_disabled_logging(self):
        """Test that logging can be disabled."""
        config = AuditConfig(enabled=False)
        logger = AuditLogger(config=config)

        logger.log_authentication_event(
            user_id="user_abc",
            event_type=AuditEventType.LOGIN_SUCCESS,
        )

        events = logger.get_events()
        assert len(events) == 0

    def test_category_logging_disabled(self):
        """Test disabling specific event categories."""
        config = AuditConfig(
            log_authentication=False,
            log_data_access=True,
        )
        logger = AuditLogger(config=config)

        # Authentication event should not be logged
        logger.log_authentication_event(
            user_id="user_abc",
            event_type=AuditEventType.LOGIN_SUCCESS,
        )

        # Data access event should be logged
        logger.log_data_access_event(
            user_id="user_abc",
            event_type=AuditEventType.DATA_READ,
            resource_type="feedback_card",
            resource_id="card_123",
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.DATA_READ

    def test_cleanup_old_logs(self):
        """Test cleaning up old logs."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        # Store events at different times
        now = time.time()
        logger.storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now - 86400,  # 1 day ago
        ))
        logger.storage.store_event(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            timestamp=now,  # Now
        ))

        # Clean up old logs (keep last 12 hours)
        removed_count = logger.cleanup_old_logs(retention_days=0.5)

        assert removed_count == 1

        events = logger.get_events()
        assert len(events) == 1

    def test_get_statistics(self):
        """Test getting audit statistics."""
        config = get_testing_config()
        logger = AuditLogger(config=config)

        # Log various events
        logger.log_authentication_event(
            user_id="user_abc",
            event_type=AuditEventType.LOGIN_SUCCESS,
            success=True,
        )
        logger.log_authentication_event(
            user_id="user_xyz",
            event_type=AuditEventType.LOGIN_FAILURE,
            success=False,
        )
        logger.log_data_access_event(
            user_id="user_abc",
            event_type=AuditEventType.DATA_READ,
            resource_type="feedback_card",
            resource_id="card_123",
            success=True,
        )

        stats = logger.get_statistics()

        assert stats["total_events"] == 3
        assert stats["success_count"] == 2
        assert stats["failure_count"] == 1


class TestAuditConfig:
    """Test audit configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = get_default_config()

        assert config.enabled is True
        assert config.retention_days == 2555  # 7 years
        assert config.log_authentication is True
        assert config.log_data_access is True
        assert config.log_admin_actions is True
        assert config.log_security_events is True

    def test_development_config(self):
        """Test development configuration."""
        config = get_development_config()

        assert config.enabled is True
        assert config.retention_days == 30  # 30 days
        assert config.include_request_body is True
        assert config.include_response_body is True
        assert config.async_logging is False  # Sync for debugging

    def test_testing_config(self):
        """Test testing configuration."""
        config = get_testing_config()

        assert config.enabled is True
        assert config.log_file_path is None  # In-memory only
        assert config.retention_days == 1
        assert config.async_logging is False  # Sync for tests

    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid retention_days
        with pytest.raises(ValueError, match="retention_days must be at least 1"):
            AuditConfig(retention_days=0)

        # Invalid max_file_size_mb
        with pytest.raises(ValueError, match="max_file_size_mb must be positive"):
            AuditConfig(max_file_size_mb=0)

        # Invalid max_backup_count
        with pytest.raises(ValueError, match="max_backup_count must be non-negative"):
            AuditConfig(max_backup_count=-1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
