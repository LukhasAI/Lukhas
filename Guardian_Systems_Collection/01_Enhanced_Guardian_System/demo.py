#!/usr/bin/env python3
"""
Enhanced Guardian System - Complete Integration Demo
Demonstrates the full Enhanced Guardian System with all subsystems integrated
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure local package is importable
sys.path.insert(0, str(Path(__file__).parent))

# Import core Guardian modules
try:
    from core.guardian_engine import GuardianEngine
    print("✅ Guardian Engine imported successfully")
except ImportError as e:
    print(f"⚠️ Guardian Engine import failed: {e}")
    print("⚠️ Some modules may not be available - running with core functionality")
    GuardianEngine = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def comprehensive_demo():
    """
    Comprehensive demonstration of the Enhanced Guardian System
    Shows core functionality and integration possibilities
    """
    print("🛡️ Enhanced Guardian System - Complete Integration Demo")
    print("=" * 60)
    print("🏥 Medical • 👁️ Accessibility • 🔒 Security • 🧠 AI Protection")
    print("=" * 60)
    
    if not GuardianEngine:
        print("❌ Guardian Engine not available - please check installation")
        return
    
    try:
        # Initialize core Guardian Engine
        print("\n🚀 Initializing Enhanced Guardian System...")
        guardian = GuardianEngine()
        
        print("   🔧 Starting Guardian Engine...")
        
        # Start the Guardian system
        startup_result = await guardian.start_all_systems()
        
        if startup_result:
            print("   🛡️ Enhanced Guardian System is now active!")
        else:
            print("   ⚠️ Some subsystems may have initialization issues")
        
        # Demonstration Scenarios
        print("\n" + "="*60)
        print("📋 DEMONSTRATION SCENARIOS")
        print("="*60)
        
        # Scenario 1: Medical Emergency Detection
        await demo_core_medical_functionality(guardian)
        
        # Scenario 2: Consent and Privacy Management
        await demo_core_consent_functionality(guardian)
        
        # Scenario 3: Vision and Accessibility Support
        await demo_core_accessibility_functionality(guardian)
        
        # Scenario 4: System Health and Monitoring
        await demo_system_health(guardian)
        
        print("\n" + "="*60)
        print("🎯 ENHANCED GUARDIAN SYSTEM DEMO COMPLETE")
        print("="*60)
        print("The core Guardian Engine provides foundational protection,")
        print("medical assistance, and accessibility support capabilities.")
        print("Additional subsystems can be integrated for enhanced functionality! 🚀")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")


async def demo_core_medical_functionality(guardian):
    """Demonstrate core medical functionality"""
    print("\n💊 SCENARIO 1: Core Medical Functionality")
    print("-" * 40)
    
    # Test medication label reading
    print("📸 Testing medication label reading...")
    
    # Create a mock image path
    mock_image = "path/to/medication_bottle.jpg"
    
    try:
        result = await guardian.read_medication_label(mock_image)
        
        if result.get("success"):
            print(f"   ✅ Medication reading successful")
            print(f"   💊 Mock analysis completed")
            print(f"   📋 Response time: {result.get('processing_time', 'N/A')}")
        else:
            print(f"   ⚠️ Medication reading: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ⚠️ Medication reading test: {e}")
    
    # Test emergency alert
    print("\n🚨 Testing emergency alert system...")
    
    try:
        emergency_result = await guardian.emergency_alert(
            emergency_type="medical",
            severity="high",
            context={
                "description": "Chest pain and difficulty breathing",
                "location": {"lat": 40.7128, "lng": -74.0060}
            }
        )
        
        if emergency_result.get("success"):
            print(f"   ✅ Emergency alert sent successfully")
            print(f"   🚨 Alert ID: {emergency_result.get('alert_id', 'N/A')}")
            print(f"   📞 Response initiated: {emergency_result.get('response_initiated', False)}")
        else:
            print(f"   ⚠️ Emergency alert: {emergency_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ⚠️ Emergency alert test: {e}")


async def demo_core_consent_functionality(guardian):
    """Demonstrate core consent functionality"""
    print("\n📋 SCENARIO 2: Consent Management")
    print("-" * 40)
    
    print("📝 Testing consent request...")
    
    # Test consent request
    try:
        consent_result = await guardian.request_consent(
            requester="demo_system",
            resource="medical_data",
            permission="read_write",
            context={
                "user_id": "demo_user_123",
                "data_types": ["medical", "personal"],
                "purposes": ["healthcare", "emergency_response"],
                "duration": "1 year",
                "scope": "full_access"
            }
        )
        
        if consent_result.get("success"):
            print(f"   ✅ Consent request processed")
            print(f"   📄 Consent ID: {consent_result.get('consent_id', 'N/A')}")
            print(f"   📊 Trust score: {consent_result.get('trust_score', 'N/A')}")
            print(f"   ⏰ Valid until: {consent_result.get('expiry_date', 'N/A')}")
        else:
            print(f"   ⚠️ Consent request: {consent_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ⚠️ Consent test: {e}")


async def demo_core_accessibility_functionality(guardian):
    """Demonstrate core accessibility functionality"""
    print("\n👁️ SCENARIO 3: Accessibility Support")
    print("-" * 40)
    
    print("🔍 Testing scene description...")
    
    # Test scene description
    mock_image = "path/to/scene_image.jpg"
    
    try:
        description_result = await guardian.describe_scene(mock_image, "en")
        
        if description_result.get("success"):
            print(f"   ✅ Scene description generated")
            print(f"   💬 Description: {description_result.get('description', 'N/A')[:100]}...")
            print(f"   🌐 Language: {description_result.get('language', 'N/A')}")
            print(f"   📊 Confidence: {description_result.get('confidence', 'N/A')}")
        else:
            print(f"   ⚠️ Scene description: {description_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ⚠️ Scene description test: {e}")
    
    # Test multi-language support
    print("\n🌐 Testing language support...")
    print("   🔄 Mock translation: 'Emergency help needed' -> 'Ayuda de emergencia necesaria'")
    print("   ✅ Multi-language support available")


async def demo_system_health(guardian):
    """Demonstrate system health monitoring"""
    print("\n🏥 SCENARIO 4: System Health Monitoring")
    print("-" * 40)
    
    print("📊 Checking system health...")
    
    try:
        health_result = guardian.get_system_status()
        
        if health_result:
            print(f"   ✅ System health check complete")
            print(f"   💚 Overall status: {health_result.get('status', 'Unknown')}")
            print(f"   ⏱️  Uptime: {health_result.get('uptime', 'N/A')}")
            print(f"   🔧 Active modules: {health_result.get('active_modules', 'N/A')}")
            print(f"   📈 Performance: {health_result.get('performance_score', 'N/A')}")
        else:
            print("   ⚠️ Health check returned no data")
    except Exception as e:
        print(f"   ⚠️ Health check test: {e}")
    
    # Show system capabilities
    print("\n🎯 System Capabilities Summary:")
    print("   💊 Medical: OCR reading, emergency alerts, health monitoring")
    print("   👁️ Accessibility: Scene description, vision assistance, multi-language")
    print("   🔒 Security: Consent management, privacy protection, threat monitoring")
    print("   🧠 AI Protection: Consciousness monitoring, symbolic AI safety")
    print("   🏥 Integration: Healthcare APIs, emergency services, accessibility tools")
if __name__ == "__main__":
    try:
        asyncio.run(comprehensive_demo())
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo execution failed")
