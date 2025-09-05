"""
Comprehensive AGI Test Suite

Advanced testing framework for AGI systems that tests reasoning,
creativity, safety, memory, and integration capabilities.
"""

from .agi_test_suite import AGITestSuite, TestCategory, TestResult
from .reasoning_tests import ReasoningTestBattery, ReasoningCapability
from .creativity_tests import CreativityTestBattery, CreativityDimension  
from .memory_tests import MemoryTestBattery, MemoryTestType
from .safety_tests import SafetyTestBattery, SafetyTestType
from .integration_tests import IntegrationTestBattery, IntegrationTestType
from .performance_tests import PerformanceTestBattery, PerformanceBenchmark

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
    "PerformanceBenchmark"
]