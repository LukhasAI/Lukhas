from pydantic import BaseModel, Field, HttpUrl, PositiveInt, NonNegativeInt, conint, constr
from typing import List, Optional, Dict, Any, Literal

# --- Nested Models for AGI Configuration ---

class CoreValues(BaseModel):
    beneficence: float
    non_maleficence: float
    autonomy: float
    justice: float
    transparency: float

class GoalAlignment(BaseModel):
    enabled: bool
    core_values: CoreValues

class ConsciousnessSettings(BaseModel):
    coherence_threshold: float
    awareness_update_hz: int
    reflection_depth: int
    stream_enabled: bool
    stream_port: int

class SelfImprovement(BaseModel):
    enabled: bool
    learning_rate: float
    improvement_cycle_minutes: int
    max_concurrent_goals: int

class AutonomousLearning(BaseModel):
    enabled: bool
    curiosity_level: float
    risk_tolerance: float
    knowledge_validation_threshold: float

class AgiSettings(BaseModel):
    self_improvement: SelfImprovement
    autonomous_learning: AutonomousLearning
    goal_alignment: GoalAlignment
    consciousness: ConsciousnessSettings

# --- Nested Models for Performance ---

class OptimizationSettings(BaseModel):
    jit_compilation: bool
    parallel_processing: bool
    gpu_acceleration: bool

class PerformanceSettings(BaseModel):
    max_workers: int
    batch_size: int
    cache_size_mb: int
    optimization: OptimizationSettings

# --- Nested Models for Memory ---

class EpisodicMemory(BaseModel):
    retention_days: int
    compression_enabled: bool

class FoldSystem(BaseModel):
    max_folds: int
    fold_threshold: float

class MemorySettings(BaseModel):
    storage_backend: str
    max_memory_gb: int
    episodic: EpisodicMemory
    fold_system: FoldSystem

# --- Nested Models for Security ---

class EncryptionSettings(BaseModel):
    algorithm: str
    key_rotation_days: int

class AuthenticationSettings(BaseModel):
    method: str
    token_expiry_hours: int

class RateLimitingSettings(BaseModel):
    requests_per_minute: int
    burst_size: int

class AuditSettings(BaseModel):
    enabled: bool
    retention_days: int

class SecuritySettings(BaseModel):
    encryption: EncryptionSettings
    authentication: AuthenticationSettings
    rate_limiting: RateLimitingSettings
    audit: AuditSettings

# --- Nested Models for Telemetry ---

class MetricsSettings(BaseModel):
    retention_hours: int
    aggregation_interval_seconds: int

class AlertsSettings(BaseModel):
    email_enabled: bool
    webhook_url: Optional[str] = None

class ExporterSettings(BaseModel):
    type: str
    endpoint: Optional[HttpUrl] = None
    region: Optional[str] = None

class TelemetrySettings(BaseModel):
    enabled: bool
    metrics: MetricsSettings
    alerts: AlertsSettings
    exporters: List[ExporterSettings]

# --- Nested Models for API ---

class CorsSettings(BaseModel):
    enabled: bool
    allowed_origins: List[str]

class ApiRateLimits(BaseModel):
    dream_generation: int
    memory_operations: int
    consciousness_queries: int

class ApiSettings(BaseModel):
    host: str
    port: int
    cors: CorsSettings
    rate_limits: ApiRateLimits

# --- Nested Models for Deployment ---

class ResourceSettings(BaseModel):
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str

class AutoscalingSettings(BaseModel):
    enabled: bool
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: int

class ProbeSettings(BaseModel):
    path: str
    interval_seconds: int

class HealthCheckSettings(BaseModel):
    liveness_probe: ProbeSettings
    readiness_probe: ProbeSettings

class DeploymentSettings(BaseModel):
    replicas: int
    resources: ResourceSettings
    autoscaling: AutoscalingSettings
    health_checks: HealthCheckSettings

# --- Nested Models for Logging ---

class LogOutput(BaseModel):
    type: Literal['stdout', 'file']
    path: Optional[str] = None
    rotation: Optional[str] = None
    retention_days: Optional[int] = None

class LoggingSettings(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    format: Literal['json', 'text']
    outputs: List[LogOutput]

# --- Nested Models for Database ---

class DbConnection(BaseModel):
    host: str
    port: int
    database: str
    ssl_mode: str

class DbPool(BaseModel):
    min_connections: int
    max_connections: int

class DatabaseSettings(BaseModel):
    type: str
    connection: DbConnection
    pool: DbPool

# --- Nested Models for Cache ---

class CacheSettings(BaseModel):
    type: str
    nodes: List[str]
    options: Dict[str, Any]

# --- Nested Models for Queue ---

class QueueSettings(BaseModel):
    type: str
    brokers: List[str]
    topics: Dict[str, str]

# --- Top-Level Settings Model ---

class SystemSettings(BaseModel):
    name: str
    version: str
    environment: str

class FeatureFlags(BaseModel):
    personality_enhancement: bool
    quantum_processing: bool
    adversarial_learning: bool
    emergent_behavior_detection: bool


class LukhasSettings(BaseModel):
    """The main settings model for the entire application."""
    system: SystemSettings
    agi: AgiSettings
    performance: PerformanceSettings
    memory: MemorySettings
    security: SecuritySettings
    telemetry: TelemetrySettings
    api: ApiSettings
    deployment: DeploymentSettings
    features: FeatureFlags
    logging: LoggingSettings
    database: DatabaseSettings
    cache: CacheSettings
    queue: QueueSettings


def validate_settings(config: Dict[str, Any]) -> LukhasSettings:
    """
    Validates a dictionary of settings against the LukhasSettings model.

    Args:
        config: A dictionary containing the application settings.

    Returns:
        A validated LukhasSettings object.

    Raises:
        pydantic.ValidationError: If the configuration is invalid.
    """
    return LukhasSettings.model_validate(config)
