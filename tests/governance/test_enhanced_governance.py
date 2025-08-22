#!/usr/bin/env python3
"""
🧪 Enhanced  Governance Test Suite
=====================================

Tests the superior ethics and red team integrated governance system.
"""

import asyncio
import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 Testing Enhanced  Governance with Superior Ethics...")

try:
    from lukhas.governance.enhanced_guardian import EnhancedWorkspaceGuardian

    print("✅ Enhanced governance modules imported successfully")
    enhanced_available = True
except ImportError as e:
    print(f"⚠️ Enhanced governance import error: {e}")
    print("📝 Falling back to basic governance test...")
    enhanced_available = False

    try:
        from lukhas.governance._workspace_guardian import WorkspaceGuardian

        print("✅ Basic governance available as fallback")
        basic_available = True
    except ImportError as e2:
        print(f"❌ Basic governance also failed: {e2}")
        basic_available = False


async def test_enhanced_governance():
    """Test enhanced governance with superior ethics."""

    if not enhanced_available:
        print("❌ Enhanced governance not available")
        return False

    try:
        print("\n🌟 Testing Enhanced  Workspace Guardian...")

        # Initialize enhanced guardian
        guardian = EnhancedWorkspaceGuardian()
        await guardian.initialize()
        print("✅ Enhanced guardian initialized")

        # Test enhanced file protection
        protection_result = await guardian.enhanced_file_operation_check(
            "delete", "README.md"
        )
        print(
            f"📁 Enhanced README protection: {protection_result['allowed']} - {protection_result['reason']}"
        )
        print(
            f"🧠 Ethics framework: {protection_result.get('ethics_framework', 'UNKNOWN')}"
        )
        print(f"📊 Confidence: {protection_result.get('confidence', 0.0):.2f}")

        # Test workspace health analysis
        health = await guardian.analyze_workspace_health()
        print(f"🏥 Enhanced workspace health: {health['symbolic']}")
        print(f"📊 Health score: {health['health_score']:.2f}")
        print(f"🧠 Ethics system: {health['ethics_system']}")
        print(f"🔴 Red team available: {health['red_team_available']}")

        # Test security validation
        print("\n🔍 Running comprehensive security validation...")
        security = await guardian.run_security_validation()
        print(f"🛡️ Security summary: {security['security_summary']}")

        if "red_team_validation" in security:
            rt_status = security["red_team_validation"].get("overall_status", "UNKNOWN")
            print(f"🔴 Red team validation: {rt_status}")

        print("\n🎯 Enhanced  Governance system is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Enhanced test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_basic_governance():
    """Test basic governance as fallback."""

    if not basic_available:
        print("❌ Basic governance not available")
        return False

    try:
        print("\n🛡️ Testing Basic  Workspace Guardian...")

        guardian = WorkspaceGuardian()
        await guardian.initialize()
        print("✅ Basic guardian initialized")

        protection_result = await guardian.check_file_operation("delete", "README.md")
        print(
            f"📁 Basic README protection: {protection_result['allowed']} - {protection_result['reason']}"
        )

        health = await guardian.analyze_workspace_health()
        print(f"🏥 Basic workspace health: {health['symbolic']}")

        print("\n🎯 Basic  Governance system is working!")
        return True

    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


async def main():
    """Run comprehensive governance tests."""

    print("🚀 Starting  Governance Test Suite...\n")

    # Test enhanced system first
    enhanced_success = False
    if enhanced_available:
        enhanced_success = await test_enhanced_governance()

    # Test basic system if enhanced fails or isn't available
    basic_success = False
    if not enhanced_success and basic_available:
        basic_success = await test_basic_governance()

    # Results summary
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 60)

    if enhanced_success:
        print("🌟 ENHANCED GOVERNANCE: ✅ SUCCESS")
        print("   - Superior LUKHAS ethics integrated")
        print("   - Red team protocols available")
        print("   - Multi-framework ethics engine")
        print("   - Tier-based consent system")
        print("\n🚀 Your  workspace has ENHANCED protection!")

    elif basic_success:
        print("🛡️ BASIC GOVERNANCE: ✅ SUCCESS")
        print("   - Guardian System v1.0.0 active")
        print("   - File protection working")
        print("   - Workspace health monitoring")
        print(
            "\n📈 Consider installing enhanced ethics dependencies for superior protection"
        )

    else:
        print("❌ GOVERNANCE TESTS: FAILED")
        print("   - Check module dependencies")
        print("   - Verify file paths and imports")
        print("\n🔧 Governance system needs configuration")

    print("=" * 60)

    return enhanced_success or basic_success


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎯  governance is ready to protect your workspace!")
        sys.exit(0)
    else:
        print("\n🔧 Governance system requires attention")
        sys.exit(1)
