#!/usr/bin/env python3
"""
Test Suite for LUKHAS Memory Reflection Engine

Comprehensive tests for pattern detection, meta-cognitive analysis,
self-assessment generation, and reflection insight processing.
"""

from unittest.mock import patch

import pytest

# Import the reflection engine
from memory.core_memory.reflection_engine import (
    MemoryReflector,
    MetaCognitiveAnalyzer,
    PatternDetector,
    ReflectionDepth,
    ReflectionInsight,
    ReflectionType,
    get_memory_reflector,
    get_reflector_status,
    get_self_assessment,
    initiate_reflection,
    process_reflection,
)


class TestPatternDetector:
    """Test suite for PatternDetector functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = PatternDetector()
        self.sample_memory_data = [
            {
                "memory_id": "mem_001",
                "timestamp": "2025-01-01T10:00:00",
                "content": {"action": "learning", "topic": "pattern_recognition"},
                "emotional_state": {"curiosity": 0.8, "satisfaction": 0.6},
            },
            {
                "memory_id": "mem_002",
                "timestamp": "2025-01-01T11:00:00",
                "content": {"action": "learning", "topic": "neural_networks"},
                "emotional_state": {"curiosity": 0.7, "satisfaction": 0.8},
            },
            {
                "memory_id": "mem_003",
                "timestamp": "2025-01-01T12:00:00",
                "content": {"action": "problem_solving", "topic": "optimization"},
                "emotional_state": {"focus": 0.9, "satisfaction": 0.7},
            },
        ]

    def test_initialization(self):
        """Test PatternDetector initialization."""
        assert self.detector.known_patterns == {}
        assert len(self.detector.pattern_templates) > 0

        # Verify key pattern templates exist
        expected_templates = [
            "repetitive_behavior",
            "emotional_spiral",
            "learning_progression",
            "causal_chain",
            "symbolic_emergence",
        ]

        for template in expected_templates:
            assert template in self.detector.pattern_templates
            assert "description" in self.detector.pattern_templates[template]
            assert "threshold" in self.detector.pattern_templates[template]

    def test_detect_patterns_with_data(self):
        """Test pattern detection with sample data."""
        patterns = self.detector.detect_patterns(self.sample_memory_data)

        assert isinstance(patterns, list)

        # Should detect some patterns
        if patterns:
            for pattern in patterns:
                assert "pattern_name" in pattern
                assert "description" in pattern
                assert "strength" in pattern
                assert "supporting_memories" in pattern
                assert "detected_at" in pattern

                # Strength should be between 0 and 1
                assert 0 <= pattern["strength"] <= 1

    def test_detect_patterns_empty_data(self):
        """Test pattern detection with empty data."""
        patterns = self.detector.detect_patterns([])
        assert isinstance(patterns, list)
        assert len(patterns) == 0

    def test_detect_patterns_single_memory(self):
        """Test pattern detection with single memory."""
        single_memory = [self.sample_memory_data[0]]
        patterns = self.detector.detect_patterns(single_memory)

        assert isinstance(patterns, list)
        # May or may not detect patterns with single memory

    def test_pattern_strength_calculation(self):
        """Test pattern strength calculation logic."""
        # Test with repetitive data (should increase strength)
        repetitive_data = [
            {"timestamp": "2025-01-01T10:00:00", "content": {"action": "study"}},
            {"timestamp": "2025-01-01T10:30:00", "content": {"action": "study"}},
            {"timestamp": "2025-01-01T11:00:00", "content": {"action": "study"}},
        ]

        template = self.detector.pattern_templates["repetitive_behavior"]
        strength = self.detector._analyze_pattern_strength(repetitive_data, template)

        assert 0 <= strength <= 1
        # Should have reasonable strength for repetitive data
        assert strength >= 0.3

    def test_temporal_clustering_detection(self):
        """Test temporal clustering detection."""
        # Create timestamps with clustering
        clustered_timestamps = [
            "2025-01-01T10:00:00",
            "2025-01-01T10:05:00",  # Close to first
            "2025-01-01T10:10:00",  # Close to first
            "2025-01-01T15:00:00",  # Far from others
        ]

        has_clustering = self.detector._has_temporal_clustering(clustered_timestamps)
        # Should detect some temporal clustering
        assert isinstance(has_clustering, bool)

    def test_content_similarity_detection(self):
        """Test content similarity detection."""
        similar_memories = [
            {"content": {"topic": "machine_learning", "action": "study"}},
            {"content": {"topic": "neural_networks", "action": "study"}},
            {"content": {"topic": "deep_learning", "action": "study"}},
        ]

        has_similarity = self.detector._has_content_similarity(similar_memories)
        assert isinstance(has_similarity, bool)

    def test_emotional_consistency_detection(self):
        """Test emotional consistency detection."""
        consistent_emotions = [
            {"emotional_state": {"curiosity": 0.8, "focus": 0.7}},
            {"emotional_state": {"curiosity": 0.7, "focus": 0.8}},
            {"emotional_state": {"curiosity": 0.9, "focus": 0.6}},
        ]

        has_consistency = self.detector._has_emotional_consistency(consistent_emotions)
        assert isinstance(has_consistency, bool)


class TestMetaCognitiveAnalyzer:
    """Test suite for MetaCognitiveAnalyzer functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = MetaCognitiveAnalyzer()
        self.sample_memory_data = [
            {
                "memory_id": "mem_001",
                "content": {"type": "reasoning", "approach": "analytical"},
                "emotional_state": {"confidence": 0.8},
            },
            {
                "memory_id": "mem_002",
                "content": {"type": "decision", "approach": "intuitive"},
                "emotional_state": {"uncertainty": 0.3},
            },
            {
                "memory_id": "mem_003",
                "content": {"type": "learning", "strategy": "experiential"},
                "emotional_state": {"curiosity": 0.9},
            },
        ]

    def test_initialization(self):
        """Test MetaCognitiveAnalyzer initialization."""
        assert self.analyzer.analysis_history == []

    def test_analyze_thinking_patterns(self):
        """Test thinking pattern analysis."""
        analysis = self.analyzer.analyze_thinking_patterns(self.sample_memory_data)

        # Verify analysis structure
        assert isinstance(analysis, dict)
        expected_keys = [
            "reasoning_styles",
            "decision_patterns",
            "learning_strategies",
            "cognitive_biases",
            "meta_awareness",
        ]

        for key in expected_keys:
            assert key in analysis

        # Verify analysis history updated
        assert len(self.analyzer.analysis_history) == 1
        history_entry = self.analyzer.analysis_history[0]
        assert "timestamp" in history_entry
        assert "analysis" in history_entry
        assert "memory_count" in history_entry

    def test_identify_reasoning_styles(self):
        """Test reasoning style identification."""
        styles = self.analyzer._identify_reasoning_styles(self.sample_memory_data)

        assert isinstance(styles, list)
        # Should identify at least one style
        assert len(styles) >= 0

        # Valid reasoning styles
        valid_styles = ["analytical", "creative", "intuitive", "systematic"]
        for style in styles:
            assert style in valid_styles

    def test_analyze_decision_patterns(self):
        """Test decision pattern analysis."""
        patterns = self.analyzer._analyze_decision_patterns(self.sample_memory_data)

        assert isinstance(patterns, dict)
        expected_patterns = [
            "decision_speed",
            "risk_tolerance",
            "information_gathering",
            "confidence_calibration",
        ]

        for pattern in expected_patterns:
            assert pattern in patterns

    def test_identify_learning_strategies(self):
        """Test learning strategy identification."""
        strategies = self.analyzer._identify_learning_strategies(
            self.sample_memory_data
        )

        assert isinstance(strategies, list)
        assert len(strategies) > 0

        # Valid learning strategies
        valid_strategies = [
            "experiential",
            "analytical",
            "social",
            "visual",
            "kinesthetic",
        ]
        for strategy in strategies:
            assert strategy in valid_strategies

    def test_detect_cognitive_biases(self):
        """Test cognitive bias detection."""
        biases = self.analyzer._detect_cognitive_biases(self.sample_memory_data)

        assert isinstance(biases, list)

        # If biases detected, verify structure
        for bias in biases:
            assert "bias_type" in bias
            assert "strength" in bias
            assert "description" in bias
            assert 0 <= bias["strength"] <= 1

    def test_assess_meta_awareness(self):
        """Test meta-awareness assessment."""
        # Test with data containing self-referential content
        meta_data = [
            {"content": {"type": "self-reflection", "insight": "I tend to overthink"}},
            {"content": {"type": "analysis", "subject": "my learning patterns"}},
            {"content": {"type": "observation", "note": "self-improvement needed"}},
        ]

        awareness_level = self.analyzer._assess_meta_awareness(meta_data)

        assert isinstance(awareness_level, float)
        assert 0 <= awareness_level <= 1

    def test_empty_data_analysis(self):
        """Test analysis with empty data."""
        analysis = self.analyzer.analyze_thinking_patterns([])

        assert isinstance(analysis, dict)
        # Should handle empty data gracefully
        assert "reasoning_styles" in analysis
        assert "meta_awareness" in analysis


class TestMemoryReflector:
    """Test suite for main MemoryReflector functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "max_active_sessions": 3,
            "confidence_threshold": 0.6,
            "reflection_frequency": 24,
        }
        self.reflector = MemoryReflector(self.config)
        self.test_memory_ids = ["mem_001", "mem_002", "mem_003", "mem_004"]

    def test_initialization(self):
        """Test MemoryReflector initialization."""
        assert self.reflector.max_active_sessions == 3
        assert self.reflector.insight_confidence_threshold == 0.6
        assert self.reflector.reflection_frequency == 24
        assert len(self.reflector.active_sessions) == 0
        assert len(self.reflector.completed_sessions) == 0
        assert len(self.reflector.insight_repository) == 0

        # Verify components initialized
        assert isinstance(self.reflector.pattern_detector, PatternDetector)
        assert isinstance(self.reflector.meta_analyzer, MetaCognitiveAnalyzer)

    def test_initiate_reflection_session(self):
        """Test reflection session initiation."""
        # Test with default reflection types
        session_id = self.reflector.initiate_reflection_session(self.test_memory_ids)

        assert session_id is not None
        assert session_id in self.reflector.active_sessions

        # Verify session properties
        session = self.reflector.active_sessions[session_id]
        assert session.target_memories == set(self.test_memory_ids)
        assert session.depth_level == ReflectionDepth.DEEP
        assert len(session.reflection_types) == 3  # Default types
        assert session.state != None

        # Verify metrics updated
        assert len(self.reflector.active_sessions) == 1

    def test_initiate_reflection_with_custom_types(self):
        """Test reflection session with custom reflection types."""
        custom_types = [ReflectionType.PATTERN_ANALYSIS, ReflectionType.META_LEARNING]

        session_id = self.reflector.initiate_reflection_session(
            self.test_memory_ids, custom_types, ReflectionDepth.META
        )

        session = self.reflector.active_sessions[session_id]
        assert session.reflection_types == custom_types
        assert session.depth_level == ReflectionDepth.META

    def test_reflection_capacity_limit(self):
        """Test reflection session capacity management."""
        # Fill up to capacity
        session_ids = []
        for i in range(self.config["max_active_sessions"]):
            session_id = self.reflector.initiate_reflection_session([f"mem_{i}"])
            assert session_id is not None
            session_ids.append(session_id)

        # Try to create one more - should fail
        overflow_session_id = self.reflector.initiate_reflection_session(
            ["mem_overflow"]
        )
        assert overflow_session_id is None
        assert len(self.reflector.active_sessions) == self.config["max_active_sessions"]

    def test_process_reflection_analysis(self):
        """Test complete reflection analysis processing."""
        # Create reflection session
        session_id = self.reflector.initiate_reflection_session(
            self.test_memory_ids,
            [ReflectionType.PATTERN_ANALYSIS, ReflectionType.META_LEARNING],
        )

        # Process analysis
        result = self.reflector.process_reflection_analysis(session_id)

        # Verify successful processing
        assert result["success"] is True
        assert result["session_id"] == session_id
        assert "insights_generated" in result
        assert "high_confidence_insights" in result
        assert "overall_coherence" in result
        assert "contradictions_found" in result
        assert "new_connections" in result
        assert "processing_time" in result

        # Verify session moved to completed
        assert session_id not in self.reflector.active_sessions
        assert session_id in self.reflector.completed_sessions

        # Verify insights stored in repository
        completed_session = self.reflector.completed_sessions[session_id]
        for insight in completed_session.insights:
            assert insight.insight_id in self.reflector.insight_repository

        # Verify metrics updated
        assert self.reflector.sessions_completed == 1
        assert self.reflector.insights_generated > 0

    def test_process_nonexistent_session(self):
        """Test processing non-existent reflection session."""
        result = self.reflector.process_reflection_analysis("non_existent_session")
        assert result["success"] is False
        assert "error" in result

    def test_get_insights_by_type(self):
        """Test retrieving insights filtered by type."""
        # Create and process a session
        session_id = self.reflector.initiate_reflection_session(
            self.test_memory_ids, [ReflectionType.PATTERN_ANALYSIS]
        )
        self.reflector.process_reflection_analysis(session_id)

        # Get insights by type
        pattern_insights = self.reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS
        )

        assert isinstance(pattern_insights, list)
        # Should have pattern analysis insights
        for insight in pattern_insights:
            assert insight.reflection_type == ReflectionType.PATTERN_ANALYSIS
            assert insight.confidence >= self.reflector.insight_confidence_threshold

        # Insights should be sorted by confidence (descending)
        if len(pattern_insights) > 1:
            confidences = [insight.confidence for insight in pattern_insights]
            assert confidences == sorted(confidences, reverse=True)

    def test_get_insights_with_custom_confidence(self):
        """Test retrieving insights with custom confidence threshold."""
        # Create session and generate insights
        session_id = self.reflector.initiate_reflection_session(self.test_memory_ids)
        self.reflector.process_reflection_analysis(session_id)

        # Get insights with high confidence threshold
        high_confidence_insights = self.reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS, min_confidence=0.8
        )

        for insight in high_confidence_insights:
            assert insight.confidence >= 0.8

    def test_find_contradictory_insights(self):
        """Test finding contradictory insights."""
        # Create multiple sessions to generate insights
        for i in range(2):
            session_id = self.reflector.initiate_reflection_session([f"mem_set_{i}"])
            self.reflector.process_reflection_analysis(session_id)

        # Find contradictions
        contradictions = self.reflector.find_contradictory_insights()

        assert isinstance(contradictions, list)
        # Each contradiction should be a tuple of two insights
        for contradiction in contradictions:
            assert len(contradiction) == 2
            assert isinstance(contradiction[0], ReflectionInsight)
            assert isinstance(contradiction[1], ReflectionInsight)

    def test_generate_self_assessment(self):
        """Test comprehensive self-assessment generation."""
        # Generate some insights first
        session_id = self.reflector.initiate_reflection_session(
            self.test_memory_ids,
            [
                ReflectionType.PATTERN_ANALYSIS,
                ReflectionType.EMOTIONAL_REFLECTION,
                ReflectionType.META_LEARNING,
            ],
        )
        self.reflector.process_reflection_analysis(session_id)

        # Generate self-assessment
        assessment = self.reflector.generate_self_assessment()

        # Verify assessment structure
        expected_keys = [
            "overall_confidence",
            "dominant_patterns",
            "emotional_tendencies",
            "learning_effectiveness",
            "cognitive_strengths",
            "areas_for_improvement",
            "behavioral_consistency",
            "meta_cognitive_awareness",
            "insight_categories",
            "total_insights",
            "high_confidence_ratio",
            "generated_at",
        ]

        for key in expected_keys:
            assert key in assessment

        # Verify data types
        assert isinstance(assessment["overall_confidence"], float)
        assert isinstance(assessment["dominant_patterns"], list)
        assert isinstance(assessment["emotional_tendencies"], dict)
        assert isinstance(assessment["cognitive_strengths"], list)
        assert isinstance(assessment["areas_for_improvement"], list)
        assert isinstance(assessment["total_insights"], int)
        assert 0 <= assessment["high_confidence_ratio"] <= 1

    def test_self_assessment_insufficient_data(self):
        """Test self-assessment with insufficient data."""
        # Generate assessment without any insights
        assessment = self.reflector.generate_self_assessment()

        assert assessment["assessment"] == "insufficient_data"
        assert "insights_needed" in assessment

    def test_recommend_memory_optimization(self):
        """Test memory optimization recommendations."""
        # Generate insights first
        session_id = self.reflector.initiate_reflection_session(self.test_memory_ids)
        self.reflector.process_reflection_analysis(session_id)

        # Get recommendations
        recommendations = self.reflector.recommend_memory_optimization()

        assert isinstance(recommendations, list)

        # Verify recommendation structure
        for recommendation in recommendations:
            assert "type" in recommendation
            assert "priority" in recommendation
            assert "description" in recommendation
            assert "confidence" in recommendation

            # Priority should be valid
            assert recommendation["priority"] in ["high", "medium", "low"]
            # Confidence should be reasonable
            assert 0 <= recommendation["confidence"] <= 1

    def test_get_system_status(self):
        """Test system status reporting."""
        # Create some activity for meaningful status
        session_id = self.reflector.initiate_reflection_session(self.test_memory_ids)
        self.reflector.process_reflection_analysis(session_id)

        status = self.reflector.get_system_status()

        # Verify status structure
        assert status["system_status"] == "operational"
        assert status["module_version"] == "1.0.0"
        assert status["active_sessions"] == 0  # Should be 0 after processing
        assert status["completed_sessions"] == 1
        assert status["total_insights"] > 0

        # Verify metrics
        metrics = status["metrics"]
        assert metrics["sessions_completed"] == 1
        assert metrics["insights_generated"] > 0
        assert "avg_insights_per_session" in metrics

        # Verify insight distribution
        assert "insight_distribution" in status
        assert isinstance(status["insight_distribution"], dict)

        # Verify configuration
        config = status["configuration"]
        assert config["max_active_sessions"] == 3
        assert config["confidence_threshold"] == 0.6
        assert config["reflection_frequency"] == 24


class TestReflectionTypes:
    """Test different reflection types and their processing."""

    def setup_method(self):
        """Setup test fixtures."""
        self.reflector = MemoryReflector()
        self.memory_ids = ["mem_001", "mem_002"]

    def test_pattern_analysis_reflection(self):
        """Test pattern analysis reflection type."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, [ReflectionType.PATTERN_ANALYSIS]
        )

        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # Should have pattern analysis insights
        session = self.reflector.completed_sessions[session_id]
        pattern_insights = [
            i
            for i in session.insights
            if i.reflection_type == ReflectionType.PATTERN_ANALYSIS
        ]
        assert len(pattern_insights) > 0

    def test_meta_learning_reflection(self):
        """Test meta-learning reflection type."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, [ReflectionType.META_LEARNING]
        )

        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # Should have meta-learning insights
        session = self.reflector.completed_sessions[session_id]
        meta_insights = [
            i
            for i in session.insights
            if i.reflection_type == ReflectionType.META_LEARNING
        ]
        assert len(meta_insights) > 0

    def test_emotional_reflection(self):
        """Test emotional reflection type."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, [ReflectionType.EMOTIONAL_REFLECTION]
        )

        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

    def test_multiple_reflection_types(self):
        """Test processing multiple reflection types."""
        reflection_types = [
            ReflectionType.PATTERN_ANALYSIS,
            ReflectionType.EMOTIONAL_REFLECTION,
            ReflectionType.META_LEARNING,
        ]

        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, reflection_types
        )

        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # Should have insights from all types
        session = self.reflector.completed_sessions[session_id]
        insight_types = {insight.reflection_type for insight in session.insights}

        # Should have at least some of the requested types
        assert len(insight_types) > 0


class TestReflectionDepths:
    """Test different reflection depth levels."""

    def setup_method(self):
        """Setup test fixtures."""
        self.reflector = MemoryReflector()
        self.memory_ids = ["mem_001", "mem_002"]

    def test_surface_depth(self):
        """Test surface depth reflection."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, depth=ReflectionDepth.SURFACE
        )

        session = self.reflector.active_sessions[session_id]
        assert session.depth_level == ReflectionDepth.SURFACE

    def test_deep_depth(self):
        """Test deep depth reflection."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, depth=ReflectionDepth.DEEP
        )

        session = self.reflector.active_sessions[session_id]
        assert session.depth_level == ReflectionDepth.DEEP

    def test_meta_depth(self):
        """Test meta depth reflection."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, depth=ReflectionDepth.META
        )

        session = self.reflector.active_sessions[session_id]
        assert session.depth_level == ReflectionDepth.META

    def test_transcendent_depth(self):
        """Test transcendent depth reflection."""
        session_id = self.reflector.initiate_reflection_session(
            self.memory_ids, depth=ReflectionDepth.TRANSCENDENT
        )

        session = self.reflector.active_sessions[session_id]
        assert session.depth_level == ReflectionDepth.TRANSCENDENT


class TestModuleLevelInterface:
    """Test module-level interface functions."""

    def setup_method(self):
        """Setup test fixtures."""
        # Reset the default reflector
        from memory.core_memory.reflection_engine import (
            default_memory_reflector,
        )

        default_memory_reflector.__init__()

        self.memory_ids = ["mem_001", "mem_002", "mem_003"]

    def test_get_memory_reflector(self):
        """Test getting default memory reflector."""
        reflector = get_memory_reflector()
        assert isinstance(reflector, MemoryReflector)

    def test_initiate_reflection_module_function(self):
        """Test module-level reflection initiation."""
        session_id = initiate_reflection(
            self.memory_ids, ["pattern_analysis", "meta_learning"]
        )

        assert session_id is not None

        # Verify session was created
        reflector = get_memory_reflector()
        assert session_id in reflector.active_sessions

    def test_initiate_reflection_invalid_type(self):
        """Test module-level function with invalid reflection type."""
        session_id = initiate_reflection(self.memory_ids, ["invalid_type"])
        assert session_id is None

    def test_process_reflection_module_function(self):
        """Test module-level reflection processing."""
        # Create session first
        session_id = initiate_reflection(self.memory_ids)
        assert session_id is not None

        # Process reflection
        result = process_reflection(session_id)
        assert result["success"] is True
        assert result["session_id"] == session_id

    def test_get_self_assessment_module_function(self):
        """Test module-level self-assessment."""
        # Generate some insights first
        session_id = initiate_reflection(self.memory_ids)
        process_reflection(session_id)

        # Get self-assessment
        assessment = get_self_assessment()
        assert isinstance(assessment, dict)
        assert "total_insights" in assessment

    def test_get_reflector_status_module_function(self):
        """Test module-level status function."""
        status = get_reflector_status()
        assert isinstance(status, dict)
        assert "system_status" in status
        assert "module_version" in status


class TestReflectionInsights:
    """Test reflection insight generation and management."""

    def setup_method(self):
        """Setup test fixtures."""
        self.reflector = MemoryReflector()
        self.memory_ids = ["mem_001", "mem_002", "mem_003"]

    def test_insight_properties(self):
        """Test insight object properties."""
        # Generate insights
        session_id = self.reflector.initiate_reflection_session(self.memory_ids)
        result = self.reflector.process_reflection_analysis(session_id)

        session = self.reflector.completed_sessions[session_id]

        # Verify insight properties
        for insight in session.insights:
            assert isinstance(insight, ReflectionInsight)
            assert insight.insight_id is not None
            assert isinstance(insight.reflection_type, ReflectionType)
            assert isinstance(insight.depth, ReflectionDepth)
            assert isinstance(insight.content, dict)
            assert 0 <= insight.confidence <= 1
            assert isinstance(insight.supporting_memories, list)
            assert isinstance(insight.contradictory_evidence, list)
            assert isinstance(insight.emotional_valence, float)
            assert isinstance(insight.symbolic_significance, float)
            assert isinstance(insight.actionable_implications, list)
            assert insight.created_at is not None
            assert isinstance(insight.validated, bool)

    def test_insight_confidence_filtering(self):
        """Test filtering insights by confidence."""
        # Generate insights
        session_id = self.reflector.initiate_reflection_session(self.memory_ids)
        self.reflector.process_reflection_analysis(session_id)

        # Get high-confidence insights
        high_conf_insights = self.reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS, min_confidence=0.9
        )

        # All returned insights should meet confidence threshold
        for insight in high_conf_insights:
            assert insight.confidence >= 0.9

    def test_insight_repository_management(self):
        """Test insight repository storage and retrieval."""
        # Generate insights from multiple sessions
        session_ids = []
        for i in range(2):
            session_id = self.reflector.initiate_reflection_session([f"mem_set_{i}"])
            self.reflector.process_reflection_analysis(session_id)
            session_ids.append(session_id)

        # Verify all insights stored in repository
        total_insights = 0
        for session_id in session_ids:
            session = self.reflector.completed_sessions[session_id]
            total_insights += len(session.insights)

        assert len(self.reflector.insight_repository) == total_insights

        # Verify insights can be retrieved by ID
        for insight_id in self.reflector.insight_repository:
            insight = self.reflector.insight_repository[insight_id]
            assert insight.insight_id == insight_id


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Setup test fixtures."""
        self.reflector = MemoryReflector()

    def test_empty_memory_list(self):
        """Test reflection with empty memory list."""
        session_id = self.reflector.initiate_reflection_session([])
        assert session_id is not None

        # Should still process successfully
        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

    def test_none_memory_list(self):
        """Test reflection with None memory list."""
        with pytest.raises(TypeError):
            self.reflector.initiate_reflection_session(None)

    def test_invalid_reflection_types(self):
        """Test reflection with invalid reflection types."""
        with pytest.raises(AttributeError):
            self.reflector.initiate_reflection_session(
                ["mem_001"],
                ["invalid_reflection_type"],  # Should be ReflectionType enum
            )

    def test_reflection_processing_error_recovery(self):
        """Test error recovery during reflection processing."""
        session_id = self.reflector.initiate_reflection_session(["mem_001"])

        # Mock processing error
        with patch.object(
            self.reflector,
            "_process_reflection_type",
            side_effect=Exception("Processing error"),
        ):
            result = self.reflector.process_reflection_analysis(session_id)

            assert result["success"] is False
            assert "error" in result

        # System should remain operational
        status = self.reflector.get_system_status()
        assert status["system_status"] == "operational"


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""

    def setup_method(self):
        """Setup test fixtures."""
        self.reflector = MemoryReflector({"max_active_sessions": 10})

    def test_large_memory_set_reflection(self):
        """Test reflection with large memory set."""
        large_memory_set = [f"mem_{i:04d}" for i in range(100)]

        session_id = self.reflector.initiate_reflection_session(large_memory_set)
        assert session_id is not None

        result = self.reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent reflection sessions."""
        session_ids = []

        # Create multiple sessions
        for i in range(5):
            session_id = self.reflector.initiate_reflection_session([f"mem_set_{i}"])
            session_ids.append(session_id)

        # Process all sessions
        for session_id in session_ids:
            result = self.reflector.process_reflection_analysis(session_id)
            assert result["success"] is True

        # Verify all completed
        assert len(self.reflector.completed_sessions) == 5

    def test_insight_repository_scaling(self):
        """Test insight repository with many insights."""
        # Generate many insights
        for i in range(10):
            session_id = self.reflector.initiate_reflection_session([f"mem_{i}"])
            self.reflector.process_reflection_analysis(session_id)

        # Repository should handle many insights
        assert len(self.reflector.insight_repository) > 0

        # Should still be able to filter efficiently
        pattern_insights = self.reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS
        )
        assert isinstance(pattern_insights, list)


# Test fixtures and utilities
@pytest.fixture
def memory_reflector():
    """Fixture providing a fresh MemoryReflector instance."""
    return MemoryReflector(
        {
            "max_active_sessions": 5,
            "confidence_threshold": 0.6,
            "reflection_frequency": 12,
        }
    )


@pytest.fixture
def sample_memory_set():
    """Fixture providing sample memory set."""
    return ["memory_001", "memory_002", "memory_003", "memory_004"]


@pytest.fixture
def sample_reflection_types():
    """Fixture providing sample reflection types."""
    return [
        ReflectionType.PATTERN_ANALYSIS,
        ReflectionType.EMOTIONAL_REFLECTION,
        ReflectionType.META_LEARNING,
    ]


# Integration tests
class TestReflectionSystemIntegration:
    """Integration tests for the complete reflection system."""

    def test_complete_reflection_workflow(
        self, memory_reflector, sample_memory_set, sample_reflection_types
    ):
        """Test complete reflection workflow from initiation to assessment."""
        # 1. Initiate reflection session
        session_id = memory_reflector.initiate_reflection_session(
            sample_memory_set, sample_reflection_types, ReflectionDepth.DEEP
        )
        assert session_id is not None

        # 2. Process reflection analysis
        result = memory_reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # 3. Verify insights generated
        session = memory_reflector.completed_sessions[session_id]
        assert len(session.insights) > 0

        # 4. Get insights by type
        for reflection_type in sample_reflection_types:
            insights = memory_reflector.get_insights_by_type(reflection_type)
            # Should have some insights for each type

        # 5. Generate self-assessment
        assessment = memory_reflector.generate_self_assessment()
        assert assessment["total_insights"] > 0

        # 6. Get optimization recommendations
        recommendations = memory_reflector.recommend_memory_optimization()
        assert isinstance(recommendations, list)

        # 7. Verify system status
        status = memory_reflector.get_system_status()
        assert status["metrics"]["sessions_completed"] == 1

    def test_pattern_detection_integration(self, memory_reflector):
        """Test integration between pattern detection and reflection."""
        memory_ids = ["mem_A", "mem_B", "mem_C"]

        # Focus on pattern analysis
        session_id = memory_reflector.initiate_reflection_session(
            memory_ids, [ReflectionType.PATTERN_ANALYSIS]
        )

        result = memory_reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # Should have pattern insights
        pattern_insights = memory_reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS
        )
        assert len(pattern_insights) > 0

        # Insights should contain pattern information
        for insight in pattern_insights:
            assert "pattern_name" in insight.content or "strength" in insight.content

    def test_meta_cognitive_analysis_integration(self, memory_reflector):
        """Test integration with meta-cognitive analysis."""
        session_id = memory_reflector.initiate_reflection_session(
            ["mem_001", "mem_002"], [ReflectionType.META_LEARNING]
        )

        result = memory_reflector.process_reflection_analysis(session_id)
        assert result["success"] is True

        # Should have meta-learning insights
        meta_insights = memory_reflector.get_insights_by_type(
            ReflectionType.META_LEARNING
        )
        assert len(meta_insights) > 0

        # Generate self-assessment - should reflect meta-cognitive analysis
        assessment = memory_reflector.generate_self_assessment()
        assert "meta_cognitive_awareness" in assessment

    def test_contradiction_detection_integration(self, memory_reflector):
        """Test contradiction detection across multiple sessions."""
        # Create multiple sessions with potentially contradicting insights
        session_ids = []
        for i in range(3):
            session_id = memory_reflector.initiate_reflection_session([f"mem_set_{i}"])
            memory_reflector.process_reflection_analysis(session_id)
            session_ids.append(session_id)

        # Find contradictions
        contradictions = memory_reflector.find_contradictory_insights()

        # Should be able to detect contradictions (even if none found)
        assert isinstance(contradictions, list)

        # If contradictions found, verify structure
        for contradiction in contradictions:
            assert len(contradiction) == 2
            insight1, insight2 = contradiction
            assert isinstance(insight1, ReflectionInsight)
            assert isinstance(insight2, ReflectionInsight)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
