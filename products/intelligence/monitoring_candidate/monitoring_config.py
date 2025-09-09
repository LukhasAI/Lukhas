#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Monitoring Configuration
========================
Extended configuration system that includes endocrine parameters and
biological-inspired monitoring settings for the enhanced LUKHAS system.
"""

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog
import yaml

logger = structlog.get_logger(__name__)


class MonitoringProfile(Enum):
    """Pre-defined monitoring profiles"""

    DEVELOPMENT = "development"  # Development environment settings
    TESTING = "testing"  # Testing environment settings
    PRODUCTION = "production"  # Production environment settings
    RESEARCH = "research"  # Research and experimentation
    DEMONSTRATION = "demonstration"  # Demo and presentation mode


@dataclass
class EndocrineMonitoringConfig:
    """Configuration for endocrine system monitoring"""

    # Monitoring intervals
    hormone_sampling_interval: float = 5.0  # seconds
    homeostasis_check_interval: float = 3.0
    coherence_calculation_interval: float = 10.0

    # Hormone thresholds for plasticity triggers
    hormone_thresholds: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            "cortisol": {
                "low": 0.2,
                "normal_min": 0.3,
                "normal_max": 0.6,
                "high": 0.75,
                "critical": 0.9,
            },
            "dopamine": {
                "low": 0.25,
                "normal_min": 0.4,
                "normal_max": 0.7,
                "high": 0.8,
                "critical": 0.95,
            },
            "serotonin": {
                "low": 0.3,
                "normal_min": 0.4,
                "normal_max": 0.7,
                "high": 0.8,
                "critical": 0.9,
            },
            "oxytocin": {
                "low": 0.2,
                "normal_min": 0.3,
                "normal_max": 0.6,
                "high": 0.75,
                "critical": 0.85,
            },
            "adrenaline": {
                "low": 0.1,
                "normal_min": 0.2,
                "normal_max": 0.5,
                "high": 0.7,
                "critical": 0.9,
            },
            "melatonin": {
                "low": 0.1,
                "normal_min": 0.2,
                "normal_max": 0.6,
                "high": 0.8,
                "critical": 0.95,
            },
            "gaba": {
                "low": 0.3,
                "normal_min": 0.4,
                "normal_max": 0.7,
                "high": 0.8,
                "critical": 0.9,
            },
            "endorphin": {
                "low": 0.2,
                "normal_min": 0.3,
                "normal_max": 0.6,
                "high": 0.75,
                "critical": 0.85,
            },
        }
    )

    # Plasticity trigger sensitivity
    plasticity_sensitivity: float = 0.8  # 0.0 = low sensitivity, 1.0 = high sensitivity
    adaptation_cooldown_minutes: int = 15
    max_concurrent_adaptations: int = 3

    # Bio-symbolic coherence parameters
    coherence_weight_biological: float = 0.6
    coherence_weight_symbolic: float = 0.4
    coherence_stability_threshold: float = 0.7
    coherence_alert_threshold: float = 0.5

    # Data retention
    snapshot_retention_hours: int = 48
    event_retention_hours: int = 72
    trend_retention_hours: int = 168  # 1 week


@dataclass
class MetricsCollectionConfig:
    """Configuration for adaptive metrics collection"""

    # Collection intervals by context
    collection_intervals: dict[str, float] = field(
        default_factory=lambda: {
            "normal_operation": 5.0,
            "high_stress": 1.0,
            "learning_mode": 2.0,
            "social_interaction": 3.0,
            "recovery_phase": 10.0,
            "creative_mode": 4.0,
            "problem_solving": 1.5,
            "adaptation_active": 2.0,
        }
    )

    # Metrics configuration
    metrics_retention_limit: int = 1000
    anomaly_detection_window: int = 50
    anomaly_sensitivity: float = 2.0  # Standard deviations
    correlation_calculation_interval: float = 30.0

    # Context detection parameters
    context_stability_threshold: float = 0.7
    context_change_sensitivity: float = 0.3

    # Quality assurance
    data_quality_threshold: float = 0.8
    metric_validation_enabled: bool = True
    outlier_detection_enabled: bool = True


@dataclass
class PlasticityConfig:
    """Configuration for plasticity trigger management"""

    # Adaptation strategies
    default_strategy: str = "gradual"
    strategy_selection_mode: str = "adaptive"  # "fixed", "adaptive", "learned"

    # Risk management
    risk_tolerance: float = 0.3
    safety_threshold: float = 0.8
    max_system_impact: float = 0.25
    validation_period_minutes: int = 15

    # Learning parameters
    adaptation_success_weight: float = 0.7
    historical_success_weight: float = 0.3
    pattern_learning_enabled: bool = True

    # Triggers configuration
    trigger_priorities: dict[str, int] = field(
        default_factory=lambda: {
            "stress_adaptation": 5,
            "performance_optimization": 4,
            "emotional_regulation": 4,
            "social_enhancement": 3,
            "recovery_consolidation": 3,
            "creative_boost": 2,
            "resilience_building": 4,
            "efficiency_tuning": 3,
        }
    )

    # Cooldown periods (minutes)
    trigger_cooldowns: dict[str, int] = field(
        default_factory=lambda: {
            "stress_adaptation": 10,
            "performance_optimization": 30,
            "emotional_regulation": 20,
            "social_enhancement": 60,
            "recovery_consolidation": 120,
            "creative_boost": 45,
            "resilience_building": 180,
            "efficiency_tuning": 40,
        }
    )


@dataclass
class DashboardConfig:
    """Configuration for hormone-driven dashboard"""

    # Display settings
    auto_adapt_mode: bool = True
    default_mode: str = "overview"
    refresh_interval: float = 1.0

    # Widget configuration
    widget_update_intervals: dict[str, float] = field(
        default_factory=lambda: {
            "hormone_radar": 2.0,
            "coherence_gauge": 3.0,
            "performance_trends": 5.0,
            "adaptation_timeline": 10.0,
            "predictions": 15.0,
            "alerts": 1.0,
        }
    )

    # Alert settings
    alert_severity_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "info": 0.1,
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95,
        }
    )

    alert_auto_resolve_timeout_minutes: int = 30
    max_active_alerts: int = 20

    # Prediction settings
    prediction_horizons: dict[str, int] = field(
        default_factory=lambda: {
            "short_term": 5,  # minutes
            "medium_term": 30,  # minutes
            "long_term": 120,  # minutes
        }
    )

    prediction_confidence_threshold: float = 0.6


@dataclass
class LearningConfig:
    """Configuration for neuroplastic learning orchestrator"""

    # Learning parameters
    learning_rate: float = 0.1
    meta_learning_enabled: bool = True
    transfer_learning_enabled: bool = True

    # Experimentation
    max_concurrent_experiments: int = 3
    experiment_safety_threshold: float = 0.8
    minimum_experiment_duration_minutes: int = 10
    maximum_experiment_duration_minutes: int = 60

    # Knowledge management
    insight_confidence_threshold: float = 0.7
    pattern_significance_threshold: float = 0.6
    knowledge_retention_limit: int = 1000

    # Learning goals
    default_learning_goals: list[str] = field(
        default_factory=lambda: [
            "performance_optimization",
            "stress_adaptation",
            "coherence_maintenance",
            "learning_efficiency",
        ]
    )

    # Phase transition parameters
    observation_duration_minutes: int = 30
    exploration_success_threshold: float = 0.6
    consolidation_trigger_threshold: float = 0.8


@dataclass
class IntegrationConfig:
    """Configuration for system integration"""

    # Signal bus settings
    signal_buffer_size: int = 5000
    signal_processing_interval: float = 0.1
    signal_persistence_enabled: bool = True

    # Cross-component coordination
    coordination_interval: float = 15.0
    correlation_update_interval: float = 60.0
    insight_generation_interval: float = 120.0

    # Health monitoring
    health_check_interval: float = 30.0
    performance_baseline_update_interval: float = 300.0
    system_optimization_interval: float = 600.0

    # Data persistence
    auto_save_interval_minutes: int = 10
    backup_retention_days: int = 30
    data_compression_enabled: bool = True


@dataclass
class ComprehensiveMonitoringConfig:
    """Complete configuration for the enhanced monitoring system"""

    # Profile and environment
    profile: MonitoringProfile = MonitoringProfile.DEVELOPMENT
    environment_name: str = "lukhas"
    config_version: str = "1.0.0"

    # Component configurations
    endocrine: EndocrineMonitoringConfig = field(default_factory=EndocrineMonitoringConfig)
    metrics: MetricsCollectionConfig = field(default_factory=MetricsCollectionConfig)
    plasticity: PlasticityConfig = field(default_factory=PlasticityConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)

    # Global settings
    debug_mode: bool = False
    log_level: str = "INFO"
    data_directory: str = "data/monitoring"

    # Feature flags
    features: dict[str, bool] = field(
        default_factory=lambda: {
            "endocrine_monitoring": True,
            "plasticity_adaptation": True,
            "bio_symbolic_coherence": True,
            "adaptive_metrics": True,
            "predictive_dashboard": True,
            "neuroplastic_learning": True,
            "cross_component_integration": True,
            "auto_optimization": True,
            "experimental_features": False,
        }
    )

    # Security and safety
    security: dict[str, Any] = field(
        default_factory=lambda: {
            "max_adaptation_impact": 0.3,
            "require_validation": True,
            "enable_rollback": True,
            "audit_logging": True,
            "encrypt_sensitive_data": False,
        }
    )


class MonitoringConfigManager:
    """Manager for monitoring system configuration"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/monitoring.yaml")
        self.config: Optional[ComprehensiveMonitoringConfig] = None
        self.profile_configs: dict[MonitoringProfile, dict[str, Any]] = {}

        # Initialize profile-specific configurations
        self._initialize_profile_configs()

    def _initialize_profile_configs(self):
        """Initialize configurations for different profiles"""

        # Development profile - verbose monitoring, low thresholds
        self.profile_configs[MonitoringProfile.DEVELOPMENT] = {
            "debug_mode": True,
            "log_level": "DEBUG",
            "endocrine": {
                "hormone_sampling_interval": 2.0,
                "plasticity_sensitivity": 0.6,
            },
            "metrics": {
                "collection_intervals": {k: v * 0.5 for k, v in MetricsCollectionConfig().collection_intervals.items()},
                "anomaly_sensitivity": 1.5,
            },
            "features": {"experimental_features": True},
        }

        # Testing profile - controlled monitoring, moderate sensitivity
        self.profile_configs[MonitoringProfile.TESTING] = {
            "debug_mode": False,
            "log_level": "INFO",
            "endocrine": {
                "plasticity_sensitivity": 0.7,
                "adaptation_cooldown_minutes": 5,
            },
            "plasticity": {"risk_tolerance": 0.5, "validation_period_minutes": 5},
            "features": {"auto_optimization": False},
        }

        # Production profile - stable monitoring, conservative settings
        self.profile_configs[MonitoringProfile.PRODUCTION] = {
            "debug_mode": False,
            "log_level": "WARNING",
            "endocrine": {
                "plasticity_sensitivity": 0.9,
                "adaptation_cooldown_minutes": 30,
            },
            "plasticity": {
                "risk_tolerance": 0.2,
                "safety_threshold": 0.9,
                "validation_period_minutes": 30,
            },
            "learning": {
                "experiment_safety_threshold": 0.9,
                "max_concurrent_experiments": 1,
            },
            "security": {
                "max_adaptation_impact": 0.2,
                "require_validation": True,
                "audit_logging": True,
            },
        }

        # Research profile - experimental monitoring, high adaptability
        self.profile_configs[MonitoringProfile.RESEARCH] = {
            "debug_mode": True,
            "log_level": "DEBUG",
            "endocrine": {
                "plasticity_sensitivity": 0.5,
                "max_concurrent_adaptations": 5,
            },
            "learning": {
                "learning_rate": 0.2,
                "max_concurrent_experiments": 5,
                "experiment_safety_threshold": 0.7,
            },
            "features": {"experimental_features": True, "neuroplastic_learning": True},
        }

        # Demonstration profile - visual monitoring, stable operation
        self.profile_configs[MonitoringProfile.DEMONSTRATION] = {
            "debug_mode": False,
            "log_level": "INFO",
            "dashboard": {
                "refresh_interval": 0.5,
                "widget_update_intervals": {k: v * 0.5 for k, v in DashboardConfig().widget_update_intervals.items()},
            },
            "endocrine": {"hormone_sampling_interval": 1.0},
            "plasticity": {"risk_tolerance": 0.4},
        }

    def load_config(self, profile: Optional[MonitoringProfile] = None) -> ComprehensiveMonitoringConfig:
        """Load configuration from file or create default"""

        # Start with default configuration
        config = ComprehensiveMonitoringConfig()

        # Apply profile-specific overrides
        if profile:
            config.profile = profile
            profile_overrides = self.profile_configs.get(profile, {})
            config = self._apply_overrides(config, profile_overrides)

        # Load from file if it exists
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    file_config = yaml.safe_load(f) if self.config_path.suffix.lower() == ".yaml" else json.load(f)

                config = self._apply_overrides(config, file_config)
                logger.info("Loaded monitoring configuration", config_path=str(self.config_path))

            except Exception as e:
                logger.error("Failed to load configuration file", error=str(e))
                logger.info("Using default configuration")

        self.config = config
        return config

    def save_config(self, config: Optional[ComprehensiveMonitoringConfig] = None):
        """Save configuration to file"""

        if config is None:
            config = self.config

        if config is None:
            logger.error("No configuration to save")
            return

        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dictionary
            config_dict = asdict(config)

            # Save to file
            with open(self.config_path, "w") as f:
                if self.config_path.suffix.lower() == ".yaml":
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, default=str)

            logger.info("Saved monitoring configuration", config_path=str(self.config_path))

        except Exception as e:
            logger.error("Failed to save configuration", error=str(e))

    def _apply_overrides(
        self, config: ComprehensiveMonitoringConfig, overrides: dict[str, Any]
    ) -> ComprehensiveMonitoringConfig:
        """Apply configuration overrides"""

        for key, value in overrides.items():
            if hasattr(config, key):
                current_value = getattr(config, key)

                if isinstance(current_value, dict) and isinstance(value, dict):
                    # Merge dictionaries
                    merged = {**current_value, **value}
                    setattr(config, key, merged)
                elif hasattr(current_value, "__dict__") and isinstance(value, dict):
                    # Update dataclass fields
                    for sub_key, sub_value in value.items():
                        if hasattr(current_value, sub_key):
                            setattr(current_value, sub_key, sub_value)
                else:
                    # Direct assignment
                    setattr(config, key, value)

        return config

    def get_component_config(self, component_name: str) -> dict[str, Any]:
        """Get configuration for a specific component"""

        if not self.config:
            raise ValueError("Configuration not loaded")

        component_configs = {
            "endocrine": asdict(self.config.endocrine),
            "metrics": asdict(self.config.metrics),
            "plasticity": asdict(self.config.plasticity),
            "dashboard": asdict(self.config.dashboard),
            "learning": asdict(self.config.learning),
            "integration": asdict(self.config.integration),
        }

        if component_name not in component_configs:
            raise ValueError(f"Unknown component: {component_name}")

        return component_configs[component_name]

    def validate_config(self, config: Optional[ComprehensiveMonitoringConfig] = None) -> list[str]:
        """Validate configuration and return list of issues"""

        if config is None:
            config = self.config

        if config is None:
            return ["No configuration to validate"]

        issues = []

        # Validate endocrine configuration
        if config.endocrine.hormone_sampling_interval <= 0:
            issues.append("Hormone sampling interval must be positive")

        if not (0.0 <= config.endocrine.plasticity_sensitivity <= 1.0):
            issues.append("Plasticity sensitivity must be between 0.0 and 1.0")

        # Validate metrics configuration
        for context, interval in config.metrics.collection_intervals.items():
            if interval <= 0:
                issues.append(f"Collection interval for {context} must be positive")

        # Validate plasticity configuration
        if not (0.0 <= config.plasticity.risk_tolerance <= 1.0):
            issues.append("Risk tolerance must be between 0.0 and 1.0")

        if config.plasticity.max_concurrent_adaptations <= 0:
            issues.append("Maximum concurrent adaptations must be positive")

        # Validate learning configuration
        if not (0.0 <= config.learning.learning_rate <= 1.0):
            issues.append("Learning rate must be between 0.0 and 1.0")

        # Validate thresholds
        for hormone, thresholds in config.endocrine.hormone_thresholds.items():
            if not (
                thresholds["low"]
                < thresholds["normal_min"]
                < thresholds["normal_max"]
                < thresholds["high"]
                < thresholds["critical"]
            ):
                issues.append(f"Hormone thresholds for {hormone} are not properly ordered")

        return issues

    def create_profile_config(self, profile: MonitoringProfile) -> ComprehensiveMonitoringConfig:
        """Create configuration for a specific profile"""

        config = ComprehensiveMonitoringConfig()
        config.profile = profile

        profile_overrides = self.profile_configs.get(profile, {})
        config = self._apply_overrides(config, profile_overrides)

        return config


# Backward/compatibility alias expected by some tests

MonitoringConfig = ComprehensiveMonitoringConfig


def create_default_monitoring_config() -> ComprehensiveMonitoringConfig:
    """Create default monitoring configuration"""
    return ComprehensiveMonitoringConfig()


def load_monitoring_config(
    config_path: Optional[str] = None, profile: Optional[MonitoringProfile] = None
) -> ComprehensiveMonitoringConfig:
    """Load monitoring configuration with optional profile"""

    manager = MonitoringConfigManager(config_path)
    return manager.load_config(profile)


def save_monitoring_config(config: ComprehensiveMonitoringConfig, config_path: Optional[str] = None):
    """Save monitoring configuration to file"""

    manager = MonitoringConfigManager(config_path)
    manager.save_config(config)


def validate_monitoring_config(config: ComprehensiveMonitoringConfig) -> list[str]:
    """Validate monitoring configuration"""

    manager = MonitoringConfigManager()
    return manager.validate_config(config)


# Example usage and configuration templates
def create_example_configs():
    """Create example configuration files for different profiles"""

    config_dir = Path("config/examples")
    config_dir.mkdir(parents=True, exist_ok=True)

    manager = MonitoringConfigManager()

    for profile in MonitoringProfile:
        config = manager.create_profile_config(profile)

        example_path = config_dir / f"monitoring_{profile.value}.yaml"
        example_manager = MonitoringConfigManager(str(example_path))
        example_manager.save_config(config)

        logger.info(
            "Created example configuration",
            profile=profile.value,
            path=str(example_path),
        )


if __name__ == "__main__":
    # Create example configurations
    create_example_configs()

    # Test configuration loading and validation
    config = load_monitoring_config(profile=MonitoringProfile.DEVELOPMENT)
    issues = validate_monitoring_config(config)

    if issues:
        logger.warning("Configuration validation issues", issues=issues)
    else:
        logger.info("Configuration validation passed")

    logger.info(
        "Monitoring configuration system ready",
        profile=config.profile.value,
        version=config.config_version,
    )