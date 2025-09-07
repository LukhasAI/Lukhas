"""
Lukhas Plugin SDK - Type Definitions

This module contains all the data structures, enums, and type definitions
used throughout the Lukhas Plugin SDK system.

Author: Lukhas AI System
Version: 1.0.0
License: Proprietary
"""
import streamlit as st
from datetime import timezone

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ==================== PLUGIN ENUMS ====================


class PluginType(Enum, timezone):
    """Plugin category types"""

    ETHICS_GUARDIAN = "ethics_guardian"
    MEMORY_COGNITION = "memory_cognition"
    VOICE_SYSTEM = "voice_system"
    CONSENT_IDENTITY = "consent_identity"
    REASONING_SYSTEM = "reasoning_system"
    UI_VISUALIZATION = "ui_visualization"
    bio_symbolic = "bio_symbolic"
    UTILITY = "utility"
    AI_MODEL = "ai_model"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"


class PluginTier(Enum):
    """Plugin pricing/access tiers"""

    BASIC = "basic"
    PRO = "pro"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    INSTITUTIONAL = "institutional"


class PluginState(Enum):
    """Plugin lifecycle states"""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class PluginStatus(Enum):
    """Plugin status states (alias for PluginState for compatibility)"""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class ConsciousnessState(Enum):
    """Lukhas consciousness states that plugins can interact with"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    DREAMING = "dreaming"
    PROCESSING = "processing"
    LEARNING = "learning"
    REFLECTION = "reflection"


class ComplianceLevel(Enum):
    """Regulatory compliance levels"""

    BASIC = "basic"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SEEDRA_V3 = "seedra_v3"
    ENTERPRISE = "enterprise"
    INSTITUTIONAL = "institutional"


# ==================== PLUGIN DATA STRUCTURES ====================


@dataclass
class SymbolicMetadata:
    """Symbolic consciousness metadata for plugin integration"""

    dream_tag: Optional[str] = None
    memory_vector: Optional[list[float]] = None
    ethics_class: Optional[str] = None
    consciousness_signature: Optional[str] = None
    symbolic_weight: float = 1.0
    emotional_resonance: Optional[dict[str, float]] = None
    # Additional attributes required by validators
    consciousness_integration: bool = True
    consciousness_aware: bool = True
    symbolic_resonance: Optional[float] = None
    symbolic_patterns: Optional[list[str]] = None

    def __post_init__(self):
        if self.emotional_resonance is None:
            self.emotional_resonance = {}
        if self.symbolic_patterns is None:
            self.symbolic_patterns = []


@dataclass
class PluginCapabilities:
    """Plugin capabilities and features"""

    features: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    lukhas_modules: list[str] = field(default_factory=list)
    symbolic_integration: bool = True
    consciousness_aware: bool = True
    memory_access: bool = False
    real_time: bool = False

    def __post_init__(self):
        if not self.features:
            self.features = []
        if not self.permissions:
            self.permissions = []
        if not self.lukhas_modules:
            self.lukhas_modules = []


@dataclass
class PluginPricing:
    """Plugin pricing and commercial information"""

    tier: PluginTier
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    free_tier_limits: Optional[dict[str, Any]] = None
    enterprise_features: Optional[list[str]] = None
    revenue_share: float = 0.7  # Developer gets 70% by default

    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {}
        if self.enterprise_features is None:
            self.enterprise_features = []


@dataclass
class PluginDependencies:
    """Plugin dependency requirements"""

    lukhas_compatibility: str  # Semver range like ">=1.0.0,<2.0.0"
    python_version: str = ">=3.9"
    system_requirements: Optional[dict[str, str]] = None
    external_services: Optional[list[str]] = None
    other_plugins: Optional[list[str]] = None

    def __post_init__(self):
        if self.system_requirements is None:
            self.system_requirements = {}
        if self.external_services is None:
            self.external_services = []
        if self.other_plugins is None:
            self.other_plugins = []


@dataclass
class PluginSecurity:
    """Plugin security and compliance information"""

    code_signed: bool = False
    sandbox_required: bool = True
    level: str = "medium"  # "low", "medium", "high"
    network_access: bool = False
    file_system_access: bool = False
    compliance_standards: list[str] = field(default_factory=list)
    security_audit_date: Optional[str] = None
    vulnerability_scan_passed: bool = False
    network_access: bool = False
    file_system_access: bool = False
    compliance_standards: list[str] = field(default_factory=list)
    security_audit_date: Optional[str] = None
    vulnerability_scan_passed: bool = False

    def __post_init__(self):
        if not self.compliance_standards:
            self.compliance_standards = []


@dataclass
class PluginManifest:
    """Complete plugin manifest structure"""

    # Required fields
    name: str
    type: PluginType
    version: str
    description: str

    # Core information
    author: str = "Unknown"
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: str = "Proprietary"

    # Lukhas integration
    dependencies: Optional[PluginDependencies] = None
    capabilities: Optional[PluginCapabilities] = None
    symbolic_metadata: Optional[SymbolicMetadata] = None

    # Commercial
    pricing: Optional[PluginPricing] = None

    # Security & Compliance
    security: Optional[PluginSecurity] = None
    compliance: Optional[list[str]] = None

    # Plugin files
    entry_point: str = "main.py"
    assets_dir: Optional[str] = "assets"
    docs_dir: Optional[str] = "docs"
    tests_dir: Optional[str] = "tests"

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        # Convert string type to enum if needed
        if isinstance(self.type, str):
            self.type = PluginType(self.type)

        # Initialize default objects
        if self.dependencies is None:
            self.dependencies = PluginDependencies(lukhas_compatibility=">=1.0.0")
        if self.capabilities is None:
            self.capabilities = PluginCapabilities()
        if self.symbolic_metadata is None:
            self.symbolic_metadata = SymbolicMetadata()
        if self.pricing is None:
            self.pricing = PluginPricing(tier=PluginTier.BASIC)
        if self.security is None:
            self.security = PluginSecurity()
        if self.compliance is None:
            self.compliance = []

        # Set timestamps
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc).isoformat()


# ==================== EXECUTION CONTEXT ====================


@dataclass
class LucasSystemState:
    """Current state of the Lukhas AI system"""

    consciousness_state: ConsciousnessState
    memory_usage: float  # Percentage
    active_dreams: int
    symbolic_coherence: float  # 0.0 to 1.0
    emotional_state: dict[str, float]
    reasoning_mode: str
    last_decision: Optional[str] = None

    def __post_init__(self):
        if not self.emotional_state:
            self.emotional_state = {}


@dataclass
class UserSession:
    """User session information"""

    user_id: Optional[str]
    session_id: str
    tier: PluginTier
    compliance_level: ComplianceLevel
    permissions: list[str]
    preferences: dict[str, Any]
    start_time: datetime

    def __post_init__(self):
        if not self.permissions:
            self.permissions = []
        if not self.preferences:
            self.preferences = {}


@dataclass
class PluginContext:
    """Context for plugin execution within Lukhas system"""

    lukhas_state: LucasSystemState
    user_session: UserSession
    plugin_config: dict[str, Any]
    environment: str = "production"  # "production", "staging", "development"
    debug_mode: bool = False
    trace_enabled: bool = True
    lukhas_system_state: Optional[LucasSystemState] = None
    plugin_directory: Optional[Path] = None
    symbolic_enabled: bool = True
    consciousness_state: ConsciousnessState = ConsciousnessState.ACTIVE

    def __post_init__(self):
        if not self.plugin_config:
            self.plugin_config = {}
        if self.lukhas_system_state is None:
            self.lukhas_system_state = self.lukhas_state


@dataclass
class PluginExecutionContext:
    """Complete context for plugin execution"""

    lukhas_state: LucasSystemState
    user_session: UserSession
    plugin_config: dict[str, Any]
    environment: str = "production"  # "production", "staging", "development"
    debug_mode: bool = False
    trace_enabled: bool = True

    def __post_init__(self):
        if not self.plugin_config:
            self.plugin_config = {}


# ==================== VALIDATION SCHEMAS ====================


@dataclass
class ValidationRule:
    """Plugin validation rule definition"""

    name: str
    description: str
    rule_type: str  # "required", "format", "range", "custom"
    validator: Optional[str] = None  # Function name for custom validators
    error_message: Optional[str] = None


@dataclass
class PluginValidationSchema:
    """Schema for validating plugin manifests and behavior"""

    version: str = "1.0.0"
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    validation_rules: list[ValidationRule] = field(default_factory=list)
    compliance_checks: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.required_fields:
            self.required_fields = [
                "name",
                "type",
                "version",
                "description",
                "dependencies.lukhas_compatibility",
            ]
        if not self.compliance_checks:
            self.compliance_checks = ["GDPR", "SEEDRA-v3"]


# ==================== ERROR TYPES ====================


class PluginError(Exception):
    """Base exception for plugin-related errors"""

    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(message)
        self.plugin_name = plugin_name
        self.error_code = error_code


class PluginLoadError(PluginError):
    """Error during plugin loading"""


class PluginValidationError(PluginError):
    """Error during plugin validation"""


class PluginExecutionError(PluginError):
    """Error during plugin execution"""


class PluginComplianceError(PluginError):
    """Error related to compliance violations"""


# ==================== SYMBOLIC TRACE TYPES ====================


@dataclass
class SymbolicTrace:
    """Symbolic execution trace for plugin monitoring"""

    plugin_id: str
    execution_id: str
    timestamp: datetime
    consciousness_impact: Optional[dict[str, Any]] = None
    memory_operations: Optional[list[dict[str, Any]]] = None
    dream_interactions: Optional[list[dict[str, Any]]] = None
    ethical_decisions: Optional[list[dict[str, Any]]] = None
    symbolic_signatures: Optional[list[str]] = None

    def __post_init__(self):
        if self.memory_operations is None:
            self.memory_operations = []
        if self.dream_interactions is None:
            self.dream_interactions = []
        if self.ethical_decisions is None:
            self.ethical_decisions = []
        if self.symbolic_signatures is None:
            self.symbolic_signatures = []


@dataclass
class ConsciousnessMapping:
    """Mapping between consciousness states and plugin parameters"""

    state: ConsciousnessState
    parameter_adjustments: dict[str, float]
    activation_threshold: float = 0.5
    response_delay_ms: int = 100
    priority_boost: float = 1.0

    def __post_init__(self):
        if not self.parameter_adjustments:
            self.parameter_adjustments = {}


# ==================== PLUGIN COMMUNICATION ====================


@dataclass
class PluginMessage:
    """Message format for inter-plugin communication"""

    sender_plugin_id: str
    recipient_plugin_id: Optional[str]  # None for broadcast
    message_type: str
    payload: dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 5=high
    requires_response: bool = False
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if not self.payload:
            self.payload = {}
        if self.correlation_id is None:
            import uuid

            self.correlation_id = str(uuid.uuid4())


@dataclass
class PluginResponse:
    """Response format for plugin message responses"""

    correlation_id: str
    sender_plugin_id: str
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.data is None:
            self.data = {}


# ==================== PLUGIN BASE CLASSES ====================


class BaseLucasPlugin(ABC):
    """Base class for all Lukhas plugins"""

    def __init__(self, context: "PluginContext"):
        self.context = context
        self._loaded = False
        self.plugin_id = f"plugin_{id(self)}"  # Generate unique ID

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute plugin main functionality"""

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up plugin resources"""

    async def load(self, context: "PluginContext") -> None:
        """Load the plugin with given context"""
        self.context = context
        await self.initialize()
        self._loaded = True

    async def terminate(self) -> None:
        """Terminate the plugin"""
        await self.cleanup()
        self._loaded = False

    async def map_consciousness_state(self) -> dict[str, Any]:
        """Map current consciousness state to plugin parameters"""
        return {
            "consciousness_state": self.context.lukhas_state.consciousness_state.value,
            "symbolic_coherence": self.context.lukhas_state.symbolic_coherence,
            "emotional_state": self.context.lukhas_state.emotional_state,
        }

    def get_status(self) -> dict[str, Any]:
        """Get plugin status information"""
        return {"loaded": self._loaded, "plugin_type": self.__class__.__name__}


@dataclass
class LoadedPlugin:
    """Represents a loaded plugin instance"""

    plugin_id: str
    instance: Optional[BaseLucasPlugin]
    manifest: Optional[PluginManifest]
    context: Optional[PluginContext]
    load_time: datetime = field(default_factory=datetime.now)
    state: PluginState = PluginState.LOADED
    file_path: Optional[Path] = None
    file_hash: str = ""
    error: Optional[str] = None
    symbolic_state: dict[str, Any] = field(default_factory=dict)
    consciousness_mapping: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not hasattr(self, "load_time"):
            self.load_time = datetime.now(timezone.utc)
