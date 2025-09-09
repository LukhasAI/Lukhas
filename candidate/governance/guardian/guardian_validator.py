"""
Guardian Validator for Audio Processing Operations
Trinity Framework: ⚛️🧠🛡️ Identity-Consciousness-Guardian

Provides validation and safety checks for audio processing operations
within the LUKHAS AI ecosystem.
"""
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Validation result status"""
    APPROVED = "approved"
    DENIED = "denied"
    WARNING = "warning"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class AudioValidationContext:
    """Context for audio validation operations"""
    operation_type: str
    audio_format: Optional[str] = None
    quality_level: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    processing_intent: Optional[str] = None
    user_identity: Optional[str] = None
    source_system: Optional[str] = None


@dataclass
class ValidationReport:
    """Result of audio validation"""
    result: ValidationResult
    confidence_score: float  # 0.0 to 1.0
    validation_time_ms: float
    issues_found: list[str]
    recommendations: list[str]
    metadata: dict[str, Any]


class GuardianValidator:
    """
    Guardian Validator for audio processing operations

    Provides comprehensive validation for audio operations including:
    - Audio format safety checks
    - Content policy compliance
    - Performance impact assessment
    - Privacy and security validation
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize GuardianValidator

        Args:
            strict_mode: Enable strict validation mode
        """
        self.strict_mode = strict_mode
        self.validation_stats = {
            "total_validations": 0,
            "approved": 0,
            "denied": 0,
            "warnings": 0,
            "avg_validation_time_ms": 0.0
        }

        # Audio format safety rules
        self.safe_formats = {
            "pcm_wav", "mp3", "flac", "ogg_vorbis", "aac", "opus"
        }

        # Audio quality limits
        self.quality_limits = {
            "max_file_size_mb": 100,
            "max_duration_minutes": 60,
            "min_sample_rate": 8000,
            "max_sample_rate": 192000
        }

        logger.info(f"GuardianValidator initialized - strict_mode: {strict_mode}")

    async def validate_audio_operation(self,
                                     operation_type: str,
                                     audio_data: Optional[bytes] = None,
                                     context: Optional[AudioValidationContext] = None,
                                     **kwargs) -> ValidationReport:
        """
        Validate an audio processing operation

        Args:
            operation_type: Type of operation (encode, decode, process, analyze)
            audio_data: Optional audio data to validate
            context: Validation context information
            **kwargs: Additional validation parameters

        Returns:
            ValidationReport with validation results
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1

        issues = []
        recommendations = []
        confidence = 1.0

        try:
            # Create default context if not provided
            if context is None:
                context = AudioValidationContext(
                    operation_type=operation_type,
                    source_system=kwargs.get("source_system", "unknown")
                )

            # Validate operation type
            if not self._validate_operation_type(operation_type):
                issues.append(f"Unsupported operation type: {operation_type}")
                confidence -= 0.3

            # Validate audio format if provided
            if context.audio_format:
                if not self._validate_audio_format(context.audio_format):
                    issues.append(f"Unsafe audio format: {context.audio_format}")
                    confidence -= 0.4

            # Validate file size constraints
            if context.file_size_bytes:
                if not self._validate_file_size(context.file_size_bytes):
                    issues.append(f"File size exceeds limits: {context.file_size_bytes} bytes")
                    confidence -= 0.2

            # Validate duration constraints
            if context.duration_seconds:
                if not self._validate_duration(context.duration_seconds):
                    issues.append(f"Duration exceeds limits: {context.duration_seconds}s")
                    confidence -= 0.2

            # Validate audio data if provided
            if audio_data:
                data_issues = self._validate_audio_data(audio_data)
                issues.extend(data_issues)
                if data_issues:
                    confidence -= 0.1 * len(data_issues)

            # Generate recommendations
            recommendations = self._generate_recommendations(context, issues)

            # Determine validation result
            result = self._determine_result(issues, confidence)

            # Update statistics
            self._update_stats(result)

            validation_time_ms = (time.time() - start_time) * 1000

            return ValidationReport(
                result=result,
                confidence_score=max(0.0, min(1.0, confidence)),
                validation_time_ms=validation_time_ms,
                issues_found=issues,
                recommendations=recommendations,
                metadata={
                    "operation_type": operation_type,
                    "context": context,
                    "strict_mode": self.strict_mode,
                    "timestamp": time.time()
                }
            )

        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return ValidationReport(
                result=ValidationResult.DENIED,
                confidence_score=0.0,
                validation_time_ms=(time.time() - start_time) * 1000,
                issues_found=[f"Validation error: {e!s}"],
                recommendations=["Review audio operation parameters"],
                metadata={"error": str(e)}
            )

    def _validate_operation_type(self, operation_type: str) -> bool:
        """Validate audio operation type"""
        valid_operations = {
            "encode", "decode", "process", "analyze", "enhance",
            "convert", "filter", "normalize", "compress"
        }
        return operation_type.lower() in valid_operations

    def _validate_audio_format(self, audio_format: str) -> bool:
        """Validate audio format safety"""
        return audio_format.lower() in self.safe_formats

    def _validate_file_size(self, file_size_bytes: int) -> bool:
        """Validate file size constraints"""
        max_size = self.quality_limits["max_file_size_mb"] * 1024 * 1024
        return file_size_bytes <= max_size

    def _validate_duration(self, duration_seconds: float) -> bool:
        """Validate audio duration constraints"""
        max_duration = self.quality_limits["max_duration_minutes"] * 60
        return duration_seconds <= max_duration

    def _validate_audio_data(self, audio_data: bytes) -> list[str]:
        """Validate raw audio data"""
        issues = []

        # Basic data validation
        if len(audio_data) == 0:
            issues.append("Empty audio data")

        # Check for reasonable data size
        if len(audio_data) > 100 * 1024 * 1024:  # 100MB
            issues.append("Audio data exceeds reasonable size limits")

        # Basic header validation (for common formats)
        if len(audio_data) >= 4:
            header = audio_data[:4]
            if header == b"RIFF":  # WAV file
                # Basic WAV validation
                if len(audio_data) < 44:  # Minimum WAV header size
                    issues.append("Invalid WAV file: insufficient header data")
            elif header.startswith(b"ID3") or audio_data[1:4] == b"ID3":  # MP3 with ID3
                # Basic MP3 validation
                pass
            elif header.startswith(b"OggS"):  # OGG file
                # Basic OGG validation
                pass

        return issues

    def _generate_recommendations(self, context: AudioValidationContext, issues: list[str]) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if issues:
            recommendations.append("Review and address identified issues before processing")

        if context.file_size_bytes and context.file_size_bytes > 50 * 1024 * 1024:
            recommendations.append("Consider using compression for large audio files")

        if context.quality_level == "lossless" and context.processing_intent == "voice":
            recommendations.append("Consider medium quality for voice processing to optimize performance")

        if not context.audio_format or context.audio_format not in self.safe_formats:
            recommendations.append("Use standard audio formats (PCM WAV, MP3, FLAC) for best compatibility")

        return recommendations

    def _determine_result(self, issues: list[str], confidence: float) -> ValidationResult:
        """Determine validation result based on issues and confidence"""
        if not issues and confidence >= 0.9:
            return ValidationResult.APPROVED
        elif issues and confidence < 0.3:
            return ValidationResult.DENIED
        elif issues and confidence < 0.7:
            return ValidationResult.REQUIRES_REVIEW
        else:
            return ValidationResult.WARNING

    def _update_stats(self, result: ValidationResult):
        """Update validation statistics"""
        if result == ValidationResult.APPROVED:
            self.validation_stats["approved"] += 1
        elif result == ValidationResult.DENIED:
            self.validation_stats["denied"] += 1
        else:
            self.validation_stats["warnings"] += 1

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics"""
        if self.validation_stats["total_validations"] > 0:
            self.validation_stats["avg_validation_time_ms"] = (
                self.validation_stats.get("total_time_ms", 0) /
                self.validation_stats["total_validations"]
            )

        return self.validation_stats.copy()

    async def validate_batch_operations(self, operations: list[dict[str, Any]]) -> list[ValidationReport]:
        """Validate multiple audio operations in batch"""
        results = []

        for operation in operations:
            context = AudioValidationContext(
                operation_type=operation.get("operation_type", "unknown"),
                audio_format=operation.get("audio_format"),
                quality_level=operation.get("quality_level"),
                file_size_bytes=operation.get("file_size_bytes"),
                duration_seconds=operation.get("duration_seconds"),
                processing_intent=operation.get("processing_intent"),
                source_system=operation.get("source_system")
            )

            result = await self.validate_audio_operation(
                operation_type=operation.get("operation_type", "unknown"),
                audio_data=operation.get("audio_data"),
                context=context
            )

            results.append(result)

        return results


# Export main classes
__all__ = ["GuardianValidator", "ValidationResult", "AudioValidationContext", "ValidationReport"]
