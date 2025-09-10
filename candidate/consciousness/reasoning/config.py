"""
Configuration module for LUKHAS reasoning engine

Simple configuration provider for consciousness reasoning components.
"""

from typing import Any


class LucasConfig:
    """Simple configuration class for LUKHAS consciousness reasoning engine"""

    @staticmethod
    def get_default() -> dict[str, Any]:
        """Get default configuration for the reasoning engine"""
        return {
            "analysis_timeout": 30,
            "cache_enabled": True,
            "max_data_size": 10000000,  # 10MB
            "symbolic_processing_enabled": True,
            "memory_persistence": True,
            "access_control_enabled": True,
            "default_analysis_type": "auto",
            "confidence_threshold": 0.7,
            "max_insights": 10,
            "max_visualizations": 5,
        }
