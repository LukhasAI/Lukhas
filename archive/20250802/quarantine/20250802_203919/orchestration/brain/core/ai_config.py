"""
+────────────────────────────────────────────────────────────────+
| MODULE       : ai_config.py                                   |
| DESCRIPTION  : Secure configuration for multiple AI APIs      |
| TYPE         : Configuration & Security Manager               |
| VERSION      : v1.0.0                                         |
| AUTHOR       : Lukhas Systems                                   |
| UPDATED      : 2025-6-14                                     |
|                                                                |
| DEPENDENCIES: keyring, python-dotenv, asyncio                 |
| - Compliance Alignment: EU AI Act, GDPR, OECD AI Principles   |
+────────────────────────────────────────────────────────────────+
"""

import os
import keyring
import subprocess
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import openai


@dataclass
class APIConfig:
    """Configuration for each AI provider"""

    name: str
    base_url: str
    rate_limit_rpm: int  # Requests per minute
    rate_limit_tpm: int  # Tokens per minute
    cost_per_1k_tokens: float
    supports_streaming: bool
    supports_multimodal: bool


class SecureKeyManager:
    """Secure API key management using macOS Keychain"""

    def __init__(self):
        self.service_prefix = "lukhas-ai"

    def store_key(self, provider: str, api_key: str) -> bool:
        """Store API key securely in macOS Keychain"""
        try:
            service_name = f"{self.service_prefix}-{provider}"
            cmd = [
                "security",
                "add-generic-password",
                "-a",
                os.getenv("USER", "unknown"),
                "-s",
                service_name,
                "-w",
                api_key,
                "-U",  # Update if exists
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error storing {provider} key: {e}")
            return False

    def get_key(self, provider: str) -> Optional[str]:
        """Retrieve API key securely from macOS Keychain"""
        try:
            service_name = f"{self.service_prefix}-{provider}"
            cmd = [
                "security",
                "find-generic-password",
                "-a",
                os.getenv("USER", "unknown"),
                "-s",
                service_name,
                "-w",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"❌ Error retrieving {provider} key: {e}")
            return None

    def setup_all_keys(self):
        """Interactive setup for all API key"""
        providers = ["openai", "anthropic", "gemini", "perplexity"]

        print("🔐 LUKHAS AI API Key Setup")
        print("=" * 50)

        for provider in providers:
            print(f"\n📋 Setting up {provider.upper()} API key...")
            existing = self.get_key(provider)

            if existing:
                print(f"✅ Existing key found for {provider}")
                update = input(f"Update {provider} key? (y/N): ").lower() == "y"
                if not update:
                    continue

            api_key = input(f"Enter your {provider.upper()} API key: ").strip()
            if api_key:
                if self.store_key(provider, api_key):
                    print(f"✅ {provider.upper()} key stored securely!")

                    # Special handling for OpenAI organization ID
                    if provider == "openai":
                        org_id = input(
                            "Enter your OpenAI Organization ID (optional, press Enter to skip): "
                        ).strip()
                        if org_id:
                            if self.store_key("openai-org", org_id):
                                print("✅ OpenAI Organization ID stored securely!")
                            else:
                                print("⚠️  Failed to store OpenAI Organization ID")
                        else:
                            print("⏭️  Skipping OpenAI Organization ID")
                else:
                    print(f"❌ Failed to store {provider} key")
            else:
                print(f"⏭️  Skipping {provider}")


class AIProviderConfigs:
    """Configuration for all AI provider"""

    @staticmethod
    def get_configs() -> Dict[str, APIConfig]:
        return {
            "openai": APIConfig(
                name="OpenAI",
                base_url="https://api.openai.com/v1",
                rate_limit_rpm=60,
                rate_limit_tpm=150000,
                cost_per_1k_tokens=0.3,  # GPT-4 approximate
                supports_streaming=True,
                supports_multimodal=True,
            ),
            "anthropic": APIConfig(
                name="Anthropic Claude",
                base_url="https://api.anthropic.com",
                rate_limit_rpm=50,
                rate_limit_tpm=100000,
                cost_per_1k_tokens=0.15,  # Claude-3 Sonnet approximate
                supports_streaming=True,
                supports_multimodal=False,
            ),
            "gemini": APIConfig(
                name="Google Gemini",
                base_url="https://generativelanguage.googleapis.com",
                rate_limit_rpm=1500,
                rate_limit_tpm=32000,
                cost_per_1k_tokens=0.01,  # Very cost effective
                supports_streaming=True,
                supports_multimodal=True,
            ),
            "perplexity": APIConfig(
                name="Perplexity",
                base_url="https://api.perplexity.ai",
                rate_limit_rpm=50,
                rate_limit_tpm=40000,
                cost_per_1k_tokens=0.02,  # Approximate
                supports_streaming=True,
                supports_multimodal=False,
            ),
        }


class EnvironmentSetup:
    """Set up environment variables for development"""

    def __init__(self):
        self.key_manager = SecureKeyManager()

    def create_env_file(self):
        """Create .env file with secure key reference"""
        env_content = f"""# LUKHAS AI Environment Configuration
        env_content = f"""  # LUKHAS AI Environment Configuration
# Generated: {self._get_timestamp()}
# Security: Keys stored in macOS Keychain, not in this file


# Development Settings
AGI_ENV = development
DEBUG = true
LOG_LEVEL = INFO

# AI Provider Settings
OPENAI_API_KEY = "$(security find-generic-password -s lukhas-ai-openai -w)"
OPENAI_ORG_ID = "$(security find-generic-password -s lukhas-ai-openai-org -w)"
ANTHROPIC_API_KEY = "$(security find-generic-password -s lukhas-ai-anthropic -w)"
GEMINI_API_KEY = "$(security find-generic-password -s lukhas-ai-gemini -w)"
PERPLEXITY_API_KEY = "$(security find-generic-password -s lukhas-ai-perplexity -w)"

# Rate Limiting
ENABLE_RATE_LIMITING = true
MAX_CONCURRENT_REQUESTS = 5

# Compliance
GDPR_MODE = true
AUDIT_LOGGING = true
PII_DETECTION = true

# Performance
CACHE_RESPONSES = true
CACHE_TTL = 3600
"""

        with open("/Users/A_G_I/LUKHAS/.env.template", "w") as f:
        with open("/Users/A_G_I/lukhas/.env.template", "w") as f:
            f.write(env_content)

        print("✅ Created .env.template file")
        print("🔒 API keys will be securely retrieved from Keychain")

    def _get_timestamp(self):
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ===============================================================
# 🎯 USAGE RECOMMENDATIONS
# ===============================================================


def print_usage_guide():
    """Print comprehensive usage guide"""
    guide = """
🎯 OPTIMAL AI USAGE STRATEGIES FOR LUKHAS AI
🎯 OPTIMAL AI USAGE STRATEGIES FOR LUKHAS AI

🤖 OPENAI(GPT - 4 / 3.5) - USE FOR:
  ✅ Complex code generation and debugging
  ✅ Technical documentation and API design
  ✅ Structured data processing(JSON / YAML)
  ✅ Mathematical computations and algorithms
  ✅ Logic - heavy problem solving

🧠 ANTHROPIC CLAUDE - USE FOR:
  ✅ Long document analysis and research
  ✅ Ethical reasoning and safety considerations
  ✅ Complex decision - making with multiple factors
  ✅ Constitutional AI alignment tasks
  ✅ Risk assessment and compliance review

🌟 GOOGLE GEMINI - USE FOR:
  ✅ High - volume, cost - sensitive tasks
  ✅ Image and multimodal analysis
  ✅ Creative content generation
  ✅ Real - time applications(fast response)
  ✅ Mobile / edge deployment scenarios

🔍 PERPLEXITY - USE FOR:
  ✅ Current events and real - time information
  ✅ Market research and competitive analysis
  ✅ Fact - checking with citations
  ✅ Technology trends and news
  ✅ Academic research with sources

💡 MULTI - AI STRATEGIES:
  🔄 Ensemble Approach: Use multiple AIs for complex problems
  🎯 Task Routing: Automatically route tasks to optimal provider
  💰 Cost Optimization: Use Gemini for bulk, OpenAI for complex
  🛡️ Safety First: Use Claude for critical decisions
  📊 Consensus: Get multiple perspectives on important choices

🚀 IMPLEMENTATION TIPS:
  * Start with Gemini for prototyping(fast + cheap)
  * Escalate to OpenAI for technical implementation
  * Use Claude for final safety and ethical review
  * Use Perplexity for real - world data validation
  * Implement fallback chains for reliability
  * Cache responses to minimize costs
  * Batch similar requests when possible
"""
    print(guide)


if __name__ == "__main__":
    print("🔐 LUKHAS AI Secure API Configuration")
    print("🔐 LUKHAS AI Secure API Configuration")
    print("=" * 50)

    # Setup key manager
    key_manager = SecureKeyManager()

    # Interactive setup
    setup_choice = input("Setup API keys now? (y/N): ").lower()
    if setup_choice == "y":
        key_manager.setup_all_keys()

    # Create environment template
    env_setup = EnvironmentSetup()
    env_setup.create_env_file()

    # Show usage guide
    print_usage_guide()

    print("\n✅ Setup complete! Your API keys are stored securely.")
    print("🔒 Use the key_manager.get_key('provider') method to access them.")
