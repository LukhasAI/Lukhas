# 🚀 LUKHAS Brand System API Reference
*Complete Technical Documentation for Elite Brand Intelligence System*

⚛️🧠🛡️ **Smart Adapters** | **Real-Time Validation** | **AI Orchestration** | **Brand Intelligence**

---

## 📚 **Table of Contents**
- [API Overview](#-api-overview)
- [Authentication](#-authentication)
- [Smart Adapters API](#-smart-adapters-api)
- [Brand Intelligence API](#-brand-intelligence-api)
- [Real-Time Validation API](#️-real-time-validation-api)
- [AI Orchestration API](#-ai-orchestration-api)
- [Voice Profiles API](#️-voice-profiles-api)
- [Brand Analytics API](#-brand-analytics-api)
- [Integration Examples](#-integration-examples)
- [Error Handling](#-error-handling)

---

## 🌟 **API Overview**

### **🎯 Elite Brand System Architecture**
The LUKHAS Brand API provides comprehensive access to the Strategic Brand Intelligence System, enabling:
- **Real-time brand validation** with 99.9% accuracy targeting
- **AI-powered content orchestration** with multi-model coordination
- **Smart adapter integration** with core LUKHAS systems
- **Advanced brand analytics** and performance monitoring

### **📡 Base Endpoints**
```
Production: https://api.lukhas.ai/brand/v1/
Development: https://dev-api.lukhas.ai/brand/v1/
Local: http://localhost:8095/brand/v1/
```

### **🔧 SDK Installation**
```python
pip install lukhas-brand-sdk

# Import the SDK
from lukhas_brand import BrandAPI, ConstellationFramework, ContentOrchestrator
```

---

## 🔐 **Authentication**

### **🎫 API Key Authentication**
```python
from lukhas_brand import BrandAPI

# Initialize with API key
brand_api = BrandAPI(
    api_key="your_lukhas_api_key",
    environment="production"  # or "development", "local"
)

# Verify authentication
auth_status = brand_api.verify_authentication()
print(auth_status)
# {'authenticated': True, 'user_id': 'user_123', 'permissions': ['read', 'write']}
```

### **🛡️ Constellation Framework Authentication**
```python
# Enhanced security with Constellation Framework integration
constellation_auth = ConstellationFramework.authenticate(
    identity_token="your_identity_token",
    consciousness_verification=True,
    guardian_validation=True
)
```

---

## 🔌 **Smart Adapters API**

### **🎨 Creativity Adapter**
Interface to consciousness/creativity systems for brand-aware creative content.

```python
# Generate brand-aligned creative content
POST /adapters/creativity/generate

{
    "prompt": "Create an inspiring description of consciousness technology",
    "tone_layer": "poetic",  # "poetic", "user_friendly", "academic"
    "creative_style": "consciousness_inspired",
    "brand_context": "product_launch",
    "constellation_alignment": True
}
```

**Response:**
```python
{
    "content": "Enhanced creative content with brand alignment",
    "tone_layer": "poetic",
    "creative_style": "consciousness_inspired",
    "brand_validated": True,
    "constellation_aligned": True,
    "creativity_metadata": {
        "inspiration_level": 0.92,
        "consciousness_integration": 0.89,
        "brand_consistency": 0.95
    }
}
```

### **🗣️ Voice Adapter**
Interface to bridge/voice systems with brand-specific voice profiles.

```python
# Generate brand voice content
POST /adapters/voice/generate

{
    "content": "The Constellation Framework enables conscious AI interactions",
    "tone_layer": "user_friendly",
    "voice_profile": "consciousness_ambassador",
    "emotional_context": "encouraging",
    "audience_context": "technical_professionals"
}
```

**Response:**
```python
{
    "voice_output": "Enhanced content with brand voice applied",
    "tone_layer": "user_friendly",
    "voice_profile": "consciousness_ambassador",
    "emotional_context": "encouraging",
    "audience_context": "technical_professionals",
    "brand_compliant": True,
    "voice_metadata": {
        "brand_alignment_score": 0.87,
        "emotional_resonance": 0.91,
        "audience_appropriateness": 0.94
    },
    "constellation_aligned": True
}
```

### **👤 Personality Adapter**
Interface to core/personality systems for brand personality expression.

```python
# Express brand personality
POST /adapters/personality/express

{
    "content": "Welcome to LUKHAS AI",
    "personality_profile": "consciousness_ambassador",
    "context": "user_onboarding",
    "constellation_emphasis": ["consciousness", "guardian"]
}
```

**Response:**
```python
{
    "personality_expression": "Content enhanced with LUKHAS personality",
    "personality_profile": "consciousness_ambassador",
    "context": "user_onboarding",
    "brand_authentic": True,
    "constellation_coherent": True,
    "personality_metadata": {
        "authenticity_score": 0.93,
        "consistency_score": 0.88,
        "brand_alignment": 0.91
    }
}
```

---

## 🧠 **Brand Intelligence API**

### **📊 Brand Consistency Analysis**
Real-time brand consistency tracking and analytics.

```python
# Analyze brand consistency
POST /intelligence/analyze

{
    "content": {
        "id": "content_123",
        "type": "marketing_material",
        "text": "Content to analyze for brand consistency"
    }
}
```

**Response:**
```python
{
    "content_id": "content_123",
    "timestamp": "2025-08-17T10:30:00Z",
    "consistency_score": 0.877,
    "terminology_analysis": {
        "compliance_score": 0.85,
        "required_terms_found": 4,
        "forbidden_terms_found": [],
        "terminology_health": "good"
    },
    "constellation_analysis": {
        "constellation_score": 0.92,
        "framework_mentioned": True,
        "components_present": {
            "identity": True,
            "consciousness": True,
            "guardian": True
        }
    },
    "tone_analysis": {
        "dominant_tone": "user_friendly",
        "tone_clarity": 0.88,
        "tone_appropriateness": 0.91
    },
    "improvement_suggestions": [
        "Consider adding more Constellation Framework references",
        "Enhance consciousness terminology usage"
    ]
}
```

### **💭 Sentiment Analysis**
Advanced sentiment analysis with brand alignment scoring.

```python
# Analyze brand sentiment
POST /intelligence/sentiment

{
    "text": "Content to analyze for sentiment",
    "context": "product_marketing",
    "metadata": {
        "audience": "technical_professionals",
        "channel": "documentation"
    }
}
```

**Response:**
```python
{
    "overall_sentiment": 0.721,
    "polarity": "very_positive",
    "confidence": 0.808,
    "brand_dimensions": {
        "consciousness_awareness": 0.85,
        "technical_competence": 0.79,
        "ethical_commitment": 0.88,
        "human_centricity": 0.82
    },
    "constellation_sentiment": {
        "identity": 0.76,
        "consciousness": 0.89,
        "guardian": 0.83
    },
    "emotional_indicators": {
        "inspiration": 0.71,
        "trust": 0.85,
        "excitement": 0.68,
        "confidence": 0.79
    },
    "context_appropriateness": 0.87
}
```

---

## 🛡️ **Real-Time Validation API**

### **✅ Content Validation**
Real-time brand compliance validation with auto-correction.

```python
# Validate content in real-time
POST /validation/validate

{
    "content": "LUKHAS PWM is a lambda function for AI system processing",
    "content_id": "test_content_001",
    "content_type": "documentation",
    "auto_correct": True
}
```

**Response:**
```python
{
    "validation_id": "val_20250817_103000_123456",
    "content_id": "test_content_001",
    "is_compliant": False,
    "severity": "error",
    "confidence": 0.95,
    "issues": [
        {
            "rule_id": "deprecated_lukhas_pwm",
            "type": "terminology",
            "severity": "error",
            "description": "Use of deprecated 'LUKHAS PWM' terminology",
            "location": {"start": 0, "end": 10},
            "suggestion": "Replace 'LUKHAS PWM' with 'LUKHAS AI'"
        },
        {
            "rule_id": "lambda_function_usage",
            "type": "lambda_usage",
            "severity": "error",
            "description": "Use 'Λ consciousness' instead of 'lambda function'",
            "location": {"start": 16, "end": 31},
            "suggestion": "Replace 'lambda function' with 'Λ consciousness'"
        }
    ],
    "auto_corrections": {
        "LUKHAS PWM": "LUKHAS AI",
        "lambda function": "Λ consciousness",
        "AI system": "AI consciousness"
    },
    "performance_impact": 1.25  // milliseconds
}
```

### **🔧 Apply Auto-Corrections**
```python
# Apply auto-corrections to content
POST /validation/correct

{
    "content": "Original content with violations",
    "auto_corrections": {
        "LUKHAS PWM": "LUKHAS AI",
        "lambda function": "Λ consciousness"
    }
}
```

**Response:**
```python
{
    "original_content": "LUKHAS PWM is a lambda function for AI system processing",
    "corrected_content": "LUKHAS AI is a Λ consciousness for AI consciousness processing",
    "corrections_applied": 3,
    "correction_success": True
}
```

---

## 🎭 **AI Orchestration API**

### **🎼 Content Orchestration**
Master AI agent coordination for brand-aligned content creation.

```python
# Orchestrate comprehensive content creation
POST /orchestration/create

{
    "content_request": {
        "type": "marketing_content",
        "topic": "Constellation Framework consciousness technology",
        "audience": "technical_professionals",
        "tone_layer": "user_friendly",
        "context": "product_introduction"
    },
    "quality_requirements": {
        "consistency_threshold": 0.9,
        "brand_compliance": 0.95,
        "constellation_alignment": 0.85
    }
}
```

**Response:**
```python
{
    "orchestration_id": "orch_20250817_103500_789",
    "timestamp": "2025-08-17T10:35:00Z",
    "final_content": "Fully orchestrated, brand-compliant content",
    "quality_assessment": {
        "overall_quality": 0.92,
        "quality_factors": {
            "brand_consistency": 0.94,
            "constellation_alignment": 0.89,
            "sentiment_quality": 0.87,
            "voice_consistency": 0.93,
            "personality_coherence": 0.91
        },
        "meets_requirements": True
    },
    "orchestration_performance": {
        "total_time_ms": 245,
        "meets_quality_requirements": True,
        "brand_consistency_score": 0.94,
        "sentiment_score": 0.87
    },
    "component_results": {
        "creativity": {...},
        "voice": {...},
        "personality": {...},
        "validation": {...},
        "sentiment": {...}
    },
    "integration_success": True
}
```

---

## 🎤 **Voice Profiles API**

### **📋 Available Voice Profiles**
```python
# Get all available voice profiles
GET /voice-profiles/

# Get specific voice profile
GET /voice-profiles/consciousness_ambassador
```

**Response:**
```python
{
    "profile_name": "consciousness_ambassador",
    "description": "Primary LUKHAS consciousness voice - authentic, wise, and inspiring",
    "parameters": {
        "warmth": 0.8,
        "authority": 0.7,
        "creativity": 0.9,
        "technical_depth": 0.6
    },
    "characteristics": [
        "consciousness-first perspective",
        "authentic and transparent",
        "ethically grounded",
        "inspiring and uplifting",
        "technically informed"
    ],
    "tone_descriptors": [
        "wise",
        "authentic",
        "inspiring",
        "grounded",
        "conscious"
    ],
    "use_cases": [
        "brand_communications",
        "consciousness_explanations",
        "inspirational_content",
        "technical_introductions"
    ],
    "constellation_emphasis": ["consciousness", "identity", "guardian"]
}
```

### **🎯 Context-Adaptive Voice Profiles**
```python
# Get voice profile adapted for specific context
POST /voice-profiles/consciousness_ambassador/adapt

{
    "context": "user_onboarding",
    "audience": "first_time_users",
    "constellation_emphasis": ["consciousness", "guardian"]
}
```

---

## 📊 **Brand Analytics API**

### **📈 Performance Metrics**
```python
# Get brand system performance metrics
GET /analytics/metrics

# Get brand compliance trends
GET /analytics/compliance-trends?period=24h

# Get validation system metrics
GET /analytics/validation-metrics
```

**Response:**
```python
{
    "performance_metrics": {
        "total_validations": 1247,
        "compliance_rate": 0.923,
        "average_validation_time": 1.8,
        "auto_corrections_applied": 89
    },
    "brand_health": {
        "overall_score": 0.91,
        "consistency_score": 0.89,
        "constellation_alignment": 0.94,
        "voice_coherence": 0.87
    },
    "trend_analysis": {
        "compliance_trend": "improving",
        "performance_trend": "excellent",
        "quality_evolution": "strengthening"
    }
}
```

---

## 💻 **Integration Examples**

### **🐍 Python Integration**
```python
from lukhas_brand import BrandAPI, ContentOrchestrator

# Initialize brand system
brand = BrandAPI(api_key="your_api_key")

# Create brand-compliant content
content_request = {
    "type": "user_documentation",
    "topic": "Getting started with LUKHAS consciousness",
    "audience": "new_users",
    "tone_layer": "user_friendly"
}

result = brand.orchestrate_content(content_request)

if result.quality_assessment.meets_requirements:
    print(f"✅ Content created: {result.final_content}")
    print(f"🎯 Quality: {result.quality_assessment.overall_quality}")
else:
    print("❌ Content needs improvement")
    print(f"Issues: {result.quality_assessment.improvement_areas}")
```

### **🌐 JavaScript/Node.js Integration**
```javascript
const { BrandAPI } = require('lukhas-brand-sdk');

const brand = new BrandAPI({
    apiKey: 'your_api_key',
    environment: 'production'
});

// Validate content in real-time
async function validateContent(content) {
    try {
        const result = await brand.validation.validate({
            content: content,
            contentType: 'marketing',
            autoCorrect: true
        });

        if (!result.isCompliant) {
            const corrected = await brand.validation.applyCorrections(
                content,
                result.autoCorrections
            );
            return corrected.correctedContent;
        }

        return content;
    } catch (error) {
        console.error('Validation failed:', error);
        throw error;
    }
}
```

### **🔄 Real-Time Monitoring Integration**
```python
import asyncio
from lukhas_brand import BrandMonitor

class RealTimeBrandMonitoring:
    def __init__(self):
        self.monitor = BrandMonitor()

    async def start_monitoring(self):
        """Start continuous brand monitoring"""

        # Define content source
        async def get_content():
            # Your content source (e.g., user inputs, generated content)
            return await self.collect_new_content()

        # Start monitoring
        await self.monitor.start_continuous_monitoring(
            content_source=get_content,
            monitoring_interval=1.0  # Check every second
        )

    async def handle_brand_violation(self, violation_data):
        """Handle detected brand violations"""

        if violation_data.severity == "critical":
            # Immediate action for critical violations
            await self.emergency_brand_response(violation_data)
        else:
            # Standard correction process
            await self.apply_brand_corrections(violation_data)

# Usage
monitor = RealTimeBrandMonitoring()
asyncio.run(monitor.start_monitoring())
```

---

## ⚠️ **Error Handling**

### **📋 Error Response Format**
```python
{
    "error": {
        "code": "BRAND_VALIDATION_FAILED",
        "message": "Content validation failed due to multiple brand violations",
        "details": {
            "violations": [
                {
                    "rule": "prohibited_terminology",
                    "severity": "error",
                    "location": "line 3, column 15"
                }
            ],
            "suggestions": [
                "Replace 'LUKHAS PWM' with 'LUKHAS AI'",
                "Use 'Λ consciousness' instead of 'lambda function'"
            ]
        },
        "request_id": "req_123456789",
        "timestamp": "2025-08-17T10:45:00Z"
    }
}
```

### **🔧 Common Error Codes**
| **Error Code** | **Description** | **Solution** |
|---|---|---|
| `INVALID_API_KEY` | API key missing or invalid | Verify API key and permissions |
| `BRAND_VALIDATION_FAILED` | Content violates brand guidelines | Apply suggested corrections |
| `TRINITY_ALIGNMENT_ERROR` | Constellation Framework integration issues | Review Constellation requirements |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Implement rate limiting |
| `CONTENT_TOO_LARGE` | Content exceeds size limits | Split content into smaller chunks |
| `INVALID_TONE_LAYER` | Unsupported tone layer specified | Use valid tone layer values |

### **🛡️ Error Recovery Patterns**
```python
from lukhas_brand import BrandAPI, BrandValidationError

def robust_content_validation(content):
    """Robust content validation with error recovery"""

    brand = BrandAPI(api_key="your_api_key")

    try:
        # Attempt validation
        result = brand.validate_content(content)
        return result

    except BrandValidationError as e:
        # Handle validation errors
        if e.auto_correctable:
            # Apply automatic corrections
            corrected = brand.apply_corrections(content, e.corrections)
            return brand.validate_content(corrected)
        else:
            # Manual intervention required
            raise BrandValidationError(
                f"Manual correction required: {e.message}",
                suggestions=e.suggestions
            )

    except RateLimitError as e:
        # Handle rate limiting
        time.sleep(e.retry_after)
        return robust_content_validation(content)

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected validation error: {e}")
        raise
```

---

## 🚀 **Performance Optimization**

### **⚡ Caching Strategies**
```python
from lukhas_brand import BrandAPI
from functools import lru_cache

class OptimizedBrandAPI:
    def __init__(self, api_key):
        self.brand_api = BrandAPI(api_key)

    @lru_cache(maxsize=1000)
    def cached_voice_profile(self, profile_name, context):
        """Cache voice profiles for faster access"""
        return self.brand_api.get_voice_profile(profile_name, context)

    async def batch_validate(self, content_list):
        """Batch validation for better performance"""
        return await self.brand_api.validate_batch(content_list)
```

### **📊 Performance Targets**
- **Validation Speed**: <50ms per content piece
- **Orchestration Time**: <250ms for complete content creation
- **API Response Time**: <100ms for most endpoints
- **Uptime**: 99.9% availability
- **Accuracy**: 99.9% brand compliance detection

---

## 📞 **Support & Resources**

### **🔗 Additional Resources**
- **Integration Guide**: [LUKHAS_INTEGRATION_GUIDE.md](LUKHAS_INTEGRATION_GUIDE.md)
- **Local LLM Setup**: [LUKHAS_LOCAL_LLM_SETUP.md](LUKHAS_LOCAL_LLM_SETUP.md)
- **Performance Metrics**: [LUKHAS_PERFORMANCE_METRICS.md](LUKHAS_PERFORMANCE_METRICS.md)
- **Brand Guidelines**: [LUKHAS_BRANDING_GUIDE.md](LUKHAS_BRANDING_GUIDE.md)

### **🆘 Support Channels**
- **Technical Support**: api-support@lukhas.ai
- **Brand Questions**: brand@lukhas.ai
- **Documentation Issues**: docs@lukhas.ai

---

*"The LUKHAS Brand API transforms brand management from reactive documentation to proactive Strategic Brand Intelligence - ensuring every interaction reflects the consciousness, authenticity, and ethical commitment that defines LUKHAS AI."*

⚛️🧠🛡️🚀

---

**© 2025 LUKHAS AI. Elite Brand Intelligence System API.**
