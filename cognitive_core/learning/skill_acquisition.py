"""
LUKHAS Cognitive AI - Skill Acquisition Engine
Advanced skill acquisition and mastery system for consciousness development.
⚛️🧠🛡️ Constellation Framework: Identity-Consciousness-Guardian
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class SkillLevel(Enum):
    """Levels of skill proficiency."""

    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class LearningPhase(Enum):
    """Phases of skill acquisition."""

    DISCOVERY = "discovery"
    PRACTICE = "practice"
    REFINEMENT = "refinement"
    MASTERY = "mastery"
    TEACHING = "teaching"


@dataclass
class Skill:
    """Represents a skill being acquired."""

    skill_id: str
    name: str
    description: str
    current_level: SkillLevel = SkillLevel.NOVICE
    target_level: SkillLevel = SkillLevel.INTERMEDIATE
    practice_hours: float = 0.0
    success_rate: float = 0.0
    learning_phase: LearningPhase = LearningPhase.DISCOVERY
    prerequisites: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_practiced: Optional[datetime] = None


@dataclass
class LearningSession:
    """Represents a learning session for skill acquisition."""

    session_id: str
    skill_id: str
    duration_minutes: float
    activities: list[str] = field(default_factory=list)
    performance_score: Optional[float] = None
    feedback: Optional[str] = None
    challenges_encountered: list[str] = field(default_factory=list)
    breakthroughs: list[str] = field(default_factory=list)
    session_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SkillAcquisitionContext:
    """Context for skill acquisition operations."""

    learning_style: str = "adaptive"
    practice_intensity: str = "moderate"
    feedback_frequency: str = "regular"
    goal_orientation: str = "mastery"
    time_commitment: str = "sustainable"
    metadata: dict[str, Any] = field(default_factory=dict)


class SkillAcquisitionEngine:
    """Advanced skill acquisition engine for consciousness development."""

    def __init__(self, context: Optional[SkillAcquisitionContext] = None):
        """Initialize the skill acquisition engine."""
        self.context = context or SkillAcquisitionContext()
        self.skills: dict[str, Skill] = {}
        self.learning_sessions: list[LearningSession] = []
        self.acquisition_history: list[dict[str, Any]] = []

    def register_skill(
        self,
        skill_id: str,
        name: str,
        description: str,
        target_level: SkillLevel = SkillLevel.INTERMEDIATE,
        prerequisites: Optional[list[str]] = None,
    ) -> Skill:
        """Register a new skill for acquisition."""
        skill = Skill(
            skill_id=skill_id,
            name=name,
            description=description,
            target_level=target_level,
            prerequisites=prerequisites or [],
        )

        self.skills[skill_id] = skill

        # Log skill registration
        self.acquisition_history.append(
            {
                "event": "skill_registered",
                "skill_id": skill_id,
                "name": name,
                "target_level": target_level.value,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        return skill

    async def practice_skill(
        self,
        skill_id: str,
        duration_minutes: float,
        activities: Optional[list[str]] = None,
        performance_score: Optional[float] = None,
    ) -> LearningSession:
        """Practice a skill and record the session."""
        if skill_id not in self.skills:
            raise ValueError(f"Skill '{skill_id}' not registered")

        skill = self.skills[skill_id]

        # Create learning session
        session = LearningSession(
            session_id=f"session_{len(self.learning_sessions)}",
            skill_id=skill_id,
            duration_minutes=duration_minutes,
            activities=activities or [],
            performance_score=performance_score,
        )

        self.learning_sessions.append(session)

        # Update skill progress
        skill.practice_hours += duration_minutes / 60.0
        skill.last_practiced = datetime.now(timezone.utc)

        if performance_score is not None:
            # Update success rate (simple moving average)
            if skill.success_rate == 0.0:
                skill.success_rate = performance_score
            else:
                skill.success_rate = (skill.success_rate * 0.8) + (performance_score * 0.2)

        # Check for level progression
        await self._evaluate_skill_progression(skill)

        return session

    async def _evaluate_skill_progression(self, skill: Skill) -> None:
        """Evaluate if a skill should progress to the next level."""
        progression_thresholds = {
            SkillLevel.NOVICE: (1.0, 0.3),  # 1 hour, 30% success
            SkillLevel.BEGINNER: (5.0, 0.5),  # 5 hours, 50% success
            SkillLevel.INTERMEDIATE: (20.0, 0.7),  # 20 hours, 70% success
            SkillLevel.ADVANCED: (50.0, 0.8),  # 50 hours, 80% success
            SkillLevel.EXPERT: (100.0, 0.9),  # 100 hours, 90% success
        }

        current_level = skill.current_level
        if current_level in progression_thresholds:
            hours_required, success_required = progression_thresholds[current_level]

            if skill.practice_hours >= hours_required and skill.success_rate >= success_required:
                # Progress to next level
                levels = list(SkillLevel)
                current_index = levels.index(current_level)
                if current_index < len(levels) - 1:
                    skill.current_level = levels[current_index + 1]

                    # Log progression
                    self.acquisition_history.append(
                        {
                            "event": "level_progression",
                            "skill_id": skill.skill_id,
                            "old_level": current_level.value,
                            "new_level": skill.current_level.value,
                            "practice_hours": skill.practice_hours,
                            "success_rate": skill.success_rate,
                            "timestamp": datetime.now(timezone.utc),
                        }
                    )

    def get_skill_progress(self, skill_id: str) -> Optional[dict[str, Any]]:
        """Get detailed progress information for a skill."""
        if skill_id not in self.skills:
            return None

        skill = self.skills[skill_id]
        sessions = [s for s in self.learning_sessions if s.skill_id == skill_id]

        return {
            "skill": skill,
            "total_sessions": len(sessions),
            "total_practice_time": skill.practice_hours,
            "current_level": skill.current_level.value,
            "target_level": skill.target_level.value,
            "success_rate": skill.success_rate,
            "recent_sessions": sessions[-5:] if sessions else [],
            "level_progress": self._calculate_level_progress(skill),
        }

    def _calculate_level_progress(self, skill: Skill) -> dict[str, Any]:
        """Calculate progress towards next level."""
        progression_thresholds = {
            SkillLevel.NOVICE: (1.0, 0.3),
            SkillLevel.BEGINNER: (5.0, 0.5),
            SkillLevel.INTERMEDIATE: (20.0, 0.7),
            SkillLevel.ADVANCED: (50.0, 0.8),
            SkillLevel.EXPERT: (100.0, 0.9),
        }

        current_level = skill.current_level
        if current_level not in progression_thresholds:
            return {"progress": 1.0, "status": "master_level"}

        hours_required, success_required = progression_thresholds[current_level]

        hours_progress = min(skill.practice_hours / hours_required, 1.0)
        success_progress = min(skill.success_rate / success_required, 1.0)

        overall_progress = (hours_progress + success_progress) / 2.0

        return {
            "progress": overall_progress,
            "hours_progress": hours_progress,
            "success_progress": success_progress,
            "hours_needed": max(0, hours_required - skill.practice_hours),
            "success_needed": max(0, success_required - skill.success_rate),
        }

    def get_all_skills(self) -> list[Skill]:
        """Get all registered skills."""
        return list(self.skills.values())

    def get_learning_sessions(self, skill_id: Optional[str] = None) -> list[LearningSession]:
        """Get learning sessions, optionally filtered by skill."""
        if skill_id is None:
            return self.learning_sessions.copy()
        return [s for s in self.learning_sessions if s.skill_id == skill_id]


# Convenience functions for quick skill acquisition
async def quick_skill_practice(
    skill_name: str, duration_minutes: float, performance_score: Optional[float] = None
) -> LearningSession:
    """Quick skill practice for simple use cases."""
    engine = SkillAcquisitionEngine()

    # Register skill if not exists
    skill_id = skill_name.lower().replace(" ", "_")
    engine.register_skill(skill_id=skill_id, name=skill_name, description=f"Quick practice of {skill_name}")

    # Practice the skill
    return await engine.practice_skill(
        skill_id=skill_id, duration_minutes=duration_minutes, performance_score=performance_score
    )


def create_skill_acquisition_context(
    learning_style: str = "adaptive", practice_intensity: str = "moderate", **kwargs
) -> SkillAcquisitionContext:
    """Create a skill acquisition context with common settings."""
    return SkillAcquisitionContext(learning_style=learning_style, practice_intensity=practice_intensity, **kwargs)


# Export main classes and functions
__all__ = [
    "LearningPhase",
    "LearningSession",
    "Skill",
    "SkillAcquisitionContext",
    "SkillAcquisitionEngine",
    "SkillLevel",
    "create_skill_acquisition_context",
    "quick_skill_practice",
]
