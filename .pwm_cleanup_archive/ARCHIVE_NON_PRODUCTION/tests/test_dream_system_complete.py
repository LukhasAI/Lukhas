#!/usr/bin/env python3
"""
LUKHAS Dream System - Comprehensive Test Suite
Generates dreams and creates logs to demonstrate system capabilities
"""

import asyncio
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dream.dream_data_sources import DreamDataCollector
from dream.dream_generator import generate_dream
from dream.dream_pipeline import UnifiedDreamPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/dream_system_test.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("ΛTRACE.test.dream_system")


class DreamSystemTester:
    """Comprehensive test suite for LUKHAS dream system."""

    def __init__(self):
        self.test_results = []
        self.dreams_generated = []
        self.log_dir = Path("logs/dreams")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self):
        """Run comprehensive dream system tests."""
        print("\n" + "=" * 70)
        print("🧪 LUKHAS DREAM SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        # Test 1: Data Collection
        await self.test_data_collection()

        # Test 2: Basic Dream Generation
        await self.test_basic_dream_generation()

        # Test 3: Narrative Dream Pipeline
        await self.test_narrative_dreams()

        # Test 4: Oracle Dreams
        await self.test_oracle_dreams()

        # Test 5: Symbolic Dreams
        await self.test_symbolic_dreams()

        # Test 6: Multi-Modal Dreams (if OpenAI available)
        await self.test_multimodal_dreams()

        # Test 7: Dream Sequences
        await self.test_dream_sequences()

        # Test 8: Memory Integration
        await self.test_memory_integration()

        # Generate reports
        self.generate_test_report()
        self.generate_dream_analysis()

        print("\n✅ All tests completed!")
        print(f"📊 Generated {len(self.dreams_generated)} dreams")
        print(f"📁 Logs saved to: {self.log_dir}")

    async def test_data_collection(self):
        """Test dream data collection from all sources."""
        print("\n📊 Test 1: Dream Data Collection")
        print("-" * 50)

        try:
            collector = DreamDataCollector()

            # Collect data with different contexts
            contexts = [
                {"mood": "creative", "activity": "exploration"},
                {"mood": "reflective", "activity": "meditation"},
                {"mood": "energetic", "activity": "problem_solving"},
            ]

            for i, context in enumerate(contexts):
                print(f"\n  Collecting data with context {i+1}...")
                data = await collector.collect_all_dream_data(context)

                # Log the collection
                log_file = self.log_dir / f"data_collection_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(data, f, indent=2)

                print(f"  ✓ Data collected from {len(data['sources'])} sources")
                print(
                    f"  ✓ Generated {len(data['synthesis']['dream_seeds'])} dream seeds"
                )

                self.test_results.append(
                    {
                        "test": "data_collection",
                        "context": context,
                        "sources_used": list(data["sources"].keys()),
                        "seeds_generated": len(data["synthesis"]["dream_seeds"]),
                        "status": "passed",
                    }
                )

            print("\n✅ Data collection test passed")

        except Exception as e:
            print(f"\n❌ Data collection test failed: {e}")
            logger.error("Data collection test failed", exc_info=True)
            self.test_results.append(
                {"test": "data_collection", "status": "failed", "error": str(e)}
            )

    async def test_basic_dream_generation(self):
        """Test basic dream generation without OpenAI."""
        print("\n🌙 Test 2: Basic Dream Generation")
        print("-" * 50)

        try:

            def mock_evaluate(action):
                return {"status": "allowed", "score": random.uniform(0.7, 1.0)}

            # Generate multiple basic dreams
            for i in range(5):
                print(f"\n  Generating basic dream {i+1}...")
                dream = generate_dream(mock_evaluate)

                # Log the dream
                dream["test_id"] = f"basic_{i+1}"
                dream["generated_at"] = datetime.utcnow().isoformat()
                self.dreams_generated.append(dream)

                log_file = self.log_dir / f"basic_dream_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(dream, f, indent=2)

                print(f"  ✓ Theme: {dream['narrative']['theme']}")
                print(f"  ✓ Emotion: {dream['narrative']['primary_emotion']}")
                print(f"  ✓ Atmosphere: {dream['narrative']['atmosphere']}")

            self.test_results.append(
                {"test": "basic_generation", "dreams_generated": 5, "status": "passed"}
            )

            print("\n✅ Basic dream generation test passed")

        except Exception as e:
            print(f"\n❌ Basic generation test failed: {e}")
            logger.error("Basic generation test failed", exc_info=True)
            self.test_results.append(
                {"test": "basic_generation", "status": "failed", "error": str(e)}
            )

    async def test_narrative_dreams(self):
        """Test narrative dream generation with pipeline."""
        print("\n📖 Test 3: Narrative Dream Pipeline")
        print("-" * 50)

        try:
            pipeline = UnifiedDreamPipeline(
                user_id="test_user", output_dir="logs/dreams/narrative"
            )

            prompts = [
                "a library where books dream their own stories",
                "conversations with the colors of sunset",
                "swimming through clouds of liquid music",
                "a garden where time grows on trees",
            ]

            for i, prompt in enumerate(prompts):
                print(f"\n  Generating narrative dream {i+1}: '{prompt[:40]}...'")

                dream = await pipeline.generate_dream_from_text(
                    prompt,
                    dream_type="narrative",
                    context={"test_run": True, "iteration": i},
                )

                dream["test_id"] = f"narrative_{i+1}"
                self.dreams_generated.append(dream)

                print(f"  ✓ Dream ID: {dream['dream_id']}")
                if "enhanced_narrative" in dream:
                    preview = dream["enhanced_narrative"]["full_text"][:100]
                    print(f"  ✓ Narrative: {preview}...")

                # Save dream log
                log_file = self.log_dir / f"narrative_dream_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(dream, f, indent=2)

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "narrative_pipeline",
                    "dreams_generated": len(prompts),
                    "status": "passed",
                }
            )

            print("\n✅ Narrative dream test passed")

        except Exception as e:
            print(f"\n❌ Narrative dream test failed: {e}")
            logger.error("Narrative dream test failed", exc_info=True)
            self.test_results.append(
                {"test": "narrative_pipeline", "status": "failed", "error": str(e)}
            )

    async def test_oracle_dreams(self):
        """Test oracle dream generation."""
        print("\n🔮 Test 4: Oracle Dreams")
        print("-" * 50)

        try:
            pipeline = UnifiedDreamPipeline(
                user_id="test_user", output_dir="logs/dreams/oracle"
            )

            oracle_requests = [
                (
                    "guidance for creative breakthrough",
                    {"mood": "stuck", "seeking": "inspiration"},
                ),
                (
                    "wisdom about relationships",
                    {"mood": "contemplative", "area": "connection"},
                ),
                ("insight for tomorrow", {"time": "evening", "state": "preparing"}),
            ]

            for i, (request, context) in enumerate(oracle_requests):
                print(f"\n  Generating oracle dream {i+1}: '{request}'")

                dream = await pipeline.generate_dream_from_text(
                    request, dream_type="oracle", context=context
                )

                dream["test_id"] = f"oracle_{i+1}"
                self.dreams_generated.append(dream)

                print(f"  ✓ Oracle ID: {dream['dream_id']}")
                if "message" in dream:
                    print(f"  ✓ Message: {dream['message']}")

                # Save oracle dream
                log_file = self.log_dir / f"oracle_dream_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(dream, f, indent=2)

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "oracle_dreams",
                    "dreams_generated": len(oracle_requests),
                    "status": "passed",
                }
            )

            print("\n✅ Oracle dream test passed")

        except Exception as e:
            print(f"\n❌ Oracle dream test failed: {e}")
            logger.error("Oracle dream test failed", exc_info=True)
            self.test_results.append(
                {"test": "oracle_dreams", "status": "failed", "error": str(e)}
            )

    async def test_symbolic_dreams(self):
        """Test symbolic dream generation."""
        print("\n🧬 Test 5: Symbolic Dreams")
        print("-" * 50)

        try:
            pipeline = UnifiedDreamPipeline(
                user_id="test_user", output_dir="logs/dreams/symbolic"
            )

            symbolic_themes = [
                "quantum entanglement of memories",
                "GLYPH resonance cascade",
                "consciousness wave collapse",
                "symbolic bridge formation",
            ]

            for i, theme in enumerate(symbolic_themes):
                print(f"\n  Generating symbolic dream {i+1}: '{theme}'")

                dream = await pipeline.generate_dream_from_text(
                    theme,
                    dream_type="symbolic",
                    context={"complexity": "high", "abstraction": "quantum"},
                )

                dream["test_id"] = f"symbolic_{i+1}"
                self.dreams_generated.append(dream)

                print(f"  ✓ Symbolic ID: {dream['dream_id']}")
                if "symbolic_elements" in dream:
                    elements = dream["symbolic_elements"]
                    print(f"  ✓ Primary GLYPH: {elements.get('primary_glyph')}")
                    print(f"  ✓ Quantum State: {elements.get('quantum_state')}")
                    print(f"  ✓ Coherence: {elements.get('coherence_factor')}")

                # Save symbolic dream
                log_file = self.log_dir / f"symbolic_dream_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(dream, f, indent=2)

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "symbolic_dreams",
                    "dreams_generated": len(symbolic_themes),
                    "status": "passed",
                }
            )

            print("\n✅ Symbolic dream test passed")

        except Exception as e:
            print(f"\n❌ Symbolic dream test failed: {e}")
            logger.error("Symbolic dream test failed", exc_info=True)
            self.test_results.append(
                {"test": "symbolic_dreams", "status": "failed", "error": str(e)}
            )

    async def test_multimodal_dreams(self):
        """Test multi-modal dream generation with OpenAI."""
        print("\n🎨 Test 6: Multi-Modal Dreams (OpenAI)")
        print("-" * 50)

        # Check if OpenAI is available
        import os

        if not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️ Skipping: OpenAI API key not set")
            self.test_results.append(
                {
                    "test": "multimodal_dreams",
                    "status": "skipped",
                    "reason": "No OpenAI API key",
                }
            )
            return

        try:
            # Test with limited generation to save API calls
            pipeline = UnifiedDreamPipeline(
                user_id="test_user",
                output_dir="logs/dreams/multimodal",
                use_openai=True,
            )

            # Generate one comprehensive multi-modal dream
            print("\n  Generating multi-modal dream...")

            dream = await pipeline.generate_dream_from_text(
                "a symphony of colors painting emotions in the sky",
                dream_type="narrative",
                context={"multimodal": True},
            )

            dream["test_id"] = "multimodal_1"
            self.dreams_generated.append(dream)

            print(f"  ✓ Multi-modal ID: {dream['dream_id']}")

            # Check generated components
            if "enhanced_narrative" in dream:
                print("  ✓ Enhanced narrative generated")
            if "generated_image" in dream:
                print(f"  ✓ Image generated: {dream['generated_image']['path']}")
            if "narration" in dream:
                print(f"  ✓ Audio generated: {dream['narration']['path']}")
            if "sora_prompt" in dream:
                print("  ✓ SORA video prompt created")

            # Save multi-modal dream
            log_file = self.log_dir / "multimodal_dream.json"
            with open(log_file, "w") as f:
                json.dump(dream, f, indent=2)

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "multimodal_dreams",
                    "status": "passed",
                    "components": list(dream.keys()),
                }
            )

            print("\n✅ Multi-modal dream test passed")

        except Exception as e:
            print(f"\n❌ Multi-modal dream test failed: {e}")
            logger.error("Multi-modal dream test failed", exc_info=True)
            self.test_results.append(
                {"test": "multimodal_dreams", "status": "failed", "error": str(e)}
            )

    async def test_dream_sequences(self):
        """Test generation of dream sequences."""
        print("\n🌊 Test 7: Dream Sequences")
        print("-" * 50)

        try:
            pipeline = UnifiedDreamPipeline(
                user_id="test_user", output_dir="logs/dreams/sequences"
            )

            # Create a connected dream sequence
            sequence_theme = "journey through the stages of transformation"
            stages = [
                "the cocoon of preparation",
                "the dissolution of old forms",
                "the void of potential",
                "the emergence of new patterns",
                "the integration of wisdom",
            ]

            sequence_dreams = []

            for i, stage in enumerate(stages):
                print(f"\n  Generating sequence dream {i+1}: '{stage}'")

                # Use previous dream context
                context = {
                    "sequence_position": i + 1,
                    "total_stages": len(stages),
                    "overall_theme": sequence_theme,
                }

                if i > 0:
                    # Reference previous dream
                    context["previous_stage"] = stages[i - 1]
                    context["continuity"] = True

                dream = await pipeline.generate_dream_from_text(
                    stage, dream_type="narrative", context=context
                )

                dream["test_id"] = f"sequence_{i+1}"
                dream["sequence_info"] = {
                    "position": i + 1,
                    "stage": stage,
                    "theme": sequence_theme,
                }

                sequence_dreams.append(dream)
                self.dreams_generated.append(dream)

                print(f"  ✓ Stage {i+1} dream generated")

            # Save sequence
            sequence_file = self.log_dir / "dream_sequence.json"
            with open(sequence_file, "w") as f:
                json.dump(
                    {
                        "theme": sequence_theme,
                        "stages": stages,
                        "dreams": sequence_dreams,
                        "generated_at": datetime.utcnow().isoformat(),
                    },
                    f,
                    indent=2,
                )

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "dream_sequences",
                    "sequence_length": len(stages),
                    "status": "passed",
                }
            )

            print("\n✅ Dream sequence test passed")

        except Exception as e:
            print(f"\n❌ Dream sequence test failed: {e}")
            logger.error("Dream sequence test failed", exc_info=True)
            self.test_results.append(
                {"test": "dream_sequences", "status": "failed", "error": str(e)}
            )

    async def test_memory_integration(self):
        """Test dream generation with memory integration."""
        print("\n🧠 Test 8: Memory Integration")
        print("-" * 50)

        try:
            # Simulate memory-influenced dreams
            memory_contexts = [
                {
                    "memory_type": "episodic",
                    "memory_content": "childhood discovery of a hidden garden",
                    "emotional_valence": 0.8,
                    "age": "distant",
                },
                {
                    "memory_type": "emotional",
                    "memory_content": "feeling of accomplishment after solving puzzle",
                    "emotional_valence": 0.9,
                    "age": "recent",
                },
                {
                    "memory_type": "procedural",
                    "memory_content": "the rhythm of creating art",
                    "emotional_valence": 0.7,
                    "age": "recurring",
                },
            ]

            pipeline = UnifiedDreamPipeline(
                user_id="test_user", output_dir="logs/dreams/memory"
            )

            for i, memory_context in enumerate(memory_contexts):
                print(f"\n  Generating memory-influenced dream {i+1}...")
                print(f"    Memory: {memory_context['memory_content']}")

                # Create dream prompt based on memory
                prompt = f"dream inspired by {memory_context['memory_content']}"

                dream = await pipeline.generate_dream_from_text(
                    prompt,
                    dream_type="narrative",
                    context={"memory_integration": memory_context},
                )

                dream["test_id"] = f"memory_{i+1}"
                dream["memory_source"] = memory_context
                self.dreams_generated.append(dream)

                print(f"  ✓ Memory dream generated: {dream['dream_id']}")

                # Save memory dream
                log_file = self.log_dir / f"memory_dream_{i+1}.json"
                with open(log_file, "w") as f:
                    json.dump(dream, f, indent=2)

            await pipeline.close()

            self.test_results.append(
                {
                    "test": "memory_integration",
                    "dreams_generated": len(memory_contexts),
                    "status": "passed",
                }
            )

            print("\n✅ Memory integration test passed")

        except Exception as e:
            print(f"\n❌ Memory integration test failed: {e}")
            logger.error("Memory integration test failed", exc_info=True)
            self.test_results.append(
                {"test": "memory_integration", "status": "failed", "error": str(e)}
            )

    def generate_test_report(self):
        """Generate comprehensive test report."""
        report = {
            "test_run_id": f"TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(self.test_results),
            "tests_passed": sum(
                1 for t in self.test_results if t["status"] == "passed"
            ),
            "tests_failed": sum(
                1 for t in self.test_results if t["status"] == "failed"
            ),
            "tests_skipped": sum(
                1 for t in self.test_results if t["status"] == "skipped"
            ),
            "total_dreams_generated": len(self.dreams_generated),
            "test_results": self.test_results,
            "dream_types_generated": self._count_dream_types(),
        }

        # Save test report
        report_file = self.log_dir / "test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 70)
        print(f"Total Tests Run: {report['total_tests']}")
        print(f"Tests Passed: {report['tests_passed']}")
        print(f"Tests Failed: {report['tests_failed']}")
        print(f"Tests Skipped: {report['tests_skipped']}")
        print(f"Total Dreams Generated: {report['total_dreams_generated']}")

        print("\nDream Types Generated:")
        for dtype, count in report["dream_types_generated"].items():
            print(f"  - {dtype}: {count}")

    def generate_dream_analysis(self):
        """Generate analysis of all generated dreams."""
        analysis = {
            "analysis_id": f"ANALYSIS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "total_dreams": len(self.dreams_generated),
            "themes": self._analyze_themes(),
            "emotions": self._analyze_emotions(),
            "narrative_quality": self._analyze_narratives(),
            "symbolic_elements": self._analyze_symbolic_elements(),
        }

        # Save analysis
        analysis_file = self.log_dir / "dream_analysis.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)

        # Save individual dream summaries
        summaries = []
        for dream in self.dreams_generated:
            summary = {
                "dream_id": dream.get("dream_id", "unknown"),
                "test_id": dream.get("test_id", "unknown"),
                "type": dream.get("type", "unknown"),
                "has_narrative": "narrative" in dream,
                "has_enhanced_narrative": "enhanced_narrative" in dream,
                "has_image": "generated_image" in dream,
                "has_audio": "narration" in dream,
                "theme": dream.get("narrative", {}).get("theme", "N/A"),
                "emotion": dream.get("narrative", {}).get("primary_emotion", "N/A"),
            }
            summaries.append(summary)

        summaries_file = self.log_dir / "dream_summaries.json"
        with open(summaries_file, "w") as f:
            json.dump(summaries, f, indent=2)

        print(f"\n📊 Dream analysis saved to: {analysis_file}")
        print(f"📋 Dream summaries saved to: {summaries_file}")

    def _count_dream_types(self):
        """Count dreams by type."""
        type_counts = {}
        for dream in self.dreams_generated:
            dtype = dream.get("type", "unknown")
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        return type_counts

    def _analyze_themes(self):
        """Analyze themes across all dreams."""
        themes = []
        for dream in self.dreams_generated:
            if "narrative" in dream and "theme" in dream["narrative"]:
                themes.append(dream["narrative"]["theme"])

        # Count unique themes
        unique_themes = list(set(themes))
        return {
            "total_themes": len(themes),
            "unique_themes": len(unique_themes),
            "most_common": unique_themes[:5] if unique_themes else [],
        }

    def _analyze_emotions(self):
        """Analyze emotions across all dreams."""
        emotions = []
        for dream in self.dreams_generated:
            if "narrative" in dream and "primary_emotion" in dream["narrative"]:
                emotions.append(dream["narrative"]["primary_emotion"])

        # Count emotion frequencies
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        return {
            "total_emotions": len(emotions),
            "unique_emotions": len(set(emotions)),
            "distribution": emotion_counts,
        }

    def _analyze_narratives(self):
        """Analyze narrative quality metrics."""
        narratives = 0
        enhanced_narratives = 0
        total_length = 0

        for dream in self.dreams_generated:
            if "narrative" in dream:
                narratives += 1
            if "enhanced_narrative" in dream:
                enhanced_narratives += 1
                text = dream["enhanced_narrative"].get("full_text", "")
                total_length += len(text)

        avg_length = (
            total_length / enhanced_narratives if enhanced_narratives > 0 else 0
        )

        return {
            "dreams_with_narrative": narratives,
            "dreams_with_enhanced_narrative": enhanced_narratives,
            "average_narrative_length": round(avg_length),
        }

    def _analyze_symbolic_elements(self):
        """Analyze symbolic elements in dreams."""
        symbolic_dreams = 0
        glyphs_used = []
        quantum_states = []

        for dream in self.dreams_generated:
            if "symbolic_elements" in dream:
                symbolic_dreams += 1
                elements = dream["symbolic_elements"]
                if "primary_glyph" in elements:
                    glyphs_used.append(elements["primary_glyph"])
                if "quantum_state" in elements:
                    quantum_states.append(elements["quantum_state"])

        return {
            "symbolic_dreams": symbolic_dreams,
            "unique_glyphs": list(set(glyphs_used)),
            "quantum_states": list(set(quantum_states)),
        }


async def main():
    """Run the comprehensive dream system test suite."""
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Run tests
    tester = DreamSystemTester()
    await tester.run_all_tests()

    print("\n🎉 Dream system testing complete!")
    print("📂 Check the logs/dreams directory for all generated content")


if __name__ == "__main__":
    asyncio.run(main())
