#!/usr/bin/env python3
"""
LUKHΛS Phase 6 – Glyph Collapse Simulator
Runs batch simulations of symbolic state collapses and logs decisions for analysis.

This module provides comprehensive simulation capabilities for testing symbolic
wavefunction collapse behavior under various entropy conditions.
"""

import asyncio
import json
import time
import random
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Import from wavefunction manager
from .wavefunction_manager import WavefunctionManager, Wavefunction, ConsciousnessPhase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for glyph collapse simulation"""
    name: str
    description: str
    num_simulations: int
    entropy_range: Tuple[float, float]
    evolution_steps: int
    time_delta: float
    templates_to_test: List[str]
    observers: List[str]
    emergency_collapse_probability: float = 0.05
    guardian_intervention_threshold: float = 0.85


@dataclass
class CollapseResult:
    """Result of a single wavefunction collapse"""
    simulation_id: str
    wavefunction_id: str
    initial_entropy: float
    final_entropy: float
    collapse_entropy: float
    original_glyphs: List[str]
    collapsed_glyph: str
    observer: str
    collapse_time: float
    evolution_steps: int
    consciousness_phase: str
    trinity_coherence: float
    superposition_strength_before: float
    guardian_intervention: bool


@dataclass
class SimulationBatch:
    """Results from a batch of simulations"""
    config: SimulationConfig
    results: List[CollapseResult]
    start_time: float
    end_time: float
    total_duration: float
    summary_statistics: Dict
    symbolic_patterns: Dict
    guardian_effectiveness: Dict


class GlyphCollapseSimulator:
    """
    Comprehensive simulator for symbolic wavefunction collapse analysis
    """
    
    # Predefined simulation configurations
    SIMULATION_CONFIGS = {
        "stability_test": SimulationConfig(
            name="Stability Test",
            description="Test collapse behavior in low-entropy stable conditions",
            num_simulations=50,
            entropy_range=(0.1, 0.4),
            evolution_steps=10,
            time_delta=0.5,
            templates_to_test=["trinity_coherence", "alert_meditation", "reflective_dreaming"],
            observers=["system", "user", "meditation_observer"]
        ),
        
        "drift_analysis": SimulationConfig(
            name="Drift Analysis",
            description="Analyze collapse patterns during entropy drift phase",
            num_simulations=100,
            entropy_range=(0.3, 0.7),
            evolution_steps=20,
            time_delta=0.3,
            templates_to_test=["creative_flow", "reflective_dreaming", "analytical_focus"],
            observers=["system", "creative_observer", "analytical_observer"]
        ),
        
        "chaos_resilience": SimulationConfig(
            name="Chaos Resilience",
            description="Test system behavior under high-entropy chaotic conditions",
            num_simulations=75,
            entropy_range=(0.7, 0.95),
            evolution_steps=15,
            time_delta=0.2,
            templates_to_test=["trinity_coherence", "entropy_chaos", "transcendent_awareness"],
            observers=["guardian_emergency", "chaos_observer", "system"],
            emergency_collapse_probability=0.15,
            guardian_intervention_threshold=0.80
        ),
        
        "phase_transitions": SimulationConfig(
            name="Phase Transitions",
            description="Study transitions between consciousness phases",
            num_simulations=200,
            entropy_range=(0.0, 1.0),
            evolution_steps=30,
            time_delta=0.4,
            templates_to_test=list(WavefunctionManager.CONSCIOUSNESS_TEMPLATES.keys()),
            observers=["system", "phase_observer", "transition_monitor"]
        ),
        
        "guardian_stress_test": SimulationConfig(
            name="Guardian Stress Test",
            description="Stress test Guardian intervention capabilities",
            num_simulations=25,
            entropy_range=(0.8, 1.0),
            evolution_steps=5,
            time_delta=0.1,
            templates_to_test=["trinity_coherence", "entropy_chaos"],
            observers=["guardian_emergency"],
            emergency_collapse_probability=0.8,
            guardian_intervention_threshold=0.75
        )
    }
    
    def __init__(self, output_dir: str = "quantum_core/simulation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simulation state
        self.current_batch: Optional[SimulationBatch] = None
        self.all_results: List[SimulationBatch] = []
        
        logger.info("🧪 Glyph Collapse Simulator initialized")
        logger.info(f"   Output directory: {self.output_dir}")
    
    async def run_simulation_batch(self, config_name: str) -> SimulationBatch:
        """Run a complete simulation batch"""
        if config_name not in self.SIMULATION_CONFIGS:
            raise ValueError(f"Unknown simulation config: {config_name}")
        
        config = self.SIMULATION_CONFIGS[config_name]
        logger.info(f"🚀 Starting simulation batch: {config.name}")
        logger.info(f"   Simulations: {config.num_simulations}")
        logger.info(f"   Entropy range: {config.entropy_range}")
        logger.info(f"   Templates: {config.templates_to_test}")
        
        start_time = time.time()
        results: List[CollapseResult] = []
        
        for sim_idx in range(config.num_simulations):
            if sim_idx % 10 == 0:
                logger.info(f"   Progress: {sim_idx}/{config.num_simulations}")
            
            try:
                result = await self._run_single_simulation(config, sim_idx)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Simulation {sim_idx} failed: {e}")
                continue
        
        end_time = time.time()
        
        # Create simulation batch
        batch = SimulationBatch(
            config=config,
            results=results,
            start_time=start_time,
            end_time=end_time,
            total_duration=end_time - start_time,
            summary_statistics=self._calculate_summary_statistics(results),
            symbolic_patterns=self._analyze_symbolic_patterns(results),
            guardian_effectiveness=self._analyze_guardian_effectiveness(results)
        )
        
        self.current_batch = batch
        self.all_results.append(batch)
        
        logger.info(f"✅ Simulation batch completed: {len(results)} successful simulations")
        logger.info(f"   Duration: {batch.total_duration:.2f}s")
        
        return batch
    
    async def _run_single_simulation(self, config: SimulationConfig, sim_idx: int) -> Optional[CollapseResult]:
        """Run a single wavefunction collapse simulation"""
        sim_id = f"{config.name.lower().replace(' ', '_')}_{sim_idx:04d}"
        
        # Create isolated wavefunction manager for this simulation
        manager = WavefunctionManager()
        
        # Select random template and observer
        template = random.choice(config.templates_to_test)
        observer = random.choice(config.observers)
        
        # Create wavefunction with random initial entropy
        initial_entropy = random.uniform(*config.entropy_range)
        wf_id = f"sim_wf_{sim_idx}"
        
        try:
            wavefunction = manager.create_wavefunction(
                wf_id=wf_id,
                template_name=template,
                initial_entropy=initial_entropy
            )
            
            original_glyphs = wavefunction.glyph_superposition.copy()
            initial_superposition = wavefunction.measure_superposition_strength()
            
            # Evolution phase
            guardian_intervention = False
            for step in range(config.evolution_steps):
                manager.evolve_system(config.time_delta)
                
                # Check for emergency collapse
                if (random.random() < config.emergency_collapse_probability and 
                    manager.global_entropy > config.guardian_intervention_threshold):
                    guardian_intervention = True
                    observer = "guardian_emergency"
                    break
                
                # Check if wavefunction naturally collapsed due to extreme entropy
                if wavefunction.entropy_score > 0.95:
                    break
            
            # Record state before collapse
            pre_collapse_entropy = wavefunction.entropy_score
            pre_collapse_phase = manager._get_current_phase()
            trinity_coherence = wavefunction.trinity_coherence
            
            # Collapse the wavefunction
            collapse_time = time.time()
            collapsed_glyph = manager.collapse_wavefunction(wf_id, observer)
            
            if not collapsed_glyph:
                logger.warning(f"Simulation {sim_id}: collapse failed")
                return None
            
            # Create result
            result = CollapseResult(
                simulation_id=sim_id,
                wavefunction_id=wf_id,
                initial_entropy=initial_entropy,
                final_entropy=manager.global_entropy,
                collapse_entropy=pre_collapse_entropy,
                original_glyphs=original_glyphs,
                collapsed_glyph=collapsed_glyph,
                observer=observer,
                collapse_time=collapse_time,
                evolution_steps=config.evolution_steps,
                consciousness_phase=pre_collapse_phase.value,
                trinity_coherence=trinity_coherence,
                superposition_strength_before=initial_superposition,
                guardian_intervention=guardian_intervention
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Single simulation {sim_id} error: {e}")
            return None
    
    def _calculate_summary_statistics(self, results: List[CollapseResult]) -> Dict:
        """Calculate summary statistics for simulation results"""
        if not results:
            return {}
        
        # Entropy statistics
        initial_entropies = [r.initial_entropy for r in results]
        collapse_entropies = [r.collapse_entropy for r in results]
        final_entropies = [r.final_entropy for r in results]
        
        # Trinity coherence statistics
        trinity_coherences = [r.trinity_coherence for r in results]
        
        # Superposition strength statistics
        superposition_strengths = [r.superposition_strength_before for r in results]
        
        # Phase distribution
        phase_counts = {}
        for result in results:
            phase = result.consciousness_phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Observer distribution
        observer_counts = {}
        for result in results:
            observer = result.observer
            observer_counts[observer] = observer_counts.get(observer, 0) + 1
        
        # Guardian intervention rate
        guardian_interventions = sum(1 for r in results if r.guardian_intervention)
        guardian_intervention_rate = guardian_interventions / len(results)
        
        return {
            "total_simulations": len(results),
            "entropy_statistics": {
                "initial": {
                    "mean": statistics.mean(initial_entropies),
                    "median": statistics.median(initial_entropies),
                    "stdev": statistics.stdev(initial_entropies) if len(initial_entropies) > 1 else 0,
                    "min": min(initial_entropies),
                    "max": max(initial_entropies)
                },
                "collapse": {
                    "mean": statistics.mean(collapse_entropies),
                    "median": statistics.median(collapse_entropies),
                    "stdev": statistics.stdev(collapse_entropies) if len(collapse_entropies) > 1 else 0,
                    "min": min(collapse_entropies),
                    "max": max(collapse_entropies)
                },
                "final": {
                    "mean": statistics.mean(final_entropies),
                    "median": statistics.median(final_entropies),
                    "stdev": statistics.stdev(final_entropies) if len(final_entropies) > 1 else 0,
                    "min": min(final_entropies),
                    "max": max(final_entropies)
                }
            },
            "trinity_coherence": {
                "mean": statistics.mean(trinity_coherences),
                "median": statistics.median(trinity_coherences),
                "stdev": statistics.stdev(trinity_coherences) if len(trinity_coherences) > 1 else 0,
                "min": min(trinity_coherences),
                "max": max(trinity_coherences)
            },
            "superposition_strength": {
                "mean": statistics.mean(superposition_strengths),
                "median": statistics.median(superposition_strengths),
                "stdev": statistics.stdev(superposition_strengths) if len(superposition_strengths) > 1 else 0,
                "min": min(superposition_strengths),
                "max": max(superposition_strengths)
            },
            "phase_distribution": phase_counts,
            "observer_distribution": observer_counts,
            "guardian_intervention_rate": guardian_intervention_rate,
            "guardian_interventions": guardian_interventions
        }
    
    def _analyze_symbolic_patterns(self, results: List[CollapseResult]) -> Dict:
        """Analyze symbolic collapse patterns"""
        if not results:
            return {}
        
        # Collapse patterns by initial glyph composition
        template_collapse_patterns = {}
        for result in results:
            template_key = "→".join(result.original_glyphs)
            if template_key not in template_collapse_patterns:
                template_collapse_patterns[template_key] = {}
            
            collapsed = result.collapsed_glyph
            template_collapse_patterns[template_key][collapsed] = \
                template_collapse_patterns[template_key].get(collapsed, 0) + 1
        
        # Most common collapse outcomes
        all_collapses = [r.collapsed_glyph for r in results]
        collapse_frequency = {}
        for glyph in all_collapses:
            collapse_frequency[glyph] = collapse_frequency.get(glyph, 0) + 1
        
        # Sort by frequency
        most_common_collapses = sorted(collapse_frequency.items(), 
                                     key=lambda x: x[1], reverse=True)
        
        # Trinity Framework preservation rate
        trinity_symbols = {"⚛️", "🧠", "🛡️"}
        trinity_collapses = sum(1 for r in results if r.collapsed_glyph in trinity_symbols)
        trinity_preservation_rate = trinity_collapses / len(results)
        
        # Entropy-collapse correlation
        entropy_collapse_correlation = self._calculate_entropy_collapse_correlation(results)
        
        return {
            "template_collapse_patterns": template_collapse_patterns,
            "collapse_frequency": collapse_frequency,
            "most_common_collapses": most_common_collapses[:10],  # Top 10
            "trinity_preservation_rate": trinity_preservation_rate,
            "trinity_collapses": trinity_collapses,
            "entropy_collapse_correlation": entropy_collapse_correlation,
            "unique_collapse_glyphs": len(set(all_collapses)),
            "total_possible_glyphs": len(set(glyph for r in results for glyph in r.original_glyphs))
        }
    
    def _calculate_entropy_collapse_correlation(self, results: List[CollapseResult]) -> Dict:
        """Calculate correlation between entropy levels and collapse outcomes"""
        entropy_ranges = {
            "low": (0.0, 0.3),
            "medium": (0.3, 0.7),
            "high": (0.7, 1.0)
        }
        
        correlation_data = {}
        for range_name, (min_entropy, max_entropy) in entropy_ranges.items():
            range_results = [r for r in results 
                           if min_entropy <= r.collapse_entropy < max_entropy]
            
            if range_results:
                range_collapses = [r.collapsed_glyph for r in range_results]
                range_frequency = {}
                for glyph in range_collapses:
                    range_frequency[glyph] = range_frequency.get(glyph, 0) + 1
                
                correlation_data[range_name] = {
                    "count": len(range_results),
                    "collapse_frequency": range_frequency,
                    "most_common": max(range_frequency.items(), key=lambda x: x[1]) if range_frequency else None
                }
        
        return correlation_data
    
    def _analyze_guardian_effectiveness(self, results: List[CollapseResult]) -> Dict:
        """Analyze Guardian System effectiveness during simulations"""
        guardian_results = [r for r in results if r.guardian_intervention]
        
        if not guardian_results:
            return {
                "interventions_triggered": 0,
                "intervention_rate": 0.0,
                "effectiveness_score": 0.0
            }
        
        # Calculate intervention effectiveness
        successful_interventions = 0
        for result in guardian_results:
            # Consider intervention successful if:
            # 1. Trinity coherence maintained > 0.5
            # 2. Final entropy < collapse entropy (stabilization)
            # 3. Collapsed to Trinity symbol
            
            trinity_maintained = result.trinity_coherence > 0.5
            entropy_stabilized = result.final_entropy < result.collapse_entropy
            trinity_collapse = result.collapsed_glyph in {"⚛️", "🧠", "🛡️"}
            
            if trinity_maintained or entropy_stabilized or trinity_collapse:
                successful_interventions += 1
        
        effectiveness_score = successful_interventions / len(guardian_results)
        
        # Intervention timing analysis
        intervention_entropies = [r.collapse_entropy for r in guardian_results]
        avg_intervention_entropy = statistics.mean(intervention_entropies)
        
        return {
            "interventions_triggered": len(guardian_results),
            "intervention_rate": len(guardian_results) / len(results),
            "successful_interventions": successful_interventions,
            "effectiveness_score": effectiveness_score,
            "average_intervention_entropy": avg_intervention_entropy,
            "intervention_entropy_range": [min(intervention_entropies), max(intervention_entropies)] if intervention_entropies else [0, 0]
        }
    
    def save_simulation_results(self, batch: SimulationBatch) -> Path:
        """Save simulation batch results to file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{batch.config.name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Convert batch to dictionary
        batch_data = {
            "config": asdict(batch.config),
            "results": [asdict(result) for result in batch.results],
            "start_time": batch.start_time,
            "end_time": batch.end_time,
            "total_duration": batch.total_duration,
            "summary_statistics": batch.summary_statistics,
            "symbolic_patterns": batch.symbolic_patterns,
            "guardian_effectiveness": batch.guardian_effectiveness,
            "metadata": {
                "lukhλs_version": "6.0.0",
                "trinity_framework": "⚛️🧠🛡️",
                "simulation_engine": "glyph_collapse_simulator",
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📁 Simulation results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save simulation results: {e}")
            raise
    
    def generate_analysis_report(self, batch: SimulationBatch) -> str:
        """Generate human-readable analysis report"""
        config = batch.config
        stats = batch.summary_statistics
        patterns = batch.symbolic_patterns
        guardian = batch.guardian_effectiveness
        
        report_lines = [
            "🧪 LUKHΛS Glyph Collapse Simulation Analysis Report",
            "=" * 60,
            f"Simulation: {config.name}",
            f"Description: {config.description}",
            f"Duration: {batch.total_duration:.2f}s",
            f"Successful Simulations: {len(batch.results)}/{config.num_simulations}",
            "",
            "📊 ENTROPY STATISTICS",
            "-" * 30,
            f"Initial Entropy - Mean: {stats['entropy_statistics']['initial']['mean']:.3f}, "
            f"StdDev: {stats['entropy_statistics']['initial']['stdev']:.3f}",
            f"Collapse Entropy - Mean: {stats['entropy_statistics']['collapse']['mean']:.3f}, "
            f"StdDev: {stats['entropy_statistics']['collapse']['stdev']:.3f}",
            f"Final Entropy - Mean: {stats['entropy_statistics']['final']['mean']:.3f}, "
            f"StdDev: {stats['entropy_statistics']['final']['stdev']:.3f}",
            "",
            "🎭 CONSCIOUSNESS PHASE DISTRIBUTION",
            "-" * 30
        ]
        
        for phase, count in stats['phase_distribution'].items():
            percentage = (count / stats['total_simulations']) * 100
            report_lines.append(f"{phase.capitalize()}: {count} ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "🔮 SYMBOLIC COLLAPSE PATTERNS",
            "-" * 30,
            f"Trinity Preservation Rate: {patterns['trinity_preservation_rate']:.1%}",
            f"Unique Collapse Glyphs: {patterns['unique_collapse_glyphs']}",
            "",
            "Most Common Collapses:"
        ])
        
        for glyph, count in patterns['most_common_collapses'][:5]:
            percentage = (count / len(batch.results)) * 100
            report_lines.append(f"  {glyph}: {count} ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "🛡️ GUARDIAN SYSTEM EFFECTIVENESS",
            "-" * 30,
            f"Interventions Triggered: {guardian['interventions_triggered']}",
            f"Intervention Rate: {guardian['intervention_rate']:.1%}",
            f"Effectiveness Score: {guardian['effectiveness_score']:.1%}",
            f"Average Intervention Entropy: {guardian['average_intervention_entropy']:.3f}",
            "",
            "⚛️🧠🛡️ TRINITY FRAMEWORK COHERENCE",
            "-" * 30,
            f"Mean Coherence: {stats['trinity_coherence']['mean']:.3f}",
            f"Coherence StdDev: {stats['trinity_coherence']['stdev']:.3f}",
            f"Min Coherence: {stats['trinity_coherence']['min']:.3f}",
            "",
            "🌊 SUPERPOSITION ANALYSIS",
            "-" * 30,
            f"Mean Superposition Strength: {stats['superposition_strength']['mean']:.3f}",
            f"Superposition StdDev: {stats['superposition_strength']['stdev']:.3f}",
            "",
            "✅ SIMULATION COMPLETE",
            f"Generated: {datetime.utcnow().isoformat()}Z"
        ])
        
        return "\n".join(report_lines)
    
    async def run_all_simulations(self) -> List[SimulationBatch]:
        """Run all predefined simulation configurations"""
        logger.info("🚀 Running all simulation configurations...")
        
        all_batches = []
        for config_name in self.SIMULATION_CONFIGS.keys():
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting {config_name}")
            logger.info(f"{'='*60}")
            
            try:
                batch = await self.run_simulation_batch(config_name)
                all_batches.append(batch)
                
                # Save results
                self.save_simulation_results(batch)
                
                # Generate and display report
                report = self.generate_analysis_report(batch)
                print("\n" + report)
                
            except Exception as e:
                logger.error(f"Failed to run simulation {config_name}: {e}")
                continue
        
        logger.info(f"\n✅ All simulations completed: {len(all_batches)} successful batches")
        return all_batches


async def main():
    """Demo of glyph collapse simulation"""
    print("🧪 LUKHΛS Phase 6: Glyph Collapse Simulator Demo")
    print("=" * 60)
    
    simulator = GlyphCollapseSimulator()
    
    # Run a single simulation batch for demo
    print("Running stability test simulation...")
    batch = await simulator.run_simulation_batch("stability_test")
    
    # Save results
    results_file = simulator.save_simulation_results(batch)
    print(f"\nResults saved to: {results_file}")
    
    # Generate and display report
    report = simulator.generate_analysis_report(batch)
    print("\n" + "=" * 60)
    print("ANALYSIS REPORT")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")