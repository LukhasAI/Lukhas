import asyncio
import os
import uuid

from memory.systems.helix_dna import HelixMemory


def test_hybrid_memory_storage():
    # Setup
    decision_id = f"decision_{uuid.uuid4().hex[:10]}"
    decision_data = {"action": "test", "parameters": {"param1": "value1"}}
    context = {"user_id": "test_user"}
    unstructured_memory = "This is a test of unstructured memory."

    # Action
    helix_memory = HelixMemory()
    asyncio.run(
        helix_memory.store_decision(
            decision_data, context, decision_id, unstructured_memory
        )
    )
    retrieved_decision = asyncio.run(helix_memory.retrieve_decision(decision_id))

    # Assert
    assert retrieved_decision is not None
    assert retrieved_decision["decision"] == decision_data
    assert retrieved_decision["context"] == context
    assert retrieved_decision["unstructured_memory"] == unstructured_memory

    # Teardown
    os.remove("helix_memory.key")
    os.remove("helix_memory_store.jsonl")
