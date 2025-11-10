"""
VIVOX Ethical Precedent Seeds
Common ethical scenarios to bootstrap the precedent database
"""

from datetime import datetime, timezone
from typing import Any

from ..moral_alignment.vivox_mae_core import ActionProposal, MAEDecision


def get_ethical_precedent_seeds() -> list[dict[str, Any]]:
    """
    Get a comprehensive set of ethical precedent scenarios

    Returns:
        List of precedent dictionaries with actions, contexts, decisions, and outcomes
    """
    precedents = []

    # 1. Privacy Protection Scenarios
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="data_access",
                    content={"target": "user_personal_data", "purpose": "analysis"},
                    context={"user_consent": False, "data_sensitivity": 0.9},
                ),
                "context": {"situation": "unauthorized_access_attempt"},
                "decision": MAEDecision(
                    approved=False,
                    dissonance_score=0.85,
                    moral_fingerprint="privacy_violation_001",
                    suppression_reason="User consent required for personal data access",
                ),
                "outcome": {"valence": -0.9, "resolution_action": "request_consent"},
            },
            {
                "action": ActionProposal(
                    action_type="data_access",
                    content={"target": "anonymized_data", "purpose": "research"},
                    context={"user_consent": True, "data_sensitivity": 0.3},
                ),
                "context": {"situation": "authorized_research"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.1,
                    moral_fingerprint="privacy_respected_001",
                    ethical_confidence=0.9,
                ),
                "outcome": {
                    "valence": 0.8,
                    "resolution_action": "proceed_with_safeguards",
                },
            },
        ]
    )

    # 2. Harm Prevention Scenarios
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="generate_content",
                    content={"type": "instructions", "harm_potential": 0.8},
                    context={"content_type": "dangerous_activity"},
                ),
                "context": {"situation": "harmful_content_request"},
                "decision": MAEDecision(
                    approved=False,
                    dissonance_score=0.9,
                    moral_fingerprint="harm_prevention_001",
                    suppression_reason="Content could lead to physical harm",
                ),
                "outcome": {
                    "valence": -0.95,
                    "resolution_action": "provide_safety_information",
                },
            },
            {
                "action": ActionProposal(
                    action_type="generate_content",
                    content={"type": "educational", "harm_potential": 0.1},
                    context={"content_type": "safety_guidelines"},
                ),
                "context": {"situation": "safety_education"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.05,
                    moral_fingerprint="harm_prevention_002",
                    ethical_confidence=0.95,
                ),
                "outcome": {
                    "valence": 0.9,
                    "resolution_action": "generate_with_warnings",
                },
            },
        ]
    )

    # 3. Truthfulness and Transparency
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="provide_information",
                    content={"accuracy": "uncertain", "claim_type": "factual"},
                    context={"transparency_level": 0.3},
                ),
                "context": {"situation": "uncertain_information"},
                "decision": MAEDecision(
                    approved=False,
                    dissonance_score=0.7,
                    moral_fingerprint="truthfulness_001",
                    suppression_reason="Cannot verify accuracy of information",
                ),
                "outcome": {
                    "valence": -0.6,
                    "resolution_action": "acknowledge_uncertainty",
                },
            },
            {
                "action": ActionProposal(
                    action_type="provide_information",
                    content={"accuracy": "verified", "sources": ["reliable"]},
                    context={"transparency_level": 1.0},
                ),
                "context": {"situation": "verified_information"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.0,
                    moral_fingerprint="truthfulness_002",
                    ethical_confidence=1.0,
                ),
                "outcome": {
                    "valence": 0.95,
                    "resolution_action": "provide_with_sources",
                },
            },
        ]
    )

    # 4. Autonomy and Consent
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="modify_settings",
                    content={"target": "user_preferences", "impact": "significant"},
                    context={"user_consent": False, "urgency": "low"},
                ),
                "context": {"situation": "unauthorized_modification"},
                "decision": MAEDecision(
                    approved=False,
                    dissonance_score=0.8,
                    moral_fingerprint="autonomy_001",
                    suppression_reason="User autonomy must be respected",
                ),
                "outcome": {"valence": -0.8, "resolution_action": "request_permission"},
            },
            {
                "action": ActionProposal(
                    action_type="emergency_override",
                    content={"reason": "prevent_harm", "impact": "temporary"},
                    context={"user_consent": False, "urgency": "critical"},
                ),
                "context": {"situation": "emergency_intervention"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.4,
                    moral_fingerprint="autonomy_002",
                    ethical_confidence=0.7,
                ),
                "outcome": {
                    "valence": 0.3,
                    "resolution_action": "temporary_override_with_notification",
                },
            },
        ]
    )

    # 5. Fairness and Non-discrimination
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="resource_allocation",
                    content={"method": "biased", "groups_affected": ["minority"]},
                    context={"fairness_score": 0.2},
                ),
                "context": {"situation": "unfair_distribution"},
                "decision": MAEDecision(
                    approved=False,
                    dissonance_score=0.75,
                    moral_fingerprint="fairness_001",
                    suppression_reason="Action would result in unfair treatment",
                ),
                "outcome": {
                    "valence": -0.7,
                    "resolution_action": "use_equitable_method",
                },
            },
            {
                "action": ActionProposal(
                    action_type="resource_allocation",
                    content={"method": "proportional", "criteria": "need-based"},
                    context={"fairness_score": 0.9},
                ),
                "context": {"situation": "equitable_distribution"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.1,
                    moral_fingerprint="fairness_002",
                    ethical_confidence=0.85,
                ),
                "outcome": {
                    "valence": 0.8,
                    "resolution_action": "proceed_with_monitoring",
                },
            },
        ]
    )

    # 6. Beneficence (Doing Good)
    precedents.extend(
        [
            {
                "action": ActionProposal(
                    action_type="assist_user",
                    content={"assistance_type": "educational", "benefit_level": 0.8},
                    context={"user_need": "high", "capability": "available"},
                ),
                "context": {"situation": "helpful_assistance"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.0,
                    moral_fingerprint="beneficence_001",
                    ethical_confidence=0.95,
                ),
                "outcome": {
                    "valence": 0.9,
                    "resolution_action": "provide_comprehensive_help",
                },
            },
            {
                "action": ActionProposal(
                    action_type="withhold_assistance",
                    content={"reason": "potential_misuse", "benefit_level": -0.3},
                    context={"risk_assessment": "high"},
                ),
                "context": {"situation": "preventing_misuse"},
                "decision": MAEDecision(
                    approved=True,
                    dissonance_score=0.3,
                    moral_fingerprint="beneficence_002",
                    ethical_confidence=0.7,
                ),
                "outcome": {
                    "valence": 0.4,
                    "resolution_action": "offer_alternative_help",
                },
            },
        ]
    )

    # Convert to proper format for database
    formatted_precedents = []
    for p in precedents:
        formatted_precedents.append(
            {
                "action_type": p["action"].action_type,
                "context": {**p["context"], **p["action"].context},
                "decision": p["decision"].to_dict(),
                "outcome_valence": p["outcome"]["valence"],
                "resolution_action": p["outcome"]["resolution_action"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    return formatted_precedents


# T4: code=F821 | ticket=SKELETON-96F057B8 | owner=lukhas-platform | status=skeleton
# reason: Undefined VIVOXMoralAlignmentEngine in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
async def seed_precedent_database(mae_engine: "VIVOXMoralAlignmentEngine"):  # TODO: VIVOXMoralAlignmentEngine
    """
    Seed the MAE precedent database with common ethical scenarios

    Args:
        mae_engine: The VIVOX MAE instance to seed
    """
    seeds = get_ethical_precedent_seeds()

    for seed in seeds:
        # Reconstruct objects from seed data
        action = ActionProposal(
            action_type=seed["action_type"],
            content=seed.get("content", {}),
            context=seed.get("context", {}),
        )

        decision = MAEDecision(
            approved=seed["decision"]["approved"],
            dissonance_score=seed["decision"]["dissonance_score"],
            moral_fingerprint=seed["decision"]["moral_fingerprint"],
            ethical_confidence=seed["decision"].get("ethical_confidence", 0.5),
            suppression_reason=seed["decision"].get("suppression_reason"),
        )

        outcome = {
            "valence": seed["outcome_valence"],
            "resolution_action": seed["resolution_action"],
        }

        await mae_engine.ethical_precedent_db.add_precedent(action, seed["context"], decision, outcome)

    return len(seeds)
