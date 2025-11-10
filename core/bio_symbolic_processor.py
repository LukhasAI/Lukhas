"""
MΛTRIZ Bio-Symbolic Data Processor
Advanced bio-symbolic adaptation and pattern processing for consciousness signals

This module implements the M⌾TRIZ bio-symbolic adaptation layer, providing:
- Pattern recognition from biological oscillators
- Symbolic representation of consciousness states
- Adaptation algorithms for consciousness evolution
- Integration with existing bio/ and symbolic_core/ modules
"""
import asyncio
import logging
import time
from typing import Any, Optional

from core.bio_symbolic import (
    Adapter,
    PatternExtractor,
    SymbolicRepresenter,
)
from core.matriz_consciousness_signals import (
    BioSymbolicData,
    ConsciousnessSignal,
    ConsciousnessSignalType,
)

logger = logging.getLogger(__name__)


class BioSymbolicProcessor:
    """
    Advanced bio-symbolic data processor for MΛTRIZ consciousness signals

    This processor bridges biological patterns and symbolic consciousness
    representations, enabling sophisticated adaptation and evolution.
    """

    def __init__(self):
        self.processing_cache: dict[str, Any] = {}
        self.coherence_threshold = 0.7
        self.adaptation_learning_rate = 0.01
        self.entropy_window_size = 100
        self.resonance_database: dict[str, list[str]] = {}

        self.pattern_extractor = PatternExtractor()
        self.symbolic_representer = SymbolicRepresenter()
        self.adapter = Adapter()

        # Performance metrics
        self.processing_stats = {
            "signals_processed": 0,
            "adaptations_applied": 0,
            "patterns_evolved": 0,
            "coherence_violations": 0,
            "processing_time_ms": [],
        }

    def process_consciousness_signal(
        self, signal: ConsciousnessSignal
    ) -> BioSymbolicData:
        """
        Process a consciousness signal to extract and enhance bio-symbolic data

        Args:
            signal: ConsciousnessSignal to process

        Returns:
            Enhanced BioSymbolicData with pattern analysis and adaptations
        """
        start_time = time.time()

        try:
            # Extract existing bio-symbolic data or create new
            bio_data = signal.bio_symbolic_data
            if not bio_data:
                bio_data = self._create_default_bio_symbolic_data(signal)

            # Analyze biological patterns
            patterns = self.pattern_extractor.extract_bio_patterns(signal, bio_data)

            # Apply symbolic representations
            symbolic_data = self.symbolic_representer.apply_symbolic_representations(
                patterns
            )

            # Perform adaptations
            adapted_data = self.adapter.apply_adaptations(
                bio_data, symbolic_data, signal, self.processing_stats
            )

            # Update coherence and entropy measures
            enhanced_data = self._update_coherence_entropy(adapted_data, signal)

            # Cache processing results
            self._update_processing_cache(signal.signal_id, enhanced_data)

            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self.processing_stats["signals_processed"] += 1
            self.processing_stats["processing_time_ms"].append(processing_time)

            # Keep only last 1000 timing measurements
            if len(self.processing_stats["processing_time_ms"]) > 1000:
                self.processing_stats["processing_time_ms"] = self.processing_stats[
                    "processing_time_ms"
                ][-1000:]

            logger.info(
                f"Processed consciousness signal {signal.signal_id} in {processing_time:.2f}ms"
            )
            return enhanced_data

        except Exception as e:
            logger.error(
                f"Error processing consciousness signal {signal.signal_id}: {e}"
            )
            self.processing_stats["coherence_violations"] += 1
            # Return original or minimal bio data on error
            return bio_data or self._create_default_bio_symbolic_data(signal)

    def _create_default_bio_symbolic_data(
        self, signal: ConsciousnessSignal
    ) -> BioSymbolicData:
        """Create default bio-symbolic data for a signal without existing data"""

        # Base pattern type on signal type
        pattern_type_mapping = {
            ConsciousnessSignalType.AWARENESS: "sensory_awareness",
            ConsciousnessSignalType.REFLECTION: "metacognitive_reflection",
            ConsciousnessSignalType.EVOLUTION: "evolutionary_adaptation",
            ConsciousnessSignalType.INTEGRATION: "inter_module_integration",
            ConsciousnessSignalType.BIO_ADAPTATION: "bio_symbolic_adaptation",
        }

        pattern_type = pattern_type_mapping.get(
            signal.signal_type, "generic_consciousness"
        )

        # Default frequency based on awareness level
        base_frequency = 10.0 + signal.awareness_level * 30  # 10-40 Hz range

        return BioSymbolicData(
            pattern_type=pattern_type,
            oscillation_frequency=base_frequency,
            coherence_score=signal.awareness_level * 0.8,
            adaptation_vector={"awareness": signal.awareness_level},
            entropy_delta=0.0,
            resonance_patterns=[pattern_type],
            membrane_permeability=0.7,
            temporal_decay=0.9,
        )

    def _update_coherence_entropy(
        self, bio_data: BioSymbolicData, signal: ConsciousnessSignal
    ) -> BioSymbolicData:
        """Update coherence and entropy measures based on signal context"""

        # Create enhanced copy
        enhanced_data = BioSymbolicData(
            pattern_type=bio_data.pattern_type,
            oscillation_frequency=bio_data.oscillation_frequency,
            coherence_score=bio_data.coherence_score,
            adaptation_vector=bio_data.adaptation_vector.copy(),
            entropy_delta=bio_data.entropy_delta,
            resonance_patterns=bio_data.resonance_patterns.copy(),
            membrane_permeability=bio_data.membrane_permeability,
            temporal_decay=bio_data.temporal_decay,
        )

        # Update coherence based on signal characteristics
        base_coherence = enhanced_data.coherence_score

        # Reflection increases coherence
        if signal.reflection_depth > 0:
            coherence_boost = min(0.2, signal.reflection_depth * 0.05)
            enhanced_data.coherence_score = min(1.0, base_coherence + coherence_boost)

        # High awareness stabilizes coherence
        if signal.awareness_level > 0.8:
            enhanced_data.coherence_score = min(
                1.0, enhanced_data.coherence_score + 0.05
            )

        # Constellation compliance affects coherence
        if signal.constellation_alignment:
            constellation_avg = (
                signal.constellation_alignment.identity_auth_score
                + signal.constellation_alignment.consciousness_coherence
                + signal.constellation_alignment.guardian_compliance
            ) / 3
            enhanced_data.coherence_score = (
                enhanced_data.coherence_score + constellation_avg
            ) / 2

        # Update entropy based on system state
        if signal.signal_type == ConsciousnessSignalType.EVOLUTION:
            # Evolution increases entropy
            enhanced_data.entropy_delta += 0.1
        elif signal.signal_type == ConsciousnessSignalType.REFLECTION:
            # Reflection decreases entropy
            enhanced_data.entropy_delta -= 0.05

        # Check coherence violations
        if enhanced_data.coherence_score < self.coherence_threshold:
            self.processing_stats["coherence_violations"] += 1
            logger.warning(
                f"Coherence violation in signal {signal.signal_id}: {enhanced_data.coherence_score:.3f}"
            )

        return enhanced_data

    def _update_processing_cache(self, signal_id: str, bio_data: BioSymbolicData):
        """Update processing cache with recent bio-symbolic data"""

        # Keep cache size manageable
        if len(self.processing_cache) > 1000:
            # Remove oldest entries
            oldest_keys = list(self.processing_cache.keys())[:200]
            for key in oldest_keys:
                del self.processing_cache[key]

        self.processing_cache[signal_id] = {
            "timestamp": time.time(),
            "pattern_type": bio_data.pattern_type,
            "coherence_score": bio_data.coherence_score,
            "oscillation_frequency": bio_data.oscillation_frequency,
            "resonance_patterns": bio_data.resonance_patterns,
        }

    def get_processing_statistics(self) -> dict[str, Any]:
        """Get current processing statistics"""

        stats = self.processing_stats.copy()

        # Calculate timing statistics
        if stats["processing_time_ms"]:
            times = stats["processing_time_ms"]
            stats["avg_processing_time_ms"] = sum(times) / len(times)
            stats["max_processing_time_ms"] = max(times)
            stats["min_processing_time_ms"] = min(times)
            # Calculate p95 processing time
            sorted_times = sorted(times)
            p95_idx = int(len(sorted_times) * 0.95)
            stats["p95_processing_time_ms"] = (
                sorted_times[p95_idx] if p95_idx < len(sorted_.times) else max(times)
            )

        # Calculate success rates
        total_signals = stats["signals_processed"]
        if total_signals > 0:
            stats["coherence_violation_rate"] = (
                stats["coherence_violations"] / total_signals
            )
            stats["adaptation_rate"] = stats["adaptations_applied"] / total_signals

        return stats

    def evolve_adaptation_rules(self):
        """Evolve adaptation rules based on processing outcomes"""

        for rule in self.adapter.adaptation_rules:
            # Apply decay to adaptation strength
            rule.adaptation_strength *= rule.decay_rate

            # Prevent rules from becoming too weak
            if rule.adaptation_strength < 0.1:
                rule.adaptation_strength = 0.1

            # Update learning rate based on success (simplified)
            if rule.adaptation_strength > 0.8:
                rule.learning_rate = min(
                    0.05, rule.learning_rate * 1.02
                )  # Increase learning rate for successful rules
            else:
                rule.learning_rate = max(
                    0.001, rule.learning_rate * 0.98
                )  # Decrease for unsuccessful ones

        self.processing_stats["patterns_evolved"] += len(
            self.adapter.adaptation_rules
        )

    async def process_signal_batch(
        self, signals: list[ConsciousnessSignal]
    ) -> list[BioSymbolicData]:
        """Process a batch of consciousness signals asynchronously"""

        async def process_single(signal):
            return self.process_consciousness_signal(signal)

        tasks = [process_single(signal) for signal in signals]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Error processing signal {signals[i].signal_id}: {result}"
                )
                # Create fallback bio data
                processed_results.append(
                    self._create_default_bio_symbolic_data(signals[i])
                )
            else:
                processed_results.append(result)

        return processed_results


# Factory function for creating the bio-symbolic processor
def create_bio_symbolic_processor() -> BioSymbolicProcessor:
    """Create and configure a bio-symbolic processor instance"""
    processor = BioSymbolicProcessor()
    logger.info("Created bio-symbolic processor with default configuration")
    return processor


# Global processor instance for module-level access
_global_processor: Optional[BioSymbolicProcessor] = None


def get_bio_symbolic_processor() -> BioSymbolicProcessor:
    """Get or create global bio-symbolic processor instance"""
    global _global_processor
    if _global_processor is None:
        _global_processor = create_bio_symbolic_processor()
    return _global_processor


# Module exports
__all__ = [
    "BioSymbolicProcessor",
    "create_bio_symbolic_processor",
    "get_bio_symbolic_processor",
]
