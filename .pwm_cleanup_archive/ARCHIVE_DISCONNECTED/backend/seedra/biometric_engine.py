"""
Biometric Engine - Advanced biometric processing for SEEDRA
Handles facial recognition, voice prints, and other biometric data
"""

import base64
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class BiometricTemplate:
    """Represents a biometric template"""

    user_id: str
    biometric_type: str  # face, voice, fingerprint, etc.
    template_data: str  # Encrypted/hashed template
    quality_score: float
    created_at: datetime
    last_used: datetime = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BiometricMatch:
    """Result of biometric matching"""

    template_id: str
    confidence: float
    match_quality: float
    processing_time: float
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class BiometricEngine:
    """Advanced biometric processing engine"""

    def __init__(self):
        self.templates: Dict[str, List[BiometricTemplate]] = {}
        self.match_threshold = 0.8
        self.quality_threshold = 0.6
        self.max_templates_per_user = 3
        self.supported_types = ["face", "voice", "fingerprint", "iris"]

    async def enroll_biometric(
        self, user_id: str, biometric_type: str, raw_data: bytes, metadata: Dict = None
    ) -> Dict:
        """Enroll biometric data for a user"""
        try:
            if biometric_type not in self.supported_types:
                return {
                    "success": False,
                    "reason": f"Unsupported biometric type: {biometric_type}",
                }

            # Process raw biometric data
            processing_result = await self._process_biometric_data(
                biometric_type, raw_data
            )

            if not processing_result["success"]:
                return processing_result

            quality_score = processing_result["quality_score"]
            if quality_score < self.quality_threshold:
                return {
                    "success": False,
                    "reason": "Biometric quality too low",
                    "quality_score": quality_score,
                }

            # Create template
            template = BiometricTemplate(
                user_id=user_id,
                biometric_type=biometric_type,
                template_data=processing_result["template_data"],
                quality_score=quality_score,
                created_at=datetime.utcnow(),
                metadata=metadata or {},
            )

            # Store template
            if user_id not in self.templates:
                self.templates[user_id] = []

            # Limit number of templates per user
            user_templates = [
                t for t in self.templates[user_id] if t.biometric_type == biometric_type
            ]
            if len(user_templates) >= self.max_templates_per_user:
                # Remove oldest template
                oldest = min(user_templates, key=lambda t: t.created_at)
                self.templates[user_id].remove(oldest)

            self.templates[user_id].append(template)

            logger.info(f"Enrolled {biometric_type} biometric for user {user_id}")

            return {
                "success": True,
                "template_id": f"{user_id}_{biometric_type}_{len(self.templates[user_id])}",
                "quality_score": quality_score,
            }

        except Exception as e:
            logger.error(f"Biometric enrollment failed: {e}")
            return {"success": False, "reason": str(e)}

    async def verify_biometric(
        self, user_id: str, biometric_type: str, raw_data: bytes
    ) -> Dict:
        """Verify biometric data against enrolled templates"""
        try:
            start_time = datetime.utcnow()

            if user_id not in self.templates:
                return {
                    "success": False,
                    "reason": "No biometric templates found for user",
                }

            # Process input biometric data
            processing_result = await self._process_biometric_data(
                biometric_type, raw_data
            )

            if not processing_result["success"]:
                return processing_result

            input_template = processing_result["template_data"]
            quality_score = processing_result["quality_score"]

            # Find matching templates
            user_templates = [
                t for t in self.templates[user_id] if t.biometric_type == biometric_type
            ]

            if not user_templates:
                return {
                    "success": False,
                    "reason": f"No {biometric_type} templates found for user",
                }

            # Match against all templates
            best_match = None
            best_confidence = 0.0

            for template in user_templates:
                match_result = await self._match_templates(
                    biometric_type, input_template, template.template_data
                )

                if match_result["confidence"] > best_confidence:
                    best_confidence = match_result["confidence"]
                    best_match = BiometricMatch(
                        template_id=f"{user_id}_{biometric_type}",
                        confidence=match_result["confidence"],
                        match_quality=min(quality_score, template.quality_score),
                        processing_time=(
                            datetime.utcnow() - start_time
                        ).total_seconds(),
                        details=match_result.get("details", {}),
                    )

                # Update template usage
                template.last_used = datetime.utcnow()

            success = best_confidence >= self.match_threshold

            return {
                "success": success,
                "confidence": best_confidence,
                "match": best_match.__dict__ if best_match else None,
                "quality_score": quality_score,
            }

        except Exception as e:
            logger.error(f"Biometric verification failed: {e}")
            return {"success": False, "reason": str(e)}

    async def _process_biometric_data(
        self, biometric_type: str, raw_data: bytes
    ) -> Dict:
        """Process raw biometric data into template"""
        try:
            if biometric_type == "face":
                return await self._process_face_data(raw_data)
            elif biometric_type == "voice":
                return await self._process_voice_data(raw_data)
            elif biometric_type == "fingerprint":
                return await self._process_fingerprint_data(raw_data)
            elif biometric_type == "iris":
                return await self._process_iris_data(raw_data)
            else:
                return {"success": False, "reason": "Unsupported biometric type"}

        except Exception as e:
            logger.error(f"Biometric processing failed: {e}")
            return {"success": False, "reason": str(e)}

    async def _process_face_data(self, raw_data: bytes) -> Dict:
        """Process facial biometric data"""
        try:
            # Simulate face detection and feature extraction
            # In production, use libraries like OpenCV, dlib, or commercial SDKs

            # Basic quality checks
            if len(raw_data) < 1000:  # Too small for face image
                return {"success": False, "reason": "Image too small"}

            # Simulate feature extraction
            face_hash = hashlib.sha256(raw_data).hexdigest()

            # Simulate quality scoring based on image characteristics
            quality_score = min(1.0, len(raw_data) / 50000)  # Simple heuristic

            # Create template (in production, this would be actual face embeddings)
            template_data = base64.b64encode(face_hash.encode()).decode()

            return {
                "success": True,
                "template_data": template_data,
                "quality_score": quality_score,
                "features_detected": ["eyes", "nose", "mouth"],  # Simulated
            }

        except Exception as e:
            return {"success": False, "reason": f"Face processing error: {e}"}

    async def _process_voice_data(self, raw_data: bytes) -> Dict:
        """Process voice biometric data"""
        try:
            # Simulate voice processing
            # In production, use audio processing libraries

            if len(raw_data) < 5000:  # Too short for voice sample
                return {"success": False, "reason": "Audio sample too short"}

            # Simulate voice feature extraction
            voice_hash = hashlib.sha256(raw_data).hexdigest()

            # Quality based on sample length and characteristics
            quality_score = min(1.0, len(raw_data) / 100000)

            template_data = base64.b64encode(voice_hash.encode()).decode()

            return {
                "success": True,
                "template_data": template_data,
                "quality_score": quality_score,
                "features_detected": ["pitch", "formants", "spectral"],  # Simulated
            }

        except Exception as e:
            return {"success": False, "reason": f"Voice processing error: {e}"}

    async def _process_fingerprint_data(self, raw_data: bytes) -> Dict:
        """Process fingerprint biometric data"""
        try:
            # Simulate fingerprint processing
            if len(raw_data) < 2000:
                return {"success": False, "reason": "Fingerprint image too small"}

            fingerprint_hash = hashlib.sha256(raw_data).hexdigest()
            quality_score = min(1.0, len(raw_data) / 30000)

            template_data = base64.b64encode(fingerprint_hash.encode()).decode()

            return {
                "success": True,
                "template_data": template_data,
                "quality_score": quality_score,
                "features_detected": ["minutiae", "ridges"],  # Simulated
            }

        except Exception as e:
            return {"success": False, "reason": f"Fingerprint processing error: {e}"}

    async def _process_iris_data(self, raw_data: bytes) -> Dict:
        """Process iris biometric data"""
        try:
            # Simulate iris processing
            if len(raw_data) < 3000:
                return {"success": False, "reason": "Iris image too small"}

            iris_hash = hashlib.sha256(raw_data).hexdigest()
            quality_score = min(1.0, len(raw_data) / 40000)

            template_data = base64.b64encode(iris_hash.encode()).decode()

            return {
                "success": True,
                "template_data": template_data,
                "quality_score": quality_score,
                "features_detected": ["iris_pattern", "pupil_boundary"],  # Simulated
            }

        except Exception as e:
            return {"success": False, "reason": f"Iris processing error: {e}"}

    async def _match_templates(
        self, biometric_type: str, template1: str, template2: str
    ) -> Dict:
        """Match two biometric templates"""
        try:
            # Simulate template matching
            # In production, use appropriate matching algorithms

            # Simple hash comparison for demo
            if template1 == template2:
                confidence = 0.95
            else:
                # Simulate partial matching based on string similarity
                template1_bytes = base64.b64decode(template1.encode())
                template2_bytes = base64.b64decode(template2.encode())

                # Simple similarity metric
                common_chars = sum(
                    1 for a, b in zip(template1_bytes, template2_bytes) if a == b
                )
                total_chars = max(len(template1_bytes), len(template2_bytes))

                confidence = common_chars / total_chars if total_chars > 0 else 0.0

            # Add some randomness for more realistic simulation
            import random

            confidence = max(0.0, min(1.0, confidence + random.uniform(-0.1, 0.1)))

            return {
                "confidence": confidence,
                "details": {
                    "algorithm": f"{biometric_type}_matcher_v1",
                    "comparison_method": "feature_vector_similarity",
                },
            }

        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return {"confidence": 0.0, "error": str(e)}

    async def get_user_biometrics(self, user_id: str) -> Dict:
        """Get summary of user's enrolled biometrics"""
        if user_id not in self.templates:
            return {"enrolled_biometrics": []}

        templates = self.templates[user_id]
        biometric_summary = {}

        for template in templates:
            bio_type = template.biometric_type
            if bio_type not in biometric_summary:
                biometric_summary[bio_type] = {
                    "count": 0,
                    "best_quality": 0.0,
                    "last_used": None,
                }

            biometric_summary[bio_type]["count"] += 1
            biometric_summary[bio_type]["best_quality"] = max(
                biometric_summary[bio_type]["best_quality"], template.quality_score
            )

            if template.last_used and (
                not biometric_summary[bio_type]["last_used"]
                or template.last_used > biometric_summary[bio_type]["last_used"]
            ):
                biometric_summary[bio_type]["last_used"] = template.last_used

        return {
            "user_id": user_id,
            "enrolled_biometrics": list(biometric_summary.keys()),
            "biometric_details": biometric_summary,
            "total_templates": len(templates),
        }

    async def remove_biometric(self, user_id: str, biometric_type: str) -> bool:
        """Remove all biometric templates of a specific type for a user"""
        try:
            if user_id not in self.templates:
                return False

            original_count = len(self.templates[user_id])
            self.templates[user_id] = [
                t for t in self.templates[user_id] if t.biometric_type != biometric_type
            ]

            removed_count = original_count - len(self.templates[user_id])

            if removed_count > 0:
                logger.info(
                    f"Removed {removed_count} {biometric_type} templates for user {user_id}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to remove biometric: {e}")
            return False

    async def update_match_threshold(self, new_threshold: float) -> bool:
        """Update the matching threshold"""
        try:
            if 0.0 <= new_threshold <= 1.0:
                self.match_threshold = new_threshold
                logger.info(f"Updated match threshold to {new_threshold}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update match threshold: {e}")
            return False

    async def get_system_stats(self) -> Dict:
        """Get biometric system statistics"""
        total_users = len(self.templates)
        total_templates = sum(len(templates) for templates in self.templates.values())

        type_counts = {}
        for templates in self.templates.values():
            for template in templates:
                bio_type = template.biometric_type
                type_counts[bio_type] = type_counts.get(bio_type, 0) + 1

        return {
            "total_users": total_users,
            "total_templates": total_templates,
            "templates_by_type": type_counts,
            "supported_types": self.supported_types,
            "match_threshold": self.match_threshold,
            "quality_threshold": self.quality_threshold,
        }
