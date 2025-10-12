# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lambd_id_controller.py
# MODULE: lukhas_id.api.controllers.lambd_id_controller
# DESCRIPTION: Controller for LUKHAS ΛiD (Lambda ID) operations, handling business logic
#              and orchestrating calls to core identity services.
# DEPENDENCIES: json, logging, datetime, typing, pathlib,
#               ...core.id_service modules, ...core.tier.tier_manager, ...core.trace.activity_logger
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Initialize ΛTRACE logger for this controller
# Note: The class will create a child logger for its instance.
logger = logging.getLogger("ΛTRACE.lukhas_id.api.controllers.lambd_id_controller")
logger.info("ΛTRACE: Initializing lambd_id_controller module.")

# Attempt to import core LUKHAS services
try:
    from ...core.id_service.lambd_id_entropy import EntropyCalculator
    from ...core.id_service.lambd_id_generator import LambdaIDGenerator
    from ...core.id_service.lambd_id_validator import LambdaIDValidator

    # Renamed for clarity if TierManager is generic
    from ...core.tier.tier_manager import LambdaTierManager

    # Assuming this is the ΛTRACE compatible logger
    from ...core.trace.activity_logger import ActivityLogger

    LUKHAS_SERVICES_AVAILABLE = True
    logger.info("ΛTRACE: Core LUKHAS ID services imported successfully for LambdaIDController.")
except ImportError as e:
    logger.error(
        f"ΛTRACE: CRITICAL - Failed to import core LUKHAS ID services for LambdaIDController: {e}. Controller will be non-functional.",
        exc_info=True,
    )
    LUKHAS_SERVICES_AVAILABLE = False
    # Define fallback classes so the file can be parsed, but operations will fail

    class LambdaIDGenerator:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK LambdaIDGenerator.")

        def generate(self, **kwargs):
            return "fallback_id_error"

    class LambdaIDValidator:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK LambdaIDValidator.")

        def validate_format(self, lid):
            return {"valid": False, "reason": "Validator not loaded"}

    class EntropyCalculator:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK EntropyCalculator.")

        def calculate_entropy(self, **kwargs):
            return 0.0

        def calculate_id_entropy(self, lid):
            return 0.0

        def get_entropy_breakdown(self, *args):
            return {}

    class LambdaTierManager:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK LambdaTierManager.")

        def get_tier_info(self, tier):
            return {}

        def get_progression_map(self):
            return {}

        def validate_upgrade_eligibility(self, ct, tt, vd):
            return {"eligible": False, "reason": "TierManager not loaded"}

    class ActivityLogger:
        def __init__(self):
            logger.error("ΛTRACE: Using FALLBACK ActivityLogger.")

        def log_activity(self, **kwargs):
            pass


# Human-readable comment: Controller class for managing Lambda ID operations.
class LambdaIDController:
    """
    Controller for LUKHAS ΛiD (Lambda ID) operations.
    This class encapsulates the business logic for generating, validating,
    and managing ΛiDs, interacting with various core services.
    """

    # Human-readable comment: Initializes the LambdaIDController and its
    # dependent services.
    def __init__(self):
        """
        Initializes the LambdaIDController, setting up core service dependencies
        (ID generator, validator, entropy calculator, tier manager, activity logger)
        and loading necessary configurations.
        """
        self.logger = logger.getChild("LambdaIDControllerInstance")  # Instance-specific logger
        self.logger.info("ΛTRACE: Initializing LambdaIDController instance.")

        if not LUKHAS_SERVICES_AVAILABLE:
            self.logger.critical(
                "ΛTRACE: Core LUKHAS services are not available. LambdaIDController may not function correctly."
            )
            # Initialize with fallback services to prevent further errors on attribute
            # access
            self.id_generator: LambdaIDGenerator = LambdaIDGenerator()
            self.id_validator: LambdaIDValidator = LambdaIDValidator()
            self.entropy_calculator: EntropyCalculator = EntropyCalculator()
            self.tier_manager: LambdaTierManager = LambdaTierManager()
            # This should be the ΛTRACE compatible one
            self.activity_logger: ActivityLogger = ActivityLogger()
        else:
            self._init_core_services()  # This method will log its own success/failure

        self._load_configuration()  # This method will log its own success/failure

        self.logger.info("ΛTRACE: LambdaIDController instance initialized.")

    # Human-readable comment: Private method to initialize core service dependencies.
    def _init_core_services(self) -> None:
        """Initializes all required core LUKHAS service dependencies."""
        self.logger.debug("ΛTRACE: Attempting to initialize core services for LambdaIDController.")
        try:
            self.id_generator = LambdaIDGenerator()
            self.id_validator = LambdaIDValidator()
            self.entropy_calculator = EntropyCalculator()
            self.tier_manager = LambdaTierManager()  # Using renamed class
            self.activity_logger = ActivityLogger()  # This is the activity logger for ΛiD operations

            self.logger.info("ΛTRACE: All core services for LambdaIDController initialized successfully.")

        except Exception as e:
            self.logger.error(f"ΛTRACE: Failed to initialize one or more core services: {e}", exc_info=True)
            # Depending on policy, could re-raise or set flags indicating degraded
            # functionality
            raise RuntimeError(f"LambdaIDController core service initialization failed: {e}") from e

    # Human-readable comment: Private method to load tier permissions and
    # other configurations.
    def _load_configuration(self) -> None:
        """Loads tier permissions and other necessary configurations from json_file or defaults."""
        self.logger.debug("ΛTRACE: Attempting to load tier permissions configuration.")
        try:
            # Path relative to this file: controllers -> api -> lukhas-id -> core -> id_service -> tier_permissions.json
            # Adjusting path: current file is in lukhas/identity/api/controllers/
            # Need to go up 3 levels to lukhas-id, then down to core/id_service
            config_path = (
                Path(__file__).resolve().parent.parent.parent / "core" / "id_service" / "tier_permissions.json"
            )
            self.logger.debug(f"ΛTRACE: Attempting to load tier config from: {config_path}")

            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    self.tier_config = json.load(f)
                self.logger.info(f"ΛTRACE: Tier permissions configuration loaded successfully from {config_path}.")
            else:
                self.logger.warning(
                    f"ΛTRACE: Tier permissions configuration file not found at {config_path}. Using default configuration."
                )
                self.tier_config = {  # Default configuration
                    "tier_permissions": {
                        "0": {"max_entropy": 2.0, "symbols_allowed": 2, "description": "Basic Tier"},
                        "1": {"max_entropy": 3.0, "symbols_allowed": 3, "description": "Standard Tier"},
                        # ... (add other tiers as per original)
                        "5": {"max_entropy": 7.0, "symbols_allowed": 8, "description": "Transcendent Tier"},
                    }
                }
        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Failed to load tier permissions configuration: {e}. Using minimal default.", exc_info=True
            )
            self.tier_config = {"tier_permissions": {}}  # Minimal default on error

    # Human-readable comment: Generates a new Lambda ID.
    def generate_id(
        self,
        user_tier: int,
        symbolic_preferences: Optional[list[str]] = None,
        entropy_requirements: Optional[dict[str, Any]] = None,
        commercial_options: Optional[dict[str, Any]] = None,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Generates a new LUKHAS ΛiD with comprehensive validation and business logic,
        considering user tier, symbolic preferences, and entropy requirements.
        """
        req_id = f"genid_{int(time.time() * 1000)}"
        self.logger.info(
            f"ΛTRACE ({req_id}): Received request to generate ΛiD. User Tier: {user_tier}, Symbolic Prefs: {bool(symbolic_preferences)}, Entropy Req: {bool(entropy_requirements)}"
        )

        # Ensure symbolic_preferences is a list if None
        sym_prefs = symbolic_preferences or []
        ent_reqs = entropy_requirements or {}
        comm_opts = commercial_options or {}
        req_meta = request_metadata or {}

        try:
            # Log the request using the activity_logger (which should be ΛTRACE
            # compatible)
            self.activity_logger.log_activity(
                # Assuming user_id in metadata
                event_type="lambda_id_generation_request",
                user_id=req_meta.get("user_id", "unknown"),
                details={"user_tier": user_tier, "symbol_count": len(sym_prefs)},
                metadata=req_meta,
            )

            if not self._validate_tier(user_tier):  # Private helper, logs internally
                self.logger.warning(f"ΛTRACE ({req_id}): Invalid user_tier '{user_tier}' provided.")
                return {
                    "success": False,
                    "error": f"Invalid tier: {user_tier}. Must be 0-5.",
                    "error_code": "INVALID_TIER",
                }

            tier_permissions = self._identity_core.resolve_access_tier(user_tier)  # Private helper, logs internally

            if sym_prefs:
                pref_validation_result = self._validate_symbolic_preferences(
                    sym_prefs, tier_permissions
                )  # Logs internally
                if not pref_validation_result["valid"]:
                    self.logger.warning(
                        f"ΛTRACE ({req_id}): Symbolic preferences validation failed: {pref_validation_result['error']}"
                    )
                    return {
                        "success": False,
                        "error": pref_validation_result["error"],
                        "error_code": "SYMBOLIC_VALIDATION_FAILED",
                    }

            generation_params = {
                "tier": user_tier,
                "symbolic_preferences": sym_prefs,
                "entropy_requirements": ent_reqs,
                "commercial_options": comm_opts,
            }
            self.logger.debug(f"ΛTRACE ({req_id}): Calling id_generator.generate with params: {generation_params}")
            lambda_id_generated = self.id_generator.generate(**generation_params)
            self.logger.info(f"ΛTRACE ({req_id}): ΛiD generated by core service: {lambda_id_generated}")

            entropy_score_val = self.entropy_calculator.calculate_entropy(symbolic_input=sym_prefs, tier=user_tier)
            self.logger.debug(
                f"ΛTRACE ({req_id}): Entropy calculated: {entropy_score_val} for {len(sym_prefs)} symbols, tier {user_tier}."
            )

            tier_info_data = self.tier_manager.get_tier_info(user_tier)  # Assumes this returns a dict
            self.logger.debug(f"ΛTRACE ({req_id}): Tier info retrieved for tier {user_tier}: {tier_info_data}")

            symbolic_repr = self._create_symbolic_representation(
                lambda_id_generated, user_tier, sym_prefs
            )  # Logs internally

            self.activity_logger.log_activity(
                event_type="lambda_id_generated_success",
                user_id=req_meta.get("user_id", "unknown"),
                details={"lambda_id": lambda_id_generated, "user_tier": user_tier, "entropy_score": entropy_score_val},
                metadata=req_meta,
            )

            response_data = {
                "success": True,
                "lambda_id": lambda_id_generated,
                "entropy_score": entropy_score_val,
                "tier_info": tier_info_data,
                "symbolic_representation": symbolic_repr,
                "generation_metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "tier": user_tier,
                    # Default min_score to 0.0
                    "entropy_requirements_met": entropy_score_val >= ent_reqs.get("min_score", 0.0),
                    "symbolic_count": len(sym_prefs),
                },
            }
            self.logger.info(f"ΛTRACE ({req_id}): ΛiD generation successful. Response: {response_data}")
            return response_data

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): ΛiD generation failed: {e}", exc_info=True)
            self.activity_logger.log_activity(
                event_type="lambda_id_generation_error",
                user_id=req_meta.get("user_id", "unknown"),
                error_message=str(e),
                details={"user_tier": user_tier},
                metadata=req_meta,
            )
            return {
                "success": False,
                "error": "Generation failed due to an internal error.",
                "error_code": "ID_GENERATION_FAILED_INTERNAL",
            }

    # ... (Other methods like validate_id, calculate_entropy, etc. will be refactored similarly) ...
    # For brevity, I will show one more method refactored and then the rest
    # will follow the pattern.

    # Human-readable comment: Validates a Lambda ID.
    def validate_id(
        self,
        lambda_id: str,
        validation_level: str = "standard",
        check_collision: bool = False,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Validates a given LUKHAS ΛiD based on specified level ('basic', 'standard', 'full'),
        optionally checking for collisions.
        """
        req_id = f"valid_{int(time.time() * 1000)}"
        self.logger.info(
            f"ΛTRACE ({req_id}): Received request to validate ΛiD: '{lambda_id}', Level: '{validation_level}', Check Collision: {check_collision}"
        )
        req_meta = request_metadata or {}

        try:
            self.activity_logger.log_activity(
                event_type="lambda_id_validation_request",
                user_id=req_meta.get("user_id", "unknown"),
                details={
                    "lambda_id_to_validate": lambda_id,
                    "validation_level": validation_level,
                    "check_collision": check_collision,
                },
                metadata=req_meta,
            )

            basic_validation_res = self.id_validator.validate_format(
                lambda_id
            )  # Assuming this logs internally or is simple
            self.logger.debug(
                f"ΛTRACE ({req_id}): Basic format validation result for '{lambda_id}': {basic_validation_res}"
            )

            if not basic_validation_res["valid"]:
                self.logger.warning(
                    f"ΛTRACE ({req_id}): Basic format validation failed for '{lambda_id}'. Reason: {basic_validation_res.get('reason')}"
                )
                return {
                    "success": True,
                    "valid": False,
                    "validation_details": basic_validation_res,
                    "validation_level": validation_level,
                    "error_code": "ID_FORMAT_INVALID",
                }

            extracted_tier_val = self._extract_tier_from_id(lambda_id)  # Logs internally

            current_validation_details: dict[str, Any] = {
                "format_valid": basic_validation_res["valid"],
                "tier_extracted": extracted_tier_val,
                "tier_compliance_check": True,
            }  # Default true

            if validation_level in ["standard", "full"]:
                id_entropy_score = self.entropy_calculator.calculate_id_entropy(lambda_id)
                current_validation_details["entropy_score_calculated"] = id_entropy_score
                self.logger.debug(f"ΛTRACE ({req_id}): ID entropy calculated for '{lambda_id}': {id_entropy_score}")

                if extracted_tier_val is not None:
                    tier_perms = self._identity_core.resolve_access_tier(extracted_tier_val)  # Logs internally
                    # Assuming max_entropy is a key in tier_perms from config
                    max_entropy_for_tier = tier_perms.get("max_entropy", 10.0)  # Default high if not found
                    current_validation_details["tier_compliance_check"] = id_entropy_score <= max_entropy_for_tier
                    current_validation_details["tier_max_entropy_limit"] = max_entropy_for_tier
                    self.logger.debug(
                        f"ΛTRACE ({req_id}): Tier compliance for '{lambda_id}' (Tier {extracted_tier_val}): Entropy {id_entropy_score} <= Limit {max_entropy_for_tier} -> {current_validation_details['tier_compliance_check']}"
                    )

            if validation_level == "full":
                if check_collision:
                    collision_check_res = self._check_collision(lambda_id)  # Logs internally
                    current_validation_details["collision_check_result"] = collision_check_res

                id_pattern_analysis = self._analyze_id_patterns(lambda_id)  # Logs internally
                current_validation_details["id_pattern_analysis_result"] = id_pattern_analysis

            is_overall_valid = all(
                [
                    current_validation_details["format_valid"],
                    current_validation_details["tier_compliance_check"],
                    not current_validation_details.get("collision_check_result", {}).get(
                        "collision_detected", False
                    ),  # False if no collision_check_result
                ]
            )

            self.activity_logger.log_activity(
                event_type="lambda_id_validation_result",
                user_id=req_meta.get("user_id", "unknown"),
                details={"validated_lambda_id": lambda_id, "is_valid": is_overall_valid, "level": validation_level},
                metadata=req_meta,
            )

            response_data = {
                "success": True,
                "valid": is_overall_valid,
                "validation_details": current_validation_details,
                "validation_level": validation_level,
                # Use consistent key
                "final_entropy_score": current_validation_details.get("entropy_score_calculated"),
                "is_tier_compliant": current_validation_details["tier_compliance_check"],
            }
            self.logger.info(
                f"ΛTRACE ({req_id}): ΛiD validation for '{lambda_id}' completed. Overall Valid: {is_overall_valid}. Response: {response_data}"
            )
            return response_data

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): ΛiD validation for '{lambda_id}' failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Validation failed due to an internal error.",
                "error_code": "ID_VALIDATION_FAILED_INTERNAL",
            }

    # Human-readable comment: Calculates entropy for a given symbolic input.
    def calculate_entropy(
        self,
        symbolic_input: list[str],
        tier: int = 0,
        calculation_method: str = "shannon",
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Calculates the entropy score for a list of symbolic inputs,
        considering user tier and specified calculation method.
        """
        req_id = f"entropy_{int(time.time() * 1000)}"
        self.logger.info(
            f"ΛTRACE ({req_id}): Received request to calculate entropy. Symbols: {len(symbolic_input)}, Tier: {tier}, Method: {calculation_method}"
        )
        req_meta = request_metadata or {}
        try:
            entropy_score_val = self.entropy_calculator.calculate_entropy(
                symbolic_input=symbolic_input, tier=tier, method=calculation_method
            )
            self.logger.debug(f"ΛTRACE ({req_id}): Entropy calculated by core service: {entropy_score_val}")

            entropy_breakdown_data = self.entropy_calculator.get_entropy_breakdown(symbolic_input, calculation_method)
            self.logger.debug(f"ΛTRACE ({req_id}): Entropy breakdown: {entropy_breakdown_data}")

            recommendations_list = self._generate_entropy_recommendations(
                entropy_score_val, tier, symbolic_input
            )  # Logs internally

            self.activity_logger.log_activity(
                event_type="entropy_calculation_success",
                user_id=req_meta.get("user_id", "unknown"),
                details={
                    "entropy_score": entropy_score_val,
                    "tier": tier,
                    "symbol_count": len(symbolic_input),
                    "method": calculation_method,
                },
                metadata=req_meta,
            )

            response_data = {
                "success": True,
                "entropy_score": entropy_score_val,
                "entropy_breakdown": entropy_breakdown_data,
                "recommendations": recommendations_list,
                "calculation_metadata": {
                    "method": calculation_method,
                    "tier": tier,
                    "symbolic_count": len(symbolic_input),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
            self.logger.info(
                f"ΛTRACE ({req_id}): Entropy calculation successful. Score: {entropy_score_val}. Response: {response_data}"
            )
            return response_data

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): Entropy calculation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Entropy calculation failed due to an internal error.",
                "error_code": "ENTROPY_CALC_FAILED_INTERNAL",
            }

    # Human-readable comment: Retrieves tier information.
    def get_tier_information(
        self,
        specific_tier: Optional[int] = None,
        include_progression: bool = False,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Retrieves information about LUKHAS ΛiD tiers, either for a specific tier
        or all tiers, optionally including progression map details.
        """
        req_id = f"tierinfo_{int(time.time() * 1000)}"
        self.logger.info(
            f"ΛTRACE ({req_id}): Received request for tier information. Specific Tier: {specific_tier}, Include Progression: {include_progression}"
        )
        try:
            result_data: dict[str, Any]
            if specific_tier is not None:
                if not self._validate_tier(specific_tier):  # Logs internally
                    self.logger.warning(f"ΛTRACE ({req_id}): Invalid specific_tier '{specific_tier}' requested.")
                    return {
                        "success": False,
                        "error": f"Invalid tier: {specific_tier}. Must be 0-5.",
                        "error_code": "INVALID_TIER_REQUESTED",
                    }

                tier_info_data = self.tier_manager.get_tier_info(specific_tier)  # Assumes this is detailed enough
                self.logger.debug(
                    f"ΛTRACE ({req_id}): Retrieved info for specific tier {specific_tier}: {tier_info_data}"
                )
                result_data = {"success": True, "tier_requested": specific_tier, "tier_information": tier_info_data}
            else:
                all_tiers_data = {str(t): self.tier_manager.get_tier_info(t) for t in range(6)}  # Tiers 0-5
                self.logger.debug(f"ΛTRACE ({req_id}): Retrieved information for all tiers.")
                result_data = {"success": True, "all_tier_information": all_tiers_data}

            if include_progression:
                # Assumes this returns serializable data
                progression_map_data = self.tier_manager.get_progression_map()
                result_data["tier_progression_map"] = progression_map_data
                self.logger.debug(f"ΛTRACE ({req_id}): Tier progression map included: {progression_map_data}")

            self.logger.info(f"ΛTRACE ({req_id}): Tier information request processed successfully.")
            return result_data

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): Failed to get tier information: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Failed to retrieve tier information due to an internal error.",
                "error_code": "TIER_INFO_FAILED_INTERNAL",
            }

    # Human-readable comment: Handles tier upgrade requests.
    def request_tier_upgrade(
        self,
        current_lambda_id: str,
        target_tier: int,
        validation_data: Optional[dict[str, Any]] = None,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Processes a request to upgrade a user's LUKHAS ΛiD to a target tier,
        performing necessary validations and generating a new ΛiD if successful.
        """
        req_id = f"tierup_{int(time.time() * 1000)}"
        self.logger.info(
            f"ΛTRACE ({req_id}): Received request for tier upgrade. Current ΛiD: '{current_lambda_id}', Target Tier: {target_tier}"
        )
        req_meta = request_metadata or {}
        val_data = validation_data or {}
        try:
            self.activity_logger.log_activity(
                event_type="tier_upgrade_process_started",
                user_id=req_meta.get("user_id", "unknown"),
                details={"current_lambda_id": current_lambda_id, "target_tier": target_tier},
                metadata=req_meta,
            )

            current_id_validation = self.validate_id(
                current_lambda_id, "full", request_metadata=req_meta
            )  # Use full validation
            if not current_id_validation.get("valid"):
                self.logger.warning(
                    f"ΛTRACE ({req_id}): Tier upgrade aborted. Current ΛiD '{current_lambda_id}' is invalid."
                )
                return {
                    "success": False,
                    "upgrade_approved": False,
                    "error": "Current ΛiD is invalid.",
                    "error_code": "UPGRADE_INVALID_CURRENT_ID",
                    "validation_details": current_id_validation.get("validation_details"),
                }

            current_tier_val = self._extract_tier_from_id(current_lambda_id)
            if current_tier_val is None:
                self.logger.error(f"ΛTRACE ({req_id}): Could not extract tier from current ΛiD '{current_lambda_id}'.")
                return {
                    "success": False,
                    "upgrade_approved": False,
                    "error": "Cannot determine current tier from ΛiD.",
                    "error_code": "UPGRADE_TIER_EXTRACTION_FAILED",
                }

            self.logger.debug(f"ΛTRACE ({req_id}): Current tier is {current_tier_val}. Target tier is {target_tier}.")
            if target_tier <= current_tier_val:
                self.logger.warning(
                    f"ΛTRACE ({req_id}): Target tier {target_tier} is not higher than current tier {current_tier_val}."
                )
                return {
                    "success": False,
                    "upgrade_approved": False,
                    "error": "Target tier must be higher than current tier.",
                    "error_code": "UPGRADE_INVALID_TARGET_TIER",
                }

            # Assuming tier_manager.validate_upgrade_eligibility exists and works as
            # intended
            upgrade_eligibility = self.tier_manager.validate_upgrade_eligibility(
                current_tier_val, target_tier, val_data
            )
            self.logger.debug(f"ΛTRACE ({req_id}): Upgrade eligibility check result: {upgrade_eligibility}")

            if not upgrade_eligibility.get("eligible"):  # type: ignore
                self.logger.warning(
                    f"ΛTRACE ({req_id}): Tier upgrade not eligible. Reason: {upgrade_eligibility.get('reason')}"
                )  # type: ignore
                return {
                    "success": True,
                    "upgrade_approved": False,
                    "error": upgrade_eligibility.get("reason"),
                    "requirements": upgrade_eligibility.get("requirements", {}),
                    "error_code": "UPGRADE_NOT_ELIGIBLE",
                }  # type: ignore

            # If eligible, proceed to generate new ID for the target tier
            # Symbolic preferences for new ID might come from validation_data or be
            # re-evaluated
            new_id_generation_result = self.generate_id(
                user_tier=target_tier,
                symbolic_preferences=val_data.get("symbolic_preferences_for_new_tier", []),  # Example key
                entropy_requirements=val_data.get("entropy_requirements_for_new_tier", {}),  # Example key
                request_metadata=req_meta,
            )  # This method logs extensively

            if not new_id_generation_result.get("success"):
                self.logger.error(
                    f"ΛTRACE ({req_id}): Failed to generate new ΛiD for tier upgrade. Error: {new_id_generation_result.get('error')}"
                )
                return {
                    "success": False,
                    "upgrade_approved": False,
                    "error": "Failed to generate new ΛiD for upgrade.",
                    "error_code": "UPGRADE_NEW_ID_GENERATION_FAILED",
                    "details": new_id_generation_result.get("error"),
                }

            new_lambda_id = new_id_generation_result["lambda_id"]
            self.activity_logger.log_activity(
                event_type="tier_upgrade_success",
                user_id=req_meta.get("user_id", "unknown"),
                details={
                    "old_lambda_id": current_lambda_id,
                    "new_lambda_id": new_lambda_id,
                    "old_tier": current_tier_val,
                    "new_tier": target_tier,
                },
                metadata=req_meta,
            )

            response_data = {
                "success": True,
                "upgrade_approved": True,
                "old_lambda_id": current_lambda_id,
                "new_lambda_id": new_lambda_id,
                "old_tier": current_tier_val,
                "new_tier": target_tier,
                "upgrade_details": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "entropy_score_new_id": new_id_generation_result.get("entropy_score"),
                    # Simplified
                    "new_tier_permissions_summary": self._resolve_access_tier(target_tier).get("description", "N/A"),
                    "new_symbolic_representation": new_id_generation_result.get("symbolic_representation"),
                },
            }
            self.logger.info(
                f"ΛTRACE ({req_id}): Tier upgrade successful. New ΛiD: {new_lambda_id}. Response: {response_data}"
            )
            return response_data

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): Tier upgrade processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "upgrade_approved": False,
                "error": "Tier upgrade failed due to an internal error.",
                "error_code": "UPGRADE_PROCESS_FAILED_INTERNAL",
            }

    # Human-readable comment: Checks the health of core services used by this
    # controller.
    def check_service_health(self, request_metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Performs a health check on all core services utilized by the LambdaIDController.
        Returns a dictionary summarizing the health status of each service.
        """
        req_id = f"health_{int(time.time() * 1000)}"
        self.logger.info(f"ΛTRACE ({req_id}): Performing core services health check.")
        try:
            service_health_statuses: dict[str, Any] = {}
            services_map = {
                "LambdaIDGenerator": self.id_generator,
                "LambdaIDValidator": self.id_validator,
                "EntropyCalculator": self.entropy_calculator,
                "LambdaTierManager": self.tier_manager,
                "ActivityLogger": self.activity_logger,
            }
            overall_health_is_good = True

            for service_name, service_instance in services_map.items():
                service_status = {"status": "unknown", "details": "Not checked"}
                try:
                    if hasattr(service_instance, "health_check") and callable(service_instance.health_check):
                        # If service has its own health_check method
                        # Assuming it returns a dict like {'status':
                        # 'healthy/unhealthy', ...}
                        service_status = service_instance.health_check()
                        self.logger.debug(f"ΛTRACE ({req_id}): Health check for '{service_name}': {service_status}")
                    elif service_instance is not None:  # Basic check: is it initialized?
                        service_status = {"status": "healthy", "details": "Instance initialized."}
                        self.logger.debug(f"ΛTRACE ({req_id}): Basic health check for '{service_name}': Initialized.")
                    else:
                        service_status = {
                            "status": "unhealthy",
                            "details": "Service instance is None (not initialized).",
                        }
                        self.logger.warning(f"ΛTRACE ({req_id}): Health check for '{service_name}': Instance is None.")
                        overall_health_is_good = False

                    if service_status.get("status") != "healthy":
                        overall_health_is_good = False
                except Exception as e_service_health:
                    self.logger.error(
                        f"ΛTRACE ({req_id}): Error during health check for service '{service_name}': {e_service_health}",
                        exc_info=True,
                    )
                    service_status = {"status": "unhealthy", "error": str(e_service_health)}
                    overall_health_is_good = False
                service_health_statuses[service_name] = service_status

            controller_version_info = "1.1.0"  # Example version for this controller
            final_status = {
                "overall_status": "healthy" if overall_health_is_good else "degraded",
                "service_details": service_health_statuses,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "controller_version": controller_version_info,
            }
            self.logger.info(
                f"ΛTRACE ({req_id}): Core services health check completed. Overall: {final_status['overall_status']}. Details: {final_status['service_details']}"
            )
            return final_status

        except Exception as e:
            self.logger.error(f"ΛTRACE ({req_id}): General health check procedure failed: {e}", exc_info=True)
            return {"overall_status": "unhealthy", "error_details": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

    # --- Private Helper Methods ---
    # Human-readable comment: Validates if a given tier is within the acceptable range.
    def _validate_tier(self, tier_to_validate: int) -> bool:
        """Validates if the provided tier is an integer within the valid range (0-5)."""
        is_valid = isinstance(tier_to_validate, int) and 0 <= tier_to_validate <= 5
        self.logger.debug(f"ΛTRACE: Validating tier {tier_to_validate}. Is valid: {is_valid}")
        return is_valid

    # Human-readable comment: Retrieves permissions for a specific tier from
    # configuration.
    def _resolve_access_tier(self, tier_level: int) -> dict[str, Any]:
        """Retrieves permissions and limits for a specific tier from the loaded configuration."""
        self.logger.debug(f"ΛTRACE: Getting permissions for tier {tier_level}.")
        # Default permissions if specific tier not found or config missing parts
        default_perms_for_tier = {"max_entropy": 1.0, "symbols_allowed": 1, "description": "Default/Unknown Tier"}
        permissions = self.tier_config.get("tier_permissions", {}).get(str(tier_level), default_perms_for_tier)
        self.logger.debug(f"ΛTRACE: Permissions for tier {tier_level}: {permissions}")
        return permissions

    # Human-readable comment: Validates symbolic preferences against tier limits.
    def _validate_symbolic_preferences(
        self, symbols_list: list[str], tier_permissions_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """Validates if the provided list of symbols conforms to the limits of the given tier permissions."""
        max_symbols_allowed = tier_permissions_dict.get("symbols_allowed", 1)  # Default to 1 if not specified
        self.logger.debug(
            f"ΛTRACE: Validating {len(symbols_list)} symbols against max allowed {max_symbols_allowed} for tier."
        )
        if len(symbols_list) > max_symbols_allowed:
            error_msg = f"Too many symbols for tier. Max allowed: {max_symbols_allowed}, provided: {len(symbols_list)}."
            self.logger.warning(f"ΛTRACE: Symbolic preference validation failed: {error_msg}")
            return {"valid": False, "error": error_msg}
        self.logger.debug("ΛTRACE: Symbolic preferences validated successfully.")
        return {"valid": True}

    # Human-readable comment: Extracts tier information from a Lambda ID string.
    def _extract_tier_from_id(self, lambda_id_str: str) -> Optional[int]:
        """Extracts the tier number from a LUKHAS ΛiD string based on its format."""
        self.logger.debug(f"ΛTRACE: Attempting to extract tier from ΛiD: '{lambda_id_str}'.")
        try:
            # Example format: LUKHAS{tier}‿{numeric_part}#{symbolic_part}
            # This is a simplified assumption; actual parsing might be more complex
            # via id_validator
            if lambda_id_str.startswith("LUKHAS") and "‿" in lambda_id_str:
                tier_part_str = lambda_id_str[1 : lambda_id_str.find("‿")]
                if tier_part_str.isdigit():
                    tier_val = int(tier_part_str)
                    self.logger.debug(f"ΛTRACE: Extracted tier {tier_val} from ΛiD '{lambda_id_str}'.")
                    return tier_val
            self.logger.warning(
                f"ΛTRACE: Could not extract valid tier from ΛiD '{lambda_id_str}' based on basic parsing."
            )
        except (ValueError, IndexError) as e:
            self.logger.error(f"ΛTRACE: Error parsing tier from ΛiD '{lambda_id_str}': {e}", exc_info=False)
        return None  # Return None if tier cannot be extracted

    # Human-readable comment: Creates a symbolic visual representation of a Lambda ID.
    def _create_symbolic_representation(self, lambda_id_str: str, tier_level: int, symbols_list: list[str]) -> str:
        """Creates a compact symbolic string representation of a ΛiD, tier, and key symbols."""
        self.logger.debug(f"ΛTRACE: Creating symbolic representation for ΛiD '{lambda_id_str}', Tier {tier_level}.")
        tier_visual_symbols = {0: "🟢", 1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴", 5: "💜"}
        tier_symbol_char = tier_visual_symbols.get(tier_level, "⚪")  # Default symbol
        # Use first few symbols for brevity, ensure they are printable
        symbols_preview = "".join(s for s in symbols_list[:3] if isinstance(s, str) and s.isprintable())
        representation = f"🆔{lambda_id_str}{tier_symbol_char}{symbols_preview}✨"
        self.logger.debug(f"ΛTRACE: Symbolic representation created: {representation}")
        return representation

    # Human-readable comment: Placeholder for Lambda ID collision check.
    def _check_collision(self, lambda_id_str: str) -> dict[str, Any]:
        """Placeholder for checking ΛiD collisions against a persistent store. (Not implemented)."""
        self.logger.warning(
            f"ΛTRACE: Collision check for ΛiD '{lambda_id_str}' is a STUB (not implemented). Returning no collision."
        )
        # In a real implementation, this would query a database or distributed ledger.
        return {
            "collision_detected": False,
            "checked_against_source": "simulated_database_check",
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Human-readable comment: Placeholder for Lambda ID pattern analysis.
    def _analyze_id_patterns(self, lambda_id_str: str) -> dict[str, Any]:
        """Placeholder for analyzing patterns or characteristics of a ΛiD. (Not implemented)."""
        self.logger.debug(f"ΛTRACE: Pattern analysis for ΛiD '{lambda_id_str}' is a STUB.")
        # Example analysis points
        has_unicode_chars = any(ord(c) > 127 for c in lambda_id_str)
        return {
            "id_length": len(lambda_id_str),
            "contains_unicode": has_unicode_chars,
            "pattern_strength_score": 0.85,
            "analysis_details": "Stubbed pattern analysis.",
        }  # Example score

    # Human-readable comment: Generates recommendations for improving entropy
    # based on score and tier.
    def _generate_entropy_recommendations(
        self, current_entropy_score: float, user_tier: int, current_symbols: list[str]
    ) -> list[str]:
        """Generates actionable recommendations for improving symbolic input entropy based on current score and tier limits."""
        self.logger.debug(
            f"ΛTRACE: Generating entropy recommendations. Score: {current_entropy_score}, Tier: {user_tier}, Symbols: {len(current_symbols)}"
        )
        recommendations_list: list[str] = []
        tier_perms = self._identity_core.resolve_access_tier(user_tier)  # Logs internally
        max_entropy_for_tier = tier_perms.get("max_entropy", 2.0)  # Default from original
        symbols_allowed_for_tier = tier_perms.get("symbols_allowed", 2)

        if current_entropy_score < max_entropy_for_tier * 0.5:  # Significantly below max
            recommendations_list.append(
                "Your current symbolic set has low entropy. Consider adding more diverse or less common symbols/phrases."
            )
        elif current_entropy_score < max_entropy_for_tier * 0.8:
            recommendations_list.append(
                "Entropy is good, but can be improved. Try adding a unique symbol or varying symbol types."
            )

        if len(current_symbols) < symbols_allowed_for_tier:
            recommendations_list.append(
                f"You can add up to {symbols_allowed_for_tier - len(current_symbols)} more symbols for your current tier to potentially increase entropy."
            )
        elif len(current_symbols) == symbols_allowed_for_tier and current_entropy_score < max_entropy_for_tier:
            recommendations_list.append(
                "You've used the maximum symbols for your tier. To further increase entropy, try replacing common symbols with more unique ones."
            )

        if current_entropy_score > max_entropy_for_tier:  # This case should ideally be prevented by generation logic
            recommendations_list.append(
                f"Warning: Current entropy ({current_entropy_score:.2f}) exceeds the typical maximum for Tier {user_tier} ({max_entropy_for_tier:.2f}). This might indicate an issue or an opportunity for tier review."
            )

        if not recommendations_list:
            recommendations_list.append("Current entropy level is good for your tier and symbol count.")

        self.logger.debug(f"ΛTRACE: Generated {len(recommendations_list)} entropy recommendations.")
        return recommendations_list


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lambd_id_controller.py
# VERSION: 1.1.0 # Updated version
# TIER SYSTEM: Controller logic considers user tiers (0-5) for operations like ID generation and validation.
# ΛTRACE INTEGRATION: ENABLED (Controller actions, service calls, errors are logged)
# CAPABILITIES: Orchestrates ΛiD generation, validation, entropy calculation, tier information retrieval,
#               and tier upgrade requests by interacting with core LUKHAS ID services.
# FUNCTIONS: (Public methods of LambdaIDController) generate_id, validate_id, calculate_entropy,
#            get_tier_information, request_tier_upgrade, check_service_health.
# CLASSES: LambdaIDController.
# DECORATORS: None within this class.
# DEPENDENCIES: json, logging, datetime, typing, pathlib, and LUKHAS core services for ID, Tier, Trace.
# INTERFACES: This class serves as a business logic layer, typically invoked by API route handlers.
# ERROR HANDLING: Catches exceptions in public methods, logs them, and returns structured error responses.
#                 Includes fallback mechanisms for service and configuration loading.
# LOGGING: Uses "ΛTRACE.lukhas_id.api.controllers.LambdaIDController" hierarchical logger.
# AUTHENTICATION: Relies on upstream (e.g., API gateway or route decorator) for user authentication.
#                 Controller methods may receive user context (e.g., user_id, tier) via parameters.
# HOW TO USE:
#   controller = LambdaIDController()
#   new_id_data = controller.generate_id(user_tier=1, symbolic_preferences=["test", "symbol"])
#   validation_status = controller.validate_id(lambda_id="Λ1‿XYZ)  # test"
# INTEGRATION NOTES: Crucial for this controller that all core LUKHAS ID services
#                    (LambdaIDGenerator, LambdaIDValidator, EntropyCalculator, LambdaTierManager, ActivityLogger)
#                    are correctly implemented and importable. Configuration for tier permissions is loaded from JSON.
# MAINTENANCE: Update default configurations and tier permission parsing if schema changes.
#              Ensure error codes returned are consistent with API design.
#              Refine helper methods like _extract_tier_from_id if ΛiD format evolves.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
