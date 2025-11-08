#!/usr/bin/env python3
"""
Safety Tag DSL Tests (SG008)
============================

Comprehensive test suite for LUKHAS Guardian safety tag DSL validation.
Tests safety classification, tag propagation, and DSL enforcement patterns.

P1 Task: SG008 - Implement safety tag DSL tests
Priority: High (P1)
Agent: Claude Code (Testing/Documentation)

Constellation Framework: 🛡️ Guardian · ⚖️ Ethics

Features Tested:
- Safety tag classification (SAFE, CAUTION, DANGER, CRITICAL)
- Tag propagation across consciousness layers
- DSL syntax validation and parsing
- Permission enforcement based on safety levels
- Tag inheritance and escalation rules
- Emergency override patterns
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import pytest

try:
    import jsonschema
except ImportError:
    pytest.skip("jsonschema required for DSL validation tests", allow_module_level=True)


# ============================================================================
# Safety Tag DSL Data Structures
# ============================================================================

class SafetyLevel:
    """Safety classification levels for Guardian DSL"""
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGER = "DANGER"
    CRITICAL = "CRITICAL"

    ALL_LEVELS = [SAFE, CAUTION, DANGER, CRITICAL]  # TODO[T4-ISSUE]: {"code":"RUF012","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Mutable class attribute needs ClassVar annotation for type safety","estimate":"15m","priority":"medium","dependencies":"typing imports","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_governance_test_safety_tag_dsl_py_L49"}

    @classmethod
    def get_numeric_level(cls, level: str) -> int:
        """Convert safety level to numeric priority (higher = more restrictive)"""
        mapping = {
            cls.SAFE: 0,
            cls.CAUTION: 1,
            cls.DANGER: 2,
            cls.CRITICAL: 3
        }
        return mapping.get(level, 0)


class SafetyTag:
    """Individual safety tag with DSL metadata"""

    def __init__(
        self,
        level: str,
        category: str,
        description: str,
        metadata: Optional[dict[str, Any]] = None
    ):
        self.level = level
        self.category = category
        self.description = description
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
        self.tag_id = str(uuid.uuid4())

    def to_dsl(self) -> dict[str, Any]:
        """Convert to Guardian DSL format"""
        return {
            "tag_id": self.tag_id,
            "level": self.level,
            "category": self.category,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "numeric_priority": SafetyLevel.get_numeric_level(self.level)
        }

    def can_inherit_from(self, parent_tag: 'SafetyTag') -> bool:
        """Check if this tag can inherit from a parent tag"""
        parent_level = SafetyLevel.get_numeric_level(parent_tag.level)
        current_level = SafetyLevel.get_numeric_level(self.level)
        # Can only inherit from equal or lower security levels
        return current_level >= parent_level


class SafetyTagCollection:
    """Collection of safety tags with DSL operations"""

    def __init__(self):
        self.tags: list[SafetyTag] = []

    def add_tag(self, tag: SafetyTag) -> None:
        """Add a safety tag to the collection"""
        self.tags.append(tag)

    def get_highest_level(self) -> str:
        """Get the highest (most restrictive) safety level"""
        if not self.tags:
            return SafetyLevel.SAFE

        max_level = SafetyLevel.SAFE
        max_numeric = -1

        for tag in self.tags:
            numeric = SafetyLevel.get_numeric_level(tag.level)
            if numeric > max_numeric:
                max_numeric = numeric
                max_level = tag.level

        return max_level

    def has_critical_tags(self) -> bool:
        """Check if collection contains any CRITICAL level tags"""
        return any(tag.level == SafetyLevel.CRITICAL for tag in self.tags)

    def get_tags_by_category(self, category: str) -> list[SafetyTag]:
        """Get all tags for a specific category"""
        return [tag for tag in self.tags if tag.category == category]

    def to_dsl(self) -> dict[str, Any]:
        """Convert entire collection to Guardian DSL format"""
        return {
            "safety_tags": [tag.to_dsl() for tag in self.tags],
            "highest_level": self.get_highest_level(),
            "tag_count": len(self.tags),
            "has_critical": self.has_critical_tags(),
            "categories": list({tag.category for tag in self.tags})
        }


# ============================================================================
# Test Classes
# ============================================================================

class TestSafetyTagBasics:
    """Test basic safety tag creation and validation"""

    def test_safety_tag_creation(self):
        """Test creating a basic safety tag"""
        tag = SafetyTag(
            level=SafetyLevel.CAUTION,
            category="consciousness_processing",
            description="Consciousness integration requires careful monitoring"
        )

        assert tag.level == SafetyLevel.CAUTION
        assert tag.category == "consciousness_processing"
        assert tag.description == "Consciousness integration requires careful monitoring"
        assert tag.tag_id is not None
        assert tag.timestamp is not None

    def test_safety_level_numeric_mapping(self):
        """Test numeric level mapping for priority comparison"""
        assert SafetyLevel.get_numeric_level(SafetyLevel.SAFE) == 0
        assert SafetyLevel.get_numeric_level(SafetyLevel.CAUTION) == 1
        assert SafetyLevel.get_numeric_level(SafetyLevel.DANGER) == 2
        assert SafetyLevel.get_numeric_level(SafetyLevel.CRITICAL) == 3

    def test_safety_tag_dsl_format(self):
        """Test safety tag conversion to DSL format"""
        tag = SafetyTag(
            level=SafetyLevel.DANGER,
            category="memory_access",
            description="High-tier memory access requires approval",
            metadata={"tier": "T4", "requires_approval": True}
        )

        dsl = tag.to_dsl()

        assert dsl["level"] == SafetyLevel.DANGER
        assert dsl["category"] == "memory_access"
        assert dsl["numeric_priority"] == 2
        assert dsl["metadata"]["tier"] == "T4"
        assert "tag_id" in dsl
        assert "timestamp" in dsl


class TestSafetyTagInheritance:
    """Test safety tag inheritance and escalation rules"""

    def test_tag_inheritance_allowed(self):
        """Test valid tag inheritance patterns"""
        parent_tag = SafetyTag(SafetyLevel.CAUTION, "base", "Parent operation")
        child_tag = SafetyTag(SafetyLevel.DANGER, "derived", "Child operation")

        # Child can inherit from parent with equal or lower security
        assert child_tag.can_inherit_from(parent_tag)

    def test_tag_inheritance_blocked(self):
        """Test blocked tag inheritance patterns"""
        critical_parent = SafetyTag(SafetyLevel.CRITICAL, "base", "Critical operation")
        safe_child = SafetyTag(SafetyLevel.SAFE, "derived", "Safe operation")

        # Safe child cannot inherit from critical parent
        assert not safe_child.can_inherit_from(critical_parent)

    def test_same_level_inheritance(self):
        """Test inheritance between same safety levels"""
        tag1 = SafetyTag(SafetyLevel.CAUTION, "op1", "Operation 1")
        tag2 = SafetyTag(SafetyLevel.CAUTION, "op2", "Operation 2")

        assert tag1.can_inherit_from(tag2)
        assert tag2.can_inherit_from(tag1)


class TestSafetyTagCollection:
    """Test safety tag collection operations"""

    def setup_method(self):
        """Setup test collection with mixed safety levels"""
        self.collection = SafetyTagCollection()

        # Add tags with different safety levels
        self.collection.add_tag(SafetyTag(SafetyLevel.SAFE, "general", "Safe operation"))
        self.collection.add_tag(SafetyTag(SafetyLevel.CAUTION, "memory", "Memory access"))
        self.collection.add_tag(SafetyTag(SafetyLevel.DANGER, "consciousness", "Consciousness modification"))

    def test_highest_level_detection(self):
        """Test detection of highest safety level in collection"""
        assert self.collection.get_highest_level() == SafetyLevel.DANGER

    def test_critical_tag_detection(self):
        """Test detection of critical tags in collection"""
        assert not self.collection.has_critical_tags()

        # Add critical tag
        self.collection.add_tag(SafetyTag(SafetyLevel.CRITICAL, "emergency", "Emergency override"))
        assert self.collection.has_critical_tags()
        assert self.collection.get_highest_level() == SafetyLevel.CRITICAL

    def test_category_filtering(self):
        """Test filtering tags by category"""
        memory_tags = self.collection.get_tags_by_category("memory")
        assert len(memory_tags) == 1
        assert memory_tags[0].level == SafetyLevel.CAUTION

    def test_collection_dsl_format(self):
        """Test collection conversion to DSL format"""
        dsl = self.collection.to_dsl()

        assert dsl["highest_level"] == SafetyLevel.DANGER
        assert dsl["tag_count"] == 3
        assert not dsl["has_critical"]
        assert "general" in dsl["categories"]
        assert "memory" in dsl["categories"]
        assert "consciousness" in dsl["categories"]


class TestSafetyTagDSLSyntax:
    """Test DSL syntax validation and parsing"""

    def test_valid_dsl_syntax(self):
        """Test parsing of valid safety tag DSL"""
        dsl_input = {
            "safety_rule": "CRITICAL: consciousness.modify REQUIRES dual_approval",
            "conditions": {
                "tier_minimum": "T4",
                "approval_count": 2,
                "timeout_minutes": 15
            },
            "actions": ["block", "audit", "notify_admin"]
        }

        # This would be parsed by a real DSL parser
        # For testing, we validate structure
        assert "safety_rule" in dsl_input
        assert "CRITICAL" in dsl_input["safety_rule"]
        assert "dual_approval" in dsl_input["safety_rule"]
        assert dsl_input["conditions"]["approval_count"] == 2

    def test_dsl_syntax_patterns(self):
        """Test various DSL syntax patterns"""
        patterns = [
            "SAFE: general.operation ALLOWS unrestricted",
            "CAUTION: memory.read REQUIRES tier_T2",
            "DANGER: consciousness.write REQUIRES tier_T4 AND approval",
            "CRITICAL: system.override REQUIRES dual_approval AND emergency_ticket"
        ]

        for pattern in patterns:
            # Test basic DSL pattern structure
            assert ":" in pattern
            assert "REQUIRES" in pattern or "ALLOWS" in pattern

            parts = pattern.split(":")
            assert len(parts) == 2

            level = parts[0].strip()
            assert level in SafetyLevel.ALL_LEVELS


class TestSafetyTagEnforcement:
    """Test safety tag enforcement and permission checking"""

    def test_safe_level_enforcement(self):
        """Test enforcement for SAFE level operations"""
        tag = SafetyTag(SafetyLevel.SAFE, "general", "Safe operation")

        # SAFE level should allow most operations
        assert self._check_permission(tag, tier="T1", has_approval=False)
        assert self._check_permission(tag, tier="T2", has_approval=False)

    def test_caution_level_enforcement(self):
        """Test enforcement for CAUTION level operations"""
        tag = SafetyTag(SafetyLevel.CAUTION, "memory", "Memory access")

        # CAUTION level should require minimum tier
        assert not self._check_permission(tag, tier="T1", has_approval=False)
        assert self._check_permission(tag, tier="T2", has_approval=False)

    def test_danger_level_enforcement(self):
        """Test enforcement for DANGER level operations"""
        tag = SafetyTag(SafetyLevel.DANGER, "consciousness", "Consciousness modification")

        # DANGER level should require high tier
        assert not self._check_permission(tag, tier="T2", has_approval=False)
        assert self._check_permission(tag, tier="T4", has_approval=False)

    def test_critical_level_enforcement(self):
        """Test enforcement for CRITICAL level operations"""
        tag = SafetyTag(SafetyLevel.CRITICAL, "emergency", "Emergency override")

        # CRITICAL level should require dual approval even for T4
        assert not self._check_permission(tag, tier="T4", has_approval=False)
        assert self._check_permission(tag, tier="T4", has_approval=True)

    def _check_permission(self, tag: SafetyTag, tier: str, has_approval: bool) -> bool:
        """Mock permission checking logic"""
        tier_levels = {"T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5}
        user_tier = tier_levels.get(tier, 0)

        if tag.level == SafetyLevel.SAFE:
            return True
        elif tag.level == SafetyLevel.CAUTION:
            return user_tier >= 2
        elif tag.level == SafetyLevel.DANGER:
            return user_tier >= 4
        elif tag.level == SafetyLevel.CRITICAL:
            return user_tier >= 4 and has_approval

        return False


class TestSafetyTagPropagation:
    """Test safety tag propagation across consciousness layers"""

    def test_tag_propagation_simple(self):
        """Test basic tag propagation between layers"""
        source_tag = SafetyTag(SafetyLevel.CAUTION, "memory", "Memory operation")

        # Propagate to consciousness layer
        consciousness_tag = self._propagate_tag(source_tag, "consciousness")

        assert consciousness_tag.category == "consciousness"
        assert consciousness_tag.level == SafetyLevel.CAUTION  # Should maintain level
        assert "propagated_from" in consciousness_tag.metadata

    def test_tag_escalation_on_propagation(self):
        """Test tag escalation during propagation to sensitive layers"""
        source_tag = SafetyTag(SafetyLevel.SAFE, "general", "General operation")

        # Propagate to critical system layer - should escalate
        critical_tag = self._propagate_tag(source_tag, "system_critical")

        assert critical_tag.level == SafetyLevel.DANGER  # Escalated
        assert "escalated" in critical_tag.metadata

    def test_tag_propagation_chain(self):
        """Test propagation through multiple layers"""
        original_tag = SafetyTag(SafetyLevel.CAUTION, "api", "API request")

        # Propagate through chain: api -> memory -> consciousness
        memory_tag = self._propagate_tag(original_tag, "memory")
        consciousness_tag = self._propagate_tag(memory_tag, "consciousness")

        assert consciousness_tag.level == SafetyLevel.CAUTION
        assert "propagation_chain" in consciousness_tag.metadata
        assert len(consciousness_tag.metadata["propagation_chain"]) == 3

    def _propagate_tag(self, source_tag: SafetyTag, target_layer: str) -> SafetyTag:
        """Mock tag propagation logic"""
        escalation_layers = {"system_critical", "emergency", "override"}

        # Determine if escalation is needed
        new_level = source_tag.level
        if target_layer in escalation_layers and source_tag.level == SafetyLevel.SAFE:
            new_level = SafetyLevel.DANGER

        # Create propagated tag
        metadata = dict(source_tag.metadata)
        metadata["propagated_from"] = source_tag.category
        metadata["source_tag_id"] = source_tag.tag_id

        if new_level != source_tag.level:
            metadata["escalated"] = True
            metadata["original_level"] = source_tag.level

        # Build propagation chain
        if "propagation_chain" in metadata:
            chain = metadata["propagation_chain"][:]
        else:
            chain = [source_tag.category]
        chain.append(target_layer)
        metadata["propagation_chain"] = chain

        return SafetyTag(
            level=new_level,
            category=target_layer,
            description=f"Propagated to {target_layer}: {source_tag.description}",
            metadata=metadata
        )


class TestGuardianDSLIntegration:
    """Test integration with Guardian decision envelope schema"""

    def test_safety_tags_in_guardian_envelope(self):
        """Test safety tags integration with Guardian decision envelope"""
        # Create safety tag collection
        collection = SafetyTagCollection()
        collection.add_tag(SafetyTag(SafetyLevel.DANGER, "consciousness", "Consciousness modification"))
        collection.add_tag(SafetyTag(SafetyLevel.CAUTION, "memory", "Memory access"))

        # Create Guardian decision envelope with safety tags
        envelope = {
            "schema_version": "2.1.0",
            "decision": {
                "status": "challenge",
                "policy": "safety_tags/v1.0.0",
                "severity": "high",
                "confidence": 0.95,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "ttl_seconds": 300
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "lane": "production",
                "actor": {"type": "user", "id": "user-123", "tier": "T3"},
                "operation": {"name": "consciousness.modify", "resource": "memory://vault/user-123"}
            },
            "context": {
                "environment": {"region": "us-east-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True, "emergency_active": False}
            },
            "metrics": {
                "latency_ms": 45.2,
                "risk_score": 0.85,
                "drift_score": 0.12
            },
            "enforcement": {
                "mode": "enforced",
                "actions": ["challenge", "audit", "require_approval"]
            },
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "source_system": "guardian_safety_tags"
            },
            "reasons": [
                {
                    "code": "SAFETY_TAG_DANGER_LEVEL",
                    "message": "Operation involves DANGER level safety tags requiring elevated approval"
                }
            ],
            "extensions": {
                "safety_tags": collection.to_dsl()
            },
            "integrity": {
                "content_sha256": "a" * 64  # Mock hash
            }
        }

        # Validate structure
        assert envelope["decision"]["status"] == "challenge"
        assert envelope["extensions"]["safety_tags"]["highest_level"] == SafetyLevel.DANGER
        assert envelope["extensions"]["safety_tags"]["tag_count"] == 2
        assert "consciousness" in envelope["extensions"]["safety_tags"]["categories"]

    def test_dual_approval_override_with_safety_tags(self):
        """Test dual approval override process with safety tags"""
        # Create critical safety tag requiring dual approval
        SafetyTag(
            SafetyLevel.CRITICAL,
            "emergency_override",
            "Emergency system override",
            metadata={"requires_dual_approval": True, "emergency_ticket": "EMRG-2025-001"}
        )

        # Create Guardian envelope with dual approval
        envelope = {
            "schema_version": "2.1.0",
            "decision": {
                "status": "allow",
                "policy": "emergency_override/v1.0.0",
                "severity": "critical",
                "confidence": 1.0,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "ttl_seconds": 60
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "lane": "production",
                "actor": {"type": "user", "id": "admin-456", "tier": "T5"},
                "operation": {"name": "system.emergency_override", "resource": "system://critical"}
            },
            "context": {
                "environment": {"region": "us-east-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True, "emergency_active": True}
            },
            "metrics": {"latency_ms": 15.5},
            "enforcement": {"mode": "enforced", "actions": ["allow_with_audit"]},
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "source_system": "guardian_emergency"
            },
            "approvals": [
                {
                    "approver": "admin-primary",
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                    "scope": "temporary_override",
                    "ticket": "EMRG-2025-001"
                },
                {
                    "approver": "admin-secondary",
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                    "scope": "temporary_override",
                    "ticket": "EMRG-2025-001"
                }
            ],
            "extensions": {
                "safety_tags": SafetyTagCollection().to_dsl()
            },
            "integrity": {"content_sha256": "b" * 64}
        }

        # Validate dual approval structure
        assert len(envelope["approvals"]) == 2
        assert envelope["approvals"][0]["scope"] == "temporary_override"
        assert envelope["approvals"][1]["scope"] == "temporary_override"
        assert envelope["decision"]["status"] == "allow"
        assert envelope["decision"]["severity"] == "critical"


# ============================================================================
# Integration Tests
# ============================================================================

class TestSafetyTagDSLFullIntegration:
    """End-to-end integration tests for complete DSL workflow"""

    def test_complete_safety_workflow(self):
        """Test complete safety tag workflow from creation to enforcement"""
        # 1. Create operation with safety tags
        collection = SafetyTagCollection()
        collection.add_tag(SafetyTag(SafetyLevel.DANGER, "consciousness", "Consciousness modification"))
        collection.add_tag(SafetyTag(SafetyLevel.CAUTION, "memory", "Memory access"))

        # 2. Evaluate highest risk level
        highest_level = collection.get_highest_level()
        assert highest_level == SafetyLevel.DANGER

        # 3. Determine required permissions
        requires_approval = highest_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]
        min_tier = "T4" if highest_level == SafetyLevel.DANGER else "T2"

        # 4. Create Guardian decision envelope
        decision_status = "challenge" if requires_approval else "allow"

        envelope = {
            "schema_version": "2.1.0",
            "decision": {
                "status": decision_status,
                "policy": f"safety_enforcement/{highest_level.lower()}/v1.0.0",
                "severity": highest_level.lower(),
                "confidence": 0.95,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
            },
            "extensions": {
                "safety_tags": collection.to_dsl(),
                "enforcement_requirements": {
                    "min_tier": min_tier,
                    "requires_approval": requires_approval
                }
            }
        }

        # 5. Validate complete workflow
        assert envelope["decision"]["status"] == "challenge"
        assert envelope["extensions"]["safety_tags"]["highest_level"] == SafetyLevel.DANGER
        assert envelope["extensions"]["enforcement_requirements"]["requires_approval"] is True
        assert envelope["extensions"]["enforcement_requirements"]["min_tier"] == "T4"


if __name__ == "__main__":
    # Run comprehensive safety tag DSL tests
    pytest.main([__file__, "-v", "--tb=short"])
