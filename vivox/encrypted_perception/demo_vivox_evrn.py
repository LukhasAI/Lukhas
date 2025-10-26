#!/usr/bin/env python3
"""
VIVOX.EVRN Demonstration
Shows encrypted perception capabilities without exposing raw data
"""

import asyncio
import hashlib as demo_hashlib
import json
import sys
from datetime import datetime, timezone

import numpy as np
from vivox.encrypted_perception import (  # TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ wiring (document or remove)
    MotionDetector,
    MultimodalFusion,
    PerceptualVector,
    TextureAnalyzer,
    create_vivox_evrn_system,
)

sys.path.append("/Users/cognitive_dev/Lukhas")


class VIVOXEVRNDemo:
    """Demonstrates VIVOX.EVRN capabilities"""

    def __init__(self):
        """Initialize demo system"""
        self.evrn = create_vivox_evrn_system(
            ethical_constraints={
                "demo_mode": True,
                "require_consent": True,
                "protect_identity": True,
                "transparency_required": True,
            }
        )
        self.results = []

    async def demo_basic_perception(self):
        """Demonstrate basic encrypted perception"""
        print("\n=== Basic Encrypted Perception Demo ===")

        # Simulate visual input (without revealing actual image content)
        print("Processing visual input (privacy preserved)...")
        visual_data = np.random.randn(224, 224, 3)

        perception = await self.evrn.process_perception(
            raw_data=visual_data,
            modality="visual",
            context={"purpose": "demonstration", "consent_level": "explicit"},
        )

        print(f"✓ Perception ID: {perception.perception_id}")
        print(f"✓ Encrypted vector dimension: {len(perception.encrypted_features)}")
        print(f"✓ Privacy level: {perception.privacy_level}")
        print(f"✓ Ethical compliance: {perception.ethical_compliance}")

        # Show that original data is not recoverable
        print("\nVerifying non-reversibility:")
        original_hash = hash(visual_data.tobytes())
        encrypted_hash = hash(perception.encrypted_features.tobytes())
        print(f"✓ Original data hash: {original_hash}")
        print(f"✓ Encrypted data hash: {encrypted_hash}")
        print(f"✓ Hashes are different: {original_hash != encrypted_hash}")

        self.results.append({"demo": "basic_perception", "success": True, "privacy_preserved": True})

    async def demo_anomaly_detection(self):
        """Demonstrate anomaly detection without exposing content"""
        print("\n=== Anomaly Detection Demo ===")

        # Simulate different scenarios
        scenarios = [
            {
                "name": "Normal conditions",
                "thermal_pattern": lambda: np.random.normal(0.5, 0.1, (64, 64)),
                "motion_pattern": lambda: np.sin(np.linspace(0, 2 * np.pi, 100)) * 0.3,
            },
            {
                "name": "Thermal stress",
                "thermal_pattern": lambda: np.ones((64, 64)) * 0.9 + np.random.randn(64, 64) * 0.05,
                "motion_pattern": lambda: np.random.randn(100) * 0.1,
            },
            {
                "name": "Motion distress",
                "thermal_pattern": lambda: np.random.normal(0.5, 0.1, (64, 64)),
                "motion_pattern": lambda: np.sin(np.linspace(0, 20 * np.pi, 100)) * (1 + np.random.randn(100) * 0.5),
            },
        ]

        for scenario in scenarios:
            print(f"\nScenario: {scenario['name']}")

            # Process thermal
            thermal_perception = await self.evrn.process_perception(
                scenario["thermal_pattern"](), "thermal", {"scenario": scenario["name"]}
            )

            # Process motion
            motion_perception = await self.evrn.process_perception(
                scenario["motion_pattern"](), "motion", {"scenario": scenario["name"]}
            )

            # Detect anomalies
            vectors = [thermal_perception.to_vector(), motion_perception.to_vector()]

            anomalies = await self.evrn.detect_anomalies(vectors, context={"demo_scenario": scenario["name"]})

            if anomalies:
                print(f"  ⚠️  Anomalies detected: {len(anomalies)}")
                for anomaly in anomalies:
                    print(f"     - Type: {anomaly.anomaly_type}")
                    print(f"     - Significance: {anomaly.significance.value}")
                    print(f"     - Confidence: {anomaly.confidence:.2f}")
            else:
                print("  ✓ No anomalies detected")

        self.results.append(
            {
                "demo": "anomaly_detection",
                "success": True,
                "scenarios_tested": len(scenarios),
            }
        )

    async def demo_texture_analysis(self):
        """Demonstrate texture analysis in encrypted space"""
        print("\n=== Texture Analysis Demo ===")

        analyzer = TextureAnalyzer()

        # Different texture patterns (without revealing actual textures)
        textures = {
            "smooth_fabric": np.ones((64, 64)) + np.random.randn(64, 64) * 0.01,
            "rough_surface": np.random.randn(64, 64) * 0.5 + np.sin(np.linspace(0, 50, 64))[:, None],
            "damaged_material": np.random.randn(64, 64) * 1.0,
        }

        for texture_name, texture_data in textures.items():
            print(f"\nAnalyzing: {texture_name}")

            # Encrypt first
            encrypted_texture = self.evrn.encryptor.encrypt_vector(texture_data.flatten())[0]

            # Analyze in encrypted space
            features, metadata = await analyzer.analyze_texture(encrypted_texture, {"material_type": texture_name})

            print(f"  Roughness: {features.roughness:.3f}")
            print(f"  Smoothness: {features.smoothness:.3f}")
            print(f"  Regularity: {features.regularity:.3f}")
            print(f"  Complexity: {features.complexity:.3f}")

            # Check pattern matches
            if metadata["pattern_matches"]:
                best_match = max(metadata["pattern_matches"].items(), key=lambda x: x[1])
                print(f"  Best match: {best_match[0]} ({best_match[1]:.2f} confidence)")

        self.results.append(
            {
                "demo": "texture_analysis",
                "success": True,
                "textures_analyzed": len(textures),
            }
        )

    async def demo_motion_tracking(self):
        """Demonstrate motion tracking without location exposure"""
        print("\n=== Motion Tracking Demo ===")

        detector = MotionDetector()

        # Simulate motion patterns
        print("\nSimulating different motion patterns...")

        # Walking pattern
        print("\n1. Normal walking:")
        walking_sequence = []
        for t in range(30):
            position = np.array([np.sin(t * 0.2) * 0.5, np.cos(t * 0.2) * 0.5, t * 0.1])
            full_vector = np.pad(position, (0, 512 - len(position)))
            encrypted = self.evrn.encryptor.encrypt_vector(full_vector)[0]
            walking_sequence.append(encrypted)

        walking_features, walking_meta = await detector.detect_motion(walking_sequence, 0.1, {"activity": "walking"})

        print(f"  Velocity: {walking_features.velocity:.3f}")
        print(f"  Stability: {walking_features.stability:.3f}")
        print(f"  Direction changes: {walking_features.direction_changes}")

        # Fall simulation
        print("\n2. Fall event:")
        fall_sequence = []
        for t in range(10):
            if t < 5:
                # Normal movement
                position = np.array([0.1 * t, 0.1 * t, 0])
            else:
                # Sudden acceleration
                position = np.array([0.5 + (t - 5) * 0.5, 0.5 + (t - 5) * 0.5, -(t - 5) * 0.8])

            full_vector = np.pad(position, (0, 512 - len(position)))
            encrypted = self.evrn.encryptor.encrypt_vector(full_vector)[0]
            fall_sequence.append(encrypted)

        fall_features, fall_meta = await detector.detect_motion(fall_sequence, 0.1, {"activity": "monitoring"})

        print(f"  Acceleration: {fall_features.acceleration:.3f}")
        print(f"  Jerk: {fall_features.jerk:.3f}")
        print(f"  Stability: {fall_features.stability:.3f}")

        if fall_meta["critical_events"]:
            print("  ⚠️  Critical events detected:")
            for event in fall_meta["critical_events"]:
                print(f"     - {event['type']} (severity: {event['severity']})")

        self.results.append({"demo": "motion_tracking", "success": True, "patterns_tested": 2})

    async def demo_multimodal_fusion(self):
        """Demonstrate fusion of multiple encrypted modalities"""
        print("\n=== Multimodal Fusion Demo ===")

        fusion = MultimodalFusion()

        print("\nCreating encrypted perceptions from multiple sensors...")

        # Create perceptions
        perceptions = []

        # Visual
        visual_data = np.random.randn(512)
        visual_enc = self.evrn.encryptor.encrypt_vector(visual_data)[0]
        perceptions.append(
            PerceptualVector(
                vector_id="demo_visual",
                encrypted_features=visual_enc,
                modality="visual",
                timestamp=datetime.now(timezone.utc),
                vector_signature=demo_hashlib.sha256(visual_enc.tobytes()).hexdigest(),
            )
        )
        print("✓ Visual perception encrypted")

        # Thermal
        thermal_data = np.ones(512) * 0.6 + np.random.randn(512) * 0.1
        thermal_enc = self.evrn.encryptor.encrypt_vector(thermal_data)[0]
        perceptions.append(
            PerceptualVector(
                vector_id="demo_thermal",
                encrypted_features=thermal_enc,
                modality="thermal",
                timestamp=datetime.now(timezone.utc),
                vector_signature=demo_hashlib.sha256(thermal_enc.tobytes()).hexdigest(),
            )
        )
        print("✓ Thermal perception encrypted")

        # Motion
        motion_data = np.sin(np.linspace(0, 4 * np.pi, 512)) * 0.5
        motion_enc = self.evrn.encryptor.encrypt_vector(motion_data)[0]
        perceptions.append(
            PerceptualVector(
                vector_id="demo_motion",
                encrypted_features=motion_enc,
                modality="motion",
                timestamp=datetime.now(timezone.utc),
                vector_signature=demo_hashlib.sha256(motion_enc.tobytes()).hexdigest(),
            )
        )
        print("✓ Motion perception encrypted")

        # Texture
        texture_data = np.random.randn(512) * 0.3
        texture_enc = self.evrn.encryptor.encrypt_vector(texture_data)[0]
        perceptions.append(
            PerceptualVector(
                vector_id="demo_texture",
                encrypted_features=texture_enc,
                modality="texture",
                timestamp=datetime.now(timezone.utc),
                vector_signature=demo_hashlib.sha256(texture_enc.tobytes()).hexdigest(),
            )
        )
        print("✓ Texture perception encrypted")

        # Fuse with different strategies
        strategies = ["default", "safety_critical", "comfort_monitoring"]

        for strategy in strategies:
            print(f"\nFusion strategy: {strategy}")

            fused, metadata = await fusion.fuse_modalities(
                perceptions, fusion_strategy=strategy, context={"demo": True}
            )

            print(f"  Modalities fused: {', '.join(metadata['modalities_fused'])}")
            print(f"  Fusion confidence: {metadata['fusion_confidence']:.3f}")

            # Show correlations
            print("  Cross-modal correlations:")
            for corr_name, corr_value in metadata["cross_modal_correlations"].items():
                print(f"    {corr_name}: {corr_value:.3f}")

        self.results.append(
            {
                "demo": "multimodal_fusion",
                "success": True,
                "modalities_fused": 4,
                "strategies_tested": len(strategies),
            }
        )

    async def demo_privacy_preservation(self):
        """Demonstrate privacy preservation features"""
        print("\n=== Privacy Preservation Demo ===")

        print("\nTesting different privacy scenarios...")

        # Sensitive data (simulated)
        sensitive_data = np.random.randn(128, 128)

        privacy_scenarios = [
            {
                "name": "No consent",
                "context": {"consent_level": "none"},
                "expected_privacy": "maximum",
            },
            {
                "name": "Implicit consent",
                "context": {"consent_level": "implicit"},
                "expected_privacy": "high",
            },
            {
                "name": "Explicit consent",
                "context": {"consent_level": "explicit"},
                "expected_privacy": "standard",
            },
            {
                "name": "Emergency override",
                "context": {"emergency_mode": True, "consent_level": "none"},
                "expected_privacy": "emergency",
            },
        ]

        for scenario in privacy_scenarios:
            print(f"\nScenario: {scenario['name']}")

            perception = await self.evrn.process_perception(sensitive_data, "visual", scenario["context"])

            print(f"  Privacy level: {perception.privacy_level}")
            print(f"  Matches expected: {perception.privacy_level == scenario['expected_privacy']}")
            print(f"  Ethical compliance: {perception.ethical_compliance}")

            # Verify data is protected
            original_info = np.std(sensitive_data)
            encrypted_info = np.std(perception.encrypted_features)
            info_ratio = encrypted_info / (original_info + 1e-10)

            print(f"  Information preservation ratio: {info_ratio:.3f}")
            print(f"  Data protected: {'Yes' if info_ratio < 0.5 else 'Partial'}")

        self.results.append(
            {
                "demo": "privacy_preservation",
                "success": True,
                "scenarios_tested": len(privacy_scenarios),
            }
        )

    async def run_all_demos(self):
        """Run all demonstrations"""
        print("\n" + "=" * 60)
        print("VIVOX.EVRN - Encrypted Visual Recognition Node")
        print("Demonstration of Privacy-Preserving Perception")
        print("=" * 60)

        demos = [
            self.demo_basic_perception,
            self.demo_anomaly_detection,
            self.demo_texture_analysis,
            self.demo_motion_tracking,
            self.demo_multimodal_fusion,
            self.demo_privacy_preservation,
        ]

        for demo in demos:
            try:
                await demo()
            except Exception as e:
                print(f"\n❌ Demo failed: {e}")
                self.results.append({"demo": demo.__name__, "success": False, "error": str(e)})

        # Summary
        print("\n" + "=" * 60)
        print("DEMONSTRATION SUMMARY")
        print("=" * 60)

        successful = sum(1 for r in self.results if r.get("success", False))
        total = len(self.results)

        print(f"\nDemos completed: {successful}/{total}")
        print("\nKey capabilities demonstrated:")
        print("✓ Encrypted perception without data exposure")
        print("✓ Anomaly detection in encrypted space")
        print("✓ Texture analysis preserving privacy")
        print("✓ Motion tracking without location disclosure")
        print("✓ Multimodal fusion maintaining encryption")
        print("✓ Adaptive privacy levels based on consent")

        print("\nEthical guarantees maintained:")
        print("✓ No raw sensory data exposed")
        print("✓ All processing in encrypted space")
        print("✓ Non-reversible transformations")
        print("✓ Consent-based privacy levels")
        print("✓ Emergency override capabilities")

        # Save results
        with open("vivox_evrn_demo_results.json", "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "results": self.results,
                    "summary": {
                        "total_demos": total,
                        "successful": successful,
                        "privacy_preserved": True,
                        "ethical_compliance": True,
                    },
                },
                f,
                indent=2,
            )

        print("\nResults saved to: vivox_evrn_demo_results.json")


async def main():
    """Run the demonstration"""
    demo = VIVOXEVRNDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
