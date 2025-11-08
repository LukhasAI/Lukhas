"""
Example usage of the Identity API for authentication.
"""

import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.lukhas.ai/v1"

def get_token(username, password):
    """
    Retrieves an authentication token from the Identity API.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "username": username,
        "password": password,
    }
    response = requests.post(f"{BASE_URL}/identity/auth/token", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    token = get_token("testuser", "password123")
    print(token)
