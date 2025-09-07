#!/usr/bin/env python3
"""
╭────────────────────────────────────────────────────────────────╮
│ MODULE       : azure_openai_client.py                         │
│ DESCRIPTION  : Azure OpenAI client for LUKHAS AI             │
│ TYPE         : Enterprise AI Client                           │
│ VERSION      : v1.0.0                                         │
│ AUTHOR       : Lukhas Systems                                   │
│ UPDATED      : 2025-06-14                                     │
│                                                                │
│ DEPENDENCIES: openai>=1.0.0, azure-identity                  │
│ - Compliance Alignment: EU AI Act, GDPR, OECD AI Principles   │
╰────────────────────────────────────────────────────────────────╯
"""
import logging
import streamlit as st

import subprocess
from typing import Optional


class LukhASAzureOpenAI:
    """Enterprise Azure OpenAI client for LUKHAS AI"""

    def __init__(self):
        """Initialize Azure OpenAI client with secure credentials"""
        self.config = self._load_secure_config()
        self.client = None
        self._initialize_client()

        print("🔵 LUKHAS AI Azure OpenAI Client")
        print("🔵 LUKHAS AI Azure OpenAI Client")
        print("=" * 40)

        if self.client:
            print("✅ Azure OpenAI client initialized")
            print(f"🌐 Endpoint: {self.config.get('endpoint', 'Not configured'}")
            print("📍 Region: UK South (GDPR Compliant)")
            print("🏢 Resource: lukhas")
        else:
            print("❌ Azure OpenAI client initialization failed")

    def _load_secure_config(self) -> dict:
        """Load Azure OpenAI configuration securely from Keychain"""
        config = {}
        config_keys = ["api-key", "endpoint", "api-version", "resource-name"]

        for key in config_keys:
            value = self._get_keychain_value(f"lukhas-ai-azure-{key}")
            if value:
                config[key.replace("-", "_")] = value

        return config

    def _get_keychain_value(self, service: str) -> Optional[str]:
        """Get value from macOS Keychain"""
        try:
            cmd = ["security", "find-generic-password", "-s", service, "-w"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            print(f"❌ Error retrieving {service}: {e}")
            return None

    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        try:
            if not all(k in self.config for k in ["api_key", "endpoint", "api_version"]):
                print("❌ Missing Azure OpenAI configuration")
                return

            # Try to import Azure OpenAI client
            try:
                from openai import AzureOpenAI

                self.client = AzureOpenAI(
                    api_key=self.config["api_key"],
                    azure_endpoint=self.config["endpoint"],
                    api_version=self.config["api_version"],
                )

            except ImportError:
                print("⚠️  Azure OpenAI client not available. Install with: pip install openai")
                return

        except Exception as e:
            print(f"❌ Error initializing Azure OpenAI client: {e}")

    def test_connection(self) -> bool:
        """Test Azure OpenAI connection"""
        if not self.client:
            print("❌ No client available")
            return False

        try:
            # Try to list models (this tests authentication)
            models = self.client.models.list()
            print("✅ Connection successful!")
            print(f"📋 Available models: {len(models.data} models found")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def chat_completion(self, messages: list[dict], model: str = "gpt-35-turbo", **kwargs):
        """Create chat completion using Azure OpenAI"""
        if not self.client:
            raise Exception("Azure OpenAI client not initialized")

        try:
            response = self.client.chat.completions.create(model=model, messages=messages, **kwargs)
            return response

        except Exception as e:
            print(f"❌ Chat completion error: {e}")
            raise

    def get_status(self) -> dict:
        """Get Azure OpenAI status and configuration"""
        return {
            "client_initialized": self.client is not None,
            "endpoint": self.config.get("endpoint", "Not configured"),
            "api_version": self.config.get("api_version", "Not configured"),
            "resource_name": self.config.get("resource_name", "Not configured"),
            "region": "UK South",
            "compliance": ["GDPR", "EU AI Act Ready"],
            "enterprise_features": [
                "Private endpoints available",
                "Data residency control",
                "Enhanced SLA",
                "Audit logging",
            ],
        }


def quick_test():
    """Quick test of Azure OpenAI setup"""
    print("🧪 Testing LUKHAS AI Azure OpenAI Setup")
    print("🧪 Testing LUKHAS AI Azure OpenAI Setup")
    print("=" * 50)

    # Initialize client
    azure_client = LukhASAzureOpenAI()

    # Test connection
    if azure_client.client:
        print("\n🔍 Testing connection...")
        azure_client.test_connection()

    # Show status
    print("\n📊 Configuration Status:")
    status = azure_client.get_status()
    for key, value in status.items():
        if isinstance(value, list):
            print(f"✅ {key}: {', '.join(value}")
        else:
            print(f"✅ {key}: {value}")

    return azure_client


def main():
    """Main function"""
    azure_client = quick_test()

    print("\n🎯 Next Steps:")
    if azure_client.client:
        print("1. ✅ Azure OpenAI client is ready")
        print("2. 📋 Deploy models in Azure Portal when needed")
        print("3. 🚀 Integrate with your AI system")
        print("4. 💼 Use for enterprise/client-facing features")
    else:
        print("1. 📦 Install Azure OpenAI: pip install openai")
        print("2. 🔑 Verify credentials are stored correctly")
        print("3. 🌐 Check Azure resource status")

    print("\n🔵 Your Enterprise AI Stack:")
    print("   Primary: Azure OpenAI (enterprise-grade)")
    print("   Backup: Regular OpenAI (latest features)")
    print("   Cost-effective: Gemini (bulk processing)")
    print("   Safety: Claude (critical decisions)")
    print("   Research: Perplexity (current info)")


if __name__ == "__main__":
    main()
