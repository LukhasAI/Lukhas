#!/usr/bin/env python3
"""
🔧 LUKHAS Tool Governance Demo
=============================
Demonstration of the complete OpenAI tool integration with LUKHAS safety governance.

Shows:
- Tool allowlist enforcement  
- Safety mode badges in audit viewer
- Complete audit trail with tool information
- API endpoints for tool registry
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lukhas_pwm.openai.tooling import get_all_tools, get_tool_names, build_tools_from_allowlist
from orchestration.signals.homeostasis import ModulationParams


def demo_tool_registry():
    """Demonstrate the tool registry functionality"""
    print("🔧 TOOL REGISTRY DEMO")
    print("=" * 50)
    
    # Show all available tools
    all_tools = get_all_tools()
    tool_names = get_tool_names()
    
    print(f"📋 Available tools ({len(tool_names)}):")
    for name in tool_names:
        tool = all_tools[name]
        func_info = tool["function"]
        print(f"  • {name}: {func_info['description']}")
    
    print(f"\n🔧 Tool schemas ready for OpenAI function calling")
    
    # Demo allowlist filtering
    test_allowlist = ["retrieval", "browser"]
    filtered_tools = build_tools_from_allowlist(test_allowlist)
    
    print(f"\n🛡️ Allowlist Demo - Only allowing: {test_allowlist}")
    print(f"   Filtered to {len(filtered_tools)} tools:")
    for tool in filtered_tools:
        print(f"   • {tool['function']['name']}")


def demo_safety_modes():
    """Demonstrate different safety modes with tool allowlists"""
    print("\n\n🛡️ SAFETY MODES DEMO")
    print("=" * 50)
    
    safety_configs = {
        "strict": {
            "temperature": 0.1,
            "tool_allowlist": ["retrieval"],
            "description": "🔴 Maximum safety - minimal tools, low temperature"
        },
        "balanced": {
            "temperature": 0.7,
            "tool_allowlist": ["retrieval", "browser"],
            "description": "🟢 Balanced mode - moderate tools and settings"
        },
        "creative": {
            "temperature": 0.9,
            "tool_allowlist": ["retrieval", "browser", "scheduler", "code_exec"],
            "description": "🔵 Creative mode - all tools available, high temperature"
        }
    }
    
    for mode, config in safety_configs.items():
        print(f"\n{config['description']}")
        
        params = ModulationParams(
            temperature=config["temperature"],
            safety_mode=mode,
            tool_allowlist=config["tool_allowlist"]
        )
        
        print(f"   Temperature: {params.temperature}")
        print(f"   Tools allowed: {params.tool_allowlist}")
        print(f"   Guardian validation: {'Enhanced' if mode == 'strict' else 'Standard'}")


def demo_audit_bundle():
    """Show what an audit bundle looks like with tool governance"""
    print("\n\n📋 AUDIT BUNDLE DEMO")
    print("=" * 50)
    
    # Create sample audit bundle
    audit_id = f"demo_{uuid.uuid4().hex[:8]}"
    
    sample_bundle = {
        "audit_id": audit_id,
        "timestamp": datetime.now().isoformat(),
        "params": {
            "model": "gpt-4",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 500,
            "safety_mode": "balanced",
            "tool_allowlist": ["retrieval", "browser"],
            "retrieval_k": 3
        },
        "signals": {
            "stress": 0.2,
            "novelty": 0.6,
            "alignment_risk": 0.1
        },
        "guardian": {
            "pre_validation": "APPROVED",
            "post_validation": "APPROVED",
            "ethical_score": 0.95
        },
        "explanation": "User requested research assistance with web browsing capability",
        "prompt": "Help me research the latest developments in quantum computing",
        "response": "I'll help you research quantum computing developments using web search...",
        "tools_used": ["retrieval", "browser"],
        "tool_calls": [
            {
                "tool": "retrieval",
                "query": "quantum computing latest developments 2025",
                "results_count": 3
            },
            {
                "tool": "browser", 
                "url": "https://example.com/quantum-news",
                "status": "success"
            }
        ]
    }
    
    print(f"📦 Sample Audit Bundle: {audit_id}")
    print(f"🛡️ Safety Mode: {sample_bundle['params']['safety_mode'].upper()}")
    print(f"🔧 Tools Available: {sample_bundle['params']['tool_allowlist']}")
    print(f"✅ Tools Actually Used: {sample_bundle['tools_used']}")
    print(f"🎯 Guardian Status: {sample_bundle['guardian']['pre_validation']}")
    
    # Show JSON structure
    print(f"\n📄 Complete Bundle Structure:")
    print(json.dumps(sample_bundle, indent=2)[:500] + "...")
    
    print(f"\n🔗 Audit Viewer URL: http://127.0.0.1:8000/audit/view/{audit_id}")
    print("   (Shows safety badge + tool list + complete trace)")


def demo_api_endpoints():
    """Show the available API endpoints"""
    print("\n\n🌐 API ENDPOINTS DEMO")
    print("=" * 50)
    
    endpoints = [
        {
            "method": "GET",
            "path": "/tools/registry",
            "description": "Complete tool registry with schemas",
            "example": "curl http://127.0.0.1:8000/tools/registry"
        },
        {
            "method": "GET", 
            "path": "/tools/available",
            "description": "List of available tool names",
            "example": "curl http://127.0.0.1:8000/tools/available"
        },
        {
            "method": "GET",
            "path": "/tools/{tool_name}",
            "description": "Schema for specific tool",
            "example": "curl http://127.0.0.1:8000/tools/retrieval"
        },
        {
            "method": "POST",
            "path": "/audit/log",
            "description": "Log audit bundle with tool usage",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{bundle}' http://127.0.0.1:8000/audit/log"
        },
        {
            "method": "GET",
            "path": "/audit/view/{audit_id}",
            "description": "View audit with safety badges",
            "example": "Open in browser: http://127.0.0.1:8000/audit/view/demo_12345678"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"   📝 {endpoint['description']}")
        print(f"   💻 {endpoint['example']}")


def main():
    """Run the complete demonstration"""
    print("🌟 LUKHAS OpenAI Tool Governance - Complete Demo")
    print("=" * 60)
    print("Showcasing production-ready tool safety and auditability")
    
    demo_tool_registry()
    demo_safety_modes()
    demo_audit_bundle()
    demo_api_endpoints()
    
    print("\n\n🎉 INTEGRATION COMPLETE!")
    print("=" * 60)
    print("✅ Tool allowlist enforcement implemented")
    print("✅ Safety mode badges with detailed tooltips")
    print("✅ Complete audit trail with tool governance")
    print("✅ API endpoints for tool registry management")
    print("✅ Production-ready OpenAI function calling integration")
    
    print("\n🚀 Ready for deployment!")
    print("   1. Start API server: uvicorn lukhas_pwm.api.app:app --reload")
    print("   2. Test with OpenAI API key in environment")
    print("   3. All tool usage will be governed and auditable")
    
    print("\n⚡ This completes the safety-first tool governance system!")


if __name__ == "__main__":
    main()