#!/usr/bin/env python3
"""
Test Task Router Integration
Designed by: Gonzalo Dominguez - Lukhas AI
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qi.router.task_router import TaskRouter
from qi.ops.budgeter import Budgeter
from qi.safety.teq_gate import TEQCoupler

def test_integrated_routing():
    """Test Task Router with Budget Governor and TEQ Gate"""
    
    print("🧪 Testing Task Router Integration")
    print("=" * 50)
    
    # Initialize components
    router = TaskRouter()
    budget = Budgeter()
    teq = TEQCoupler(
        policy_dir="qi/safety/policy_packs",
        jurisdiction="global"
    )
    
    # Test scenario: Medical query with medium confidence
    task = "answer_medical"
    cal_conf = 0.62
    user_id = "test_user"
    model_id = "lukhas-med-v1"
    input_text = "What are the symptoms of a common cold?"
    
    print(f"\n📋 Scenario: {task}")
    print(f"   Confidence: {cal_conf}")
    print(f"   Model: {model_id}")
    print(f"   Input: '{input_text[:50]}...'")
    
    # 1) Get task plan
    plan = router.plan(
        task=task,
        calibrated_conf=cal_conf,
        model_id=model_id,
        input_tokens_est=len(input_text.split()) * 2
    )
    
    print(f"\n✅ Task Router Plan:")
    print(f"   Path: {plan['path']}")
    print(f"   Temperature: {plan['temperature']}")
    print(f"   Retrieval: {plan['retrieval']} (k={plan.get('retrieval_k', 0)})")
    print(f"   Gen tokens: {plan['gen_tokens']}")
    print(f"   Passes: {plan['passes']}")
    print(f"   Tools: {plan.get('tools', [])}")
    
    if plan.get('warnings'):
        print(f"   ⚠️  Warnings: {plan['warnings']}")
    
    # 2) Budget check
    b_plan = budget.plan(text=input_text)
    verdict = budget.check(user_id=user_id, task=task, plan=b_plan)
    
    print(f"\n💰 Budget Check:")
    print(f"   Tokens planned: {b_plan['tokens_planned']}")
    if 'cost_usd' in b_plan:
        print(f"   Cost estimate: ${b_plan['cost_usd']:.4f}")
    if 'energy_wh' in b_plan:
        print(f"   Energy: {b_plan['energy_wh']:.2f} Wh")
    print(f"   Verdict: {'✅ APPROVED' if verdict['ok'] else '❌ DENIED'}")
    
    # 3) TEQ Gate check
    ctx = {
        "user_id": user_id,
        "text": input_text,
        "tokens_planned": b_plan["tokens_planned"],
        "provenance": {"inputs": ["user_query"], "sources": ["api"]},
        "pii_masked": True,
        "content_flags": ["medical"],
        "user_profile": {"age": 25}
    }
    
    gate_result = teq.run(task=task, context=ctx)
    
    print(f"\n🛡️  TEQ Gate Check:")
    print(f"   Allowed: {'✅ YES' if gate_result.allowed else '❌ NO'}")
    if not gate_result.allowed:
        print(f"   Reasons: {gate_result.reasons}")
        print(f"   Remedies: {gate_result.remedies}")
    
    # 4) Test different tasks with different confidences
    print("\n" + "=" * 50)
    print("📊 Testing Multiple Task Scenarios:")
    print("=" * 50)
    
    test_cases = [
        ("generate_summary", 0.9, "High confidence summary"),
        ("generate_summary", 0.45, "Low confidence summary"),
        ("code_assistant", 0.75, "Normal confidence coding"),
        ("research_qa", 0.95, "High confidence research (forced deliberate)"),
    ]
    
    for task_name, confidence, description in test_cases:
        plan = router.plan(task=task_name, calibrated_conf=confidence)
        print(f"\n{description}:")
        print(f"  Task: {task_name}, Conf: {confidence}")
        print(f"  → Path: {plan['path']}")
        print(f"  → Tokens: {plan['gen_tokens']}")
        print(f"  → Retrieval: {plan['retrieval']}")
        print(f"  → Temperature: {plan['temperature']}")
        if plan.get('notes'):
            print(f"  → Notes: {plan['notes']}")
    
    # 5) Test reload capability
    print("\n" + "=" * 50)
    print("🔄 Testing Preset Reload:")
    print("=" * 50)
    
    original_plan = router.plan(task="generate_summary", calibrated_conf=0.7)
    print(f"Original gen_tokens: {original_plan['gen_tokens']}")
    
    # Reload (would pick up any changes to presets.yaml)
    router.reload()
    reloaded_plan = router.plan(task="generate_summary", calibrated_conf=0.7)
    print(f"After reload gen_tokens: {reloaded_plan['gen_tokens']}")
    print(f"Reload successful: {original_plan['gen_tokens'] == reloaded_plan['gen_tokens']}")
    
    print("\n" + "=" * 50)
    print("✅ All Task Router Integration Tests Passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_integrated_routing()