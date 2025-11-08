"""
Example usage of the Guardian API.
"""

import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.lukhas.ai/v1"

def get_safety_protocols():
    """
    Retrieves the current safety protocols from the Guardian API.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/guardian/safety/protocols", headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    protocols = get_safety_protocols()
    print(protocols)
