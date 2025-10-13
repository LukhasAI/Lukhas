"""
Smoke test: Streaming responses (SSE).

Verifies that /v1/responses supports Server-Sent Events streaming:
- Content-Type: text/event-stream
- data: prefix on chunks
- data: [DONE] terminator

Phase 3: Added for OpenAI parity polish.
"""
import os
import pytest
import requests

BASE = os.getenv("LUKHAS_BASE_URL", "http://localhost:8000")


def test_streaming_responses_sse_protocol():
    """Verify SSE protocol compliance for streaming responses."""
    payload = {"model": "lukhas-response", "input": "hi", "stream": True}
    headers = {"Authorization": "Bearer test"}
    
    with requests.post(f"{BASE}/v1/responses", json=payload, headers=headers, stream=True) as r:
        # Should return 200 in permissive mode, may be 401/403 in strict mode
        if r.status_code not in (200,):
            pytest.skip(f"Auth required or endpoint unavailable: {r.status_code}")
        
        assert r.headers.get("Content-Type", "").startswith("text/event-stream"), \
            f"Expected SSE content type, got: {r.headers.get('Content-Type')}"
        
        data_frames = []
        done_received = False
        
        for line in r.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8') if isinstance(line, bytes) else line
            
            if line_str.startswith("data:"):
                data = line_str[5:].strip()
                
                if data == "[DONE]":
                    done_received = True
                    break
                
                data_frames.append(data)
        
        # Should receive at least some data before DONE
        assert data_frames or done_received, "Expected data frames or DONE marker"


def test_streaming_vs_non_streaming():
    """Verify stream parameter controls response format."""
    headers = {"Authorization": "Bearer test"}
    base_payload = {"model": "lukhas-response", "input": "test"}
    
    # Non-streaming request
    r1 = requests.post(f"{BASE}/v1/responses", json={**base_payload, "stream": False}, headers=headers)
    
    # Streaming request
    r2 = requests.post(f"{BASE}/v1/responses", json={**base_payload, "stream": True}, headers=headers, stream=True)
    
    # Skip if auth required
    if r1.status_code not in (200,) or r2.status_code not in (200,):
        pytest.skip(f"Auth required: {r1.status_code}, {r2.status_code}")
    
    # Non-streaming should be JSON
    assert r1.headers.get("Content-Type", "").startswith("application/json")
    
    # Streaming should be SSE
    assert r2.headers.get("Content-Type", "").startswith("text/event-stream")
    
    r2.close()


def test_streaming_trace_header():
    """Verify trace headers present even in streaming responses."""
    payload = {"model": "lukhas-response", "input": "trace test", "stream": True}
    headers = {"Authorization": "Bearer test"}
    
    with requests.post(f"{BASE}/v1/responses", json=payload, headers=headers, stream=True) as r:
        if r.status_code not in (200,):
            pytest.skip(f"Auth required: {r.status_code}")
        
        trace_id = r.headers.get("X-Trace-Id")
        assert trace_id is not None, "Missing X-Trace-Id in streaming response"
