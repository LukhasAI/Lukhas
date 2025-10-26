# owner: Jules-09
# tier: tier2
# module_uid: integration.end_to_end.consciousness_memory
# criticality: P1

import os
import uuid

import pytest
import requests

# Assuming the API is running on localhost:8000
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# NOTE: This test makes assumptions about the data structure of the
# consciousness and memory services. It also assumes that the 'store'
# operation for memory uses a 'key' to identify the data for later retrieval.
# These assumptions should be verified against the actual implementation.

def get_access_token():
    """Helper function to get an access token."""
    login_data = {
        "user_id": "test_user",
        "password": "test_password"
    }
    login_url = f"{BASE_URL}/api/v2/auth/login"
    response = requests.post(login_url, json=login_data)
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.mark.tier2
@pytest.mark.integration
def test_consciousness_memory_integration():
    """
    Test consciousness state persistence in memory:
    consciousness_state -> memory_storage -> state_retrieval -> consciousness_restoration
    """
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        # 1. Get a consciousness state
        consciousness_query_data = {
            "query": "Generate a unique consciousness state for integration testing.",
            "awareness_level": 0.9,
            "include_emotional_context": True
        }
        consciousness_url = f"{BASE_URL}/api/v2/consciousness/query"
        consciousness_response = requests.post(consciousness_url, headers=headers, json=consciousness_query_data)
        assert consciousness_response.status_code == 200
        consciousness_state = consciousness_response.json()["result"]
        assert "consciousness" in consciousness_state

        # 2. Store the consciousness state in memory
        memory_key = f"consciousness_state_{uuid.uuid4()}"
        store_data = {
            "action": "store",
            "content": {"key": memory_key, "data": consciousness_state},
            "memory_type": "consciousness_integration"
        }
        memory_store_url = f"{BASE_URL}/api/v2/memory/store"
        store_response = requests.post(memory_store_url, headers=headers, json=store_data)
        assert store_response.status_code == 200
        store_result = store_response.json()["result"]
        assert store_result.get("stored") is True

        # 3. Retrieve the consciousness state from memory
        retrieve_data = {
            "action": "retrieve",
            "query": memory_key,
            "memory_type": "consciousness_integration"
        }
        memory_retrieve_url = f"{BASE_URL}/api/v2/memory/retrieve"
        retrieve_response = requests.post(memory_retrieve_url, headers=headers, json=retrieve_data)
        assert retrieve_response.status_code == 200
        retrieved_state_data = retrieve_response.json()["result"]

        # 4. Compare the original and retrieved states
        assert retrieved_state_data is not None, "Retrieved data is None"
        retrieved_state = retrieved_state_data.get("data")
        assert consciousness_state == retrieved_state, "Original and retrieved consciousness states do not match"

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
