# owner: Jules-03
# tier: tier1
# module_uid: candidate.memory.folds.fold_engine
# criticality: P0

from datetime import datetime, timedelta, timezone

import pytest

from memory.fakes.agimemory_fake import AGIMemoryFake
from memory.folds.fold_engine import MemoryFold, MemoryPriority, MemoryType


@pytest.mark.tier1
@pytest.mark.memory
class TestMemoryFold:
    """Test suite for the MemoryFold class."""

    def test_creation_defaults(self):
        """Test basic creation of a MemoryFold with default values."""
        fold = MemoryFold(key="test_key", content="test_content")
        assert fold.key == "test_key"
        assert fold.content == "test_content"
        assert fold.memory_type == MemoryType.SEMANTIC
        assert fold.priority == MemoryPriority.MEDIUM
        assert fold.owner_id is None
        assert fold.access_count == 0
        assert len(fold.associated_keys) == 0
        assert len(fold.tags) == 0
        assert isinstance(fold.created_at_utc, datetime)
        assert fold.last_accessed_utc == fold.created_at_utc

    def test_creation_with_specific_values(self):
        """Test creation with specific values for all parameters."""
        timestamp = datetime.now(timezone.utc) - timedelta(days=1)
        fold = MemoryFold(
            key="key123",
            content={"data": [1, 2, 3]},
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.HIGH,
            owner_id="user-abc",
            timestamp_utc=timestamp,
        )
        assert fold.key == "key123"
        assert fold.content == {"data": [1, 2, 3]}
        assert fold.memory_type == MemoryType.EPISODIC
        assert fold.priority == MemoryPriority.HIGH
        assert fold.owner_id == "user-abc"
        assert fold.created_at_utc == timestamp

    def test_initial_importance_calculation(self):
        """Test the initial importance score calculation for different priorities and types."""
        # High priority episodic memory
        fold_high = MemoryFold(key="high", content="", priority=MemoryPriority.HIGH, memory_type=MemoryType.EPISODIC)
        assert 0.79 <= fold_high.importance_score <= 0.81 # around 0.80

        # Critical identity memory
        fold_critical = MemoryFold(key="critical", content="", priority=MemoryPriority.CRITICAL, memory_type=MemoryType.IDENTITY)
        assert fold_critical.importance_score > 0.95 # should be very high

        # Low priority context memory
        fold_low = MemoryFold(key="low", content="", priority=MemoryPriority.LOW, memory_type=MemoryType.CONTEXT)
        assert 0.24 <= fold_low.importance_score <= 0.26 # around 0.30 - 0.05 = 0.25

    def test_update(self):
        """Test the update method."""
        fold = MemoryFold(key="upd-key", content="initial")
        initial_importance = fold.importance_score
        initial_access_count = fold.access_count

        fold.update("new content", new_priority=MemoryPriority.HIGH)

        assert fold.content == "new content"
        assert fold.priority == MemoryPriority.HIGH
        assert fold.access_count == initial_access_count + 1
        assert fold.importance_score != initial_importance
        assert fold.last_accessed_utc > fold.created_at_utc

    def test_retrieve(self):
        """Test the retrieve method."""
        fold = MemoryFold(key="ret-key", content="ret_content")
        retrieved_content = fold.retrieve()

        assert retrieved_content is not None
        assert fold.access_count == 1
        assert fold.last_accessed_utc > fold.created_at_utc

    def test_add_association(self):
        """Test adding associations to other folds."""
        fold = MemoryFold(key="assoc-key", content="")
        assert fold.add_association("related_key_1")
        assert "related_key_1" in fold.associated_keys
        # Test adding same key again
        assert fold.add_association("related_key_1")
        assert len(fold.associated_keys) == 1
        # Test self-association
        assert not fold.add_association("assoc-key")
        assert "assoc-key" not in fold.associated_keys

    def test_add_tag(self):
        """Test adding tags."""
        fold = MemoryFold(key="tag-key", content="")
        assert fold.add_tag("  Important  ")
        assert "important" in fold.tags
        # Test adding same tag again
        assert fold.add_tag("important")
        assert len(fold.tags) == 1
        # Test adding empty tag
        assert not fold.add_tag("   ")

    def test_to_dict(self):
        """Test the to_dict method for serialization."""
        fold = MemoryFold(key="dict-key", content="some content")
        fold.add_tag("test")
        fold.add_association("another_key")
        fold_dict = fold.to_dict()

        assert fold_dict["key"] == "dict-key"
        assert fold_dict["memory_type"] == "semantic"
        assert "content_preview" in fold_dict
        assert "test" in fold_dict["tags"]
        assert "another_key" in fold_dict["associated_keys"]

    def test_current_importance_calculation(self):
        """Test the dynamic recalculation of the importance score."""
        fold = MemoryFold(key="dyn-key", content="dynamic content", priority=MemoryPriority.MEDIUM)
        initial_score = fold.importance_score

        # Simulate access to increase importance
        fold.retrieve()
        fold.retrieve()
        score_after_2_accesses = fold._calculate_current_importance()
        assert score_after_2_accesses > initial_score

        # Simulate time decay
        fold.last_accessed_utc = datetime.now(timezone.utc) - timedelta(days=8)
        score_after_decay = fold._calculate_current_importance()
        assert score_after_decay < score_after_2_accesses

        # Simulate adding associations
        fold.add_association("rel1")
        fold.add_association("rel2")
        score_with_associations = fold._calculate_current_importance()
        assert score_with_associations > score_after_decay

    def test_tier_access(self):
        """Test the tier access control."""
        identity_fold = MemoryFold(key="id-fold", content="secret", memory_type=MemoryType.IDENTITY)
        assert identity_fold.retrieve(tier_level=4) is None
        assert identity_fold.retrieve(tier_level=5) is not None

    def test_drift_metrics(self):
        """Test the drift metrics update."""
        fold = MemoryFold(key="drift-key", content="stable")
        fold.update("changed")
        fold.update("changed again")
        assert fold.driftScore > 0

    def test_auto_reflect(self):
        """Test the auto_reflect method."""
        fold = MemoryFold(key="reflect-key", content="reflect")
        assert fold.auto_reflect() is None
        fold.driftScore = 0.5
        assert fold.auto_reflect() is not None

    def test_tier_filtered_content(self):
        """Test the _get_tier_filtered_content method."""
        emotional_fold = MemoryFold(key="emo-key", content="emotional content", memory_type=MemoryType.EMOTIONAL)
        assert emotional_fold._get_tier_filtered_content(tier_level=3) is not None

        collapsed_fold = MemoryFold(key="col-key", content="collapsed content")
        collapsed_fold.collapseHash = "somehash"
        filtered_content = collapsed_fold._get_tier_filtered_content(tier_level=1)
        assert "COLLAPSED" in filtered_content["summary"]

    def test_dream_drift_factor(self):
        """Test the _calculate_dream_drift_factor method."""
        fold = MemoryFold(key="dream-key", content="dreamy")

        # Test novelty boost
        feedback = {"novelty_score": 0.8}
        factor = fold._calculate_dream_drift_factor(feedback)
        assert factor > 0

        # Test repetition decay
        feedback = {"repetition_score": 0.9}
        factor = fold._calculate_dream_drift_factor(feedback)
        assert factor < 0

        # Test contradiction lock
        feedback = {"contradiction_detected": True}
        factor = fold._calculate_dream_drift_factor(feedback)
        assert factor == 0


@pytest.mark.tier1
@pytest.mark.memory
class TestAGIMemoryFake:
    """Test suite for the AGIMemoryFake class."""

    @pytest.fixture
    def agi_fake(self):
        """Fixture for a clean AGIMemoryFake instance."""
        return AGIMemoryFake()

    def test_put_and_get(self, agi_fake):
        """Test putting and getting a value."""
        agi_fake.put("key1", "value1")
        assert agi_fake.get("key1") == "value1"
        assert agi_fake.get("non-existent") is None

    def test_fold_operations(self, agi_fake):
        """Test the fold operations."""
        fid = agi_fake.fold_open()
        assert isinstance(fid, str)

        agi_fake.fold_append(fid, {"a": 1})
        agi_fake.fold_append(fid, {"b": 2})

        assert len(agi_fake.folds[fid]) == 2

        res = agi_fake.fold_close(fid)
        assert res["count"] == 2
        assert isinstance(res["lineage"], int)
