"""
Audit decorators for easy integration into AGI systems
Provides automatic audit logging with minimal code changes
"""

import asyncio
import functools
import inspect
import traceback
from datetime import datetime
from typing import Callable, Optional

from .audit_trail import AuditEventType, AuditSeverity, get_audit_trail


def audit_operation(
    operation_type: Optional[str] = None,
    capture_args: bool = True,
    capture_result: bool = True,
    severity: AuditSeverity = AuditSeverity.INFO,
):
    """
    Decorator to audit any operation

    Usage:
        @audit_operation("data_processing")
        async def process_data(data):
            return transformed_data
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            audit = get_audit_trail()

            # Determine operation type
            op_type = operation_type or f"{func.__module__}.{func.__name__}"

            # Capture function arguments
            details = {"operation": op_type}
            if capture_args:
                # Get argument names
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Filter out sensitive args
                safe_args = {}
                for name, value in bound_args.arguments.items():
                    if name not in ["password", "secret", "token", "key"]:
                        safe_args[name] = str(value)[:100]  # Truncate long values
                details["arguments"] = safe_args

            # Log operation start
            event_id = await audit.log_event(
                AuditEventType.SYSTEM_START,
                func.__module__,
                details,
                severity=severity,
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Log success
                success_details = details.copy()
                if capture_result and result is not None:
                    success_details["result"] = str(result)[:200]
                success_details["success"] = True

                await audit.log_event(
                    AuditEventType.SYSTEM_STOP,
                    func.__module__,
                    success_details,
                    severity=severity,
                    parent_id=event_id,
                )

                return result

            except Exception as e:
                # Log error
                error_details = details.copy()
                error_details["error"] = str(e)
                error_details["traceback"] = traceback.format_exc()

                await audit.log_event(
                    AuditEventType.SYSTEM_ERROR,
                    func.__module__,
                    error_details,
                    severity=AuditSeverity.ERROR,
                    parent_id=event_id,
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def audit_decision(decision_type: str, capture_alternatives: bool = True):
    """
    Decorator specifically for decision-making functions

    Usage:
        @audit_decision("action_selection")
        async def select_action(state, options):
            return chosen_action, confidence
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            audit = get_audit_trail()

            # Generate decision ID
            decision_id = f"decision_{datetime.now().timestamp()}"

            # Capture decision context
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            context = {
                "function": func.__name__,
                "inputs": {k: str(v)[:100] for k, v in bound_args.arguments.items()},
            }

            # Log decision initiation
            await audit.log_event(
                AuditEventType.DECISION_INITIATED,
                func.__module__,
                {
                    "decision_id": decision_id,
                    "decision_type": decision_type,
                    "context": context,
                },
            )

            try:
                # Execute decision function
                result = await func(*args, **kwargs)

                # Extract decision details
                if isinstance(result, tuple) and len(result) >= 2:
                    decision, confidence = result[0], result[1]
                    alternatives = result[2] if len(result) > 2 else None
                else:
                    decision = result
                    confidence = 1.0
                    alternatives = None

                # Log decision made
                await audit.log_decision_chain(
                    decision_id=decision_id,
                    decision_type=decision_type,
                    steps=[
                        {
                            "description": "Direct decision",
                            "result": str(decision),
                        }
                    ],
                    outcome={"decision": str(decision)},
                    rationale=f"Decision made by {func.__name__}",
                    confidence=confidence,
                    alternatives_considered=(
                        alternatives if capture_alternatives else None
                    ),
                )

                return result

            except Exception as e:
                # Log decision failure
                await audit.log_event(
                    AuditEventType.SYSTEM_ERROR,
                    func.__module__,
                    {
                        "decision_id": decision_id,
                        "error": str(e),
                        "decision_type": decision_type,
                    },
                    severity=AuditSeverity.ERROR,
                )
                raise

        return wrapper

    return decorator


def audit_consciousness_change(func: Callable) -> Callable:
    """
    Decorator for consciousness state changes

    Usage:
        @audit_consciousness_change
        async def update_consciousness(self, new_state):
            old_state = self.current_state
            self.current_state = new_state
            return old_state, new_state
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        audit = get_audit_trail()

        # Execute function
        result = await func(*args, **kwargs)

        # Extract states from result
        if isinstance(result, tuple) and len(result) >= 2:
            from_state, to_state = result[0], result[1]

            # Detect emergence
            emergence = (
                to_state.get("coherence", 0) > 0.85
                and to_state.get("complexity", 0) > 0.8
            )

            # Log transition
            await audit.log_consciousness_transition(
                from_state=from_state,
                to_state=to_state,
                trigger=func.__name__,
                metrics={
                    "processing_time": 0,  # Would be measured in real implementation
                    "energy_consumed": 0,
                },
                emergence_detected=emergence,
            )

        return result

    return wrapper


def audit_learning(learning_type: str = "general"):
    """
    Decorator for learning operations

    Usage:
        @audit_learning("skill_acquisition")
        async def learn_skill(self, skill_data):
            return learning_result
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            audit = get_audit_trail()

            # Generate learning ID
            learning_id = f"learn_{datetime.now().timestamp()}"

            # Log learning start
            await audit.log_event(
                AuditEventType.LEARNING_GOAL_SET,
                func.__module__,
                {
                    "learning_id": learning_id,
                    "learning_type": learning_type,
                    "function": func.__name__,
                },
            )

            try:
                # Execute learning function
                result = await func(*args, **kwargs)

                # Log learning result
                if isinstance(result, dict):
                    await audit.log_learning_progress(
                        learning_id=learning_id,
                        topic=result.get("topic", learning_type),
                        progress=result.get("progress", 1.0),
                        knowledge_gained=result.get("knowledge", {}),
                        performance_metrics=result.get("metrics", {}),
                    )
                else:
                    # Basic logging for non-dict results
                    await audit.log_event(
                        AuditEventType.KNOWLEDGE_ACQUIRED,
                        func.__module__,
                        {
                            "learning_id": learning_id,
                            "result": str(result)[:200],
                        },
                    )

                return result

            except Exception as e:
                # Log learning failure
                await audit.log_event(
                    AuditEventType.LEARNING_FAILURE,
                    func.__module__,
                    {
                        "learning_id": learning_id,
                        "error": str(e),
                        "learning_type": learning_type,
                    },
                    severity=AuditSeverity.WARNING,
                )
                raise

        return wrapper

    return decorator


def audit_security(operation: str = "access_control"):
    """
    Decorator for security operations

    Usage:
        @audit_security("api_access")
        async def validate_access(self, user, resource):
            return is_allowed
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            audit = get_audit_trail()

            # Capture security context
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Extract user/resource info safely
            user = bound_args.arguments.get("user", "unknown")
            resource = bound_args.arguments.get("resource", "unknown")

            try:
                # Execute security function
                result = await func(*args, **kwargs)

                # Log based on result
                if result is True or (
                    isinstance(result, dict) and result.get("allowed")
                ):
                    await audit.log_event(
                        AuditEventType.ACCESS_GRANTED,
                        func.__module__,
                        {
                            "operation": operation,
                            "user": str(user),
                            "resource": str(resource),
                            "function": func.__name__,
                        },
                    )
                else:
                    await audit.log_event(
                        AuditEventType.ACCESS_DENIED,
                        func.__module__,
                        {
                            "operation": operation,
                            "user": str(user),
                            "resource": str(resource),
                            "reason": (
                                result.get("reason", "Permission denied")
                                if isinstance(result, dict)
                                else "Permission denied"
                            ),
                        },
                        severity=AuditSeverity.WARNING,
                    )

                return result

            except Exception:
                # Log security exception as potential threat
                await audit.log_security_event(
                    threat_type="security_exception",
                    threat_level="HIGH",
                    source=f"{func.__module__}.{func.__name__}",
                    action_taken="exception_raised",
                    blocked=True,
                )
                raise

        return wrapper

    return decorator


# Convenience decorators for common operations
audit_api_call = audit_operation("api_call", capture_args=True, capture_result=True)
audit_memory_operation = audit_operation("memory_operation", capture_args=True)
audit_dream_operation = audit_operation("dream_operation", capture_result=True)
audit_config_change = audit_operation("config_change", severity=AuditSeverity.WARNING)
