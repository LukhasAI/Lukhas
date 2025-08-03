#!/usr/bin/env python3
"""
Test Suite for Feedback Integration
===================================
Tests for the integrated feedback collection and interpretability system.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
import uuid

from feedback.user_feedback_system import (
    UserFeedbackSystem,
    FeedbackType,
    ComplianceRegion,
    FeedbackItem,
    EmotionEmoji
)
from dashboard.interpretability_dashboard import UnifiedInterpretabilityDashboard
from consciousness.interfaces.natural_language_interface import NaturalLanguageConsciousnessInterface
from core.common.exceptions import ValidationError


@pytest.fixture
async def feedback_system():
    """Create initialized feedback system"""
    system = UserFeedbackSystem(config={
        "enable_emoji": True,
        "min_feedback_interval": 1  # 1 second for testing
    })
    
    # Mock services
    mock_nl = Mock()
    mock_nl._analyze_emotion = AsyncMock(return_value={
        "positive": 0.7,
        "negative": 0.3
    })
    
    mock_audit = Mock()
    mock_audit.log_event = AsyncMock()
    
    from core.interfaces.dependency_injection import register_service
    register_service("nl_consciousness_interface", mock_nl)
    register_service("audit_service", mock_audit)
    
    await system.initialize()
    return system


@pytest.fixture
async def dashboard():
    """Create initialized dashboard"""
    dash = UnifiedInterpretabilityDashboard(config={
        "enable_realtime": True
    })
    
    # Mock services
    mock_nl = Mock()
    mock_nl.get_status = AsyncMock(return_value={"operational": True})
    
    mock_feedback = Mock()
    mock_feedback.get_status = AsyncMock(return_value={"operational": True})
    
    from core.interfaces.dependency_injection import register_service
    register_service("nl_consciousness_interface", mock_nl)
    register_service("user_feedback_system", mock_feedback)
    
    await dash.initialize()
    return dash


@pytest.fixture
async def integrated_system(feedback_system, dashboard):
    """Create integrated system with feedback and dashboard"""
    # Link systems
    dashboard.feedback_system = feedback_system
    feedback_system.dashboard = dashboard
    
    return {
        "feedback": feedback_system,
        "dashboard": dashboard
    }


class TestFeedbackCollection:
    """Test feedback collection functionality"""
    
    @pytest.mark.asyncio
    async def test_rating_feedback(self, feedback_system):
        """Test rating feedback collection"""
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.RATING,
            content={"rating": 5},
            context={"action_type": "test"}
        )
        
        assert feedback_id in feedback_system.feedback_items
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.content["rating"] == 5
        assert feedback.processed_sentiment["positive"] > 0.5
    
    @pytest.mark.asyncio
    async def test_emoji_feedback(self, feedback_system):
        """Test emoji feedback collection"""
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.EMOJI,
            content={"emoji": EmotionEmoji.VERY_HAPPY.value},
            context={"action_type": "test"}
        )
        
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.content["emoji"] == "😄"
        assert feedback.processed_sentiment["positive"] == 1.0
    
    @pytest.mark.asyncio
    async def test_text_feedback_with_sentiment(self, feedback_system):
        """Test text feedback with sentiment analysis"""
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.TEXT,
            content={"text": "This was incredibly helpful and clear!"},
            context={"action_type": "explanation"}
        )
        
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.processed_sentiment["positive"] == 0.7  # From mock
    
    @pytest.mark.asyncio
    async def test_quick_feedback(self, feedback_system):
        """Test quick thumbs up/down feedback"""
        # Thumbs up
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.QUICK,
            content={"rating": 5, "thumbs_up": True},
            context={"quick_feedback": True}
        )
        
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.processed_sentiment["positive"] > 0.5
    
    @pytest.mark.asyncio
    async def test_feedback_rate_limiting(self, feedback_system):
        """Test rate limiting prevents spam"""
        # First feedback should succeed
        await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action_1",
            feedback_type=FeedbackType.RATING,
            content={"rating": 5},
            context={}
        )
        
        # Immediate second feedback should fail
        with pytest.raises(ValidationError, match="wait before submitting"):
            await feedback_system.collect_feedback(
                user_id="test_user",
                session_id="test_session",
                action_id="test_action_2",
                feedback_type=FeedbackType.RATING,
                content={"rating": 5},
                context={}
            )
    
    @pytest.mark.asyncio
    async def test_compliance_regions(self, feedback_system):
        """Test compliance region handling"""
        # EU region requires explicit consent
        with pytest.raises(ValidationError, match="consent required"):
            await feedback_system.collect_feedback(
                user_id="new_user",
                session_id="test_session",
                action_id="test_action",
                feedback_type=FeedbackType.TEXT,
                content={"text": "test"},
                context={},
                region=ComplianceRegion.EU
            )
        
        # Global region doesn't require explicit consent
        feedback_id = await feedback_system.collect_feedback(
            user_id="global_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.TEXT,
            content={"text": "test"},
            context={},
            region=ComplianceRegion.GLOBAL
        )
        
        assert feedback_id in feedback_system.feedback_items


class TestFeedbackManagement:
    """Test feedback editing and deletion"""
    
    @pytest.mark.asyncio
    async def test_edit_feedback(self, feedback_system):
        """Test editing feedback"""
        # Create feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.TEXT,
            content={"text": "Original feedback"},
            context={}
        )
        
        # Edit feedback
        success = await feedback_system.edit_feedback(
            feedback_id=feedback_id,
            user_id="test_user",
            new_content={"text": "Edited feedback"}
        )
        
        assert success
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.content["text"] == "Edited feedback"
        assert len(feedback.edit_history) == 1
    
    @pytest.mark.asyncio
    async def test_delete_feedback(self, feedback_system):
        """Test soft deletion of feedback"""
        # Create feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.RATING,
            content={"rating": 5},
            context={}
        )
        
        # Delete feedback
        success = await feedback_system.delete_feedback(
            feedback_id=feedback_id,
            user_id="test_user"
        )
        
        assert success
        feedback = feedback_system.feedback_items[feedback_id]
        assert feedback.is_deleted
        assert not feedback.is_editable
    
    @pytest.mark.asyncio
    async def test_ownership_validation(self, feedback_system):
        """Test users can only edit/delete their own feedback"""
        # Create feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id="user1",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.TEXT,
            content={"text": "User 1 feedback"},
            context={}
        )
        
        # Try to edit as different user
        with pytest.raises(ValidationError, match="own feedback"):
            await feedback_system.edit_feedback(
                feedback_id=feedback_id,
                user_id="user2",
                new_content={"text": "Hacked!"}
            )
        
        # Try to delete as different user
        with pytest.raises(ValidationError, match="own feedback"):
            await feedback_system.delete_feedback(
                feedback_id=feedback_id,
                user_id="user2"
            )


class TestFeedbackAggregation:
    """Test feedback aggregation and summaries"""
    
    @pytest.mark.asyncio
    async def test_action_feedback_summary(self, feedback_system):
        """Test aggregating feedback for an action"""
        action_id = "test_action"
        
        # Add multiple feedback items
        for i in range(5):
            await asyncio.sleep(0.1)  # Avoid rate limiting
            await feedback_system.collect_feedback(
                user_id=f"user_{i}",
                session_id="test_session",
                action_id=action_id,
                feedback_type=FeedbackType.RATING,
                content={"rating": 4 + (i % 2)},  # Alternating 4 and 5
                context={}
            )
        
        # Add emoji feedback
        await asyncio.sleep(0.1)
        await feedback_system.collect_feedback(
            user_id="emoji_user",
            session_id="test_session",
            action_id=action_id,
            feedback_type=FeedbackType.EMOJI,
            content={"emoji": "😊"},
            context={}
        )
        
        # Get summary
        summary = await feedback_system.get_action_feedback(action_id)
        
        assert summary.total_feedback == 6
        assert summary.average_rating == 4.5  # Average of 4,5,4,5,4
        assert summary.emoji_distribution["😊"] == 1
    
    @pytest.mark.asyncio
    async def test_user_feedback_history(self, feedback_system):
        """Test retrieving user feedback history"""
        user_id = "test_user"
        
        # Add feedback over time
        feedback_ids = []
        for i in range(3):
            await asyncio.sleep(0.1)
            feedback_id = await feedback_system.collect_feedback(
                user_id=user_id,
                session_id="test_session",
                action_id=f"action_{i}",
                feedback_type=FeedbackType.TEXT,
                content={"text": f"Feedback {i}"},
                context={}
            )
            feedback_ids.append(feedback_id)
        
        # Get history
        history = await feedback_system.get_user_feedback_history(user_id)
        
        assert len(history) == 3
        # Should be in reverse chronological order
        assert history[0].feedback_id == feedback_ids[2]
        assert history[2].feedback_id == feedback_ids[0]
    
    @pytest.mark.asyncio
    async def test_feedback_report_generation(self, feedback_system):
        """Test generating feedback reports"""
        # Add feedback
        start_time = datetime.now(timezone.utc)
        
        for i in range(3):
            await asyncio.sleep(0.1)
            await feedback_system.collect_feedback(
                user_id=f"user_{i}",
                session_id="test_session",
                action_id="test_action",
                feedback_type=FeedbackType.RATING,
                content={"rating": 4 + (i % 2)},
                context={}
            )
        
        end_time = datetime.now(timezone.utc)
        
        # Generate report
        report = await feedback_system.generate_feedback_report(
            start_date=start_time,
            end_date=end_time,
            anonymize=True
        )
        
        assert report["summary"]["total_feedback"] == 3
        assert report["summary"]["unique_users"] == 3
        assert report["summary"]["feedback_by_type"]["rating"] == 3
        assert "satisfaction_score" in report["summary"]


class TestDashboardIntegration:
    """Test dashboard integration with feedback"""
    
    @pytest.mark.asyncio
    async def test_decision_tracking_with_feedback(self, integrated_system):
        """Test tracking decisions and integrating feedback"""
        dashboard = integrated_system["dashboard"]
        feedback_system = integrated_system["feedback"]
        
        # Track a decision
        decision_id = "test_decision_001"
        await dashboard.track_decision(
            decision_id=decision_id,
            module="test_module",
            decision_type="recommendation",
            input_data={"query": "test query"},
            reasoning_steps=[
                {"step": "Analyzed input", "confidence": 0.9},
                {"step": "Generated options", "confidence": 0.8}
            ],
            output={"recommendation": "Option A"},
            confidence=0.85
        )
        
        # Collect feedback for the decision
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id=decision_id,
            feedback_type=FeedbackType.RATING,
            content={"rating": 5},
            context={"decision_id": decision_id}
        )
        
        # Integrate feedback with decision
        await dashboard.integrate_feedback(
            decision_id=decision_id,
            feedback_data={
                "feedback_id": feedback_id,
                "user_id": "test_user",
                "type": "rating",
                "content": {"rating": 5},
                "sentiment": {"positive": 1.0, "negative": 0.0}
            }
        )
        
        # Check decision has feedback reference
        decision = dashboard.decisions[decision_id]
        assert len(decision["feedback_references"]) == 1
        assert decision["feedback_references"][0]["feedback_id"] == feedback_id
    
    @pytest.mark.asyncio
    async def test_feedback_influence_tracking(self, integrated_system):
        """Test tracking how feedback influences decisions"""
        dashboard = integrated_system["dashboard"]
        feedback_system = integrated_system["feedback"]
        
        user_id = "influential_user"
        
        # User gives feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id=user_id,
            session_id="session1",
            action_id="action1",
            feedback_type=FeedbackType.TEXT,
            content={"text": "I prefer detailed explanations"},
            context={"preference": "detail"}
        )
        
        # Later decision references this feedback
        decision_id = "decision_002"
        await dashboard.track_decision(
            decision_id=decision_id,
            module="test_module",
            decision_type="explanation_style",
            input_data={"user_id": user_id},
            reasoning_steps=[
                {"step": "Retrieved user feedback", "confidence": 0.9},
                {"step": "Adjusted response style", "confidence": 0.95}
            ],
            output={"style": "detailed"},
            confidence=0.9
        )
        
        # Link feedback to decision
        await dashboard.integrate_feedback(
            decision_id=decision_id,
            feedback_data={
                "feedback_id": feedback_id,
                "user_id": user_id,
                "type": "historical",
                "influence": "high"
            }
        )
        
        # Check influence
        decision = dashboard.decisions[decision_id]
        assert any(ref["feedback_id"] == feedback_id 
                  for ref in decision["feedback_references"])
    
    @pytest.mark.asyncio
    async def test_real_time_dashboard_updates(self, integrated_system):
        """Test real-time dashboard updates with feedback"""
        dashboard = integrated_system["dashboard"]
        feedback_system = integrated_system["feedback"]
        
        initial_status = await dashboard.get_status()
        initial_decisions = initial_status["total_decisions"]
        
        # Track multiple decisions
        for i in range(3):
            await dashboard.track_decision(
                decision_id=f"rt_decision_{i}",
                module="test_module",
                decision_type="test",
                input_data={"index": i},
                reasoning_steps=[{"step": "Test step", "confidence": 0.8}],
                output={"result": f"Result {i}"},
                confidence=0.8
            )
        
        # Collect feedback
        for i in range(2):
            await asyncio.sleep(0.1)
            await feedback_system.collect_feedback(
                user_id="test_user",
                session_id="test_session",
                action_id=f"rt_decision_{i}",
                feedback_type=FeedbackType.QUICK,
                content={"rating": 5, "thumbs_up": True},
                context={}
            )
        
        # Check updated status
        updated_status = await dashboard.get_status()
        assert updated_status["total_decisions"] == initial_decisions + 3


class TestComplianceFeatures:
    """Test GDPR and compliance features"""
    
    @pytest.mark.asyncio
    async def test_user_data_export(self, feedback_system):
        """Test exporting all user data"""
        user_id = "export_test_user"
        
        # Create various feedback
        feedback_ids = []
        for i in range(3):
            await asyncio.sleep(0.1)
            feedback_id = await feedback_system.collect_feedback(
                user_id=user_id,
                session_id=f"session_{i}",
                action_id=f"action_{i}",
                feedback_type=FeedbackType.TEXT,
                content={"text": f"Feedback {i}"},
                context={"index": i}
            )
            feedback_ids.append(feedback_id)
        
        # Export data
        export_data = await feedback_system.export_user_data(user_id)
        
        assert export_data["user_id"] == user_id
        assert len(export_data["feedback_history"]) == 3
        assert all(item["feedback_id"] in feedback_ids 
                  for item in export_data["feedback_history"])
    
    @pytest.mark.asyncio
    async def test_data_retention_cleanup(self, feedback_system):
        """Test automatic cleanup of old feedback"""
        # Create old feedback
        old_feedback = FeedbackItem(
            feedback_id="old_feedback",
            user_id="test_user",
            session_id="old_session",
            action_id="old_action",
            timestamp=datetime.now(timezone.utc) - timedelta(days=100),
            feedback_type=FeedbackType.TEXT,
            content={"text": "Old feedback"},
            context={},
            compliance_region=ComplianceRegion.GLOBAL
        )
        
        feedback_system.feedback_items["old_feedback"] = old_feedback
        
        # Run cleanup
        removed_count = await feedback_system.cleanup_old_feedback()
        
        assert removed_count == 1
        assert "old_feedback" not in feedback_system.feedback_items
    
    @pytest.mark.asyncio
    async def test_anonymization(self, feedback_system):
        """Test feedback anonymization"""
        # Create feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            action_id="test_action",
            feedback_type=FeedbackType.TEXT,
            content={"text": "Personal feedback"},
            context={"personal_data": "sensitive info"},
            region=ComplianceRegion.EU
        )
        
        feedback = feedback_system.feedback_items[feedback_id]
        anonymized = feedback.anonymize()
        
        assert anonymized.user_id == "anonymous"
        assert anonymized.feedback_id != feedback_id
        assert "personal_data" not in anonymized.context
        assert anonymized.content == feedback.content  # Content preserved


class TestAPIIntegration:
    """Test API-level integration"""
    
    @pytest.mark.asyncio
    async def test_integrated_chat_with_feedback(self):
        """Test integrated chat API with feedback"""
        # This would typically test against the actual API
        # For unit tests, we mock the behavior
        
        from api.integrated_consciousness_api import IntegratedChatRequest
        
        request = IntegratedChatRequest(
            message="Test message",
            user_id="test_user",
            enable_feedback=True,
            region=ComplianceRegion.EU
        )
        
        assert request.enable_feedback
        assert request.region == ComplianceRegion.EU
    
    @pytest.mark.asyncio
    async def test_feedback_widgets(self, feedback_system):
        """Test feedback widget rendering"""
        from feedback.user_feedback_system import FeedbackWidget
        
        widget = FeedbackWidget(feedback_system)
        
        # Test rating widget
        rating_html = widget.render_rating_widget()
        assert "⭐" in rating_html
        assert "Rate this response" in rating_html
        
        # Test emoji grid
        emoji_html = widget.render_emoji_grid()
        assert "😊" in emoji_html
        assert "emoji-grid" in emoji_html
        
        # Test quick feedback
        quick_html = widget.render_quick_feedback()
        assert "👍" in quick_html
        assert "👎" in quick_html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])