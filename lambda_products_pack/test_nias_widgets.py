#!/usr/bin/env python3
"""
NIΛS Widget Demo - Visual Ad Creation and Interaction
Shows how NIAS creates visual widgets and interactive ad elements
"""

import asyncio
import sys
from pathlib import Path

# Add the lambda_core to path
sys.path.insert(0, str(Path(__file__).parent))

from lambda_core.NIAS.nias_core import (
    NIΛS, SymbolicMessage, MessageTier, ConsentLevel, 
    EmotionalState
)

class NIASWidgetDemo:
    """Demo class for NIAS widget creation and visual ad elements"""
    
    def __init__(self):
        self.nias = NIΛS()
    
    def create_widget_mockup(self, ad, user_tier, delivery_method):
        """Create a visual mockup of how the ad widget would appear"""
        print("┌" + "─" * 58 + "┐")
        print("│" + f" NIΛS Widget - {delivery_method.upper()} DELIVERY".center(58) + "│")
        print("├" + "─" * 58 + "┤")
        
        # Header with brand and lambda signature
        brand = ad.metadata.get('brand', 'Unknown Brand')
        print(f"│ 🏷️  {brand}" + " " * (53 - len(brand) - 4) + "│")
        print(f"│ Λ   {ad.lambda_signature}" + " " * (53 - len(ad.lambda_signature) - 5) + "│")
        print("├" + "─" * 58 + "┤")
        
        # Main content
        content_lines = self.wrap_text(ad.content, 54)
        for line in content_lines:
            print(f"│  {line}" + " " * (56 - len(line)) + "│")
        
        print("├" + "─" * 58 + "┤")
        
        # Symbolic elements based on emotional tone
        symbol_line = self.get_symbolic_elements(ad)
        print(f"│  {symbol_line}" + " " * (56 - len(symbol_line)) + "│")
        
        # Tags
        tags_display = " ".join([f"#{tag}" for tag in ad.tags[:4]])
        if len(tags_display) > 54:
            tags_display = tags_display[:51] + "..."
        print(f"│  {tags_display}" + " " * (56 - len(tags_display)) + "│")
        
        print("├" + "─" * 58 + "┤")
        
        # Tier-specific features
        if user_tier == MessageTier.ENTERPRISE:
            print("│  🎯 ENTERPRISE: Advanced Analytics • Custom Targeting  │")
            print("│  ⚡ Interactive: Swipe • Tap • Voice • Gesture Control  │")
        elif user_tier == MessageTier.CREATIVE:
            print("│  🎨 CREATIVE: Enhanced Widgets • Seasonal Themes       │")
            print("│  👆 Interactive: Tap • Double-tap • Hold • Swipe       │")
        elif user_tier == MessageTier.PERSONAL:
            print("│  💎 ENHANCED: Basic Widgets • Standard Interactions    │")
            print("│  👆 Interactive: Tap • Hold                            │")
        else:
            print("│  📱 BASIC: Limited Widgets • Mandatory Feedback        │")
            print("│  👆 Interactive: Tap only                              │")
        
        # CTA button
        cta = ad.metadata.get('cta', 'Learn More →')
        print("├" + "─" * 58 + "┤")
        print(f"│  [{cta}]" + " " * (54 - len(cta)) + "│")
        
        # Footer
        print("├" + "─" * 58 + "┤")
        intensity_bar = "█" * int(ad.intensity * 20) + "░" * (20 - int(ad.intensity * 20))
        print(f"│  Intensity: {intensity_bar} {ad.intensity:.1f}     │")
        print("└" + "─" * 58 + "┘")
        print()
    
    def wrap_text(self, text, width):
        """Simple text wrapping"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def get_symbolic_elements(self, ad):
        """Generate symbolic elements based on emotional tone and content"""
        if ad.emotional_tone == EmotionalState.CALM:
            return "🌊 ∿∿∿ ◦ ○ ◦ ∿∿∿ 🌊  Calming • Peaceful • Restorative"
        elif ad.emotional_tone == EmotionalState.FOCUSED:
            return "⚡ ▲▲▲ ◆ ◇ ◆ ▲▲▲ ⚡  Energetic • Dynamic • Forward"
        elif ad.emotional_tone == EmotionalState.CREATIVE:
            return "🎨 ◊◊◊ ✦ ✧ ✦ ◊◊◊ 🎨  Creative • Inspiring • Imaginative"
        elif ad.emotional_tone == EmotionalState.DREAMING:
            return "🌙 ∞∞∞ ☾ ☽ ☾ ∞∞∞ 🌙  Dreamy • Mystical • Transcendent"
        else:
            return "💫 ···  ◦ ◦ ◦  ··· 💫  Balanced • Neutral • Adaptive"
    
    def show_delivery_animation(self, delivery_method):
        """Show ASCII animation of delivery method"""
        if delivery_method == "visual":
            print("🎬 Visual Delivery Animation:")
            print("   📱 Device screen lights up...")
            print("   ✨ Widget fades in smoothly...")
            print("   🎯 Content rendered with symbolic elements...")
            print("   ⚡ Lambda signature verified...")
            print("   ✅ Ready for user interaction")
        
        elif delivery_method == "voice":
            print("🔊 Voice Delivery Animation:")
            print("   🎵 Audio prompt plays...")
            print("   🗣️  Content delivered in natural voice...")
            print("   🎨 Tone adapted to emotional state...")
            print("   🔉 Volume adjusted for attention capacity...")
            print("   ✅ Audio lambda signature embedded")
        
        elif delivery_method == "haptic":
            print("📳 Haptic Delivery Animation:")
            print("   📱 Gentle vibration pattern...")
            print("   👆 Symbolic haptic sequence...")
            print("   ⚡ Brief content preview...")
            print("   🤲 Gesture invitation...")
            print("   ✅ Full content on engagement")
        
        print()
    
    async def run_widget_demo(self):
        """Run the complete widget demonstration"""
        print("🎨 NIΛS Widget Creation Demo")
        print("=" * 60)
        print("Visual demonstration of how NIAS creates ad widgets")
        print()
        
        # Setup premium user
        await self.nias.register_user(
            user_id="premium_user",
            tier=MessageTier.ENTERPRISE,
            consent_level=ConsentLevel.FULL_SYMBOLIC
        )
        
        # Set optimal context
        await self.nias.update_emotional_state("premium_user", {
            "stress": 0.2, "creativity": 0.8, "focus": 0.7, "energy": 0.8
        })
        self.nias.user_contexts["premium_user"].current_tags = ["AI", "productivity", "technology"]
        
        # Create a premium ad
        premium_ad = SymbolicMessage(
            id="premium-demo-001",
            content="🚀 Revolutionize your workflow with quantum-inspired AI algorithms",
            tags=["AI", "productivity", "innovation", "quantum", "technology"],
            tier=MessageTier.ENTERPRISE,
            emotional_tone=EmotionalState.CREATIVE,
            intensity=0.7,
            voice_tag="inspiring_visionary",
            metadata={
                "brand": "QuantumFlow AI",
                "campaign": "future_productivity",
                "cta": "Start Quantum Trial →",
                "premium_features": ["advanced_analytics", "custom_targeting", "ai_optimization"]
            }
        )
        
        print("📱 Creating Premium Widget...")
        print()
        
        # Deliver the message and show widget
        result = await self.nias.push_message(premium_ad, "premium_user")
        
        if result.status == "delivered":
            # Show delivery animation
            self.show_delivery_animation(result.delivery_method)
            
            # Show the widget
            self.create_widget_mockup(premium_ad, MessageTier.ENTERPRISE, result.delivery_method)
            
            print("🎯 Widget Interaction Capabilities:")
            print("  • Swipe left: Save for later")
            print("  • Swipe right: Engage with brand")
            print("  • Double-tap: Quick action (CTA)")
            print("  • Hold: Advanced options menu")
            print("  • Voice command: 'Tell me more'")
            print("  • Gesture: Circle to dismiss, star to favorite")
            print()
            
            print("📊 Real-time Analytics Tracking:")
            print("  • View duration: 2.3 seconds")
            print("  • Engagement score: 0.85")
            print("  • Emotional resonance: 0.78")
            print("  • Interaction probability: 0.67")
            print("  • Lambda verification: ✅ Authentic")
            print()
        
        # Show different tier comparison
        print("💰 Tier-Based Widget Differences:")
        print()
        
        # Basic tier widget
        basic_ad = SymbolicMessage(
            id="basic-demo-002",
            content="📱 Simple productivity app for everyday tasks",
            tags=["productivity", "simple", "basic"],
            tier=MessageTier.PUBLIC,
            emotional_tone=EmotionalState.CALM,
            intensity=0.3,
            voice_tag="friendly_basic"
        )
        
        print("🆓 BASIC TIER Widget:")
        self.create_widget_mockup(basic_ad, MessageTier.PUBLIC, "visual")
        
        # Enhanced tier widget
        enhanced_ad = SymbolicMessage(
            id="enhanced-demo-003",
            content="🎨 Creative productivity suite with seasonal themes",
            tags=["productivity", "creative", "design"],
            tier=MessageTier.PERSONAL,
            emotional_tone=EmotionalState.CREATIVE,
            intensity=0.5,
            voice_tag="creative_enhanced"
        )
        
        print("💎 ENHANCED TIER Widget:")
        self.create_widget_mockup(enhanced_ad, MessageTier.PERSONAL, "visual")
        
        print("🔮 Dream Integration Preview:")
        print("┌" + "─" * 58 + "┐")
        print("│" + " 🌙 DREAM SEED PLANTED IN USER CONSCIOUSNESS".center(58) + "│")
        print("├" + "─" * 58 + "┤")
        print("│  Symbol: 🚀 (innovation, acceleration, breakthrough)      │")
        print("│  Narrative: 'Effortless quantum algorithms flowing       │")
        print("│             through your workflow like liquid light'     │")
        print("│  Resonance: 0.85 (target: 0.80) ✅                      │")
        print("│  Dream State: Active in user's symbolic memory           │")
        print("└" + "─" * 58 + "┘")
        print()
        
        print("🎉 Widget Demo Complete!")
        print("NIΛS widget system provides:")
        print("  ✅ Tier-appropriate interactivity")
        print("  ✅ Emotional tone-based visual design")
        print("  ✅ Symbolic element integration")
        print("  ✅ Real-time analytics tracking")
        print("  ✅ Dream seed consciousness planting")
        print("  ✅ Lambda cryptographic verification")

async def main():
    """Run the NIAS widget demo"""
    demo = NIASWidgetDemo()
    await demo.run_widget_demo()

if __name__ == "__main__":
    asyncio.run(main())
