#!/usr/bin/env python3
"""
LUKHAS 2030 Symbolic Communication Consolidation
Universal symbolic language system for MΛTRIZ integration.

This script provides a bridge function to convert the state of a
SymbolicWorld object into a valid MΛTRIZ node.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone

from candidate.core.symbolic.glyph_engine import generate_glyph

# Assuming execution from a context where 'candidate' is in the Python path.
from candidate.core.symbolic.symbolic_core import SymbolicWorld


def consolidate_symbolic_communication():
    """
    This function is a placeholder for a larger consolidation effort.
    Currently, the main functionality is provided by the bridge function
    `create_matriz_node_from_symbolic_world`.
    """
    print("Consolidation of symbolic communication systems is a work in progress.")
    print("Use `create_matriz_node_from_symbolic_world` for MΛTRIZ integration.")


def create_matriz_node_from_symbolic_world(symbolic_world: SymbolicWorld) -> dict:
    """
    Creates a MΛTRIZ node from a SymbolicWorld instance.

    This function acts as a bridge, converting the state and structure of a
    SymbolicWorld into a valid MΛTRIZ node dictionary, compliant with the
    `lukhas://schemas/matriz_node_v1.json` schema.

    Args:
        symbolic_world: An instance of SymbolicWorld containing symbols and relationships.

    Returns:
        A dictionary representing a MΛTRIZ node.
    """
    # Generate a glyph, a unique symbolic representation of the world's current state.
    world_state_dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": "jules-integration-consolidator",
        "tier_level": 5,  # System-level agent
        "symbol_count": len(symbolic_world.symbols),
        "relationship_count": len(symbolic_world.relationships),
    }
    glyph = generate_glyph(world_state_dict)

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    trace_id = f"trace-{uuid.uuid4()}"

    # Construct the MΛTRIZ node dictionary according to the defined schema.
    matriz_node = {
        "version": 1,
        "id": f"node-{uuid.uuid4()}",
        "type": "CONTEXT",  # Represents the context of the symbolic world.
        "labels": ["symbolic-world", "consolidation-bridge"],
        "state": {
            "confidence": 0.9,
            "salience": 0.8,
            "novelty": 0.5,
            "utility": 0.7,
        },
        "timestamps": {
            "created_ts": now_ms,
            "updated_ts": now_ms,
        },
        # Provenance tracks the origin and capabilities of the node producer.
        "provenance": {
            "producer": "candidate.core.integration.consolidate_symbolic_communication",
            "capabilities": [
                "symbolic-consolidation",
                "matriz-bridge",
                "glyph-generation",
            ],
            "tenant": "lukhas-internal",
            "trace_id": trace_id,
            "consent_scopes": ["internal-system-analysis"],
            "policy_version": "v1.0.0",
        },
        "links": [],
        # Evidence provides verifiable artifacts related to the node's creation.
        "evidence": [
            {
                "kind": "artifact",
                "uri": f"glyph:{glyph}",
                "hash": hashlib.sha256(f"glyph:{glyph}".encode()).hexdigest(),
            }
        ],
        "schema_ref": "lukhas://schemas/matriz_node_v1.json",
    }

    # Convert relationships in the SymbolicWorld to MΛTRIZ links.
    for symbol_name, relationships in symbolic_world.relationships.items():
        for rel in relationships:
            # Avoid duplicating links since they are stored for both symbols in the world.
            if rel.symbol1.name == symbol_name:
                matriz_node["links"].append(
                    {
                        "target_node_id": f"symbol:{rel.symbol2.name}",  # Placeholder ID for the target symbol.
                        "link_type": "semantic",  # Mapping can be refined based on rel.type.
                        "direction": ("bidirectional" if rel.is_bidirectional() else "unidirectional"),
                        "explanation": f"Relationship of type '{rel.type}'",
                    }
                )

    return matriz_node


if __name__ == "__main__":
    # This block serves as a demonstration of how to use the bridge function.
    print("--- Symbolic Communication to MΛTRIZ Node Bridge Demonstration ---")

    # 1. Create an example SymbolicWorld instance
    print("\n[1] Creating an example SymbolicWorld...")
    world = SymbolicWorld()
    s1 = world.create_symbol("concept:consciousness", {"type": "abstract", "domain": "philosophy"})
    s2 = world.create_symbol("concept:machine", {"type": "concrete", "domain": "engineering"})
    s3 = world.create_symbol("property:sentience", {"type": "attribute", "domain": "philosophy"})
    world.link_symbols(s1, s2, "potential_host_of")
    world.link_symbols(s1, s3, "has_property")
    print(f"    - World created with {len(world.symbols)} symbols and {len(world.relationships)} relationships.")

    # 2. Call the bridge function to generate a MΛTRIZ node
    print("\n[2] Calling the bridge function...")
    matriz_node = create_matriz_node_from_symbolic_world(world)
    print("    - MΛTRIZ node created successfully.")

    # 3. Print the resulting MΛTRIZ node
    print("\n[3] Resulting MΛTRIZ Node (pretty-printed):")
    print(json.dumps(matriz_node, indent=2))

    print("\n--- Demonstration Complete ---")