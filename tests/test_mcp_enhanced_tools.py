#!/usr/bin/env python3
"""Test the new writeFile and createFile MCP tools"""

import requests
import json
import time

def test_enhanced_mcp_tools():
    """Test the new file editing capabilities"""
    base_url = "http://localhost:8766/mcp"
    headers = {"Content-Type": "application/json"}
    
    print("🧪 Testing Enhanced MCP Tools - File Editing Capabilities")
    print("=" * 60)
    
    # Test 1: Verify new tools are listed
    print("\n1️⃣ Testing enhanced tools list...")
    tools_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=tools_payload, timeout=5)
        if response.status_code == 200:
            result = response.json().get('result', {})
            tools = result.get('tools', [])
            tool_names = [tool.get('name') for tool in tools]
            
            required_tools = ['search', 'fetch', 'writeFile', 'createFile']
            missing_tools = [tool for tool in required_tools if tool not in tool_names]
            
            print(f"✅ Total tools: {len(tool_names)}")
            print(f"   Core tools: {tool_names[:4]}")
            print(f"   File tools: {[t for t in tool_names if t in ['writeFile', 'createFile']]}")
            
            if missing_tools:
                print(f"❌ Missing tools: {missing_tools}")
                return False
        else:
            print(f"❌ Tools/list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools/list error: {e}")
        return False
    
    # Test 2: Test createFile tool
    print("\n2️⃣ Testing createFile tool...")
    test_file_path = "test_mcp_file.py"
    test_content = '''"""Test file created by MCP writeFile tool"""

def hello_lukhas():
    print("Hello from LUKHAS MCP file creation!")
    return "success"

if __name__ == "__main__":
    hello_lukhas()
'''
    
    create_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "createFile",
            "arguments": {
                "path": test_file_path,
                "content": test_content,
                "template": "python"
            }
        }
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=create_payload, timeout=10)
        if response.status_code == 200:
            result = response.json().get('result', {})
            content = result.get('content', [])
            if content and content[0].get('type') == 'text':
                create_result = json.loads(content[0]['text'])
                
                if create_result.get('success'):
                    print(f"✅ File created successfully:")
                    print(f"   Path: {create_result.get('relativePath')}")
                    print(f"   Size: {create_result.get('size')} bytes")
                    print(f"   Template: {create_result.get('template')}")
                else:
                    print(f"❌ CreateFile failed: {create_result.get('error')}")
                    return False
            else:
                print("❌ CreateFile returned invalid format!")
                return False
        else:
            print(f"❌ CreateFile failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CreateFile error: {e}")
        return False
    
    # Test 3: Test writeFile tool (overwrite)
    print("\n3️⃣ Testing writeFile tool...")
    updated_content = '''"""Test file UPDATED by MCP writeFile tool"""

def hello_lukhas_updated():
    print("Hello from LUKHAS MCP file UPDATE!")
    print("This file was modified using the writeFile tool!")
    return "updated_success"

def new_function():
    return "This function was added via writeFile"

if __name__ == "__main__":
    hello_lukhas_updated()
    print(new_function())
'''
    
    write_payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "writeFile",
            "arguments": {
                "path": test_file_path,
                "content": updated_content,
                "overwrite": True
            }
        }
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=write_payload, timeout=10)
        if response.status_code == 200:
            result = response.json().get('result', {})
            content = result.get('content', [])
            if content and content[0].get('type') == 'text':
                write_result = json.loads(content[0]['text'])
                
                if write_result.get('success'):
                    print(f"✅ File updated successfully:")
                    print(f"   Path: {write_result.get('relativePath')}")
                    print(f"   Size: {write_result.get('size')} bytes") 
                    print(f"   Overwritten: {write_result.get('overwritten')}")
                else:
                    print(f"❌ WriteFile failed: {write_result.get('error')}")
                    return False
            else:
                print("❌ WriteFile returned invalid format!")
                return False
        else:
            print(f"❌ WriteFile failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ WriteFile error: {e}")
        return False
    
    # Test 4: Verify file was actually created
    print("\n4️⃣ Verifying file creation...")
    import os
    test_file_full_path = f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{test_file_path}"
    
    if os.path.exists(test_file_full_path):
        with open(test_file_full_path, 'r') as f:
            content = f.read()
        
        if "UPDATED by MCP writeFile tool" in content and "new_function" in content:
            print(f"✅ File verification successful:")
            print(f"   File exists at: {test_file_path}")
            print(f"   Content length: {len(content)} chars")
            print(f"   Contains updates: ✅")
        else:
            print(f"❌ File content verification failed!")
            return False
    else:
        print(f"❌ File not found at: {test_file_full_path}")
        return False
    
    print("\n🎉 All Enhanced MCP Tools PASSED!")
    print("✅ ChatGPT can now create and edit files in your LUKHAS repo!")
    print("🔧 Available operations: search, fetch, writeFile, createFile")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_mcp_tools()
    exit(0 if success else 1)