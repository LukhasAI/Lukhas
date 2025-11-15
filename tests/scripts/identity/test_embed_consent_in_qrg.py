"""
Unit Tests for the embed_consent_in_qrg script.

This test suite verifies the functionality of the consent hash generation and
its embedding into Quantum Resonance Glyphs (QRGs).
"""

import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add the script's directory to the Python path to allow for direct import
sys.path.insert(0, './scripts/identity')

# Mock the LUKHAS modules *before* importing the script
# This ensures the script's imports resolve to our mocks
mock_consent_manager = MagicMock()
@unittest.mock.patch('dataclasses.dataclass', lambda x: x)
class MockConsentRecord:
    def __init__(self, consent_id, user_id, purpose_id, granted_at, method, consent_text):
        self.consent_id = consent_id
        self.user_id = user_id
        self.purpose_id = purpose_id
        self.granted_at = granted_at
        self.method = method
        self.consent_text = consent_text
mock_consent_manager.ConsentRecord = MockConsentRecord

mock_qrg_core = MagicMock()
sys.modules['lukhas'] = MagicMock()
sys.modules['lukhas.governance'] = MagicMock()
sys.modules['lukhas.governance.consent'] = mock_consent_manager
sys.modules['lukhas.products'] = MagicMock()
sys.modules['lukhas.products.security'] = MagicMock()
sys.modules['lukhas.products.security.qrg'] = mock_qrg_core


import embed_consent_in_qrg


class TestEmbedConsentInQRG(unittest.TestCase):
    """Test cases for the QRG consent embedding script."""

    def setUp(self):
        """Set up test data."""
        self.user_id = "test_user_123"
        self.consent_id = "consent_abc_456"
        self.purpose_id = "core_functionality"
        self.timestamp = datetime(2025, 11, 12, 10, 0, 0)

        # We use the script's own mocked record for consistency in testing
        self.consent_record = embed_consent_in_qrg.MockConsentRecord(
            consent_id=self.consent_id,
            user_id=self.user_id,
            purpose_id=self.purpose_id,
            granted_at=self.timestamp,
            method="api_call",
            consent_text="I agree to the terms for core_functionality."
        )

    def test_generate_consent_hash_consistency(self):
        """
        Tests that the consent hash generation is consistent and produces
        the expected hash for a given record.
        """
        expected_hash = "95df9cd7a32c944618458174ab55d3e1776ca409cbf6fb869bf6c7766821ea3b"

        generated_hash = embed_consent_in_qrg.generate_consent_hash(self.consent_record)

        self.assertEqual(generated_hash, expected_hash)

    def test_generate_consent_hash_sensitivity(self):
        """
        Tests that any change in the consent record data results in a
        different hash.
        """
        original_hash = embed_consent_in_qrg.generate_consent_hash(self.consent_record)

        # Modify a field and re-hash
        modified_record = embed_consent_in_qrg.MockConsentRecord(
             consent_id=self.consent_id,
            user_id="a_different_user", # Changed field
            purpose_id=self.purpose_id,
            granted_at=self.timestamp,
            method="api_call",
            consent_text="I agree to the terms for core_functionality."
        )

        new_hash = embed_consent_in_qrg.generate_consent_hash(modified_record)

        self.assertNotEqual(original_hash, new_hash)

    @patch('embed_consent_in_qrg.QIResonanceGlyph')
    def test_embed_consent_in_qrg_workflow(self, mock_qrg_generator_class):
        """
        Tests the end-to-end workflow of embedding the consent hash into a QRG.
        """
        # --- Arrange ---
        # Mock the QRG generator and its methods
        mock_generator_instance = MagicMock()
        mock_base_glyph = MagicMock(glyph_id="base_glyph_1")
        mock_embedded_glyph = MagicMock(glyph_id="embedded_glyph_1")

        mock_generator_instance.generate_auth_glyph.return_value = mock_base_glyph
        mock_generator_instance.embed_hidden_data.return_value = mock_embedded_glyph
        mock_qrg_generator_class.return_value = mock_generator_instance

        # --- Act ---
        result_glyph = embed_consent_in_qrg.embed_consent_in_qrg(
            self.user_id, self.consent_record
        )

        # --- Assert ---
        # Verify that the QRG generator was instantiated and used correctly
        mock_qrg_generator_class.assert_called_once()
        mock_generator_instance.generate_auth_glyph.assert_called_once_with(
            user_identity=self.user_id
        )

        # Verify that the embedding method was called with the correct payload
        mock_generator_instance.embed_hidden_data.assert_called_once()

        # Inspect the arguments passed to embed_hidden_data
        _call_args, call_kwargs = mock_generator_instance.embed_hidden_data.call_args
        self.assertEqual(call_kwargs['glyph'], mock_base_glyph)

        hidden_payload = call_kwargs['hidden_payload']
        self.assertIn("claims", hidden_payload)

        claims = hidden_payload['claims']
        expected_hash = embed_consent_in_qrg.generate_consent_hash(self.consent_record)
        self.assertEqual(claims['consent_hash'], expected_hash)
        self.assertEqual(claims['consent_id'], self.consent_id)

        # Verify that the final, embedded glyph is returned
        self.assertEqual(result_glyph, mock_embedded_glyph)

if __name__ == '__main__':
    unittest.main()
