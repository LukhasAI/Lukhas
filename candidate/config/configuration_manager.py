"""
Configuration Manager - BATCH 7 Completion
Redirects to existing config functionality
"""
from candidate.monitoring.config_loader import ConfigLoader
from pathlib import Path

class ConfigurationManager:
    """Unified configuration management for LUKHAS"""

    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config_path = Path("candidate/config")
        self.config_path.mkdir(exist_ok=True)

    def load_dynamic_config(self, config_name: str):
        """Load configuration dynamically"""
        return self.config_loader.load_config(config_name)

    def reload_config(self):
        """Reload all configurations"""
        return self.config_loader.reload()

    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self.config_loader.get(key, default)

# Usage example
if __name__ == "__main__":
    config_manager = ConfigurationManager()
    print("✅ Configuration Manager working")
