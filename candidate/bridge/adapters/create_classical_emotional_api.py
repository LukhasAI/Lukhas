#!/usr/bin/env python3
from typing import Any

"""
LUKHAS Classical Emotional Intelligence API - Non-Quantum Alternative
Bio-symbolic emotional processing without quantum enhancement
"""

from datetime import datetime
from enum import Enum
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="LUKHAS Classical Emotional Intelligence API",
    description="Safe, predictable emotional intelligence without quantum effects",
    version="1.0.0",
)


class EmotionModel(str, Enum):
    """Classical emotion models available"""

    PLUTCHIK = "plutchik"  # Wheel of emotions
    EKMAN = "ekman"  # Basic emotions
    VAD = "vad"  # Valence-Arousal-Dominance
    PANAS = "panas"  # Positive/Negative affect


class ClassicalEmotionalContext(BaseModel):
    """Input for classical emotional analysis"""

    text: str = Field(..., description="Text to analyze emotionally")
    user_state: Optional[dict[str, float]] = Field(None, description="Known user emotional state")
    context_type: str = Field("general", description="Type of interaction")
    emotion_model: EmotionModel = Field(EmotionModel.VAD, description="Emotion model to use")
    stability_threshold: float = Field(0.7, ge=0, le=1, description="Emotional stability target")


class ClassicalHormonalState(BaseModel):
    """Simulated hormonal state using classical models"""

    stress_level: float = Field(..., ge=0, le=1, description="General stress indicator")
    energy_level: float = Field(..., ge=0, le=1, description="Energy/fatigue")
    social_comfort: float = Field(..., ge=0, le=1, description="Social ease")
    focus_level: float = Field(..., ge=0, le=1, description="Attention/concentration")
    mood_stability: float = Field(..., ge=0, le=1, description="Emotional stability")


class ClassicalEmotionalVector(BaseModel):
    """Classical emotional state representation"""

    primary_emotion: str
    intensity: float = Field(..., ge=0, le=1)
    secondary_emotions: dict[str, float]
    valence: float = Field(..., ge=-1, le=1)
    arousal: float = Field(..., ge=0, le=1)
    dominance: float = Field(..., ge=0, le=1)


class ClassicalCoherenceResponse(BaseModel):
    """Classical emotional analysis response"""

    analysis_id: str
    timestamp: str
    coherence_score: float = Field(..., ge=0, le=1, description="Classical coherence (max 1.0)")
    emotional_state: ClassicalEmotionalVector
    physiological_indicators: ClassicalHormonalState
    response_guidelines: dict[str, float]
    empathy_markers: list[str]
    stability_assessment: dict[str, Any]
    classical_confidence: float = Field(..., ge=0, le=1)


class ClassicalEmotionEngine:
    """Classical emotion processing engine"""

    def __init__(self):
        # Plutchik's wheel of emotions
        self.plutchik_emotions = {
            "joy": {"valence": 0.8, "arousal": 0.6, "opposites": ["sadness"]},
            "trust": {
                "valence": 0.6,
                "arousal": 0.3,
                "opposites": ["disgust"],
            },
            "fear": {"valence": -0.7, "arousal": 0.8, "opposites": ["anger"]},
            "surprise": {
                "valence": 0.1,
                "arousal": 0.7,
                "opposites": ["anticipation"],
            },
            "sadness": {"valence": -0.6, "arousal": 0.3, "opposites": ["joy"]},
            "disgust": {
                "valence": -0.5,
                "arousal": 0.5,
                "opposites": ["trust"],
            },
            "anger": {"valence": -0.7, "arousal": 0.8, "opposites": ["fear"]},
            "anticipation": {
                "valence": 0.3,
                "arousal": 0.6,
                "opposites": ["surprise"],
            },
        }

        # Emotion regulation strategies
        self.regulation_strategies = {
            "reappraisal": 0.8,  # Cognitive reframing
            "suppression": 0.3,  # Emotion suppression
            "acceptance": 0.7,  # Emotional acceptance
            "distraction": 0.5,  # Attention shifting
            "social_sharing": 0.6,  # Social support
        }

    async def analyze_emotional_coherence(self, context: ClassicalEmotionalContext) -> ClassicalCoherenceResponse:
        """Analyze emotional coherence using classical methods"""

        analysis_id = f"classical_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extract emotions using chosen model
        emotional_state = await self._extract_emotions(context.text, context.emotion_model)

        # Calculate physiological indicators
        physiological = self._calculate_physiological_state(emotional_state, context.context_type, context.user_state)

        # Calculate coherence (classical, max 1.0)
        coherence, stability = self._calculate_classical_coherence(
            emotional_state, physiological, context.stability_threshold
        )

        # Generate response guidelines
        guidelines = self._generate_response_guidelines(emotional_state, physiological, context.context_type)

        # Identify empathy markers
        empathy_markers = self._identify_empathy_patterns(context.text, emotional_state)

        # Assess stability
        stability_assessment = self._assess_emotional_stability(emotional_state, physiological, context.user_state)

        # Calculate confidence
        confidence = self._calculate_confidence(emotional_state, physiological)

        return ClassicalCoherenceResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            coherence_score=coherence,
            emotional_state=emotional_state,
            physiological_indicators=physiological,
            response_guidelines=guidelines,
            empathy_markers=empathy_markers,
            stability_assessment=stability_assessment,
            classical_confidence=confidence,
        )

    async def _extract_emotions(self, text: str, model: EmotionModel) -> ClassicalEmotionalVector:
        """Extract emotions using classical NLP methods"""

        # Simplified emotion detection
        text_lower = text.lower()
        detected_emotions = {}

        # Keyword-based detection (in production, use proper NLP)
        emotion_keywords = {
            "joy": ["happy", "glad", "pleased", "delighted", "joyful"],
            "sadness": ["sad", "unhappy", "depressed", "down", "blue"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
            "fear": ["afraid", "scared", "worried", "anxious", "nervous"],
            "trust": ["trust", "confident", "secure", "reliable"],
            "disgust": ["disgusted", "repulsed", "revolted"],
            "surprise": ["surprised", "amazed", "astonished", "shocked"],
            "anticipation": [
                "excited",
                "eager",
                "looking forward",
                "expecting",
            ],
        }

        # Count keyword matches
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                detected_emotions[emotion] = min(1.0, count * 0.3)

        # Determine primary emotion
        if detected_emotions:
            primary_emotion = max(detected_emotions, key=detected_emotions.get)
            intensity = detected_emotions[primary_emotion]
        else:
            primary_emotion = "neutral"
            intensity = 0.5

        # Calculate VAD values
        if primary_emotion in self.plutchik_emotions:
            vad = self.plutchik_emotions[primary_emotion]
            valence = vad["valence"] * intensity
            arousal = vad["arousal"] * intensity
        else:
            valence = 0.0
            arousal = 0.3

        # Remove primary from secondary
        secondary = detected_emotions.copy()
        if primary_emotion in secondary:
            del secondary[primary_emotion]

        return ClassicalEmotionalVector(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=secondary,
            valence=valence,
            arousal=arousal,
            dominance=0.5,  # Neutral dominance by default
        )

    def _calculate_physiological_state(
        self,
        emotions: ClassicalEmotionalVector,
        context_type: str,
        user_state: Optional[dict[str, float]],
    ) -> ClassicalHormonalState:
        """Calculate physiological indicators from emotions"""

        # Base calculations from emotional state
        stress_level = max(0, emotions.arousal * abs(emotions.valence))
        energy_level = 0.5 + emotions.arousal * 0.3

        # Social comfort based on positive valence
        social_comfort = 0.5 + emotions.valence * 0.3

        # Focus inversely related to extreme emotions
        focus_level = 1.0 - (emotions.intensity * 0.5)

        # Mood stability based on emotion intensity
        mood_stability = 1.0 - (emotions.intensity * 0.3)

        # Adjust based on context
        if context_type == "support":
            social_comfort = min(1.0, social_comfort + 0.2)
            stress_level = max(0, stress_level - 0.1)
        elif context_type == "analytical":
            focus_level = min(1.0, focus_level + 0.2)
            energy_level = min(1.0, energy_level + 0.1)

        # Consider user state if provided
        if user_state and user_state.get("fatigue", 0) > 0.7:
            energy_level = max(0, energy_level - 0.3)
            focus_level = max(0, focus_level - 0.2)

        return ClassicalHormonalState(
            stress_level=stress_level,
            energy_level=energy_level,
            social_comfort=social_comfort,
            focus_level=focus_level,
            mood_stability=mood_stability,
        )

    def _calculate_classical_coherence(
        self,
        emotions: ClassicalEmotionalVector,
        physiology: ClassicalHormonalState,
        threshold: float,
    ) -> tuple[float, float]:
        """Calculate coherence without quantum effects"""

        # Emotional consistency
        emotional_consistency = 1.0 - len(emotions.secondary_emotions) * 0.1

        # Physiological balance
        physio_values = [
            physiology.stress_level,
            physiology.energy_level,
            physiology.social_comfort,
            physiology.focus_level,
            physiology.mood_stability,
        ]
        physio_balance = 1.0 - np.std(physio_values)

        # Alignment between emotion and physiology
        alignment = 1.0

        # High arousal should match high energy
        energy_arousal_diff = abs(emotions.arousal - physiology.energy_level)
        alignment -= energy_arousal_diff * 0.2

        # Positive emotions should reduce stress
        if (emotions.valence > 0 and physiology.stress_level > 0.5) or (
            emotions.valence < 0 and physiology.stress_level < 0.3
        ):
            alignment -= 0.2

        # Calculate final coherence (classical max of 1.0)
        coherence = (emotional_consistency + physio_balance + alignment) / 3
        coherence = max(0, min(1.0, coherence))

        # Stability relative to threshold
        stability = coherence / threshold if threshold > 0 else 1.0

        return coherence, stability

    def _generate_response_guidelines(
        self,
        emotions: ClassicalEmotionalVector,
        physiology: ClassicalHormonalState,
        context_type: str,
    ) -> dict[str, float]:
        """Generate response modulation guidelines"""

        guidelines = {
            "empathy_level": 0.5,
            "energy_matching": 0.5,
            "formality": 0.5,
            "directness": 0.5,
            "warmth": 0.5,
            "patience": 0.5,
        }

        # Adjust based on emotions
        if emotions.primary_emotion in ["sadness", "fear"]:
            guidelines["empathy_level"] = 0.8
            guidelines["warmth"] = 0.7
            guidelines["patience"] = 0.8

        elif emotions.primary_emotion in ["anger", "disgust"]:
            guidelines["patience"] = 0.9
            guidelines["directness"] = 0.3
            guidelines["empathy_level"] = 0.7

        elif emotions.primary_emotion in ["joy", "trust"]:
            guidelines["warmth"] = 0.8
            guidelines["energy_matching"] = 0.7

        # Adjust based on physiology
        guidelines["energy_matching"] = physiology.energy_level

        if physiology.stress_level > 0.7:
            guidelines["patience"] = min(1.0, guidelines["patience"] + 0.2)
            guidelines["directness"] = max(0, guidelines["directness"] - 0.2)

        # Context adjustments
        if context_type == "support":
            guidelines["empathy_level"] = min(1.0, guidelines["empathy_level"] + 0.2)
            guidelines["warmth"] = min(1.0, guidelines["warmth"] + 0.2)
        elif context_type == "analytical":
            guidelines["directness"] = min(1.0, guidelines["directness"] + 0.3)
            guidelines["formality"] = min(1.0, guidelines["formality"] + 0.2)

        return guidelines

    def _identify_empathy_patterns(self, text: str, emotions: ClassicalEmotionalVector) -> list[str]:
        """Identify empathy markers in text"""

        markers = []
        text_lower = text.lower()

        # Acknowledgment patterns
        acknowledgments = [
            "i understand",
            "i see",
            "i hear you",
            "that makes sense",
            "i can imagine",
        ]

        for phrase in acknowledgments:
            if phrase in text_lower:
                markers.append(f"acknowledgment: {phrase}")

        # Validation patterns
        validations = [
            "valid",
            "reasonable",
            "understandable",
            "natural",
            "makes sense",
        ]

        if emotions.valence < 0:  # Negative emotions
            for word in validations:
                if word in text_lower:
                    markers.append("emotional_validation")
                    break

        # Support patterns
        support_words = ["help", "support", "here for", "assist", "together"]
        for word in support_words:
            if word in text_lower:
                markers.append("support_offering")
                break

        # Mirroring language
        if emotions.intensity > 0.6:
            intensity_words = ["very", "really", "quite", "extremely"]
            if any(word in text_lower for word in intensity_words):
                markers.append("intensity_matching")

        return markers

    def _assess_emotional_stability(
        self,
        emotions: ClassicalEmotionalVector,
        physiology: ClassicalHormonalState,
        user_state: Optional[dict[str, float]],
    ) -> dict[str, Any]:
        """Assess emotional stability factors"""

        assessment = {
            "current_stability": physiology.mood_stability,
            "risk_factors": [],
            "protective_factors": [],
            "recommendations": [],
        }

        # Risk factors
        if emotions.intensity > 0.8:
            assessment["risk_factors"].append("High emotional intensity")

        if len(emotions.secondary_emotions) > 3:
            assessment["risk_factors"].append("Multiple conflicting emotions")

        if physiology.stress_level > 0.7:
            assessment["risk_factors"].append("Elevated stress")

        if physiology.energy_level < 0.3:
            assessment["risk_factors"].append("Low energy/fatigue")

        # Protective factors
        if physiology.social_comfort > 0.6:
            assessment["protective_factors"].append("Good social comfort")

        if physiology.focus_level > 0.6:
            assessment["protective_factors"].append("Maintained focus")

        if emotions.valence > 0.3:
            assessment["protective_factors"].append("Positive emotional valence")

        # Recommendations based on assessment
        if len(assessment["risk_factors"]) > len(assessment["protective_factors"]):
            assessment["recommendations"].append("Consider emotion regulation strategies")

            # Suggest best strategies based on state
            if physiology.stress_level > 0.7:
                assessment["recommendations"].append("Relaxation techniques recommended")
            if emotions.intensity > 0.8:
                assessment["recommendations"].append("Cognitive reappraisal may help")

        return assessment

    def _calculate_confidence(
        self,
        emotions: ClassicalEmotionalVector,
        physiology: ClassicalHormonalState,
    ) -> float:
        """Calculate confidence in the analysis"""

        confidence = 0.5  # Base confidence

        # Higher confidence with clear primary emotion
        confidence += emotions.intensity * 0.2

        # Higher confidence with consistent physiology
        if physiology.mood_stability > 0.7:
            confidence += 0.15

        # Lower confidence with many secondary emotions
        confidence -= len(emotions.secondary_emotions) * 0.05

        # Ensure bounds
        return max(0.1, min(0.95, confidence))


# Initialize engine
emotion_engine = ClassicalEmotionEngine()


@app.post(
    "/api/v1/classical-emotional-coherence",
    response_model=ClassicalCoherenceResponse,
)
async def analyze_classical_coherence(context: ClassicalEmotionalContext):
    """
    Analyze emotional coherence using classical, non-quantum methods.

    Benefits over quantum version:
    - No risk of quantum interference
    - Predictable, bounded coherence (max 1.0)
    - Deterministic emotional analysis
    - Compatible with all systems
    - Based on established psychological models
    """
    try:
        response = await emotion_engine.analyze_emotional_coherence(context)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classical analysis failed: {e!s}")


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to LUKHAS Classical Emotional Intelligence API",
        "description": "Safe, predictable emotional analysis without quantum effects",
        "features": [
            "Classical emotion models (Plutchik, Ekman, VAD)",
            "Bounded coherence scores (0-1)",
            "Evidence-based psychology",
            "Deterministic analysis",
            "System-safe implementation",
        ],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "classical",
        "qi_free": True,
        "models_available": ["plutchik", "ekman", "vad", "panas"],
    }


@app.get("/api/v1/emotion-models")
async def get_emotion_models():
    """Get available emotion models"""
    return {
        "models": {
            "plutchik": {
                "description": "Wheel of emotions with 8 primary emotions",
                "use_case": "General emotional analysis",
            },
            "ekman": {
                "description": "Six basic universal emotions",
                "use_case": "Cross-cultural analysis",
            },
            "vad": {
                "description": "Valence-Arousal-Dominance dimensional model",
                "use_case": "Nuanced emotional states",
            },
            "panas": {
                "description": "Positive and Negative Affect Schedule",
                "use_case": "Mood assessment",
            },
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
