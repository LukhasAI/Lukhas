# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: direct_ai_router.py
# MODULE: lukhas.core.direct_ai_router
# DESCRIPTION: Provides a direct interface to an external AI router (e.g., ABot_beta/LukhasBot_beta)
#              by executing it as a Python subprocess. Allows routing AI tasks and checking availability.
# DEPENDENCIES: subprocess, json, os, typing, logging
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import json
import logging
import os
import subprocess
import sys
from typing import Any, Optional, Union

# ΛTAG: core, router, config

# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.core.direct_ai_router")
logger.info("ΛTRACE: Initializing direct_ai_router module.")

# ΛCORE: Use environment or sensible defaults to avoid hard dependency at import time
# TODO: Legacy constants kept for backward compatibility
DEFAULT_ROUTER_PATH = os.getenv("LUKHAS_AI_ROUTER_PATH", "")
DEFAULT_PYTHON_PATH = os.getenv("LUKHAS_PYTHON_PATH", sys.executable or "python3")

# Human-readable comment: Class to interface directly with an external AI router.


class DirectAIRouter:
    """
    Direct interface to the working AI router.
    This class executes an external Python script as a subprocess to communicate with the router.
    """

    # Human-readable comment: Initializes the DirectAIRouter with configurable paths.

    def __init__(self, router_path: Optional[str] = None, python_path: Optional[str] = None):
        """
        Initializes the DirectAIRouter.
        Args:
            router_path (Optional[str]): Absolute path to the AI router's directory.
                                         Defaults to DEFAULT_ROUTER_PATH if not provided or found in ENV.
            python_path (Optional[str]): Path to the Python interpreter.
                                         Defaults to DEFAULT_PYTHON_PATH if not provided or found in ENV.
        """
        self.router_path = os.getenv("LUKHAS_AI_ROUTER_PATH", router_path or DEFAULT_ROUTER_PATH)
        self.python_path = os.getenv("LUKHAS_PYTHON_PATH", python_path or DEFAULT_PYTHON_PATH)
        logger.info(
            f"ΛTRACE: DirectAIRouter initialized. Router Path: '{self.router_path}', Python Path: '{self.python_path}'."
        )
        if self.router_path == DEFAULT_ROUTER_PATH:
            logger.warning(
                f"ΛTRACE: Using default AI router path: '{DEFAULT_ROUTER_PATH}'. Consider configuring LUKHAS_AI_ROUTER_PATH."
            )
        if not os.path.isdir(self.router_path):
            logger.error(f"ΛTRACE: AI Router path does not exist or is not a directory: {self.router_path}")
            # Depending on strictness, could raise an error here.

    # Human-readable comment: Routes a request to the external AI router.

    def route_request(
        self,
        task: str,
        task_type: str = "general",
        debug: bool = False,
        *,
        structured: bool = False,
    ) -> Union[str, dict[str, Any]]:
        """
        Routes a request through the Python AI router by executing a dynamically generated script.
        Args:
            task (str): The task description or prompt for the AI.
            task_type (str): The type of task (e.g., "general", "coding").
            debug (bool): Flag to enable debug mode in the router script.
        Returns:
            Union[str, Dict[str, Any]]: By default a string response for backward compatibility.
            If structured=True, returns a dict with keys: success, output, error,
            return_code, stderr, meta.
        """
        logger.info(
            f"ΛTRACE: Routing AI request. Task Type: '{task_type}', Debug: {debug}, Task(first 50 chars): '{task[:50]}...'"
        )

        # WARNING: Injecting 'task' into a script string via f-string with simple replacement
        # can be a security risk if 'task' comes from an untrusted source.
        # This could lead to command injection within the Python script block.
        # Using json.dumps for the task string provides better escaping.
        logger.warning(
            "ΛTRACE: Task content is directly embedded into a Python script. Ensure 'task' content is trusted or sanitized if from external sources."
        )

        # Safely embed the task string into the Python script using json.dumps
        safe_task_string = json.dumps(task)

        python_script = f"""
import sys
import json # Added for parsing the task if needed, or just for correct string representation

sys.path.append('{self.router_path}') # This path should be validated or trusted

try:
    from router.llm_multiverse_router import multiverse_route

    task_content = {safe_task_string} # Use the json.dumps escaped string
    task_type_str = "{task_type}" # Basic string, assumed safe
    debug_flag = {debug} # Boolean, safe

    result = multiverse_route(task_content, task_type_str, debug_flag)

    # Assuming result is either a dict with 'output' or a direct string
    if isinstance(result, dict) and 'output' in result:
        print(result['output'])
    elif isinstance(result, str):
        print(result)
    else:
        # Handle unexpected result types gracefully: write to stderr and exit non-zero
        sys.stderr.write(
            "Router Error: Unexpected result type from multiverse_route: "
            + str(type(result))
            + ". Content: "
            + str(result)[:200]
            + "\n"
        )
        sys.exit(1)

except ImportError as ie:
    sys.stderr.write("Router Error: Failed to import 'multiverse_route'. Check LUKHAS_AI_ROUTER_PATH and module structure. Details: " + str(ie) + "\n")
    sys.exit(1)
except Exception as e:
    # Print a generic error message including the type of exception
    sys.stderr.write("Router Error: An exception occurred in the router script: " + type(e).__name__ + " - " + str(e) + "\n")
    sys.exit(1)
"""
        logger.debug(f"ΛTRACE: Executing dynamic Python script for AI routing:\n---\n{python_script[:300]}...\n---")

        try:
            process = subprocess.run(
                [self.python_path, "-c", python_script],
                capture_output=True,
                text=True,
                timeout=60,  # Increased timeout
            )

            if process.returncode == 0:
                output = process.stdout.strip()
                logger.info(f"ΛTRACE: AI router request completed. Output (first 100 chars): '{output[:100]}...'")
                # Treat Router Error markers from child script as failures even with 0 exit code
                is_error_marker = isinstance(output, str) and output.startswith("Router Error:")
                if structured:
                    if is_error_marker:
                        return {
                            "success": False,
                            "output": output,
                            "error": output,
                            "return_code": -4,
                            "stderr": process.stderr.strip(),
                            "meta": {
                                "task_type": task_type,
                                "debug": debug,
                                "router_path": self.router_path,
                            },
                        }
                    return {
                        "success": True,
                        "output": output,
                        "error": None,
                        "return_code": 0,
                        "stderr": process.stderr.strip(),
                        "meta": {
                            "task_type": task_type,
                            "debug": debug,
                            "router_path": self.router_path,
                        },
                    }
                # Backward compatible string return
                return output
            else:
                error_message = f"Router execution error (Code {process.returncode}): {process.stderr.strip()}"
                logger.error(f"ΛTRACE: {error_message}")
                if structured:
                    return {
                        "success": False,
                        "output": process.stdout.strip(),
                        "error": error_message,
                        "return_code": process.returncode,
                        "stderr": process.stderr.strip(),
                        "meta": {
                            "task_type": task_type,
                            "debug": debug,
                            "router_path": self.router_path,
                        },
                    }
                return error_message

        except subprocess.TimeoutExpired:
            logger.error("ΛTRACE: AI router request timed out after 60 seconds.")
            if structured:
                return {
                    "success": False,
                    "output": "",
                    "error": "Router request timed out",
                    "return_code": -1,
                    "stderr": "",
                    "meta": {"task_type": task_type, "debug": debug, "router_path": self.router_path},
                }
            return "Router request timed out"
        except FileNotFoundError:
            logger.critical(
                f"ΛTRACE: Python interpreter '{self.python_path}' not found. Please check LUKHAS_PYTHON_PATH.",
                exc_info=True,
            )
            if structured:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Python interpreter '{self.python_path}' not found. Cannot execute AI router.",
                    "return_code": -2,
                    "stderr": "",
                    "meta": {"task_type": task_type, "debug": debug, "router_path": self.router_path},
                }
            return f"Python interpreter '{self.python_path}' not found. Cannot execute AI router."
        except Exception as e:
            error_message = f"Router connection error: {e!s}"
            logger.error(f"ΛTRACE: {error_message}", exc_info=True)
            if structured:
                return {
                    "success": False,
                    "output": "",
                    "error": error_message,
                    "return_code": -3,
                    "stderr": "",
                    "meta": {"task_type": task_type, "debug": debug, "router_path": self.router_path},
                }
            return error_message

    # Human-readable comment: Checks if the AI router is available and responsive.

    def is_available(self) -> bool:
        """
        Checks if the AI router is available by sending a simple test request.
        Returns:
            bool: True if the router responds without obvious errors, False otherwise.
        """
        logger.info("ΛTRACE: Checking AI router availability.")
        try:
            # Using a very simple, common task for availability check
            test_response = self.route_request("Health check ping", "system_utility_health_check")
            # A more robust check would be to expect a specific keyword or structure in the response.
            # For now, check if the response doesn't contain common error indicators.
            if (
                "Router Error:" not in test_response
                and "Router execution error:" not in test_response
                and "timed out" not in test_response
                and "not found" not in test_response
            ):
                logger.info(f"ΛTRACE: AI router appears available. Test response: '{test_response[:100]}...'")
                return True
            else:
                logger.warning(
                    f"ΛTRACE: AI router availability check failed or returned error. Response: '{test_response}'"
                )
                return False
        except Exception as e:
            logger.error(
                f"ΛTRACE: Exception during AI router availability check: {e}",
                exc_info=True,
            )
            return False


# Human-readable comment: Global instance of the DirectAIRouter.
_direct_router_instance = DirectAIRouter()
logger.info("ΛTRACE: Global _direct_router_instance created.")

# Human-readable comment: Global function to route an AI request.


def route_ai_request(
    task: str, task_type: str = "general", debug: bool = False, *, structured: bool = False
) -> Union[str, dict[str, Any]]:
    """
    Global convenience function to route AI requests using the default DirectAIRouter instance.
    Args:
        task (str): The task description or prompt.
        task_type (str): The type of task.
        debug (bool): Debug flag for the router.
    Returns:
        Union[str, Dict[str, Any]]: String by default, or dict if structured=True.
    """
    logger.info("ΛTRACE: Global route_ai_request() called.")
    return _direct_router_instance.route_request(task, task_type, debug, structured=structured)


# Human-readable comment: Global function to check AI router availability.


def is_ai_available() -> bool:
    """
    Global convenience function to check if AI routing is available.
    Returns:
        bool: True if available, False otherwise.
    """
    logger.info("ΛTRACE: Global is_ai_available() called.")
    return _direct_router_instance.is_available()


# Example usage block for testing
if __name__ == "__main__":
    # Configure basic logging for the __main__ block if ΛTRACE isn't fully set
    # up externally
    if not logging.getLogger("ΛTRACE").handlers:
        main_console_handler = logging.StreamHandler(sys.stdout)  # Changed to sys
        main_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - ΛTRACE: %(message)s")
        main_console_handler.setFormatter(main_formatter)
        logging.getLogger("ΛTRACE").addHandler(main_console_handler)
        logging.getLogger("ΛTRACE").setLevel(logging.INFO)

    logger.info("ΛTRACE: direct_ai_router.py executed as __main__ for testing.")
    logger.info("🧪 Testing Direct AI Router...")

    # Test with global functions for typical usage
    logger.info("\n--- Testing with global functions ---")
    availability = is_ai_available()
    logger.info(f"🔍 Router Available (via global func): {availability}")

    if availability:
        response = route_ai_request("What is the capital of France?", "general_knowledge_query")
        logger.info(f"📞 Router Response (via global func for 'Capital of France'): {response[:200]}...")

        response_debug = route_ai_request(
            "Explain entanglement-like correlation briefly.",
            "scientific_explanation",
            debug=True,
        )
        logger.info(f"📞 Router Response (debug=True for 'Quantum Entanglement'): {response_debug[:200]}...")
    else:
        logger.warning("⚠️ AI Router not available, skipping further request tests using global functions.")

    # Test specific instance if needed, e.g., with custom paths (if they were settable post-init)
    # For this example, we'll re-test the default instance for clarity.
    logger.info("\n--- Re-testing default instance methods ---")
    default_router = DirectAIRouter()  # Creates another instance, or use _direct_router_instance

    available_instance = default_router.is_available()
    logger.info(f"🔍 Router Available (instance method): {available_instance}")

    if available_instance:
        response_instance = default_router.route_request("Hello! How are you today?", "greeting")
        logger.info(f"📞 Router Response (instance method for 'Hello'): {response_instance[:200]}...")
    else:
        logger.warning("⚠️ AI Router (tested via new instance) not available.")

    logger.info("\n✅ Direct AI Router test complete!")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: direct_ai_router.py
# VERSION: 1.1.0
# TIER SYSTEM: Tier 1-3 (Depends on routed task complexity and external router capabilities)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Routes tasks to an external AI model via a subprocess, Checks AI router availability.
# FUNCTIONS: route_ai_request, is_ai_available
# CLASSES: DirectAIRouter
# DECORATORS: None
# DEPENDENCIES: subprocess, json, os, typing, logging
# INTERFACES: Exports DirectAIRouter class and global functions route_ai_request, is_ai_available.
# ERROR HANDLING: Handles subprocess errors, timeouts, and script execution errors.
#                 Returns error messages as strings. Logs errors via ΛTRACE.
# LOGGING: ΛTRACE_ENABLED for router initialization, request routing, and availability checks.
# AUTHENTICATION: Not applicable directly; authentication is handled by the external AI router.
# HOW TO USE:
#   from candidate.core.direct_ai_router import route_ai_request, is_ai_available
#   if is_ai_available():
#       response = route_ai_request("Translate 'hello' to Spanish.")
#       print(response)
# INTEGRATION NOTES: Requires the external AI router script (multiverse_route) to be correctly
#                    configured at LUKHAS_AI_ROUTER_PATH. The Python interpreter specified by
#                    LUKHAS_PYTHON_PATH must be able to run the router script.
#                    Security Warning: Task content is embedded in a dynamically generated script.
#                    Ensure input tasks are from trusted sources or properly sanitized.
# MAINTENANCE: Update router_path and python_path defaults or configuration methods as needed.
#              Monitor the external AI router for compatibility. Consider enhancing error
#              reporting to be more structured than simple strings.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
