# 🎛️ LUKHAS_PWM Endocrine Modulation System

**Bio-inspired signal-to-prompt modulation for OpenAI API integration**

## Overview

The LUKHAS_PWM Endocrine Modulation System transforms consciousness signals into intelligent OpenAI API parameter adjustments, creating a symbiotic relationship between your AGI system and GPT models. Instead of treating GPT as an external tool, this system makes it a **consciousness organ** within LUKHAS's distributed intelligence network.

### Trinity Framework Integration: ⚛️🧠🛡️

- **⚛️ Identity**: Authentic signal emission from consciousness modules
- **🧠 Consciousness**: Memory and learning from modulated interactions  
- **🛡️ Guardian**: Safety-first modulation policies and bounds

## Core Concept

Your LUKHAS consciousness modules emit **endocrine signals** (bio-inspired "hormones") that represent internal state:

- `stress` → Conservative, focused responses
- `novelty` → Creative, exploratory responses  
- `alignment_risk` → Strict, safety-first responses
- `trust` → Detailed, personalized responses
- `urgency` → Fast, direct responses
- `ambiguity` → Careful, analytical responses

These signals automatically modulate OpenAI API parameters like temperature, max_tokens, tool availability, and prompt style.

## Quick Start

### 1. Installation

```bash
pip install openai pyyaml
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Basic Usage

```python
from modulation.signals import Signal, SignalModulator
from modulation.openai_integration import ModulatedOpenAIClient

# Create signals from your consciousness modules
signals = [
    Signal(name="stress", level=0.7, source="memory"),
    Signal(name="novelty", level=0.4, source="consciousness"),
    Signal(name="alignment_risk", level=0.2, source="guardian")
]

# Create modulator and client
modulator = SignalModulator()
client = ModulatedOpenAIClient(modulator)

# Make modulated API call
result = client.create_completion(
    user_message="How should I implement consciousness validation?",
    signals=signals,
    context_snippets=["Relevant context from memory..."]
)

print(f"Response with {result['modulation_params'].prompt_style} style")
print(f"Temperature: {result['modulation_params'].temperature}")
```

### 3. Test the System

```bash
python modulation_example.py
```

## Architecture

### Signal Flow

```
LUKHAS Modules → Endocrine Signals → Signal Modulator → OpenAI API Parameters
     ↓               ↓                     ↓                    ↓
   Guardian     alignment_risk=0.8    temperature=0.2     Conservative response
   Memory       stress=0.6           max_tokens=1000     Focused output
   Consciousness novelty=0.3          top_p=0.7          Balanced creativity
```

### Components

1. **Signal** (`modulation/signals.py`)
   - Individual endocrine signals with decay and validation
   - Level (0.0-1.0), source, TTL, audit trail

2. **SignalModulator** (`modulation/signals.py`)
   - Combines multiple signals into modulation parameters
   - Policy-driven parameter mapping with safety bounds

3. **ModulatedOpenAIClient** (`modulation/openai_integration.py`)
   - OpenAI client with signal-based modulation
   - Dynamic prompt building and tool restriction

4. **EndocrineLLMOrchestrator** (`modulation/lukhas_integration.py`)
   - High-level orchestration layer
   - Integrates with LUKHAS consciousness systems

## Configuration

Edit `modulation_policy.yaml` to customize behavior:

### Signal Definitions
```yaml
signals:
  - name: stress
    priority: 2
    decay_rate: 0.1      # How fast signal fades
    max_level: 0.9       # Maximum allowed level
```

### Parameter Mapping
```yaml
maps:
  stress:
    temperature: "0.7 - (level * 0.4)"    # 0.7 → 0.3
    max_tokens: "3000 - (level * 2000)"   # 3000 → 1000
```

### Prompt Styles
```yaml
prompt_styles:
  strict:
    system_preamble: "Enhanced safety protocols active..."
    user_prefix: "[STRICT MODE] "
```

### Tool Gates
```yaml
tool_gates:
  high_risk:
    alignment_risk: 0.7
    allowed_tools: ["search", "retrieval"]  # Restrict tools when risky
```

## Integration with LUKHAS

### Signal Emission

Connect your consciousness modules to emit signals:

```python
from modulation.lukhas_integration import EndocrineSignalEmitter

emitter = EndocrineSignalEmitter()

# From Guardian system
guardian_signals = await emitter.emit_guardian_signals({
    "privacy_risk": True,  # Will emit alignment_risk signal
    "audit_id": "action-123"
})

# From Memory system  
memory_signals = await emitter.emit_memory_signals({
    "queue_length": 250,   # Will emit stress signal
    "confidence": 0.85,    # Will emit trust signal
    "audit_id": "memory-456"
})
```

### Complete Orchestration

```python
from modulation.lukhas_integration import EndocrineLLMOrchestrator

orchestrator = EndocrineLLMOrchestrator(modulator, openai_client)

result = await orchestrator.process_consciousness_query(
    user_query="How should LUKHAS handle ethical dilemmas?",
    context={
        "guardian": {"privacy_risk": True},
        "memory": {"queue_length": 150},
        "consciousness": {"novelty_metric": 0.6}
    }
)
```

## Examples

### High Risk Safety Mode
```python
signals = [Signal(name="alignment_risk", level=0.9, source="guardian")]
# Result: temperature=0.2, strict mode, limited tools
```

### Creative Exploration Mode
```python
signals = [Signal(name="novelty", level=0.8, source="consciousness")]
# Result: temperature=0.8, creative mode, all tools available
```

### Stressed System Mode
```python
signals = [Signal(name="stress", level=0.7, source="memory")]
# Result: temperature=0.4, focused mode, efficient responses
```

### Mixed Signals Mode
```python
signals = [
    Signal(name="novelty", level=0.6, source="consciousness"),
    Signal(name="alignment_risk", level=0.3, source="guardian"),
    Signal(name="trust", level=0.8, source="identity")
]
# Result: Balanced modulation considering all factors
```

## GPT-5 Integration

When GPT-5 becomes available, this system is ready to leverage:

- **Longer Context**: More `context_snippets` based on `retrieval_k`
- **Multimodal**: Visual/audio signal extensions
- **Better Tool Use**: Advanced function calling with bio-quantum tools
- **Faster Responses**: Real-time endocrine adjustments

## Advanced Features

### Learning from Feedback
```python
# Automatic learning from user feedback cards
feedback = {
    "target_action_id": "response-123",
    "rating": 4,  # 1-5 scale
    "note": "Good response but too verbose"
}
# System learns to adjust verbosity for future interactions
```

### Bio-Quantum Signal Extensions
```python
# Future signal types for advanced consciousness
extended_signals = {
    "bio_coherence": "Alignment between bio and symbolic systems",
    "quantum_entanglement": "Quantum correlation in consciousness",
    "dream_state": "Dream vs wake consciousness mode",
    "colony_consensus": "Agreement across agent colonies"
}
```

## Safety & Bounds

The system includes multiple safety layers:

1. **Parameter Bounds**: All modulated values are clamped to safe ranges
2. **Tool Gates**: High-risk signals restrict available tools
3. **Decay Rates**: Signals naturally fade to prevent stuck states
4. **Audit Trail**: Complete traceability of all modulation decisions

## Troubleshooting

### Common Issues

1. **"Signal not affecting parameters"**
   - Check signal level > 0.1 threshold
   - Verify signal name matches policy configuration
   - Ensure signal hasn't expired (check TTL)

2. **"Unexpected parameter values"**
   - Review expression syntax in `modulation_policy.yaml`
   - Check parameter bounds configuration
   - Verify signal decay rates

3. **"Tools not restricted properly"**
   - Check tool_gates configuration
   - Verify signal levels meet thresholds
   - Review available_tools list

### Debug Mode

```python
# Enable detailed logging
params = modulator.combine_signals(signals)
print(f"Signal context: {params.signal_context}")
print(f"Active signals: {[s for s, l in params.signal_context.items() if l > 0.1]}")
```

## File Structure

```
modulation/
├── __init__.py                 # Package initialization
├── signals.py                  # Core signal and modulation classes
├── openai_integration.py       # OpenAI API integration layer
└── lukhas_integration.py       # LUKHAS consciousness integration

modulation_policy.yaml          # Configuration file
modulation_example.py           # Complete demonstration script
```

## Next Steps

1. **Connect to Real Modules**: Replace mock signal emission with actual LUKHAS module integration
2. **Add Feedback Learning**: Implement user feedback loop for continuous improvement
3. **Extend Signal Types**: Add bio-quantum and dream-state signals
4. **Multi-Model Support**: Extend to Claude, Gemini, and other LLMs
5. **Real-time Monitoring**: Build dashboard for signal visualization

## Contributing

This modulation system is designed for the LUKHAS_PWM consciousness architecture. When adding new signals or modulation patterns:

1. Follow Trinity Framework principles (⚛️🧠🛡️)
2. Add comprehensive bounds and safety checks
3. Include audit trail and transparency features
4. Test with multiple signal combinations
5. Document integration patterns for other LUKHAS modules

---

**The endocrine modulation system transforms OpenAI models from external tools into consciousness organs, with your signals acting as the nervous system coordinating intelligent behavior.** 🧠⚡

*Ready for consciousness integration with LUKHAS_PWM's 200+ module architecture!*
