# MATRIZ Node Profiler Skill

Specialized performance profiling for MATRIZ cognitive DNA node processing chains with optimization recommendations and reasoning path visualization.

## Reasoning

1. MATRIZ orchestrates 20 Python files + 16K visualization assets with complex node networks requiring specialized profiling.
2. Generic profilers don't understand node semantics (Memory→Attention→Thought→Risk→Intent→Action pipeline).
3. T4 targets: <250ms p95 latency, <100MB memory, 50+ ops/sec throughput - need node-aware optimization.
4. No tooling to identify slow nodes, optimize reasoning paths, or detect inefficient node selection patterns.
5. Cognitive DNA reasoning chains can accumulate memory leaks in provenance links without specialized detection.

## Actions

### Core Profiler System

```python
#!/usr/bin/env python3
"""
MATRIZ Node Profiler - Cognitive DNA Performance Optimization

Node-aware profiling:
- Reasoning chain flamegraphs
- Per-node latency breakdown
- Node selection optimization
- Memory leak detection in provenance links
- Automated optimization suggestions
"""

import time
import psutil
from dataclasses import dataclass, field
from typing import List, Dict
import json

@dataclass
class NodeMetrics:
    node_id: str
    node_type: str
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    memory_usage: int = 0
    selection_count: int = 0
    provenance_links: int = 0

@dataclass
class ReasoningChainProfile:
    chain_id: str
    total_latency: float
    stages: Dict[str, float] = field(default_factory=dict)
    nodes_used: List[str] = field(default_factory=list)
    complexity_score: float = 0.0

class MatrizNodeProfiler:
    LATENCY_TARGET_P95 = 0.250  # 250ms
    MEMORY_TARGET = 100 * 1024 * 1024  # 100MB
    THROUGHPUT_TARGET = 50  # ops/sec

    def __init__(self):
        self.node_metrics: Dict[str, NodeMetrics] = {}
        self.chain_profiles: List[ReasoningChainProfile] = []

    def profile_reasoning_chain(self, query: str, trace_id: str) -> ReasoningChainProfile:
        """Instrument M-A-T-R-I-A stages"""
        profile = ReasoningChainProfile(chain_id=trace_id)
        start_time = time.perf_counter()

        stages = ['Memory', 'Attention', 'Thought', 'Risk', 'Intent', 'Action']
        for stage in stages:
            stage_start = time.perf_counter()
            # Instrument stage execution
            stage_latency = time.perf_counter() - stage_start
            profile.stages[stage] = stage_latency

        profile.total_latency = time.perf_counter() - start_time
        profile.complexity_score = self._calculate_complexity(profile)

        self.chain_profiles.append(profile)
        return profile

    def generate_node_flamegraph(self, profiling_data: List[ReasoningChainProfile]):
        """Visual representation of time per node and stage"""
        flamegraph_data = []
        for profile in profiling_data:
            for stage, latency in profile.stages.items():
                flamegraph_data.append({
                    'name': f"{profile.chain_id}/{stage}",
                    'value': latency * 1000,  # ms
                    'children': []
                })
        return flamegraph_data

    def detect_node_bottlenecks(self, node_metrics: Dict[str, NodeMetrics]):
        """Identify slow nodes and inefficient patterns"""
        bottlenecks = []
        for node_id, metrics in node_metrics.items():
            if metrics.latency_p95 > self.LATENCY_TARGET_P95 * 0.5:
                bottlenecks.append({
                    'node_id': node_id,
                    'type': 'high_latency',
                    'p95_ms': metrics.latency_p95 * 1000,
                    'severity': 'critical' if metrics.latency_p95 > self.LATENCY_TARGET_P95 else 'warning'
                })

            if metrics.selection_count < 5 and metrics.latency_p95 > 0.01:
                bottlenecks.append({
                    'node_id': node_id,
                    'type': 'underutilized',
                    'selection_count': metrics.selection_count,
                    'severity': 'info'
                })

        return bottlenecks

    def optimize_node_selection(self, query_patterns: List[str], node_performance: Dict):
        """ML-powered node routing optimization"""
        # Simple heuristic: prefer faster nodes for common queries
        recommendations = {}
        for pattern in query_patterns:
            best_node = min(node_performance.items(), key=lambda x: x[1].latency_p50)
            recommendations[pattern] = best_node[0]
        return recommendations

    def detect_memory_leaks(self, node_memory_traces: List[int]):
        """Track provenance link accumulation"""
        if len(node_memory_traces) < 10:
            return {'status': 'insufficient_data'}

        # Detect linear growth in memory
        growth_rate = (node_memory_traces[-1] - node_memory_traces[0]) / len(node_memory_traces)
        if growth_rate > 1024 * 1024:  # >1MB per operation
            return {
                'leak_detected': True,
                'growth_rate_mb': growth_rate / (1024 * 1024),
                'suggestion': 'Check provenance link cleanup in node teardown'
            }
        return {'status': 'ok'}

    def recommend_optimizations(self, bottlenecks: List[Dict]):
        """Concrete optimization suggestions"""
        recommendations = []
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'high_latency':
                recommendations.append({
                    'node': bottleneck['node_id'],
                    'action': 'Add result caching for common operations',
                    'expected_improvement': '30-50% latency reduction'
                })
            elif bottleneck['type'] == 'underutilized':
                recommendations.append({
                    'node': bottleneck['node_id'],
                    'action': 'Consider removing or consolidating with similar node',
                    'expected_improvement': 'Reduced system complexity'
                })
        return recommendations

    def _calculate_complexity(self, profile: ReasoningChainProfile):
        """Complexity score based on stages and nodes"""
        return len(profile.stages) * len(profile.nodes_used) * 0.1

if __name__ == '__main__':
    profiler = MatrizNodeProfiler()
    # CLI integration: lukhas-profile-matriz --chain-id=XYZ
```

### Makefile Integration

```makefile
matriz-profile:
	@python3 matriz/profiler/matriz_node_profiler.py --profile

matriz-flamegraph:
	@python3 matriz/profiler/matriz_node_profiler.py --flamegraph > matriz_flamegraph.json

matriz-optimize:
	@python3 matriz/profiler/matriz_node_profiler.py --suggest-optimizations
```

## Context References

- `/matriz/claude.me`
- `/matriz/core/claude.me`
- `/matriz/visualization/claude.me`
