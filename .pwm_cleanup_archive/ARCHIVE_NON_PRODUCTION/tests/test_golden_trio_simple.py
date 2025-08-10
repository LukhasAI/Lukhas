#!/usr/bin/env python3
"""
Simplified Golden Trio Test Runner
Tests what's available and reports on missing dependencies
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

test_results = {
    "test_suite": "Golden Trio Integration",
    "execution_date": datetime.now().isoformat(),
    "tests": [],
}


def test_import(module_path, component_name):
    """Test if a module can be imported"""
    test = {
        "name": f"Import {component_name}",
        "module": module_path,
        "status": "PASS",
        "message": "",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        exec(f"from {module_path} import *")
        test["message"] = f"Successfully imported {component_name}"
        print(f"✅ {test['name']}: {test['message']}")
    except ImportError as e:
        test["status"] = "FAIL"
        test["message"] = f"Import error: {str(e)}"
        print(f"❌ {test['name']}: {test['message']}")
    except Exception as e:
        test["status"] = "ERROR"
        test["message"] = f"Unexpected error: {str(e)}"
        print(f"🚨 {test['name']}: {test['message']}")

    test_results["tests"].append(test)
    return test["status"] == "PASS"


def test_component_init(import_path, class_name, component_name):
    """Test if a component can be initialized"""
    test = {
        "name": f"Initialize {component_name}",
        "component": class_name,
        "status": "PASS",
        "message": "",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        module = __import__(import_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        instance = cls()
        test["message"] = f"Successfully initialized {component_name}"
        print(f"✅ {test['name']}: {test['message']}")
        return instance
    except Exception as e:
        test["status"] = "FAIL"
        test["message"] = f"Initialization error: {str(e)}"
        print(f"❌ {test['name']}: {test['message']}")
        return None
    finally:
        test_results["tests"].append(test)


def test_hub_attributes(hub, hub_name, expected_attrs):
    """Test if a hub has expected attributes"""
    test = {
        "name": f"{hub_name} Attributes",
        "hub": hub_name,
        "status": "PASS",
        "message": "",
        "timestamp": datetime.now().isoformat(),
    }

    if hub is None:
        test["status"] = "SKIP"
        test["message"] = "Hub not available for testing"
        print(f"⏭️  {test['name']}: {test['message']}")
    else:
        missing = []
        for attr in expected_attrs:
            if not hasattr(hub, attr):
                missing.append(attr)

        if missing:
            test["status"] = "FAIL"
            test["message"] = f"Missing attributes: {missing}"
            print(f"❌ {test['name']}: {test['message']}")
        else:
            test["message"] = "All expected attributes present"
            print(f"✅ {test['name']}: {test['message']}")

    test_results["tests"].append(test)


def main():
    """Run simplified tests"""
    print("\n🚀 Golden Trio Simplified Test Suite")
    print("=" * 60)

    # Test imports
    print("\n📦 Testing Imports...")
    test_import("dast.integration.dast_integration_hub", "DAST Hub")
    test_import("abas.integration.abas_integration_hub", "ABAS Hub")
    test_import("orchestration.golden_trio.trio_orchestrator", "TrioOrchestrator")
    test_import("symbolic.core.symbolic_language", "Symbolic Framework")
    test_import("analysis_tools.audit_decision_embedding_engine", "Audit Engine")
    test_import("ethics.seedra.seedra_core", "SEEDRA Core")

    # Test component initialization
    print("\n🔧 Testing Component Initialization...")

    # Test DAST Hub
    try:
        from dast.integration.dast_integration_hub import (
            get_dast_integration_hub,
        )

        dast_hub = get_dast_integration_hub()
        test_results["tests"].append(
            {
                "name": "DAST Hub Factory",
                "status": "PASS",
                "message": "get_dast_integration_hub() successful",
                "timestamp": datetime.now().isoformat(),
            }
        )
        print("✅ DAST Hub Factory: Successful")

        # Test attributes
        test_hub_attributes(
            dast_hub,
            "DAST Hub",
            [
                "trio_orchestrator",
                "dast_engine",
                "audit_engine",
                "symbolic_framework",
                "seedra",
                "registered_components",
            ],
        )
    except Exception as e:
        test_results["tests"].append(
            {
                "name": "DAST Hub Factory",
                "status": "FAIL",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"❌ DAST Hub Factory: {e}")

    # Test ABAS Hub
    try:
        from abas.integration.abas_integration_hub import (
            get_abas_integration_hub,
        )

        abas_hub = get_abas_integration_hub()
        test_results["tests"].append(
            {
                "name": "ABAS Hub Factory",
                "status": "PASS",
                "message": "get_abas_integration_hub() successful",
                "timestamp": datetime.now().isoformat(),
            }
        )
        print("✅ ABAS Hub Factory: Successful")

        # Test attributes
        test_hub_attributes(
            abas_hub,
            "ABAS Hub",
            [
                "trio_orchestrator",
                "abas_engine",
                "ethics_engine",
                "audit_engine",
                "seedra",
                "registered_components",
            ],
        )
    except Exception as e:
        test_results["tests"].append(
            {
                "name": "ABAS Hub Factory",
                "status": "FAIL",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"❌ ABAS Hub Factory: {e}")

    # Test Symbolic Framework
    try:
        from symbolic.core.symbolic_language import SymbolicLanguageFramework

        framework = SymbolicLanguageFramework()
        test_results["tests"].append(
            {
                "name": "Symbolic Framework Init",
                "status": "PASS",
                "message": "Framework initialized",
                "timestamp": datetime.now().isoformat(),
            }
        )
        print("✅ Symbolic Framework Init: Successful")

        # Test methods
        if hasattr(framework, "register_patterns"):
            print("✅ Symbolic Framework: Has register_patterns method")
        else:
            print("❌ Symbolic Framework: Missing register_patterns method")

    except Exception as e:
        test_results["tests"].append(
            {
                "name": "Symbolic Framework Init",
                "status": "FAIL",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"❌ Symbolic Framework Init: {e}")

    # Calculate summary
    total = len(test_results["tests"])
    passed = len([t for t in test_results["tests"] if t["status"] == "PASS"])
    failed = len([t for t in test_results["tests"] if t["status"] == "FAIL"])
    errors = len([t for t in test_results["tests"] if t["status"] == "ERROR"])
    skipped = len([t for t in test_results["tests"] if t["status"] == "SKIP"])

    # Add summary
    test_results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": (passed / total * 100) if total > 0 else 0,
    }

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Errors: {errors} 🚨")
    print(f"Skipped: {skipped} ⏭️")
    print(f"Pass Rate: {test_results['summary']['pass_rate']:.1f}%")

    # Save results
    with open("test_results_golden_trio_simple.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print("\n📄 Results saved to: test_results_golden_trio_simple.json")


if __name__ == "__main__":
    main()
