"""Comprehensive tests for Drift Detector Archival functionality."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from core.consciousness.drift_detector import (
    ConsciousnessDriftDetector,
    FileDriftArchive,
    SQLiteDriftArchive,
    get_drift_archive_backend,
)


class TestFileDriftArchive:
    """Test suite for file-based drift archive."""

    @pytest.fixture
    def archive_dir(self, tmp_path):
        """Temporary archive directory."""
        return tmp_path / "drift_archives"

    @pytest.fixture
    def file_archive(self, archive_dir):
        """File-based archive."""
        return FileDriftArchive(archive_dir)

    def test_archive_creates_directory(self, archive_dir):
        """Archive should create directory if it doesn't exist."""
        FileDriftArchive(archive_dir)
        assert archive_dir.exists()

    def test_archive_snapshot(self, file_archive):
        """Test archiving a drift snapshot."""
        snapshot = {
            "layers": {"layer1": {"driftScore": 0.75, "affect_delta": 0.2}},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        archive_id = file_archive.archive_snapshot(snapshot)

        assert archive_id.startswith("drift_")
        # Verify file was created
        archive_files = list(file_archive.archive_dir.glob("drift_archive_*.jsonl"))
        assert len(archive_files) > 0

    def test_query_archives(self, file_archive):
        """Test querying archived snapshots."""
        # Archive multiple snapshots
        now = datetime.now(timezone.utc)

        for i in range(3):
            snapshot = {
                "layers": {"layer1": {"driftScore": 0.5 + i * 0.1}},
                "timestamp": (now - timedelta(hours=i)).isoformat(),
            }
            file_archive.archive_snapshot(snapshot)

        # Query all
        results = file_archive.query_archives()
        assert len(results) == 3

        # Query with min_drift filter
        results = file_archive.query_archives(min_drift=0.6)
        assert len(results) == 2  # Only snapshots with drift >= 0.6

    def test_query_with_time_range(self, file_archive):
        """Test querying with time range filters."""
        now = datetime.now(timezone.utc)

        for i in range(5):
            snapshot = {
                "layers": {"layer1": {"driftScore": 0.5}},
                "timestamp": (now - timedelta(hours=i)).isoformat(),
            }
            file_archive.archive_snapshot(snapshot)

        # Query recent only
        start_time = now - timedelta(hours=2)
        results = file_archive.query_archives(start_time=start_time)
        assert len(results) >= 2

    def test_query_by_layer(self, file_archive):
        """Test querying by specific layer."""
        snapshot1 = {
            "layers": {"layer1": {"driftScore": 0.5}, "layer2": {"driftScore": 0.6}},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        snapshot2 = {
            "layers": {"layer3": {"driftScore": 0.7}},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        file_archive.archive_snapshot(snapshot1)
        file_archive.archive_snapshot(snapshot2)

        # Query for layer1
        results = file_archive.query_archives(layer="layer1")
        assert len(results) == 1

        # Query for layer3
        results = file_archive.query_archives(layer="layer3")
        assert len(results) == 1


class TestSQLiteDriftArchive:
    """Test suite for SQLite-based drift archive."""

    @pytest.fixture
    def db_path(self, tmp_path):
        """Temporary database path."""
        return tmp_path / "drift_archives.db"

    @pytest.fixture
    def sqlite_archive(self, db_path):
        """SQLite archive."""
        return SQLiteDriftArchive(db_path)

    def test_database_initialization(self, sqlite_archive, db_path):
        """Test database schema creation."""
        assert db_path.exists()

        import sqlite3

        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='drift_archives'"
            )
            tables = cursor.fetchall()
            assert len(tables) == 1

    def test_archive_snapshot_with_indexing(self, sqlite_archive):
        """Test archiving with metadata indexing."""
        snapshot = {
            "layers": {
                "layer1": {"driftScore": 0.75},
                "layer2": {"driftScore": 0.60},
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        archive_id = sqlite_archive.archive_snapshot(snapshot)

        assert archive_id.startswith("drift_")

        # Verify indexed metadata
        import sqlite3

        with sqlite3.connect(sqlite_archive.db_path) as conn:
            cursor = conn.execute(
                "SELECT max_drift_score, layer_count FROM drift_archives WHERE archive_id = ?",
                (archive_id,),
            )
            row = cursor.fetchone()
            assert row[0] == 0.75  # max drift score
            assert row[1] == 2  # layer count

    def test_indexed_query_performance(self, sqlite_archive):
        """Test that queries use indexes."""
        # Archive many snapshots
        for i in range(100):
            snapshot = {
                "layers": {"layer1": {"driftScore": i / 100}},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            sqlite_archive.archive_snapshot(snapshot)

        # Query with indexed filter (should be fast)
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        results = sqlite_archive.query_archives(start_time=start_time, min_drift=0.5)

        # Should find ~50 results with drift >= 0.5
        assert len(results) >= 45

    def test_query_ordering(self, sqlite_archive):
        """Test that query results are ordered by time descending."""
        # Archive snapshots with different timestamps
        for i in range(5):
            snapshot = {
                "layers": {"layer1": {"driftScore": 0.5}},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            sqlite_archive.archive_snapshot(snapshot)

        results = sqlite_archive.query_archives()

        # Results should be in descending order (most recent first)
        assert len(results) == 5
        for i in range(len(results) - 1):
            assert results[i]["archived_at"] >= results[i + 1]["archived_at"]


class TestDriftDetectorWithArchival:
    """Test suite for ConsciousnessDriftDetector with archival support."""

    @pytest.fixture
    def archive_backend(self, tmp_path):
        """File-based archive backend."""
        return FileDriftArchive(tmp_path / "archives")

    def test_reset_archives_history(self, archive_backend):
        """Test that reset() archives history before clearing."""
        detector = ConsciousnessDriftDetector(
            archive_backend=archive_backend, archive_on_reset=True
        )

        # Simulate some drift history
        detector.record_snapshot("layer1", 0.75, 0.2)
        detector.record_snapshot("layer2", 0.65, 0.1)

        # Reset should return archive ID
        archive_id = detector.reset()

        assert archive_id is not None
        assert archive_id.startswith("drift_")

    def test_archival_can_be_disabled(self, archive_backend):
        """Test that archival can be disabled."""
        detector = ConsciousnessDriftDetector(
            archive_backend=archive_backend, archive_on_reset=False
        )

        # Add some history
        detector.record_snapshot("layer1", 0.75, 0.2)

        archive_id = detector.reset()

        # Should not archive
        assert archive_id is None

    def test_query_archived_snapshots(self, archive_backend):
        """Test querying archived snapshots from detector."""
        detector = ConsciousnessDriftDetector(
            archive_backend=archive_backend, archive_on_reset=True
        )

        # Archive some snapshots
        for i in range(3):
            detector.record_snapshot("layer1", 0.5 + i * 0.1, 0.0)
            detector.reset()

        # Query archives
        results = detector.query_archived_snapshots()

        assert len(results) >= 3

    def test_archive_failure_does_not_prevent_reset(self, tmp_path):
        """Test that archive failure doesn't block reset."""
        # Create archive with invalid path (will fail)
        bad_archive = FileDriftArchive(Path("/invalid/path/archives"))

        detector = ConsciousnessDriftDetector(
            archive_backend=bad_archive, archive_on_reset=True
        )

        # Add some history
        detector.record_snapshot("layer1", 0.75, 0.2)

        # Reset should complete even if archive fails
        archive_id = detector.reset()

        # Archive should fail, but reset should succeed
        assert archive_id is None  # Archive failed

    def test_default_archive_creation(self):
        """Test that default archive is created when none provided."""
        detector = ConsciousnessDriftDetector(archive_on_reset=True)

        # Should have created default file archive
        assert detector._archive_backend is not None

    def test_no_archive_backend_warning(self):
        """Test warning when querying without archive backend."""
        detector = ConsciousnessDriftDetector(archive_backend=None, archive_on_reset=False)

        results = detector.query_archived_snapshots()

        # Should return empty list
        assert results == []

    def test_archive_includes_all_layers(self, archive_backend):
        """Test that archive includes all layers."""
        detector = ConsciousnessDriftDetector(
            archive_backend=archive_backend, archive_on_reset=True
        )

        # Record multiple layers
        detector.record_snapshot("layer1", 0.75, 0.2)
        detector.record_snapshot("layer2", 0.65, 0.1)
        detector.record_snapshot("layer3", 0.55, 0.0)

        # Reset and archive
        detector.reset()

        # Query back
        results = detector.query_archived_snapshots()
        assert len(results) >= 1

        # Verify all layers are in the snapshot
        snapshot = results[0]["snapshot"]
        assert "layers" in snapshot
        assert len(snapshot["layers"]) == 3


class TestArchiveBackendFactory:
    """Test suite for archive backend factory function."""

    def test_create_file_backend(self, tmp_path):
        """Test creating file archive backend."""
        backend = get_drift_archive_backend(backend_type="file", archive_dir=tmp_path / "archives")

        assert isinstance(backend, FileDriftArchive)

    def test_create_sqlite_backend(self, tmp_path):
        """Test creating SQLite archive backend."""
        backend = get_drift_archive_backend(backend_type="sqlite", db_path=tmp_path / "test.db")

        assert isinstance(backend, SQLiteDriftArchive)

    def test_invalid_backend_type_raises_error(self):
        """Test that invalid backend type raises error."""
        with pytest.raises(ValueError, match="Unknown backend type"):
            get_drift_archive_backend(backend_type="invalid")

    def test_default_file_backend_path(self):
        """Test default path for file backend."""
        backend = get_drift_archive_backend(backend_type="file")

        assert isinstance(backend, FileDriftArchive)
        assert "drift_archives" in str(backend.archive_dir)

    def test_default_sqlite_backend_path(self):
        """Test default path for SQLite backend."""
        backend = get_drift_archive_backend(backend_type="sqlite")

        assert isinstance(backend, SQLiteDriftArchive)
        assert "drift_archives.db" in str(backend.db_path)
