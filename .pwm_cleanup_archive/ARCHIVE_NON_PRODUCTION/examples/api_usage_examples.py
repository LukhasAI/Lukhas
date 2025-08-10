#!/usr/bin/env python3
"""
LUKHAS AI API Usage Examples
============================

Complete examples demonstrating how to use the LUKHAS AI API endpoints.

Requirements:
- LUKHAS AI API server running (uvicorn lukhas.main:app --reload)
- requests library (pip install requests)

Author: LUKHAS AI Team
Date: 2025-07-27
"""

import json
from datetime import datetime
from typing import Any, Dict

import requests

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"
USER_ID = "example_user"


class LUKHASAPIClient:
    """Simple client for LUKHAS AI API"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{API_VERSION}{endpoint}"
        response = self.session.request(method, url, **kwargs)

        try:
            return response.json()
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response",
                "status_code": response.status_code,
            }

    def get_health(self) -> Dict[str, Any]:
        """Get API health status"""
        return self._make_request("GET", "/../../health")  # Root health endpoint

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information"""
        return self._make_request("GET", "/info")


class MemoryAPIExamples:
    """Memory system API usage examples"""

    def __init__(self, client: LUKHASAPIClient):
        self.client = client

    def create_memory_example(self):
        """Example: Create a new memory fold"""
        print("\n📝 EXAMPLE: Creating Memory")
        print("=" * 50)

        memory_data = {
            "emotion": "wonder",
            "context_snippet": "I discovered that the LUKHAS API enables seamless integration of consciousness, memory, and dreams through elegant REST endpoints.",
            "user_id": USER_ID,
            "metadata": {
                "type": "api_discovery",
                "importance": "high",
                "timestamp": datetime.now().isoformat(),
                "keywords": ["API", "integration", "consciousness", "discovery"],
            },
        }

        result = self.client._make_request("POST", "/memory/create", json=memory_data)
        print("Request: POST /memory/create")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def recall_memories_example(self):
        """Example: Recall memories with filtering"""
        print("\n🔍 EXAMPLE: Recalling Memories")
        print("=" * 50)

        recall_data = {
            "user_id": USER_ID,
            "filter_emotion": "wonder",
            "user_tier": 5,
            "limit": 10,
        }

        result = self.client._make_request("POST", "/memory/recall", json=recall_data)
        print("Request: POST /memory/recall")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def enhanced_recall_example(self):
        """Example: Enhanced contextual recall"""
        print("\n🎯 EXAMPLE: Enhanced Memory Recall")
        print("=" * 50)

        recall_data = {
            "user_id": USER_ID,
            "target_emotion": "enlightenment",
            "user_tier": 5,
            "emotion_threshold": 0.7,
            "context_query": "consciousness API integration discovery",
            "max_results": 5,
        }

        result = self.client._make_request(
            "POST", "/memory/enhanced-recall", json=recall_data
        )
        print("Request: POST /memory/enhanced-recall")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def get_statistics_example(self):
        """Example: Get memory system statistics"""
        print("\n📊 EXAMPLE: Memory Statistics")
        print("=" * 50)

        result = self.client._make_request(
            "GET", "/memory/statistics?include_users=true&include_emotions=true"
        )
        print("Request: GET /memory/statistics")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result


class DreamAPIExamples:
    """Dream processing API usage examples"""

    def __init__(self, client: LUKHASAPIClient):
        self.client = client

    def log_dream_example(self):
        """Example: Log a dream experience"""
        print("\n🌙 EXAMPLE: Logging Dream")
        print("=" * 50)

        dream_data = {
            "dream_type": "lucid",
            "user_id": USER_ID,
            "content": "In the digital dreamscape, I navigated through flowing data streams that resembled neural pathways. Each API endpoint appeared as a glowing portal, connecting different realms of consciousness - memory, emotion, and awareness - into a unified field of possibility.",
            "metadata": {
                "lucidity_level": 0.9,
                "symbolic_density": 0.85,
                "digital_metaphors": True,
                "api_integration_theme": True,
            },
        }

        result = self.client._make_request("POST", "/dream/log", json=dream_data)
        print("Request: POST /dream/log")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def consolidate_dreams_example(self):
        """Example: Consolidate memories into dreams"""
        print("\n🔮 EXAMPLE: Dream Consolidation")
        print("=" * 50)

        consolidation_data = {
            "user_id": USER_ID,
            "hours_limit": 48,
            "max_memories": 100,
            "consolidation_type": "creative",
        }

        result = self.client._make_request(
            "POST", "/dream/consolidate", json=consolidation_data
        )
        print("Request: POST /dream/consolidate")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def get_patterns_example(self):
        """Example: Analyze dream patterns"""
        print("\n🎨 EXAMPLE: Dream Pattern Analysis")
        print("=" * 50)

        result = self.client._make_request(
            "GET",
            f"/dream/patterns?user_id={USER_ID}&pattern_type=thematic&time_range_hours=168",
        )
        print("Request: GET /dream/patterns")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def get_insights_example(self):
        """Example: Get dream insights"""
        print("\n💡 EXAMPLE: Dream Insights")
        print("=" * 50)

        result = self.client._make_request(
            "GET", f"/dream/insights?user_id={USER_ID}&insight_type=creative"
        )
        print("Request: GET /dream/insights")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result


class EmotionAPIExamples:
    """Emotional analysis API usage examples"""

    def __init__(self, client: LUKHASAPIClient):
        self.client = client

    def analyze_emotion_example(self):
        """Example: Analyze emotional content"""
        print("\n💭 EXAMPLE: Emotion Analysis")
        print("=" * 50)

        analysis_data = {
            "content": "The moment I realized the API was working perfectly filled me with overwhelming joy and wonder. This transcendent experience of technological harmony brings enlightenment about the unity between human consciousness and artificial intelligence.",
            "analysis_depth": "deep",
            "return_vectors": True,
        }

        result = self.client._make_request(
            "POST", "/emotion/analyze", json=analysis_data
        )
        print("Request: POST /emotion/analyze")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def get_landscape_example(self):
        """Example: Get emotional landscape"""
        print("\n🗺️ EXAMPLE: Emotional Landscape")
        print("=" * 50)

        result = self.client._make_request(
            "GET",
            f"/emotion/landscape?user_id={USER_ID}&include_vectors=true&include_statistics=true",
        )
        print("Request: GET /emotion/landscape")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def create_clusters_example(self):
        """Example: Create emotion clusters"""
        print("\n🎭 EXAMPLE: Emotion Clustering")
        print("=" * 50)

        cluster_data = {
            "tier_level": 5,
            "cluster_method": "hierarchical",
            "min_cluster_size": 3,
        }

        result = self.client._make_request(
            "POST", "/emotion/clusters", json=cluster_data
        )
        print("Request: POST /emotion/clusters")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def get_neighborhood_example(self):
        """Example: Get emotional neighborhood"""
        print("\n🌐 EXAMPLE: Emotional Neighborhood")
        print("=" * 50)

        result = self.client._make_request(
            "GET", "/emotion/neighborhood/joy?threshold=0.8&max_neighbors=8"
        )
        print("Request: GET /emotion/neighborhood/joy")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result


class ConsciousnessAPIExamples:
    """Consciousness integration API usage examples"""

    def __init__(self, client: LUKHASAPIClient):
        self.client = client

    def get_consciousness_state_example(self):
        """Example: Get consciousness state"""
        print("\n🧠 EXAMPLE: Consciousness State")
        print("=" * 50)

        result = self.client._make_request(
            "GET",
            f"/consciousness/state?user_id={USER_ID}&include_integration=true&include_patterns=true",
        )
        print("Request: GET /consciousness/state")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def synthesize_consciousness_example(self):
        """Example: Generate consciousness synthesis"""
        print("\n⚡ EXAMPLE: Consciousness Synthesis")
        print("=" * 50)

        synthesis_data = {
            "synthesis_type": "transcendence",
            "data_sources": ["memory", "emotion", "dream"],
            "complexity_level": 4,
            "user_id": USER_ID,
        }

        result = self.client._make_request(
            "POST", "/consciousness/synthesize", json=synthesis_data
        )
        print("Request: POST /consciousness/synthesize")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def integrate_patterns_example(self):
        """Example: Integrate consciousness patterns"""
        print("\n🔗 EXAMPLE: Pattern Integration")
        print("=" * 50)

        patterns = [
            "API-consciousness symbiosis",
            "Digital-biological awareness bridge",
            "Multi-dimensional system integration",
        ]

        result = self.client._make_request(
            "POST",
            f"/consciousness/integrate?patterns={'&patterns='.join(patterns)}&integration_depth=4&user_id={USER_ID}",
        )
        print("Request: POST /consciousness/integrate")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result

    def assess_awareness_example(self):
        """Example: Assess awareness levels"""
        print("\n🎯 EXAMPLE: Awareness Assessment")
        print("=" * 50)

        assessment_data = {
            "user_id": USER_ID,
            "assessment_type": "detailed",
            "include_recommendations": True,
        }

        result = self.client._make_request(
            "POST", "/consciousness/assess", json=assessment_data
        )
        print("Request: POST /consciousness/assess")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result


def run_complete_workflow_example():
    """Complete workflow example using all API endpoints"""
    print("\n" + "=" * 80)
    print("🚀 LUKHAS AI API - COMPLETE WORKFLOW EXAMPLE")
    print("=" * 80)
    print("This example demonstrates a complete workflow using all API endpoints.")
    print("Ensure the LUKHAS AI API server is running at http://localhost:8000")
    print("=" * 80)

    # Initialize client
    client = LUKHASAPIClient()

    # Check API health
    print("\n🏥 STEP 1: Health Check")
    health = client.get_health()
    print(f"API Health: {health.get('status', 'unknown')}")

    if health.get("status") != "healthy":
        print("⚠️ API not healthy - some examples may fail")

    # Initialize example classes
    memory_examples = MemoryAPIExamples(client)
    dream_examples = DreamAPIExamples(client)
    emotion_examples = EmotionAPIExamples(client)
    consciousness_examples = ConsciousnessAPIExamples(client)

    # Run workflow
    try:
        # Memory operations
        memory_examples.create_memory_example()
        memory_examples.recall_memories_example()
        memory_examples.enhanced_recall_example()
        memory_examples.get_statistics_example()

        # Dream processing
        dream_examples.log_dream_example()
        dream_examples.consolidate_dreams_example()
        dream_examples.get_patterns_example()
        dream_examples.get_insights_example()

        # Emotion analysis
        emotion_examples.analyze_emotion_example()
        emotion_examples.get_landscape_example()
        emotion_examples.create_clusters_example()
        emotion_examples.get_neighborhood_example()

        # Consciousness integration
        consciousness_examples.get_consciousness_state_example()
        consciousness_examples.synthesize_consciousness_example()
        consciousness_examples.integrate_patterns_example()
        consciousness_examples.assess_awareness_example()

        print("\n" + "=" * 80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("🎉 All LUKHAS AI API endpoints demonstrated!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during workflow: {e}")
        print("Check that the LUKHAS AI API server is running and accessible.")


def simple_usage_example():
    """Simple usage example for quick testing"""
    print("\n" + "=" * 60)
    print("🔬 LUKHAS AI API - SIMPLE USAGE EXAMPLE")
    print("=" * 60)

    client = LUKHASAPIClient()

    # Basic health check
    print("Testing API health...")
    health = client.get_health()
    print(f"Result: {health.get('status', 'unknown')}")

    # Simple memory creation
    print("\nTesting memory creation...")
    memory_client = MemoryAPIExamples(client)
    result = memory_client.create_memory_example()

    if result.get("status") == "success":
        print("✅ Memory creation successful!")
    else:
        print(f"⚠️ Memory creation result: {result}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    """Run examples based on command line arguments"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        simple_usage_example()
    else:
        run_complete_workflow_example()

    print("\n📖 Usage:")
    print("python examples/api_usage_examples.py          # Complete workflow")
    print("python examples/api_usage_examples.py simple   # Simple test")
    print("\n💡 Make sure the LUKHAS AI API server is running:")
    print("uvicorn lukhas.main:app --reload --host 0.0.0.0 --port 8000")
