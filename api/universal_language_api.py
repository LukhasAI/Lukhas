"""
LUKHAS Universal Language API Endpoints
========================================
FastAPI endpoints for multi-modal language processing,
high-entropy password generation, and OpenAI integration.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from core.colonies.consensus_mechanisms import ConsensusMethod
from core.colonies.enhanced_colony import EnhancedReasoningColony
from lukhas.consciousness.reflection.openai_modulated_service import (
    OpenAIModulatedService,
)
from lukhas.orchestration.gpt_colony_orchestrator import (
    GPTColonyOrchestrator,
    OrchestrationMode,
    OrchestrationTask,
)

# Import LUKHAS components
from lukhas.orchestration.signals.signal_bus import Signal, SignalBus, SignalType
from symbolic.exchange.universal_exchange import (
    ExchangeProtocol,
    UniversalSymbolExchange,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LUKHAS Universal Language API",
    description="Multi-modal language processing and high-entropy password generation",
    version="1.0.0",
)

# Security
security = HTTPBearer()

# Global instances
signal_bus = SignalBus()
orchestrator = GPTColonyOrchestrator(signal_bus=signal_bus)
universal_exchange = UniversalSymbolExchange(signal_bus)
openai_service = OpenAIModulatedService()

# Register colonies
colony = EnhancedReasoningColony("main-colony")
orchestrator.register_colony("main-colony", colony)


# ==================== Request/Response Models ====================


class MultiModalInput(BaseModel):
    """Multi-modal input for language understanding"""

    text: Optional[str] = None
    emoji: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    gesture_sequence: Optional[List[str]] = None


class SymbolUnderstandingRequest(BaseModel):
    """Request for symbol understanding"""

    input: MultiModalInput
    context: Optional[Dict[str, Any]] = {}
    user_id: str


class SymbolUnderstandingResponse(BaseModel):
    """Response from symbol understanding"""

    meaning: str
    confidence: float
    universal_symbol: Optional[str] = None
    entropy_bits: float
    metadata: Dict[str, Any] = {}


class PasswordGenerationRequest(BaseModel):
    """Request for password generation"""

    entropy_bits: int = Field(default=256, ge=128, le=512)
    modalities: List[str] = ["text", "emoji", "gesture"]
    memorability_score: float = Field(default=0.8, ge=0.0, le=1.0)
    user_preferences: Optional[Dict[str, Any]] = {}


class PasswordGenerationResponse(BaseModel):
    """Response from password generation"""

    password_elements: Dict[str, Any]
    entropy_bits: float
    memorability_score: float
    strength_rating: str
    cracking_time_estimate: str


class ExchangeInitiationRequest(BaseModel):
    """Request to initiate symbol exchange"""

    participants: List[str]
    protocol: str = "differential"
    privacy_level: str = "high"


class LanguageBuildRequest(BaseModel):
    """Request to build universal language element"""

    words: List[str]
    symbols: List[str]
    images: Optional[List[str]] = []
    sounds: Optional[List[str]] = []
    gestures: Optional[List[Dict[str, Any]]] = []
    target_meaning: str


class ColonyConsensusRequest(BaseModel):
    """Request for colony consensus"""

    proposal: str
    method: str = "weighted_vote"
    urgency: float = Field(default=0.5, ge=0.0, le=1.0)
    participants: Optional[List[str]] = None


# ==================== Helper Functions ====================


def calculate_entropy(elements: Dict[str, Any]) -> float:
    """Calculate entropy from multi-modal elements"""
    entropy_bits = 0.0

    # Text entropy
    if elements.get("text"):
        charset_size = 94  # ASCII printable
        entropy_bits += len(elements["text"]) * math.log2(charset_size)

    # Emoji entropy
    if elements.get("emojis"):
        emoji_space = 3664  # Unicode emojis
        entropy_bits += len(elements["emojis"]) * math.log2(emoji_space)

    # Gesture entropy
    if elements.get("gestures"):
        gesture_space = 1000  # gesture × timing × pressure
        entropy_bits += len(elements["gestures"]) * math.log2(gesture_space)

    # Image entropy (simplified)
    if elements.get("images"):
        entropy_bits += 50 * len(elements["images"])  # ~50 bits per image

    # Sound entropy (simplified)
    if elements.get("sounds"):
        entropy_bits += 40 * len(elements["sounds"])  # ~40 bits per sound

    return entropy_bits


def estimate_cracking_time(entropy_bits: float) -> str:
    """Estimate time to crack based on entropy"""
    # Assuming 1 trillion guesses per second
    guesses_per_second = 1e12
    total_possibilities = 2**entropy_bits
    seconds = total_possibilities / (2 * guesses_per_second)  # Average case

    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} hours"
    elif seconds < 31536000:
        return f"{seconds/86400:.2f} days"
    elif seconds < 3.15e9:  # 100 years
        return f"{seconds/31536000:.2f} years"
    else:
        return f"{seconds/3.15e9:.2e} centuries"


def get_strength_rating(entropy_bits: float) -> str:
    """Get password strength rating based on entropy"""
    if entropy_bits < 40:
        return "Very Weak"
    elif entropy_bits < 60:
        return "Weak"
    elif entropy_bits < 80:
        return "Fair"
    elif entropy_bits < 100:
        return "Good"
    elif entropy_bits < 128:
        return "Strong"
    elif entropy_bits < 256:
        return "Very Strong"
    else:
        return "Uncrackable"


# ==================== API Endpoints ====================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LUKHAS Universal Language API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/v1/symbols/understand",
            "/api/v1/password/generate",
            "/api/v1/exchange/initiate",
            "/api/v1/language/build",
            "/api/v1/colony/consensus",
        ],
    }


@app.post("/api/v1/symbols/understand", response_model=SymbolUnderstandingResponse)
async def understand_symbols(
    request: SymbolUnderstandingRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Understand multi-modal symbolic input"""
    try:
        # Create orchestration task
        task = OrchestrationTask(
            task_id=f"understand_{request.user_id}_{datetime.now().timestamp()}",
            content=f"Understand symbol: {request.input.dict()}",
            context=request.context,
            mode=OrchestrationMode.COLLABORATIVE,
        )

        # Process through orchestrator
        result = await orchestrator.process_task(task)

        # Calculate entropy of input
        entropy = calculate_entropy(
            {
                "text": request.input.text,
                "emojis": request.input.emoji,
                "gestures": request.input.gesture_sequence,
            }
        )

        # Implement universal symbol lookup
        universal_symbol = None
        try:
            # Get the Universal Language translator
            from universal_language.translator import UniversalTranslator
            translator = UniversalTranslator()

            # Try to find the universal symbol for this input
            # First convert to symbol if it's text
            if isinstance(request.input, str):
                # Look for existing symbol or create one
                from universal_language.vocabulary import get_unified_vocabulary
                vocabulary = get_unified_vocabulary()
                symbol = vocabulary.manager.find_symbol(request.input)

                if symbol and symbol.glyph:
                    universal_symbol = symbol.glyph
                elif result.final_decision:
                    # Try to translate the decision to a universal symbol
                    translation_result = translator.translate(
                        str(result.final_decision),
                        target_type="glyph"
                    )
                    if translation_result and translation_result.is_successful():
                        universal_symbol = str(translation_result.target)
        except Exception as lookup_error:
            logger.debug(f"Universal symbol lookup failed: {lookup_error}")
            # Continue without universal symbol

        return SymbolUnderstandingResponse(
            meaning=str(result.final_decision) if result.final_decision else "unknown",
            confidence=result.confidence,
            universal_symbol=universal_symbol,
            entropy_bits=entropy,
            metadata={
                "processing_time": result.processing_time,
                "mode_used": result.mode_used.value,
            },
        )

    except Exception as e:
        logger.error(f"Symbol understanding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/password/generate", response_model=PasswordGenerationResponse)
async def generate_password(
    request: PasswordGenerationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Generate high-entropy password using multi-modal elements"""
    try:
        password_elements = {}

        # Generate text component
        if "text" in request.modalities:
            # Simple random text generation (would use better algorithm in production)
            import random
            import string

            text_length = max(3, request.entropy_bits // 20)
            password_elements["text"] = "".join(
                random.choices(string.ascii_letters + string.digits, k=text_length)
            )

        # Generate emoji component
        if "emoji" in request.modalities:
            emojis = ["🌟", "🔐", "🧬", "💫", "🎯", "🚀", "💎", "🔥"]
            emoji_count = min(len(emojis), max(2, request.entropy_bits // 50))
            password_elements["emojis"] = random.sample(emojis, emoji_count)

        # Generate gesture component
        if "gesture" in request.modalities:
            gestures = [
                {"type": "swipe_up", "timing": 0.3, "pressure": 0.8},
                {"type": "circle", "timing": 0.5, "pressure": 0.6},
                {"type": "tap_tap_hold", "timing": 1.2, "pressure": 0.9},
                {"type": "zigzag", "timing": 0.7, "pressure": 0.7},
            ]
            gesture_count = min(len(gestures), max(1, request.entropy_bits // 80))
            password_elements["gestures"] = random.sample(gestures, gesture_count)

        # Calculate actual entropy
        actual_entropy = calculate_entropy(password_elements)

        # Calculate memorability (simplified)
        element_count = sum(
            len(v) if isinstance(v, (list, str)) else 1
            for v in password_elements.values()
        )
        memorability = max(0.3, min(1.0, 1.0 - (element_count / 20)))

        return PasswordGenerationResponse(
            password_elements=password_elements,
            entropy_bits=actual_entropy,
            memorability_score=memorability,
            strength_rating=get_strength_rating(actual_entropy),
            cracking_time_estimate=estimate_cracking_time(actual_entropy),
        )

    except Exception as e:
        logger.error(f"Password generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/exchange/initiate")
async def initiate_exchange(
    request: ExchangeInitiationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Initiate privacy-preserving symbol exchange"""
    try:
        # Map protocol string to enum
        protocol_map = {
            "differential": ExchangeProtocol.DIFFERENTIAL,
            "federated": ExchangeProtocol.FEDERATED,
            "colony": ExchangeProtocol.COLONY,
            "hashed": ExchangeProtocol.HASHED,
        }
        protocol = protocol_map.get(request.protocol, ExchangeProtocol.DIFFERENTIAL)

        # Initiate exchange
        session_id = await universal_exchange.initiate_exchange(
            initiator_id=request.participants[0],
            participant_ids=request.participants[1:],
            protocol=protocol,
        )

        return {
            "session_id": session_id,
            "participants": request.participants,
            "protocol": request.protocol,
            "privacy_level": request.privacy_level,
            "status": "initiated",
        }

    except Exception as e:
        logger.error(f"Exchange initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/language/build")
async def build_language(
    request: LanguageBuildRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Build universal language element from multi-modal inputs"""
    try:
        # Create comprehensive input
        combined_input = {
            "words": request.words,
            "symbols": request.symbols,
            "images": request.images or [],
            "sounds": request.sounds or [],
            "gestures": request.gestures or [],
            "target": request.target_meaning,
        }

        # Process through orchestrator
        task = OrchestrationTask(
            task_id=f"build_{request.target_meaning}_{datetime.now().timestamp()}",
            content=f"Build universal symbol for: {request.target_meaning}",
            context=combined_input,
            mode=OrchestrationMode.FEDERATED,
        )

        result = await orchestrator.process_task(task)

        # Calculate entropy contribution
        entropy = calculate_entropy(
            {
                "text": " ".join(request.words),
                "emojis": " ".join(request.symbols),
                "gestures": request.gestures,
            }
        )

        return {
            "target_meaning": request.target_meaning,
            "universal_symbol": result.final_decision,
            "confidence": result.confidence,
            "entropy_contribution": entropy,
            "input_modalities": len(
                [
                    x
                    for x in [
                        request.words,
                        request.symbols,
                        request.images,
                        request.sounds,
                        request.gestures,
                    ]
                    if x
                ]
            ),
            "status": "created" if result.confidence > 0.7 else "pending_validation",
        }

    except Exception as e:
        logger.error(f"Language building error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/colony/consensus")
async def colony_consensus(
    request: ColonyConsensusRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Request colony consensus on a proposal"""
    try:
        # Map method string to enum
        method_map = {
            "majority_vote": ConsensusMethod.MAJORITY_VOTE,
            "weighted_vote": ConsensusMethod.WEIGHTED_VOTE,
            "hormone": ConsensusMethod.HORMONE,
            "byzantine": ConsensusMethod.BYZANTINE,
            "emergent": ConsensusMethod.EMERGENT,
        }
        method_map.get(request.method, ConsensusMethod.WEIGHTED_VOTE)

        # Update hormone levels based on urgency
        if request.urgency > 0.7:
            colony.homeostasis.update_hormone_levels(
                {"urgency": request.urgency, "stress": request.urgency * 0.5}
            )

        # Create consensus task
        task = OrchestrationTask(
            task_id=f"consensus_{datetime.now().timestamp()}",
            content=request.proposal,
            context={"urgency": request.urgency},
            mode=OrchestrationMode.PARALLEL,
        )

        # Process through orchestrator
        result = await orchestrator.process_task(task)

        return {
            "proposal": request.proposal,
            "decision": str(result.final_decision),
            "confidence": result.confidence,
            "method_used": request.method,
            "urgency_level": request.urgency,
            "processing_time": result.processing_time,
            "consensus_reached": result.confidence > 0.6,
        }

    except Exception as e:
        logger.error(f"Colony consensus error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_statistics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get system statistics"""
    try:
        # Get various statistics
        exchange_stats = universal_exchange.get_universal_stats()
        orchestrator_stats = orchestrator.get_performance_report()

        # Get active signals
        active_signals = signal_bus.get_active_signals()

        return {
            "system_status": "operational",
            "universal_symbols": exchange_stats.get("adopted_symbols", 0),
            "active_sessions": exchange_stats.get("active_sessions", 0),
            "colonies_registered": orchestrator_stats.get("registered_colonies", 0),
            "tasks_completed": orchestrator_stats.get("completed_tasks", 0),
            "active_signals": len(active_signals),
            "performance_metrics": orchestrator_stats.get("metrics", {}),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Startup/Shutdown Events ====================


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("LUKHAS Universal Language API starting up...")

    # Initialize colonies
    for i in range(3):
        colony = EnhancedReasoningColony(f"colony_{i}")
        orchestrator.register_colony(f"colony_{i}", colony)

    # Emit startup signal
    signal = Signal(
        name=SignalType.NOVELTY,
        source="api_startup",
        level=1.0,
        metadata={"event": "system_startup"},
    )
    signal_bus.publish(signal)

    logger.info("API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("LUKHAS Universal Language API shutting down...")

    # Emit shutdown signal
    signal = Signal(
        name=SignalType.STRESS,
        source="api_shutdown",
        level=0.1,
        metadata={"event": "system_shutdown"},
    )
    signal_bus.publish(signal)

    logger.info("API shutdown complete")


# ==================== Run Server ====================

if __name__ == "__main__":
    import os

    import uvicorn

    # Configuration from environment variables with sensible defaults
    host = os.getenv("LUKHAS_LANG_API_HOST", "0.0.0.0")
    port = int(os.getenv("LUKHAS_LANG_API_PORT", "8081"))  # Different default port
    log_level = os.getenv("LUKHAS_LOG_LEVEL", "info").lower()

    logger.info(f"Starting LUKHAS Universal Language API on {host}:{port}")

    uvicorn.run(app, host=host, port=port, log_level=log_level)
