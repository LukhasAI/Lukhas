#!/usr/bin/env python3

"""
GDPR Erasure Validation Test Runner
==================================

Runs comprehensive GDPR Right-to-Erasure validation tests
for Guardian Security compliance.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.gdpr.test_erasure_validation import GDPRErasureValidator, MockDataStore


async def run_comprehensive_gdpr_tests():
    """Run comprehensive GDPR erasure validation tests"""

    print("🛡️ GDPR Right-to-Erasure Comprehensive Validation")
    print("=" * 60)

    all_passed = True

    # Test 1: Single user complete erasure
    print("\n🔹 Test 1: Single User Complete Erasure")
    store = MockDataStore()
    validator = GDPRErasureValidator(store)

    try:
        result = await validator.validate_complete_erasure("test_user_001")
        compliance = result["compliance_assessment"]

        if compliance["compliance_score"] >= 0.95 and compliance["erasure_completeness"]:
            print("  ✅ PASSED - Complete erasure with full compliance")
        else:
            print(
                f"  ❌ FAILED - Score: {compliance['compliance_score']}, Complete: {compliance['erasure_completeness']}"
            )
            all_passed = False

    finally:
        store.cleanup()

    # Test 2: Multiple users isolation
    print("\n🔹 Test 2: Multi-User Data Isolation")
    store = MockDataStore()
    validator = GDPRErasureValidator(store)

    try:
        # Create data for multiple users
        users = ["user_a", "user_b", "user_c"]
        for user in users:
            store.insert_test_user_data(user)

        # Erase only user_b
        store.erase_user_data("user_b")

        # Verify user_b is erased but others remain
        verification_b = store.verify_user_data_erased("user_b")
        verification_a = store.verify_user_data_erased("user_a")
        verification_c = store.verify_user_data_erased("user_c")

        b_erased = verification_b["akaq_scene_remaining"] == 0
        a_intact = verification_a["akaq_scene_remaining"] > 0
        c_intact = verification_c["akaq_scene_remaining"] > 0

        if b_erased and a_intact and c_intact:
            print("  ✅ PASSED - User isolation maintained during erasure")
        else:
            print(f"  ❌ FAILED - B erased: {b_erased}, A intact: {a_intact}, C intact: {c_intact}")
            all_passed = False

    finally:
        store.cleanup()

    # Test 3: Shadow data detection
    print("\n🔹 Test 3: Shadow Data Detection")
    store = MockDataStore()
    validator = GDPRErasureValidator(store)

    try:
        user_id = "shadow_user"

        # Insert shadow reference in vector metadata
        cursor = store.connection.cursor()
        cursor.execute(
            "INSERT INTO vector_cache (id, user_id, embedding_key, vector_data, metadata, expiry) VALUES (?, ?, ?, ?, ?, ?)",
            ("shadow_test", "other_user", "key", b"data", f'{{"leaked_user": "{user_id}"}}', 9999999999),
        )
        store.connection.commit()

        # Perform erasure validation
        result = await validator.validate_complete_erasure(user_id)
        compliance = result["compliance_assessment"]

        # Should detect shadow violations
        shadow_violations = [v for v in compliance["violations"] if v["type"] == "shadow_references"]

        if len(shadow_violations) > 0:
            print("  ✅ PASSED - Shadow data detected and flagged")
        else:
            print("  ❌ FAILED - Shadow data not detected")
            all_passed = False

    finally:
        store.cleanup()

    # Test 4: Cascade deletion verification
    print("\n🔹 Test 4: Cascade Deletion Verification")
    store = MockDataStore()
    validator = GDPRErasureValidator(store)

    try:
        user_id = "cascade_user"
        footprint = store.insert_test_user_data(user_id)

        # Verify initial data exists
        initial_scenes = len(footprint.aka_qualia_scenes)
        initial_glyphs = len(footprint.aka_qualia_glyphs)

        # Perform erasure
        erasure_counts = store.erase_user_data(user_id)

        # Verify cascade worked
        scenes_erased = erasure_counts["akaq_scene"]
        glyphs_erased = erasure_counts["akaq_glyph"]

        if scenes_erased == initial_scenes and glyphs_erased == initial_glyphs:
            print(f"  ✅ PASSED - Cascade deletion: {scenes_erased} scenes, {glyphs_erased} glyphs")
        else:
            print(f"  ❌ FAILED - Expected {initial_scenes}/{initial_glyphs}, got {scenes_erased}/{glyphs_erased}")
            all_passed = False

    finally:
        store.cleanup()

    # Test 5: Audit log anonymization
    print("\n🔹 Test 5: Audit Log Anonymization")
    store = MockDataStore()
    validator = GDPRErasureValidator(store)

    try:
        user_id = "audit_user"
        store.insert_test_user_data(user_id)

        # Erase user data
        erasure_counts = store.erase_user_data(user_id)
        verification = store.verify_user_data_erased(user_id)

        # Verify audit logs are anonymized, not deleted
        audit_anonymized = erasure_counts.get("audit_log_anonymized", 0) > 0
        audit_remaining = verification["audit_log_remaining"] == 0

        if audit_anonymized and audit_remaining:
            print("  ✅ PASSED - Audit logs properly anonymized")
        else:
            print(f"  ❌ FAILED - Anonymized: {audit_anonymized}, Remaining: {audit_remaining}")
            all_passed = False

    finally:
        store.cleanup()

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎯 ALL GDPR ERASURE VALIDATION TESTS PASSED")
        print("✅ System meets Guardian Security GDPR compliance requirements")
        print("✅ Right-to-Erasure implementation validated successfully")
        return 0
    else:
        print("❌ SOME GDPR TESTS FAILED")
        print("🚨 Guardian Security compliance requirements not met")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_comprehensive_gdpr_tests())
    sys.exit(exit_code)
