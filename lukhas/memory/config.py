"""
LUKHAS AI Memory Configuration
Configuration settings for the memory system
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryConfig:
    """Memory system configuration"""

    # Core limits
    max_folds: int = 1000
    cascade_threshold: float = 0.997  # 99.7% prevention rate

    # Performance targets (milliseconds)
    target_creation_time_ms: float = 10.0
    target_access_time_ms: float = 50.0
    target_consolidation_time_ms: float = 100.0

    # Validation ranges
    min_emotional_valence: float = -1.0
    max_emotional_valence: float = 1.0
    min_importance: float = 0.0
    max_importance: float = 1.0

    # Feature flags
    memory_active: bool = False
    enable_matriz_instrumentation: bool = True
    enable_performance_monitoring: bool = True

    # Error handling
    max_error_rate: float = 0.05  # 5% max error rate
    enable_graceful_degradation: bool = True

    # Memory management
    consolidation_trigger_ratio: float = 0.9  # Trigger at 90% capacity
    importance_pruning_threshold: float = 0.1  # Remove below 10% importance

    @classmethod
    def from_environment(cls) -> "MemoryConfig":
        """Create config from environment variables"""
        return cls(
            max_folds=int(os.getenv("MEMORY_MAX_FOLDS", "1000")),
            cascade_threshold=float(os.getenv("MEMORY_CASCADE_THRESHOLD", "0.997")),
            target_creation_time_ms=float(os.getenv("MEMORY_TARGET_CREATION_MS", "10.0")),
            target_access_time_ms=float(os.getenv("MEMORY_TARGET_ACCESS_MS", "50.0")),
            target_consolidation_time_ms=float(os.getenv("MEMORY_TARGET_CONSOLIDATION_MS", "100.0")),
            memory_active=os.getenv("MEMORY_ACTIVE", "false").lower() == "true",
            enable_matriz_instrumentation=os.getenv("MEMORY_MATRIZ_ENABLED", "true").lower() == "true",
            enable_performance_monitoring=os.getenv("MEMORY_PERF_MONITORING", "true").lower() == "true",
            max_error_rate=float(os.getenv("MEMORY_MAX_ERROR_RATE", "0.05")),
            enable_graceful_degradation=os.getenv("MEMORY_GRACEFUL_DEGRADATION", "true").lower() == "true",
            consolidation_trigger_ratio=float(os.getenv("MEMORY_CONSOLIDATION_TRIGGER", "0.9")),
            importance_pruning_threshold=float(os.getenv("MEMORY_PRUNING_THRESHOLD", "0.1")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "max_folds": self.max_folds,
            "cascade_threshold": self.cascade_threshold,
            "performance_targets": {
                "creation_time_ms": self.target_creation_time_ms,
                "access_time_ms": self.target_access_time_ms,
                "consolidation_time_ms": self.target_consolidation_time_ms,
            },
            "validation_ranges": {
                "emotional_valence": [
                    self.min_emotional_valence,
                    self.max_emotional_valence,
                ],
                "importance": [self.min_importance, self.max_importance],
            },
            "feature_flags": {
                "memory_active": self.memory_active,
                "matriz_instrumentation": self.enable_matriz_instrumentation,
                "performance_monitoring": self.enable_performance_monitoring,
                "graceful_degradation": self.enable_graceful_degradation,
            },
            "management": {
                "max_error_rate": self.max_error_rate,
                "consolidation_trigger_ratio": self.consolidation_trigger_ratio,
                "importance_pruning_threshold": self.importance_pruning_threshold,
            },
        }

    def validate(self) -> dict[str, Any]:
        """Validate configuration settings"""
        issues = []

        if self.max_folds <= 0:
            issues.append("max_folds must be positive")

        if not (0.0 <= self.cascade_threshold <= 1.0):
            issues.append("cascade_threshold must be between 0.0 and 1.0")

        if self.target_creation_time_ms <= 0:
            issues.append("target_creation_time_ms must be positive")

        if self.target_access_time_ms <= 0:
            issues.append("target_access_time_ms must be positive")

        if self.min_emotional_valence >= self.max_emotional_valence:
            issues.append("min_emotional_valence must be less than max_emotional_valence")

        if self.min_importance >= self.max_importance:
            issues.append("min_importance must be less than max_importance")

        if not (0.0 <= self.max_error_rate <= 1.0):
            issues.append("max_error_rate must be between 0.0 and 1.0")

        return {"valid": len(issues) == 0, "issues": issues, "config": self.to_dict()}


# Global configuration instance
_config = None


def get_memory_config() -> MemoryConfig:
    """Get or create global memory configuration"""
    global _config
    if _config is None:
        _config = MemoryConfig.from_environment()
    return _config


def reload_config() -> MemoryConfig:
    """Reload configuration from environment"""
    global _config
    _config = MemoryConfig.from_environment()
    return _config