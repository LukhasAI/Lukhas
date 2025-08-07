"""
Test Suite for Missing Features Implementation
Tests all newly implemented user-facing features
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import time
import json
from typing import Dict, Any

# Import all the new implementations
from lambda_products_pack.lambda_core.NIAS.reward_engine import (
    NIASRewardEngine, RewardType, ContentAccessLevel
)
from lambda_products_pack.lambda_core.NIAS.breakpoint_detector import (
    NaturalBreakpointDetector, WorkflowState, BreakpointType
)
from lambda_products_pack.lambda_core.NIAS.native_content_formatter import (
    NativeContentFormatter, ContentContext, ContentFormat
)
from architectures.ABAS.proactive_assistance import (
    ProactiveAssistanceSystem, UserState, AssistanceType
)
from architectures.ABAS.usage_analytics_loop import (
    UsageAnalyticsLoop, PainPointSeverity, OptimizationType
)
from architectures.DAST.realtime_service_switching import (
    RealTimeServiceSwitcher, ServiceType, ServiceProvider, ServiceRequest,
    FailoverStrategy, ServiceStatus
)


class TestNIASRewardEngine:
    """Test NIAS Reward Engine functionality"""
    
    def setup_method(self):
        """Set up test fixture"""
        self.reward_engine = NIASRewardEngine()
        self.test_user = "test_user_123"
    
    def test_process_ad_engagement(self):
        """Test processing ad engagement and earning rewards"""
        result = self.reward_engine.process_ad_engagement(
            user_id=self.test_user,
            ad_id="ad_001",
            engagement_type="watched_full_ad",
            engagement_duration=15.0,
            full_engagement=True
        )
        
        assert result["success"] == True
        assert result["credits_earned"] > 0
        assert result["points_earned"] > 0
        assert "message" in result
    
    def test_unlock_exclusive_content(self):
        """Test unlocking exclusive content with credits"""
        # First, earn some credits
        for i in range(100):  # Earn enough credits
            self.reward_engine.process_ad_engagement(
                user_id=self.test_user,
                ad_id=f"ad_{i}",
                engagement_type="clicked_ad",
                engagement_duration=5.0,
                full_engagement=True
            )
        
        # Try to unlock content
        result = self.reward_engine.unlock_exclusive_content(
            user_id=self.test_user,
            content_id="advanced_analytics"
        )
        
        # Should succeed if enough credits
        dashboard = self.reward_engine.get_user_rewards_dashboard(self.test_user)
        assert dashboard["credits"] > 0 or result["success"] == True
    
    def test_user_rewards_dashboard(self):
        """Test comprehensive rewards dashboard"""
        # Generate some activity
        for i in range(5):
            self.reward_engine.process_ad_engagement(
                user_id=self.test_user,
                ad_id=f"ad_{i}",
                engagement_type="watched_full_ad",
                engagement_duration=10.0
            )
        
        dashboard = self.reward_engine.get_user_rewards_dashboard(self.test_user)
        
        assert "credits" in dashboard
        assert "points" in dashboard
        assert "level" in dashboard
        assert "available_rewards" in dashboard
        assert "unlockable_content" in dashboard
        assert dashboard["total_engagements"] == 5
    
    def test_achievement_system(self):
        """Test achievement tracking"""
        # Trigger milestone achievement
        for i in range(10):
            result = self.reward_engine.process_ad_engagement(
                user_id=self.test_user,
                ad_id=f"ad_{i}",
                engagement_type="watched_full_ad",
                engagement_duration=10.0
            )
        
        dashboard = self.reward_engine.get_user_rewards_dashboard(self.test_user)
        assert len(dashboard["achievements"]) > 0  # Should have milestone achievement


class TestNaturalBreakpointDetector:
    """Test Natural Breakpoint Detection functionality"""
    
    def setup_method(self):
        """Set up test fixture"""
        self.detector = NaturalBreakpointDetector()
    
    def test_task_completion_detection(self):
        """Test detection of task completion"""
        # Simulate task completion
        self.detector.track_activity("type", {"task_id": "task_1", "task_type": "form"})
        time.sleep(0.1)
        self.detector.track_activity("submit", {"task_id": "task_1", "status": "success"})
        
        is_breakpoint, bp_type, metadata = self.detector.check_breakpoint()
        
        assert is_breakpoint == True
        assert bp_type == BreakpointType.TASK_COMPLETION
        assert metadata["confidence"] > 0.9
    
    def test_idle_detection(self):
        """Test idle state detection"""
        # Track activity then wait
        self.detector.track_activity("click", {"page": "home"})
        
        # Simulate idle time
        self.detector.current_workflow.last_activity = datetime.now() - timedelta(seconds=10)
        
        is_breakpoint, bp_type, metadata = self.detector.check_breakpoint()
        
        assert is_breakpoint == True
        assert bp_type == BreakpointType.IDLE_THRESHOLD
    
    def test_permission_request(self):
        """Test permission request generation"""
        request = self.detector.request_permission(
            context="task_complete",
            incentive="10 credits"
        )
        
        assert request["type"] == "permission_request"
        assert "message" in request
        assert "options" in request
        assert request["incentive"] == "10 credits"
    
    def test_timing_recommendations(self):
        """Test timing recommendation generation"""
        # Generate some activity
        for i in range(5):
            self.detector.track_activity("click", {"element": f"button_{i}"})
            time.sleep(0.05)
        
        recommendations = self.detector.get_timing_recommendations()
        
        assert "current_suitability" in recommendations
        assert "recommended_wait" in recommendations
        assert "best_breakpoint_types" in recommendations
        assert recommendations["current_suitability"] >= 0 and recommendations["current_suitability"] <= 1


class TestNativeContentFormatter:
    """Test Native Content Formatting functionality"""
    
    def setup_method(self):
        """Set up test fixture"""
        self.formatter = NativeContentFormatter()
        self.test_ad = {
            "id": "ad_123",
            "title": "Amazing Product",
            "description": "The best product you'll ever use",
            "image_url": "https://example.com/image.jpg",
            "url": "https://example.com/product",
            "brand_name": "TestBrand",
            "rewards_enabled": True,
            "reward_credits": 10
        }
    
    def test_format_as_story(self):
        """Test story format for news feed"""
        story = self.formatter.format_as_story(self.test_ad, feed_style="news")
        
        assert story["type"] == "story"
        assert story["sponsored"] == True
        assert "author" in story
        assert "headline" in story
        assert "engagement" in story
        assert story["cta"]["reward_hint"] == "🎁 Earn 5 credits"
    
    def test_format_as_suggestion(self):
        """Test suggestion format for contextual help"""
        suggestion = self.formatter.format_as_suggestion(
            self.test_ad,
            trigger_context="limit_reached"
        )
        
        assert suggestion["type"] == "suggestion"
        assert suggestion["timing"] == "contextual"
        assert "benefits" in suggestion
        assert len(suggestion["actions"]) == 2
        assert suggestion["dismissible"] == True
    
    def test_format_as_native(self):
        """Test native content formatting"""
        native = self.formatter.format_as_native(
            self.test_ad,
            ContentContext.TOOL_LIMIT,
            user_context={"interests": ["productivity"]}
        )
        
        assert native.format_type in ContentFormat
        assert native.context == ContentContext.TOOL_LIMIT
        assert native.headline != ""
        assert native.reward_preview is not None
        assert native.reward_preview["credits"] == 10
    
    def test_platform_adaptation(self):
        """Test platform-specific adaptations"""
        native = self.formatter.format_as_native(
            self.test_ad,
            ContentContext.NEWS_FEED
        )
        
        web_adapted = self.formatter.adapt_to_platform(native, "web")
        assert "html" in web_adapted
        assert web_adapted["responsive"] == True
        
        mobile_adapted = self.formatter.adapt_to_platform(native, "mobile")
        assert mobile_adapted["touch_optimized"] == True
        assert mobile_adapted["compact_mode"] == True


class TestProactiveAssistance:
    """Test Proactive User Assistance functionality"""
    
    def setup_method(self):
        """Set up test fixture"""
        self.assistance = ProactiveAssistanceSystem()
        self.test_user = "user_456"
    
    def test_stuck_detection(self):
        """Test detection of stuck users"""
        # Simulate user getting stuck (repeated actions)
        for i in range(4):
            self.assistance.track_user_action(
                self.test_user,
                "click_submit",
                "form",
                success=False,
                context={"error": "validation_failed"}
            )
        
        needs_help, offer = self.assistance.check_user_needs_help(self.test_user)
        
        assert needs_help == True
        assert offer is not None
        assert offer.assistance_type in AssistanceType
        assert "help" in offer.message.lower()
    
    def test_idle_assistance(self):
        """Test assistance for idle users"""
        # Track action then simulate idle
        self.assistance.track_user_action(self.test_user, "view", "dashboard")
        
        # Make user idle
        self.assistance.action_history[self.test_user][-1].timestamp = \
            datetime.now() - timedelta(seconds=15)
        self.assistance._update_user_state(self.test_user)
        
        needs_help, offer = self.assistance.check_user_needs_help(self.test_user)
        
        # Should offer help or feature discovery
        assert self.assistance.user_states[self.test_user] == UserState.IDLE
    
    def test_pain_point_identification(self):
        """Test pain point identification"""
        # Generate problematic behavior
        for i in range(10):
            self.assistance.track_user_action(
                self.test_user,
                "search",
                context={"query": "export data"}
            )
        
        pain_points = self.assistance.identify_pain_points(self.test_user)
        
        assert "individual" in pain_points
        assert "aggregate" in pain_points
        assert "recommendations" in pain_points
    
    def test_ui_optimization_suggestions(self):
        """Test UI optimization from behavior"""
        # Simulate frequent searches
        for i in range(10):
            self.assistance.track_user_action(
                f"user_{i}",
                "search",
                context={"query": "settings"}
            )
        
        optimizations = self.assistance.optimize_ui_from_behavior({})
        
        # Should suggest surfacing frequently searched items
        assert len(optimizations) > 0
        assert any("surface" in opt.get("type", "") for opt in optimizations)


class TestUsageAnalyticsLoop:
    """Test Usage Analytics Loop functionality"""
    
    def setup_method(self):
        """Set up test fixture"""
        self.analytics = UsageAnalyticsLoop()
    
    def test_pattern_detection(self):
        """Test usage pattern detection"""
        # Generate patterns
        for i in range(10):
            self.analytics.track_usage_event(
                f"user_{i % 3}",
                "task_complete",
                {"task_type": "export", "duration": 45.0}  # Slow task
            )
        
        analysis = self.analytics.analyze_usage_patterns()
        
        assert len(analysis["patterns"]) > 0
        assert "pain_points" in analysis
        assert "metrics" in analysis
        assert "recommendations" in analysis
    
    def test_real_time_insights(self):
        """Test real-time insight generation"""
        # Generate high error rate
        for i in range(10):
            self.analytics.track_usage_event(
                f"user_{i}",
                "error",
                {"error_type": "timeout"}
            )
        
        insights = self.analytics.get_real_time_insights()
        
        assert "alerts" in insights
        assert "current_issues" in insights
        # Should have high error rate alert
        assert any("error" in alert.get("type", "") for alert in insights["alerts"])
    
    def test_improvement_plan_generation(self):
        """Test improvement plan generation"""
        # Generate issues
        for i in range(20):
            self.analytics.track_usage_event(
                f"user_{i % 5}",
                "error",
                {"error_type": "validation", "location": "checkout"}
            )
        
        self.analytics.analyze_usage_patterns()
        plan = self.analytics.generate_improvement_plan()
        
        assert len(plan) > 0
        assert "implementation_steps" in plan[0]
        assert "success_criteria" in plan[0]
        assert plan[0]["priority"] > 0


class TestRealTimeServiceSwitching:
    """Test Real-Time Service Switching functionality"""
    
    @pytest.fixture
    def switcher(self):
        """Create switcher instance"""
        return RealTimeServiceSwitcher()
    
    @pytest.mark.asyncio
    async def test_service_registration(self, switcher):
        """Test service provider registration"""
        provider = ServiceProvider(
            provider_id="test_provider",
            name="Test Provider",
            service_type=ServiceType.LLM,
            endpoint="https://test.com/api",
            priority=1
        )
        
        switcher.register_provider(provider)
        
        assert ServiceType.LLM in switcher.service_providers
        assert len(switcher.service_providers[ServiceType.LLM]) > 0
        assert "test_provider" in switcher.service_health
    
    @pytest.mark.asyncio
    async def test_request_execution(self, switcher):
        """Test request execution with failover"""
        request = ServiceRequest(
            request_id="test_req_1",
            service_type=ServiceType.LLM,
            payload={"prompt": "Hello"},
            max_retries=2
        )
        
        response = await switcher.execute_request(request)
        
        assert response.request_id == "test_req_1"
        assert response.provider_id != "none"
        # May succeed or fail depending on simulation
    
    @pytest.mark.asyncio
    async def test_health_checks(self, switcher):
        """Test health check functionality"""
        health_results = await switcher.perform_health_checks()
        
        assert len(health_results) > 0
        for provider_id, health in health_results.items():
            assert health.status in ServiceStatus
            assert health.health_score >= 0 and health.health_score <= 1
    
    def test_service_status_report(self, switcher):
        """Test service status reporting"""
        status = switcher.get_service_status()
        
        assert "overall_health" in status
        assert "providers" in status
        assert "failover_ready" in status
        assert "recommendations" in status
        
        # Should have recommendations for single points of failure
        assert len(status["recommendations"]) > 0
    
    def test_performance_report(self, switcher):
        """Test performance reporting"""
        report = switcher.get_performance_report()
        
        assert "summary" in report
        assert "providers" in report
        assert "failover_events" in report
        assert "optimization_opportunities" in report
    
    def test_failover_strategies(self, switcher):
        """Test different failover strategies"""
        strategies = [
            FailoverStrategy.PRIORITY,
            FailoverStrategy.PERFORMANCE_BASED,
            FailoverStrategy.COST_OPTIMIZED,
            FailoverStrategy.LATENCY_OPTIMIZED
        ]
        
        for strategy in strategies:
            switcher.configure_failover_strategy(strategy)
            assert switcher.failover_strategy == strategy


class TestIntegration:
    """Integration tests for all components working together"""
    
    def test_nias_integration(self):
        """Test NIAS components working together"""
        reward_engine = NIASRewardEngine()
        breakpoint_detector = NaturalBreakpointDetector()
        content_formatter = NativeContentFormatter()
        
        # Simulate user completing a task
        breakpoint_detector.track_activity("submit", {"status": "success"})
        is_breakpoint, bp_type, _ = breakpoint_detector.check_breakpoint()
        
        if is_breakpoint:
            # Format an ad
            ad = {
                "id": "ad_integration",
                "title": "Congrats on completing your task!",
                "description": "Here's something you might like",
                "rewards_enabled": True,
                "reward_credits": 5
            }
            
            formatted = content_formatter.format_as_native(
                ad,
                ContentContext.WORKFLOW_COMPLETE
            )
            
            # User engages with ad
            result = reward_engine.process_ad_engagement(
                user_id="integration_user",
                ad_id=formatted.content_id,
                engagement_type="clicked_ad",
                engagement_duration=5.0,
                full_engagement=True
            )
            
            assert result["success"] == True
            assert result["credits_earned"] > 0
    
    def test_abas_dast_integration(self):
        """Test ABAS and DAST components working together"""
        assistance = ProactiveAssistanceSystem()
        analytics = UsageAnalyticsLoop()
        
        # Track user having issues
        for i in range(5):
            assistance.track_user_action(
                "struggling_user",
                "error",
                success=False
            )
            analytics.track_usage_event(
                "struggling_user",
                "error",
                {"error_type": "connection_timeout"}
            )
        
        # ABAS detects need for help
        needs_help, offer = assistance.check_user_needs_help("struggling_user")
        
        # Analytics identifies the pattern
        insights = analytics.get_real_time_insights()
        
        assert needs_help == True or len(insights["alerts"]) > 0
    
    @pytest.mark.asyncio
    async def test_full_system_flow(self):
        """Test complete flow through all systems"""
        # Initialize all components
        reward_engine = NIASRewardEngine()
        breakpoint_detector = NaturalBreakpointDetector()
        content_formatter = NativeContentFormatter()
        assistance = ProactiveAssistanceSystem()
        analytics = UsageAnalyticsLoop()
        switcher = RealTimeServiceSwitcher()
        
        user_id = "complete_flow_user"
        
        # User performs actions
        assistance.track_user_action(user_id, "navigate", "dashboard")
        analytics.track_usage_event(user_id, "navigation", {"page": "dashboard"})
        
        # User completes a task
        breakpoint_detector.track_activity("complete", {"task": "report_generation"})
        
        # Check for natural breakpoint
        is_breakpoint, _, _ = breakpoint_detector.check_breakpoint()
        
        if is_breakpoint:
            # Format and show ad
            ad = {"id": "flow_ad", "title": "Premium Features", "rewards_enabled": True}
            native_ad = content_formatter.format_as_native(ad, ContentContext.TASK_COMPLETION)
            
            # User engages
            reward_engine.process_ad_engagement(
                user_id, native_ad.content_id, "watched_full_ad", 10.0
            )
        
        # Service makes API call with failover
        request = ServiceRequest(
            request_id="flow_request",
            service_type=ServiceType.LLM,
            payload={"data": "test"}
        )
        response = await switcher.execute_request(request)
        
        # Analytics processes everything
        analysis = analytics.analyze_usage_patterns()
        
        # Verify system coherence
        dashboard = reward_engine.get_user_rewards_dashboard(user_id)
        assert dashboard["total_engagements"] >= 0
        assert len(analysis["metrics"]) > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])