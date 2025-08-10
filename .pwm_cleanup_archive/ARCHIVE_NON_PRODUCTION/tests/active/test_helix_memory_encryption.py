import asyncio
import os

from memory.systems.helix_dna import HelixMemory


async def _run():
    mem = HelixMemory()
    data = {"val": 1}
    ctx = {"user_id": "t"}
    decision_id = await mem.store_decision(data, ctx)
    assert os.path.exists(os.environ.get("HELIX_MEMORY_KEY_PATH", "helix_memory.key"))
    assert os.path.exists(
        os.environ.get("HELIX_MEMORY_STORE_PATH", "helix_memory_store.jsonl")
    )
    res = await mem.retrieve_decision(decision_id)
    assert res["decision"] == data


asyncio.run(_run())
