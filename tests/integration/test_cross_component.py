from matriz.core.memory_system import MemorySystem, MemoryType, MemoryQuery
from fastapi.testclient import TestClient
from serve.main import app
from labs.core.security.auth import get_auth_system
# import asyncio
# from core.orchestration.core import OrchestrationCore
# from labs.consciousness.awareness.awareness_engine import AwarenessEngine

def test_matriz_memory_workflow():
    """Tests the basic store and retrieve workflow of the MATRIZ MemorySystem."""
    memory_system = MemorySystem()

    # 1. Store a memory item
    content = {"question": "What is the capital of France?", "answer": "Paris"}
    memory_id = memory_system.store_memory(
        content=content,
        memory_type=MemoryType.EPISODIC,
        tags={"geography", "france"},
    )

    # 2. Retrieve the memory item
    query = MemoryQuery(query_text="France", memory_types=[MemoryType.EPISODIC])
    retrieved_memories = memory_system.retrieve_memories(query)

    # 3. Verify the retrieved memory
    assert len(retrieved_memories) == 1
    retrieved_memory = retrieved_memories[0]
    assert retrieved_memory.id == memory_id
    assert retrieved_memory.content == content

def test_identity_api_workflow():
    """Tests the authentication and authorization workflow of the Identity and API components."""
    client = TestClient(app)
    auth_system = get_auth_system()
    user_id = "test_user"

    # 1. Generate a JWT token
    token = auth_system.generate_jwt(user_id)

    # 2. Make an authenticated API request
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/v1/models", headers=headers)

    # 3. Verify the request was successful
    assert response.status_code == 200

    # 4. Make a request with an invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/v1/models", headers=headers)

    # 5. Verify the request was unauthorized
    assert response.status_code == 401

# def test_orchestration_consciousness_workflow():
#     """Tests the interaction between the Orchestration and Consciousness components."""
#     orchestration_core = OrchestrationCore()

#     # 1. Initialize the OrchestrationCore
#     asyncio.run(orchestration_core.initialize())

#     # 2. Verify that the AwarenessEngine was initialized
#     assert isinstance(orchestration_core.awareness_system, AwarenessEngine)

#     # 3. Verify that the OrchestrationCore is running
#     assert orchestration_core.is_running is True
