#!/usr/bin/env python3
"""
DΛST Core - Dynamic Lambda Symbol Tracker
Real-time symbolic context tracking and activity stream management

Part of the Lambda Products Suite by LUKHAS AI
Commercial Version - Ready for Enterprise Deployment
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("Lambda.DΛST")


class SymbolCategory(Enum):
    """Categories of symbolic tags"""

    ACTIVITY = "activity"  # Current activities (work, rest, create)
    CONTEXT = "context"  # Environmental context (home, office, travel)
    MOOD = "mood"  # Emotional/mental state
    FOCUS = "focus"  # Focus areas (project, learning, problem)
    GOAL = "goal"  # Current goals and intentions
    RELATIONSHIP = "relationship"  # Social context
    TEMPORAL = "temporal"  # Time-based context (morning, deadline)
    CREATIVE = "creative"  # Creative activities and inspiration
    LEARNING = "learning"  # Knowledge acquisition activities
    WELLNESS = "wellness"  # Health and wellbeing activities


class SymbolSource(Enum):
    """Sources of symbolic information"""

    USER_EXPLICIT = "user_explicit"  # Manually set by user
    CALENDAR = "calendar"  # Calendar integration
    ACTIVITY_TRACKER = "activity_tracker"  # Device/app activity
    LOCATION = "location"  # GPS/location services
    BIOMETRIC = "biometric"  # Wearables/health devices
    APP_INTEGRATION = "app_integration"  # Third-party app data
    AI_INFERENCE = "ai_inference"  # ML-derived insights
    SOCIAL = "social"  # Social media/communication
    ENVIRONMENTAL = "environmental"  # IoT/environmental sensors


class SymbolConfidence(Enum):
    """Confidence levels for symbolic information"""

    EXPLICIT = "explicit"  # 1.0 - User explicitly set
    HIGH = "high"  # 0.8-0.9 - Strong evidence
    MEDIUM = "medium"  # 0.5-0.7 - Moderate evidence
    LOW = "low"  # 0.2-0.4 - Weak evidence
    INFERRED = "inferred"  # 0.1-0.3 - AI guess


@dataclass
class SymbolicTag:
    """Individual symbolic tag with metadata"""

    symbol: str  # The symbolic tag itself
    category: SymbolCategory  # Category of symbol
    source: SymbolSource  # Where it came from
    confidence: float  # Confidence level (0.0-1.0)
    weight: float = 1.0  # Importance weight
    expires_at: Optional[datetime] = None  # When tag becomes invalid
    metadata: dict[str, Any] = None  # Additional context
    lambda_signature: str = None  # Λ authenticity signature
    created_at: datetime = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.lambda_signature is None:
            tag_hash = hashlib.sha256(f"{self.symbol}{self.category.value}".encode()).hexdigest()[:8]
            self.lambda_signature = f"Λ-SYMBOL-{tag_hash.upper()}"

    def is_valid(self) -> bool:
        """Check if symbolic tag is still valid"""
        return not (self.expires_at and datetime.now() > self.expires_at)

    def update_confidence(self, new_evidence: float, source_weight: float = 1.0):
        """Update confidence based on new evidence"""
        # Weighted average with source reliability
        total_weight = 1.0 + source_weight
        self.confidence = (self.confidence + (new_evidence * source_weight)) / total_weight
        self.confidence = min(1.0, max(0.0, self.confidence))
        self.last_updated = datetime.now()


@dataclass
class ContextSnapshot:
    """Complete symbolic context at a point in time"""

    user_id: str
    tags: list[SymbolicTag]
    primary_activity: Optional[str] = None
    focus_score: float = 0.5  # How focused the context is (0.0-1.0)
    coherence_score: float = 0.5  # How coherent the tags are together
    stability_score: float = 0.5  # How stable this context is
    lambda_fingerprint: str = None  # Unique identifier for this context
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.lambda_fingerprint is None:
            context_data = f"{self.user_id}{len(self.tags)}{self.timestamp.isoformat()}"
            context_hash = hashlib.sha256(context_data.encode()).hexdigest()[:12]
            self.lambda_fingerprint = f"Λ-CTX-{context_hash.upper()}"


@dataclass
class SymbolRule:
    """Rules for symbolic tag management"""

    id: str
    condition: str  # Rule condition (e.g., "if location:office")
    action: str  # Action to take (e.g., "add work")
    target_symbol: str  # Symbol to add/remove/modify
    priority: int = 0  # Rule priority (higher = more important)
    enabled: bool = True
    lambda_signature: str = None


class DΛST:
    """
    Dynamic Lambda Symbol Tracker

    Core Features:
    - Real-time symbolic context tracking
    - Multi-source data integration
    - Intelligent symbol inference
    - Context coherence analysis
    - Temporal pattern recognition
    - Integration with NIΛS and ΛBAS systems
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()
        self.lambda_brand = "Λ"

        # Core storage
        self.user_contexts: dict[str, ContextSnapshot] = {}
        self.symbol_histories: dict[str, list[tuple[datetime, list[SymbolicTag]]]] = {}
        self.symbol_rules: dict[str, list[SymbolRule]] = {}
        self.symbol_patterns: dict[str, dict[str, Any]] = {}  # Learned patterns

        # Integration connectors
        self.data_sources: dict[str, Any] = {}
        self.external_integrations: dict[str, bool] = {
            "calendar": False,
            "location": False,
            "activity_tracker": False,
            "biometric": False,
        }

        # Symbol analysis
        self.symbol_relationships: dict[str, dict[str, float]] = {}  # Symbol co-occurrence
        self.temporal_patterns: dict[str, list[tuple[int, list[str]]]] = {}  # Hour -> common symbols

        logger.info("DΛST system initialized with symbolic consciousness")

    def _default_config(self) -> dict:
        """Default DΛST configuration"""
        return {
            "brand": "LUKHAS",
            "symbol": "Λ",
            "max_active_symbols": 50,
            "symbol_decay_hours": 24,
            "confidence_threshold": 0.2,
            "auto_inference": True,
            "pattern_learning": True,
            "temporal_analysis": True,
            "coherence_analysis": True,
            "privacy_mode": True,
        }

    async def register_user(self, user_id: str, initial_tags: Optional[list[str]] = None) -> bool:
        """Register a new user with DΛST system"""
        try:
            # Create initial context
            if initial_tags is None:
                initial_tags = ["general", "available"]

            symbolic_tags = [
                SymbolicTag(
                    symbol=tag,
                    category=SymbolCategory.ACTIVITY,
                    source=SymbolSource.USER_EXPLICIT,
                    confidence=1.0,
                )
                for tag in initial_tags
            ]

            context = ContextSnapshot(
                user_id=user_id,
                tags=symbolic_tags,
                primary_activity=initial_tags[0] if initial_tags else None,
            )

            self.user_contexts[user_id] = context
            self.symbol_histories[user_id] = []
            self.symbol_rules[user_id] = []
            self.symbol_patterns[user_id] = {}

            # Initialize default rules
            await self._create_default_rules(user_id)

            logger.info(f"Registered user {user_id} with DΛST symbolic tracking")
            return True

        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
            return False

    async def _create_default_rules(self, user_id: str):
        """Create default symbolic rules for a user"""
        default_rules = [
            SymbolRule(
                id="morning-energy",
                condition="time >= 06:00 AND time <= 10:00",
                action="add",
                target_symbol="morning-energy",
                priority=1,
            ),
            SymbolRule(
                id="evening-wind-down",
                condition="time >= 18:00 AND time <= 22:00",
                action="add",
                target_symbol="evening",
                priority=1,
            ),
            SymbolRule(
                id="focus-coherence",
                condition="focus_score >= 0.8",
                action="add",
                target_symbol="deep-focus",
                priority=2,
            ),
            SymbolRule(
                id="activity-cleanup",
                condition="symbol_age >= 4 hours AND confidence <= 0.3",
                action="remove",
                target_symbol="*",  # Any symbol matching condition
                priority=0,
            ),
        ]

        for rule in default_rules:
            rule.id = f"{user_id}-{rule.id}"
            rule.lambda_signature = f"Λ-RULE-{rule.id[:8].upper()}"

        self.symbol_rules[user_id] = default_rules

    async def add_symbol(
        self,
        user_id: str,
        symbol: str,
        category: SymbolCategory,
        source: SymbolSource = SymbolSource.USER_EXPLICIT,
        confidence: float = 1.0,
        metadata: Optional[dict] = None,
        expires_in_hours: Optional[int] = None,
    ) -> bool:
        """Add a symbolic tag to user's context"""
        if user_id not in self.user_contexts:
            logger.error(f"User not registered: {user_id}")
            return False

        try:
            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)

            # Create symbolic tag
            tag = SymbolicTag(
                symbol=symbol,
                category=category,
                source=source,
                confidence=confidence,
                metadata=metadata or {},
                expires_at=expires_at,
            )

            # Get current context
            context = self.user_contexts[user_id]

            # Check if symbol already exists - update if so
            existing_tag = None
            for existing in context.tags:
                if existing.symbol == symbol and existing.category == category:
                    existing_tag = existing
                    break

            if existing_tag:
                # Update existing tag with new evidence
                source_weights = {
                    SymbolSource.USER_EXPLICIT: 1.0,
                    SymbolSource.CALENDAR: 0.9,
                    SymbolSource.ACTIVITY_TRACKER: 0.8,
                    SymbolSource.BIOMETRIC: 0.7,
                    SymbolSource.AI_INFERENCE: 0.5,
                }

                weight = source_weights.get(source, 0.6)
                existing_tag.update_confidence(confidence, weight)

                # Update metadata
                existing_tag.metadata.update(tag.metadata)

                if expires_at and (not existing_tag.expires_at or expires_at > existing_tag.expires_at):
                    existing_tag.expires_at = expires_at

            else:
                # Add new tag
                context.tags.append(tag)

                # Limit number of active symbols
                if len(context.tags) > self.config["max_active_symbols"]:
                    # Remove lowest confidence, expired, or oldest symbols
                    context.tags.sort(
                        key=lambda t: (
                            t.is_valid(),  # Valid first
                            t.confidence,  # Higher confidence first
                            t.last_updated,  # More recent first
                        ),
                        reverse=True,
                    )
                    context.tags = context.tags[: self.config["max_active_symbols"]]

            # Update context analysis
            await self._update_context_analysis(user_id)

            # Learn symbol relationships
            if self.config["pattern_learning"]:
                await self._update_symbol_relationships(user_id, symbol)

            logger.debug(f"Added symbol '{symbol}' to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding symbol: {e}")
            return False

    async def remove_symbol(self, user_id: str, symbol: str, category: Optional[SymbolCategory] = None) -> bool:
        """Remove a symbolic tag from user's context"""
        if user_id not in self.user_contexts:
            return False

        try:
            context = self.user_contexts[user_id]
            original_count = len(context.tags)

            # Remove matching symbols
            context.tags = [
                tag
                for tag in context.tags
                if not (tag.symbol == symbol and (category is None or tag.category == category))
            ]

            removed = len(context.tags) < original_count

            if removed:
                await self._update_context_analysis(user_id)
                logger.debug(f"Removed symbol '{symbol}' from user {user_id}")

            return removed

        except Exception as e:
            logger.error(f"Error removing symbol: {e}")
            return False

    async def get_current_tags(
        self,
        user_id: str,
        category_filter: Optional[SymbolCategory] = None,
        confidence_threshold: Optional[float] = None,
    ) -> list[str]:
        """Get current symbolic tags for a user (primary API for integrations)"""
        if user_id not in self.user_contexts:
            return []

        try:
            context = self.user_contexts[user_id]
            threshold = confidence_threshold or self.config["confidence_threshold"]

            # Filter valid, high-confidence tags
            filtered_tags = [
                tag
                for tag in context.tags
                if (
                    tag.is_valid()
                    and tag.confidence >= threshold
                    and (category_filter is None or tag.category == category_filter)
                )
            ]

            # Sort by confidence and weight
            filtered_tags.sort(key=lambda t: t.confidence * t.weight, reverse=True)

            return [tag.symbol for tag in filtered_tags]

        except Exception as e:
            logger.error(f"Error getting current tags: {e}")
            return []

    async def get_context_snapshot(self, user_id: str) -> Optional[ContextSnapshot]:
        """Get complete context snapshot for a user"""
        if user_id not in self.user_contexts:
            return None

        # Clean expired symbols first
        await self._clean_expired_symbols(user_id)

        # Update analysis scores
        await self._update_context_analysis(user_id)

        return self.user_contexts[user_id]

    async def _clean_expired_symbols(self, user_id: str):
        """Remove expired symbols from user context"""
        if user_id not in self.user_contexts:
            return

        context = self.user_contexts[user_id]
        context.tags = [tag for tag in context.tags if tag.is_valid()]

    async def _update_context_analysis(self, user_id: str):
        """Update context analysis scores"""
        if user_id not in self.user_contexts:
            return

        context = self.user_contexts[user_id]
        valid_tags = [tag for tag in context.tags if tag.is_valid()]

        if not valid_tags:
            context.focus_score = 0.0
            context.coherence_score = 0.0
            context.stability_score = 0.0
            return

        # Calculate focus score (how concentrated the symbols are)
        category_counts = {}
        for tag in valid_tags:
            category_counts[tag.category] = category_counts.get(tag.category, 0) + 1

        if category_counts:
            max_category_count = max(category_counts.values())
            context.focus_score = max_category_count / len(valid_tags)

        # Calculate coherence score (how well symbols work together)
        coherence_sum = 0.0
        coherence_count = 0

        for i, tag1 in enumerate(valid_tags):
            for tag2 in valid_tags[i + 1 :]:
                relationship_key = f"{tag1.symbol}:{tag2.symbol}"
                reverse_key = f"{tag2.symbol}:{tag1.symbol}"

                coherence = 0.5  # Default neutral coherence
                if user_id in self.symbol_relationships:
                    user_relationships = self.symbol_relationships[user_id]
                    if relationship_key in user_relationships:
                        coherence = user_relationships[relationship_key]
                    elif reverse_key in user_relationships:
                        coherence = user_relationships[reverse_key]

                coherence_sum += coherence
                coherence_count += 1

        if coherence_count > 0:
            context.coherence_score = coherence_sum / coherence_count
        else:
            context.coherence_score = 1.0  # Single symbol is perfectly coherent

        # Calculate stability score (how much context has changed recently)
        if self.symbol_histories.get(user_id):
            recent_history = self.symbol_histories[user_id][-3:]  # Last 3 snapshots
            if len(recent_history) > 1:
                current_symbols = {tag.symbol for tag in valid_tags}

                stability_scores = []
                for _timestamp, historical_tags in recent_history[:-1]:  # Exclude current
                    historical_symbols = {tag.symbol for tag in historical_tags}

                    if historical_symbols or current_symbols:
                        intersection = current_symbols.intersection(historical_symbols)
                        union = current_symbols.union(historical_symbols)
                        similarity = len(intersection) / len(union) if union else 1.0
                        stability_scores.append(similarity)

                if stability_scores:
                    context.stability_score = sum(stability_scores) / len(stability_scores)

        # Update primary activity (highest confidence activity-type symbol)
        activity_tags = [tag for tag in valid_tags if tag.category == SymbolCategory.ACTIVITY]
        if activity_tags:
            primary_tag = max(activity_tags, key=lambda t: t.confidence * t.weight)
            context.primary_activity = primary_tag.symbol
        else:
            context.primary_activity = None

    async def _update_symbol_relationships(self, user_id: str, new_symbol: str):
        """Update learned relationships between symbols"""
        if user_id not in self.symbol_relationships:
            self.symbol_relationships[user_id] = {}

        context = self.user_contexts[user_id]
        current_symbols = [tag.symbol for tag in context.tags if tag.is_valid()]

        # Update co-occurrence relationships
        for existing_symbol in current_symbols:
            if existing_symbol != new_symbol:
                relationship_key = f"{new_symbol}:{existing_symbol}"

                # Increase relationship strength
                current_strength = self.symbol_relationships[user_id].get(relationship_key, 0.5)
                new_strength = min(1.0, current_strength + 0.1)
                self.symbol_relationships[user_id][relationship_key] = new_strength

    async def update_from_calendar(self, user_id: str, calendar_events: list[dict]) -> bool:
        """Update symbols from calendar integration"""
        if not self.external_integrations.get("calendar", False):
            return False

        try:
            for event in calendar_events:
                # Extract symbolic information from calendar events
                event_title = event.get("title", "").lower()
                event_type = event.get("type", "meeting")
                event.get("start_time")

                # Determine symbols based on event content
                symbols_to_add = []

                if any(word in event_title for word in ["meeting", "call", "sync"]):
                    symbols_to_add.append(("meeting", SymbolCategory.ACTIVITY))

                if any(word in event_title for word in ["focus", "deep work", "coding"]):
                    symbols_to_add.append(("deep-work", SymbolCategory.FOCUS))

                if any(word in event_title for word in ["break", "lunch", "coffee"]):
                    symbols_to_add.append(("break", SymbolCategory.WELLNESS))

                # Add symbols with calendar confidence
                for symbol, category in symbols_to_add:
                    await self.add_symbol(
                        user_id=user_id,
                        symbol=symbol,
                        category=category,
                        source=SymbolSource.CALENDAR,
                        confidence=0.8,
                        metadata={"event_title": event.get("title"), "event_type": event_type},
                        expires_in_hours=event.get("duration_hours", 2),
                    )

            return True

        except Exception as e:
            logger.error(f"Error updating from calendar: {e}")
            return False

    async def update_from_activity(self, user_id: str, activity_data: dict) -> bool:
        """Update symbols from activity tracker data"""
        if not self.external_integrations.get("activity_tracker", False):
            return False

        try:
            # Extract symbols from activity data
            app_usage = activity_data.get("app_usage", {})
            location = activity_data.get("location")
            activity_data.get("device_state")

            # App usage patterns
            for app, usage_minutes in app_usage.items():
                if usage_minutes > 10:  # Significant usage
                    app_symbols = self._infer_symbols_from_app(app)

                    for symbol, category in app_symbols:
                        confidence = min(0.7, usage_minutes / 60.0)  # Up to 0.7 confidence
                        await self.add_symbol(
                            user_id=user_id,
                            symbol=symbol,
                            category=category,
                            source=SymbolSource.ACTIVITY_TRACKER,
                            confidence=confidence,
                            expires_in_hours=2,
                        )

            # Location-based symbols
            if location:
                location_symbol, category = self._infer_symbol_from_location(location)
                if location_symbol:
                    await self.add_symbol(
                        user_id=user_id,
                        symbol=location_symbol,
                        category=category,
                        source=SymbolSource.LOCATION,
                        confidence=0.8,
                        expires_in_hours=8,  # Location symbols last longer
                    )

            return True

        except Exception as e:
            logger.error(f"Error updating from activity: {e}")
            return False

    def _infer_symbols_from_app(self, app_name: str) -> list[tuple[str, SymbolCategory]]:
        """Infer symbolic tags from application usage"""
        app_mappings = {
            "code": [("coding", SymbolCategory.ACTIVITY), ("focus", SymbolCategory.FOCUS)],
            "vscode": [("coding", SymbolCategory.ACTIVITY), ("development", SymbolCategory.FOCUS)],
            "slack": [
                ("communication", SymbolCategory.ACTIVITY),
                ("team-work", SymbolCategory.RELATIONSHIP),
            ],
            "zoom": [
                ("meeting", SymbolCategory.ACTIVITY),
                ("video-call", SymbolCategory.RELATIONSHIP),
            ],
            "spotify": [("music", SymbolCategory.MOOD), ("creative", SymbolCategory.CREATIVE)],
            "notion": [
                ("planning", SymbolCategory.ACTIVITY),
                ("documentation", SymbolCategory.FOCUS),
            ],
            "browser": [
                ("research", SymbolCategory.LEARNING),
                ("browsing", SymbolCategory.ACTIVITY),
            ],
            "figma": [
                ("design", SymbolCategory.CREATIVE),
                ("visual-work", SymbolCategory.ACTIVITY),
            ],
        }

        app_lower = app_name.lower()
        for app_pattern, symbols in app_mappings.items():
            if app_pattern in app_lower:
                return symbols

        return [("app-usage", SymbolCategory.ACTIVITY)]

    def _infer_symbol_from_location(self, location: str) -> tuple[Optional[str], SymbolCategory]:
        """Infer symbolic tag from location"""
        location_lower = location.lower()

        if any(word in location_lower for word in ["office", "work", "company"]):
            return ("office", SymbolCategory.CONTEXT)
        elif any(word in location_lower for word in ["home", "house", "apartment"]):
            return ("home", SymbolCategory.CONTEXT)
        elif any(word in location_lower for word in ["gym", "fitness", "workout"]):
            return ("fitness", SymbolCategory.WELLNESS)
        elif any(word in location_lower for word in ["cafe", "coffee", "restaurant"]):
            return ("social", SymbolCategory.RELATIONSHIP)
        elif any(word in location_lower for word in ["park", "outdoor", "nature"]):
            return ("outdoor", SymbolCategory.WELLNESS)

        return (None, SymbolCategory.CONTEXT)

    async def apply_symbol_rules(self, user_id: str):
        """Apply symbolic rules for automatic tag management"""
        if user_id not in self.symbol_rules:
            return

        context = self.user_contexts[user_id]
        current_time = datetime.now()

        for rule in self.symbol_rules[user_id]:
            if not rule.enabled:
                continue

            # Evaluate rule condition (simplified evaluation)
            if await self._evaluate_rule_condition(rule, context, current_time):
                await self._execute_rule_action(rule, user_id)

    async def _evaluate_rule_condition(
        self, rule: SymbolRule, context: ContextSnapshot, current_time: datetime
    ) -> bool:
        """Evaluate if a rule condition is met"""
        condition = rule.condition.lower()

        # Time-based conditions
        current_hour = current_time.hour
        if "time >=" in condition and "time <=" in condition:
            # Parse time range (simplified)
            import re

            times = re.findall(r"time [><=]+ (\d{2}):(\d{2})", condition)
            if len(times) >= 2:
                start_hour, start_min = map(int, times[0])
                end_hour, end_min = map(int, times[1])

                start_time = start_hour + start_min / 60.0
                end_time = end_hour + end_min / 60.0
                current_time_float = current_hour + current_time.minute / 60.0

                return start_time <= current_time_float <= end_time

        # Focus score conditions
        if "focus_score >=" in condition:
            threshold_match = re.search(r"focus_score >= ([\d.]+)", condition)
            if threshold_match:
                threshold = float(threshold_match.group(1))
                return context.focus_score >= threshold

        # Symbol age conditions
        if "symbol_age >=" in condition and "confidence <=" in condition:
            age_match = re.search(r"symbol_age >= (\d+) hours", condition)
            conf_match = re.search(r"confidence <= ([\d.]+)", condition)

            if age_match and conf_match:
                age_threshold_hours = int(age_match.group(1))
                conf_threshold = float(conf_match.group(1))

                # Check if any symbols meet this condition
                cutoff_time = current_time - timedelta(hours=age_threshold_hours)
                for tag in context.tags:
                    if tag.last_updated < cutoff_time and tag.confidence <= conf_threshold:
                        return True

        return False

    async def _execute_rule_action(self, rule: SymbolRule, user_id: str):
        """Execute a rule action"""
        action = rule.action.lower()
        target = rule.target_symbol

        if action == "add":
            # Determine appropriate category (simplified)
            category = SymbolCategory.ACTIVITY  # Default
            if "focus" in target:
                category = SymbolCategory.FOCUS
            elif "morning" in target or "evening" in target:
                category = SymbolCategory.TEMPORAL

            await self.add_symbol(
                user_id=user_id,
                symbol=target,
                category=category,
                source=SymbolSource.AI_INFERENCE,
                confidence=0.6,
                metadata={"rule_id": rule.id},
            )

        elif action == "remove":
            if target == "*":
                # Remove symbols matching rule condition
                context = self.user_contexts[user_id]
                current_time = datetime.now()

                # Remove old, low-confidence symbols
                if "symbol_age" in rule.condition and "confidence" in rule.condition:
                    age_match = re.search(r"symbol_age >= (\d+) hours", rule.condition)
                    conf_match = re.search(r"confidence <= ([\d.]+)", rule.condition)

                    if age_match and conf_match:
                        age_threshold_hours = int(age_match.group(1))
                        conf_threshold = float(conf_match.group(1))
                        cutoff_time = current_time - timedelta(hours=age_threshold_hours)

                        context.tags = [
                            tag
                            for tag in context.tags
                            if not (tag.last_updated < cutoff_time and tag.confidence <= conf_threshold)
                        ]
            else:
                await self.remove_symbol(user_id, target)

    def get_symbol_analytics(self, user_id: str, hours: int = 24) -> dict[str, Any]:
        """Get analytics about user's symbolic patterns"""
        if user_id not in self.symbol_histories:
            return {"error": "No symbol history found"}

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_history = [
            (timestamp, tags) for timestamp, tags in self.symbol_histories[user_id] if timestamp > cutoff_time
        ]

        if not recent_history:
            return {"error": "No recent symbol data"}

        # Analyze patterns
        all_symbols = []
        category_counts = {}
        source_counts = {}

        for _timestamp, tags in recent_history:
            for tag in tags:
                all_symbols.append(tag.symbol)
                category = tag.category.value
                source = tag.source.value

                category_counts[category] = category_counts.get(category, 0) + 1
                source_counts[source] = source_counts.get(source, 0) + 1

        # Most common symbols
        symbol_counts = {}
        for symbol in all_symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        most_common = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Current context
        current_context = self.user_contexts.get(user_id)

        return {
            "user_id": user_id,
            "analysis_period_hours": hours,
            "total_symbol_events": len(all_symbols),
            "unique_symbols": len(set(all_symbols)),
            "most_common_symbols": most_common,
            "category_distribution": category_counts,
            "source_distribution": source_counts,
            "current_context": {
                "total_active_symbols": len(current_context.tags) if current_context else 0,
                "focus_score": current_context.focus_score if current_context else 0,
                "coherence_score": current_context.coherence_score if current_context else 0,
                "stability_score": current_context.stability_score if current_context else 0,
                "primary_activity": current_context.primary_activity if current_context else None,
            }
            if current_context
            else None,
        }

    def get_system_metrics(self) -> dict[str, Any]:
        """Get DΛST system metrics"""
        total_users = len(self.user_contexts)
        total_symbols = sum(len(context.tags) for context in self.user_contexts.values())

        # Integration status
        active_integrations = sum(1 for status in self.external_integrations.values() if status)

        # Symbol category distribution
        category_counts = {}
        for context in self.user_contexts.values():
            for tag in context.tags:
                category = tag.category.value
                category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "system": "DΛST",
            "version": "1.0.0-lambda",
            "lambda_brand": self.lambda_brand,
            "total_users": total_users,
            "total_active_symbols": total_symbols,
            "active_integrations": active_integrations,
            "symbol_categories": category_counts,
            "learned_relationships": sum(len(rels) for rels in self.symbol_relationships.values()),
            "config": {
                "max_symbols_per_user": self.config["max_active_symbols"],
                "auto_inference": self.config["auto_inference"],
                "pattern_learning": self.config["pattern_learning"],
                "privacy_mode": self.config["privacy_mode"],
            },
        }


# Demo and testing
if __name__ == "__main__":

    async def demo():
        print("🔮 DΛST - Dynamic Lambda Symbol Tracker Demo")
        print("=" * 60)

        # Initialize DΛST
        dast = DΛST()

        # Register test user
        await dast.register_user("alice", ["working", "focused"])
        print("✅ Registered user: alice")
        print(f"   Initial tags: {await dast.get_current_tags('alice')}")

        # Add some symbols from different sources
        await dast.add_symbol("alice", "coding", SymbolCategory.ACTIVITY, SymbolSource.ACTIVITY_TRACKER, 0.8)
        await dast.add_symbol("alice", "creative-flow", SymbolCategory.CREATIVE, SymbolSource.AI_INFERENCE, 0.6)
        await dast.add_symbol("alice", "office", SymbolCategory.CONTEXT, SymbolSource.LOCATION, 0.9)

        print(f"\n📊 Updated tags: {await dast.get_current_tags('alice')}")

        # Get context snapshot
        context = await dast.get_context_snapshot("alice")
        if context:
            print("\n🎯 Context Analysis:")
            print(f"   Primary Activity: {context.primary_activity}")
            print(f"   Focus Score: {context.focus_score:.2f}")
            print(f"   Coherence Score: {context.coherence_score:.2f}")
            print(f"   Stability Score: {context.stability_score:.2f}")
            print(f"   Λ Fingerprint: {context.lambda_fingerprint}")

        # Simulate activity tracker update
        activity_data = {
            "app_usage": {"vscode": 45, "slack": 10, "browser": 15},
            "location": "home office",
        }

        # Enable activity tracker integration for demo
        dast.external_integrations["activity_tracker"] = True
        dast.external_integrations["location"] = True

        await dast.update_from_activity("alice", activity_data)
        print(f"\n🔄 After activity update: {await dast.get_current_tags('alice')}")

        # Apply rules
        await dast.apply_symbol_rules("alice")
        print(f"\n⚡ After rule application: {await dast.get_current_tags('alice')}")

        # Get analytics
        analytics = dast.get_symbol_analytics("alice", 1)  # Last hour
        print("\n📈 Symbol Analytics:")
        if "error" not in analytics:
            print(f"   Unique symbols: {analytics['unique_symbols']}")
            print(f"   Most common: {analytics['most_common_symbols'][:3]}")
            print(f"   Categories: {analytics['category_distribution']}")

        # System metrics
        system_metrics = dast.get_system_metrics()
        print("\n🔧 System Metrics:")
        print(f"   Total Users: {system_metrics['total_users']}")
        print(f"   Active Symbols: {system_metrics['total_active_symbols']}")
        print(f"   Integrations: {system_metrics['active_integrations']}")
        print(f"   Pattern Learning: {system_metrics['config']['pattern_learning']}")

    asyncio.run(demo())
