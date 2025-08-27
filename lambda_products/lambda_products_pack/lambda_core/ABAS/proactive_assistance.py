"""
Proactive User Assistance System for ABAS
Detects when users are stuck or struggling and offers intelligent help
"""

import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class UserState(Enum):
    """User behavioral states"""

    ACTIVE = "active"
    IDLE = "idle"
    STUCK = "stuck"
    STRUGGLING = "struggling"
    FRUSTRATED = "frustrated"
    EXPLORING = "exploring"
    LEARNING = "learning"
    PRODUCTIVE = "productive"
    CONFUSED = "confused"
    SEARCHING = "searching"


class AssistanceType(Enum):
    """Types of assistance offered"""

    TOOLTIP = "tooltip"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    VIDEO_GUIDE = "video_guide"
    LIVE_CHAT = "live_chat"
    AI_SUGGESTION = "ai_suggestion"
    FEATURE_HIGHLIGHT = "feature_highlight"
    SHORTCUT_TIP = "shortcut_tip"
    EXAMPLE = "example"
    FAQ = "faq"


class PainPointType(Enum):
    """Types of user pain points"""

    NAVIGATION = "navigation"
    FEATURE_DISCOVERY = "feature_discovery"
    TASK_COMPLETION = "task_completion"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE = "performance"
    UNDERSTANDING = "understanding"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    DATA_ENTRY = "data_entry"
    WORKFLOW = "workflow"


@dataclass
class UserAction:
    """Individual user action"""

    timestamp: datetime
    action_type: str
    target: Optional[str] = None
    success: bool = True
    duration: float = 0.0
    error_code: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class StuckPattern:
    """Pattern indicating user is stuck"""

    pattern_id: str
    name: str
    indicators: list[str]
    threshold: float
    confidence: float = 0.0
    occurrences: int = 0


@dataclass
class AssistanceOffer:
    """Proactive assistance offer"""

    offer_id: str
    assistance_type: AssistanceType
    title: str
    message: str
    action_required: bool = False
    auto_dismiss_time: Optional[float] = None
    priority: int = 1
    context: dict[str, Any] = field(default_factory=dict)


class ProactiveAssistanceSystem:
    """
    Detects when users need help and proactively offers assistance
    Makes the system feel intelligent and caring
    """

    def __init__(self):
        self.user_states: dict[str, UserState] = {}
        self.action_history: dict[str, list[UserAction]] = {}
        self.stuck_patterns = self._initialize_stuck_patterns()
        self.assistance_history: dict[str, list[AssistanceOffer]] = {}
        self.pain_points: dict[str, list[PainPointType]] = {}

        # Detection thresholds
        self.idle_threshold = 10.0  # seconds
        self.stuck_threshold = 15.0  # seconds
        self.repeat_action_threshold = 3  # times
        self.error_rate_threshold = 0.3  # 30% errors
        self.frustration_indicators = [
            "rapid_clicks",
            "backspace_spam",
            "escape_key",
            "repeated_undo",
            "rage_clicks",
            "circular_navigation",
        ]

        # Assistance configuration
        self.assistance_cooldown = 60.0  # seconds between offers
        self.last_assistance_time: dict[str, datetime] = {}
        self.dismissed_offers: set[str] = set()

    def track_user_action(
        self,
        user_id: str,
        action_type: str,
        target: Optional[str] = None,
        success: bool = True,
        context: Optional[dict] = None,
    ) -> None:
        """Track user action for pattern detection"""
        if user_id not in self.action_history:
            self.action_history[user_id] = []
            self.user_states[user_id] = UserState.ACTIVE

        action = UserAction(
            timestamp=datetime.now(),
            action_type=action_type,
            target=target,
            success=success,
            context=context or {},
        )

        # Calculate duration from previous action
        if self.action_history[user_id]:
            prev_action = self.action_history[user_id][-1]
            action.duration = (action.timestamp - prev_action.timestamp).total_seconds()

        self.action_history[user_id].append(action)

        # Update user state
        self._update_user_state(user_id)

        # Check for stuck patterns
        self._detect_stuck_patterns(user_id)

    def check_user_needs_help(
        self, user_id: str
    ) -> tuple[bool, Optional[AssistanceOffer]]:
        """
        Check if user needs help and generate appropriate assistance
        Returns (needs_help, assistance_offer)
        """

        # Check cooldown
        if not self._check_assistance_cooldown(user_id):
            return False, None

        # Get current user state
        user_state = self.user_states.get(user_id, UserState.ACTIVE)

        # Priority 1: User is stuck
        if user_state == UserState.STUCK:
            offer = self._generate_stuck_assistance(user_id)
            if offer:
                return True, offer

        # Priority 2: User is struggling
        if user_state == UserState.STRUGGLING:
            offer = self._generate_struggle_assistance(user_id)
            if offer:
                return True, offer

        # Priority 3: User is frustrated
        if user_state == UserState.FRUSTRATED:
            offer = self._generate_frustration_assistance(user_id)
            if offer:
                return True, offer

        # Priority 4: User is confused
        if user_state == UserState.CONFUSED:
            offer = self._generate_confusion_assistance(user_id)
            if offer:
                return True, offer

        # Priority 5: User is idle
        if user_state == UserState.IDLE:
            idle_time = self._calculate_idle_time(user_id)
            if idle_time > self.idle_threshold:
                offer = self._generate_idle_assistance(user_id)
                if offer:
                    return True, offer

        # Priority 6: User is searching
        if user_state == UserState.SEARCHING:
            offer = self._generate_search_assistance(user_id)
            if offer:
                return True, offer

        return False, None

    def identify_pain_points(self, user_id: Optional[str] = None) -> dict[str, Any]:
        """
        Identify pain points from user behavior
        Can be for specific user or across all users
        """
        pain_points_analysis = {
            "individual": {},
            "aggregate": {},
            "recommendations": [],
        }

        if user_id:
            # Analyze specific user
            user_pain_points = self._analyze_user_pain_points(user_id)
            pain_points_analysis["individual"] = user_pain_points

        # Analyze aggregate patterns
        all_pain_points = self._analyze_aggregate_pain_points()
        pain_points_analysis["aggregate"] = all_pain_points

        # Generate recommendations
        recommendations = self._generate_pain_point_recommendations(all_pain_points)
        pain_points_analysis["recommendations"] = recommendations

        return pain_points_analysis

    def optimize_ui_from_behavior(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Generate UI optimization suggestions based on behavior
        """
        optimizations = []

        # Check for frequently searched features
        searched_features = self._identify_frequently_searched_features(behavioral_data)
        for feature in searched_features:
            optimizations.append(
                {
                    "type": "surface_feature",
                    "feature": feature["name"],
                    "reason": f"Searched {feature['count']} times",
                    "suggestion": f"Move '{feature['name']}' to main navigation or dashboard",
                    "impact": "high",
                    "confidence": 0.9,
                }
            )

        # Check for high-abandonment points
        abandonment_points = self._identify_abandonment_points(behavioral_data)
        for point in abandonment_points:
            optimizations.append(
                {
                    "type": "simplify_flow",
                    "location": point["location"],
                    "abandonment_rate": point["rate"],
                    "suggestion": f"Simplify or provide guidance at {point['location']}",
                    "impact": "high",
                    "confidence": 0.85,
                }
            )

        # Check for confusion patterns
        confusion_areas = self._identify_confusion_areas(behavioral_data)
        for area in confusion_areas:
            optimizations.append(
                {
                    "type": "improve_clarity",
                    "area": area["name"],
                    "confusion_indicators": area["indicators"],
                    "suggestion": f"Add tooltips or improve labeling in {area['name']}",
                    "impact": "medium",
                    "confidence": 0.75,
                }
            )

        # Check for inefficient workflows
        inefficient_workflows = self._identify_inefficient_workflows(behavioral_data)
        for workflow in inefficient_workflows:
            optimizations.append(
                {
                    "type": "streamline_workflow",
                    "workflow": workflow["name"],
                    "current_steps": workflow["steps"],
                    "suggested_steps": workflow["optimized_steps"],
                    "suggestion": f"Reduce steps from {workflow['steps']} to {workflow['optimized_steps']}",
                    "impact": "medium",
                    "confidence": 0.7,
                }
            )

        return optimizations

    def record_assistance_response(
        self, user_id: str, offer_id: str, response: str, helpful: Optional[bool] = None
    ) -> None:
        """Record user response to assistance offer"""
        if response == "dismissed":
            self.dismissed_offers.add(offer_id)

        # Update assistance history
        if user_id in self.assistance_history:
            for offer in self.assistance_history[user_id]:
                if offer.offer_id == offer_id:
                    offer.context["user_response"] = response
                    offer.context["helpful"] = helpful
                    break

        # Learn from response
        self._learn_from_assistance_response(user_id, offer_id, response, helpful)

    def _initialize_stuck_patterns(self) -> list[StuckPattern]:
        """Initialize patterns that indicate user is stuck"""
        patterns = [
            StuckPattern(
                pattern_id="repeated_action",
                name="Repeated Same Action",
                indicators=["same_action_3x", "no_progress"],
                threshold=3,
            ),
            StuckPattern(
                pattern_id="circular_navigation",
                name="Circular Navigation",
                indicators=["back_forth_navigation", "revisiting_pages"],
                threshold=2,
            ),
            StuckPattern(
                pattern_id="error_loop",
                name="Error Loop",
                indicators=["repeated_errors", "same_error_3x"],
                threshold=2,
            ),
            StuckPattern(
                pattern_id="search_failure",
                name="Search Without Results",
                indicators=["multiple_searches", "no_selection"],
                threshold=3,
            ),
            StuckPattern(
                pattern_id="form_struggle",
                name="Form Completion Issues",
                indicators=["validation_errors", "field_revisits"],
                threshold=4,
            ),
            StuckPattern(
                pattern_id="feature_hunt",
                name="Looking for Feature",
                indicators=["menu_exploration", "settings_search"],
                threshold=5,
            ),
        ]
        return patterns

    def _update_user_state(self, user_id: str) -> None:
        """Update user state based on recent actions"""
        if user_id not in self.action_history:
            return

        recent_actions = self.action_history[user_id][-10:]

        # Check for idle
        if recent_actions:
            last_action = recent_actions[-1]
            idle_time = (datetime.now() - last_action.timestamp).total_seconds()
            if idle_time > self.idle_threshold:
                self.user_states[user_id] = UserState.IDLE
                return

        # Check for frustration
        frustration_count = sum(
            1
            for action in recent_actions
            if action.action_type in self.frustration_indicators
        )
        if frustration_count >= 3:
            self.user_states[user_id] = UserState.FRUSTRATED
            return

        # Check for struggling (high error rate)
        error_count = sum(1 for action in recent_actions if not action.success)
        if len(recent_actions) > 0:
            error_rate = error_count / len(recent_actions)
            if error_rate > self.error_rate_threshold:
                self.user_states[user_id] = UserState.STRUGGLING
                return

        # Check for searching
        search_count = sum(
            1 for action in recent_actions if "search" in action.action_type.lower()
        )
        if search_count >= 2:
            self.user_states[user_id] = UserState.SEARCHING
            return

        # Check for confused (random actions)
        if self._detect_random_behavior(recent_actions):
            self.user_states[user_id] = UserState.CONFUSED
            return

        # Check for stuck patterns
        if self._is_stuck(user_id):
            self.user_states[user_id] = UserState.STUCK
            return

        # Otherwise, user is active
        self.user_states[user_id] = UserState.ACTIVE

    def _detect_stuck_patterns(self, user_id: str) -> None:
        """Detect if user matches any stuck patterns"""
        if user_id not in self.action_history:
            return

        recent_actions = self.action_history[user_id][-20:]

        for pattern in self.stuck_patterns:
            # Check repeated action pattern
            if pattern.pattern_id == "repeated_action":
                if self._check_repeated_actions(recent_actions):
                    pattern.occurrences += 1
                    pattern.confidence = min(1.0, pattern.occurrences * 0.2)

            # Check circular navigation
            elif pattern.pattern_id == "circular_navigation":
                if self._check_circular_navigation(recent_actions):
                    pattern.occurrences += 1
                    pattern.confidence = min(1.0, pattern.occurrences * 0.25)

            # Check error loop
            elif pattern.pattern_id == "error_loop":
                if self._check_error_loop(recent_actions):
                    pattern.occurrences += 1
                    pattern.confidence = min(1.0, pattern.occurrences * 0.3)

    def _check_repeated_actions(self, actions: list[UserAction]) -> bool:
        """Check for repeated same actions"""
        if len(actions) < 3:
            return False

        # Check last 3 actions
        last_3 = actions[-3:]
        action_types = [a.action_type for a in last_3]
        return len(set(action_types)) == 1

    def _check_circular_navigation(self, actions: list[UserAction]) -> bool:
        """Check for back-and-forth navigation"""
        if len(actions) < 4:
            return False

        targets = [a.target for a in actions[-4:] if a.target]
        if len(targets) < 4:
            return False

        # Check for A-B-A-B pattern
        return targets[0] == targets[2] and targets[1] == targets[3]

    def _check_error_loop(self, actions: list[UserAction]) -> bool:
        """Check for repeated errors"""
        error_actions = [a for a in actions[-5:] if not a.success]
        return len(error_actions) >= 3

    def _detect_random_behavior(self, actions: list[UserAction]) -> bool:
        """Detect random/confused behavior"""
        if len(actions) < 5:
            return False

        # Check for high variety of unrelated actions
        action_types = [a.action_type for a in actions]
        unique_ratio = len(set(action_types)) / len(action_types)

        # High unique ratio with short durations indicates confusion
        avg_duration = statistics.mean(
            [a.duration for a in actions if a.duration > 0] or [1]
        )
        return unique_ratio > 0.8 and avg_duration < 2.0

    def _is_stuck(self, user_id: str) -> bool:
        """Check if user is stuck based on patterns"""
        high_confidence_patterns = [
            p for p in self.stuck_patterns if p.confidence > 0.6
        ]
        return len(high_confidence_patterns) > 0

    def _calculate_idle_time(self, user_id: str) -> float:
        """Calculate how long user has been idle"""
        if user_id not in self.action_history or not self.action_history[user_id]:
            return 0.0

        last_action = self.action_history[user_id][-1]
        return (datetime.now() - last_action.timestamp).total_seconds()

    def _check_assistance_cooldown(self, user_id: str) -> bool:
        """Check if enough time passed since last assistance"""
        if user_id not in self.last_assistance_time:
            return True

        time_since_last = (
            datetime.now() - self.last_assistance_time[user_id]
        ).total_seconds()
        return time_since_last > self.assistance_cooldown

    def _generate_stuck_assistance(self, user_id: str) -> Optional[AssistanceOffer]:
        """Generate assistance for stuck user"""
        # Identify what they're stuck on
        stuck_context = self._identify_stuck_context(user_id)

        return AssistanceOffer(
            offer_id=f"stuck_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.AI_SUGGESTION,
            title="Need Help?",
            message=f"I noticed you might be having trouble with {stuck_context}. Would you like me to help?",
            action_required=True,
            priority=1,
            context={"stuck_on": stuck_context},
        )

    def _generate_struggle_assistance(self, user_id: str) -> Optional[AssistanceOffer]:
        """Generate assistance for struggling user"""
        struggle_type = self._identify_struggle_type(user_id)

        return AssistanceOffer(
            offer_id=f"struggle_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.TUTORIAL,
            title="Quick Tip",
            message=f"Here's a easier way to {struggle_type}",
            auto_dismiss_time=10.0,
            priority=2,
            context={"struggle_type": struggle_type},
        )

    def _generate_frustration_assistance(
        self, user_id: str
    ) -> Optional[AssistanceOffer]:
        """Generate assistance for frustrated user"""
        return AssistanceOffer(
            offer_id=f"frustration_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.LIVE_CHAT,
            title="Let's Fix This Together",
            message="I can see this is frustrating. Would you like to chat with our support team?",
            action_required=True,
            priority=1,
            context={"emotion": "frustrated"},
        )

    def _generate_confusion_assistance(self, user_id: str) -> Optional[AssistanceOffer]:
        """Generate assistance for confused user"""
        return AssistanceOffer(
            offer_id=f"confusion_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.VIDEO_GUIDE,
            title="Watch a Quick Demo",
            message="Would you like to see how this works?",
            auto_dismiss_time=15.0,
            priority=3,
            context={"state": "confused"},
        )

    def _generate_idle_assistance(self, user_id: str) -> Optional[AssistanceOffer]:
        """Generate assistance for idle user"""
        suggested_action = self._suggest_next_action(user_id)

        return AssistanceOffer(
            offer_id=f"idle_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.FEATURE_HIGHLIGHT,
            title="While You're Here",
            message=f"Did you know you can {suggested_action}?",
            auto_dismiss_time=20.0,
            priority=5,
            context={"suggested_action": suggested_action},
        )

    def _generate_search_assistance(self, user_id: str) -> Optional[AssistanceOffer]:
        """Generate assistance for searching user"""
        search_target = self._identify_search_target(user_id)

        return AssistanceOffer(
            offer_id=f"search_{user_id}_{int(time.time())}",
            assistance_type=AssistanceType.SHORTCUT_TIP,
            title="Looking for Something?",
            message=f"Try pressing Ctrl+K to quickly find {search_target}",
            auto_dismiss_time=8.0,
            priority=4,
            context={"search_target": search_target},
        )

    def _identify_stuck_context(self, user_id: str) -> str:
        """Identify what user is stuck on"""
        recent_actions = self.action_history.get(user_id, [])[-5:]
        if not recent_actions:
            return "this task"

        # Look for common targets
        targets = [a.target for a in recent_actions if a.target]
        if targets:
            most_common = max(set(targets), key=targets.count)
            return most_common

        return "this task"

    def _identify_struggle_type(self, user_id: str) -> str:
        """Identify what user is struggling with"""
        recent_errors = [
            a for a in self.action_history.get(user_id, [])[-10:] if not a.success
        ]

        if not recent_errors:
            return "complete this action"

        # Analyze error patterns
        error_types = [a.action_type for a in recent_errors]
        if "form" in " ".join(error_types).lower():
            return "fill out this form"
        elif "upload" in " ".join(error_types).lower():
            return "upload your file"

        return "complete this action"

    def _suggest_next_action(self, user_id: str) -> str:
        """Suggest next action for idle user"""
        suggestions = [
            "explore our new features",
            "customize your dashboard",
            "check out the shortcuts guide",
            "view your analytics",
            "set up integrations",
        ]

        # Could be more intelligent based on user history
        import random

        return random.choice(suggestions)

    def _identify_search_target(self, user_id: str) -> str:
        """Identify what user is searching for"""
        search_actions = [
            a
            for a in self.action_history.get(user_id, [])[-10:]
            if "search" in a.action_type.lower()
        ]

        if search_actions and search_actions[-1].context.get("query"):
            return search_actions[-1].context["query"]

        return "what you need"

    def _analyze_user_pain_points(self, user_id: str) -> dict[str, Any]:
        """Analyze pain points for specific user"""
        if user_id not in self.action_history:
            return {}

        actions = self.action_history[user_id]

        pain_points = {
            "navigation_issues": self._count_navigation_issues(actions),
            "error_frequency": self._calculate_error_frequency(actions),
            "task_abandonment": self._count_abandoned_tasks(actions),
            "time_to_complete": self._calculate_avg_task_time(actions),
            "help_requests": self._count_help_requests(actions),
        }

        # Identify primary pain point
        max_issue = max(
            pain_points.items(),
            key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0,
        )
        pain_points["primary_issue"] = max_issue[0]

        return pain_points

    def _analyze_aggregate_pain_points(self) -> dict[str, Any]:
        """Analyze pain points across all users"""
        all_pain_points = {
            "common_errors": {},
            "abandonment_points": {},
            "slow_tasks": [],
            "help_hotspots": [],
        }

        for _user_id, actions in self.action_history.items():
            # Collect error types
            for action in actions:
                if not action.success and action.error_code:
                    all_pain_points["common_errors"][action.error_code] = (
                        all_pain_points["common_errors"].get(action.error_code, 0) + 1
                    )

            # Identify abandonment points
            abandoned = self._identify_abandonment_point(actions)
            if abandoned:
                all_pain_points["abandonment_points"][abandoned] = (
                    all_pain_points["abandonment_points"].get(abandoned, 0) + 1
                )

        return all_pain_points

    def _generate_pain_point_recommendations(
        self, pain_points: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on pain points"""
        recommendations = []

        # High error areas
        if pain_points.get("common_errors"):
            top_error = max(pain_points["common_errors"].items(), key=lambda x: x[1])
            recommendations.append(
                f"Fix error '{top_error[0]}' - affecting {top_error[1]} users"
            )

        # Abandonment points
        if pain_points.get("abandonment_points"):
            top_abandonment = max(
                pain_points["abandonment_points"].items(), key=lambda x: x[1]
            )
            recommendations.append(
                f"Simplify '{top_abandonment[0]}' - {top_abandonment[1]} users quit here"
            )

        return recommendations

    def _identify_frequently_searched_features(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify features users frequently search for"""
        search_counts = {}

        for _user_id, actions in self.action_history.items():
            for action in actions:
                if "search" in action.action_type.lower() and action.context.get(
                    "query"
                ):
                    query = action.context["query"]
                    search_counts[query] = search_counts.get(query, 0) + 1

        # Return top searched items
        sorted_searches = sorted(
            search_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [{"name": s[0], "count": s[1]} for s in sorted_searches[:5]]

    def _identify_abandonment_points(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify where users abandon tasks"""
        abandonment_points = []

        for _user_id, actions in self.action_history.items():
            # Look for long idle periods after specific actions
            for i in range(len(actions) - 1):
                time_gap = (
                    actions[i + 1].timestamp - actions[i].timestamp
                ).total_seconds()
                if time_gap > 60:  # 1 minute gap suggests abandonment
                    abandonment_points.append(
                        {
                            "location": actions[i].target or actions[i].action_type,
                            "rate": 1.0,  # Would calculate actual rate with more data
                        }
                    )

        return abandonment_points[:5]

    def _identify_confusion_areas(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify areas causing confusion"""
        confusion_areas = []

        # Look for areas with random clicking or repeated actions
        for _user_id, actions in self.action_history.items():
            targets_with_confusion = set()
            for i in range(len(actions) - 3):
                window = actions[i : i + 4]
                if self._detect_random_behavior(window):
                    for action in window:
                        if action.target:
                            targets_with_confusion.add(action.target)

            for target in targets_with_confusion:
                confusion_areas.append(
                    {"name": target, "indicators": ["random_clicks", "hesitation"]}
                )

        return confusion_areas[:5]

    def _identify_inefficient_workflows(
        self, behavioral_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify workflows that could be optimized"""
        workflows = []

        # This would analyze common action sequences and identify optimization opportunities
        # Simplified example
        workflows.append({"name": "Data Export", "steps": 5, "optimized_steps": 2})

        return workflows

    def _count_navigation_issues(self, actions: list[UserAction]) -> int:
        """Count navigation-related issues"""
        return sum(
            1
            for a in actions
            if "navigation" in a.action_type.lower() and not a.success
        )

    def _calculate_error_frequency(self, actions: list[UserAction]) -> float:
        """Calculate error frequency"""
        if not actions:
            return 0.0
        errors = sum(1 for a in actions if not a.success)
        return errors / len(actions)

    def _count_abandoned_tasks(self, actions: list[UserAction]) -> int:
        """Count abandoned tasks"""
        # Simplified - would need task tracking
        abandoned = 0
        for i in range(len(actions) - 1):
            time_gap = (actions[i + 1].timestamp - actions[i].timestamp).total_seconds()
            if time_gap > 300:  # 5 minute gap
                abandoned += 1
        return abandoned

    def _calculate_avg_task_time(self, actions: list[UserAction]) -> float:
        """Calculate average task completion time"""
        # Simplified - would need task boundaries
        if not actions:
            return 0.0

        task_times = []
        current_task_start = actions[0].timestamp

        for i in range(1, len(actions)):
            if actions[i].action_type in ["submit", "save", "complete"]:
                task_time = (actions[i].timestamp - current_task_start).total_seconds()
                task_times.append(task_time)
                if i < len(actions) - 1:
                    current_task_start = actions[i + 1].timestamp

        return statistics.mean(task_times) if task_times else 0.0

    def _count_help_requests(self, actions: list[UserAction]) -> int:
        """Count explicit help requests"""
        return sum(1 for a in actions if "help" in a.action_type.lower())

    def _identify_abandonment_point(self, actions: list[UserAction]) -> Optional[str]:
        """Identify where user abandoned task"""
        if not actions:
            return None

        # Look for last action before long idle
        for i in range(len(actions) - 1):
            time_gap = (actions[i + 1].timestamp - actions[i].timestamp).total_seconds()
            if time_gap > 300:  # 5 minutes
                return actions[i].target or actions[i].action_type

        return None

    def _learn_from_assistance_response(
        self, user_id: str, offer_id: str, response: str, helpful: Optional[bool]
    ) -> None:
        """Learn from user response to improve future assistance"""
        # This would implement learning logic to improve assistance
        # For now, just track success rate
        if helpful is not None:
            # Would update ML model or heuristics
            pass


# Example usage
if __name__ == "__main__":
    assistance_system = ProactiveAssistanceSystem()

    # Simulate user getting stuck
    user_id = "user_123"

    # User tries same action multiple times
    for _i in range(3):
        assistance_system.track_user_action(
            user_id,
            "click_submit",
            "form",
            success=False,
            context={"error": "validation_failed"},
        )
        time.sleep(0.1)

    # Check if user needs help
    needs_help, offer = assistance_system.check_user_needs_help(user_id)

    if needs_help and offer:
        print(f"Assistance offered: {offer.title}")
        print(f"Message: {offer.message}")
        print(f"Type: {offer.assistance_type.value}")

    # Identify pain points
    pain_points = assistance_system.identify_pain_points(user_id)
    print(f"\nPain points: {pain_points}")

    # Get UI optimization suggestions
    optimizations = assistance_system.optimize_ui_from_behavior({})
    print(f"\nUI optimizations: {optimizations}")
