import asyncio
import os

# Ensure the root directory is in the Python path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from production_main import LUKHASProduction


class TestProductionMain(unittest.TestCase):
    @patch("production_main.initialize_branding")
    @patch("production_main.get_system_signature")
    @patch("production_main.get_trinity_context")
    @patch("production_main.uvicorn")
    def test_initialization(
        self,
        mock_uvicorn,
        mock_get_trinity_context,
        mock_get_system_signature,
        mock_initialize_branding,
    ):
        """Test that the LUKHASProduction class can be initialized."""
        # Arrange
        mock_initialize_branding.return_value = asyncio.Future()
        mock_initialize_branding.return_value.set_result(True)
        mock_get_system_signature.return_value = "Test Signature"
        mock_get_trinity_context.return_value = {"framework": "Test Framework"}

        # Act
        system = LUKHASProduction()
        initialized = asyncio.run(system.initialize_systems())

        # Assert
        self.assertTrue(initialized)
        self.assertEqual(system.system_health["status"], "operational")
        self.assertIn("branding", system.components)
        self.assertIn("consciousness", system.components)
        self.assertIn("memory", system.components)
        self.assertIn("identity", system.components)
        self.assertIn("governance", system.components)
        self.assertIn("creativity", system.components)
        self.assertIn("api_gateway", system.components)

    @patch("production_main.LUKHASProduction.start_api_server")
    @patch("production_main.LUKHASProduction.stop_systems")
    def test_main_function(self, mock_stop_systems, mock_start_api_server):
        """Test the main function runs without errors."""
        # Arrange
        mock_start_api_server.return_value = asyncio.Future()
        mock_start_api_server.return_value.set_result(None)

        # Act & Assert
        try:
            # We need to run the main function in a way that it doesn't block forever.
            # We can patch the start_api_server to not run indefinitely.
            from production_main import main

            exit_code = asyncio.run(main())
            self.assertEqual(exit_code, 0)
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
