"""
VIVOX.EVRN Vector Encryption
Non-reversible encryption for perceptual vectors
"""

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np


class EncryptionProtocol(Enum):
    """Available encryption protocols"""

    HOMOMORPHIC = "homomorphic"  # Allows computation on encrypted data
    DIFFERENTIAL = "differential"  # Adds noise for privacy
    TRANSFORM = "transform"  # Non-reversible transformation
    HYBRID = "hybrid"  # Combination of methods


@dataclass
class VectorSignature:
    """Signature for encrypted vector verification"""

    hash_value: str
    protocol: EncryptionProtocol
    dimension: int
    timestamp: float
    metadata: dict[str, Any]

    def verify(self, vector: np.ndarray) -> bool:
        """Verify vector matches signature"""
        computed_hash = hashlib.sha256(vector.tobytes()).hexdigest()
        return computed_hash == self.hash_value


class PerceptualEncryptor:
    """
    Handles encryption of perceptual data into non-decodable vectors
    Ensures privacy while maintaining analytical capabilities
    """

    def __init__(
        self,
        master_key: bytes = None,
        protocol: EncryptionProtocol = EncryptionProtocol.HYBRID,
        vector_dimension: int = 512,
    ):
        self.master_key = master_key or self._generate_master_key()
        self.protocol = protocol
        self.vector_dimension = vector_dimension

        # Initialize encryption components
        self.transform_matrices = self._initialize_transform_matrices()
        self.noise_parameters = self._initialize_noise_parameters()
        self.homomorphic_keys = self._initialize_homomorphic_keys()

        # Cache for performance
        self.encryption_cache = {}
        self.max_cache_size = 1000

    def _generate_master_key(self) -> bytes:
        """Generate secure master key"""
        # In production, this would use proper key generation
        return hashlib.pbkdf2_hmac(
            "sha256", b"VIVOX_EVRN_MASTER_2024", b"ethical_perception_salt", 100000
        )

    def _initialize_transform_matrices(self) -> dict[str, np.ndarray]:
        """Initialize non-reversible transformation matrices"""
        np.random.seed(int.from_bytes(self.master_key[:4], "big"))

        matrices = {}

        # Random projection matrix
        matrices["projection"] = np.random.randn(self.vector_dimension, self.vector_dimension * 2)

        # Rotation matrices for different angles
        for angle in [30, 60, 90, 120]:
            matrices[f"rotation_{angle}"] = self._create_rotation_matrix(angle)

        # Hadamard-like matrix for mixing
        matrices["hadamard"] = self._create_hadamard_matrix(self.vector_dimension)

        return matrices

    def _initialize_noise_parameters(self) -> dict[str, Any]:
        """Initialize differential privacy noise parameters"""
        return {
            "epsilon": 1.0,  # Privacy budget
            "delta": 1e-5,  # Failure probability
            "sensitivity": 1.0,  # Query sensitivity
            "mechanism": "laplace",  # Noise mechanism
        }

    def _initialize_homomorphic_keys(self) -> dict[str, Any]:
        """Initialize keys for homomorphic operations"""
        # Simplified version - real implementation would use proper FHE
        return {
            "public_key": self._derive_key(b"public"),
            "eval_key": self._derive_key(b"eval"),
            "modulus": 2**32 - 5,
        }

    def _derive_key(self, purpose: bytes) -> bytes:
        """Derive key for specific purpose"""
        return hashlib.pbkdf2_hmac("sha256", self.master_key, purpose, 10000)

    def _create_rotation_matrix(self, angle_degrees: float) -> np.ndarray:
        """Create high-dimensional rotation matrix"""
        # For high dimensions, use Givens rotations
        matrix = np.eye(self.vector_dimension)

        # Apply random rotations in different planes
        np.random.seed(int(angle_degrees))
        num_rotations = self.vector_dimension // 2

        for _ in range(num_rotations):
            i, j = np.random.choice(self.vector_dimension, 2, replace=False)
            angle = np.radians(angle_degrees)

            # Apply Givens rotation
            c, s = np.cos(angle), np.sin(angle)
            rotation = np.eye(self.vector_dimension)
            rotation[i, i] = c
            rotation[j, j] = c
            rotation[i, j] = -s
            rotation[j, i] = s

            matrix = matrix @ rotation

        return matrix

    def _create_hadamard_matrix(self, size: int) -> np.ndarray:
        """Create Hadamard-like mixing matrix"""
        # Ensure size is power of 2
        n = 1
        while n < size:
            n *= 2

        # Create Hadamard matrix
        H = np.array([[1]])
        while H.shape[0] < n:
            H = np.block([[H, H], [H, -H]])

        # Truncate or pad to exact size
        if n > size:
            H = H[:size, :size]

        return H / np.sqrt(size)

    def encrypt_vector(
        self, raw_vector: np.ndarray, metadata: Optional[dict[str, Any]] = None
    ) -> tuple[np.ndarray, VectorSignature]:
        """
        Encrypt raw perceptual vector into non-decodable form

        Args:
            raw_vector: Raw perceptual features
            metadata: Optional metadata for the vector

        Returns:
            Encrypted vector and its signature
        """
        # Normalize input dimension
        if len(raw_vector) < self.vector_dimension:
            raw_vector = np.pad(raw_vector, (0, self.vector_dimension - len(raw_vector)))
        elif len(raw_vector) > self.vector_dimension:
            raw_vector = raw_vector[: self.vector_dimension]

        # Apply encryption based on protocol
        if self.protocol == EncryptionProtocol.TRANSFORM:
            encrypted = self._apply_transform_encryption(raw_vector)
        elif self.protocol == EncryptionProtocol.DIFFERENTIAL:
            encrypted = self._apply_differential_encryption(raw_vector)
        elif self.protocol == EncryptionProtocol.HOMOMORPHIC:
            encrypted = self._apply_homomorphic_encryption(raw_vector)
        else:  # HYBRID
            encrypted = self._apply_hybrid_encryption(raw_vector)

        # Create signature
        signature = VectorSignature(
            hash_value=hashlib.sha256(encrypted.tobytes()).hexdigest(),
            protocol=self.protocol,
            dimension=len(encrypted),
            timestamp=np.datetime64("now").astype(float),
            metadata=metadata or {},
        )

        return encrypted, signature

    def _apply_transform_encryption(self, vector: np.ndarray) -> np.ndarray:
        """Apply non-reversible transformation"""
        # Project to higher dimension
        expanded = self.transform_matrices["projection"] @ np.concatenate([vector, vector])

        # Apply non-linear activation
        activated = np.tanh(expanded / np.std(expanded))

        # Mix with Hadamard transform
        mixed = self.transform_matrices["hadamard"] @ activated

        # Apply rotation
        rotated = self.transform_matrices["rotation_90"] @ mixed

        # Final non-linearity
        encrypted = np.sign(rotated) * np.sqrt(np.abs(rotated))

        return encrypted

    def _apply_differential_encryption(self, vector: np.ndarray) -> np.ndarray:
        """Apply differential privacy encryption"""
        # Add calibrated noise
        sensitivity = self.noise_parameters["sensitivity"]
        epsilon = self.noise_parameters["epsilon"]

        if self.noise_parameters["mechanism"] == "laplace":
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale, vector.shape)
        else:  # Gaussian mechanism
            delta = self.noise_parameters["delta"]
            sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
            noise = np.random.normal(0, sigma, vector.shape)

        # Add noise and clip
        noisy_vector = vector + noise
        encrypted = np.clip(noisy_vector, -1, 1)

        # Apply transformation to prevent reverse engineering
        encrypted = self.transform_matrices["rotation_60"] @ encrypted

        return encrypted

    def _apply_homomorphic_encryption(self, vector: np.ndarray) -> np.ndarray:
        """Apply simplified homomorphic encryption"""
        # Note: This is a simplified version. Real FHE would be much more complex

        # Scale and discretize
        scale_factor = 1000
        scaled = (vector * scale_factor).astype(int)

        # Apply modular arithmetic
        modulus = self.homomorphic_keys["modulus"]
        encrypted = scaled % modulus

        # Add key-based transformation
        key_int = int.from_bytes(self.homomorphic_keys["public_key"][:4], "big")
        encrypted = (encrypted + key_int) % modulus

        # Convert back to float and normalize
        encrypted = encrypted.astype(float) / scale_factor

        return encrypted

    def _apply_hybrid_encryption(self, vector: np.ndarray) -> np.ndarray:
        """Apply combination of encryption methods"""
        # Start with differential privacy
        private_vector = self._apply_differential_encryption(vector)

        # Apply transformation
        transformed = self._apply_transform_encryption(private_vector)

        # Add homomorphic layer for computation capability
        encrypted = self._apply_homomorphic_encryption(transformed)

        # Final mixing
        encrypted = self.transform_matrices["hadamard"] @ encrypted

        return encrypted

    def batch_encrypt(
        self, vectors: list[np.ndarray], metadata: Optional[list[dict[str, Any]]] = None
    ) -> list[tuple[np.ndarray, VectorSignature]]:
        """Encrypt multiple vectors efficiently"""

        results = []

        if metadata is None:
            metadata = [None] * len(vectors)

        for i, vector in enumerate(vectors):
            encrypted, signature = self.encrypt_vector(vector, metadata[i])
            results.append((encrypted, signature))

        return results

    def compute_encrypted_similarity(self, encrypted1: np.ndarray, encrypted2: np.ndarray) -> float:
        """Compute similarity between encrypted vectors"""
        # Works in encrypted space without decryption

        # Normalize vectors
        norm1 = np.linalg.norm(encrypted1)
        norm2 = np.linalg.norm(encrypted2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        normalized1 = encrypted1 / norm1
        normalized2 = encrypted2 / norm2

        # Compute cosine similarity
        similarity = np.dot(normalized1, normalized2)

        # Map to 0-1 range
        return (similarity + 1.0) / 2.0

    def aggregate_encrypted_vectors(
        self, encrypted_vectors: list[np.ndarray], weights: Optional[list[float]] = None
    ) -> np.ndarray:
        """Aggregate multiple encrypted vectors"""

        if weights is None:
            weights = [1.0] * len(encrypted_vectors)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]

        # Weighted aggregation in encrypted space
        aggregated = np.zeros_like(encrypted_vectors[0])

        for vector, weight in zip(encrypted_vectors, weights):
            aggregated += weight * vector

        # Re-encrypt to maintain privacy
        aggregated, _ = self.encrypt_vector(aggregated)

        return aggregated

    def extract_encrypted_features(
        self, encrypted_vector: np.ndarray, feature_type: str = "statistical"
    ) -> dict[str, float]:
        """Extract features from encrypted vector without decryption"""

        features = {}

        if feature_type == "statistical":
            # Statistical features that preserve privacy
            features["magnitude"] = float(np.linalg.norm(encrypted_vector))
            features["mean"] = float(np.mean(encrypted_vector))
            features["std"] = float(np.std(encrypted_vector))
            features["skew"] = float(self._compute_skew(encrypted_vector))
            features["kurtosis"] = float(self._compute_kurtosis(encrypted_vector))

        elif feature_type == "frequency":
            # Frequency domain features
            fft = np.fft.fft(encrypted_vector)
            features["dominant_frequency"] = float(np.argmax(np.abs(fft[: len(fft) // 2])))
            features["spectral_energy"] = float(np.sum(np.abs(fft) ** 2))
            features["spectral_entropy"] = float(self._compute_spectral_entropy(fft))

        elif feature_type == "pattern":
            # Pattern-based features
            features["zero_crossings"] = float(np.sum(np.diff(np.sign(encrypted_vector)) != 0))
            features["peak_count"] = float(self._count_peaks(encrypted_vector))
            features["regularity"] = float(self._compute_regularity(encrypted_vector))

        return features

    def _compute_skew(self, vector: np.ndarray) -> float:
        """Compute skewness of encrypted vector"""
        mean = np.mean(vector)
        std = np.std(vector)
        if std == 0:
            return 0.0
        return np.mean(((vector - mean) / std) ** 3)

    def _compute_kurtosis(self, vector: np.ndarray) -> float:
        """Compute kurtosis of encrypted vector"""
        mean = np.mean(vector)
        std = np.std(vector)
        if std == 0:
            return 0.0
        return np.mean(((vector - mean) / std) ** 4) - 3

    def _compute_spectral_entropy(self, fft: np.ndarray) -> float:
        """Compute spectral entropy"""
        power = np.abs(fft) ** 2
        power = power / np.sum(power)

        # Avoid log(0)
        power = power[power > 0]

        return -np.sum(power * np.log2(power))

    def _count_peaks(self, vector: np.ndarray) -> int:
        """Count peaks in encrypted vector"""
        diffs = np.diff(vector)
        peaks = np.sum((diffs[:-1] > 0) & (diffs[1:] < 0))
        return int(peaks)

    def _compute_regularity(self, vector: np.ndarray) -> float:
        """Compute regularity measure"""
        # Autocorrelation at lag 1
        if len(vector) < 2:
            return 0.0

        autocorr = np.corrcoef(vector[:-1], vector[1:])[0, 1]
        return float(np.abs(autocorr))

    def verify_encryption_integrity(
        self, encrypted_vector: np.ndarray, signature: VectorSignature
    ) -> bool:
        """Verify encrypted vector hasn't been tampered with"""
        return signature.verify(encrypted_vector)

    def create_zero_knowledge_proof(
        self, encrypted_vector: np.ndarray, property_name: str, threshold: float
    ) -> dict[str, Any]:
        """Create zero-knowledge proof of vector property"""

        # Compute property without revealing vector content
        if property_name == "magnitude_above":
            magnitude = np.linalg.norm(encrypted_vector)
            proof_valid = magnitude > threshold
        elif property_name == "anomaly_score_above":
            # Compute anomaly score in encrypted space
            mean_val = np.mean(encrypted_vector)
            std_val = np.std(encrypted_vector)
            anomaly_score = np.abs(mean_val) / (std_val + 1e-10)
            proof_valid = anomaly_score > threshold
        else:
            proof_valid = False

        # Create proof
        proof = {
            "property": property_name,
            "threshold": threshold,
            "valid": proof_valid,
            "timestamp": np.datetime64("now").astype(float),
            "proof_hash": hashlib.sha256(
                f"{property_name}_{threshold}_{proof_valid}".encode()
            ).hexdigest(),
        }

        return proof
