#!/usr/bin/env python3
"""
Stable Imports Adapter for Experience Products
==============================================
Provides stable interface adapters that replace candidate/ module dependencies.
This ensures T4 architecture compliance by using registry-based discovery.
"""

import logging

from lukhas.core.interfaces import CoreInterface
from lukhas.core.registry import get_registered, register


# Exception classes that replace candidate.core.common.exceptions
class LukhasError(Exception):
    """Base exception for LUKHAS system errors"""
    pass


class ValidationError(LukhasError):
    """Exception for validation errors"""
    pass


class ConfigurationError(LukhasError):
    """Exception for configuration errors"""
    pass


class ServiceError(LukhasError):
    """Exception for service-related errors"""
    pass


# Logging utilities that replace candidate.core.common.logger
def get_logger(name: str):
    """Get logger instance - stable interface"""
    return logging.getLogger(name)


def configure_logging(level=logging.INFO):
    """Configure logging with consistent format"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# Dependency injection that replaces candidate.core.interfaces.dependency_injection
def get_service(service_name: str):
    """Get service via registry - T4 compliant interface"""
    return get_registered(service_name)


def register_service(service_name: str, service_instance):
    """Register service via registry - T4 compliant interface"""
    return register(service_name, service_instance)


def service_exists(service_name: str) -> bool:
    """Check if service exists in registry"""
    return get_registered(service_name) is not None


# Audio/Speech interfaces that replace candidate audio modules
class AudioInterface(CoreInterface):
    """Protocol for audio processing components"""

    async def process_audio(self, audio_data: bytes, **kwargs) -> dict:
        """Process audio data and return results"""
        raise NotImplementedError

    async def configure(self, config: dict) -> bool:
        """Configure audio processing parameters"""
        raise NotImplementedError


class SpeechRecognitionInterface(AudioInterface):
    """Protocol for speech recognition implementations"""

    async def recognize_speech(self, audio_data: bytes, **kwargs) -> str:
        """Recognize speech from audio data"""
        raise NotImplementedError

    async def train_model(self, training_data: list, **kwargs) -> bool:
        """Train or fine-tune speech recognition model"""
        raise NotImplementedError


# Dashboard interfaces that replace candidate dashboard modules
class DashboardInterface(CoreInterface):
    """Protocol for dashboard components"""

    async def render_component(self, component_id: str, data: dict) -> dict:
        """Render dashboard component"""
        raise NotImplementedError

    async def update_data(self, component_id: str, new_data: dict) -> bool:
        """Update component data"""
        raise NotImplementedError


class AdaptiveDashboardInterface(DashboardInterface):
    """Protocol for adaptive dashboard implementations"""

    async def adapt_to_user(self, user_preferences: dict) -> bool:
        """Adapt dashboard to user preferences"""
        raise NotImplementedError

    async def learn_from_interaction(self, interaction_data: dict) -> bool:
        """Learn from user interactions"""
        raise NotImplementedError


# Voice processing interfaces
class VoiceInterface(CoreInterface):
    """Protocol for voice processing components"""

    async def synthesize_voice(self, text: str, voice_config: dict) -> bytes:
        """Synthesize voice from text"""
        raise NotImplementedError

    async def analyze_voice(self, audio_data: bytes) -> dict:
        """Analyze voice characteristics"""
        raise NotImplementedError


# Factory functions for getting implementations via registry
def get_audio_processor(processor_type: str = "default"):
    """Get audio processor implementation"""
    return get_service(f"audio_processor_{processor_type}")


def get_speech_recognizer(recognizer_type: str = "default"):
    """Get speech recognizer implementation"""
    return get_service(f"speech_recognizer_{recognizer_type}")


def get_dashboard_adapter(dashboard_type: str = "default"):
    """Get dashboard adapter implementation"""
    return get_service(f"dashboard_{dashboard_type}")


def get_voice_synthesizer(synthesizer_type: str = "default"):
    """Get voice synthesizer implementation"""
    return get_service(f"voice_synthesizer_{synthesizer_type}")


# Initialization function
def initialize_experience_adapters():
    """Initialize all experience module adapters"""
    logger = get_logger(__name__)
    logger.info("Initializing experience module stable adapters")

    # Register default null implementations if needed
    if not service_exists("audio_processor_default"):
        register_service("audio_processor_default", None)

    if not service_exists("speech_recognizer_default"):
        register_service("speech_recognizer_default", None)

    if not service_exists("dashboard_default"):
        register_service("dashboard_default", None)

    if not service_exists("voice_synthesizer_default"):
        register_service("voice_synthesizer_default", None)

    logger.info("Experience module stable adapters initialized")


# Auto-initialize when imported
initialize_experience_adapters()
