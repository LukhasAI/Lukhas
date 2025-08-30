#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - SEMANTIC EXTRACTOR
║ Extract semantic knowledge from episodic memories
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: semantic_extractor.py
║ Path: memory/neocortical/semantic_extractor.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╚══════════════════════════════════════════════════════════════════════════════════
"""

import json
import re
from collections import Counter, defaultdict
from typing import Any


class SemanticExtractor:
    """
    Extracts semantic features and relationships from episodic memories.
    Identifies patterns, categories, and abstract concepts.
    """

    def __init__(
        self,
        min_pattern_frequency: int = 2,
        similarity_threshold: float = 0.6,
        abstraction_levels: int = 3,
    ):
        self.min_pattern_frequency = min_pattern_frequency
        self.similarity_threshold = similarity_threshold
        self.abstraction_levels = abstraction_levels

        # Pattern storage
        self.observed_patterns: dict[str, int] = Counter()
        self.semantic_clusters: dict[str, set[str]] = defaultdict(set)
        self.abstraction_hierarchy: dict[int, dict[str, set[str]]] = {
            level: {} for level in range(abstraction_levels)
        }

        # Relationship extraction
        self.entity_relations: dict[str, dict[str, set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self.causal_chains: list[tuple[str, str, float]] = []  # (cause, effect, confidence)

        # Statistics
        self.total_episodes_processed = 0
        self.unique_concepts_extracted = 0

        logger.info(
            "SemanticExtractor initialized",
            min_pattern_freq=min_pattern_frequency,
            abstraction_levels=abstraction_levels,
        )

    def extract_semantics(self, episodes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Extract semantic knowledge from a batch of episodes.
        Returns structured semantic representation.
        """

        # Extract features from each episode
        all_features = []
        for episode in episodes:
            features = self._extract_episode_features(episode)
            all_features.append(features)
            self.total_episodes_processed += 1

        # Find common patterns
        patterns = self._find_common_patterns(all_features)

        # Build semantic clusters
        clusters = self._cluster_semantically(patterns)

        # Extract relationships
        relationships = self._extract_relationships(episodes)

        # Build abstraction hierarchy
        hierarchy = self._build_abstractions(clusters)

        # Generate semantic summary
        semantic_knowledge = {
            "patterns": patterns,
            "clusters": clusters,
            "relationships": relationships,
            "hierarchy": hierarchy,
            "statistics": {
                "episodes_processed": len(episodes),
                "unique_patterns": len(patterns),
                "semantic_clusters": len(clusters),
                "abstraction_levels": len(hierarchy),
            },
        }

        return semantic_knowledge

    def extract_concept(self, episode: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        Extract primary concept and attributes from single episode.
        Returns (concept_name, attributes).
        """

        features = self._extract_episode_features(episode)

        # Identify primary concept
        concept = self._identify_primary_concept(features)

        # Extract attributes
        attributes = self._extract_attributes(features, concept)

        return concept, attributes

    def find_semantic_similarity(self, episode1: dict[str, Any], episode2: dict[str, Any]) -> float:
        """Calculate semantic similarity between two episodes"""

        features1 = self._extract_episode_features(episode1)
        features2 = self._extract_episode_features(episode2)

        # Compare feature overlap
        common_features = features1["entities"] & features2["entities"]
        total_features = features1["entities"] | features2["entities"]

        if not total_features:
            return 0.0

        entity_similarity = len(common_features) / len(total_features)

        # Compare actions
        action_similarity = self._compare_sequences(
            features1.get("actions", []), features2.get("actions", [])
        )

        # Compare attributes
        attr_similarity = self._compare_attributes(
            features1.get("attributes", {}), features2.get("attributes", {})
        )

        # Weighted combination
        similarity = 0.4 * entity_similarity + 0.3 * action_similarity + 0.3 * attr_similarity

        return similarity

    def _extract_episode_features(self, episode: dict[str, Any]) -> dict[str, Any]:
        """Extract semantic features from episode"""

        features = {
            "entities": set(),
            "actions": [],
            "attributes": {},
            "temporal": [],
            "spatial": [],
            "emotional": {},
        }

        # Convert to string for analysis
        json.dumps(episode, sort_keys=True)

        # Extract entities (simplified - would use NER in practice)
        for key, value in episode.items():
            if isinstance(value, str):
                # Extract noun-like entities
                words = re.findall(r"\b[A-Za-z]+\b", value)
                features["entities"].update(words)

            # Extract actions (verbs)
            if key in ["action", "event", "verb", "activity"]:
                features["actions"].append(value)

            # Extract attributes
            if key not in ["id", "timestamp", "type"]:
                features["attributes"][key] = value

            # Temporal features
            if key in ["time", "when", "duration", "timestamp"]:
                features["temporal"].append(value)

            # Spatial features
            if key in ["location", "place", "where", "position"]:
                features["spatial"].append(value)

            # Emotional features
            if key in ["emotion", "feeling", "valence", "arousal"]:
                features["emotional"][key] = value

        return features

    def _find_common_patterns(self, feature_sets: list[dict[str, Any]]) -> dict[str, list[Any]]:
        """Find patterns that occur frequently across episodes"""

        patterns = defaultdict(list)

        # Entity co-occurrence patterns
        entity_pairs = []
        for features in feature_sets:
            entities = list(features["entities"])
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    entity_pairs.append((entities[i], entities[j]))

        pair_counts = Counter(entity_pairs)
        frequent_pairs = [
            pair for pair, count in pair_counts.items() if count >= self.min_pattern_frequency
        ]
        patterns["entity_pairs"] = frequent_pairs

        # Action sequences
        action_sequences = []
        for features in feature_sets:
            if len(features["actions"]) >= 2:
                for i in range(len(features["actions"]) - 1):
                    seq = (features["actions"][i], features["actions"][i + 1])
                    action_sequences.append(seq)

        seq_counts = Counter(action_sequences)
        frequent_sequences = [
            seq for seq, count in seq_counts.items() if count >= self.min_pattern_frequency
        ]
        patterns["action_sequences"] = frequent_sequences

        # Attribute patterns
        attr_patterns = defaultdict(list)
        for features in feature_sets:
            for key, value in features["attributes"].items():
                attr_patterns[key].append(value)

        # Find common attribute values
        for key, values in attr_patterns.items():
            value_counts = Counter(values)
            common_values = [
                v for v, count in value_counts.most_common(3) if count >= self.min_pattern_frequency
            ]
            if common_values:
                patterns[f"common_{key}"] = common_values

        # Update observed patterns
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                pattern_key = f"{pattern_type}:{pattern}"
                self.observed_patterns[pattern_key] += 1

        return dict(patterns)

    def _cluster_semantically(self, patterns: dict[str, list[Any]]) -> dict[str, set[str]]:
        """Cluster patterns into semantic groups"""

        clusters = defaultdict(set)

        # Cluster by entity relationships
        if "entity_pairs" in patterns:
            for entity1, entity2 in patterns["entity_pairs"]:
                cluster_key = f"related_to_{entity1}"
                clusters[cluster_key].add(entity2)
                cluster_key = f"related_to_{entity2}"
                clusters[cluster_key].add(entity1)

        # Cluster by action types
        if "action_sequences" in patterns:
            for action1, action2 in patterns["action_sequences"]:
                clusters["action_chains"].add(f"{action1}->{action2}")

        # Cluster by common attributes
        for key, values in patterns.items():
            if key.startswith("common_"):
                attr_name = key.replace("common_", "")
                for value in values:
                    clusters[f"{attr_name}_cluster"].add(str(value))

        # Update semantic clusters
        for cluster_key, members in clusters.items():
            self.semantic_clusters[cluster_key].update(members)

        return dict(clusters)

    def _extract_relationships(self, episodes: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract relationships between entities and concepts"""

        relationships = {
            "causal": [],
            "temporal": [],
            "hierarchical": [],
            "associative": [],
        }

        # Extract causal relationships
        for i in range(len(episodes) - 1):
            ep1 = episodes[i]
            ep2 = episodes[i + 1]

            # Simple causality detection
            if "outcome" in ep2 and "action" in ep1:
                cause = ep1.get("action", "unknown")
                effect = ep2.get("outcome", "unknown")
                confidence = 0.5  # Would calculate based on frequency

                relationships["causal"].append(
                    {"cause": cause, "effect": effect, "confidence": confidence}
                )

                self.causal_chains.append((cause, effect, confidence))

        # Extract temporal relationships
        temporal_events = []
        for ep in episodes:
            if "timestamp" in ep or "time" in ep:
                event = ep.get("event", ep.get("action", "unknown"))
                time = ep.get("timestamp", ep.get("time", 0))
                temporal_events.append((time, event))

        temporal_events.sort()
        for i in range(len(temporal_events) - 1):
            relationships["temporal"].append(
                {"before": temporal_events[i][1], "after": temporal_events[i + 1][1]}
            )

        # Extract hierarchical relationships (is-a, part-of)
        for ep in episodes:
            if "category" in ep and "type" in ep:
                relationships["hierarchical"].append(
                    {"child": ep["type"], "parent": ep["category"], "relation": "is-a"}
                )

        # Extract associative relationships
        for cluster_key, members in self.semantic_clusters.items():
            if len(members) >= 2:
                members_list = list(members)
                for i in range(len(members_list)):
                    for j in range(i + 1, len(members_list)):
                        relationships["associative"].append(
                            {
                                "entity1": members_list[i],
                                "entity2": members_list[j],
                                "context": cluster_key,
                            }
                        )

        return relationships

    def _build_abstractions(self, clusters: dict[str, set[str]]) -> dict[int, dict[str, set[str]]]:
        """Build multi-level abstraction hierarchy"""

        hierarchy = {level: {} for level in range(self.abstraction_levels)}

        # Level 0: Direct clusters
        hierarchy[0] = dict(clusters.items())

        # Level 1: Merge similar clusters
        if self.abstraction_levels > 1:
            for cluster1_key, cluster1_members in clusters.items():
                for cluster2_key, cluster2_members in clusters.items():
                    if cluster1_key != cluster2_key:
                        overlap = cluster1_members & cluster2_members
                        if len(overlap) / max(len(cluster1_members), len(cluster2_members)) > 0.5:
                            merged_key = f"{cluster1_key}__{cluster2_key}"
                            hierarchy[1][merged_key] = cluster1_members | cluster2_members

        # Level 2: Abstract categories
        if self.abstraction_levels > 2:
            # Group by pattern type
            for key in hierarchy[1]:
                if "action" in key:
                    hierarchy[2].setdefault("behavioral_patterns", set()).update(hierarchy[1][key])
                elif "related" in key:
                    hierarchy[2].setdefault("relational_patterns", set()).update(hierarchy[1][key])
                else:
                    hierarchy[2].setdefault("attribute_patterns", set()).update(hierarchy[1][key])

        # Update stored hierarchy
        for level, level_clusters in hierarchy.items():
            self.abstraction_hierarchy[level].update(level_clusters)

        # Count unique concepts
        all_concepts = set()
        for level_clusters in hierarchy.values():
            for members in level_clusters.values():
                all_concepts.update(members)
        self.unique_concepts_extracted = len(all_concepts)

        return hierarchy

    def _identify_primary_concept(self, features: dict[str, Any]) -> str:
        """Identify the primary concept from features"""

        # Priority order for concept identification
        if features["actions"]:
            return features["actions"][0]

        if features["entities"]:
            # Return most frequent entity
            entity_counts = Counter(features["entities"])
            return entity_counts.most_common(1)[0][0]

        # Fallback to first attribute
        if features["attributes"]:
            return list(features["attributes"].keys())[0]

        return "unknown"

    def _extract_attributes(self, features: dict[str, Any], concept: str) -> dict[str, Any]:
        """Extract relevant attributes for a concept"""

        attributes = {}

        # Direct attributes
        attributes.update(features["attributes"])

        # Derived attributes
        if features["temporal"]:
            attributes["temporal_context"] = features["temporal"]

        if features["spatial"]:
            attributes["spatial_context"] = features["spatial"]

        if features["emotional"]:
            attributes["emotional_context"] = features["emotional"]

        # Related entities
        related = []
        for entity in features["entities"]:
            if entity != concept:
                related.append(entity)
        if related:
            attributes["related_entities"] = related

        return attributes

    def _compare_sequences(self, seq1: list[Any], seq2: list[Any]) -> float:
        """Compare two sequences for similarity"""

        if not seq1 or not seq2:
            return 0.0 if (seq1 or seq2) else 1.0

        # Use longest common subsequence
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs_length = dp[m][n]
        return lcs_length / max(m, n)

    def _compare_attributes(self, attrs1: dict, attrs2: dict) -> float:
        """Compare two attribute dictionaries"""

        if not attrs1 and not attrs2:
            return 1.0
        if not attrs1 or not attrs2:
            return 0.0

        common_keys = set(attrs1.keys()) & set(attrs2.keys())
        all_keys = set(attrs1.keys()) | set(attrs2.keys())

        if not all_keys:
            return 0.0

        # Key overlap
        key_similarity = len(common_keys) / len(all_keys)

        # Value similarity for common keys
        value_similarity = 0.0
        for key in common_keys:
            if attrs1[key] == attrs2[key]:
                value_similarity += 1.0
            elif isinstance(attrs1[key], (int, float)) and isinstance(attrs2[key], (int, float)):
                # Numeric similarity
                diff = abs(attrs1[key] - attrs2[key])
                max_val = max(abs(attrs1[key]), abs(attrs2[key]))
                if max_val > 0:
                    value_similarity += 1.0 - min(diff / max_val, 1.0)

        if common_keys:
            value_similarity /= len(common_keys)

        return 0.5 * key_similarity + 0.5 * value_similarity

    def get_metrics(self) -> dict[str, Any]:
        """Get extractor metrics"""

        return {
            "total_episodes_processed": self.total_episodes_processed,
            "unique_concepts_extracted": self.unique_concepts_extracted,
            "observed_patterns": len(self.observed_patterns),
            "semantic_clusters": len(self.semantic_clusters),
            "causal_chains": len(self.causal_chains),
            "abstraction_levels": self.abstraction_levels,
            "most_common_patterns": [
                pattern for pattern, _ in self.observed_patterns.most_common(5)
            ],
        }


# Example usage
if __name__ == "__main__":
    extractor = SemanticExtractor()

    # Test episodes
    episodes = [
        {
            "event": "learning",
            "action": "study",
            "subject": "mathematics",
            "topic": "calculus",
            "duration": "2 hours",
            "outcome": "understood derivatives",
        },
        {
            "event": "learning",
            "action": "practice",
            "subject": "mathematics",
            "topic": "calculus",
            "duration": "1 hour",
            "outcome": "solved problems",
        },
        {
            "event": "teaching",
            "action": "explain",
            "subject": "mathematics",
            "student": "colleague",
            "outcome": "student understood",
        },
    ]

    # Extract semantics
    print("=== Semantic Extraction Demo ===\n")

    semantics = extractor.extract_semantics(episodes)

    print("Patterns found:")
    for pattern_type, patterns in semantics["patterns"].items():
        print(f"  {pattern_type}: {patterns}")

    print("\nSemantic clusters:")
    for cluster, members in semantics["clusters"].items():
        print(f"  {cluster}: {members}")

    print("\nRelationships:")
    for rel_type, rels in semantics["relationships"].items():
        if rels:
            print(f"  {rel_type}: {rels[:2]}...")  # First 2

    # Test similarity
    print("\n--- Similarity Test ---")
    similarity = extractor.find_semantic_similarity(episodes[0], episodes[1])
    print(f"Similarity between first two episodes: {similarity:.2f}")

    # Metrics
    print("\n--- Metrics ---")
    for key, value in extractor.get_metrics().items():
        print(f"{key}: {value}")
