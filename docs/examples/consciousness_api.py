"""
Example usage of the Consciousness Chat API.
"""

import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.lukhas.ai/v1"

def chat(message, session_id=None, user_id=None):
    """
    Sends a message to the Consciousness Chat API.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "message": message,
        "session_id": session_id,
        "user_id": user_id,
    }
    response = requests.post(f"{BASE_URL}/chat", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    response = chat("Hello, LUKHAS!")
    print(response)
