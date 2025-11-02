#!/usr/bin/env python3
"""
Comprehensive tests for encryption algorithm types and metadata.

Tests all aspects of the type-safe encryption algorithm system including:
- Algorithm enumeration
- Metadata accuracy and completeness
- Utility functions
- Validation logic
- Type safety

Constellation Framework: 🛡️ Guardian Excellence - Encryption Types Testing

Related Issues:
- #614: Define EncryptionAlgorithm Enum (P2 - PREREQUISITE for #613)
"""

import unittest
from dataclasses import fields

from core.security.encryption_types import (
    ALGORITHM_METADATA,
    AlgorithmMetadata,
    EncryptionAlgorithm,
    SecurityLevel,
    get_algorithm_metadata,
    get_post_quantum_algorithms,
    get_recommended_algorithms,
    is_aead_algorithm,
    validate_algorithm_choice,
)


class TestEncryptionAlgorithm(unittest.TestCase):
    """Test EncryptionAlgorithm enum."""

    def test_enum_values(self):
        """Test that all expected algorithms are defined."""
        expected_algorithms = {
            "aes-256-gcm",
            "chacha20-poly1305",
            "aes-256-cbc",
            "kyber768",
            "kyber1024",
        }

        actual_algorithms = {algo.value for algo in EncryptionAlgorithm}

        self.assertEqual(expected_algorithms, actual_algorithms, "Algorithm enum should contain all expected values")

    def test_enum_is_string_type(self):
        """Test that enum values are strings for serialization."""
        for algo in EncryptionAlgorithm:
            self.assertIsInstance(algo.value, str, f"{algo.name} value should be a string")

    def test_enum_member_access(self):
        """Test direct member access to algorithms."""
        # Test accessing each algorithm by name
        self.assertEqual(EncryptionAlgorithm.AES_256_GCM.value, "aes-256-gcm")
        self.assertEqual(EncryptionAlgorithm.CHACHA20_POLY1305.value, "chacha20-poly1305")
        self.assertEqual(EncryptionAlgorithm.AES_256_CBC.value, "aes-256-cbc")
        self.assertEqual(EncryptionAlgorithm.KYBER768.value, "kyber768")
        self.assertEqual(EncryptionAlgorithm.KYBER1024.value, "kyber1024")

    def test_enum_from_value(self):
        """Test constructing enum from string value."""
        algo = EncryptionAlgorithm("aes-256-gcm")
        self.assertEqual(algo, EncryptionAlgorithm.AES_256_GCM)

    def test_enum_comparison(self):
        """Test enum comparison operations."""
        algo1 = EncryptionAlgorithm.AES_256_GCM
        algo2 = EncryptionAlgorithm.AES_256_GCM
        algo3 = EncryptionAlgorithm.CHACHA20_POLY1305

        self.assertEqual(algo1, algo2)
        self.assertNotEqual(algo1, algo3)

    def test_enum_hash(self):
        """Test that enum members are hashable (for dict keys)."""
        algo_set = {
            EncryptionAlgorithm.AES_256_GCM,
            EncryptionAlgorithm.CHACHA20_POLY1305,
        }
        self.assertEqual(len(algo_set), 2)

        # Test as dict key
        algo_dict = {
            EncryptionAlgorithm.AES_256_GCM: "value1",
            EncryptionAlgorithm.CHACHA20_POLY1305: "value2",
        }
        self.assertEqual(len(algo_dict), 2)


class TestSecurityLevel(unittest.TestCase):
    """Test SecurityLevel enum."""

    def test_security_levels_defined(self):
        """Test that all security levels are defined."""
        expected_levels = {"legacy", "standard", "high", "post-quantum"}
        actual_levels = {level.value for level in SecurityLevel}

        self.assertEqual(expected_levels, actual_levels, "SecurityLevel should contain all expected values")

    def test_security_level_ordering(self):
        """Test that security levels have meaningful names."""
        # Just verify they exist and are accessible
        self.assertEqual(SecurityLevel.LEGACY.value, "legacy")
        self.assertEqual(SecurityLevel.STANDARD.value, "standard")
        self.assertEqual(SecurityLevel.HIGH.value, "high")
        self.assertEqual(SecurityLevel.POST_QUANTUM.value, "post-quantum")


class TestAlgorithmMetadata(unittest.TestCase):
    """Test AlgorithmMetadata dataclass."""

    def test_metadata_is_frozen(self):
        """Test that metadata instances are immutable."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.AES_256_GCM]

        with self.assertRaises(Exception):
            metadata.key_size = 512  # Should fail - frozen dataclass

    def test_metadata_has_all_required_fields(self):
        """Test that metadata has all required fields."""
        required_fields = {
            "name",
            "key_size",
            "nonce_size",
            "tag_size",
            "block_size",
            "pq_resistant",
            "security_level",
            "aead",
            "recommended",
            "description",
            "performance_tier",
        }

        actual_fields = {field.name for field in fields(AlgorithmMetadata)}

        self.assertEqual(required_fields, actual_fields, "AlgorithmMetadata should have all required fields")

    def test_metadata_field_types(self):
        """Test that metadata fields have correct types."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.AES_256_GCM]

        self.assertIsInstance(metadata.name, str)
        self.assertIsInstance(metadata.key_size, int)
        self.assertIsInstance(metadata.nonce_size, int)
        self.assertIsInstance(metadata.tag_size, int)
        self.assertIsInstance(metadata.pq_resistant, bool)
        self.assertIsInstance(metadata.security_level, SecurityLevel)
        self.assertIsInstance(metadata.aead, bool)
        self.assertIsInstance(metadata.recommended, bool)
        self.assertIsInstance(metadata.description, str)
        self.assertIsInstance(metadata.performance_tier, int)


class TestAlgorithmMetadataRegistry(unittest.TestCase):
    """Test ALGORITHM_METADATA registry completeness and accuracy."""

    def test_all_algorithms_have_metadata(self):
        """Test that all algorithms have metadata defined."""
        for algo in EncryptionAlgorithm:
            self.assertIn(algo, ALGORITHM_METADATA, f"Algorithm {algo.name} should have metadata")

    def test_aes_256_gcm_metadata(self):
        """Test AES-256-GCM metadata accuracy."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.AES_256_GCM]

        self.assertEqual(metadata.name, "AES-256-GCM")
        self.assertEqual(metadata.key_size, 256)
        self.assertEqual(metadata.nonce_size, 12)  # 96 bits
        self.assertEqual(metadata.tag_size, 16)  # 128 bits
        self.assertEqual(metadata.block_size, 16)  # 128-bit blocks
        self.assertFalse(metadata.pq_resistant)
        self.assertEqual(metadata.security_level, SecurityLevel.STANDARD)
        self.assertTrue(metadata.aead)
        self.assertTrue(metadata.recommended)
        self.assertIsInstance(metadata.description, str)
        self.assertGreater(len(metadata.description), 50)
        self.assertEqual(metadata.performance_tier, 5)

    def test_chacha20_poly1305_metadata(self):
        """Test ChaCha20-Poly1305 metadata accuracy."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.CHACHA20_POLY1305]

        self.assertEqual(metadata.name, "ChaCha20-Poly1305")
        self.assertEqual(metadata.key_size, 256)
        self.assertEqual(metadata.nonce_size, 12)  # 96 bits
        self.assertEqual(metadata.tag_size, 16)  # 128 bits
        self.assertIsNone(metadata.block_size)  # Stream cipher
        self.assertFalse(metadata.pq_resistant)
        self.assertEqual(metadata.security_level, SecurityLevel.STANDARD)
        self.assertTrue(metadata.aead)
        self.assertTrue(metadata.recommended)
        self.assertIsInstance(metadata.description, str)
        self.assertGreater(len(metadata.description), 50)
        self.assertEqual(metadata.performance_tier, 4)

    def test_aes_256_cbc_metadata(self):
        """Test AES-256-CBC metadata accuracy (legacy)."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.AES_256_CBC]

        self.assertEqual(metadata.name, "AES-256-CBC")
        self.assertEqual(metadata.key_size, 256)
        self.assertEqual(metadata.nonce_size, 16)  # 128-bit IV
        self.assertEqual(metadata.tag_size, 0)  # No built-in auth
        self.assertEqual(metadata.block_size, 16)
        self.assertFalse(metadata.pq_resistant)
        self.assertEqual(metadata.security_level, SecurityLevel.LEGACY)
        self.assertFalse(metadata.aead)
        self.assertFalse(metadata.recommended)
        self.assertIsInstance(metadata.description, str)
        self.assertIn("legacy", metadata.description.lower())

    def test_kyber768_metadata(self):
        """Test Kyber768 metadata accuracy (post-quantum)."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.KYBER768]

        self.assertEqual(metadata.name, "Kyber768")
        self.assertEqual(metadata.key_size, 768)
        self.assertEqual(metadata.nonce_size, 32)
        self.assertEqual(metadata.tag_size, 0)  # KEM, not AEAD
        self.assertIsNone(metadata.block_size)  # Not applicable to KEMs
        self.assertTrue(metadata.pq_resistant)
        self.assertEqual(metadata.security_level, SecurityLevel.POST_QUANTUM)
        self.assertFalse(metadata.aead)  # KEM, not AEAD
        self.assertFalse(metadata.recommended)  # Experimental
        self.assertIsInstance(metadata.description, str)
        self.assertIn("post-quantum", metadata.description.lower())

    def test_kyber1024_metadata(self):
        """Test Kyber1024 metadata accuracy (post-quantum)."""
        metadata = ALGORITHM_METADATA[EncryptionAlgorithm.KYBER1024]

        self.assertEqual(metadata.name, "Kyber1024")
        self.assertEqual(metadata.key_size, 1024)
        self.assertEqual(metadata.nonce_size, 32)
        self.assertEqual(metadata.tag_size, 0)  # KEM, not AEAD
        self.assertIsNone(metadata.block_size)  # Not applicable to KEMs
        self.assertTrue(metadata.pq_resistant)
        self.assertEqual(metadata.security_level, SecurityLevel.POST_QUANTUM)
        self.assertFalse(metadata.aead)  # KEM, not AEAD
        self.assertFalse(metadata.recommended)  # Experimental
        self.assertIsInstance(metadata.description, str)
        self.assertIn("post-quantum", metadata.description.lower())

    def test_metadata_descriptions_non_empty(self):
        """Test that all metadata descriptions are meaningful."""
        for algo, metadata in ALGORITHM_METADATA.items():
            self.assertIsInstance(metadata.description, str)
            self.assertGreater(
                len(metadata.description), 50, f"{algo.name} description should be meaningful (>50 chars)"
            )

    def test_performance_tiers_in_valid_range(self):
        """Test that performance tiers are in valid range 1-5."""
        for algo, metadata in ALGORITHM_METADATA.items():
            self.assertGreaterEqual(metadata.performance_tier, 1, f"{algo.name} performance tier should be >= 1")
            self.assertLessEqual(metadata.performance_tier, 5, f"{algo.name} performance tier should be <= 5")


class TestGetAlgorithmMetadata(unittest.TestCase):
    """Test get_algorithm_metadata function."""

    def test_get_metadata_for_valid_algorithm(self):
        """Test getting metadata for valid algorithm."""
        metadata = get_algorithm_metadata(EncryptionAlgorithm.AES_256_GCM)
        self.assertIsInstance(metadata, AlgorithmMetadata)
        self.assertEqual(metadata.name, "AES-256-GCM")

    def test_get_metadata_returns_same_instance(self):
        """Test that function returns registry instance."""
        metadata1 = get_algorithm_metadata(EncryptionAlgorithm.AES_256_GCM)
        metadata2 = ALGORITHM_METADATA[EncryptionAlgorithm.AES_256_GCM]
        self.assertIs(metadata1, metadata2)


class TestGetRecommendedAlgorithms(unittest.TestCase):
    """Test get_recommended_algorithms function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        recommended = get_recommended_algorithms()
        self.assertIsInstance(recommended, list)

    def test_all_recommended_algorithms_included(self):
        """Test that all recommended algorithms are returned."""
        recommended = get_recommended_algorithms()

        # Verify expected recommended algorithms
        self.assertIn(EncryptionAlgorithm.AES_256_GCM, recommended)
        self.assertIn(EncryptionAlgorithm.CHACHA20_POLY1305, recommended)

        # Verify non-recommended algorithms are excluded
        self.assertNotIn(EncryptionAlgorithm.AES_256_CBC, recommended)
        self.assertNotIn(EncryptionAlgorithm.KYBER768, recommended)

    def test_all_returned_algorithms_are_recommended(self):
        """Test that all returned algorithms have recommended=True."""
        recommended = get_recommended_algorithms()

        for algo in recommended:
            metadata = ALGORITHM_METADATA[algo]
            self.assertTrue(metadata.recommended, f"{algo.name} should be recommended")

    def test_at_least_one_recommended_algorithm(self):
        """Test that at least one algorithm is recommended."""
        recommended = get_recommended_algorithms()
        self.assertGreater(len(recommended), 0, "Should have at least one recommended algorithm")


class TestGetPostQuantumAlgorithms(unittest.TestCase):
    """Test get_post_quantum_algorithms function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        pq_algos = get_post_quantum_algorithms()
        self.assertIsInstance(pq_algos, list)

    def test_post_quantum_algorithms_included(self):
        """Test that post-quantum algorithms are returned."""
        pq_algos = get_post_quantum_algorithms()

        self.assertIn(EncryptionAlgorithm.KYBER768, pq_algos)
        self.assertIn(EncryptionAlgorithm.KYBER1024, pq_algos)

    def test_non_post_quantum_algorithms_excluded(self):
        """Test that non-post-quantum algorithms are excluded."""
        pq_algos = get_post_quantum_algorithms()

        self.assertNotIn(EncryptionAlgorithm.AES_256_GCM, pq_algos)
        self.assertNotIn(EncryptionAlgorithm.CHACHA20_POLY1305, pq_algos)
        self.assertNotIn(EncryptionAlgorithm.AES_256_CBC, pq_algos)

    def test_all_returned_algorithms_are_post_quantum(self):
        """Test that all returned algorithms have pq_resistant=True."""
        pq_algos = get_post_quantum_algorithms()

        for algo in pq_algos:
            metadata = ALGORITHM_METADATA[algo]
            self.assertTrue(metadata.pq_resistant, f"{algo.name} should be post-quantum resistant")

    def test_post_quantum_count(self):
        """Test that we have the expected number of post-quantum algorithms."""
        pq_algos = get_post_quantum_algorithms()
        self.assertEqual(len(pq_algos), 2, "Should have exactly 2 post-quantum algorithms (Kyber768, Kyber1024)")


class TestIsAeadAlgorithm(unittest.TestCase):
    """Test is_aead_algorithm function."""

    def test_aead_algorithms_return_true(self):
        """Test that AEAD algorithms return True."""
        self.assertTrue(is_aead_algorithm(EncryptionAlgorithm.AES_256_GCM))
        self.assertTrue(is_aead_algorithm(EncryptionAlgorithm.CHACHA20_POLY1305))

    def test_non_aead_algorithms_return_false(self):
        """Test that non-AEAD algorithms return False."""
        self.assertFalse(is_aead_algorithm(EncryptionAlgorithm.AES_256_CBC))
        self.assertFalse(is_aead_algorithm(EncryptionAlgorithm.KYBER768))
        self.assertFalse(is_aead_algorithm(EncryptionAlgorithm.KYBER1024))

    def test_return_type_is_bool(self):
        """Test that function returns boolean."""
        result = is_aead_algorithm(EncryptionAlgorithm.AES_256_GCM)
        self.assertIsInstance(result, bool)


class TestValidateAlgorithmChoice(unittest.TestCase):
    """Test validate_algorithm_choice function."""

    def test_valid_algorithm_default_settings(self):
        """Test validation with default settings (require AEAD, no legacy)."""
        # AES-GCM should be valid
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.AES_256_GCM)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # ChaCha20-Poly1305 should be valid
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.CHACHA20_POLY1305)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_non_aead_fails_with_require_aead(self):
        """Test that non-AEAD algorithms fail when AEAD is required."""
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.AES_256_CBC, require_aead=True)
        self.assertFalse(valid)
        self.assertIsInstance(error, str)
        self.assertIn("not AEAD", error)

    def test_non_aead_passes_without_require_aead(self):
        """Test that non-AEAD algorithms pass when AEAD is not required."""
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.KYBER768, require_aead=False, allow_legacy=False)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_legacy_fails_without_allow_legacy(self):
        """Test that legacy algorithms fail when not allowed."""
        valid, error = validate_algorithm_choice(
            EncryptionAlgorithm.AES_256_CBC, require_aead=False, allow_legacy=False
        )
        self.assertFalse(valid)
        self.assertIsInstance(error, str)
        self.assertIn("legacy", error.lower())

    def test_legacy_passes_with_allow_legacy(self):
        """Test that legacy algorithms pass when allowed."""
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.AES_256_CBC, require_aead=False, allow_legacy=True)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_post_quantum_validation(self):
        """Test validation of post-quantum algorithms."""
        # Kyber768 should pass with relaxed settings
        valid, error = validate_algorithm_choice(EncryptionAlgorithm.KYBER768, require_aead=False, allow_legacy=False)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_return_type(self):
        """Test that function returns tuple of (bool, Optional[str])."""
        result = validate_algorithm_choice(EncryptionAlgorithm.AES_256_GCM)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertTrue(result[1] is None or isinstance(result[1], str))


class TestTypeSafety(unittest.TestCase):
    """Test type safety features."""

    def test_cannot_create_invalid_enum_value(self):
        """Test that invalid enum values raise errors."""
        with self.assertRaises(ValueError):
            EncryptionAlgorithm("invalid-algorithm")

    def test_enum_in_function_signatures(self):
        """Test that functions accept only EncryptionAlgorithm enum."""
        # Valid enum should work
        metadata = get_algorithm_metadata(EncryptionAlgorithm.AES_256_GCM)
        self.assertIsInstance(metadata, AlgorithmMetadata)

        # String should fail at type-checking level (runtime may vary)
        # This documents the expected behavior for type checkers

    def test_metadata_registry_keys_are_enums(self):
        """Test that registry keys are EncryptionAlgorithm enums."""
        for key in ALGORITHM_METADATA.keys():
            self.assertIsInstance(key, EncryptionAlgorithm)

    def test_algorithm_comparison_type_safety(self):
        """Test that algorithm comparisons are type-safe."""
        algo = EncryptionAlgorithm.AES_256_GCM

        # Should be able to compare with same enum
        self.assertTrue(algo == EncryptionAlgorithm.AES_256_GCM)
        self.assertFalse(algo == EncryptionAlgorithm.CHACHA20_POLY1305)

        # String comparison returns True due to str inheritance (Python Enum behavior)
        # But .value should be used for string comparison in practice
        self.assertEqual(algo.value, "aes-256-gcm")
        self.assertNotEqual(algo.value, "invalid")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete encryption types system."""

    def test_complete_workflow_aes_gcm(self):
        """Test complete workflow for AES-256-GCM."""
        # 1. Select algorithm
        algorithm = EncryptionAlgorithm.AES_256_GCM

        # 2. Validate choice
        valid, error = validate_algorithm_choice(algorithm)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # 3. Get metadata
        metadata = get_algorithm_metadata(algorithm)
        self.assertEqual(metadata.name, "AES-256-GCM")

        # 4. Verify it's AEAD
        self.assertTrue(is_aead_algorithm(algorithm))

        # 5. Verify it's recommended
        self.assertIn(algorithm, get_recommended_algorithms())

        # 6. Verify it's not post-quantum
        self.assertNotIn(algorithm, get_post_quantum_algorithms())

    def test_complete_workflow_kyber768(self):
        """Test complete workflow for Kyber768 (post-quantum)."""
        # 1. Select algorithm
        algorithm = EncryptionAlgorithm.KYBER768

        # 2. Validate choice (relaxed settings for KEMs)
        valid, error = validate_algorithm_choice(algorithm, require_aead=False, allow_legacy=False)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # 3. Get metadata
        metadata = get_algorithm_metadata(algorithm)
        self.assertEqual(metadata.name, "Kyber768")
        self.assertTrue(metadata.pq_resistant)

        # 4. Verify it's not AEAD (it's a KEM)
        self.assertFalse(is_aead_algorithm(algorithm))

        # 5. Verify it's not recommended (experimental)
        self.assertNotIn(algorithm, get_recommended_algorithms())

        # 6. Verify it's post-quantum
        self.assertIn(algorithm, get_post_quantum_algorithms())

    def test_selecting_recommended_algorithm(self):
        """Test workflow for selecting a recommended algorithm."""
        # Get all recommended algorithms
        recommended = get_recommended_algorithms()
        self.assertGreater(len(recommended), 0)

        # Select first recommended algorithm
        algorithm = recommended[0]

        # It should validate with strict settings
        valid, error = validate_algorithm_choice(algorithm)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # Get its metadata
        metadata = get_algorithm_metadata(algorithm)
        self.assertTrue(metadata.recommended)
        self.assertTrue(metadata.aead)

    def test_legacy_algorithm_rejection(self):
        """Test that legacy algorithms are properly rejected."""
        algorithm = EncryptionAlgorithm.AES_256_CBC

        # Should fail with default settings
        valid, error = validate_algorithm_choice(algorithm)
        self.assertFalse(valid)
        self.assertIsInstance(error, str)

        # Should pass with allow_legacy=True
        valid, error = validate_algorithm_choice(algorithm, require_aead=False, allow_legacy=True)
        self.assertTrue(valid)
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
