#!/usr/bin/env python3
"""Test MCP server minimal format compliance"""

import json

import requests


def test_mcp_server():
    url = "http://localhost:8766/mcp"
    headers = {"Content-Type": "application/json"}

    # Test search tool
    search_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {"query": "test"}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=search_payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        # Check if response has the minimal format
        result = response.json().get('result', {})
        content = result.get('content', [])
        if content and content[0].get('type') == 'text':
            text_content = json.loads(content[0]['text'])
            if 'hits' in text_content:
                print("✅ Minimal format detected - has 'hits' array")
                return True
            else:
                print("❌ Missing 'hits' array in response")
                return False
        else:
            print("❌ No text content found")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_mcp_server()
