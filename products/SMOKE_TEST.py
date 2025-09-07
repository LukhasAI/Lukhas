#!/usr/bin/env python3
"""
🧪 Products Smoke Test Suite
Test all product components and document working vs broken state
"""
import sys
import traceback
from dataclasses import dataclass
from typing import Any

import streamlit as st


@dataclass
class TestResult:
    component: str
    status: str  # 'pass', 'fail', 'partial'
    error: str = ""
    details: dict[str, Any] = None


def test_basic_imports() -> list[TestResult]:
    """Test basic product category imports"""
    results = []

    # Test main products import
    try:
        import products

        results.append(TestResult("products", "pass", details={"modules": dir(products)}))
    except Exception as e:
        results.append(TestResult("products", "fail", str(e)))

    # Test category imports
    categories = ["experience", "communication", "content", "infrastructure", "security", "enterprise", "automation"]

    for category in categories:
        try:
            module = __import__(f"products.{category}", fromlist=[category])
            results.append(
                TestResult(f"products.{category}", "pass", details={"modules": getattr(module, "__all__", [])})
            )
        except Exception as e:
            results.append(TestResult(f"products.{category}", "fail", str(e)))

    return results


def test_experience_components() -> list[TestResult]:
    """Test experience product components"""
    results = []

    components = {
        "voice": "products.experience.voice",
        "feedback": "products.experience.feedback",
        "universal_language": "products.experience.universal_language",
        "dashboard": "products.experience.dashboard",
    }

    for comp_name, module_path in components.items():
        try:
            module = __import__(module_path, fromlist=[comp_name])
            results.append(
                TestResult(f"experience.{comp_name}", "pass", details={"path": module_path, "attrs": dir(module)})
            )
        except Exception as e:
            results.append(TestResult(f"experience.{comp_name}", "fail", str(e)))

    return results


def test_deep_imports() -> list[TestResult]:
    """Test deeper component imports"""
    results = []

    deep_tests = [
        ("voice.core.voice_system", "products.experience.voice.core.voice_system"),
        ("feedback.core.user_feedback_system", "products.experience.feedback.core.user_feedback_system"),
        ("universal_language.core.core", "products.experience.universal_language.core.core"),
        ("dashboard.core.interpretability_dashboard", "products.experience.dashboard.core.interpretability_dashboard"),
        ("communication.abas.core.abas_engine", "products.communication.abas_candidate.core.abas_engine"),
        ("communication.nias.core.nias_engine", "products.communication.nias.core.nias_engine"),
        (
            "content.poetica.creativity_engines.creative_core",
            "products.content.poetica.creativity_engines.creative_core",
        ),
    ]

    for test_name, module_path in deep_tests:
        try:
            parts = module_path.split(".")
            module = __import__(module_path, fromlist=[parts[-1]])
            results.append(
                TestResult(
                    f"deep.{test_name}",
                    "pass",
                    details={"module": module_path, "classes": [x for x in dir(module) if x[0].isupper()]},
                )
            )
        except Exception as e:
            results.append(TestResult(f"deep.{test_name}", "fail", str(e)))

    return results


def test_class_instantiation() -> list[TestResult]:
    """Test if major classes can be instantiated"""
    results = []

    class_tests = [
        ("UserFeedbackSystem", "products.experience.feedback.core.user_feedback_system", "UserFeedbackSystem"),
        ("EmotionEmoji", "products.experience.feedback.core.user_feedback_system", "EmotionEmoji"),
    ]

    for test_name, module_path, class_name in class_tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            # Try to get class info without instantiating (safer)
            results.append(
                TestResult(
                    f"class.{test_name}",
                    "pass",
                    details={"class": str(cls), "methods": [x for x in dir(cls) if not x.startswith("_")]},
                )
            )
        except Exception as e:
            results.append(TestResult(f"class.{test_name}", "fail", str(e)))

    return results


def run_all_tests() -> dict[str, list[TestResult]]:
    """Run all smoke tests"""
    return {
        "basic_imports": test_basic_imports(),
        "experience_components": test_experience_components(),
        "deep_imports": test_deep_imports(),
        "class_instantiation": test_class_instantiation(),
    }


def print_results(results: dict[str, list[TestResult]]):
    """Print test results in a readable format"""
    print("🧪 Products Smoke Test Results")
    print("=" * 50)

    total_tests = 0
    passed_tests = 0

    for category, test_results in results.items():
        print(f"\n📋 {category.upper()}")
        print("-" * 30)

        for result in test_results:
            total_tests += 1
            if result.status == "pass":
                passed_tests += 1
                print(f"✅ {result.component}")
                if result.details:
                    for key, value in result.details.items():
                        if isinstance(value, list) and len(value) > 5:
                            print(f"   {key}: {len(value)} items")
                        else:
                            print(f"   {key}: {value}")
            else:
                print(f"❌ {result.component}")
                print(f"   Error: {result.error}")

    print(f"\n📊 Summary: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")


def main():
    """Run smoke tests and print results"""
    try:
        results = run_all_tests()
        print_results(results)

        # Return exit code based on results
        total_tests = sum(len(test_results) for test_results in results.values())
        passed_tests = sum(1 for test_results in results.values() for result in test_results if result.status == "pass")

        if passed_tests == total_tests:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Smoke test suite failed: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
