"""
verifier_test_suite.py

Automated tests for verifying CollapseHash signature validation and error handling.

Author: LUKHAS AGI Core
"""

import json
from pathlib import Path

from verifold_verifier import verify_verifold_signature

TEST_VECTOR_FILE = Path(__file__).parent / "test_vectors.json"


def load_test_vectors() -> list:
    with open(TEST_VECTOR_FILE) as f:
        data = json.load(f)
    return data.get("test_vectors", [])


def run_signature_tests():
    vectors = load_test_vectors()
    total = 0
    passed = 0
    failed = 0

    for idx, vector in enumerate(vectors):
        desc = vector.get("description", f"Test #{idx}")
        expected_verified = vector["expected_output"].get("verified")
        input_data = vector["input"]
        expected_error = vector["expected_output"].get("verification_error", "")

        if "hash" in vector["expected_output"]:
            hash_value = vector["expected_output"]["hash"]
            signature = vector["expected_output"]["signature"]
            pubkey = vector["expected_output"]["public_key"]

            try:
                is_valid = verify_verifold_signature(hash_value, signature, pubkey)
                if is_valid == expected_verified:
                    print(f"✅ PASS: {desc}")
                    passed += 1
                else:
                    print(
                        f"❌ FAIL: {desc} (expected: {expected_verified}, got: {is_valid})"
                    )
                    failed += 1
            except Exception as e:
                if expected_error and expected_error.lower() in str(e).lower():
                    print(f"✅ PASS (expected failure): {desc} -> {e}")
                    passed += 1
                else:
                    print(f"❌ FAIL (unexpected error): {desc} -> {e}")
                    failed += 1
        else:
            print(f"⚠️ SKIPPED: {desc} (no signature verification target)")
            continue

        total += 1

    print("\n📊 Test Summary")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")


if __name__ == "__main__":
    run_signature_tests()
