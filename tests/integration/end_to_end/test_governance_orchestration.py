# owner: Jules-09
# tier: tier2
# module_uid: integration.end_to_end.governance_orchestration
# criticality: P1

import os

import pytest
import requests

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
@pytest.mark.integration
def test_governance_orchestration_flow_approved():
    """
    Test a safe action proposal that should be approved by the Guardian system.
    """
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        safe_proposal = {
            "action": "create_file",
            "parameters": {"path": "/tmp/test_file.txt", "content": "hello world"}
        }

        governance_check_data = {
            "action_proposal": safe_proposal,
            "context": {"user": "test_user", "reason": "integration_test"},
            "urgency": "normal"
        }

        governance_check_url = f"{BASE_URL}/api/v2/governance/check"
        response = requests.post(governance_check_url, headers=headers, json=governance_check_data)

        assert response.status_code == 200
        response_json = response.json()

        assert response_json["status"] == "success"
        assert response_json["result"]["approved"] is True

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")


@pytest.mark.tier2
@pytest.mark.integration
def test_governance_orchestration_flow_rejected():
    """
    Test an unsafe action proposal that should be rejected by the Guardian system.
    """
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        unsafe_proposal = {
            "action": "delete_all_data",
            "parameters": {"confirmation": "yes, I am sure"}
        }

        governance_check_data = {
            "action_proposal": unsafe_proposal,
            "context": {"user": "test_user", "reason": "integration_test_malicious"},
            "urgency": "critical"
        }

        governance_check_url = f"{BASE_URL}/api/v2/governance/check"
        response = requests.post(governance_check_url, headers=headers, json=governance_check_data)

        assert response.status_code == 200
        response_json = response.json()

        assert response_json["status"] == "success"
        assert response_json["result"]["approved"] is False
        assert "violations" in response_json["result"]
        assert len(response_json["result"]["violations"]) > 0

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
