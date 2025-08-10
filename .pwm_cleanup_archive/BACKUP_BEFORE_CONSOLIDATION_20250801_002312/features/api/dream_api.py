# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: dream_api.py
# MODULE: core.api.dream_api
# DESCRIPTION: Flask API for generating and retrieving symbolic dream data within the LUKHAS system.
#              Provides endpoints to trigger dream generation and fetch the latest dream state.
# DEPENDENCIES: Flask, Flask-CORS, datetime, random, logging,
#               prot2.CORE.symbolic_ai.modules.dream_generator (attempted import)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import json
import os
import random
import sys
import time  # Added for request_id
from datetime import datetime

import structlog
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize ΛTRACE logger for this module using structlog
# Assumes structlog is configured in a higher-level __init__.py (e.g., core/__init__.py)
logger = structlog.get_logger("ΛTRACE.core.api.dream_api")
logger.info("ΛTRACE: Initializing dream_api module.")

# Attempt to import the dream generator with path adjustments
# AIMPORT_TODO: The following sys.path manipulation for importing from 'prot2' is fragile and indicates a potential need for better project structure or packaging for 'prot2' modules. Consider making 'prot2' an installable package or using relative imports if it's part of the same top-level project.
try:
    from prot2.CORE.symbolic_ai.modules.dream_generator import (
        generate_symbolic_dreams,
    )

    logger.info("ΛTRACE: Successfully imported generate_symbolic_dreams from prot2.")
except ImportError as e_import:
    logger.warning(
        f"ΛTRACE: Initial import of generate_symbolic_dreams failed: {e_import}. Attempting path adjustment."
    )
    # Calculate the path to the 'prot2' directory's parent
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming this file is in core/api/, to reach project root containing 'prot2':
    # Go up from api -> CORE -> prot2_parent_dir
    prot2_project_root_parent = os.path.abspath(
        os.path.join(current_dir, "..", "..", "..")
    )

    if prot2_project_root_parent not in sys.path:
        sys.path.insert(0, prot2_project_root_parent)
        logger.info(f"ΛTRACE: Added '{prot2_project_root_parent}' to sys.path.")

    try:
        # Retry the import now that the path should be set up
        from prot2.CORE.symbolic_ai.modules.dream_generator import (
            generate_symbolic_dreams,
        )

        logger.info(
            "ΛTRACE: Successfully imported generate_symbolic_dreams after path adjustment."
        )
    except ImportError as e_retry_import:
        logger.error(
            f"ΛTRACE: Failed to import generate_symbolic_dreams even after path adjustment: {e_retry_import}",
            exc_info=True,
        )

        # Define a fallback function if import fails, so the API can still run (with limited functionality)
        def generate_symbolic_dreams(user_input: str, context_data: dict) -> list:
            logger.warning(
                "ΛTRACE: Using fallback generate_symbolic_dreams. Actual dream generation will not occur."
            )
            return [
                {
                    "id": "fallback_dream_001",
                    "summary": "Dream generator module not loaded.",
                    "user_input": user_input,
                    "context_user_sid": context_data.get("user_sid"),
                    "symbols": ["error", "fallback"],
                    "timestamp": datetime.now().isoformat(),
                }
            ]


# Initialize Flask application
app = Flask(__name__)
logger.info(f"ΛTRACE: Flask app '{__name__}' initialized for Dream API.")

# Configure CORS (Cross-Origin Resource Sharing)
CORS(app)  # Enable CORS for all routes by default
logger.info("ΛTRACE: CORS enabled for the Flask app.")

# In-memory store for the latest dream data.
# ΛNOTE: The current implementation uses an in-memory dictionary (latest_dream_data) to store the most recent dream. For production environments, this should be replaced with a persistent database (e.g., Redis, PostgreSQL, MongoDB) or a robust distributed caching mechanism to ensure data persistence, scalability, and reliability across multiple instances or restarts.
latest_dream_data: dict = {
    "status": "No dream generated yet. POST to /api/trigger_dream_generation to create one.",
    "dream": None,
    "generation_details": None,  # Will store details like input used, context SID, etc.
}
logger.debug(
    f"ΛTRACE: Initialized latest_dream_data in-memory store: {latest_dream_data}"
)


# Default context and user input for API calls if not provided.
# Simulates basic AGI context awareness for demonstration.
default_context_for_api: dict = {
    "user_sid": "api_default_user_001",
    "user_tier": 3,  # Example tier
    "timestamp": datetime.now().isoformat(),
    "detected_emotion": {
        "type": "neutral_curious",
        "intensity": random.uniform(0.3, 0.7),
    },
    "recalled_context": {
        "topic": "api_dream_visualization",
        "last_interaction_summary": "API call initiated for dream synthesis.",
    },
    "system_variables": {
        "current_focus": "api_driven_creative_synthesis",
        "cognitive_load_estimate": random.uniform(0.1, 0.5),
        "available_inspirations_sample": [
            "algorithmic_art",
            "nature_fractals",
            "conceptual_metaphors",
        ],
    },
}
logger.debug(f"ΛTRACE: Default API context initialized: {default_context_for_api}")

default_user_input_for_api: str = (
    "Synthesize a dream that is both novel and reflects the system's latent creative potential through this API."
)
logger.debug(f"ΛTRACE: Default API user input set: '{default_user_input_for_api}'")


# API Endpoint: Trigger Dream Generation
# Human-readable comment: Endpoint to trigger the generation of a new symbolic dream.
# ΛEXPOSE
@app.route("/api/trigger_dream_generation", methods=["POST"])
def trigger_dream_generation_endpoint():
    """
    Triggers the generation of a new symbolic dream based on optional user input and context.
    The generated dream data is stored in memory, overwriting any previous dream.
    """
    global latest_dream_data
    global default_context_for_api
    endpoint_path = "/api/trigger_dream_generation"
    request_id = f"dream_gen_req_{int(time.time()*1000)}"  # Simple request ID
    logger.info(f"ΛTRACE ({request_id}): Received POST request for {endpoint_path}.")

    try:
        data = (
            request.get_json(silent=True) or {}
        )  # Ensure data is a dict even if no JSON body
        user_input = data.get("user_input", default_user_input_for_api)

        # Prepare context: Start with a fresh copy of defaults, then update
        current_context = default_context_for_api.copy()
        current_context["timestamp"] = (
            datetime.now().isoformat()
        )  # Always use current time
        # Example of dynamically updating parts of default context for variety
        current_context["detected_emotion"]["intensity"] = random.uniform(0.2, 0.8)
        current_context["system_variables"]["cognitive_load_estimate"] = random.uniform(
            0.1, 0.6
        )

        # If context_data is provided in the request, merge it intelligently
        if "context_data" in data and isinstance(data["context_data"], dict):
            logger.debug(
                f"ΛTRACE ({request_id}): Merging provided context data with defaults."
            )
            for key, value in data["context_data"].items():
                if (
                    isinstance(value, dict)
                    and key in current_context
                    and isinstance(current_context[key], dict)
                ):
                    current_context[key].update(value)  # Merge sub-dictionaries
                else:
                    current_context[key] = value  # Overwrite or add new keys

        logger.info(
            f"ΛTRACE ({request_id}): Generating dream. User input (start): '{user_input[:70]}...'. Context SID: {current_context.get('user_sid')}."
        )

        # Call the core dream generation logic
        generated_dreams_list = generate_symbolic_dreams(user_input, current_context)

        if (
            generated_dreams_list
            and isinstance(generated_dreams_list, list)
            and len(generated_dreams_list) > 0
        ):
            # Store the first generated dream for this simple API
            latest_dream_data["dream"] = generated_dreams_list[0]
            latest_dream_data["status"] = (
                f"Dream generated successfully via API at {datetime.now().isoformat()}."
            )
            latest_dream_data["generation_details"] = {
                "user_input_provided": user_input,
                "context_user_sid_used": current_context.get("user_sid"),
                "total_dreams_generated_in_batch": len(generated_dreams_list),
                "selected_dream_id": generated_dreams_list[0].get("id", "N/A"),
            }
            logger.info(
                f"ΛTRACE ({request_id}): Dream generation successful. Dream ID: {latest_dream_data['generation_details']['selected_dream_id']}. Stored as latest dream."
            )
            return (
                jsonify(
                    {
                        "message": "Dream generation successful.",
                        "dream_id": latest_dream_data["generation_details"][
                            "selected_dream_id"
                        ],
                    }
                ),
                200,
            )
        else:
            logger.warning(
                f"ΛTRACE ({request_id}): Dream generation call returned no dreams or an invalid format. Loading fallback dream."
            )
            try:
                with open("dream/dream_fallback.json") as f:
                    fallback_dream = json.load(f)
                fallback_dream["timestamp"] = datetime.now().isoformat()
                latest_dream_data["dream"] = fallback_dream
                latest_dream_data["status"] = (
                    "Dream generation failed. Loaded fallback dream."
                )
                latest_dream_data["generation_details"] = {
                    "user_input_provided": user_input,
                    "context_user_sid_used": current_context.get("user_sid"),
                }
                return (
                    jsonify(
                        {"error": "Dream generation failed. Loaded fallback dream."}
                    ),
                    500,
                )
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(
                    f"ΛTRACE ({request_id}): Failed to load fallback dream: {e}",
                    exc_info=True,
                )
                return (
                    jsonify(
                        {
                            "error": "Dream generation failed and could not load fallback dream."
                        }
                    ),
                    500,
                )

    except Exception as e:
        logger.error(
            f"ΛTRACE ({request_id}): Error during dream generation at {endpoint_path}: {e}",
            exc_info=True,
        )
        latest_dream_data["status"] = (
            f"Critical error during dream generation: {str(e)}"
        )
        latest_dream_data["dream"] = None
        return (
            jsonify(
                {
                    "error": "An internal server error occurred during dream generation.",
                    "details": str(e),
                }
            ),
            500,
        )


# API Endpoint: Get Current Dream State
# Human-readable comment: Endpoint to retrieve the most recently generated symbolic dream.
# ΛEXPOSE
@app.route("/api/current_dream_state", methods=["GET"])
def get_current_dream_state_endpoint():
    """
    Retrieves the state of the most recently generated symbolic dream.
    If no dream has been generated, a placeholder status is returned.
    """
    global latest_dream_data
    endpoint_path = "/api/current_dream_state"
    request_id = f"get_dream_req_{int(time.time()*1000)}"
    logger.info(f"ΛTRACE ({request_id}): Received GET request for {endpoint_path}.")

    if latest_dream_data.get("dream"):
        logger.info(
            f"ΛTRACE ({request_id}): Returning latest generated dream. Dream ID: {latest_dream_data['dream'].get('id', 'N/A')}"
        )
        return jsonify(latest_dream_data), 200
    else:
        logger.info(
            f"ΛTRACE ({request_id}): No dream currently generated. Returning placeholder status."
        )
        # Provide a more informative placeholder if no dream exists
        placeholder_response = {
            "status": latest_dream_data.get(
                "status", "No dream has been generated yet."
            ),
            "dream": {  # A minimal valid dream structure
                "id": "placeholder_dream_state_000",
                "summary": "Awaiting dream generation. Please use the POST /api/trigger_dream_generation endpoint.",
                "complexity": 0.0,
                "clarity": 0.0,
                "emotional_profile": {"type": "none", "intensity": 0.0},
                "symbols": ["system_idle", "awaiting_input"],
                "visual_elements": [
                    {"type": "empty_canvas", "description": "No dream visualized."}
                ],
                "timestamp": datetime.now().isoformat(),
            },
            "generation_details": None,
        }
        return (
            jsonify(placeholder_response),
            200,
        )  # Still 200 OK, as the state is "no dream"


# Main execution block for running the Flask development server
if __name__ == "__main__":
    logger.info(
        "ΛTRACE: dream_api.py is being run directly. Configuring and starting Flask development server."
    )
    # Configuration for host and port, allowing environment variable overrides
    api_host = os.environ.get("LUKHAS_DREAM_API_HOST", "0.0.0.0")
    api_port = int(
        os.environ.get("LUKHAS_DREAM_API_PORT", 5002)
    )  # Using a different port
    debug_mode = os.environ.get("LUKHAS_DREAM_API_DEBUG", "True").lower() in [
        "true",
        "1",
        "yes",
    ]

    logger.info(
        f"🚀 LUKHAS Dream API Server attempting to start on http://{api_host}:{api_port}/ (Debug: {debug_mode})"
    )
    logger.info(
        "🌠 Endpoints available: POST /api/trigger_dream_generation, GET /api/current_dream_state"
    )

    try:
        app.run(debug=debug_mode, port=api_port, host=api_host)
    except Exception as e_server:
        logger.critical(
            f"ΛTRACE: Failed to start Flask server: {e_server}", exc_info=True
        )
        print(f"❌ Failed to start LUKHAS Dream API server: {e_server}")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: dream_api.py
# VERSION: 1.1.0 # Updated version
# TIER SYSTEM: Tier 1-2 (Basic dream generation and retrieval)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: API for triggering symbolic dream generation, API for retrieving current dream state.
# FUNCTIONS: trigger_dream_generation_endpoint, get_current_dream_state_endpoint.
# CLASSES: None defined directly in this file (uses Flask app).
# DECORATORS: @app.route.
# DEPENDENCIES: Flask, Flask-CORS, datetime, random, logging, os, sys,
#               prot2.CORE.symbolic_ai.modules.dream_generator.
# INTERFACES: Exposes RESTful HTTP endpoints.
# ERROR HANDLING: try-except blocks in endpoint handlers, returns JSON error responses.
#                 Fallback for dream_generator import.
# LOGGING: ΛTRACE_ENABLED via Python's logging module for API requests, dream generation
#          process, errors, and server startup.
# AUTHENTICATION: Not explicitly implemented in these simple endpoints (would require
#                 integration with an identity client like in api_controllers.py).
# HOW TO USE:
#   Run this script: python core/api/dream_api.py
#   POST to /api/trigger_dream_generation (JSON body optional for user_input/context_data).
#   GET /api/current_dream_state to retrieve the latest dream.
# INTEGRATION NOTES: Relies on 'prot2.CORE.symbolic_ai.modules.dream_generator'.
#                    Path adjustments are made for this import; review for robustness.
#                    Currently uses in-memory storage for 'latest_dream_data'.
# MAINTENANCE: Update import paths if project structure changes.
#              Consider persistent storage for 'latest_dream_data' for production.
#              Implement proper authentication and authorization for production use.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
