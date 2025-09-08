"""
Colony Demo Scripts
Moved from main modules to prevent import side-effects
"""
import streamlit as st


def run_governance_demo():
    """Run governance colony demo"""
    import asyncio

    from ..governance_colony_enhanced import GovernanceColony

    colony = GovernanceColony()

    async def demo():
        # Demo ethical decision
        decision = await colony.validate_decision(
            {
                "action": "generate_response",
                "content": "test content",
                "context": {"user_tier": "basic"},
            }
        )
        print(f"Decision validated: {decision}")

    asyncio.run(demo())


def run_reasoning_demo():
    """Run reasoning colony demo"""
    import asyncio

    from ..reasoning_colony import ReasoningColony

    colony = ReasoningColony()

    async def demo():
        result = await colony.reason({"query": "What is consciousness?", "depth": 3})
        print(f"Reasoning result: {result}")

    asyncio.run(demo())


def run_memory_demo():
    """Run memory colony demo"""
    import asyncio

    from ..memory_colony_enhanced import MemoryColony

    colony = MemoryColony()

    async def demo():
        # Store memory
        memory_id = await colony.store({"content": "Test memory", "importance": 0.8})
        print(f"Stored memory: {memory_id}")

        # Recall memory
        recalled = await colony.recall(memory_id)
        print(f"Recalled: {recalled}")

    asyncio.run(demo())


if __name__ == "__main__":
    import sys

    demos = {
        "governance": run_governance_demo,
        "reasoning": run_reasoning_demo,
        "memory": run_memory_demo,
    }

    if len(sys.argv) > 1 and sys.argv[1] in demos:
        demos[sys.argv[1]]()
    else:
        print(f"Usage: python -m core.colonies.demo {{{'|'.join(demos.keys()}")
