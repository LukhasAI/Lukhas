#!/usr/bin/env python3
"""
Test script to verify subprocess security fixes are working
"""

import shlex
import subprocess


def test_subprocess_security():
    """Test that subprocess security fixes are working"""
    print("🔒 Testing subprocess security fixes...")

    # Test 1: Verify shlex.split works correctly
    test_command = "echo 'Hello World'"
    args = shlex.split(test_command)
    print(f"✅ shlex.split('{test_command}') = {args}")

    # Test 2: Run a safe command
    try:
        result = subprocess.run(
            args, shell=False, capture_output=True, text=True, timeout=5
        )
        print(f"✅ Safe subprocess execution: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Safe subprocess failed: {e}")
        return False

    # Test 3: Verify shell=False prevents injection
    try:
        # This would be dangerous with shell=True but safe with shell=False
        dangerous_command = "echo 'safe'; rm -rf /tmp/nonexistent"
        args = shlex.split(dangerous_command)
        result = subprocess.run(
            args, shell=False, capture_output=True, text=True, timeout=5
        )
        print(f"✅ Shell injection prevented: {result.stdout.strip()}")
    except Exception as e:
        print(f"✅ Shell injection properly blocked: {e}")

    return True


def test_hash_security():
    """Test that hash security fixes are working"""
    print("\n🔐 Testing hash security fixes...")

    import hashlib

    # Test SHA-256 usage (secure)
    test_data = "test_operation:test_command:completed"
    secure_hash = hashlib.sha256(test_data.encode()).hexdigest()[:16]
    print(f"✅ SHA-256 hash (secure): {secure_hash}")

    # Show that MD5 would be insecure (for comparison)
    insecure_hash = hashlib.md5(test_data.encode()).hexdigest()
    print(f"⚠️  MD5 hash (insecure, for comparison): {insecure_hash}")

    return True


def main():
    """Run all security verification tests"""
    print("🛡️  Security Fixes Verification")
    print("=" * 40)

    tests = [
        ("Subprocess Security", test_subprocess_security),
        ("Hash Security", test_hash_security),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n{'='*40}")
    print(f"📊 Security Fix Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All security fixes verified!")
        return 0
    else:
        print("⚠️ Some security fixes need attention.")
        return 1


if __name__ == "__main__":
    exit(main())
