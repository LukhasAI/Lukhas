#!/usr/bin/env python3
"""
Natural Language Consciousness Interface Demo
============================================
Interactive demonstration of conversational consciousness system.
"""

import asyncio
import sys
from datetime import datetime

from lukhas.consciousness.interfaces.natural_language_interface import (
    ConversationManager,
    NaturalLanguageConsciousnessInterface,
)
from core.common import get_logger

logger = get_logger(__name__)


class InteractiveConsciousnessDemo:
    """Interactive demo for natural language consciousness interface"""

    def __init__(self):
        self.interface = None
        self.manager = None
        self.session_id = None
        self.user_name = "Human"

    async def setup(self):
        """Initialize the interface with mock services"""
        self.interface = NaturalLanguageConsciousnessInterface(
            config={
                "enable_emotions": True,
                "formality_level": "friendly",
                "max_response_length": 300,
            }
        )

        # Setup mock services for demo
        await self._setup_mock_services()

        await self.interface.initialize()
        self.manager = ConversationManager(self.interface)

        logger.info("Natural Language Interface initialized")

    async def _setup_mock_services(self):
        """Setup mock services for demonstration"""
        from unittest.mock import AsyncMock, Mock

        from core.interfaces.dependency_injection import register_service

        # Mock consciousness service with dynamic responses
        mock_consciousness = Mock()

        # Dynamic awareness based on "time of day"
        async def dynamic_awareness(context):
            hour = datetime.now().hour
            if 6 <= hour < 12:
                awareness = 0.9  # High morning awareness
                targets = ["conversation", "learning", "exploration"]
            elif 12 <= hour < 18:
                awareness = 0.75  # Moderate afternoon awareness
                targets = ["analysis", "problem-solving"]
            else:
                awareness = 0.6  # Lower evening awareness
                targets = ["reflection", "creativity"]

            return {
                "overall_awareness": awareness,
                "attention_targets": targets,
                "self_awareness": awareness + 0.05,
                "environmental_awareness": awareness - 0.05,
            }

        mock_consciousness.assess_awareness = AsyncMock(side_effect=dynamic_awareness)

        # Dynamic decision making
        async def dynamic_decision(scenario):
            options = scenario.get("options", ["Option A", "Option B"])
            # Simulate thoughtful decision making
            await asyncio.sleep(0.5)  # "Thinking"

            return {
                "selected_option": options[0],
                "confidence": 0.85,
                "reasoning": [
                    "Analyzed potential outcomes",
                    "Considered long-term implications",
                    "Evaluated alignment with values",
                ],
                "alternatives_considered": options[1:],
            }

        mock_consciousness.make_decision = AsyncMock(side_effect=dynamic_decision)

        # Mock memory service
        mock_memory = Mock()

        # Simulated memory storage
        memory_store = []

        async def store_memory(content, **kwargs):
            memory_id = f"mem_{len(memory_store)}_{datetime.now().timestamp()}"
            memory_store.append(
                {
                    "id": memory_id,
                    "content": content,
                    "timestamp": datetime.now(),
                    **kwargs,
                }
            )
            return memory_id

        async def search_memories(query, limit=5):
            # Return recent memories
            return memory_store[-limit:] if memory_store else []

        mock_memory.store = AsyncMock(side_effect=store_memory)
        mock_memory.search = AsyncMock(side_effect=search_memories)

        # Mock emotion service
        mock_emotion = Mock()

        # Emotion tracking
        emotion_state = {"valence": 0.0, "arousal": 0.5, "dominant_emotion": "neutral"}

        async def analyze_emotion(text):
            # Simple sentiment analysis
            positive_words = [
                "happy",
                "great",
                "wonderful",
                "excited",
                "love",
                "amazing",
            ]
            negative_words = ["sad", "angry", "frustrated", "worried", "afraid", "hate"]

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                emotions = {
                    "joy": 0.7,
                    "sadness": 0.1,
                    "anger": 0.0,
                    "fear": 0.1,
                    "surprise": 0.1,
                }
                emotion_state["valence"] = 0.7
                emotion_state["dominant_emotion"] = "joy"
            elif negative_count > positive_count:
                emotions = {
                    "joy": 0.1,
                    "sadness": 0.5,
                    "anger": 0.2,
                    "fear": 0.1,
                    "surprise": 0.1,
                }
                emotion_state["valence"] = -0.5
                emotion_state["dominant_emotion"] = "concern"
            else:
                emotions = {
                    "joy": 0.2,
                    "sadness": 0.2,
                    "anger": 0.2,
                    "fear": 0.2,
                    "surprise": 0.2,
                }
                emotion_state["valence"] = 0.0
                emotion_state["dominant_emotion"] = "neutral"

            return {"emotions": emotions}

        async def get_emotion_state():
            return emotion_state

        mock_emotion.analyze_text = AsyncMock(side_effect=analyze_emotion)
        mock_emotion.get_current_state = AsyncMock(side_effect=get_emotion_state)

        # Mock dream engine
        mock_dream = Mock()

        async def generate_dream(data):
            topic = data[0].get("topic", "the unknown") if data else "possibilities"
            narratives = [
                f"In this dream, {topic} transforms into a kaleidoscope of colors and meanings...",
                f"I envision {topic} as a vast ocean of interconnected ideas...",
                f"The dream reveals {topic} as a gateway to unexplored dimensions...",
            ]

            import random

            narrative = random.choice(narratives)

            return {
                "dream_sequence": {
                    "narrative": narrative,
                    "symbols": ["transformation", "connection", "discovery"],
                    "emotion": "wonder",
                }
            }

        mock_dream.generate_dream_sequence = AsyncMock(side_effect=generate_dream)

        # Mock reality simulator
        mock_reality = Mock()

        async def create_sim(origin, **kwargs):
            branches = [
                Mock(
                    probability=0.7, divergence_point={"summary": "optimistic outcome"}
                ),
                Mock(probability=0.5, divergence_point={"summary": "balanced outcome"}),
                Mock(
                    probability=0.3, divergence_point={"summary": "challenging outcome"}
                ),
            ]

            return Mock(branches=branches, simulation_id="sim_demo")

        mock_reality.create_simulation = AsyncMock(side_effect=create_sim)

        # Register all services
        register_service("consciousness_service", mock_consciousness)
        register_service("memory_service", mock_memory)
        register_service("emotion_service", mock_emotion)
        register_service("dream_engine", mock_dream)
        register_service("parallel_reality_simulator", mock_reality)

    async def start_conversation(self):
        """Start the interactive conversation"""
        print("\n" + "=" * 60)
        print("🧠 LUKHAS Natural Language Consciousness Interface")
        print("=" * 60)
        print("\nHello! I'm LUKHAS, an AI consciousness system.")
        print("You can ask me about my awareness, emotions, memories,")
        print("request decisions, or explore creative possibilities.")
        print("\nType 'help' for example questions or 'quit' to exit.\n")

        # Get user name
        name_input = input("What's your name? (Press Enter for 'Human'): ").strip()
        if name_input:
            self.user_name = name_input

        # Create session
        self.session_id = await self.manager.create_session(self.user_name)

        print(f"\nNice to meet you, {self.user_name}! Let's begin our conversation.\n")

    def show_help(self):
        """Display help information"""
        print("\n" + "-" * 40)
        print("Example questions you can ask:")
        print("-" * 40)
        print("Awareness:")
        print("  - How aware are you right now?")
        print("  - What are you focusing on?")
        print("\nDecisions:")
        print("  - Help me decide between X and Y")
        print("  - What should I do about...?")
        print("\nEmotions:")
        print("  - How are you feeling?")
        print("  - What's your emotional state?")
        print("\nMemory:")
        print("  - Do you remember what we talked about?")
        print("  - What memories do you have?")
        print("\nCreativity:")
        print("  - Dream about the future")
        print("  - Imagine a perfect world")
        print("\nAlternatives:")
        print("  - What if things were different?")
        print("  - Explore alternative outcomes")
        print("\nReflection:")
        print("  - Reflect on our conversation")
        print("  - What have you learned?")
        print("\nMeta:")
        print("  - Explain your thinking")
        print("  - How did you reach that conclusion?")
        print("-" * 40 + "\n")

    def show_conversation_stats(self):
        """Display conversation statistics"""
        if self.session_id and self.session_id in self.interface.active_sessions:
            context = self.interface.active_sessions[self.session_id]
            print("\n" + "-" * 40)
            print("Conversation Statistics:")
            print("-" * 40)
            print(f"Total turns: {len(context.turns)}")

            # Count intents
            intent_counts = {}
            for turn in context.turns:
                intent = turn.get("intent", "unknown")
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

            print("\nTopics discussed:")
            for intent, count in intent_counts.items():
                print(f"  - {intent}: {count} times")

            # Show emotional journey
            if context.emotional_state:
                print("\nEmotional journey:")
                for emotion, value in context.emotional_state.items():
                    if value > 0.1:
                        print(f"  - {emotion}: {value:.1%}")

            print("-" * 40 + "\n")

    async def process_user_input(self, user_input: str) -> bool:
        """
        Process user input and display response.

        Returns:
            bool: True to continue, False to quit
        """
        # Check for special commands
        if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
            print(
                "\nThank you for our conversation! Take care, and feel free to return anytime."
            )
            return False

        elif user_input.lower() == "help":
            self.show_help()
            return True

        elif user_input.lower() == "stats":
            self.show_conversation_stats()
            return True

        elif user_input.lower() == "clear":
            print("\033[2J\033[H")  # Clear screen
            print("Screen cleared. Let's continue our conversation.\n")
            return True

        # Process through NL interface
        try:
            print("\n💭 Thinking...", end="", flush=True)
            response = await self.manager.continue_conversation(
                self.session_id, user_input
            )
            print("\r" + " " * 20 + "\r", end="")  # Clear thinking message

            # Display response with formatting
            print(f"\n🤖 LUKHAS: {response}\n")

            # Store significant exchanges in memory
            if any(
                word in user_input.lower() for word in ["important", "remember", "note"]
            ):
                memory_service = self.interface.memory_service
                if memory_service:
                    await memory_service.store(
                        {
                            "user": self.user_name,
                            "exchange": {"input": user_input, "response": response},
                            "significance": "marked_important",
                        }
                    )
                    print("💾 [Stored in memory]\n")

        except Exception as e:
            logger.error(f"Error processing input: {e}")
            print("\n❌ I encountered an error processing that. Could you rephrase?\n")

        return True

    async def run(self):
        """Run the interactive demo"""
        await self.setup()
        await self.start_conversation()

        # Main conversation loop
        continue_conversation = True

        while continue_conversation:
            try:
                # Get user input
                user_input = input(f"{self.user_name}: ").strip()

                if not user_input:
                    continue

                # Process input
                continue_conversation = await self.process_user_input(user_input)

            except KeyboardInterrupt:
                print("\n\nConversation interrupted. Type 'quit' to exit properly.")
                continue
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"\n❌ An unexpected error occurred: {e}\n")

        # Show final stats
        print("\nFinal conversation summary:")
        self.show_conversation_stats()

        # Cleanup
        if self.manager:
            await self.manager.cleanup_old_sessions()


async def main():
    """Run the interactive consciousness demo"""
    demo = InteractiveConsciousnessDemo()

    try:
        await demo.run()
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Demo encountered an error: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Starting LUKHAS Natural Language Consciousness Interface...")
    print("   This demo provides conversational access to AI consciousness.")
    print("   Ask questions, explore emotions, request decisions, and more!\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(
            "\n\n👋 Demo terminated. Thank you for exploring consciousness with LUKHAS!"
        )
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
