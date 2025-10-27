"""
Comprehensive tests for MATRIZ CognitiveNode interface and helpers.

Tests cover:
- Node initialization
- MATRIZ node creation with schema compliance
- State management and validation
- Link creation and validation
- Trigger creation
- Reflection creation
- Deterministic hashing
- Error handling and edge cases
"""

import os
import sys
from unittest.mock import Mock

import pytest

# Ensure repository root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Skip if Python < 3.10 (matriz requirement)
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10), reason="matriz module requires Python 3.10+"
)

try:
    from MATRIZ.core.node_interface import (
        CognitiveNode,
        NodeLink,
        NodeProvenance,
        NodeReflection,
        NodeState,
        NodeTrigger,
    )

    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False

    # Mocks for test discovery
    class CognitiveNode:
        pass

    class NodeState:
        pass

    class NodeLink:
        pass

    class NodeTrigger:
        pass

    class NodeReflection:
        pass

    class NodeProvenance:
        pass


# Create a concrete implementation for testing
@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNode(CognitiveNode):
    """Concrete node for testing."""

    def process(self, input_data):
        return {
            "answer": "test_result",
            "confidence": 0.9,
            "matriz_node": self.create_matriz_node(
                node_type="CONTEXT",
                state=NodeState(confidence=0.9, salience=0.8),
                additional_data={"test": True},
            ),
        }

    def validate_output(self, output):
        return "answer" in output and "matriz_node" in output


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNodeInitialization:
    """Test CognitiveNode initialization."""

    def test_node_initializes_with_required_params(self):
        """Node should initialize with name and capabilities."""
        node = TestNode(node_name="test_node", capabilities=["test"])

        assert node.node_name == "test_node"
        assert node.capabilities == ["test"]
        assert node.tenant == "default"

    def test_node_initializes_with_custom_tenant(self):
        """Node should accept custom tenant."""
        node = TestNode(node_name="test", capabilities=["test"], tenant="custom")

        assert node.tenant == "custom"

    def test_node_initializes_with_empty_history(self):
        """Node should start with empty processing history."""
        node = TestNode(node_name="test", capabilities=["test"])

        assert node.processing_history == []

    def test_node_repr_is_descriptive(self):
        """Node __repr__ should include key info."""
        node = TestNode(node_name="test_node", capabilities=["cap1", "cap2"])

        repr_str = repr(node)
        assert "TestNode" in repr_str
        assert "test_node" in repr_str


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNodeStateCreation:
    """Test NodeState dataclass."""

    def test_state_requires_confidence_and_salience(self):
        """NodeState must have confidence and salience."""
        state = NodeState(confidence=0.8, salience=0.7)

        assert state.confidence == 0.8
        assert state.salience == 0.7

    def test_state_optional_fields_default_none(self):
        """Optional state fields should default to None."""
        state = NodeState(confidence=0.8, salience=0.7)

        assert state.valence is None
        assert state.arousal is None
        assert state.novelty is None
        assert state.urgency is None

    def test_state_accepts_all_optional_fields(self):
        """NodeState should accept all optional emotional fields."""
        state = NodeState(
            confidence=0.9,
            salience=0.8,
            valence=0.5,
            arousal=0.6,
            novelty=0.7,
            urgency=0.3,
            shock_factor=0.2,
            risk=0.4,
            utility=0.9,
        )

        assert state.valence == 0.5
        assert state.arousal == 0.6
        assert state.novelty == 0.7
        assert state.urgency == 0.3
        assert state.shock_factor == 0.2
        assert state.risk == 0.4
        assert state.utility == 0.9


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestMATRIZNodeCreation:
    """Test create_matriz_node method."""

    def test_creates_node_with_required_fields(self):
        """Created MATRIZ node should have all required fields."""
        node = TestNode(node_name="test", capabilities=["test"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        # Required top-level fields
        assert "version" in matriz_node
        assert "id" in matriz_node
        assert "type" in matriz_node
        assert "state" in matriz_node
        assert "timestamps" in matriz_node
        assert "provenance" in matriz_node

    def test_creates_node_with_valid_type(self):
        """Created node should have valid MATRIZ type."""
        node = TestNode(node_name="test", capabilities=["test"])

        matriz_node = node.create_matriz_node(
            node_type="COMPUTATION", state=NodeState(confidence=0.9, salience=0.8)
        )

        assert matriz_node["type"] == "COMPUTATION"

    def test_rejects_invalid_node_type(self):
        """Should raise ValueError for invalid node type."""
        node = TestNode(node_name="test", capabilities=["test"])

        with pytest.raises(ValueError, match="Invalid node type"):
            node.create_matriz_node(
                node_type="INVALID_TYPE", state=NodeState(confidence=0.8, salience=0.7)
            )

    def test_creates_unique_node_ids(self):
        """Each created node should have unique ID."""
        node = TestNode(node_name="test", capabilities=["test"])

        node1 = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )
        node2 = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        assert node1["id"] != node2["id"]

    def test_node_stores_in_processing_history(self):
        """Created nodes should be added to processing history."""
        node = TestNode(node_name="test", capabilities=["test"])

        initial_count = len(node.processing_history)
        node.create_matriz_node(node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7))

        assert len(node.processing_history) == initial_count + 1

    def test_state_from_nodestate_object(self):
        """Should accept NodeState object for state."""
        node = TestNode(node_name="test", capabilities=["test"])
        state_obj = NodeState(confidence=0.9, salience=0.8, valence=0.5)

        matriz_node = node.create_matriz_node(node_type="EMOTION", state=state_obj)

        assert matriz_node["state"]["confidence"] == 0.9
        assert matriz_node["state"]["salience"] == 0.8
        assert matriz_node["state"]["valence"] == 0.5

    def test_state_from_dict(self):
        """Should accept dict for state."""
        node = TestNode(node_name="test", capabilities=["test"])
        state_dict = {"confidence": 0.95, "salience": 0.85, "custom_field": "value"}

        matriz_node = node.create_matriz_node(node_type="CONTEXT", state=state_dict)

        assert matriz_node["state"]["confidence"] == 0.95
        assert matriz_node["state"]["salience"] == 0.85
        assert matriz_node["state"]["custom_field"] == "value"

    def test_additional_data_merged_into_state(self):
        """Additional data should be merged into state."""
        node = TestNode(node_name="test", capabilities=["test"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT",
            state=NodeState(confidence=0.8, salience=0.7),
            additional_data={"answer": "42", "metadata": {"source": "test"}},
        )

        assert matriz_node["state"]["answer"] == "42"
        assert matriz_node["state"]["metadata"]["source"] == "test"

    def test_provenance_includes_producer(self):
        """Provenance should include producer path."""
        node = TestNode(node_name="test", capabilities=["testing"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        provenance = matriz_node["provenance"]
        assert "producer" in provenance
        assert "TestNode" in provenance["producer"]

    def test_provenance_includes_capabilities(self):
        """Provenance should include node capabilities."""
        node = TestNode(node_name="test", capabilities=["cap1", "cap2"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        assert "cap1" in matriz_node["provenance"]["capabilities"]
        assert "cap2" in matriz_node["provenance"]["capabilities"]

    def test_provenance_includes_tenant(self):
        """Provenance should include tenant."""
        node = TestNode(node_name="test", capabilities=["test"], tenant="tenant_123")

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        assert matriz_node["provenance"]["tenant"] == "tenant_123"


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNodeValidation:
    """Test validate_matriz_node method."""

    def test_validates_complete_node(self):
        """Valid complete node should pass validation."""
        node = TestNode(node_name="test", capabilities=["test"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        assert node.validate_matriz_node(matriz_node) is True

    def test_rejects_node_missing_version(self):
        """Node without version should fail validation."""
        node = TestNode(node_name="test", capabilities=["test"])

        invalid_node = {"id": "test", "type": "CONTEXT", "state": {}}

        assert node.validate_matriz_node(invalid_node) is False

    def test_rejects_node_missing_state_confidence(self):
        """Node without state.confidence should fail."""
        node = TestNode(node_name="test", capabilities=["test"])

        invalid_node = {
            "version": 1,
            "id": "test",
            "type": "CONTEXT",
            "state": {"salience": 0.7},
            "timestamps": {},
            "provenance": {},
        }

        assert node.validate_matriz_node(invalid_node) is False

    def test_rejects_out_of_range_confidence(self):
        """Confidence outside [0,1] should fail validation."""
        node = TestNode(node_name="test", capabilities=["test"])

        invalid_node = {
            "version": 1,
            "id": "test",
            "type": "CONTEXT",
            "state": {"confidence": 1.5, "salience": 0.7},
            "timestamps": {},
            "provenance": {
                "producer": "test",
                "capabilities": [],
                "tenant": "test",
                "trace_id": "test",
                "consent_scopes": [],
            },
        }

        assert node.validate_matriz_node(invalid_node) is False

    def test_rejects_missing_provenance_fields(self):
        """Node with incomplete provenance should fail."""
        node = TestNode(node_name="test", capabilities=["test"])

        invalid_node = {
            "version": 1,
            "id": "test",
            "type": "CONTEXT",
            "state": {"confidence": 0.8, "salience": 0.7},
            "timestamps": {},
            "provenance": {"producer": "test"},  # Missing required fields
        }

        assert node.validate_matriz_node(invalid_node) is False


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestLinkCreation:
    """Test create_link method."""

    def test_creates_link_with_valid_params(self):
        """Should create link with valid parameters."""
        node = TestNode(node_name="test", capabilities=["test"])

        link = node.create_link(
            target_node_id="target-123",
            link_type="causal",
            direction="unidirectional",
        )

        assert isinstance(link, NodeLink)
        assert link.target_node_id == "target-123"
        assert link.link_type == "causal"
        assert link.direction == "unidirectional"

    def test_link_accepts_all_valid_types(self):
        """Should accept all valid link types."""
        node = TestNode(node_name="test", capabilities=["test"])
        valid_types = ["temporal", "causal", "semantic", "emotional", "spatial", "evidence"]

        for link_type in valid_types:
            link = node.create_link(target_node_id="test", link_type=link_type)
            assert link.link_type == link_type

    def test_link_rejects_invalid_type(self):
        """Should reject invalid link type."""
        node = TestNode(node_name="test", capabilities=["test"])

        with pytest.raises(ValueError, match="Invalid link type"):
            node.create_link(target_node_id="test", link_type="invalid")

    def test_link_accepts_bidirectional(self):
        """Should accept bidirectional direction."""
        node = TestNode(node_name="test", capabilities=["test"])

        link = node.create_link(
            target_node_id="test", link_type="semantic", direction="bidirectional"
        )

        assert link.direction == "bidirectional"

    def test_link_rejects_invalid_direction(self):
        """Should reject invalid direction."""
        node = TestNode(node_name="test", capabilities=["test"])

        with pytest.raises(ValueError, match="Invalid direction"):
            node.create_link(target_node_id="test", link_type="causal", direction="invalid")

    def test_link_accepts_optional_weight(self):
        """Should accept optional weight."""
        node = TestNode(node_name="test", capabilities=["test"])

        link = node.create_link(target_node_id="test", link_type="causal", weight=0.85)

        assert link.weight == 0.85

    def test_link_accepts_optional_explanation(self):
        """Should accept optional explanation."""
        node = TestNode(node_name="test", capabilities=["test"])

        link = node.create_link(
            target_node_id="test",
            link_type="causal",
            explanation="This causes that",
        )

        assert link.explanation == "This causes that"


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestReflectionCreation:
    """Test create_reflection method."""

    def test_creates_reflection_with_valid_params(self):
        """Should create reflection with valid parameters."""
        node = TestNode(node_name="test", capabilities=["test"])

        reflection = node.create_reflection(
            reflection_type="affirmation", cause="validation_success"
        )

        assert isinstance(reflection, NodeReflection)
        assert reflection.reflection_type == "affirmation"
        assert reflection.cause == "validation_success"

    def test_reflection_accepts_all_valid_types(self):
        """Should accept all valid reflection types."""
        node = TestNode(node_name="test", capabilities=["test"])
        valid_types = [
            "regret",
            "affirmation",
            "dissonance_resolution",
            "moral_conflict",
            "self_question",
        ]

        for refl_type in valid_types:
            reflection = node.create_reflection(reflection_type=refl_type, cause="test")
            assert reflection.reflection_type == refl_type

    def test_reflection_rejects_invalid_type(self):
        """Should reject invalid reflection type."""
        node = TestNode(node_name="test", capabilities=["test"])

        with pytest.raises(ValueError, match="Invalid reflection type"):
            node.create_reflection(reflection_type="invalid", cause="test")

    def test_reflection_accepts_old_and_new_state(self):
        """Should accept old and new state dicts."""
        node = TestNode(node_name="test", capabilities=["test"])

        old_state = {"confidence": 0.7}
        new_state = {"confidence": 0.9}

        reflection = node.create_reflection(
            reflection_type="affirmation",
            cause="improvement",
            old_state=old_state,
            new_state=new_state,
        )

        assert reflection.old_state == old_state
        assert reflection.new_state == new_state

    def test_reflection_has_timestamp(self):
        """Reflection should include timestamp."""
        node = TestNode(node_name="test", capabilities=["test"])

        reflection = node.create_reflection(reflection_type="affirmation", cause="test")

        assert reflection.timestamp > 0


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestDeterministicHashing:
    """Test get_deterministic_hash method."""

    def test_same_input_produces_same_hash(self):
        """Same input should always produce same hash."""
        node = TestNode(node_name="test", capabilities=["test"])

        input_data = {"query": "test", "value": 42}
        hash1 = node.get_deterministic_hash(input_data)
        hash2 = node.get_deterministic_hash(input_data)

        assert hash1 == hash2

    def test_different_input_produces_different_hash(self):
        """Different input should produce different hash."""
        node = TestNode(node_name="test", capabilities=["test"])

        input1 = {"query": "test1"}
        input2 = {"query": "test2"}

        hash1 = node.get_deterministic_hash(input1)
        hash2 = node.get_deterministic_hash(input2)

        assert hash1 != hash2

    def test_key_order_does_not_affect_hash(self):
        """Dict key order should not affect hash (canonical JSON)."""
        node = TestNode(node_name="test", capabilities=["test"])

        input1 = {"a": 1, "b": 2, "c": 3}
        input2 = {"c": 3, "a": 1, "b": 2}

        hash1 = node.get_deterministic_hash(input1)
        hash2 = node.get_deterministic_hash(input2)

        assert hash1 == hash2

    def test_hash_includes_node_name(self):
        """Hash should be unique to node type."""
        node1 = TestNode(node_name="node1", capabilities=["test"])
        node2 = TestNode(node_name="node2", capabilities=["test"])

        same_input = {"query": "test"}
        hash1 = node1.get_deterministic_hash(same_input)
        hash2 = node2.get_deterministic_hash(same_input)

        # Should differ because node names differ
        assert hash1 != hash2

    def test_hash_is_sha256_length(self):
        """Hash should be valid SHA-256 (64 hex characters)."""
        node = TestNode(node_name="test", capabilities=["test"])

        hash_val = node.get_deterministic_hash({"test": "data"})

        assert len(hash_val) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in hash_val)


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestProcessingHistory:
    """Test processing history tracking."""

    def test_get_trace_returns_copy(self):
        """get_trace should return copy of history."""
        node = TestNode(node_name="test", capabilities=["test"])
        node.create_matriz_node(node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7))

        trace = node.get_trace()

        # Modify the returned trace
        trace.append("extra_item")

        # Original should be unchanged
        assert len(node.processing_history) == 1
        assert len(trace) == 2

    def test_get_trace_includes_all_created_nodes(self):
        """Trace should include all nodes created by this processor."""
        node = TestNode(node_name="test", capabilities=["test"])

        node.create_matriz_node(node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7))
        node.create_matriz_node(node_type="DECISION", state=NodeState(confidence=0.9, salience=0.8))

        trace = node.get_trace()

        assert len(trace) == 2
        assert trace[0]["type"] == "CONTEXT"
        assert trace[1]["type"] == "DECISION"


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_state_requires_confidence_and_salience(self):
        """Creating node without required state fields should fail."""
        node = TestNode(node_name="test", capabilities=["test"])

        with pytest.raises(ValueError, match="confidence.*salience"):
            node.create_matriz_node(node_type="CONTEXT", state={"missing_required": True})

    def test_empty_capabilities_list(self):
        """Node with empty capabilities should work."""
        node = TestNode(node_name="test", capabilities=[])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        assert matriz_node["provenance"]["capabilities"] == []

    def test_very_long_node_name(self):
        """Very long node name should be handled."""
        long_name = "x" * 1000
        node = TestNode(node_name=long_name, capabilities=["test"])

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT", state=NodeState(confidence=0.8, salience=0.7)
        )

        # Should not crash
        assert "id" in matriz_node

    def test_complex_additional_data(self):
        """Complex nested additional data should be handled."""
        node = TestNode(node_name="test", capabilities=["test"])

        complex_data = {
            "nested": {"level1": {"level2": {"value": 42}}},
            "list": [1, 2, 3],
            "mixed": {"a": [1, 2], "b": {"c": 3}},
        }

        matriz_node = node.create_matriz_node(
            node_type="CONTEXT",
            state=NodeState(confidence=0.8, salience=0.7),
            additional_data=complex_data,
        )

        assert matriz_node["state"]["nested"]["level1"]["level2"]["value"] == 42
        assert matriz_node["state"]["list"] == [1, 2, 3]
