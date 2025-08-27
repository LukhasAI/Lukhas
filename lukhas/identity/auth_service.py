"""
LUKHAS Identity Authentication Service
=====================================
Unified authentication service that bridges legacy systems with modern identity management.
Provides secure authentication with fallback support and progressive enhancement.
"""

import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path

# Standard library fallback imports
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Try importing LUKHAS identity components with fallbacks
try:
    from .wallet import WalletManager
    WALLET_AVAILABLE = True
except ImportError:
    WALLET_AVAILABLE = False

# NOTE: Disabled cross-lane import from candidate
# try:
#     from candidate.core.orchestration.brain.identity_manager import IdentityManager
#     IDENTITY_MANAGER_AVAILABLE = True
# except ImportError:
#     IDENTITY_MANAGER_AVAILABLE = False
IDENTITY_MANAGER_AVAILABLE = False  # Disabled to avoid cross-lane import

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    """Authentication result container"""
    success: bool
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    permissions: List[str] = None
    expires_at: Optional[float] = None
    error: Optional[str] = None
    auth_method: str = "unknown"
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


@dataclass
class UserProfile:
    """User profile container"""
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: float = None
    last_login: Optional[float] = None
    permissions: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = ["basic_access"]
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = time.time()


class AuthenticationService:
    """
    Unified authentication service for LUKHAS AI.
    
    Supports multiple authentication methods:
    - Local username/password with secure hashing
    - JWT token-based authentication (if available)
    - Wallet-based authentication (if available) 
    - Identity Manager integration (if available)
    - API key authentication for services
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("auth.service")
        
        # Initialize storage
        self._init_storage()
        
        # Initialize components based on availability
        self._init_wallet_integration()
        self._init_identity_integration()
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = self.config.get("session_timeout", 3600)  # 1 hour
        
        # Security settings
        self.secret_key = self._get_or_generate_secret()
        self.password_pepper = self.config.get("password_pepper", "lukhas_ai_pepper")
        
        self.logger.info("Authentication service initialized")
    
    def _init_storage(self):
        """Initialize user storage"""
        self.storage_path = Path(self.config.get("storage_path", "data/auth"))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.storage_path / "users.json"
        self.sessions_file = self.storage_path / "sessions.json" 
        
        # Load existing data
        self.users = self._load_json_file(self.users_file, {})
        self._cleanup_expired_sessions()
    
    def _init_wallet_integration(self):
        """Initialize wallet integration if available"""
        if WALLET_AVAILABLE:
            try:
                self.wallet_manager = WalletManager()
                self.logger.info("✅ Wallet authentication available")
            except Exception as e:
                self.logger.warning(f"Wallet integration failed: {e}")
                self.wallet_manager = None
        else:
            self.wallet_manager = None
            self.logger.info("ℹ️ Wallet authentication not available")
    
    def _init_identity_integration(self):
        """Initialize identity manager integration if available"""
        if IDENTITY_MANAGER_AVAILABLE:
            try:
                self.identity_manager = IdentityManager()
                self.logger.info("✅ Identity Manager integration available")
            except Exception as e:
                self.logger.warning(f"Identity Manager integration failed: {e}")
                self.identity_manager = None
        else:
            self.identity_manager = None
            self.logger.info("ℹ️ Identity Manager not available")
    
    def authenticate_user(
        self, 
        username: str, 
        password: str,
        auth_method: str = "password"
    ) -> AuthResult:
        """
        Authenticate user with username/password
        
        Args:
            username: Username or email
            password: Password or authentication token
            auth_method: Authentication method to use
            
        Returns:
            Authentication result
        """
        try:
            # Try wallet authentication first if available
            if auth_method == "wallet" and self.wallet_manager:
                return self._authenticate_wallet(username, password)
            
            # Try identity manager authentication
            if auth_method == "identity" and self.identity_manager:
                return self._authenticate_identity(username, password)
            
            # Default to local authentication
            return self._authenticate_local(username, password)
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return AuthResult(
                success=False,
                error=str(e),
                auth_method=auth_method
            )
    
    def authenticate_token(self, token: str) -> AuthResult:
        """
        Authenticate using a session token or JWT
        
        Args:
            token: Authentication token
            
        Returns:
            Authentication result
        """
        try:
            # Try JWT first if available
            if JWT_AVAILABLE and token.count('.') == 2:
                return self._authenticate_jwt(token)
            
            # Try session token
            return self._authenticate_session_token(token)
            
        except Exception as e:
            self.logger.error(f"Token authentication error: {e}")
            return AuthResult(
                success=False,
                error=str(e),
                auth_method="token"
            )
    
    def authenticate_api_key(self, api_key: str, service_name: str = "unknown") -> AuthResult:
        """
        Authenticate using API key
        
        Args:
            api_key: API key
            service_name: Name of the service requesting authentication
            
        Returns:
            Authentication result
        """
        try:
            # Check if API key exists in users
            api_user = None
            for user_id, user_data in self.users.items():
                if user_data.get("api_key") == api_key:
                    api_user = user_data
                    api_user["user_id"] = user_id
                    break
            
            if not api_user:
                return AuthResult(
                    success=False,
                    error="Invalid API key",
                    auth_method="api_key"
                )
            
            # Create session token
            session_token = self._create_session_token(api_user["user_id"])
            
            return AuthResult(
                success=True,
                user_id=api_user["user_id"],
                session_token=session_token,
                permissions=api_user.get("permissions", ["api_access"]),
                expires_at=time.time() + self.session_timeout,
                auth_method="api_key"
            )
            
        except Exception as e:
            self.logger.error(f"API key authentication error: {e}")
            return AuthResult(
                success=False,
                error=str(e),
                auth_method="api_key"
            )
    
    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> UserProfile:
        """
        Create a new user account
        
        Args:
            username: Username
            password: Password
            email: Email address
            permissions: List of permissions
            
        Returns:
            User profile
        """
        # Check if user exists
        user_id = self._generate_user_id(username)
        if user_id in self.users:
            raise ValueError(f"User {username} already exists")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user profile
        profile = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            permissions=permissions or ["basic_access"],
            created_at=time.time()
        )
        
        # Store user data
        self.users[user_id] = {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "permissions": profile.permissions,
            "created_at": profile.created_at,
            "last_login": None,
            "api_key": self._generate_api_key()
        }
        
        self._save_users()
        
        self.logger.info(f"Created user: {username}")
        return profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        user_data = self.users.get(user_id)
        if not user_data:
            return None
        
        return UserProfile(
            user_id=user_id,
            username=user_data["username"],
            email=user_data.get("email"),
            created_at=user_data["created_at"],
            last_login=user_data.get("last_login"),
            permissions=user_data.get("permissions", ["basic_access"]),
            metadata=user_data.get("metadata", {})
        )
    
    def update_user_permissions(self, user_id: str, permissions: List[str]) -> bool:
        """Update user permissions"""
        if user_id not in self.users:
            return False
        
        self.users[user_id]["permissions"] = permissions
        self._save_users()
        
        self.logger.info(f"Updated permissions for user {user_id}: {permissions}")
        return True
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke a session token"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            self._save_sessions()
            return True
        return False
    
    def _authenticate_local(self, username: str, password: str) -> AuthResult:
        """Local username/password authentication"""
        # Find user
        user_data = None
        user_id = None
        
        for uid, data in self.users.items():
            if data["username"] == username or data.get("email") == username:
                user_data = data
                user_id = uid
                break
        
        if not user_data:
            return AuthResult(
                success=False,
                error="User not found",
                auth_method="local"
            )
        
        # Verify password
        if not self._verify_password(password, user_data["password_hash"]):
            return AuthResult(
                success=False,
                error="Invalid password",
                auth_method="local"
            )
        
        # Update last login
        self.users[user_id]["last_login"] = time.time()
        self._save_users()
        
        # Create session
        session_token = self._create_session_token(user_id)
        
        return AuthResult(
            success=True,
            user_id=user_id,
            session_token=session_token,
            permissions=user_data.get("permissions", ["basic_access"]),
            expires_at=time.time() + self.session_timeout,
            auth_method="local"
        )
    
    def _authenticate_wallet(self, username: str, signature: str) -> AuthResult:
        """Wallet-based authentication (if available)"""
        if not self.wallet_manager:
            return AuthResult(
                success=False,
                error="Wallet authentication not available",
                auth_method="wallet"
            )
        
        # This would integrate with the actual wallet system
        # For now, return a placeholder
        return AuthResult(
            success=False,
            error="Wallet authentication not implemented",
            auth_method="wallet"
        )
    
    def _authenticate_identity(self, username: str, token: str) -> AuthResult:
        """Identity manager authentication (if available)"""
        if not self.identity_manager:
            return AuthResult(
                success=False,
                error="Identity manager not available",
                auth_method="identity"
            )
        
        # This would integrate with the identity manager
        # For now, return a placeholder
        return AuthResult(
            success=False,
            error="Identity manager authentication not implemented",
            auth_method="identity"
        )
    
    def _authenticate_jwt(self, token: str) -> AuthResult:
        """JWT token authentication (if available)"""
        if not JWT_AVAILABLE:
            return AuthResult(
                success=False,
                error="JWT not available",
                auth_method="jwt"
            )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if not user_id or user_id not in self.users:
                return AuthResult(
                    success=False,
                    error="Invalid token payload",
                    auth_method="jwt"
                )
            
            return AuthResult(
                success=True,
                user_id=user_id,
                session_token=token,
                permissions=payload.get("permissions", ["basic_access"]),
                expires_at=payload.get("exp"),
                auth_method="jwt"
            )
            
        except jwt.ExpiredSignatureError:
            return AuthResult(
                success=False,
                error="Token expired",
                auth_method="jwt"
            )
        except jwt.InvalidTokenError:
            return AuthResult(
                success=False,
                error="Invalid token",
                auth_method="jwt"
            )
    
    def _authenticate_session_token(self, token: str) -> AuthResult:
        """Session token authentication"""
        session_data = self.active_sessions.get(token)
        
        if not session_data:
            return AuthResult(
                success=False,
                error="Invalid session token",
                auth_method="session"
            )
        
        # Check expiration
        if time.time() > session_data["expires_at"]:
            del self.active_sessions[token]
            self._save_sessions()
            return AuthResult(
                success=False,
                error="Session expired",
                auth_method="session"
            )
        
        return AuthResult(
            success=True,
            user_id=session_data["user_id"],
            session_token=token,
            permissions=session_data.get("permissions", ["basic_access"]),
            expires_at=session_data["expires_at"],
            auth_method="session"
        )
    
    def _create_session_token(self, user_id: str) -> str:
        """Create a new session token"""
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + self.session_timeout
        
        user_data = self.users.get(user_id, {})
        
        self.active_sessions[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": expires_at,
            "permissions": user_data.get("permissions", ["basic_access"])
        }
        
        self._save_sessions()
        return token
    
    def _hash_password(self, password: str) -> str:
        """Hash a password with salt and pepper"""
        salt = secrets.token_hex(32)
        # Combine password with pepper and salt
        combined = f"{password}{self.password_pepper}{salt}"
        password_hash = hashlib.pbkdf2_hmac('sha256', combined.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against stored hash"""
        try:
            salt, hash_hex = stored_hash.split(':', 1)
            combined = f"{password}{self.password_pepper}{salt}"
            password_hash = hashlib.pbkdf2_hmac('sha256', combined.encode(), salt.encode(), 100000)
            return hmac.compare_digest(hash_hex, password_hash.hex())
        except Exception:
            return False
    
    def _generate_user_id(self, username: str) -> str:
        """Generate a user ID from username"""
        return hashlib.sha256(f"lukhas_user_{username}_{time.time()}".encode()).hexdigest()[:16]
    
    def _generate_api_key(self) -> str:
        """Generate an API key"""
        return f"lukhas_api_{secrets.token_urlsafe(32)}"
    
    def _get_or_generate_secret(self) -> str:
        """Get or generate secret key"""
        secret_file = self.storage_path / "secret.key"
        
        if secret_file.exists():
            return secret_file.read_text().strip()
        
        # Generate new secret
        secret = secrets.token_urlsafe(64)
        secret_file.write_text(secret)
        secret_file.chmod(0o600)  # Restrict permissions
        
        return secret
    
    def _load_json_file(self, file_path: Path, default: Any = None) -> Any:
        """Safely load JSON file"""
        if not file_path.exists():
            return default
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return default
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")
    
    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Only save non-expired sessions
            current_time = time.time()
            valid_sessions = {
                token: data for token, data in self.active_sessions.items()
                if data["expires_at"] > current_time
            }
            
            with open(self.sessions_file, 'w') as f:
                json.dump(valid_sessions, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving sessions: {e}")
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.active_sessions.items()
            if data["expires_at"] <= current_time
        ]
        
        for token in expired_tokens:
            del self.active_sessions[token]
        
        if expired_tokens:
            self.logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")


# Global authentication service instance
_auth_service = None


def get_auth_service(config: Optional[Dict[str, Any]] = None) -> AuthenticationService:
    """Get the global authentication service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService(config)
    return _auth_service


# Convenience functions
def authenticate_user(username: str, password: str, **kwargs) -> AuthResult:
    """Authenticate user with global service"""
    return get_auth_service().authenticate_user(username, password, **kwargs)


def authenticate_token(token: str) -> AuthResult:
    """Authenticate token with global service"""
    return get_auth_service().authenticate_token(token)


def authenticate_api_key(api_key: str, service_name: str = "unknown") -> AuthResult:
    """Authenticate API key with global service"""
    return get_auth_service().authenticate_api_key(api_key, service_name)


# Export key components
__all__ = [
    "AuthenticationService",
    "AuthResult",
    "UserProfile",
    "get_auth_service",
    "authenticate_user",
    "authenticate_token",
    "authenticate_api_key"
]