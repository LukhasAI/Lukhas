#!/usr/bin/env python3
"""Test Perplexity API with minimal request."""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")
print(f"API Key: {api_key[:10]}...{api_key[-5:]}")

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, can you respond with just the word 'SUCCESS'?"
        }
    ]
}

print("Sending request...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        print("✅ Success!")
    else:
        print("❌ Failed")

except Exception as e:
    print(f"Exception: {e}")
