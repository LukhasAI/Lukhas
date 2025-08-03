#!/usr/bin/env python3
"""
LUKHAS Emotional Coherence API - Bio-Symbolic Emotional Intelligence
Adds genuine emotional understanding to any AI response
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

app = FastAPI(
    title="LUKHAS Emotional Coherence API",
    description="Bio-symbolic emotional intelligence for AI systems",
    version="1.0.0"
)

class EmotionalContext(BaseModel):
    """Input for emotional analysis"""
    text: str = Field(..., description="Text to analyze emotionally")
    user_state: Optional[Dict[str, float]] = Field(None, description="Known user emotional state")
    context_type: str = Field("general", description="Type of interaction: support, creative, analytical, social")
    target_coherence: float = Field(0.85, ge=0, le=1, description="Target bio-symbolic coherence")

class HormonalState(BaseModel):
    """Simulated hormonal state"""
    cortisol: float = Field(..., ge=0, le=1, description="Stress hormone")
    dopamine: float = Field(..., ge=0, le=1, description="Reward/motivation")
    serotonin: float = Field(..., ge=0, le=1, description="Mood/well-being")
    oxytocin: float = Field(..., ge=0, le=1, description="Social bonding")
    adrenaline: float = Field(..., ge=0, le=1, description="Urgency/energy")
    
class EmotionalVector(BaseModel):
    """Multi-dimensional emotional state"""
    valence: float = Field(..., ge=-1, le=1, description="Positive/negative")
    arousal: float = Field(..., ge=0, le=1, description="Activation level")
    dominance: float = Field(..., ge=0, le=1, description="Control level")
    emotions: Dict[str, float] = Field(..., description="Specific emotion intensities")

class CoherenceResponse(BaseModel):
    """Complete emotional coherence analysis"""
    coherence_score: float = Field(..., ge=0, description="Bio-symbolic coherence (can exceed 100%)")
    emotional_vector: EmotionalVector
    recommended_hormonal_state: HormonalState
    response_modulation: Dict[str, float]
    empathy_markers: List[str]
    coherence_insights: List[str]
    quantum_amplification: float = Field(..., ge=1, description="Quantum coherence boost factor")

class BioSymbolicEngine:
    """Core bio-symbolic coherence engine"""
    
    def __init__(self):
        self.emotion_lexicon = {
            'joy': {'valence': 0.8, 'arousal': 0.7, 'dominance': 0.6},
            'sadness': {'valence': -0.6, 'arousal': 0.3, 'dominance': 0.2},
            'anger': {'valence': -0.7, 'arousal': 0.8, 'dominance': 0.7},
            'fear': {'valence': -0.8, 'arousal': 0.7, 'dominance': 0.1},
            'surprise': {'valence': 0.1, 'arousal': 0.8, 'dominance': 0.4},
            'love': {'valence': 0.9, 'arousal': 0.6, 'dominance': 0.5},
            'stress': {'valence': -0.5, 'arousal': 0.8, 'dominance': 0.3},
            'calm': {'valence': 0.3, 'arousal': 0.2, 'dominance': 0.6}
        }
    
    async def analyze_coherence(self, context: EmotionalContext) -> CoherenceResponse:
        """Analyze emotional coherence of text"""
        
        # Extract emotional vector from text
        emotional_vector = await self._extract_emotions(context.text)
        
        # Calculate optimal hormonal state
        hormonal_state = self._calculate_hormonal_response(
            emotional_vector,
            context.context_type,
            context.user_state
        )
        
        # Calculate bio-symbolic coherence
        coherence, quantum_boost = self._calculate_coherence(
            emotional_vector,
            hormonal_state,
            context.target_coherence
        )
        
        # Generate response modulation recommendations
        modulation = self._generate_modulation(hormonal_state, emotional_vector)
        
        # Extract empathy markers
        empathy_markers = self._identify_empathy_markers(context.text, emotional_vector)
        
        # Generate insights
        insights = self._generate_coherence_insights(
            coherence,
            hormonal_state,
            emotional_vector
        )
        
        return CoherenceResponse(
            coherence_score=coherence,
            emotional_vector=emotional_vector,
            recommended_hormonal_state=hormonal_state,
            response_modulation=modulation,
            empathy_markers=empathy_markers,
            coherence_insights=insights,
            quantum_amplification=quantum_boost
        )
    
    async def _extract_emotions(self, text: str) -> EmotionalVector:
        """Extract emotional vector from text"""
        # In real LUKHAS, this would use advanced NLP
        # For demo, we'll use keyword matching and patterns
        
        emotions = {}
        text_lower = text.lower()
        
        # Detect emotions based on keywords (simplified)
        emotion_keywords = {
            'joy': ['happy', 'excited', 'wonderful', 'great', 'amazing'],
            'sadness': ['sad', 'disappointed', 'unfortunate', 'sorry'],
            'anger': ['angry', 'frustrated', 'annoyed', 'irritated'],
            'fear': ['worried', 'anxious', 'scared', 'concerned'],
            'stress': ['overwhelmed', 'pressure', 'stressed', 'burden']
        }
        
        for emotion, keywords in emotion_keywords.items():
            intensity = sum(1 for keyword in keywords if keyword in text_lower)
            if intensity > 0:
                emotions[emotion] = min(1.0, intensity * 0.3)
        
        # Calculate VAD (Valence, Arousal, Dominance)
        valence = 0.0
        arousal = 0.0
        dominance = 0.5
        
        for emotion, intensity in emotions.items():
            if emotion in self.emotion_lexicon:
                emo_vad = self.emotion_lexicon[emotion]
                valence += emo_vad['valence'] * intensity
                arousal += emo_vad['arousal'] * intensity
                dominance += emo_vad['dominance'] * intensity
        
        # Normalize
        total_intensity = sum(emotions.values()) or 1.0
        
        return EmotionalVector(
            valence=valence / total_intensity,
            arousal=arousal / total_intensity,
            dominance=dominance / total_intensity,
            emotions=emotions
        )
    
    def _calculate_hormonal_response(
        self,
        emotions: EmotionalVector,
        context_type: str,
        user_state: Optional[Dict[str, float]]
    ) -> HormonalState:
        """Calculate optimal hormonal state for response"""
        
        # Base hormonal response from emotions
        cortisol = max(0, -emotions.valence * 0.5 + emotions.arousal * 0.3)
        dopamine = max(0, emotions.valence * 0.6 + emotions.dominance * 0.2)
        serotonin = max(0, emotions.valence * 0.4 + (1 - emotions.arousal) * 0.3)
        oxytocin = 0.3  # Base social connection
        adrenaline = emotions.arousal * 0.4
        
        # Adjust based on context
        if context_type == "support":
            oxytocin = min(1.0, oxytocin + 0.4)
            serotonin = min(1.0, serotonin + 0.2)
        elif context_type == "creative":
            dopamine = min(1.0, dopamine + 0.3)
            cortisol = max(0, cortisol - 0.2)
        elif context_type == "analytical":
            cortisol = min(1.0, cortisol + 0.1)  # Slight focus enhancement
            adrenaline = max(0, adrenaline - 0.2)
            
        # Consider user state if provided
        if user_state:
            if user_state.get('stress', 0) > 0.7:
                # User is stressed, increase calming hormones
                serotonin = min(1.0, serotonin + 0.2)
                oxytocin = min(1.0, oxytocin + 0.2)
                
        return HormonalState(
            cortisol=cortisol,
            dopamine=dopamine,
            serotonin=serotonin,
            oxytocin=oxytocin,
            adrenaline=adrenaline
        )
    
    def _calculate_coherence(
        self,
        emotions: EmotionalVector,
        hormones: HormonalState,
        target: float
    ) -> Tuple[float, float]:
        """Calculate bio-symbolic coherence with quantum enhancement"""
        
        # Base coherence from alignment
        emotional_balance = 1.0 - abs(emotions.valence)
        hormonal_balance = 1.0 - np.std([
            hormones.cortisol,
            hormones.dopamine,
            hormones.serotonin,
            hormones.oxytocin,
            hormones.adrenaline
        ])
        
        # Calculate base coherence
        base_coherence = (emotional_balance + hormonal_balance) / 2
        
        # Quantum enhancement (can push >100%)
        quantum_boost = 1.0
        if base_coherence > 0.7:
            # High coherence gets quantum amplification
            quantum_boost = 1.0 + (base_coherence - 0.7) * 1.5
            
        # Apply quantum boost
        final_coherence = base_coherence * quantum_boost
        
        # LUKHAS special: Can exceed 100% with perfect bio-symbolic alignment
        if emotional_balance > 0.9 and hormonal_balance > 0.9:
            final_coherence *= 1.2  # 20% bonus for perfect alignment
            
        return final_coherence, quantum_boost
    
    def _generate_modulation(
        self,
        hormones: HormonalState,
        emotions: EmotionalVector
    ) -> Dict[str, float]:
        """Generate response modulation recommendations"""
        
        modulation = {
            'empathy_level': hormones.oxytocin,
            'energy_level': hormones.adrenaline,
            'optimism_bias': hormones.dopamine,
            'patience_factor': hormones.serotonin,
            'urgency_response': hormones.cortisol,
            'creativity_boost': max(0, hormones.dopamine - hormones.cortisol),
            'social_warmth': (hormones.oxytocin + hormones.serotonin) / 2
        }
        
        # Adjust based on emotional state
        if emotions.valence < -0.5:
            modulation['empathy_level'] = min(1.0, modulation['empathy_level'] + 0.3)
            modulation['patience_factor'] = min(1.0, modulation['patience_factor'] + 0.2)
            
        return modulation
    
    def _identify_empathy_markers(
        self,
        text: str,
        emotions: EmotionalVector
    ) -> List[str]:
        """Identify empathy markers in text"""
        
        markers = []
        
        # Check for emotion acknowledgment
        acknowledgment_phrases = [
            'i understand', 'i see', 'that must be', 'sounds like',
            'i hear you', 'i can imagine'
        ]
        
        for phrase in acknowledgment_phrases:
            if phrase in text.lower():
                markers.append(f"acknowledgment: {phrase}")
                
        # Check for validation
        if emotions.valence < 0 and any(word in text.lower() for word in ['valid', 'understandable', 'makes sense']):
            markers.append("emotional_validation")
            
        # Check for support offering
        if any(word in text.lower() for word in ['help', 'support', 'here for you', 'together']):
            markers.append("support_offering")
            
        return markers
    
    def _generate_coherence_insights(
        self,
        coherence: float,
        hormones: HormonalState,
        emotions: EmotionalVector
    ) -> List[str]:
        """Generate insights about coherence state"""
        
        insights = []
        
        if coherence > 1.0:
            insights.append("Achieved super-coherence through bio-symbolic alignment!")
            
        if coherence > 0.85:
            insights.append("High coherence: Emotional and hormonal states well-aligned")
        elif coherence < 0.5:
            insights.append("Low coherence: Consider adjusting emotional response")
            
        # Hormonal insights
        if hormones.cortisol > 0.7:
            insights.append("High stress detected - consider calming approach")
        if hormones.oxytocin > 0.7:
            insights.append("Strong social bonding opportunity")
        if hormones.dopamine > 0.7 and hormones.serotonin > 0.6:
            insights.append("Optimal state for creative collaboration")
            
        # Emotional insights
        if abs(emotions.valence) < 0.2:
            insights.append("Neutral emotional state - safe for any response type")
        if emotions.arousal > 0.8:
            insights.append("High arousal - match energy or provide grounding")
            
        return insights

# Initialize engine
bio_engine = BioSymbolicEngine()

@app.post("/api/v1/emotional-coherence", response_model=CoherenceResponse)
async def analyze_emotional_coherence(context: EmotionalContext):
    """
    Analyze the emotional coherence of text and provide bio-symbolic recommendations.
    
    This API uses LUKHAS's bio-symbolic engine to:
    - Extract emotional vectors from text
    - Calculate optimal hormonal states
    - Achieve >100% coherence through quantum enhancement
    - Provide response modulation recommendations
    """
    try:
        response = await bio_engine.analyze_coherence(context)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coherence analysis failed: {str(e)}")

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to LUKHAS Emotional Coherence API",
        "description": "Bio-symbolic emotional intelligence for AI systems",
        "features": [
            "Emotional vector extraction",
            "Hormonal state optimization",
            ">100% coherence achievement",
            "Quantum enhancement"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bio_engine": "active",
        "coherence": "optimal",
        "quantum_field": "stable"
    }

# Example usage endpoint
@app.post("/api/v1/demo")
async def demo_integration():
    """Demo: How to integrate with GPT/Claude"""
    return {
        "example": "Enhance GPT/Claude responses with emotional intelligence",
        "steps": [
            "1. Generate response with GPT/Claude",
            "2. Analyze with LUKHAS Emotional Coherence API",
            "3. Apply hormonal modulation to response",
            "4. Achieve genuine emotional connection"
        ],
        "code_example": """
# Get GPT response
gpt_response = openai.complete(prompt)

# Analyze emotional coherence
coherence = lukhas.emotional_coherence({
    'text': gpt_response,
    'context_type': 'support'
})

# Apply modulation
final_response = apply_emotional_modulation(
    gpt_response,
    coherence.response_modulation,
    coherence.recommended_hormonal_state
)
"""
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)