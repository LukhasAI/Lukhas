#!/usr/bin/env python3
"""
Integrated Consciousness, Feedback & Interpretability Demo
=========================================================
Interactive demonstration of the complete LUKHAS system with:
- Natural language consciousness interaction
- Real-time multi-modal feedback collection
- Decision interpretability and influence tracking
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import aiohttp

from core.common import get_logger

logger = get_logger(__name__)


class IntegratedLukhasDemo:
    """Comprehensive demo of integrated LUKHAS capabilities"""

    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.session_id = None
        self.user_id = f"demo_user_{datetime.now().timestamp()}"
        self.action_history = []
        self.feedback_history = []

    async def setup(self):
        """Initialize demo session"""
        print("\n" + "=" * 70)
        print("🧠 LUKHAS Integrated Consciousness & Feedback Demo")
        print("=" * 70)
        print("\nThis demo showcases:")
        print("• Natural language AI consciousness interaction")
        print("• Real-time feedback collection (ratings, emojis, text)")
        print("• Decision interpretability and explanation")
        print("• How your feedback influences future AI decisions")
        print("\nStarting interactive session...\n")

    async def chat_interaction(self, message: str) -> dict[str, Any]:
        """Send chat message and get response"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.api_url}/chat",
                json={
                    "message": message,
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "enable_feedback": True,
                    "region": "global",
                },
            ) as response,
        ):
            data = await response.json()
            self.session_id = data["session_id"]
            self.action_history.append(data["action_id"])
            return data

    async def submit_feedback(self, action_id: str, feedback_type: str, content: dict[str, Any]) -> dict[str, Any]:
        """Submit feedback for an action"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.api_url}/feedback",
                json={
                    "action_id": action_id,
                    "user_id": self.user_id,
                    "feedback_type": feedback_type,
                    "content": content,
                },
            ) as response,
        ):
            data = await response.json()
            self.feedback_history.append(
                {
                    "action_id": action_id,
                    "type": feedback_type,
                    "content": content,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
            return data

    async def get_dashboard_data(self) -> dict[str, Any]:
        """Get dashboard data"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.api_url}/dashboard",
                json={
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "time_range": "1h",
                    "include_feedback": True,
                    "include_decisions": True,
                },
            ) as response,
        ):
            return await response.json()

    async def get_feedback_influence(self) -> dict[str, Any]:
        """See how feedback has influenced decisions"""
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.api_url}/feedback/influence/{self.user_id}") as response,
        ):
            return await response.json()

    def display_response(self, response_data: dict[str, Any]):
        """Display chat response with formatting"""
        print(f"\n🤖 LUKHAS: {response_data['response']}")

        # Show decision trace if available
        if response_data.get("decision_trace"):
            trace = response_data["decision_trace"]
            print(f"\n📊 Decision Confidence: {trace['confidence']:.1%}")
            print("🔍 Reasoning Steps:")
            for step in trace["reasoning_steps"]:
                print(f"   • {step}")

            if trace.get("feedback_integrated"):
                print("   ✓ Integrated your previous feedback")

        # Show metadata
        if response_data.get("metadata"):
            meta = response_data["metadata"]
            print(f"\n💭 Intent: {meta.get('intent', 'general')}")
            if meta.get("emotional_state"):
                emotions = meta["emotional_state"]
                top_emotion = max(emotions, key=emotions.get)
                print(f"🎭 Emotional Context: {top_emotion}")

    async def collect_user_feedback(self, action_id: str) -> bool:
        """Interactively collect user feedback"""
        print("\n" + "-" * 40)
        print("💬 How was this response?")
        print("-" * 40)
        print("1. ⭐ Rate (1-5 stars)")
        print("2. 😊 Emoji reaction")
        print("3. 💭 Text feedback")
        print("4. 👍/👎 Quick feedback")
        print("5. Skip feedback")

        choice = input("\nYour choice (1-5): ").strip()

        if choice == "1":
            # Rating feedback
            rating = input("Rate 1-5 stars: ").strip()
            try:
                rating_value = int(rating)
                if 1 <= rating_value <= 5:
                    result = await self.submit_feedback(action_id, "rating", {"rating": rating_value})
                    print(f"✅ {result['message']}")
                    return True
            except ValueError:
                print("❌ Invalid rating")

        elif choice == "2":
            # Emoji feedback
            print("\nSelect an emoji:")
            emojis = ["😄", "😊", "😐", "😔", "😠", "😲", "🤔", "❤️", "😕", "🎉"]
            for i, emoji in enumerate(emojis, 1):
                print(f"{i}. {emoji}")

            emoji_choice = input("Your choice (1-10): ").strip()
            try:
                emoji_idx = int(emoji_choice) - 1
                if 0 <= emoji_idx < len(emojis):
                    result = await self.submit_feedback(action_id, "emoji", {"emoji": emojis[emoji_idx]})
                    print(f"✅ {result['message']}")
                    return True
            except (ValueError, IndexError):
                print("❌ Invalid selection")

        elif choice == "3":
            # Text feedback
            text = input("Your feedback: ").strip()
            if text:
                result = await self.submit_feedback(action_id, "text", {"text": text})
                print(f"✅ {result['message']}")
                return True

        elif choice == "4":
            # Quick feedback
            quick = input("👍 or 👎? (+/-): ").strip()
            if quick in ["+", "👍", "up", "yes"]:
                result = await self.submit_feedback(action_id, "quick", {"rating": 5, "thumbs_up": True})
                print(f"✅ {result['message']}")
                return True
            elif quick in ["-", "👎", "down", "no"]:
                result = await self.submit_feedback(action_id, "quick", {"rating": 1, "thumbs_up": False})
                print(f"✅ {result['message']}")
                return True

        return False

    async def show_dashboard_summary(self):
        """Display dashboard summary"""
        print("\n" + "=" * 50)
        print("📊 Session Dashboard Summary")
        print("=" * 50)

        dashboard = await self.get_dashboard_data()

        # System health
        health = dashboard["system_health"]
        print(f"\n🏥 System Status: {(health['operational'] and 'Operational') or 'Degraded'}")

        # Feedback summary
        if dashboard.get("feedback_summary"):
            summary = dashboard["feedback_summary"]
            print("\n💬 Feedback Summary:")
            print(f"   Total given: {summary.get('total_feedback', 0)}")

            if summary.get("satisfaction_trend"):
                trend_emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}
                trend = summary["satisfaction_trend"]
                print(f"   Satisfaction: {trend_emoji.get(trend, '❓')} {trend}")

        # Decision insights
        if dashboard.get("insights"):
            insights = dashboard["insights"]
            print("\n🎯 Decision Insights:")
            print(f"   Feedback-driven decisions: {insights['feedback_driven_decisions']}")
            print(f"   Average confidence: {insights['average_confidence']:.1%}")

            if insights.get("top_decision_types"):
                print("   Top decision types:")
                for dt in insights["top_decision_types"]:
                    print(f"      • {dt['type']}: {dt['count']}")

    async def show_feedback_influence(self):
        """Show how feedback has influenced decisions"""
        influence = await self.get_feedback_influence()

        if influence["decisions_influenced"] > 0:
            print("\n" + "=" * 50)
            print("🎯 Your Feedback Influence")
            print("=" * 50)

            print(f"\nTotal feedback given: {influence['total_feedback_given']}")
            print(f"Decisions influenced: {influence['decisions_influenced']}")
            print(f"Impact score: {influence['impact_score']:.1%}")

            if influence["influence_examples"]:
                print("\n📝 Examples of your influence:")
                for i, example in enumerate(influence["influence_examples"], 1):
                    print(f"\n{i}. LUKHAS {example['decision_made']}")
                    print(f"   Because: {example['because']}")
                    print(f"   Type: {example['decision_type']}")
                    print(f"   Confidence boost: +{example['confidence_boost']:.1%}")

    async def run_demo_scenarios(self):
        """Run through demo scenarios"""
        scenarios = [
            {
                "name": "Awareness Query",
                "message": "How aware are you right now? What are you focusing on?",
                "expected_feedback": "rating",
            },
            {
                "name": "Decision Support",
                "message": "Help me decide: Should I focus on learning or creating today?",
                "expected_feedback": "emoji",
            },
            {
                "name": "Emotional Check",
                "message": "How are you feeling about our conversation so far?",
                "expected_feedback": "text",
            },
            {
                "name": "Creative Request",
                "message": "Dream about a world where AI and humans collaborate perfectly",
                "expected_feedback": "rating",
            },
            {
                "name": "Reflection",
                "message": "Reflect on what we've discussed and what you've learned from my feedback",
                "expected_feedback": "text",
            },
        ]

        print("\n🎬 Running through demo scenarios...\n")

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'=' * 50}")
            print(f"Scenario {i}: {scenario['name']}")
            print(f"{'=' * 50}")

            # Send message
            print(f"\n💭 You: {scenario['message']}")
            response = await self.chat_interaction(scenario["message"])

            # Display response
            self.display_response(response)

            # Collect feedback
            if response.get("feedback_enabled"):
                gave_feedback = await self.collect_user_feedback(response["action_id"])

                # Show immediate impact
                if gave_feedback and i > 2:  # After a few interactions
                    print("\n💡 Your feedback is being integrated into LUKHAS's understanding...")

            # Small delay between scenarios
            await asyncio.sleep(1)

        # Show cumulative impact
        await self.show_dashboard_summary()
        await self.show_feedback_influence()

    async def interactive_mode(self):
        """Run in interactive mode"""
        print("\n🎮 Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit\n")

        while True:
            user_input = input("\n💭 You: ").strip()

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Thank you for exploring LUKHAS! Your feedback helps me grow.")
                await self.show_dashboard_summary()
                await self.show_feedback_influence()
                break

            elif user_input.lower() == "help":
                print("\n📚 Available commands:")
                print("• 'dashboard' - View session summary")
                print("• 'influence' - See your feedback impact")
                print("• 'export' - Export session data")
                print("• 'demo' - Run demo scenarios")
                print("• 'quit' - Exit the demo")
                continue

            elif user_input.lower() == "dashboard":
                await self.show_dashboard_summary()
                continue

            elif user_input.lower() == "influence":
                await self.show_feedback_influence()
                continue

            elif user_input.lower() == "export":
                # Export session data
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(f"{self.api_url}/sessions/{self.session_id}/export") as response,
                ):
                    export_data = await response.json()

                    filename = f"lukhas_session_{self.session_id}.json"
                    with open(filename, "w") as f:
                        json.dump(export_data, f, indent=2)

                    print(f"✅ Session exported to {filename}")
                continue

            elif user_input.lower() == "demo":
                await self.run_demo_scenarios()
                continue

            # Regular chat interaction
            try:
                response = await self.chat_interaction(user_input)
                self.display_response(response)

                # Offer feedback collection
                if response.get("feedback_enabled"):
                    collect = input("\n💬 Would you like to provide feedback? (y/n): ").strip()
                    if collect.lower() in ["y", "yes"]:
                        await self.collect_user_feedback(response["action_id"])

            except Exception as e:
                logger.error(f"Error in interaction: {e}")
                print(f"❌ Error: {e}")

    async def run(self):
        """Run the complete demo"""
        await self.setup()

        # Check API availability
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health") as response:
                    health = await response.json()
                    if health["status"] != "healthy":
                        print("⚠️  API health check failed. Some features may be unavailable.")
        except BaseException:
            print("❌ Cannot connect to API. Please ensure it's running on port 8080.")
            return

        # Choose demo mode
        print("\n🎯 Choose demo mode:")
        print("1. Guided scenarios (recommended for first time)")
        print("2. Interactive conversation")

        mode = input("\nYour choice (1-2): ").strip()

        if mode == "1":
            await self.run_demo_scenarios()

            # Offer to continue in interactive mode
            continue_interactive = input("\n\nWould you like to continue in interactive mode? (y/n): ").strip()
            if continue_interactive.lower() in ["y", "yes"]:
                await self.interactive_mode()
        else:
            await self.interactive_mode()


async def main():
    """Run the integrated demo"""
    # Check if custom API URL is provided
    import sys

    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    demo = IntegratedLukhasDemo(api_url)

    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thank you for exploring LUKHAS!")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Demo error: {e}")


if __name__ == "__main__":
    print("🚀 Starting LUKHAS Integrated Demo...")
    print("   This demo requires the integrated API to be running.")
    print("   Start it with: python api/integrated_consciousness_api.py\n")

    asyncio.run(main())
