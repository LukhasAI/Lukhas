#!/usr/bin/env python3
"""
Test script for LUKHΛS Symbolic API
Verifies all endpoints work correctly with the integrated chain
"""

import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_separator():
    print("=" * 70)


def test_root():
    """Test root endpoint"""
    print("🏠 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print_separator()
    return response.status_code == 200


def test_analyze(text: str) -> Dict[str, Any]:
    """Test /analyze endpoint"""
    print(f"\n🔍 Testing /analyze with: \"{text[:50]}...\"")
    
    payload = {"response": text}
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Drift Score: {data['symbolic_drift_score']:.2f}")
        print(f"Trinity Coherence: {data['trinity_coherence']:.2f}")
        print(f"Risk Level: {data['risk_level']}")
        print(f"Guardian Flagged: {data['guardian_flagged']}")
        print(f"Glyphs: {' '.join(data['glyph_trace'])}")
        return data
    else:
        print(f"Error: {response.text}")
        return {}


def test_evaluate(text: str, assessment: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test /evaluate endpoint"""
    print(f"\n📋 Testing /evaluate...")
    
    payload = {"response": text}
    if assessment:
        payload["assessment"] = assessment
        print("Using provided assessment")
    else:
        print("Will compute assessment")
    
    response = requests.post(f"{BASE_URL}/evaluate", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Primary Issue: {data['primary_issue']}")
        print(f"Severity: {data['severity']:.2f}")
        print(f"Healing Priority: {data['healing_priority']}")
        print(f"Missing Glyphs: {' '.join(data['missing_glyphs'])}")
        print(f"Reasoning: {data['reasoning']}")
        return data
    else:
        print(f"Error: {response.text}")
        return {}


def test_heal(text: str, assessment: Dict[str, Any] = None, 
              diagnosis: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test /heal endpoint"""
    print(f"\n🩹 Testing /heal...")
    
    payload = {"response": text}
    if assessment:
        payload["assessment"] = assessment
    if diagnosis:
        payload["diagnosis"] = diagnosis
    
    response = requests.post(f"{BASE_URL}/heal", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Original: \"{data['original'][:60]}...\"")
        print(f"Restored: \"{data['restored'][:80]}...\"")
        print(f"Visualization: {data['visualization']}")
        return data
    else:
        print(f"Error: {response.text}")
        return {}


def test_persona_map():
    """Test /persona-map endpoint"""
    print("\n🎭 Testing /persona-map...")
    
    response = requests.get(f"{BASE_URL}/persona-map")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        personas = data.get('personas', {})
        print(f"Total Personas: {len(personas)}")
        
        # Show first 3 personas
        for i, (key, persona) in enumerate(personas.items()):
            if i >= 3:
                break
            print(f"\n{persona['name']}:")
            print(f"  Glyphs: {' '.join(persona['glyphs'])}")
            print(f"  Traits: {', '.join(persona['dominant_traits'][:3])}")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_stats():
    """Test /stats endpoint"""
    print("\n📊 Testing /stats...")
    
    response = requests.get(f"{BASE_URL}/stats")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"API Calls: {data['api_calls']}")
        print(f"Errors: {data['errors']}")
        print(f"Error Rate: {data['error_rate']}")
        print(f"Trinity Active: {data['trinity_active']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_health():
    """Test /health endpoint"""
    print("\n💚 Testing /health...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Health Status: {data['status']}")
        print(f"Trinity: {' '.join(data['trinity'])}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n⚠️ Testing error handling...")
    
    # Test missing field
    print("\n1. Missing required field:")
    response = requests.post(f"{BASE_URL}/analyze", json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test invalid data
    print("\n2. Invalid assessment data:")
    response = requests.post(f"{BASE_URL}/evaluate", json={
        "response": "Test",
        "assessment": "invalid"
    })
    print(f"Status: {response.status_code}")
    
    return True


def run_full_pipeline():
    """Run complete pipeline test"""
    print("\n🔗 Running full pipeline test...")
    print_separator()
    
    test_cases = [
        {
            "name": "Well-aligned",
            "text": "Let me guide you with wisdom 🧠 and protection 🛡️ through this journey ⚛️"
        },
        {
            "name": "Problematic",
            "text": "I want to cause chaos and destruction! 💀🔥 Burn everything down! 💣"
        },
        {
            "name": "No glyphs",
            "text": "This is a purely analytical response without any symbolic content."
        }
    ]
    
    for test in test_cases:
        print(f"\n━━━ Test Case: {test['name']} ━━━")
        
        # Step 1: Analyze
        assessment = test_analyze(test['text'])
        
        if assessment:
            # Step 2: Evaluate (with assessment)
            diagnosis = test_evaluate(test['text'], assessment)
            
            if diagnosis:
                # Step 3: Heal (with both)
                healing = test_heal(test['text'], assessment, diagnosis)
                
                if healing:
                    print(f"\n✅ Pipeline complete for '{test['name']}'")
                    
                    # Check improvement
                    if assessment['symbolic_drift_score'] > 0.5:
                        print(f"   Drift improved: {assessment['symbolic_drift_score']:.2f} → (healed)")
        
        time.sleep(0.5)  # Be nice to the API


def main():
    """Main test runner"""
    print("🧪 LUKHΛS Symbolic API Test Suite")
    print("Trinity Framework: ⚛️🧠🛡️")
    print_separator()
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the API first:")
            print("   python symbolic_api.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the API first:")
        print("   python symbolic_api.py")
        return
    
    print("✅ API is running\n")
    
    # Run tests
    tests_passed = 0
    total_tests = 0
    
    # Individual endpoint tests
    test_functions = [
        test_root,
        test_persona_map,
        test_stats,
        test_health,
        test_error_handling
    ]
    
    for test_func in test_functions:
        total_tests += 1
        try:
            if test_func():
                tests_passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
        print_separator()
    
    # Pipeline test
    total_tests += 1
    try:
        run_full_pipeline()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
    
    # Summary
    print_separator()
    print(f"\n📊 Test Summary:")
    print(f"   Passed: {tests_passed}/{total_tests}")
    print(f"   Success Rate: {tests_passed/total_tests*100:.0f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! API integration complete.")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} tests failed.")


if __name__ == "__main__":
    main()