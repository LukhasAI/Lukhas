# owner: Jules-09
# tier: tier2
# module_uid: integration.end_to_end.multi_component_workflows
# criticality: P1

import pytest
import requests
import os

# Assuming the API is running on localhost:8000
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# NOTE: This test assumes that a complex workflow can be executed by chaining
# calls to the /api/v2/process endpoint. It also makes assumptions about the
# input and output formats of the different services. These should be verified.

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
@pytest.mark.e2e
def test_multi_component_workflows():
    """
    Complex workflows involving multiple components:
    workflow_initiation -> component_coordination -> state_synchronization -> result_aggregation
    """
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        # Define a workflow as a sequence of operations
        workflow_steps = [
            {
                "operation": "consciousness.query",
                "data": {"query": "What is the capital of France?"}
            },
            {
                "operation": "memory.store",
                "data": {"content": {"key": "capital_of_france", "data": "Paris"}, "memory_type": "facts"}
            },
            {
                "operation": "governance.check",
                "data": {"action_proposal": {"action": "share_fact", "fact": "capital_of_france"}}
            }
        ]

        # Execute the workflow
        results = {}
        for i, step in enumerate(workflow_steps):
            process_url = f"{BASE_URL}/api/v2/process"

            # Use the result of the previous step if needed
            if i > 0 and "share_fact" in step["data"].get("action_proposal", {}).get("fact", ""):
                step["data"]["action_proposal"]["fact"] = results[i-1]

            response = requests.post(process_url, headers=headers, json=step)
            assert response.status_code == 200

            response_json = response.json()
            assert response_json["status"] == "success"

            results[i] = response_json["result"]

        # Final assertion
        assert results[2]["approved"] == True

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
