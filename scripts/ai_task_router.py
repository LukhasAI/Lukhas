#!/usr/bin/env python3
"""
LUKHAS AI Task Router
====================

Unified task routing daemon that:
1. Dequeues tasks from Redis priority queue (blocking BZPOPMIN)
2. Routes tasks to appropriate AI agents (Jules/Codex/Gemini/Ollama)
3. Executes tasks and handles responses
4. Logs all operations for observability

This is the core orchestration service that makes LUKHAS AI-driven automation
work end-to-end: Webhooks → Redis → Router → AI Agents → Execution

Architecture:
- Event-driven (no polling, pure Redis BZPOPMIN blocking)
- Priority-aware (CRITICAL tasks execute first)
- Multi-agent (routes to Jules, Codex, Gemini, Ollama based on task.agent)
- Resilient (graceful shutdown, error handling, retries)

Usage:
    # Run as daemon
    python3 scripts/ai_task_router.py --daemon

    # Run with verbose logging
    python3 scripts/ai_task_router.py --log-level DEBUG

    # Run with custom Redis URL
    python3 scripts/ai_task_router.py --redis-url redis://prod:6379
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.queue.redis_queue import RedisTaskQueue, Task, TaskPriority, TaskType
from bridge.llm_wrappers.jules_wrapper import JulesClient
from bridge.llm_wrappers.codex_wrapper import CodexClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/ai_task_router.log")
    ]
)
logger = logging.getLogger(__name__)


class AITaskRouter:
    """
    Unified AI task router for LUKHAS orchestration.

    Routes tasks from Redis queue to appropriate AI agents:
    - jules: Google Jules for complex coding tasks
    - codex: OpenAI Codex for code generation/fixes
    - gemini: Google Gemini for multi-modal tasks
    - ollama: Local Ollama for fast semantic analysis
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize task router."""
        self.redis_url = redis_url
        self.running = False
        self.task_count = 0
        self.error_count = 0
        self.start_time: Optional[datetime] = None

        # AI clients (initialized on demand)
        self._jules_client: Optional[JulesClient] = None
        self._codex_client: Optional[CodexClient] = None

    async def start(self):
        """Start the task router daemon."""
        self.running = True
        self.start_time = datetime.utcnow()

        logger.info("🚀 Starting LUKHAS AI Task Router")
        logger.info(f"📡 Redis: {self.redis_url}")
        logger.info("⚡ Waiting for tasks...")

        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )

        # Main event loop
        try:
            await self._run_event_loop()
        except Exception as e:
            logger.error(f"Fatal error in event loop: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()

    async def _run_event_loop(self):
        """Main event loop: dequeue tasks and route to agents."""
        async with RedisTaskQueue(self.redis_url) as queue:
            while self.running:
                try:
                    # Blocking dequeue with 5-second timeout for graceful shutdown
                    task = await queue.dequeue(timeout=5)

                    if not task:
                        # Timeout - check if still running and continue
                        continue

                    # Route and execute task
                    logger.info(
                        f"📥 Received task {task.task_id[:8]}... "
                        f"(priority={task.priority.name}, agent={task.agent})"
                    )

                    await self._route_task(task)
                    self.task_count += 1

                except Exception as e:
                    logger.error(f"Error processing task: {e}", exc_info=True)
                    self.error_count += 1

                    # Brief pause on error to prevent tight error loops
                    await asyncio.sleep(1)

    async def _route_task(self, task: Task):
        """
        Route task to appropriate AI agent.

        Args:
            task: Task to execute
        """
        agent_lower = task.agent.lower()

        try:
            if agent_lower == "jules":
                await self._handle_jules_task(task)
            elif agent_lower == "codex":
                await self._handle_codex_task(task)
            elif agent_lower == "gemini":
                await self._handle_gemini_task(task)
            elif agent_lower == "ollama":
                await self._handle_ollama_task(task)
            else:
                logger.warning(f"Unknown agent '{task.agent}' - skipping task")

        except Exception as e:
            logger.error(
                f"Error executing task {task.task_id[:8]}... with {task.agent}: {e}",
                exc_info=True
            )
            raise

    async def _handle_jules_task(self, task: Task):
        """
        Handle task with Jules agent.

        Creates Jules session with auto-PR mode if PR number provided.
        """
        logger.info(f"🤖 Routing to Jules: {task.prompt[:100]}...")

        # Initialize Jules client if needed
        if not self._jules_client:
            self._jules_client = JulesClient()

        async with self._jules_client as jules:
            # Determine automation mode based on task priority
            automation_mode = "AUTO_CREATE_PR" if task.pr_number else None

            # Get source_id from context or use default
            source_id = task.context.get("source_id", "sources/github/LukhasAI/Lukhas")

            # Create Jules session
            session = await jules.create_session(
                prompt=task.prompt,
                source_id=source_id,
                automation_mode=automation_mode
            )

            logger.info(
                f"✅ Jules session created: {session.get('name', 'unknown')}"
            )

            # If PR number provided, add comment linking to Jules session
            if task.pr_number and session.get("name"):
                session_url = f"https://jules.app/{session['name']}"
                logger.info(f"🔗 Jules session: {session_url}")

    async def _handle_codex_task(self, task: Task):
        """
        Handle task with Codex agent.

        Routes to appropriate Codex method based on task type.
        """
        logger.info(f"🤖 Routing to Codex: {task.prompt[:100]}...")

        # Initialize Codex client if needed
        if not self._codex_client:
            self._codex_client = CodexClient()

        async with self._codex_client as codex:
            # Route based on task type
            if task.task_type == TaskType.BUG_FIX:
                # Extract code and error from context
                code = task.context.get("code", "")
                error = task.context.get("error", task.prompt)

                response = await codex.fix_code(code=code, error=error)

            elif task.task_type == TaskType.REFACTORING:
                code = task.context.get("code", "")
                response = await codex.refactor(code=code, instructions=task.prompt)

            elif task.task_type == TaskType.DOCUMENTATION:
                code = task.context.get("code", "")
                style = task.context.get("style", "google")
                response = await codex.document(code=code, style=style)

            else:
                # Default: code generation
                response = await codex.complete(prompt=task.prompt)

            logger.info(
                f"✅ Codex completed ({response.tokens_used} tokens): "
                f"{response.content[:100]}..."
            )

    async def _handle_gemini_task(self, task: Task):
        """
        Handle task with Gemini agent.

        TODO: Implement Gemini wrapper and integration.
        """
        logger.warning(f"⚠️ Gemini agent not yet implemented - task skipped")

    async def _handle_ollama_task(self, task: Task):
        """
        Handle task with Ollama agent.

        Used for fast local semantic analysis (architectural linting).
        TODO: Implement Ollama wrapper and integration.
        """
        logger.warning(f"⚠️ Ollama agent not yet implemented - task skipped")

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("🛑 Shutting down AI Task Router...")
        self.running = False

    async def cleanup(self):
        """Cleanup resources."""
        uptime = datetime.utcnow() - self.start_time if self.start_time else None

        logger.info("📊 Task Router Statistics:")
        logger.info(f"  - Tasks processed: {self.task_count}")
        logger.info(f"  - Errors: {self.error_count}")
        if uptime:
            logger.info(f"  - Uptime: {uptime}")

        # Close AI clients
        if self._jules_client:
            logger.debug("Closing Jules client...")

        if self._codex_client:
            logger.debug("Closing Codex client...")

        logger.info("✅ Cleanup complete")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AI Task Router")
    parser.add_argument(
        "--redis-url",
        default="redis://localhost:6379",
        help="Redis connection URL"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (requires daemonize package)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Create logs directory if needed
    Path("logs").mkdir(exist_ok=True)

    # Daemon mode
    if args.daemon:
        try:
            import daemon
            import daemon.pidfile

            pid_file = "/var/run/lukhas_task_router.pid"

            with daemon.DaemonContext(
                pidfile=daemon.pidfile.PIDLockFile(pid_file),
                working_directory=Path.cwd(),
            ):
                router = AITaskRouter(redis_url=args.redis_url)
                await router.start()

        except ImportError:
            logger.error(
                "Daemon mode requires 'python-daemon' package: "
                "pip install python-daemon"
            )
            sys.exit(1)
    else:
        # Run in foreground
        router = AITaskRouter(redis_url=args.redis_url)
        await router.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
