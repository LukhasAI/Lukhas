"""
Tests for the LUKHAS Tag Registry System
"""

from core.tags import (
    TagCategory,
    TagDefinition,
    explain_tag,
    get_decision_tags,
    get_hormone_tags,
    get_tag_registry,
)


class TestTagRegistry:
    """Test the tag registry functionality"""

    def test_registry_initialization(self):
        """Test that registry initializes with core tags"""
        registry = get_tag_registry()

        # Check core tags exist
        assert registry.get_tag("#TAG:core") is not None
        assert registry.get_tag("#TAG:neuroplastic") is not None
        assert registry.get_tag("#TAG:consciousness") is not None

        # Check tag count
        assert len(registry.tags) >= 20

    def test_tag_categories(self):
        """Test tag categorization"""
        registry = get_tag_registry()

        # Get emotion tags
        emotion_tags = registry.get_tags_by_category(TagCategory.EMOTION)
        tag_names = [tag.name for tag in emotion_tags]

        assert "#TAG:emotion" in tag_names
        assert "#TAG:vad" in tag_names
        assert "#TAG:mood" in tag_names

    def test_tag_relationships(self):
        """Test parent-child and related tag relationships"""
        registry = get_tag_registry()

        # Test hormone parent-child
        hormone_tag = registry.get_tag("#TAG:hormone")
        assert "#TAG:cortisol" in hormone_tag.child_tags
        assert "#TAG:dopamine" in hormone_tag.child_tags

        # Test child knows parent
        cortisol_tag = registry.get_tag("#TAG:cortisol")
        assert "#TAG:hormone" in cortisol_tag.parent_tags

        # Test related tags
        emotion_tag = registry.get_tag("#TAG:emotion")
        assert "#TAG:vad" in emotion_tag.related_tags

    def test_get_related_tags(self):
        """Test getting related tags with depth"""
        registry = get_tag_registry()

        # Get tags related to emotion
        related = registry.get_related_tags("#TAG:emotion", depth=1)
        assert "#TAG:vad" in related
        assert "#TAG:mood" in related

        # Get tags related to mood (which should include hormone)
        mood_related = registry.get_related_tags("#TAG:mood", depth=1)
        assert "#TAG:hormone" in mood_related

    def test_explain_tag(self):
        """Test human-readable tag explanations"""
        # Test basic explanation
        explanation = explain_tag("#TAG:neuroplastic")
        assert "neuroplastic" in explanation.lower()
        assert "adapts and changes" in explanation

        # Test with context
        context = {"situation": "high stress", "load": "overload"}
        explanation = explain_tag("#TAG:neuroplastic", context)
        assert "Activated because:" in explanation
        assert "High stress" in explanation

    def test_get_hormone_tags(self):
        """Test getting all hormone tags"""
        hormone_tags = get_hormone_tags()

        assert "#TAG:hormone" in hormone_tags
        assert "#TAG:cortisol" in hormone_tags
        assert "#TAG:dopamine" in hormone_tags
        assert "#TAG:serotonin" in hormone_tags
        assert "#TAG:oxytocin" in hormone_tags
        assert len(hormone_tags) == 5

    def test_get_decision_tags(self):
        """Test getting decision-relevant tags"""
        # Test ethical decision
        tags = get_decision_tags("ethical risk assessment")
        assert "#TAG:decision" in tags
        assert "#TAG:ethics" in tags  # Has "risk detection" trigger

    def test_tag_priority(self):
        """Test tag priority system"""
        registry = get_tag_registry()

        # Core and governance should have high priority
        core_tag = registry.get_tag("#TAG:core")
        assert core_tag.priority == 1

        governance_tag = registry.get_tag("#TAG:governance")
        assert governance_tag.priority == 1

        # Sub-tags should have lower priority
        vad_tag = registry.get_tag("#TAG:vad")
        assert vad_tag.priority >= 4

    def test_tag_confidence_requirements(self):
        """Test confidence requirements for tags"""
        registry = get_tag_registry()

        # Ethics should require high confidence
        ethics_tag = registry.get_tag("#TAG:ethics")
        assert ethics_tag.confidence_required == 0.9

        # Most tags should have default confidence
        emotion_tag = registry.get_tag("#TAG:emotion")
        assert emotion_tag.confidence_required == 0.7

    def test_tag_effects_and_triggers(self):
        """Test tag triggers and effects"""
        registry = get_tag_registry()

        # Test cortisol triggers and effects
        cortisol = registry.get_tag("#TAG:cortisol")
        assert "System overload" in cortisol.triggers
        assert "Heightened alertness" in cortisol.effects

        # Test dream triggers
        dream = registry.get_tag("#TAG:dream")
        assert "Rest cycles" in dream.triggers
        assert "Memory consolidation" in dream.effects

    def test_custom_tag_registration(self):
        """Test registering custom tags"""
        registry = get_tag_registry()

        # Create custom tag
        custom_tag = TagDefinition(
            name="#TAG:test_custom",
            category=TagCategory.LEARNING,
            description="Test custom tag",
            human_meaning="A tag created for testing",
            triggers=["test event"],
            effects=["test effect"],
            priority=5,
        )

        # Register it
        registry.register_tag(custom_tag)

        # Verify it exists
        retrieved = registry.get_tag("#TAG:test_custom")
        assert retrieved is not None
        assert retrieved.human_meaning == "A tag created for testing"

        # Check it's in category index
        learning_tags = registry.get_tags_by_category(TagCategory.LEARNING)
        tag_names = [tag.name for tag in learning_tags]
        assert "#TAG:test_custom" in tag_names

    def test_tag_report_generation(self):
        """Test comprehensive tag report"""
        registry = get_tag_registry()
        report = registry.generate_tag_report()

        assert "total_tags" in report
        assert report["total_tags"] > 20

        assert "categories" in report
        assert TagCategory.CORE.value in report["categories"]

        assert "high_priority_tags" in report
        assert len(report["high_priority_tags"]) > 0

        # Check high priority tags are actually high priority
        for tag_info in report["high_priority_tags"]:
            assert tag_info["priority"] <= 3

    def test_explain_unknown_tag(self):
        """Test explaining unknown tag"""
        explanation = explain_tag("#TAG:does_not_exist")
        assert "Unknown tag" in explanation
