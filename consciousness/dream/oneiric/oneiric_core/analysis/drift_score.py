# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: drift_score.py
# MODULE: oneiric_core.analysis
# DESCRIPTION: Symbolic drift analysis for Oneiric Core, calculating and tracking
#              user's symbolic state evolution through dream metrics. Provides
#              drift scoring, profile updates, and trend analysis capabilities.
# DEPENDENCIES: json, typing, user_repository
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import json
from typing import Dict, Optional
from ..db.user_repository import get_user_profile, update_drift_profile

async def calculate_drift_score(user_id: str, dream_metrics: dict) -> dict:
    """
    Calculate drift score based on dream metrics and user history

    Args:
        user_id: User identifier
        dream_metrics: Current dream analysis metrics

    Returns:
        Dictionary with drift analysis results
    """
    # Get user's existing profile
    current_profile = await get_user_profile(user_id)

    # Extract key metrics from dream
    symbolic_entropy = dream_metrics.get('symbolic_entropy', 0.0)
    emotional_charge = dream_metrics.get('emotional_charge', 0.0)
    narrative_coherence = dream_metrics.get('narrative_coherence', 1.0)

    # Calculate drift from baseline
    baseline_entropy = current_profile.get('avg_entropy', 0.5)
    baseline_emotional = current_profile.get('avg_emotional', 0.0)
    baseline_coherence = current_profile.get('avg_coherence', 0.8)

    # Compute drift deltas
    entropy_drift = symbolic_entropy - baseline_entropy
    emotional_drift = emotional_charge - baseline_emotional
    coherence_drift = narrative_coherence - baseline_coherence

    # Overall drift score (weighted combination)
    drift_score = (
        0.4 * abs(entropy_drift) +
        0.3 * abs(emotional_drift) +
        0.3 * abs(coherence_drift)
    )

    # Drift analysis result
    drift_result = {
        'drift_score': round(drift_score, 3),
        'entropy_drift': round(entropy_drift, 3),
        'emotional_drift': round(emotional_drift, 3),
        'coherence_drift': round(coherence_drift, 3),
        'timestamp': dream_metrics.get('timestamp'),
        'is_significant': drift_score > 0.2  # Threshold for significant drift
    }

    return drift_result

async def update_user_drift_profile(user_id: str, dream_metrics: dict) -> dict:
    """
    Update user's drift profile with new dream data

    Args:
        user_id: User identifier
        dream_metrics: Current dream analysis metrics

    Returns:
        Updated drift profile
    """
    # Get current profile
    current_profile = await get_user_profile(user_id)

    # Initialize if empty
    if not current_profile:
        current_profile = {
            'total_dreams': 0,
            'avg_entropy': 0.5,
            'avg_emotional': 0.0,
            'avg_coherence': 0.8,
            'drift_history': []
        }

    # Calculate drift
    drift_result = await calculate_drift_score(user_id, dream_metrics)

    # Update running averages
    total_dreams = current_profile.get('total_dreams', 0)
    new_total = total_dreams + 1

    # Running average updates
    current_profile['avg_entropy'] = (
        (current_profile['avg_entropy'] * total_dreams +
         dream_metrics.get('symbolic_entropy', 0.5)) / new_total
    )

    current_profile['avg_emotional'] = (
        (current_profile['avg_emotional'] * total_dreams +
         dream_metrics.get('emotional_charge', 0.0)) / new_total
    )

    current_profile['avg_coherence'] = (
        (current_profile['avg_coherence'] * total_dreams +
         dream_metrics.get('narrative_coherence', 0.8)) / new_total
    )

    current_profile['total_dreams'] = new_total

    # Add drift to history (keep last 100 entries)
    drift_history = current_profile.get('drift_history', [])
    drift_history.append(drift_result)
    current_profile['drift_history'] = drift_history[-100:]

    # Save updated profile
    await update_drift_profile(user_id, current_profile)

    return current_profile

async def get_drift_trends(user_id: str, days: int = 30) -> dict:
    """
    Analyze drift trends over time

    Args:
        user_id: User identifier
        days: Number of days to analyze

    Returns:
        Drift trend analysis
    """
    profile = await get_user_profile(user_id)
    if not profile or not profile.get('drift_history'):
        return {'trend': 'insufficient_data', 'avg_drift': 0.0}

    # Get recent drift history
    recent_drifts = profile['drift_history'][-days:]

    if len(recent_drifts) < 2:
        return {'trend': 'insufficient_data', 'avg_drift': 0.0}

    # Calculate trend
    avg_drift = sum(d['drift_score'] for d in recent_drifts) / len(recent_drifts)

    # Simple trend analysis (compare first half vs second half)
    mid_point = len(recent_drifts) // 2
    first_half_avg = sum(d['drift_score'] for d in recent_drifts[:mid_point]) / mid_point
    second_half_avg = sum(d['drift_score'] for d in recent_drifts[mid_point:]) / (len(recent_drifts) - mid_point)

    trend = 'stable'
    if second_half_avg > first_half_avg * 1.2:
        trend = 'increasing'
    elif second_half_avg < first_half_avg * 0.8:
        trend = 'decreasing'

    return {
        'trend': trend,
        'avg_drift': round(avg_drift, 3),
        'recent_avg': round(second_half_avg, 3),
        'baseline_avg': round(first_half_avg, 3),
        'total_dreams': len(recent_drifts)
    }

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: drift_score.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 2-5 (Advanced symbolic analysis)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Drift score calculation, symbolic state tracking, trend analysis,
#               profile evolution monitoring, entropy/emotional/coherence analysis
# FUNCTIONS: calculate_drift_score, update_user_drift_profile, get_drift_trends
# CLASSES: None
# DECORATORS: None
# DEPENDENCIES: json, typing, user_repository
# INTERFACES: User profile database operations
# ERROR HANDLING: Graceful handling of missing data
# LOGGING: ΛTRACE_ENABLED for drift calculations
# AUTHENTICATION: None (uses repository layer)
# HOW TO USE:
#   drift = await calculate_drift_score("user_id", dream_metrics)
#   profile = await update_user_drift_profile("user_id", dream_metrics)
# INTEGRATION NOTES: Core to symbolic evolution tracking in dream generation
# MAINTENANCE: Monitor drift thresholds and algorithm effectiveness
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
