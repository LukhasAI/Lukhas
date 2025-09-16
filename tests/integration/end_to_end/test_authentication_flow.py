# owner: Jules-09
# tier: tier2
# module_uid: integration.end_to_end.authentication_flow
# criticality: P1

import os

import pytest
import requests

# Assuming the API is running on localhost:8000
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# NOTE: This test assumes a user with user_id 'test_user' and password 'test_password'
# exists in the system. This should be handled by a seeding mechanism in a real
# test environment.

@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.e2e
def test_full_authentication_flow():
    """
    Test complete user authentication journey:
    login -> get_token -> access_protected_resource
    """
    # Step 1: Login and get token
    login_data = {
        "user_id": "test_user",
        "password": "test_password"
    }

    login_url = f"{BASE_URL}/api/v2/auth/login"

    try:
        response = requests.post(login_url, json=login_data)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

        response_json = response.json()
        assert "access_token" in response_json, "Response JSON does not contain 'access_token'"
        access_token = response_json["access_token"]

        # Step 2: Use the token to access a protected resource
        protected_url = f"{BASE_URL}/api/v2/consciousness/query"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        consciousness_query_data = {
            "query": "What is the meaning of life?",
            "awareness_level": 0.8,
            "include_emotional_context": True
        }

        protected_response = requests.post(protected_url, headers=headers, json=consciousness_query_data)

        assert protected_response.status_code == 200, f"Expected status code 200, but got {protected_response.status_code}. Response: {protected_response.text}"

        protected_response_json = protected_response.json()
        assert protected_response_json["status"] == "success", "The status of the protected resource response was not 'success'"

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to the API failed: {e}. Make sure the API is running at {BASE_URL}.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
