"""
LUKHAS AI Voice Quality Analytics System
Comprehensive voice quality analysis and metrics with Trinity Framework integration.
⚛️ Identity-aware quality assessment
🧠 Consciousness-driven quality optimization
🛡️ Guardian-validated quality monitoring
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from lukhas.core.common.glyph import GLYPHSymbol, create_glyph
from lukhas.core.common.logger import get_logger
from lukhas.governance.guardian import GuardianValidator
from lukhas.voice.audio_processing import AudioBuffer, AudioFormat

logger = get_logger(__name__)


class VoiceQualityMetric(Enum):
    """Voice quality metrics"""

    SIGNAL_TO_NOISE_RATIO = "snr"
    TOTAL_HARMONIC_DISTORTION = "thd"
    DYNAMIC_RANGE = "dynamic_range"
    FREQUENCY_RESPONSE = "frequency_response"
    SPECTRAL_CENTROID = "spectral_centroid"
    SPECTRAL_ROLLOFF = "spectral_rolloff"
    ZERO_CROSSING_RATE = "zero_crossing_rate"
    FUNDAMENTAL_FREQUENCY = "fundamental_frequency"
    JITTER = "jitter"
    SHIMMER = "shimmer"
    HARMONICS_TO_NOISE_RATIO = "hnr"
    VOICE_ACTIVITY_DETECTION = "vad"
    PITCH_STABILITY = "pitch_stability"
    FORMANT_ANALYSIS = "formant_analysis"
    SPEECH_RATE = "speech_rate"
    PAUSE_ANALYSIS = "pause_analysis"
    EMOTIONAL_PROSODY = "emotional_prosody"
    INTELLIGIBILITY_SCORE = "intelligibility"


class QualityGrade(Enum):
    """Quality grades"""

    EXCELLENT = "excellent"  # 90-100%
    VERY_GOOD = "very_good"  # 80-89%
    GOOD = "good"  # 70-79%
    FAIR = "fair"  # 60-69%
    POOR = "poor"  # 50-59%
    VERY_POOR = "very_poor"  # <50%


@dataclass
class VoiceQualityScore:
    """Voice quality score for a specific metric"""

    metric: VoiceQualityMetric
    value: float
    unit: str
    grade: QualityGrade
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric": self.metric.value,
            "value": self.value,
            "unit": self.unit,
            "grade": self.grade.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class VoiceQualityReport:
    """Comprehensive voice quality report"""

    overall_score: float
    overall_grade: QualityGrade

    # Individual metric scores
    scores: dict[VoiceQualityMetric, VoiceQualityScore] = field(default_factory=dict)

    # Audio characteristics
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    channels: int = 1
    format: AudioFormat = AudioFormat.PCM_16

    # Analysis metadata
    analysis_time_ms: float = 0.0
    algorithms_used: list[str] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    issues_detected: list[str] = field(default_factory=list)

    # Context information
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "overall_score": self.overall_score,
            "overall_grade": self.overall_grade.value,
            "scores": {metric.value: score.to_dict() for metric, score in self.scores.items()},
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format.value,
            "analysis_time_ms": self.analysis_time_ms,
            "algorithms_used": self.algorithms_used,
            "recommendations": self.recommendations,
            "issues_detected": self.issues_detected,
            "context": self.context,
        }


class VoiceQualityAnalyzer(ABC):
    """Abstract base class for voice quality analyzers"""

    @abstractmethod
    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Analyze voice quality for specific metric"""
        pass

    @abstractmethod
    def get_metric_type(self) -> VoiceQualityMetric:
        """Get the metric this analyzer handles"""
        pass


class SNRAnalyzer(VoiceQualityAnalyzer):
    """Signal-to-Noise Ratio analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate SNR"""
        data = buffer.data

        # Estimate signal and noise
        # Simple method: assume top 10% of energy is signal, bottom 10% is noise
        energy = data**2
        sorted_energy = np.sort(energy)

        signal_energy = np.mean(sorted_energy[-int(0.1 * len(sorted_energy)) :])
        noise_energy = np.mean(sorted_energy[: int(0.1 * len(sorted_energy))])

        if noise_energy == 0:
            snr_db = 60.0  # Very high SNR
        else:
            snr_db = 10 * np.log10(signal_energy / noise_energy)

        # Grade based on SNR
        if snr_db >= 40:
            grade = QualityGrade.EXCELLENT
        elif snr_db >= 30:
            grade = QualityGrade.VERY_GOOD
        elif snr_db >= 20:
            grade = QualityGrade.GOOD
        elif snr_db >= 15:
            grade = QualityGrade.FAIR
        elif snr_db >= 10:
            grade = QualityGrade.POOR
        else:
            grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO,
            value=float(snr_db),
            unit="dB",
            grade=grade,
            metadata={
                "signal_energy": float(signal_energy),
                "noise_energy": float(noise_energy),
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO


class THDAnalyzer(VoiceQualityAnalyzer):
    """Total Harmonic Distortion analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate THD"""
        data = buffer.data
        sample_rate = buffer.sample_rate

        # FFT analysis
        fft = np.fft.rfft(data)
        magnitude = np.abs(fft)
        frequencies = np.fft.rfftfreq(len(data), 1 / sample_rate)

        # Find fundamental frequency (peak in 80-800 Hz range)
        f0_range = (frequencies >= 80) & (frequencies <= 800)
        if np.any(f0_range):
            f0_idx = np.argmax(magnitude[f0_range])
            f0 = frequencies[f0_range][f0_idx]

            # Calculate harmonic energy
            fundamental_energy = magnitude[f0_range][f0_idx] ** 2

            # Find harmonics (2f0, 3f0, etc.)
            harmonic_energy = 0.0
            for harmonic in range(2, 6):  # Up to 5th harmonic
                h_freq = harmonic * f0
                if h_freq < frequencies[-1]:
                    h_idx = np.argmin(np.abs(frequencies - h_freq))
                    harmonic_energy += magnitude[h_idx] ** 2

            # Calculate THD
            if fundamental_energy > 0:
                thd = np.sqrt(harmonic_energy / fundamental_energy)
                thd_percent = thd * 100
            else:
                thd_percent = 50.0  # High distortion if no fundamental
        else:
            thd_percent = 50.0  # High distortion if no fundamental found

        # Grade based on THD
        if thd_percent <= 1.0:
            grade = QualityGrade.EXCELLENT
        elif thd_percent <= 3.0:
            grade = QualityGrade.VERY_GOOD
        elif thd_percent <= 5.0:
            grade = QualityGrade.GOOD
        elif thd_percent <= 10.0:
            grade = QualityGrade.FAIR
        elif thd_percent <= 20.0:
            grade = QualityGrade.POOR
        else:
            grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION,
            value=float(thd_percent),
            unit="%",
            grade=grade,
            metadata={
                "fundamental_frequency": float(f0) if "f0" in locals() else None,
                "fundamental_energy": (float(fundamental_energy) if "fundamental_energy" in locals() else None),
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION


class DynamicRangeAnalyzer(VoiceQualityAnalyzer):
    """Dynamic range analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate dynamic range"""
        data = buffer.data

        # Calculate RMS in sliding windows
        window_size = 2048
        hop_size = 512

        rms_values = []
        for i in range(0, len(data) - window_size, hop_size):
            window = data[i : i + window_size]
            rms = np.sqrt(np.mean(window**2))
            if rms > 0:
                rms_values.append(rms)

        if len(rms_values) < 2:
            dynamic_range_db = 20.0  # Default moderate range
        else:
            rms_values = np.array(rms_values)
            max_rms = np.max(rms_values)
            min_rms = np.min(rms_values[rms_values > 0])

            dynamic_range_db = 20 * np.log10(max_rms / min_rms) if min_rms > 0 else 20.0

        # Grade based on dynamic range
        if dynamic_range_db >= 60:
            grade = QualityGrade.EXCELLENT
        elif dynamic_range_db >= 40:
            grade = QualityGrade.VERY_GOOD
        elif dynamic_range_db >= 25:
            grade = QualityGrade.GOOD
        elif dynamic_range_db >= 15:
            grade = QualityGrade.FAIR
        elif dynamic_range_db >= 10:
            grade = QualityGrade.POOR
        else:
            grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.DYNAMIC_RANGE,
            value=float(dynamic_range_db),
            unit="dB",
            grade=grade,
            metadata={
                "max_rms": float(max_rms) if "max_rms" in locals() else None,
                "min_rms": float(min_rms) if "min_rms" in locals() else None,
                "rms_windows": len(rms_values),
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.DYNAMIC_RANGE


class SpectralCentroidAnalyzer(VoiceQualityAnalyzer):
    """Spectral centroid analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate spectral centroid"""
        data = buffer.data
        sample_rate = buffer.sample_rate

        # FFT analysis
        fft = np.fft.rfft(data)
        magnitude = np.abs(fft)
        frequencies = np.fft.rfftfreq(len(data), 1 / sample_rate)

        # Calculate spectral centroid
        if np.sum(magnitude) > 0:
            spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)
        else:
            spectral_centroid = sample_rate / 4  # Default to quarter Nyquist

        # Grade based on spectral centroid for voice
        # Good voice quality typically has centroid around 1-3 kHz
        if 1000 <= spectral_centroid <= 3000:
            grade = QualityGrade.EXCELLENT
        elif 800 <= spectral_centroid <= 4000:
            grade = QualityGrade.VERY_GOOD
        elif 600 <= spectral_centroid <= 5000:
            grade = QualityGrade.GOOD
        elif 400 <= spectral_centroid <= 6000:
            grade = QualityGrade.FAIR
        elif 200 <= spectral_centroid <= 8000:
            grade = QualityGrade.POOR
        else:
            grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.SPECTRAL_CENTROID,
            value=float(spectral_centroid),
            unit="Hz",
            grade=grade,
            metadata={
                "spectral_energy": float(np.sum(magnitude)),
                "frequency_range": [float(frequencies[0]), float(frequencies[-1])],
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.SPECTRAL_CENTROID


class ZeroCrossingRateAnalyzer(VoiceQualityAnalyzer):
    """Zero crossing rate analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate zero crossing rate"""
        data = buffer.data
        sample_rate = buffer.sample_rate

        # Calculate zero crossings
        zero_crossings = np.sum(np.diff(np.sign(data)) != 0)
        zcr = zero_crossings / len(data) * sample_rate / 2  # Normalize to Hz

        # Grade based on ZCR for voice
        # Voice typically has ZCR around 50-200 Hz
        if 50 <= zcr <= 200:
            grade = QualityGrade.EXCELLENT
        elif 30 <= zcr <= 300:
            grade = QualityGrade.VERY_GOOD
        elif 20 <= zcr <= 400:
            grade = QualityGrade.GOOD
        elif 10 <= zcr <= 500:
            grade = QualityGrade.FAIR
        elif 5 <= zcr <= 700:
            grade = QualityGrade.POOR
        else:
            grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.ZERO_CROSSING_RATE,
            value=float(zcr),
            unit="Hz",
            grade=grade,
            metadata={
                "total_zero_crossings": int(zero_crossings),
                "samples": len(data),
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.ZERO_CROSSING_RATE


class PitchStabilityAnalyzer(VoiceQualityAnalyzer):
    """Pitch stability analyzer"""

    async def analyze(self, buffer: AudioBuffer) -> VoiceQualityScore:
        """Calculate pitch stability"""
        data = buffer.data
        sample_rate = buffer.sample_rate

        # Frame-based pitch extraction
        frame_size = 2048
        hop_size = 512

        pitches = []
        for i in range(0, len(data) - frame_size, hop_size):
            frame = data[i : i + frame_size]

            # Autocorrelation-based pitch detection
            autocorr = np.correlate(frame, frame, mode="full")
            autocorr = autocorr[len(autocorr) // 2 :]

            # Find peak in pitch range (80-800 Hz)
            min_period = int(sample_rate / 800)
            max_period = int(sample_rate / 80)

            if max_period < len(autocorr):
                search_range = autocorr[min_period:max_period]
                if len(search_range) > 0:
                    peak_idx = np.argmax(search_range) + min_period
                    if autocorr[peak_idx] > 0.3 * autocorr[0]:  # Significant peak
                        pitch = sample_rate / peak_idx
                        pitches.append(pitch)

        if len(pitches) < 3:
            # Not enough pitch data
            stability_score = 50.0
            grade = QualityGrade.FAIR
        else:
            pitches = np.array(pitches)

            # Calculate pitch stability (coefficient of variation)
            pitch_std = np.std(pitches)
            pitch_mean = np.mean(pitches)

            if pitch_mean > 0:
                cv = pitch_std / pitch_mean
                stability_score = max(0, 100 * (1 - cv * 10))  # Convert to 0-100 scale
            else:
                stability_score = 0.0

            # Grade based on stability
            if stability_score >= 90:
                grade = QualityGrade.EXCELLENT
            elif stability_score >= 80:
                grade = QualityGrade.VERY_GOOD
            elif stability_score >= 70:
                grade = QualityGrade.GOOD
            elif stability_score >= 60:
                grade = QualityGrade.FAIR
            elif stability_score >= 50:
                grade = QualityGrade.POOR
            else:
                grade = QualityGrade.VERY_POOR

        return VoiceQualityScore(
            metric=VoiceQualityMetric.PITCH_STABILITY,
            value=float(stability_score),
            unit="%",
            grade=grade,
            metadata={
                "pitch_frames": len(pitches),
                "mean_pitch": float(np.mean(pitches)) if len(pitches) > 0 else None,
                "pitch_std": float(np.std(pitches)) if len(pitches) > 0 else None,
            },
        )

    def get_metric_type(self) -> VoiceQualityMetric:
        return VoiceQualityMetric.PITCH_STABILITY


class LUKHASVoiceAnalytics:
    """Main LUKHAS voice analytics engine"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.LUKHASVoiceAnalytics")
        self.guardian = GuardianValidator()

        # Initialize analyzers
        self.analyzers = {
            VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO: SNRAnalyzer(),
            VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION: THDAnalyzer(),
            VoiceQualityMetric.DYNAMIC_RANGE: DynamicRangeAnalyzer(),
            VoiceQualityMetric.SPECTRAL_CENTROID: SpectralCentroidAnalyzer(),
            VoiceQualityMetric.ZERO_CROSSING_RATE: ZeroCrossingRateAnalyzer(),
            VoiceQualityMetric.PITCH_STABILITY: PitchStabilityAnalyzer(),
        }

        # Quality thresholds for overall grading
        self.grade_weights = {
            VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO: 0.25,
            VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION: 0.20,
            VoiceQualityMetric.DYNAMIC_RANGE: 0.15,
            VoiceQualityMetric.SPECTRAL_CENTROID: 0.10,
            VoiceQualityMetric.ZERO_CROSSING_RATE: 0.10,
            VoiceQualityMetric.PITCH_STABILITY: 0.20,
        }

        # Analysis statistics
        self.stats = {
            "analyses_performed": 0,
            "average_analysis_time": 0.0,
            "quality_distribution": {grade.value: 0 for grade in QualityGrade},
        }

        self.logger.info("LUKHAS Voice Analytics initialized")

    async def analyze_voice_quality(
        self,
        audio_data: bytes,
        sample_rate: int = 44100,
        channels: int = 1,
        format: AudioFormat = AudioFormat.PCM_16,
        metrics: Optional[list[VoiceQualityMetric]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> VoiceQualityReport:
        """
        Analyze voice quality comprehensively

        Args:
            audio_data: Audio data as bytes
            sample_rate: Audio sample rate
            channels: Number of channels
            format: Audio format
            metrics: Specific metrics to analyze (all if None)
            context: Analysis context

        Returns:
            Voice quality report
        """
        start_time = time.time()
        self.stats["analyses_performed"] += 1

        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "voice_quality_analysis",
                    "audio_length": len(audio_data),
                    "context": context or {},
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected analysis: {validation_result.get('reason')}")

            # Convert audio data to AudioBuffer
            if format == AudioFormat.PCM_16:
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            elif format == AudioFormat.FLOAT_32:
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
            else:
                raise ValueError(f"Unsupported audio format: {format}")

            buffer = AudioBuffer(
                data=audio_array,
                sample_rate=sample_rate,
                channels=channels,
                format=format,
            )

            # Select metrics to analyze
            if metrics is None:
                metrics_to_analyze = list(self.analyzers.keys())
            else:
                metrics_to_analyze = [m for m in metrics if m in self.analyzers]

            # Run analyses
            scores = {}
            algorithms_used = []

            for metric in metrics_to_analyze:
                try:
                    analyzer = self.analyzers[metric]
                    score = await analyzer.analyze(buffer)
                    scores[metric] = score
                    algorithms_used.append(metric.value)
                except Exception as e:
                    self.logger.warning(f"Analysis failed for {metric.value}: {e!s}")

            # Calculate overall score
            overall_score, overall_grade = self._calculate_overall_quality(scores)

            # Generate recommendations
            recommendations = self._generate_recommendations(scores)
            issues_detected = self._detect_issues(scores)

            # Create report
            report = VoiceQualityReport(
                overall_score=overall_score,
                overall_grade=overall_grade,
                scores=scores,
                duration_seconds=len(audio_array) / sample_rate,
                sample_rate=sample_rate,
                channels=channels,
                format=format,
                analysis_time_ms=(time.time() - start_time) * 1000,
                algorithms_used=algorithms_used,
                recommendations=recommendations,
                issues_detected=issues_detected,
                context=context or {},
            )

            # Update statistics
            self.stats["quality_distribution"][overall_grade.value] += 1
            self.stats["average_analysis_time"] = (
                self.stats["average_analysis_time"] * (self.stats["analyses_performed"] - 1) + report.analysis_time_ms
            ) / self.stats["analyses_performed"]

            # Emit GLYPH event
            glyph_token = create_glyph(
                GLYPHSymbol.CREATE,
                "voice_pipeline",
                "consciousness",
                {
                    "event_type": "voice.quality.analyzed",
                    "overall_score": overall_score,
                    "overall_grade": overall_grade.value,
                    "metrics_analyzed": len(scores),
                    "analysis_time_ms": report.analysis_time_ms,
                    "audio_duration": report.duration_seconds,
                },
            )

            return report

        except Exception as e:
            self.logger.error(f"Voice quality analysis failed: {e!s}")

            # Return minimal report with error
            return VoiceQualityReport(
                overall_score=0.0,
                overall_grade=QualityGrade.VERY_POOR,
                analysis_time_ms=(time.time() - start_time) * 1000,
                issues_detected=[f"Analysis failed: {e!s}"],
                context=context or {},
            )

    def _calculate_overall_quality(
        self, scores: dict[VoiceQualityMetric, VoiceQualityScore]
    ) -> tuple[float, QualityGrade]:
        """Calculate overall quality score and grade"""
        if not scores:
            return 0.0, QualityGrade.VERY_POOR

        # Convert grades to numeric values
        grade_values = {
            QualityGrade.EXCELLENT: 95,
            QualityGrade.VERY_GOOD: 85,
            QualityGrade.GOOD: 75,
            QualityGrade.FAIR: 65,
            QualityGrade.POOR: 55,
            QualityGrade.VERY_POOR: 25,
        }

        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0

        for metric, score in scores.items():
            weight = self.grade_weights.get(metric, 0.1)
            value = grade_values[score.grade]
            weighted_sum += value * weight
            total_weight += weight

        overall_score = 0.0 if total_weight == 0 else weighted_sum / total_weight

        # Convert score to grade
        if overall_score >= 90:
            overall_grade = QualityGrade.EXCELLENT
        elif overall_score >= 80:
            overall_grade = QualityGrade.VERY_GOOD
        elif overall_score >= 70:
            overall_grade = QualityGrade.GOOD
        elif overall_score >= 60:
            overall_grade = QualityGrade.FAIR
        elif overall_score >= 50:
            overall_grade = QualityGrade.POOR
        else:
            overall_grade = QualityGrade.VERY_POOR

        return overall_score, overall_grade

    def _generate_recommendations(self, scores: dict[VoiceQualityMetric, VoiceQualityScore]) -> list[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        for metric, score in scores.items():
            if score.grade in [QualityGrade.POOR, QualityGrade.VERY_POOR]:
                if metric == VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO:
                    recommendations.append("Consider noise reduction preprocessing")
                elif metric == VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION:
                    recommendations.append("Check for audio clipping and reduce gain")
                elif metric == VoiceQualityMetric.DYNAMIC_RANGE:
                    recommendations.append("Improve microphone positioning and room acoustics")
                elif metric == VoiceQualityMetric.SPECTRAL_CENTROID:
                    recommendations.append("Adjust EQ settings for better voice clarity")
                elif metric == VoiceQualityMetric.PITCH_STABILITY:
                    recommendations.append("Consider voice training for pitch consistency")

        return recommendations

    def _detect_issues(self, scores: dict[VoiceQualityMetric, VoiceQualityScore]) -> list[str]:
        """Detect specific audio quality issues"""
        issues = []

        for metric, score in scores.items():
            if score.grade == QualityGrade.VERY_POOR:
                if metric == VoiceQualityMetric.SIGNAL_TO_NOISE_RATIO:
                    issues.append("Excessive background noise detected")
                elif metric == VoiceQualityMetric.TOTAL_HARMONIC_DISTORTION:
                    issues.append("High distortion detected - possible clipping")
                elif metric == VoiceQualityMetric.DYNAMIC_RANGE:
                    issues.append("Poor dynamic range - audio may be over-compressed")
                elif metric == VoiceQualityMetric.ZERO_CROSSING_RATE:
                    issues.append("Unusual zero crossing rate - check for artifacts")

        return issues

    async def batch_analyze(
        self,
        audio_files: list[tuple[str, bytes]],
        sample_rate: int = 44100,
        format: AudioFormat = AudioFormat.PCM_16,
    ) -> list[VoiceQualityReport]:
        """
        Analyze multiple audio files in batch

        Args:
            audio_files: List of (filename, audio_data) tuples
            sample_rate: Audio sample rate
            format: Audio format

        Returns:
            List of quality reports
        """
        reports = []

        for filename, audio_data in audio_files:
            try:
                report = await self.analyze_voice_quality(
                    audio_data=audio_data,
                    sample_rate=sample_rate,
                    format=format,
                    context={"filename": filename},
                )
                reports.append(report)
            except Exception as e:
                self.logger.error(f"Failed to analyze {filename}: {e!s}")
                # Add error report
                reports.append(
                    VoiceQualityReport(
                        overall_score=0.0,
                        overall_grade=QualityGrade.VERY_POOR,
                        issues_detected=[f"Analysis failed: {e!s}"],
                        context={"filename": filename},
                    )
                )

        return reports

    def get_analytics_stats(self) -> dict[str, Any]:
        """Get analytics statistics"""
        return self.stats.copy()

    def get_supported_metrics(self) -> list[VoiceQualityMetric]:
        """Get list of supported quality metrics"""
        return list(self.analyzers.keys())


# Convenience function
async def analyze_voice_quality(
    audio_data: bytes,
    sample_rate: int = 44100,
    format: AudioFormat = AudioFormat.PCM_16,
) -> VoiceQualityReport:
    """
    Simple voice quality analysis

    Args:
        audio_data: Audio data as bytes
        sample_rate: Audio sample rate
        format: Audio format

    Returns:
        Voice quality report
    """
    analytics = LUKHASVoiceAnalytics()
    return await analytics.analyze_voice_quality(audio_data, sample_rate, format=format)


# Export main classes
__all__ = [
    "LUKHASVoiceAnalytics",
    "QualityGrade",
    "VoiceQualityMetric",
    "VoiceQualityReport",
    "VoiceQualityScore",
    "analyze_voice_quality",
]
