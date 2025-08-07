"""
LUKHΛS Identity Database
========================

User storage and management for the ΛiD system.
Implements file-based storage with symbolic metadata tracking.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import json
import os
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    """
    File-based user database with symbolic tracking.
    Stores users with tier assignments, tokens, and glyph trails.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.consent_log = self.data_dir / "consent_log.jsonl"
        self._ensure_files_exist()
        self._load_users()
    
    def _ensure_files_exist(self):
        """Ensure database files exist with proper structure."""
        if not self.users_file.exists():
            # Initialize with demo user for OpenAI
            initial_data = {
                "openai_demo": {
                    "email": "reviewer@openai.com",
                    "tier": "T5",
                    "token": "LUKHAS-T5-GATE",
                    "glyphs": ["🛡️", "⚛️", "🧠"],
                    "consent": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "lambda_id": "LAMBDA-OPENAI-DEMO",
                    "password_hash": self._hash_password("demo_password"),
                    "sessions": [],
                    "metadata": {
                        "trinity_score": 1.0,
                        "drift_score": 0.0,
                        "cultural_profile": "universal",
                        "personality_type": "analytical"
                    }
                }
            }
            self._save_users(initial_data)
        
        if not self.consent_log.exists():
            self.consent_log.touch()
    
    def _load_users(self):
        """Load users from JSON file."""
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self.users = {}
    
    def _save_users(self, users: Optional[Dict] = None):
        """Save users to JSON file."""
        if users is None:
            users = self.users
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256 (simplified for demo)."""
        # In production, use bcrypt or argon2
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self, tier: str) -> str:
        """Generate a secure token for user session."""
        random_part = secrets.token_urlsafe(32)
        return f"LUKHAS-{tier}-{random_part}"
    
    def _generate_lambda_id(self, email: str) -> str:
        """Generate a unique Lambda ID for the user."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
        return f"LAMBDA-{email_hash.upper()}-{timestamp}"
    
    def _log_consent(self, email: str, action: str, glyphs: List[str]):
        """Log consent action with symbolic tracking."""
        consent_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "email": email,
            "action": action,
            "glyphs": glyphs,
            "trinity_framework": ["⚛️", "🧠", "🛡️"],
            "consent_given": True
        }
        
        try:
            with open(self.consent_log, 'a') as f:
                f.write(json.dumps(consent_record) + '\n')
        except Exception as e:
            logger.error(f"Error logging consent: {e}")
    
    def create_user(self, email: str, password: str, tier: str = "T1", 
                   cultural_profile: str = "universal", 
                   personality_type: str = "balanced") -> Dict[str, Any]:
        """
        Create a new user with symbolic initialization.
        
        Args:
            email: User's email address
            password: User's password (will be hashed)
            tier: Authentication tier (T1-T5)
            cultural_profile: User's cultural background
            personality_type: User's personality profile
        
        Returns:
            User data dictionary
        """
        if email in self.users:
            raise ValueError(f"User {email} already exists")
        
        # Generate user data
        user_id = email.split('@')[0].replace('.', '_').lower()
        lambda_id = self._generate_lambda_id(email)
        token = self._generate_token(tier)
        
        # Assign glyphs based on tier
        tier_glyphs = {
            "T1": ["⚛️"],  # Basic identity
            "T2": ["⚛️", "🔐"],  # With security
            "T3": ["⚛️", "🔐", "🧠"],  # With consciousness
            "T4": ["⚛️", "🔐", "🧠", "🌍"],  # With cultural
            "T5": ["🛡️", "⚛️", "🧠"]  # Full Trinity
        }
        
        user_data = {
            "email": email,
            "tier": tier,
            "token": token,
            "glyphs": tier_glyphs.get(tier, ["⚛️"]),
            "consent": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "lambda_id": lambda_id,
            "password_hash": self._hash_password(password),
            "sessions": [token],  # Track active sessions
            "metadata": {
                "trinity_score": 0.3 if tier < "T3" else 0.7 if tier < "T5" else 1.0,
                "drift_score": 0.0,
                "cultural_profile": cultural_profile,
                "personality_type": personality_type,
                "last_login": None,
                "login_count": 0
            }
        }
        
        # Store user
        self.users[user_id] = user_data
        self._save_users()
        
        # Log consent
        self._log_consent(email, "registration", user_data["glyphs"])
        
        return user_data
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and return user data with new session token.
        
        Args:
            email: User's email
            password: User's password
        
        Returns:
            User data with new session token or None if auth fails
        """
        user_id = email.split('@')[0].replace('.', '_').lower()
        
        if user_id not in self.users:
            # Check by email
            for uid, user in self.users.items():
                if user.get("email") == email:
                    user_id = uid
                    break
            else:
                return None
        
        user = self.users[user_id]
        
        # Verify password
        if user["password_hash"] != self._hash_password(password):
            return None
        
        # Generate new session token
        new_token = self._generate_token(user["tier"])
        user["sessions"].append(new_token)
        
        # Update metadata
        user["metadata"]["last_login"] = datetime.now(timezone.utc).isoformat()
        user["metadata"]["login_count"] = user["metadata"].get("login_count", 0) + 1
        
        # Update token
        user["token"] = new_token
        
        # Save changes
        self._save_users()
        
        # Log consent
        self._log_consent(email, "login", user["glyphs"])
        
        return user
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify token and return associated user data.
        
        Args:
            token: Session token to verify
        
        Returns:
            User data if token is valid, None otherwise
        """
        for user_id, user in self.users.items():
            if token in user.get("sessions", []) or token == user.get("token"):
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email address."""
        user_id = email.split('@')[0].replace('.', '_').lower()
        
        if user_id in self.users:
            return self.users[user_id]
        
        # Search by email field
        for uid, user in self.users.items():
            if user.get("email") == email:
                return user
        
        return None
    
    def update_user_tier(self, email: str, new_tier: str) -> bool:
        """
        Update user's tier and associated glyphs.
        
        Args:
            email: User's email
            new_tier: New tier assignment (T1-T5)
        
        Returns:
            True if successful, False otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            return False
        
        # Update tier and glyphs
        tier_glyphs = {
            "T1": ["⚛️"],
            "T2": ["⚛️", "🔐"],
            "T3": ["⚛️", "🔐", "🧠"],
            "T4": ["⚛️", "🔐", "🧠", "🌍"],
            "T5": ["🛡️", "⚛️", "🧠"]
        }
        
        user["tier"] = new_tier
        user["glyphs"] = tier_glyphs.get(new_tier, ["⚛️"])
        user["metadata"]["trinity_score"] = 0.3 if new_tier < "T3" else 0.7 if new_tier < "T5" else 1.0
        
        # Find user ID and save
        for uid, u in self.users.items():
            if u.get("email") == email:
                self.users[uid] = user
                break
        
        self._save_users()
        
        # Log tier change
        self._log_consent(email, f"tier_change_to_{new_tier}", user["glyphs"])
        
        return True
    
    def invalidate_token(self, token: str) -> bool:
        """Remove token from active sessions."""
        for user_id, user in self.users.items():
            if token in user.get("sessions", []):
                user["sessions"].remove(token)
                self._save_users()
                return True
        return False
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users (admin function)."""
        return self.users.copy()


# Initialize global database instance
user_db = UserDatabase()