"""
Lukhas Neural Intelligence System - Main Entry Point
File: neural_intelligence_main.py
Path: neural_intelligence/neural_intelligence_main.py
Created: 2025-01-13
Author: Lukhas AI Research Team
Version: 2.0

Professional entry point for the Lukhas Neural Intelligence System.
Integrates all cognitive components while preserving unique Lukhas innovations.
"""
from typing import Dict
import time
import streamlit as st

import asyncio
import logging
from typing import Optional

from cognitive_core import NeuralIntelligenceSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("LukhasMain")


class LukhasNeuralIntelligence:
    """
    Main interface for the Lukhas Neural Intelligence System

    This provides a clean, professional API while preserving all unique
    Lukhas innovations (Dreams, Healix, Flashback, DriftScore, CollapseHash).
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the Lukhas Neural Intelligence System"""
        logger.info("🚀 Initializing Lukhas Neural Intelligence System")

        self.config = config or {}
        self.neural_intelligence = NeuralIntelligenceSystem(config)

        logger.info("✅ Lukhas Neural Intelligence System ready")

    async def process_request(self, request: str, context: Optional[dict] = None) -> dict:
        """
        Process an intelligence request using the full Lukhas system

        Args:
            request: The input request/query
            context: Optional context for the request

        Returns:
            Dict containing response and metadata
        """
        input_data = {
            "text": request,
            "context": context or {},
            "enable_dreams": self.config.get("enable_dreams", True),
            "enable_healix": self.config.get("enable_healix", True),
            "timestamp": asyncio.get_event_loop().time(),
        }

        response = await self.neural_intelligence.process_intelligence_request(input_data)

        return {
            "response": response.content,
            "confidence": response.confidence,
            "capability_level": response.capability_level.value,
            "metadata": response.metadata,
            "lukhas_innovations": self.neural_intelligence.get_lukhas_innovations_status(),
        }

    def get_system_status(self) -> dict:
        """Get comprehensive system status including Lukhas innovations"""
        return self.neural_intelligence.get_system_status()

    def get_innovations_status(self) -> dict:
        """Get status of unique Lukhas innovations"""
        return self.neural_intelligence.get_lukhas_innovations_status()


async def main():
    """Main demo function showcasing the professional Lukhas system"""
    print("🧠 Lukhas Neural Intelligence System - Professional Demo")
    print("=" * 60)

    # Initialize system
    config = {
        "enable_dreams": True,
        "enable_healix": True,
        "log_level": "INFO",
    }

    lukhas = LukhasNeuralIntelligence(config)

    # Show system status
    status = lukhas.get_system_status()
    print(f"Session ID: {status['session_id']}")
    print(f"Capability Level: {status['capability_level']}")

    # Show Lukhas innovations
    innovations = lukhas.get_innovations_status()
    print("\n🌟 Lukhas Unique Innovations:")
    for name, info in innovations.items():
        status_icon = "✅" if info["active"] else "⚠️"
        print(f"  {status_icon} {name.title()}: {info['description']}")

    # Demo requests
    test_requests = [
        "What is artificial intelligence?",
        "How can I improve my cognitive performance?",
        "Explain quantum-inspired computing in simple terms",
        "What makes Lukhas unique compared to other AI systems?",
    ]

    print("\n🔄 Processing Demo Requests:")
    print("-" * 40)

    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Request: {request}")

        response_data = await lukhas.process_request(request)

        print(f"   Response: {response_data['response'][:150]}...")
        print(f"   Confidence: {response_data['confidence']:.2f}")
        print(f"   Dreams Active: {response_data['lukhas_innovations']['dreams']['active']}")
        print(f"   Healix Active: {response_data['lukhas_innovations']['healix']['active']}")

    # Final status
    final_status = lukhas.get_system_status()
    print("\n📊 Final Metrics:")
    print(f"   Total Interactions: {final_status['performance_metrics']['total_interactions']}")
    print(f"   Average Confidence: {final_status['performance_metrics']['average_confidence']:.3f}")
    print(f"   Learning Patterns: {final_status['learning_patterns']}")

    print("\n✨ Lukhas Neural Intelligence System Demo Complete")


if __name__ == "__main__":
    asyncio.run(main())
