"""
Example usage of the Consciousness API for memory management.
"""

import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.lukhas.ai/v1"

def query_memory(query):
    """
    Sends a query to the memory system.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"query": query}
    response = requests.post(f"{BASE_URL}/consciousness/memory/query", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    results = query_memory("What is the nature of reality?")
    print(results)
