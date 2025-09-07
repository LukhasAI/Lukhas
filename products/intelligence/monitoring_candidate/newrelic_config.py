#!/usr/bin/env python3
"""
LUKHAS AI - NewRelic Monitoring Configuration
GitHub Student Pack Integration ($300/month value)
==============================================

Configures comprehensive monitoring for LUKHAS AI production system.
"""
import logging
import os
import time
from typing import Optional

# NewRelic Python Agent Configuration
NEWRELIC_CONFIG = {
    "app_name": "LUKHAS AI Production",
    "license_key": os.getenv("NEWRELIC_LICENSE_KEY", ""),
    "environment": "production",
    # Application Configuration
    "application_logging": {
        "enabled": True,
        "forwarding": {
            "enabled": True,
            "max_samples_stored": 10000,
        },
        "metrics": {
            "enabled": True,
        },
        "local_decorating": {
            "enabled": True,
        },
    },
    # Transaction Configuration
    "transaction_tracer": {
        "enabled": True,
        "transaction_threshold": 0.5,  # 500ms
        "record_sql": "obfuscated",
        "stack_trace_threshold": 0.5,
        "explain_enabled": True,
        "explain_threshold": 0.5,
    },
    # Error Collector
    "error_collector": {
        "enabled": True,
        "capture_source": True,
        "ignore_errors": ["404", "401"],
    },
    # Browser Monitoring (for future web interface)
    "browser_monitoring": {
        "auto_instrument": True,
    },
    # Distributed Tracing
    "distributed_tracing": {
        "enabled": True,
    },
    # Custom Attributes for LUKHAS AI
    "attributes": {
        "include": [
            "request.*",
            "response.*",
            "lukhas.*",
            "consciousness.*",
            "trinity.*",
        ]
    },
}


class LUKHASNewRelicMonitoring:
    """
    NewRelic monitoring integration for LUKHAS AI
    Tracks consciousness technology metrics and performance
    """

    def __init__(self, license_key: Optional[str] = None):
        self.license_key = license_key or os.getenv("NEWRELIC_LICENSE_KEY")
        self.enabled = bool(self.license_key)
        self.logger = logging.getLogger(__name__)

        if self.enabled:
            self._initialize_newrelic()
        else:
            self.logger.warning("NewRelic license key not provided - monitoring disabled")

    def _initialize_newrelic(self):
        """Initialize NewRelic monitoring"""
        try:
            import newrelic.agent

            # Configure NewRelic with our settings
            config = NEWRELIC_CONFIG.copy()
            config["license_key"] = self.license_key

            newrelic.agent.initialize(config_file=None, config_settings=config)

            # Set custom attributes
            newrelic.agent.add_custom_attribute("service.name", "LUKHAS AI")
            newrelic.agent.add_custom_attribute("service.version", "2.0.0")
            newrelic.agent.add_custom_attribute("trinity.framework", "⚛️🧠🛡️")
            newrelic.agent.add_custom_attribute("deployment.environment", "production")
            newrelic.agent.add_custom_attribute("deployment.platform", "Azure Container Apps")
            newrelic.agent.add_custom_attribute("github.student_pack", True)

            self.logger.info("✅ NewRelic monitoring initialized")

        except ImportError:
            self.logger.error("❌ NewRelic Python agent not installed")
            self.enabled = False
        except Exception as e:
            self.logger.error(f"❌ NewRelic initialization failed: {e}")
            self.enabled = False

    def track_consciousness_interaction(
        self,
        session_id: str,
        message: str,
        response: str,
        consciousness_level: float,
        model_used: str,
    ):
        """Track consciousness interface interactions"""
        if not self.enabled:
            return

        try:
            import newrelic.agent

            # Record custom event
            newrelic.agent.record_custom_event(
                "LUKHASConsciousnessInteraction",
                {
                    "session_id": session_id,
                    "message_length": len(message),
                    "response_length": len(response),
                    "consciousness_level": consciousness_level,
                    "model_used": model_used,
                    "timestamp": int(time.time()),
                },
            )

            # Add transaction attributes
            newrelic.agent.add_custom_attribute("consciousness.level", consciousness_level)
            newrelic.agent.add_custom_attribute("consciousness.model", model_used)
            newrelic.agent.add_custom_attribute("consciousness.session", session_id)

        except Exception as e:
            self.logger.error(f"Failed to track consciousness interaction: {e}")

    def track_dream_generation(
        self,
        prompt: str,
        style: str,
        dream_length: int,
        consciousness_score: float,
        generation_time_ms: int,
    ):
        """Track dream generation metrics"""
        if not self.enabled:
            return

        try:
            import newrelic.agent

            # Record custom event
            newrelic.agent.record_custom_event(
                "LUKHASDreamGeneration",
                {
                    "prompt_length": len(prompt),
                    "style": style,
                    "dream_length": dream_length,
                    "consciousness_score": consciousness_score,
                    "generation_time_ms": generation_time_ms,
                    "timestamp": int(time.time()),
                },
            )

            # Add custom metrics
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Dreams/GenerationTime", generation_time_ms)
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Dreams/ConsciousnessScore", consciousness_score)

        except Exception as e:
            self.logger.error(f"Failed to track dream generation: {e}")

    def track_trinity_framework_health(
        self,
        identity_health: float,
        consciousness_health: float,
        guardian_health: float,
    ):
        """Track Trinity Framework component health"""
        if not self.enabled:
            return

        try:
            import newrelic.agent

            # Record Trinity Framework metrics
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Trinity/Identity", identity_health)
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Trinity/Consciousness", consciousness_health)
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Trinity/Guardian", guardian_health)

            overall_health = (identity_health + consciousness_health + guardian_health) / 3
            newrelic.agent.record_custom_metric("Custom/LUKHAS/Trinity/Overall", overall_health)

            # Record health event
            newrelic.agent.record_custom_event(
                "LUKHASTrinityHealth",
                {
                    "identity_health": identity_health,
                    "consciousness_health": consciousness_health,
                    "guardian_health": guardian_health,
                    "overall_health": overall_health,
                    "timestamp": int(time.time()),
                },
            )

        except Exception as e:
            self.logger.error(f"Failed to track Trinity Framework health: {e}")

    def track_api_performance(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        user_agent: str = "",
    ):
        """Track API endpoint performance"""
        if not self.enabled:
            return

        try:
            import newrelic.agent

            # NewRelic automatically tracks web transactions, but we can add custom attributes
            newrelic.agent.add_custom_attribute("api.endpoint", endpoint)
            newrelic.agent.add_custom_attribute("api.method", method)
            newrelic.agent.add_custom_attribute("api.status_code", status_code)
            newrelic.agent.add_custom_attribute("api.response_time_ms", response_time_ms)

            if user_agent:
                newrelic.agent.add_custom_attribute("api.user_agent", user_agent[:100])  # Truncate

        except Exception as e:
            self.logger.error(f"Failed to track API performance: {e}")


# Global monitoring instance
newrelic_monitor: Optional[LUKHASNewRelicMonitoring] = None


def initialize_monitoring(
    license_key: Optional[str] = None,
) -> LUKHASNewRelicMonitoring:
    """Initialize global NewRelic monitoring"""
    global newrelic_monitor
    newrelic_monitor = LUKHASNewRelicMonitoring(license_key)
    return newrelic_monitor


def get_monitor() -> Optional[LUKHASNewRelicMonitoring]:
    """Get the global monitoring instance"""
    return newrelic_monitor


# Custom decorators for easy monitoring
def monitor_consciousness_endpoint(func):
    """Decorator for consciousness endpoints"""

    def wrapper(*args, **kwargs):
        if newrelic_monitor and newrelic_monitor.enabled:
            import newrelic.agent

            with newrelic.agent.FunctionTrace(name=f"consciousness.{func.__name__}"):
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def monitor_dream_endpoint(func):
    """Decorator for dream generation endpoints"""

    def wrapper(*args, **kwargs):
        if newrelic_monitor and newrelic_monitor.enabled:
            import newrelic.agent

            with newrelic.agent.FunctionTrace(name=f"dreams.{func.__name__}"):
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def monitor_trinity_component(component_name: str):
    """Decorator for Trinity Framework components"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if newrelic_monitor and newrelic_monitor.enabled:
                import newrelic.agent

                with newrelic.agent.FunctionTrace(name=f"trinity.{component_name}.{func.__name__}"):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
