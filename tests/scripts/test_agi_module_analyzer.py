import pytest

pytest.importorskip("networkx", reason="networkx required for agi_module_analyzer tests")

from scripts.analysis.agi_module_analyzer import AGIModuleAnalyzer, ModuleAnalysis


def test_analyze_interface_patterns_common_interfaces():
    analyzer = AGIModuleAnalyzer(root_path=".")
    analyzer.modules = {
        "module_a": ModuleAnalysis(
            path="module_a",
            purpose="",
            complexity_score=0.0,
            dependencies=[],
            interfaces=["foo", "bar"],
            core_functions=[],
            potential_merges=[],
            abstraction_level="",
            agi_component_type="",
        ),
        "module_b": ModuleAnalysis(
            path="module_b",
            purpose="",
            complexity_score=0.0,
            dependencies=[],
            interfaces=["foo"],
            core_functions=[],
            potential_merges=[],
            abstraction_level="",
            agi_component_type="",
        ),
    }
    modules = [{"module": "module_a"}, {"module": "module_b"}]
    patterns = analyzer._analyze_interface_patterns(modules)
    assert patterns["common_interfaces"] == ["foo"]  # ΛTAG: interface_analysis_test
