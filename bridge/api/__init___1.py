# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: lukhas_id.api
# DESCRIPTION: Initializes the LUKHAS ΛiD API Flask application, including configuration,
#              extensions, blueprints, logging, and error handlers.
# DEPENDENCIES: Flask, Flask-CORS, Flask-Limiter, logging, datetime, os, pathlib,
#               .routes.lambd_id_routes
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

from core.common import get_logger
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
from pathlib import Path
import traceback # For more detailed error logging if needed

# Initialize ΛTRACE logger for this API package

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


logger = logging.getLogger("ΛTRACE.lukhas_id.api")
logger.info("ΛTRACE: Initializing LUKHAS ΛiD API package.")

# Import route blueprints
try:
    from .routes.lambd_id_routes import lambd_id_bp
    logger.info("ΛTRACE: Successfully imported lambd_id_bp blueprint.")
except ImportError as e:
    logger.error(f"ΛTRACE: Failed to import lambd_id_bp blueprint: {e}", exc_info=True)
    lambd_id_bp = None # Fallback

# Human-readable comment: Application factory function for the LUKHAS ΛiD API.
def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory for LUKHAS ΛiD API. Creates and configures a Flask app instance.

    Args:
        config_name (str): Configuration environment (e.g., 'development', 'testing', 'production').

    Returns:
        Flask: The configured Flask application instance.
    """
    logger.info(f"ΛTRACE: Creating Flask app with config_name: '{config_name}'.")

    app = Flask(__name__)
    logger.debug(f"ΛTRACE: Flask app instance '{__name__}' created.")

    _configure_app(app, config_name)           # Configures app settings
    _initialize_extensions(app)                # Initializes Flask extensions like CORS, Limiter
    _register_blueprints(app)                  # Registers API route blueprints
    _configure_app_logging(app, config_name)   # Configures Flask's operational logging
    _register_error_handlers(app)              # Sets up custom error handlers
    _add_health_check_endpoint(app)            # Adds a health check endpoint
    _add_request_response_logging(app)         # Adds middleware for request/response logging

    logger.info(f"ΛTRACE: Flask app creation complete for config '{config_name}'.")
    return app

# Human-readable comment: Configures the Flask application instance.
def _configure_app(app: Flask, config_name: str) -> None:
    """Configures the Flask application with settings based on the environment."""
    logger.info(f"ΛTRACE: Configuring app for '{config_name}' environment.")

    # CLAUDE_EDIT_v0.13: Fixed hardcoded secret key vulnerability - require env var in production
    secret_key = os.environ.get('LUKHAS_ID_API_SECRET_KEY')
    if not secret_key and config_name == 'production':
        raise ValueError("LUKHAS_ID_API_SECRET_KEY must be set in production environment")
    app.config['SECRET_KEY'] = secret_key or 'dev-only-key'
    app.config['DEBUG'] = (config_name == 'development')
    app.config['TESTING'] = (config_name == 'testing')
    logger.debug(f"ΛTRACE: App SECRET_KEY {'set from ENV' if 'LUKHAS_ID_API_SECRET_KEY' in os.environ else 'is default'}. DEBUG={app.config['DEBUG']}, TESTING={app.config['TESTING']}.")

    # Rate limiting configuration
    app.config['RATELIMIT_STORAGE_URL'] = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://') # Use Redis in prod
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window' # Other options: 'moving-window', etc.
    app.config['RATELIMIT_HEADERS_ENABLED'] = True
    logger.debug(f"ΛTRACE: Rate limiting configured. Storage: {app.config['RATELIMIT_STORAGE_URL']}.")

    # CORS configuration - adjust origins for production
    cors_origins = os.environ.get('LUKHAS_ID_API_CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000,https://*.lukhas.ai').split(',')
    app.config['CORS_ORIGINS'] = [origin.strip() for origin in cors_origins]
    logger.debug(f"ΛTRACE: CORS configured for origins: {app.config['CORS_ORIGINS']}.")

    # ΛiD specific application configuration (can be loaded from a dedicated config file or ENV)
    app.config['LAMBD_ID_SETTINGS'] = {
        'max_generation_attempts': int(os.environ.get('LAMBD_ID_MAX_GEN_ATTEMPTS', 5)),
        'default_tier': int(os.environ.get('LAMBD_ID_DEFAULT_TIER', 0)),
        'enable_collision_detection': os.environ.get('LAMBD_ID_COLLISION_DETECTION', 'True').lower() == 'true',
        'enable_activity_logging': os.environ.get('LAMBD_ID_ACTIVITY_LOGGING', 'True').lower() == 'true'
    }
    logger.debug(f"ΛTRACE: LAMBD_ID_SETTINGS configured: {app.config['LAMBD_ID_SETTINGS']}.")
    logger.info(f"ΛTRACE: App configuration for '{config_name}' complete.")

# Human-readable comment: Initializes Flask extensions.
def _initialize_extensions(app: Flask) -> None:
    """Initializes Flask extensions such as CORS and Limiter."""
    logger.info("ΛTRACE: Initializing Flask extensions.")

    # Initialize CORS with origins from app.config
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'), supports_credentials=True)
    logger.debug("ΛTRACE: CORS initialized.")

    # Initialize rate limiter
    limiter = Limiter(
        app=app, # Corrected: pass app directly
        key_func=get_remote_address,
        default_limits=[os.environ.get('DEFAULT_RATE_LIMIT_PER_HOUR', "1000 per hour"),
                        os.environ.get('DEFAULT_RATE_LIMIT_PER_MINUTE', "100 per minute")]
    )
    app.extensions['limiter'] = limiter # Store limiter instance if needed elsewhere
    logger.debug(f"ΛTRACE: Flask-Limiter initialized with default limits.")
    logger.info("ΛTRACE: Flask extensions initialized.")

# Human-readable comment: Registers API blueprints with the Flask application.
def _register_blueprints(app: Flask) -> None:
    """Registers all API blueprints for the application."""
    logger.info("ΛTRACE: Registering blueprints.")

    if lambd_id_bp:
        app.register_blueprint(lambd_id_bp, url_prefix='/api/v1/lambda-id') # Example prefix
        logger.debug("ΛTRACE: lambd_id_bp blueprint registered at /api/v1/lambda-id.")
    else:
        logger.error("ΛTRACE: lambd_id_bp is None, skipping registration. ΛiD routes will be unavailable.")

    # API Info Endpoint (general to this API application)
    # Human-readable comment: Defines a general API information endpoint.
    @app.route('/api/v1/id-api/info', methods=['GET']) # More specific path
    def id_api_info_endpoint():
        """Provides general information about the LUKHAS ΛiD API."""
        endpoint_path = '/api/v1/id-api/info'
        logger.info(f"ΛTRACE: Request to {endpoint_path}.")
        info_data = {
            'api_name': 'LUKHAS ΛiD API',
            'version': app.config.get('API_VERSION_LID', '1.0.1'), # Assuming a config var for version
            'description': 'LUKHAS Lambda Identity (ΛiD) Management System API.',
            'contact_support': os.environ.get('LUKHAS_SUPPORT_EMAIL', 'support@lukhas.ai'),
            'documentation_url': 'https://docs.lukhas.ai/apis/lambda-id'
        }
        logger.debug(f"ΛTRACE: Returning API info: {info_data}")
        return jsonify(info_data), 200
    logger.debug("ΛTRACE: General API info endpoint registered at /api/v1/id-api/info.")
    logger.info("ΛTRACE: Blueprints registered.")

# Human-readable comment: Configures Flask's application logging (distinct from ΛTRACE for operational logs).
def _configure_app_logging(app: Flask, config_name: str) -> None:
    """Configures Flask's built-in logger for application operational messages."""
    log_level_str = os.environ.get('LUKHAS_ID_API_LOG_LEVEL', 'DEBUG' if config_name == 'development' else 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger.info(f"ΛTRACE: Configuring Flask app logging. Level: {log_level_str}.")

    # Ensure logs directory exists (e.g., project_root/logs/lukhas_id_api/)
    # Path().parent.parent assumes this __init__.py is two levels deep from where 'logs' should be.
    # Adjust if structure is different. Example: api/__init__.py -> lukhas/identity/ -> project_root/
    logs_base_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
    api_log_dir = logs_base_dir / 'lukhas_id_api'
    try:
        api_log_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"ΛTRACE: Log directory ensured at {api_log_dir}.")
    except OSError as e:
        logger.error(f"ΛTRACE: Could not create log directory {api_log_dir}: {e}", exc_info=True)
        # Continue without file logging if directory creation fails
        log_file_handler = None
    else:
        log_file_path = api_log_dir / 'lukhas_id_api_operational.log'
        log_file_handler = logging.FileHandler(log_file_path)
        log_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

    # Remove default Flask handler to avoid duplicate console logs if we add our own
    app.logger.handlers.clear()
    app.logger.setLevel(log_level)

    # Console Handler for Flask operational logs
    console_handler = logging.StreamHandler(sys.stdout) # Use stdout for console
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s (FlaskOp) - %(levelname)s - %(message)s'))
    app.logger.addHandler(console_handler)

    if log_file_handler:
        app.logger.addHandler(log_file_handler)
        logger.info(f"ΛTRACE: Flask app operational logs will be written to {log_file_path}.")
    else:
        logger.warning("ΛTRACE: File logging for Flask app operational logs is disabled due to directory issue.")

    # Also ensure our ΛTRACE logger has a handler if none were configured externally (e.g. for dev)
    if not logging.getLogger("ΛTRACE").handlers:
        trace_console_handler = logging.StreamHandler(sys.stdout)
        trace_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ΛTRACE: %(message)s'))
        logging.getLogger("ΛTRACE").addHandler(trace_console_handler)
        logging.getLogger("ΛTRACE").setLevel(logging.DEBUG if config_name == 'development' else logging.INFO)
        logger.info("ΛTRACE: Basic console handler added for ΛTRACE root logger (as no handlers were found).")

    app.logger.info(f"LUKHAS ΛiD API (Flask Operational) logging configured at level {log_level_str}.") # Uses app.logger
    logger.info("ΛTRACE: Flask app operational logging configuration complete.") # Uses module's ΛTRACE logger


# Human-readable comment: Registers custom error handlers for the Flask application.
def _register_error_handlers(app: Flask) -> None:
    """Registers custom JSON error handlers for common HTTP status codes."""
    logger.info("ΛTRACE: Registering custom error handlers.")

    # Human-readable comment: Handles 400 Bad Request errors.
    @app.errorhandler(400)
    def handle_bad_request(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 400 Bad Request errors by returning a JSON response."""
        err_desc = str(error.description) if hasattr(error, 'description') else 'Invalid request format or data.'
        logger.warning(f"ΛTRACE: Handling 400 Bad Request. Path: {request.path}. Description: {err_desc}", exc_info=False)
        return jsonify({'success': False, 'error': 'Bad Request', 'error_code': 'BAD_REQUEST', 'message': err_desc}), 400

    # Human-readable comment: Handles 401 Unauthorized errors.
    @app.errorhandler(401)
    def handle_unauthorized(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 401 Unauthorized errors, typically due to missing or invalid authentication."""
        logger.warning(f"ΛTRACE: Handling 401 Unauthorized. Path: {request.path}.", exc_info=False)
        return jsonify({'success': False, 'error': 'Unauthorized', 'error_code': 'UNAUTHORIZED_ACCESS', 'message': 'Valid authentication credentials are required.'}), 401

    # Human-readable comment: Handles 403 Forbidden errors.
    @app.errorhandler(403)
    def handle_forbidden(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 403 Forbidden errors, due to insufficient permissions for an authenticated user."""
        logger.warning(f"ΛTRACE: Handling 403 Forbidden. Path: {request.path}. User (if available): {getattr(request,'user_id','N/A')}.", exc_info=False)
        return jsonify({'success': False, 'error': 'Forbidden', 'error_code': 'INSUFFICIENT_PERMISSIONS', 'message': 'You do not have sufficient permissions to access this resource.'}), 403

    # Human-readable comment: Handles 404 Not Found errors.
    @app.errorhandler(404)
    def handle_not_found(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 404 Not Found errors when a requested resource does not exist."""
        logger.warning(f"ΛTRACE: Handling 404 Not Found. Path: {request.path}.", exc_info=False)
        return jsonify({'success': False, 'error': 'Not Found', 'error_code': 'RESOURCE_NOT_FOUND', 'message': 'The requested resource could not be found on this server.'}), 404

    # Human-readable comment: Handles 405 Method Not Allowed errors.
    @app.errorhandler(405)
    def handle_method_not_allowed(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 405 Method Not Allowed errors when an HTTP method is not supported for an endpoint."""
        logger.warning(f"ΛTRACE: Handling 405 Method Not Allowed. Path: {request.path}, Method: {request.method}.", exc_info=False)
        return jsonify({'success': False, 'error': 'Method Not Allowed', 'error_code': 'METHOD_NOT_SUPPORTED', 'message': f"The method '{request.method}' is not allowed for the resource '{request.path}'."}), 405

    # Human-readable comment: Handles 429 Rate Limit Exceeded errors.
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error: Any) -> tuple[str, int]: # error type is specific to Flask-Limiter
        """Handles 429 Too Many Requests errors when rate limits are exceeded."""
        retry_after_val = str(error.retry_after) if hasattr(error, 'retry_after') else None
        logger.warning(f"ΛTRACE: Handling 429 Rate Limit Exceeded. Path: {request.path}, Remote Addr: {get_remote_address()}. RetryAfter: {retry_after_val}", exc_info=False)
        return jsonify({'success': False, 'error': 'Rate Limit Exceeded', 'error_code': 'TOO_MANY_REQUESTS', 'message': 'You have exceeded the allowed rate limit. Please try again later.', 'retry_after_seconds': retry_after_val}), 429

    # Human-readable comment: Handles generic 500 Internal Server Errors.
    @app.errorhandler(500) # Catches exceptions explicitly raised as 500 or Werkzeug internal 500s
    def handle_internal_server_error(error: Exception) -> tuple[str, int]: # type: ignore
        """Handles 500 Internal Server Error, typically for unhandled exceptions in app code."""
        logger.error(f"ΛTRACE: Handling 500 Internal Server Error. Path: {request.path}. Error: {error}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal Server Error', 'error_code': 'INTERNAL_SERVER_ERROR_CAUGHT', 'message': 'An unexpected internal error occurred. The LUKHAS team has been notified.'}), 500

    # Human-readable comment: Handles all other uncaught Python exceptions.
    @app.errorhandler(Exception) # Catch-all for any other Python exceptions not caught by specific handlers
    def handle_generic_exception(error: Exception) -> tuple[str, int]:
        """Handles any other uncaught Python exceptions, returning a generic 500 error."""
        logger.critical(f"ΛTRACE: Handling generic unhandled Python exception. Path: {request.path}. Error: {error}", exc_info=True)
        # It's good practice to not expose detailed error messages from generic exceptions to the client.
        return jsonify({'success': False, 'error': 'Unexpected System Error', 'error_code': 'UNHANDLED_SYSTEM_EXCEPTION', 'message': 'An unexpected critical error occurred. The LUKHAS technical team has been alerted.'}), 500
    logger.info("ΛTRACE: Custom error handlers registered.")

# Human-readable comment: Adds a health check endpoint to the application.
def _add_health_check_endpoint(app: Flask) -> None:
    """Adds a /health endpoint for monitoring application health and dependencies."""
    logger.info("ΛTRACE: Adding health check endpoint.")

    # Human-readable comment: Health check endpoint for the ΛiD API.
    @app.route('/healthz') # Common path for health checks, also used by Kubernetes
    @app.route('/api/v1/id-api/health') # API-versioned health check
    def health_check_endpoint_func(): # Renamed for clarity
        """Provides a health status report for the API and its key dependencies."""
        path_accessed = request.path
        logger.info(f"ΛTRACE: Health check requested at {path_accessed}.")
        try:
            # Basic health indicators
            current_health_status: Dict[str, Any] = {
                'application_status': 'healthy', 'timestamp': datetime.now().isoformat(),
                'api_version': app.config.get('API_VERSION_LID', '1.0.1'),
                'environment': 'development' if app.config.get('DEBUG') else 'production',
                'service_dependencies': {'core_api_interface': 'healthy', 'logging_subsystem': 'healthy'}
            }

            # Example: Check critical dependencies like core services (if applicable here)
            # This is a placeholder; actual checks would involve pinging or testing connections.
            try:
                # Attempt a non-mutating operation or import check
                # from ...core.id_service.lambd_id_generator import LambdaIDGenerator # Path needs to be correct
                # _ = LambdaIDGenerator() # Simple instantiation test
                current_health_status['service_dependencies']['id_generator_service'] = 'healthy_mock_check'
            except ImportError:
                logger.warning("ΛTRACE: Health Check: id_generator_service import failed (dependency issue).")
                current_health_status['service_dependencies']['id_generator_service'] = 'unavailable_import_failed'
                current_health_status['application_status'] = 'degraded'

            # Determine overall status code
            http_status_code = 200 if current_health_status['application_status'] == 'healthy' else 503 # 503 Service Unavailable
            logger.info(f"ΛTRACE: Health check at {path_accessed} completed. Status: {current_health_status['application_status']}, HTTP Code: {http_status_code}.")
            return jsonify(current_health_status), http_status_code

        except Exception as e_health:
            logger.error(f"ΛTRACE: Critical error during health check at {path_accessed}: {e_health}", exc_info=True)
            return jsonify({'application_status': 'unhealthy', 'timestamp': datetime.now().isoformat(), 'error_details': 'Health check routine failed.'}), 503
    logger.info("ΛTRACE: Health check endpoint added at /healthz and /api/v1/id-api/health.")

# Human-readable comment: Adds request and response logging middleware.
def _add_request_response_logging(app: Flask) -> None:
    """Adds middleware to log details of incoming requests and outgoing responses using ΛTRACE."""
    logger.info("ΛTRACE: Adding request/response logging middleware.")

    # Human-readable comment: Logs information about each incoming request.
    @app.before_request
    def log_incoming_request_info():
        """Logs details of each incoming HTTP request, excluding health checks."""
        if not request.path.startswith(('/healthz', '/api/v1/id-api/health')): # Avoid logging frequent health checks
            user_id = request.headers.get('X-User-ID', 'anonymous') # Example: Get User ID if available
            logger.info(f"ΛTRACE: Incoming Request --> User: '{user_id}', Method: {request.method}, Path: {request.path}, RemoteAddr: {request.remote_addr}, Headers: {dict(request.headers)}")
            if request.data: # Log request body if present (be careful with sensitive data in prod logs)
                 logger.debug(f"ΛTRACE: Request Body (first 500 chars): {request.get_data(as_text=True)[:500]}")

    # Human-readable comment: Logs information about each outgoing response.
    @app.after_request
    def log_outgoing_response_info(response: Any) -> Any: # Response type is flask.Response
        """Logs details of each outgoing HTTP response, excluding health checks."""
        if not request.path.startswith(('/healthz', '/api/v1/id-api/health')):
            user_id = request.headers.get('X-User-ID', 'anonymous')
            logger.info(f"ΛTRACE: Outgoing Response <-- User: '{user_id}', Method: {request.method}, Path: {request.path}, Status: {response.status_code}, Size: {response.content_length} bytes")
            if response.is_json and response.content_length is not None and response.content_length < 2048 : # Log small JSON response bodies
                 logger.debug(f"ΛTRACE: Response Body (JSON): {response.get_data(as_text=True)}")
        return response
    logger.info("ΛTRACE: Request/response logging middleware added.")

# Human-readable comment: Main block for development server execution.
if __name__ == '__main__':
    logger.info("ΛTRACE: lukhas_id.api.__init__.py executed as main script.")
    # Create Flask app instance using the factory with 'development' config
    flask_app = create_app(config_name='development')

    # Development server specific settings
    dev_host = os.environ.get('LUKHAS_ID_API_DEV_HOST', '0.0.0.0')
    dev_port = int(os.environ.get('LUKHAS_ID_API_DEV_PORT', 5003)) # Using a distinct port
    dev_debug_mode = flask_app.config.get('DEBUG', True)

    logger.info(f"🚀 LUKHAS ΛiD API Development Server starting on http://{dev_host}:{dev_port}/ (Debug: {dev_debug_mode})")
    logger.info(f"🔗 Registered Blueprints (example): /api/v1/lambda-id/*")
    logger.info(f"ℹ️ API Info endpoint: /api/v1/id-api/info")
    logger.info(f"🩺 Health Check endpoint: /healthz or /api/v1/id-api/health")

    try:
        # Run the Flask development server
        # For production, use a WSGI server like Gunicorn or uWSGI.
        flask_app.run(host=dev_host, port=dev_port, debug=dev_debug_mode, threaded=True)
    except Exception as e_server_main:
        logger.critical(f"ΛTRACE: Failed to start LUKHAS ΛiD API development server: {e_server_main}", exc_info=True)
        print(f"❌ Failed to start LUKHAS ΛiD API server: {e_server_main}")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.1.0 # Updated version
# TIER SYSTEM: Authentication/Authorization handled by specific endpoints (e.g., via @require_auth in api_controllers)
# ΛTRACE INTEGRATION: ENABLED (Extensive logging for app creation, config, requests, errors)
# CAPABILITIES: Flask application factory for LUKHAS ΛiD API.
#               Sets up configuration, extensions (CORS, Limiter), blueprints,
#               logging (Flask operational & ΛTRACE), error handlers, health checks.
# FUNCTIONS: create_app, _configure_app, _initialize_extensions, _register_blueprints,
#            _configure_app_logging, _register_error_handlers, _add_health_check_endpoint,
#            _add_request_response_logging.
# CLASSES: None (uses Flask app object).
# DECORATORS: @app.route, @app.errorhandler, @app.before_request, @app.after_request.
# DEPENDENCIES: Flask, Flask-CORS, Flask-Limiter, logging, datetime, os, pathlib, traceback.
# INTERFACES: Creates and returns a Flask application instance.
# ERROR HANDLING: Registers custom handlers for HTTP error codes and generic exceptions.
# LOGGING: ΛTRACE_ENABLED for detailed API lifecycle and operational tracing.
#          Configures Flask's operational logger to output to console and a file.
# AUTHENTICATION: Framework for authentication is set up (e.g. SECRET_KEY); specific
#                 auth logic resides in endpoints or dedicated auth modules.
# HOW TO USE:
#   from identity.api import create_app
#   app = create_app(config_name='production')
#   # Then run with a WSGI server, e.g., gunicorn "your_project.wsgi:app"
# INTEGRATION NOTES: This __init__.py is the entry point for creating the ΛiD API application.
#                    Ensure environment variables for configuration (SECRET_KEY, CORS_ORIGINS, etc.) are set.
#                    Logging paths and levels are configurable.
# MAINTENANCE: Review and update configurations, especially for production (SECRET_KEY, CORS, rate limits).
#              Ensure blueprint registration and route prefixes are correct as the API evolves.
#              Monitor logs (both operational and ΛTRACE) for issues.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
