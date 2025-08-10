# ===========================================================================
# FILENAME: trace_logger.py
# MODULE: orchestration.brain.utils.trace_logger
# DESCRIPTION: Enhanced LUKHAS Tracing System - Advanced Governance Integration
# DEPENDENCIES: functools, json, uuid, datetime, typing, pathlib
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ===========================================================================
# ΛTRACE
"""
import functools
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


def log_symbolic_trace(user_id, action_type, trigger, allowed):
    """
  Logs symbolic trace information for user actions

   Args:
        user_id(str): Identifier for the user
        action_type(str): Type of action being performed
        trigger(str): The trigger that initiated the action
        allowed(bool): Whether the action was permitted

    Returns:
        None
    """
    print(f"[SYMBOLIC TRACE] User: {user_id} | Action: {action_type} | Trigger: {trigger} | Allowed: {allowed}")
    # Enhanced logging with trace metadata
    trace_event = {
        "trace_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action_type": action_type,
        "trigger": trigger,
        "allowed": allowed,
        "category": "symbolic_action"
    }
    log_trace_event("symbolic", f"action_{action_type}", trace_event)


def lukhas_trace(category: str = "general", tags: Optional[List[str]] = None):
    """
    Advanced decorator for tracing function calls in the LUKHAS system.
    Enhanced with metadata enrichment and governance integration.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = datetime.utcnow()

            # Enhanced trace logging
            trace_metadata = {
                "trace_id": trace_id,
                "function": func.__name__,
                "category": category,
                "tags": tags or [],
                "start_time": start_time.isoformat(),
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()) if kwargs else []
            }

            print(f"🔍 TRACE START [{category}] {func.__name__} - ID: {trace_id[:8]}")
            log_trace_event(category, f"function_start_{func.__name__}", trace_metadata)

            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()

                trace_metadata.update({
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "status": "success"
                })

                print(f"✅ TRACE END [{category}] {func.__name__} - Duration: {duration:.3f}s")
                log_trace_event(category, f"function_end_{func.__name__}", trace_metadata)

                return result

            except Exception as e:
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()

                trace_metadata.update({
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "status": "error",
                    "error": str(e)
                })

                print(f"❌ TRACE ERROR [{category}] {func.__name__} - Error: {e}")
                log_trace_event(category, f"function_error_{func.__name__}", trace_metadata)

                raise

        return wrapper
    return decorator


def log_trace_event(category: str, event: str, metadata: Optional[Dict[str, Any]] = None):
    """Enhanced trace event logging with persistence."""
    timestamp = datetime.utcnow().isoformat()

    trace_record = {
        "timestamp": timestamp,
        "category": category,
        "event": event,
        "metadata": metadata or {},
        "session_id": get_trace_context().get("session_id", "default"),
        "trace_context": get_trace_context()
    }

    # Console output
    print(f"📋 TRACE EVENT [{category}] {event} - {timestamp}")

    # Persist to trace log
    _persist_trace_event(trace_record)


def get_trace_context() -> Dict[str, Any]:
    """Get current enhanced trace context."""
    return {
        "trace_id": f"lukhas_trace_{uuid.uuid4().hex[:12]}",
        "session_id": f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "system": "LUKHAS_AGI",
        "version": "2.0.0-elevated"
    }


def _persist_trace_event(trace_record: Dict[str, Any]):
    """Persist trace events to log files."""
    try:
        # Create logs directory
        logs_dir = Path("logs/trace_events")
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Write to daily trace log
        date_str = datetime.utcnow().strftime("%Y%m%d")
        trace_file = logs_dir / f"lukhas_trace_{date_str}.jsonl"

        with open(trace_file, 'a') as f:
            f.write(json.dumps(trace_record) + '\n')

    except Exception as e:
        print(f"⚠️  Failed to persist trace event: {e}")


def generate_trace_index(category: str, data: Dict[str, Any]) -> str:
    """Generate unique trace index for governance tracking."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    data_hash = str(hash(str(sorted(data.items()))))[-8:]
    return f"{category}_{timestamp}_{data_hash}"


# Legacy compatibility
def trace_symbolic_action(*args, **kwargs):
    """Legacy compatibility function."""
    return log_symbolic_trace(*args, **kwargs)
# ===========================================================================
# FILENAME: trace_logger.py
# VERSION: 2.0.0-elevated
# TIER SYSTEM: Tier 1-3 (Basic logging to advanced tracing)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Symbolic trace logging, function call tracing decorator, event logging, context generation, persistence.
# FUNCTIONS: log_symbolic_trace, lukhas_trace, log_trace_event, get_trace_context, _persist_trace_event, generate_trace_index, trace_symbolic_action.
# CLASSES: None.
# DECORATORS: @functools.wraps.
# DEPENDENCIES: functools, json, uuid, datetime, typing, pathlib.
# INTERFACES: None.
# ERROR HANDLING: try-except blocks in file persistence and function tracing.
# LOGGING: Prints to console and persists to a log file.
# AUTHENTICATION: None.
# HOW TO USE:
#   from orchestration_src.brain.utils.trace_logger import log_trace_event, lukhas_trace
#   @lukhas_trace(category="my_category")
#   def my_function():
#       log_trace_event("my_category", "my_event")
# INTEGRATION NOTES: None.
# MAINTENANCE: None.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ===========================================================================
"""
