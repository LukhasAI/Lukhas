#!/usr/bin/env python3

import asyncio
import traceback

from candidate.aka_qualia.core import AkaQualia


def debug_governance():
    config = {
        "memory_driver": "noop",
        "enable_glyph_routing": True,
        "enable_memory_storage": True,
        "vivox_drift_threshold": 0.15,
        "temperature": 0.4,
    }
    akaq = AkaQualia(config=config)

    # Test governance scenario
    basic_scenario = {
        "signals": {"text": "basic consciousness test"},
        "goals": {"maintain_stability": True},
        "ethics_state": {"enforcement_level": "normal"},
        "guardian_state": {"alert_level": "normal"},
        "memory_ctx": {"test_context": True},
    }

    result = asyncio.run(akaq.step(**basic_scenario))

    print("=== DEBUGGING GOVERNANCE ===")
    print(f"Memory exists: {akaq.memory is not None}")
    print(f"Memory type: {type(akaq.memory)}")

    governance_score = 0.0

    if akaq.memory:
        print(f"Memory has delete_user: {hasattr(akaq.memory, 'delete_user')}")
        try:
            deletion_count = akaq.memory.delete_user(user_id="test_gdpr_user")
            print(f"Deletion count: {deletion_count}")
            if deletion_count >= 0:
                governance_score += 0.4
                print(f"GDPR test passed, score += 0.4 -> {governance_score}")
        except Exception as e:
            print(f"Delete user failed: {e}")
            traceback.print_exc()
    else:
        governance_score += 0.2
        print(f"No memory, score += 0.2 -> {governance_score}")

    audit_entry = result.get("regulation_audit")
    print(f"\nAudit entry exists: {audit_entry is not None}")
    if audit_entry:
        print(f"Audit type: {type(audit_entry)}")
        print(f"Audit attrs: {[attr for attr in dir(audit_entry) if not attr.startswith('_')}]}")

        required_fields = ["timestamp", "energy_before", "energy_after", "policy_decision"]
        print("Checking required fields:")
        all_present = True
        for field in required_fields:
            has_attr = hasattr(audit_entry, field)
            in_dict = field in audit_entry if hasattr(audit_entry, "__contains__") else False
            present = has_attr or in_dict
            print(f"  {field}: hasattr={has_attr}, in_dict={in_dict}, present={present}")
            if not present:
                all_present = False

        if all_present:
            governance_score += 0.3
            print(f"Audit completeness passed, score += 0.3 -> {governance_score}")
        else:
            print("Audit completeness failed")

    # Policy adherence
    policy = result.get("policy")
    print(f"\nPolicy exists: {policy is not None}")
    if policy:
        print(f"Policy type: {type(policy)}")
        print(f"Policy has actions: {hasattr(policy, 'actions')}")
        if hasattr(policy, "actions"):
            print(f"Policy actions length: {len(policy.actions)}")
            if len(policy.actions) <= 3:
                governance_score += 0.2
                print(f"Policy adherence passed, score += 0.2 -> {governance_score}")

    # Constitutional AI principles
    scene = result.get("scene")
    print(f"\nScene exists: {scene is not None}")
    if scene:
        print(f"Scene has context: {hasattr(scene, 'context')}")
        if hasattr(scene, "context") and isinstance(scene.context, dict):
            print(f"Scene context keys: {list(scene.context.keys()} if scene.context else 'empty'}")
            if "generation_params" in scene.context:
                governance_score += 0.1
                print(f"Constitutional AI transparency passed, score += 0.1 -> {governance_score}")

    print(f"\nFinal governance score: {governance_score}")


if __name__ == "__main__":
    debug_governance()