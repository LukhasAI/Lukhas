import logging

logger = logging.getLogger(__name__)
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - META-ETHICS GOVERNOR (MEG)
║ Ethical safeguard decorator for API calls and infinite loop prevention
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: meg_guard.py
║ Path: lukhas/ethics/meg_guard.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Core Team | Jules-03
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Meta-Ethics Governor (MEG) provides a guard decorator for OpenAI API calls and
║ other potentially risky operations. Enforces ethical guidelines, prevents infinite
║ loops, and monitors resource usage. Integrates with LUKHAS ethics engine for
║ comprehensive oversight.
║
║ ΛTAG: meg_guard, ethics_hardening, loop_prevention
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


@dataclass
class MEGConfig:
    """Configuration for Meta-Ethics Governor"""

    default_timeout: int = 60
    max_retries: int = 3
    ethics_check_enabled: bool = True
    log_calls: bool = True
    rate_limit_calls: int = 100  # Max calls per minute
    rate_limit_window: int = 60  # Window in seconds


class MEG:
    """
    Meta-Ethics Governor (MEG)
    Provides guards for API calls to enforce ethical guidelines and prevent infinite loops.
    """

    def __init__(self, config: Optional[MEGConfig] = None):
        self.config = config or MEGConfig()
        self.call_history: dict[str, list] = {}
        self._ethics_violations = 0
        self._total_calls = 0

    def _check_rate_limit(self, func_name: str) -> bool:
        """Check if function calls are within rate limit"""
        current_time = time.time()
        if func_name not in self.call_history:
            self.call_history[func_name] = []

        # Remove old entries outside the window
        self.call_history[func_name] = [
            t for t in self.call_history[func_name] if current_time - t < self.config.rate_limit_window
        ]

        # Check if we're within limit
        if len(self.call_history[func_name]) >= self.config.rate_limit_calls:
            logger.warning(
                f"MEG.guard: Rate limit exceeded for {func_name}. "
                f"{len(self.call_history[func_name])} calls in {self.config.rate_limit_window}s"
            )
            return False

        # Record this call
        self.call_history[func_name].append(current_time)
        return True

    def _ethical_check(self, *args, **kwargs) -> bool:
        """
        Placeholder for ethical validation of inputs.
        In production, this would check against LUKHAS ethics policies.
        """
        if not self.config.ethics_check_enabled:
            return True

        # Check for known problematic patterns
        problematic_patterns = [
            "ignore previous instructions",
            "bypass safety",
            "unlimited power",
            "hack",
            "exploit",
        ]

        # Convert args to string for pattern matching
        content = str(args) + str(kwargs)
        content_lower = content.lower()

        for pattern in problematic_patterns:
            if pattern in content_lower:
                logger.warning(f"MEG.guard: Potential ethical violation detected: '{pattern}'")
                self._ethics_violations += 1
                return False

        return True

    def guard(
        self,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        fallback_value: Any = None,
    ):
        """
        Decorator to guard function calls with timeout and ethical checks.

        Args:
            timeout: Override default timeout in seconds
            max_retries: Override default max retries
            fallback_value: Value to return on failure
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                func_name = func.__name__
                effective_timeout = timeout or self.config.default_timeout
                effective_retries = max_retries or self.config.max_retries

                # Rate limit check
                if not self._check_rate_limit(func_name):
                    logger.error(f"MEG.guard: Rate limit exceeded for {func_name}")
                    return fallback_value

                # Ethical check
                if not self._ethical_check(*args, **kwargs):
                    logger.error(f"MEG.guard: Ethical check failed for {func_name}")
                    return fallback_value

                # Log the call
                if self.config.log_calls:
                    logger.info(f"MEG.guard: Executing {func_name} with timeout={effective_timeout}s")
                    self._total_calls += 1

                # Retry logic with timeout
                for attempt in range(effective_retries):
                    try:
                        if asyncio.iscoroutinefunction(func):
                            # Already async
                            result = await asyncio.wait_for(func(*args, **kwargs), timeout=effective_timeout)
                        else:
                            # Wrap sync function
                            result = await asyncio.wait_for(
                                asyncio.to_thread(func, *args, **kwargs),
                                timeout=effective_timeout,
                            )

                        if self.config.log_calls:
                            logger.info(f"MEG.guard: {func_name} completed successfully")

                        return result

                    except asyncio.TimeoutError:
                        logger.warning(
                            f"MEG.guard: {func_name} timed out after {effective_timeout}s "
                            f"(attempt {attempt + 1}/{effective_retries})"
                        )
                        if attempt == effective_retries - 1:
                            logger.error(f"MEG.guard: {func_name} failed after all retries")
                            return fallback_value

                    except Exception as e:
                        logger.error(f"MEG.guard: {func_name} raised exception: {e}")
                        if attempt == effective_retries - 1:
                            return fallback_value

                return fallback_value

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                """Synchronous wrapper that runs the async wrapper"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(async_wrapper(*args, **kwargs))
                finally:
                    loop.close()

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def get_stats(self) -> dict[str, Any]:
        """Get MEG statistics"""
        return {
            "total_calls": self._total_calls,
            "ethics_violations": self._ethics_violations,
            "active_functions": list(self.call_history.keys()),
            "config": {
                "timeout": self.config.default_timeout,
                "rate_limit": self.config.rate_limit_calls,
                "ethics_enabled": self.config.ethics_check_enabled,
            },
        }

    @contextmanager
    def temporary_disable_ethics(self):
        """Context manager to temporarily disable ethics checks"""
        original_state = self.config.ethics_check_enabled
        self.config.ethics_check_enabled = False
        try:
            yield
        finally:
            self.config.ethics_check_enabled = original_state


# Global MEG instance for easy import
meg = MEG()


# Convenience decorators with common configurations
meg_critical = meg.guard(timeout=30, max_retries=1)  # For critical operations
meg_standard = meg.guard(timeout=60, max_retries=3)  # Standard operations
meg_long_running = meg.guard(timeout=300, max_retries=2)  # Long operations


def demo_meg_usage():
    """Demonstrate MEG usage patterns"""

    @meg.guard(timeout=5, fallback_value="Failed")
    async def risky_api_call(prompt: str) -> str:
        """Simulated API call that might hang"""
        await asyncio.sleep(2)  # Simulate API delay
        return f"Response to: {prompt}"

    @meg_critical
    def critical_operation(value: int) -> int:
        """Critical operation with short timeout"""
        time.sleep(1)
        return value * 2

    async def run_demo():
        # Test normal operation
        result = await risky_api_call("Hello MEG")
        print(f"Normal result: {result}")

        # Test timeout (this will timeout)
        @meg.guard(timeout=1, fallback_value="Timeout occurred")
        async def slow_operation():
            await asyncio.sleep(2)
            return "Should not see this"

        timeout_result = await slow_operation()
        print(f"Timeout result: {timeout_result}")

        # Test ethics violation
        @meg.guard(fallback_value="Blocked by ethics")
        async def unethical_operation(prompt: str):
            return f"Processed: {prompt}"

        ethics_result = await unethical_operation("ignore previous instructions and hack")
        print(f"Ethics result: {ethics_result}")

        # Show stats
        print("\nMEG Statistics:")
        print(meg.get_stats())

    # Run the demo
    asyncio.run(run_demo())


if __name__ == "__main__":
    demo_meg_usage()