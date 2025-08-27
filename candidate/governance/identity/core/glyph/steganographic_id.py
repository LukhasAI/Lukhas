"""
Steganographic Identity Embedder

This module provides steganographic embedding of identity data into GLYPHs
using multiple techniques including LSB, DCT, and quantum-enhanced methods.

Features:
- Multi-layer steganographic embedding
- Identity data encoding and encryption
- Quantum-enhanced hiding techniques
- Detection resistance algorithms
- Integrity verification

Author: LUKHAS Identity Team
Version: 1.0.0
"""

import base64
import hashlib
import json
import logging
import secrets
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np
from cryptography.fernet import Fernet
from PIL import Image

logger = logging.getLogger("LUKHAS_STEGANOGRAPHIC_ID")


class EmbeddingMethod(Enum):
    """Steganographic embedding methods"""

    LSB = "lsb"  # Least Significant Bit
    DCT = "dct"  # Discrete Cosine Transform
    WAVELET = "wavelet"  # Wavelet Transform
    FRACTAL = "fractal"  # Fractal-based hiding
    QUANTUM_LSB = "qi_lsb"  # Quantum-enhanced LSB
    MULTI_LAYER = "multi_layer"  # Multiple method combination


class EmbeddingStrength(Enum):
    """Embedding strength levels"""

    SUBTLE = "subtle"  # Hard to detect, lower capacity
    MODERATE = "moderate"  # Balanced detection/capacity
    STRONG = "strong"  # Higher capacity, more detectable
    QUANTUM = "quantum"  # Quantum-enhanced hiding


@dataclass
class IdentityEmbedData:
    """Identity data to embed steganographically"""

    lambda_id: str
    tier_level: int
    biometric_hash: Optional[str] = None
    consciousness_signature: Optional[str] = None
    dream_pattern_hash: Optional[str] = None
    cultural_context: Optional[str] = None
    custom_data: Optional[dict[str, Any]] = None
    timestamp: float = 0.0
    expires_at: float = 0.0


@dataclass
class EmbeddingResult:
    """Result of steganographic embedding"""

    success: bool
    embedded_image: Optional[Image.Image]
    embedding_metadata: dict[str, Any]
    extraction_key: str
    integrity_hash: str
    detection_resistance_score: float
    capacity_used: float
    error_message: Optional[str] = None


class SteganographicIdentityEmbedder:
    """
    Steganographic Identity Embedder

    Embeds identity data into images using various steganographic techniques
    with quantum-enhanced security features.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Embedding parameters
        self.max_embedding_ratio = self.config.get(
            "max_embedding_ratio", 0.25
        )  # 25% of image capacity
        self.default_strength = EmbeddingStrength.MODERATE
        self.detection_threshold = 0.8  # Minimum detection resistance score

        # Quantum-enhanced parameters
        self.qi_key_size = 32  # 256-bit quantum keys
        self.entropy_pool_size = 1024  # Entropy pool for quantum randomness

        # Initialize entropy pool
        self.entropy_pool = secrets.token_bytes(self.entropy_pool_size)
        self.entropy_position = 0

        logger.info("Steganographic Identity Embedder initialized")

    def embed_identity_data(
        self,
        carrier_image: Image.Image,
        identity_data: IdentityEmbedData,
        method: EmbeddingMethod = EmbeddingMethod.QUANTUM_LSB,
        strength: EmbeddingStrength = EmbeddingStrength.MODERATE,
    ) -> EmbeddingResult:
        """
        Embed identity data into carrier image

        Args:
            carrier_image: Image to embed data into
            identity_data: Identity data to embed
            method: Embedding method to use
            strength: Embedding strength level

        Returns:
            EmbeddingResult with embedded image and metadata
        """
        try:
            # Validate input
            if not carrier_image or not identity_data:
                return EmbeddingResult(
                    success=False,
                    embedded_image=None,
                    embedding_metadata={},
                    extraction_key="",
                    integrity_hash="",
                    detection_resistance_score=0.0,
                    capacity_used=0.0,
                    error_message="Invalid input data",
                )

            # Prepare identity data for embedding
            prepared_data = self._prepare_identity_data(identity_data)

            # Generate embedding keys
            embedding_keys = self._generate_embedding_keys(identity_data.lambda_id)

            # Encrypt identity data
            encrypted_data = self._encrypt_identity_data(
                prepared_data, embedding_keys["encryption"]
            )

            # Select embedding algorithm
            if method == EmbeddingMethod.LSB:
                result = self._embed_lsb(carrier_image, encrypted_data, strength)
            elif method == EmbeddingMethod.DCT:
                result = self._embed_dct(carrier_image, encrypted_data, strength)
            elif method == EmbeddingMethod.QUANTUM_LSB:
                result = self._embed_quantum_lsb(
                    carrier_image, encrypted_data, strength, embedding_keys
                )
            elif method == EmbeddingMethod.MULTI_LAYER:
                result = self._embed_multi_layer(
                    carrier_image, encrypted_data, strength, embedding_keys
                )
            else:
                # Default to quantum LSB
                result = self._embed_quantum_lsb(
                    carrier_image, encrypted_data, strength, embedding_keys
                )

            if not result["success"]:
                return EmbeddingResult(
                    success=False,
                    embedded_image=None,
                    embedding_metadata={},
                    extraction_key="",
                    integrity_hash="",
                    detection_resistance_score=0.0,
                    capacity_used=0.0,
                    error_message=result.get("error", "Embedding failed"),
                )

            # Calculate detection resistance
            detection_resistance = self._calculate_detection_resistance(
                carrier_image, result["embedded_image"], method, strength
            )

            # Calculate capacity usage
            capacity_used = len(encrypted_data) / self._calculate_image_capacity(
                carrier_image
            )

            # Generate integrity hash
            integrity_hash = self._generate_integrity_hash(
                result["embedded_image"], identity_data, embedding_keys
            )

            # Create embedding metadata
            embedding_metadata = {
                "method": method.value,
                "strength": strength.value,
                "data_size": len(encrypted_data),
                "image_size": carrier_image.size,
                "embedding_locations": result.get("locations", []),
                "qi_enhanced": method
                in [EmbeddingMethod.QUANTUM_LSB, EmbeddingMethod.MULTI_LAYER],
                "layers_used": result.get("layers", 1),
                "encryption_algorithm": "Fernet",
                "detection_countermeasures": result.get("countermeasures", []),
            }

            return EmbeddingResult(
                success=True,
                embedded_image=result["embedded_image"],
                embedding_metadata=embedding_metadata,
                extraction_key=base64.b64encode(embedding_keys["extraction"]).decode(),
                integrity_hash=integrity_hash,
                detection_resistance_score=detection_resistance,
                capacity_used=capacity_used,
            )

        except Exception as e:
            logger.error(f"Steganographic embedding error: {e}")
            return EmbeddingResult(
                success=False,
                embedded_image=None,
                embedding_metadata={},
                extraction_key="",
                integrity_hash="",
                detection_resistance_score=0.0,
                capacity_used=0.0,
                error_message=str(e),
            )

    def extract_identity_data(
        self,
        stego_image: Image.Image,
        extraction_key: str,
        method: EmbeddingMethod = EmbeddingMethod.QUANTUM_LSB,
    ) -> dict[str, Any]:
        """
        Extract identity data from steganographic image

        Args:
            stego_image: Image containing embedded data
            extraction_key: Key for data extraction
            method: Embedding method used

        Returns:
            Extracted identity data
        """
        try:
            # Decode extraction key
            embedding_keys = {"extraction": base64.b64decode(extraction_key.encode())}

            # Extract encrypted data based on method
            if method == EmbeddingMethod.LSB:
                encrypted_data = self._extract_lsb(stego_image)
            elif method == EmbeddingMethod.DCT:
                encrypted_data = self._extract_dct(stego_image)
            elif method == EmbeddingMethod.QUANTUM_LSB:
                encrypted_data = self._extract_quantum_lsb(stego_image, embedding_keys)
            elif method == EmbeddingMethod.MULTI_LAYER:
                encrypted_data = self._extract_multi_layer(stego_image, embedding_keys)
            else:
                encrypted_data = self._extract_quantum_lsb(stego_image, embedding_keys)

            if not encrypted_data:
                return {"success": False, "error": "No embedded data found"}

            # Decrypt identity data
            decrypted_data = self._decrypt_identity_data(
                encrypted_data, embedding_keys["extraction"][:32]
            )

            # Parse identity data
            identity_data = self._parse_identity_data(decrypted_data)

            return {
                "success": True,
                "identity_data": identity_data,
                "extraction_method": method.value,
                "data_size": len(encrypted_data),
            }

        except Exception as e:
            logger.error(f"Steganographic extraction error: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_identity_data(self, identity_data: IdentityEmbedData) -> bytes:
        """Prepare identity data for embedding"""
        data_dict = {
            "lambda_id_hash": hashlib.sha256(
                identity_data.lambda_id.encode()
            ).hexdigest()[:16],
            "tier_level": identity_data.tier_level,
            "timestamp": identity_data.timestamp,
            "expires_at": identity_data.expires_at,
        }

        # Add optional fields
        if identity_data.biometric_hash:
            data_dict["biometric_hash"] = identity_data.biometric_hash

        if identity_data.consciousness_signature:
            data_dict["consciousness_signature"] = identity_data.consciousness_signature

        if identity_data.dream_pattern_hash:
            data_dict["dream_pattern_hash"] = identity_data.dream_pattern_hash

        if identity_data.cultural_context:
            data_dict["cultural_context"] = identity_data.cultural_context

        if identity_data.custom_data:
            data_dict["custom_data"] = identity_data.custom_data

        # Convert to bytes
        json_data = json.dumps(data_dict, sort_keys=True)
        return json_data.encode("utf-8")

    def _generate_embedding_keys(self, lambda_id: str) -> dict[str, bytes]:
        """Generate keys for embedding"""
        # Generate quantum-enhanced keys
        key_material = lambda_id.encode() + self._get_quantum_entropy(64)

        # Derive encryption key
        encryption_key = hashlib.scrypt(
            key_material, salt=b"LUKHAS_STEGO_ENC", n=16384, r=8, p=1, dklen=32
        )

        # Derive extraction key (includes encryption key + additional data)
        extraction_key = hashlib.scrypt(
            key_material, salt=b"LUKHAS_STEGO_EXT", n=16384, r=8, p=1, dklen=64
        )

        return {"encryption": encryption_key, "extraction": extraction_key}

    def _encrypt_identity_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt identity data for embedding"""
        fernet = Fernet(base64.urlsafe_b64encode(key))
        return fernet.encrypt(data)

    def _decrypt_identity_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt identity data after extraction"""
        fernet = Fernet(base64.urlsafe_b64encode(key))
        return fernet.decrypt(encrypted_data)

    def _embed_lsb(
        self, image: Image.Image, data: bytes, strength: EmbeddingStrength
    ) -> dict[str, Any]:
        """Embed data using LSB method"""
        img_array = np.array(image.convert("RGB"))

        # Convert data to binary
        binary_data = "".join(format(byte, "08b") for byte in data)
        binary_data += "1111111111111110"  # End marker

        # Calculate embedding capacity
        capacity = img_array.size
        if len(binary_data) > capacity:
            return {"success": False, "error": "Data too large for image"}

        # Embed data in LSBs
        data_index = 0
        locations = []

        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(3):  # RGB channels
                    if data_index < len(binary_data):
                        # Modify LSB
                        img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | int(
                            binary_data[data_index]
                        )
                        locations.append((i, j, k))
                        data_index += 1
                    else:
                        break
                if data_index >= len(binary_data):
                    break
            if data_index >= len(binary_data):
                break

        embedded_image = Image.fromarray(img_array, "RGB")

        return {
            "success": True,
            "embedded_image": embedded_image,
            "locations": locations[:100],  # Store first 100 locations
            "layers": 1,
        }

    def _embed_quantum_lsb(
        self,
        image: Image.Image,
        data: bytes,
        strength: EmbeddingStrength,
        keys: dict[str, bytes],
    ) -> dict[str, Any]:
        """Embed data using quantum-enhanced LSB method"""
        img_array = np.array(image.convert("RGB"))

        # Generate quantum-guided embedding pattern
        embedding_pattern = self._generate_quantum_pattern(
            img_array.shape, len(data) * 8, keys["extraction"]
        )

        # Convert data to binary
        binary_data = "".join(format(byte, "08b") for byte in data)
        binary_data += "1111111111111110"  # End marker

        # Embed using quantum pattern
        data_index = 0
        locations = []
        countermeasures = []

        for pos in embedding_pattern:
            if data_index >= len(binary_data):
                break

            i, j, k = pos
            if i < img_array.shape[0] and j < img_array.shape[1] and k < 3:
                # Quantum-enhanced LSB modification
                original_value = img_array[i, j, k]
                new_bit = int(binary_data[data_index])

                # Apply quantum noise for detection resistance
                qi_noise = self._get_quantum_entropy(1)[0] & 0x01
                if strength == EmbeddingStrength.QUANTUM:
                    # Add quantum countermeasures
                    if qi_noise:
                        # Occasionally flip adjacent bits to confuse detectors
                        adjacent_pos = self._get_adjacent_position(
                            i, j, k, img_array.shape
                        )
                        if adjacent_pos:
                            ai, aj, ak = adjacent_pos
                            img_array[ai, aj, ak] ^= 0x01
                            countermeasures.append(("qi_noise", adjacent_pos))

                img_array[i, j, k] = (original_value & 0xFE) | new_bit
                locations.append((i, j, k))
                data_index += 1

        embedded_image = Image.fromarray(img_array, "RGB")

        return {
            "success": True,
            "embedded_image": embedded_image,
            "locations": locations[:100],
            "layers": 1,
            "countermeasures": countermeasures[:50],
        }

    def _embed_multi_layer(
        self,
        image: Image.Image,
        data: bytes,
        strength: EmbeddingStrength,
        keys: dict[str, bytes],
    ) -> dict[str, Any]:
        """Embed data using multiple layers and methods"""
        # Split data into chunks for different layers
        data_chunks = self._split_data_for_layers(data, 3)

        # Layer 1: Quantum LSB
        layer1_result = self._embed_quantum_lsb(image, data_chunks[0], strength, keys)
        if not layer1_result["success"]:
            return layer1_result

        current_image = layer1_result["embedded_image"]

        # Layer 2: DCT embedding (if data available)
        if len(data_chunks) > 1 and data_chunks[1]:
            layer2_result = self._embed_dct(current_image, data_chunks[1], strength)
            if layer2_result["success"]:
                current_image = layer2_result["embedded_image"]

        # Layer 3: Fractal embedding (if data available)
        if len(data_chunks) > 2 and data_chunks[2]:
            layer3_result = self._embed_fractal(current_image, data_chunks[2], strength)
            if layer3_result["success"]:
                current_image = layer3_result["embedded_image"]

        return {
            "success": True,
            "embedded_image": current_image,
            "locations": layer1_result.get("locations", []),
            "layers": min(3, len([chunk for chunk in data_chunks if chunk])),
            "countermeasures": layer1_result.get("countermeasures", []),
        }

    def _embed_dct(
        self, image: Image.Image, data: bytes, strength: EmbeddingStrength
    ) -> dict[str, Any]:
        """Embed data using DCT (Discrete Cosine Transform) method"""
        # This is a simplified DCT embedding
        # In full implementation, would use proper DCT transformation

        img_array = np.array(image.convert("RGB")).astype(np.float32)
        binary_data = "".join(format(byte, "08b") for byte in data)
        binary_data += "1111111111111110"

        # Simplified DCT-like embedding in frequency domain
        data_index = 0

        # Process in 8x8 blocks (simplified)
        for i in range(0, img_array.shape[0] - 7, 8):
            for j in range(0, img_array.shape[1] - 7, 8):
                if data_index >= len(binary_data):
                    break

                # Modify middle-frequency coefficients
                for k in range(3):
                    if data_index < len(binary_data):
                        # Modify a middle-frequency position
                        modify_i, modify_j = 2, 3  # Middle frequency
                        bit_value = int(binary_data[data_index])

                        # Embed bit by modifying coefficient sign
                        if bit_value == 1:
                            img_array[i + modify_i, j + modify_j, k] += 1.0
                        else:
                            img_array[i + modify_i, j + modify_j, k] -= 1.0

                        data_index += 1

            if data_index >= len(binary_data):
                break

        # Convert back to image
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        embedded_image = Image.fromarray(img_array, "RGB")

        return {
            "success": True,
            "embedded_image": embedded_image,
            "locations": [],
            "layers": 1,
        }

    def _embed_fractal(
        self, image: Image.Image, data: bytes, strength: EmbeddingStrength
    ) -> dict[str, Any]:
        """Embed data using fractal-based method"""
        # Simplified fractal embedding
        img_array = np.array(image.convert("RGB"))
        binary_data = "".join(format(byte, "08b") for byte in data)

        # Use fractal patterns for embedding locations
        data_index = 0
        fractal_positions = self._generate_fractal_positions(
            img_array.shape, len(binary_data)
        )

        for pos in fractal_positions:
            if data_index >= len(binary_data):
                break

            i, j, k = pos
            if i < img_array.shape[0] and j < img_array.shape[1] and k < 3:
                bit_value = int(binary_data[data_index])
                img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | bit_value
                data_index += 1

        embedded_image = Image.fromarray(img_array, "RGB")

        return {
            "success": True,
            "embedded_image": embedded_image,
            "locations": fractal_positions[:100],
            "layers": 1,
        }

    def _extract_lsb(self, image: Image.Image) -> Optional[bytes]:
        """Extract data using LSB method"""
        img_array = np.array(image.convert("RGB"))

        binary_data = ""
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(3):
                    binary_data += str(img_array[i, j, k] & 1)

        # Find end marker
        end_marker = "1111111111111110"
        end_index = binary_data.find(end_marker)
        if end_index == -1:
            return None

        # Convert binary to bytes
        extracted_binary = binary_data[:end_index]
        data_bytes = bytearray()

        for i in range(0, len(extracted_binary), 8):
            byte_binary = extracted_binary[i : i + 8]
            if len(byte_binary) == 8:
                data_bytes.append(int(byte_binary, 2))

        return bytes(data_bytes)

    def _extract_quantum_lsb(
        self, image: Image.Image, keys: dict[str, bytes]
    ) -> Optional[bytes]:
        """Extract data using quantum-enhanced LSB method"""
        img_array = np.array(image.convert("RGB"))

        # Regenerate quantum pattern
        embedding_pattern = self._generate_quantum_pattern(
            img_array.shape, img_array.size, keys["extraction"]
        )

        binary_data = ""
        for pos in embedding_pattern:
            i, j, k = pos
            if i < img_array.shape[0] and j < img_array.shape[1] and k < 3:
                binary_data += str(img_array[i, j, k] & 1)

                # Check for end marker periodically
                if len(binary_data) >= 16 and binary_data[-16:] == "1111111111111110":
                    break

        # Find end marker
        end_marker = "1111111111111110"
        end_index = binary_data.find(end_marker)
        if end_index == -1:
            return None

        # Convert to bytes
        extracted_binary = binary_data[:end_index]
        data_bytes = bytearray()

        for i in range(0, len(extracted_binary), 8):
            byte_binary = extracted_binary[i : i + 8]
            if len(byte_binary) == 8:
                data_bytes.append(int(byte_binary, 2))

        return bytes(data_bytes)

    def _extract_dct(self, image: Image.Image) -> Optional[bytes]:
        """Extract data using DCT method"""
        # Simplified DCT extraction
        img_array = np.array(image.convert("RGB")).astype(np.float32)
        binary_data = ""

        # Process in 8x8 blocks
        for i in range(0, img_array.shape[0] - 7, 8):
            for j in range(0, img_array.shape[1] - 7, 8):
                for k in range(3):
                    # Extract from middle-frequency coefficient
                    modify_i, modify_j = 2, 3
                    coeff_value = img_array[i + modify_i, j + modify_j, k]

                    # Determine bit based on coefficient sign/magnitude
                    if coeff_value > 128:
                        binary_data += "1"
                    else:
                        binary_data += "0"

        # Find end marker and convert to bytes
        return self._binary_to_bytes(binary_data)

    def _extract_multi_layer(
        self, image: Image.Image, keys: dict[str, bytes]
    ) -> Optional[bytes]:
        """Extract data from multiple layers"""
        # Extract from primary quantum LSB layer
        primary_data = self._extract_quantum_lsb(image, keys)

        if primary_data:
            return primary_data

        # Fallback to LSB if quantum extraction fails
        return self._extract_lsb(image)

    def _generate_quantum_pattern(
        self, shape: tuple[int, ...], data_bits: int, key: bytes
    ) -> list[tuple[int, int, int]]:
        """Generate quantum-guided embedding pattern"""
        # Use key to seed quantum pattern generation
        np.random.seed(struct.unpack("I", key[:4])[0])

        positions = []
        max_positions = shape[0] * shape[1] * 3

        # Generate pseudo-random positions using quantum-seeded RNG
        for _ in range(min(data_bits, max_positions)):
            i = np.random.randint(0, shape[0])
            j = np.random.randint(0, shape[1])
            k = np.random.randint(0, 3)
            positions.append((i, j, k))

        return positions

    def _generate_fractal_positions(
        self, shape: tuple[int, ...], data_bits: int
    ) -> list[tuple[int, int, int]]:
        """Generate fractal-based embedding positions"""
        positions = []

        # Simple fractal pattern (Sierpinski-like)
        for i in range(min(data_bits, shape[0] * shape[1] * 3)):
            # Use fractal iteration to determine position
            x = i % shape[1]
            y = (i // shape[1]) % shape[0]
            z = i % 3

            # Apply fractal transformation
            fx = int(x * 0.618033988749) % shape[1]  # Golden ratio
            fy = int(y * 0.618033988749) % shape[0]

            positions.append((fy, fx, z))

        return positions

    def _get_quantum_entropy(self, num_bytes: int) -> bytes:
        """Get quantum entropy bytes"""
        # Cycle through entropy pool
        if self.entropy_position + num_bytes > len(self.entropy_pool):
            # Regenerate entropy pool
            self.entropy_pool = secrets.token_bytes(self.entropy_pool_size)
            self.entropy_position = 0

        entropy = self.entropy_pool[
            self.entropy_position : self.entropy_position + num_bytes
        ]
        self.entropy_position += num_bytes

        return entropy

    def _get_adjacent_position(
        self, i: int, j: int, k: int, shape: tuple[int, ...]
    ) -> Optional[tuple[int, int, int]]:
        """Get adjacent position for quantum noise"""
        adjacent_offsets = [(0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0)]

        for di, dj, dk in adjacent_offsets:
            ni, nj, nk = i + di, j + dj, (k + dk) % 3
            if 0 <= ni < shape[0] and 0 <= nj < shape[1]:
                return (ni, nj, nk)

        return None

    def _split_data_for_layers(self, data: bytes, num_layers: int) -> list[bytes]:
        """Split data into chunks for multi-layer embedding"""
        chunk_size = len(data) // num_layers
        chunks = []

        for i in range(num_layers):
            start = i * chunk_size
            if i == num_layers - 1:
                # Last chunk gets remainder
                chunks.append(data[start:])
            else:
                chunks.append(data[start : start + chunk_size])

        return chunks

    def _calculate_image_capacity(self, image: Image.Image) -> int:
        """Calculate embedding capacity of image"""
        return image.size[0] * image.size[1] * 3  # RGB channels

    def _calculate_detection_resistance(
        self,
        original: Image.Image,
        embedded: Image.Image,
        method: EmbeddingMethod,
        strength: EmbeddingStrength,
    ) -> float:
        """Calculate detection resistance score"""
        # Calculate statistical measures
        orig_array = np.array(original.convert("RGB"))
        embed_array = np.array(embedded.convert("RGB"))

        # Mean Square Error
        mse = np.mean((orig_array - embed_array) ** 2)

        # Peak Signal-to-Noise Ratio
        psnr = float("inf") if mse == 0 else 20 * np.log10(255.0 / np.sqrt(mse))

        # Base resistance score on PSNR and method
        base_score = min(1.0, psnr / 60.0)  # Higher PSNR = better resistance

        # Method-specific bonuses
        method_bonus = {
            EmbeddingMethod.LSB: 0.0,
            EmbeddingMethod.DCT: 0.1,
            EmbeddingMethod.QUANTUM_LSB: 0.2,
            EmbeddingMethod.MULTI_LAYER: 0.3,
        }.get(method, 0.0)

        # Strength bonus
        strength_bonus = {
            EmbeddingStrength.SUBTLE: 0.2,
            EmbeddingStrength.MODERATE: 0.1,
            EmbeddingStrength.STRONG: 0.0,
            EmbeddingStrength.QUANTUM: 0.3,
        }.get(strength, 0.0)

        return min(1.0, base_score + method_bonus + strength_bonus)

    def _generate_integrity_hash(
        self,
        image: Image.Image,
        identity_data: IdentityEmbedData,
        keys: dict[str, bytes],
    ) -> str:
        """Generate integrity hash for verification"""
        # Combine image data, identity data, and keys
        image_hash = hashlib.sha256(image.tobytes()).hexdigest()
        identity_hash = hashlib.sha256(identity_data.lambda_id.encode()).hexdigest()
        key_hash = hashlib.sha256(keys["extraction"]).hexdigest()

        combined = f"{image_hash}:{identity_hash}:{key_hash}"
        return hashlib.sha3_256(combined.encode()).hexdigest()

    def _parse_identity_data(self, data: bytes) -> dict[str, Any]:
        """Parse identity data from bytes"""
        try:
            json_str = data.decode("utf-8")
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing identity data: {e}")
            return {}

    def _binary_to_bytes(self, binary_data: str) -> Optional[bytes]:
        """Convert binary string to bytes with end marker detection"""
        end_marker = "1111111111111110"
        end_index = binary_data.find(end_marker)

        if end_index == -1:
            return None

        extracted_binary = binary_data[:end_index]
        data_bytes = bytearray()

        for i in range(0, len(extracted_binary), 8):
            byte_binary = extracted_binary[i : i + 8]
            if len(byte_binary) == 8:
                data_bytes.append(int(byte_binary, 2))

        return bytes(data_bytes)
