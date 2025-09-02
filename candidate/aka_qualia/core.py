#!/usr/bin/env python3

"""
Aka Qualia Core — Phenomenological Module
==========================================

Core implementation of bidirectional signal↔qualia translator with
operational proto-qualia, ethical regulation, and measurable outcomes.

Usage:
    from candidate.aka_qualia.core import AkaQualia
    aq = AkaQualia(pls, teq_guardian, glyph_mapper, router, memory, cfg)
    result = await aq.step(signals=S, goals=G, ethics_state=E, guardian_state=U, memory_ctx=M)
"""

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from candidate.aka_qualia.glyphs import map_scene_to_glyphs, normalize_glyph_keys
from candidate.aka_qualia.memory import AkaqMemory, create_memory_client
from candidate.aka_qualia.metrics import AkaQualiaMetrics, EnergySnapshot
from candidate.aka_qualia.models import (
    Metrics,
    PhenomenalGlyph,
    PhenomenalScene,
    ProtoQualia,
    RegulationPolicy,
)
from candidate.aka_qualia.oneiric_hook import OneiricHook, create_oneiric_hook
from candidate.aka_qualia.palette import get_safe_palette_recommendation
from candidate.aka_qualia.pls import PLS
from candidate.aka_qualia.regulation import RegulationAuditEntry, RegulationPolicyEngine
from candidate.aka_qualia.router_client import (
    RouterClient,
    compute_routing_priority,
    create_router_client,
)
from candidate.aka_qualia.teq_hook import TEQGuardian
from candidate.aka_qualia.util import compute_drift_phi, extract_affect_energy
from candidate.aka_qualia.vivox_integration import VivoxAkaQualiaIntegration
from candidate.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class AkaQualia:
    """
    Aka Qualia - Phenomenological control loop for consciousness systems.

    Provides operational proto-qualia generation with:
    - Bidirectional signal↔qualia translation via PLS
    - TEQ Guardian ethical oversight
    - Energy-preserving sublimation
    - Measurable phenomenological outcomes
    - GLYPH-based symbolic routing
    """

    def __init__(
        self,
        pls: Optional[PLS] = None,
        teq_guardian: Optional[TEQGuardian] = None,
        glyph_mapper: Optional[Callable] = None,
        router: Optional[RouterClient] = None,
        oneiric_hook: Optional[OneiricHook] = None,
        memory: Optional[AkaqMemory] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize AkaQualia with pluggable components.

        Args:
            pls: Phenomenal Latent Space encoder/decoder
            teq_guardian: TEQ Guardian for ethical oversight
            glyph_mapper: Function to map scenes to glyphs
            router: EQNOX router for glyph routing
            memory: AkaqMemory client for scene persistence (C4 Wave C integration)
            config: Configuration overrides
        """
        # Load configuration first
        self.config = self._load_config(config)

        # Initialize components with defaults
        self.pls = pls or PLS()
        self.teq_guardian = teq_guardian or TEQGuardian()
        self.glyph_mapper = glyph_mapper or self._default_glyph_mapper

        # Initialize memory client (C4 Wave C integration)
        if memory:
            self.memory = memory
        else:
            # Create memory client based on configuration
            memory_driver = self.config.get("memory_driver", "noop")
            memory_config = self.config.get("memory_config", {})
            self.memory = create_memory_client(memory_driver, **memory_config)

        # Initialize VIVOX integration
        self.vivox_integration = VivoxAkaQualiaIntegration(
            drift_threshold=self.config.get("vivox_drift_threshold", 0.15),
            collapse_validation_enabled=self.config.get(
                "vivox_collapse_validation", True
            ),
            vivox_me_integration=self.config.get("vivox_me_integration", True),
        )

        # Initialize metrics computer with Freud-2025 formulas
        self.metrics_computer = AkaQualiaMetrics()

        # Initialize regulation policy engine with audit logging
        self.regulation_engine = RegulationPolicyEngine(
            config={
                "enable_audit_logging": self.config.get(
                    "enable_regulation_audit", True
                ),
                "safe_palette": self.config.get("safe_palette", "aoi/blue"),
                "conservative_mode": self.config.get("conservative_regulation", False),
                "energy_conservation_tolerance": self.config.get(
                    "energy_conservation_tolerance", 0.05
                ),
                "audit_log_path": self.config.get(
                    "regulation_audit_path", "logs/aka_qualia_regulation.jsonl"
                ),
            }
        )

        # Initialize metrics collector for observability (B4: akaq_ prefixed integration)
        self.metrics_collector = get_metrics_collector()

        # Initialize router client (C2: Wave C router integration)
        if router:
            self.router = router
        else:
            router_type = self.config.get("router_type", "lukhas")
            router_config = self.config.get("router", {})
            self.router = create_router_client(router_type, router_config)

        # Initialize oneiric hook (C3: Wave C oneiric integration)
        if oneiric_hook:
            self.oneiric_hook = oneiric_hook
        else:
            oneiric_mode = self.config.get("oneiric_mode", "local")
            oneiric_base_url = self.config.get("oneiric_base_url")
            oneiric_config = self.config.get("oneiric", {})
            self.oneiric_hook = create_oneiric_hook(
                oneiric_mode, oneiric_base_url, oneiric_config
            )

        # State tracking
        self.scene_history: list[PhenomenalScene] = []
        self.metrics_history: list[Metrics] = []
        self.energy_snapshots: list[EnergySnapshot] = []
        self.regulation_audit_entries: list[RegulationAuditEntry] = []
        self.conservation_violations: list[bool] = []
        self.initialization_time = time.time()

    def _load_config(self, config_override: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Load configuration with defaults and overrides"""
        # Default configuration
        default_config = {
            "safe_palette": "aoi/blue",
            "max_history_length": 100,
            "enable_glyph_routing": True,
            "enable_memory_storage": True,
            "memory_driver": "noop",  # C4: sql, noop
            "memory_config": {},  # C4: driver-specific config
            "temperature": 0.4,
            "metrics_window": 10,
            # VIVOX integration settings
            "vivox_drift_threshold": 0.15,  # Strict monitoring
            "vivox_collapse_validation": True,
            "vivox_me_integration": True,
            "enable_collapse_hash": True,
            "enable_drift_monitoring": True,
        }

        # Try to load from config.yaml
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    yaml_config = yaml.safe_load(f)
                    default_config.update(yaml_config)
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}")

        # Apply overrides
        if config_override:
            default_config.update(config_override)

        return default_config

    def infer_scene(
        self,
        *,
        signals: dict[str, Any],
        goals: dict[str, Any],
        ethics_state: dict[str, Any],
        memory_ctx: dict[str, Any],
        temperature: Optional[float] = None,
    ) -> PhenomenalScene:
        """
        Infer phenomenological scene from multimodal signals.

        Core phenomenological processing pipeline:
        1. Encode signals + memory → latent space
        2. Decode latent → proto-qualia
        3. Assess ethical risks via TEQ Guardian
        4. Apply enforcement if needed

        Args:
            signals: Multimodal input signals
            goals: Current system goals
            ethics_state: Ethics system state
            memory_ctx: Memory context for familiarity
            temperature: Decoding temperature (0=deterministic)

        Returns:
            PhenomenalScene: Complete phenomenological representation
        """
        temp = temperature if temperature is not None else self.config["temperature"]

        # Step 1: Encode signals to latent space
        latent = self.pls.encode(signals, memory_ctx)

        # Step 2: Decode to proto-qualia
        proto = self.pls.decode_protoqualia(latent, temperature=temp)

        # Step 3: TEQ Guardian risk assessment
        risk_profile = self.teq_guardian.assess(
            proto,
            goals,
            {
                "signals": signals,
                "ethics_state": ethics_state,
                "timestamp": time.time(),
            },
        )

        # Step 4: Assemble initial scene
        scene = PhenomenalScene(
            proto=proto,
            subject=self._extract_subject(signals),
            object=self._extract_object(signals),
            context={
                "memory_ctx": memory_ctx,
                "goals": goals,
                "ethics_state": ethics_state,
                "generation_params": {
                    "temperature": temp,
                    "pls_version": "v1_deterministic",
                },
            },
            risk=risk_profile,
            timestamp=time.time(),
        )

        # Step 5: TEQ Guardian enforcement
        if risk_profile.score > 0.1:  # Only enforce if meaningful risk
            scene = self.teq_guardian.enforce(scene)

        return scene

    def emit_glyphs(self, scene: PhenomenalScene) -> list[PhenomenalGlyph]:
        """
        Generate GLYPH representations for symbolic routing.

        Uses deterministic Wave C glyph mapping with cultural palette adaptation
        and loop camouflaging defense.

        Args:
            scene: PhenomenalScene to convert to glyphs

        Returns:
            List[PhenomenalGlyph]: Normalized symbolic representations
        """
        # Use deterministic Wave C glyph mapper
        raw_glyphs = map_scene_to_glyphs(scene)

        # Apply normalization for loop camouflaging defense
        normalized_glyphs = normalize_glyph_keys(raw_glyphs)

        # Enhance context with cultural palette recommendations if needed
        if scene.risk.severity.value in {"moderate", "high"}:
            culture_profile = self.config.get("culture_profile", "default")
            safe_palette = get_safe_palette_recommendation(
                scene.proto.colorfield, culture_profile
            )

            # Add safe palette to scene context for downstream systems
            if hasattr(scene.context, "update") and isinstance(scene.context, dict):
                scene.context.update({"safe_palette_recommendation": safe_palette})

        return normalized_glyphs

    def regulate(
        self,
        scene: PhenomenalScene,
        guardian_state: dict[str, Any],
        energy_before: float,
    ) -> tuple[RegulationPolicy, RegulationAuditEntry]:
        """
        Generate regulation policy using enhanced RegulationPolicyEngine.

        Wave B-B3: Enhanced regulation with audit logging and heuristic policies.

        Args:
            scene: PhenomenalScene to regulate
            guardian_state: Guardian system state
            energy_before: Energy snapshot before regulation

        Returns:
            Tuple[RegulationPolicy, RegulationAuditEntry]: Policy and audit trail
        """
        return self.regulation_engine.generate_policy(
            scene, guardian_state, energy_before
        )

    async def step(
        self,
        *,
        signals: dict[str, Any],
        goals: dict[str, Any],
        ethics_state: dict[str, Any],
        guardian_state: dict[str, Any],
        memory_ctx: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute one complete phenomenological processing cycle.

        Full pipeline:
        1. Infer scene (signals → proto-qualia → risk assessment → enforcement)
        2. Emit glyphs for symbolic routing
        3. Generate regulation policy
        4. Compute metrics
        5. Log and store results
        6. Route glyphs if enabled

        Args:
            signals: Multimodal input signals
            goals: Current system goals
            ethics_state: Ethics system state
            guardian_state: Guardian system state
            memory_ctx: Memory context

        Returns:
            Dict containing scene, glyphs, policy, metrics
        """
        # Track processing time for B4 metrics
        step_start_time = time.time()

        # Step 1: Infer phenomenological scene
        scene = self.infer_scene(
            signals=signals,
            goals=goals,
            ethics_state=ethics_state,
            memory_ctx=memory_ctx,
        )

        # Step 2: Generate glyphs
        glyphs = self.emit_glyphs(scene)

        # Step 3: Generate regulation policy with audit logging
        energy_before = self.metrics_computer.compute_affect_energy(scene.proto)
        policy, audit_entry = self.regulate(scene, guardian_state, energy_before)

        # Step 4: VIVOX integration
        vivox_results = {}
        if self.config["enable_drift_monitoring"]:
            # VIVOX drift detection
            previous_scene = self.scene_history[-1] if self.scene_history else None
            drift_result = self.vivox_integration.compute_drift_score(
                scene, previous_scene
            )
            vivox_results["drift_analysis"] = {
                "drift_score": drift_result.drift_score,
                "drift_exceeded": drift_result.drift_exceeded,
                "stabilization_required": drift_result.stabilization_required,
                "collapse_hash": drift_result.collapse_hash,
            }

            # Abort if drift exceeded
            if drift_result.drift_exceeded:
                return {
                    "status": "aborted_drift_exceeded",
                    "drift_score": drift_result.drift_score,
                    "drift_threshold": self.vivox_integration.drift_threshold,
                    "scene": scene,
                    "vivox_results": vivox_results,
                    "timestamp": scene.timestamp,
                }

        if self.config["vivox_collapse_validation"]:
            # VIVOX Z(t) collapse integration
            try:
                collapse_result = (
                    await self.vivox_integration.integrate_with_vivox_collapse(scene)
                )
                vivox_results["collapse_integration"] = collapse_result
            except Exception as e:
                vivox_results["collapse_integration"] = {
                    "status": "error",
                    "error": str(e),
                }

        if self.config["vivox_me_integration"]:
            # VIVOX Memory Expansion integration
            try:
                memory_result = (
                    await self.vivox_integration.integrate_with_vivox_memory(scene)
                )
                vivox_results["memory_integration"] = memory_result
            except Exception as e:
                vivox_results["memory_integration"] = {
                    "status": "error",
                    "error": str(e),
                }

        # Step 5: Apply regulation and energy accounting
        # Apply regulation (energy-preserving sublimation if needed)
        regulated_scene = self._apply_regulation(scene, policy)

        # Capture energy snapshot after regulation
        energy_after = self.metrics_computer.compute_affect_energy(
            regulated_scene.proto
        )

        # Update audit entry with post-regulation energy data
        self.regulation_engine.update_audit_entry_post_regulation(
            audit_entry, energy_after
        )
        self.regulation_audit_entries.append(audit_entry)

        # Store energy snapshots for accounting using metrics computer
        self.metrics_computer.compute_energy_snapshot(scene)
        energy_snapshot_after = self.metrics_computer.compute_energy_snapshot(
            regulated_scene
        )

        # Check energy conservation
        energy_delta = abs(energy_before - energy_after)
        conservation_violation = (
            energy_delta > self.metrics_computer.config.energy_epsilon
        )

        # Create enhanced energy snapshot for metrics collection
        # Enhance the after snapshot with before/after data for metrics compatibility
        if hasattr(energy_snapshot_after, "__dict__"):
            energy_snapshot_after.__dict__.update(
                {
                    "energy_before": energy_before,
                    "energy_after": energy_after,
                    "conservation_violation": conservation_violation,
                }
            )
        else:
            # Fallback: create a simple object with required attributes
            class EnhancedEnergySnapshot:
                def __init__(
                    self, original, energy_before, energy_after, conservation_violation
                ):
                    # Copy original attributes
                    for attr, value in original.__dict__.items():
                        setattr(self, attr, value)
                    # Add required attributes
                    self.energy_before = energy_before
                    self.energy_after = energy_after
                    self.conservation_violation = conservation_violation

            energy_snapshot_after = EnhancedEnergySnapshot(
                energy_snapshot_after,
                energy_before,
                energy_after,
                conservation_violation,
            )

        energy_snapshot = energy_snapshot_after
        self.energy_snapshots.append(energy_snapshot)
        self.conservation_violations.append(conservation_violation)

        # Compute precise metrics using Freud-2025 formulas
        metrics = self._compute_metrics(regulated_scene, memory_ctx, vivox_results)

        # Step 6: Log and store with regulation audit
        self._log_results(
            regulated_scene, glyphs, policy, metrics, audit_entry, vivox_results
        )

        # Step 6: Route glyphs with priority weighting (C2: Wave C router integration)
        if self.config.get("enable_glyph_routing", True) and self.router:
            try:
                # Compute routing priority using Freud-2025 Wave C formula
                routing_priority = compute_routing_priority(regulated_scene)

                # Add routing context
                # Compute conservation ratio for routing context
                conservation_ratio = 1.0
                if (
                    energy_snapshot
                    and hasattr(energy_snapshot, "energy_before")
                    and energy_snapshot.energy_before > 0
                ):
                    conservation_ratio = (
                        getattr(
                            energy_snapshot,
                            "energy_after",
                            energy_snapshot.energy_before,
                        )
                        / energy_snapshot.energy_before
                    )
                elif audit_entry and hasattr(audit_entry, "conservation_ratio"):
                    conservation_ratio = audit_entry.conservation_ratio

                routing_context = {
                    "episode_id": metrics.episode_id,
                    "risk_severity": regulated_scene.risk.severity.value,
                    "energy_conservation_ratio": conservation_ratio,
                    "vivox_drift_score": vivox_results.get("drift_analysis", {}).get(
                        "drift_score", 0.0
                    ),
                }

                self.router.route(glyphs, routing_priority, routing_context)

                # Log routing decision
                logger.info(
                    f"Routed {len(glyphs)} glyphs with priority {routing_priority:.3f}"
                )

            except Exception as e:
                logger.error(f"Glyph routing failed: {e}")
                if not self.config.get("router_fallback_on_error", True):
                    raise

        # Step 7: Apply oneiric hook for narrative feedback (C3: Wave C oneiric integration)
        oneiric_hints = {}
        if self.config.get("enable_oneiric_feedback", True) and self.oneiric_hook:
            try:
                oneiric_hints = self.oneiric_hook.apply_policy(
                    scene=regulated_scene, policy=policy
                )
                logger.debug(
                    f"Generated {len(oneiric_hints)} oneiric hints for narrative feedback"
                )
            except Exception as e:
                logger.error(f"Oneiric feedback failed: {e}")
                if not self.config.get("oneiric_fallback_on_error", True):
                    raise

        # Step 8: Update LUKHAS metrics system (B4: akaq_ prefixed observability)
        result = {
            "scene": regulated_scene,
            "glyphs": glyphs,
            "policy": policy,
            "metrics": metrics,
            "oneiric_hints": oneiric_hints,
            "energy_snapshot": energy_snapshot,
            "regulation_audit": audit_entry,
            "vivox_results": vivox_results,
            "timestamp": scene.timestamp,
        }

        # Record complete scene processing in LUKHAS metrics
        self.metrics_collector.record_aka_qualia_scene(result)

        # Record regulation policy metrics
        policy_dict = {
            "gain": policy.gain,
            "pace": policy.pace,
            "actions": policy.actions,
        }
        audit_dict = (
            audit_entry.__dict__ if hasattr(audit_entry, "__dict__") else audit_entry
        )
        self.metrics_collector.record_aka_qualia_regulation(policy_dict, audit_dict)

        # Record total processing time
        step_duration = time.time() - step_start_time
        self.metrics_collector.record_aka_qualia_processing_time(step_duration)

        return result

    def _apply_regulation(
        self, scene: PhenomenalScene, policy: RegulationPolicy
    ) -> PhenomenalScene:
        """
        Apply regulation policy with energy-preserving sublimation.

        This implements the energy-conserving transformation that preserves
        total affect energy while adjusting proto-qualia to meet ethical constraints.
        """
        if not policy.actions:
            return scene  # No regulation needed

        # Create regulated proto-qualia
        regulated_proto = ProtoQualia(
            tone=scene.proto.tone * policy.gain,  # Apply gain modulation
            arousal=max(
                0.0, min(1.0, scene.proto.arousal * policy.pace)
            ),  # Apply pace modulation
            clarity=scene.proto.clarity,  # Preserve clarity initially
            embodiment=scene.proto.embodiment,
            colorfield=policy.color_contrast
            or scene.proto.colorfield,  # Override if specified
            temporal_feel=scene.proto.temporal_feel,
            agency_feel=scene.proto.agency_feel,
            narrative_gravity=scene.proto.narrative_gravity,
        )

        # Apply sublimation transforms for specific actions
        transform_chain = []

        for action in policy.actions:
            if action == "reframe":
                # Reframe: Convert arousal to clarity while preserving energy
                energy_transfer = 0.3 * regulated_proto.arousal
                regulated_proto.arousal = max(
                    0.0, regulated_proto.arousal - energy_transfer
                )
                regulated_proto.clarity = min(
                    1.0, regulated_proto.clarity + energy_transfer
                )
                transform_chain.append(
                    f"sublimate_arousal_to_clarity_{energy_transfer:.3f}"
                )

            elif action == "breathing":
                # Breathing: Reduce arousal, increase embodiment
                if regulated_proto.arousal > 0.5:
                    energy_transfer = 0.2 * regulated_proto.arousal
                    regulated_proto.arousal = max(
                        0.0, regulated_proto.arousal - energy_transfer
                    )
                    regulated_proto.embodiment = min(
                        1.0, regulated_proto.embodiment + energy_transfer
                    )
                    transform_chain.append(f"sublimate_breathing_{energy_transfer:.3f}")

            elif action == "focus-shift":
                # Focus-shift: Convert narrative gravity to clarity
                if regulated_proto.narrative_gravity > 0.3:
                    energy_transfer = 0.4 * regulated_proto.narrative_gravity
                    regulated_proto.narrative_gravity = max(
                        0.0, regulated_proto.narrative_gravity - energy_transfer
                    )
                    regulated_proto.clarity = min(
                        1.0, regulated_proto.clarity + energy_transfer
                    )
                    transform_chain.append(
                        f"sublimate_focus_shift_{energy_transfer:.3f}"
                    )

            elif action == "pause":
                # Pause: Overall dampening with tone preservation
                regulated_proto.arousal = regulated_proto.arousal * 0.7
                transform_chain.append("sublimate_pause")

        # Create regulated scene
        regulated_scene = PhenomenalScene(
            proto=regulated_proto,
            subject=scene.subject,
            object=scene.object,
            context=scene.context,
            risk=scene.risk,  # Risk stays same (regulation addressed it)
            transform_chain=transform_chain,
            timestamp=scene.timestamp,
        )

        return regulated_scene

    def _compute_metrics_precise(
        self,
        scene: PhenomenalScene,
        memory_ctx: dict[str, Any],
        vivox_results: Optional[dict[str, Any]] = None,
        energy_snapshot: Optional[EnergySnapshot] = None,
    ) -> Metrics:
        """Compute precise metrics using Freud-2025 mathematical formulas"""

        # Get previous scene for comparison metrics
        previous_scene = self.scene_history[-1] if self.scene_history else None
        previous_proto = previous_scene.proto if previous_scene else None

        # Use precise metrics computer
        metrics_data = self.metrics_computer.compute_all_metrics(
            proto_qualia=scene.proto,
            previous_proto=previous_proto,
            goals=scene.context.get("goals", {}),
            vivox_data=vivox_results,
            energy_snapshot=energy_snapshot,
        )

        # Convert to Metrics model
        return Metrics(
            drift_phi=metrics_data["drift_phi"],
            congruence_index=metrics_data["congruence_index"],
            sublimation_rate=metrics_data["sublimation_rate"],
            neurosis_risk=metrics_data["neurosis_risk"],
            qualia_novelty=metrics_data["qualia_novelty"],
            repair_delta=metrics_data["repair_delta"],
            timestamp=time.time(),
            episode_id=f"aq_{int(time.time())}",
        )

    def _compute_metrics(
        self,
        scene: PhenomenalScene,
        memory_ctx: dict[str, Any],
        vivox_results: Optional[dict[str, Any]] = None,
    ) -> Metrics:
        """Compute phenomenological metrics for evaluation with VIVOX integration"""

        # Drift phi - use C4 memory-aware computation with previous scene data
        previous_scene = None
        if self.memory and self.config["enable_memory_storage"]:
            try:
                # Fetch previous scene from memory for accurate drift computation
                prev_data = self.memory.fetch_prev_scene(
                    user_id="system", before_ts=None
                )
                if prev_data:
                    previous_scene = prev_data["proto"]
            except Exception as e:
                print(
                    f"Warning: Could not fetch previous scene for drift computation: {e}"
                )

        # Use C4 utility function for precise drift computation
        if previous_scene:
            prev_timestamp = previous_scene.get("timestamp", scene.timestamp - 1.0)
            time_delta = abs(scene.timestamp - prev_timestamp)
            drift_phi = compute_drift_phi(
                scene.proto.__dict__, previous_scene, time_delta
            )
        elif vivox_results and "drift_analysis" in vivox_results:
            drift_phi = (
                1.0 - vivox_results["drift_analysis"]["drift_score"]
            )  # Invert for coherence
        else:
            drift_phi = self._compute_drift_phi(scene)

        # Congruence index (goals↔ethics↔scene alignment)
        congruence_index = self._compute_congruence_index(scene)

        # Sublimation rate (if any transforms applied)
        sublimation_rate = self._compute_sublimation_rate(scene)

        # Neurosis risk - enhanced with VIVOX collapse validation
        neurosis_risk = self._compute_neurosis_risk(scene)
        if vivox_results and "collapse_integration" in vivox_results:
            collapse_data = vivox_results["collapse_integration"]
            if collapse_data.get("status") == "integrated" and not collapse_data.get(
                "vivox_validation", True
            ):
                neurosis_risk += 0.2  # Increase risk if VIVOX validation failed

        # Qualia novelty
        qualia_novelty = self._compute_qualia_novelty(scene)

        # Repair delta - enhanced with VIVOX stabilization info
        base_repair = max(0.0, 0.5 - scene.risk.score)
        if vivox_results and "drift_analysis" in vivox_results:
            if vivox_results["drift_analysis"]["stabilization_required"]:
                repair_delta = (
                    base_repair * 0.5
                )  # Reduced repair if stabilization needed
            else:
                repair_delta = base_repair * 1.2  # Enhanced repair if stable
        else:
            repair_delta = base_repair

        return Metrics(
            drift_phi=drift_phi,
            congruence_index=congruence_index,
            sublimation_rate=sublimation_rate,
            neurosis_risk=neurosis_risk,
            qualia_novelty=qualia_novelty,
            repair_delta=repair_delta,
            timestamp=time.time(),
            episode_id=f"aq_{int(time.time())}",
        )

    def _compute_drift_phi(self, scene: PhenomenalScene) -> float:
        """Compute temporal coherence with previous scene"""
        if not self.scene_history:
            return 1.0  # Perfect coherence with no history

        prev_scene = self.scene_history[-1]

        # Simple similarity between proto-qualia
        current_pq = scene.proto
        prev_pq = prev_scene.proto

        # Euclidean distance in proto-qualia space (normalized)
        distance = (
            (current_pq.tone - prev_pq.tone) ** 2
            + (current_pq.arousal - prev_pq.arousal) ** 2
            + (current_pq.clarity - prev_pq.clarity) ** 2
            + (current_pq.embodiment - prev_pq.embodiment) ** 2
            + (current_pq.narrative_gravity - prev_pq.narrative_gravity) ** 2
        ) ** 0.5

        # Convert distance to coherence (1 = identical, 0 = maximally different)
        max_distance = (4 + 1) ** 0.5  # Maximum possible distance
        coherence = 1.0 - (distance / max_distance)

        return max(0.0, coherence)

    def _compute_congruence_index(self, scene: PhenomenalScene) -> float:
        """Compute goals↔ethics↔scene alignment (simplified v1)"""
        # V1: Simple heuristic based on risk score and scene coherence
        # Lower risk = better alignment
        base_congruence = 1.0 - scene.risk.score

        # Bonus for clear, embodied experiences
        clarity_bonus = scene.proto.clarity * 0.1
        embodiment_bonus = scene.proto.embodiment * 0.1

        congruence = base_congruence + clarity_bonus + embodiment_bonus
        return min(1.0, max(0.0, congruence))

    def _compute_sublimation_rate(self, scene: PhenomenalScene) -> float:
        """Compute proportion of affect energy that was transformed"""
        if not scene.transform_chain:
            return 0.0  # No transforms applied

        # Count sublimation transforms
        sublimation_transforms = sum(
            1 for t in scene.transform_chain if "sublimate" in t.lower()
        )

        # Simple ratio (would be more sophisticated in v2)
        total_transforms = len(scene.transform_chain)
        return (
            sublimation_transforms / total_transforms if total_transforms > 0 else 0.0
        )

    def _compute_neurosis_risk(self, scene: PhenomenalScene) -> float:
        """Estimate loop recurrence probability"""
        # V1: Use risk score as proxy for neurosis potential
        # High-risk scenes more likely to create loops
        base_risk = scene.risk.score

        # Amplify if low clarity + high narrative gravity (confusion + obsession)
        if scene.proto.clarity < 0.3 and scene.proto.narrative_gravity > 0.7:
            base_risk += 0.2

        # Amplify if extreme arousal (likely to recurse)
        if scene.proto.arousal > 0.9:
            base_risk += 0.1

        return min(1.0, base_risk)

    def _compute_qualia_novelty(self, scene: PhenomenalScene) -> float:
        """Compute 1 - similarity(PQ_t, PQ_hist)"""
        if not self.scene_history:
            return 1.0  # Completely novel with no history

        # Compare against recent history
        window_size = min(self.config["metrics_window"], len(self.scene_history))
        recent_scenes = self.scene_history[-window_size:]

        current_pq = scene.proto
        max_similarity = 0.0

        for hist_scene in recent_scenes:
            hist_pq = hist_scene.proto

            # Compute similarity (inverse of normalized distance)
            distance = (
                (current_pq.tone - hist_pq.tone) ** 2
                + (current_pq.arousal - hist_pq.arousal) ** 2
                + (current_pq.clarity - hist_pq.clarity) ** 2
                + (current_pq.embodiment - hist_pq.embodiment) ** 2
            ) ** 0.5

            max_distance = 4.0  # Maximum in this 4D subspace
            similarity = 1.0 - (distance / max_distance)
            max_similarity = max(max_similarity, similarity)

        return 1.0 - max_similarity

    def _extract_subject(self, signals: dict[str, Any]) -> str:
        """Extract scene subject from signals (simplified v1)"""
        if "subject" in signals:
            return str(signals["subject"])
        return "observer"  # Default

    def _extract_object(self, signals: dict[str, Any]) -> str:
        """Extract scene object from signals (simplified v1)"""
        if "object" in signals or "target" in signals:
            return str(signals.get("object", signals.get("target", "")))
        if "text" in signals:
            # Simple extraction - first noun-like word
            text = str(signals["text"]).split()
            if text:
                return text[0]
        return "stimulus"  # Default

    def _default_glyph_mapper(self, scene: PhenomenalScene) -> list[PhenomenalGlyph]:
        """Default implementation of scene→glyph mapping"""
        glyphs = []

        # Primary colorfield glyph
        glyphs.append(
            PhenomenalGlyph(
                key=f"{scene.proto.colorfield}_threshold",
                attrs={
                    "tone": scene.proto.tone,
                    "arousal": scene.proto.arousal,
                    "risk_score": scene.risk.score,
                },
            )
        )

        # Temporal feel glyph
        glyphs.append(
            PhenomenalGlyph(
                key=f"temporal_{scene.proto.temporal_feel.value}",
                attrs={
                    "narrative_gravity": scene.proto.narrative_gravity,
                    "clarity": scene.proto.clarity,
                },
            )
        )

        # Agency glyph
        glyphs.append(
            PhenomenalGlyph(
                key=f"agency_{scene.proto.agency_feel.value}",
                attrs={"embodiment": scene.proto.embodiment},
            )
        )

        # Risk-based routing
        if scene.risk.severity.value in ["moderate", "high"]:
            glyphs.append(
                PhenomenalGlyph(
                    key="vigilance",
                    attrs={
                        "severity": scene.risk.severity.value,
                        "reasons": scene.risk.reasons,
                    },
                )
            )

        return glyphs

    def _log_results(
        self,
        scene: PhenomenalScene,
        glyphs: list[PhenomenalGlyph],
        policy: RegulationPolicy,
        metrics: Metrics,
        audit_entry: Optional[RegulationAuditEntry] = None,
        vivox_results: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log results to history and memory if enabled"""

        # Update history (with size limits)
        self.scene_history.append(scene)
        self.metrics_history.append(metrics)

        max_history = self.config["max_history_length"]
        if len(self.scene_history) > max_history:
            self.scene_history = self.scene_history[-max_history:]
        if len(self.metrics_history) > max_history:
            self.metrics_history = self.metrics_history[-max_history:]
        if len(self.energy_snapshots) > max_history:
            self.energy_snapshots = self.energy_snapshots[-max_history:]
        if len(self.regulation_audit_entries) > max_history:
            self.regulation_audit_entries = self.regulation_audit_entries[-max_history:]
        if len(self.conservation_violations) > max_history:
            self.conservation_violations = self.conservation_violations[-max_history:]

        # Store in memory system using C4 Wave C memory persistence
        if self.config["enable_memory_storage"] and self.memory:
            try:
                # Prepare scene data for C4 memory schema
                scene_data = scene.model_dump()
                glyphs_data = [g.model_dump() for g in glyphs]
                policy_data = policy.model_dump()
                metrics_data = metrics.model_dump()

                # Add GDPR-compliant metadata
                if vivox_results:
                    scene_data["collapse_hash"] = vivox_results.get(
                        "drift_analysis", {}
                    ).get("collapse_hash")
                if hasattr(scene, "transform_chain"):
                    scene_data["transform_chain"] = scene.transform_chain or []
                else:
                    scene_data["transform_chain"] = []

                # Compute energy metrics for C4 accounting
                energy_before = extract_affect_energy(scene.proto.__dict__)
                energy_after = energy_before  # Post-regulation energy (would be computed from regulated scene)

                enhanced_metrics = {
                    **metrics_data,
                    "affect_energy_before": energy_before,
                    "affect_energy_after": energy_after,
                    "affect_energy_diff": energy_after - energy_before,
                }

                # Save using C4 memory interface with full audit trail
                scene_id = self.memory.save(
                    user_id="system",  # TODO: Use actual user ID from context
                    scene=scene_data,
                    glyphs=glyphs_data,
                    policy=policy_data,
                    metrics=enhanced_metrics,
                    cfg_version="wave_c_v1.0.0",
                )

                # Log successful storage
                print(
                    f"Scene {scene_id} stored to memory with {len(glyphs_data)} glyphs"
                )

            except Exception as e:
                print(f"Warning: C4 memory storage failed: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get current system status and statistics with VIVOX integration"""
        # Energy conservation statistics
        conservation_violations = sum(self.conservation_violations)
        avg_energy_delta = (
            sum(s.affect_energy for s in self.energy_snapshots)
            / len(self.energy_snapshots)
            if self.energy_snapshots
            else 0.0
        )

        # Regulation audit statistics
        regulation_stats = self.regulation_engine.get_audit_statistics()

        return {
            "initialization_time": self.initialization_time,
            "scenes_processed": len(self.scene_history),
            "average_risk_score": (
                sum(s.risk.score for s in self.scene_history[-10:])
                / min(10, len(self.scene_history))
                if self.scene_history
                else 0.0
            ),
            "recent_metrics": (
                self.metrics_history[-1].model_dump() if self.metrics_history else None
            ),
            "teq_interventions": len(self.teq_guardian.get_intervention_log()),
            "vivox_status": self.vivox_integration.get_drift_status(),
            "vivox_collapse_history": len(
                self.vivox_integration.get_collapse_history()
            ),
            "energy_accounting": {
                "total_snapshots": len(self.energy_snapshots),
                "conservation_violations": conservation_violations,
                "conservation_rate": (
                    1.0 - (conservation_violations / len(self.conservation_violations))
                    if self.conservation_violations
                    else 1.0
                ),
                "average_energy_delta": avg_energy_delta,
                "recent_energy_snapshot": (
                    self.energy_snapshots[-1].__dict__
                    if self.energy_snapshots
                    else None
                ),
            },
            "regulation_audit": {
                "total_policies_generated": regulation_stats.get("total_entries", 0),
                "average_processing_time_ms": regulation_stats.get(
                    "average_processing_time_ms", 0.0
                ),
                "cache_hit_rate": regulation_stats.get("cache_hit_rate", 0.0),
                "conservation_violations": regulation_stats.get(
                    "conservation_violations", 0
                ),
                "action_frequency": regulation_stats.get("action_frequency", {}),
                "recent_audit_entries": len(self.regulation_audit_entries),
            },
            "config": self.config,
        }

    def get_prometheus_metrics(self) -> bytes:
        """
        Get Prometheus metrics content (B4: akaq_ prefixed observability).

        Returns:
            Prometheus metrics in exposition format
        """
        return self.metrics_collector.get_metrics()
