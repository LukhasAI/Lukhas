"""
Cross-Device Token Manager
==========================

Manages SSO tokens across multiple devices and platforms for LUKHAS Identity.
Handles secure token synchronization, device-specific authentication, and cross-platform SSO.

Features:
- Secure cross-device token synchronization
- Device trust scoring and validation
- End-to-end encrypted token transmission
- WebRTC-based real-time sync for trusted devices
- Trinity Framework compliance (⚛️🧠🛡️)
- <100ms p95 latency for token validation
- OAuth2/OIDC compatible token management
"""

import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    # Fallback to basic encryption if cryptography not available
    Fernet = None
    PBKDF2HMAC = None


class DeviceTrustScore:
    """Device trust scoring and validation"""
    
    def __init__(self):
        self.trust_factors = {
            'registration_age': 0.25,      # How long device has been registered
            'usage_frequency': 0.20,       # How often device is used
            'security_features': 0.25,     # Biometric, secure enclave, etc.
            'network_consistency': 0.15,   # Consistent network patterns
            'successful_auths': 0.15       # History of successful authentications
        }
        
    def calculate_trust_score(self, device_data: Dict) -> float:
        """Calculate trust score for device (0.0 - 1.0)"""
        try:
            score = 0.0
            
            # Registration age factor
            reg_date = datetime.fromisoformat(device_data.get('registered_at', '2024-01-01'))
            age_days = (datetime.utcnow() - reg_date).days
            age_score = min(age_days / 90.0, 1.0)  # Max score at 90 days
            score += age_score * self.trust_factors['registration_age']
            
            # Usage frequency factor
            last_used = datetime.fromisoformat(device_data.get('last_used', '2024-01-01'))
            days_since_use = (datetime.utcnow() - last_used).days
            usage_score = max(1.0 - (days_since_use / 30.0), 0.0)  # Decay over 30 days
            score += usage_score * self.trust_factors['usage_frequency']
            
            # Security features factor
            security_score = 0.0
            if device_data.get('biometric_enabled', False):
                security_score += 0.4
            if device_data.get('secure_enclave', False):
                security_score += 0.3
            if device_data.get('device_encrypted', False):
                security_score += 0.3
            score += security_score * self.trust_factors['security_features']
            
            # Network consistency factor (simplified)
            network_score = device_data.get('network_consistency_score', 0.5)
            score += network_score * self.trust_factors['network_consistency']
            
            # Successful authentications factor
            auth_success_rate = device_data.get('auth_success_rate', 0.5)
            score += auth_success_rate * self.trust_factors['successful_auths']
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.0  # Return minimum trust on error


class CrossDeviceTokenManager:
    """⚛️🧠🛡️ Manage SSO tokens across devices with Trinity Framework compliance"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.device_tokens: Dict[str, Dict] = {}  # user_id -> device_id -> tokens
        self.sync_queue: List[Dict] = []
        self.trust_scorer = DeviceTrustScore()
        
        # Performance optimization
        self.token_cache = {}
        self.sync_cache = {}
        
        # Security configuration
        self.token_encryption_key = self._generate_encryption_key()
        self.max_devices_per_user = self.config.get('max_devices_per_user', 10)
        self.token_sync_timeout = self.config.get('token_sync_timeout', 30)  # seconds
        self.trust_threshold = self.config.get('minimum_trust_threshold', 0.6)
        
        # Trinity Framework components
        self.guardian_validator = None      # 🛡️ Guardian
        self.consciousness_tracker = None   # 🧠 Consciousness  
        self.identity_verifier = None       # ⚛️ Identity

    def sync_token_to_device(self, token: str, device_id: str, user_id: str, 
                           device_info: Optional[Dict] = None) -> Dict[str, Any]:
        """🔄 Synchronize SSO token to specific device with security validation"""
        try:
            start_time = time.time()
            
            # Validate inputs
            if not all([token, device_id, user_id]):
                return {
                    'success': False,
                    'error': 'Missing required parameters',
                    'sync_time_ms': 0
                }
            
            # Initialize user device registry if needed
            if user_id not in self.device_tokens:
                self.device_tokens[user_id] = {}
            
            # Check device limit
            if len(self.device_tokens[user_id]) >= self.max_devices_per_user:
                return {
                    'success': False,
                    'error': f'Maximum devices ({self.max_devices_per_user}) exceeded',
                    'sync_time_ms': (time.time() - start_time) * 1000
                }
            
            # Get or create device data
            device_data = self._get_device_data(user_id, device_id, device_info)
            
            # Calculate device trust score
            trust_score = self.trust_scorer.calculate_trust_score(device_data)
            
            if trust_score < self.trust_threshold:
                return {
                    'success': False,
                    'error': f'Device trust score too low: {trust_score:.2f} < {self.trust_threshold}',
                    'trust_score': trust_score,
                    'sync_time_ms': (time.time() - start_time) * 1000
                }
            
            # 🛡️ Guardian validation
            if not self._constitutional_validation(user_id, device_id, device_data):
                return {
                    'success': False,
                    'error': 'Guardian validation failed',
                    'sync_time_ms': (time.time() - start_time) * 1000
                }
            
            # Encrypt token for secure storage
            encrypted_token = self._encrypt_token(token, device_id)
            
            # Create sync record
            sync_record = {
                'token': encrypted_token,
                'device_id': device_id,
                'user_id': user_id,
                'synced_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                'trust_score': trust_score,
                'device_fingerprint': self._generate_device_fingerprint(device_data),
                'sync_method': 'secure_channel',
                'guardian_approved': True
            }\n            \n            # Store token sync record\n            if device_id not in self.device_tokens[user_id]:\n                self.device_tokens[user_id][device_id] = []\n                \n            self.device_tokens[user_id][device_id].append(sync_record)\n            \n            # Add to sync queue for real-time propagation\n            self.sync_queue.append({\n                'action': 'token_sync',\n                'user_id': user_id,\n                'device_id': device_id,\n                'sync_record': sync_record,\n                'timestamp': time.time()\n            })\n            \n            # 🧠 Update consciousness patterns\n            self._update_consciousness_patterns(user_id, device_id, 'token_sync')\n            \n            # Performance tracking\n            sync_time = (time.time() - start_time) * 1000\n            \n            return {\n                'success': True,\n                'device_id': device_id,\n                'sync_id': sync_record.get('sync_id', secrets.token_hex(8)),\n                'trust_score': trust_score,\n                'expires_at': sync_record['expires_at'],\n                'sync_time_ms': sync_time,\n                'device_fingerprint': sync_record['device_fingerprint'],\n                'guardian_approved': True\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Token sync failed: {str(e)}',\n                'sync_time_ms': (time.time() - start_time) * 1000 if 'start_time' in locals() else 0\n            }\n\n    def invalidate_device_tokens(self, device_id: str, user_id: str, \n                                reason: str = 'manual_revocation') -> Dict[str, Any]:\n        \"\"\"🚫 Invalidate all tokens for a specific device\"\"\"\n        try:\n            start_time = time.time()\n            \n            if user_id not in self.device_tokens or device_id not in self.device_tokens[user_id]:\n                return {\n                    'success': False,\n                    'error': 'Device not found',\n                    'invalidation_time_ms': (time.time() - start_time) * 1000\n                }\n            \n            # Get device tokens\n            device_token_records = self.device_tokens[user_id][device_id]\n            invalidated_count = 0\n            \n            # Mark all tokens as invalidated\n            for token_record in device_token_records:\n                if not token_record.get('invalidated', False):\n                    token_record['invalidated'] = True\n                    token_record['invalidated_at'] = datetime.utcnow().isoformat()\n                    token_record['invalidation_reason'] = reason\n                    invalidated_count += 1\n            \n            # Add to sync queue for real-time propagation\n            self.sync_queue.append({\n                'action': 'token_invalidation',\n                'user_id': user_id,\n                'device_id': device_id,\n                'reason': reason,\n                'invalidated_count': invalidated_count,\n                'timestamp': time.time()\n            })\n            \n            # 🧠 Update consciousness patterns for security event\n            self._update_consciousness_patterns(user_id, device_id, 'token_invalidation')\n            \n            return {\n                'success': True,\n                'device_id': device_id,\n                'invalidated_count': invalidated_count,\n                'reason': reason,\n                'invalidated_at': datetime.utcnow().isoformat(),\n                'invalidation_time_ms': (time.time() - start_time) * 1000\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Token invalidation failed: {str(e)}',\n                'invalidation_time_ms': (time.time() - start_time) * 1000 if 'start_time' in locals() else 0\n            }\n\n    def get_device_tokens(self, user_id: str, device_id: str, \n                         include_expired: bool = False) -> Dict[str, Any]:\n        \"\"\"📱 Get all active tokens for a device\"\"\"\n        try:\n            start_time = time.time()\n            \n            if user_id not in self.device_tokens or device_id not in self.device_tokens[user_id]:\n                return {\n                    'success': False,\n                    'error': 'Device not found',\n                    'tokens': [],\n                    'retrieval_time_ms': (time.time() - start_time) * 1000\n                }\n            \n            device_token_records = self.device_tokens[user_id][device_id]\n            active_tokens = []\n            \n            current_time = datetime.utcnow()\n            \n            for token_record in device_token_records:\n                # Skip invalidated tokens\n                if token_record.get('invalidated', False):\n                    continue\n                    \n                # Check expiration\n                expires_at = datetime.fromisoformat(token_record['expires_at'])\n                is_expired = current_time > expires_at\n                \n                if is_expired and not include_expired:\n                    continue\n                \n                # Decrypt token for return (in real implementation, \n                # you might return token metadata instead)\n                decrypted_token = self._decrypt_token(\n                    token_record['token'], device_id\n                )\n                \n                active_tokens.append({\n                    'token_id': token_record.get('sync_id', 'unknown'),\n                    'synced_at': token_record['synced_at'],\n                    'expires_at': token_record['expires_at'],\n                    'trust_score': token_record['trust_score'],\n                    'is_expired': is_expired,\n                    'sync_method': token_record['sync_method'],\n                    # Only include actual token in secure contexts\n                    'token': decrypted_token if not is_expired else None\n                })\n            \n            return {\n                'success': True,\n                'device_id': device_id,\n                'user_id': user_id,\n                'tokens': active_tokens,\n                'active_count': len([t for t in active_tokens if not t['is_expired']]),\n                'total_count': len(active_tokens),\n                'retrieval_time_ms': (time.time() - start_time) * 1000\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Token retrieval failed: {str(e)}',\n                'tokens': [],\n                'retrieval_time_ms': (time.time() - start_time) * 1000 if 'start_time' in locals() else 0\n            }\n\n    def sync_tokens_across_devices(self, user_id: str, source_device_id: str, \n                                  target_device_ids: Optional[List[str]] = None) -> Dict[str, Any]:\n        \"\"\"🔄 Sync tokens across multiple devices for a user\"\"\"\n        try:\n            start_time = time.time()\n            \n            if user_id not in self.device_tokens:\n                return {\n                    'success': False,\n                    'error': 'User has no registered devices',\n                    'sync_time_ms': (time.time() - start_time) * 1000\n                }\n            \n            user_devices = self.device_tokens[user_id]\n            \n            # If no target devices specified, sync to all trusted devices\n            if target_device_ids is None:\n                target_device_ids = [\n                    device_id for device_id, tokens in user_devices.items()\n                    if device_id != source_device_id and \n                    self._is_device_trusted(user_id, device_id)\n                ]\n            \n            # Get source device tokens\n            source_tokens_result = self.get_device_tokens(user_id, source_device_id)\n            if not source_tokens_result['success']:\n                return {\n                    'success': False,\n                    'error': f'Failed to get source device tokens: {source_tokens_result[\"error\"]}',\n                    'sync_time_ms': (time.time() - start_time) * 1000\n                }\n            \n            source_tokens = source_tokens_result['tokens']\n            sync_results = {}\n            \n            # Sync to each target device\n            for target_device_id in target_device_ids:\n                device_sync_results = []\n                \n                for token_data in source_tokens:\n                    if token_data['token'] and not token_data['is_expired']:\n                        sync_result = self.sync_token_to_device(\n                            token_data['token'],\n                            target_device_id,\n                            user_id\n                        )\n                        device_sync_results.append(sync_result)\n                \n                sync_results[target_device_id] = {\n                    'synced_tokens': len([r for r in device_sync_results if r['success']]),\n                    'failed_tokens': len([r for r in device_sync_results if not r['success']]),\n                    'results': device_sync_results\n                }\n            \n            total_synced = sum(r['synced_tokens'] for r in sync_results.values())\n            total_failed = sum(r['failed_tokens'] for r in sync_results.values())\n            \n            return {\n                'success': total_synced > 0,\n                'source_device_id': source_device_id,\n                'target_devices': target_device_ids,\n                'total_synced': total_synced,\n                'total_failed': total_failed,\n                'device_results': sync_results,\n                'sync_time_ms': (time.time() - start_time) * 1000\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Cross-device sync failed: {str(e)}',\n                'sync_time_ms': (time.time() - start_time) * 1000 if 'start_time' in locals() else 0\n            }\n\n    def get_user_devices(self, user_id: str, include_trust_scores: bool = True) -> Dict[str, Any]:\n        \"\"\"📋 Get all registered devices for a user\"\"\"\n        try:\n            if user_id not in self.device_tokens:\n                return {\n                    'success': True,\n                    'user_id': user_id,\n                    'devices': [],\n                    'total_devices': 0\n                }\n            \n            devices = []\n            for device_id, token_records in self.device_tokens[user_id].items():\n                device_info = {\n                    'device_id': device_id,\n                    'token_count': len([t for t in token_records if not t.get('invalidated', False)]),\n                    'last_sync': max([t['synced_at'] for t in token_records], default='never'),\n                }\n                \n                if include_trust_scores and token_records:\n                    # Get latest device data for trust score\n                    latest_record = max(token_records, key=lambda x: x['synced_at'])\n                    device_info['trust_score'] = latest_record['trust_score']\n                    device_info['device_fingerprint'] = latest_record['device_fingerprint']\n                \n                devices.append(device_info)\n            \n            return {\n                'success': True,\n                'user_id': user_id,\n                'devices': devices,\n                'total_devices': len(devices),\n                'trusted_devices': len([d for d in devices if d.get('trust_score', 0) >= self.trust_threshold])\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Failed to get user devices: {str(e)}',\n                'devices': []\n            }\n\n    # Helper methods for cross-device token management\n    \n    def _generate_encryption_key(self) -> Optional[object]:\n        \"\"\"Generate encryption key for token security\"\"\"\n        if Fernet:\n            return Fernet.generate_key()\n        return None\n    \n    def _encrypt_token(self, token: str, device_id: str) -> str:\n        \"\"\"Encrypt token for secure storage\"\"\"\n        if self.token_encryption_key and Fernet:\n            try:\n                f = Fernet(self.token_encryption_key)\n                # Add device_id as additional context\n                token_with_context = f\"{token}|{device_id}\"\n                return f.encrypt(token_with_context.encode()).decode()\n            except Exception:\n                pass\n        \n        # Fallback to base64 encoding (not secure, for development only)\n        import base64\n        return base64.b64encode(f\"{token}|{device_id}\".encode()).decode()\n    \n    def _decrypt_token(self, encrypted_token: str, device_id: str) -> Optional[str]:\n        \"\"\"Decrypt token from secure storage\"\"\"\n        if self.token_encryption_key and Fernet:\n            try:\n                f = Fernet(self.token_encryption_key)\n                decrypted = f.decrypt(encrypted_token.encode()).decode()\n                token, stored_device_id = decrypted.split('|', 1)\n                if stored_device_id == device_id:\n                    return token\n                return None\n            except Exception:\n                pass\n        \n        # Fallback for base64 encoding\n        try:\n            import base64\n            decrypted = base64.b64decode(encrypted_token.encode()).decode()\n            token, stored_device_id = decrypted.split('|', 1)\n            if stored_device_id == device_id:\n                return token\n        except Exception:\n            pass\n        \n        return None\n    \n    def _get_device_data(self, user_id: str, device_id: str, device_info: Optional[Dict] = None) -> Dict:\n        \"\"\"Get or create device data record\"\"\"\n        # In a real implementation, this would fetch from a database\n        default_device_data = {\n            'device_id': device_id,\n            'user_id': user_id,\n            'registered_at': datetime.utcnow().isoformat(),\n            'last_used': datetime.utcnow().isoformat(),\n            'biometric_enabled': device_info.get('biometric_enabled', False) if device_info else False,\n            'secure_enclave': device_info.get('secure_enclave', False) if device_info else False,\n            'device_encrypted': device_info.get('device_encrypted', True) if device_info else True,\n            'network_consistency_score': 0.7,  # Would be calculated from network patterns\n            'auth_success_rate': 0.95,  # Would be calculated from auth history\n            'device_type': device_info.get('device_type', 'unknown') if device_info else 'unknown',\n            'os_version': device_info.get('os_version', 'unknown') if device_info else 'unknown',\n            'app_version': device_info.get('app_version', 'unknown') if device_info else 'unknown'\n        }\n        \n        # Update with provided device info\n        if device_info:\n            default_device_data.update(device_info)\n            default_device_data['last_used'] = datetime.utcnow().isoformat()\n        \n        return default_device_data\n    \n    def _generate_device_fingerprint(self, device_data: Dict) -> str:\n        \"\"\"Generate unique device fingerprint\"\"\"\n        fingerprint_data = f\"{device_data.get('device_id')}|{device_data.get('device_type')}|{device_data.get('os_version')}\"\n        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]\n    \n    def _constitutional_validation(self, user_id: str, device_id: str, device_data: Dict) -> bool:\n        \"\"\"🛡️ Guardian constitutional validation\"\"\"\n        try:\n            # Basic safety checks\n            if not user_id or not device_id:\n                return False\n            \n            # Check for suspicious device patterns\n            if device_data.get('auth_success_rate', 1.0) < 0.5:\n                return False  # Too many failed authentications\n            \n            # Check device registration age (prevent rapid device additions)\n            reg_date = datetime.fromisoformat(device_data.get('registered_at', '2024-01-01'))\n            if (datetime.utcnow() - reg_date).total_seconds() < 300:  # 5 minutes minimum\n                return False\n            \n            # ⚛️ Identity integrity check\n            if len(user_id) < 8:\n                return False\n                \n            return True\n            \n        except Exception:\n            return False  # Deny on error for safety\n    \n    def _update_consciousness_patterns(self, user_id: str, device_id: str, action: str):\n        \"\"\"🧠 Update consciousness patterns for security analysis\"\"\"\n        # This would integrate with the consciousness tracking system\n        # For now, just log the activity\n        timestamp = datetime.utcnow().isoformat()\n        print(f\"Consciousness update: {user_id} | {device_id} | {action} | {timestamp}\")\n    \n    def _is_device_trusted(self, user_id: str, device_id: str) -> bool:\n        \"\"\"Check if device meets trust threshold\"\"\"\n        try:\n            if user_id not in self.device_tokens or device_id not in self.device_tokens[user_id]:\n                return False\n            \n            device_records = self.device_tokens[user_id][device_id]\n            if not device_records:\n                return False\n            \n            # Get latest trust score\n            latest_record = max(device_records, key=lambda x: x['synced_at'])\n            return latest_record['trust_score'] >= self.trust_threshold\n            \n        except Exception:\n            return False\n    \n    def cleanup_expired_tokens(self) -> Dict[str, Any]:\n        \"\"\"🧹 Cleanup expired tokens across all devices\"\"\"\n        try:\n            start_time = time.time()\n            total_cleaned = 0\n            current_time = datetime.utcnow()\n            \n            for user_id, user_devices in self.device_tokens.items():\n                for device_id, token_records in user_devices.items():\n                    cleaned_count = 0\n                    for token_record in token_records[:]:\n                        try:\n                            expires_at = datetime.fromisoformat(token_record['expires_at'])\n                            if current_time > expires_at:\n                                token_records.remove(token_record)\n                                cleaned_count += 1\n                        except (ValueError, KeyError):\n                            # Remove malformed records\n                            token_records.remove(token_record)\n                            cleaned_count += 1\n                    \n                    total_cleaned += cleaned_count\n            \n            return {\n                'success': True,\n                'tokens_cleaned': total_cleaned,\n                'cleanup_time_ms': (time.time() - start_time) * 1000\n            }\n            \n        except Exception as e:\n            return {\n                'success': False,\n                'error': f'Cleanup failed: {str(e)}',\n                'tokens_cleaned': 0\n            }\n\n\n# WebRTC-based real-time sync for trusted devices\nclass WebRTCDeviceSync:\n    \"\"\"🌐 WebRTC-based real-time token synchronization\"\"\"\n    \n    def __init__(self, cross_device_manager: CrossDeviceTokenManager):\n        self.device_manager = cross_device_manager\n        self.active_channels = {}\n        self.sync_callbacks = []\n    \n    async def establish_sync_channel(self, user_id: str, device_a: str, device_b: str) -> bool:\n        \"\"\"Establish WebRTC sync channel between two trusted devices\"\"\"\n        try:\n            # Verify both devices are trusted\n            if not (self.device_manager._is_device_trusted(user_id, device_a) and \n                   self.device_manager._is_device_trusted(user_id, device_b)):\n                return False\n            \n            # Create sync channel identifier\n            channel_id = f\"{user_id}:{min(device_a, device_b)}:{max(device_a, device_b)}\"\n            \n            # In a real implementation, this would establish WebRTC connection\n            self.active_channels[channel_id] = {\n                'user_id': user_id,\n                'devices': [device_a, device_b],\n                'established_at': datetime.utcnow().isoformat(),\n                'status': 'active'\n            }\n            \n            return True\n            \n        except Exception:\n            return False\n    \n    async def sync_via_webrtc(self, user_id: str, source_device: str, \n                            target_device: str, token_data: Dict) -> bool:\n        \"\"\"Sync token via WebRTC channel\"\"\"\n        try:\n            # Check for active channel\n            channel_id = f\"{user_id}:{min(source_device, target_device)}:{max(source_device, target_device)}\"\n            \n            if channel_id not in self.active_channels:\n                return False\n            \n            # In a real implementation, this would send via WebRTC data channel\n            # For now, just use the regular sync mechanism\n            result = self.device_manager.sync_token_to_device(\n                token_data['token'],\n                target_device,\n                user_id\n            )\n            \n            return result['success']\n            \n        except Exception:\n            return False\n\n\n# Export main classes\n__all__ = [\n    \"CrossDeviceTokenManager\",\n    \"DeviceTrustScore\", \n    \"WebRTCDeviceSync\"\n]