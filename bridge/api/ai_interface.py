# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lukhas_ai_interface.py
# MODULE: core.lukhas_ai_interface
# DESCRIPTION: Provides a universal AI interface for Lukhas components, routing
#              requests through an external AI router (e.g., ABot_beta) based on task type.
# DEPENDENCIES: sys, os, pathlib, typing, enum, logging, router.llm_multiverse_router (external)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import os
import sys
from enum import Enum
from pathlib import Path
from typing import Optional  # Dict, Any, List not in signatures, but good for context

# Initialize logger for ΛTRACE

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

logger = logging.getLogger("ΛTRACE.core.lukhas_ai_interface")
logger.info("ΛTRACE: Initializing lukhas_ai_interface module.")

# --- External Router Path Configuration ---
# TODO: Consider a more robust way to manage this dependency, e.g.,
# through a plugin system or service discovery.
DEFAULT_AI_ROUTER_PATH = "/Users/A_G_I/Lukhas/Lukhas-ecosystem/ABot_beta/LukhasBot_beta"
AI_ROUTER_PATH = os.getenv("LUKHAS_AI_ROUTER_PATH", DEFAULT_AI_ROUTER_PATH)

if AI_ROUTER_PATH == DEFAULT_AI_ROUTER_PATH:
    logger.warning(
        f"ΛTRACE: Using default AI router path: '{DEFAULT_AI_ROUTER_PATH}'. Consider configuring LUKHAS_AI_ROUTER_PATH environment variable."
    )

if Path(AI_ROUTER_PATH).is_dir():
    # Modifying sys.path is generally discouraged, but might be necessary for
    # unmanaged external dependencies.
    logger.info(
        f"ΛTRACE: Adding AI Router path '{AI_ROUTER_PATH}' to sys.path to attempt import of 'router.llm_multiverse_router'."
    )
    sys.path.insert(0, AI_ROUTER_PATH)
else:
    logger.error(
        f"ΛTRACE: LUKHAS_AI_ROUTER_PATH '{AI_ROUTER_PATH}' does not exist or is not a directory. 'multiverse_route' import will likely fail."
    )

# --- Attempt to import from External Router ---
ROUTER_AVAILABLE = False
multiverse_route = None
try:
    from router.llm_multiverse_router import multiverse_route

    ROUTER_AVAILABLE = True
    logger.info("ΛTRACE: Successfully imported 'multiverse_route' from AI router.")
except ImportError as e:
    logger.error(
        f"ΛTRACE: Failed to import 'multiverse_route' from '{AI_ROUTER_PATH}'. AI interface will be non-functional. Error: {e}",
        exc_info=True,
    )
    logger.warning(
        f"⚠️ WARNING: LUKHAS AI Router module ('router.llm_multiverse_router') not found at '{AI_ROUTER_PATH}' or its dependencies are missing. AI functionality will be disabled."
    )
except Exception as e_general:  # Catch any other exception during import
    logger.critical(
        f"ΛTRACE: An unexpected error occurred while trying to import 'multiverse_route': {e_general}",
        exc_info=True,
    )
    logger.critical(
        f"⚠️ CRITICAL WARNING: An unexpected error occurred during AI router import: {e_general}. AI functionality will be disabled."
    )

# Human-readable comment: Defines task types for optimal AI model routing.


class LukhusAITaskType(Enum):
    """
    Enumerates AI task types to guide the `multiverse_route` for selecting
    the most appropriate AI model or processing pipeline.
    """

    CODE = "code"  # Programming, debugging, code analysis, software design
    ETHICS = "ethics"  # Security reviews, compliance checks, ethical implications
    WEB = "web"  # Web research, data gathering from online sources
    CREATIVE = "creative"  # Content generation, creative writing, brainstorming
    GENERAL = "general"  # General queries, conversation, summarization, Q&A
    AUDIT = "ethics"  # Specific alias for auditing tasks, routes to ethics model
    DOCUMENTATION = (
        "creative"  # Documentation generation, routes to creative/writing model
    )
    ANALYSIS = (
        "code"  # Data analysis, logical reasoning, routes to code/analytical model
    )
    SYSTEM = (
        "system"  # For system-level commands or internal routing logic if supported
    )

    @classmethod
    def _missing_(cls, value):  # Handle potential string inputs gracefully
        logger.warning(
            f"ΛTRACE: LukhusAITaskType received an unknown value '{value}'. Defaulting to GENERAL."
        )
        return cls.GENERAL


logger.info(
    f"ΛTRACE: LukhusAITaskType Enum defined with values: {[task_type.value for task_type in LukhusAITaskType]}."
)

# Human-readable comment: Main class providing a universal AI interface.


class LukhusAI:
    """
    Universal AI interface for all Lukhas components.
    It uses an external AI router (multiverse_route) to process requests.
    """

    # Human-readable comment: Initializes the LukhusAI interface.

    def __init__(self, component_name: str = "LukhusGenericComponent"):
        """
        Initializes the LukhusAI interface.
        Args:
            component_name (str): Name of the Lukhas component using this interface,
                                  used for context in prompts.
        """
        self.component_name = component_name
        self.router_available = ROUTER_AVAILABLE  # Based on import-time check
        self.instance_logger = logger.getChild(
            f"LukhusAI.{self.component_name}"
        )  # Instance-specific logger
        self.instance_logger.info(
            f"ΛTRACE: LukhusAI instance created for component '{self.component_name}'. Router available: {self.router_available}."
        )

    # Human-readable comment: Generates an AI response using the external router.

    def generate_response(
        self,
        prompt: str,
        task_type: LukhusAITaskType = LukhusAITaskType.GENERAL,
        model_preference: Optional[
            str
        ] = None,  # Note: multiverse_route might not use this directly
        debug: bool = False,
    ) -> str:
        """
        Generates an AI response by routing the prompt through `multiverse_route`.
        Args:
            prompt (str): The input prompt for the AI.
            task_type (LukhusAITaskType): The type of task to perform.
            model_preference (Optional[str]): Preferred AI model (actual use depends on router).
            debug (bool): Flag to enable debug mode in the router.
        Returns:
            str: The AI's response, or an error message if issues occur.
        TODO: Consider returning a more structured object (e.g., a dataclass with success, data, error_code).
        """
        self.instance_logger.info(
            f"ΛTRACE: generate_response called. TaskType: {task_type.value},
            Debug: {debug}, Prompt(first 50): '{prompt[:50]}...'"
        )

        if not self.router_available or multiverse_route is None:
            error_msg = f"[{self.component_name}] AI router is not available. Please check configuration and logs."
            self.instance_logger.error("ΛTRACE: " + error_msg)
            return error_msg

        try:
            # Add component context to prompt for better routing or contextualization
            # by the AI
            enhanced_prompt = f"[Context: Invoked by LUKHAS Component '{self.component_name}']\nTask: {prompt}"
            self.instance_logger.debug(
                f"ΛTRACE: Enhanced prompt: '{enhanced_prompt[:100]}...'"
            )

            # Route through multiverse router
            # Assuming multiverse_route handles model_preference if passed, or ignores it.
            # The original multiverse_route signature was (task, task_type, debug)
            route_args = {
                "task": enhanced_prompt,
                "task_type": task_type.value,
                "debug": debug,
            }
            # if model_preference: # If multiverse_route is updated to take it
            #     route_args["model_preference"] = model_preference

            result = multiverse_route(**route_args)

            # Extract response from router's typical debug format if needed
            if isinstance(result, dict) and "output" in result:
                response_content = result["output"]
                self.instance_logger.info(
                    f"ΛTRACE: AI response received (from dict output). Length: {len(response_content)}."
                )
                self.instance_logger.debug(
                    f"ΛTRACE: Full AI dict result: {result if debug else {'output_preview': response_content[:100]+'...'}}"
                )
                return str(response_content)  # Ensure string
            elif isinstance(result, str):
                self.instance_logger.info(
                    f"ΛTRACE: AI response received (direct string). Length: {len(result)}."
                )
                self.instance_logger.debug(
                    f"ΛTRACE: Full AI string result (first 100): {result[:100]+'...'}"
                )
                return result
            else:
                unexpected_type_msg = f"[{self.component_name}] AI router returned unexpected result type: {type(result)}. Content: {str(result)[:200]}"
                self.instance_logger.error(f"ΛTRACE: {unexpected_type_msg}")
                return unexpected_type_msg

        except Exception as e:
            error_msg = f"[{self.component_name}] AI Error during multiverse_route call: {type(e).__name__} - {str(e)}"
            self.instance_logger.error(f"ΛTRACE: {error_msg}", exc_info=True)
            return error_msg

    # --- Specialized Helper Methods ---
    # These methods provide convenient wrappers around generate_response for
    # common task types.

    # Human-readable comment: Provides specialized AI assistance for coding tasks.

    def code_assistance(self, prompt: str, language: str = "") -> str:
        """Generates code or provides coding assistance."""
        self.instance_logger.info(
            f"ΛTRACE: code_assistance requested. Language: '{language}'."
        )
        enhanced_prompt = (
            f"Programming Language: {language}\nRequest: {prompt}"
            if language
            else prompt
        )
        return self.generate_response(enhanced_prompt, LukhusAITaskType.CODE)

    # Human-readable comment: Performs security and compliance auditing tasks.

    def security_audit(self, prompt: str) -> str:
        """Performs security, compliance, or ethical auditing tasks."""
        self.instance_logger.info("ΛTRACE: security_audit requested.")
        return self.generate_response(
            prompt, LukhusAITaskType.AUDIT
        )  # AUDIT aliases to ETHICS

    # Human-readable comment: Conducts web research and gathers data.

    def web_research(self, prompt: str) -> str:
        """Performs web research and data gathering tasks."""
        self.instance_logger.info("ΛTRACE: web_research requested.")
        return self.generate_response(prompt, LukhusAITaskType.WEB)

    # Human-readable comment: Assists with documentation generation.

    def documentation_assist(self, prompt: str) -> str:
        """Assists with generating or improving documentation."""
        self.instance_logger.info("ΛTRACE: documentation_assist requested.")
        return self.generate_response(
            prompt, LukhusAITaskType.DOCUMENTATION
        )  # DOCUMENTATION aliases to CREATIVE

    # Human-readable comment: Generates creative content.

    def creative_generation(self, prompt: str) -> str:
        """Generates creative content (text, ideas, etc.)."""
        self.instance_logger.info("ΛTRACE: creative_generation requested.")
        return self.generate_response(prompt, LukhusAITaskType.CREATIVE)

    # Human-readable comment: Performs analysis and provides insights on given
    # data or context.

    def analysis(self, prompt: str, context: str = "") -> str:
        """Performs analysis and provides insights, potentially with added context."""
        self.instance_logger.info(
            f"ΛTRACE: analysis requested. Context provided: {bool(context)}."
        )
        enhanced_prompt = (
            f"Context for Analysis:\n{context}\n\nAnalysis Request: {prompt}"
            if context
            else prompt
        )
        return self.generate_response(
            enhanced_prompt, LukhusAITaskType.ANALYSIS
        )  # ANALYSIS aliases to CODE

    # Human-readable comment: Engages in general conversation.

    def chat(self, message: str) -> str:
        """Engages in general conversation or answers general questions."""
        self.instance_logger.info("ΛTRACE: chat message received.")
        return self.generate_response(message, LukhusAITaskType.GENERAL)


# --- Convenience Global Functions ---
# These functions provide quick, stateless access to LukhusAI functionalities.

# Human-readable comment: Quick access to code assistance.


def ai_code(
    prompt: str, language: str = "", component: str = "LukhusQuickAccess"
) -> str:
    """Global convenience function for code assistance."""
    logger.debug(f"ΛTRACE: Global ai_code() called by component '{component}'.")
    ai_instance = LukhusAI(component)
    return ai_instance.code_assistance(prompt, language)


# Human-readable comment: Quick access to security auditing.


def ai_audit(prompt: str, component: str = "LukhusQuickAccess") -> str:
    """Global convenience function for security/ethical audits."""
    logger.debug(f"ΛTRACE: Global ai_audit() called by component '{component}'.")
    ai_instance = LukhusAI(component)
    return ai_instance.security_audit(prompt)


# Human-readable comment: Quick access to documentation assistance.


def ai_docs(prompt: str, component: str = "LukhusQuickAccess") -> str:
    """Global convenience function for documentation assistance."""
    logger.debug(f"ΛTRACE: Global ai_docs() called by component '{component}'.")
    ai_instance = LukhusAI(component)
    return ai_instance.documentation_assist(prompt)


# Human-readable comment: Quick access to general chat.


def ai_chat(message: str, component: str = "LukhusQuickAccess") -> str:
    """Global convenience function for general chat."""
    logger.debug(f"ΛTRACE: Global ai_chat() called by component '{component}'.")
    ai_instance = LukhusAI(component)
    return ai_instance.chat(message)


# Human-readable comment: Quick access to web research.


def ai_research(prompt: str, component: str = "LukhusQuickAccess") -> str:
    """Global convenience function for web research."""
    logger.debug(f"ΛTRACE: Global ai_research() called by component '{component}'.")
    ai_instance = LukhusAI(component)
    return ai_instance.web_research(prompt)


# Human-readable comment: Example usage and testing block.
if __name__ == "__main__":
    # Configure basic logging for the __main__ block if ΛTRACE isn't fully set
    # up externally
    if not logging.getLogger("ΛTRACE").handlers:
        main_console_handler = logging.StreamHandler(sys.stdout)
        main_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - ΛTRACE: %(message)s"
        )
        main_console_handler.setFormatter(main_formatter)
        logging.getLogger("ΛTRACE").addHandler(main_console_handler)
        logging.getLogger("ΛTRACE").setLevel(
            logging.INFO
        )  # Set to INFO or DEBUG for testing

    logger.info("ΛTRACE: lukhas_ai_interface.py executed as __main__ for testing.")
    logger.info("🧪 Testing Lukhas AI Interface...")

    if not ROUTER_AVAILABLE:
        logger.error(
            "ΛTRACE: AI Router not available. Cannot proceed with __main__ tests."
        )
        logger.error(
            "❌ AI Router not available. Aborting tests. Check LUKHAS_AI_ROUTER_PATH and router dependencies."
        )
        sys.exit(1)

    # Test using the LukhusAI class instance
    logger.info("\n--- Testing LukhusAI class instance (TestComponent) ---")
    ai_instance_test = LukhusAI("TestComponent")

    code_prompt = "Write a Python function to add two numbers."
    logger.info(
        f"ΛTRACE: __main__ testing code_assistance with prompt: '{code_prompt}'"
    )
    code_response = ai_instance_test.code_assistance(code_prompt, language="Python")
    logger.info(
        f"💻 Code Assistance:\nPrompt: '{code_prompt}'\nResponse (first 100 chars): {code_response[:100]}...\n"
    )

    chat_prompt = "What is the weather like today?"
    logger.info(f"ΛTRACE: __main__ testing chat with prompt: '{chat_prompt}'")
    chat_response = ai_instance_test.chat(chat_prompt)
    logger.info(
        f"💬 General Chat:\nPrompt: '{chat_prompt}'\nResponse (first 100 chars): {chat_response[:100]}...\n"
    )

    # Test using global convenience functions
    logger.info("\n--- Testing global convenience functions (LukhusQuickAccess) ---")
    docs_prompt = (
        "Explain the purpose of a class constructor in object-oriented programming."
    )
    logger.info(
        f"ΛTRACE: __main__ testing global ai_docs() with prompt: '{docs_prompt}'"
    )
    docs_response_global = ai_docs(docs_prompt)
    logger.info(
        f"📖 Documentation Assist (global):\nPrompt: '{docs_prompt}'\nResponse (first 100 chars): {docs_response_global[:100]}...\n"
    )

    research_prompt = "Who won the Nobel Prize in Physics in 2023?"
    logger.info(
        f"ΛTRACE: __main__ testing global ai_research() with prompt: '{research_prompt}'"
    )
    research_response_global = ai_research(research_prompt)
    logger.info(
        f"🌐 Web Research (global):\nPrompt: '{research_prompt}'\nResponse (first 100 chars): {research_response_global[:100]}...\n"
    )

    logger.info("ΛTRACE: __main__ tests completed.")
    logger.info("✅ Lukhas AI Interface test complete!")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lukhas_ai_interface.py
# VERSION: 1.1.0
# TIER SYSTEM: Tier 1-3 (Depends on the complexity of AI task and capabilities of the routed model)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Provides a unified interface to various AI functionalities (code, ethics, web,
#               creative, general chat, audit, documentation, analysis) via an external router.
# FUNCTIONS: ai_code, ai_audit, ai_docs, ai_chat, ai_research (convenience global functions).
# CLASSES: LukhusAITaskType (Enum for task types), LukhusAI (Main interface class).
# DECORATORS: None.
# DEPENDENCIES: sys, os, pathlib, typing, enum, logging. Critically depends on successful
#               import of 'multiverse_route' from an external AI router module.
# INTERFACES: Exports LukhusAI class and global convenience functions.
# ERROR HANDLING: Catches exceptions during AI router calls and import failures.
#                 Returns error messages as strings. Logs errors via ΛTRACE.
# LOGGING: ΛTRACE_ENABLED for interface initialization, request routing, and errors.
# AUTHENTICATION: Not handled directly; relies on the external AI router for any authentication.
# HOW TO USE:
#   from core.lukhas_ai_interface import LukhusAI, LukhusAITaskType, ai_code
#   # Using class instance
#   ai = LukhusAI(component_name="MyModule")
#   response = ai.generate_response("Explain black holes.", LukhusAITaskType.GENERAL)
#   # Using global convenience function
#   code_snippet = ai_code("Generate a regex for email validation.")
# INTEGRATION NOTES: Requires LUKHAS_AI_ROUTER_PATH environment variable to be set to the
#                    directory containing the 'router' module (for 'multiverse_route').
#                    The AI router itself must be operational.
# MAINTENANCE: Ensure LukhusAITaskType enum aligns with capabilities of `multiverse_route`.
#              Monitor the external AI router for compatibility.
#              Consider improving error reporting (e.g., structured responses).
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
