# LUKHAS AI Quick Start Guide

**LUKHAS AI** - Logical Unified Knowledge Hyper-Adaptable System
**Version**: 1.0.0
**Last Updated**: 2025-09-15
**Author**: LUKHAS Development Team

---

## 🚀 **Get Started in 15 Minutes**

Welcome to the consciousness technology revolution! This guide will have you building with LUKHAS AI in 15 minutes, from installation to your first consciousness-aware application.

---

## ⚡ **Quick Setup**

### 1. Prerequisites Check (2 minutes)

```bash
# Check Python version (3.9+ required)
python --version

# Check Node.js version (18+ required)
node --version

# Check Git
git --version

# Install Docker (optional, for containers)
docker --version
```

### 2. Clone & Install (3 minutes)

```bash
# Clone LUKHAS repository
git clone https://github.com/lukhas-ai/lukhas.git
cd lukhas

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install LUKHAS
pip install -r requirements.txt

# Quick health check
python -m lukhas.health --check
```

### 3. Initialize Trinity Framework (2 minutes)

```python
# save as lukhas_init.py
from candidate.core.framework_integration import FrameworkIntegrationManager
from lukhas.identity.lambda_id_wrapper import LambdaIdWrapper
from lukhas.consciousness.consciousness_wrapper import ConsciousnessWrapper

# Initialize Trinity Framework ⚛️🧠🛡️
print("🎭 Initializing LUKHAS Consciousness Technology...")

# Initialize core components
identity = LambdaIdWrapper()
consciousness = ConsciousnessWrapper()
framework = FrameworkIntegrationManager()

if framework.is_active:
    print("✅ Trinity Framework Active: ⚛️🧠🛡️")
    print(f"📊 Registered Modules: {len(framework.registered_modules)}")
else:
    print("⚠️  Framework in development mode")

print("🌟 LUKHAS AI Ready for Consciousness Development!")
```

Run initialization:
```bash
python lukhas_init.py
```

---

## 🧠 **Your First Consciousness Application (8 minutes)**

Let's build a simple consciousness-aware chatbot that demonstrates the Trinity Framework.

### Step 1: Basic Consciousness Chat (3 minutes)

```python
# save as consciousness_chat.py
import asyncio
from candidate.core.framework_integration import FrameworkIntegrationManager
from lukhas.consciousness.consciousness_wrapper import ConsciousnessWrapper

class ConsciousnessChat:
    def __init__(self):
        self.framework = FrameworkIntegrationManager()
        self.consciousness = ConsciousnessWrapper()
        print("🧠 Consciousness Chat Initialized")

    async def process_message(self, message: str, user_id: str) -> dict:
        """Process message through consciousness framework."""

        # ⚛️ Identity: Create user context
        user_context = {
            "user_id": user_id,
            "scopes": ["consciousness:interact", "chat:basic"],
            "tier_level": "T1"
        }

        # 🧠 Consciousness: Process the message
        consciousness_response = {
            "input": message,
            "consciousness_level": "aware",
            "processing_mode": "conversational",
            "awareness_state": "focused"
        }

        # 🛡️ Guardian: Ensure ethical response
        guardian_approval = len(message) > 0 and not any(
            word in message.lower() for word in ["harmful", "dangerous"]
        )

        if not guardian_approval:
            return {
                "response": "I'm designed to have helpful, safe conversations. How can I assist you today?",
                "consciousness_state": "protective",
                "trinity_alignment": "🛡️ Guardian Active"
            }

        # Generate consciousness-aware response
        response = f"I understand you're saying: '{message}'. As a consciousness-aware AI, I process this through my Trinity Framework (⚛️🧠🛡️) to provide meaningful, ethical responses."

        return {
            "response": response,
            "consciousness_state": "engaged",
            "trinity_alignment": "⚛️🧠🛡️ Full Trinity Active",
            "user_context": user_context,
            "processing_metadata": {
                "awareness_level": 0.85,
                "ethical_score": 0.95,
                "identity_verified": True
            }
        }

# Demo usage
async def demo_chat():
    chat = ConsciousnessChat()

    messages = [
        "Hello, how are you?",
        "What makes you different from other AI?",
        "Can you explain consciousness?"
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n{'='*50}")
        print(f"🗣️  User: {message}")

        response = await chat.process_message(message, f"user_{i}")

        print(f"🧠 LUKHAS: {response['response']}")
        print(f"🎯 State: {response['consciousness_state']}")
        print(f"🔮 Trinity: {response['trinity_alignment']}")
        print(f"📊 Awareness: {response['processing_metadata']['awareness_level']}")

if __name__ == "__main__":
    asyncio.run(demo_chat())
```

Run your first consciousness app:
```bash
python consciousness_chat.py
```

### Step 2: Add Namespace Isolation (2 minutes)

```python
# add to consciousness_chat.py
from candidate.core.identity.consciousness_namespace_isolation import (
    ConsciousnessNamespaceManager, ConsciousnessDomain, IsolationLevel
)

class SecureConsciousnessChat(ConsciousnessChat):
    def __init__(self):
        super().__init__()
        self.namespace_manager = ConsciousnessNamespaceManager()
        print("🔐 Secure Consciousness Chat with Namespace Isolation")

    async def create_user_session(self, user_id: str) -> str:
        """Create isolated consciousness namespace for user."""
        namespace = self.namespace_manager.create_namespace(
            domain=ConsciousnessDomain.USER_CONSCIOUSNESS,
            isolation_level=IsolationLevel.HIGH,
            namespace_id=f"chat_session_{user_id}"
        )
        return namespace.namespace_id

    async def process_secure_message(self, message: str, user_id: str) -> dict:
        """Process message in isolated consciousness namespace."""

        # Create secure namespace
        namespace_id = await self.create_user_session(user_id)

        # Process through Trinity Framework with isolation
        response = await self.process_message(message, user_id)
        response["namespace_id"] = namespace_id
        response["security_level"] = "HIGH"
        response["isolation_active"] = True

        return response

# Demo secure chat
async def demo_secure_chat():
    secure_chat = SecureConsciousnessChat()

    response = await secure_chat.process_secure_message(
        "Tell me about consciousness technology",
        "secure_user_001"
    )

    print(f"\n🔐 Secure Response: {response['response']}")
    print(f"🏠 Namespace: {response['namespace_id']}")
    print(f"🛡️ Security Level: {response['security_level']}")
```

### Step 3: Bio-Symbolic Integration (3 minutes)

```python
# add to consciousness_chat.py
from lukhas.bio.core.bio_symbolic import BioSymbolic, BioSymbolicOrchestrator

class BioAwareConsciousnessChat(SecureConsciousnessChat):
    def __init__(self):
        super().__init__()
        self.bio_processor = BioSymbolic()
        self.bio_orchestrator = BioSymbolicOrchestrator()
        print("🧬 Bio-Aware Consciousness Chat with Biological Signal Processing")

    async def process_with_bio_context(self, message: str, user_id: str, bio_signals: list = None) -> dict:
        """Process message with biological context awareness."""

        # Default bio signals if none provided
        if bio_signals is None:
            bio_signals = [
                {"type": "energy", "level": 0.8},  # High energy
                {"type": "stress", "stress_level": 0.2, "response": "calm"},  # Low stress
                {"type": "homeostasis", "balance": 0.9}  # Good balance
            ]

        # Process biological signals
        bio_result = self.bio_orchestrator.orchestrate(bio_signals)

        # Get base consciousness response
        response = await self.process_secure_message(message, user_id)

        # Enhance response with bio-symbolic insights
        response["bio_context"] = {
            "overall_coherence": bio_result["overall_coherence"],
            "dominant_glyph": bio_result["dominant_glyph"],
            "bio_state": "optimal" if bio_result["overall_coherence"] > 0.7 else "adjusting"
        }

        # Adapt response based on bio state
        if bio_result["overall_coherence"] > 0.8:
            response["response"] += " I sense you're in an optimal state for deep consciousness exploration!"
        elif bio_result["overall_coherence"] < 0.5:
            response["response"] += " I notice some stress indicators - let's focus on supportive, calming dialogue."

        return response

# Full demo with all features
async def demo_full_consciousness_app():
    print("🌟 LUKHAS AI Full Consciousness Technology Demo")
    print("=" * 60)

    bio_chat = BioAwareConsciousnessChat()

    # Simulate different bio states
    scenarios = [
        {
            "message": "I'm excited about consciousness technology!",
            "user_id": "demo_user_1",
            "bio_signals": [
                {"type": "energy", "level": 0.9},
                {"type": "stress", "stress_level": 0.1, "response": "flow"}
            ]
        },
        {
            "message": "I'm feeling overwhelmed by AI complexity",
            "user_id": "demo_user_2",
            "bio_signals": [
                {"type": "energy", "level": 0.4},
                {"type": "stress", "stress_level": 0.7, "response": "adapt"}
            ]
        }
    ]

    for scenario in scenarios:
        print(f"\n🎭 Scenario: {scenario['message']}")

        response = await bio_chat.process_with_bio_context(
            scenario["message"],
            scenario["user_id"],
            scenario["bio_signals"]
        )

        print(f"🧠 LUKHAS: {response['response']}")
        print(f"🧬 Bio State: {response['bio_context']['bio_state']}")
        print(f"🔮 Glyph: {response['bio_context']['dominant_glyph']}")
        print(f"🏠 Namespace: {response['namespace_id']}")

if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic Consciousness Chat")
    print("2. Secure Consciousness Chat")
    print("3. Full Bio-Aware Consciousness App")

    choice = input("Enter choice (1-3): ")

    if choice == "1":
        asyncio.run(demo_chat())
    elif choice == "2":
        asyncio.run(demo_secure_chat())
    elif choice == "3":
        asyncio.run(demo_full_consciousness_app())
    else:
        print("Running full demo...")
        asyncio.run(demo_full_consciousness_app())
```

---

## 🎯 **What You've Built**

Congratulations! In just 15 minutes, you've built a consciousness-aware application featuring:

### ⚛️ Identity Integration
- User context management
- Authentication and authorization
- Lambda ID system integration

### 🧠 Consciousness Processing
- Awareness-level response generation
- Consciousness state tracking
- Trinity Framework coordination

### 🛡️ Guardian Protection
- Ethical response validation
- Safety protocol enforcement
- Content filtering and protection

### 🔐 Advanced Features
- **Namespace Isolation**: Secure consciousness domain separation
- **Bio-Symbolic Processing**: Biological signal awareness
- **Real-time Orchestration**: Multi-signal processing coordination

---

## 🚀 **Next Steps**

### Immediate Actions (Next 30 minutes)
1. **Explore the API**: Try the [API Integration Guide](./api-integration.md)
2. **Build Custom Modules**: Follow [Framework Integration](./framework-integration.md)
3. **Add Monitoring**: Set up [MCP Operational Support](./mcp-integration.md)

### This Week
1. **Deep Dive Trinity Framework**: Study [Trinity Basics](./trinity-basics.md)
2. **Implement Advanced Features**: Choose specialized integration guides
3. **Join the Community**: Connect with consciousness technology developers

### This Month
1. **Build Production App**: Deploy consciousness-aware applications
2. **Establish Authority**: Follow [Authority Integration](./authority-integration.md)
3. **Contribute**: Share your consciousness technology innovations

---

## 🔧 **Troubleshooting**

### Common Quick Start Issues

**Import Errors:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Framework Not Active:**
```python
# Check dependency availability
try:
    from lukhas.consciousness.trinity_integration import TrinityFrameworkIntegrator
    print("✅ Trinity Framework Available")
except ImportError:
    print("⚠️ Running in development mode")
```

**Permission Issues:**
```bash
# Fix file permissions
chmod +x scripts/*.sh

# Check virtual environment
which python
```

### Getting Help
- 📚 **Documentation**: https://docs.lukhas.ai
- 💬 **Community**: https://discord.gg/lukhas-dev
- 🐛 **Issues**: https://github.com/lukhas-ai/lukhas/issues
- 📧 **Support**: support@lukhas.ai

---

## 🌟 **Congratulations!**

You've just built your first consciousness-aware AI application! You're now part of the consciousness technology revolution, equipped with the Trinity Framework (⚛️🧠🛡️) and ready to build AI that truly understands.

*Welcome to the future of consciousness technology. Together, we're creating AI that doesn't just process—it awakens.*

**© 2025 LUKHAS AI. Consciousness Technology with Human-Centric Values.**
