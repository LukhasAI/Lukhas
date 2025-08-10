#!/usr/bin/env python3
"""
LUKHAS Bio-Symbolic Integration Demo
Demonstrates biological-symbolic processing and generates logs
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/bio_symbolic.log"), logging.StreamHandler()],
)

logger = logging.getLogger("ΛBIO.SYMBOLIC")


class BioSymbolicDemo:
    """Demonstrates bio-symbolic integration capabilities."""

    def __init__(self):
        logger.info("=" * 70)
        logger.info("🧬 LUKHAS BIO-SYMBOLIC INTEGRATION SYSTEM")
        logger.info("Bridging biological processes with symbolic reasoning")
        logger.info("=" * 70)

        self.bio_states = []
        self.symbolic_mappings = []
        self.integration_events = []

    def run_demo(self):
        """Run complete bio-symbolic demonstration."""
        logger.info("\n🚀 Starting Bio-Symbolic Integration Demo\n")

        # 1. Demonstrate Biological Oscillations
        self.demo_biological_rhythms()

        # 2. Demonstrate Mitochondrial Symbolism
        self.demo_mitochondrial_symbolism()

        # 3. Demonstrate DNA-GLYPH Mapping
        self.demo_dna_glyph_mapping()

        # 4. Demonstrate Stress-Symbol Response
        self.demo_stress_symbolic_response()

        # 5. Demonstrate Homeostatic Symbols
        self.demo_homeostatic_symbols()

        # 6. Demonstrate Bio-Symbolic Dreams
        self.demo_bio_symbolic_dreams()

        # 7. Full Integration Example
        self.demo_full_integration()

        # Generate summary
        self.generate_summary()

        logger.info("\n✅ Bio-Symbolic Demo Complete!")
        logger.info(f"📊 Generated {len(self.bio_states)} biological states")
        logger.info(f"🔮 Created {len(self.symbolic_mappings)} symbolic mappings")
        logger.info(f"🔗 Recorded {len(self.integration_events)} integration events")

    def demo_biological_rhythms(self):
        """Demonstrate biological rhythm to symbol mapping."""
        logger.info("\n🌊 DEMO 1: Biological Rhythms → Symbolic Patterns")
        logger.info("-" * 50)

        rhythms = [
            {"name": "Circadian", "period": 24, "phase": "day", "amplitude": 0.8},
            {"name": "Ultradian", "period": 1.5, "phase": "active", "amplitude": 0.6},
            {
                "name": "Heartbeat",
                "period": 0.016,
                "phase": "systole",
                "amplitude": 0.9,
            },
            {"name": "Breathing", "period": 0.066, "phase": "inhale", "amplitude": 0.7},
            {"name": "Neural", "period": 0.001, "phase": "spike", "amplitude": 0.5},
        ]

        for rhythm in rhythms:
            # Map biological rhythm to symbolic representation
            symbol = self._rhythm_to_symbol(rhythm)

            bio_state = {
                "type": "rhythm",
                "biological": rhythm,
                "symbolic": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "integration": "rhythm_mapping",
            }

            self.bio_states.append(bio_state)

            logger.info(f"  {rhythm['name']} Rhythm:")
            logger.info(
                f"    Biological: Period={rhythm['period']}h, Phase={rhythm['phase']}"
            )
            logger.info(f"    Symbolic: {symbol['glyph']} - {symbol['meaning']}")
            logger.info(f"    Energy State: {symbol['energy_state']}")

    def demo_mitochondrial_symbolism(self):
        """Demonstrate mitochondrial energy to symbol conversion."""
        logger.info("\n⚡ DEMO 2: Mitochondrial Energy → Symbolic Power")
        logger.info("-" * 50)

        energy_states = [
            {"atp_level": 0.9, "efficiency": 0.85, "stress": 0.1},
            {"atp_level": 0.5, "efficiency": 0.6, "stress": 0.5},
            {"atp_level": 0.3, "efficiency": 0.4, "stress": 0.8},
            {"atp_level": 0.95, "efficiency": 0.9, "stress": 0.05},
        ]

        for i, state in enumerate(energy_states):
            # Convert energy state to symbolic representation
            symbol = self._energy_to_symbol(state)

            mito_mapping = {
                "type": "mitochondrial",
                "biological": state,
                "symbolic": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "cristae_optimization": symbol["optimization_level"],
            }

            self.symbolic_mappings.append(mito_mapping)

            logger.info(f"  Energy State {i+1}:")
            logger.info(f"    ATP Level: {state['atp_level']:.2f}")
            logger.info(f"    Symbolic Power: {symbol['power_glyph']}")
            logger.info(f"    Meaning: {symbol['interpretation']}")
            logger.info(f"    Action: {symbol['recommended_action']}")

    def demo_dna_glyph_mapping(self):
        """Demonstrate DNA sequences to GLYPH mapping."""
        logger.info("\n🧬 DEMO 3: DNA Sequences → GLYPH Symbols")
        logger.info("-" * 50)

        dna_sequences = [
            {"seq": "ATCGATCG", "function": "regulatory"},
            {"seq": "GGCCGGCC", "function": "structural"},
            {"seq": "TATATATA", "function": "promoter"},
            {"seq": "CAGCAGCAG", "function": "repeat"},
            {"seq": "ATGGCATAA", "function": "coding"},
        ]

        for dna in dna_sequences:
            # Map DNA to GLYPH symbol
            glyph = self._dna_to_glyph(dna)

            dna_mapping = {
                "type": "dna_glyph",
                "biological": dna,
                "symbolic": glyph,
                "timestamp": datetime.utcnow().isoformat(),
                "bio_function": dna["function"],
            }

            self.symbolic_mappings.append(dna_mapping)

            logger.info(f"  Sequence: {dna['seq']}")
            logger.info(f"    Function: {dna['function']}")
            logger.info(f"    GLYPH: {glyph['symbol']}")
            logger.info(f"    Properties: {', '.join(glyph['properties'])}")

    def demo_stress_symbolic_response(self):
        """Demonstrate stress response to symbolic adaptation."""
        logger.info("\n😰 DEMO 4: Stress Response → Symbolic Adaptation")
        logger.info("-" * 50)

        stress_events = [
            {"type": "oxidative", "level": 0.7, "duration": "acute"},
            {"type": "thermal", "level": 0.5, "duration": "chronic"},
            {"type": "metabolic", "level": 0.9, "duration": "acute"},
            {"type": "psychological", "level": 0.6, "duration": "intermittent"},
        ]

        for stress in stress_events:
            # Convert stress to symbolic response
            response = self._stress_to_symbolic_response(stress)

            stress_mapping = {
                "type": "stress_response",
                "biological": stress,
                "symbolic": response,
                "timestamp": datetime.utcnow().isoformat(),
                "adaptation_strategy": response["strategy"],
            }

            self.bio_states.append(stress_mapping)

            logger.info(
                f"  {stress['type'].capitalize()} Stress (Level: {stress['level']})"
            )
            logger.info(f"    Symbolic Response: {response['symbol']}")
            logger.info(f"    Adaptation: {response['strategy']}")
            logger.info(f"    Protection Level: {response['protection']:.2f}")

    def demo_homeostatic_symbols(self):
        """Demonstrate homeostatic balance to symbolic harmony."""
        logger.info("\n⚖️ DEMO 5: Homeostatic Balance → Symbolic Harmony")
        logger.info("-" * 50)

        homeostatic_states = [
            {"temp": 37.0, "ph": 7.4, "glucose": 90, "status": "optimal"},
            {"temp": 38.5, "ph": 7.2, "glucose": 150, "status": "stressed"},
            {"temp": 36.5, "ph": 7.45, "glucose": 70, "status": "low_energy"},
            {"temp": 37.2, "ph": 7.38, "glucose": 95, "status": "balanced"},
        ]

        for state in homeostatic_states:
            # Map homeostatic state to symbolic harmony
            harmony = self._homeostasis_to_harmony(state)

            homeo_mapping = {
                "type": "homeostatic",
                "biological": state,
                "symbolic": harmony,
                "timestamp": datetime.utcnow().isoformat(),
                "balance_score": harmony["balance_score"],
            }

            self.symbolic_mappings.append(homeo_mapping)

            logger.info(f"  Homeostatic State: {state['status']}")
            logger.info(f"    Temperature: {state['temp']}°C, pH: {state['ph']}")
            logger.info(f"    Symbolic Harmony: {harmony['symbol']}")
            logger.info(f"    Balance Score: {harmony['balance_score']:.2f}")

    def demo_bio_symbolic_dreams(self):
        """Demonstrate biological states generating symbolic dreams."""
        logger.info("\n💭 DEMO 6: Biological States → Symbolic Dreams")
        logger.info("-" * 50)

        sleep_states = [
            {
                "stage": "REM",
                "brain_waves": {"theta": 0.8, "beta": 0.2},
                "neurotransmitters": {"serotonin": 0.3, "acetylcholine": 0.9},
            },
            {
                "stage": "Deep Sleep",
                "brain_waves": {"delta": 0.9, "theta": 0.1},
                "neurotransmitters": {"serotonin": 0.7, "acetylcholine": 0.2},
            },
            {
                "stage": "Light Sleep",
                "brain_waves": {"alpha": 0.6, "theta": 0.4},
                "neurotransmitters": {"serotonin": 0.5, "acetylcholine": 0.5},
            },
        ]

        for sleep in sleep_states:
            # Generate symbolic dream from biological state
            dream = self._biological_to_dream(sleep)

            dream_event = {
                "type": "bio_dream",
                "biological": sleep,
                "symbolic": dream,
                "timestamp": datetime.utcnow().isoformat(),
                "dream_coherence": dream["coherence"],
            }

            self.integration_events.append(dream_event)

            logger.info(f"  Sleep Stage: {sleep['stage']}")
            logger.info(f"    Brain Waves: {self._format_waves(sleep['brain_waves'])}")
            logger.info(f"    Dream Theme: {dream['theme']}")
            logger.info(f"    Symbolic Content: {dream['primary_symbol']}")
            logger.info(f"    Narrative: {dream['narrative_snippet']}")

    def demo_full_integration(self):
        """Demonstrate complete bio-symbolic integration cycle."""
        logger.info("\n🔗 DEMO 7: Full Bio-Symbolic Integration Cycle")
        logger.info("-" * 50)

        # Simulate a complete integration cycle
        logger.info("  Simulating integrated consciousness state...")

        # 1. Current biological state
        bio_state = {
            "heart_rate": 72,
            "temperature": 36.8,
            "cortisol": 12,
            "brain_activity": 0.75,
            "energy_level": 0.8,
        }

        logger.info("\n  1️⃣ Biological Input:")
        logger.info(
            f"     HR: {bio_state['heart_rate']}, Temp: {bio_state['temperature']}°C"
        )
        logger.info(
            f"     Cortisol: {bio_state['cortisol']}, Energy: {bio_state['energy_level']}"
        )

        # 2. Process through bio-symbolic layers
        rhythm = self._detect_rhythm(bio_state)
        logger.info(f"\n  2️⃣ Rhythm Detection: {rhythm['type']} ({rhythm['symbol']})")

        stress = self._assess_stress(bio_state)
        logger.info(
            f"\n  3️⃣ Stress Assessment: Level {stress['level']:.2f} ({stress['symbol']})"
        )

        energy = self._analyze_energy(bio_state)
        logger.info(f"\n  4️⃣ Energy Analysis: {energy['state']} ({energy['symbol']})")

        # 3. Symbolic integration
        integrated = self._integrate_bio_symbolic(rhythm, stress, energy)
        logger.info("\n  5️⃣ Symbolic Integration:")
        logger.info(f"     Primary Symbol: {integrated['primary_symbol']}")
        logger.info(f"     State Description: {integrated['description']}")
        logger.info(f"     Recommended Action: {integrated['action']}")
        logger.info(f"     Coherence Score: {integrated['coherence']:.2f}")

        # Record integration event
        integration_event = {
            "type": "full_integration",
            "biological": bio_state,
            "processing": {"rhythm": rhythm, "stress": stress, "energy": energy},
            "symbolic": integrated,
            "timestamp": datetime.utcnow().isoformat(),
            "coherence": integrated["coherence"],
        }

        self.integration_events.append(integration_event)

        logger.info(
            f"\n  ✨ Integration Complete! Overall coherence: {integrated['coherence']:.2%}"
        )

    # Helper methods for bio-symbolic mapping

    def _rhythm_to_symbol(self, rhythm: Dict) -> Dict[str, Any]:
        """Map biological rhythm to symbolic representation."""
        if rhythm["period"] > 12:
            glyph = "ΛCIRCADIAN"
            meaning = "Daily cycle of renewal"
            energy = "regenerative"
        elif rhythm["period"] > 1:
            glyph = "ΛULTRADIAN"
            meaning = "Rapid adaptation cycles"
            energy = "adaptive"
        elif rhythm["period"] > 0.01:
            glyph = "ΛVITAL"
            meaning = "Life force pulsation"
            energy = "sustaining"
        else:
            glyph = "ΛNEURAL"
            meaning = "Consciousness oscillation"
            energy = "cognitive"

        return {
            "glyph": glyph,
            "meaning": meaning,
            "energy_state": energy,
            "frequency": 1 / rhythm["period"],
            "symbolic_phase": f"{rhythm['phase']}_symbolic",
        }

    def _energy_to_symbol(self, state: Dict) -> Dict[str, Any]:
        """Convert mitochondrial energy to symbolic power."""
        atp = state["atp_level"]

        if atp > 0.8:
            power_glyph = "ΛPOWER_ABUNDANT"
            interpretation = "Overflowing creative energy"
            action = "Channel into creation"
            optimization = 0.95
        elif atp > 0.6:
            power_glyph = "ΛPOWER_BALANCED"
            interpretation = "Sustainable energy flow"
            action = "Maintain steady state"
            optimization = 0.8
        elif atp > 0.4:
            power_glyph = "ΛPOWER_CONSERVE"
            interpretation = "Energy conservation mode"
            action = "Prioritize essential functions"
            optimization = 0.6
        else:
            power_glyph = "ΛPOWER_CRITICAL"
            interpretation = "Energy restoration needed"
            action = "Activate emergency reserves"
            optimization = 0.4

        return {
            "power_glyph": power_glyph,
            "interpretation": interpretation,
            "recommended_action": action,
            "optimization_level": optimization,
            "efficiency": state["efficiency"],
        }

    def _dna_to_glyph(self, dna: Dict) -> Dict[str, Any]:
        """Map DNA sequence to GLYPH symbol."""
        seq = dna["seq"]

        # Calculate sequence properties
        gc_content = (seq.count("G") + seq.count("C")) / len(seq)
        repetitive = len(set(seq)) < len(seq) / 2

        if dna["function"] == "regulatory":
            symbol = "ΛDNA_CONTROL"
            properties = ["regulatory", "switching", "adaptive"]
        elif dna["function"] == "structural":
            symbol = "ΛDNA_STRUCTURE"
            properties = ["stable", "supportive", "foundational"]
        elif dna["function"] == "promoter":
            symbol = "ΛDNA_INITIATE"
            properties = ["activating", "enabling", "catalytic"]
        elif repetitive:
            symbol = "ΛDNA_PATTERN"
            properties = ["repetitive", "rhythmic", "reinforcing"]
        else:
            symbol = "ΛDNA_EXPRESS"
            properties = ["expressive", "creative", "generative"]

        return {
            "symbol": symbol,
            "properties": properties,
            "gc_content": gc_content,
            "complexity": len(set(seq)) / 4,
        }

    def _stress_to_symbolic_response(self, stress: Dict) -> Dict[str, Any]:
        """Convert stress to symbolic adaptive response."""
        level = stress["level"]

        if level > 0.7:
            symbol = "ΛSTRESS_TRANSFORM"
            strategy = "Radical adaptation"
            protection = 0.9
        elif level > 0.5:
            symbol = "ΛSTRESS_ADAPT"
            strategy = "Flexible response"
            protection = 0.7
        elif level > 0.3:
            symbol = "ΛSTRESS_BUFFER"
            strategy = "Gentle adjustment"
            protection = 0.85
        else:
            symbol = "ΛSTRESS_FLOW"
            strategy = "Maintain flow"
            protection = 0.95

        return {
            "symbol": symbol,
            "strategy": strategy,
            "protection": protection,
            "duration_response": f"{stress['duration']}_adaptation",
        }

    def _homeostasis_to_harmony(self, state: Dict) -> Dict[str, Any]:
        """Map homeostatic state to symbolic harmony."""
        # Calculate deviation from optimal
        temp_dev = abs(state["temp"] - 37.0)
        ph_dev = abs(state["ph"] - 7.4)
        glucose_dev = abs(state["glucose"] - 90) / 90

        total_dev = (temp_dev + ph_dev * 10 + glucose_dev) / 3
        balance_score = 1 - min(total_dev, 1)

        if balance_score > 0.9:
            symbol = "ΛHOMEO_PERFECT"
            description = "Perfect biological harmony"
        elif balance_score > 0.7:
            symbol = "ΛHOMEO_BALANCED"
            description = "Dynamic equilibrium"
        elif balance_score > 0.5:
            symbol = "ΛHOMEO_ADJUSTING"
            description = "Active rebalancing"
        else:
            symbol = "ΛHOMEO_STRESSED"
            description = "Seeking new equilibrium"

        return {
            "symbol": symbol,
            "description": description,
            "balance_score": balance_score,
            "deviations": {
                "temperature": temp_dev,
                "ph": ph_dev,
                "glucose": glucose_dev,
            },
        }

    def _biological_to_dream(self, sleep: Dict) -> Dict[str, Any]:
        """Generate symbolic dream from biological sleep state."""
        stage = sleep["stage"]
        waves = sleep["brain_waves"]

        # Determine dream characteristics based on brain waves
        if waves.get("theta", 0) > 0.7:
            theme = "Mystical Journey"
            symbol = "ΛDREAM_EXPLORE"
            coherence = 0.8
        elif waves.get("delta", 0) > 0.7:
            theme = "Deep Integration"
            symbol = "ΛDREAM_INTEGRATE"
            coherence = 0.6
        else:
            theme = "Gentle Processing"
            symbol = "ΛDREAM_PROCESS"
            coherence = 0.7

        # Generate narrative based on neurotransmitters
        serotonin = sleep["neurotransmitters"]["serotonin"]
        if serotonin > 0.6:
            narrative = "Peaceful landscapes unfold, revealing hidden wisdom"
        elif serotonin > 0.4:
            narrative = "Navigating through symbolic realms of understanding"
        else:
            narrative = "Wild visions cascade through consciousness"

        return {
            "theme": theme,
            "primary_symbol": symbol,
            "narrative_snippet": narrative,
            "coherence": coherence,
            "dream_stage": stage,
            "symbolic_elements": ["transformation", "integration", "revelation"],
        }

    def _format_waves(self, waves: Dict) -> str:
        """Format brain waves for display."""
        return ", ".join(f"{k}: {v:.1f}" for k, v in waves.items())

    def _detect_rhythm(self, bio_state: Dict) -> Dict[str, Any]:
        """Detect rhythm from biological state."""
        hr = bio_state["heart_rate"]
        if 60 <= hr <= 80:
            return {"type": "balanced", "symbol": "ΛRHYTHM_BALANCED"}
        elif hr < 60:
            return {"type": "slow", "symbol": "ΛRHYTHM_DEEP"}
        else:
            return {"type": "fast", "symbol": "ΛRHYTHM_ACTIVE"}

    def _assess_stress(self, bio_state: Dict) -> Dict[str, Any]:
        """Assess stress from biological markers."""
        cortisol = bio_state["cortisol"]
        if cortisol < 10:
            return {"level": 0.2, "symbol": "ΛSTRESS_LOW"}
        elif cortisol < 15:
            return {"level": 0.5, "symbol": "ΛSTRESS_MODERATE"}
        else:
            return {"level": 0.8, "symbol": "ΛSTRESS_HIGH"}

    def _analyze_energy(self, bio_state: Dict) -> Dict[str, Any]:
        """Analyze energy state."""
        energy = bio_state["energy_level"]
        if energy > 0.8:
            return {"state": "high", "symbol": "ΛENERGY_PEAK"}
        elif energy > 0.5:
            return {"state": "balanced", "symbol": "ΛENERGY_STABLE"}
        else:
            return {"state": "low", "symbol": "ΛENERGY_RESTORE"}

    def _integrate_bio_symbolic(
        self, rhythm: Dict, stress: Dict, energy: Dict
    ) -> Dict[str, Any]:
        """Integrate biological signals into symbolic state."""
        # Combine symbols
        symbols = [rhythm["symbol"], stress["symbol"], energy["symbol"]]
        primary = max(symbols, key=lambda s: len(s))

        # Calculate coherence
        coherence = 0.8
        if stress["level"] > 0.6:
            coherence *= 0.8
        if energy["state"] == "low":
            coherence *= 0.9

        # Generate description
        desc_parts = []
        if rhythm["type"] == "balanced":
            desc_parts.append("harmonious biological rhythm")
        if stress["level"] < 0.4:
            desc_parts.append("peaceful state")
        if energy["state"] == "high":
            desc_parts.append("abundant energy")

        description = (
            "A " + ", ".join(desc_parts) if desc_parts else "Complex biological state"
        )

        # Recommend action
        if stress["level"] > 0.6:
            action = "Activate stress adaptation protocols"
        elif energy["state"] == "low":
            action = "Initiate energy restoration"
        else:
            action = "Maintain current harmonious state"

        return {
            "primary_symbol": primary,
            "all_symbols": symbols,
            "description": description,
            "action": action,
            "coherence": coherence,
        }

    def generate_summary(self):
        """Generate summary of bio-symbolic demo."""
        summary = {
            "demo_id": f"BIO_SYM_DEMO_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "total_biological_states": len(self.bio_states),
            "total_symbolic_mappings": len(self.symbolic_mappings),
            "total_integration_events": len(self.integration_events),
            "demo_sections": [
                "Biological Rhythms",
                "Mitochondrial Energy",
                "DNA-GLYPH Mapping",
                "Stress Response",
                "Homeostatic Balance",
                "Bio-Symbolic Dreams",
                "Full Integration",
            ],
        }

        # Save summary
        summary_file = Path("logs") / "bio_symbolic_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        # Save detailed data
        detailed_data = {
            "bio_states": self.bio_states,
            "symbolic_mappings": self.symbolic_mappings,
            "integration_events": self.integration_events,
        }

        data_file = Path("logs") / "bio_symbolic_data.json"
        with open(data_file, "w") as f:
            json.dump(detailed_data, f, indent=2)

        logger.info(f"\n📊 Summary saved to: {summary_file}")
        logger.info(f"📊 Detailed data saved to: {data_file}")


def main():
    """Run the bio-symbolic demonstration."""
    demo = BioSymbolicDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
