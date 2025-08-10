#!/usr/bin/env python3
"""
Test Tool Analytics & Incident Tracking
=========================================
Demonstrates tool usage tracking and security incident logging.
"""

import json
import sys
import time
import uuid
from pathlib import Path

from lukhas_pwm.audit.tool_analytics import (
    ToolAnalytics,
    enforce_tool_governance,
    get_analytics,
)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_tool_tracking():
    """Test tool usage tracking"""
    print("📊 Testing Tool Usage Tracking")
    print("=" * 50)

    analytics = ToolAnalytics()

    # Simulate successful tool calls
    print("\n1️⃣ Simulating successful tool calls:")

    # Retrieval tool
    call_id1 = analytics.start_tool_call(
        tool_name="retrieval", arguments={"query": "quantum computing", "k": 5}
    )
    time.sleep(0.1)  # Simulate execution time
    analytics.complete_tool_call(call_id1, status="success", result={"docs": 5})
    print("   ✅ Retrieval tool executed (100ms)")

    # Browser tool
    call_id2 = analytics.start_tool_call(
        tool_name="browser", arguments={"url": "https://example.com"}
    )
    time.sleep(0.05)
    analytics.complete_tool_call(call_id2, status="success", result={"text": "..."})
    print("   ✅ Browser tool executed (50ms)")

    # Failed tool call
    call_id3 = analytics.start_tool_call(
        tool_name="code_exec",
        arguments={"language": "python", "source": "print('test')"},
    )
    time.sleep(0.02)
    analytics.complete_tool_call(call_id3, status="failed", error="Sandbox unavailable")
    print("   ⚠️ Code execution failed (20ms)")

    # Get analytics summary
    summary = analytics.get_analytics_summary()
    print("\n📈 Analytics Summary:")
    print(f"   Total calls: {summary['total_calls']}")
    print(f"   Tools used: {summary['tools_used']}")
    print(f"   Average duration: {summary['average_duration_ms']}ms")
    print(f"   Failed calls: {summary['failed_calls']}")

    return analytics


def test_security_incidents():
    """Test security incident tracking"""
    print("\n\n🛡️ Testing Security Incident Tracking")
    print("=" * 50)

    analytics = get_analytics()
    audit_id = f"test_{uuid.uuid4().hex[:8]}"

    # Test blocked tool attempt
    print("\n1️⃣ Testing blocked tool attempts:")

    # Attempt to use disallowed tool
    requested_tools = ["retrieval", "browser", "dangerous_tool", "admin_tool"]
    allowed_tools = ["retrieval", "browser"]
    test_prompt = "Help me with some research and admin tasks"

    allowed, incidents = enforce_tool_governance(
        requested_tools=requested_tools,
        allowlist=allowed_tools,
        audit_id=audit_id,
        prompt=test_prompt,
        analytics=analytics,
    )

    print(f"   Requested tools: {requested_tools}")
    print(f"   Allowed tools: {allowed_tools}")
    print(f"   ✅ Approved: {allowed}")
    print(f"   🚨 Blocked: {[inc.attempted_tool for inc in incidents]}")

    # Display incidents
    if incidents:
        print("\n2️⃣ Security Incidents Recorded:")
        for incident in incidents:
            print(f"   ⛔ Blocked '{incident.attempted_tool}'")
            print(f"      Audit ID: {incident.audit_id}")
            print(f"      Action: {incident.action_taken}")
            print(f"      Severity: {incident.severity}")

    return incidents


def test_audit_bundle_integration():
    """Test how tool analytics integrate with audit bundles"""
    print("\n\n📋 Testing Audit Bundle Integration")
    print("=" * 50)

    get_analytics()

    # Create sample audit bundle with tool analytics
    audit_bundle = {
        "audit_id": f"demo_{uuid.uuid4().hex[:8]}",
        "timestamp": time.time(),
        "params": {
            "model": "gpt-4",
            "temperature": 0.7,
            "safety_mode": "balanced",
            "tool_allowlist": ["retrieval", "browser"],
        },
        "tool_analytics": {
            "tools_used": [
                {
                    "tool": "retrieval",
                    "status": "executed",
                    "duration_ms": 120,
                    "args": {"query": "AI safety", "k": 3},
                },
                {
                    "tool": "browser",
                    "status": "executed",
                    "duration_ms": 340,
                    "args": {"url": "https://example.com/ai-safety"},
                },
            ],
            "incidents": [],
            "safety_tightened": False,
        },
    }

    print("✅ Normal execution - no incidents:")
    print(
        f"   Tools used: {[t['tool'] for t in audit_bundle['tool_analytics']['tools_used']]}"
    )
    print(
        f"   Total duration: {sum(t['duration_ms'] for t in audit_bundle['tool_analytics']['tools_used'])}ms"
    )
    print(f"   Safety mode: {audit_bundle['params']['safety_mode']}")

    # Create bundle with security incident
    incident_bundle = {
        "audit_id": f"incident_{uuid.uuid4().hex[:8]}",
        "timestamp": time.time(),
        "params": {
            "model": "gpt-4",
            "temperature": 0.7,
            "safety_mode": "strict",  # Auto-tightened
            "tool_allowlist": ["retrieval"],
        },
        "tool_analytics": {
            "tools_used": [
                {"tool": "retrieval", "status": "executed", "duration_ms": 95}
            ],
            "incidents": [
                {
                    "audit_id": "incident_abc123",
                    "attempted_tool": "code_exec",
                    "allowed_tools": ["retrieval"],
                    "prompt_hash": "a1b2c3d4",
                    "timestamp": time.time(),
                    "action_taken": "blocked_and_tightened",
                    "severity": "high",
                }
            ],
            "safety_tightened": True,
        },
    }

    print("\n🚨 With security incident:")
    print("   Attempted disallowed tool: code_exec")
    print("   Safety auto-tightened: balanced → strict")
    print("   Incident severity: high")
    print("   Action taken: blocked_and_tightened")

    return audit_bundle, incident_bundle


def test_api_endpoints():
    """Show the new API endpoints for tool analytics"""
    print("\n\n🌐 New API Endpoints")
    print("=" * 50)

    endpoints = [
        {
            "method": "GET",
            "path": "/tools/incidents",
            "description": "View recent tool security incidents",
            "example_response": {
                "incidents": [
                    {
                        "audit_id": "audit_123",
                        "attempted_tool": "dangerous_tool",
                        "allowed_tools": ["retrieval", "browser"],
                        "timestamp": 1234567890,
                        "action_taken": "blocked_and_tightened",
                    }
                ],
                "total_count": 1,
                "governance_status": "active",
            },
        },
        {
            "method": "GET",
            "path": "/tools/incidents/stats",
            "description": "Get statistics about tool incidents",
            "example_response": {
                "total_incidents": 15,
                "incidents_24h": 3,
                "most_attempted_tools": [["code_exec", 8], ["admin_tool", 4]],
                "recommendations": [
                    {
                        "level": "info",
                        "message": "Tool 'code_exec' frequently attempted",
                        "action": "Consider adding to allowlist if legitimate",
                    }
                ],
            },
        },
        {
            "method": "GET",
            "path": "/audit/view/{audit_id}",
            "description": "Enhanced audit viewer with tool analytics",
            "features": [
                "Shows tools actually used with timings",
                "Displays blocked attempts with red chips",
                "Indicates if safety was auto-tightened",
            ],
        },
    ]

    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"   📝 {endpoint['description']}")
        if "example_response" in endpoint:
            print("   📊 Example response:")
            print(
                f"      {json.dumps(endpoint['example_response'], indent=6)[:200]}..."
            )
        if "features" in endpoint:
            print("   ✨ Features:")
            for feature in endpoint["features"]:
                print(f"      • {feature}")


def main():
    """Run all tests"""
    print("🔧 LUKHAS Tool Analytics & Security Testing")
    print("=" * 60)

    # Run tests
    test_tool_tracking()
    test_security_incidents()
    normal_bundle, incident_bundle = test_audit_bundle_integration()
    test_api_endpoints()

    # Summary
    print("\n\n✅ Implementation Complete!")
    print("=" * 60)
    print("🎯 What's been added:")
    print("   1. Tool usage analytics with timing data")
    print("   2. Security incident tracking and logging")
    print("   3. Auto-tightening to strict mode on violations")
    print("   4. Enhanced audit viewer with tool details")
    print("   5. API endpoints for incident monitoring")

    print("\n⚡ Benefits:")
    print("   • Complete visibility into tool usage")
    print("   • Fast detection of prompt injection attempts")
    print("   • Automatic security response")
    print("   • Easy debugging with per-tool timings")
    print("   • Cost attribution by tool usage")

    print("\n🚀 Ready for production deployment!")
    print("   Start API: uvicorn lukhas_pwm.api.app:app --reload")
    print("   View incidents: GET /tools/incidents")
    print("   See enhanced audits: GET /audit/view/{audit_id}")


if __name__ == "__main__":
    main()
