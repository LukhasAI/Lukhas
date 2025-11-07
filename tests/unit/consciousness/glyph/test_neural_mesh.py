
import sys
import pytest
from unittest.mock import MagicMock, patch, call
import numpy as np
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Mock the modules that are not available in the test environment
# This is necessary to be able to import the module under test
mock_glyph = MagicMock()
mock_glyph.EmotionVector = MagicMock()
mock_glyph.Glyph = MagicMock()
mock_glyph.GlyphFactory = MagicMock()
mock_glyph.GlyphType = MagicMock()
sys.modules['core.common.glyph'] = mock_glyph

mock_glyphs = MagicMock()
mock_glyphs.GLYPH_MAP = {
    "☯": "balance",
    "🪞": "reflection",
    "🌪️": "chaos",
    "🔁": "iteration",
    "💡": "insight",
    "🔗": "connection",
    "🛡️": "protection",
    "🌱": "growth",
    "❓": "uncertainty",
    "👁️": "awareness",
}
mock_glyphs.get_glyph_meaning = lambda x: mock_glyphs.GLYPH_MAP.get(x, "unknown")
sys.modules['core.glyph.glyphs'] = mock_glyphs

mock_memory_fold = MagicMock()
mock_memory_fold.MemoryFoldConfig = MagicMock()
mock_memory_fold.MemoryFoldSystem = MagicMock()
sys.modules['memory.folds.memory_fold'] = mock_memory_fold

# Now, we can import the module under test
from core.glyph.glyph_memory_integration import (
    GlyphBinding,
    FoldLineage,
    CompressionType,
    GlyphMemoryIndex,
    EmotionalFoldingEngine,
    GlyphAffectCoupler,
    DreamMemoryBridge,
    GlyphMemorySystem,
    get_glyph_memory_system,
    create_glyph_memory,
    recall_by_glyphs,
    fold_recent_memories,
)

# Test Data
TEST_AFFECT_VECTOR_1 = np.array([0.1, 0.2, 0.3])
TEST_AFFECT_VECTOR_2 = np.array([0.4, 0.5, 0.6])
TEST_MEMORY_FOLD_1 = {
    "hash": "fold1",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "emotion": "joy",
    "emotion_vector": np.array([0.8, 0.6, 0.4]),
    "relevance_score": 0.8,
    "context": "A happy memory",
    "user_id": "user1",
}
TEST_MEMORY_FOLD_2 = {
    "hash": "fold2",
    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
    "emotion": "joy",
    "emotion_vector": np.array([0.7, 0.5, 0.3]),
    "relevance_score": 0.9,
    "context": "Another happy memory",
    "user_id": "user1",
}
TEST_MEMORY_FOLD_3 = {
    "hash": "fold3",
    "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    "emotion": "sadness",
    "emotion_vector": np.array([-0.8, -0.6, -0.4]),
    "relevance_score": 0.5,
    "context": "A sad memory",
    "user_id": "user1",
}
TEST_MEMORY_FOLD_4 = {
    "hash": "fold4",
    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
    "emotion": "joy",
    "emotion_vector": np.array([0.75, 0.55, 0.35]),
    "relevance_score": 0.85,
    "context": "A third happy memory",
    "user_id": "user1",
}


@pytest.fixture
def mock_memory_system():
    """Fixture for a mocked MemoryFoldSystem."""
    mock_system = MagicMock()
    mock_system.recall_memory_folds.return_value = [
        TEST_MEMORY_FOLD_1,
        TEST_MEMORY_FOLD_2,
        TEST_MEMORY_FOLD_3,
        TEST_MEMORY_FOLD_4,
    ]
    mock_system.enhanced_recall_memory_folds.return_value = [
        TEST_MEMORY_FOLD_1,
        TEST_MEMORY_FOLD_2,
        TEST_MEMORY_FOLD_4,
    ]
    mock_system.create_memory_fold.return_value = {
        "hash": "new_fold",
        "emotion": "neutral",
        "context_snippet": "folded content",
        "user_id": "user1",
        "metadata": {},
    }
    mock_system.emotion_vectors = {"joy": np.array([0.8, 0.6, 0.4])}
    # Mock the database attribute for retrieve_by_glyph_affect
    mock_system.database.get_folds.return_value = [TEST_MEMORY_FOLD_1]

    return mock_system


class TestGlyphDataclasses:
    """Tests for the dataclasses."""

    def test_glyph_binding(self):
        """Test the GlyphBinding dataclass."""
        ts = datetime.utcnow()
        binding = GlyphBinding(
            glyph="💡",
            fold_key="fold1",
            affect_vector=TEST_AFFECT_VECTOR_1,
            binding_strength=0.9,
            created_at=ts,
            metadata={"source": "test"},
        )
        assert binding.glyph == "💡"
        assert binding.fold_key == "fold1"
        np.testing.assert_array_equal(binding.affect_vector, TEST_AFFECT_VECTOR_1)
        assert binding.binding_strength == 0.9
        assert binding.created_at == ts
        assert binding.metadata == {"source": "test"}

    def test_fold_lineage(self):
        """Test the FoldLineage dataclass."""
        ts = datetime.utcnow()
        lineage = FoldLineage(
            fold_key="fold_new",
            parent_key="fold1",
            emotion_delta=TEST_AFFECT_VECTOR_2,
            compression_ratio=0.5,
            timestamp=ts,
            glyphs={"💡", "🔗"},
            salience_score=0.85,
        )
        assert lineage.fold_key == "fold_new"
        assert lineage.parent_key == "fold1"
        np.testing.assert_array_equal(lineage.emotion_delta, TEST_AFFECT_VECTOR_2)
        assert lineage.compression_ratio == 0.5
        assert lineage.timestamp == ts
        assert lineage.glyphs == {"💡", "🔗"}
        assert lineage.salience_score == 0.85


class TestGlyphMemoryIndex:
    """Tests for the GlyphMemoryIndex class."""

    @pytest.fixture
    def index(self):
        return GlyphMemoryIndex()

    def test_init(self, index):
        assert isinstance(index.glyph_to_folds, defaultdict)
        assert isinstance(index.fold_to_glyphs, defaultdict)
        assert index.glyph_bindings == {}

    def test_bind_glyph_to_fold(self, index):
        binding = index.bind_glyph_to_fold(
            "💡", "fold1", TEST_AFFECT_VECTOR_1, 0.9
        )
        assert index.glyph_to_folds["💡"] == {"fold1"}
        assert index.fold_to_glyphs["fold1"] == {"💡"}
        assert index.glyph_bindings[("💡", "fold1")] == binding
        assert binding.binding_strength == 0.9

    def test_get_folds_by_glyph(self, index):
        index.bind_glyph_to_fold("💡", "fold1", TEST_AFFECT_VECTOR_1, 0.9)
        index.bind_glyph_to_fold("💡", "fold2", TEST_AFFECT_VECTOR_2, 0.7)
        index.bind_glyph_to_fold("🔗", "fold1", TEST_AFFECT_VECTOR_1, 0.8)

        folds = index.get_folds_by_glyph("💡")
        assert len(folds) == 2
        assert folds[0][0] == "fold1"  # Sorted by strength
        assert folds[1][0] == "fold2"

        folds_strong = index.get_folds_by_glyph("💡", min_strength=0.8)
        assert len(folds_strong) == 1
        assert folds_strong[0][0] == "fold1"

        assert index.get_folds_by_glyph("❓") == []

    def test_get_glyphs_by_fold(self, index):
        b1 = index.bind_glyph_to_fold("💡", "fold1", TEST_AFFECT_VECTOR_1, 0.9)
        b2 = index.bind_glyph_to_fold("🔗", "fold1", TEST_AFFECT_VECTOR_1, 0.8)

        glyphs = index.get_glyphs_by_fold("fold1")
        assert len(glyphs) == 2
        assert ("💡", b1) in glyphs
        assert ("🔗", b2) in glyphs

        assert index.get_glyphs_by_fold("fold2") == []

    def test_calculate_glyph_affinity(self, index):
        index.bind_glyph_to_fold("💡", "fold1", TEST_AFFECT_VECTOR_1)
        index.bind_glyph_to_fold("💡", "fold2", TEST_AFFECT_VECTOR_1)
        index.bind_glyph_to_fold("🔗", "fold1", TEST_AFFECT_VECTOR_1)
        index.bind_glyph_to_fold("🔗", "fold3", TEST_AFFECT_VECTOR_1)

        # 1 common fold (fold1), 3 unique folds (fold1, fold2, fold3) -> 1/3
        affinity = index.calculate_glyph_affinity("💡", "🔗")
        assert affinity == pytest.approx(1 / 3)

        # No common folds
        index.bind_glyph_to_fold("❓", "fold4", TEST_AFFECT_VECTOR_1)
        affinity_zero = index.calculate_glyph_affinity("💡", "❓")
        assert affinity_zero == 0.0

        # Non-existent glyph
        affinity_none = index.calculate_glyph_affinity("💡", "🌱")
        assert affinity_none == 0.0


class TestEmotionalFoldingEngine:
    """Tests for the EmotionalFoldingEngine class."""

    @pytest.fixture
    def engine(self, mock_memory_system):
        return EmotionalFoldingEngine(mock_memory_system)

    def test_identify_foldable_memories(self, engine):
        groups = engine.identify_foldable_memories()
        # Expects a group of the two 'joy' memories with high relevance
        assert len(groups) == 1
        assert len(groups[0]) == 3
        assert groups[0][0]["hash"] in ["fold1", "fold2", "fold4"]

    def test_fold_memory_group(self, engine):
        memory_group = [TEST_MEMORY_FOLD_1, TEST_MEMORY_FOLD_2]
        folded_memory = engine.fold_memory_group(memory_group)

        assert folded_memory is not None
        assert folded_memory["hash"] == "new_fold"
        engine.memory_system.create_memory_fold.assert_called_once()
        # Check that lineage was tracked
        assert "new_fold" in engine.fold_lineages

    def test_fold_memory_group_insufficient_mems(self, engine):
        assert engine.fold_memory_group([TEST_MEMORY_FOLD_1]) is None

    def test_fold_memory_group_no_emotion_vectors(self, engine):
        group_no_emotion = [
            {"hash": "f4", "context": "c4"},
            {"hash": "f5", "context": "c5"},
        ]
        assert engine.fold_memory_group(group_no_emotion) is None

    def test_compression_types(self, engine):
        group = [TEST_MEMORY_FOLD_1, TEST_MEMORY_FOLD_2]

        # CONSOLIDATION (default)
        engine.fold_memory_group(group, compression_type=CompressionType.CONSOLIDATION)
        call_args = engine.memory_system.create_memory_fold.call_args
        assert "Consolidated themes" in call_args[1]["context_snippet"]

        # ABSTRACTION
        engine.fold_memory_group(group, compression_type=CompressionType.ABSTRACTION)
        call_args = engine.memory_system.create_memory_fold.call_args
        assert "Pattern abstraction" in call_args[1]["context_snippet"]

        # SYNTHESIS
        engine.fold_memory_group(group, compression_type=CompressionType.SYNTHESIS)
        call_args = engine.memory_system.create_memory_fold.call_args
        assert "Synthesized insight" in call_args[1]["context_snippet"]


class TestGlyphAffectCoupler:
    """Tests for the GlyphAffectCoupler class."""

    @pytest.fixture
    def coupler(self, mock_memory_system):
        index = GlyphMemoryIndex()
        return GlyphAffectCoupler(mock_memory_system, index)

    def test_init(self, coupler):
        assert "💡" in coupler.glyph_affect_map
        np.testing.assert_array_equal(
            coupler.glyph_affect_map["💡"], np.array([0.6, 0.7, 0.5])
        )

    def test_couple_glyph_with_memory(self, coupler):
        binding = coupler.couple_glyph_with_memory("💡", TEST_MEMORY_FOLD_1)

        assert binding is not None
        assert binding.glyph == "💡"
        assert binding.fold_key == "fold1"
        assert "glyph_💡" in TEST_MEMORY_FOLD_1.setdefault("tags", set())

        # Test affect blending
        mem_affect = TEST_MEMORY_FOLD_1["emotion_vector"]
        glyph_affect = coupler.glyph_affect_map["💡"]
        expected_affect = 0.5 * mem_affect + 0.5 * glyph_affect
        np.testing.assert_allclose(binding.affect_vector, expected_affect)

    def test_retrieve_by_glyph_affect(self, coupler):
        # Bind a glyph first
        binding = coupler.couple_glyph_with_memory("💡", TEST_MEMORY_FOLD_1)

        # Mock the index return for the retrieve call
        coupler.glyph_index.get_folds_by_glyph = MagicMock(
            return_value=[("fold1", binding)]
        )

        results = coupler.retrieve_by_glyph_affect("💡", affect_threshold=1.0)
        assert len(results) == 1
        assert results[0]["hash"] == "fold1"
        assert "affect_distance" in results[0]

        # Test threshold
        results_filtered = coupler.retrieve_by_glyph_affect("💡", affect_threshold=0.1)
        assert len(results_filtered) == 0


class TestDreamMemoryBridge:
    """Tests for the DreamMemoryBridge class."""

    @pytest.fixture
    def bridge(self, mock_memory_system):
        index = GlyphMemoryIndex()
        engine = EmotionalFoldingEngine(mock_memory_system)
        return DreamMemoryBridge(mock_memory_system, index, engine)

    def test_process_dream_state(self, bridge):
        dream_data = {
            "emotion": "joy",
            "content": "A happy dream",
            "glyphs": ["💡", "🌱"],
        }
        results = bridge.process_dream_state(dream_data)

        assert results["processed_memories"] == 3
        assert set(results["activated_glyphs"]) == {"💡", "🌱"}
        # New associations are created for each glyph with each similar memory
        assert results["new_associations"] > 0
        # Folding is triggered
        assert len(results["folded_memories"]) == 1

    def test_get_dream_glyph_landscape(self, bridge):
        dream_data = {"emotion": "joy", "glyphs": ["💡", "💡", "🌱"]}
        bridge.process_dream_state(dream_data)

        landscape = bridge.get_dream_glyph_landscape()
        assert landscape["total_activations"] == 3
        assert landscape["unique_glyphs"] == 2
        assert landscape["top_glyphs"][0]["glyph"] == "💡"
        assert landscape["top_glyphs"][0]["activation_count"] == 2


class TestGlyphMemorySystem:
    """Tests for the main GlyphMemorySystem integration class."""

    @pytest.fixture
    def system(self):
        # Use patch to mock the dependent systems within the constructor
        with patch(
            "core.glyph.glyph_memory_integration.MemoryFoldSystem"
        ) as MockMemSys, patch(
            "core.glyph.glyph_memory_integration.GlyphMemoryIndex"
        ) as MockIndex, patch(
            "core.glyph.glyph_memory_integration.EmotionalFoldingEngine"
        ) as MockEngine, patch(
            "core.glyph.glyph_memory_integration.GlyphAffectCoupler"
        ) as MockCoupler, patch(
            "core.glyph.glyph_memory_integration.DreamMemoryBridge"
        ) as MockBridge:
            # Re-initialize the system to use the mocks
            glyph_system = GlyphMemorySystem(memory_fold_config={})
            yield glyph_system

    def test_create_glyph_indexed_memory(self, system):
        system.memory_system.create_memory_fold.return_value = TEST_MEMORY_FOLD_1
        system.create_glyph_indexed_memory("joy", "context", ["💡"])
        system.affect_coupler.couple_glyph_with_memory.assert_called_once()

        # Test no auto-coupling
        system.create_glyph_indexed_memory(
            "joy", "context", ["💡"], auto_couple=False
        )
        system.glyph_index.bind_glyph_to_fold.assert_called()

    def test_recall_by_glyph_pattern_any(self, system):
        system.glyph_index.get_folds_by_glyph.side_effect = [
            [("fold1", MagicMock())],
            [("fold2", MagicMock())],
        ]
        system.memory_system.recall_memory_folds.return_value = [
            TEST_MEMORY_FOLD_1,
            TEST_MEMORY_FOLD_2,
        ]

        results = system.recall_by_glyph_pattern(["💡", "🔗"], mode="any")
        assert len(results) == 2
        assert {r["hash"] for r in results} == {"fold1", "fold2"}

    def test_recall_by_glyph_pattern_all(self, system):
        system.glyph_index.get_folds_by_glyph.side_effect = [
            [("fold1", MagicMock()), ("fold2", MagicMock())],
            [("fold1", MagicMock())],
        ]
        # Intersection should be "fold1"
        system.memory_system.recall_memory_folds.return_value = [TEST_MEMORY_FOLD_1]

        results = system.recall_by_glyph_pattern(["💡", "🔗"], mode="all")
        assert len(results) == 1
        assert results[0]["hash"] == "fold1"

    def test_perform_temporal_folding(self, system):
        system.folding_engine.identify_foldable_memories.return_value = [
            [TEST_MEMORY_FOLD_1, TEST_MEMORY_FOLD_2]
        ]
        system.folding_engine.fold_memory_group.return_value = {"hash": "new_fold"}
        lineage = MagicMock()
        lineage.glyphs = {"💡"}
        system.folding_engine.fold_lineages.get.return_value = lineage

        results = system.perform_temporal_folding()
        assert results["groups_identified"] == 1
        assert results["memories_folded"] == 2
        assert results["new_folds"] == ["new_fold"]
        assert "💡" in results["preserved_glyphs"]

    def test_get_memory_glyph_statistics(self, system):
        system.memory_system.get_system_statistics.return_value = {"base": "stats"}
        system.dream_bridge.get_dream_glyph_landscape.return_value = {"dream": "stats"}

        stats = system.get_memory_glyph_statistics()
        assert stats["base"] == "stats"
        assert "glyph_integration" in stats
        assert stats["glyph_integration"]["dream_activations"]["dream"] == "stats"


class TestConvenienceFunctions:
    """Tests for the global convenience functions."""

    @patch("core.glyph.glyph_memory_integration.GlyphMemorySystem")
    def test_convenience_functions_call_system(self, MockGlyphSystem):
        # This ensures that get_glyph_memory_system is fresh for the test
        with patch("core.glyph.glyph_memory_integration._global_glyph_system", None):
            mock_instance = MockGlyphSystem.return_value

            create_glyph_memory("joy", "context", ["💡"])
            mock_instance.create_glyph_indexed_memory.assert_called_with(
                "joy", "context", ["💡"], None
            )

            recall_by_glyphs(["💡"])
            mock_instance.recall_by_glyph_pattern.assert_called_with(
                ["💡"], "any", user_tier=5, limit=50
            )

            fold_recent_memories(hours=12)
            mock_instance.perform_temporal_folding.assert_called_with(
                time_window=timedelta(hours=12)
            )

    def test_get_glyph_memory_system_singleton(self):
        with patch("core.glyph.glyph_memory_integration._global_glyph_system", None):
            system1 = get_glyph_memory_system()
            system2 = get_glyph_memory_system()
            assert system1 is system2
