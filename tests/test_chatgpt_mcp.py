#!/usr/bin/env python3
"""Test ChatGPT MCP requirements - 5 critical tests"""

import json
import time

import requests


def test_chatgpt_mcp_requirements():
    """Run the 5 critical tests for ChatGPT MCP compatibility"""
    base_url = "http://localhost:8766/mcp"
    headers = {"Content-Type": "application/json"}

    print("🧪 Testing ChatGPT MCP Requirements")
    print("=" * 50)

    # Test 1: Initialize must be quick
    print("\n1️⃣ Testing initialize method...")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "clientInfo": {"name": "dbg", "version": "1.0"},
            "capabilities": {"lukhas.tools": {}}
        }
    }

    try:
        start_time = time.time()
        response = requests.post(base_url, headers=headers, json=init_payload, timeout=5)
        duration = time.time() - start_time

        if response.status_code == 200:
            result = response.json().get('result', {})
            server_info = result.get('serverInfo', {})
            print(f"✅ Initialize successful ({duration:.3f}s)")
            print(f"   Server: {server_info.get('name', 'Unknown')}")
            print(f"   Version: {server_info.get('version', 'Unknown')}")
        else:
            print(f"❌ Initialize failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Initialize error: {e}")
        return False

    # Test 2: Tools/list must show both names
    print("\n2️⃣ Testing tools/list method...")
    tools_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    try:
        response = requests.post(base_url, headers=headers, json=tools_payload, timeout=5)
        if response.status_code == 200:
            result = response.json().get('result', {})
            tools = result.get('lukhas.tools', [])
            tool_names = [tool.get('name') for tool in tools]

            if 'search' in tool_names and 'fetch' in tool_names:
                print(f"✅ Tools found: {tool_names[:6]}...")  # Show first 6
                print("   Required tools: search ✅, fetch ✅")
            else:
                print(f"❌ Missing required tools. Found: {tool_names}")
                return False
        else:
            print(f"❌ Tools/list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools/list error: {e}")
        return False

    # Test 3: Fetch schema must contain required 'id'
    print("\n3️⃣ Testing fetch tool schema...")
    try:
        fetch_tool = None
        for tool in tools:
            if tool.get('name') == 'fetch':
                fetch_tool = tool
                break

        if fetch_tool:
            input_schema = fetch_tool.get('inputSchema', {})
            properties = input_schema.get('properties', {})
            required = input_schema.get('required', [])

            has_id = 'id' in properties
            id_required = 'id' in required

            print("✅ Fetch tool schema analysis:")
            print(f"   hasId: {has_id}")
            print(f"   required: {required}")
            print(f"   id in required: {id_required}")

            if not (has_id and id_required):
                print("❌ Fetch tool missing required 'id' parameter!")
                return False
        else:
            print("❌ Fetch tool not found!")
            return False
    except Exception as e:
        print(f"❌ Schema analysis error: {e}")
        return False

    # Test 4: Search should return ids (plus optional hits)
    print("\n4️⃣ Testing search returns IDs...")
    search_payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {
                "query": "lukhas",
                "limit": 2,
                "recency_days": 30  # Extra arg to test permissive handling
            }
        }
    }

    try:
        response = requests.post(base_url, headers=headers, json=search_payload, timeout=5)
        if response.status_code == 200:
            result = response.json().get('result', {})
            content = result.get('content', [])
            if content and content[0].get('type') == 'text':
                search_result = json.loads(content[0]['text'])

                has_ids = 'ids' in search_result
                has_hits = 'hits' in search_result
                ids = search_result.get('ids', [])

                print("✅ Search result analysis:")
                print(f"   Has IDs: {has_ids}")
                print(f"   Has hits: {has_hits}")
                print(f"   ID count: {len(ids)}")
                print(f"   Sample IDs: {ids[:2] if ids else 'None'}")

                if not (has_ids and ids):
                    print("❌ Search must return IDs for fetch!")
                    return False
            else:
                print("❌ Search returned invalid content format!")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

    # Test 5: Fetch should accept id and return the doc
    print("\n5️⃣ Testing fetch with ID...")
    if ids:
        test_id = ids[0]  # Use first ID from search
        fetch_payload = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"id": test_id}
            }
        }

        try:
            response = requests.post(base_url, headers=headers, json=fetch_payload, timeout=5)
            if response.status_code == 200:
                result = response.json().get('result', {})
                content = result.get('content', [])
                if content and content[0].get('type') == 'text':
                    fetch_result = json.loads(content[0]['text'])

                    required_fields = ['id', 'title', 'text']
                    has_all_fields = all(field in fetch_result for field in required_fields)

                    print("✅ Fetch result analysis:")
                    print(f"   ID: {fetch_result.get('id', 'Missing')}")
                    print(f"   Title: {fetch_result.get('title', 'Missing')[:50]}...")
                    print(f"   Has required fields: {has_all_fields}")
                    print(f"   Fields: {list(fetch_result.keys())}")

                    if not has_all_fields:
                        print(f"❌ Fetch missing required fields! Need: {required_fields}")
                        return False
                else:
                    print("❌ Fetch returned invalid content format!")
                    return False
            else:
                print(f"❌ Fetch failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Fetch error: {e}")
            return False
    else:
        print("❌ No IDs available for fetch test!")
        return False

    print("\n🎉 All ChatGPT MCP requirements PASSED!")
    print("✅ Ready to refresh ChatGPT connector - banner should disappear!")
    return True

if __name__ == "__main__":
    success = test_chatgpt_mcp_requirements()
    exit(0 if success else 1)
