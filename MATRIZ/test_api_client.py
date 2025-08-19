#!/usr/bin/env python3
"""
MATADA-AGI API Client Test
Test client to verify the FastAPI server functionality
"""

import asyncio
import json
import requests
import websockets
from typing import Dict, Any

class MatadaAPIClient:
    """Simple client for testing the MATADA-AGI API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def query(self, query_text: str, include_trace: bool = True, include_nodes: bool = True) -> Dict[str, Any]:
        """Send query to the API"""
        try:
            payload = {
                "query": query_text,
                "include_trace": include_trace,
                "include_nodes": include_nodes
            }
            response = requests.post(f"{self.base_url}/query", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            response = requests.get(f"{self.base_url}/system/info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_nodes(self) -> Dict[str, Any]:
        """List available cognitive nodes"""
        try:
            response = requests.get(f"{self.base_url}/system/nodes")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def websocket_test(self) -> Dict[str, Any]:
        """Test WebSocket connection"""
        try:
            ws_url = self.base_url.replace("http://", "ws://") + "/ws"
            async with websockets.connect(ws_url) as websocket:
                # Send ping
                await websocket.send(json.dumps({
                    "type": "ping",
                    "data": {"test": "ping"},
                    "timestamp": "2024-01-01T00:00:00"
                }))
                
                # Receive pong
                response = await websocket.recv()
                pong = json.loads(response)
                
                # Send query
                await websocket.send(json.dumps({
                    "type": "query",
                    "data": {"query": "What is 5 + 3?"},
                    "timestamp": "2024-01-01T00:00:00"
                }))
                
                # Receive query response
                response = await websocket.recv()
                query_result = json.loads(response)
                
                return {
                    "pong": pong,
                    "query_result": query_result
                }
        except Exception as e:
            return {"error": str(e)}

def main():
    """Run comprehensive API tests"""
    print("🧪 MATADA-AGI API Client Test")
    print("=" * 50)
    
    client = MatadaAPIClient()
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    health = client.health_check()
    if "error" in health:
        print(f"❌ Health check failed: {health['error']}")
        print("💡 Make sure the API server is running: python run_api_server.py")
        return
    else:
        print(f"✅ API is healthy - Status: {health['status']}")
        print(f"   Registered nodes: {health['registered_nodes']}")
        print(f"   Uptime: {health['uptime_seconds']:.1f}s")
    
    # Test 2: System Information
    print("\n2️⃣ Testing System Information...")
    system_info = client.get_system_info()
    if "error" in system_info:
        print(f"❌ System info failed: {system_info['error']}")
    else:
        print(f"✅ System info retrieved")
        print(f"   Nodes: {len(system_info['nodes'])}")
        print(f"   MATADA graph size: {system_info['matada_graph_size']}")
        for node in system_info['nodes']:
            print(f"   - {node['name']}: {', '.join(node['capabilities'][:2])}...")
    
    # Test 3: List Nodes
    print("\n3️⃣ Testing Node Listing...")
    nodes = client.list_nodes()
    if "error" in nodes:
        print(f"❌ Node listing failed: {nodes['error']}")
    else:
        print(f"✅ Node listing retrieved")
        for name, info in nodes['nodes'].items():
            print(f"   - {name} ({info['class']}): {info['processing_history_count']} processed")
    
    # Test 4: Mathematical Query
    print("\n4️⃣ Testing Mathematical Query...")
    math_result = client.query("What is 15 + 27?")
    if "error" in math_result:
        print(f"❌ Math query failed: {math_result['error']}")
    else:
        print(f"✅ Math query successful")
        print(f"   Answer: {math_result['answer']}")
        print(f"   Confidence: {math_result['confidence']:.3f}")
        print(f"   Processing time: {math_result['processing_time']:.3f}s")
        if math_result.get('matada_nodes'):
            print(f"   MATADA nodes created: {len(math_result['matada_nodes'])}")
    
    # Test 5: Factual Query
    print("\n5️⃣ Testing Factual Query...")
    fact_result = client.query("What is the capital of Japan?")
    if "error" in fact_result:
        print(f"❌ Fact query failed: {fact_result['error']}")
    else:
        print(f"✅ Fact query successful")
        print(f"   Answer: {fact_result['answer']}")
        print(f"   Confidence: {fact_result['confidence']:.3f}")
        print(f"   Processing time: {fact_result['processing_time']:.3f}s")
    
    # Test 6: Unknown Query
    print("\n6️⃣ Testing Unknown Query...")
    unknown_result = client.query("What is the meaning of purple elephants?")
    if "error" in unknown_result:
        print(f"❌ Unknown query failed: {unknown_result['error']}")
    else:
        print(f"✅ Unknown query handled")
        print(f"   Answer: {unknown_result['answer']}")
        print(f"   Confidence: {unknown_result['confidence']:.3f}")
    
    # Test 7: WebSocket Connection
    print("\n7️⃣ Testing WebSocket Connection...")
    try:
        ws_result = asyncio.run(client.websocket_test())
        if "error" in ws_result:
            print(f"❌ WebSocket test failed: {ws_result['error']}")
        else:
            print(f"✅ WebSocket connection successful")
            print(f"   Pong received: {ws_result['pong']['type']}")
            query_result = ws_result['query_result']
            if query_result.get('type') == 'response':
                answer = query_result['data']['answer']
                confidence = query_result['data']['confidence']
                print(f"   Query result: {answer} (confidence: {confidence:.3f})")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Test Completed!")
    print("\n💡 You can explore the API interactively at:")
    print(f"   📖 Swagger UI: {client.base_url}/docs")
    print(f"   📋 ReDoc: {client.base_url}/redoc")

if __name__ == "__main__":
    main()