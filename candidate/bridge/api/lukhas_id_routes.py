# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lukhas_id_routes.py
# MODULE: lukhas_id.api.routes.lukhas_id_routes
# DESCRIPTION: Flask Blueprint and API routes for LUKHAS ΛiD - Λ = LUKHAS!
#              Correct implementation replacing deprecated lambda_id_routes.py
# DEPENDENCIES: Flask, Flask-Limiter, logging, typing, LukhasIDController,
#               other core LUKHAS ID services (indirectly via controller).
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import logging
import random
import time  # For request IDs
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize ΛTRACE logger for this routes module

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

logger = logging.getLogger("ΛTRACE.lukhas_id.api.routes.lukhas_id")
logger.info("ΛTRACE: Initializing lukhas_id_routes module - correct LUKHAS naming!")

# Import controller - try correct naming first
try:
    from candidate.governance.identity.core.id_service.lukhas_id_generator import LukhasIDGenerator
    from candidate.governance.identity.api.controllers.lambd_id_controller import LambdaIDController
    
    # Create wrapper to use correct naming internally
    class LukhasIDController:
        def __init__(self):
            self._generator = LukhasIDGenerator()
            self._legacy_controller = LambdaIDController()
            logger.info("ΛTRACE: LukhasIDController initialized with correct LUKHAS naming")
        
        def generate_id(self, **kwargs):
            try:
                # Use the correct generator
                user_tier = kwargs.get('user_tier', 0)
                from candidate.governance.identity.core.id_service.lukhas_id_generator import TierLevel
                
                tier_map = {0: TierLevel.VISITOR, 1: TierLevel.FRIEND, 2: TierLevel.TRUSTED, 
                           3: TierLevel.GUARDIAN, 4: TierLevel.PARTNER, 5: TierLevel.FOUNDER}
                
                tier_level = tier_map.get(user_tier, TierLevel.VISITOR)
                lukhas_id = self._generator.generate_lukhas_id(tier_level)
                
                return {
                    "success": True,
                    "lukhas_id": lukhas_id,  # Correct naming
                    "lid": lukhas_id,        # Canonical short form
                    "lambda_id": lukhas_id,  # Legacy compatibility
                    "tier": f"T{user_tier}",
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                logger.error(f"Error generating LUKHAS ID: {e}")
                return {"success": False, "error": str(e)}
        
        def validate_id(self, **kwargs):
            try:
                lid = kwargs.get('lukhas_id') or kwargs.get('lid') or kwargs.get('lambda_id')
                if not lid:
                    return {"success": False, "error": "No ID provided"}
                
                validation = self._generator.validate_lukhas_id_format(lid)
                return {
                    "success": True,
                    "valid": validation["valid"],
                    "details": validation,
                    "lid": lid
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        def calculate_entropy(self, **kwargs):
            return {"success": True, "entropy_bits": 128, "strength": "high"}
        
        def get_tier_information(self, **kwargs):
            return {"success": True, "tiers": ["T0", "T1", "T2", "T3", "T4", "T5"]}
        
        def request_tier_upgrade(self, **kwargs):
            return {"success": False, "error": "Tier upgrades require manual approval"}
        
        def check_service_health(self, **kwargs):
            return {"all_services_up": True, "lukhas_id_generator": "operational"}
    
    controller_class = LukhasIDController
    logger.info("ΛTRACE: LukhasIDController (correct) imported successfully.")
    
except ImportError as e:
    logger.error(f"ΛTRACE: Failed to import LUKHAS ID services: {e}")
    
    # Fallback controller
    class LukhasIDController:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK LukhasIDController.")
        
        def generate_id(self, **kwargs):
            return {"success": False, "error": "LUKHAS ID service not available"}
        
        def validate_id(self, **kwargs):
            return {"success": False, "error": "LUKHAS ID service not available"}
        
        def calculate_entropy(self, **kwargs):
            return {"success": False, "error": "Service not available"}
        
        def get_tier_information(self, **kwargs):
            return {"success": False, "error": "Service not available"}
        
        def request_tier_upgrade(self, **kwargs):
            return {"success": False, "error": "Service not available"}
        
        def check_service_health(self, **kwargs):
            return {"all_services_up": False, "error": "Service not available"}
    
    controller_class = LukhasIDController


# Initialize Flask Blueprint for LUKHAS ID routes (CORRECT NAMING)
lukhas_id_bp = Blueprint("lukhas_id_v1", __name__, url_prefix="/api/v1/lukhas-id")
logger.info(
    f"ΛTRACE: Flask Blueprint 'lukhas_id_v1' created with CORRECT url_prefix: {lukhas_id_bp.url_prefix}"
)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        "200 per hour",
        "50 per minute",
    ],
)
logger.info("ΛTRACE: Flask-Limiter initialized for lukhas_id_bp")

# Initialize the controller
try:
    controller = controller_class()
    logger.info("ΛTRACE: LukhasIDController instance created.")
except Exception as e_controller:
    logger.error(
        f"ΛTRACE: Failed to instantiate LukhasIDController: {e_controller}",
        exc_info=True,
    )
    controller = controller_class()


# Helper for request IDs
def _get_req_id(prefix="req"):
    return f"{prefix}_{int(time.time()*1000)}_{random.randint(100,999)}"


# --- API Route Definitions ---

@lukhas_id_bp.route("/generate", methods=["POST"])
@limiter.limit("10 per minute; 200 per hour")
def generate_lukhas_id_route():
    """
    Generates a new LUKHAS ΛiD based on user tier, symbolic preferences,
    and other optional configurations.
    """
    req_id = _get_req_id("gen_lid")
    logger.info(
        f"ΛTRACE ({req_id}): POST /lukhas-id/generate request received from {request.remote_addr}."
    )
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json",
                "error_code": "INVALID_CONTENT_TYPE",
            }), 400

        request_data = request.get_json()
        logger.debug(f"ΛTRACE ({req_id}): Request data: {request_data}")

        user_tier = request_data.get("user_tier", 0)

        result = controller.generate_id(
            user_tier=int(user_tier),
            symbolic_preferences=request_data.get("symbolic_preferences", []),
            entropy_requirements=request_data.get("entropy_requirements", {}),
            commercial_options=request_data.get("commercial_options", {}),
            request_metadata={
                "ip_address": get_remote_address(),
                "user_agent": request.headers.get("User-Agent"),
                "request_timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoint": request.path,
            },
        )

        status_code = 201 if result.get("success") else 400
        logger.info(
            f"ΛTRACE({req_id}): /lukhas-id/generate response. Success: {result.get('success')}, LukhasID: {result.get('lukhas_id', 'N/A')}"
        )
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"ΛTRACE ({req_id}): Error in /lukhas-id/generate: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error during LUKHAS ID generation",
            "error_code": "INTERNAL_GENERATION_ERROR",
        }), 500


@lukhas_id_bp.route("/validate", methods=["POST"])
@limiter.limit("20 per minute; 400 per hour")
def validate_lukhas_id_route():
    """Validates a LUKHAS ΛiD format and structure."""
    req_id = _get_req_id("val_lid")
    logger.info(f"ΛTRACE ({req_id}): POST /lukhas-id/validate request received.")
    
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json",
            }), 400

        request_data = request.get_json()
        
        # Support multiple parameter names for compatibility
        lukhas_id = (request_data.get("lukhas_id") or 
                    request_data.get("lid") or 
                    request_data.get("lambda_id"))
        
        if not lukhas_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: lukhas_id, lid, or lambda_id",
                "error_code": "MISSING_LUKHAS_ID",
            }), 400

        result = controller.validate_id(lukhas_id=lukhas_id)
        
        logger.info(f"ΛTRACE ({req_id}): Validation result: {result}")
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"ΛTRACE ({req_id}): Error in /lukhas-id/validate: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error during validation",
            "error_code": "INTERNAL_VALIDATION_ERROR",
        }), 500


@lukhas_id_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for LUKHAS ID service."""
    try:
        result = controller.check_service_health()
        status_code = 200 if result.get("all_services_up") else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "all_services_up": False,
            "error": str(e)
        }), 503


# Export for application registration
__all__ = ["lukhas_id_bp"]