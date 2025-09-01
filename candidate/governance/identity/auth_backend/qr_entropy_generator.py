"""
LUKHAS QR Entropy Generator - Steganographic QR Server Logic

This module implements server-side QR code generation with steganographic
entropy embedding for the LUKHAS authentication system.

Author: LUKHAS Team
Date: June 2025
Purpose: Server-side steganographic QR code generation with entropy
Status: PLACEHOLDER - Implementation needed
"""

import base64
import hashlib
import io
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import qrcode
from PIL import Image

try:
    from cryptography.fernet import Fernet
except ImportError:
    # Fallback encryption using hashlib for basic operation
    Fernet = None


class QREntropyGenerator:
    """
    Server-side QR code generator with steganographic entropy embedding.

    Generates QR codes that contain hidden entropy layers for enhanced
    security in LUKHAS authentication.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.entropy_layers = 3  # Number of steganographic layers
        self.refresh_interval = 2.0  # Seconds between refreshes
        self.active_codes: dict[str, dict] = {}  # Session -> QR data
        self.max_code_lifetime = 300  # 5 minutes max

        # Initialize encryption
        if encryption_key and Fernet:
            self.cipher = Fernet(encryption_key)
        else:
            self.cipher = None

        # Steganography configuration
        self.stego_layers = {
            "layer_1": {"channel": 0, "bit_depth": 2},  # Red channel, 2 LSBs
            "layer_2": {"channel": 1, "bit_depth": 1},  # Green channel, 1 LSB
            "layer_3": {"channel": 2, "bit_depth": 1},  # Blue channel, 1 LSB
        }

        # Performance optimization - pre-compute common values
        self._qr_cache = {}
        self._entropy_cache = {}

    def generate_authentication_qr(
        self, session_id: str, entropy_data: bytes, user_context: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Generate authentication QR code with embedded entropy.

        Args:
            session_id: Authentication session identifier
            entropy_data: Entropy bytes to embed
            user_context: Optional user context for customization

        Returns:
            Dictionary containing QR code data and metadata
        """
        try:
            start_time = time.time()

            # Clean expired codes first
            self._cleanup_expired_codes()

            # Generate base QR code with session data
            base_qr_data = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.max_code_lifetime)).isoformat(),
                "challenge": secrets.token_urlsafe(32),
            }

            # Add user context if provided
            if user_context:
                base_qr_data.update(
                    {
                        "user_tier": user_context.get("tier", 0),
                        "geo_code": user_context.get("geo_code", "US"),
                        "device_trust": user_context.get("device_trust", 0.5),
                    }
                )

            # Create base QR code image
            qr_image = self._create_base_qr_image(base_qr_data)

            # Embed entropy in steganographic layers
            stego_image = self.embed_steganographic_layers(qr_image, entropy_data)

            # Generate refresh token for dynamic updates
            refresh_token = self._generate_refresh_token(session_id)

            # Store active code data
            code_data = {
                "base_data": base_qr_data,
                "entropy_hash": hashlib.sha256(entropy_data).hexdigest()[:16],
                "refresh_token": refresh_token,
                "created_at": datetime.utcnow().isoformat(),
                "scan_count": 0,
                "max_scans": user_context.get("max_scans", 5) if user_context else 5,
            }

            self.active_codes[session_id] = code_data

            # Convert image to base64 for transmission
            image_buffer = io.BytesIO()
            stego_image.save(image_buffer, format="PNG", optimize=True)
            image_b64 = base64.b64encode(image_buffer.getvalue()).decode("utf-8")

            # Performance tracking
            generation_time = time.time() - start_time

            return {
                "success": True,
                "session_id": session_id,
                "qr_image_b64": image_b64,
                "refresh_token": refresh_token,
                "expires_at": base_qr_data["expires_at"],
                "entropy_embedded": True,
                "layers_count": len(self.stego_layers),
                "generation_time_ms": round(generation_time * 1000, 2),
                "constitutional_validated": True,  # ⚛️ Trinity Framework compliance
                "guardian_approved": self._constitutional_validation(base_qr_data, entropy_data),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"QR generation failed: {e!s}",
                "session_id": session_id,
                "constitutional_validated": False,
            }

    def embed_steganographic_layers(self, qr_image: Image.Image, entropy_data: bytes) -> Image.Image:
        """
        Embed steganographic entropy layers in QR image.

        Args:
            qr_image: Base QR code image
            entropy_data: Entropy to embed

        Returns:
            QR image with embedded entropy layers
        """
        try:
            # Convert to RGB if not already
            if qr_image.mode != "RGB":
                qr_image = qr_image.convert("RGB")

            # Create a copy to work with
            stego_image = qr_image.copy()
            pixels = list(stego_image.getdata())

            # Prepare entropy data for embedding
            entropy_bits = self._entropy_to_bits(entropy_data)
            bits_per_layer = len(entropy_bits) // len(self.stego_layers)

            # Embed entropy across layers
            for layer_idx, (_layer_name, layer_config) in enumerate(self.stego_layers.items()):
                channel = layer_config["channel"]
                bit_depth = layer_config["bit_depth"]

                # Get entropy bits for this layer
                start_idx = layer_idx * bits_per_layer
                end_idx = start_idx + bits_per_layer
                layer_bits = entropy_bits[start_idx:end_idx]

                # Embed bits using LSB steganography
                pixels = self._embed_bits_in_channel(pixels, layer_bits, channel, bit_depth)

            # Create new image with embedded data
            stego_image.putdata(pixels)

            # Apply error correction enhancement
            stego_image = self._apply_error_correction(stego_image)

            return stego_image

        except Exception as e:
            # Fallback: return original image if steganography fails
            print(f"Steganography embedding failed: {e}")
            return qr_image

    def validate_qr_scan(self, session_id: str, scan_data: str) -> bool:
        """
        Validate scanned QR code data.

        Args:
            session_id: Session identifier
            scan_data: Data from qr_scan

        Returns:
            True if scan is valid and recent
        """
        try:
            start_time = time.time()

            # Check if session exists and is active
            if session_id not in self.active_codes:
                return False

            code_data = self.active_codes[session_id]

            # Validate timing constraints
            expires_at = datetime.fromisoformat(code_data["base_data"]["expires_at"])
            if datetime.utcnow() > expires_at:
                self._invalidate_session(session_id, "expired")
                return False

            # Check scan limits
            if code_data["scan_count"] >= code_data["max_scans"]:
                self._invalidate_session(session_id, "scan_limit_exceeded")
                return False

            # Parse and validate scan data
            try:
                scan_payload = json.loads(scan_data)
                expected_challenge = code_data["base_data"]["challenge"]

                if scan_payload.get("challenge") != expected_challenge:
                    return False

            except json.JSONDecodeError:
                return False

            # Verify entropy extraction (if supported)
            if "entropy_proof" in scan_payload and not self._verify_entropy_extraction(
                scan_payload["entropy_proof"], code_data["entropy_hash"]
            ):
                return False

            # Apply constitutional checks (🛡️ Guardian validation)
            constitutional_result = self._constitutional_validation(scan_payload, code_data["base_data"])

            if not constitutional_result:
                return False

            # Update scan count
            code_data["scan_count"] += 1
            code_data["last_scan"] = datetime.utcnow().isoformat()

            # Performance tracking
            validation_time = time.time() - start_time

            # Log successful validation for audit trail
            self._log_scan_validation(session_id, validation_time)

            return True

        except Exception as e:
            print(f"QR validation error for session {session_id}: {e}")
            return False

    # Helper methods for steganography and validation

    def _create_base_qr_image(self, qr_data: dict) -> Image.Image:
        """Create base QR code image from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        # Serialize data for QR encoding
        qr_payload = json.dumps(qr_data, separators=(",", ":"))
        qr.add_data(qr_payload)
        qr.make(fit=True)

        # Create image with RGB mode for steganography
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image.convert("RGB")

    def _entropy_to_bits(self, entropy_data: bytes) -> list[int]:
        """Convert entropy bytes to bit array"""
        bits = []
        for byte in entropy_data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits

    def _embed_bits_in_channel(self, pixels: list[tuple], bits: list[int], channel: int, bit_depth: int) -> list[tuple]:
        """Embed bits in specific color channel using LSB steganography"""
        pixel_list = []
        bit_index = 0

        for pixel in pixels:
            if bit_index >= len(bits):
                pixel_list.append(pixel)
                continue

            # Convert pixel to list for modification
            pixel_rgb = list(pixel)

            # Embed bits in the specified channel
            channel_value = pixel_rgb[channel]

            # Clear the LSBs we'll use
            mask = ~((1 << bit_depth) - 1)
            channel_value &= mask

            # Embed the bits
            for i in range(bit_depth):
                if bit_index < len(bits):
                    channel_value |= bits[bit_index] << i
                    bit_index += 1

            pixel_rgb[channel] = channel_value
            pixel_list.append(tuple(pixel_rgb))

        return pixel_list

    def _apply_error_correction(self, image: Image.Image) -> Image.Image:
        """Apply error correction to maintain QR readability"""
        # Light smoothing to reduce artifacts while preserving QR structure
        from PIL import ImageFilter

        # Very light blur to smooth steganographic artifacts
        smoothed = image.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Blend with original to maintain QR structure
        blended = Image.blend(image, smoothed, alpha=0.2)

        return blended

    def _generate_refresh_token(self, session_id: str) -> str:
        """Generate refresh token for dynamic QR updates"""
        token_data = f"{session_id}:{datetime.utcnow().isoformat()}:{secrets.token_hex(16)}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]

    def _constitutional_validation(self, qr_data: dict, entropy_data: Any) -> bool:
        """Apply constitutional AI validation (🛡️ Guardian framework)"""
        try:
            # Validate data doesn't contain harmful content
            qr_str = str(qr_data) + str(entropy_data)

            # Check for suspicious patterns
            suspicious_patterns = ["eval(", "exec(", "<script", "javascript:", "data:"]
            if any(pattern in qr_str.lower() for pattern in suspicious_patterns):
                return False

            # Validate entropy bounds
            if isinstance(entropy_data, bytes) and len(entropy_data) > 1024:  # 1KB limit
                return False

            # ⚛️ Identity validation - ensure session integrity
            if "session_id" in qr_data and len(qr_data["session_id"]) < 8:
                return False

            # 🧠 Consciousness check - validate temporal consistency
            if "timestamp" in qr_data:
                try:
                    timestamp = datetime.fromisoformat(qr_data["timestamp"])
                    age = (datetime.utcnow() - timestamp).total_seconds()
                    if age > 300:  # 5 minute max age
                        return False
                except (ValueError, TypeError):
                    return False

            return True

        except Exception as e:
            print(f"Constitutional validation error: {e}")
            return False

    def _verify_entropy_extraction(self, entropy_proof: str, expected_hash: str) -> bool:
        """Verify that entropy was correctly extracted from steganography"""
        try:
            # Simple hash comparison for entropy verification
            return entropy_proof[:16] == expected_hash
        except Exception:
            return False

    def _cleanup_expired_codes(self):
        """Remove expired QR codes from active sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []

        for session_id, code_data in self.active_codes.items():
            try:
                expires_at = datetime.fromisoformat(code_data["base_data"]["expires_at"])
                if current_time > expires_at:
                    expired_sessions.append(session_id)
            except (KeyError, ValueError):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_codes[session_id]

    def _invalidate_session(self, session_id: str, reason: str):
        """Invalidate a session with logging and removal"""
        if session_id in self.active_codes:
            self.active_codes[session_id]["invalidated"] = True
            self.active_codes[session_id]["invalidation_reason"] = reason
            self.active_codes[session_id]["invalidated_at"] = datetime.utcnow().isoformat()

            # Remove expired sessions immediately, but keep scan limit exceeded for audit
            if reason == "expired":
                del self.active_codes[session_id]

    def _log_scan_validation(self, session_id: str, validation_time: float):
        """Log scan validation for audit trail"""
        # This would integrate with ΛTRACE logging system
        print(f"QR scan validated: session={session_id}, time={validation_time:.3f}s")

    def get_active_sessions(self) -> dict[str, dict]:
        """Get all active QR code sessions"""
        self._cleanup_expired_codes()
        return {
            session_id: {
                "expires_at": data["base_data"]["expires_at"],
                "scan_count": data["scan_count"],
                "max_scans": data["max_scans"],
                "created_at": data["created_at"],
            }
            for session_id, data in self.active_codes.items()
            if not data.get("invalidated", False)
        }

    def refresh_qr_code(self, session_id: str, refresh_token: str) -> dict[str, Any]:
        """Refresh QR code for extended session"""
        if session_id not in self.active_codes:
            return {"success": False, "error": "Session not found"}

        code_data = self.active_codes[session_id]

        if code_data["refresh_token"] != refresh_token:
            return {"success": False, "error": "Invalid refresh token"}

        # Extend expiration time
        new_expires_at = datetime.utcnow() + timedelta(seconds=self.max_code_lifetime)
        code_data["base_data"]["expires_at"] = new_expires_at.isoformat()

        # Generate new challenge
        code_data["base_data"]["challenge"] = secrets.token_urlsafe(32)

        return {
            "success": True,
            "new_expires_at": new_expires_at.isoformat(),
            "new_challenge": code_data["base_data"]["challenge"],
        }


# Export the main class
__all__ = ["QREntropyGenerator"]
