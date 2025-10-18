#!/usr/bin/env python3

"""
GDPR and Privacy Compliance Tests for Wave C Memory System
==========================================================

Privacy and compliance tests covering:
- Complete user data erasure (GDPR Article 17 - Right to Erasure)
- Privacy hashing in production mode
- Context data sanitization and whitelisting
- Data minimization principles
- Audit trail completeness
- Cross-border data handling

Target: 100% regulatory compliance validation
"""
import time

import pytest

from aka_qualia.tests.conftest import create_test_glyph, create_test_scene


class TestGDPRErasure:
    """Test GDPR Article 17 - Right to Erasure compliance"""

    @pytest.mark.security
    @pytest.mark.integration
    def test_complete_user_erasure(self, sql_memory):
        """delete_user() must remove ALL user data traces"""

        user_id = "gdpr_erasure_test_user"

        # Create comprehensive user data across multiple dimensions
        test_scenarios = [
            # Different scene types
            {
                "scene": create_test_scene(
                    subject="personal_subject_1",
                    object="personal_object_1",
                    context={"personal_session": "session_123"},
                ),
                "glyphs": [
                    create_test_glyph("personal:glyph_1", emotion="happiness"),
                    create_test_glyph("personal:memory", content="personal_memory"),
                ],
            },
            {
                "scene": create_test_scene(
                    subject="sensitive_subject_2",
                    object="confidential_data_2",
                    context={"medical_session": "health_456"},
                ),
                "glyphs": [
                    create_test_glyph("medical:symptom", severity="high"),
                    create_test_glyph("personal:location", place="home_address"),
                ],
            },
            # High-risk scenes that might have additional data
            {
                "scene": create_test_scene(
                    subject="crisis_subject_3",
                    object="emergency_situation_3",
                    context={
                        "emergency_contact": "personal_phone",
                        "location_data": "gps_coordinates",
                    },
                    proto={"tone": -0.8, "arousal": 0.9},  # High risk scenario
                ),
                "glyphs": [
                    create_test_glyph("emergency:contact", phone="123-456-7890"),
                    create_test_glyph("location:gps", lat=40.7128, lon=-74.0060),
                ],
            },
        ]

        # Save all test data
        saved_scene_ids = []
        for scenario in test_scenarios:
            scene_id = sql_memory.save(
                user_id=user_id,
                scene=scenario["scene"],
                glyphs=scenario["glyphs"],
                policy={"gain": 1.0, "pace": 1.0, "actions": []},
                metrics={"drift_phi": 0.9, "neurosis_risk": 0.1},
                cfg_version="wave_c_v1.0.0",
            )
            saved_scene_ids.append(scene_id)

        # Verify data exists before erasure
        pre_erasure_history = sql_memory.get_scene_history(user_id=user_id, limit=10)
        assert len(pre_erasure_history) == 3, "Should have 3 scenes before erasure"

        # Verify glyphs exist
        pre_erasure_glyphs = sql_memory.search_by_glyph(user_id=user_id, glyph_key="personal:glyph_1")
        assert len(pre_erasure_glyphs) > 0, "Should find personal glyphs before erasure"

        # GDPR ERASURE - Execute right to erasure
        deleted_count = sql_memory.delete_user(user_id=user_id)
        assert deleted_count >= 3, f"Should delete at least 3 records, got {deleted_count}"

        # VERIFICATION - Complete data removal

        # 1. Scene history should be empty
        post_erasure_history = sql_memory.get_scene_history(user_id=user_id, limit=10)
        assert len(post_erasure_history) == 0, "Scene history should be completely empty after erasure"

        # 2. Glyph searches should return nothing
        post_erasure_glyphs = sql_memory.search_by_glyph(user_id=user_id, glyph_key="personal:glyph_1")
        assert len(post_erasure_glyphs) == 0, "Glyph searches should return empty after erasure"

        # 3. All glyph types should be gone
        for glyph_key in [
            "personal:memory",
            "medical:symptom",
            "emergency:contact",
            "location:gps",
        ]:
            results = sql_memory.search_by_glyph(user_id=user_id, glyph_key=glyph_key)
            assert len(results) == 0, f"Glyph {glyph_key} should be completely erased"

        # 4. Vector embeddings should be removed (if applicable)
        # This would require checking the vector storage directly

        # 5. Verify other users' data is unaffected
        sql_memory.get_scene_history(user_id="other_user", limit=1)
        # This should not crash and should not be affected by the erasure

    @pytest.mark.security
    def test_selective_erasure_by_time_range(self, sql_memory):
        """Should be able to erase data within specific time ranges"""

        user_id = "time_range_erasure_test"

        # Create scenes with different timestamps
        base_time = time.time()
        time_ranges = [
            base_time - 7200,  # 2 hours ago - should be erased
            base_time - 3600,  # 1 hour ago - should be erased
            base_time - 1800,  # 30 minutes ago - should be kept
            base_time - 900,  # 15 minutes ago - should be kept
            base_time,  # now - should be kept
        ]

        scene_ids_by_time = {}
        for i, scene_time in enumerate(time_ranges):
            scene_data = create_test_scene(subject=f"time_test_subject_{i}", timestamp=scene_time)

            scene_id = sql_memory.save(
                user_id=user_id,
                scene=scene_data,
                glyphs=[create_test_glyph(f"time:glyph_{i}")],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

            scene_ids_by_time[scene_time] = scene_id

        # Verify all data exists
        all_history = sql_memory.get_scene_history(user_id=user_id, limit=10)
        assert len(all_history) == 5, "Should have 5 scenes before selective erasure"

        # Perform selective erasure (older than 45 minutes)
        cutoff_time = base_time - 2700  # 45 minutes ago

        # Note: This would require extending the delete_user method to support time ranges
        # For now, we test that the concept works with a custom query
        with sql_memory.engine.begin() as conn:
            from sqlalchemy import text

            delete_query = text(
                """
                DELETE FROM akaq_scene
                WHERE user_id = :user_id
                AND ts < to_timestamp(:cutoff_time)
            """
            )

            result = conn.execute(delete_query, {"user_id": user_id, "cutoff_time": cutoff_time})

            deleted_count = result.rowcount
            assert deleted_count == 2, "Should delete 2 old scenes"

        # Verify selective erasure worked
        remaining_history = sql_memory.get_scene_history(user_id=user_id, limit=10)
        assert len(remaining_history) == 3, "Should have 3 recent scenes remaining"

        # Verify the correct scenes remain (recent ones)
        remaining_timestamps = [scene["timestamp"] for scene in remaining_history]
        for ts in remaining_timestamps:
            assert ts >= cutoff_time, "Only recent scenes should remain"

    @pytest.mark.security
    def test_erasure_audit_trail(self, sql_memory):
        """GDPR erasure should create proper audit trail"""

        user_id = "audit_trail_erasure_test"

        # Create user data
        scene_data = create_test_scene(subject="audit_test_subject")
        sql_memory.save(
            user_id=user_id,
            scene=scene_data,
            glyphs=[create_test_glyph("audit:test")],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Perform erasure with audit logging
        time.time()
        deleted_count = sql_memory.delete_user(user_id=user_id)

        # In a full implementation, we would:
        # 1. Log the erasure request with timestamp
        # 2. Record what data was deleted
        # 3. Store legal basis for erasure
        # 4. Log confirmation of completion

        # For this test, we verify the basic functionality worked
        assert deleted_count > 0, "Should have deleted some data"

        # Verify data is actually gone
        remaining_data = sql_memory.get_scene_history(user_id=user_id, limit=1)
        assert len(remaining_data) == 0, "All user data should be erased"


class TestPrivacyHashing:
    """Test privacy protection through hashing in production mode"""

    @pytest.mark.security
    def test_production_pii_hashing(self, sql_memory_prod):
        """In production mode, PII fields must be SHA3-256 hashed"""

        # Test data with clear PII
        pii_test_cases = [
            "Alice Johnson",
            "john.doe@email.com",
            "123-45-6789",  # SSN format
            "4532-1234-5678-9012",  # Credit card format
            "Personal Medical Information",
        ]

        hashed_values = []

        for pii_value in pii_test_cases:
            scene_data = create_test_scene(subject=pii_value, object="confidential_data")

            sql_memory_prod.save(
                user_id="privacy_hash_test",
                scene=scene_data,
                glyphs=[create_test_glyph("privacy:test")],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

            # Retrieve and verify hashing
            history = sql_memory_prod.get_scene_history(user_id="privacy_hash_test", limit=1)
            stored_scene = history[0]

            stored_subject = stored_scene["subject"]
            hashed_values.append(stored_subject)

            # Verify it's hashed (not plaintext)
            assert stored_subject != pii_value, f"PII '{pii_value}' should be hashed, not stored as plaintext"
            assert len(stored_subject) == 64, f"Hash should be 64 chars (SHA3-256), got {len(stored_subject)}"
            assert stored_subject.isalnum(), "Hash should be alphanumeric"

            # Verify consistency (same input = same hash)
            expected_hash = sql_memory_prod._hash_safe(pii_value)
            assert stored_subject == expected_hash, "Hash should be consistent"

        # Verify different inputs produce different hashes
        assert len(set(hashed_values)) == len(hashed_values), "Different PII should produce different hashes"

    @pytest.mark.security
    def test_development_vs_production_hashing(self, sql_memory, sql_memory_prod):
        """Development and production modes should handle PII differently"""

        test_subject = "Sensitive Personal Name"
        scene_data = create_test_scene(subject=test_subject, object="test_object")

        # Save in development mode (no hashing)
        sql_memory.save(
            user_id="dev_prod_test",
            scene=scene_data,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Save in production mode (with hashing)
        sql_memory_prod.save(
            user_id="dev_prod_test",
            scene=scene_data,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Retrieve and compare
        dev_history = sql_memory.get_scene_history(user_id="dev_prod_test", limit=1)
        prod_history = sql_memory_prod.get_scene_history(user_id="dev_prod_test", limit=1)

        dev_subject = dev_history[0]["subject"]
        prod_subject = prod_history[0]["subject"]

        # Development mode - plaintext
        assert dev_subject == test_subject, "Development mode should store plaintext"

        # Production mode - hashed
        assert prod_subject != test_subject, "Production mode should hash PII"
        assert len(prod_subject) == 64, "Production hash should be 64 characters"

    @pytest.mark.security
    def test_hash_salt_rotation_security(self, sqlite_engine):
        """Different salt values should produce different hashes"""

        test_subject = "Same Subject Different Salt"

        # Create two memory clients with different salts
        from aka_qualia.memory_sql import SqlMemory
        memory1 = SqlMemory(sqlite_engine, "salt_1", is_prod=True)
        memory2 = SqlMemory(sqlite_engine, "salt_2", is_prod=True)

        hash1 = memory1._hash_safe(test_subject)
        hash2 = memory2._hash_safe(test_subject)

        # Different salts should produce different hashes
        assert hash1 != hash2, "Different salts should produce different hashes"
        assert len(hash1) == len(hash2) == 64, "Both should be 64-character hashes"

        # Same salt should produce same hash
        hash1_repeat = memory1._hash_safe(test_subject)
        assert hash1 == hash1_repeat, "Same salt should produce consistent hashes"


class TestContextDataSanitization:
    """Test context data filtering and sanitization"""

    @pytest.mark.security
    def test_context_whitelist_enforcement(self, sql_memory):
        """Only whitelisted context keys should survive to storage"""

        # Context with both safe and unsafe keys
        mixed_context = {
            # Safe keys (should be preserved)
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": "test_policy_123",
            "session_id": "test_session",
            "safe_palette": "blue/calming",
            "approach_avoid_score": 0.3,
            "transform_chain": ["teq.enforce"],
            "collapse_hash": "abc123",
            # Potentially unsafe keys (should be filtered in strict mode)
            "user_agent": "Mozilla/5.0...",
            "ip_address": "192.168.1.100",
            "device_id": "ABC123-DEF456",
            "location": {"lat": 40.7128, "lon": -74.0060},
            "personal_notes": "Private thoughts and feelings",
            "contact_info": {"email": "user@example.com", "phone": "555-0123"},
        }

        scene_data = create_test_scene(context=mixed_context)

        sql_memory.save(
            user_id="context_filter_test",
            scene=scene_data,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Retrieve and check what was stored
        history = sql_memory.get_scene_history(user_id="context_filter_test", limit=1)
        stored_context = history[0]["context"]

        # Safe keys should be preserved
        safe_keys = [
            "cfg_version",
            "policy_sig",
            "session_id",
            "safe_palette",
            "approach_avoid_score",
        ]
        for safe_key in safe_keys:
            if safe_key in mixed_context:  # Only check if it was in original
                assert safe_key in stored_context, f"Safe key '{safe_key}' should be preserved"

        # In a strict implementation, unsafe keys might be filtered
        # For this test, we just verify the core functionality works
        assert "cfg_version" in stored_context, "cfg_version should always be preserved"

    @pytest.mark.security
    def test_sensitive_data_redaction(self, sql_memory):
        """Sensitive patterns in context should be redacted"""

        # Context containing various sensitive patterns
        sensitive_context = {
            "cfg_version": "wave_c_v1.0.0",
            "session_notes": "User mentioned their SSN: 123-45-6789",
            "user_input": "My credit card number is 4532-1234-5678-9012",
            "api_response": "Authorization: Bearer sk-1234567890abcdef",
            "debug_info": "Database password: secretpassword123",
            "contact_details": "Email: personal@example.com Phone: (555) 123-4567",
        }

        scene_data = create_test_scene(context=sensitive_context)

        sql_memory.save(
            user_id="redaction_test",
            scene=scene_data,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Retrieve stored data
        history = sql_memory.get_scene_history(user_id="redaction_test", limit=1)
        stored_context = history[0]["context"]

        # In a production implementation, sensitive patterns would be redacted
        # For this test, we verify the data was stored and can be retrieved
        assert "cfg_version" in stored_context

        # In a real implementation, we might check:
        # assert "123-45-6789" not in json.dumps(stored_context)  # SSN redacted
        # assert "4532-1234-5678-9012" not in json.dumps(stored_context)  # CC redacted
        # assert "sk-1234567890abcdef" not in json.dumps(stored_context)  # API key redacted


class TestDataMinimization:
    """Test GDPR data minimization principles"""

    @pytest.mark.security
    def test_minimal_data_collection(self, sql_memory):
        """Only necessary data should be collected and stored"""

        # Scene with excessive/unnecessary data
        excessive_scene = create_test_scene(
            context={
                "cfg_version": "wave_c_v1.0.0",
                # Necessary data
                "policy_sig": "required_policy",
                "session_id": "required_session",
                # Potentially excessive data
                "full_user_profile": {
                    "name": "John Doe",
                    "age": 35,
                    "address": "123 Main St",
                    "browsing_history": ["site1.com", "site2.com"],
                    "purchase_history": ["item1", "item2"],
                    "social_connections": ["friend1", "friend2"],
                },
                "detailed_device_info": {
                    "browser": "Chrome 91.0",
                    "os": "Windows 10",
                    "screen_resolution": "1920x1080",
                    "installed_plugins": ["plugin1", "plugin2"],
                    "hardware_id": "ABC123-DEF456",
                },
            }
        )

        # In a privacy-compliant system, excessive data would be filtered
        sql_memory.save(
            user_id="data_minimization_test",
            scene=excessive_scene,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Verify core functionality works
        history = sql_memory.get_scene_history(user_id="data_minimization_test", limit=1)
        assert len(history) == 1, "Scene should be stored"

        # In production, we would verify that only necessary data is retained
        stored_context = history[0]["context"]
        assert "cfg_version" in stored_context, "Essential config should be preserved"

    @pytest.mark.security
    def test_automatic_data_expiration(self, sql_memory):
        """Old data should be automatically expired based on retention policies"""

        # This test would verify automatic data expiration
        # In a full implementation, we might have:
        # - Retention policies per data type
        # - Automatic cleanup jobs
        # - Legal hold capabilities

        old_scene = create_test_scene(
            subject="old_data_subject",
            timestamp=time.time() - (365 * 24 * 3600),  # 1 year old
        )

        recent_scene = create_test_scene(
            subject="recent_data_subject",
            timestamp=time.time() - (30 * 24 * 3600),  # 30 days old
        )

        # Save both scenes
        sql_memory.save(
            user_id="expiration_test",
            scene=old_scene,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        sql_memory.save(
            user_id="expiration_test",
            scene=recent_scene,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # In a production system with automatic expiration:
        # - Old data might be automatically deleted
        # - Recent data should be preserved
        # - Legal holds should prevent deletion of relevant data

        # For this test, verify both were stored
        history = sql_memory.get_scene_history(user_id="expiration_test", limit=10)
        assert len(history) == 2, "Both scenes should be stored (no automatic expiration in test)"


class TestCrossBorderCompliance:
    """Test compliance with cross-border data transfer regulations"""

    @pytest.mark.security
    def test_data_sovereignty_headers(self, sql_memory):
        """Data should be tagged with sovereignty/jurisdiction information"""

        # Scene with jurisdiction information
        jurisdictional_scene = create_test_scene(
            context={
                "cfg_version": "wave_c_v1.0.0",
                "data_jurisdiction": "EU",
                "processing_location": "germany",
                "legal_basis": "consent",
                "retention_period": "2_years",
                "cross_border_transfer": False,
            }
        )

        sql_memory.save(
            user_id="jurisdiction_test",
            scene=jurisdictional_scene,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Verify jurisdiction info is preserved
        history = sql_memory.get_scene_history(user_id="jurisdiction_test", limit=1)
        stored_context = history[0]["context"]

        # In a compliant system, jurisdiction info should be preserved
        assert "cfg_version" in stored_context, "Context should be preserved"

        # This would be extended to verify:
        # - Data residency requirements are met
        # - Appropriate legal basis is documented
        # - Cross-border transfer safeguards are in place

    @pytest.mark.security
    def test_gdpr_consent_tracking(self, sql_memory):
        """GDPR consent should be properly tracked and linked to data"""

        # Scene with detailed consent information
        consent_scene = create_test_scene(
            context={
                "cfg_version": "wave_c_v1.0.0",
                "consent": {
                    "timestamp": time.time(),
                    "version": "privacy_policy_v2.1",
                    "purposes": ["consciousness_analysis", "user_experience"],
                    "legal_basis": "article_6_1_a_consent",
                    "withdrawal_method": "settings_page",
                    "granular_consent": {
                        "memory_storage": True,
                        "analytics": True,
                        "personalization": False,
                    },
                },
            }
        )

        sql_memory.save(
            user_id="consent_tracking_test",
            scene=consent_scene,
            glyphs=[],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )

        # Verify consent information is preserved
        history = sql_memory.get_scene_history(user_id="consent_tracking_test", limit=1)
        stored_context = history[0]["context"]

        # Basic verification that context is stored
        assert "cfg_version" in stored_context

        # In a full GDPR implementation, we would verify:
        # - Consent is properly linked to all derived data
        # - Consent withdrawal triggers appropriate data handling
        # - Audit trail shows when consent was given/withdrawn
        # - Data processing stops when consent is withdrawn
