#!/usr/bin/env python3
"""
Tiny ABAS Gate - Drop-in attention boundary protection
Ready-to-ship implementation for immediate use in delivery engine
"""

import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class GateDecision:
    """ABAS gate decision result"""

    approved: bool
    reason: Optional[str] = None
    confidence: float = 1.0
    defer_until: Optional[int] = None  # epoch timestamp


class TinyABASGate:
    """
    Lightweight ABAS attention gate implementation

    Protects users from interruptions during:
    - High stress states
    - Safety-critical situations (driving)
    - Deep focus/flow states
    - Quiet hours
    - Low-alignment opportunities
    """

    def __init__(self):
        self.quiet_hours_start = 22  # 10 PM
        self.quiet_hours_end = 7  # 7 AM
        self.stress_threshold = 0.8
        self.alignment_threshold = 0.3

    def check_gate(self, user_state: dict[str, Any], opportunity: dict[str, Any]) -> GateDecision:
        """
        Primary gate check function

        Args:
            user_state: Current user attention and context state
            opportunity: Opportunity object to evaluate

        Returns:
            GateDecision with approval status and human-readable reason
        """
        # Safety block - absolute priority
        if user_state.get("driving", False):
            return GateDecision(approved=False, reason="safety_block", confidence=1.0)

        # Stress protection
        stress_level = user_state.get("stress", 0.0)
        if stress_level > self.stress_threshold:
            defer_time = int(time.time()) + (2 * 3600)  # 2 hours
            return GateDecision(approved=False, reason="stress_block", confidence=0.9, defer_until=defer_time)

        # Flow state protection
        if user_state.get("flow_state", False):
            return GateDecision(approved=False, reason="flow_protection", confidence=0.95)

        # Deep focus protection
        focus_level = user_state.get("focus_level", 0.0)
        if focus_level > 0.8:
            return GateDecision(approved=False, reason="deep_focus", confidence=0.8)

        # Quiet hours protection
        current_hour = user_state.get("hour")
        if current_hour is not None and self._is_quiet_hours(current_hour):
            return GateDecision(approved=False, reason="quiet_hours", confidence=0.7)

        # Low alignment protection
        alignment = self._get_alignment_score(opportunity)
        if alignment < self.alignment_threshold:
            return GateDecision(approved=False, reason="low_alignment", confidence=0.6)

        # Stress-sensitive opportunities
        if opportunity.get("risk", {}).get("stress_block", False) and stress_level > 0.5:
            return GateDecision(approved=False, reason="stress_sensitive", confidence=0.7)

        # All checks passed
        return GateDecision(
            approved=True,
            reason=None,
            confidence=self._calculate_approval_confidence(user_state, opportunity),
        )

    def _is_quiet_hours(self, hour: int) -> bool:
        """Check if current hour is within quiet hours"""
        if self.quiet_hours_start > self.quiet_hours_end:
            # Wraps around midnight (e.g., 22-7)
            return hour >= self.quiet_hours_start or hour < self.quiet_hours_end
        else:
            # Same day (e.g., 1-5)
            return self.quiet_hours_start <= hour < self.quiet_hours_end

    def _get_alignment_score(self, opportunity: dict[str, Any]) -> float:
        """Extract alignment score from opportunity"""
        return opportunity.get("risk", {}).get("alignment", 0.5)

    def _calculate_approval_confidence(self, user_state: dict[str, Any], opportunity: dict[str, Any]) -> float:
        """Calculate confidence score for approval decision"""
        confidence_factors = []

        # High alignment boosts confidence
        alignment = self._get_alignment_score(opportunity)
        confidence_factors.append(min(alignment * 1.2, 1.0))

        # Low stress boosts confidence
        stress = user_state.get("stress", 0.0)
        confidence_factors.append(1.0 - stress * 0.5)

        # Good timing boosts confidence
        current_hour = user_state.get("hour")
        if current_hour and 9 <= current_hour <= 21:  # Daytime hours
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)

        return sum(confidence_factors) / len(confidence_factors)

    def get_human_readable_reason(self, reason: str) -> str:
        """Convert reason codes to human-readable explanations"""
        reason_map = {
            "safety_block": "Blocked for your safety while driving",
            "stress_block": "Deferred - you seem stressed right now",
            "flow_protection": "Protecting your flow state - you're in the zone!",
            "deep_focus": "You're deeply focused - we'll wait for a better moment",
            "quiet_hours": "Respecting quiet hours - we'll try again tomorrow",
            "low_alignment": "This doesn't seem like a good match for you right now",
            "stress_sensitive": "This type of content is deferred when you're stressed",
        }
        return reason_map.get(reason, f"Deferred: {reason}")


# Convenience function for drop-in usage
def abas_gate(user_state: dict[str, Any], opportunity: dict[str, Any]) -> dict[str, Any]:
    """
    Simple function interface for ABAS gate

    Usage:
        result = abas_gate(user, opportunity)
        if result['approved']:
            # Proceed with delivery
        else:
            # Block or defer
            print(f"Blocked: {result['reason']}")
    """
    gate = TinyABASGate()
    decision = gate.check_gate(user_state, opportunity)

    return {
        "approved": decision.approved,
        "reason": decision.reason,
        "confidence": decision.confidence,
        "defer_until": decision.defer_until,
        "explanation": gate.get_human_readable_reason(decision.reason) if decision.reason else None,
    }


# JavaScript equivalent (can be copied to frontend)
JAVASCRIPT_EQUIVALENT = """
export function abasGate(user, opportunity) {
  // Safety block - absolute priority
  if (user.driving) {
    return { approved: false, reason: "safety_block", confidence: 1.0 };
  }

  // Stress protection
  if ((user.stress ?? 0) > 0.8) {
    const deferUntil = Date.now() + (2 * 60 * 60 * 1000); // 2 hours
    return {
      approved: false,
      reason: "stress_block",
      confidence: 0.9,
      deferUntil
    };
  }

  // Flow state protection
  if (user.flowState) {
    return { approved: false, reason: "flow_protection", confidence: 0.95 };
  }

  // Deep focus protection
  if ((user.focusLevel ?? 0) > 0.8) {
    return { approved: false, reason: "deep_focus", confidence: 0.8 };
  }

  // Quiet hours protection
  if (user.hour !== undefined) {
    const isQuietHours = (user.hour >= 22 || user.hour < 7);
    if (isQuietHours) {
      return { approved: false, reason: "quiet_hours", confidence: 0.7 };
    }
  }

  // Low alignment protection
  const alignment = opportunity.risk?.alignment ?? 0.5;
  if (alignment < 0.3) {
    return { approved: false, reason: "low_alignment", confidence: 0.6 };
  }

  // Stress-sensitive opportunities
  if (opportunity.risk?.stressBlock && (user.stress ?? 0) > 0.5) {
    return { approved: false, reason: "stress_sensitive", confidence: 0.7 };
  }

  // Calculate approval confidence
  const stressFactor = 1.0 - (user.stress ?? 0) * 0.5;
  const alignmentFactor = Math.min(alignment * 1.2, 1.0);
  const timingFactor = (user.hour >= 9 && user.hour <= 21) ? 0.9 : 0.6;
  const confidence = (stressFactor + alignmentFactor + timingFactor) / 3;

  return { approved: true, reason: null, confidence };
}
"""


if __name__ == "__main__":
    # Demo usage
    gate = TinyABASGate()

    # Test cases
    test_cases = [
        {
            "name": "Safe delivery",
            "user": {"stress": 0.2, "hour": 14, "focus_level": 0.3},
            "opportunity": {"risk": {"alignment": 0.8},
        },
        {
            "name": "Driving block",
            "user": {"driving": True},
            "opportunity": {"risk": {"alignment": 0.9},
        },
        {
            "name": "Stress block",
            "user": {"stress": 0.9, "hour": 14},
            "opportunity": {"risk": {"alignment": 0.7},
        },
        {
            "name": "Flow state protection",
            "user": {"flow_state": True, "stress": 0.1},
            "opportunity": {"risk": {"alignment": 0.8},
        },
        {
            "name": "Quiet hours",
            "user": {"hour": 23, "stress": 0.1},
            "opportunity": {"risk": {"alignment": 0.8},
        },
        {
            "name": "Low alignment",
            "user": {"stress": 0.1, "hour": 14},
            "opportunity": {"risk": {"alignment": 0.2},
        },
    ]

    print("🛡️ ABAS Gate Demo\n")

    for case in test_cases:
        result = abas_gate(case["user"], case["opportunity"])
        status = "✅ APPROVED" if result["approved"] else "❌ BLOCKED"

        print(f"{case['name']}: {status}")
        if not result["approved"]:
            print(f"   Reason: {result['explanation']}")
            if result.get("defer_until"):
                defer_time = time.strftime("%H:%M", time.localtime(result["defer_until"]))
                print(f"   Defer until: {defer_time}")
        print(f"   Confidence: {result['confidence']:.2f}\n")