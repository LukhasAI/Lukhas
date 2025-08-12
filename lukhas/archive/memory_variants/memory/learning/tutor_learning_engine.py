"""
Tests for the TutorEngine component.
"""

from typing import Any

import pytest
from docututor.symbolic_knowledge_core.knowledge_graph import (
    SystemKnowledgeGraph,
)
from docututor.tutoring_engine.tutor import (
    DifficultyLevel,
    TutorEngine,
    TutorMessageType,
)


# Mock Lukhas interfaces
class TestTutorLearningEngine:
    async def synthesize_speech(self, text: str, style: dict[str, Any]):
        return True


class TestTutorLearningEngine:
    async def get_user_metrics(self, user_id: str) -> dict[str, float]:
        return {"stress": 0.4, "attention": 0.8, "cognitive_load": 0.5}


@pytest.fixture
def skg():
    """Create a test knowledge graph."""
    return SystemKnowledgeGraph()


@pytest.fixture
def tutor_engine(skg):
    """Create a TutorEngine instance with mock interfaces."""
    return TutorEngine(
        skg=skg, voice_interface=MockVoiceInterface(), bio_interface=MockBioInterface()
    )


@pytest.fixture
def sample_config():
    """Create a sample session configuration."""
    return {
        "voice_enabled": True,
        "bio_oscillator_aware": True,
        "cultural_context": "technical",
    }


@pytest.mark.asyncio
async def test_create_session(tutor_engine, sample_config):
    """Test creation of a new learning session."""
    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    assert session.topic == "Python Basics"
    assert session.user_id == "test_user_1"
    assert session.voice_enabled
    assert len(session.messages) > 0  # Should have welcome message
    assert session.messages[0].message_type == TutorMessageType.ENCOURAGEMENT


@pytest.mark.asyncio
async def test_handle_good_response(tutor_engine, sample_config):
    """Test handling of a good user response."""
    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    responses = await tutor_engine.handle_user_response(
        session.session_id,
        "The concept involves variables and data types, which are fundamental to programming.",
    )

    assert len(responses) > 0
    assert any(r.message_type == TutorMessageType.FEEDBACK for r in responses)
    assert "Excellent" in responses[0].content


@pytest.mark.asyncio
async def test_handle_poor_response(tutor_engine, sample_config):
    """Test handling of a response that shows poor understanding."""
    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    responses = await tutor_engine.handle_user_response(
        session.session_id, "I'm not sure about this."
    )

    assert len(responses) > 0
    assert any(r.message_type == TutorMessageType.HINT for r in responses)
    assert "another way" in responses[0].content


@pytest.mark.asyncio
async def test_bio_oscillator_adaptation(tutor_engine, sample_config):
    """Test adaptation based on bio-oscillator feedback."""

    # Override bio metrics to simulate stress
    async def get_stressed_metrics(user_id: str):
        return {"stress": 0.8, "attention": 0.3}

    tutor_engine.bio.get_user_metrics = get_stressed_metrics

    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    responses = await tutor_engine.handle_user_response(
        session.session_id, "This is complicated."
    )

    assert len(responses) > 0
    assert "step back" in responses[0].content  # Should adapt to high stress
    assert responses[0].voice_style["emotion"] == "calming"


@pytest.mark.asyncio
async def test_session_end(tutor_engine, sample_config):
    """Test proper session end and summary generation."""
    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    # Simulate some interaction
    await tutor_engine.handle_user_response(session.session_id, "Test response")

    summary = await tutor_engine.end_session(session.session_id)

    assert "duration_minutes" in summary
    assert "objectives_completed" in summary
    assert "messages_exchanged" in summary
    assert session.session_id not in tutor_engine.active_sessions


@pytest.mark.asyncio
async def test_voice_integration(tutor_engine, sample_config):
    """Test voice synthesis integration."""
    voice_calls = []

    async def mock_synthesize(text: str, style: dict[str, Any]):
        voice_calls.append((text, style))
        return True

    tutor_engine.voice.synthesize_speech = mock_synthesize

    await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    assert len(voice_calls) > 0
    assert voice_calls[0][1]["emotion"] == "welcoming"  # Welcome message


@pytest.mark.asyncio
async def test_learning_progression(tutor_engine, sample_config):
    """Test progression through learning objectives."""
    session = await tutor_engine.create_session(
        topic="Python Basics",
        user_id="test_user_1",
        difficulty=DifficultyLevel.BEGINNER,
        config=sample_config,
    )

    initial_objective = session.current_objective_index

    # Simulate a very good response
    responses = await tutor_engine.handle_user_response(
        session.session_id,
        "The concept involves variables, data types, and control structures, which are fundamental to programming.",
    )

    assert session.current_objective_index > initial_objective
    assert any("next topic" in r.content for r in responses)
