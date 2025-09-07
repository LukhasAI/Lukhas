"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

Memory Services API Example
"""
import asyncio

import streamlit as st
from memory_services import MemoryQuery, MemoryServicesAPI, MemoryStore


async def main():
    # Initialize API
    api = MemoryServicesAPI(storage_backend="standard")

    # Store a memory
    memory = MemoryStore(
        content="Important meeting notes",
        type="text",
        tags=["meeting", "important"],
        importance=0.9,
    )

    memory_id = await api.store(memory)
    print(f"Stored memory: {memory_id}")

    # Search memories
    query = MemoryQuery(query="meeting", limit=10)

    results = await api.retrieve(query)
    print(f"Found {len(results)} memories")


if __name__ == "__main__":
    asyncio.run(main())
