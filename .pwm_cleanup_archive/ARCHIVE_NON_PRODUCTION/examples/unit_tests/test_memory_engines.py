import asyncio
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from memory.core_memory.adaptive_memory_engine import AdaptiveMemoryEngine
from memory.core_memory.dream_memory_manager import DreamMemoryManager


def test_adaptive_memory_engine_basic():
    engine = AdaptiveMemoryEngine()
    assert asyncio.run(engine.initialize())
    result = asyncio.run(engine.process({"sample": True}))
    assert result["status"] == "success"
    asyncio.run(engine.shutdown())
    assert engine.active is False


def test_dream_memory_manager_basic():
    manager = DreamMemoryManager()
    assert asyncio.run(manager.initialize())
    result = asyncio.run(manager.process({"sample": True}))
    assert result["status"] == "success"
    asyncio.run(manager.shutdown())
    assert manager.active is False
