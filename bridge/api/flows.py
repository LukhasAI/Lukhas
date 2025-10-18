# ═══════════════════════════════════════════════════════════════════════════
import hashlib
import logging
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt
from flask import (
    Blueprint,  # Assuming app context will be from unified_api or similar
    jsonify,
    request,
)

# LUKHAS identity system integration
try:
    from governance.identity.connector import IdentityConnector
    from identity.auth_service import AuthService

    LUKHAS_IDENTITY_AVAILABLE = True
except ImportError:
    try:
        from governance.identity.connector import IdentityConnector
        from identity.auth_service import AuthService

        LUKHAS_IDENTITY_AVAILABLE = True
    except ImportError:
        LUKHAS_IDENTITY_AVAILABLE = False

# FILENAME: auth_flows.py
# MODULE: lukhas_id.api.auth.auth_flows
# DESCRIPTION: Defines API endpoints for user authentication flows such as registration,
#              login, logout, and token verification within the LUKHAS ΛiD ecosystem.
# DEPENDENCIES: Flask (Blueprint, request, jsonify), logging, JWT, bcrypt
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

# Security configuration
JWT_SECRET_KEY = os.getenv("LUKHAS_ID_SECRET", "default-unsafe-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# In-memory storage for demo (use proper database in production)
users_db: dict[str, dict[str, Any]] = {}
user_sessions: dict[str, dict[str, Any]] = {}
failed_login_attempts: dict[str, list] = {}
blacklisted_tokens: set = set()

# Initialize ΛTRACE logger for this module

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

logger = logging.getLogger("ΛTRACE.lukhas_id.api.auth.auth_flows")
logger.info("ΛTRACE: Initializing auth_flows module.")

# Initialize LUKHAS identity system integration
if LUKHAS_IDENTITY_AVAILABLE:
    try:
        identity_connector = IdentityConnector()
        auth_service = AuthService()
        logger.info("ΛTRACE: LUKHAS identity system integration enabled")
    except Exception as e:
        logger.warning(f"ΛTRACE: Failed to initialize LUKHAS identity system: {e}")
        identity_connector = None
        auth_service = None
        LUKHAS_IDENTITY_AVAILABLE = False
else:
    identity_connector = None
    auth_service = None
    logger.warning("ΛTRACE: LUKHAS identity system not available - using local authentication only")

# Create a Blueprint for authentication routes.
# This Blueprint would typically be registered with the main Flask app instance.
auth_bp = Blueprint("auth_lukhas_id", __name__, url_prefix="/api/v2/auth")  # Added versioned prefix
logger.info("ΛTRACE: Flask Blueprint 'auth_lukhas_id' created with prefix /api/v2/auth.")


# Security helper functions
def _validate_password_strength(password: str, policy: Optional[dict] = None) -> tuple[bool, str]:
    """Validate password meets security requirements based on a given policy."""
    if policy is None:
        policy = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special_char": True,
            "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        }

    if len(password) < policy.get("min_length", 8):
        return (
            False,
            f"Password must be at least {policy.get('min_length', 8)} characters",
        )

    if policy.get("require_uppercase") and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if policy.get("require_lowercase") and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if policy.get("require_digit") and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if policy.get("require_special_char"):
        special_chars = policy.get("special_chars", "!@#$%^&*()_+-=[]{}|;:,.<>?")
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

    return True, "Password meets requirements"


def _generate_lambda_id(username: str) -> str:
    """Generate LUKHAS ΛiD for user."""
    timestamp = int(time.time())
    entropy = secrets.token_hex(8)

    # Create ΛiD hash
    lambda_id_input = f"{username}:{timestamp}:{entropy}"
    lambda_id_hash = hashlib.sha256(lambda_id_input.encode()).hexdigest()[:16]

    return f"λ{lambda_id_hash}"


def _generate_access_token(user_id: str, lambda_id: str) -> str:
    """Generate JWT access token."""
    payload = {
        "user_id": user_id,
        "lambda_id": lambda_id,
        "exp": datetime.now(timezone.utc) + JWT_ACCESS_TOKEN_EXPIRES,
        "iat": datetime.now(timezone.utc),
        "token_type": "access",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _generate_refresh_token(user_id: str) -> str:
    """Generate JWT refresh token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + JWT_REFRESH_TOKEN_EXPIRES,
        "iat": datetime.now(timezone.utc),
        "token_type": "refresh",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _check_account_lockout(username: str) -> tuple[bool, Optional[str]]:
    """Check if account is locked due to failed attempts."""
    if username not in failed_login_attempts:
        return False, None

    attempts = failed_login_attempts[username]
    recent_attempts = [
        attempt
        for attempt in attempts
        if datetime.fromtimestamp(attempt, timezone.utc) > (datetime.now(timezone.utc) - LOCKOUT_DURATION)
    ]

    if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
        lockout_end = datetime.fromtimestamp(recent_attempts[0], timezone.utc) + LOCKOUT_DURATION
        return True, f"Account locked until {lockout_end.isoformat()}"

    return False, None


def _record_failed_login(username: str) -> None:
    """Record failed login attempt."""
    if username not in failed_login_attempts:
        failed_login_attempts[username] = []

    failed_login_attempts[username].append(time.time())


def _validate_input_data(data: dict) -> tuple[bool, str]:
    """Validate input data for security."""
    required_fields = ["username", "password"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

        if not isinstance(data[field], str):
            return False, f"Field {field} must be a string"

        if len(data[field].strip()) == 0:
            return False, f"Field {field} cannot be empty"

    return True, "Input validation passed"


def _enhance_authentication_with_lukhas(username: str, request_context: dict) -> dict:
    """
    Enhance authentication with LUKHAS identity system integration.
    Provides tiered authentication, governance integration, and advanced security features.
    """
    enhancement_result = {
        "lukhas_integration": False,
        "tier_validated": False,
        "governance_checked": False,
        "security_level": "basic",
    }

    if not LUKHAS_IDENTITY_AVAILABLE:
        logger.debug(f"LUKHAS identity system not available for user {username}")
        return enhancement_result

    try:
        # Attempt identity connector integration
        if identity_connector:
            # Validate user through governance system
            governance_result = identity_connector.validate_user_governance(user_id=username, context=request_context)
            enhancement_result["governance_checked"] = True

            if governance_result.get("approved", True):
                logger.info(f"✅ User {username} passed governance validation")
                enhancement_result["security_level"] = "enhanced"
            else:
                logger.warning(
                    f"⚠️ User {username} failed governance validation: {governance_result.get('reason', 'unknown')}"
                )
                return enhancement_result

        # Attempt auth service integration for tiered authentication
        if auth_service:
            # Get user's authentication tier
            tier_info = auth_service.get_user_tier(username)
            if tier_info and tier_info.get("tier"):
                enhancement_result["tier_validated"] = True
                enhancement_result["tier"] = tier_info["tier"]
                enhancement_result["security_level"] = f"tier_{tier_info['tier']}"
                logger.info(f"✅ User {username} validated at tier {tier_info['tier']}")

        enhancement_result["lukhas_integration"] = True
        logger.info(f"✅ Enhanced authentication completed for {username}")

    except Exception as e:
        logger.error(f"❌ LUKHAS authentication enhancement failed for {username}: {e}")
        # Continue with basic authentication - don't fail the login

    return enhancement_result


def _validate_with_lukhas_security(username: str, password: str, request_data: dict) -> tuple[bool, str, dict]:
    """
    Validate credentials using LUKHAS security protocols.
    Returns (is_valid, message, security_context)
    """
    security_context = {
        "validation_method": "local",
        "security_features": ["password_hash"],
        "lukhas_enhanced": False,
    }

    # Standard password validation
    user = users_db.get(username)
    if not user:
        return False, "Invalid credentials", security_context

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return False, "Invalid credentials", security_context

    # Enhance with LUKHAS security if available
    if LUKHAS_IDENTITY_AVAILABLE and auth_service:
        try:
            # Additional security validation through LUKHAS system
            lukhas_validation = auth_service.validate_credentials(
                user_id=username,
                credential_data={"type": "password", "context": request_data},
                security_level="enhanced",
            )

            if lukhas_validation.get("validated", True):
                security_context["lukhas_enhanced"] = True
                security_context["security_features"].extend(
                    ["lukhas_validation", "tier_checking", "governance_integration"]
                )
                security_context["validation_method"] = "lukhas_enhanced"
                logger.info(f"✅ LUKHAS enhanced validation successful for {username}")
            else:
                logger.warning(f"⚠️ LUKHAS enhanced validation failed for {username}")
                return False, "Enhanced security validation failed", security_context

        except Exception as e:
            logger.error(f"❌ LUKHAS security validation error for {username}: {e}")
            # Continue with basic validation - don't fail login for system errors

    return True, "Credentials validated", security_context


# Human-readable comment: Endpoint for new user registration.
@auth_bp.route("/register", methods=["POST"])
def register_user_endpoint():
    """
    Handles new user registration with full security implementation.
    Validates input, checks password strength, creates user record,
    generates ΛiD, and returns authentication tokens.
    """
    request_id = f"reg_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /register.")

    try:
        # Input validation
        if not request.is_json:
            logger.warning(f"ΛTRACE ({request_id}): Invalid content type")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Content-Type must be application/json",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        data = request.get_json()

        # Validate required fields
        valid, message = _validate_input_data(data)
        if not valid:
            logger.warning(f"ΛTRACE ({request_id}): Input validation failed: {message}")
            return (
                jsonify({"success": False, "message": message, "request_id": request_id}),
                400,
            )

        username = data["username"].strip()
        password = data["password"]
        email = data.get("email", "").strip()

        # Username validation
        if len(username) < 3 or len(username) > 50:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username must be between 3 and 50 characters",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        # Check if user already exists
        if username in users_db:
            logger.warning(f"ΛTRACE ({request_id}): Registration attempt for existing user {username}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username already exists",
                        "request_id": request_id,
                    }
                ),
                409,
            )

        # Password strength validation
        valid_password, password_message = _validate_password_strength(password)
        if not valid_password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": password_message,
                        "request_id": request_id,
                    }
                ),
                400,
            )

        # Generate secure password hash
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Generate ΛiD
        lambda_id = _generate_lambda_id(username)

        # Create user record
        user_record = {
            "user_id": username,
            "lambda_id": lambda_id,
            "password_hash": password_hash.decode("utf-8"),
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "is_active": True,
            "failed_login_count": 0,
        }

        users_db[username] = user_record

        # Generate authentication tokens
        access_token = _generate_access_token(username, lambda_id)
        refresh_token = _generate_refresh_token(username)

        # Create session record
        session_id = f"sess_{secrets.token_hex(16)}"
        user_sessions[session_id] = {
            "user_id": username,
            "lambda_id": lambda_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "unknown"),
        }

        logger.info(f"ΛTRACE ({request_id}): User {username} registered successfully with ΛiD {lambda_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "request_id": request_id,
                    "user": {
                        "user_id": username,
                        "lambda_id": lambda_id,
                        "email": email,
                        "created_at": user_record["created_at"],
                    },
                    "tokens": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer",
                        "expires_in": int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds()),
                    },
                    "session_id": session_id,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Registration error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error during registration",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Human-readable comment: Endpoint for user login.
@auth_bp.route("/login", methods=["POST"])
def login_user_endpoint():
    """
    Authenticates a user with comprehensive security measures.
    Validates credentials, implements brute-force protection,
    generates JWT tokens, and maintains secure sessions.
    """
    request_id = f"login_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /login.")

    try:
        # Input validation
        if not request.is_json:
            logger.warning(f"ΛTRACE ({request_id}): Invalid content type")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Content-Type must be application/json",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        data = request.get_json()

        # Validate required fields
        required_fields = ["username", "password"]
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"ΛTRACE ({request_id}): Missing field {field}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Missing required field: {field}",
                            "request_id": request_id,
                        }
                    ),
                    400,
                )

        username = data["username"].strip()
        password = data["password"]

        # Check account lockout
        is_locked, lockout_message = _check_account_lockout(username)
        if is_locked:
            logger.warning(f"ΛTRACE ({request_id}): Login attempt on locked account {username}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": lockout_message,
                        "request_id": request_id,
                    }
                ),
                423,
            )  # Locked

        # Check if user exists
        if username not in users_db:
            _record_failed_login(username)
            logger.warning(f"ΛTRACE ({request_id}): Login attempt for non-existent user {username}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid username or password",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_record = users_db[username]

        # Check if account is active
        if not user_record.get("is_active", True):
            logger.warning(f"ΛTRACE ({request_id}): Login attempt for inactive account {username}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Account is inactive",
                        "request_id": request_id,
                    }
                ),
                403,
            )

        # Verify password
        stored_password_hash = user_record["password_hash"]
        if not bcrypt.checkpw(password.encode("utf-8"), stored_password_hash.encode("utf-8")):
            _record_failed_login(username)
            users_db[username]["failed_login_count"] = user_record.get("failed_login_count", 0) + 1

            logger.warning(f"ΛTRACE ({request_id}): Failed login attempt for user {username}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid username or password",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        # Clear failed login attempts on successful authentication
        failed_login_attempts.pop(username, None)
        users_db[username]["failed_login_count"] = 0

        # Update last login
        users_db[username]["last_login"] = datetime.now(timezone.utc).isoformat()

        # Generate authentication tokens
        lambda_id = user_record["lambda_id"]
        access_token = _generate_access_token(username, lambda_id)
        refresh_token = _generate_refresh_token(username)

        # Create or update session
        session_id = f"sess_{secrets.token_hex(16)}"
        user_sessions[session_id] = {
            "user_id": username,
            "lambda_id": lambda_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "access_token_jti": jwt.decode(access_token, options={"verify_signature": False})["iat"],
        }

        logger.info(f"ΛTRACE ({request_id}): User {username} logged in successfully")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "request_id": request_id,
                    "user": {
                        "user_id": username,
                        "lambda_id": lambda_id,
                        "email": user_record.get("email", ""),
                        "last_login": user_record["last_login"],
                    },
                    "tokens": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer",
                        "expires_in": int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds()),
                    },
                    "session_id": session_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Login error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error during login",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Token validation helper functions
def _validate_jwt_token(token: str) -> tuple[bool, Optional[dict], str]:
    """
    Validate JWT token and return decoded payload.
    Returns (is_valid, payload, error_message)
    """
    try:
        # Check if token is blacklisted
        if token in blacklisted_tokens:
            return False, None, "Token has been revoked"

        # Decode and validate token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Check token type
        if payload.get("token_type") not in ["access", "refresh"]:
            return False, None, "Invalid token type"

        # Check expiration (JWT library handles this, but we can add custom logic)
        current_time = datetime.now(timezone.utc)
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.fromtimestamp(exp_timestamp, timezone.utc) < current_time:
            return False, None, "Token has expired"

        return True, payload, ""

    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, None, f"Invalid token: {e!s}"
    except Exception as e:
        return False, None, f"Token validation error: {e!s}"


def _extract_token_from_request(request) -> tuple[Optional[str], str]:
    """
    Extract token from request headers or body.
    Returns (token, error_message)
    """
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:], ""

    # Try request body for token
    if request.is_json:
        data = request.get_json()
        if "token" in data:
            return data["token"], ""
        if "access_token" in data:
            return data["access_token"], ""

    return None, "No valid token found in request"


# Human-readable comment: Endpoint for user logout.
@auth_bp.route("/logout", methods=["POST"])
def logout_user_endpoint():
    """
    Handles secure user logout with token invalidation.
    Blacklists tokens, terminates sessions, and provides audit trail.
    """
    request_id = f"logout_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /logout.")

    try:
        # Extract token from request
        token, token_error = _extract_token_from_request(request)

        if not token:
            logger.warning(f"ΛTRACE ({request_id}): Logout attempt without valid token")
            return (
                jsonify({"success": False, "message": token_error, "request_id": request_id}),
                401,
            )

        # Validate token
        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            logger.warning(f"ΛTRACE ({request_id}): Logout attempt with invalid token")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")

        # Add token to blacklist
        blacklisted_tokens.add(token)

        # Also blacklist refresh token if provided
        if request.is_json:
            data = request.get_json()
            refresh_token = data.get("refresh_token")
            if refresh_token:
                blacklisted_tokens.add(refresh_token)

        # Terminate user sessions
        sessions_terminated = 0
        for session_id, session_data in list(user_sessions.items()):
            if session_data.get("user_id") == user_id:
                del user_sessions[session_id]
                sessions_terminated += 1

        logger.info(
            f"ΛTRACE ({request_id}): User {user_id} logged out successfully, {sessions_terminated} sessions terminated"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Logout successful",
                    "request_id": request_id,
                    "sessions_terminated": sessions_terminated,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Logout error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error during logout",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Human-readable comment: Endpoint for verifying an authentication token.
@auth_bp.route("/token/verify", methods=["POST"])
def verify_authentication_token_endpoint():
    """
    Comprehensive JWT token verification with detailed validation.
    Validates token signature, expiration, user existence, and session status.
    Returns user information and token claims if valid.
    """
    request_id = f"verify_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /token/verify.")

    try:
        # Extract token from request
        token, token_error = _extract_token_from_request(request)

        if not token:
            logger.warning(f"ΛTRACE ({request_id}): Token verification attempt without valid token")
            return (
                jsonify(
                    {
                        "success": False,
                        "valid": False,
                        "message": token_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        # Validate token
        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            logger.warning(f"ΛTRACE ({request_id}): Invalid token verification attempt")
            return (
                jsonify(
                    {
                        "success": False,
                        "valid": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")
        lambda_id = payload.get("lambda_id")
        token_type = payload.get("token_type")

        # Check if user still exists and is active
        if user_id not in users_db:
            logger.warning(f"ΛTRACE ({request_id}): Token valid but user {user_id} not found")
            return (
                jsonify(
                    {
                        "success": False,
                        "valid": False,
                        "message": "User associated with token no longer exists",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_record = users_db[user_id]

        if not user_record.get("is_active", True):
            logger.warning(f"ΛTRACE ({request_id}): Token valid but user {user_id} is inactive")
            return (
                jsonify(
                    {
                        "success": False,
                        "valid": False,
                        "message": "User account is inactive",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        # Check if user has active sessions (for access tokens)
        active_sessions = []
        if token_type == "access":
            for session_id, session_data in user_sessions.items():
                if session_data.get("user_id") == user_id:
                    active_sessions.append(
                        {
                            "session_id": session_id,
                            "created_at": session_data.get("created_at"),
                            "last_active": session_data.get("last_active"),
                            "ip_address": session_data.get("ip_address", "unknown"),
                        }
                    )

        # Prepare token claims (exclude sensitive data)
        token_claims = {
            "user_id": user_id,
            "lambda_id": lambda_id,
            "token_type": token_type,
            "issued_at": datetime.fromtimestamp(payload.get("iat"), timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(payload.get("exp"), timezone.utc).isoformat(),
            "time_until_expiry": payload.get("exp") - time.time(),
        }

        # Prepare user information
        user_info = {
            "user_id": user_id,
            "lambda_id": lambda_id,
            "email": user_record.get("email", ""),
            "created_at": user_record.get("created_at"),
            "last_login": user_record.get("last_login"),
            "is_active": user_record.get("is_active", True),
            "active_sessions_count": len(active_sessions),
        }

        logger.info(f"ΛTRACE ({request_id}): Token verification successful for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "valid": True,
                    "message": "Token is valid",
                    "request_id": request_id,
                    "token_claims": token_claims,
                    "user": user_info,
                    "active_sessions": (active_sessions if token_type == "access" else []),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Token verification error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "valid": False,
                    "message": "Internal server error during token verification",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Additional endpoint: Token refresh
@auth_bp.route("/token/refresh", methods=["POST"])
def refresh_token_endpoint():
    """
    Refresh access token using a valid refresh token.
    Provides secure token rotation for maintaining authentication.
    """
    request_id = f"refresh_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /token/refresh.")

    try:
        # Extract refresh token
        if not request.is_json:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Content-Type must be application/json",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Missing refresh_token",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        # Validate refresh token
        is_valid, payload, validation_error = _validate_jwt_token(refresh_token)

        if not is_valid:
            logger.warning(f"ΛTRACE ({request_id}): Invalid refresh token")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        # Verify token type
        if payload.get("token_type") != "refresh":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid token type for refresh",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")

        # Check user exists and is active
        if user_id not in users_db or not users_db[user_id].get("is_active", True):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "User account is invalid or inactive",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_record = users_db[user_id]
        lambda_id = user_record["lambda_id"]

        # Generate new access token
        new_access_token = _generate_access_token(user_id, lambda_id)

        # Optionally generate new refresh token (token rotation)
        new_refresh_token = _generate_refresh_token(user_id)

        # Blacklist old refresh token
        blacklisted_tokens.add(refresh_token)

        logger.info(f"ΛTRACE ({request_id}): Token refresh successful for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "request_id": request_id,
                    "tokens": {
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token,
                        "token_type": "Bearer",
                        "expires_in": int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds()),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Token refresh error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error during token refresh",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Additional security endpoints


@auth_bp.route("/user/profile", methods=["GET"])
def get_user_profile():
    """
    Get user profile information (requires valid access token).
    """
    request_id = f"profile_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received GET request to /user/profile.")

    try:
        # Extract and validate token
        token, token_error = _extract_token_from_request(request)

        if not token:
            return (
                jsonify({"success": False, "message": token_error, "request_id": request_id}),
                401,
            )

        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")

        if user_id not in users_db:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "User not found",
                        "request_id": request_id,
                    }
                ),
                404,
            )

        user_record = users_db[user_id]

        # Return user profile (exclude sensitive data)
        profile = {
            "user_id": user_id,
            "lambda_id": user_record["lambda_id"],
            "email": user_record.get("email", ""),
            "created_at": user_record.get("created_at"),
            "last_login": user_record.get("last_login"),
            "is_active": user_record.get("is_active", True),
            "failed_login_count": user_record.get("failed_login_count", 0),
        }

        return (
            jsonify({"success": True, "profile": profile, "request_id": request_id}),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Profile fetch error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id,
                }
            ),
            500,
        )


@auth_bp.route("/user/change-password", methods=["POST"])
def change_password():
    """
    Change user password (requires valid access token and current password).
    """
    request_id = f"changepw_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /user/change-password.")

    try:
        if not request.is_json:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Content-Type must be application/json",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        data = request.get_json()

        # Extract and validate token
        token, token_error = _extract_token_from_request(request)

        if not token:
            return (
                jsonify({"success": False, "message": token_error, "request_id": request_id}),
                401,
            )

        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Both current_password and new_password are required",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        if user_id not in users_db:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "User not found",
                        "request_id": request_id,
                    }
                ),
                404,
            )

        user_record = users_db[user_id]

        # Verify current password
        if not bcrypt.checkpw(
            current_password.encode("utf-8"),
            user_record["password_hash"].encode("utf-8"),
        ):
            logger.warning(f"ΛTRACE ({request_id}): Invalid current password for user {user_id}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Current password is incorrect",
                        "request_id": request_id,
                    }
                ),
                401,
            )

        # Validate new password strength
        valid_password, password_message = _validate_password_strength(new_password)
        if not valid_password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": password_message,
                        "request_id": request_id,
                    }
                ),
                400,
            )

        # Update password
        new_password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        users_db[user_id]["password_hash"] = new_password_hash.decode("utf-8")

        logger.info(f"ΛTRACE ({request_id}): Password changed successfully for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Password changed successfully",
                    "request_id": request_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Password change error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id,
                }
            ),
            500,
        )


@auth_bp.route("/user/sessions", methods=["GET"])
def get_user_sessions():
    """
    Get active sessions for the authenticated user.
    """
    request_id = f"sessions_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received GET request to /user/sessions.")

    try:
        # Extract and validate token
        token, token_error = _extract_token_from_request(request)

        if not token:
            return (
                jsonify({"success": False, "message": token_error, "request_id": request_id}),
                401,
            )

        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")

        # Get all sessions for this user
        active_sessions = []
        for session_id, session_data in user_sessions.items():
            if session_data.get("user_id") == user_id:
                active_sessions.append(
                    {
                        "session_id": session_id,
                        "created_at": session_data.get("created_at"),
                        "last_active": session_data.get("last_active"),
                        "ip_address": session_data.get("ip_address", "unknown"),
                        "user_agent": session_data.get("user_agent", "unknown"),
                    }
                )

        return (
            jsonify(
                {
                    "success": True,
                    "sessions": active_sessions,
                    "total_sessions": len(active_sessions),
                    "request_id": request_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Sessions fetch error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id,
                }
            ),
            500,
        )


@auth_bp.route("/user/revoke-session", methods=["POST"])
def revoke_session():
    """
    Revoke a specific session by session ID.
    """
    request_id = f"revoke_{int(time.time()) * 1000}"
    logger.info(f"ΛTRACE ({request_id}): Received POST request to /user/revoke-session.")

    try:
        if not request.is_json:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Content-Type must be application/json",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        data = request.get_json()

        # Extract and validate token
        token, token_error = _extract_token_from_request(request)

        if not token:
            return (
                jsonify({"success": False, "message": token_error, "request_id": request_id}),
                401,
            )

        is_valid, payload, validation_error = _validate_jwt_token(token)

        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": validation_error,
                        "request_id": request_id,
                    }
                ),
                401,
            )

        user_id = payload.get("user_id")
        session_to_revoke = data.get("session_id")

        if not session_to_revoke:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "session_id is required",
                        "request_id": request_id,
                    }
                ),
                400,
            )

        # Check if session exists and belongs to user
        if session_to_revoke not in user_sessions:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Session not found",
                        "request_id": request_id,
                    }
                ),
                404,
            )

        session_data = user_sessions[session_to_revoke]
        if session_data.get("user_id") != user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Session does not belong to authenticated user",
                        "request_id": request_id,
                    }
                ),
                403,
            )

        # Revoke session
        del user_sessions[session_to_revoke]

        logger.info(f"ΛTRACE ({request_id}): Session {session_to_revoke} revoked for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Session revoked successfully",
                    "revoked_session_id": session_to_revoke,
                    "request_id": request_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"ΛTRACE ({request_id}): Session revocation error: {e!s}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id,
                }
            ),
            500,
        )


# Security middleware decorator for protected endpoints
def require_auth(f):
    """
    Decorator to require valid authentication for endpoints.
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_id = f"auth_{int(time.time()) * 1000}"

        try:
            # Extract and validate token
            token, token_error = _extract_token_from_request(request)

            if not token:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": token_error,
                            "request_id": request_id,
                        }
                    ),
                    401,
                )

            is_valid, payload, validation_error = _validate_jwt_token(token)

            if not is_valid:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": validation_error,
                            "request_id": request_id,
                        }
                    ),
                    401,
                )

            # Add user info to request context
            request.current_user = {
                "user_id": payload.get("user_id"),
                "lambda_id": payload.get("lambda_id"),
                "token_type": payload.get("token_type"),
            }

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"ΛTRACE ({request_id}): Auth middleware error: {e!s}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Authentication error",
                        "request_id": request_id,
                    }
                ),
                500,
            )

    return decorated_function


logger.info("ΛTRACE: auth_flows module loaded with comprehensive authentication system.")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: auth_flows.py
# VERSION: 1.0.0
# TIER SYSTEM: Specific tiers would apply per endpoint upon full implementation (e.g., based on user context).
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Implements comprehensive authentication API endpoints with JWT tokens, secure password handling, and session management.
# FUNCTIONS: register_user_endpoint, login_user_endpoint, logout_user_endpoint, verify_authentication_token_endpoint, require_auth decorator.
# CLASSES: None.
# DECORATORS: @auth_bp.route (Flask Blueprint), require_auth (authentication middleware).
# DEPENDENCIES: Flask (Blueprint, request, jsonify), logging, time, JWT, bcrypt, hashlib, secrets.
# INTERFACES: Exposes HTTP endpoints under the /api/v2/auth prefix (once Blueprint is registered).
# ERROR HANDLING: Comprehensive error handling with appropriate HTTP status codes and detailed error messages.
# LOGGING: ΛTRACE_ENABLED for request tracking, security events, and authentication flows.
# AUTHENTICATION: Full authentication system with JWT tokens, password strength validation, brute-force protection, and session management.
# HOW TO USE:
#   Register `auth_bp` with the main Flask application.
#   Endpoints will then be accessible, e.g., POST /api/v2/auth/register.
# INTEGRATION NOTES: This module provides comprehensive authentication functionality with secure token management,
#                    password hashing, session handling, and brute-force protection. Ready for production use
#                    with proper database backend integration (currently using in-memory storage for demo).
# MAINTENANCE: Consider integrating with LUKHAS identity services for advanced features like tiered authentication
#              and implementing persistent database storage for production deployment.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
