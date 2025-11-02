# path: qi/feedback/triage.py
from __future__ import annotations

import json
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from qi.feedback.schema import FeedbackCluster
from qi.feedback.store import get_store


class FeedbackTriage:
    """Deduplication and clustering for feedback cards."""

    def __init__(self):
        self.store = get_store()
        self.dedup_window_minutes = 5  # Dedup window
        self.min_cluster_size = 3  # Minimum samples for clustering

    def _dedup_key(self, fc: dict[str, Any]) -> str:
        """Generate deduplication key."""
        session = fc.get("session_hash", "")
        task = fc.get("context", {}).get("task", "")
        jurisdiction = fc.get("context", {}).get("jurisdiction", "")
        return f"{session}:{task}:{jurisdiction}"

    def deduplicate(self, feedback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove duplicate feedback entries within time window."""
        deduped = []
        seen = {}

        for fc in feedback:
            key = self._dedup_key(fc)
            ts_str = fc.get("ts", "")

            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", ""))
            except Exception:
                ts = datetime.now(timezone.utc)

            if key in seen:
                last_ts = seen[key]
                if (ts - last_ts).total_seconds() < self.dedup_window_minutes * 60:
                    continue  # Skip duplicate

            seen[key] = ts
            deduped.append(fc)

        return deduped

    def cluster_by_task(self, feedback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Cluster feedback by task and jurisdiction."""
        clusters = defaultdict(list)

        # Group by (task, jurisdiction)
        for fc in feedback:
            task = fc.get("context", {}).get("task", "unknown")
            jurisdiction = fc.get("context", {}).get("jurisdiction", "global")
            key = (task, jurisdiction)
            clusters[key].append(fc)

        # Build cluster objects
        cluster_list = []
        for (task, jurisdiction), fcs in clusters.items():
            if len(fcs) < self.min_cluster_size:
                continue  # Skip small clusters

            # Calculate statistics
            satisfactions = [fc.get("feedback", {}).get("satisfaction", 0.5) for fc in fcs]
            sat_mean = statistics.mean(satisfactions)
            sat_var = statistics.variance(satisfactions) if len(satisfactions) > 1 else 0.0

            # Collect common issues
            issue_counter = Counter()
            for fc in fcs:
                issues = fc.get("feedback", {}).get("issues", [])
                issue_counter.update(issues)

            common_issues = [issue for issue, _ in issue_counter.most_common(5)]

            # Calculate drift if we have baseline
            drift_delta = None
            if sat_mean < 0.4:  # Low satisfaction indicates drift
                drift_delta = 0.5 - sat_mean  # Distance from neutral

            cluster = FeedbackCluster(
                task=task,
                jurisdiction=jurisdiction,
                feedback_ids=[fc.get("fc_id", "") for fc in fcs],
                sat_mean=sat_mean,
                sat_var=sat_var,
                n_samples=len(fcs),
                common_issues=common_issues,
                drift_delta=drift_delta,
            )

            # Use json_encoders from schema
            cluster_dict = json.loads(cluster.json())
            cluster_list.append(cluster_dict)

        return cluster_list

    def compute_task_weights(self, clusters: list[dict[str, Any]]) -> dict[str, float]:
        """Compute calibration weights based on satisfaction."""
        weights = {}

        for cluster in clusters:
            task = cluster.get("task")
            sat_mean = cluster.get("sat_mean", 0.5)
            n_samples = cluster.get("n_samples", 0)

            if not task or n_samples < self.min_cluster_size:
                continue

            # Weight formula: SAT_norm = clip((SAT - 0.5) * 2, 0, 1)
            sat_norm = max(0, min(1, (sat_mean - 0.5) * 2))

            # w = min(w_max, α * SAT_norm) where α≈0.5, w_max≈0.2
            alpha = 0.5
            w_max = 0.2
            weight = min(w_max, alpha * sat_norm)

            weights[task] = weight

        return weights

    def run_triage(self, limit: int = 1000) -> dict[str, Any]:
        """Run full triage pipeline."""
        # Read recent feedback
        feedback = self.store.read_feedback(limit=limit)

        # Deduplicate
        deduped = self.deduplicate(feedback)

        # Cluster
        clusters = self.cluster_by_task(deduped)

        # Compute weights
        weights = self.compute_task_weights(clusters)

        # Persist clusters
        self.store.write_clusters(clusters)

        # Generate stats
        stats = {
            "total_feedback": len(feedback),
            "after_dedup": len(deduped),
            "clusters_generated": len(clusters),
            "task_weights": weights,
            "timestamp": time.time(),
        }

        return stats

    def get_cluster_by_id(self, cluster_id: str) -> dict[str, Any] | None:
        """Get a specific cluster by ID."""
        clusters = self.store.read_clusters()
        for cluster in clusters:
            if cluster.get("cluster_id") == cluster_id:
                return cluster
        return None

    def get_clusters_for_task(self, task: str) -> list[dict[str, Any]]:
        """Get all clusters for a specific task."""
        clusters = self.store.read_clusters()
        return [c for c in clusters if c.get("task") == task]


# Singleton instance
_triage = None


def get_triage() -> FeedbackTriage:
    """Get singleton triage instance."""
    global _triage
    if _triage is None:
        _triage = FeedbackTriage()
    return _triage
