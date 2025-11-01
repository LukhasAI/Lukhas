"""
Router Fast-Path Selection Load Tests

Validates router efficiency per audit requirement:
- ≥80% fast node selection under load
- Adaptive routing heuristics validation
- Performance degradation testing

Usage:
    pytest tests/performance/test_router_fast_path.py -v
    python tests/performance/test_router_fast_path.py
"""
import asyncio
import statistics
import time
from typing import Dict, List

import pytest

try:
    from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
    from matriz.core.node_interface import CognitiveNode
    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False

class FastMockNode(CognitiveNode):
    """Mock node with fast response time"""

    def __init__(self, name: str, latency_ms: float=5.0):
        self.name = name
        self.latency_ms = latency_ms
        self.process_count = 0

    def process(self, data: Dict) -> Dict:
        time.sleep(self.latency_ms / 1000.0)
        self.process_count += 1
        return {
            'answer': f'Fast response from {self.name}',
            'confidence': 0.9,
            'node': self.name,
            'process_count': self.process_count
        }

class SlowMockNode(CognitiveNode):
    """Mock node with slow response time"""

    def __init__(self, name: str, latency_ms: float=50.0):
        self.name = name
        self.latency_ms = latency_ms
        self.process_count = 0

    def process(self, data: Dict) -> Dict:
        time.sleep(self.latency_ms / 1000.0)
        self.process_count += 1
        return {'answer': f'Slow response from {self.name}', 'confidence': 0.7, 'node': self.name, 'process_count': self.process_count}

class RouterFastPathLoadTest:
    """Load test suite for router fast-path selection"""

    def __init__(self):
        if not MATRIZ_AVAILABLE:
            pytest.skip('MATRIZ modules not available')
        self.orchestrator = AsyncCognitiveOrchestrator()
        self._setup_nodes()

    def _setup_nodes(self):
        """Setup fast and slow nodes for testing"""
        self.orchestrator.register_node('facts_fast', FastMockNode('facts_fast', 5.0))
        self.orchestrator.register_node('math_fast', FastMockNode('math_fast', 8.0))
        self.orchestrator.register_node('facts', SlowMockNode('facts', 45.0))
        self.orchestrator.register_node('math', SlowMockNode('math', 50.0))
        self.orchestrator.register_node('general_fast', FastMockNode('general_fast', 10.0))
        self.orchestrator.register_node('general_slow', SlowMockNode('general_slow', 40.0))

    async def test_fast_path_selection_under_load(self, num_requests: int=100) -> Dict:
        """Test fast-path selection under concurrent load"""
        print(f'🚀 Testing router fast-path selection with {num_requests} requests...')
        warmup_queries = ['What is 2+2?', 'What is the capital of France?', 'Hello there']
        for query in warmup_queries:
            for _ in range(5):
                await self.orchestrator.process_query(query)
        start_time = time.perf_counter()

        async def process_request(request_id: int) -> Dict:
            query = f'Test query {request_id}: What is {request_id * 2}?'
            result = await self.orchestrator.process_query(query)
            return {
                'id': request_id,
                'success': 'error' not in result,
                'latency_ms': result.get('metrics', {}).get('total_duration_ms', 0),
                'selected_node': self._extract_selected_node(result),
                'within_budget': result.get('metrics', {}).get('within_budget', False)
            }
        tasks = [process_request(i) for i in range(num_requests)]
        request_results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.perf_counter() - start_time
        successful_results = [r for r in request_results if isinstance(r, dict) and r['success']]
        fast_nodes = {'facts_fast', 'math_fast', 'general_fast'}
        fast_selections = sum((1 for r in successful_results if r['selected_node'] in fast_nodes))
        fast_path_rate = fast_selections / len(successful_results) * 100 if successful_results else 0
        latencies = [r['latency_ms'] for r in successful_results]
        avg_latency = statistics.mean(latencies) if latencies else 0
        p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies) if latencies else 0
        results = {
            'test': 'router_fast_path_load',
            'num_requests': num_requests,
            'successful_requests': len(successful_results),
            'fast_path_selections': fast_selections,
            'fast_path_rate_percent': round(fast_path_rate, 1),
            'total_time_seconds': round(total_time, 2),
            'throughput_rps': round(len(successful_results) / total_time, 1),
            'latency_ms': {
                'average': round(avg_latency, 2),
                'p95': round(p95_latency, 2),
            },
            'slo_compliance': {
                'target_fast_path_rate': 80.0,
                'actual_fast_path_rate': round(fast_path_rate, 1),
                'compliant': fast_path_rate >= 80.0,
            },
            'node_usage': self._analyze_node_usage(),
        }
        print('📊 Fast-Path Selection Results:')
        print(f'   Fast-Path Rate: {fast_path_rate:.1f}% (target: ≥80%)')
        print(f'   Success Rate: {len(successful_results)}/{num_requests}')
        print(f"   Throughput: {results['throughput_rps']} req/sec")
        print(f'   P95 Latency: {p95_latency:.1f}ms')
        print(f"   SLO Compliance: {('✅ PASS' if fast_path_rate >= 80.0 else '❌ FAIL')}")
        return results

    async def test_adaptive_routing_degradation(self) -> Dict:
        """Test adaptive routing when fast nodes become slow"""
        print('🔄 Testing adaptive routing under node degradation...')
        normal_results = []
        for i in range(20):
            result = await self.orchestrator.process_query(f'Normal query {i}')
            normal_results.append(self._extract_selected_node(result))
        for node_name in ['facts_fast', 'math_fast']:
            if node_name in self.orchestrator.node_health:
                health = self.orchestrator.node_health[node_name]
                health['failure_count'] += 20
                health['recent_latencies'].extend([100.0] * 10)
        degraded_results = []
        for i in range(20):
            result = await self.orchestrator.process_query(f'Degraded query {i}')
            degraded_results.append(self._extract_selected_node(result))
        fast_nodes = {'facts_fast', 'math_fast', 'general_fast'}
        normal_fast_rate = sum((1 for node in normal_results if node in fast_nodes)) / len(normal_results) * 100
        degraded_fast_rate = sum((1 for node in degraded_results if node in fast_nodes)) / len(degraded_results) * 100
        routing_adaptation = normal_fast_rate - degraded_fast_rate
        results = {
            'test': 'adaptive_routing_degradation',
            'normal_phase': {
                'fast_path_rate': round(normal_fast_rate, 1),
                'node_distribution': self._count_node_usage(normal_results)
            },
            'degraded_phase': {
                'fast_path_rate': round(degraded_fast_rate, 1),
                'node_distribution': self._count_node_usage(degraded_results)
            },
            'adaptation': {
                'routing_change_percent': round(routing_adaptation, 1),
                'adaptive': routing_adaptation > 10.0
            }
        }
        print('📊 Adaptive Routing Results:')
        print(f'   Normal Fast-Path: {normal_fast_rate:.1f}%')
        print(f'   Degraded Fast-Path: {degraded_fast_rate:.1f}%')
        print(f'   Adaptation: {routing_adaptation:.1f}% reduction')
        print(f"   Adaptive Behavior: {('✅ YES' if routing_adaptation > 10.0 else '❌ NO')}")
        return results

    def _extract_selected_node(self, result: Dict) -> str:
        """Extract selected node from orchestrator result"""
        if 'stages' in result:
            for stage in result['stages']:
                if stage.get('stage_type') == 'processing' and stage.get('success'):
                    stage_data = stage.get('data', {})
                    if isinstance(stage_data, dict) and 'node' in stage_data:
                        return stage_data['node']
        node_health = result.get('node_health', {})
        if node_health:
            active_nodes = [(name, health['success_count'] + health['failure_count']) for (name, health) in node_health.items()]
            if active_nodes:
                return max(active_nodes, key=lambda x: x[1])[0]
        return 'unknown'

    def _analyze_node_usage(self) -> Dict[str, int]:
        """Analyze node usage from orchestrator health metrics"""
        usage = {}
        for (node_name, health) in self.orchestrator.node_health.items():
            usage[node_name] = health['success_count'] + health['failure_count']
        return usage

    def _count_node_usage(self, node_list: List[str]) -> Dict[str, int]:
        """Count node usage from list of selected nodes"""
        counts = {}
        for node in node_list:
            counts[node] = counts.get(node, 0) + 1
        return counts

async def run_all_fast_path_tests():
    """Run complete router fast-path test suite"""
    print('🚀 Starting Router Fast-Path Selection Load Tests...')
    print('=' * 60)
    if not MATRIZ_AVAILABLE:
        print('❌ MATRIZ modules not available - skipping tests')
        return []
    tester = RouterFastPathLoadTest()
    results = []
    try:
        results.append(await tester.test_fast_path_selection_under_load(50))
        results.append(await tester.test_adaptive_routing_degradation())
        print('\n' + '=' * 60)
        print('📊 ROUTER FAST-PATH TEST SUMMARY')
        print('=' * 60)
        all_compliant = True
        for result in results:
            test_name = result['test'].replace('_', ' ').title()
            if 'slo_compliance' in result:
                compliant = result['slo_compliance']['compliant']
                status = '✅ PASS' if compliant else '❌ FAIL'
                print(f'{test_name}: {status}')
                all_compliant = all_compliant and compliant
            else:
                adaptive = result.get('adaptation', {}).get('adaptive', False)
                status = '✅ ADAPTIVE' if adaptive else '⚠️ STATIC'
                print(f'{test_name}: {status}')
        print(f"\nOverall Fast-Path Compliance: {('✅ ALL PASS' if all_compliant else '❌ SOME FAILED')}")
        return results
    except Exception as e:
        print(f'❌ Fast-path tests failed: {e}')
        return []

@pytest.mark.performance
@pytest.mark.asyncio
async def test_router_fast_path_load():
    """pytest-compatible router fast-path load test"""
    if not MATRIZ_AVAILABLE:
        pytest.skip('MATRIZ not available')
    tester = RouterFastPathLoadTest()
    results = await tester.test_fast_path_selection_under_load(30)
    assert results['slo_compliance']['compliant'], 'Router fast-path selection rate below 80%'

@pytest.mark.performance
@pytest.mark.asyncio
async def test_adaptive_routing():
    """pytest-compatible adaptive routing test"""
    if not MATRIZ_AVAILABLE:
        pytest.skip('MATRIZ not available')
    tester = RouterFastPathLoadTest()
    results = await tester.test_adaptive_routing_degradation()
    assert results['adaptation']['adaptive'], 'Router failed to adapt to node degradation'
if __name__ == '__main__':
    asyncio.run(run_all_fast_path_tests())
