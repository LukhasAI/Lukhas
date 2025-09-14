# owner: Jules-09
# tier: tier2
# module_uid: integration.end_to_end.decision_pipeline
# criticality: P1

import pytest
import requests
import os

# Assuming the API is running on localhost:8000
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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
@pytest.mark.e2e
def test_ai_decision_making_pipeline():
    """
    AI decision-making from input to action:
    input_processing -> consciousness_evaluation -> memory_consultation -> decision_generation -> action_execution
    """
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1: Input Processing (Symbolic Encoding)
        input_data = "This is a test input for the decision pipeline."
        process_url = f"{BASE_URL}/api/v2/process"

        encode_request = {
            "operation": "symbolic.encode",
            "data": {"text": input_data}
        }
        encode_response = requests.post(process_url, headers=headers, json=encode_request)
        assert encode_response.status_code == 200
        encoded_data = encode_response.json()["result"]
        assert "glyphs" in encoded_data

        # Step 2: Consciousness Evaluation
        consciousness_request = {
            "operation": "consciousness.query",
            "data": {
                "query": f"Evaluate the following symbols: {encoded_data['glyphs']}",
                "awareness_level": 0.9
            }
        }
        consciousness_response = requests.post(process_url, headers=headers, json=consciousness_request)
        assert consciousness_response.status_code == 200
        consciousness_result = consciousness_response.json()["result"]
        assert "consciousness" in consciousness_result

        # Step 3: Memory Consultation
        memory_request = {
            "operation": "memory.search",
            "data": {
                "query": f"Find related memories for: {consciousness_result['consciousness']}",
                "memory_type": "decision_making"
            }
        }
        memory_response = requests.post(process_url, headers=headers, json=memory_request)
        assert memory_response.status_code == 200
        memory_result = memory_response.json()["result"]
        assert "results" in memory_result

        # Step 4: Decision Generation (Symbolic Analysis)
        analysis_request = {
            "operation": "symbolic.analyze",
            "data": {"content": f"{consciousness_result['consciousness']} {memory_result['results']}"}
        }
        analysis_response = requests.post(process_url, headers=headers, json=analysis_request)
        assert analysis_response.status_code == 200
        decision_data = analysis_response.json()["result"]
        assert "analysis" in decision_data

        # Step 5: Action Execution (Coordination)
        action_request = {
            "operation": "coordination.orchestrate",
            "data": {
                "task": {
                    "name": "execute_decision",
                    "decision": decision_data["analysis"]
                }
            }
        }
        action_response = requests.post(process_url, headers=headers, json=action_request)
        assert action_response.status_code == 200
        action_result = action_response.json()["result"]
        assert action_result["status"] == "coordinated"

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
