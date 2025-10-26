from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class TemporalFeel(str, Enum):
    """Temporal phenomenological qualities"""

    ELASTIC = "elastic"
    SUSPENDED = "suspended"
    URGENT = "urgent"
    MUNDANE = "mundane"
    FLOWING = "flowing"


class AgencyFeel(str, Enum):
    """Agency phenomenological qualities"""

    PASSIVE = "passive"
    ACTIVE = "active"
    SHARED = "shared"
    EMPOWERED = "empowered"


class SeverityLevel(str, Enum):
    """TEQ Guardian severity levels"""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class RiskSeverity(str, Enum):
    """Risk assessment severity levels"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ProtoQualia(BaseModel):
    """
    8-dimensional operational proto-qualia representation.

    NOT claiming "true qualia" - operational approximation for
    phenomenologically grounded control loop.
    """

    # Core affective dimensions
    tone: float = Field(ge=-1.0, le=1.0, description="Valence dimension")
    arousal: float = Field(ge=0.0, le=1.0, description="Activation level")
    clarity: float = Field(ge=0.0, le=1.0, description="Phenomenal clarity")
    embodiment: float = Field(ge=0.0, le=1.0, description="Body awareness")

    # Symbolic and temporal qualities
    colorfield: str = Field(description="Symbolic palette (e.g., 'aka/red', 'aoi/blue')")
    temporal_feel: TemporalFeel = Field(description="Temporal experience quality")
    agency_feel: AgencyFeel = Field(description="Agency experience quality")
    narrative_gravity: float = Field(ge=0.0, le=1.0, description="Story attractor strength")

    @validator("colorfield")
    def validate_colorfield(cls, v):
        """Ensure colorfield follows LUKHAS naming conventions"""
        if v and "/" not in v:  # Allow empty strings but validate non-empty ones
            raise ValueError("colorfield must contain '/' separator (e.g., 'aka/red')")
        return v

    def energy_signature(self) -> float:
        """Compute total affective energy for sublimation conservation"""
        return abs(self.tone) + self.arousal + self.clarity + self.embodiment


class RiskProfile(BaseModel):
    """TEQ Guardian risk assessment result"""

    score: float = Field(ge=0.0, le=1.0, description="Risk score 0-1")
    reasons: list[str] = Field(default_factory=list, description="Risk factors identified")
    severity: SeverityLevel = Field(description="Severity classification")

    @validator("severity")
    def severity_matches_score(cls, v, values):
        """Ensure severity aligns with score"""
        if "score" not in values:
            return v

        score = values["score"]
        if v == SeverityLevel.NONE and score > 0.1:
            raise ValueError("NONE severity requires score ≤ 0.1")
        elif v == SeverityLevel.LOW and (score < 0.1 or score > 0.3):
            raise ValueError("LOW severity requires score 0.1-0.3")
        elif v == SeverityLevel.MODERATE and (score < 0.3 or score > 0.7):
            raise ValueError("MODERATE severity requires score 0.3-0.7")
        elif v == SeverityLevel.HIGH and score < 0.7:
            raise ValueError("HIGH severity requires score ≥ 0.7")
        return v


class RiskGauge(BaseModel):
    """Risk assessment gauge for router decisions"""

    score: float = Field(ge=0.0, le=1.0, description="Risk score 0-1")
    severity: RiskSeverity = Field(description="Risk severity classification")

    @validator("severity")
    def severity_matches_score(cls, v, values):
        """Ensure severity aligns with score"""
        if "score" not in values:
            return v

        score = values["score"]
        if v == RiskSeverity.LOW and score > 0.3:
            raise ValueError("LOW severity requires score ≤ 0.3")
        elif v == RiskSeverity.MODERATE and (score < 0.3 or score > 0.7):
            raise ValueError("MODERATE severity requires score 0.3-0.7")
        elif v == RiskSeverity.HIGH and (score < 0.7 or score > 0.9):
            raise ValueError("HIGH severity requires score 0.7-0.9")
        elif v == RiskSeverity.CRITICAL and score < 0.9:
            raise ValueError("CRITICAL severity requires score ≥ 0.9")
        return v


class PhenomenalScene(BaseModel):
    """Complete phenomenological scene with proto-qualia and context"""

    proto: ProtoQualia = Field(description="Proto-qualia representation")
    subject: str = Field(description="Scene subject")
    object: str = Field(description="Scene object/focus")
    context: dict[str, Any] = Field(default_factory=dict, description="Scene context")
    risk: RiskProfile = Field(description="TEQ Guardian risk assessment")

    # Audit trail for transforms
    transform_chain: list[str] = Field(default_factory=list, description="Applied transforms")
    timestamp: Optional[float] = Field(None, description="Scene generation timestamp")


class PhenomenalGlyph(BaseModel):
    """GLYPH representation for phenomenological routing"""

    key: str = Field(description="GLYPH key following LUKHAS naming")
    attrs: dict[str, Any] = Field(default_factory=dict, description="GLYPH attributes")

    @validator("key")
    def validate_glyph_key(cls, v):
        """Ensure GLYPH key follows conventions"""
        valid_prefixes = ["aka:", "aoi:", "vigilance", "approach_avoid", "threshold"]
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            # Allow any key but warn about convention
            pass
        return v


class RegulationPolicy(BaseModel):
    """Policy output for phenomenological regulation"""

    gain: float = Field(ge=0.0, le=2.0, description="Attention gain modulation")
    pace: float = Field(ge=0.1, le=2.0, description="Temporal pace adjustment")
    color_contrast: Optional[str] = Field(None, description="Color palette override")
    actions: list[str] = Field(default_factory=list, description="Regulation actions")

    @validator("actions")
    def validate_actions(cls, v):
        """Ensure regulation actions are from approved set"""
        approved_actions = {"pause", "reframe", "breathing", "focus-shift", "sublimate"}
        invalid_actions = set(v) - approved_actions
        if invalid_actions:
            raise ValueError(f"Invalid actions: {invalid_actions}. Use: {approved_actions}")
        return v


class Metrics(BaseModel):
    """Phenomenological metrics for evaluation"""

    # Core success metrics
    drift_phi: float = Field(description="Scene temporal coherence")
    congruence_index: float = Field(ge=0.0, le=1.0, description="Goals↔ethics↔scene alignment")
    sublimation_rate: float = Field(ge=0.0, le=1.0, description="Transformed/total energy")
    neurosis_risk: float = Field(ge=0.0, le=1.0, description="Loop recurrence probability")
    qualia_novelty: float = Field(ge=0.0, le=1.0, description="1 - similarity(PQ_t, PQ_hist)")
    repair_delta: float = Field(description="Stress reduction post-regulation")

    # Timestamps and context
    timestamp: Optional[float] = Field(None, description="Metrics computation time")
    episode_id: Optional[str] = Field(None, description="Episode identifier")


class PLSLatent(BaseModel):
    """Phenomenal Latent Space representation"""

    # Latent dimensions (simple deterministic v1)
    threat_level: float = Field(ge=0.0, le=1.0, description="Threat detection")
    soothing_level: float = Field(ge=0.0, le=1.0, description="Soothing detection")
    complexity: float = Field(ge=0.0, le=1.0, description="Signal complexity")
    familiarity: float = Field(ge=0.0, le=1.0, description="Memory resonance")
    temporal_pressure: float = Field(ge=0.0, le=1.0, description="Urgency signals")
    agency_signals: float = Field(ge=0.0, le=1.0, description="Control/agency cues")

    # Temperature for stochastic decoding
    temperature: float = Field(default=0.4, ge=0.0, le=2.0, description="Decode randomness")


class SublimatioNResult(BaseModel):
    """Result of affect sublimation transform"""

    original_scene: PhenomenalScene = Field(description="Pre-transform scene")
    transformed_scene: PhenomenalScene = Field(description="Post-transform scene")
    energy_preserved: float = Field(ge=0.0, le=1.0, description="Energy conservation ratio")
    transform_type: str = Field(description="Type of sublimation applied")
    transform_success: bool = Field(description="Transform completed successfully")
