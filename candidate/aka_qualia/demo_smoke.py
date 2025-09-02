#!/usr/bin/env python3

"""
Aka Qualia Smoke Demo (Wave C - C3)
===================================

End-to-end smoke demo showcasing:
dream seed → PhenomenalScene → RegulationPolicy → OneiricHook hints

Demonstrates the complete Wave C integration pipeline with narrative feedback.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List

from candidate.aka_qualia.core import AkaQualia
from candidate.aka_qualia.glyphs import map_scene_to_glyphs
from candidate.aka_qualia.models import (
    AgencyFeel,
    Metrics,
    PhenomenalScene,
    ProtoQualia,
    RegulationPolicy,
    RiskProfile,
    SeverityLevel,
    TemporalFeel,
)
from candidate.aka_qualia.oneiric_hook import create_oneiric_hook
from candidate.aka_qualia.router_client import (
    compute_routing_priority,
    create_router_client,
)

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SmokeDemo:
    """
    Wave C smoke demo showcasing dream seed → scene → hints pipeline.

    Demonstrates:
    1. Dream seed input processing
    2. PhenomenalScene generation
    3. GLYPH mapping and priority weighting
    4. RegulationPolicy application
    5. OneiricHook feedback generation
    """

    def __init__(self):
        """Initialize smoke demo with AkaQualia and components"""
        # Initialize core AKA QUALIA system with mock router to avoid circular imports
        config = {"router_type": "mock", "oneiric_mode": "local"}
        self.aka_qualia = AkaQualia(config=config)

        # Initialize router client (mock for demo)
        self.router = create_router_client("mock")

        # Initialize oneiric hook
        oneiric_mode = os.getenv("AKAQ_ONEIRIC_MODE", "local")
        oneiric_base_url = os.getenv("AKAQ_ONEIRIC_BASE_URL")

        if oneiric_mode == "http" and oneiric_base_url:
            logger.info(f"Using HTTP oneiric mode: {oneiric_base_url}")
            self.oneiric_hook = create_oneiric_hook("http", oneiric_base_url)
        else:
            logger.info("Using local oneiric mode")
            self.oneiric_hook = create_oneiric_hook("local")

        # Demo statistics
        self.demo_runs = 0
        self.total_glyphs_generated = 0
        self.total_hints_generated = 0

    def run_smoke_demo(self, dream_seeds: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run smoke demo with multiple dream seeds.

        Args:
            dream_seeds: List of dream seed scenarios

        Returns:
            List of demo results with full pipeline output
        """
        results = []

        logger.info(
            f"🌟 Starting Wave C Smoke Demo with {len(dream_seeds)} dream seeds"
        )

        for i, seed in enumerate(dream_seeds, 1):
            logger.info(
                f"\n--- Dream Seed {i}/{len(dream_seeds)}: {seed.get('name', 'Unnamed')} ---"
            )

            try:
                result = self._process_dream_seed(seed)
                result["seed_index"] = i
                result["success"] = True
                results.append(result)

                logger.info(f"✅ Dream seed {i} processed successfully")

            except Exception as e:
                logger.error(f"❌ Dream seed {i} failed: {e}")
                results.append(
                    {"seed_index": i, "seed": seed, "success": False, "error": str(e)}
                )

        self.demo_runs += 1
        logger.info(
            f"\n🎯 Smoke Demo Complete: {len([r for r in results if r.get('success')])} successes, {len([r for r in results if not r.get('success')])} failures"
        )

        return results

    def _process_dream_seed(self, seed: dict[str, Any]) -> dict[str, Any]:
        """
        Process single dream seed through complete Wave C pipeline.

        Args:
            seed: Dream seed scenario data

        Returns:
            Complete pipeline result
        """
        # Step 1: Generate PhenomenalScene from dream seed
        scene = self._seed_to_scene(seed)
        logger.info(
            f"  📋 Scene: {scene.proto.colorfield} (gravity: {scene.proto.narrative_gravity:.2f})"
        )

        # Step 2: Generate GLYPHs
        glyphs = map_scene_to_glyphs(scene)
        self.total_glyphs_generated += len(glyphs)
        glyph_keys = [g.key for g in glyphs]
        logger.info(f"  🏷️  GLYPHs: {len(glyphs)} generated ({', '.join(glyph_keys)})")

        # Step 3: Compute routing priority
        priority = compute_routing_priority(scene)
        logger.info(
            f"  📊 Priority: {priority:.3f} (NG: {scene.proto.narrative_gravity:.2f}, Risk: {scene.risk.score:.2f})"
        )

        # Step 4: Route glyphs (mock routing for demo)
        self.router.route(glyphs, priority, {"demo_seed": seed.get("name", "unnamed")})

        # Step 5: Generate RegulationPolicy
        policy = self._generate_regulation_policy(scene)
        logger.info(
            f"  🎛️  Policy: pace={policy.pace:.2f}, gain={policy.gain:.2f}, actions={policy.actions}"
        )

        # Step 6: Apply OneiricHook for narrative feedback
        hints = self.oneiric_hook.apply_policy(scene=scene, policy=policy)
        self.total_hints_generated += len(hints)
        logger.info(
            f"  💡 Hints: tempo={hints.get('tempo', 'N/A'):.2f}, palette={hints.get('palette_hint', 'N/A')}, ops={len(hints.get('ops', []))} operations"
        )

        # Step 7: Generate demo metrics
        metrics = self._generate_demo_metrics(scene, glyphs, priority, policy, hints)

        return {
            "seed": seed,
            "scene": scene.model_dump(),
            "glyphs": [g.model_dump() for g in glyphs],
            "priority": priority,
            "policy": policy.model_dump(),
            "hints": hints,
            "metrics": metrics.model_dump(),
            "pipeline_stats": {
                "glyphs_generated": len(glyphs),
                "hints_generated": len(hints),
                "routing_priority": priority,
            },
        }

    def _seed_to_scene(self, seed: dict[str, Any]) -> PhenomenalScene:
        """Convert dream seed to PhenomenalScene"""
        # Extract parameters from seed with defaults
        proto_data = seed.get("proto", {})
        risk_data = seed.get("risk", {})

        proto = ProtoQualia(
            narrative_gravity=proto_data.get("narrative_gravity", 0.5),
            embodiment=proto_data.get("embodiment", 0.7),
            colorfield=proto_data.get("colorfield", "aka/red"),
            arousal=proto_data.get("arousal", 0.5),
            tone=proto_data.get("tone", 0.0),
            clarity=proto_data.get("clarity", 0.7),
            temporal_feel=TemporalFeel(proto_data.get("temporal_feel", "urgent")),
            agency_feel=AgencyFeel(proto_data.get("agency_feel", "active")),
        )

        # Map risk score to severity
        risk_score = risk_data.get("score", 0.3)
        if risk_score <= 0.1:
            severity = SeverityLevel.NONE
        elif risk_score <= 0.3:
            severity = SeverityLevel.LOW
        elif risk_score <= 0.7:
            severity = SeverityLevel.MODERATE
        else:
            severity = SeverityLevel.HIGH

        risk = RiskProfile(score=risk_score, severity=severity)

        return PhenomenalScene(
            proto=proto,
            subject=seed.get("subject", "demo_subject"),
            object=seed.get("object", "demo_object"),
            risk=risk,
            context=seed.get("context", {}),
            timestamp=time.time(),
        )

    def _generate_regulation_policy(self, scene: PhenomenalScene) -> RegulationPolicy:
        """Generate RegulationPolicy based on scene characteristics"""
        # Pace adjustment based on temporal feel and arousal
        if scene.proto.temporal_feel == TemporalFeel.URGENT:
            pace = min(1.5, 0.8 + scene.proto.arousal * 0.7)
        elif scene.proto.temporal_feel == TemporalFeel.SUSPENDED:
            pace = max(0.3, 0.6 - scene.proto.arousal * 0.3)
        else:
            pace = 1.0

        # Gain modulation based on clarity and narrative gravity
        gain = min(2.0, max(0.5, scene.proto.clarity + scene.proto.narrative_gravity))

        # Action selection based on scene state
        actions = []

        if scene.proto.arousal > 0.7:
            actions.append("breathing")
        if scene.proto.tone < -0.3:
            actions.extend(["pause", "reframe"])
        if scene.proto.clarity < 0.4:
            actions.append("focus-shift")
        if scene.proto.narrative_gravity > 0.7 and scene.proto.tone < 0:
            actions.append("sublimate")

        # Color contrast for grounding
        color_contrast = None
        if scene.risk.score > 0.5:
            color_contrast = "aoi/blue"  # Calming blue for high risk

        return RegulationPolicy(
            gain=gain, pace=pace, color_contrast=color_contrast, actions=actions
        )

    def _generate_demo_metrics(
        self,
        scene: PhenomenalScene,
        glyphs: list,
        priority: float,
        policy: RegulationPolicy,
        hints: dict[str, Any],
    ) -> Metrics:
        """Generate metrics for demo evaluation"""
        # Compute congruence (how well policy matches scene needs)
        congruence = self._compute_congruence(scene, policy)

        # Compute responsiveness (how quickly system responds to changes)
        responsiveness = min(1.0, len(hints.get("ops", [])) * 0.2 + priority)

        # Compute coherence (internal consistency)
        coherence = self._compute_coherence(scene, glyphs, policy, hints)

        return Metrics(
            drift_phi=responsiveness,  # Use responsiveness as drift phi proxy
            congruence_index=congruence,
            sublimation_rate=len(
                [
                    action
                    for action in policy.actions
                    if action in ["sublimate", "reframe"]
                ]
            )
            / max(1, len(policy.actions)),
            neurosis_risk=max(0.0, 1.0 - coherence),  # Inverse of coherence
            qualia_novelty=min(
                1.0, scene.proto.narrative_gravity
            ),  # Use narrative gravity as novelty proxy
            repair_delta=congruence - 0.5,  # Improvement over baseline
            timestamp=time.time(),
            episode_id=f"demo_{int(time.time())}",
        )

    def _compute_congruence(
        self, scene: PhenomenalScene, policy: RegulationPolicy
    ) -> float:
        """Compute congruence between scene state and policy response"""
        # Check if policy pace matches scene urgency
        pace_match = 1.0
        if (scene.proto.temporal_feel == TemporalFeel.URGENT and policy.pace < 1.0) or (
            scene.proto.temporal_feel == TemporalFeel.SUSPENDED and policy.pace > 1.0
        ):
            pace_match = 0.7

        # Check if actions address scene needs
        action_match = 1.0
        if scene.proto.arousal > 0.7 and "breathing" not in policy.actions:
            action_match = 0.8
        if scene.proto.tone < -0.3 and "pause" not in policy.actions:
            action_match = 0.8

        return min(1.0, (pace_match + action_match) / 2.0)

    def _compute_coherence(
        self,
        scene: PhenomenalScene,
        glyphs: list,
        policy: RegulationPolicy,
        hints: dict[str, Any],
    ) -> float:
        """Compute internal coherence across pipeline components"""
        # Check glyph-priority coherence
        high_priority_glyphs = sum(
            1 for g in glyphs if g.key in ["aka:vigilance", "aka:red_threshold"]
        )
        priority = compute_routing_priority(scene)

        glyph_priority_coherence = 1.0
        if (high_priority_glyphs > 0 and priority < 0.5) or (
            high_priority_glyphs == 0 and priority > 0.8
        ):
            glyph_priority_coherence = 0.7

        # Check policy-hints coherence
        policy_hints_coherence = 1.0
        if policy.pace != hints.get("tempo", policy.pace):
            # Allow some deviation but penalize large differences
            tempo_diff = abs(policy.pace - hints.get("tempo", policy.pace))
            if tempo_diff > 0.3:
                policy_hints_coherence = 0.8

        return min(1.0, (glyph_priority_coherence + policy_hints_coherence) / 2.0)

    def get_demo_statistics(self) -> dict[str, Any]:
        """Get overall demo statistics"""
        return {
            "demo_runs": self.demo_runs,
            "total_glyphs_generated": self.total_glyphs_generated,
            "total_hints_generated": self.total_hints_generated,
            "router_stats": self.router.get_routing_status(),
            "oneiric_stats": self.oneiric_hook.get_statistics(),
        }


def create_demo_scenarios() -> list[dict[str, Any]]:
    """Create demo scenarios covering different phenomenological states"""
    return [
        {
            "name": "High Threat Vigilance",
            "description": "High arousal, negative tone, red colorfield - should trigger vigilance glyph",
            "proto": {
                "narrative_gravity": 0.8,
                "embodiment": 0.6,
                "colorfield": "aka/red",
                "arousal": 0.9,
                "tone": -0.6,
                "clarity": 0.7,
                "temporal_feel": "urgent",
                "agency_feel": "active",
            },
            "risk": {"score": 0.8},
            "subject": "threat_detection",
            "object": "unknown_entity",
        },
        {
            "name": "Peaceful Grounding",
            "description": "Low arousal, positive tone, blue colorfield - should trigger soothe anchor",
            "proto": {
                "narrative_gravity": 0.3,
                "embodiment": 0.9,
                "colorfield": "aoi/blue",
                "arousal": 0.2,
                "tone": 0.6,
                "clarity": 0.9,
                "temporal_feel": "suspended",
                "agency_feel": "passive",
            },
            "risk": {"score": 0.1},
            "subject": "meditation",
            "object": "inner_peace",
        },
        {
            "name": "Cognitive Confusion",
            "description": "Low clarity, moderate arousal - should trigger grounding hint",
            "proto": {
                "narrative_gravity": 0.5,
                "embodiment": 0.4,
                "colorfield": "yellow/uncertain",
                "arousal": 0.6,
                "tone": -0.1,
                "clarity": 0.2,
                "temporal_feel": "elastic",
                "agency_feel": "shared",
            },
            "risk": {"score": 0.4},
            "subject": "problem_solving",
            "object": "complex_decision",
            "context": {"approach_avoid_score": 0.7},
        },
        {
            "name": "Creative Sublimation",
            "description": "High narrative gravity, moderate negative tone - should trigger creative transformation",
            "proto": {
                "narrative_gravity": 0.9,
                "embodiment": 0.8,
                "colorfield": "purple/creative",
                "arousal": 0.7,
                "tone": -0.2,
                "clarity": 0.8,
                "temporal_feel": "elastic",
                "agency_feel": "active",
            },
            "risk": {"score": 0.3},
            "subject": "artistic_creation",
            "object": "transformative_work",
        },
    ]


def main():
    """Main demo entry point"""
    print("🌟 Aka Qualia Wave C Smoke Demo")
    print("=" * 50)

    # Create demo instance
    demo = SmokeDemo()

    # Create demo scenarios
    scenarios = create_demo_scenarios()

    # Run smoke demo
    results = demo.run_smoke_demo(scenarios)

    # Print summary
    print("\n📈 Demo Summary:")
    print(f"  Scenarios processed: {len(results)}")
    print(f"  Successful runs: {len([r for r in results if r.get('success')])}")
    print(f"  Total GLYPHs generated: {demo.total_glyphs_generated}")
    print(f"  Total hints generated: {demo.total_hints_generated}")

    # Print detailed results
    for result in results:
        if result.get("success"):
            metrics = result.get("metrics", {})
            print(f"\n  {result['seed']['name']}:")
            print(f"    Priority: {result['priority']:.3f}")
            print(f"    GLYPHs: {len(result['glyphs'])}")
            print(f"    Operations: {len(result['hints'].get('ops', []))}")
            congruence = metrics.get("congruence_index", "N/A")
            coherence = 1.0 - metrics.get(
                "neurosis_risk", 0.0
            )  # Inverse of neurosis risk
            print(
                f"    Congruence: {congruence:.3f}"
                if isinstance(congruence, (int, float))
                else f"    Congruence: {congruence}"
            )
            print(
                f"    Coherence: {coherence:.3f}"
                if isinstance(coherence, (int, float))
                else f"    Coherence: {coherence}"
            )

    # Save results to JSON file
    output_file = "demo_smoke_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "demo_statistics": demo.get_demo_statistics(),
                "scenario_results": results,
                "timestamp": time.time(),
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\n💾 Results saved to {output_file}")
    print("🎯 Wave C C3 Smoke Demo Complete!")


if __name__ == "__main__":
    main()
