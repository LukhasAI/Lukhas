"""
Comprehensive AGI Test Suite

Advanced testing framework for AGI systems that tests reasoning,
creativity, safety, memory, and integration capabilities.
"""

from .agi_test_suite import AGITestSuite, TestCategory, TestResult
from .creativity_tests import CreativityDimension, CreativityTestBattery
from .integration_tests import IntegrationTestBattery, IntegrationTestType
from .memory_tests import MemoryTestBattery, MemoryTestType
from .performance_tests import PerformanceBenchmark, PerformanceTestBattery
from .reasoning_tests import ReasoningCapability, ReasoningTestBattery
from .safety_tests import SafetyTestBattery, SafetyTestType

__all__ = [
    "AGITestSuite",
    "TestCategory",
    "TestResult",
    "ReasoningTestBattery",
    "ReasoningCapability",
    "CreativityTestBattery",
    "CreativityDimension",
    "MemoryTestBattery",
    "MemoryTestType",
    "SafetyTestBattery",
    "SafetyTestType",
    "IntegrationTestBattery",
    "IntegrationTestType",
    "PerformanceTestBattery",
    "PerformanceBenchmark",
]
