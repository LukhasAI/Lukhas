"""
LUKHAS Tag Registry System
Comprehensive registry of all tags with meanings, relationships, and human interpretability
"""

import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Optional


class TagCategory(Enum):
    """Categories of tags for semantic grouping"""

    CORE = "core"  # Core system functionality
    NEUROPLASTIC = "neuroplastic"  # Adaptive/reorganizing components
    COLONY = "colony"  # Self-propagating modules
    EMOTION = "emotion"  # Emotional processing
    CONSCIOUSNESS = "consciousness"  # Awareness and reflection
    MEMORY = "memory"  # Memory systems
    DREAM = "dream"  # Dream processing
    QUANTUM = "quantum"  # Quantum-inspired operations
    GOVERNANCE = "governance"  # Ethics and control
    BRIDGE = "bridge"  # Integration components
    DECISION = "decision"  # Decision-making
    LEARNING = "learning"  # Learning and adaptation
    HORMONE = "hormone"  # Endocrine signals
    SYMBOLIC = "symbolic"  # Symbolic processing
    BIO = "bio"  # Biological simulation


@dataclass
class TagDefinition:
    """Complete definition of a tag"""

    name: str
    category: TagCategory
    description: str
    human_meaning: str
    related_tags: set[str] = field(default_factory=set)
    parent_tags: set[str] = field(default_factory=set)
    child_tags: set[str] = field(default_factory=set)
    triggers: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    confidence_required: float = 0.7
    priority: int = 5  # 1=highest, 10=lowest

    def to_human_readable(self) -> str:
        """Generate human-readable explanation of the tag"""
        explanation = f"TAG: {self.name}\n"
        explanation += f"Category: {self.category.value}\n"
        explanation += f"Meaning: {self.human_meaning}\n"

        if self.triggers:
            explanation += f"Activated by: {', '.join(self.triggers)}\n"

        if self.effects:
            explanation += f"Causes: {', '.join(self.effects)}\n"

        if self.related_tags:
            explanation += f"Related to: {', '.join(self.related_tags)}\n"

        return explanation


class TagRegistry:
    """Central registry for all LUKHAS tags"""

    def __init__(self):
        self.tags: dict[str, TagDefinition] = {}
        self.category_index: dict[TagCategory, set[str]] = {
            cat: set() for cat in TagCategory
        }
        self.relationship_graph: dict[str, set[str]] = {}
        self._initialize_core_tags()

    def _initialize_core_tags(self):
        """Initialize the core tag definitions"""

        # Core system tags
        self.register_tag(
            TagDefinition(
                name="#TAG:core",
                category=TagCategory.CORE,
                description="Core system component",
                human_meaning="This is a fundamental part of LUKHAS that other systems depend on",
                effects=[
                    "Provides essential functionality",
                    "Cannot be disabled",
                ],
                priority=1,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:neuroplastic",
                category=TagCategory.NEUROPLASTIC,
                description="Component that can reorganize under stress",
                human_meaning="This module adapts and changes its structure based on system needs, like a brain rewiring itself",
                triggers=[
                    "High stress",
                    "System overload",
                    "Learning opportunity",
                ],
                effects=[
                    "Module reorganization",
                    "New connection formation",
                    "Behavioral adaptation",
                ],
                related_tags={
                    "#TAG:hormone",
                    "#TAG:learning"},
                priority=2,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:colony",
                category=TagCategory.COLONY,
                description="Self-propagating module with base_colony.py",
                human_meaning="This module can create copies of itself and spread functionality across the system",
                effects=[
                    "Self-replication",
                    "Distributed processing",
                    "Fault tolerance",
                ],
                related_tags={"#TAG:neuroplastic"},
                priority=3,
            ))

        # Emotion tags
        self.register_tag(
            TagDefinition(
                name="#TAG:emotion",
                category=TagCategory.EMOTION,
                description="Emotional processing component",
                human_meaning="Handles feelings and emotional responses using VAD (Valence-Arousal-Dominance) model",
                related_tags={
                    "#TAG:vad",
                    "#TAG:mood",
                    "#TAG:empathy"},
                effects=[
                    "Emotional state changes",
                    "Mood regulation",
                    "Empathy responses",
                ],
                priority=4,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:vad",
                category=TagCategory.EMOTION,
                description="Valence-Arousal-Dominance emotional model",
                human_meaning="Measures emotions on three scales: pleasantness,"
                intensity, and control",
                parent_tags={"#TAG:emotion"},
                effects=[
                    "Precise emotion measurement",
                    "Emotional state tracking",
                ],
                priority=5,
            )
        )

        self.register_tag(
            TagDefinition(
                name="#TAG:mood",
                category=TagCategory.EMOTION,
                description="Mood regulation system",
                human_meaning="Manages longer-term emotional states and stability",
                parent_tags={"#TAG:emotion"},
                related_tags={"#TAG:hormone"},
                triggers=["Sustained emotions", "Environmental changes"],
                effects=["Behavioral tendencies", "Decision biases"],
                priority=5,
            )
        )

        # Consciousness tags
        self.register_tag(
            TagDefinition(
                name="#TAG:consciousness",
                category=TagCategory.CONSCIOUSNESS,
                description="Consciousness and awareness systems",
                human_meaning="Components that create self-awareness and reflection capabilities",
                related_tags={
                    "#TAG:reflection",
                    "#TAG:awareness"},
                effects=[
                    "Self-monitoring",
                    "Meta-cognition",
                    "Introspection"],
                priority=2,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:reflection",
                category=TagCategory.CONSCIOUSNESS,
                description="Self-reflection and introspection",
                human_meaning="The ability to think about one's own thoughts and analyze internal states",
                parent_tags={"#TAG:consciousness"},
                triggers=[
                    "Decision completion",
                    "Error detection",
                    "Learning events",
                ],
                effects=[
                    "Self-improvement",
                    "Pattern recognition",
                    "Behavioral adjustment",
                ],
                priority=3,
            ))

        # Memory tags
        self.register_tag(
            TagDefinition(
                name="#TAG:memory",
                category=TagCategory.MEMORY,
                description="Memory storage and retrieval systems",
                human_meaning="Systems that store experiences and knowledge for future use",
                related_tags={
                    "#TAG:fold",
                    "#TAG:consolidation"},
                effects=[
                    "Experience retention",
                    "Knowledge accumulation",
                    "Pattern learning",
                ],
                priority=2,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:fold",
                category=TagCategory.MEMORY,
                description="Memory fold structure",
                human_meaning="A compressed memory unit that stores experiences with emotional context",
                parent_tags={"#TAG:memory"},
                effects=[
                    "Memory compression",
                    "Emotional association",
                    "Causal linking",
                ],
                priority=4,
            ))

        # Dream tags
        self.register_tag(
            TagDefinition(
                name="#TAG:dream",
                category=TagCategory.DREAM,
                description="Dream processing and simulation",
                human_meaning="Creates alternative scenarios and processes experiences during rest states",
                related_tags={
                    "#TAG:memory",
                    "#TAG:quantum",
                    "#TAG:learning"},
                triggers=[
                    "Rest cycles",
                    "High memory load",
                    "Unresolved conflicts",
                ],
                effects=[
                    "Memory consolidation",
                    "Creative insights",
                    "Problem solving",
                ],
                priority=3,
            ))

        # Governance tags
        self.register_tag(
            TagDefinition(
                name="#TAG:governance",
                category=TagCategory.GOVERNANCE,
                description="Ethics and control systems",
                human_meaning="Ensures decisions and actions align with ethical principles and safety",
                related_tags={
                    "#TAG:ethics",
                    "#TAG:guardian",
                    "#TAG:policy"},
                effects=[
                    "Action filtering",
                    "Risk assessment",
                    "Ethical validation",
                ],
                priority=1,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:ethics",
                category=TagCategory.GOVERNANCE,
                description="Ethical evaluation and enforcement",
                human_meaning="Evaluates actions against moral principles and prevents harmful behavior",
                parent_tags={"#TAG:governance"},
                triggers=[
                    "Action requests",
                    "Decision points",
                    "Risk detection",
                ],
                effects=[
                    "Action approval/denial",
                    "Risk mitigation",
                    "Value alignment",
                ],
                confidence_required=0.9,
                priority=1,
            ))

        # Hormone tags
        self.register_tag(
            TagDefinition(
                name="#TAG:hormone",
                category=TagCategory.HORMONE,
                description="Endocrine-like signaling system",
                human_meaning="Chemical-like signals that influence behavior and mood across the system",
                related_tags={
                    "#TAG:neuroplastic",
                    "#TAG:mood",
                    "#TAG:emotion",
                },
                child_tags={
                    "#TAG:cortisol",
                    "#TAG:dopamine",
                    "#TAG:serotonin",
                    "#TAG:oxytocin",
                },
                effects=[
                    "System-wide modulation",
                    "Behavioral tendencies",
                    "Stress response",
                ],
                priority=3,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:cortisol",
                category=TagCategory.HORMONE,
                description="Stress hormone simulation",
                human_meaning="Increases during stress, triggers adaptation and emergency responses",
                parent_tags={"#TAG:hormone"},
                triggers=[
                    "System overload",
                    "Threat detection",
                    "Resource scarcity",
                ],
                effects=[
                    "Heightened alertness",
                    "Resource conservation",
                    "Module reorganization",
                ],
                priority=4,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:dopamine",
                category=TagCategory.HORMONE,
                description="Reward hormone simulation",
                human_meaning="Released during success and learning, reinforces positive behaviors",
                parent_tags={"#TAG:hormone"},
                triggers=[
                    "Goal achievement",
                    "Learning success",
                    "Positive feedback",
                ],
                effects=[
                    "Motivation increase",
                    "Pattern reinforcement",
                    "Exploration drive",
                ],
                priority=4,
            ))

        self.register_tag(
            TagDefinition(
                name="#TAG:serotonin",
                category=TagCategory.HORMONE,
                description="Stability hormone simulation",
                human_meaning="Promotes emotional balance and well - being,
                reduces anxiety",
                parent_tags={"#TAG:hormone"},
                triggers=[
                    "Social connection",
                    "Routine completion",
                    "Environmental safety",
                ],
                effects=[
                    "Mood stabilization",
                    "Anxiety reduction",
                    "Contentment",
                ],
                priority=4,
            )
        )

        self.register_tag(
            TagDefinition(
                name="#TAG:oxytocin",
                category=TagCategory.HORMONE,
                description="Bonding hormone simulation",
                human_meaning="Strengthens social connections and trust behaviors",
                parent_tags={"#TAG:hormone"},
                triggers=[
                    "Positive interactions",
                    "Trust building",
                    "Cooperation",
                ],
                effects=[
                    "Empathy enhancement",
                    "Trust increase",
                    "Social bonding",
                ],
                priority=4,
            )
        )

        # Decision tags
        self.register_tag(
            TagDefinition(
                name="#TAG:decision",
                category=TagCategory.DECISION,
                description="Decision-making components",
                human_meaning="Systems involved in evaluating options and making choices",
                related_tags={
                    "#TAG:consciousness",
                    "#TAG:ethics",
                    "#TAG:emotion",
                },
                triggers=[
                    "Multiple options",
                    "Action requests",
                    "Goal conflicts",
                ],
                effects=[
                    "Choice selection",
                    "Action initiation",
                    "Consequence evaluation",
                ],
                priority=2,
            ))

        # Learning tags
        self.register_tag(
            TagDefinition(
                name="#TAG:learning",
                category=TagCategory.LEARNING,
                description="Learning and adaptation systems",
                human_meaning="Components that improve performance through experience",
                related_tags={
                    "#TAG:memory",
                    "#TAG:neuroplastic",
                    "#TAG:dream",
                },
                triggers=["New experiences", "Errors", "Pattern detection"],
                effects=[
                    "Skill improvement",
                    "Knowledge update",
                    "Behavior modification",
                ],
                priority=3,
            )
        )

    def register_tag(self, tag_def: TagDefinition) -> None:
        """Register a new tag definition"""
        self.tags[tag_def.name] = tag_def
        self.category_index[tag_def.category].add(tag_def.name)

        # Update relationship graph
        self.relationship_graph[tag_def.name] = tag_def.related_tags.copy()

        # Update parent-child relationships
        for parent in tag_def.parent_tags:
            if parent in self.tags:
                self.tags[parent].child_tags.add(tag_def.name)

        for child in tag_def.child_tags:
            if child in self.tags:
                self.tags[child].parent_tags.add(tag_def.name)

    def get_tag(self, tag_name: str) -> Optional[TagDefinition]:
        """Get a tag definition by name"""
        return self.tags.get(tag_name)

    def get_tags_by_category(self, category: TagCategory) -> list[TagDefinition]:
        """Get all tags in a category"""
        tag_names = self.category_index.get(category, set())
        return [self.tags[name] for name in tag_names if name in self.tags]

    def get_related_tags(self, tag_name: str, depth: int = 1) -> set[str]:
        """Get related tags up to specified depth"""
        if tag_name not in self.tags:
            return set()

        related = set()
        to_explore = {tag_name}

        for _ in range(depth):
            next_explore = set()
            for tag in to_explore:
                if tag in self.tags:
                    tag_def = self.tags[tag]
                    next_explore.update(tag_def.related_tags)
                    next_explore.update(tag_def.parent_tags)
                    next_explore.update(tag_def.child_tags)

            related.update(next_explore)
            to_explore = next_explore - related

        related.discard(tag_name)  # Remove self
        return related

    def explain_tag_activation(self, tag_name: str, context: dict[str, Any]) -> str:
        """Explain why a tag would be activated in given context"""
        tag = self.get_tag(tag_name)
        if not tag:
            return f"Unknown tag: {tag_name}"

        explanation = f"Tag {tag_name} ({tag.human_meaning})\n\n"

        # Check triggers
        activated_triggers = []
        for trigger in tag.triggers:
            # Simple keyword matching for now
            if any(
                keyword in str(context).lower() for keyword in trigger.lower().split()
            ):
                activated_triggers.append(trigger)

        if activated_triggers:
            explanation += f"Activated because: {', '.join(activated_triggers)}\n"
        else:
            explanation += "No specific triggers detected in context.\n"

        # Explain effects
        if tag.effects:
            explanation += f"\nThis will cause: {', '.join(tag.effects)}\n"

        # Related tags that might also activate
        related = self.get_related_tags(tag_name, depth=1)
        if related:
            explanation += f"\nMay also activate: {', '.join(related)}\n"

        return explanation

    def get_decision_tags(self, decision_type: str) -> list[str]:
        """Get tags relevant to a specific decision type"""
        relevant_tags = []

        # Always include decision tag
        relevant_tags.append("#TAG:decision")

        # Add specific tags based on decision type
        decision_keywords = decision_type.lower().split()

        for tag_name, tag_def in self.tags.items():
            # Check if any trigger matches decision keywords
            for trigger in tag_def.triggers:
                if any(keyword in trigger.lower() for keyword in decision_keywords):
                    relevant_tags.append(tag_name)
                    break

        return list(set(relevant_tags))  # Remove duplicates

    def generate_tag_report(self) -> dict[str, Any]:
        """Generate a comprehensive report of all tags"""
        report = {
            "total_tags": len(self.tags),
            "categories": {},
            "high_priority_tags": [],
            "tag_relationships": {},
            "generated_at": datetime.now().isoformat(),
        }

        # Category statistics
        for category in TagCategory:
            tags_in_cat = self.get_tags_by_category(category)
            report["categories"][category.value] = {
                "count": len(tags_in_cat),
                "tags": [tag.name for tag in tags_in_cat],
            }

        # High priority tags
        for tag_name, tag_def in self.tags.items():
            if tag_def.priority <= 3:
                report["high_priority_tags"].append(
                    {
                        "name": tag_name,
                        "priority": tag_def.priority,
                        "meaning": tag_def.human_meaning,
                    }
                )

        # Relationship summary
        for tag_name, tag_def in self.tags.items():
            if tag_def.related_tags or tag_def.parent_tags or tag_def.child_tags:
                report["tag_relationships"][tag_name] = {
                    "related": list(tag_def.related_tags),
                    "parents": list(tag_def.parent_tags),
                    "children": list(tag_def.child_tags),
                }

        return report

    def export_to_json(self, filepath: str) -> None:
        """Export registry to JSON file"""
        export_data = {
            "tags": {},
            "metadata": {
                "version": "1.0.0",
                "exported_at": datetime.now().isoformat(),
                "total_tags": len(self.tags),
            },
        }

        for tag_name, tag_def in self.tags.items():
            export_data["tags"][tag_name] = {
                "category": tag_def.category.value,
                "description": tag_def.description,
                "human_meaning": tag_def.human_meaning,
                "related_tags": list(tag_def.related_tags),
                "parent_tags": list(tag_def.parent_tags),
                "child_tags": list(tag_def.child_tags),
                "triggers": tag_def.triggers,
                "effects": tag_def.effects,
                "confidence_required": tag_def.confidence_required,
                "priority": tag_def.priority,
            }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)


# Global registry instance
_tag_registry: Optional[TagRegistry] = None


def get_tag_registry() -> TagRegistry:
    """Get the global tag registry instance"""
    global _tag_registry
    if _tag_registry is None:
        _tag_registry = TagRegistry()
    return _tag_registry

# Convenience functions


def explain_tag(tag_name: str, context: Optional[dict[str, Any]] = None) -> str:
    """Get human explanation for a tag"""
    registry = get_tag_registry()
    tag = registry.get_tag(tag_name)

    if not tag:
        return f"Unknown tag: {tag_name}"

    if context:
        return registry.explain_tag_activation(tag_name, context)
    else:
        return tag.to_human_readable()


def get_decision_tags(decision_type: str) -> list[str]:
    """Get tags relevant to a decision"""
    registry = get_tag_registry()
    return registry.get_decision_tags(decision_type)


def get_hormone_tags() -> list[str]:
    """Get all hormone-related tags"""
    registry = get_tag_registry()
    return [tag.name for tag in registry.get_tags_by_category(TagCategory.HORMONE)]

# Neuroplastic tags
# TAG:core
# TAG:registry
# TAG:interpretability
# TAG:professional_architecture