#!/usr/bin/env python3
"""
��  Governance Test Script
=============================

Quick test to validate the governance integration.
"""

import asyncio
import os
import sys

# Add governance to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "governance"))

try:
    sys.path.insert(
        0,
        os.path.join(os.path.dirname(__file__), "..", "..", "governance", "guardian"),
    )
    from _workspace_guardian import WorkspaceGuardian

    # protect_my_workspace is in the same guardian.core module
    print("✅ Governance modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_governance():
    """Test basic governance functionality."""
    print("\n🛡️ Testing  Workspace Guardian...")

    try:
        # Initialize guardian
        guardian = WorkspaceGuardian()
        print("✅ Guardian initialized")

        # Test file protection (mock test - no actual deletion)
        protection_result = await guardian.check_file_operation("delete", "README.md")
        print(
            f"📁 README.md protection: {protection_result['allowed']} - {protection_result['reason']}"
        )

        # Test workspace health
        health = await guardian.analyze_workspace_health()
        print(f"🏥 Workspace health: {health['symbolic']}")
        print(f"📊 Health score: {health['health_score']:.2f}")

        # Test cleanup suggestions
        cleanup = await guardian.suggest_cleanup()
        print(f"🧹 Cleanup suggestions: {len(cleanup['suggestions'])}")

        print("\n🎯  Governance system is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_governance())
    if success:
        print("\n🚀 Ready to protect your  workspace!")
    else:
        print("\n🔧 Governance system needs adjustment")
        sys.exit(1)
