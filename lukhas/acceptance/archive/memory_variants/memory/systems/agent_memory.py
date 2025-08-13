# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: memory/core_memory/agent_memory.py
# MODULE: memory.core_memory.agent_memory
# DESCRIPTION: Manages agent-specific shared memory using JSONL files with
#              file locking for inter-process safety.
# DEPENDENCIES: json, os, asyncio, threading, fcntl, datetime, pathlib, typing, structlog
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

# Standard Library Imports
import asyncio
import fcntl  # ΛCAUTION: fcntl is Unix-specific, limiting cross-platform compatibility.
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Third-Party Imports
import structlog

# LUKHAS Core Imports
# from ..core.decorators import core_tier_required # Conceptual
# Initialize logger for this module
# ΛTRACE: Standard logger setup for AgentMemory.


# --- LUKHAS Tier System Placeholder ---
# ΛNOTE: The lukhas_tier_required decorator is a placeholder for conceptual tiering.
def lukhas_tier_required(level: int):
    def decorator(func):
        func._lukhas_tier = level
        return func

    return decorator


# ΛNOTE: `fcntl` usage makes this module Unix-specific. Consider
# alternatives or conditional imports for wider compatibility.
@lukhas_tier_required(1)  # Conceptual tier for core agent memory functionality
class AgentMemory:
    """
    Manages a shared memory space for multi-agent collaboration, persisting
    event-driven data to a JSONL file for each agent. #AIDENTITY: Each agent has its own memory file.

    Provides thread-safe and process-safe (via file locking) mechanisms
    for appending and reading memory entries.

    #ΛNOTE: Async methods currently wrap sync file I/O. For high concurrency,
    #       consider `asyncio.to_thread` (Python 3.9+) or a dedicated I/O thread pool.
    #ΛCAUTION: Performance may degrade with very large memory files due to full/partial reads.
    #           JSONL format can be sensitive to corruption if not handled carefully.
    """

    # AIDENTITY: agent_id is core to this class, defining the memory scope.
    def __init__(
        self, agent_id: str = "default_agent", memory_base_path: Optional[str] = None
    ):
        """
        Initializes AgentMemory for a specific agent.

        Args:
            agent_id: A unique identifier for the agent.
            memory_base_path: The base directory path for storing agent memory files.
                              Defaults to LUKHAS_SHARED_MEMORY_PATH or ./data/shared_memory.
        """
        self.agent_id = agent_id

        # ΛDRIFT_POINT: If LUKHAS_SHARED_MEMORY_PATH is inconsistent across environments/agents,
        # memory will be fragmented or inaccessible.
        if memory_base_path is None:
            base_dir_str = os.getenv(
                "LUKHAS_SHARED_MEMORY_PATH", "./.data/shared_memory"
            )
            base_dir = Path(base_dir_str)
            # ΛTRACE: Using shared memory path for agent memory.
            log.debug(
                "Using shared memory path for AgentMemory.",
                agent_id=self.agent_id,
                path_source="env_default",
                configured_path=str(base_dir),
            )
        else:
            base_dir = Path(memory_base_path)
            # ΛTRACE: Using provided base path for AgentMemory.
            log.debug(
                "Using provided base path for AgentMemory.",
                agent_id=self.agent_id,
                path_source="constructor_arg",
                configured_path=str(base_dir),
            )

        self.memory_path = base_dir / f"{self.agent_id}_memory.jsonl"
        self.lock = (
            threading.RLock()
        )  # Thread-safety for internal methods if called directly or via executor

        self._ensure_memory_file()
        # ΛTRACE: AgentMemory initialized.
        log.info(
            "AgentMemory initialized.",
            agent_id=self.agent_id,
            memory_file_location=str(self.memory_path),
        )

    def _ensure_memory_file(self) -> None:
        """Ensures the memory file and its parent directory exist."""
        # ΛTRACE: Ensuring memory file and directory exist.
        log.debug(
            "Ensuring memory file exists.",
            agent_id=self.agent_id,
            path=str(self.memory_path),
        )
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.memory_path.exists():
                self.memory_path.touch()
                # ΛTRACE: Created new agent memory file.
                log.info(
                    "Created agent memory file.",
                    agent_id=self.agent_id,
                    path=str(self.memory_path),
                )
        except OSError as e:
            # ΛTRACE: Error ensuring memory file/directory.
            log.error(
                "Failed to ensure memory file/directory.",
                agent_id=self.agent_id,
                target_path=str(self.memory_path.parent),
                error_message=str(e),
                exc_info=True,
            )
            raise

    # ΛSEED_CHAIN: Appended data (event_type, data payload) becomes a seed for this agent or others.
    # AIDENTITY: Memory is associated with self.agent_id.
    @lukhas_tier_required(1)
    async def append_memory(self, event_type: str, data: dict[str, Any]) -> bool:
        """
        Appends an event entry to this agent's shared memory.
        Async interface to a synchronous file operation. Consider `asyncio.to_thread`.
        """
        # ΛTRACE: Attempting to append memory for agent.
        log.debug(
            "Attempting to append memory.",
            for_agent_id=self.agent_id,
            event_category=event_type,
            data_keys=list(data.keys()),
        )
        try:
            # ΛNOTE: Using run_in_executor for sync I/O in async context.
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None, self._append_memory_internal, self.agent_id, event_type, data
            )
        except Exception as e:
            # ΛTRACE: Error in async wrapper for append_memory.
            log.error(
                "Error during async wrapper for append_memory.",
                agent_id=self.agent_id,
                event_type=event_type,
                error=str(e),
                exc_info=True,
            )
            return False

    def _append_memory_internal(
        self, agent_id: str, event_type: str, data: dict[str, Any]
    ) -> bool:
        """Internal synchronous method to append an entry to the shared memory file."""
        # ΛTRACE: Internal sync append operation started.
        log.debug(
            "Starting internal sync append.",
            for_agent_id=agent_id,
            event_category=event_type,
        )
        try:
            with self.lock:  # Thread-level lock
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent_id": agent_id,  # AIDENTITY
                    "event_type": event_type,
                    "data": data,  # ΛSEED_CHAIN: This data is the seed.
                }

                # ΛCAUTION: File operations are synchronous and use fcntl
                # (Unix-specific).
                with open(self.memory_path, "a", encoding="utf-8") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Process-level lock
                    try:
                        json.dump(entry, f)
                        f.write("\n")
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                # ΛTRACE: Memory entry appended successfully (sync internal).
                log.debug(
                    "Memory entry appended successfully (sync internal).",
                    by_agent_id=agent_id,
                    event_category=event_type,
                    file_path=str(self.memory_path),
                )
                return True
        except Exception as e:
            # ΛTRACE: Error during internal sync append operation.
            log.error(
                "Failed to append to shared memory (sync internal).",
                for_agent_id=agent_id,
                file_path=str(self.memory_path),
                error_message=str(e),
                exc_info=True,
            )
            return False

    # ΛRECALL: Core method for reading/recalling agent memories.
    # AIDENTITY: Filters by agent_id.
    @lukhas_tier_required(1)
    async def read_memory(
        self,
        key_filter: Optional[
            str
        ] = None,  # ΛNOTE: key_filter seems unused, event_type_filter is used instead.
        agent_filter: Optional[str] = None,
        event_type_filter: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Reads entries from shared memory, defaulting to this agent's memories if agent_filter is None.
        Async interface to a synchronous file operation. Consider `asyncio.to_thread`.
        """
        effective_event_type_filter = (
            event_type_filter or key_filter
        )  # Uses key_filter as fallback for event_type_filter
        effective_agent_filter = (
            agent_filter if agent_filter is not None else self.agent_id
        )  # Defaults to current agent's memory

        # ΛTRACE: Attempting to read memory for agent.
        log.debug(
            "Attempting to read memory.",
            for_agent_filter=effective_agent_filter,
            for_event_filter=effective_event_type_filter,
            result_limit=limit,
        )
        try:
            # ΛNOTE: Using run_in_executor for sync I/O in async context.
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None,
                self._read_memory_internal,
                effective_agent_filter,
                effective_event_type_filter,
                limit,
            )
        except Exception as e:
            # ΛTRACE: Error in async wrapper for read_memory.
            log.error(
                "Error during async wrapper for read_memory.",
                agent_filter=effective_agent_filter,
                event_filter=effective_event_type_filter,
                error=str(e),
                exc_info=True,
            )
            return []

    def _read_memory_internal(
        self,
        agent_filter: Optional[str] = None,  # AIDENTITY
        event_type_filter: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Internal synchronous method to read entries from the shared memory file."""
        # ΛTRACE: Internal sync read operation started.
        log.debug(
            "Starting internal sync read.",
            for_agent_filter=agent_filter,
            for_event_filter=event_type_filter,
        )
        try:
            with self.lock:  # Thread-level lock
                if not self.memory_path.exists():
                    # ΛTRACE: Memory file does not exist for reading.
                    log.debug(
                        "Memory file does not exist for reading.",
                        agent_filter=agent_filter,
                        target_path=str(self.memory_path),
                    )
                    return []

                entries: list[dict[str, Any]] = []
                # ΛCAUTION: Reads all lines then reverses; could be memory intensive for
                # large files.
                with open(self.memory_path, encoding="utf-8") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Process-level lock
                    try:
                        raw_lines = f.readlines()
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                for line in reversed(raw_lines):  # Process newest first
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line.strip())
                        # AIDENTITY: Filtering by agent_id.
                        if agent_filter and entry.get("agent_id") != agent_filter:
                            continue
                        if (
                            event_type_filter
                            and entry.get("event_type") != event_type_filter
                        ):
                            continue
                        entries.append(entry)
                        if len(entries) >= limit:
                            break
                    except json.JSONDecodeError:
                        # ΛCAUTION: Potential data loss if lines are malformed.
                        # ΛTRACE: Malformed JSON line skipped during read.
                        log.warning(
                            "Skipping malformed JSON line in memory file.",
                            file_path=str(self.memory_path),
                            line_preview=line[:100],
                        )
                        continue

                # ΛTRACE: Memory read operation complete (sync internal).
                log.debug(
                    "Memory read operation complete (sync internal).",
                    entries_found=len(entries),
                    for_agent_filter=agent_filter,
                    for_event_filter=event_type_filter,
                    file_path=str(self.memory_path),
                )
                return entries

        except Exception as e:
            # ΛTRACE: Error during internal sync read operation.
            log.error(
                "Failed to read from shared memory (sync internal).",
                file_path=str(self.memory_path),
                agent_filter=agent_filter,
                error_message=str(e),
                exc_info=True,
            )
            return []

    # ΛRECALL: Specific recall for "insight_discovered" events.
    # AIDENTITY: Retrieves insights for a specific agent_id.
    @lukhas_tier_required(1)
    async def get_agent_insights(
        self, agent_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Retrieves 'insight_discovered' entries for a given agent."""
        # ΛTRACE: Fetching agent insights.
        log.debug("Fetching agent insights.", for_agent_id=agent_id, result_limit=limit)
        return await self.read_memory(
            agent_filter=agent_id, event_type_filter="insight_discovered", limit=limit
        )

    # ΛRECALL: Recalls recent activities for the current agent.
    # AIDENTITY: Operates on the current agent's (self.agent_id) memory.
    @lukhas_tier_required(1)
    async def get_recent_activities(
        self, minutes: int = 60, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Retrieves all activities for the current agent from the last N minutes."""
        # ΛTRACE: Fetching recent activities for current agent.
        log.debug(
            "Fetching recent activities.",
            for_agent_id=self.agent_id,
            minutes_span=minutes,
            result_limit=limit,
        )

        # ΛCAUTION: Heuristic `limit * 5` might still not be enough for sparse
        # activities over long periods.
        candidate_entries = await self.read_memory(limit=limit * 5)

        cutoff_timestamp = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        recent_filtered_entries: list[dict[str, Any]] = []

        for entry in candidate_entries:
            try:
                entry_timestamp_str = entry["timestamp"]
                entry_timestamp_obj = datetime.fromisoformat(entry_timestamp_str)
                if entry_timestamp_obj.tzinfo is None:  # Ensure TZ aware for comparison
                    entry_timestamp_obj = entry_timestamp_obj.replace(
                        tzinfo=timezone.utc
                    )

                if entry_timestamp_obj.timestamp() >= cutoff_timestamp:
                    recent_filtered_entries.append(entry)
                if len(recent_filtered_entries) >= limit:
                    break
            except (
                ValueError,
                KeyError,
                TypeError,
            ) as e:  # Added TypeError for fromisoformat
                # ΛTRACE: Warning: Skipping entry with invalid timestamp during recent
                # activity filtering.
                log.warning(
                    "Skipping entry with invalid timestamp during recent activity filtering.",
                    agent_id=self.agent_id,
                    entry_data_preview=str(entry)[:100],
                    error_details=str(e),
                )
                continue

        # ΛTRACE: Recent activities retrieval complete.
        log.debug(
            "Recent activities retrieval complete.",
            for_agent_id=self.agent_id,
            count=len(recent_filtered_entries),
        )
        return recent_filtered_entries


# --- Global Instance and Convenience Functions ---
# ΛNOTE: Manages a global default AgentMemory instance. This could be a #ΛDRIFT_POINT if not handled carefully
# in complex multi-threaded/processed scenarios, despite the internal lock
# in AgentMemory.
_shared_memory_instance: Optional[AgentMemory] = None
_global_memory_lock = threading.Lock()  # Lock for managing the global instance itself


# AIDENTITY: `get_shared_memory` is key for obtaining agent-specific or
# global memory access.
def get_shared_memory(
    agent_id: str = "global_default", base_path: Optional[str] = None
) -> AgentMemory:
    """Retrieves or creates a shared memory instance. Manages a global default."""
    global _shared_memory_instance
    # ΛTRACE: get_shared_memory called.
    log.debug(
        "get_shared_memory called.",
        requested_agent_id=agent_id,
        has_global_instance=(_shared_memory_instance is not None),
    )
    if agent_id == "global_default" and _shared_memory_instance:
        return _shared_memory_instance

    with _global_memory_lock:  # Protects creation of _shared_memory_instance
        if agent_id == "global_default":
            if _shared_memory_instance is None:
                # ΛTRACE: Initializing default global shared memory instance.
                log.info(
                    "Initializing default global shared memory instance.",
                    base_path=base_path,
                )
                _shared_memory_instance = AgentMemory(
                    agent_id=agent_id, memory_base_path=base_path
                )
            return _shared_memory_instance
        else:
            # ΛTRACE: Providing new AgentMemory instance for specific agent.
            log.info(
                f"Providing AgentMemory instance for specific agent: {agent_id}",
                base_path=base_path,
            )
            return AgentMemory(agent_id=agent_id, memory_base_path=base_path)


# ΛSEED_CHAIN: Convenience function to append data that can act as a seed.
# AIDENTITY: Operates on a specific agent's memory.
async def append_to_shared_memory(
    agent_id: str,
    event_type: str,
    data: dict[str, Any],
    base_path: Optional[str] = None,
) -> bool:
    """Convenience async function to append to shared memory for a specific agent."""
    # ΛTRACE: Convenience function append_to_shared_memory called.
    log.debug(
        "append_to_shared_memory called.", for_agent_id=agent_id, event_type=event_type
    )
    memory = get_shared_memory(agent_id, base_path=base_path)
    return await memory.append_memory(event_type, data)


# ΛRECALL: Convenience function to read/recall from agent memory.
# AIDENTITY: Can filter by agent_id or default to a global agent.
async def read_from_shared_memory(
    agent_filter: Optional[str] = None,
    event_type_filter: Optional[str] = None,
    limit: int = 100,
    base_path: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Convenience async function to read from shared memory."""
    agent_to_query = agent_filter if agent_filter is not None else "global_default"
    # ΛTRACE: Convenience function read_from_shared_memory called.
    log.debug(
        "read_from_shared_memory called.",
        agent_to_query=agent_to_query,
        event_filter=event_type_filter,
    )
    memory = get_shared_memory(agent_to_query, base_path=base_path)
    # ΛNOTE: The agent_filter passed to memory.read_memory will be agent_to_query.
    # If agent_filter was None originally, it defaults to "global_default", meaning it reads global_default's own memory.
    # Reading "all agents" would require a different mechanism or iteration.
    return await memory.read_memory(
        agent_filter=agent_to_query, event_type_filter=event_type_filter, limit=limit
    )


# ΛNOTE: Example usage demonstrating core functionalities.
# ΛEXPOSE: This main_example could be run as a CLI test or demo.
async def main_example():
    """Example usage of the AgentMemory system."""
    if not structlog.is_configured():
        structlog.configure(
            processors=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.dev.ConsoleRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    # ΛTRACE: Starting AgentMemory main_example.
    log.info("🧠 Testing LUKHAS Shared Memory System (Async Example)")

    agent1_id = "ΛResearchAgent_Test"  # AIDENTITY
    agent2_id = "ΛValidationAgent_Test"  # AIDENTITY

    # ΛSEED_CHAIN: Appending task completion data for agent1.
    success1 = await append_to_shared_memory(
        agent1_id,
        "task_completed",
        {
            "task": "quantum_gravity_simulation",
            "status": "converged",
            "insights": [
                "Found potential unification variable.",
                "Simulation matches Hawking radiation prediction.",
            ],
        },
    )
    log.info("Agent 1 append status", success=success1, agent_id=agent1_id)

    # ΛSEED_CHAIN: Appending insight data for agent2.
    success2 = await append_to_shared_memory(
        agent2_id,
        "insight_discovered",
        {
            "insight": "Observed anomaly in cosmic microwave background.",
            "confidence": 0.92,
            "related_simulation": "quantum_gravity_simulation",
        },
    )
    log.info("Agent 2 append status", success=success2, agent_id=agent2_id)

    # ΛRECALL: Reading entries for agent1.
    agent1_entries = await read_from_shared_memory(agent_filter=agent1_id, limit=5)
    log.info(
        f"Found {len(agent1_entries)} entries for {agent1_id}",
        entries_data_preview=[str(e)[:100] for e in agent1_entries],
        agent_id=agent1_id,
    )

    # ΛRECALL: Getting insights for agent2.
    agent2_mem_instance = get_shared_memory(agent_id=agent2_id)
    agent2_insights = await agent2_mem_instance.get_agent_insights(
        agent_id=agent2_id, limit=5
    )
    log.info(
        f"Found {len(agent2_insights)} insights for {agent2_id}",
        insights_data_preview=[str(i)[:100] for i in agent2_insights],
        agent_id=agent2_id,
    )

    # ΛRECALL: Getting recent activities for agent1.
    agent1_mem_instance = get_shared_memory(agent_id=agent1_id)
    recent_agent1 = await agent1_mem_instance.get_recent_activities(minutes=5, limit=10)
    log.info(
        f"Found {len(recent_agent1)} recent activities for {agent1_id}",
        activities_data_preview=[str(a)[:100] for a in recent_agent1],
        agent_id=agent1_id,
    )

    # ΛNOTE: Cleanup instructions for test files.
    # default_base = Path(os.getenv("LUKHAS_SHARED_MEMORY_PATH", "./.data/shared_memory"))
    # Path(default_base / f"{agent1_id}_memory.jsonl").unlink(missing_ok=True)
    # Path(default_base / f"{agent2_id}_memory.jsonl").unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main_example())

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: memory/core_memory/agent_memory.py
# VERSION: 1.2.0 # Updated version
# TIER SYSTEM: Tier 1 (Core Agent Functionality, conceptual via @lukhas_tier_required)
# ΛTRACE INTEGRATION: ENABLED (via structlog)
# CAPABILITIES: Manages agent-specific, event-driven shared memory persisted to
#               JSONL files. Provides thread-safe and process-safe (Unix-like)
#               mechanisms for appending and reading memory entries.
# FUNCTIONS: get_shared_memory, append_to_shared_memory, read_from_shared_memory, main_example (async)
# CLASSES: AgentMemory
# DECORATORS: @lukhas_tier_required (conceptual)
# DEPENDENCIES: json, os, asyncio, threading, fcntl, datetime, pathlib, typing, structlog
# INTERFACES: AgentMemory class methods, and convenience functions for shared memory access.
# ERROR HANDLING: Logs errors for file operations, JSON parsing, and async wrappers.
#                 Uses file locking (fcntl) for process safety.
# LOGGING: ΛTRACE_ENABLED (uses structlog for debug, info, warning, error messages).
# AUTHENTICATION: Identity managed via `agent_id`. Tiering is conceptual.
# HOW TO USE:
#   memory = AgentMemory(agent_id="my_agent")
#   await memory.append_memory("event_type", {"key": "value"})
#   entries = await memory.read_memory(event_type_filter="event_type")
#   Or use convenience functions:
#   await append_to_shared_memory("my_agent", "event_type", {"key": "value"})
#   entries = await read_from_shared_memory(agent_filter="my_agent")
# INTEGRATION NOTES: `fcntl` makes it Unix-specific. Async methods wrap sync I/O.
#   Default memory path is configurable via LUKHAS_SHARED_MEMORY_PATH env var.
# MAINTENANCE: Consider `asyncio.to_thread` for I/O. Add platform checks or
#              alternatives for `fcntl` if Windows compatibility is needed.
#              Implement strategies for managing large memory files if they grow indefinitely.
# CONTACT: LUKHAS DEVELOPMENT TEAM (dev@lukhas.ai)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
