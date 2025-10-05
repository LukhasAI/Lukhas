#!/usr/bin/env python3
"""Test MCP server fetch tool minimal format compliance"""

import requests
import json

def test_fetch_tool():
    url = "http://localhost:8766/mcp"
    headers = {"Content-Type": "application/json"}
    
    # Test fetch tool
    fetch_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "fetch",
            "arguments": {"url": "https://lukhas.ai/docs/test"}
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=fetch_payload, timeout=5)
        print(f"Status: {response.status_code}")
        result_json = response.json()
        print(f"Response: {json.dumps(result_json, indent=2)}")
        
        # Check if response has the minimal format
        result = result_json.get('result', {})
        content = result.get('content', [])
        if content and content[0].get('type') == 'text':
            text_content = json.loads(content[0]['text'])
            required_fields = ['title', 'url', 'mimeType', 'text']
            if all(field in text_content for field in required_fields):
                print("✅ Minimal fetch format detected - has all required fields")
                print(f"Fields: {list(text_content.keys())}")
                return True
            else:
                print(f"❌ Missing required fields. Has: {list(text_content.keys())}")
                return False
        else:
            print("❌ No text content found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_fetch_tool()