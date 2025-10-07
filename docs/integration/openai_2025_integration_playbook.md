---
status: wip
type: documentation
owner: unknown
module: integration
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# OpenAI Integration Playbook - 2025 Edition

## Overview: Modern OpenAI Integration for LUKHAS AI

This playbook provides complete integration patterns for OpenAI's 2025 APIs, optimized for cost efficiency, safety, and performance in production commerce applications.

## Core API Strategy

### Primary Models (2025 Aligned)
- **Text Generation**: `gpt-4.1` (latest reasoning model)
- **Image Generation**: `dall-e-3` with `hd` quality for advertising creative
- **Image Understanding**: `gpt-4-vision-preview` for content analysis
- **Moderation**: `omni-moderation-latest` for all user-facing content
- **Embeddings**: `text-embedding-3-large` for semantic matching

### API Endpoints
```python
# 2025 Responses API (Structured Outputs)
OPENAI_BASE_URL = "https://api.openai.com/v1"
RESPONSES_ENDPOINT = "/responses"  # New structured output endpoint
LEGACY_CHAT_ENDPOINT = "/chat/completions"  # Fallback
```

## Cost Optimization Strategies

### 1. Cache-First Creative Pipeline
```python
import hashlib
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreativeRequest:
    opportunity_id: str
    product_category: str
    target_audience: str
    brand_voice: str

def get_cache_key(request: CreativeRequest) -> str:
    """Generate deterministic cache key for reusable creative"""
    content = f"{request.product_category}:{request.target_audience}:{request.brand_voice}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]

async def generate_creative_cached(request: CreativeRequest) -> dict:
    cache_key = get_cache_key(request)
    
    # Check Redis cache first
    cached = await redis_client.get(f"creative:{cache_key}")
    if cached:
        return json.loads(cached)
    
    # Generate new creative
    creative = await generate_with_openai(request)
    
    # Cache for 24 hours (reuse across similar opportunities)
    await redis_client.setex(f"creative:{cache_key}", 86400, json.dumps(creative))
    return creative
```

### 2. Intelligent Batching
```python
class BatchProcessor:
    def __init__(self, batch_size=10, timeout_seconds=2):
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.pending_requests = []
        
    async def add_request(self, request) -> dict:
        """Add request to batch, process when full or timeout"""
        self.pending_requests.append(request)
        
        if len(self.pending_requests) >= self.batch_size:
            return await self._process_batch()
        
        # Set timeout for partial batches
        await asyncio.sleep(self.timeout_seconds)
        if self.pending_requests:
            return await self._process_batch()
    
    async def _process_batch(self) -> list[dict]:
        """Process accumulated requests in single API call"""
        if not self.pending_requests:
            return []
            
        # Combine prompts for batch processing
        batch_prompt = self._create_batch_prompt(self.pending_requests)
        response = await openai_client.responses.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": batch_prompt}],
            response_format={"type": "json_object"}
        )
        
        results = json.loads(response.choices[0].message.content)
        self.pending_requests.clear()
        return results["responses"]
```

## Safety & Moderation Pipeline

### Content Moderation Chain
```python
async def moderate_content_chain(content: str) -> dict:
    """Multi-layer content moderation with OpenAI and custom rules"""
    
    # Layer 1: OpenAI Moderation
    moderation = await openai_client.moderations.create(
        input=content,
        model="omni-moderation-latest"
    )
    
    if moderation.results[0].flagged:
        return {
            "approved": False,
            "reason": "openai_moderation",
            "categories": moderation.results[0].categories
        }
    
    # Layer 2: Custom Business Rules
    custom_check = await check_custom_moderation(content)
    if not custom_check["approved"]:
        return custom_check
    
    # Layer 3: Brand Safety
    brand_safe = await check_brand_safety(content)
    return brand_safe

async def check_custom_moderation(content: str) -> dict:
    """Custom moderation rules for commerce content"""
    flagged_patterns = [
        r'\b(get rich quick|guaranteed money|no risk)\b',
        r'\b(limited time|act now|hurry)\b',  # Urgency manipulation
        r'\b(secret|hidden|insider)\b',       # Exclusivity manipulation
    ]
    
    for pattern in flagged_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return {
                "approved": False,
                "reason": "manipulative_language",
                "pattern": pattern
            }
    
    return {"approved": True}
```

## Structured Output Implementation

### Responses API Integration (2025)
```python
from pydantic import BaseModel, Field
from typing import Literal

class OpportunityResponse(BaseModel):
    """Structured response for DAST provider"""
    opportunities: list[dict] = Field(..., max_items=5)
    reasoning: str = Field(..., max_length=200)
    confidence: float = Field(..., ge=0.0, le=1.0)
    safety_flags: list[str] = Field(default_factory=list)

class NIASCreative(BaseModel):
    """Structured creative output for NIAS"""
    copy: str = Field(..., max_length=90, description="Ad copy under 90 chars")
    image_prompt: str = Field(..., max_length=400, description="DALL-E prompt")
    tone: Literal["informative", "playful", "premium", "urgent"] = "informative"
    call_to_action: str = Field(..., max_length=20)

async def get_structured_opportunities(intent: str) -> OpportunityResponse:
    """Get opportunities with guaranteed schema compliance"""
    
    response = await openai_client.responses.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a DAST provider finding relevant commercial opportunities."
            },
            {
                "role": "user", 
                "content": f"Find opportunities for: {intent}"
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "opportunity_response",
                "schema": OpportunityResponse.model_json_schema()
            }
        }
    )
    
    return OpportunityResponse.model_validate_json(
        response.choices[0].message.content
    )
```

## Error Handling & Resilience

### Exponential Backoff with Circuit Breaker
```python
import asyncio
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery

class OpenAICircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call_with_breaker(self, func, *args, **kwargs):
        """Execute OpenAI call with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN - OpenAI unavailable")
        
        try:
            result = await self._call_with_retry(func, *args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    async def _call_with_retry(self, func, *args, **kwargs):
        """Exponential backoff retry logic"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Exponential backoff: 1s, 2s, 4s
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        if self.last_failure_time is None:
            return True
        return datetime.now() > self.last_failure_time + timedelta(seconds=self.timeout_seconds)
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

## Performance Monitoring

### Comprehensive Metrics Collection
```python
import time
from dataclasses import dataclass
from typing import Dict, List
import logging

@dataclass
class APIMetrics:
    endpoint: str
    model: str
    duration_ms: int
    tokens_used: int
    cost_usd: float
    success: bool
    error_type: str = None

class OpenAIMetricsCollector:
    def __init__(self):
        self.metrics: List[APIMetrics] = []
        self.model_costs = {
            "gpt-4.1": {"input": 0.00001, "output": 0.00003},  # Per token
            "dall-e-3": {"hd": 0.080, "standard": 0.040},      # Per image
            "text-embedding-3-large": {"input": 0.00000013}    # Per token
        }
    
    async def track_api_call(self, func, model: str, endpoint: str, *args, **kwargs):
        """Wrap OpenAI calls with metrics tracking"""
        start_time = time.time()
        
        try:
            response = await func(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Calculate tokens and cost
            tokens_used = self._extract_token_usage(response)
            cost_usd = self._calculate_cost(model, tokens_used, endpoint)
            
            # Record successful call
            self.metrics.append(APIMetrics(
                endpoint=endpoint,
                model=model,
                duration_ms=duration_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                success=True
            ))
            
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Record failed call
            self.metrics.append(APIMetrics(
                endpoint=endpoint,
                model=model,
                duration_ms=duration_ms,
                tokens_used=0,
                cost_usd=0.0,
                success=False,
                error_type=type(e).__name__
            ))
            
            raise e
    
    def get_performance_summary(self, last_n_minutes=60) -> Dict:
        """Generate performance summary for monitoring dashboard"""
        cutoff_time = time.time() - (last_n_minutes * 60)
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {"status": "no_data"}
        
        total_calls = len(recent_metrics)
        successful_calls = len([m for m in recent_metrics if m.success])
        total_cost = sum(m.cost_usd for m in recent_metrics)
        avg_latency = sum(m.duration_ms for m in recent_metrics) / total_calls
        
        return {
            "status": "healthy" if successful_calls / total_calls > 0.95 else "degraded",
            "total_calls": total_calls,
            "success_rate": successful_calls / total_calls,
            "total_cost_usd": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "cost_per_success": round(total_cost / successful_calls, 4) if successful_calls > 0 else 0
        }
```

## Integration Code Examples

### Complete DAST Provider Implementation
```python
class OpenAIDastProvider:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.circuit_breaker = OpenAICircuitBreaker()
        self.metrics = OpenAIMetricsCollector()
    
    async def get_opportunities(
        self, 
        intent: str, 
        context: dict = None
    ) -> List[dict]:
        """Get commercial opportunities for user intent"""
        
        async def _api_call():
            response = await self.client.responses.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_dast_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": self._format_intent_prompt(intent, context)
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "opportunities",
                        "schema": self._get_opportunity_schema()
                    }
                },
                max_tokens=2000
            )
            return response
        
        # Execute with circuit breaker and metrics
        response = await self.circuit_breaker.call_with_breaker(
            self.metrics.track_api_call,
            _api_call,
            "gpt-4.1",
            "responses"
        )
        
        # Parse and validate response
        result = json.loads(response.choices[0].message.content)
        return result.get("opportunities", [])
```

### Complete NIAS Creative Implementation
```python
class OpenAINiasCreative:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.cache = CreativeCache()
    
    async def generate_creative(
        self,
        opportunity: dict,
        user_context: dict = None
    ) -> dict:
        """Generate advertising creative for opportunity"""
        
        # Check cache first
        cache_key = self._get_cache_key(opportunity)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Generate copy
        copy_response = await self.client.responses.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": self._get_copy_system_prompt()
                },
                {
                    "role": "user",
                    "content": self._format_copy_prompt(opportunity)
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ad_copy",
                    "schema": NIASCreative.model_json_schema()
                }
            }
        )
        
        copy_data = json.loads(copy_response.choices[0].message.content)
        
        # Generate image if needed
        if opportunity.get("needs_visual", True):
            image_response = await self.client.images.generate(
                model="dall-e-3",
                prompt=copy_data["image_prompt"],
                size="1024x1024",
                quality="hd",
                n=1
            )
            copy_data["image_url"] = image_response.data[0].url
        
        # Moderate content
        moderation_result = await moderate_content_chain(copy_data["copy"])
        if not moderation_result["approved"]:
            raise ValueError(f"Content moderation failed: {moderation_result['reason']}")
        
        # Cache result
        await self.cache.set(cache_key, copy_data, ttl_seconds=86400)
        
        return copy_data
```

## Deployment Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT_SECONDS=30

# Cost Controls
OPENAI_DAILY_BUDGET_USD=100.00
OPENAI_RATE_LIMIT_RPM=1000
OPENAI_ALERT_THRESHOLD_USD=80.00

# Performance
OPENAI_CIRCUIT_BREAKER_FAILURES=5
OPENAI_CIRCUIT_BREAKER_TIMEOUT=60
REDIS_CACHE_URL=redis://localhost:6379/1
```

### Production Checklist

#### Pre-Launch
- [ ] API keys secured in environment (never hardcoded)
- [ ] Rate limiting configured (respect OpenAI limits)
- [ ] Cost monitoring alerts active
- [ ] Circuit breaker tested with failure scenarios
- [ ] Content moderation chain validated
- [ ] Cache hit rates >70% for creative generation
- [ ] Error handling covers all OpenAI exceptions
- [ ] Metrics dashboard operational
- [ ] Backup provider configured (Claude/Gemini)

#### Monitoring
- [ ] Track success rate >99.5%
- [ ] Monitor average latency <2000ms
- [ ] Alert on daily cost >$80
- [ ] Track cache hit rate >70%
- [ ] Monitor token usage efficiency
- [ ] Track content moderation rejection rate
- [ ] Alert on circuit breaker activation

#### Optimization
- [ ] Batch similar requests where possible
- [ ] Cache responses for 24+ hours
- [ ] Use cheaper models for simple tasks
- [ ] Compress prompts while maintaining quality
- [ ] Implement smart retry logic
- [ ] Monitor and optimize token usage
- [ ] A/B test prompt variations for cost/quality

## Cost Management

### Daily Budget Enforcement
```python
class CostController:
    def __init__(self, daily_budget_usd: float):
        self.daily_budget = daily_budget_usd
        self.today_spend = 0.0
        self.last_reset = datetime.now().date()
    
    async def check_budget_before_call(self, estimated_cost: float):
        """Check if call would exceed daily budget"""
        self._reset_if_new_day()
        
        if self.today_spend + estimated_cost > self.daily_budget:
            raise BudgetExceededException(
                f"Call would exceed daily budget: {self.today_spend + estimated_cost} > {self.daily_budget}"
            )
    
    def record_spend(self, cost: float):
        """Record actual spend after API call"""
        self.today_spend += cost
        
        # Alert at 80% of budget
        if self.today_spend > self.daily_budget * 0.8:
            logger.warning(f"OpenAI spend at {self.today_spend}/{self.daily_budget} (80% of budget)")
```

This playbook provides production-ready OpenAI integration patterns optimized for 2025 APIs, with comprehensive cost controls, safety measures, and performance monitoring suitable for a T4-level commerce platform.