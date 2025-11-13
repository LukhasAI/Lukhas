"""
Unit tests for the Operational Event Signing Script.
"""

import hashlib
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the script's directory to the Python path to allow for direct import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scripts/identity")))

import sign_ops_events


class TestSignOpsEvents(unittest.TestCase):
    """Test suite for the sign_ops_events script."""

    def setUp(self):
        """Set up test environment; create dummy files."""
        self.test_input_dir = "test_data_temp"
        os.makedirs(self.test_input_dir, exist_ok=True)

        self.input_file_path = os.path.join(self.test_input_dir, "release_notes.md")
        self.output_file_path = os.path.join(self.test_input_dir, "release_notes.json")
        self.file_content = "## Release v1.2.3\n\n- New feature: QRG signing.\n"

        with open(self.input_file_path, "w", encoding="utf-8") as f:
            f.write(self.file_content)

        self.user_identity = "test-release-manager"

    def tearDown(self):
        """Clean up test environment; remove dummy files."""
        if os.path.exists(self.input_file_path):
            os.remove(self.input_file_path)
        if os.path.exists(self.output_file_path):
            os.remove(self.output_file_path)
        if os.path.exists(self.test_input_dir):
            os.rmdir(self.test_input_dir)

    @patch("sign_ops_events.QIResonanceGlyph")
    def test_sign_event_file_success(self, MockQIResonanceGlyph):
        """
        Verify that sign_event_file correctly generates a signed artifact dictionary.
        """
        # Configure the mock to return a predictable object
        mock_glyph_instance = MagicMock()
        mock_glyph_instance.to_dict.return_value = {"glyph_id": "fake-glyph-id"}
        MockQIResonanceGlyph.return_value.generate_auth_glyph.return_value = mock_glyph_instance

        # Call the function under test
        artifact = sign_ops_events.sign_event_file(
            self.input_file_path, self.user_identity
        )

        # Assert the artifact structure and content
        self.assertIn("signer_identity", artifact)
        self.assertEqual(artifact["signer_identity"], self.user_identity)

        self.assertIn("timestamp_utc", artifact)
        self.assertIn("content_sha256", artifact)
        self.assertEqual(
            artifact["content_sha256"],
            hashlib.sha256(self.file_content.encode("utf-8")).hexdigest(),
        )

        self.assertIn("signature", artifact)
        self.assertEqual(artifact["signature"]["glyph_id"], "fake-glyph-id")

        self.assertIn("original_content", artifact)
        self.assertEqual(artifact["original_content"], self.file_content)

        # Verify that the mock was called correctly
        mock_generator = MockQIResonanceGlyph.return_value
        mock_generator.generate_auth_glyph.assert_called_once()


    def test_sign_event_file_not_found(self):
        """
        Test that sign_event_file returns None if the input file does not exist.
        """
        result = sign_ops_events.sign_event_file("non_existent_file.md", self.user_identity)
        self.assertIsNone(result)

    @patch("sign_ops_events.sign_event_file")
    def test_main_function_e2e(self, mock_sign_event_file):
        """
        Test the main function's argument parsing and file writing logic.
        """
        # Mock the return value of the core signing logic
        mock_artifact = {"status": "success"}
        mock_sign_event_file.return_value = mock_artifact

        # Simulate command-line arguments
        test_args = [
            "sign_ops_events.py",
            "--input-file", self.input_file_path,
            "--output-file", self.output_file_path,
            "--user-identity", self.user_identity,
        ]

        with patch.object(sys, "argv", test_args):
            sign_ops_events.main()

        # Verify that the signing function was called with correct args
        mock_sign_event_file.assert_called_with(
            self.input_file_path, self.user_identity
        )

        # Verify that the output file was written correctly
        self.assertTrue(os.path.exists(self.output_file_path))
        with open(self.output_file_path, "r", encoding="utf-8") as f:
            written_data = json.load(f)
        self.assertEqual(written_data, mock_artifact)


if __name__ == "__main__":
    unittest.main()
