"""
NIAS Transparency Layers - Demonstration and Testing
Shows the 7-tier transparency system in action without external dependencies
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict


# Recreate the enums for demonstration
class UserTier(Enum):
    """User tiers for NIAS transparency levels"""

    GUEST = "guest"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"
    DEVELOPER = "developer"
    AUDITOR = "auditor"


class TransparencyLevel(Enum):
    """Transparency levels for NIAS explanations"""

    MINIMAL = "minimal"
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"
    AUDIT_TRAIL = "audit_trail"
    FULL_DEBUG = "full_debug"


class NIASTransparencyDemo:
    """Demonstration of NIAS Transparency Layers functionality"""

    def __init__(self):
        # Transparency configuration
        self.transparency_config = {
            UserTier.GUEST: TransparencyLevel.MINIMAL,
            UserTier.STANDARD: TransparencyLevel.SUMMARY,
            UserTier.PREMIUM: TransparencyLevel.DETAILED,
            UserTier.ENTERPRISE: TransparencyLevel.COMPREHENSIVE,
            UserTier.ADMIN: TransparencyLevel.TECHNICAL,
            UserTier.DEVELOPER: TransparencyLevel.AUDIT_TRAIL,
            UserTier.AUDITOR: TransparencyLevel.FULL_DEBUG,
        }

        self.explanation_cache = {}
        self.query_history = []
        self.mutation_history = []
        self.filtered_content = []

    async def get_transparency_level(
        self, user_context: Dict[str, Any]
    ) -> TransparencyLevel:
        """Determine transparency level based on user tier"""
        user_tier_str = user_context.get("tier", "guest")

        try:
            user_tier = UserTier(user_tier_str.lower())
        except ValueError:
            user_tier = UserTier.GUEST

        # Check for explicit transparency preference
        if "transparency_preference" in user_context:
            pref = user_context["transparency_preference"]
            try:
                return TransparencyLevel(pref)
            except ValueError:
                pass

        return self.transparency_config.get(user_tier, TransparencyLevel.MINIMAL)

    def _generate_minimal_explanation(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Generate minimal explanation for guest users"""
        return {
            "type": "minimal",
            "summary": "Content filtered based on system policies",
            "action_taken": decision.get("action", "filtered"),
        }

    def _generate_summary_explanation(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary explanation for standard users"""
        return {
            "type": "summary",
            "summary": f"Content {decision.get('action', 'filtered')} due to {decision.get('reason', 'policy match')}",
            "categories": decision.get("matched_categories", []),
            "confidence": decision.get("confidence", "high"),
        }

    def _generate_detailed_explanation(
        self, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed explanation for premium users"""
        return {
            "type": "detailed",
            "summary": f"Content {decision.get('action', 'filtered')} due to {decision.get('reason', 'policy match')}",
            "categories": decision.get("matched_categories", []),
            "confidence": decision.get("confidence", "high"),
            "policy_details": decision.get("policies_triggered", []),
            "alternatives": decision.get("suggested_alternatives", []),
            "appeal_process": "Available through user settings",
        }

    def _generate_comprehensive_explanation(
        self, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation for enterprise users"""
        return {
            "type": "comprehensive",
            "summary": f"Content {decision.get('action', 'filtered')} due to {decision.get('reason', 'policy match')}",
            "categories": decision.get("matched_categories", []),
            "confidence": decision.get("confidence", "high"),
            "policy_details": decision.get("policies_triggered", []),
            "decision_tree": decision.get("decision_path", []),
            "risk_assessment": decision.get("risk_scores", {}),
            "compliance_notes": decision.get("compliance_requirements", []),
            "alternatives": decision.get("suggested_alternatives", []),
            "appeal_process": "Available through enterprise dashboard",
            "custom_rules": decision.get("custom_rules_applied", []),
        }

    def _generate_technical_explanation(
        self, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate technical explanation for admin users"""
        return {
            "type": "technical",
            "decision_data": decision,
            "algorithm_version": "2.5.1",
            "processing_time_ms": decision.get("processing_time", 45),
            "feature_vectors": decision.get(
                "features", {"spam_score": 0.89, "toxicity": 0.12}
            ),
            "model_scores": decision.get(
                "model_outputs", {"primary": 0.92, "secondary": 0.88}
            ),
            "threshold_values": decision.get(
                "thresholds", {"spam": 0.7, "toxicity": 0.5}
            ),
            "debug_flags": decision.get(
                "debug", {"cache_hit": False, "fast_path": True}
            ),
        }

    async def _generate_audit_trail_explanation(
        self, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate audit trail explanation for developers"""
        return {
            "type": "audit_trail",
            "decision_data": decision,
            "audit_trail": {
                "decision_id": decision.get("id"),
                "timestamp": datetime.now().isoformat(),
                "checkpoints": [
                    {"step": "consent_check", "status": "passed", "time_ms": 5},
                    {"step": "content_analysis", "status": "completed", "time_ms": 30},
                    {"step": "policy_evaluation", "status": "triggered", "time_ms": 10},
                    {"step": "decision_made", "status": "filtered", "time_ms": 2},
                ],
            },
            "symbolic_trace": decision.get(
                "symbolic_trace", ["RULE_SPAM_001", "RULE_MARKETING_002"]
            ),
            "ethics_validation": decision.get(
                "ethics_check", {"passed": True, "score": 0.95}
            ),
            "consent_verification": decision.get(
                "consent_status", {"verified": True, "timestamp": "2025-07-30T10:00:00"}
            ),
            "system_state": {
                "components": ["filter_engine", "policy_manager", "audit_logger"],
                "active_policies": 15,
            },
        }

    async def _generate_full_debug_explanation(
        self, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate full debug explanation for auditors"""
        return {
            "type": "full_debug",
            "decision_data": decision,
            "complete_audit": {
                "full_trace": "Complete decision trace with 247 events",
                "memory_snapshot": "System memory state at decision time",
                "performance_profile": "Detailed performance metrics",
            },
            "system_snapshot": {
                "components": {
                    "filter_engine": {"status": "active", "version": "2.5.1"},
                    "policy_manager": {"status": "active", "policies": 15},
                    "audit_logger": {"status": "active", "queue_size": 42},
                },
                "consent_records": 1523,
                "active_filters": ["spam", "toxicity", "marketing", "phishing"],
                "performance_metrics": {
                    "avg_processing_time_ms": 45,
                    "p95_processing_time_ms": 120,
                    "cache_hit_rate": 0.82,
                    "active_components": 7,
                },
            },
            "query_history": self.query_history[-5:],
            "mutation_history": self.mutation_history[-5:],
            "error_logs": [],
            "compliance_status": {
                "gdpr_compliant": True,
                "consent_rate": 0.98,
                "data_retention_compliant": True,
                "last_audit": datetime.now().isoformat(),
            },
        }

    async def generate_explanation(
        self, decision: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate tier-appropriate explanation for NIAS decision"""
        transparency_level = await self.get_transparency_level(user_context)

        explanation = {
            "decision_id": decision.get("id"),
            "timestamp": datetime.now().isoformat(),
            "transparency_level": transparency_level.value,
            "user_tier": user_context.get("tier", "guest"),
        }

        # Generate explanation based on transparency level
        if transparency_level == TransparencyLevel.MINIMAL:
            explanation["content"] = self._generate_minimal_explanation(decision)
        elif transparency_level == TransparencyLevel.SUMMARY:
            explanation["content"] = self._generate_summary_explanation(decision)
        elif transparency_level == TransparencyLevel.DETAILED:
            explanation["content"] = self._generate_detailed_explanation(decision)
        elif transparency_level == TransparencyLevel.COMPREHENSIVE:
            explanation["content"] = self._generate_comprehensive_explanation(decision)
        elif transparency_level == TransparencyLevel.TECHNICAL:
            explanation["content"] = self._generate_technical_explanation(decision)
        elif transparency_level == TransparencyLevel.AUDIT_TRAIL:
            explanation["content"] = await self._generate_audit_trail_explanation(
                decision
            )
        elif transparency_level == TransparencyLevel.FULL_DEBUG:
            explanation["content"] = await self._generate_full_debug_explanation(
                decision
            )

        return explanation

    async def filter_content_demo(
        self, content: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Demonstrate content filtering with transparency"""
        # Simulate filtering decision
        decision = {
            "id": f"decision_{content.get('id', 'unknown')}",
            "filtered": True,
            "action": "blocked",
            "reason": "spam_detected",
            "matched_categories": ["spam", "marketing"],
            "confidence": "high",
            "policies_triggered": ["anti-spam-v2", "marketing-filter"],
            "processing_time": 42,
            "risk_scores": {"spam": 0.89, "phishing": 0.23},
            "compliance_requirements": ["GDPR Article 6", "CAN-SPAM Act"],
            "suggested_alternatives": [
                "Reduce promotional language",
                "Add unsubscribe link",
            ],
            "decision_path": [
                "initial_scan",
                "keyword_match",
                "ml_classification",
                "policy_check",
            ],
            "symbolic_trace": [
                "SCAN_001",
                "MATCH_SPAM_KEYWORDS",
                "ML_CLASSIFY_SPAM",
                "POLICY_TRIGGER",
            ],
            "ethics_check": {"passed": True, "score": 0.92},
            "consent_status": {"verified": True, "type": "explicit"},
        }

        # Generate explanation
        explanation = await self.generate_explanation(decision, user_context)
        decision["explanation"] = explanation

        # Record for history
        self.filtered_content.append(
            {
                "content": content,
                "result": decision,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return decision


async def run_transparency_demo():
    """Run comprehensive demonstration of transparency layers"""
    demo = NIASTransparencyDemo()

    print("=" * 80)
    print("🔍 NIAS TRANSPARENCY LAYERS DEMONSTRATION")
    print("=" * 80)
    print()

    # Test content
    test_content = {
        "id": "demo_content_001",
        "type": "advertisement",
        "data": "AMAZING OFFER! Buy now and save 90%! Limited time only!",
    }

    # Test with all user tiers
    user_tiers = [
        ("Guest User", "guest"),
        ("Standard User", "standard"),
        ("Premium User", "premium"),
        ("Enterprise User", "enterprise"),
        ("Admin User", "admin"),
        ("Developer", "developer"),
        ("Auditor", "auditor"),
    ]

    results = []

    for user_name, tier in user_tiers:
        print(f"\n{'=' * 60}")
        print(f"👤 {user_name} (Tier: {tier})")
        print(f"{'=' * 60}")

        user_context = {"tier": tier, "user_id": f"demo_{tier}_user"}

        result = await demo.filter_content_demo(test_content, user_context)
        explanation = result["explanation"]

        print(f"\n📊 Transparency Level: {explanation['transparency_level']}")
        print(f"⏰ Generated: {explanation['timestamp']}")

        content = explanation["content"]
        print(f"\n📝 Explanation Type: {content['type']}")

        # Display tier-specific information
        if content["type"] == "minimal":
            print(f"   Summary: {content['summary']}")
            print(f"   Action: {content['action_taken']}")

        elif content["type"] == "summary":
            print(f"   Summary: {content['summary']}")
            print(f"   Categories: {', '.join(content['categories'])}")
            print(f"   Confidence: {content['confidence']}")

        elif content["type"] == "detailed":
            print(f"   Summary: {content['summary']}")
            print(f"   Categories: {', '.join(content['categories'])}")
            print(f"   Policies: {', '.join(content['policy_details'])}")
            print(f"   Alternatives: {', '.join(content['alternatives'][:2])}")
            print(f"   Appeal: {content['appeal_process']}")

        elif content["type"] == "comprehensive":
            print(f"   Summary: {content['summary']}")
            print(f"   Risk Assessment: {content['risk_assessment']}")
            print(f"   Compliance: {', '.join(content['compliance_notes'][:2])}")
            print(f"   Decision Path: {' → '.join(content['decision_tree'][:3])}...")

        elif content["type"] == "technical":
            print(f"   Algorithm: v{content['algorithm_version']}")
            print(f"   Processing: {content['processing_time_ms']}ms")
            print(f"   Model Scores: {content['model_scores']}")
            print(f"   Thresholds: {content['threshold_values']}")

        elif content["type"] == "audit_trail":
            print(
                f"   Audit Steps: {len(content['audit_trail']['checkpoints'])} checkpoints"
            )
            print(f"   Symbolic Trace: {' → '.join(content['symbolic_trace'])}")
            print(f"   Ethics Score: {content['ethics_validation']['score']}")
            print(f"   Active Policies: {content['system_state']['active_policies']}")

        elif content["type"] == "full_debug":
            print(
                f"   System Components: {len(content['system_snapshot']['components'])}"
            )
            print("   Performance Metrics:")
            metrics = content["system_snapshot"]["performance_metrics"]
            print(f"      - Avg Processing: {metrics['avg_processing_time_ms']}ms")
            print(f"      - Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
            print(
                f"   Compliance Status: GDPR={content['compliance_status']['gdpr_compliant']}"
            )
            print("   Complete Audit: Available")

        results.append(
            {
                "tier": tier,
                "transparency_level": explanation["transparency_level"],
                "info_items": len(content.keys()),
            }
        )

    # Summary
    print(f"\n\n{'=' * 80}")
    print("📊 DEMONSTRATION SUMMARY")
    print(f"{'=' * 80}")
    print("\n✅ Successfully demonstrated 7-tier transparency system:")
    print("\n| Tier | Transparency Level | Information Items |")
    print("|------|-------------------|-------------------|")
    for r in results:
        print(
            f"| {r['tier']:10} | {r['transparency_level']:17} | {r['info_items']:17} |"
        )

    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Progressive information disclosure")
    print("   ✅ Tier-appropriate explanations")
    print("   ✅ Natural language summaries")
    print("   ✅ Technical details for admins")
    print("   ✅ Full audit trails for developers")
    print("   ✅ Complete system snapshot for auditors")

    # Test natural language generation
    print(f"\n\n{'=' * 80}")
    print("💬 NATURAL LANGUAGE EXPLANATION EXAMPLES")
    print(f"{'=' * 80}")

    for tier_name, tier in [
        ("Standard", "standard"),
        ("Premium", "premium"),
        ("Admin", "admin"),
    ]:
        user_context = {"tier": tier}
        result = await demo.filter_content_demo(test_content, user_context)

        # Generate natural language
        content = result["explanation"]["content"]
        if tier == "standard":
            nl = f"This content was blocked because it matched these categories: {', '.join(content['categories'])}."
        elif tier == "premium":
            nl = f"This content was blocked because it matched {', '.join(content['categories'])} categories and triggered {len(content['policy_details'])} policies. {content['appeal_process']}"
        else:
            nl = f"Technical Analysis - Algorithm: v{content['algorithm_version']} | Processing: {content['processing_time_ms']}ms | Model scores: {content['model_scores']}"

        print(f"\n{tier_name}: {nl}")

    print(f"\n{'=' * 80}")
    print("✅ DEMONSTRATION COMPLETE")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    asyncio.run(run_transparency_demo())
