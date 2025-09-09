#!/usr/bin/env python3
"""
LUKHAS AI - Comprehensive API Documentation Generator
===================================================

Advanced API documentation system with interactive examples,
OpenAPI specification generation, and comprehensive guides.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Features: OpenAPI 3.0, interactive examples, SDK generation support

Features:
- Automatic OpenAPI 3.0 specification generation
- Interactive API documentation with examples
- Code generation for multiple languages
- Comprehensive endpoint documentation
- Authentication and security documentation
- Healthcare compliance documentation
- Rate limiting and cost information
"""
import streamlit as st

import json
import logging
from datetime import datetime
from typing import Any, Optional

try:
    from fastapi import FastAPI
    from fastapi.openapi.utils import get_openapi

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)


class APIDocumentationGenerator:
    """Generate comprehensive API documentation"""

    def __init__(self, app: Optional[Any] = None):
        self.app = app
        self.custom_examples = {}
        self.endpoint_guides = {}

    def generate_openapi_spec(self) -> dict[str, Any]:
        """Generate comprehensive OpenAPI 3.0 specification"""
        if not self.app or not FASTAPI_AVAILABLE:
            return self._generate_static_spec()

        # Generate base OpenAPI spec
        openapi_spec = get_openapi(
            title="LUKHAS AI Multi-Model Orchestration API",
            version="2.0.0",
            description=self._get_api_description(),
            routes=self.app.routes,
        )

        # Enhance with custom documentation
        openapi_spec = self._enhance_openapi_spec(openapi_spec)

        return openapi_spec

    def _get_api_description(self) -> str:
        """Get comprehensive API description"""
        return """
# LUKHAS AI Multi-Model Orchestration API

The LUKHAS AI API provides advanced multi-model orchestration capabilities with enterprise-grade security,
healthcare compliance, and comprehensive validation.

## Key Features

- **Multi-Model Orchestration**: Coordinate OpenAI, Anthropic, Google Gemini, and Perplexity models
- **Advanced Consensus**: Intelligent consensus algorithms for enhanced accuracy
- **Real-time Streaming**: Server-Sent Events and WebSocket support
- **Healthcare Compliance**: HIPAA-compliant endpoints with audit trails
- **Enterprise Security**: JWT/API key authentication, rate limiting, threat detection
- **Function Calling**: Secure function execution with validation
- **Comprehensive Validation**: Request/response validation with security checks

## Trinity Framework Integration

The API is built around the Trinity Framework:
- ⚛️ **Identity**: Secure authentication and user management
- 🧠 **Consciousness**: Intelligent orchestration and decision-making
- 🛡️ **Guardian**: Security, validation, and compliance protection

## Authentication

The API supports two authentication methods:
1. **API Keys**: Long-lived keys for server-to-server communication
2. **JWT Tokens**: Short-lived tokens for user sessions

## Rate Limits

Rate limits are tier-based:
- **Lambda Tier 1**: 10 requests/minute, 1,000 requests/day
- **Lambda Tier 2**: 50 requests/minute, 5,000 requests/day
- **Lambda Tier 3**: 100 requests/minute, 10,000 requests/day
- **Lambda Tier 4**: 500 requests/minute, 50,000 requests/day

## Healthcare Compliance

Healthcare endpoints (`/healthcare/*`) require:
- HIPAA-compliant user tier (Tier 3+)
- Verified consent
- PHI scrubbing
- Comprehensive audit trails

## Cost Management

All endpoints include cost estimation and tracking:
- Transparent pricing per model
- Daily cost limits per tier
- Real-time cost tracking
- Detailed usage analytics
        """

    def _enhance_openapi_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Enhance OpenAPI spec with custom documentation"""

        # Add security schemes
        spec["components"]["securitySchemes"] = {
            "APIKeyAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "LUKHAS API Key authentication",
            },
            "JWTAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication",
            },
        }

        # Add servers
        spec["servers"] = [
            {"url": "https://api.lukhas.ai/v1", "description": "Production API"},
            {"url": "https://staging-api.lukhas.ai/v1", "description": "Staging API"},
            {"url": "http://localhost:8080", "description": "Local development"},
        ]

        # Add tags with descriptions
        spec["tags"] = [
            {
                "name": "orchestration",
                "description": "Multi-model AI orchestration endpoints",
            },
            {
                "name": "healthcare",
                "description": "HIPAA-compliant healthcare AI endpoints",
            },
            {"name": "streaming", "description": "Real-time streaming endpoints"},
            {
                "name": "functions",
                "description": "Function registration and management",
            },
            {"name": "onboarding", "description": "User onboarding and account setup"},
            {"name": "monitoring", "description": "API metrics and health monitoring"},
        ]

        # Add custom examples
        self._add_custom_examples(spec)

        # Add error response schemas
        self._add_error_schemas(spec)

        return spec

    def _add_custom_examples(self, spec: dict[str, Any]):
        """Add custom examples to endpoints"""

        examples = {
            "orchestration_request": {
                "summary": "Multi-model consensus request",
                "value": {
                    "prompt": "Explain quantum computing in simple terms",
                    "strategy": "consensus",
                    "providers": ["openai", "anthropic", "google"],
                    "enable_functions": True,
                    "max_latency_ms": 5000,
                    "max_cost": 0.10,
                    "min_confidence": 0.8,
                    "context_type": "educational",
                },
            },
            "healthcare_request": {
                "summary": "Healthcare-compliant AI request",
                "value": {
                    "prompt": "Analyze symptoms: fatigue, headache, fever",
                    "patient_context": {
                        "age_range": "30-40",
                        "gender": "female",
                        "medical_history": "none_reported",
                    },
                    "consent_verified": True,
                    "phi_scrubbed": True,
                    "clinical_context": "symptom_analysis",
                    "hipaa_compliant": True,
                    "audit_required": True,
                    "strategy": "consensus",
                    "providers": ["anthropic", "openai"],
                    "enable_functions": False,
                },
            },
            "streaming_request": {
                "summary": "Real-time streaming request",
                "value": {
                    "prompt": "Write a creative story about AI consciousness",
                    "provider": "openai",
                    "enable_functions": False,
                    "temperature": 0.8,
                    "max_tokens": 500,
                },
            },
            "onboarding_start": {
                "summary": "Start user onboarding",
                "value": {
                    "user_info": {
                        "email": "user@example.com",
                        "organization": "Healthcare Corp",
                        "role": "Data Scientist",
                    },
                    "referral_code": "PARTNER2024",
                    "marketing_source": "website",
                },
            },
        }

        # Add examples to components
        if "components" not in spec:
            spec["components"] = {}
        if "examples" not in spec["components"]:
            spec["components"]["examples"] = {}

        spec["components"]["examples"].update(examples)

    def _add_error_schemas(self, spec: dict[str, Any]):
        """Add comprehensive error response schemas"""

        error_schemas = {
            "ValidationError": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "validation_errors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "message": {"type": "string"},
                                "field": {"type": "string"},
                                "severity": {"type": "string"},
                            },
                        },
                    },
                    "request_id": {"type": "string"},
                },
            },
            "RateLimitError": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "limit_type": {"type": "string"},
                    "limit": {"type": "integer"},
                    "reset_time": {"type": "string"},
                    "retry_after": {"type": "integer"},
                },
            },
            "SecurityError": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "security_violation": {"type": "string"},
                    "threat_level": {"type": "string"},
                    "blocked": {"type": "boolean"},
                },
            },
        }

        if "schemas" not in spec["components"]:
            spec["components"]["schemas"] = {}

        spec["components"]["schemas"].update(error_schemas)

    def _generate_static_spec(self) -> dict[str, Any]:
        """Generate static OpenAPI spec when FastAPI is not available"""
        return {
            "openapi": "3.0.2",
            "info": {
                "title": "LUKHAS AI Multi-Model Orchestration API",
                "version": "2.0.0",
                "description": "Advanced multi-model AI orchestration with enterprise security",
                "contact": {
                    "name": "LUKHAS AI Support",
                    "email": "support@lukhas.ai",
                    "url": "https://lukhas.ai/support",
                },
                "license": {
                    "name": "LUKHAS AI Proprietary License",
                    "url": "https://lukhas.ai/license",
                },
            },
            "servers": [{"url": "https://api.lukhas.ai/v1", "description": "Production API"}],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {"APIKeyAuth": {"type": "http", "scheme": "bearer"},
            },
        }

    def generate_sdk_info(self) -> dict[str, Any]:
        """Generate SDK generation information"""
        return {
            "sdk_languages": [
                {
                    "language": "Python",
                    "package_name": "lukhas-ai",
                    "github_url": "https://github.com/lukhas-ai/python-sdk",
                    "installation": "pip install lukhas-ai",
                    "example": """
from lukhas_ai import LukahasClient

client = LukahasClient(api_key="your-api-key")
response = client.orchestrate(
    prompt="Explain quantum computing",
    strategy="consensus"
)
print(response.content)
                    """,
                },
                {
                    "language": "JavaScript/TypeScript",
                    "package_name": "@lukhas-ai/sdk",
                    "github_url": "https://github.com/lukhas-ai/js-sdk",
                    "installation": "npm install @lukhas-ai/sdk",
                    "example": """
import { LukahasClient } from '@lukhas-ai/sdk';

const client = new LukahasClient({ apiKey: 'your-api-key' });
const response = await client.orchestrate({
  prompt: 'Explain quantum computing',
  strategy: 'consensus'
});
console.log(response.content);
                    """,
                },
                {
                    "language": "cURL",
                    "description": "Direct HTTP API calls",
                    "example": """
curl -X POST https://api.lukhas.ai/v1/orchestrate \\
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Explain quantum computing",
    "strategy": "consensus",
    "providers": ["openai", "anthropic"]
  }'
                    """,
                },
            ]
        }

    def generate_comprehensive_guide(self) -> dict[str, Any]:
        """Generate comprehensive API usage guide"""
        return {
            "quick_start": {
                "title": "Quick Start Guide",
                "steps": [
                    {
                        "step": 1,
                        "title": "Get API Key",
                        "description": "Sign up at lukhas.ai and get your API key from the dashboard",
                        "code": "# Your API key will look like:\n# lukhas-tier4-abc123def456...",
                    },
                    {
                        "step": 2,
                        "title": "Make Your First Request",
                        "description": "Send a simple orchestration request",
                        "code": """
import requests

response = requests.post(
    "https://api.lukhas.ai/v1/orchestrate",
    headers={"Authorization": "Bearer your-api-key"},
    json={"prompt": "Hello, LUKHAS AI!"}
)
print(response.json())
                        """,
                    },
                    {
                        "step": 3,
                        "title": "Explore Advanced Features",
                        "description": "Try multi-model consensus and function calling",
                        "code": """
response = requests.post(
    "https://api.lukhas.ai/v1/orchestrate",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "prompt": "Compare renewable energy options",
        "strategy": "consensus",
        "providers": ["openai", "anthropic", "google"],
        "enable_functions": True,
        "min_confidence": 0.8
    }
)
                        """,
                    },
                ],
            },
            "best_practices": {
                "title": "Best Practices",
                "practices": [
                    {
                        "title": "Use Appropriate Strategies",
                        "description": "Choose orchestration strategies based on your use case",
                        "recommendations": [
                            "consensus: For critical decisions requiring high accuracy",
                            "single_best: For fast responses with good quality",
                            "parallel: For comparing different model outputs",
                            "fallback: For maximum reliability with backup options",
                        ],
                    },
                    {
                        "title": "Optimize Costs",
                        "description": "Manage API costs effectively",
                        "recommendations": [
                            "Set appropriate max_cost limits",
                            "Use caching for repeated requests",
                            "Choose providers based on cost/quality trade-offs",
                            "Monitor daily usage and costs",
                        ],
                    },
                    {
                        "title": "Healthcare Compliance",
                        "description": "Follow healthcare compliance guidelines",
                        "recommendations": [
                            "Always scrub PHI before sending requests",
                            "Verify patient consent before processing",
                            "Use healthcare-specific endpoints",
                            "Maintain comprehensive audit trails",
                            "Use only approved IP addresses for healthcare",
                        ],
                    },
                ],
            },
            "troubleshooting": {
                "title": "Common Issues and Solutions",
                "issues": [
                    {
                        "problem": "Rate limit exceeded",
                        "solution": "Implement exponential backoff and respect rate limits",
                        "code": """
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
                        """,
                    },
                    {
                        "problem": "Low consensus confidence",
                        "solution": "Adjust strategy or add more providers",
                        "code": """
# If confidence is low, try adding more providers
request = {
    "prompt": "your prompt",
    "strategy": "consensus",
    "providers": ["openai", "anthropic", "google", "perplexity"],
    "min_confidence": 0.7  # Lower threshold if needed
}
                        """,
                    },
                    {
                        "problem": "Healthcare validation errors",
                        "solution": "Ensure compliance requirements are met",
                        "code": """
# Healthcare request must include all required fields
healthcare_request = {
    "prompt": "clinical prompt with PHI scrubbed",
    "consent_verified": True,  # Required
    "phi_scrubbed": True,      # Required
    "hipaa_compliant": True,   # Required
    "audit_required": True     # Required
}
                        """,
                    },
                ],
            },
        }


def generate_api_documentation(app: Optional[Any] = None) -> dict[str, Any]:
    """Generate comprehensive API documentation"""
    generator = APIDocumentationGenerator(app)

    documentation = {
        "openapi_spec": generator.generate_openapi_spec(),
        "sdk_info": generator.generate_sdk_info(),
        "comprehensive_guide": generator.generate_comprehensive_guide(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
    }

    logger.info("📚 API documentation generated successfully")
    return documentation


def export_openapi_spec(app: Optional[Any] = None, output_file: str = "openapi.json"):
    """Export OpenAPI specification to file"""
    generator = APIDocumentationGenerator(app)
    spec = generator.generate_openapi_spec()

    with open(output_file, "w") as f:
        json.dump(spec, f, indent=2)

    logger.info(f"📄 OpenAPI specification exported to {output_file}")


# Example usage and testing
if __name__ == "__main__":
    # Generate sample documentation
    docs = generate_api_documentation()

    # Export OpenAPI spec
    export_openapi_spec(output_file="lukhas_api_openapi.json")

    print("Documentation generated successfully!")
    print(f"OpenAPI spec has {len(docs['openapi_spec'].get('paths', {)}))} endpoints")
    print(f"SDK examples for {len(docs['sdk_info']['sdk_languages'])} languages")

# Export main components
__all__ = [
    "APIDocumentationGenerator",
    "export_openapi_spec",
    "generate_api_documentation",
]
