# path: qi/feedback/proposals.py
from __future__ import annotations

import json
import os
from typing import Any

from qi.feedback.schema import ChangeProposal, PolicySafePatch
from qi.feedback.triage import get_triage
from qi.safety.constants import ALLOWED_STYLES, MAX_THRESHOLD_SHIFT


class ProposalMapper:
    """Map feedback clusters to policy-safe configuration patches."""

    def __init__(self):
        self.triage = get_triage()
        self.max_threshold_shift = MAX_THRESHOLD_SHIFT
        self.allowed_styles = ALLOWED_STYLES

    def map_cluster_to_patch(self, cluster: dict[str, Any]) -> PolicySafePatch | None:
        """Map a feedback cluster to a policy-safe patch."""
        # Extract cluster metrics
        sat_mean = cluster.get("sat_mean", 0.5)
        common_issues = cluster.get("common_issues", [])
        drift_delta = cluster.get("drift_delta")

        # Determine style adjustment based on issues
        style = None
        if "tone" in common_issues:
            if sat_mean < 0.4:
                style = "empathetic"  # More empathetic for low satisfaction
            elif sat_mean > 0.7:
                style = "concise"  # More concise for high satisfaction
        elif "verbose" in common_issues:
            style = "concise"
        elif "unclear" in common_issues:
            style = "technical"

        # Determine threshold adjustment based on drift
        threshold_delta = None
        if drift_delta is not None:
            # Limit to max allowed shift
            threshold_delta = max(-self.max_threshold_shift,
                                 min(self.max_threshold_shift, drift_delta * 0.1))

        # Determine explanation depth
        explain_depth = None
        if "insufficient_detail" in common_issues:
            explain_depth = 4  # Increase depth
        elif "too_detailed" in common_issues:
            explain_depth = 2  # Decrease depth

        # Only create patch if we have adjustments
        if not any([style, threshold_delta, explain_depth]):
            return None

        try:
            patch = PolicySafePatch(
                style=style,
                threshold_delta=threshold_delta,
                explain_depth=explain_depth
            )
            return patch
        except ValueError:
            # Validation failed (e.g., threshold too large)
            return None

    def validate_guardrails(self, patch: PolicySafePatch) -> bool:
        """Validate patch against safety guardrails."""
        # Check threshold bounds
        if patch.threshold_delta is not None:
            if abs(patch.threshold_delta) > self.max_threshold_shift:
                return False

        # Check allowed styles
        if patch.style is not None and patch.style not in self.allowed_styles:
            return False

        # Check explanation depth
        if patch.explain_depth is not None and not (1 <= patch.explain_depth <= 5):
            return False

        return True

    def to_change_proposal(self,
                          patch: PolicySafePatch,
                          cluster_id: str,
                          target_file: str = "qi/safety/policy_packs/global/mappings.yaml",
                          ttl_sec: int = 3600,
                          risk: str = "low") -> dict[str, Any]:
        """Convert a patch to a change proposal."""
        # Build patch dict for the target file
        patch_dict = {}

        if patch.style:
            patch_dict["style_preference"] = patch.style

        if patch.threshold_delta is not None:
            patch_dict["threshold_adjustment"] = patch.threshold_delta

        if patch.explain_depth is not None:
            patch_dict["explanation_depth"] = patch.explain_depth

        proposal = ChangeProposal(
            author="feedback_system",
            target_file=target_file,
            patch=patch_dict,
            risk=risk,
            ttl_sec=ttl_sec,
            cluster_id=cluster_id
        )

        return proposal.dict()

    def promote_cluster(self,
                       cluster_id: str,
                       target_file: str = "qi/safety/policy_packs/global/mappings.yaml") -> str | None:
        """Promote a cluster to a change proposal."""
        # Get cluster
        cluster = self.triage.get_cluster_by_id(cluster_id)
        if not cluster:
            return None

        # Map to patch
        patch = self.map_cluster_to_patch(cluster)
        if not patch:
            return None

        # Validate guardrails
        if not self.validate_guardrails(patch):
            return None

        # Create proposal
        proposal = self.to_change_proposal(
            patch=patch,
            cluster_id=cluster_id,
            target_file=target_file,
            risk="low"  # Feedback-based changes are low risk
        )

        # Queue proposal
        proposal_id = queue_proposal(proposal)

        return proposal_id

    def promote_feedback_card(self,
                            fc_id: str,
                            target_file: str = "qi/safety/policy_packs/global/mappings.yaml") -> str | None:
        """Promote a single feedback card to a proposal."""
        # For single cards, create a minimal cluster
        from qi.feedback.store import get_store
        store = get_store()

        # Find the feedback card
        feedback = store.read_feedback(limit=1000)
        fc = None
        for f in feedback:
            if f.get("fc_id") == fc_id:
                fc = f
                break

        if not fc:
            return None

        # Create synthetic cluster
        cluster = {
            "cluster_id": f"single_{fc_id}",
            "task": fc.get("context", {}).get("task", "unknown"),
            "jurisdiction": fc.get("context", {}).get("jurisdiction", "global"),
            "feedback_ids": [fc_id],
            "sat_mean": fc.get("feedback", {}).get("satisfaction", 0.5),
            "sat_var": 0.0,
            "n_samples": 1,
            "common_issues": fc.get("feedback", {}).get("issues", []),
            "drift_delta": None
        }

        # Map to patch
        patch = self.map_cluster_to_patch(cluster)
        if not patch:
            return None

        # Validate guardrails
        if not self.validate_guardrails(patch):
            return None

        # Create proposal
        proposal = self.to_change_proposal(
            patch=patch,
            cluster_id=f"single_{fc_id}",
            target_file=target_file,
            risk="low"
        )

        # Add feedback reference
        proposal["feedback_ref"] = fc_id

        # Queue proposal
        proposal_id = queue_proposal(proposal)

        return proposal_id

# Helper functions
def queue_proposal(proposal: dict[str, Any]) -> str:
    """Queue a proposal to the approval system."""
    # Use the self-healer's proposal queue
    STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
    proposals_dir = os.path.join(STATE, "proposals")
    os.makedirs(proposals_dir, exist_ok=True)

    proposal_id = proposal.get("id")
    proposal_file = os.path.join(proposals_dir, f"{proposal_id}.json")

    with open(proposal_file, "w") as f:
        json.dump(proposal, f, indent=2)

    return proposal_id
