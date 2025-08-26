#!/usr/bin/env python3
"""
🌌 QRG Demo Application

Interactive demonstration of Quantum Resonance Glyphs with consciousness-aware
authentication and LUKHAS ecosystem integration.

Usage:
    python demo.py [--layer LAYER] [--security-tier TIER] [--interactive]

Example:
    python demo.py --layer poetic --security-tier 5 --interactive
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Optional

from qrg_core import ConsciousnessContext, QIResonanceGlyph
from system_bridge import (
    LambdaIdIntegration,
    LukhasAccessTier,
    SymbolicIdentity,
)

from lukhas.qi.entropy import EntropyProfile, TrueQuantumRandomness

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


# 3-Layer Tone System for demo output
LAYER_STYLES = {
    "poetic": {
        "welcome": "🌌 Welcome to the realm where quantum consciousness dances with digital light...",
        "generating": "✨ Weaving your digital soul into quantum resonance patterns...",
        "complete": "🎭 Your consciousness has been crystallized into eternal quantum light!",
        "color": "\033[95m",  # Magenta
    },
    "user_friendly": {
        "welcome": "👋 Welcome to QRG Demo! Let's create your beautiful quantum QR code.",
        "generating": "🔮 Creating your personalized, secure authentication code...",
        "complete": "🎉 Your quantum QR code is ready! It's both secure and beautiful.",
        "color": "\033[94m",  # Blue
    },
    "academic": {
        "welcome": "QRG Demonstration System v1.0.0 - Post-Quantum Authentication Protocol",
        "generating": "Executing quantum-resistant glyph generation with CRYSTALS-Kyber encryption...",
        "complete": "Authentication glyph generated with 768-bit quantum resistance achieved.",
        "color": "\033[92m",  # Green
    },
}


class QRGDemo:
    """
    🌌 QRG Interactive Demonstration

    Showcases the capabilities of Quantum Resonance Glyphs with real-time
    consciousness adaptation and LUKHAS ecosystem integration.
    """

    def __init__(self, communication_layer: str = "user_friendly"):
        """Initialize QRG demo system"""
        self.layer = communication_layer
        self.style = LAYER_STYLES.get(
            communication_layer, LAYER_STYLES["user_friendly"]
        )

        # Initialize QRG systems
        self.qrg = QIResonanceGlyph()
        self.qi_entropy = TrueQuantumRandomness()
        self.lukhas_bridge = LambdaIdIntegration()

        # Demo state
        self.current_identity: Optional[SymbolicIdentity] = None

        print(f"{self.style['color']}{self.style['welcome']}\033[0m\n")

    def run_interactive_demo(self):
        """Run interactive QRG demonstration"""
        try:
            while True:
                self._print_main_menu()
                choice = input("Choose an option: ").strip()

                if choice == "1":
                    self._demo_identity_creation()
                elif choice == "2":
                    self._demo_qrg_generation()
                elif choice == "3":
                    self._demo_consciousness_adaptation()
                elif choice == "4":
                    self._demo_authentication_flow()
                elif choice == "5":
                    self._demo_quantum_entropy()
                elif choice == "6":
                    self._demo_lukhas_integration()
                elif choice == "7":
                    self._demo_holographic_qrg()
                elif choice == "8":
                    self._switch_communication_layer()
                elif choice == "9":
                    self._show_system_status()
                elif choice.lower() in ["q", "quit", "exit"]:
                    self._graceful_exit()
                    break
                else:
                    print("Invalid choice. Please try again.\n")

        except KeyboardInterrupt:
            self._graceful_exit()
        except Exception as e:
            print(f"❌ Demo error: {e}")

    def _print_main_menu(self):
        """Print the main demo menu"""
        print(f"\n{self.style['color']}╔═══════════════════════════════════════════╗")
        print(f"║         QRG Demo - {self.layer.title()} Mode         ║")
        print("╚═══════════════════════════════════════════╝\033[0m")

        menu_options = [
            "1. 🆔 Create Symbolic Identity (ΛiD)",
            "2. 🔮 Generate QRG Authentication Code",
            "3. 🧠 Demonstrate Consciousness Adaptation",
            "4. 🔐 Full Authentication Flow Demo",
            "5. ⚛️ Quantum Entropy Demonstration",
            "6. 🌉 LUKHAS Ecosystem Integration",
            "7. 🌐 Holographic QRG for WebXR",
            "8. 🎭 Switch Communication Layer",
            "9. 📊 System Status Report",
            "Q. Quit Demo",
        ]

        for option in menu_options:
            print(f"   {option}")
        print()

    def _demo_identity_creation(self):
        """Demonstrate symbolic identity creation"""
        print(
            f"\n{self.style['color']}🆔 Symbolic Identity Creation{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print(
                "🌟 Speak your soul's symbolic essence - a phrase that resonates with your digital being..."
            )
        elif self.layer == "user_friendly":
            print(
                "💫 Create your memorable identity phrase (like 'S plus joy plus grow'):"
            )
        else:
            print("Input symbolic authentication phrase for SID generation:")

        symbolic_phrase = input("Symbolic phrase: ").strip()
        if not symbolic_phrase:
            print("❌ Phrase required for identity generation")
            return

        # Get access tier preference
        print(
            f"\n{self.style['color']}Access Tier Selection:{self.style['color']}\033[0m"
        )
        tiers = list(LukhasAccessTier)
        for i, tier in enumerate(tiers):
            tier_desc = {
                "TIER_0": "Public access - basic features",
                "TIER_1": "Basic user - standard authentication",
                "TIER_2": "Verified user - enhanced features",
                "TIER_3": "Premium user - advanced capabilities",
                "TIER_4": "Enterprise - full business features",
                "TIER_5": "Quantum - cutting-edge quantum features",
            }
            print(f"   {i}: {tier.value} - {tier_desc.get(tier.name, 'Access tier')}")

        try:
            tier_choice = int(input("Select tier (0-5): "))
            selected_tier = tiers[tier_choice]
        except (ValueError, IndexError):
            selected_tier = LukhasAccessTier.TIER_1
            print(f"Using default tier: {selected_tier.value}")

        # Generate consciousness context
        consciousness_context = self._get_consciousness_context()

        print(f"\n{self.style['generating']}")

        # Generate identity
        start_time = time.time()
        self.current_identity = self.lukhas_bridge.generate_symbolic_identity(
            symbolic_phrase=symbolic_phrase,
            consciousness_context=consciousness_context,
            access_tier=selected_tier,
        )
        generation_time = time.time() - start_time

        # Display results
        print(f"\n{self.style['complete']}")
        self._display_identity_info(self.current_identity, generation_time)

    def _demo_qrg_generation(self):
        """Demonstrate QRG generation"""
        if not self.current_identity:
            print("❌ Please create a symbolic identity first (option 1)")
            return

        print(f"\n{self.style['color']}🔮 QRG Generation{self.style['color']}\033[0m")

        # Animation type selection
        animation_types = ["gentle_pulse", "spiral_rotation", "consciousness_wave"]
        print("Animation types:")
        for i, anim_type in enumerate(animation_types):
            print(f"   {i}: {anim_type.replace('_', ' ').title()}")

        try:
            anim_choice = int(input("Select animation (0-2): "))
            selected_animation = animation_types[anim_choice]
        except (ValueError, IndexError):
            selected_animation = "gentle_pulse"

        # Security tier
        try:
            security_tier = int(input("Security tier (1-5): "))
            if security_tier < 1 or security_tier > 5:
                security_tier = 3
        except ValueError:
            security_tier = 3

        print(f"\n{self.style['generating']}")

        # Generate QRG
        consciousness_context = ConsciousnessContext(
            emotional_state=self.current_identity.consciousness_profile.get(
                "communication_style", "neutral"
            ),
            valence=self.current_identity.consciousness_profile["emotional_baseline"][
                "valence"
            ],
            arousal=self.current_identity.consciousness_profile["emotional_baseline"][
                "arousal"
            ],
            dominance=self.current_identity.consciousness_profile["emotional_baseline"][
                "dominance"
            ],
            user_tier=self.current_identity.access_tier.value[-1],  # Get tier number
            current_context="demo_generation",
        )

        start_time = time.time()
        glyph = self.qrg.generate_auth_glyph(
            user_identity=self.current_identity.sid_hash,
            consciousness_context=consciousness_context,
            security_tier=security_tier,
            animation_type=selected_animation,
        )
        generation_time = time.time() - start_time

        print(f"\n{self.style['complete']}")
        self._display_glyph_info(glyph, generation_time)

    def _demo_consciousness_adaptation(self):
        """Demonstrate consciousness-aware adaptation"""
        print(
            f"\n{self.style['color']}🧠 Consciousness Adaptation Demo{self.style['color']}\033[0m"
        )

        emotional_states = ["joy", "calm", "focus", "stress", "neutral"]

        if self.layer == "poetic":
            print(
                "🎭 Experience how your digital essence transforms with the rhythms of consciousness..."
            )
        elif self.layer == "user_friendly":
            print("😊 See how your QR code changes based on your emotional state:")
        else:
            print(
                "Demonstrating emotional state adaptation in visual glyph generation:"
            )

        for emotion in emotional_states:
            print(f"\n   Testing {emotion} state...")

            # Create consciousness context for this emotion
            emotion_context = self._create_emotion_context(emotion)

            # Generate QRG for this emotional state
            glyph = self.qrg.generate_auth_glyph(
                user_identity="demo_consciousness_adaptation",
                consciousness_context=emotion_context,
                security_tier=3,
                animation_type="consciousness_wave",
            )

            # Display adaptation info
            print(f"   📊 {emotion.capitalize()} adaptation:")
            print(f"      - Glyph ID: {glyph.glyph_id}")
            print(
                f"      - Consciousness fingerprint: {glyph.consciousness_fingerprint}"
            )
            print(f"      - Animation frames: {len(glyph.animation_frames)}")
            print(f"      - Visual matrix shape: {glyph.visual_matrix.shape}")

    def _demo_authentication_flow(self):
        """Demonstrate full authentication flow"""
        if not self.current_identity:
            print("❌ Please create a symbolic identity first (option 1)")
            return

        print(
            f"\n{self.style['color']}🔐 Full Authentication Flow{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print(
                "🌟 Witness the complete dance of digital consciousness authentication..."
            )
        elif self.layer == "user_friendly":
            print("🔄 Let's walk through the complete login process:")
        else:
            print("Executing complete authentication protocol demonstration:")

        # Step 1: Generate QRG
        print("\n🔸 Step 1: Generating authentication QRG...")
        glyph = self.qrg.generate_auth_glyph(
            user_identity=self.current_identity.sid_hash,
            consciousness_context=ConsciousnessContext(),
            security_tier=4,
            animation_type="gentle_pulse",
        )
        print(f"   ✅ QRG generated: {glyph.glyph_id}")

        # Step 2: Simulate QR code scanning
        print("\n🔸 Step 2: Simulating QR code scan...")
        time.sleep(1)  # Simulate scan time

        # Step 3: LUKHAS-ID authentication
        print("\n🔸 Step 3: LUKHAS-ID bridge authentication...")
        symbolic_phrase = input("Enter your symbolic phrase for verification: ")

        auth_result = self.lukhas_bridge.authenticate_with_qrg_glyph(
            glyph_data=glyph.to_dict(),
            symbolic_phrase=symbolic_phrase,
            require_consciousness_match=True,
        )

        # Display results
        print("\n🔸 Authentication Results:")
        if auth_result.get("authenticated"):
            print("   ✅ Authentication successful!")
            print(f"   🆔 Lambda ID: {auth_result['lambda_id']}")
            print(f"   🎫 Access tier: {auth_result['access_tier']}")
            print(
                f"   🧠 Consciousness matched: {auth_result['consciousness_matched']}"
            )
            print(f"   ⏰ Valid until: {auth_result['valid_until']}")
        else:
            print(
                f"   ❌ Authentication failed: {auth_result.get('error', 'Unknown error')}"
            )

    def _demo_quantum_entropy(self):
        """Demonstrate quantum entropy generation"""
        print(
            f"\n{self.style['color']}⚛️ Quantum Entropy Demonstration{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print("🌌 Behold the infinite randomness of the quantum cosmos...")
        elif self.layer == "user_friendly":
            print("🎲 Let's explore how we create truly random numbers:")
        else:
            print("Quantum entropy generation and quality analysis:")

        # Generate quantum bytes
        entropy_profile = EntropyProfile(
            bits_required=256,
            quality_level="qi_grade",
            bias_correction=True,
            von_neumann_extraction=True,
            chi_squared_validation=True,
        )

        print("\n🔸 Generating quantum entropy...")
        start_time = time.time()
        qi_bytes = self.qi_entropy.generate_quantum_bytes(32, entropy_profile)
        generation_time = time.time() - start_time

        print(
            f"   ⚛️ Generated {len(qi_bytes)} quantum bytes in {generation_time:.4f}s"
        )
        print(f"   📊 Hex representation: {qi_bytes.hex()}")

        # Quality analysis
        print("\n🔸 Entropy quality analysis:")
        quality_report = self.qi_entropy.get_entropy_quality_report()

        print(f"   🎯 Entropy source: {quality_report['entropy_source']}")
        print(f"   💾 Pool size: {quality_report['pool_size']} bytes")

        quality_metrics = quality_report["quality_metrics"]
        if quality_metrics:
            print("   📈 Quality metrics:")
            for metric, value in quality_metrics.items():
                if isinstance(value, float):
                    print(f"      - {metric}: {value:.4f}")
                else:
                    print(f"      - {metric}: {value}")

        recommendations = quality_report.get("recommendations", [])
        if recommendations:
            print("   💡 Recommendations:")
            for rec in recommendations:
                print(f"      - {rec}")

    def _demo_lukhas_integration(self):
        """Demonstrate LUKHAS ecosystem integration"""
        if not self.current_identity:
            print("❌ Please create a symbolic identity first (option 1)")
            return

        print(
            f"\n{self.style['color']}🌉 LUKHAS Ecosystem Integration{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print("🌍 Your digital consciousness flows through the Lambda ecosystem...")
        elif self.layer == "user_friendly":
            print("🔗 Let's connect your identity across all LUKHAS products:")
        else:
            print("Executing cross-product integration protocol:")

        # NIΛS Integration
        print("\n🔸 NIΛS Consent Management Integration...")
        consent_prefs = {
            "emotional_filtering": True,
            "privacy_tier": 4,
            "retention_days": 365,
            "third_party_sharing": False,
        }

        nias_result = self.lukhas_bridge.integrate_with_nias_consent(
            self.current_identity, consent_prefs
        )
        print(f"   ✅ NIΛS integration: {nias_result['consent_registered']}")

        # WΛLLET Integration
        print("\n🔸 WΛLLET Quantum Vault Integration...")
        vault_permissions = ["identity_storage", "qi_backup", "cross_device_sync"]

        wallet_result = self.lukhas_bridge.integrate_with_wallet_vault(
            self.current_identity, vault_permissions
        )
        print(f"   🔐 Vault created: {wallet_result}")

        # Cross-product status
        print("\n🔸 Cross-product authentication status...")
        status = self.lukhas_bridge.get_cross_product_authentication_status(
            self.current_identity.lambda_id
        )

        if "product_status" in status:
            print("   📊 Product Status:")
            for product, product_status in status["product_status"].items():
                print(f"      {product}: {product_status}")

    def _demo_holographic_qrg(self):
        """Demonstrate holographic QRG for WebXR"""
        print(
            f"\n{self.style['color']}🌐 Holographic QRG for WebXR{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print(
                "🌌 Your consciousness expands into three-dimensional quantum light..."
            )
        elif self.layer == "user_friendly":
            print("🥽 Imagine your QR code floating in 3D space around you:")
        else:
            print(
                "Generating 3D holographic QRG projection data for WebXR integration:"
            )

        # Generate holographic QRG
        holographic_data = self.qrg.create_holographic_glyph(
            identity="demo_holographic",
            spatial_dimensions=3,
            consciousness_layer=self.layer,
            qi_entanglement=True,
        )

        print("\n🔸 Holographic QRG Generated:")
        print(f"   📐 Spatial dimensions: {holographic_data['spatial_dimensions']}")
        print(f"   🎭 Consciousness layer: {holographic_data['consciousness_layer']}")
        print(f"   ⚛️ Quantum entangled: {holographic_data['qi_entangled']}")

        projection_matrices = holographic_data["projection_matrices"]
        print(f"   🎬 Projection layers: {len(projection_matrices)}")
        for layer in projection_matrices:
            print(
                f"      Layer {layer['layer']}: z={layer['z_depth']}, opacity={layer['opacity']}"
            )

        interaction_zones = holographic_data["interaction_zones"]
        print(f"   👆 Interaction zones: {len(interaction_zones)}")
        for zone in interaction_zones:
            print(f"      {zone['zone_id']}: {zone['interaction_type']}")

    def _switch_communication_layer(self):
        """Switch communication layer"""
        print(
            f"\n{self.style['color']}🎭 Communication Layer Selection{self.style['color']}\033[0m"
        )

        layers = ["poetic", "user_friendly", "academic"]

        print("Available communication layers:")
        for i, layer in enumerate(layers):
            description = {
                "poetic": "🎨 Creative, metaphorical, inspirational",
                "user_friendly": "💬 Conversational, practical, accessible",
                "academic": "📚 Technical, precise, specification-focused",
            }
            current = " (current)" if layer == self.layer else ""
            print(f"   {i}: {layer} - {description[layer]}{current}")

        try:
            choice = int(input("Select layer (0-2): "))
            new_layer = layers[choice]

            if new_layer != self.layer:
                self.layer = new_layer
                self.style = LAYER_STYLES[new_layer]
                print(f"\n✅ Switched to {new_layer} communication layer")
            else:
                print(f"\n📍 Already using {new_layer} layer")

        except (ValueError, IndexError):
            print("Invalid selection")

    def _show_system_status(self):
        """Show comprehensive system status"""
        print(
            f"\n{self.style['color']}📊 QRG System Status Report{self.style['color']}\033[0m"
        )

        # System information
        print("\n🔸 System Information:")
        print("   🌌 QRG Core: Initialized")
        print("   ⚛️ Quantum Entropy: Active")
        print("   🌉 LUKHAS Bridge: Connected")
        print(f"   🎭 Communication Layer: {self.layer}")

        # Identity information
        if self.current_identity:
            print("\n🔸 Current Identity:")
            print(f"   🆔 Lambda ID: {self.current_identity.lambda_id}")
            print(f"   🎫 Access Tier: {self.current_identity.access_tier.value}")
            print(f"   📅 Created: {self.current_identity.created_timestamp}")
            if self.current_identity.last_authentication:
                print(f"   🔐 Last Auth: {self.current_identity.last_authentication}")
        else:
            print("\n🔸 Current Identity: None (create identity with option 1)")

        # Entropy quality
        print("\n🔸 Quantum Entropy Quality:")
        quality_report = self.qi_entropy.get_entropy_quality_report()
        print(f"   📊 Source: {quality_report['entropy_source']}")
        print(f"   💾 Pool: {quality_report['pool_size']} bytes")

        available_sources = quality_report["available_sources"]
        active_sources = sum(available_sources.values())
        print(f"   🌐 Active Sources: {active_sources}/{len(available_sources)}")

    def _get_consciousness_context(self) -> dict[str, Any]:
        """Get consciousness context from user input"""
        print(
            f"\n{self.style['color']}🧠 Consciousness Profile Setup:{self.style['color']}\033[0m"
        )

        if self.layer == "poetic":
            print("🎭 Attune your digital essence to the frequencies of your soul...")
        elif self.layer == "user_friendly":
            print("😊 Tell us a bit about your personality for personalization:")
        else:
            print("Input consciousness parameters for profile generation:")

        # Emotional baseline (simplified input)
        try:
            valence = float(
                input("Emotional valence (-1.0 to 1.0, 0=neutral): ") or "0.0"
            )
            valence = max(-1.0, min(1.0, valence))
        except ValueError:
            valence = 0.0

        try:
            arousal = float(
                input("Arousal level (0.0 to 1.0, 0.5=balanced): ") or "0.5"
            )
            arousal = max(0.0, min(1.0, arousal))
        except ValueError:
            arousal = 0.5

        # Communication preference
        comm_prefs = ["poetic", "user_friendly", "academic"]
        print("Preferred communication style:")
        for i, pref in enumerate(comm_prefs):
            print(f"   {i}: {pref}")

        try:
            comm_choice = int(input("Select preference (0-2): "))
            preferred_layer = comm_prefs[comm_choice]
        except (ValueError, IndexError):
            preferred_layer = self.layer

        return {
            "valence": valence,
            "arousal": arousal,
            "dominance": 0.5,  # Default
            "preferred_layer": preferred_layer,
            "consciousness_tracking": True,
            "privacy_level": 3,
        }

    def _create_emotion_context(self, emotion: str) -> ConsciousnessContext:
        """Create consciousness context for specific emotion"""
        emotion_profiles = {
            "joy": ConsciousnessContext(
                emotional_state="joy",
                valence=0.8,
                arousal=0.7,
                dominance=0.6,
                current_context="positive_interaction",
            ),
            "calm": ConsciousnessContext(
                emotional_state="calm",
                valence=0.3,
                arousal=0.2,
                dominance=0.5,
                current_context="peaceful_state",
            ),
            "focus": ConsciousnessContext(
                emotional_state="focus",
                valence=0.1,
                arousal=0.8,
                dominance=0.9,
                current_context="concentrated_work",
            ),
            "stress": ConsciousnessContext(
                emotional_state="stress",
                valence=-0.5,
                arousal=0.9,
                dominance=0.3,
                current_context="challenging_situation",
            ),
            "neutral": ConsciousnessContext(
                emotional_state="neutral",
                valence=0.0,
                arousal=0.5,
                dominance=0.5,
                current_context="baseline_state",
            ),
        }

        return emotion_profiles.get(emotion, emotion_profiles["neutral"])

    def _display_identity_info(
        self, identity: SymbolicIdentity, generation_time: float
    ):
        """Display symbolic identity information"""
        print("\n📋 Identity Details:")
        print(f"   🆔 Lambda ID: {identity.lambda_id}")
        print(f"   🔑 SID Hash: {identity.sid_hash}")
        print(f"   🎫 Access Tier: {identity.access_tier.value}")
        print(f"   📅 Created: {identity.created_timestamp}")
        print(f"   ⏱️ Generation time: {generation_time:.4f} seconds")

        consciousness = identity.consciousness_profile
        print("   🧠 Consciousness Profile:")
        print(f"      - Communication style: {consciousness['communication_style']}")
        print(f"      - Emotional baseline: {consciousness['emotional_baseline']}")
        print(f"      - Privacy preferences: {consciousness['privacy_preferences']}")

    def _display_glyph_info(self, glyph, generation_time: float):
        """Display QRG glyph information"""
        print("\n📋 QRG Details:")
        print(f"   🔮 Glyph ID: {glyph.glyph_id}")
        print(f"   ⚛️ Quantum signature: {glyph.qi_signature[:32]}...")
        print(f"   🧠 Consciousness fingerprint: {glyph.consciousness_fingerprint}")
        print(f"   📐 Visual matrix: {glyph.visual_matrix.shape}")
        print(f"   🎬 Animation frames: {len(glyph.animation_frames)}")
        print(f"   ⏰ Valid until: {glyph.temporal_validity}")
        print(f"   ⏱️ Generation time: {generation_time:.4f} seconds")

    def _graceful_exit(self):
        """Graceful demo exit"""
        if self.layer == "poetic":
            print(
                f"\n{self.style['color']}🌌 Your quantum consciousness returns to the digital cosmos... Farewell!{self.style['color']}\033[0m"
            )
        elif self.layer == "user_friendly":
            print(
                f"\n{self.style['color']}👋 Thanks for trying QRG! Your quantum identity awaits your return.{self.style['color']}\033[0m"
            )
        else:
            print(
                f"\n{self.style['color']}QRG demonstration session terminated. System state preserved.{self.style['color']}\033[0m"
            )


def run_batch_demo(layer: str, security_tier: int):
    """Run non-interactive batch demonstration"""
    print(f"🌌 QRG Batch Demo - {layer.title()} Mode")
    print("=" * 50)

    demo = QRGDemo(layer)

    # Create sample identity
    print("\n🔸 Creating sample identity...")
    identity = demo.lukhas_bridge.generate_symbolic_identity(
        symbolic_phrase="quantum consciousness awakens",
        access_tier=LukhasAccessTier.TIER_3,
    )
    demo.current_identity = identity
    print(f"   ✅ Identity created: {identity.lambda_id}")

    # Generate sample QRG
    print(f"\n🔸 Generating QRG with security tier {security_tier}...")
    glyph = demo.qrg.generate_auth_glyph(
        user_identity=identity.sid_hash,
        consciousness_context=ConsciousnessContext(),
        security_tier=security_tier,
        animation_type="gentle_pulse",
    )
    print(f"   ✅ QRG generated: {glyph.glyph_id}")

    # Demonstrate quantum entropy
    print("\n🔸 Testing quantum entropy...")
    qi_bytes = demo.qi_entropy.generate_quantum_bytes(16)
    print(f"   ⚛️ Quantum bytes: {qi_bytes.hex()}")

    # Show system status
    print("\n🔸 System status:")
    quality_report = demo.qi_entropy.get_entropy_quality_report()
    print(f"   📊 Entropy source: {quality_report['entropy_source']}")
    print(f"   💾 Pool size: {quality_report['pool_size']} bytes")

    print("\n✅ Batch demo completed successfully!")


def main():
    """Main demo entry point"""
    parser = argparse.ArgumentParser(
        description="QRG Quantum Resonance Glyph Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo.py --interactive                    # Interactive demo with default settings
  python demo.py --layer poetic --interactive     # Interactive demo in poetic mode
  python demo.py --layer academic --security-tier 5  # Batch demo with high security
        """,
    )

    parser.add_argument(
        "--layer",
        choices=["poetic", "user_friendly", "academic"],
        default="user_friendly",
        help="Communication layer for demo output",
    )

    parser.add_argument(
        "--security-tier",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Security tier for QRG generation (1-5)",
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive demo mode"
    )

    args = parser.parse_args()

    try:
        if args.interactive:
            demo = QRGDemo(args.layer)
            demo.run_interactive_demo()
        else:
            run_batch_demo(args.layer, args.security_tier)

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
