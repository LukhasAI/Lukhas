"""Hook Registry for Memory Management

This module manages the registration and execution of memory hooks,
providing a centralized system for extending memory operations.

ΛTAG: memory_hook_registry
"""

import time
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from candidate.core.common import LukhasError, get_logger

from .base import HookExecutionError, MemoryHook, MemoryItem

logger = get_logger(__name__)


class HookRegistrationError(LukhasError):
    """Raised when hook registration fails"""


class HookPriority(IntEnum):
    """Priority levels for hook execution order"""

    CRITICAL = 0  # Executed first
    HIGH = 10
    NORMAL = 50
    LOW = 90
    BACKGROUND = 100  # Executed last


@dataclass
class RegisteredHook:
    """Container for registered hook information"""

    hook: MemoryHook
    priority: HookPriority
    tags: set[str]
    max_retries: int = 3
    timeout_seconds: float = 5.0
    fail_on_error: bool = False

    def __post_init__(self):
        """Validate hook registration"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class HookRegistry:
    """Manages memory hook registration and execution

    The registry maintains hooks organized by priority and provides
    safe execution with error handling, timeouts, and circuit breakers.
    """

    def __init__(self, max_hooks_per_priority: int = 10, global_timeout_seconds: float = 30.0):
        """Initialize hook registry

        Args:
            max_hooks_per_priority: Maximum hooks allowed per priority level
            global_timeout_seconds: Total timeout for all hook execution
        """
        self._hooks: dict[HookPriority, list[RegisteredHook]] = defaultdict(list)
        self._hook_names: set[str] = set()
        self._max_hooks_per_priority = max_hooks_per_priority
        self._global_timeout = global_timeout_seconds

        # Circuit breaker state
        self._circuit_breaker_enabled = True
        self._failed_hooks: dict[str, int] = defaultdict(int)
        self._circuit_breaker_threshold = 5
        self._disabled_hooks: set[str] = set()

        # Performance monitoring
        self._execution_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "timeout_count": 0,
            "circuit_breaker_trips": 0,
        }

    def register_hook(
        self,
        hook: MemoryHook,
        priority: HookPriority = HookPriority.NORMAL,
        tags: Optional[set[str]] = None,
        max_retries: int = 3,
        timeout_seconds: float = 5.0,
        fail_on_error: bool = False,
    ) -> None:
        """Register a new memory hook

        Args:
            hook: The hook instance to register
            priority: Execution priority
            tags: Optional tags for filtering
            max_retries: Maximum retry attempts on failure
            timeout_seconds: Timeout for individual hook execution
            fail_on_error: Whether to stop execution chain on error

        Raises:
            HookRegistrationError: If registration fails
        """
        hook_name = hook.get_hook_name()

        # Validate registration
        if hook_name in self._hook_names:
            raise HookRegistrationError(f"Hook already registered: {hook_name}")

        if len(self._hooks[priority]) >= self._max_hooks_per_priority:
            raise HookRegistrationError(
                f"Maximum hooks ({self._max_hooks_per_priority}) reached for priority {priority.name}"
            )

        # Create registered hook
        registered = RegisteredHook(
            hook=hook,
            priority=priority,
            tags=tags or set(),
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            fail_on_error=fail_on_error,
        )

        # Register
        self._hooks[priority].append(registered)
        self._hook_names.add(hook_name)

        logger.info(f"Registered hook: {hook_name} with priority {priority.name}")

    def unregister_hook(self, hook_name: str) -> bool:
        """Unregister a hook

        Args:
            hook_name: Name of hook to unregister

        Returns:
            True if hook was found and unregistered
        """
        if hook_name not in self._hook_names:
            return False

        # Find and remove hook
        for priority_hooks in self._hooks.values():
            for i, registered in enumerate(priority_hooks):
                if registered.hook.get_hook_name() == hook_name:
                    priority_hooks.pop(i)
                    self._hook_names.remove(hook_name)
                    self._disabled_hooks.discard(hook_name)
                    self._failed_hooks.pop(hook_name, None)
                    logger.info(f"Unregistered hook: {hook_name}")
                    return True

        return False

    def execute_before_store(self, item: MemoryItem, tags: Optional[set[str]] = None) -> MemoryItem:
        """Execute all before_store hooks in priority order

        Args:
            item: Memory item to process
            tags: Optional tags to filter hooks

        Returns:
            Processed memory item

        Raises:
            HookExecutionError: If a critical hook fails
        """
        return self._execute_hooks("before_store", item, tags)

    def execute_after_recall(self, item: MemoryItem, tags: Optional[set[str]] = None) -> MemoryItem:
        """Execute all after_recall hooks in priority order

        Args:
            item: Memory item to process
            tags: Optional tags to filter hooks

        Returns:
            Processed memory item

        Raises:
            HookExecutionError: If a critical hook fails
        """
        return self._execute_hooks("after_recall", item, tags)

    def _execute_hooks(self, operation: str, item: MemoryItem, tags: Optional[set[str]] = None) -> MemoryItem:
        """Execute hooks for given operation

        Args:
            operation: 'before_store' or 'after_recall'
            item: Memory item to process
            tags: Optional tags to filter hooks

        Returns:
            Processed memory item
        """
        start_time = time.time()
        self._execution_metrics["total_executions"] += 1

        # Collect hooks to execute
        hooks_to_execute = self._collect_hooks(tags)

        # Process through each hook
        processed_item = item
        executed_count = 0

        try:
            for registered in hooks_to_execute:
                # Check global timeout
                if time.time() - start_time > self._global_timeout:
                    logger.warning(f"Global timeout reached after {executed_count} hooks")
                    self._execution_metrics["timeout_count"] += 1
                    break

                # Check circuit breaker
                hook_name = registered.hook.get_hook_name()
                if self._is_circuit_broken(hook_name):
                    logger.debug(f"Skipping hook {hook_name} - circuit breaker open")
                    continue

                # Execute hook
                try:
                    processed_item = self._execute_single_hook(registered, operation, processed_item)
                    executed_count += 1

                except HookExecutionError as e:
                    if registered.fail_on_error:
                        logger.error(f"Critical hook {hook_name} failed: {e}")
                        self._execution_metrics["failed_executions"] += 1
                        raise
                    else:
                        logger.warning(f"Hook {hook_name} failed (non-critical): {e}")
                        self._record_failure(hook_name)

            self._execution_metrics["successful_executions"] += 1

        except Exception:
            self._execution_metrics["failed_executions"] += 1
            raise

        finally:
            elapsed = time.time() - start_time
            logger.debug(f"Executed {executed_count} hooks in {elapsed:.3f}s")

        return processed_item

    def _collect_hooks(self, tags: Optional[set[str]] = None) -> list[RegisteredHook]:
        """Collect hooks to execute based on tags and priority

        Args:
            tags: Optional tags to filter hooks

        Returns:
            List of hooks sorted by priority
        """
        hooks_to_execute = []

        # Collect hooks in priority order
        for priority in sorted(HookPriority):
            for registered in self._hooks[priority]:
                # Skip disabled hooks
                if not registered.hook.is_enabled():
                    continue

                # Filter by tags if specified
                if tags and not registered.tags.intersection(tags):
                    continue

                hooks_to_execute.append(registered)

        return hooks_to_execute

    def _execute_single_hook(self, registered: RegisteredHook, operation: str, item: MemoryItem) -> MemoryItem:
        """Execute a single hook with retry and timeout

        Args:
            registered: Registered hook information
            operation: 'before_store' or 'after_recall'
            item: Memory item to process

        Returns:
            Processed memory item

        Raises:
            HookExecutionError: If hook fails after retries
        """
        hook = registered.hook
        hook_name = hook.get_hook_name()

        for attempt in range(registered.max_retries):
            try:
                start_time = time.time()

                # Execute hook operation
                if operation == "before_store":
                    result = hook.before_store(item)
                else:  # after_recall
                    result = hook.after_recall(item)

                # Record success
                elapsed = time.time() - start_time
                hook._update_metrics(operation, elapsed)

                # Validate result
                if not isinstance(result, MemoryItem):
                    raise HookExecutionError(f"Hook {hook_name} returned invalid type: {type(result)}")

                # Reset failure count on success
                self._failed_hooks[hook_name] = 0

                return result

            except Exception as e:
                logger.warning(f"Hook {hook_name} attempt {attempt + 1} failed: {e}")

                if attempt == registered.max_retries - 1:
                    # Final attempt failed
                    elapsed = time.time() - start_time
                    hook._update_metrics(operation, elapsed, error=True)
                    self._record_failure(hook_name)
                    raise HookExecutionError(f"Hook {hook_name} failed: {e!s}")

                # Wait before retry
                time.sleep(0.1 * (attempt + 1))

        return item  # Should not reach here

    def _is_circuit_broken(self, hook_name: str) -> bool:
        """Check if circuit breaker is tripped for hook

        Args:
            hook_name: Name of hook to check

        Returns:
            True if circuit is broken
        """
        if not self._circuit_breaker_enabled:
            return False

        return hook_name in self._disabled_hooks

    def _record_failure(self, hook_name: str) -> None:
        """Record hook failure and check circuit breaker

        Args:
            hook_name: Name of failed hook
        """
        self._failed_hooks[hook_name] += 1

        if self._failed_hooks[hook_name] >= self._circuit_breaker_threshold:
            self._disabled_hooks.add(hook_name)
            self._execution_metrics["circuit_breaker_trips"] += 1
            logger.warning(f"Circuit breaker tripped for hook: {hook_name}")

    def reset_circuit_breaker(self, hook_name: Optional[str] = None) -> None:
        """Reset circuit breaker for hook(s)

        Args:
            hook_name: Specific hook to reset, or None for all
        """
        if hook_name:
            self._disabled_hooks.discard(hook_name)
            self._failed_hooks.pop(hook_name, None)
            logger.info(f"Reset circuit breaker for hook: {hook_name}")
        else:
            self._disabled_hooks.clear()
            self._failed_hooks.clear()
            logger.info("Reset all circuit breakers")

    def get_registered_hooks(self) -> dict[str, dict[str, any]]:
        """Get information about all registered hooks

        Returns:
            Dictionary of hook information by name
        """
        hooks_info = {}

        for priority_hooks in self._hooks.values():
            for registered in priority_hooks:
                hook = registered.hook
                hook_name = hook.get_hook_name()

                hooks_info[hook_name] = {
                    "version": hook.get_hook_version(),
                    "priority": registered.priority.name,
                    "tags": list(registered.tags),
                    "enabled": hook.is_enabled(),
                    "circuit_broken": hook_name in self._disabled_hooks,
                    "failure_count": self._failed_hooks.get(hook_name, 0),
                    "metrics": hook.get_metrics(),
                }

        return hooks_info

    def get_registry_metrics(self) -> dict[str, any]:
        """Get registry performance metrics

        Returns:
            Dictionary of registry metrics
        """
        total_hooks = sum(len(hooks) for hooks in self._hooks.values())
        enabled_hooks = sum(1 for hooks in self._hooks.values() for reg in hooks if reg.hook.is_enabled())

        return {
            "total_hooks": total_hooks,
            "enabled_hooks": enabled_hooks,
            "disabled_by_circuit_breaker": len(self._disabled_hooks),
            "execution_metrics": self._execution_metrics.copy(),
            "hooks_by_priority": {priority.name: len(hooks) for priority, hooks in self._hooks.items()},
        }

    def enable_circuit_breaker(self) -> None:
        """Enable circuit breaker protection"""
        self._circuit_breaker_enabled = True
        logger.info("Circuit breaker enabled")

    def disable_circuit_breaker(self) -> None:
        """Disable circuit breaker protection"""
        self._circuit_breaker_enabled = False
        logger.info("Circuit breaker disabled")
