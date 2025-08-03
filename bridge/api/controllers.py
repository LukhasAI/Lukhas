# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: api_controllers.py
# MODULE: core.api_controllers
# DESCRIPTION: Provides REST API controllers for LUKHAS AGI system modules,
#              exposing services via HTTP with authentication and error handling.
# DEPENDENCIES: Flask, functools, os, sys, typing, datetime, traceback, logging,
#               various AGI module services (ethics, memory, etc.), IdentityClient.
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify
from functools import wraps
import os
import sys
from typing import Dict, Any, Optional, Callable  # Added Callable
from datetime import datetime
import traceback
import structlog  # Changed from logging

# Initialize logger for ΛTRACE using structlog
# Assumes structlog is configured in a higher-level __init__.py (e.g., core/__init__.py)

# Import service registry to get learning service without circular dependency
from orchestration.service_registry import get_service, ServiceNames
from orchestration.learning_initializer import initialize_learning_service  # Ensures service is registered


#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


def _get_learning_service():
    """Get learning service from registry to avoid circular dependency."""
    service = get_service(ServiceNames.LEARNING)
    if service is None:
        logger.error("ΛTRACE: Learning service not available in registry")
        # Return a callable that returns the fallback service to maintain compatibility
        from .fallback_services import FallbackLearningService
        return lambda: FallbackLearningService()
    # Return a callable that returns the service to maintain compatibility with existing code
    return lambda: service


logger = structlog.get_logger("ΛTRACE.core.api_controllers")
logger.info("ΛTRACE: Initializing api_controllers module.")

# Add parent directory for imports if necessary, though direct relative imports are preferred.
# This line might be problematic if 'core' is not the immediate parent of where this runs.
# Consider structuring imports to avoid sys.path manipulation if possible.
# sys.path.insert(0, os.path.dirname(__file__)) # Commented out, assuming standard Python path mechanisms

# Import module services
# It's good practice to have these services clearly defined and importable.
# The fallback classes are useful for development if services are not yet available.
# AIMPORT_TODO: Review the direct imports for AGI services (EthicsService, MemoryService, etc.). For robustness and clearer dependency management in production, consider structuring these services as part of an installable package or ensuring consistent relative import paths if they belong to the same top-level project structure. The current direct imports might rely on specific PYTHONPATH configurations.
try:
    # Assuming these modules are structured to be importable, e.g., they are in PYTHONPATH
    # or installed as part of a larger package.
    # For example: from core_modules.ethics.ethics_service import EthicsService
    # For now, using the provided relative-like import paths.
    from ethics.ethics_service import EthicsService
    from memory.memory_service import MemoryService
    from creativity.creativity_service import CreativityService
    from consciousness.consciousness_service import ConsciousnessService
    # Learning service is now obtained through the service registry
    from quantum.quantum_service import QuantumService
    from identity.interface import IdentityClient  # Needs to be a defined interface

    logger.info("ΛTRACE: Successfully imported AGI module services and IdentityClient.")
except ImportError as e:
    logger.warning(
        f"ΛTRACE: Some AGI module service imports failed: {e}. Using fallback classes for development."
    )
    # ΛCORE: Import fallback services from dedicated module
    from .fallback_services import (
        FallbackEthicsService as EthicsService,
        FallbackMemoryService as MemoryService,
        FallbackCreativityService as CreativityService,
        FallbackConsciousnessService as ConsciousnessService,
        FallbackLearningService as LearningService,
        FallbackQuantumService as QuantumService,
        FallbackIdentityClient as IdentityClient,
    )

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "LUKHAS_API_SECRET", "default_dev_secret_key_please_change"
)  # Changed default
logger.info(
    f"ΛTRACE: Flask app '{__name__}' initialized. SECRET_KEY {'is set from ENV' if 'LUKHAS_API_SECRET' in os.environ else 'is default'}."
)

# Initialize services
# ΛNOTE: Service initialization is basic (direct instantiation). For production and larger systems, consider using a dependency injection framework (e.g., `python-dependency-injector`) or a service locator pattern. This would improve testability, configurability, and decoupling of components. Fallback services are used if primary service imports fail.
ethics_service = EthicsService()
memory_service = MemoryService()
creativity_service = CreativityService()
consciousness_service = ConsciousnessService()
# Get learning service from registry through the lazy getter
learning_service_getter = _get_learning_service()
learning_service = learning_service_getter()
quantum_service = QuantumService()
identity_client = IdentityClient()  # This client handles auth and activity logging
logger.info("ΛTRACE: All AGI module services initialized (potentially fallbacks).")

# API Configuration
API_VERSION = "v1.0.0"  # More semantic versioning
BASE_PATH = f"/api/{API_VERSION}"
logger.info(f"ΛTRACE: API configured. Version: {API_VERSION}, Base Path: {BASE_PATH}")


# Authentication Decorator
# AIDENTITY: This decorator handles authentication by checking 'X-User-ID' and authorization against required LUKHAS tiers using an IdentityClient. It logs access attempts and outcomes.
def require_auth(required_tier: str = "LAMBDA_TIER_1") -> Callable:
    """
    Decorator factory to enforce authentication and tier-based authorization for API endpoints.
    Logs access attempts using ΛTRACE via identity_client.
    Args:
        required_tier (str): The minimum LUKHAS tier required to access the endpoint.
    Returns:
        Callable: The decorator function.
    """

    # This is the actual decorator
    def decorator(f: Callable) -> Callable:
        @wraps(f)  # Preserves metadata of the decorated function
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            endpoint_name = request.path
            user_id = request.headers.get("X-User-ID")
            logger.info(
                f"ΛTRACE: Auth attempt for endpoint '{endpoint_name}'. User-ID from header: '{user_id}', Required Tier: '{required_tier}'."
            )

            if not user_id:
                logger.warning(
                    f"ΛTRACE: Auth failed for '{endpoint_name}': Missing X-User-ID header."
                )
                identity_client.log_activity(
                    "auth_failure_missing_uid",
                    "anonymous",
                    {
                        "endpoint": endpoint_name,
                        "required_tier": required_tier,
                        "reason": "Missing X-User-ID",
                    },
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required: Missing X-User-ID header.",
                            "error_code": "AUTH_MISSING_USER_ID",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    ),
                    401,
                )

            # Verify user access tier
            if not identity_client.verify_user_access(user_id, required_tier):
                logger.warning(
                    f"ΛTRACE: Auth failed for '{endpoint_name}': User '{user_id}' has insufficient tier for '{required_tier}'."
                )
                identity_client.log_activity(
                    "auth_failure_insufficient_tier",
                    user_id,
                    {
                        "endpoint": endpoint_name,
                        "required_tier": required_tier,
                        "reason": "Insufficient tier",
                    },
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Access denied: Insufficient tier. Required: {required_tier}.",
                            "error_code": "AUTH_INSUFFICIENT_TIER",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    ),
                    403,
                )

            # Add user_id to request context for use in the endpoint function
            request.user_id = user_id  # type: ignore # Flask's request is dynamic
            logger.info(
                f"ΛTRACE: Auth success for '{endpoint_name}': User '{user_id}' granted access for tier '{required_tier}'."
            )
            identity_client.log_activity(
                "auth_success",
                user_id,
                {"endpoint": endpoint_name, "required_tier": required_tier},
            )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Standardized API Error Handling Function
def handle_api_error(
    error: Exception, endpoint: str, user_id: Optional[str]
) -> Dict[str, Any]:
    """
    Centralized error handling for API endpoints. Logs the error using ΛTRACE
    and returns a standardized JSON error response.
    Args:
        error (Exception): The exception that occurred.
        endpoint (str): The API endpoint path where the error occurred.
        user_id (Optional[str]): The ID of the user making the request, if available.
    Returns:
        Dict[str, Any]: A standardized error response dictionary.
    """
    error_message = str(error)
    error_type_name = type(error).__name__
    detailed_traceback = traceback.format_exc()

    log_user_id = user_id if user_id else "unknown_or_pre_auth"
    logger.error(
        f"ΛTRACE: API Error at endpoint '{endpoint}'. User: '{log_user_id}'. Type: {error_type_name}. Message: {error_message}. Traceback: {detailed_traceback}"
    )

    # Log error activity via IdentityClient (which should also use ΛTRACE)
    identity_client.log_activity(
        "api_internal_error",
        log_user_id,
        {
            "endpoint": endpoint,
            "error_message": error_message,
            "error_type": error_type_name,
            "timestamp": datetime.utcnow().isoformat(),
            # "traceback_snippet": detailed_traceback.splitlines()[-3:] # Example snippet
        },
    )

    # Standardized error response structure
    return {
        "success": False,
        "error": f"An internal error occurred: {error_message}",
        "error_code": "API_INTERNAL_SERVER_ERROR",
        "endpoint_errored": endpoint,
        "error_details": {
            "type": error_type_name
        },  # Avoid exposing full traceback in response for security
        "timestamp": datetime.utcnow().isoformat(),
    }


# Helper to get user_id from request, defaulting for logging if not present
def get_request_user_id() -> str:
    return getattr(request, "user_id", "anonymous_or_internal")


# ===============================
# ETHICS MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Ethics module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/ethics/assess", methods=["POST"])
@require_auth("LAMBDA_TIER_1")  # Example tier
def ethics_assess_action_endpoint():  # Renamed for clarity
    """Assess ethical implications of a proposed action or scenario."""
    endpoint_path = "/ethics/assess"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "action" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'action'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'action' in request body.",
                        "error_code": "REQUEST_MISSING_ACTION",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling ethics_service.assess_action for user '{user_id}', action: '{data['action']}'."
        )
        result = ethics_service.assess_action(
            user_id,
            data["action"],
            data.get("context", {}),
            data.get("assessment_type", "comprehensive"),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for checking compliance with ethical guidelines.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/ethics/compliance", methods=["POST"])
@require_auth("LAMBDA_TIER_2")  # Example tier
def ethics_check_compliance_endpoint():  # Renamed for clarity
    """Check a proposal or system design for compliance with ethical guidelines."""
    endpoint_path = "/ethics/compliance"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "proposal" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'proposal'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'proposal' in request body.",
                        "error_code": "REQUEST_MISSING_PROPOSAL",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling ethics_service.check_compliance for user '{user_id}'."
        )
        result = ethics_service.check_compliance(
            user_id,
            data["proposal"],
            data.get("guidelines", []),
            data.get("compliance_level", "standard"),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# MEMORY MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Memory module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/memory/store", methods=["POST"])
@require_auth("LAMBDA_TIER_1")
def memory_store_item_endpoint():  # Renamed
    """Store an item (e.g., text, data) in the AGI's memory system."""
    endpoint_path = "/memory/store"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "content" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'content'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'content' in request body.",
                        "error_code": "REQUEST_MISSING_CONTENT",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling memory_service.store_memory for user '{user_id}'."
        )
        result = memory_service.store_memory(
            user_id,
            data["content"],
            data.get("memory_type", "general"),
            data.get("access_level", "user"),
            data.get("metadata", {}),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for retrieving a specific memory item.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/memory/retrieve/<memory_id>", methods=["GET"])
@require_auth("LAMBDA_TIER_1")
def memory_retrieve_item_endpoint(memory_id: str):  # Renamed
    """Retrieve a specific memory item by its ID."""
    endpoint_path = f"/memory/retrieve/{memory_id}"
    user_id = get_request_user_id()
    logger.info(
        f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'. Memory ID: {memory_id}."
    )
    try:
        logger.debug(
            f"ΛTRACE: Calling memory_service.retrieve_memory for user '{user_id}', memory_id '{memory_id}'."
        )
        result = memory_service.retrieve_memory(user_id, memory_id)
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for searching memory items.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/memory/search", methods=["POST"])
@require_auth("LAMBDA_TIER_1")
def memory_search_items_endpoint():  # Renamed
    """Search stored memories based on a query and optional filters."""
    endpoint_path = "/memory/search"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "query" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'query'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'query' in request body.",
                        "error_code": "REQUEST_MISSING_QUERY",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling memory_service.search_memory for user '{user_id}', query: '{data['query']}'."
        )
        result = memory_service.search_memory(
            user_id,
            data["query"],
            data.get("search_type", "semantic"),
            data.get("limit", 10),
            data.get("filters", {}),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# CREATIVITY MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Creativity module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/creativity/generate", methods=["POST"])
@require_auth("LAMBDA_TIER_1")
def creativity_generate_content_endpoint():  # Renamed
    """Generate various types of creative content based on a prompt."""
    endpoint_path = "/creativity/generate"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "content_type" not in data or "prompt" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'content_type' or 'prompt'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'content_type' or 'prompt' in request body.",
                        "error_code": "REQUEST_MISSING_CREATIVITY_FIELDS",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling creativity_service.generate_content for user '{user_id}', type: '{data['content_type']}'."
        )
        result = creativity_service.generate_content(
            user_id,
            data["content_type"],
            data["prompt"],
            data.get("style"),
            data.get("parameters", {}),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for synthesizing dream-like content.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/creativity/dream", methods=["POST"])
@require_auth("LAMBDA_TIER_3")  # Higher tier for specialized function
def creativity_synthesize_dream_endpoint():  # Renamed
    """Synthesize dream-like narratives or content based on input data."""
    endpoint_path = "/creativity/dream"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if (
            not data or "dream_data" not in data
        ):  # Assuming 'dream_data' is the key input
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'dream_data'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'dream_data' in request body.",
                        "error_code": "REQUEST_MISSING_DREAM_DATA",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling creativity_service.synthesize_dream for user '{user_id}'."
        )
        result = creativity_service.synthesize_dream(
            user_id, data["dream_data"], data.get("synthesis_type", "narrative")
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# CONSCIOUSNESS MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Consciousness module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/consciousness/awareness", methods=["POST"])
@require_auth("LAMBDA_TIER_1")
def consciousness_process_awareness_endpoint():  # Renamed
    """Process an incoming stream of data for consciousness awareness modeling."""
    endpoint_path = "/consciousness/awareness"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "input_stream" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'input_stream'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'input_stream' in request body.",
                        "error_code": "REQUEST_MISSING_AWARENESS_STREAM",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling consciousness_service.process_awareness for user '{user_id}'."
        )
        result = consciousness_service.process_awareness(
            user_id,
            data["input_stream"],
            data.get("awareness_level", "basic_awareness"),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for performing introspective analysis.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/consciousness/introspect", methods=["POST"])
@require_auth("LAMBDA_TIER_2")
def consciousness_perform_introspection_endpoint():  # Renamed
    """Initiate an introspective analysis process on a specified focus area."""
    endpoint_path = "/consciousness/introspect"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "focus_area" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'focus_area'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'focus_area' in request body.",
                        "error_code": "REQUEST_MISSING_INTROSPECTION_FOCUS",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling consciousness_service.introspect for user '{user_id}', focus: '{data['focus_area']}'."
        )
        result = consciousness_service.introspect(
            user_id,
            data["focus_area"],
            data.get("depth", 0.5),
            data.get("introspection_type", "self_reflection"),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for retrieving the current consciousness state.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/consciousness/state", methods=["GET"])
@require_auth("LAMBDA_TIER_1")
def consciousness_get_state_endpoint():  # Renamed
    """Retrieve the current state of the consciousness model."""
    endpoint_path = "/consciousness/state"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        include_detailed_str = request.args.get("detailed", "false", type=str)
        include_detailed = include_detailed_str.lower() == "true"
        logger.debug(
            f"ΛTRACE: Calling consciousness_service.get_consciousness_state for user '{user_id}', detailed: {include_detailed}."
        )
        result = consciousness_service.get_consciousness_state(
            user_id, include_detailed
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# LEARNING MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Learning module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/learning/learn", methods=["POST"])
@require_auth("LAMBDA_TIER_1")
def learning_learn_from_data_endpoint():  # Renamed
    """Initiate a learning process from a specified data source."""
    endpoint_path = "/learning/learn"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "data_source" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'data_source'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'data_source' in request body.",
                        "error_code": "REQUEST_MISSING_LEARNING_DATA",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling learning_service.learn_from_data for user '{user_id}'."
        )
        result = learning_service.learn_from_data(
            user_id,
            data["data_source"],
            data.get("learning_mode", "supervised"),
            data.get("learning_objectives", []),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for adapting behavior based on context.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/learning/adapt", methods=["POST"])
@require_auth("LAMBDA_TIER_2")
def learning_adapt_behavior_endpoint():  # Renamed
    """Adapt AGI behavior based on provided context and target behaviors."""
    endpoint_path = "/learning/adapt"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if (
            not data
            or "adaptation_context" not in data
            or "behavior_targets" not in data
        ):
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'adaptation_context' or 'behavior_targets'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'adaptation_context' or 'behavior_targets' in request body.",
                        "error_code": "REQUEST_MISSING_ADAPTATION_FIELDS",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling learning_service.adapt_behavior for user '{user_id}'."
        )
        result = learning_service.adapt_behavior(
            user_id,
            data["adaptation_context"],
            data["behavior_targets"],
            data.get("adaptation_strategy", "gradual"),
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# QUANTUM MODULE API ENDPOINTS
# ===============================
# Human-readable comment: Endpoints for interacting with the Quantum module.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/quantum/compute", methods=["POST"])
@require_auth("LAMBDA_TIER_3")  # Higher tier for quantum computation
def quantum_perform_computation_endpoint():  # Renamed
    """Execute a quantum algorithm with specified input qubits and gates."""
    endpoint_path = "/quantum/compute"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "algorithm" not in data or "input_qubits" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'algorithm' or 'input_qubits'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'algorithm' or 'input_qubits' in request body.",
                        "error_code": "REQUEST_MISSING_QUANTUM_COMPUTE_FIELDS",
                    }
                ),
                400,
            )

        # Validate and convert input_qubits to complex numbers
        try:
            # This list comprehension handles numbers directly or dicts like {'real': x, 'imag': y}
            qubits = [
                (
                    complex(q_val)
                    if isinstance(q_val, (int, float))
                    else complex(q_val["real"], q_val["imag"])
                )
                for q_val in data["input_qubits"]
            ]
            logger.debug(f"ΛTRACE: Parsed input_qubits: {qubits}")
        except (KeyError, ValueError, TypeError) as q_err:
            logger.warning(
                f"ΛTRACE: Invalid qubit format in request to {endpoint_path} from user '{user_id}': {q_err}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid qubit format. Each qubit must be a number or a dict {'real': x, 'imag': y}.",
                        "error_code": "INVALID_QUBIT_FORMAT",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling quantum_service.quantum_compute for user '{user_id}', algorithm: '{data['algorithm']}'."
        )
        result = quantum_service.quantum_compute(
            user_id,
            data["algorithm"],
            qubits,
            data.get("quantum_gates"),  # quantum_gates is optional
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# Human-readable comment: Endpoint for creating entanglement-like correlation.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/quantum/entangle", methods=["POST"])
@require_auth("LAMBDA_TIER_4")  # Highest tier for advanced quantum operations
def quantum_create_entanglement_endpoint():  # Renamed
    """Create entanglement-like correlation between specified target systems."""
    endpoint_path = "/quantum/entangle"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    try:
        data = request.get_json()
        if not data or "entanglement_type" not in data or "target_systems" not in data:
            logger.warning(
                f"ΛTRACE: Bad request to {endpoint_path} from user '{user_id}': Missing 'entanglement_type' or 'target_systems'."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Missing 'entanglement_type' or 'target_systems' in request body.",
                        "error_code": "REQUEST_MISSING_ENTANGLEMENT_FIELDS",
                    }
                ),
                400,
            )

        logger.debug(
            f"ΛTRACE: Calling quantum_service.quantum_entangle for user '{user_id}', type: '{data['entanglement_type']}'."
        )
        result = quantum_service.quantum_entangle(
            user_id,
            data["entanglement_type"],
            data["target_systems"],
            data.get("entanglement_strength", 1.0),  # Default strength
        )
        logger.info(
            f"ΛTRACE: Response for {endpoint_path} (user '{user_id}'): {result}"
        )
        return jsonify(result)

    except Exception as e:
        error_response = handle_api_error(e, endpoint_path, user_id)
        return jsonify(error_response), 500


# ===============================
# SYSTEM STATUS AND HEALTH
# ===============================
# Human-readable comment: General system health and information endpoints.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/health", methods=["GET"])
def system_health_check_endpoint():  # Renamed
    """Provides a basic health check of the API server and connected modules."""
    endpoint_path = f"{BASE_PATH}/health"
    logger.info(f"ΛTRACE: Request received for {endpoint_path} (health check).")
    # Basic check, can be expanded to ping services
    health_status = {
        "success": True,
        "status": "healthy",
        "api_version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "module_statuses": {  # Example, could be dynamic
            "ethics": "available",
            "memory": "available",
            "creativity": "available",
            "consciousness": "available",
            "learning": "available",
            "quantum": "available",
            "identity_client": "available",
        },
    }
    logger.info(f"ΛTRACE: Health check response: {health_status}")
    return jsonify(health_status)


# Human-readable comment: Endpoint for API information.
# ΛEXPOSE
@app.route(f"{BASE_PATH}/info", methods=["GET"])
@require_auth("LAMBDA_TIER_1")  # Basic info might still need some auth
def system_api_info_endpoint():  # Renamed
    """Returns information about the API, its version, and available module endpoints."""
    endpoint_path = f"{BASE_PATH}/info"
    user_id = get_request_user_id()
    logger.info(f"ΛTRACE: Request received for {endpoint_path} by user '{user_id}'.")
    api_info_data = {
        "success": True,
        "api_name": "LUKHAS AGI API",
        "api_version": API_VERSION,
        "base_path": BASE_PATH,
        "timestamp": datetime.utcnow().isoformat(),
        "module_endpoints": {
            "ethics": {
                "base": "/ethics",
                "endpoints": ["/assess (POST)", "/compliance (POST)"],
                "description": "Ethical assessment and compliance.",
            },
            "memory": {
                "base": "/memory",
                "endpoints": [
                    "/store (POST)",
                    "/retrieve/<id> (GET)",
                    "/search (POST)",
                ],
                "description": "Memory operations.",
            },
            "creativity": {
                "base": "/creativity",
                "endpoints": ["/generate (POST)", "/dream (POST)"],
                "description": "Creative content generation.",
            },
            "consciousness": {
                "base": "/consciousness",
                "endpoints": [
                    "/awareness (POST)",
                    "/introspect (POST)",
                    "/state (GET)",
                ],
                "description": "Consciousness modeling.",
            },
            "learning": {
                "base": "/learning",
                "endpoints": ["/learn (POST)", "/adapt (POST)"],
                "description": "Learning and adaptation.",
            },
            "quantum": {
                "base": "/quantum",
                "endpoints": ["/compute (POST)", "/entangle (POST)"],
                "description": "Quantum-inspired processing.",
            },
        },
        "authentication_details": {
            "method": "HTTP Header",
            "header_name": "X-User-ID",
            "tier_system_info": "LUKHAS Lambda Tiers (e.g., LAMBDA_TIER_1 to LAMBDA_TIER_5)",
        },
    }
    logger.info(f"ΛTRACE: API info response for user '{user_id}': {api_info_data}")
    return jsonify(api_info_data)


# ===============================
# FLASK ERROR HANDLERS
# ===============================
# Human-readable comment: Standard Flask error handlers for 404, 405, 500.
@app.errorhandler(404)
def handle_not_found_error(
    error: Exception,
) -> Any:  # error type is werkzeug.exceptions.NotFound
    """Handles 404 Not Found errors with a standardized JSON response."""
    logger.warning(
        f"ΛTRACE: 404 Not Found error at path '{request.path}'. Error: {error}"
    )
    return (
        jsonify(
            {
                "success": False,
                "error": "The requested API endpoint was not found.",
                "error_code": "ENDPOINT_NOT_FOUND",
                "path": request.path,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        404,
    )


@app.errorhandler(405)
def handle_method_not_allowed_error(
    error: Exception,
) -> Any:  # error type is werkzeug.exceptions.MethodNotAllowed
    """Handles 405 Method Not Allowed errors with a standardized JSON response."""
    logger.warning(
        f"ΛTRACE: 405 Method Not Allowed error for method '{request.method}' at path '{request.path}'. Error: {error}"
    )
    return (
        jsonify(
            {
                "success": False,
                "error": f"The method '{request.method}' is not allowed for this endpoint.",
                "error_code": "METHOD_NOT_ALLOWED",
                "path": request.path,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        405,
    )


@app.errorhandler(500)
def handle_internal_server_error(
    error: Exception,
) -> Any:  # Catches general internal server errors
    """Handles 500 Internal Server Errors with a standardized JSON response."""
    # Note: This is a generic 500 handler. Specific endpoint errors are caught by `handle_api_error`.
    # This will catch unhandled exceptions within Flask routing or before endpoint logic fully engages.
    user_id_for_log = request.headers.get("X-User-ID", "unknown_or_pre_auth")
    logger.critical(
        f"ΛTRACE: Unhandled 500 Internal Server Error at path '{request.path}' for user '{user_id_for_log}'. Error: {error}. Traceback: {traceback.format_exc()}"
    )
    identity_client.log_activity(  # Log critical failure
        "api_unhandled_critical_error",
        user_id_for_log,
        {
            "path": request.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
        },
    )
    return (
        jsonify(
            {
                "success": False,
                "error": "An unexpected internal server error occurred. The LUKHAS team has been notified.",
                "error_code": "UNHANDLED_INTERNAL_SERVER_ERROR",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        500,
    )


# Main execution block for running the Flask development server
if __name__ == "__main__":
    logger.info(
        "ΛTRACE: api_controllers.py is being run directly. Starting Flask development server."
    )
    # Development server settings
    host_setting = os.environ.get("LUKHAS_API_HOST", "0.0.0.0")
    port_setting = int(
        os.environ.get("LUKHAS_API_PORT", 5001)
    )  # Changed default port to avoid common conflicts
    debug_setting = os.environ.get("LUKHAS_DEBUG_MODE", "False").lower() in [
        "true",
        "1",
        "yes",
    ]

    logger.info(
        f"🚀 LUKHAS AGI API Server starting on {host_setting}:{port_setting} (Debug: {debug_setting})..."
    )
    logger.info(f"🔗 API Base Path: {BASE_PATH}")
    logger.info(f"🔑 Authentication expected via 'X-User-ID' header.")
    logger.info(f"🩺 Health Check endpoint available at: {BASE_PATH}/health")

    # It's generally recommended not to use Flask's built-in server for production.
    # Use a production-grade WSGI server like Gunicorn or uWSGI instead.
    app.run(host=host_setting, port=port_setting, debug=debug_setting)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: api_controllers.py
# VERSION: 1.1.0
# TIER SYSTEM: Endpoints specify required LAMBDA_TIER (e.g., LAMBDA_TIER_1 to LAMBDA_TIER_4)
# ΛTRACE INTEGRATION: ENABLED (Extensive logging for requests, auth, errors, and operations)
# CAPABILITIES: Provides HTTP API endpoints for Ethics, Memory, Creativity, Consciousness,
#               Learning, and Quantum modules. Includes system health and info endpoints.
# FUNCTIONS: require_auth (decorator), handle_api_error, get_request_user_id,
#            plus numerous Flask route handler functions.
# CLASSES: Fallback service classes (EthicsService, MemoryService, etc.) for development.
# DECORATORS: @app.route, @require_auth, @wraps, @app.errorhandler.
# DEPENDENCIES: Flask, functools, os, sys, typing, datetime, traceback, logging, AGI services.
# INTERFACES: Exposes RESTful HTTP endpoints.
# ERROR HANDLING: Centralized via handle_api_error and Flask's @app.errorhandler.
# LOGGING: ΛTRACE_ENABLED using Python's logging module for API lifecycle and operations.
# AUTHENTICATION: Via X-User-ID header and tier checking, managed by IdentityClient.
# HOW TO USE:
#   Run this script (e.g., python core/api_controllers.py).
#   Send HTTP requests to endpoints like /api/v1.0.0/ethics/assess (POST).
#   Include 'X-User-ID' header for authentication.
# INTEGRATION NOTES: Assumes AGI service classes (EthicsService, etc.) and IdentityClient
#                    are correctly implemented and importable. Service initialization is basic;
#                    consider a more robust DI or service location pattern for production.
# MAINTENANCE: Update endpoint definitions, required tiers, and request/response structures
#              as AGI module services evolve. Ensure fallback classes are kept minimal
#              and only for dev convenience if real services are unavailable.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
