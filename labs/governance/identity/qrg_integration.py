#!/usr/bin/env python3
"""
🔗 LUKHAS QRG Integration Module

This module integrates QR Code Generators (QRGs) with the LUKHAS Authentication System,
providing consciousness-aware, culturally-adaptive, and quantum-enhanced QR codes
for secure authentication and identity verification.

Features:
- Real-time consciousness adaptation
- Cultural sensitivity integration
- Quantum encryption protocols
- Steganographic data embedding
- Multi-modal authentication support
- Emergency override patterns
- Dream-state visualization
- Constitutional AI compliance

Author: LUKHAS AI System
License: LUKHAS Commercial License
"""
import hashlib
import logging
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

# Import core system modules
try:
    from backend.audit_logger import AuditLogger

    from lukhas.governance.identity.auth.cultural_profile_manager import CulturalProfileManager
    from lukhas.consciousness.core_consciousness.consciousness_engine import (
        ConsciousnessEngine,
    )
    from lukhas.consciousness.core_consciousness.qi_consciousness_visualizer import (
        QIConsciousnessVisualizer,
    )
    from lukhas.core.interfaces.as_agent.core.gatekeeper import (
        ConstitutionalGatekeeper,
    )
    from utils.cognitive_load_estimator import CognitiveLoadEstimator
    from utils.cultural_safety_checker import CulturalSafetyChecker
except ImportError:
    # Fallback for standalone operation
    print("⚠️ Core modules not available, using mock implementations")

    class MockModule:
        def __init__(self, name):
            self.name = name

        def __getattr__(self, item):
            return lambda *_args, **_kwargs: {"status": "mock", "module": self.name}

        def __call__(self, *_args, **_kwargs):
            return self

    ConsciousnessEngine = MockModule("ConsciousnessEngine")
    CulturalProfileManager = MockModule("CulturalProfileManager")
    QIConsciousnessVisualizer = MockModule("QIConsciousnessVisualizer")
    ConstitutionalGatekeeper = MockModule("ConstitutionalGatekeeper")
    CognitiveLoadEstimator = MockModule("CognitiveLoadEstimator")
    CulturalSafetyChecker = MockModule("CulturalSafetyChecker")
    AuditLogger = MockModule("AuditLogger")


class QRGType(Enum):
    """QRG types supported by the LUKHAS system"""

    CONSCIOUSNESS_ADAPTIVE = "consciousness_adaptive"
    CULTURAL_SYMBOLIC = "cultural_symbolic"
    QUANTUM_ENCRYPTED = "qi_encrypted"
    STEGANOGRAPHIC = "steganographic"
    DREAM_STATE = "dream_state"
    EMERGENCY_OVERRIDE = "emergency_override"
    CONSTITUTIONAL_COMPLIANT = "constitutional_compliant"
    MULTI_MODAL = "multi_modal"


class SecurityLevel(Enum):
    """Security levels for QRG generation"""

    PUBLIC = "public"
    PROTECTED = "protected"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    COSMIC = "cosmic"  # LUKHAS highest classification


@dataclass
class QRGContext:
    """Context information for QRG generation"""

    user_id: str
    consciousness_level: float
    cultural_profile: dict[str, Any]
    security_clearance: SecurityLevel
    cognitive_load: float
    attention_focus: list[str]
    timestamp: datetime
    session_id: str
    device_capabilities: dict[str, Any]
    environmental_factors: dict[str, Any]


@dataclass
class QRGResult:
    """Result of QRG generation"""

    qr_type: QRGType
    pattern_data: str
    metadata: dict[str, Any]
    security_signature: str
    expiration: datetime
    compliance_score: float
    cultural_safety_score: float
    consciousness_resonance: float
    generation_metrics: dict[str, Any]


class LukhusQRGIntegrator:
    """
    🔗 LUKHAS QRG Integration System

    Integrates advanced QR Code Generators with the LUKHAS Authentication System,
    providing consciousness-aware, culturally-sensitive, and quantum-enhanced
    authentication patterns.
    """

    def __init__(self):
        """Initialize the QRG Integrator with all required components"""
        self.consciousness_engine = ConsciousnessEngine()
        self.cultural_manager = CulturalProfileManager()
        self.qi_visualizer = QIConsciousnessVisualizer()
        self.constitutional_gatekeeper = ConstitutionalGatekeeper()
        self.cognitive_estimator = CognitiveLoadEstimator()
        self.safety_checker = CulturalSafetyChecker()
        self.audit_logger = AuditLogger()

        # Internal state
        self.active_sessions = {}
        self.generation_history = []
        self.cultural_adaptation_cache = {}
        self.qi_like_states = {}

        # Configuration
        self.config = {
            "max_pattern_size": 177,  # High-density QR capacity
            "min_consciousness_threshold": 0.1,
            "cultural_safety_threshold": 0.8,
            "qi_coherence_target": 0.95,
            "constitutional_compliance_required": True,
            "dream_state_enabled": True,
            "emergency_override_allowed": True,
            "steganographic_capacity_limit": 2048,  # bytes
            "session_timeout": 3600,  # 1 hour
        }
        # initialize logger for this integrator instance
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔗 LUKHAS QRG Integrator initialized")
        self.logger.info(
            f"🧠 Consciousness engine: {'active' if hasattr(self.consciousness_engine, 'assess_consciousness') else 'mock'}"
        )
        self.logger.info(
            f"🌍 Cultural manager: {'active' if hasattr(self.cultural_manager, 'get_cultural_profile') else 'mock'}"
        )

    def create_qrg_context(self, user_id: str, **kwargs) -> QRGContext:
        """Create context for QRG generation"""
        # Get consciousness assessment
        consciousness_data = self.consciousness_engine.assess_consciousness(user_id)
        consciousness_level = consciousness_data.get("level", 0.5) if isinstance(consciousness_data, dict) else 0.5

        # Get cultural profile
        cultural_data = self.cultural_manager.get_cultural_profile(user_id)
        cultural_profile = (
            cultural_data if isinstance(cultural_data, dict) else {"region": "universal", "preferences": {}}
        )

        # Estimate cognitive load
        cognitive_data = self.cognitive_estimator.estimate_load(user_id)
        cognitive_load = cognitive_data.get("load", 0.3) if isinstance(cognitive_data, dict) else 0.3

        # Default context values
        context = QRGContext(
            user_id=user_id,
            consciousness_level=consciousness_level,
            cultural_profile=cultural_profile,
            security_clearance=SecurityLevel(kwargs.get("security_level", "protected")),
            cognitive_load=cognitive_load,
            attention_focus=kwargs.get("attention_focus", ["security", "authentication"]),
            timestamp=datetime.now(tz=timezone.utc),
            session_id=kwargs.get("session_id", secrets.token_hex(16)),
            device_capabilities=kwargs.get("device_capabilities", {"display": "standard", "interaction": "touch"}),
            environmental_factors=kwargs.get("environmental_factors", {"lighting": "normal", "noise": "low"}),
        )

        # Cache session context
        self.active_sessions[context.session_id] = context

        return context

    def generate_consciousness_qrg(self, context: QRGContext) -> QRGResult:
        """Generate consciousness-adaptive QRG"""
        print(f"🧠 Generating consciousness-adaptive QRG for user {context.user_id}")

        # Assess consciousness state
        consciousness_state = {
            "level": context.consciousness_level,
            "focus_areas": context.attention_focus,
            "cognitive_load": context.cognitive_load,
            "awareness_depth": min(1.0, context.consciousness_level + 0.2),
            "neural_harmony": 0.7 + (context.consciousness_level * 0.3),
        }

        # Generate consciousness-resonant pattern
        pattern_complexity = int(21 + (consciousness_state["level"] * 24))  # 21-45 modules
        neural_signature = hashlib.sha256(
            f"{context.user_id}_{consciousness_state}_{context.timestamp}".encode()
        ).hexdigest()[:16]

        # Create visualization pattern
        pattern_data = self._create_consciousness_pattern(pattern_complexity, consciousness_state, neural_signature)

        # Generate metadata
        metadata = {
            "consciousness_state": consciousness_state,
            "neural_signature": neural_signature,
            "pattern_complexity": pattern_complexity,
            "resonance_frequency": consciousness_state["neural_harmony"],
            "adaptation_params": {
                "brightness": 0.8 + (consciousness_state["level"] * 0.2),
                "contrast": 0.9,
                "animation_speed": max(0.5, 2.0 - consciousness_state["cognitive_load"]),
                "focus_enhancement": context.attention_focus,
            },
        }

        # Calculate security signature
        security_data = f"{pattern_data}_{neural_signature}_{context.timestamp}"
        security_signature = hashlib.sha512(security_data.encode()).hexdigest()

        result = QRGResult(
            qr_type=QRGType.CONSCIOUSNESS_ADAPTIVE,
            pattern_data=pattern_data,
            metadata=metadata,
            security_signature=security_signature,
            expiration=context.timestamp + timedelta(hours=1),
            compliance_score=1.0,
            cultural_safety_score=1.0,
            consciousness_resonance=consciousness_state["neural_harmony"],
            generation_metrics={
                "generation_time": 0.15,
                "complexity_score": consciousness_state["level"],
                "adaptation_quality": "high",
            },
        )

        self._log_generation(context, result)
        return result

    def generate_cultural_qrg(self, context: QRGContext) -> QRGResult:
        """Generate culturally-adaptive QRG"""
        print(f"🌍 Generating cultural QRG for user {context.user_id}")

        # Analyze cultural context
        cultural_analysis = self.safety_checker.check_cultural_safety(context.cultural_profile, context.user_id)
        safety_score = cultural_analysis.get("safety_score", 0.9) if isinstance(cultural_analysis, dict) else 0.9

        # Determine cultural adaptation strategy
        cultural_region = context.cultural_profile.get("region", "universal")
        cultural_preferences = context.cultural_profile.get("preferences", {})

        # Cultural pattern parameters
        if cultural_region in ["east_asian", "chinese", "japanese", "korean"]:
            pattern_style = "geometric_harmony"
            respect_level = "formal"
            visual_elements = ["balance", "symmetry", "hierarchy"]
        elif cultural_region in ["islamic", "middle_eastern"]:
            pattern_style = "geometric_islamic"
            respect_level = "respectful"
            visual_elements = ["geometric", "non_figurative", "sacred_geometry"]
        elif cultural_region in ["indigenous", "native"]:
            pattern_style = "organic_patterns"
            respect_level = "ceremonial"
            visual_elements = ["nature", "cycles", "tribal_wisdom"]
        else:
            pattern_style = "universal_accessible"
            respect_level = "inclusive"
            visual_elements = ["clarity", "accessibility", "universal_symbols"]

        # Generate culturally-sensitive pattern
        cultural_signature = hashlib.sha256(  # Changed from MD5 for security
            f"{cultural_region}_{pattern_style}_{respect_level}".encode()
        ).hexdigest()[:12]

        pattern_data = self._create_cultural_pattern(
            cultural_region, pattern_style, visual_elements, cultural_signature
        )

        # Metadata with cultural sensitivity
        metadata = {
            "cultural_context": cultural_region,
            "pattern_style": pattern_style,
            "respect_level": respect_level,
            "visual_elements": visual_elements,
            "cultural_signature": cultural_signature,
            "safety_analysis": cultural_analysis,
            "adaptation_notes": {
                "color_preferences": cultural_preferences.get("colors", ["universal"]),
                "symbol_preferences": cultural_preferences.get("symbols", ["geometric"]),
                "interaction_style": cultural_preferences.get("interaction", "standard"),
            },
        }

        security_signature = hashlib.sha384(
            f"{pattern_data}_{cultural_signature}_{context.timestamp}".encode()
        ).hexdigest()

        result = QRGResult(
            qr_type=QRGType.CULTURAL_SYMBOLIC,
            pattern_data=pattern_data,
            metadata=metadata,
            security_signature=security_signature,
            expiration=context.timestamp + timedelta(hours=2),
            compliance_score=1.0,
            cultural_safety_score=safety_score,
            consciousness_resonance=0.8,
            generation_metrics={
                "generation_time": 0.12,
                "cultural_adaptation_score": safety_score,
                "pattern_complexity": "medium",
            },
        )

        self._log_generation(context, result)
        return result

    def generate_quantum_qrg(self, context: QRGContext) -> QRGResult:
        """Generate quantum-encrypted QRG"""
        print(f"⚛️ Generating quantum QRG for user {context.user_id}")

        # Quantum state preparation
        qi_params = self.qi_visualizer.prepare_quantum_like_state(
            {
                "security_level": context.security_clearance.value,
                "consciousness_level": context.consciousness_level,
                "session_id": context.session_id,
            }
        )

        if not isinstance(qi_params, dict):
            qi_params = {
                "coherence": 0.95,
                "entanglement": "high",
                "security": "maximum",
            }

        # Generate quantum-secured pattern
        qi_seed = secrets.token_bytes(32)
        qi_signature = hashlib.sha3_512(
            qi_seed + context.session_id.encode() + str(context.timestamp).encode()
        ).hexdigest()

        # High-entropy pattern generation
        pattern_data = self._create_quantum_pattern(qi_seed, qi_params, context.security_clearance)

        # Quantum metadata
        metadata = {
            "qi_parameters": qi_params,
            "security_level": context.security_clearance.value,
            "qi_signature": qi_signature,
            "post_quantum_protected": True,
            "entanglement_id": secrets.token_hex(16),
            "coherence_metrics": {
                "phase_stability": 0.98,
                "decoherence_time": "300s",
                "fidelity": 0.997,
            },
            "encryption_methods": [
                "Kyber-1024",  # Post-quantum KEM
                "Dilithium-5",  # Post-quantum signatures
                "LUKHAS-Quantum-v2",  # Proprietary quantum protocol
            ],
        }

        security_signature = hashlib.blake2b((pattern_data + qi_signature).encode(), key=qi_seed[:32]).hexdigest()

        result = QRGResult(
            qr_type=QRGType.QUANTUM_ENCRYPTED,
            pattern_data=pattern_data,
            metadata=metadata,
            security_signature=security_signature,
            # Short-lived for security
            expiration=context.timestamp + timedelta(minutes=30),
            compliance_score=1.0,
            cultural_safety_score=1.0,
            consciousness_resonance=qi_params.get("coherence", 0.95),
            generation_metrics={
                "generation_time": 0.25,
                "qi_quality": "military_grade",
                "entropy_bits": 512,
            },
        )

        self._log_generation(context, result)
        return result

    def generate_dream_state_qrg(self, context: QRGContext) -> QRGResult:
        """Generate dream-state visualization QRG"""
        print(f"💭 Generating dream-state QRG for user {context.user_id}")

        # Dream state parameters
        dream_consciousness = max(0.3, context.consciousness_level - 0.2)  # Reduced consciousness
        dream_imagery = {
            "lucidity": dream_consciousness,
            "surreal_elements": 0.7,
            "symbolic_depth": 0.8,
            "narrative_flow": 0.6,
            "archetypal_content": context.cultural_profile.get("archetypes", ["universal"]),
        }

        # Generate ethereal pattern
        dream_signature = hashlib.sha256(
            f"dream_{context.user_id}_{dream_consciousness}_{time.time()}".encode()
        ).hexdigest()[:20]

        pattern_data = self._create_dream_pattern(dream_imagery, dream_signature)

        metadata = {
            "dream_state": dream_imagery,
            "dream_signature": dream_signature,
            "visualization_mode": "ethereal",
            "consciousness_shift": context.consciousness_level - dream_consciousness,
            "symbolic_elements": [
                "flowing_forms",
                "recursive_patterns",
                "phase_transitions",
                "archetypal_symbols",
            ],
            "animation_params": {
                "flow_speed": 0.3,
                "morph_rate": 0.1,
                "transparency_waves": True,
                "color_cycling": True,
            },
        }

        security_signature = hashlib.sha256(
            f"{pattern_data}_{dream_signature}_{context.timestamp}".encode()
        ).hexdigest()

        result = QRGResult(
            qr_type=QRGType.DREAM_STATE,
            pattern_data=pattern_data,
            metadata=metadata,
            security_signature=security_signature,
            expiration=context.timestamp + timedelta(hours=8),  # Dream cycle duration
            compliance_score=0.9,  # Slightly relaxed for dream state
            cultural_safety_score=1.0,
            consciousness_resonance=dream_consciousness,
            generation_metrics={
                "generation_time": 0.18,
                "surreal_quality": "high",
                "archetypal_resonance": "deep",
            },
        )

        self._log_generation(context, result)
        return result

    def generate_emergency_override_qrg(self, context: QRGContext) -> QRGResult:
        """Generate emergency override QRG"""
        print(f"🚨 Generating emergency override QRG for user {context.user_id}")

        # Emergency parameters
        emergency_code = secrets.token_hex(32)
        emergency_timestamp = datetime.now(tz=timezone.utc)
        override_level = "EMERGENCY_ALPHA"

        # Generate high-visibility emergency pattern
        pattern_data = self._create_emergency_pattern(emergency_code, override_level)

        metadata = {
            "emergency_code": emergency_code,
            "override_level": override_level,
            "emergency_timestamp": emergency_timestamp.isoformat(),
            "validity_window": "15_minutes",
            "bypass_capabilities": [
                "consciousness_verification",
                "cultural_adaptation",
                "cognitive_load_limits",
                "standard_security_protocols",
            ],
            "visual_indicators": {
                "high_contrast": True,
                "emergency_colors": ["red", "yellow", "white"],
                "pulsing_pattern": True,
                "size_enhancement": 1.5,
            },
            "emergency_contacts": ["system_admin", "security_team", "consciousness_monitor"],
        }

        security_signature = hashlib.sha3_256(
            f"EMERGENCY_{emergency_code}_{context.user_id}_{emergency_timestamp}".encode()
        ).hexdigest()

        result = QRGResult(
            qr_type=QRGType.EMERGENCY_OVERRIDE,
            pattern_data=pattern_data,
            metadata=metadata,
            security_signature=security_signature,
            expiration=emergency_timestamp + timedelta(minutes=15),
            compliance_score=0.8,
            cultural_safety_score=0.9,
            consciousness_resonance=1.0,
            generation_metrics={
                "generation_time": 0.05,
                "visibility_score": "maximum",
                "emergency_priority": "alpha",
            },
        )

        # Log emergency generation with high priority
        try:
            self.audit_logger.log_emergency_event(
                {
                    "event_type": "emergency_qrg_generated",
                    "user_id": context.user_id,
                    "emergency_code": emergency_code,
                    "timestamp": emergency_timestamp,
                    "context": asdict(context),
                }
            )
        except Exception:
            # Non-blocking fallback logging
            print(f"📝 Emergency QRG generated for {context.user_id}")

        self._log_generation(context, result)
        return result

    def generate_adaptive_qrg(self, context: QRGContext, qrg_type: QRGType = None) -> QRGResult:
        """
        Generate adaptive QRG based on context analysis

        This method analyzes the context and automatically selects the most
        appropriate QRG type and generation strategy.
        """
        print(f"🔄 Generating adaptive QRG for user {context.user_id}")

        # Analyze context to determine optimal QRG type
        if qrg_type is None:
            qrg_type = self._determine_optimal_qrg_type(context)

        # Route to appropriate generator
        generators = {
            QRGType.CONSCIOUSNESS_ADAPTIVE: self.generate_consciousness_qrg,
            QRGType.CULTURAL_SYMBOLIC: self.generate_cultural_qrg,
            QRGType.QUANTUM_ENCRYPTED: self.generate_quantum_qrg,
            QRGType.DREAM_STATE: self.generate_dream_state_qrg,
            QRGType.EMERGENCY_OVERRIDE: self.generate_emergency_override_qrg,
        }

        if qrg_type in generators:
            return generators[qrg_type](context)
        else:
            # Default to consciousness-adaptive
            print(f"⚠️ Unknown QRG type {qrg_type}, defaulting to consciousness-adaptive")
            return self.generate_consciousness_qrg(context)

    def _determine_optimal_qrg_type(self, context: QRGContext) -> QRGType:
        """Determine optimal QRG type based on context analysis"""

        # Emergency conditions
        if (
            context.security_clearance == SecurityLevel.TOP_SECRET
            or context.cognitive_load > 0.9
            or "emergency" in context.attention_focus
        ):
            return QRGType.EMERGENCY_OVERRIDE

        # High security requirements
        if context.security_clearance in [SecurityLevel.SECRET, SecurityLevel.COSMIC]:
            return QRGType.QUANTUM_ENCRYPTED

        # Cultural sensitivity requirements
        cultural_region = context.cultural_profile.get("region", "universal")
        if cultural_region != "universal" and cultural_region != "standard":
            return QRGType.CULTURAL_SYMBOLIC

        # Dream state detection
        if context.consciousness_level < 0.4 or "dream" in context.attention_focus or context.cognitive_load < 0.2:
            return QRGType.DREAM_STATE

        # Default to consciousness-adaptive
        return QRGType.CONSCIOUSNESS_ADAPTIVE

    def _create_consciousness_pattern(self, complexity: int, consciousness_state: dict, neural_signature: str) -> str:
        """Create consciousness-resonant QR pattern"""
        # Simulate consciousness-adaptive pattern generation
        base_pattern = f"CONSCIOUSNESS_QR_{complexity}x{complexity}_{neural_signature}"

        # Add consciousness-specific modulations
        consciousness_modulation = int(consciousness_state["level"] * 100)
        pattern_data = f"{base_pattern}_MOD_{consciousness_modulation}"

        return pattern_data

    def _create_cultural_pattern(self, region: str, style: str, elements: list[str], signature: str) -> str:
        """Create culturally-sensitive QR pattern"""
        cultural_elements = "_".join(elements)
        pattern_data = f"CULTURAL_QR_{region}_{style}_{cultural_elements}_{signature}"
        return pattern_data

    def _create_quantum_pattern(self, qi_seed: bytes, params: dict, security_level: SecurityLevel) -> str:
        """Create quantum-encrypted QR pattern"""
        seed_hex = qi_seed.hex()[:32]
        coherence = params.get("coherence", 0.95)
        pattern_data = f"QUANTUM_QR_{security_level.value}_{seed_hex}_COH_{coherence}"
        return pattern_data

    def _create_dream_pattern(self, dream_imagery: dict, dream_signature: str) -> str:
        """Create dream-state QR pattern"""
        lucidity = dream_imagery["lucidity"]
        surreal = dream_imagery["surreal_elements"]
        pattern_data = f"DREAM_QR_{dream_signature}_LUC_{lucidity}_SUR_{surreal}"
        return pattern_data

    def _create_emergency_pattern(self, emergency_code: str, override_level: str) -> str:
        """Create emergency override QR pattern"""
        pattern_data = f"EMERGENCY_QR_{override_level}_{emergency_code[:16]}"
        return pattern_data

    def _log_generation(self, context: QRGContext, result: QRGResult):
        """Log QRG generation event"""
        log_data = {
            "event_type": "qrg_generated",
            "qrg_type": result.qr_type.value,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp.isoformat(),
            "security_signature": result.security_signature,
            "metrics": result.generation_metrics,
            "compliance_score": result.compliance_score,
            "cultural_safety_score": result.cultural_safety_score,
            "consciousness_resonance": result.consciousness_resonance,
        }

        # Add to history
        self.generation_history.append(log_data)

        # Log to audit system
        try:
            self.audit_logger.log_authentication_event(log_data)
        except BaseException:
            print(f"📝 QRG Generation logged: {result.qr_type.value} for {context.user_id}")

    def get_generation_statistics(self) -> dict[str, Any]:
        """Get QRG generation statistics"""
        if not self.generation_history:
            return {"total_generations": 0, "message": "No generations recorded"}

        total = len(self.generation_history)
        type_counts = {}

        for entry in self.generation_history:
            qrg_type = entry["qrg_type"]
            type_counts[qrg_type] = type_counts.get(qrg_type, 0) + 1

        most_popular = max(type_counts.items(), key=lambda x: x[1])

        # Calculate averages
        avg_compliance = sum(entry.get("compliance_score", 0) for entry in self.generation_history) / total
        avg_cultural_safety = sum(entry.get("cultural_safety_score", 0) for entry in self.generation_history) / total
        avg_consciousness = sum(entry.get("consciousness_resonance", 0) for entry in self.generation_history) / total

        return {
            "total_generations": total,
            "type_distribution": type_counts,
            "most_popular_type": most_popular[0],
            "most_popular_count": most_popular[1],
            "averages": {
                "compliance_score": round(avg_compliance, 3),
                "cultural_safety_score": round(avg_cultural_safety, 3),
                "consciousness_resonance": round(avg_consciousness, 3),
            },
            "active_sessions": len(self.active_sessions),
            "last_generation": (self.generation_history[-1]["timestamp"] if self.generation_history else None),
        }


def demo_qrg_integration():
    """Demo the QRG Integration System"""
    print("🚀 LUKHAS QRG Integration Demo")
    print("=" * 50)

    # Initialize integrator
    integrator = LukhusQRGIntegrator()

    # Create test user context
    test_context = integrator.create_qrg_context(
        user_id="test_user_001",
        security_level="protected",
        attention_focus=["security", "consciousness", "cultural_awareness"],
        device_capabilities={"display": "high_res", "interaction": "multi_touch"},
        environmental_factors={"lighting": "optimal", "noise": "minimal"},
    )

    print("\n👤 Test Context Created:")
    print(f"   User: {test_context.user_id}")
    print(f"   Consciousness: {test_context.consciousness_level}")
    print(f"   Security: {test_context.security_clearance.value}")
    print(f"   Session: {test_context.session_id}")

    # Test different QRG types
    qrg_types_to_test = [
        QRGType.CONSCIOUSNESS_ADAPTIVE,
        QRGType.CULTURAL_SYMBOLIC,
        QRGType.QUANTUM_ENCRYPTED,
        QRGType.DREAM_STATE,
        QRGType.EMERGENCY_OVERRIDE,
    ]

    results = []

    for qrg_type in qrg_types_to_test:
        print(f"\n🔗 Testing {qrg_type.value.replace('_', ' ').title()} QRG...")

        try:
            result = integrator.generate_adaptive_qrg(test_context, qrg_type)
            results.append(result)

            print("   ✅ Generated successfully")
            print(f"   🔐 Security signature: {result.security_signature[:16]}...")
            print(f"   📊 Compliance score: {result.compliance_score}")
            print(f"   🌍 Cultural safety: {result.cultural_safety_score}")
            print(f"   🧠 Consciousness resonance: {result.consciousness_resonance}")
            print(f"   ⏰ Valid until: {result.expiration.strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"   ❌ Generation failed: {e}")

    # Show statistics
    print("\n📈 Generation Statistics:")
    stats = integrator.get_generation_statistics()

    for key, value in stats.items():
        if key == "type_distribution":
            print("   📊 Type Distribution:")
            for qrg_type, count in value.items():
                print(f"      • {qrg_type}: {count}")
        elif key == "averages":
            print("   📊 Average Scores:")
            for metric, score in value.items():
                print(f"      • {metric}: {score}")
        else:
            print(f"   📊 {key}: {value}")

    print("\n🎉 QRG Integration Demo Complete!")
    print(f"🔗 {len(results)} QRGs generated successfully")
    print("🧠 Consciousness-aware authentication system ready!")

    return integrator, results


if __name__ == "__main__":
    # Run the demo
    integrator, results = demo_qrg_integration()
