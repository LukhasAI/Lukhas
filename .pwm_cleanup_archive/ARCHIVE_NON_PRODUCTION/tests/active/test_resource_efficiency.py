from core.core_utilities import (
    ResourceEfficiencyAnalyzer,
    get_resource_efficiency_table,
)


def test_collect_metrics_returns_numbers():
    analyzer = ResourceEfficiencyAnalyzer()
    metrics = analyzer.collect_metrics()
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert isinstance(metrics["cpu_percent"], float)
    assert isinstance(metrics["memory_percent"], float)
    assert metrics["cpu_percent"] >= 0.0
    assert metrics["memory_percent"] >= 0.0


def test_resource_efficiency_table_structure():
    table = get_resource_efficiency_table()
    assert isinstance(table, list)
    assert len(table) >= 3
    for row in table:
        assert "Architecture" in row and "Energy" in row and "Memory" in row
