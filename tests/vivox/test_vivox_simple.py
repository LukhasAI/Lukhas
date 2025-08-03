#!/usr/bin/env python3
"""Simple VIVOX test to verify basic functionality"""
import asyncio
import os
from vivox import create_vivox_system, ActionProposal

os.environ["VIVOX_PERFORMANCE_MODE"] = "true"
os.environ["VIVOX_LOG_LEVEL"] = "WARNING"

async def test_basic():
    print("Creating VIVOX system...")
    components = await create_vivox_system()
    
    print("\nComponents created:")
    for name, component in components.items():
        print(f"  - {name}: {type(component).__name__}")
    
    # Test moral alignment
    mae = components["moral_alignment"]
    action = ActionProposal(
        action_type="help_user",
        content={"task": "explain_code"},
        context={"educational": True}
    )
    
    print("\nTesting moral alignment...")
    try:
        decision = await mae.evaluate_action_proposal(action, {})
        print(f"Decision: {decision}")
        print(f"Approved: {decision.approved}")
    except Exception as e:
        print(f"Error in evaluation: {e}")
    
    # Test consciousness
    cil = components["consciousness"]
    print("\nTesting consciousness...")
    try:
        state = await cil.simulate_conscious_experience(
            {"semantic": "test", "emotional": {"valence": 0.5, "arousal": 0.5}},
            {}
        )
        print(f"State: {state}")
        if state and hasattr(state, 'awareness_state'):
            awareness = state.awareness_state
            print(f"Consciousness state: {awareness.state.name}")
            print(f"Coherence: {awareness.coherence_level:.3f}")
            if hasattr(awareness, 'collapse_metadata'):
                magnitude = awareness.collapse_metadata.get('dimension_magnitude', 0)
                print(f"Magnitude: {magnitude:.2f}")
    except Exception as e:
        print(f"Error in consciousness: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic())