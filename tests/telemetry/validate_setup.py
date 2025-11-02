#!/usr/bin/env python3
"""
Validation script for telemetry smoke test setup.

Runs basic validation to ensure telemetry test infrastructure is working
correctly before running the full test suite.
"""

import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def validate_imports():
    """Validate that required modules can be imported."""
    print("🔍 Validating imports...")

    try:
        import pytest

        print(f"  ✅ pytest {pytest.__version__}")
    except ImportError as e:
        print(f"  ❌ pytest import failed: {e}")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider

        print("  ✅ OpenTelemetry imports successful")
    except ImportError as e:
        print(f"  ❌ OpenTelemetry import failed: {e}")
        return False

    try:
        # Test telemetry fixtures
        from conftest import CapturedSpan, InMemorySpanExporter, TelemetryCapture

        print("  ✅ Telemetry fixtures import successful")
    except ImportError as e:
        print(f"  ❌ Telemetry fixtures import failed: {e}")
        return False

    try:
        # Test authorization middleware
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        from matrix_authz_middleware import AuthzRequest, MatrixAuthzMiddleware

        print("  ✅ Authorization middleware import successful")
    except ImportError as e:
        print(f"  ❌ Authorization middleware import failed: {e}")
        return False

    return True


def validate_fixtures():
    """Validate that telemetry fixtures work correctly."""
    print("\n🔍 Validating telemetry fixtures...")

    try:
        from conftest import CapturedSpan, TelemetryCapture

        # Test basic fixture functionality
        capture = TelemetryCapture()
        test_span = CapturedSpan(
            name="authz.check",
            attributes={"subject": "lukhas:user:test", "tier": "trusted", "decision": "allow"},
            status="OK",
            status_message=None,
            duration_ms=15.5,
            trace_id="12345678901234567890123456789012",
            span_id="1234567890123456",
        )
        capture.spans.append(test_span)

        # Test helper methods
        authz_spans = capture.get_authz_spans()
        assert len(authz_spans) == 1, "Should find one authz span"
        assert authz_spans[0].name == "authz.check", "Span name should be authz.check"

        # Test span filtering
        assert capture.has_span("authz.check"), "Should detect authz.check span"
        assert not capture.has_span("nonexistent"), "Should not detect nonexistent span"

        print("  ✅ TelemetryCapture working correctly")
        print("  ✅ CapturedSpan working correctly")
        print("  ✅ Span filtering working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Fixture validation failed: {e}")
        return False


def validate_authorization_middleware():
    """Validate that authorization middleware is accessible."""
    print("\n🔍 Validating authorization middleware...")

    try:
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        from matrix_authz_middleware import AuthzRequest, MatrixAuthzMiddleware

        # Test middleware instantiation
        MatrixAuthzMiddleware(shadow_mode=True)
        print("  ✅ Middleware instantiation successful")

        # Test request creation
        AuthzRequest(
            subject="lukhas:user:test",
            tier="trusted",
            tier_num=3,
            scopes=["memoria.read"],
            module="memoria",
            action="recall",
            capability_token="test-token",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2",
        )
        print("  ✅ AuthzRequest creation successful")
        return True

    except Exception as e:
        print(f"  ❌ Authorization middleware validation failed: {e}")
        return False


def validate_matrix_contract():
    """Validate that Matrix contracts are accessible."""
    print("\n🔍 Validating Matrix contracts...")

    try:
        contract_path = REPO_ROOT / "memory" / "matrix_memoria.json"
        if contract_path.exists():
            import json

            with open(contract_path) as f:
                contract = json.load(f)

            # Check for telemetry specification
            if "telemetry" in contract:
                telemetry = contract["telemetry"]
                if "spans" in telemetry:
                    print(f"  ✅ Found {len(telemetry['spans'])} telemetry span specifications")
                else:
                    print("  ⚠️ No span specifications in telemetry section")

                if "opentelemetry_semconv_version" in telemetry:
                    version = telemetry["opentelemetry_semconv_version"]
                    print(f"  ✅ OpenTelemetry semconv version: {version}")
                else:
                    print("  ⚠️ No semconv version specified")
            else:
                print("  ⚠️ No telemetry section in contract")

            print("  ✅ Matrix contract loaded successfully")
            return True
        else:
            print(f"  ⚠️ Matrix contract not found at {contract_path}")
            return True  # Not a hard failure

    except Exception as e:
        print(f"  ❌ Matrix contract validation failed: {e}")
        return False


def validate_test_discovery():
    """Validate that pytest can discover telemetry tests."""
    print("\n🔍 Validating test discovery...")

    try:
        test_files = ["test_authz_spans.py", "test_authz_attributes.py", "test_authz_integration.py"]

        for test_file in test_files:
            test_path = Path(__file__).parent / test_file
            if test_path.exists():
                print(f"  ✅ Found {test_file}")
            else:
                print(f"  ❌ Missing {test_file}")
                return False

        print("  ✅ All telemetry test files found")
        return True

    except Exception as e:
        print(f"  ❌ Test discovery validation failed: {e}")
        return False


def main():
    """Run all validation checks."""
    print("🚀 Telemetry Smoke Test Setup Validation")
    print("=" * 50)

    validations = [
        validate_imports,
        validate_fixtures,
        validate_authorization_middleware,
        validate_matrix_contract,
        validate_test_discovery,
    ]

    all_passed = True
    for validation in validations:
        if not validation():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validations passed! Telemetry test setup is ready.")
        print("\nTo run telemetry tests:")
        print("  cd tests/telemetry")
        print("  python -m pytest -v -m telemetry")
        return 0
    else:
        print("❌ Some validations failed. Please fix issues before running tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
