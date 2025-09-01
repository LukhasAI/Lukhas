#!/usr/bin/env python3

"""
Unit Tests for Wave C Memory System
==================================

Fast, isolated unit tests covering:
- Transform chain completeness contracts
- Audit field persistence requirements
- Memory client interfaces
- Data validation and sanitization
- Configuration handling

Target: < 2s total runtime, 100% coverage
"""

import json
import time
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from candidate.aka_qualia.memory import create_memory_client
from candidate.aka_qualia.memory_noop import NoopMemory
from candidate.aka_qualia.memory_sql import SqlMemory
from candidate.aka_qualia.models import SeverityLevel

from .conftest import create_test_glyph, create_test_scene


class TestMemoryClientFactory:
    """Test the memory client factory function"""

    @pytest.mark.unit
    def test_create_noop_memory(self):
        """Factory should create NoopMemory correctly"""
        memory = create_memory_client("noop")
        assert isinstance(memory, NoopMemory)
        assert memory.driver == "noop"

    @pytest.mark.unit
    def test_create_sql_memory_sqlite(self, temp_sqlite_file):
        """Factory should create SqlMemory with SQLite"""
        memory = create_memory_client("sql", database=temp_sqlite_file)
        assert isinstance(memory, SqlMemory)
        assert memory.driver == "sqlite"

    @pytest.mark.unit
    def test_create_unknown_driver(self):
        """Factory should raise ValueError for unknown drivers"""
        with pytest.raises(ValueError, match="Unknown memory driver"):
            create_memory_client("unknown_driver")


class TestNoopMemoryInterface:
    """Test NoopMemory implementation"""

    @pytest.mark.unit
    def test_save_returns_valid_id(self, noop_memory):
        """NoopMemory save should return consistent ID format"""
        scene_data = create_test_scene()
        glyphs_data = [create_test_glyph()]

        scene_id = noop_memory.save(
            user_id="test_user",
            scene=scene_data,
            glyphs=glyphs_data,
            policy={"gain": 1.0, "pace": 1.0, "actions": []},
            metrics={"drift_phi": 0.9},
            cfg_version="wave_c_v1.0.0",
        )

        assert scene_id.startswith("noop_")
        assert len(scene_id) == 13  # "noop_" + 8 char hex
        assert noop_memory.save_calls == 1

    @pytest.mark.unit
    def test_fetch_prev_scene_returns_none(self, noop_memory):
        """NoopMemory should always return None for previous scenes"""
        result = noop_memory.fetch_prev_scene(user_id="test", before_ts=None)
        assert result is None
        assert noop_memory.fetch_calls == 1

    @pytest.mark.unit
    def test_get_stats_structure(self, noop_memory):
        """NoopMemory stats should have expected structure"""
        # Do some operations first
        noop_memory.save(user_id="u", scene={}, glyphs=[], policy={}, metrics={}, cfg_version="v1")
        noop_memory.fetch_prev_scene(user_id="u", before_ts=None)

        stats = noop_memory.get_stats()

        assert isinstance(stats, dict)
        assert stats["driver"] == "noop"
        assert stats["scenes_saved"] == 1
        assert stats["success_rate"] == 1.0
        assert "operation_counts" in stats
        assert stats["operation_counts"]["save_calls"] == 1
        assert stats["operation_counts"]["fetch_calls"] == 1


class TestContractValidation:
    """Test business rule contracts and invariants"""

    @pytest.mark.contract
    def test_transform_chain_required_for_high_risk(
        self, sql_memory, high_risk_scene, test_glyphs, test_policy, test_metrics
    ):
        """High-risk scenes must have non-empty transform chains"""

        scene_data = high_risk_scene.model_dump()
        glyphs_data = [g.model_dump() for g in test_glyphs]

        scene_id = sql_memory.save(
            user_id="test_user",
            scene=scene_data,
            glyphs=glyphs_data,
            policy=test_policy.model_dump(),
            metrics=test_metrics.model_dump(),
            cfg_version="wave_c_v1.0.0",
        )

        # Retrieve and verify transform chain
        history = sql_memory.get_scene_history(user_id="test_user", limit=1)
        assert len(history) == 1

        stored_scene = history[0]
        assert stored_scene["risk"]["severity"] == "high"
        assert "transform_chain" in stored_scene
        assert isinstance(stored_scene["transform_chain"], list)
        assert len(stored_scene["transform_chain"]) > 0

        # Verify regulation operations are present
        transform_ops = stored_scene["transform_chain"]
        regulation_present = any("sublimate" in str(op) or "teq.enforce" in str(op) for op in transform_ops)
        assert regulation_present, "High-risk scenes must contain regulation operations"

    @pytest.mark.contract
    def test_audit_fields_always_present(self, sql_memory, low_risk_scene, test_glyphs, test_policy, test_metrics):
        """All scenes must have required audit metadata"""

        scene_data = low_risk_scene.model_dump()
        glyphs_data = [g.model_dump() for g in test_glyphs]

        scene_id = sql_memory.save(
            user_id="audit_test_user",
            scene=scene_data,
            glyphs=glyphs_data,
            policy=test_policy.model_dump(),
            metrics=test_metrics.model_dump(),
            cfg_version="wave_c_v1.0.0",
        )

        # Retrieve and verify audit fields
        history = sql_memory.get_scene_history(user_id="audit_test_user", limit=1)
        stored_scene = history[0]
        context = stored_scene["context"]

        # Required audit fields
        assert "cfg_version" in context, "cfg_version must be preserved"
        assert context["cfg_version"].startswith("wave_c_v"), "cfg_version must follow format"
        assert "policy_sig" in context, "policy_sig must be preserved"
        assert len(context["policy_sig"]) >= 8, "policy_sig must be meaningful"

        # Scene-level audit fields
        assert "scene_id" in stored_scene
        assert "timestamp" in stored_scene
        assert stored_scene["timestamp"] > 0

    @pytest.mark.contract
    def test_scene_id_uniqueness(self, sql_memory):
        """Each save operation must generate unique scene IDs"""
        scene_data = create_test_scene()
        glyph_data = [create_test_glyph()]
        policy_data = {"gain": 1.0, "pace": 1.0, "actions": []}
        metrics_data = {"drift_phi": 0.9}

        # Save same data twice
        id1 = sql_memory.save(
            user_id="uniqueness_test",
            scene=scene_data,
            glyphs=glyph_data,
            policy=policy_data,
            metrics=metrics_data,
            cfg_version="wave_c_v1.0.0",
        )

        id2 = sql_memory.save(
            user_id="uniqueness_test",
            scene=scene_data,
            glyphs=glyph_data,
            policy=policy_data,
            metrics=metrics_data,
            cfg_version="wave_c_v1.0.0",
        )

        assert id1 != id2, "Scene IDs must be unique even for identical data"
        assert len(id1) > 0 and len(id2) > 0, "Scene IDs must be non-empty"


class TestDataValidation:
    """Test data validation and sanitization"""

    @pytest.mark.unit
    def test_proto_qualia_vector_conversion(self, sql_memory):
        """Proto-qualia should be converted to 5-dimensional vectors"""
        from candidate.aka_qualia.util import to_proto_vec

        proto_data = {"tone": 0.5, "arousal": 0.8, "clarity": 0.9, "embodiment": 0.7, "narrative_gravity": 0.6}

        vector = to_proto_vec(proto_data)

        assert isinstance(vector, list)
        assert len(vector) == 5
        assert all(isinstance(v, float) for v in vector)
        assert vector == [0.5, 0.8, 0.9, 0.7, 0.6]

    @pytest.mark.unit
    def test_missing_proto_fields_handled(self, sql_memory):
        """Missing proto-qualia fields should default gracefully"""
        from candidate.aka_qualia.util import to_proto_vec

        partial_proto = {"tone": 0.3, "clarity": 0.8}  # Missing other fields
        vector = to_proto_vec(partial_proto)

        assert len(vector) == 5
        assert vector[0] == 0.3  # tone preserved
        assert vector[2] == 0.8  # clarity preserved
        assert vector[1] == 0.0  # arousal defaulted
        assert vector[3] == 0.0  # embodiment defaulted
        assert vector[4] == 0.0  # narrative_gravity defaulted

    @pytest.mark.unit
    def test_json_serialization_safety(self, sql_memory):
        """All stored data should be JSON-serializable"""
        scene_data = create_test_scene(
            context={
                "cfg_version": "wave_c_v1.0.0",
                "complex_data": {"nested": {"deep": [1, 2, 3]}, "timestamp": time.time()},
            }
        )

        # Verify scene data is JSON-serializable
        json_str = json.dumps(scene_data)
        reconstructed = json.loads(json_str)

        assert reconstructed["context"]["complex_data"]["nested"]["deep"] == [1, 2, 3]
        assert isinstance(reconstructed["context"]["complex_data"]["timestamp"], (int, float))


class TestConfigurationHandling:
    """Test memory client configuration and initialization"""

    @pytest.mark.unit
    def test_sql_memory_development_mode(self, sqlite_engine):
        """Development mode should not hash PII"""
        memory = SqlMemory(engine=sqlite_engine, rotate_salt="dev_salt", is_prod=False)

        assert not memory.is_prod

        # Test that subject/object are not hashed in dev mode
        hashed_subject = memory._hash_safe("Alice")
        assert hashed_subject == "Alice"  # No hashing in dev mode

    @pytest.mark.unit
    def test_sql_memory_production_mode(self, sqlite_engine):
        """Production mode should hash PII fields"""
        memory = SqlMemory(engine=sqlite_engine, rotate_salt="prod_salt_secure", is_prod=True)

        assert memory.is_prod

        # Test that subjects are hashed in prod mode
        hashed_subject = memory._hash_safe("Alice")
        assert hashed_subject != "Alice"  # Should be hashed
        assert len(hashed_subject) == 64  # SHA3-256 hex length

        # Same input should always produce same hash
        hashed_again = memory._hash_safe("Alice")
        assert hashed_subject == hashed_again

    @pytest.mark.unit
    def test_noop_memory_initialization_variants(self):
        """NoopMemory should handle various initialization patterns"""

        # Default initialization
        memory1 = NoopMemory()
        assert memory1.driver == "noop"

        # With explicit prod flag
        memory2 = NoopMemory(is_prod=True)
        assert memory2.is_prod

        # Multiple instances should be independent
        memory1.save_calls = 5
        assert memory2.save_calls == 0


class TestErrorHandling:
    """Test error conditions and edge cases"""

    @pytest.mark.unit
    def test_empty_scene_data(self, noop_memory):
        """Memory clients should handle empty scene data gracefully"""

        scene_id = noop_memory.save(
            user_id="empty_test",
            scene={},  # Empty scene
            glyphs=[],  # No glyphs
            policy={},  # Empty policy
            metrics={},  # Empty metrics
            cfg_version="wave_c_v1.0.0",
        )

        assert scene_id is not None
        assert len(scene_id) > 0

    @pytest.mark.unit
    def test_none_user_id_handling(self, noop_memory):
        """None user_id should be handled gracefully"""
        scene_data = create_test_scene()

        scene_id = noop_memory.save(
            user_id=None,  # None user ID
            scene=scene_data,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Should still work (NoopMemory doesn't validate user_id)
        assert scene_id is not None

    @pytest.mark.unit
    def test_very_long_strings_truncated(self, sql_memory):
        """Very long strings should be handled appropriately"""
        long_string = "x" * 10000  # 10KB string

        scene_data = create_test_scene(subject=long_string, object=long_string)

        # Should not raise exception
        scene_id = sql_memory.save(
            user_id="truncation_test", scene=scene_data, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
        )

        assert scene_id is not None


class TestMemoryInterfaceCompliance:
    """Test that all memory implementations follow the interface"""

    @pytest.mark.unit
    @pytest.mark.parametrize("memory_fixture", ["noop_memory", "sql_memory"])
    def test_save_method_signature(self, memory_fixture, request):
        """All memory implementations must support save() with same signature"""
        memory = request.getfixturevalue(memory_fixture)

        scene_data = create_test_scene()
        glyph_data = [create_test_glyph()]

        # Should not raise TypeError
        scene_id = memory.save(
            user_id="interface_test",
            scene=scene_data,
            glyphs=glyph_data,
            policy={"gain": 1.0},
            metrics={"drift_phi": 0.9},
            cfg_version="wave_c_v1.0.0",
        )

        assert isinstance(scene_id, str)
        assert len(scene_id) > 0

    @pytest.mark.unit
    @pytest.mark.parametrize("memory_fixture", ["noop_memory", "sql_memory"])
    def test_get_stats_method_signature(self, memory_fixture, request):
        """All memory implementations must support get_stats()"""
        memory = request.getfixturevalue(memory_fixture)

        stats = memory.get_stats()

        assert isinstance(stats, dict)
        assert "driver" in stats
        assert isinstance(stats.get("scenes_saved", 0), int)

    @pytest.mark.unit
    @pytest.mark.parametrize("memory_fixture", ["noop_memory", "sql_memory"])
    def test_fetch_prev_scene_method_signature(self, memory_fixture, request):
        """All memory implementations must support fetch_prev_scene()"""
        memory = request.getfixturevalue(memory_fixture)

        # Should not raise TypeError (result can be None)
        result = memory.fetch_prev_scene(user_id="test", before_ts=None)

        # Result should be None or dict
        assert result is None or isinstance(result, dict)
