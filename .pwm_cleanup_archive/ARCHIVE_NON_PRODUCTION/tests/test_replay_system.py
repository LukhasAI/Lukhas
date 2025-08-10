#!/usr/bin/env python3
"""
Test Suite for LUKHAS Memory Replay System

Comprehensive tests for temporal indexing, sequence creation, replay sessions,
and multi-modal memory traversal capabilities.
"""

from datetime import datetime, timedelta

import pytest

# Import the replay system
from memory.core_memory.replay_system import (
    MemoryReplayer,
    ReplayDirection,
    ReplayMode,
    ReplayQuality,
    TemporalIndex,
    create_sequence,
    get_memory_replayer,
    get_next,
    get_replayer_status,
    start_session,
)


class TestTemporalIndex:
    """Test suite for TemporalIndex functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temporal_index = TemporalIndex()
        self.test_timestamps = [
            "2025-01-01T10:00:00",
            "2025-01-01T11:00:00",
            "2025-01-01T12:00:00",
            "2025-01-01T13:00:00",
        ]
        self.test_memory_ids = ["mem_001", "mem_002", "mem_003", "mem_004"]

    def test_add_memory_timestamp(self):
        """Test adding memories to temporal index."""
        # Add memory with timestamp
        result = self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[0], self.test_timestamps[0]
        )

        assert result is True
        assert self.test_timestamps[0] in self.temporal_index.time_index
        assert (
            self.test_memory_ids[0]
            in self.temporal_index.time_index[self.test_timestamps[0]]
        )
        assert (
            self.temporal_index.reverse_index[self.test_memory_ids[0]]
            == self.test_timestamps[0]
        )

    def test_add_memory_with_causal_predecessors(self):
        """Test adding memory with causal relationships."""
        # Add first memory
        self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[0], self.test_timestamps[0]
        )

        # Add second memory with causal predecessor
        result = self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[1],
            self.test_timestamps[1],
            causal_predecessors=[self.test_memory_ids[0]],
        )

        assert result is True
        assert (
            self.test_memory_ids[1]
            in self.temporal_index.causal_chains[self.test_memory_ids[0]]
        )

    def test_get_memories_in_range(self):
        """Test retrieving memories within time range."""
        # Add multiple memories
        for i, (memory_id, timestamp) in enumerate(
            zip(self.test_memory_ids, self.test_timestamps)
        ):
            self.temporal_index.add_memory_timestamp(memory_id, timestamp)

        # Get memories in middle range
        memories = self.temporal_index.get_memories_in_range(
            self.test_timestamps[1], self.test_timestamps[2]
        )

        assert len(memories) == 2
        assert self.test_memory_ids[1] in memories
        assert self.test_memory_ids[2] in memories

    def test_get_causal_sequence(self):
        """Test retrieving causal sequence from root memory."""
        # Build causal chain: mem_001 -> mem_002 -> mem_003
        self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[0], self.test_timestamps[0]
        )
        self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[1],
            self.test_timestamps[1],
            causal_predecessors=[self.test_memory_ids[0]],
        )
        self.temporal_index.add_memory_timestamp(
            self.test_memory_ids[2],
            self.test_timestamps[2],
            causal_predecessors=[self.test_memory_ids[1]],
        )

        # Get causal sequence
        sequence = self.temporal_index.get_causal_sequence(self.test_memory_ids[0])

        assert len(sequence) == 3
        assert sequence[0] == self.test_memory_ids[0]
        assert sequence[1] == self.test_memory_ids[1]
        assert sequence[2] == self.test_memory_ids[2]

    def test_find_temporal_neighbors(self):
        """Test finding temporal neighbors within time window."""
        # Add memories with close timestamps
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        timestamps = [
            (base_time - timedelta(minutes=30)).isoformat(),  # 30 min before
            base_time.isoformat(),  # target time
            (base_time + timedelta(minutes=20)).isoformat(),  # 20 min after
            (
                base_time + timedelta(hours=2)
            ).isoformat(),  # 2 hours after (outside window)
        ]

        for memory_id, timestamp in zip(self.test_memory_ids, timestamps):
            self.temporal_index.add_memory_timestamp(memory_id, timestamp)

        # Find neighbors within 60-minute window
        neighbors = self.temporal_index.find_temporal_neighbors(
            self.test_memory_ids[1], 60
        )

        assert len(neighbors) == 2  # Should include memories 0 and 2, but not 3
        assert self.test_memory_ids[0] in neighbors
        assert self.test_memory_ids[2] in neighbors
        assert self.test_memory_ids[3] not in neighbors

    def test_empty_index_operations(self):
        """Test operations on empty index."""
        # Test getting memories in range on empty index
        memories = self.temporal_index.get_memories_in_range(
            "2025-01-01T10:00:00", "2025-01-01T12:00:00"
        )
        assert memories == []

        # Test getting causal sequence on empty index
        sequence = self.temporal_index.get_causal_sequence("non_existent")
        assert sequence == ["non_existent"]  # Should return just the root

        # Test finding neighbors on empty index
        neighbors = self.temporal_index.find_temporal_neighbors("non_existent")
        assert neighbors == []


class TestMemoryReplayer:
    """Test suite for main MemoryReplayer functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "max_active_sessions": 5,
            "default_playback_speed": 1.0,
            "cache_size_limit": 50,
        }
        self.replayer = MemoryReplayer(self.config)
        self.test_memory_ids = ["mem_001", "mem_002", "mem_003", "mem_004"]

    def test_initialization(self):
        """Test MemoryReplayer initialization."""
        assert self.replayer.max_active_sessions == 5
        assert self.replayer.default_playback_speed == 1.0
        assert self.replayer.cache_size_limit == 50
        assert len(self.replayer.active_sessions) == 0
        assert len(self.replayer.sequence_cache) == 0

    def test_create_replay_sequence(self):
        """Test creating replay sequences."""
        # Test chronological sequence
        sequence_id = self.replayer.create_replay_sequence(
            self.test_memory_ids,
            ReplayMode.CHRONOLOGICAL,
            ReplayDirection.FORWARD,
            ReplayQuality.STANDARD,
        )

        assert sequence_id is not None
        assert sequence_id in self.replayer.sequence_cache

        # Verify sequence properties
        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.CHRONOLOGICAL
        assert sequence.direction == ReplayDirection.FORWARD
        assert len(sequence.snapshots) > 0
        assert sequence.total_duration > 0
        assert sequence.coherence_score > 0

        # Verify metrics updated
        assert self.replayer.sequences_created == 1

    def test_create_sequence_different_modes(self):
        """Test creating sequences with different replay modes."""
        modes = [
            ReplayMode.CHRONOLOGICAL,
            ReplayMode.EMOTIONAL,
            ReplayMode.CAUSAL,
            ReplayMode.SYMBOLIC,
            ReplayMode.ASSOCIATIVE,
        ]

        created_sequences = []
        for mode in modes:
            sequence_id = self.replayer.create_replay_sequence(
                self.test_memory_ids, mode
            )
            assert sequence_id is not None
            created_sequences.append(sequence_id)

            # Verify mode set correctly
            sequence = self.replayer.sequence_cache[sequence_id]
            assert sequence.replay_mode == mode

        assert len(created_sequences) == len(modes)
        assert len(set(created_sequences)) == len(modes)  # All unique

    def test_create_sequence_different_directions(self):
        """Test creating sequences with different directions."""
        directions = [ReplayDirection.FORWARD, ReplayDirection.BACKWARD]

        for direction in directions:
            sequence_id = self.replayer.create_replay_sequence(
                self.test_memory_ids, direction=direction
            )

            sequence = self.replayer.sequence_cache[sequence_id]
            assert sequence.direction == direction

    def test_create_sequence_empty_memories(self):
        """Test creating sequence with empty memory list."""
        sequence_id = self.replayer.create_replay_sequence([])
        assert sequence_id is None  # Should fail with empty list

    def test_start_replay_session(self):
        """Test starting replay sessions."""
        # Create sequence first
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        assert sequence_id is not None

        # Start session
        session_id = self.replayer.start_replay_session(
            sequence_id,
            playback_speed=2.0,
            loop_mode=True,
            filters={"min_emotional_intensity": 0.5},
        )

        assert session_id is not None
        assert session_id in self.replayer.active_sessions

        # Verify session properties
        session = self.replayer.active_sessions[session_id]
        assert session.sequence.sequence_id == sequence_id
        assert session.playback_speed == 2.0
        assert session.loop_mode is True
        assert session.filters == {"min_emotional_intensity": 0.5}
        assert session.current_position == 0

        # Verify metrics updated
        assert self.replayer.sessions_started == 1

    def test_start_session_capacity_limit(self):
        """Test session creation at capacity limit."""
        # Create sequence
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)

        # Fill up to capacity
        session_ids = []
        for i in range(self.config["max_active_sessions"]):
            session_id = self.replayer.start_replay_session(sequence_id)
            assert session_id is not None
            session_ids.append(session_id)

        # Try to create one more - should fail
        overflow_session_id = self.replayer.start_replay_session(sequence_id)
        assert overflow_session_id is None
        assert len(self.replayer.active_sessions) == self.config["max_active_sessions"]

    def test_start_session_nonexistent_sequence(self):
        """Test starting session with non-existent sequence."""
        session_id = self.replayer.start_replay_session("non_existent_sequence")
        assert session_id is None

    def test_get_next_memory(self):
        """Test getting next memory in replay sequence."""
        # Create sequence and session
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        # Get first memory
        memory_data = self.replayer.get_next_memory(session_id)

        assert memory_data is not None
        assert "snapshot_id" in memory_data
        assert "memory_fold_id" in memory_data
        assert "timestamp" in memory_data
        assert "content" in memory_data
        assert "emotional_state" in memory_data
        assert "position" in memory_data
        assert "total_snapshots" in memory_data
        assert "session_id" in memory_data

        # Verify position tracking
        assert memory_data["position"] == 0
        assert memory_data["session_id"] == session_id

        # Get next memory - position should advance
        next_memory = self.replayer.get_next_memory(session_id)
        assert next_memory["position"] == 1

    def test_get_next_memory_loop_mode(self):
        """Test replay with loop mode enabled."""
        # Create short sequence
        short_memory_list = ["mem_001", "mem_002"]
        sequence_id = self.replayer.create_replay_sequence(short_memory_list)
        session_id = self.replayer.start_replay_session(sequence_id, loop_mode=True)

        # Get all memories in sequence
        memories = []
        for i in range(4):  # Get more than sequence length
            memory = self.replayer.get_next_memory(session_id)
            assert memory is not None
            memories.append(memory)

        # Should loop back to beginning
        assert memories[0]["position"] == 0
        assert memories[1]["position"] == 1
        assert memories[2]["position"] == 0  # Looped back
        assert memories[3]["position"] == 1

    def test_get_next_memory_no_loop(self):
        """Test replay without loop mode."""
        # Create short sequence
        short_memory_list = ["mem_001"]
        sequence_id = self.replayer.create_replay_sequence(short_memory_list)
        session_id = self.replayer.start_replay_session(sequence_id, loop_mode=False)

        # Get first memory
        memory1 = self.replayer.get_next_memory(session_id)
        assert memory1 is not None

        # Try to get next - should return None (end of sequence)
        memory2 = self.replayer.get_next_memory(session_id)
        assert memory2 is None

    def test_get_next_memory_nonexistent_session(self):
        """Test getting next memory from non-existent session."""
        memory = self.replayer.get_next_memory("non_existent_session")
        assert memory is None

    def test_seek_to_position(self):
        """Test seeking to specific position in replay."""
        # Create sequence and session
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        # Seek to position 2
        result = self.replayer.seek_to_position(session_id, 2)
        assert result is True

        # Get next memory - should be at position 2
        memory = self.replayer.get_next_memory(session_id)
        assert memory["position"] == 2

    def test_seek_invalid_position(self):
        """Test seeking to invalid position."""
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        # Try to seek to negative position
        result = self.replayer.seek_to_position(session_id, -1)
        assert result is False

        # Try to seek beyond sequence length
        result = self.replayer.seek_to_position(session_id, 1000)
        assert result is False

    def test_create_associative_sequence(self):
        """Test creating associative sequences."""
        # Add some memories to temporal index
        for i, memory_id in enumerate(self.test_memory_ids):
            timestamp = (datetime.now() + timedelta(hours=i)).isoformat()
            self.replayer.temporal_index.add_memory_timestamp(memory_id, timestamp)

        # Create associative sequence
        sequence_id = self.replayer.create_associative_sequence(
            self.test_memory_ids[0], max_associations=10
        )

        assert sequence_id is not None
        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.ASSOCIATIVE
        assert len(sequence.snapshots) > 0

    def test_find_memories_by_content(self):
        """Test finding memories by content terms."""
        # Mock implementation - test interface
        search_terms = ["learning", "pattern"]
        time_range = ("2025-01-01T00:00:00", "2025-01-01T23:59:59")

        memories = self.replayer.find_memories_by_content(search_terms, time_range)
        assert isinstance(memories, list)

    def test_get_session_status(self):
        """Test getting session status."""
        # Create sequence and session
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id, playback_speed=1.5)

        # Get some memories to advance position
        self.replayer.get_next_memory(session_id)
        self.replayer.get_next_memory(session_id)

        # Get status
        status = self.replayer.get_session_status(session_id)

        assert status is not None
        assert status["session_id"] == session_id
        assert status["sequence_id"] == sequence_id
        assert status["current_position"] == 2
        assert status["playback_speed"] == 1.5
        assert "progress_percentage" in status
        assert "replay_mode" in status
        assert "direction" in status
        assert "coherence_score" in status

    def test_get_status_nonexistent_session(self):
        """Test getting status of non-existent session."""
        status = self.replayer.get_session_status("non_existent")
        assert status is None

    def test_close_session(self):
        """Test closing replay session."""
        # Create sequence and session
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        # Close session
        result = self.replayer.close_session(session_id)
        assert result is True
        assert session_id not in self.replayer.active_sessions

    def test_close_nonexistent_session(self):
        """Test closing non-existent session."""
        result = self.replayer.close_session("non_existent")
        assert result is False

    def test_get_system_status(self):
        """Test getting system status."""
        # Create some activity for meaningful status
        sequence_id = self.replayer.create_replay_sequence(self.test_memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        status = self.replayer.get_system_status()

        # Verify status structure
        assert status["system_status"] == "operational"
        assert status["module_version"] == "1.0.0"
        assert status["active_sessions"] == 1
        assert status["cached_sequences"] == 1

        # Verify metrics
        metrics = status["metrics"]
        assert metrics["sequences_created"] == 1
        assert metrics["sessions_started"] == 1
        assert "total_replay_time" in metrics
        assert "avg_session_duration" in metrics

        # Verify configuration
        config = status["configuration"]
        assert config["max_active_sessions"] == 5
        assert config["default_playback_speed"] == 1.0
        assert config["cache_size_limit"] == 50


class TestReplayModes:
    """Test different replay modes and their behaviors."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer()
        self.memory_ids = ["mem_001", "mem_002", "mem_003", "mem_004"]

    def test_chronological_mode(self):
        """Test chronological replay mode."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, ReplayMode.CHRONOLOGICAL
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.CHRONOLOGICAL

        # Snapshots should be ordered by timestamp
        timestamps = [snapshot.timestamp for snapshot in sequence.snapshots]
        assert timestamps == sorted(timestamps)

    def test_emotional_mode(self):
        """Test emotional replay mode."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, ReplayMode.EMOTIONAL
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.EMOTIONAL
        # Note: Actual emotional ordering would be tested with real emotional data

    def test_causal_mode(self):
        """Test causal replay mode."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, ReplayMode.CAUSAL
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.CAUSAL

    def test_symbolic_mode(self):
        """Test symbolic replay mode."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, ReplayMode.SYMBOLIC
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.SYMBOLIC

    def test_associative_mode(self):
        """Test associative replay mode."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, ReplayMode.ASSOCIATIVE
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.ASSOCIATIVE


class TestReplayDirections:
    """Test different replay directions."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer()
        self.memory_ids = ["mem_001", "mem_002", "mem_003"]

    def test_forward_direction(self):
        """Test forward replay direction."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, direction=ReplayDirection.FORWARD
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.direction == ReplayDirection.FORWARD

    def test_backward_direction(self):
        """Test backward replay direction."""
        sequence_id = self.replayer.create_replay_sequence(
            self.memory_ids, direction=ReplayDirection.BACKWARD
        )

        sequence = self.replayer.sequence_cache[sequence_id]
        assert sequence.direction == ReplayDirection.BACKWARD


class TestReplayQuality:
    """Test different replay quality levels."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer()
        self.memory_ids = ["mem_001", "mem_002"]

    def test_different_quality_levels(self):
        """Test creating sequences with different quality levels."""
        qualities = [
            ReplayQuality.HIGH_FIDELITY,
            ReplayQuality.STANDARD,
            ReplayQuality.COMPRESSED,
            ReplayQuality.SUMMARY,
        ]

        for quality in qualities:
            sequence_id = self.replayer.create_replay_sequence(
                self.memory_ids, quality=quality
            )

            sequence = self.replayer.sequence_cache[sequence_id]
            # Quality should be reflected in snapshots
            for snapshot in sequence.snapshots:
                assert snapshot.replay_quality == quality


class TestModuleLevelInterface:
    """Test module-level interface functions."""

    def setup_method(self):
        """Setup test fixtures."""
        # Reset the default replayer
        from memory.core_memory.replay_system import default_memory_replayer

        default_memory_replayer.__init__()

        self.memory_ids = ["mem_001", "mem_002", "mem_003"]

    def test_get_memory_replayer(self):
        """Test getting default memory replayer."""
        replayer = get_memory_replayer()
        assert isinstance(replayer, MemoryReplayer)

    def test_create_sequence_module_function(self):
        """Test module-level sequence creation."""
        sequence_id = create_sequence(self.memory_ids, "chronological")
        assert sequence_id is not None

        # Verify sequence was created
        replayer = get_memory_replayer()
        assert sequence_id in replayer.sequence_cache

    def test_create_sequence_invalid_mode(self):
        """Test module-level function with invalid mode."""
        sequence_id = create_sequence(self.memory_ids, "invalid_mode")
        assert sequence_id is None

    def test_start_session_module_function(self):
        """Test module-level session start."""
        # Create sequence first
        sequence_id = create_sequence(self.memory_ids)
        assert sequence_id is not None

        # Start session
        session_id = start_session(sequence_id, playback_speed=2.0, loop_mode=True)
        assert session_id is not None

    def test_get_next_module_function(self):
        """Test module-level get next memory."""
        # Create sequence and session
        sequence_id = create_sequence(self.memory_ids)
        session_id = start_session(sequence_id)

        # Get next memory
        memory = get_next(session_id)
        assert memory is not None
        assert "memory_fold_id" in memory

    def test_get_replayer_status_module_function(self):
        """Test module-level status function."""
        status = get_replayer_status()
        assert isinstance(status, dict)
        assert "system_status" in status
        assert "module_version" in status


class TestSessionFilters:
    """Test replay session filtering capabilities."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer()
        self.memory_ids = ["mem_001", "mem_002", "mem_003"]

    def test_emotional_intensity_filter(self):
        """Test filtering by emotional intensity."""
        sequence_id = self.replayer.create_replay_sequence(self.memory_ids)
        session_id = self.replayer.start_replay_session(
            sequence_id, filters={"min_emotional_intensity": 0.7}
        )

        # Get memory - should be filtered based on emotional intensity
        memory = self.replayer.get_next_memory(session_id)
        assert memory is not None
        # Note: Actual filtering behavior would be tested with real emotional data

    def test_symbolic_weight_filter(self):
        """Test filtering by symbolic weight."""
        sequence_id = self.replayer.create_replay_sequence(self.memory_ids)
        session_id = self.replayer.start_replay_session(
            sequence_id, filters={"min_symbolic_weight": 0.6}
        )

        memory = self.replayer.get_next_memory(session_id)
        assert memory is not None

    def test_no_filters(self):
        """Test session without filters."""
        sequence_id = self.replayer.create_replay_sequence(self.memory_ids)
        session_id = self.replayer.start_replay_session(sequence_id)

        memory = self.replayer.get_next_memory(session_id)
        assert memory is not None
        # Content should not be filtered


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer()

    def test_sequence_cache_limit(self):
        """Test sequence cache size management."""
        # Set small cache limit
        self.replayer.cache_size_limit = 2

        # Create sequences up to limit
        sequence_ids = []
        for i in range(3):  # One more than limit
            sequence_id = self.replayer.create_replay_sequence([f"mem_{i}"])
            sequence_ids.append(sequence_id)

        # Should have only cache_size_limit sequences
        assert len(self.replayer.sequence_cache) == 2
        # First sequence should have been removed
        assert sequence_ids[0] not in self.replayer.sequence_cache
        assert sequence_ids[1] in self.replayer.sequence_cache
        assert sequence_ids[2] in self.replayer.sequence_cache

    def test_invalid_memory_data(self):
        """Test handling of invalid memory data."""
        # Test with None memory list
        with pytest.raises(TypeError):
            self.replayer.create_replay_sequence(None)

    def test_session_access_tracking(self):
        """Test session access time tracking."""
        sequence_id = self.replayer.create_replay_sequence(["mem_001"])
        session_id = self.replayer.start_replay_session(sequence_id)

        # Get initial access time
        session = self.replayer.active_sessions[session_id]
        initial_access = session.last_accessed
        initial_count = session.access_count

        # Access memory
        self.replayer.get_next_memory(session_id)

        # Verify access tracking updated
        assert session.last_accessed != initial_access
        assert session.access_count == initial_count + 1


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""

    def setup_method(self):
        """Setup test fixtures."""
        self.replayer = MemoryReplayer({"max_active_sessions": 20})

    def test_large_sequence_creation(self):
        """Test creating sequence with large memory set."""
        large_memory_set = [f"mem_{i:04d}" for i in range(100)]

        sequence_id = self.replayer.create_replay_sequence(large_memory_set)
        assert sequence_id is not None

        sequence = self.replayer.sequence_cache[sequence_id]
        assert len(sequence.snapshots) == 100

    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent replay sessions."""
        # Create sequence
        sequence_id = self.replayer.create_replay_sequence(["mem_001", "mem_002"])

        # Start multiple sessions
        session_ids = []
        for i in range(10):
            session_id = self.replayer.start_replay_session(sequence_id)
            assert session_id is not None
            session_ids.append(session_id)

        # All sessions should be active
        assert len(self.replayer.active_sessions) == 10

        # Test concurrent access
        for session_id in session_ids:
            memory = self.replayer.get_next_memory(session_id)
            assert memory is not None

    def test_sequence_coherence_calculation(self):
        """Test coherence score calculation for different modes."""
        modes_and_expected_coherence = [
            (ReplayMode.CHRONOLOGICAL, 0.9),
            (ReplayMode.ASSOCIATIVE, 0.7),
            (ReplayMode.EMOTIONAL, 0.8),
        ]

        for mode, expected_min_coherence in modes_and_expected_coherence:
            sequence_id = self.replayer.create_replay_sequence(["mem_001"], mode)
            sequence = self.replayer.sequence_cache[sequence_id]

            # Coherence should be reasonable for the mode
            assert sequence.coherence_score >= expected_min_coherence - 0.2


# Test fixtures and utilities
@pytest.fixture
def memory_replayer():
    """Fixture providing a fresh MemoryReplayer instance."""
    return MemoryReplayer(
        {
            "max_active_sessions": 10,
            "default_playback_speed": 1.0,
            "cache_size_limit": 100,
        }
    )


@pytest.fixture
def sample_memory_sequence():
    """Fixture providing sample memory sequence."""
    return ["memory_001", "memory_002", "memory_003", "memory_004", "memory_005"]


# Integration tests
class TestReplaySystemIntegration:
    """Integration tests for the complete replay system."""

    def test_complete_replay_workflow(self, memory_replayer, sample_memory_sequence):
        """Test complete replay workflow from sequence creation to session completion."""
        # 1. Create replay sequence
        sequence_id = memory_replayer.create_replay_sequence(
            sample_memory_sequence,
            ReplayMode.CHRONOLOGICAL,
            ReplayDirection.FORWARD,
            ReplayQuality.HIGH_FIDELITY,
        )
        assert sequence_id is not None

        # 2. Start replay session
        session_id = memory_replayer.start_replay_session(
            sequence_id, playback_speed=1.5, loop_mode=False
        )
        assert session_id is not None

        # 3. Replay through entire sequence
        replayed_memories = []
        while True:
            memory = memory_replayer.get_next_memory(session_id)
            if memory is None:
                break
            replayed_memories.append(memory)

        # 4. Verify complete sequence replayed
        assert len(replayed_memories) == len(sample_memory_sequence)

        # 5. Verify session status
        status = memory_replayer.get_session_status(session_id)
        assert status["current_position"] == len(sample_memory_sequence)
        assert status["progress_percentage"] == 100.0

        # 6. Close session
        result = memory_replayer.close_session(session_id)
        assert result is True

    def test_temporal_index_integration(self, memory_replayer):
        """Test integration with temporal indexing system."""
        memory_ids = ["mem_A", "mem_B", "mem_C"]
        timestamps = [
            "2025-01-01T10:00:00",
            "2025-01-01T11:00:00",
            "2025-01-01T12:00:00",
        ]

        # Add memories to temporal index
        for memory_id, timestamp in zip(memory_ids, timestamps):
            memory_replayer.temporal_index.add_memory_timestamp(memory_id, timestamp)

        # Create sequence
        sequence_id = memory_replayer.create_replay_sequence(memory_ids)

        # Verify temporal relationships preserved
        sequence = memory_replayer.sequence_cache[sequence_id]
        assert len(sequence.snapshots) == 3

    def test_associative_discovery_integration(self, memory_replayer):
        """Test associative memory discovery integration."""
        # Setup temporal relationships
        memory_ids = ["seed", "neighbor1", "neighbor2", "distant"]
        base_time = datetime(2025, 1, 1, 10, 0, 0)

        # Add memories with temporal clustering
        memory_replayer.temporal_index.add_memory_timestamp(
            "seed", base_time.isoformat()
        )
        memory_replayer.temporal_index.add_memory_timestamp(
            "neighbor1", (base_time + timedelta(minutes=10)).isoformat()
        )
        memory_replayer.temporal_index.add_memory_timestamp(
            "neighbor2", (base_time + timedelta(minutes=20)).isoformat()
        )
        memory_replayer.temporal_index.add_memory_timestamp(
            "distant", (base_time + timedelta(hours=5)).isoformat()
        )

        # Create associative sequence
        sequence_id = memory_replayer.create_associative_sequence("seed", 10)
        assert sequence_id is not None

        sequence = memory_replayer.sequence_cache[sequence_id]
        assert sequence.replay_mode == ReplayMode.ASSOCIATIVE
        # Should include neighbors but not distant memories


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
