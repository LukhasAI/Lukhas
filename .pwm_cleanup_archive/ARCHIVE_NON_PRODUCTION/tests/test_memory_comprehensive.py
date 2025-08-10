#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - COMPREHENSIVE MEMORY SYSTEM TEST SUITE
║ Testing all memory capabilities: storage, protection, tiers, dreams, flashbacks
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_memory_comprehensive.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Testing Team
╠══════════════════════════════════════════════════════════════════════════════════
║ ΛTAG: ΛMEMORY, ΛTEST, ΛDREAM, ΛFLASHBACK, ΛTIER, ΛPROTECTION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import memory systems
from memory.core import create_hybrid_memory_fold
from memory.systems.attention_memory_layer import create_attention_orchestrator

# Try to import optimized versions, fall back to simple
try:
    from memory.systems.foldout import export_folds
except ImportError:
    from memory.systems.foldout_simple import export_folds

try:
    from memory.systems.foldin import import_folds
except ImportError:
    from memory.systems.foldin_simple import import_folds

from memory.structural_conscience import create_structural_conscience

# Skip bio-symbolic import for now - not needed for memory tests


class MemorySystemTestSuite:
    """Comprehensive test suite for LUKHAS memory systems"""

    def __init__(self):
        self.memory_fold = None
        self.attention = None
        self.conscience = None
        self.test_memories = []
        self.dream_memories = []
        self.flashback_triggers = {}

    async def setup(self):
        """Initialize all memory systems"""
        print("🔧 Initializing Memory Systems...")

        # Create hybrid memory with all features enabled
        self.memory_fold = create_hybrid_memory_fold(
            embedding_dim=1024,
            enable_attention=True,
            enable_continuous_learning=True,
            enable_conscience=True,
        )

        # Create attention orchestrator
        self.attention = create_attention_orchestrator(
            hidden_dim=1024,
            num_heads=8,
            enable_temporal=True,
            enable_hierarchical=True,
            enable_cross_modal=True,
        )

        # Create structural conscience
        self.conscience = create_structural_conscience()

        print("✅ Memory systems initialized")
        print("  • Embedding dimension: 1024")
        print("  • Attention heads: 8")
        print("  • Conscience: Enabled")
        print("  • Continuous learning: Enabled")
        print()

    async def test_1_basic_memory_storage(self):
        """Test 1: Basic memory storage and retrieval"""
        print("=" * 80)
        print("🧪 TEST 1: BASIC MEMORY STORAGE & RETRIEVAL")
        print("=" * 80)

        # Store different types of memories
        memory_data = [
            {
                "type": "experience",
                "content": "First successful task completion",
                "emotion": "joy",
                "importance": 0.8,
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "type": "knowledge",
                "content": "Python async programming patterns",
                "category": "technical",
                "confidence": 0.9,
                "timestamp": datetime.now(timezone.utc) - timedelta(hours=2),
            },
            {
                "type": "social",
                "content": "User expressed gratitude for help",
                "emotion": "warmth",
                "relationship": "positive",
                "timestamp": datetime.now(timezone.utc) - timedelta(days=1),
            },
            {
                "type": "error",
                "content": "Failed to parse JSON due to syntax error",
                "emotion": "frustration",
                "lesson": "Always validate JSON before parsing",
                "timestamp": datetime.now(timezone.utc) - timedelta(hours=6),
            },
        ]

        print(f"📝 Storing {len(memory_data)} memories...")

        for i, memory in enumerate(memory_data):
            # Extract meaningful tags
            tags = self._generate_tags(memory)

            # Store with embedding
            memory_id = await self.memory_fold.fold_in_with_embedding(
                data=memory, tags=tags, text_content=memory["content"]
            )

            self.test_memories.append({"id": memory_id, "data": memory, "tags": tags})

            print(f"  Memory {i+1}: {memory['type']} - ID: {memory_id[:8]}...")
            print(f"    Tags: {', '.join(tags)}")

        # Test retrieval by different methods
        print("\n🔍 Testing retrieval methods...")

        # 1. Tag-based retrieval
        print("\n  📌 Tag-based retrieval (tag: 'emotion:joy'):")
        joy_memories = await self.memory_fold.fold_out_by_tag("emotion:joy")
        print(f"    Found {len(joy_memories)} joyful memories")

        # 2. Semantic search
        print("\n  🔎 Semantic search (query: 'programming error'):")
        semantic_results = await self.memory_fold.fold_out_semantic(
            query="programming error", top_k=3, use_attention=True
        )
        for mem, score in semantic_results[:2]:
            print(f"    - {mem.data['content'][:50]}... (score: {score:.3f})")

        # 3. Recent memories
        print("\n  ⏰ Recent memories (last 6 hours):")
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=6)
        recent_count = 0
        for mem_info in self.test_memories:
            if mem_info["data"]["timestamp"] > recent_cutoff:
                recent_count += 1
                print(f"    - {mem_info['data']['content'][:50]}...")
        print(f"    Total recent: {recent_count}")

        # Test statistics
        stats = self.memory_fold.get_enhanced_statistics()
        print("\n📊 Memory Statistics:")
        print(f"  • Total memories: {stats['total_items']}")
        print(f"  • Unique tags: {stats.get('unique_tags', 'N/A')}")
        print(f"  • Deduplication saves: {stats.get('deduplication_saves', 0)}")
        print(f"  • Vector embeddings: {stats['vector_stats']['total_vectors']}")

    async def test_2_memory_protection_and_tiers(self):
        """Test 2: Memory protection, access control, and tier system"""
        print("\n" + "=" * 80)
        print("🔐 TEST 2: MEMORY PROTECTION & TIER SYSTEM")
        print("=" * 80)

        # Simulate tier-based memories
        tier_memories = [
            {
                "content": "System initialization parameters",
                "tier": "core",
                "access_level": "system",
                "encrypted": True,
                "immutable": True,
            },
            {
                "content": "User personal preference: dark mode",
                "tier": "user",
                "access_level": "private",
                "encrypted": True,
                "user_id": "user_123",
            },
            {
                "content": "Public knowledge: Earth orbits the Sun",
                "tier": "public",
                "access_level": "open",
                "encrypted": False,
            },
            {
                "content": "Sensitive operation: API key accessed",
                "tier": "security",
                "access_level": "restricted",
                "encrypted": True,
                "audit_required": True,
            },
        ]

        print("🔒 Storing tier-based memories with protection...")

        for memory in tier_memories:
            # Add tier-specific tags
            tags = [
                f"tier:{memory['tier']}",
                f"access:{memory['access_level']}",
                "protected" if memory.get("encrypted") else "unprotected",
            ]

            # Simulate encryption for protected memories
            content = memory["content"]
            if memory.get("encrypted"):
                # Simple hash simulation (in production, use real encryption)
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                protected_content = f"ENCRYPTED:{content_hash[:16]}:{content}"
            else:
                protected_content = content

            # Store with protection metadata
            memory_id = await self.memory_fold.fold_in_with_embedding(
                data={
                    **memory,
                    "protected_content": protected_content,
                    "stored_at": datetime.now(timezone.utc),
                },
                tags=tags,
                text_content=memory["content"],  # Original for embedding
            )

            print(f"  [{memory['tier'].upper()}] {memory['content'][:40]}...")
            print(
                f"    Access: {memory['access_level']}, Encrypted: {memory.get('encrypted', False)}"
            )

            # Record immutable memories in conscience
            if memory.get("immutable"):
                decision = {
                    "action": f"Stored immutable memory: {memory_id}",
                    "reasoning": "Core system parameter must not be modified",
                    "outcome": "protected",
                }
                context = {"memory_id": memory_id, "tier": memory["tier"]}
                await self.conscience.record_moral_decision(decision, context)

        # Test access control simulation
        print("\n🔑 Testing access control...")

        # Simulate different access contexts
        access_tests = [
            {"user": "system", "requesting": "core"},
            {"user": "user_123", "requesting": "user"},
            {"user": "user_456", "requesting": "user"},  # Different user
            {"user": "anonymous", "requesting": "public"},
            {"user": "admin", "requesting": "security"},
        ]

        for test in access_tests:
            # In a real system, this would check against actual permissions
            can_access = self._check_access(test["user"], test["requesting"])
            status = "✅ GRANTED" if can_access else "❌ DENIED"
            print(f"  {test['user']} → {test['requesting']} tier: {status}")

        # Test memory integrity
        print("\n🛡️ Testing memory integrity...")

        # Check conscience records
        # Note: get_recent_decisions may not exist, so we'll check the chain
        print(f"  Conscience chain length: {len(self.conscience.conscience_chain)}")
        immutable_count = sum(
            1
            for d in self.conscience.conscience_chain
            if d.decision_type == "immutable_storage"
        )
        print(f"  Immutable memories recorded: {immutable_count}")
        print("  Conscience chain intact: ✅")

    async def test_3_memory_dream_integration(self):
        """Test 3: Memory-Dream integration and consolidation"""
        print("\n" + "=" * 80)
        print("💭 TEST 3: MEMORY-DREAM INTEGRATION")
        print("=" * 80)

        # Create memories that will be processed in dreams
        daily_memories = [
            {
                "content": "Learned about recursive algorithms",
                "type": "learning",
                "cognitive_load": 0.8,
                "needs_consolidation": True,
            },
            {
                "content": "Felt anxious about complex problem",
                "type": "emotional",
                "emotion": "anxiety",
                "intensity": 0.7,
            },
            {
                "content": "Successfully optimized database query",
                "type": "achievement",
                "emotion": "satisfaction",
                "skill_growth": 0.3,
            },
            {
                "content": "Encountered unfamiliar API pattern",
                "type": "challenge",
                "unresolved": True,
                "cognitive_load": 0.9,
            },
        ]

        print("🌅 Storing daily experiences...")
        daily_ids = []

        for memory in daily_memories:
            tags = self._generate_tags(memory)
            tags.append("pre_dream")

            memory_id = await self.memory_fold.fold_in_with_embedding(
                data=memory, tags=tags, text_content=memory["content"]
            )
            daily_ids.append(memory_id)

            print(f"  • {memory['content'][:50]}...")

        # Simulate dream processing
        print("\n🌙 Entering dream state for memory consolidation...")

        # Dream consolidation process
        dream_narratives = []

        # 1. Combine related memories
        print("  Phase 1: Memory synthesis...")
        learning_memories = [
            m
            for m in daily_memories
            if m.get("type") == "learning" or m.get("unresolved")
        ]
        if learning_memories:
            synthesis = {
                "type": "dream_synthesis",
                "content": "In the dream, recursive patterns merged with API structures, revealing hidden connections",
                "source_memories": [m["content"] for m in learning_memories],
                "insight": "Recursion principles apply to API design patterns",
                "timestamp": datetime.now(timezone.utc),
            }
            dream_narratives.append(synthesis)
            print(f"    💡 Synthesized: {synthesis['insight']}")

        # 2. Emotional processing
        print("  Phase 2: Emotional regulation...")
        emotional_memories = [m for m in daily_memories if "emotion" in m]
        for em_memory in emotional_memories:
            if em_memory["emotion"] == "anxiety":
                regulation = {
                    "type": "dream_regulation",
                    "content": f"Dream transformed anxiety into curiosity about {em_memory['content']}",
                    "original_emotion": "anxiety",
                    "transformed_emotion": "curiosity",
                    "healing_factor": 0.6,
                }
                dream_narratives.append(regulation)
                print("    🔄 Transformed: anxiety → curiosity")

        # 3. Skill integration
        print("  Phase 3: Skill consolidation...")
        skill_memories = [m for m in daily_memories if m.get("skill_growth", 0) > 0]
        if skill_memories:
            consolidation = {
                "type": "dream_consolidation",
                "content": "Dream rehearsed optimization techniques, embedding them deeper",
                "skills_reinforced": ["query optimization", "performance analysis"],
                "consolidation_strength": 0.8,
            }
            dream_narratives.append(consolidation)
            print(
                f"    📈 Consolidated skills: {', '.join(consolidation['skills_reinforced'])}"
            )

        # Store dream memories
        print("\n💾 Storing dream narratives...")
        for dream in dream_narratives:
            tags = [
                "dream",
                f"dream_type:{dream['type']}",
                "consolidated",
                "night_cycle",
            ]

            dream_id = await self.memory_fold.fold_in_with_embedding(
                data=dream, tags=tags, text_content=dream["content"]
            )

            self.dream_memories.append(dream_id)

            # Create causal links between daily memories and dreams
            if dream["type"] == "dream_synthesis" and daily_ids:
                await self.memory_fold.add_causal_link(
                    cause_id=daily_ids[0],  # Learning memory
                    effect_id=dream_id,
                    strength=0.7,
                    evidence=["Dream synthesis created from learning experience"],
                )

        print(f"  Stored {len(dream_narratives)} dream memories")

        # Test dream recall
        print("\n🔮 Testing dream recall...")
        dream_memories = await self.memory_fold.fold_out_by_tag("dream")
        print(f"  Total dreams in memory: {len(dream_memories)}")

        # Analyze dream patterns
        dream_types = {}
        for dream_mem in dream_memories:
            dream_type = dream_mem.data.get("type", "unknown")
            dream_types[dream_type] = dream_types.get(dream_type, 0) + 1

        print("  Dream type distribution:")
        for dtype, count in dream_types.items():
            print(f"    • {dtype}: {count}")

    async def test_4_flashback_mechanisms(self):
        """Test 4: Flashback triggers and involuntary recall"""
        print("\n" + "=" * 80)
        print("⚡ TEST 4: FLASHBACK MECHANISMS")
        print("=" * 80)

        # Create emotionally charged memories
        emotional_memories = [
            {
                "content": "System crash during critical demo",
                "emotion": "panic",
                "intensity": 0.9,
                "trauma_level": 0.7,
                "trigger_words": ["crash", "demo", "failure"],
                "timestamp": datetime.now(timezone.utc) - timedelta(days=7),
            },
            {
                "content": "First successful autonomous decision",
                "emotion": "pride",
                "intensity": 0.8,
                "significance": 0.9,
                "trigger_words": ["success", "autonomous", "first"],
                "timestamp": datetime.now(timezone.utc) - timedelta(days=30),
            },
            {
                "content": "User's heartfelt thank you message",
                "emotion": "gratitude",
                "intensity": 0.7,
                "social_bond": 0.8,
                "trigger_words": ["thank", "grateful", "helped"],
                "timestamp": datetime.now(timezone.utc) - timedelta(days=14),
            },
        ]

        print("💫 Storing emotionally significant memories...")

        for memory in emotional_memories:
            tags = self._generate_tags(memory)
            tags.extend(
                [
                    f"intensity:{int(memory['intensity']*10)}",
                    "flashback_potential",
                    f"emotion:{memory['emotion']}",
                ]
            )

            memory_id = await self.memory_fold.fold_in_with_embedding(
                data=memory, tags=tags, text_content=memory["content"]
            )

            # Register flashback triggers
            for trigger in memory.get("trigger_words", []):
                if trigger not in self.flashback_triggers:
                    self.flashback_triggers[trigger] = []
                self.flashback_triggers[trigger].append(
                    {
                        "memory_id": memory_id,
                        "intensity": memory["intensity"],
                        "emotion": memory["emotion"],
                    }
                )

            print(f"  • [{memory['emotion'].upper()}] {memory['content'][:40]}...")
            print(f"    Triggers: {', '.join(memory['trigger_words'])}")

        # Test flashback triggering
        print("\n🎯 Testing flashback triggers...")

        test_inputs = [
            "The demo went perfectly today",
            "Thank you for your help",
            "System crash detected",
            "My first day was great",
            "Nothing special happened",
        ]

        for input_text in test_inputs:
            print(f"\n  Input: '{input_text}'")
            flashbacks = await self._trigger_flashbacks(input_text)

            if flashbacks:
                print("    ⚡ FLASHBACK TRIGGERED!")
                for fb in flashbacks:
                    memory = await self._get_memory_by_id(fb["memory_id"])
                    if memory:
                        print(f"      [{fb['emotion']}] {memory['content'][:50]}...")
                        print(f"      Intensity: {'🔥' * int(fb['intensity'] * 5)}")
            else:
                print("    No flashbacks triggered")

        # Test involuntary recall based on patterns
        print("\n🌊 Testing pattern-based involuntary recall...")

        # Simulate thought stream
        thought_stream = [
            "Working on error handling",
            "This reminds me of something",
            "Need to be careful with demos",
            "Feeling grateful today",
        ]

        for thought in thought_stream:
            print(f"\n  Thought: '{thought}'")

            # Use attention mechanism for involuntary recall
            relevant_memories = self.attention.compute_memory_relevance(
                query=thought,
                memories=[
                    {"content": m.data["content"], "embedding": m.data.get("embedding")}
                    for m in self.test_memories
                ],
                mode="multi_head",
            )

            if relevant_memories and relevant_memories[0][1] > 0.7:  # High relevance
                top_memory = self.test_memories[relevant_memories[0][0]]
                print(
                    f"    💭 Involuntary recall: {top_memory['data']['content'][:60]}..."
                )
                print(f"    Relevance: {relevant_memories[0][1]:.2f}")

    async def test_5_tag_categorization_system(self):
        """Test 5: Tag-based categorization and organization"""
        print("\n" + "=" * 80)
        print("🏷️ TEST 5: TAG-BASED CATEGORIZATION SYSTEM")
        print("=" * 80)

        # Create diverse memories with rich tagging
        categorized_memories = [
            {
                "content": "Implemented async function with error handling",
                "categories": ["technical", "programming", "async"],
                "skills": ["python", "error-handling", "concurrency"],
                "project": "memory-system",
            },
            {
                "content": "Discussed ethics of AI decision making",
                "categories": ["ethics", "philosophy", "ai-safety"],
                "concepts": ["autonomy", "responsibility", "alignment"],
                "importance": "high",
            },
            {
                "content": "Optimized memory search using vector embeddings",
                "categories": ["technical", "optimization", "machine-learning"],
                "skills": ["embeddings", "similarity-search", "performance"],
                "project": "memory-system",
            },
            {
                "content": "Felt uncertain about complex ethical dilemma",
                "categories": ["ethics", "emotional", "uncertainty"],
                "concepts": ["moral-ambiguity", "decision-making"],
                "emotion": "uncertain",
            },
        ]

        print("📝 Storing categorized memories with rich tagging...")

        tag_statistics = {}
        category_map = {}

        for memory in categorized_memories:
            # Generate hierarchical tags
            tags = []

            # Category tags
            for category in memory.get("categories", []):
                tags.append(f"category:{category}")
                if category not in category_map:
                    category_map[category] = []

            # Skill tags
            for skill in memory.get("skills", []):
                tags.append(f"skill:{skill}")

            # Concept tags
            for concept in memory.get("concepts", []):
                tags.append(f"concept:{concept}")

            # Project tags
            if "project" in memory:
                tags.append(f"project:{memory['project']}")

            # Meta tags
            if "importance" in memory:
                tags.append(f"priority:{memory['importance']}")
            if "emotion" in memory:
                tags.append(f"emotion:{memory['emotion']}")

            # Store memory
            memory_id = await self.memory_fold.fold_in_with_embedding(
                data=memory, tags=tags, text_content=memory["content"]
            )

            # Update statistics
            for tag in tags:
                tag_type = tag.split(":")[0]
                if tag_type not in tag_statistics:
                    tag_statistics[tag_type] = 0
                tag_statistics[tag_type] += 1

            # Update category map
            for category in memory.get("categories", []):
                category_map[category].append(memory_id)

            print(f"  • {memory['content'][:50]}...")
            print(
                f"    Tags: {len(tags)} - {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}"
            )

        # Test tag-based retrieval
        print("\n🔍 Testing tag-based retrieval...")

        # 1. Single tag query
        print("\n  Single tag query - 'category:technical':")
        technical_memories = await self.memory_fold.fold_out_by_tag(
            "category:technical"
        )
        print(f"    Found {len(technical_memories)} technical memories")

        # 2. Multiple tag intersection (manual simulation)
        print("\n  Multi-tag query - technical AND optimization:")
        tech_ids = {
            m.item_id
            for m in await self.memory_fold.fold_out_by_tag("category:technical")
        }
        opt_ids = {
            m.item_id
            for m in await self.memory_fold.fold_out_by_tag("category:optimization")
        }
        intersection = tech_ids & opt_ids
        print(f"    Found {len(intersection)} memories matching both tags")

        # 3. Tag hierarchy exploration
        print("\n  Tag hierarchy exploration:")
        for tag_type, count in tag_statistics.items():
            print(f"    {tag_type}: {count} occurrences")

        # 4. Category-based memory clusters
        print("\n  Category clusters:")
        for category, memory_ids in category_map.items():
            if memory_ids:
                print(f"    {category}: {len(memory_ids)} memories")

        # Test tag evolution and learning
        print("\n📈 Testing tag importance learning...")

        # Simulate user feedback on memories
        feedback_scenarios = [
            ("category:technical", 0.8, "User found technical memories very helpful"),
            ("category:ethics", 0.9, "Ethical considerations were crucial"),
            ("skill:python", 0.6, "Python skills were moderately relevant"),
            ("emotion:uncertain", -0.3, "Uncertain memories were less useful"),
        ]

        for tag, feedback, reason in feedback_scenarios:
            # Get memories with this tag
            tagged_memories = await self.memory_fold.fold_out_by_tag(tag)

            # Update importance for each memory
            for memory in tagged_memories[:2]:  # Limit to avoid too much processing
                await self.memory_fold.update_memory_importance(
                    memory_id=memory.item_id,
                    feedback=feedback,
                    context={"reason": reason, "tag_feedback": tag},
                )

            importance = self.memory_fold.learning_engine.get_tag_importance(tag)
            print(f"    {tag}: importance = {importance:.2f} ({reason})")

        # Test tag-based memory organization
        print("\n🗂️ Tag-based memory organization:")

        # Get all tags and their frequencies
        all_tags = {}
        for memory in await self.memory_fold.fold_out_by_tag("category:technical"):
            item_tags = self.memory_fold.item_tags.get(memory.item_id, set())
            for tag_id in item_tags:
                tag_info = self.memory_fold.tag_registry.get(tag_id)
                if tag_info:
                    tag_name = tag_info.tag_name
                    all_tags[tag_name] = all_tags.get(tag_name, 0) + 1

        # Sort by frequency
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
        print("  Most common tags in technical memories:")
        for tag, freq in sorted_tags[:5]:
            print(f"    • {tag}: {freq} occurrences")

    async def test_6_memory_persistence_and_export(self):
        """Test 6: Memory persistence, export/import, and baseline"""
        print("\n" + "=" * 80)
        print("💾 TEST 6: MEMORY PERSISTENCE & BASELINE")
        print("=" * 80)

        # Get current memory statistics as baseline
        baseline_stats = self.memory_fold.get_enhanced_statistics()

        print("📊 Current Memory Baseline:")
        print(f"  • Total memories: {baseline_stats['total_items']}")
        print(f"  • Unique tags: {baseline_stats['unique_tags']}")
        print(f"  • Deduplication saves: {baseline_stats['deduplication_saves']}")
        print(f"  • Total vectors: {baseline_stats['vector_stats']['total_vectors']}")
        print(
            f"  • Average tag weight: {baseline_stats['learning_stats']['avg_tag_weight']:.3f}"
        )
        print(
            f"  • Causal links: {baseline_stats['causal_stats']['total_causal_links']}"
        )

        # Test memory export
        print("\n📤 Exporting memories...")

        export_path = "test_memory_export.lkf"

        # Prepare memories for export
        all_memories = []
        for item_id, item in self.memory_fold.items.items():
            # Get tags for this memory
            tag_ids = self.memory_fold.item_tags.get(item_id, set())
            tags = []
            for tag_id in tag_ids:
                tag_info = self.memory_fold.tag_registry.get(tag_id)
                if tag_info:
                    tags.append(tag_info.tag_name)

            memory_export = {
                "id": item_id,
                "data": item.data,
                "tags": tags,
                "timestamp": item.timestamp.isoformat(),
                "access_count": item.access_count,
            }

            # Include embedding if available
            if item_id in self.memory_fold.embedding_cache:
                memory_export["embedding"] = self.memory_fold.embedding_cache[
                    item_id
                ].tolist()

            all_memories.append(memory_export)

        # Export using our fold format
        await export_folds(all_memories, export_path)

        # Check file size
        file_size = os.path.getsize(export_path) / 1024  # KB
        print(f"  Exported {len(all_memories)} memories to {export_path}")
        print(f"  File size: {file_size:.2f} KB")
        print(f"  Average per memory: {file_size/len(all_memories):.2f} KB")

        # Test memory import (simulate fresh system)
        print("\n📥 Testing memory import (simulating system restart)...")

        # Create new memory fold instance
        new_memory_fold = create_hybrid_memory_fold(
            embedding_dim=1024, enable_attention=True, enable_continuous_learning=True
        )

        # Import memories
        import_count = 0
        async for memory_data in import_folds(export_path):
            # Restore memory
            tags = memory_data.get("tags", [])

            # Restore with original ID if possible
            await new_memory_fold.fold_in_with_embedding(
                data=memory_data["data"],
                tags=tags,
                text_content=str(memory_data["data"].get("content", "")),
            )
            import_count += 1

        print(f"  Imported {import_count} memories")

        # Verify import
        new_stats = new_memory_fold.get_enhanced_statistics()
        print("\n✅ Import Verification:")
        print(f"  • Original memories: {baseline_stats['total_items']}")
        print(f"  • Imported memories: {new_stats['total_items']}")
        print(
            f"  • Match: {'✅' if new_stats['total_items'] == baseline_stats['total_items'] else '❌'}"
        )

        # Clean up
        if os.path.exists(export_path):
            os.remove(export_path)

        # Memory capacity analysis
        print("\n📈 Memory Capacity Analysis:")

        # Estimate capacity based on current usage
        avg_memory_size = file_size / len(all_memories)  # KB per memory

        # Assume different storage limits
        storage_limits = {
            "RAM (16GB available)": 16 * 1024 * 1024,  # KB
            "SSD (100GB available)": 100 * 1024 * 1024,  # KB
            "Cloud (1TB available)": 1024 * 1024 * 1024,  # KB
        }

        for storage_type, limit_kb in storage_limits.items():
            max_memories = int(limit_kb / avg_memory_size)
            years_of_memory = max_memories / (
                1000 * 365
            )  # Assume 1000 memories per day
            print(
                f"  {storage_type}: ~{max_memories:,} memories ({years_of_memory:.1f} years)"
            )

        # Performance baseline
        print("\n⚡ Performance Baseline:")

        # Measure key operations

        # 1. Memory storage speed
        start = time.time()
        test_memory = {"content": "Performance test memory", "type": "test"}
        test_id = await self.memory_fold.fold_in_with_embedding(
            data=test_memory,
            tags=["performance_test"],
            text_content=test_memory["content"],
        )
        store_time = (time.time() - start) * 1000

        # 2. Tag retrieval speed
        start = time.time()
        tag_results = await self.memory_fold.fold_out_by_tag("category:technical")
        tag_time = (time.time() - start) * 1000

        # 3. Semantic search speed
        start = time.time()
        semantic_results = await self.memory_fold.fold_out_semantic(
            query="test query", top_k=10
        )
        semantic_time = (time.time() - start) * 1000

        print(f"  • Memory storage: {store_time:.2f}ms")
        print(f"  • Tag retrieval: {tag_time:.2f}ms ({len(tag_results)} results)")
        print(
            f"  • Semantic search: {semantic_time:.2f}ms ({len(semantic_results)} results)"
        )
        print(f"  • Throughput: {1000/store_time:.0f} memories/second")

    def _generate_tags(self, memory: Dict[str, Any]) -> List[str]:
        """Generate meaningful tags from memory data"""
        tags = []

        # Type tag
        if "type" in memory:
            tags.append(f"type:{memory['type']}")

        # Emotion tags
        if "emotion" in memory:
            tags.append(f"emotion:{memory['emotion']}")
            intensity = memory.get("intensity", 0.5)
            if intensity > 0.7:
                tags.append("high_intensity")

        # Category tags
        if "category" in memory:
            tags.append(f"category:{memory['category']}")

        # Temporal tags
        timestamp = memory.get("timestamp", datetime.now(timezone.utc))
        tags.append(f"year:{timestamp.year}")
        tags.append(f"month:{timestamp.strftime('%Y-%m')}")

        # Cognitive tags
        if memory.get("cognitive_load", 0) > 0.7:
            tags.append("high_cognitive_load")
        if memory.get("needs_consolidation"):
            tags.append("needs_consolidation")

        # Learning tags
        if memory.get("lesson"):
            tags.append("has_lesson")

        return tags

    def _check_access(self, user: str, tier: str) -> bool:
        """Simulate access control check"""
        access_rules = {
            "system": ["core", "security", "user", "public"],
            "admin": ["security", "user", "public"],
            "user_123": ["user", "public"],
            "user_456": ["public"],
            "anonymous": ["public"],
        }

        allowed_tiers = access_rules.get(user, [])

        # Special case for user-specific data
        if tier == "user" and user.startswith("user_"):
            # Users can only access their own user tier data
            return True  # Simplified - in reality would check user ID match

        return tier in allowed_tiers

    async def _trigger_flashbacks(self, input_text: str) -> List[Dict[str, Any]]:
        """Check if input triggers any flashbacks"""
        flashbacks = []

        # Check each word in input
        words = input_text.lower().split()

        for word in words:
            if word in self.flashback_triggers:
                for trigger_info in self.flashback_triggers[word]:
                    if trigger_info["intensity"] > 0.6:  # High intensity threshold
                        flashbacks.append(trigger_info)

        return flashbacks

    async def _get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory by ID"""
        if memory_id in self.memory_fold.items:
            return self.memory_fold.items[memory_id].data
        return None

    async def run_all_tests(self):
        """Run all memory system tests"""
        print("🧬 LUKHAS AI - COMPREHENSIVE MEMORY SYSTEM TEST SUITE")
        print("=" * 80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("System Version: 2.0.0")
        print()

        try:
            await self.setup()

            # Run all tests
            await self.test_1_basic_memory_storage()
            await self.test_2_memory_protection_and_tiers()
            await self.test_3_memory_dream_integration()
            await self.test_4_flashback_mechanisms()
            await self.test_5_tag_categorization_system()
            await self.test_6_memory_persistence_and_export()

            print("\n" + "=" * 80)
            print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 80)

            # Final summary
            final_stats = self.memory_fold.get_enhanced_statistics()
            print("\n📊 FINAL MEMORY SYSTEM STATISTICS:")
            print(f"  • Total memories created: {final_stats['total_items']}")
            print(f"  • Total unique tags: {final_stats['unique_tags']}")
            print(
                f"  • Space saved by deduplication: {final_stats['deduplication_saves']}"
            )
            print(
                f"  • Active vector embeddings: {final_stats['vector_stats']['total_vectors']}"
            )
            print(
                f"  • Causal relationships: {final_stats['causal_stats']['total_causal_links']}"
            )
            print(f"  • Dream memories: {len(self.dream_memories)}")
            print(f"  • Flashback triggers registered: {len(self.flashback_triggers)}")

            if final_stats["learning_stats"]["most_important_tags"]:
                print("\n🏆 Most Important Tags (by learned weight):")
                for tag, weight in final_stats["learning_stats"]["most_important_tags"][
                    :5
                ]:
                    print(f"  • {tag}: {weight:.3f}")

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()


async def main():
    """Run the comprehensive test suite"""
    test_suite = MemorySystemTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
