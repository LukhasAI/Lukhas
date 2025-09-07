#!/usr/bin/env python3
"""
MATRIZ Cognitive Node Interface

This module defines the base interface that all MATRIZ cognitive nodes must implement.
Every node MUST emit MATRIZ format nodes for complete interpretability and governance.

The MATRIZ format ensures:
- Full traceability of cognitive processes
- Deterministic reproduction of results
- Ethical governance through provenance tracking
- Causal chain reconstruction for interpretability
"""
from typing import List
from typing import Dict
import streamlit as st

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class NodeState:
    """Standard state structure for MATRIZ nodes"""

    confidence: float  # 0.0 - 1.0
    salience: float  # 0.0 - 1.0
    valence: Optional[float] = None  # -1.0 to 1.0 (emotional valence)
    arousal: Optional[float] = None  # 0.0 - 1.0 (emotional arousal)
    novelty: Optional[float] = None  # 0.0 - 1.0 (how novel this is)
    urgency: Optional[float] = None  # 0.0 - 1.0 (time pressure)
    shock_factor: Optional[float] = None  # 0.0 - 1.0 (unexpected factor)
    risk: Optional[float] = None  # 0.0 - 1.0 (risk assessment)
    utility: Optional[float] = None  # 0.0 - 1.0 (value/usefulness)


@dataclass
class NodeLink:
    """Connection between MATRIZ nodes"""

    target_node_id: str
    link_type: str  # temporal, causal, semantic, emotional, spatial, evidence
    direction: str  # bidirectional, unidirectional
    weight: Optional[float] = None
    explanation: Optional[str] = None


@dataclass
class NodeTrigger:
    """Event that triggered this node's creation or update"""

    event_type: str
    timestamp: int  # epoch milliseconds
    trigger_node_id: Optional[str] = None
    effect: Optional[str] = None


@dataclass
class NodeReflection:
    """Introspective log about this node's processing"""

    reflection_type: str  # regret, affirmation, dissonance_resolution, moral_conflict, self_question
    timestamp: int  # epoch milliseconds
    old_state: Optional[dict] = None
    new_state: Optional[dict] = None
    cause: Optional[str] = None


@dataclass
class NodeProvenance:
    """Complete provenance tracking for governance"""

    producer: str  # Module path or service name
    capabilities: list[str]  # What this producer can do
    tenant: str  # Tenant identifier
    trace_id: str  # Execution trace ID
    consent_scopes: list[str]  # What consent scopes apply
    subject_pseudonym: Optional[str] = None
    model_signature: Optional[str] = None
    policy_version: Optional[str] = None
    colony: Optional[dict] = None  # Colony/swarm metadata


class CognitiveNode(ABC):
    """
    Abstract base class for all MATRIZ cognitive nodes.

    Every cognitive node must:
    1. Process input deterministically
    2. Emit complete MATRIZ format nodes
    3. Support interpretability through tracing
    4. Validate its own outputs

    The MATRIZ format ensures complete auditability and governance.
    """

    def __init__(self, node_name: str, capabilities: list[str], tenant: str = "default"):
        """
        Initialize the cognitive node.

        Args:
            node_name: Unique identifier for this node type
            capabilities: List of capabilities this node provides
            tenant: Tenant identifier for multi-tenancy
        """
        self.node_name = node_name
        self.capabilities = capabilities
        self.tenant = tenant
        self.processing_history: list[dict] = []

    @abstractmethod
    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process input data and return result with MATRIZ node.

        This method MUST:
        1. Process the input deterministically
        2. Create a complete MATRIZ format node
        3. Return both the result and the MATRIZ node
        4. Support reproducible execution

        Args:
            input_data: Input to process (must be JSON-serializable)

        Returns:
            Dict containing:
            - 'answer': The processing result
            - 'confidence': Confidence in the result (0.0-1.0)
            - 'matriz_node': Complete MATRIZ format node
            - 'processing_time': Time taken in seconds
        """
        pass

    @abstractmethod
    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the output of this node's processing.

        This method should check:
        1. Output format correctness
        2. MATRIZ node completeness
        3. Logical consistency
        4. Ethical compliance (if applicable)

        Args:
            output: The output from process() method

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_trace(self) -> list[dict]:
        """
        Return the complete processing trace for interpretability.

        Returns:
            List of all MATRIZ nodes created by this processor
        """
        return self.processing_history.copy()

    def create_matriz_node(
        self,
        node_type: str,
        state: Union[NodeState, dict],
        links: Optional[list[NodeLink]] = None,
        triggers: Optional[list[NodeTrigger]] = None,
        reflections: Optional[list[NodeReflection]] = None,
        evolves_to: Optional[list[str]] = None,
        trace_id: Optional[str] = None,
        additional_data: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Create a complete MATRIZ format node.

        This is a helper method that ensures all nodes conform to the MATRIZ schema.

        Args:
            node_type: Type from allowed MATRIZ types
            state: Node state (NodeState object or dict)
            links: Connections to other nodes
            triggers: What triggered this node
            reflections: Introspective logs
            evolves_to: Future evolution paths
            trace_id: Execution trace identifier
            additional_data: Extra fields for the state

        Returns:
            Complete MATRIZ format node
        """
        node_id = str(uuid.uuid4())
        current_time = int(time.time() * 1000)  # epoch milliseconds

        # Validate node type
        allowed_types = [
            "SENSORY_IMG",
            "SENSORY_AUD",
            "SENSORY_VID",
            "SENSORY_TOUCH",
            "EMOTION",
            "INTENT",
            "DECISION",
            "CONTEXT",
            "MEMORY",
            "REFLECTION",
            "CAUSAL",
            "TEMPORAL",
            "AWARENESS",
            "HYPOTHESIS",
            "REPLAY",
            "DRM",
            "COMPUTATION",  # Add COMPUTATION as valid type for mathematical nodes
            "VALIDATION",  # Add VALIDATION as valid type for validation nodes
        ]
        if node_type not in allowed_types:
            raise ValueError(f"Invalid node type '{node_type}'. Must be one of: {allowed_types}")

        # Convert state to dict if NodeState object
        if isinstance(state, NodeState):
            state_dict = {"confidence": state.confidence, "salience": state.salience}
            # Add optional fields if not None
            for field in [
                "valence",
                "arousal",
                "novelty",
                "urgency",
                "shock_factor",
                "risk",
                "utility",
            ]:
                value = getattr(state, field)
                if value is not None:
                    state_dict[field] = value
        else:
            state_dict = dict(state)

        # Add additional data to state
        if additional_data:
            state_dict.update(additional_data)

        # Ensure required state fields
        if "confidence" not in state_dict or "salience" not in state_dict:
            raise ValueError("State must include 'confidence' and 'salience' fields")

        # Create provenance
        provenance = NodeProvenance(
            producer=f"{self.__class__.__module__}.{self.__class__.__name__}",
            capabilities=self.capabilities,
            tenant=self.tenant,
            trace_id=trace_id or str(uuid.uuid4()),
            consent_scopes=["cognitive_processing"],  # Default scope
        )

        # Build the MATRIZ node
        matriz_node = {
            "version": 1,
            "id": node_id,
            "type": node_type,
            "state": state_dict,
            "timestamps": {"created_ts": current_time},
            "provenance": {
                "producer": provenance.producer,
                "capabilities": provenance.capabilities,
                "tenant": provenance.tenant,
                "trace_id": provenance.trace_id,
                "consent_scopes": provenance.consent_scopes,
            },
            "links": [link.__dict__ if isinstance(link, NodeLink) else link for link in (links or [])],
            "evolves_to": evolves_to or [],
            "triggers": [
                trigger.__dict__ if isinstance(trigger, NodeTrigger) else trigger for trigger in (triggers or [])
            ],
            "reflections": [
                refl.__dict__ if isinstance(refl, NodeReflection) else refl for refl in (reflections or [])
            ],
            "schema_ref": "lukhas://schemas/matriz_node_v1.json",
        }

        # Store in processing history
        self.processing_history.append(matriz_node)

        return matriz_node

    def validate_matriz_node(self, node: dict[str, Any]) -> bool:
        """
        Validate that a node conforms to MATRIZ schema.

        Args:
            node: The node to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            required_fields = [
                "version",
                "id",
                "type",
                "state",
                "timestamps",
                "provenance",
            ]
            for field in required_fields:
                if field not in node:
                    return False

            # Check state required fields
            state = node.get("state", {})
            if "confidence" not in state or "salience" not in state:
                return False

            # Check confidence and salience ranges
            confidence = state.get("confidence", 0)
            salience = state.get("salience", 0)
            if not (0 <= confidence <= 1) or not (0 <= salience <= 1):
                return False

            # Check provenance required fields
            provenance = node.get("provenance", {})
            prov_required = [
                "producer",
                "capabilities",
                "tenant",
                "trace_id",
                "consent_scopes",
            ]
            return all(field in provenance for field in prov_required)

        except Exception:
            return False

    def create_reflection(
        self,
        reflection_type: str,
        cause: str,
        old_state: Optional[dict] = None,
        new_state: Optional[dict] = None,
    ) -> NodeReflection:
        """
        Create a reflection about this node's processing.

        Args:
            reflection_type: Type of reflection (regret, affirmation, etc.)
            cause: What caused this reflection
            old_state: Previous state (if applicable)
            new_state: New state (if applicable)

        Returns:
            NodeReflection object
        """
        allowed_types = [
            "regret",
            "affirmation",
            "dissonance_resolution",
            "moral_conflict",
            "self_question",
        ]
        if reflection_type not in allowed_types:
            raise ValueError(f"Invalid reflection type. Must be one of: {allowed_types}")

        return NodeReflection(
            reflection_type=reflection_type,
            timestamp=int(time.time() * 1000),
            old_state=old_state,
            new_state=new_state,
            cause=cause,
        )

    def create_link(
        self,
        target_node_id: str,
        link_type: str,
        direction: str = "unidirectional",
        weight: Optional[float] = None,
        explanation: Optional[str] = None,
    ) -> NodeLink:
        """
        Create a link to another MATRIZ node.

        Args:
            target_node_id: ID of the target node
            link_type: Type of link (temporal, causal, semantic, emotional, spatial, evidence)
            direction: bidirectional or unidirectional
            weight: Optional weight (0.0-1.0)
            explanation: Optional explanation of the link

        Returns:
            NodeLink object
        """
        allowed_link_types = [
            "temporal",
            "causal",
            "semantic",
            "emotional",
            "spatial",
            "evidence",
        ]
        if link_type not in allowed_link_types:
            raise ValueError(f"Invalid link type. Must be one of: {allowed_link_types}")

        allowed_directions = ["bidirectional", "unidirectional"]
        if direction not in allowed_directions:
            raise ValueError(f"Invalid direction. Must be one of: {allowed_directions}")

        return NodeLink(
            target_node_id=target_node_id,
            link_type=link_type,
            direction=direction,
            weight=weight,
            explanation=explanation,
        )

    def get_deterministic_hash(self, input_data: dict[str, Any]) -> str:
        """
        Generate a deterministic hash for reproducible processing.

        This ensures that the same input always produces the same hash,
        enabling deterministic node creation and caching.

        Args:
            input_data: The input data to hash

        Returns:
            Deterministic hash string
        """
        import hashlib
        import json

        # Create deterministic JSON representation
        canonical_json = json.dumps(input_data, sort_keys=True, separators=(",", ":"))

        # Add node identifier for uniqueness
        hash_input = f"{self.node_name}:{canonical_json}"

        # Generate SHA-256 hash
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        """String representation of the node"""
        return f"{self.__class__.__name__}(name='{self.node_name}', capabilities={self.capabilities})"
