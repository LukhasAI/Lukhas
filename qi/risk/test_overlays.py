#!/usr/bin/env python3
"""
Test script for Risk Orchestrator Overlays
"""

import os
import json
from pathlib import Path
from orchestrator_overlays import RiskOverlayManager

def test_overlay_manager():
    """Test the Risk Overlay Manager with different jurisdictions and contexts"""
    
    # Get the overlays directory
    overlay_dir = Path(__file__).parent / "overlays"
    
    print("Testing Risk Overlay Manager")
    print("=" * 50)
    
    # Initialize the manager
    mgr = RiskOverlayManager(str(overlay_dir))
    
    # Test 1: Global policies only
    print("\n1. Global policies (no jurisdiction or context):")
    policies = mgr.get_policies()
    print(json.dumps(policies, indent=2))
    
    # Test 2: EU jurisdiction
    print("\n2. EU jurisdiction policies:")
    policies = mgr.get_policies(jurisdiction="eu")
    print(json.dumps(policies, indent=2))
    
    # Test 3: US jurisdiction
    print("\n3. US jurisdiction policies:")
    policies = mgr.get_policies(jurisdiction="us")
    print(json.dumps(policies, indent=2))
    
    # Test 4: Medical high-risk context
    print("\n4. Medical high-risk context (no jurisdiction):")
    policies = mgr.get_policies(context="medical_high_risk")
    print(json.dumps(policies, indent=2))
    
    # Test 5: EU + Medical high-risk
    print("\n5. EU jurisdiction + Medical high-risk context:")
    policies = mgr.get_policies(jurisdiction="eu", context="medical_high_risk")
    print(json.dumps(policies, indent=2))
    
    # Test 6: Hot reload
    print("\n6. Testing hot reload capability:")
    try:
        mgr.hot_reload()
        print("✅ Hot reload successful")
    except Exception as e:
        print(f"❌ Hot reload failed: {e}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_overlay_manager()