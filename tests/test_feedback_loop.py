#!/usr/bin/env python3
"""
Test the Symbolic Feedback Loop
"""

import asyncio
from cognition.symbolic_feedback_loop import test_feedback_loop_stability

async def main():
    """Run feedback loop tests"""
    result = await test_feedback_loop_stability()
    return result

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(main())
    exit(0 if success else 1)