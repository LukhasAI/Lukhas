import logging

logger = logging.getLogger(__name__)
import base64
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from candidate.core.common import get_logger

logger = get_logger(__name__)


class PrivacyManager:
    """
    Manages data privacy, permissions, and regulatory compliance.
    Implements privacy by design principles and supports various
    privacy-preserving mechanisms.
    """

    def __init__(self):
        self.privacy_settings = {}
        self.user_permissions = {}
        self.data_retention_policies = {
            "interaction_history": 30,  # Days to keep interaction history
            "user_data": 365,  # Days to keep user data
            "system_logs": 90,  # Days to keep system logs
        }
        self.privacy_log = []
        self.anonymization_salt = os.urandom(16)  # Salt for anonymization
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def set_privacy_setting(self, key, value):
        """Set a privacy setting"""
        self.privacy_settings[key] = value

        # Log the change
        self.log_privacy_event({"action": "privacy_setting_changed", "setting": key, "new_value": value})

    def get_privacy_setting(self, key):
        """Get a privacy setting"""
        return self.privacy_settings.get(key, None)

    def apply_privacy_mechanisms(self, data):
        """Apply privacy mechanisms such as data anonymization or encryption"""
        if not data:
            return data

        # Determine which privacy mechanisms to apply
        should_anonymize = self.privacy_settings.get("anonymize_data", True)
        should_encrypt = self.privacy_settings.get("encrypt_sensitive_data", True)

        processed_data = data

        # Apply anonymization if enabled
        if should_anonymize:
            processed_data = self.anonymize_data(processed_data)

        # Apply encryption for sensitive fields if enabled
        if should_encrypt:
            processed_data = self.encrypt_sensitive_fields(processed_data)

        return processed_data

    def anonymize_data(self, data):
        """Anonymize personal data"""
        if not data:
            return data

        # Create a copy to modify
        anonymized_data = json.loads(json.dumps(data))

        # Fields to anonymize
        pii_fields = [
            "name",
            "email",
            "address",
            "phone",
            "ip_address",
            "user_id",
            "full_name",
            "birth_date",
            "social_security_number",
            "credit_card",
            "password",
        ]

        # Helper function to recursively process dictionary
        def anonymize_dict(d):
            if not isinstance(d, dict):
                return d

            for key in list(d.keys()):
                if key.lower() in pii_fields:
                    # Anonymize this field
                    d[key] = self._hash_pii_value(d[key])
                elif isinstance(d[key], dict):
                    # Recurse into nested dictionaries
                    d[key] = anonymize_dict(d[key])
                elif isinstance(d[key], list):
                    # Recurse into lists
                    d[key] = [anonymize_dict(item) if isinstance(item, dict) else item for item in d[key]]
            return d

        return anonymize_dict(anonymized_data)

    def encrypt_sensitive_fields(self, data):
        """Encrypt sensitive fields in the data"""
        if not data:
            return data

        # Create a copy to modify
        encrypted_data = json.loads(json.dumps(data))

        # Fields to encrypt
        sensitive_fields = [
            "password",
            "credit_card",
            "social_security_number",
            "health_data",
            "biometric_data",
            "financial_data",
        ]

        # Helper function to recursively process dictionary
        def encrypt_dict(d):
            if not isinstance(d, dict):
                return d

            for key in list(d.keys()):
                if key.lower() in sensitive_fields:
                    # Encrypt this field
                    if d[key] and isinstance(d[key], (str, int, float)):
                        d[key] = self._encrypt_value(str(d[key]))
                elif isinstance(d[key], dict):
                    # Recurse into nested dictionaries
                    d[key] = encrypt_dict(d[key])
                elif isinstance(d[key], list):
                    # Recurse into lists
                    d[key] = [encrypt_dict(item) if isinstance(item, dict) else item for item in d[key]]
            return d

        return encrypt_dict(encrypted_data)

    def decrypt_field(self, encrypted_value):
        """Decrypt an encrypted field value"""
        if not encrypted_value or not encrypted_value.startswith("ENCRYPTED:"):
            return encrypted_value

        # Remove prefix
        encrypted_bytes = encrypted_value[10:]

        try:
            # Convert from base64 to bytes and decrypt
            encrypted_bytes = base64.b64decode(encrypted_bytes)
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            return "[Decryption Error]"

    def check_permissions(self, user_id, action, resource=None):
        """
        Check if a user has permission for an action on a resource

        Args:
            user_id: ID of the user
            action: Action being performed
            resource: Resource being accessed (optional)

        Returns:
            Dict with allowed status and reason
        """
        # Default deny if user has no permissions
        if user_id not in self.user_permissions:
            return {"allowed": False, "reason": "User has no permissions"}

        # Get user's permissions
        permissions = self.user_permissions[user_id]

        # Check for explicit permission for this action
        if action in permissions.get("allowed_actions", []):
            return {"allowed": True}

        # Check for explicit denial for this action
        if action in permissions.get("denied_actions", []):
            return {"allowed": False, "reason": f"Action '{action}' explicitly denied"}

        # Check resource-specific permissions if resource provided
        if resource and "resources" in permissions and resource in permissions["resources"]:
            # Check if action is allowed for this resource
            resource_permissions = permissions["resources"][resource]
            if action in resource_permissions.get("allowed_actions", []):
                return {"allowed": True}
            if action in resource_permissions.get("denied_actions", []):
                return {
                    "allowed": False,
                    "reason": f"Action '{action}' denied for resource '{resource}'",
                }

        # Handle default permission policy
        default_policy = self.privacy_settings.get("default_permission_policy", "deny")

        if default_policy == "allow":
            return {"allowed": True}
        else:
            return {"allowed": False, "reason": "Default denial of permission"}

    def set_user_permissions(self, user_id, permissions):
        """Set permissions for a user"""
        self.user_permissions[user_id] = permissions

        # Log the change
        self.log_privacy_event({"action": "user_permissions_updated", "user_id": user_id})

    def apply_retention_policy(self, data_type, data):
        """Apply data retention policy to the given data"""
        if not data:
            return data

        # Get retention period in days
        retention_days = self.data_retention_policies.get(data_type, 30)

        # Calculate cutoff date
        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=retention_days)
        cutoff_timestamp = cutoff_date.timestamp()

        # Filter data based on timestamp
        if isinstance(data, list):
            # Handle lists of items
            def should_retain(item):
                # Check if item has timestamp
                if isinstance(item, dict) and "timestamp" in item:
                    try:
                        # Parse timestamp from iso_format or check if it's a float
                        if isinstance(item["timestamp"], str):
                            item_time = datetime.fromisoformat(item["timestamp"]).timestamp()
                        else:
                            item_time = float(item["timestamp"])

                        return item_time >= cutoff_timestamp
                    except (ValueError, TypeError):
                        # If timestamp can't be parsed, retain by default
                        return True
                return True

            return [item for item in data if should_retain(item)]

        if isinstance(data, dict):
            # Handle dictionary with timestamps as keys or with timestamp field
            if "timestamp" in data:
                try:
                    if isinstance(data["timestamp"], str):
                        item_time = datetime.fromisoformat(data["timestamp"]).timestamp()
                    else:
                        item_time = float(data["timestamp"])

                    if item_time < cutoff_timestamp:
                        return None  # Don't retain
                except (ValueError, TypeError):
                    pass  # Keep data if timestamp can't be parsed

            return data

        return data

    def create_gdpr_report(self, user_id):
        """Create a GDPR compliance report for a user's data"""
        # This would extract all data related to a user
        # Simplified implementation
        report = {
            "user_id": user_id,
            "report_generated": datetime.now(tz=timezone.utc).isoformat(),
            "data_categories": [
                {
                    "category": "user_profile",
                    "retention_period": f"{self.data_retention_policies.get('user_data', 365)} days",
                    "processing_purpose": "Personalization and user identification",
                },
                {
                    "category": "interaction_history",
                    "retention_period": f"{self.data_retention_policies.get('interaction_history', 30)} days",
                    "processing_purpose": "Service improvement and user experience optimization",
                },
            ],
            "data_sharing": [],  # Would list third parties data is shared with
            "data_subject_rights": {
                "access": True,
                "rectification": True,
                "erasure": True,
                "restrict_processing": True,
                "data_portability": True,
                "object": True,
            },
        }

        return report

    def log_privacy_event(self, event):
        """Log a privacy-related event"""
        if not event:
            return

        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(tz=timezone.utc).isoformat()

        # Add event to log
        self.privacy_log.append(event)

        # Trim log if too long
        if len(self.privacy_log) > 1000:
            self.privacy_log = self.privacy_log[-1000:]

        # Log the event
        logger.info(f"Privacy event: {event.get('action', 'unknown')}")

    def get_privacy_logs(self, limit=100):
        """Get privacy logs, with optional limit"""
        if not self.privacy_log:
            return []

        # Return most recent logs
        return self.privacy_log[-limit:]

    def _hash_pii_value(self, value):
        """Hash a PII value for anonymization"""
        if value is None:
            return None

        # Convert to string
        value_str = str(value)

        # Create salted hash
        hasher = hashlib.sha256()
        hasher.update(self.anonymization_salt)
        hasher.update(value_str.encode())

        # Return prefix and hash
        return f"ANON:{hasher.hexdigest()[:16]}"

    def _encrypt_value(self, value):
        """Encrypt a sensitive value"""
        if value is None:
            return None

        # Convert to string and bytes
        value_bytes = str(value).encode("utf-8")

        # Encrypt
        encrypted_bytes = self.cipher_suite.encrypt(value_bytes)

        # Convert to base64 string and add prefix
        encrypted_string = base64.b64encode(encrypted_bytes).decode("utf-8")
        return f"ENCRYPTED:{encrypted_string}"

    def _generate_encryption_key(self):
        """Generate a key for encryption"""
        # In a production system, this would be stored securely
        # and possibly derived from a master key

        # Create a key derivation function
        password = b"adaptive-agi-secure-key"  # This would be a secure secret in production
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.anonymization_salt,
            iterations=100000,
        )

        # Derive key
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key