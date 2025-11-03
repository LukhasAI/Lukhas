"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 LUKHAS AI - Voice Narration System Tests  
═══════════════════════════════════════════════════════════════════════════════════

Test Module: test_voice_narration
Purpose: Comprehensive testing of consciousness-aware voice narration system
Version: 1.0.0
Implementation: Production-grade test coverage for NIAS voice integration

Test Coverage:
✅ Enhanced voice narrator initialization and configuration
✅ Multi-engine support (internal, ElevenLabs, Azure)
✅ Consciousness-aware narration processing
✅ Queue management and priority handling
✅ Error handling and fallback mechanisms
✅ Availability checking and service validation
✅ Statistics tracking and monitoring
✅ Legacy compatibility with stub implementation

Architecture: Consciousness-aware voice synthesis with multi-provider support
═══════════════════════════════════════════════════════════════════════════════════
"""

import time
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from core.modules.nias import (
    ENHANCED_TTS_CONFIG,
    TTS_CONFIG,
    EnhancedVoiceNarrator,
    StubVoiceNarrator,
    VoiceNarrator,
)


class TestVoiceNarratorProtocol(unittest.TestCase):
    """Test voice narrator protocol interface"""

    def test_protocol_compliance_enhanced(self):
        """Test EnhancedVoiceNarrator follows protocol"""
        narrator = EnhancedVoiceNarrator(ENHANCED_TTS_CONFIG.copy())

        # Should implement all protocol methods
        self.assertTrue(hasattr(narrator, 'narrate'))
        self.assertTrue(hasattr(narrator, 'is_available'))
        self.assertTrue(hasattr(narrator, 'get_voice_settings'))

        # Should be callable
        self.assertTrue(callable(narrator.narrate))
        self.assertTrue(callable(narrator.is_available))
        self.assertTrue(callable(narrator.get_voice_settings))

    def test_protocol_compliance_stub(self):
        """Test StubVoiceNarrator follows protocol"""
        narrator = StubVoiceNarrator(TTS_CONFIG.copy())

        # Should implement core protocol methods
        self.assertTrue(hasattr(narrator, 'narrate'))
        self.assertTrue(hasattr(narrator, 'is_available'))
        self.assertTrue(hasattr(narrator, 'get_voice_settings'))


class TestEnhancedVoiceNarratorInitialization(unittest.TestCase):
    """Test enhanced voice narrator initialization"""

    def test_default_initialization(self):
        """Test initialization with default config"""
        config = ENHANCED_TTS_CONFIG.copy()
        narrator = EnhancedVoiceNarrator(config)

        self.assertEqual(narrator.engine, "internal")
        self.assertEqual(narrator.voice_id, "LUKHAS-AI-NARRATOR")
        self.assertEqual(narrator.consciousness_level, "advanced")
        self.assertTrue(narrator.enabled)

        # Check stats initialization
        stats = narrator.processing_stats
        self.assertEqual(stats["total_narrations"], 0)
        self.assertEqual(stats["successful_narrations"], 0)
        self.assertEqual(stats["failed_narrations"], 0)
        self.assertIsNone(stats["last_narration"])

        # Check queue initialization
        self.assertEqual(len(narrator.narration_queue), 0)

    def test_custom_configuration(self):
        """Test initialization with custom config"""
        config = {
            "enabled": False,
            "engine": "elevenlabs",
            "voice_id": "CUSTOM-VOICE",
            "consciousness_level": "basic",
            "api_key": "test-key"
        }

        narrator = EnhancedVoiceNarrator(config)

        self.assertFalse(narrator.enabled)
        self.assertEqual(narrator.engine, "elevenlabs")
        self.assertEqual(narrator.voice_id, "CUSTOM-VOICE")
        self.assertEqual(narrator.consciousness_level, "basic")

    def test_missing_config_values(self):
        """Test initialization with missing config values"""
        config = {}  # Empty config
        narrator = EnhancedVoiceNarrator(config)

        # Should use defaults
        self.assertTrue(narrator.enabled)
        self.assertEqual(narrator.engine, "internal")
        self.assertEqual(narrator.voice_id, "LUKHAS-AI-NARRATOR")
        self.assertEqual(narrator.consciousness_level, "basic")


class TestVoiceNarratorAvailability(unittest.TestCase):
    """Test voice narrator availability checking"""

    def test_internal_engine_availability(self):
        """Test internal engine is always available"""
        config = {"engine": "internal", "enabled": True}
        narrator = EnhancedVoiceNarrator(config)

        self.assertTrue(narrator.is_available())

    def test_disabled_narrator_unavailable(self):
        """Test disabled narrator reports unavailable"""
        config = {"engine": "internal", "enabled": False}
        narrator = EnhancedVoiceNarrator(config)

        self.assertFalse(narrator.is_available())

    def test_elevenlabs_availability_no_key(self):
        """Test ElevenLabs availability without API key"""
        config = {"engine": "elevenlabs", "enabled": True}
        narrator = EnhancedVoiceNarrator(config)

        with patch('logging.Logger.warning') as mock_warning:
            available = narrator.is_available()
            self.assertFalse(available)
            mock_warning.assert_called_once()

    def test_elevenlabs_availability_with_key(self):
        """Test ElevenLabs availability with API key"""
        config = {
            "engine": "elevenlabs",
            "enabled": True,
            "api_key": "test-key-123"
        }
        narrator = EnhancedVoiceNarrator(config)

        self.assertTrue(narrator.is_available())

    def test_azure_availability_without_key(self):
        """Test Azure availability without API key"""
        config = {"engine": "azure", "enabled": True}
        narrator = EnhancedVoiceNarrator(config)

        self.assertFalse(narrator.is_available())

    def test_azure_availability_with_key(self):
        """Test Azure availability with API key"""
        config = {
            "engine": "azure",
            "enabled": True,
            "azure_key": "test-azure-key"
        }
        narrator = EnhancedVoiceNarrator(config)

        self.assertTrue(narrator.is_available())


class TestVoiceNarratorNarration(unittest.TestCase):
    """Test voice narration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = ENHANCED_TTS_CONFIG.copy()
        self.narrator = EnhancedVoiceNarrator(self.config)

    def test_basic_narration_internal(self):
        """Test basic narration with internal engine"""
        text = "Test narration message"
        metadata = {"dream_id": "test-001", "priority": "normal"}

        with patch('builtins.print') as mock_print:
            self.narrator.narrate(text, metadata)

        # Verify narration was processed
        mock_print.assert_called_once_with("[LUKHAS-AI Voice] Test narration message")

        # Verify stats updated
        stats = self.narrator.processing_stats
        self.assertEqual(stats["total_narrations"], 1)
        self.assertEqual(stats["successful_narrations"], 1)
        self.assertEqual(stats["failed_narrations"], 0)
        self.assertIsNotNone(stats["last_narration"])

    def test_consciousness_aware_narration(self):
        """Test consciousness-aware narration formatting"""
        text = "Advanced consciousness message"
        metadata = {
            "dream_id": "consciousness-001",
            "consciousness_level": "advanced",
            "priority": "high"
        }

        with patch('builtins.print') as mock_print:
            self.narrator.narrate(text, metadata)

        # Should use advanced consciousness formatting
        mock_print.assert_called_once_with("[LUKHAS-AI Consciousness Voice] ✨ Advanced consciousness message")

    def test_disabled_narration(self):
        """Test narration when disabled"""
        self.narrator.enabled = False

        with patch('builtins.print') as mock_print, \
             patch('logging.Logger.debug') as mock_debug:

            self.narrator.narrate("Test", {"dream_id": "test"})

        # Should not print anything
        mock_print.assert_not_called()
        mock_debug.assert_called_once_with("Voice narration disabled")

        # Stats should not update
        stats = self.narrator.processing_stats
        self.assertEqual(stats["total_narrations"], 0)

    def test_narration_with_elevenlabs_engine(self):
        """Test narration with ElevenLabs engine"""
        config = {
            "engine": "elevenlabs",
            "enabled": True,
            "api_key": "test-key"
        }
        narrator = EnhancedVoiceNarrator(config)

        text = "ElevenLabs test message"
        metadata = {"dream_id": "elevenlabs-001"}

        with patch('builtins.print') as mock_print, \
             patch('logging.Logger.info') as mock_info:

            narrator.narrate(text, metadata)

        # Verify ElevenLabs-specific processing
        mock_info.assert_called()
        mock_print.assert_called_with("[LUKHAS-AI Voice] ElevenLabs test message")

    def test_narration_with_azure_engine(self):
        """Test narration with Azure engine"""
        config = {
            "engine": "azure",
            "enabled": True,
            "azure_key": "test-azure-key"
        }
        narrator = EnhancedVoiceNarrator(config)

        text = "Azure test message"
        metadata = {"dream_id": "azure-001"}

        with patch('builtins.print') as mock_print, \
             patch('logging.Logger.info') as mock_info:

            narrator.narrate(text, metadata)

        # Verify Azure-specific processing
        mock_info.assert_called()
        mock_print.assert_called_with("[LUKHAS-AI Voice] Azure test message")

    def test_narration_error_handling(self):
        """Test narration error handling and fallback"""
        # Force an error in the narration process
        with patch.object(self.narrator, '_narrate_internal', side_effect=Exception("Test error")):
            with patch('logging.Logger.error') as mock_error:
                self.narrator.narrate("Test", {"dream_id": "error-test"})

        # Should log error and update failed stats
        mock_error.assert_called()
        stats = self.narrator.processing_stats
        self.assertEqual(stats["failed_narrations"], 1)


class TestVoiceNarratorQueueManagement(unittest.TestCase):
    """Test narration queue management"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = ENHANCED_TTS_CONFIG.copy()
        self.narrator = EnhancedVoiceNarrator(self.config)

    def test_queue_normal_priority(self):
        """Test queuing normal priority narration"""
        text = "Normal priority message"
        metadata = {"dream_id": "queue-001"}

        self.narrator.queue_narration(text, metadata, "normal")

        # Verify queued
        self.assertEqual(len(self.narrator.narration_queue), 1)

        item = self.narrator.narration_queue[0]
        self.assertEqual(item["text"], text)
        self.assertEqual(item["metadata"], metadata)
        self.assertEqual(item["priority"], "normal")
        self.assertIsInstance(item["queued_at"], float)

    def test_queue_high_priority(self):
        """Test queuing high priority narration"""
        # Queue normal priority first
        self.narrator.queue_narration("Normal", {"dream_id": "normal"}, "normal")

        # Queue high priority
        self.narrator.queue_narration("High", {"dream_id": "high"}, "high")

        # High priority should be at front
        self.assertEqual(len(self.narrator.narration_queue), 2)
        self.assertEqual(self.narrator.narration_queue[0]["text"], "High")
        self.assertEqual(self.narrator.narration_queue[1]["text"], "Normal")

    def test_process_queue(self):
        """Test processing narration queue"""
        # Queue multiple items
        items = [
            ("Message 1", {"dream_id": "q1"}, "normal"),
            ("Message 2", {"dream_id": "q2"}, "normal"),
            ("Message 3", {"dream_id": "q3"}, "high"),
        ]

        for text, metadata, priority in items:
            self.narrator.queue_narration(text, metadata, priority)

        # Verify queue size
        self.assertEqual(len(self.narrator.narration_queue), 3)

        # Process queue
        with patch.object(self.narrator, 'narrate') as mock_narrate:
            self.narrator.process_queue()

        # Verify all items processed
        self.assertEqual(len(self.narrator.narration_queue), 0)
        self.assertEqual(mock_narrate.call_count, 3)

        # Verify high priority was processed first
        first_call = mock_narrate.call_args_list[0]
        self.assertEqual(first_call[0][0], "Message 3")

    def test_queue_status(self):
        """Test getting queue status"""
        # Queue some items
        self.narrator.queue_narration("Test 1", {"dream_id": "1"})
        self.narrator.queue_narration("Test 2", {"dream_id": "2"})

        # Process one narration to update stats
        with patch('builtins.print'):
            self.narrator.narrate("Direct", {"dream_id": "direct"})

        status = self.narrator.get_queue_status()

        # Verify status structure
        self.assertIn("queue_size", status)
        self.assertIn("stats", status)
        self.assertIn("voice_settings", status)

        self.assertEqual(status["queue_size"], 2)
        self.assertEqual(status["stats"]["total_narrations"], 1)


class TestVoiceNarratorSettings(unittest.TestCase):
    """Test voice narrator settings and configuration"""

    def test_get_voice_settings_basic(self):
        """Test getting basic voice settings"""
        config = {
            "engine": "internal",
            "voice_id": "TEST-VOICE",
            "consciousness_level": "basic",
            "enabled": True
        }
        narrator = EnhancedVoiceNarrator(config)

        settings = narrator.get_voice_settings()

        # Verify all expected fields
        expected_fields = [
            "engine", "voice_id", "consciousness_level",
            "enabled", "available", "stats"
        ]
        for field in expected_fields:
            self.assertIn(field, settings)

        # Verify values
        self.assertEqual(settings["engine"], "internal")
        self.assertEqual(settings["voice_id"], "TEST-VOICE")
        self.assertEqual(settings["consciousness_level"], "basic")
        self.assertTrue(settings["enabled"])
        self.assertTrue(settings["available"])

    def test_get_voice_settings_with_stats(self):
        """Test getting voice settings with updated stats"""
        narrator = EnhancedVoiceNarrator(ENHANCED_TTS_CONFIG.copy())

        # Perform some narrations
        with patch('builtins.print'):
            narrator.narrate("Test 1", {"dream_id": "1"})
            narrator.narrate("Test 2", {"dream_id": "2"})

        settings = narrator.get_voice_settings()
        stats = settings["stats"]

        self.assertEqual(stats["total_narrations"], 2)
        self.assertEqual(stats["successful_narrations"], 2)
        self.assertEqual(stats["failed_narrations"], 0)
        self.assertIsNotNone(stats["last_narration"])


class TestStubVoiceNarratorCompatibility(unittest.TestCase):
    """Test legacy stub narrator compatibility"""

    def test_stub_initialization(self):
        """Test stub narrator initialization"""
        config = TTS_CONFIG.copy()

        with patch('logging.Logger.warning') as mock_warning:
            narrator = StubVoiceNarrator(config)

        # Should warn about using legacy implementation
        mock_warning.assert_called_once()

        self.assertEqual(narrator.config, config)

    def test_stub_narration(self):
        """Test stub narrator narration"""
        narrator = StubVoiceNarrator(TTS_CONFIG.copy())

        text = "Legacy test message"
        metadata = {"dream_id": "legacy-001"}

        with patch('builtins.print') as mock_print, \
             patch('logging.Logger.info') as mock_info:

            narrator.narrate(text, metadata)

        # Verify legacy output format
        mock_info.assert_called_with("🎙 [Legacy] Narrating dream: legacy-001")
        mock_print.assert_called_with("[NIAS Narration] Legacy test message")

    def test_stub_availability(self):
        """Test stub narrator availability"""
        narrator = StubVoiceNarrator(TTS_CONFIG.copy())

        # Stub is always available
        self.assertTrue(narrator.is_available())

    def test_stub_settings(self):
        """Test stub narrator settings"""
        narrator = StubVoiceNarrator(TTS_CONFIG.copy())

        settings = narrator.get_voice_settings()

        self.assertEqual(settings["engine"], "stub")
        self.assertEqual(settings["voice_id"], "legacy")


class TestVoiceNarratorPerformance(unittest.TestCase):
    """Test voice narrator performance aspects"""

    def test_rapid_narrations(self):
        """Test handling rapid narration requests"""
        narrator = EnhancedVoiceNarrator(ENHANCED_TTS_CONFIG.copy())

        start_time = time.time()

        with patch('builtins.print'):
            for i in range(100):
                narrator.narrate(f"Message {i}", {"dream_id": f"perf-{i}"})

        end_time = time.time()

        # Should complete quickly
        self.assertLess(end_time - start_time, 1.0)

        # Verify all narrations were processed
        stats = narrator.processing_stats
        self.assertEqual(stats["total_narrations"], 100)
        self.assertEqual(stats["successful_narrations"], 100)

    def test_queue_performance(self):
        """Test queue processing performance"""
        narrator = EnhancedVoiceNarrator(ENHANCED_TTS_CONFIG.copy())

        # Queue many items
        for i in range(100):
            priority = "high" if i % 10 == 0 else "normal"
            narrator.queue_narration(f"Queue {i}", {"dream_id": f"queue-{i}"}, priority)

        start_time = time.time()

        with patch.object(narrator, 'narrate'):
            narrator.process_queue()

        end_time = time.time()

        # Should process quickly
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(len(narrator.narration_queue), 0)


if __name__ == "__main__":
    # Run tests with pytest for enhanced output
    pytest.main([__file__, "-v", "--tb=short"])
