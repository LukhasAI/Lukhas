#!/usr/bin/env python3
"""
Advanced Memory Fold Test Suite
Tests with data injection, images, and controlled scenarios.
"""

import json
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.core import MemoryFoldSystem


class AdvancedMemoryFoldTester:
    """Advanced test suite for Memory Fold System."""

    def __init__(self):
        self.memory_system = MemoryFoldSystem()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "scenarios": {},
            "performance": {},
            "errors": [],
        }

    def log_result(
        self, test_name: str, passed: bool, details: Any = None, error: str = None
    ):
        """Log test results."""
        if passed:
            self.test_results["passed"] += 1
            status = "✅ PASSED"
        else:
            self.test_results["failed"] += 1
            status = "❌ FAILED"
            if error:
                self.test_results["errors"].append({"test": test_name, "error": error})

        self.test_results["scenarios"][test_name] = {
            "status": status,
            "details": details,
            "error": error,
        }

        print(f"{status} - {test_name}")
        if error:
            print(f"  Error: {error}")

    def test_scenario_1_mass_data_injection(self):
        """Test 1: Mass data injection with varied emotions."""
        print("\n=== Scenario 1: Mass Data Injection ===")
        start_time = time.time()

        # Generate test data
        emotions = [
            "joy",
            "sadness",
            "fear",
            "anger",
            "trust",
            "surprise",
            "anticipation",
            "disgust",
            "peaceful",
            "anxious",
            "curious",
            "excited",
            "reflective",
            "nostalgic",
            "hopeful",
            "confused",
        ]

        contexts = [
            "Discovered a new algorithm that solves the problem",
            "Lost important data due to system crash",
            "Detected potential security breach in the system",
            "Frustrated by continuous integration failures",
            "Successfully deployed to production",
            "Unexpected behavior in quantum module",
            "Planning next sprint objectives",
            "Code review revealed serious issues",
            "Achieved perfect test coverage",
            "Worried about scalability limits",
            "Exploring new framework possibilities",
            "Team celebration after major release",
            "Thinking about system architecture",
            "Remembering the early prototype days",
            "Optimistic about future improvements",
            "Unclear requirements from stakeholders",
        ]

        created_memories = []

        try:
            # Inject 100 memories
            for i in range(100):
                emotion = random.choice(emotions)
                context = random.choice(contexts)

                memory = self.memory_system.create_memory_fold(
                    emotion=emotion,
                    context_snippet=f"[Test {i}] {context}",
                    user_id=f"test_user_{i % 5}",  # 5 different users
                    metadata={
                        "test_id": i,
                        "batch": "mass_injection",
                        "timestamp_offset": i * 3600,  # Spread over time
                    },
                )
                created_memories.append(memory)

            elapsed = time.time() - start_time

            # Verify all were created
            stats = self.memory_system.get_system_statistics()

            self.log_result(
                "Mass Data Injection",
                passed=len(created_memories) == 100,
                details={
                    "memories_created": len(created_memories),
                    "total_in_db": stats["total_folds"],
                    "time_elapsed": f"{elapsed:.2f}s",
                    "rate": f"{100/elapsed:.1f} memories/second",
                },
            )

            self.test_results["performance"]["mass_injection"] = {
                "count": 100,
                "time": elapsed,
                "rate": 100 / elapsed,
            }

        except Exception as e:
            self.log_result("Mass Data Injection", False, error=str(e))

    def test_scenario_2_emotional_clustering(self):
        """Test 2: Emotional clustering and similarity patterns."""
        print("\n=== Scenario 2: Emotional Clustering Analysis ===")

        try:
            # Test emotional distances between all primary emotions
            primary_emotions = [
                "joy",
                "trust",
                "fear",
                "surprise",
                "sadness",
                "disgust",
                "anger",
                "anticipation",
            ]

            distance_matrix = {}

            for em1 in primary_emotions:
                distance_matrix[em1] = {}
                for em2 in primary_emotions:
                    distance = self.memory_system.calculate_emotion_distance(em1, em2)
                    distance_matrix[em1][em2] = round(distance, 3)

            # Find closest pairs
            closest_pairs = []
            for em1 in primary_emotions:
                for em2 in primary_emotions:
                    if em1 < em2:  # Avoid duplicates
                        dist = distance_matrix[em1][em2]
                        closest_pairs.append((em1, em2, dist))

            closest_pairs.sort(key=lambda x: x[2])

            # Test clustering
            clusters = self.memory_system.create_emotion_clusters(tier_level=5)

            self.log_result(
                "Emotional Clustering",
                passed=True,
                details={
                    "closest_pairs": closest_pairs[:5],
                    "cluster_count": len(clusters),
                    "largest_cluster": max(len(v) for v in clusters.values()),
                },
            )

        except Exception as e:
            self.log_result("Emotional Clustering", False, error=str(e))

    def test_scenario_3_image_metadata_storage(self):
        """Test 3: Storing image data in memory metadata."""
        print("\n=== Scenario 3: Image Metadata Storage ===")

        try:
            # Create a simple test image (1x1 pixel, base64 encoded)
            # This is a tiny PNG: transparent 1x1 pixel
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

            # Create memory with image
            memory_with_image = self.memory_system.create_memory_fold(
                emotion="joy",
                context_snippet="Captured a beautiful sunset photo",
                user_id="photographer",
                metadata={
                    "type": "visual_memory",
                    "image_data": test_image_base64,
                    "image_metadata": {
                        "format": "png",
                        "size": "1x1",
                        "captured_at": datetime.utcnow().isoformat(),
                        "location": {"lat": 37.7749, "lon": -122.4194},
                        "tags": ["sunset", "nature", "photography"],
                    },
                },
            )

            # Verify storage
            recalled = self.memory_system.recall_memory_folds(
                user_id="photographer", user_tier=5, limit=1
            )

            image_retrieved = False
            if (
                recalled
                and recalled[0]["metadata"].get("image_data") == test_image_base64
            ):
                image_retrieved = True

            # Test multiple images
            image_memories = []
            for i in range(5):
                mem = self.memory_system.create_memory_fold(
                    emotion=random.choice(["joy", "peaceful", "excited"]),
                    context_snippet=f"Photo collection item {i}",
                    metadata={
                        "image_data": test_image_base64,
                        "image_id": f"img_{i}",
                        "collection": "test_collection",
                    },
                )
                image_memories.append(mem)

            self.log_result(
                "Image Metadata Storage",
                passed=image_retrieved,
                details={
                    "image_stored": True,
                    "image_retrieved": image_retrieved,
                    "image_size_bytes": len(test_image_base64),
                    "multiple_images": len(image_memories),
                },
            )

        except Exception as e:
            self.log_result("Image Metadata Storage", False, error=str(e))

    def test_scenario_4_temporal_patterns(self):
        """Test 4: Temporal pattern analysis and time-based recall."""
        print("\n=== Scenario 4: Temporal Pattern Analysis ===")

        try:
            # Create memories at different times of day
            time_patterns = {
                "morning": (6, 12),
                "afternoon": (12, 18),
                "evening": (18, 22),
                "night": (22, 6),
            }

            # Inject memories with specific timestamps
            now = datetime.utcnow()
            temporal_memories = []

            for period, (start_hour, end_hour) in time_patterns.items():
                for i in range(5):
                    # Calculate timestamp
                    if period == "night" and start_hour > end_hour:
                        hour = (
                            random.randint(22, 23)
                            if random.random() > 0.5
                            else random.randint(0, 5)
                        )
                    else:
                        hour = random.randint(start_hour, end_hour - 1)

                    timestamp = now.replace(hour=hour, minute=random.randint(0, 59))

                    # Create memory with manual timestamp (hack: modify after creation)
                    memory = self.memory_system.create_memory_fold(
                        emotion="neutral",
                        context_snippet=f"{period.capitalize()} activity",
                        metadata={"time_period": period, "manual_hour": hour},
                    )
                    temporal_memories.append(memory)

            # Test vision prompts for different times
            morning_prompt = self.memory_system.vision_manager.get_prompt_for_fold(
                {"emotion": "peaceful", "timestamp": now.replace(hour=8).isoformat()},
                user_tier=5,
            )

            night_prompt = self.memory_system.vision_manager.get_prompt_for_fold(
                {"emotion": "peaceful", "timestamp": now.replace(hour=23).isoformat()},
                user_tier=5,
            )

            self.log_result(
                "Temporal Pattern Analysis",
                passed=True,
                details={
                    "temporal_memories": len(temporal_memories),
                    "morning_context": morning_prompt["visual_metadata"][
                        "time_context"
                    ],
                    "night_context": night_prompt["visual_metadata"]["time_context"],
                    "prompts_differ": morning_prompt != night_prompt,
                },
            )

        except Exception as e:
            self.log_result("Temporal Pattern Analysis", False, error=str(e))

    def test_scenario_5_stress_test_limits(self):
        """Test 5: Stress test system limits and edge cases."""
        print("\n=== Scenario 5: Stress Test & Edge Cases ===")

        edge_cases = []

        # Test 1: Empty context
        try:
            memory = self.memory_system.create_memory_fold(
                emotion="neutral",
                context_snippet="",
                metadata={"test": "empty_context"},
            )
            edge_cases.append(("Empty context", "✅ Handled"))
        except Exception as e:
            edge_cases.append(("Empty context", f"❌ Failed: {str(e)}"))

        # Test 2: Very long context
        try:
            long_context = "A" * 10000  # 10k characters
            memory = self.memory_system.create_memory_fold(
                emotion="neutral",
                context_snippet=long_context,
                metadata={"test": "long_context"},
            )
            edge_cases.append(("10k character context", "✅ Handled"))
        except Exception as e:
            edge_cases.append(("10k character context", f"❌ Failed: {str(e)}"))

        # Test 3: Unknown emotion
        try:
            memory = self.memory_system.create_memory_fold(
                emotion="quantum_superposition",
                context_snippet="Testing unknown emotion",
                metadata={"test": "unknown_emotion"},
            )
            edge_cases.append(("Unknown emotion", "✅ Handled (interpolated)"))
        except Exception as e:
            edge_cases.append(("Unknown emotion", f"❌ Failed: {str(e)}"))

        # Test 4: Special characters
        try:
            memory = self.memory_system.create_memory_fold(
                emotion="joy",
                context_snippet="Testing émojis 🎉 and spëcial çharacters ñ λ ∑ ∫",
                metadata={"test": "special_chars"},
            )
            edge_cases.append(("Special characters", "✅ Handled"))
        except Exception as e:
            edge_cases.append(("Special characters", f"❌ Failed: {str(e)}"))

        # Test 5: Rapid creation
        try:
            start = time.time()
            for i in range(50):
                self.memory_system.create_memory_fold(
                    emotion="neutral",
                    context_snippet=f"Rapid test {i}",
                )
            elapsed = time.time() - start
            rate = 50 / elapsed
            edge_cases.append(("Rapid creation (50)", f"✅ {rate:.1f}/sec"))
        except Exception as e:
            edge_cases.append(("Rapid creation", f"❌ Failed: {str(e)}"))

        # Test 6: Concurrent recall
        try:
            import concurrent.futures

            def recall_test():
                return self.memory_system.recall_memory_folds(limit=10)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(recall_test) for _ in range(10)]
                results = [f.result() for f in futures]

            edge_cases.append(("Concurrent recall", "✅ Handled"))
        except Exception as e:
            edge_cases.append(("Concurrent recall", f"❌ Failed: {str(e)}"))

        self.log_result(
            "Stress Test & Edge Cases",
            passed=all("✅" in result for _, result in edge_cases),
            details={"edge_cases": edge_cases},
        )

    def test_scenario_6_consolidation_patterns(self):
        """Test 6: Dream consolidation with specific patterns."""
        print("\n=== Scenario 6: Dream Consolidation Patterns ===")

        try:
            # Create a pattern of memories
            pattern_data = [
                # Morning routine pattern
                ("anticipation", "Waking up ready for the day"),
                ("peaceful", "Morning meditation completed"),
                ("joy", "Perfect cup of coffee"),
                # Work pattern
                ("curious", "Investigating new algorithm"),
                ("confused", "Bug in the quantum module"),
                ("determined", "Working through the problem"),
                ("excited", "Found the solution!"),
                # Evening pattern
                ("reflective", "Reviewing today's progress"),
                ("peaceful", "Relaxing with music"),
                ("nostalgic", "Thinking about past projects"),
            ]

            # Create memories
            for emotion, context in pattern_data:
                self.memory_system.create_memory_fold(
                    emotion=emotion,
                    context_snippet=context,
                    user_id="pattern_user",
                    metadata={"pattern": "daily_routine"},
                )

            # Run consolidation
            result = self.memory_system.dream_consolidate_memories(
                hours_limit=1, max_memories=20, user_id="pattern_user"  # Recent only
            )

            # Analyze themes
            themes_found = []
            if result["consolidated_memories"]:
                for consolidation in result["consolidated_memories"]:
                    themes_found.extend(consolidation.get("theme_count", []))

            self.log_result(
                "Dream Consolidation Patterns",
                passed=result["consolidated_count"] > 0,
                details={
                    "memories_processed": len(pattern_data),
                    "consolidations": result["consolidated_count"],
                    "themes_extracted": len(set(themes_found)),
                    "success": result["success"],
                },
            )

        except Exception as e:
            self.log_result("Dream Consolidation Patterns", False, error=str(e))

    def test_scenario_7_tier_access_control(self):
        """Test 7: Tier-based access control scenarios."""
        print("\n=== Scenario 7: Tier Access Control ===")

        try:
            # Create a rich memory
            rich_memory = self.memory_system.create_memory_fold(
                emotion="joy",
                context_snippet="Confidential: Project breakthrough achieved",
                user_id="admin",
                metadata={
                    "confidential": True,
                    "project": "AGI_CORE",
                    "breakthrough_details": "Solved consciousness recursion",
                },
            )

            # Test different tier accesses
            tier_results = {}

            for tier in range(6):
                memories = self.memory_system.recall_memory_folds(
                    user_id="admin", user_tier=tier, limit=1
                )

                if memories:
                    memory = memories[0]
                    tier_results[f"tier_{tier}"] = {
                        "has_context": "context" in memory
                        and memory["context"] != "[Context Hidden - Tier 2+ Required]",
                        "has_emotion_vector": "emotion_vector" in memory,
                        "has_metadata": bool(memory.get("metadata")),
                        "has_vision": "vision_prompt" in memory,
                    }
                else:
                    tier_results[f"tier_{tier}"] = "No access"

            # Verify tier restrictions work
            tier_0_restricted = not tier_results["tier_0"]["has_context"]
            tier_5_full = all(tier_results["tier_5"].values())

            self.log_result(
                "Tier Access Control",
                passed=tier_0_restricted and tier_5_full,
                details={
                    "tier_restrictions": tier_results,
                    "tier_0_restricted": tier_0_restricted,
                    "tier_5_full_access": tier_5_full,
                },
            )

        except Exception as e:
            self.log_result("Tier Access Control", False, error=str(e))

    def test_scenario_8_emotional_evolution(self):
        """Test 8: Track emotional evolution over time."""
        print("\n=== Scenario 8: Emotional Evolution Tracking ===")

        try:
            # Simulate emotional journey
            emotional_journey = [
                ("anxious", "Starting new project, feeling uncertain"),
                ("curious", "Exploring the problem space"),
                ("confused", "Hit unexpected complexity"),
                ("frustrated", "Several approaches failed"),
                ("determined", "Not giving up, trying new angle"),
                ("excited", "Breakthrough moment!"),
                ("joy", "Solution works perfectly"),
                ("peaceful", "Satisfied with achievement"),
                ("reflective", "Learning from the journey"),
            ]

            # Create timeline
            journey_memories = []
            base_time = datetime.utcnow() - timedelta(hours=len(emotional_journey))

            for i, (emotion, context) in enumerate(emotional_journey):
                memory = self.memory_system.create_memory_fold(
                    emotion=emotion,
                    context_snippet=context,
                    user_id="journey_user",
                    metadata={
                        "journey_step": i,
                        "journey_id": "problem_solving",
                        "timestamp_order": i,
                    },
                )
                journey_memories.append(memory)

            # Calculate emotional trajectory
            trajectory = []
            for i in range(len(journey_memories) - 1):
                current = emotional_journey[i][0]
                next_emotion = emotional_journey[i + 1][0]
                distance = self.memory_system.calculate_emotion_distance(
                    current, next_emotion
                )
                trajectory.append(
                    {
                        "from": current,
                        "to": next_emotion,
                        "distance": round(distance, 3),
                    }
                )

            # Find biggest emotional shifts
            trajectory.sort(key=lambda x: x["distance"], reverse=True)
            biggest_shifts = trajectory[:3]

            self.log_result(
                "Emotional Evolution Tracking",
                passed=True,
                details={
                    "journey_length": len(emotional_journey),
                    "biggest_shifts": biggest_shifts,
                    "total_distance": sum(t["distance"] for t in trajectory),
                },
            )

        except Exception as e:
            self.log_result("Emotional Evolution Tracking", False, error=str(e))

    def test_scenario_9_search_performance(self):
        """Test 9: Search and retrieval performance."""
        print("\n=== Scenario 9: Search Performance ===")

        try:
            # Ensure we have enough data
            if self.memory_system.get_system_statistics()["total_folds"] < 100:
                # Add more if needed
                for i in range(50):
                    self.memory_system.create_memory_fold(
                        emotion=random.choice(["joy", "trust", "fear"]),
                        context_snippet=f"Performance test memory {i}",
                    )

            performance_results = {}

            # Test 1: Basic recall
            start = time.time()
            results = self.memory_system.recall_memory_folds(limit=100)
            performance_results["basic_recall_100"] = time.time() - start

            # Test 2: Filtered recall
            start = time.time()
            results = self.memory_system.recall_memory_folds(
                filter_emotion="joy", limit=50
            )
            performance_results["filtered_recall_50"] = time.time() - start

            # Test 3: Enhanced recall with similarity
            start = time.time()
            results = self.memory_system.enhanced_recall_memory_folds(
                target_emotion="peaceful", emotion_threshold=0.5, max_results=20
            )
            performance_results["enhanced_recall_20"] = time.time() - start

            # Test 4: Emotional distance calculations
            start = time.time()
            for _ in range(100):
                self.memory_system.calculate_emotion_distance("joy", "sadness")
            performance_results["100_distance_calcs"] = time.time() - start

            # Test 5: Statistics
            start = time.time()
            stats = self.memory_system.get_system_statistics()
            performance_results["get_statistics"] = time.time() - start

            # All operations should be fast
            all_fast = all(t < 1.0 for t in performance_results.values())

            self.log_result(
                "Search Performance",
                passed=all_fast,
                details={
                    "operations": {
                        k: f"{v*1000:.1f}ms" for k, v in performance_results.items()
                    },
                    "all_under_1s": all_fast,
                },
            )

            self.test_results["performance"].update(performance_results)

        except Exception as e:
            self.log_result("Search Performance", False, error=str(e))

    def test_scenario_10_data_integrity(self):
        """Test 10: Data integrity and persistence."""
        print("\n=== Scenario 10: Data Integrity ===")

        try:
            # Create test memory with specific data
            test_data = {
                "emotion": "trust",
                "context": "Data integrity test memory",
                "metadata": {
                    "test_id": "integrity_001",
                    "checksum": "abc123",
                    "nested": {"level1": {"level2": {"deep_value": "preserved"}}},
                    "array": [1, 2, 3, {"nested": "in_array"}],
                    "unicode": "Testing émojis 🎉 λ ∑",
                    "number": 3.14159,
                    "boolean": True,
                    "null_value": None,
                },
            }

            # Create memory
            created = self.memory_system.create_memory_fold(
                emotion=test_data["emotion"],
                context_snippet=test_data["context"],
                user_id="integrity_tester",
                metadata=test_data["metadata"],
            )

            # Recall it
            recalled = self.memory_system.recall_memory_folds(
                user_id="integrity_tester", user_tier=5, limit=1
            )

            integrity_checks = []

            if recalled:
                memory = recalled[0]

                # Check each field
                integrity_checks.append(
                    ("emotion", memory["emotion"] == test_data["emotion"])
                )
                integrity_checks.append(
                    ("context", memory["context"] == test_data["context"])
                )
                integrity_checks.append(("hash", len(memory["hash"]) == 64))  # SHA-256

                # Check metadata preservation
                if "metadata" in memory:
                    meta = memory["metadata"]
                    integrity_checks.append(
                        ("test_id", meta.get("test_id") == "integrity_001")
                    )
                    integrity_checks.append(
                        (
                            "nested_data",
                            meta.get("nested", {})
                            .get("level1", {})
                            .get("level2", {})
                            .get("deep_value")
                            == "preserved",
                        )
                    )
                    integrity_checks.append(
                        ("array", meta.get("array") == test_data["metadata"]["array"])
                    )
                    integrity_checks.append(
                        (
                            "unicode",
                            meta.get("unicode") == test_data["metadata"]["unicode"],
                        )
                    )
                    integrity_checks.append(("number", meta.get("number") == 3.14159))
                    integrity_checks.append(("boolean", meta.get("boolean") is True))

                # Check emotion vector
                if "emotion_vector" in memory:
                    vector = memory["emotion_vector"]
                    integrity_checks.append(("vector_shape", len(vector) == 3))
                    integrity_checks.append(
                        (
                            "vector_type",
                            all(isinstance(v, (int, float)) for v in vector),
                        )
                    )

            all_passed = all(check[1] for check in integrity_checks)

            self.log_result(
                "Data Integrity",
                passed=all_passed,
                details={"checks": integrity_checks, "all_passed": all_passed},
            )

        except Exception as e:
            self.log_result("Data Integrity", False, error=str(e))

    def run_all_tests(self):
        """Run all test scenarios."""
        print("=" * 60)
        print("LUKHAS Memory Fold System - Advanced Test Suite")
        print("=" * 60)

        # Run all test scenarios
        self.test_scenario_1_mass_data_injection()
        self.test_scenario_2_emotional_clustering()
        self.test_scenario_3_image_metadata_storage()
        self.test_scenario_4_temporal_patterns()
        self.test_scenario_5_stress_test_limits()
        self.test_scenario_6_consolidation_patterns()
        self.test_scenario_7_tier_access_control()
        self.test_scenario_8_emotional_evolution()
        self.test_scenario_9_search_performance()
        self.test_scenario_10_data_integrity()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(
            f"Total Tests: {self.test_results['passed'] + self.test_results['failed']}"
        )
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌")
        print(
            f"Success Rate: {self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100:.1f}%"
        )

        if self.test_results["errors"]:
            print("\n❌ ERRORS:")
            for error in self.test_results["errors"]:
                print(f"  - {error['test']}: {error['error']}")

        # Performance summary
        print("\n📊 PERFORMANCE METRICS:")
        if "mass_injection" in self.test_results["performance"]:
            perf = self.test_results["performance"]["mass_injection"]
            print(f"  - Mass injection rate: {perf['rate']:.1f} memories/second")

        for key, value in self.test_results["performance"].items():
            if key != "mass_injection" and isinstance(value, (int, float)):
                print(f"  - {key}: {value*1000:.1f}ms")

        # Save results
        self.save_results()

    def save_results(self):
        """Save test results to file."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_fold_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print(f"\n📁 Results saved to: {filename}")


if __name__ == "__main__":
    tester = AdvancedMemoryFoldTester()
    tester.run_all_tests()
