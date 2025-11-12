"""Comprehensive test suite for LUKHAS governance audit modules."""

import json
import os
import time
from unittest.mock import MagicMock, patch

import pytest
from pathlib import Path

from lukhas.governance.audit import AuditEvent, AuditEventType, AuditLogger
from lukhas.governance.audit.config import AuditConfig, get_default_config, get_development_config, get_testing_config
from lukhas.governance.audit.storage import InMemoryAuditStorage, FileAuditStorage


# region: Fixtures

@pytest.fixture
def test_config():
    """Provides a testing configuration with in-memory storage."""
    return get_testing_config()

@pytest.fixture
def logger(test_config):
    """Provides an AuditLogger instance with in-memory storage for testing."""
    return AuditLogger(config=test_config)

@pytest.fixture
def file_logger(tmp_path):
    """Provides an AuditLogger instance with file-based storage for testing."""
    log_file = tmp_path / "audit.jsonl"
    config = AuditConfig(log_file_path=log_file, async_logging=False, max_file_size_mb=1, max_backup_count=2)
    return AuditLogger(config=config)

# endregion


# region: Tests for config.py

def test_audit_config_defaults():
    """Test that AuditConfig initializes with correct default values."""
    config = AuditConfig()
    assert config.enabled is True
    assert config.log_file_path is None
    assert config.retention_days == 2555
    assert config.max_file_size_mb == 100
    assert config.max_backup_count == 10
    assert config.async_logging is True

def test_audit_config_post_init_validation():
    """Test the validation logic in AuditConfig.__post_init__."""
    with pytest.raises(ValueError, match="retention_days must be at least 1"):
        AuditConfig(retention_days=0)

    with pytest.raises(ValueError, match="max_file_size_mb must be positive"):
        AuditConfig(max_file_size_mb=0)

    with pytest.raises(ValueError, match="max_backup_count must be non-negative"):
        AuditConfig(max_backup_count=-1)

def test_audit_config_path_creation(tmp_path):
    """Test that the log file's parent directory is created if it doesn't exist."""
    log_dir = tmp_path / "audit_logs"
    log_file = log_dir / "audit.log"
    assert not log_dir.exists()

    AuditConfig(log_file_path=log_file)
    assert log_dir.exists()
    assert log_dir.is_dir()

def test_get_default_config():
    """Test the get_default_config helper function."""
    config = get_default_config()
    assert config.enabled is True
    assert isinstance(config.log_file_path, Path)
    assert config.log_file_path.name == "audit.jsonl"
    assert config.retention_days == 2555
    assert config.include_request_body is False
    assert config.async_logging is True

def test_get_development_config():
    """Test the get_development_config helper function."""
    config = get_development_config()
    assert config.retention_days == 30
    assert config.include_request_body is True
    assert config.async_logging is False

def test_get_testing_config():
    """Test the get_testing_config helper function."""
    config = get_testing_config()
    assert config.log_file_path is None
    assert config.retention_days == 1
    assert config.async_logging is False

# endregion


# region: Tests for logger.py

def test_logger_initialization(test_config):
    """Test AuditLogger initialization."""
    logger = AuditLogger(config=test_config)
    assert logger.config == test_config
    assert isinstance(logger.storage, InMemoryAuditStorage)

def test_logger_initialization_with_file_storage(tmp_path):
    """Test that AuditLogger correctly initializes FileAuditStorage."""
    log_file = tmp_path / "audit.jsonl"
    config = AuditConfig(log_file_path=log_file)
    logger = AuditLogger(config=config)
    assert isinstance(logger.storage, FileAuditStorage)

def test_logger_initialization_with_explicit_storage():
    """Test that AuditLogger uses the storage instance provided."""
    mock_storage = MagicMock(spec=InMemoryAuditStorage)
    logger = AuditLogger(storage=mock_storage)
    assert logger.storage == mock_storage

def test_log_event(logger):
    """Test the basic log_event method."""
    event = AuditEvent(event_type=AuditEventType.SYSTEM_STARTUP, user_id="system")
    logger.log_event(event)

    events = logger.get_events()
    assert len(events) == 1
    assert events[0].user_id == "system"
    assert events[0].event_type == AuditEventType.SYSTEM_STARTUP

def test_log_event_disabled(test_config):
    """Test that no event is logged when the logger is disabled."""
    test_config.enabled = False
    logger = AuditLogger(config=test_config)
    event = AuditEvent(event_type=AuditEventType.SYSTEM_STARTUP)
    logger.log_event(event)

    assert len(logger.get_events()) == 0

def test_log_authentication_event(logger):
    """Test logging an authentication event."""
    logger.log_authentication_event(
        user_id="testuser",
        event_type=AuditEventType.LOGIN_SUCCESS,
        ip_address="127.0.0.1"
    )
    events = logger.get_events(user_id="testuser")
    assert len(events) == 1
    assert events[0].event_type == AuditEventType.LOGIN_SUCCESS
    assert events[0].ip_address == "127.0.0.1"

def test_log_authentication_event_disabled(test_config):
    """Test that auth events are not logged when disabled."""
    test_config.log_authentication = False
    logger = AuditLogger(config=test_config)
    logger.log_authentication_event("testuser", AuditEventType.LOGIN_SUCCESS)
    assert len(logger.get_events()) == 0

def test_log_data_access_event(logger):
    """Test logging a data access event."""
    logger.log_data_access_event(
        user_id="testuser",
        event_type=AuditEventType.DATA_READ,
        resource_type="document",
        resource_id="doc123"
    )
    events = logger.get_events()
    assert len(events) == 1
    assert events[0].resource_type == "document"
    assert events[0].resource_id == "doc123"

def test_log_security_event(logger):
    """Test logging a security event."""
    logger.log_security_event(
        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
        ip_address="1.2.3.4",
        metadata={"limit": 100, "path": "/api/v1/data"}
    )
    events = logger.get_events()
    assert len(events) == 1
    assert events[0].event_type == AuditEventType.RATE_LIMIT_EXCEEDED
    assert events[0].metadata["limit"] == 100

def test_log_admin_action(logger):
    """Test logging an administrative action."""
    logger.log_admin_action(
        user_id="admin",
        event_type=AuditEventType.CONFIG_CHANGE,
        action="Set rate limit to 200"
    )
    events = logger.get_events(user_id="admin")
    assert len(events) == 1
    assert events[0].event_type == AuditEventType.CONFIG_CHANGE
    assert events[0].action == "Set rate limit to 200"

def test_get_events_filtering(logger):
    """Test filtering of events in get_events."""
    logger.log_authentication_event("user1", AuditEventType.LOGIN_SUCCESS, success=True)
    logger.log_authentication_event("user1", AuditEventType.LOGIN_FAILURE, success=False)
    logger.log_data_access_event("user2", AuditEventType.DATA_READ, "doc", "1")
    logger.log_data_access_event("user1", AuditEventType.DATA_UPDATE, "doc", "2")

    # Filter by user_id
    assert len(logger.get_events(user_id="user1")) == 3
    assert len(logger.get_events(user_id="user2")) == 1

    # Filter by event_type
    assert len(logger.get_events(event_types=[AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE])) == 2

    # Filter by success status
    assert len(logger.get_events(success=True)) == 3
    assert len(logger.get_events(success=False)) == 1

    # Combined filters
    assert len(logger.get_events(user_id="user1", event_types=[AuditEventType.DATA_UPDATE])) == 1

@patch('time.time')
def test_cleanup_old_logs(mock_time, logger):
    """Test cleanup of old logs."""
    now = 1730000000.0
    one_day = 86400
    retention_days = logger.config.retention_days

    old_timestamp = now - (retention_days * one_day) - 1
    new_timestamp = now - (retention_days * one_day) + 1

    logger.log_event(AuditEvent(user_id="user_old", timestamp=old_timestamp))
    logger.log_event(AuditEvent(user_id="user_new", timestamp=new_timestamp))

    assert len(logger.get_events()) == 2

    mock_time.return_value = now
    removed_count = logger.cleanup_old_logs()

    assert removed_count == 1

    remaining_events = logger.get_events()
    assert len(remaining_events) == 1
    assert remaining_events[0].user_id == "user_new"

def test_get_statistics(logger):
    """Test retrieval of audit log statistics."""
    logger.log_authentication_event("user1", AuditEventType.LOGIN_SUCCESS, success=True)
    logger.log_authentication_event("user1", AuditEventType.LOGIN_FAILURE, success=False)
    stats = logger.get_statistics()

    assert stats["total_events"] == 2
    assert stats["success_count"] == 1
    assert stats["failure_count"] == 1
    assert stats["event_type_counts"][AuditEventType.LOGIN_SUCCESS.value] == 1

# endregion


# region: Tests for events.py

def test_audit_event_to_json():
    """Test the to_json method of AuditEvent."""
    event = AuditEvent(
        event_type=AuditEventType.DATA_CREATE,
        user_id="test_user",
        metadata={"key": "value"}
    )
    event_json = event.to_json()
    event_dict = json.loads(event_json)

    assert event_dict["event_type"] == "data.create"
    assert event_dict["user_id"] == "test_user"
    assert event_dict["metadata"]["key"] == "value"

# endregion


# region: Tests for storage.py

def test_file_storage_log_and_get(file_logger):
    """Test logging to and retrieving from FileAuditStorage."""
    file_logger.log_data_access_event(
        user_id="file_user",
        event_type=AuditEventType.DATA_DELETE,
        resource_type="file",
        resource_id="f1"
    )

    events = file_logger.get_events(user_id="file_user")
    assert len(events) == 1
    assert events[0].resource_type == "file"

def test_file_storage_cleanup(file_logger):
    """Test cleanup of old logs in FileAuditStorage."""
    now = time.time()
    one_day = 86400

    old_event = AuditEvent(user_id="old", timestamp=now - (2 * one_day))
    new_event = AuditEvent(user_id="new", timestamp=now)

    file_logger.log_event(old_event)
    file_logger.log_event(new_event)

    assert len(file_logger.get_events()) == 2

    removed_count = file_logger.cleanup_old_logs(retention_days=1)
    assert removed_count == 1

    remaining_events = file_logger.get_events()
    assert len(remaining_events) == 1
    assert remaining_events[0].user_id == "new"

@patch('os.path.getsize')
def test_file_storage_rotation(mock_getsize, file_logger, tmp_path):
    """Test log file rotation is triggered by size."""
    mock_getsize.return_value = (file_logger.config.max_file_size_mb * 1024 * 1024) + 1

    file_logger.log_event(AuditEvent(user_id="event_that_triggers_rotation"))

    backup_files = list(tmp_path.glob("audit.*.jsonl"))
    assert len(backup_files) == 1

@patch('time.time')
@patch('os.path.getsize')
def test_file_storage_backup_cleanup(mock_getsize, mock_time, file_logger, tmp_path):
    """Test cleanup of old backup files."""
    mock_getsize.return_value = (file_logger.config.max_file_size_mb * 1024 * 1024) + 1

    timestamps = [1700000000, 1700000001, 1700000002]
    for i, ts in enumerate(timestamps):
        mock_time.return_value = ts
        file_logger.log_event(AuditEvent(user_id=f"user_{i}"))

    backup_files = sorted(list(tmp_path.glob("audit.*.jsonl")))
    assert len(backup_files) == 2

    backup_names = [p.name for p in backup_files]
    assert "audit.1700000000.jsonl" not in backup_names
    assert "audit.1700000001.jsonl" in backup_names
    assert "audit.1700000002.jsonl" in backup_names

def test_file_storage_get_statistics(file_logger):
    """Test get_statistics for FileAuditStorage."""
    file_logger.log_authentication_event("user1", AuditEventType.LOGIN_SUCCESS, success=True)
    file_logger.log_authentication_event("user1", AuditEventType.LOGIN_FAILURE, success=False)

    stats = file_logger.get_statistics()

    assert stats["total_events"] == 2
    assert stats["success_count"] == 1
    assert stats["failure_count"] == 1
    assert stats["storage_type"] == "file"
    assert "file_size_bytes" in stats

# endregion
