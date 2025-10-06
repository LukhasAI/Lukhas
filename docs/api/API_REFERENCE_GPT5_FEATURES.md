---
status: wip
type: documentation
---
# GPT5 Features API Reference

## Table of Contents
1. [Signal-to-Prompt Modulation](#signal-to-prompt-modulation)
2. [Homeostasis Controller](#homeostasis-controller)
3. [Feedback Cards System](#feedback-cards-system)
4. [Optimized OpenAI Client](#optimized-openai-client)
5. [Audit Trail System](#audit-trail-system)
6. [Personal Symbol Dictionary](#personal-symbol-dictionary)
7. [Integration Examples](#integration-examples)

---

## Signal-to-Prompt Modulation

### Overview
Maps system signals (stress, novelty, risk) to OpenAI API parameters for adaptive behavior.

### Basic Usage
```python
from orchestration.signals.prompt_modulator import PromptModulator, Signal, SignalType

# Initialize modulator
modulator = PromptModulator()

# Create signals
signals = [
    Signal(SignalType.STRESS, level=0.7, source="system"),
    Signal(SignalType.NOVELTY, level=0.4, source="detector")
]

# Get modulated parameters
params = modulator.combine_signals(signals)
# Returns: {'temperature': 0.3, 'top_p': 0.5, 'max_output_tokens': 800, ...}

# Apply to OpenAI call
openai_kwargs = modulator.apply_to_openai_kwargs(base_kwargs, params)
```

### Configuration
```python
# Custom policy
policy = {
    "signals": [
        {"name": "stress", "weight": 0.9, "cooldown_ms": 800},
        {"name": "novelty", "weight": 0.6, "cooldown_ms": 500}
    ],
    "bounds": {
        "temperature": [0.0, 1.0],
        "top_p": [0.1, 1.0]
    }
}
modulator = PromptModulator(policy=policy)
```

### Signal Types
- `STRESS`: System under load
- `ALIGNMENT_RISK`: Potential safety concern
- `NOVELTY`: New/unusual input
- `TRUST`: Established user trust
- `URGENCY`: Time-sensitive request
- `AMBIGUITY`: Unclear intent

---

## Homeostasis Controller

### Overview
Manages hormone-like signals to maintain system balance.

### Basic Usage
```python
from orchestration.signals.homeostasis_controller import HomeostasisController
from orchestration.signals.signal_bus import SignalBus

# Initialize
signal_bus = SignalBus()
controller = HomeostasisController(signal_bus)

# Start controller
await controller.start()

# Process events
signals = controller.process_event(
    event_type="resource",
    event_data={"cpu": 0.85, "memory": 0.75},
    source="monitor"
)

# Record feedback
controller.record_feedback(0.8, {"user_satisfied": True})

# Get status
status = controller.get_status()
print(f"State: {status['state']}")
print(f"Stress: {status['stress_level']:.1%}")
```

### Event Types
- `request`: API request metrics
- `error`: Error events
- `resource`: CPU/memory usage
- `drift`: Behavioral drift
- `session`: Session events
- `queue`: Queue depth

### Homeostasis States
- `BALANCED`: Optimal functioning
- `STRESSED`: Under pressure
- `OVERLOADED`: Too much activity
- `UNDERUTILIZED`: Not enough activity
- `RECOVERING`: Returning to balance
- `CRITICAL`: Needs intervention

---

## Feedback Cards System

### Overview
Human-in-the-loop fine-tuning with various feedback types.

### Basic Usage
```python
from feedback.feedback_cards import FeedbackCardsManager, FeedbackCategory

# Initialize
manager = FeedbackCardsManager()

# Create rating card
card = manager.create_rating_card(
    user_input="Explain quantum computing",
    ai_response="Quantum computing uses...",
    category=FeedbackCategory.CLARITY
)

# Submit feedback
manager.submit_feedback(
    card_id=card.card_id,
    rating=4,
    annotation="Good but needs examples",
    user_id="user123"
)

# Get training data
training_cards = manager.get_cards_for_training(
    min_impact=0.3,
    limit=100
)
```

### Feedback Types
- **Rating**: 1-5 star ratings
- **Comparison**: A vs B preference
- **Correction**: Improved response
- **Annotation**: Additional notes
- **Validation**: Yes/No accuracy
- **Freeform**: Open text

### Categories
- `ACCURACY`: Factual correctness
- `HELPFULNESS`: Utility of response
- `SAFETY`: Risk assessment
- `CREATIVITY`: Innovation level
- `CLARITY`: Understandability
- `RELEVANCE`: On-topic alignment
- `COMPLETENESS`: Thoroughness
- `TONE`: Communication style

---

## Optimized OpenAI Client

### Overview
Reduces API costs through caching and rate limiting.

### Basic Usage
```python
from bridge.llm_wrappers.openai_optimized import OptimizedOpenAIClient, CacheStrategy

# Initialize with caching
client = OptimizedOpenAIClient(
    cache_strategy=CacheStrategy.EXACT_MATCH,
    cache_ttl=3600,  # 1 hour
    cache_size=1000
)

# Make cached request
response = await client.complete(
    prompt="What is Python?",
    model="gpt-3.5-turbo",
    max_tokens=100,
    use_cache=True
)

# Batch processing
from bridge.llm_wrappers.openai_optimized import BatchProcessor

batch = BatchProcessor(client)
responses = await batch.process_batch(
    prompts=["Question 1", "Question 2"],
    max_concurrent=5
)

# Get statistics
stats = client.get_statistics()
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
print(f"Cost saved: ${stats['cost_saved']:.4f}")
```

### Cache Strategies
- `NONE`: No caching
- `EXACT_MATCH`: Exact prompt matching
- `SEMANTIC`: Semantic similarity
- `EMBEDDING`: Embedding-based matching

### Rate Limiting
```python
from bridge.llm_wrappers.openai_optimized import RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,
    tokens_per_minute=90000,
    initial_backoff_ms=1000,
    max_backoff_ms=60000
)
client = OptimizedOpenAIClient(rate_config=config)
```

---

## Audit Trail System

### Overview
Complete transparency and traceability for all decisions.

### Basic Usage
```python
from governance.audit_trail import AuditTrail, DecisionType, AuditLevel

# Initialize
audit = AuditTrail(
    audit_level=AuditLevel.DETAILED,
    retention_days=90,
    enable_explanations=True
)

# Log decision
entry = audit.log_decision(
    decision_type=DecisionType.RESPONSE,
    decision="Generated helpful response",
    reasoning="Clear user question",
    confidence=0.85,
    input_data={"prompt": "User question"},
    output_data={"response": "AI response"},
    session_id="session123"
)

# Get explanation
explanation = audit.explain_decision(entry.audit_id)
print(explanation["human"])

# Search audit trail
entries = audit.search(
    decision_type=DecisionType.SAFETY,
    min_confidence=0.7,
    limit=50
)

# Generate transparency report
report = audit.generate_transparency_report("session123")
```

### Decision Types
- `RESPONSE`: AI responses
- `MODERATION`: Content filtering
- `ROUTING`: Request routing
- `CACHING`: Cache decisions
- `SAFETY`: Safety interventions
- `LEARNING`: Model updates
- `CONFIGURATION`: Config changes
- `SYSTEM`: System operations

### Audit Levels
- `MINIMAL`: Basic tracking
- `STANDARD`: Normal operations
- `DETAILED`: Include reasoning
- `FORENSIC`: Full reconstruction

---

## Personal Symbol Dictionary

### Overview
User-specific symbolic communication and personalization.

### Basic Usage
```python
from core.glyph.personal_symbol_dictionary import (
    PersonalSymbolDictionary, SymbolType
)

# Initialize
dictionary = PersonalSymbolDictionary()

# Add personal symbol
symbol = dictionary.add_symbol(
    user_id="user123",
    symbol="🚀",
    meaning="launch project",
    symbol_type=SymbolType.ACTION,
    examples=["Let's 🚀 tomorrow", "Ready to 🚀?"]
)

# Interpret text
interpretation = dictionary.interpret_symbols(
    user_id="user123",
    text="The code is 🌟 but needs 🔨"
)
print(interpretation["translated"])
# Output: "The code is [excellent] but needs [fixing]"

# Learn from usage
dictionary.learn_from_usage(
    user_id="user123",
    symbol="🚀",
    context="project management",
    success=True
)

# Suggest symbols
suggestions = dictionary.suggest_symbols(
    user_id="user123",
    concept="problem",
    limit=5
)
```

### Symbol Types
- `CONCEPT`: Abstract ideas
- `EMOTION`: Feelings/states
- `ACTION`: Commands/actions
- `OBJECT`: Things/entities
- `RELATIONSHIP`: Connections
- `MODIFIER`: Enhancers
- `PERSONAL`: User-specific

### Symbol Evolution
```python
# Merge symbols
compound = dictionary.merge_symbols(
    user_id="user123",
    symbols=["🌟", "🚀"],
    new_symbol="🌟🚀",
    new_meaning="excellent launch"
)

# Export/Import
export = dictionary.export_dictionary("user123")
dictionary.import_dictionary("user456", export)
```

---

## Integration Examples

### Complete Flow Example
```python
import asyncio
from orchestration.signals.signal_bus import SignalBus
from orchestration.signals.homeostasis_controller import HomeostasisController
from orchestration.signals.prompt_modulator import PromptModulator
from bridge.llm_wrappers.openai_optimized import OptimizedOpenAIClient
from governance.audit_trail import AuditTrail, DecisionType
from feedback.feedback_cards import FeedbackCardsManager
from core.glyph.personal_symbol_dictionary import PersonalSymbolDictionary

async def integrated_response(user_id: str, user_input: str):
    # 1. Interpret personal symbols
    dictionary = PersonalSymbolDictionary()
    interpreted = dictionary.interpret_symbols(user_id, user_input)

    # 2. Check system state
    signal_bus = SignalBus()
    homeostasis = HomeostasisController(signal_bus)
    signals = homeostasis.process_event(
        "request",
        {"rate": 10, "response_time": 50},
        "api"
    )

    # 3. Modulate parameters
    modulator = PromptModulator()
    params = modulator.combine_signals(signals)

    # 4. Generate response with caching
    client = OptimizedOpenAIClient()
    base_kwargs = {
        "messages": [{"role": "user", "content": interpreted["translated"]}],
        "model": "gpt-3.5-turbo"
    }
    kwargs = modulator.apply_to_openai_kwargs(base_kwargs, params)
    response = await client.complete(**kwargs)

    # 5. Log to audit trail
    audit = AuditTrail()
    entry = audit.log_decision(
        decision_type=DecisionType.RESPONSE,
        decision="Generated response",
        confidence=interpreted["confidence"],
        input_data={"original": user_input, "interpreted": interpreted},
        output_data={"response": response},
        session_id=f"session_{user_id}"
    )

    # 6. Create feedback card
    feedback = FeedbackCardsManager()
    card = feedback.create_rating_card(
        user_input=user_input,
        ai_response=response["choices"][0]["message"]["content"],
        session_id=f"session_{user_id}"
    )

    return {
        "response": response,
        "audit_id": entry.audit_id,
        "feedback_card_id": card.card_id,
        "symbols_used": interpreted["symbols_found"]
    }

# Run example
async def main():
    result = await integrated_response("user123", "Let's 🚀 the new feature!")
    print(result)

asyncio.run(main())
```

### Monitoring Dashboard
```python
def get_system_dashboard():
    """Get comprehensive system status"""

    # Homeostasis status
    homeostasis = HomeostasisController(SignalBus())
    health = homeostasis.get_status()

    # Cache statistics
    client = OptimizedOpenAIClient()
    cache_stats = client.get_statistics()

    # Audit statistics
    audit = AuditTrail()
    audit_stats = audit.get_statistics()

    # Feedback statistics
    feedback = FeedbackCardsManager()
    feedback_stats = feedback.get_statistics()

    return {
        "system_health": {
            "state": health["state"],
            "stress_level": health["stress_level"],
            "active_hormones": health["active_hormones"]
        },
        "performance": {
            "cache_hit_rate": cache_stats["cache_hit_rate"],
            "tokens_saved": cache_stats["tokens_saved"],
            "cost_saved": cache_stats["cost_saved"]
        },
        "transparency": {
            "total_decisions": audit_stats["total_entries"],
            "average_confidence": audit_stats["average_confidence"],
            "safety_interventions": audit_stats["safety_interventions"]
        },
        "feedback": {
            "total_cards": feedback_stats["total_cards"],
            "completion_rate": feedback_stats["completion_rate"],
            "average_rating": feedback_stats["average_rating"]
        }
    }
```

## Best Practices

1. **Always use caching** for repeated queries
2. **Monitor homeostasis state** for system health
3. **Log critical decisions** to audit trail
4. **Collect feedback** on important responses
5. **Personalize symbols** for frequent users
6. **Review transparency reports** regularly
7. **Tune modulation policies** based on feedback
8. **Export audit trails** for compliance

## Error Handling

All systems include comprehensive error handling:

```python
try:
    response = await client.complete(prompt, use_cache=True)
except openai.RateLimitError:
    # Handled automatically with backoff
    pass
except Exception as e:
    # Log to audit trail
    audit.log_decision(
        decision_type=DecisionType.SYSTEM,
        decision="Error occurred",
        reasoning=str(e),
        confidence=0.0
    )
```

## Performance Considerations

- **Caching**: 40-60% cost reduction typical
- **Rate Limiting**: Prevents API overages
- **Batch Processing**: 5-10x throughput improvement
- **Symbol Dictionary**: <10ms interpretation time
- **Audit Overhead**: <5ms per decision
- **Homeostasis Response**: <100ms typical

## Troubleshooting

### Cache Not Working
```python
# Check cache statistics
stats = client.get_statistics()
if stats["cache_hit_rate"] == 0:
    # Verify cache strategy
    print(client.cache_strategy)
    # Clear and rebuild cache
    client.clear_cache()
```

### High Stress Levels
```python
# Reset homeostasis
controller.reset()
# Adjust thresholds
controller.policy.stress_threshold = 0.8
```

### Missing Audit Entries
```python
# Verify audit level
print(audit.audit_level)
# Check retention
audit.cleanup_old_entries()
```

## Support

For issues or questions:
- Check the [Implementation Summary](./GPT5_AUDIT_IMPLEMENTATION_SUMMARY.md)
- Review the [GPT5 Audit Document](./openai/GPT5_AUDITS_LUKHAS.md)
- Open an issue on GitHub
