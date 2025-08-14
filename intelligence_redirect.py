"""
Intelligence Module Redirect
============================
This module redirects imports from the deprecated intelligence module
to their new consolidated locations.

The intelligence module has been consolidated into:
- consciousness/reasoning/advanced_engines/ - Core intelligence engines
- orchestration/agent_orchestrator/ - Agent bridge functionality
- governance/ - Safety validation
- orchestration/brain/monitoring/ - Monitoring capabilities
- tools/benchmarking/ - Performance benchmarking
"""

import warnings

def __getattr__(name):
    """Redirect imports with deprecation warning"""
    
    redirects = {
        # Core engines
        "LukhasMetaCognitiveEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasCausalReasoningEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasAutonomousGoalEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasCuriosityEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasTheoryOfMindEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasNarrativeIntelligenceEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasDimensionalIntelligenceEngine": "consciousness.reasoning.advanced_engines.intelligence_engines",
        "LukhasSubsystemOrchestrator": "consciousness.reasoning.advanced_engines.intelligence_engines",
        
        # Agent bridge
        "LukhasAgentBridge": "orchestration.agent_orchestrator.intelligence_bridge",
        "AgentType": "orchestration.agent_orchestrator.intelligence_bridge",
        "IntelligenceRequestType": "orchestration.agent_orchestrator.intelligence_bridge",
        "AgentRequest": "orchestration.agent_orchestrator.intelligence_bridge",
        "IntelligenceResponse": "orchestration.agent_orchestrator.intelligence_bridge",
        
        # Safety validation
        "LukhasIntelligenceSafetyValidator": "governance.intelligence_safety_validator",
        "SafetyLevel": "governance.intelligence_safety_validator",
        "ValidationResult": "governance.intelligence_safety_validator",
        "SafetyBounds": "governance.intelligence_safety_validator",
        
        # Monitoring
        "LukhasIntelligenceMonitor": "orchestration.brain.monitoring.intelligence_monitor",
        "MetricType": "orchestration.brain.monitoring.intelligence_monitor",
        "AlertLevel": "orchestration.brain.monitoring.intelligence_monitor",
        
        # Benchmarking
        "LukhasIntelligenceBenchmarking": "tools.benchmarking.intelligence_benchmark",
        "BenchmarkType": "tools.benchmarking.intelligence_benchmark",
        "BenchmarkScenario": "tools.benchmarking.intelligence_benchmark",
    }
    
    if name in redirects:
        new_location = redirects[name]
        warnings.warn(
            f"The intelligence module has been consolidated. "
            f"Please import {name} from {new_location} instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Dynamic import from new location
        module_path, class_name = new_location.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, name)
    
    raise AttributeError(f"module 'intelligence' has no attribute '{name}'")

# Provide module-level docstring for help()
__doc__ = __doc__
__all__ = []  # Empty to discourage imports