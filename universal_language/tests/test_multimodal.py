#!/usr/bin/env python3
"""
Unit tests for the multimodal module in Universal Language.
"""

import unittest
from universal_language.multimodal import ModalityType, ModalityProcessor


class TestModalityProcessor(unittest.TestCase):
    """Tests for the ModalityProcessor class."""

    def setUp(self):
        """Set up a new ModalityProcessor for each test."""
        self.processor = ModalityProcessor()

    def test_process_text_modality(self):
        """Test processing of the TEXT modality."""
        data = "Hello, world!"
        result = self.processor.process(data, ModalityType.TEXT)
        self.assertEqual(result["modality"], "text")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertEqual(result["metadata"]["text_length"], 13)
        self.assertEqual(self.processor.get_processed_count(), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.TEXT), 1)

    def test_process_image_modality(self):
        """Test processing of the IMAGE modality."""
        data = {"path": "/images/test.png"}
        result = self.processor.process(data, ModalityType.IMAGE)
        self.assertEqual(result["modality"], "image")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertTrue(result["metadata"]["image_processed"])
        self.assertEqual(self.processor.get_processed_count(), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.IMAGE), 1)

    def test_process_audio_modality(self):
        """Test processing of the AUDIO modality."""
        data = {"format": "mp3", "duration": 300}
        result = self.processor.process(data, ModalityType.AUDIO)
        self.assertEqual(result["modality"], "audio")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertEqual(self.processor.get_processed_count(), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.AUDIO), 1)

    def test_process_video_modality(self):
        """Test processing of the VIDEO modality."""
        data = {"resolution": "1080p"}
        result = self.processor.process(data, ModalityType.VIDEO)
        self.assertEqual(result["modality"], "video")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertEqual(self.processor.get_processed_count(), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.VIDEO), 1)

    def test_process_color_modality_with_hex(self):
        """Test processing of the COLOR modality with a hex code."""
        data = "#FF0000"
        result = self.processor.process(data, ModalityType.COLOR)
        self.assertEqual(result["modality"], "color")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertTrue(result["metadata"]["color_processed"])
        self.assertTrue(result["metadata"]["hex_parsed"])
        self.assertEqual(self.processor.get_processed_count(ModalityType.COLOR), 1)

    def test_process_color_modality_without_hex(self):
        """Test processing of the COLOR modality without a hex code."""
        data = "red"
        result = self.processor.process(data, ModalityType.COLOR)
        self.assertEqual(result["modality"], "color")
        self.assertEqual(result["data"], data)
        self.assertTrue(result["processed"])
        self.assertTrue(result["metadata"]["color_processed"])
        self.assertNotIn("hex_parsed", result["metadata"])
        self.assertEqual(self.processor.get_processed_count(ModalityType.COLOR), 1)

    def test_get_processed_count_with_multiple_modalities(self):
        """Test get_processed_count with multiple processed items."""
        self.processor.process("text data", ModalityType.TEXT)
        self.processor.process("more text data", ModalityType.TEXT)
        self.processor.process({"path": "/image.jpg"}, ModalityType.IMAGE)
        self.assertEqual(self.processor.get_processed_count(), 3)
        self.assertEqual(self.processor.get_processed_count(ModalityType.TEXT), 2)
        self.assertEqual(self.processor.get_processed_count(ModalityType.IMAGE), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.AUDIO), 0)


if __name__ == "__main__":
    unittest.main()
