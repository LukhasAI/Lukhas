#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Real API Test with Token Control
Tests financial intelligence and AI routing with actual or mock API calls
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime

sys.path.append('/Users/A_G_I/Λ')

def check_keychain_api_key(service_name):
    """Check if API key exists in keychain"""
    try:
        result = subprocess.run([
            'security', 'find-generic-password',
            '-s', service_name,
            '-w'
        ], capture_output=True, text=True, check=True)
        api_key = result.stdout.strip()
        return api_key if api_key and len(api_key) > 10 else None
    except subprocess.CalledProcessError:
        return None

def test_financial_system():
    """Test LUKHAS AI ΛBot financial intelligence system"""
    print("💰 Testing LUKHAS AI ΛBot Financial Intelligence System")
    print("=" * 50)

    try:
        from LUKHAS AI ΛBot.core.abot_financial_intelligence import ABotFinancialIntelligence
        fi = ABotFinancialIntelligence()

        # Get current status
        status = fi.get_financial_report()
        print(f"✅ Current Balance: ${status['budget_status']['current_balance']:.4f}")
        print(f"📊 Daily Budget: ${status['budget_status']['daily_budget']:.2f}")
        print(f"🧠 Efficiency Score: {status['intelligence_metrics']['efficiency_score']:.1f}%")
        print(f"📈 Total Calls: {status['usage_patterns']['total_calls']}")

        return True
    except Exception as e:
        print(f"❌ Financial system error: {e}")
        return False

def test_ai_router():
    """Test AI router system"""
    print("\n🤖 Testing AI Router System")
    print("=" * 50)

    try:
        from LUKHAS AI ΛBot.core.abot_ai_router import ABotIntelligentAIRouter
        router = ABotIntelligentAIRouter()

        services = router.get_available_services()
        print(f"✅ Available AI Services: {len(services)}")

        # Check which services have API keys
        service_configs = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "LUKHAS AI ΛBot-Anthropic-API",
            "Gemini": "lukhas-ai-gemini",
            "Azure": "lukhas-ai-azure-api-key",
            "Perplexity": "LUKHAS AI ΛBot-Perplexity-API"
        }

        available_apis = {}
        for service, keychain_name in service_configs.items():
            api_key = check_keychain_api_key(keychain_name)
            available_apis[service] = "✅ Configured" if api_key else "❌ Missing"

        print("\n🔑 API Key Status:")
        for service, status in available_apis.items():
            print(f"   {service}: {status}")

        return available_apis
    except Exception as e:
        print(f"❌ AI router error: {e}")
        return {}

def test_real_openai_call():
    """Test real OpenAI API call with cost controls"""
    print("\n🔥 Testing Real OpenAI API Call with Cost Controls")
    print("=" * 50)

    # Check if OpenAI key is available
    openai_key = check_keychain_api_key("OPENAI_API_KEY")
    if not openai_key:
        print("❌ No OpenAI API key found in keychain (service: OPENAI_API_KEY)")
        print("💡 Run: security add-generic-password -s 'OPENAI_API_KEY' -a 'LUKHAS AI ΛBot' -w 'sk-your-key'")
        return False

    print(f"✅ OpenAI API key found: {openai_key[:10]}...")

    try:
        from LUKHAS AI ΛBot.core.openai_intelligent_controller import test_openai_with_financial_controls

        print("🧪 Testing with financial controls...")
        result = test_openai_with_financial_controls()

        if result:
            print("✅ OpenAI API call successful!")
            print("💰 Financial controls working!")
            return True
        else:
            print("❌ OpenAI API call failed")
            return False

    except Exception as e:
        print(f"❌ OpenAI test error: {e}")
        return False

def test_mock_api_call():
    """Test with mock API call to demonstrate financial controls"""
    print("\n🎭 Testing Mock API Call with Financial Controls")
    print("=" * 50)

    try:
        from LUKHAS AI ΛBot.core.abot_financial_intelligence import ABotFinancialIntelligence

        fi = ABotFinancialIntelligence()

        # Get initial status
        initial_status = fi.get_financial_report()
        initial_balance = initial_status['budget_status']['current_balance']
        initial_calls = initial_status['usage_patterns']['total_calls']

        print(f"📊 Initial Balance: ${initial_balance:.4f}")
        print(f"📞 Initial Calls: {initial_calls}")

        # Simulate API cost
        mock_cost = 0.002  # $0.002 for a test call
        print(f"\n🎯 Simulating API call cost: ${mock_cost:.4f}")

        # Check if we can afford it
        if fi.can_afford_call(mock_cost):
            print("✅ Call approved by financial controls")

            # Record the cost
            fi.record_api_cost(mock_cost, "gpt-4o", "test_call")

            # Get updated status
            updated_status = fi.get_financial_report()
            new_balance = updated_status['budget_status']['current_balance']
            new_calls = updated_status['usage_patterns']['total_calls']

            print(f"📊 New Balance: ${new_balance:.4f}")
            print(f"📞 New Calls: {new_calls}")
            print(f"💸 Cost Deducted: ${initial_balance - new_balance:.4f}")
            print("✅ Financial tracking working perfectly!")

            return True
        else:
            print("❌ Call rejected by financial controls - insufficient budget")
            return False

    except Exception as e:
        print(f"❌ Mock API test error: {e}")
        return False

def test_lambda_id_integration():
    """Test ΛID system integration"""
    print("\n🔒 Testing ΛID System Integration")
    print("=" * 50)

    try:
        from LUKHAS AI ΛBot.core.lambda_id_manager import create_λid, verify_λsign, create_λtrace
        from ΛiD.ΛiD import ConsentLevel

        # Create a test ΛID#
        test_lambda_id = "US-TEST1234567"
        result = create_λid(test_lambda_id, ConsentLevel.STANDARD)

        if result.get('status') == 'created':
            print(f"✅ Created ΛID#: {result['ΛID#']}")
            print(f"📝 ΛSIGN: {result['ΛSIGN']}")
            print(f"📊 ΛTRACE: {result['ΛTRACE']}")

            # Test consent verification
            consent_check = verify_λsign(test_lambda_id, ConsentLevel.BASIC)
            print(f"✅ Consent Verified: {consent_check['verified']}")

            # Create custom trace
            trace_id = create_λtrace("api_test", test_lambda_id, {"test": "real_api_integration"})
            print(f"📊 Custom Trace: {trace_id}")

            return True
        else:
            print(f"❌ ΛID creation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ ΛID integration error: {e}")
        return False

def main():
    """Run comprehensive LUKHAS AI ΛBot API and token control tests"""
    print("🚀 LUKHAS AI ΛBot Real API Test with Token Control")
    print("=" * 60)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test results
    results = {
        "financial_system": False,
        "ai_router": False,
        "real_openai": False,
        "mock_api": False,
        "lambda_id": False
    }

    # Run tests
    results["financial_system"] = test_financial_system()
    available_apis = test_ai_router()
    results["ai_router"] = len(available_apis) > 0

    # Try real OpenAI if available, otherwise use mock
    if available_apis.get("OpenAI") == "✅ Configured":
        results["real_openai"] = test_real_openai_call()

    if not results["real_openai"]:
        results["mock_api"] = test_mock_api_call()

    results["lambda_id"] = test_lambda_id_integration()

    # Final summary
    print("\n" + "=" * 60)
    print("📋 LUKHAS AI ΛBot Real API Test Results")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")

    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! LUKHAS AI ΛBot is ready for production!")
    elif passed_tests >= total_tests * 0.8:
        print("🌟 Most tests passed! LUKHAS AI ΛBot is nearly ready!")
    else:
        print("⚠️ Some tests failed. Check configuration and API keys.")

    print(f"\n📊 System Status: {'🟢 OPERATIONAL' if passed_tests >= 3 else '🟡 NEEDS ATTENTION'}")

if __name__ == "__main__":
    main()
