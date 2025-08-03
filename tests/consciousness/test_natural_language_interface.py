#!/usr/bin/env python3
"""
Test Suite for Natural Language Consciousness Interface
======================================================
Tests for conversational consciousness system interaction.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from consciousness.interfaces.natural_language_interface import (
    NaturalLanguageConsciousnessInterface,
    ConversationManager,
    ConversationIntent,
    EmotionalTone,
    ConversationContext,
    NLUResult
)
from core.common import GLYPHToken, GLYPHSymbol
from core.common.exceptions import LukhasError


@pytest.fixture
def mock_services():
    """Create mock services for testing"""
    services = {
        "consciousness_service": Mock(),
        "memory_service": Mock(),
        "emotion_service": Mock(),
        "dream_engine": Mock(),
        "parallel_reality_simulator": Mock()
    }
    
    # Configure consciousness service
    services["consciousness_service"].assess_awareness = AsyncMock(return_value={
        "overall_awareness": 0.75,
        "attention_targets": ["test", "conversation"],
        "self_awareness": 0.8,
        "environmental_awareness": 0.7
    })
    
    services["consciousness_service"].make_decision = AsyncMock(return_value={
        "selected_option": "Option A",
        "confidence": 0.85,
        "reasoning": ["Logical analysis", "Best outcome probability"],
        "alternatives_considered": ["Option B", "Option C"]
    })
    
    # Configure memory service
    services["memory_service"].search = AsyncMock(return_value=[
        {"id": "mem1", "summary": "Previous interaction", "timestamp": datetime.now()},
        {"id": "mem2", "summary": "Related memory", "timestamp": datetime.now()}
    ])
    
    # Configure emotion service
    services["emotion_service"].analyze_text = AsyncMock(return_value={
        "emotions": {"joy": 0.6, "sadness": 0.1, "anger": 0.0, "fear": 0.1, "surprise": 0.2}
    })
    
    services["emotion_service"].get_current_state = AsyncMock(return_value={
        "dominant_emotion": "contentment",
        "valence": 0.7,
        "arousal": 0.5,
        "dominance": 0.6
    })
    
    # Configure dream engine
    services["dream_engine"].generate_dream_sequence = AsyncMock(return_value={
        "dream_sequence": {
            "narrative": "In a world of endless possibilities, ideas flow like rivers..."
        }
    })
    
    # Configure reality simulator
    services["parallel_reality_simulator"].create_simulation = AsyncMock(return_value=Mock(
        branches=[
            Mock(probability=0.8, divergence_point={"summary": "optimistic path"}),
            Mock(probability=0.6, divergence_point={"summary": "neutral path"}),
            Mock(probability=0.4, divergence_point={"summary": "challenging path"})
        ]
    ))
    
    return services


@pytest.fixture
async def nl_interface(mock_services):
    """Create initialized NL interface with mocked services"""
    with patch('consciousness.interfaces.natural_language_interface.get_service') as mock_get:
        def get_service_side_effect(service_name):
            return mock_services.get(service_name)
        
        mock_get.side_effect = get_service_side_effect
        
        interface = NaturalLanguageConsciousnessInterface(config={
            "enable_emotions": True,
            "formality_level": "balanced",
            "max_response_length": 500
        })
        
        await interface.initialize()
        return interface


class TestNaturalLanguageInterface:
    """Test natural language consciousness interface"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_services):
        """Test interface initialization"""
        with patch('consciousness.interfaces.natural_language_interface.get_service') as mock_get:
            mock_get.side_effect = lambda name: mock_services.get(name)
            
            interface = NaturalLanguageConsciousnessInterface()
            assert not interface.operational
            
            await interface.initialize()
            assert interface.operational
            assert interface.consciousness_service is not None
    
    @pytest.mark.asyncio
    async def test_intent_detection(self, nl_interface):
        """Test intent detection from natural language"""
        test_cases = [
            ("How aware are you?", ConversationIntent.QUERY_AWARENESS),
            ("Help me decide between A and B", ConversationIntent.MAKE_DECISION),
            ("Reflect on what we discussed", ConversationIntent.REFLECT),
            ("Do you remember yesterday?", ConversationIntent.EXPLORE_MEMORY),
            ("How do you feel?", ConversationIntent.EMOTIONAL_CHECK),
            ("Dream about flying", ConversationIntent.DREAM_REQUEST),
            ("What if things were different?", ConversationIntent.REALITY_EXPLORATION),
            ("Explain your thinking", ConversationIntent.EXPLAIN_THOUGHT),
            ("Hello there", ConversationIntent.GENERAL_CHAT),
            ("Blah blah blah", ConversationIntent.UNKNOWN)
        ]
        
        for input_text, expected_intent in test_cases:
            detected = nl_interface._detect_intent(input_text)
            assert detected == expected_intent, f"Failed for: {input_text}"
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, nl_interface):
        """Test entity extraction from user input"""
        # Decision entities
        entities = nl_interface._extract_entities(
            "Help me decide between working and resting",
            ConversationIntent.MAKE_DECISION
        )
        assert "options" in entities
        assert entities["options"] == ["working", "resting"]
        
        # Memory time references
        entities = nl_interface._extract_entities(
            "Remember what happened yesterday",
            ConversationIntent.EXPLORE_MEMORY
        )
        assert "time_reference" in entities
        assert "yesterday" in entities["time_reference"]
        
        # Dream topic
        entities = nl_interface._extract_entities(
            "Dream about space exploration",
            ConversationIntent.DREAM_REQUEST
        )
        assert "dream_topic" in entities
        assert "space exploration" in entities["dream_topic"]
    
    @pytest.mark.asyncio
    async def test_emotion_analysis(self, nl_interface):
        """Test emotion analysis of user input"""
        # Test with emotion service available
        emotions = await nl_interface._analyze_emotion("I'm so happy today!")
        assert emotions["joy"] > 0.5
        
        # Test fallback emotion detection
        nl_interface.emotion_service = None
        emotions = await nl_interface._analyze_emotion("I'm feeling sad and worried")
        assert emotions["sadness"] > 0
        assert emotions["fear"] > 0
    
    @pytest.mark.asyncio
    async def test_awareness_query_processing(self, nl_interface):
        """Test processing awareness queries"""
        response = await nl_interface.process_input("How aware are you right now?")
        
        assert "awareness level" in response.lower() or "75" in response
        assert any(word in response.lower() for word in ["aware", "consciousness", "attention"])
    
    @pytest.mark.asyncio
    async def test_decision_processing(self, nl_interface):
        """Test decision-making request processing"""
        response = await nl_interface.process_input(
            "Help me decide between studying and exercising"
        )
        
        assert "Option A" in response or "recommend" in response.lower()
        assert "85%" in response or "confidence" in response.lower()
    
    @pytest.mark.asyncio
    async def test_memory_exploration(self, nl_interface):
        """Test memory exploration requests"""
        response = await nl_interface.process_input("Do you remember anything from yesterday?")
        
        assert "2" in response or "memories" in response.lower()
        assert "found" in response.lower() or "remember" in response.lower()
    
    @pytest.mark.asyncio
    async def test_emotional_check(self, nl_interface):
        """Test emotional state queries"""
        response = await nl_interface.process_input("How are you feeling?")
        
        assert "contentment" in response.lower() or "feeling" in response.lower()
        assert any(word in response.lower() for word in ["emotion", "feel", "state"])
    
    @pytest.mark.asyncio
    async def test_dream_request(self, nl_interface):
        """Test dream/creative requests"""
        response = await nl_interface.process_input("Dream about a perfect world")
        
        assert "possibilities" in response.lower() or "dream" in response.lower()
        assert len(response) > 50  # Should be descriptive
    
    @pytest.mark.asyncio
    async def test_reality_exploration(self, nl_interface):
        """Test alternative reality exploration"""
        response = await nl_interface.process_input("What if we took a different approach?")
        
        assert "realities" in response.lower() or "possibilities" in response.lower()
        assert "3" in response or "path" in response.lower()
    
    @pytest.mark.asyncio
    async def test_conversation_context(self, nl_interface):
        """Test conversation context management"""
        session_id = "test_session"
        
        # First turn
        response1 = await nl_interface.process_input(
            "How aware are you?",
            session_id=session_id
        )
        
        # Check context was created
        assert session_id in nl_interface.active_sessions
        context = nl_interface.active_sessions[session_id]
        assert len(context.turns) == 1
        assert context.active_intent == ConversationIntent.QUERY_AWARENESS
        
        # Second turn
        response2 = await nl_interface.process_input(
            "And how do you feel about that?",
            session_id=session_id
        )
        
        # Check context updated
        assert len(context.turns) == 2
        assert context.active_intent == ConversationIntent.EMOTIONAL_CHECK
    
    @pytest.mark.asyncio
    async def test_tone_application(self, nl_interface):
        """Test emotional tone application to responses"""
        # Test empathetic tone
        response = nl_interface._apply_tone(
            "Your request has been processed.",
            EmotionalTone.EMPATHETIC
        )
        assert response.startswith("I understand")
        
        # Test analytical tone
        response = nl_interface._apply_tone(
            "I think this is the best option.",
            EmotionalTone.ANALYTICAL
        )
        assert "analyze" in response
        
        # Test supportive tone
        response = nl_interface._apply_tone(
            "That's an interesting question.",
            EmotionalTone.SUPPORTIVE
        )
        assert "help" in response.lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, nl_interface):
        """Test error response generation"""
        # Test with missing service
        nl_interface.consciousness_service = None
        response = await nl_interface.process_input("How aware are you?")
        
        assert "not available" in response.lower() or "issue" in response.lower()
    
    @pytest.mark.asyncio
    async def test_glyph_handling(self, nl_interface):
        """Test GLYPH token handling"""
        token = GLYPHToken(
            symbol=GLYPHSymbol.QUERY,
            source="test_module",
            target="nl_consciousness_interface",
            payload={"text": "How are you feeling?"}
        )
        
        response_token = await nl_interface.handle_glyph(token)
        assert response_token.symbol == GLYPHSymbol.ACKNOWLEDGE
        assert "response" in response_token.payload
    
    @pytest.mark.asyncio
    async def test_conversation_manager(self, nl_interface):
        """Test conversation manager functionality"""
        manager = ConversationManager(nl_interface)
        
        # Create session
        session_id = await manager.create_session("test_user")
        assert "test_user" in session_id
        
        # Continue conversation
        response = await manager.continue_conversation(
            session_id,
            "Tell me about your awareness"
        )
        assert len(response) > 0
        
        # Get history
        history = await manager.get_conversation_history(session_id)
        assert len(history) == 1
        assert history[0]["user"] == "Tell me about your awareness"
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self, nl_interface):
        """Test old session cleanup"""
        manager = ConversationManager(nl_interface)
        
        # Create old session
        old_session = "old_session"
        nl_interface.active_sessions[old_session] = ConversationContext(
            session_id=old_session,
            user_id="test"
        )
        
        # Add old turn
        from datetime import timedelta
        old_time = datetime.now() - timedelta(hours=2)
        nl_interface.active_sessions[old_session].turns.append({
            "timestamp": old_time,
            "user": "old input",
            "system": "old response",
            "intent": "general_chat"
        })
        
        # Clean up
        await manager.cleanup_old_sessions()
        
        # Old session should be removed
        assert old_session not in nl_interface.active_sessions
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, nl_interface):
        """Test confidence calculation for intent detection"""
        context = ConversationContext("test", None)
        
        # High confidence - clear intent match
        confidence = nl_interface._calculate_confidence(
            "How aware are you right now?",
            ConversationIntent.QUERY_AWARENESS,
            context
        )
        assert confidence > 0.7
        
        # Low confidence - unknown intent
        confidence = nl_interface._calculate_confidence(
            "xyz",
            ConversationIntent.UNKNOWN,
            context
        )
        assert confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_nlu_pipeline(self, nl_interface):
        """Test complete NLU pipeline"""
        context = ConversationContext("test", None)
        
        nlu_result = await nl_interface._understand_input(
            "I'm feeling sad, can you help me decide what to do?",
            context
        )
        
        assert nlu_result.intent == ConversationIntent.MAKE_DECISION
        assert nlu_result.confidence > 0.5
        assert nlu_result.emotional_context["sadness"] > 0
        assert nlu_result.suggested_tone == EmotionalTone.EMPATHETIC


if __name__ == "__main__":
    pytest.main([__file__, "-v"])