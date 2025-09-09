#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
📚 LUKHAS Module Interface Example
==================================
Complete example showing how to create a LUKHAS-compliant module
that integrates with Memory, Consciousness, and Guardian systems.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from core.common import GLYPHSymbol, GLYPHToken, get_logger
from core.common.exceptions import LukhasError, ValidationError

# LUKHAS imports
from core.interfaces import CoreInterface
from core.interfaces.dependency_injection import (
    get_service,
    register_service,
)
from core.interfaces.memory_interface import MemoryType

# Configure logging
logger = get_logger(__name__)


# Example data structures
@dataclass
class AnalysisRequest:
    """Request for data analysis"""

    data: dict[str, Any]
    analysis_type: str
    priority: str = "normal"
    ethical_check: bool = True


@dataclass
class AnalysisResult:
    """Result of analysis"""

    request_id: str
    findings: dict[str, Any]
    confidence: float
    memory_id: Optional[str] = None
    ethical_approval: Optional[bool] = None


class DataAnalyzer(CoreInterface):
    """
    Example LUKHAS module that analyzes data with full integration.

    This module demonstrates:
    - Proper interface implementation
    - Dependency injection usage
    - Memory system integration
    - Consciousness coordination
    - Guardian validation
    - GLYPH communication
    - Error handling
    - Performance monitoring
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the data analyzer module"""
        self.config = config or {}
        self.operational = False
        self.memory_service = None
        self.consciousness_service = None
        self.guardian_service = None

        # Performance metrics
        self.metrics = {
            "analyses_completed": 0,
            "analyses_failed": 0,
            "average_time_ms": 0,
            "memory_stores": 0,
            "ethical_rejections": 0,
        }

        # Internal state
        self._analysis_history: list[AnalysisResult] = []

    async def initialize(self) -> None:
        """
        Initialize the module and register with dependency injection.

        This method:
        1. Gets required services
        2. Registers itself
        3. Performs startup checks
        """
        try:
            logger.info("Initializing DataAnalyzer module...")

            # Get required services through dependency injection
            self.memory_service = get_service("memory_service")
            self.consciousness_service = get_service("consciousness_service")
            self.guardian_service = get_service("guardian_service")

            # Register this module
            register_service("data_analyzer", self, singleton=True)

            # Perform startup checks
            await self._perform_startup_checks()

            self.operational = True
            logger.info("DataAnalyzer module initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DataAnalyzer: {e}")
            raise LukhasError(f"Initialization failed: {e}")

    async def _perform_startup_checks(self) -> None:
        """Perform startup validation checks"""
        # Check memory service
        if self.memory_service:
            try:
                status = await self.memory_service.get_status()
                if not status.get("operational"):
                    logger.warning("Memory service not fully operational")
            except Exception as e:
                logger.warning(f"Could not check memory service status: {e}")

        # Check consciousness service
        if self.consciousness_service:
            awareness = await self.consciousness_service.assess_awareness({})
            logger.info(f"Consciousness awareness level: {awareness.get('overall_awareness', 0)}")

    async def analyze_data(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main analysis method with full integration.

        This demonstrates the complete flow:
        1. Validate request with Guardian
        2. Get consciousness input
        3. Perform analysis
        4. Store in memory
        5. Return results
        """
        import time

        start_time = time.time()

        try:
            # Step 1: Guardian validation (if requested)
            if request.ethical_check and self.guardian_service:
                validation = await self._validate_with_guardian(request)
                if not validation["approved"]:
                    self.metrics["ethical_rejections"] += 1
                    raise ValidationError(f"Guardian rejected: {validation['reasoning']}")

            # Step 2: Get consciousness assessment
            consciousness_input = None
            if self.consciousness_service:
                consciousness_input = await self._get_consciousness_input(request)

            # Step 3: Perform actual analysis
            findings = await self._perform_analysis(request, consciousness_input)

            # Step 4: Create result
            result = AnalysisResult(
                request_id=f"analysis_{datetime.now(timezone.utc).timestamp()}",
                findings=findings,
                confidence=findings.get("confidence", 0.8),
                ethical_approval=True if request.ethical_check else None,
            )

            # Step 5: Store in memory (if significant)
            if findings.get("significance", 0.5) > 0.7 and self.memory_service:
                memory_id = await self._store_in_memory(request, result)
                result.memory_id = memory_id
                self.metrics["memory_stores"] += 1

            # Update metrics
            self.metrics["analyses_completed"] += 1
            elapsed_ms = (time.time() - start_time) * 1000
            self._update_average_time(elapsed_ms)

            # Add to history
            self._analysis_history.append(result)
            if len(self._analysis_history) > 100:
                self._analysis_history.pop(0)

            return result

        except Exception as e:
            self.metrics["analyses_failed"] += 1
            logger.error(f"Analysis failed: {e}")
            raise

    async def _validate_with_guardian(self, request: AnalysisRequest) -> dict[str, Any]:
        """Validate analysis request with Guardian system"""
        action = {
            "type": "data_analysis",
            "data_type": request.analysis_type,
            "data_size": len(str(request.data)),
            "requester": "data_analyzer",
        }

        context = {"priority": request.priority, "purpose": "user_requested_analysis"}

        return await self.guardian_service.validate_action(action, context)

    async def _get_consciousness_input(self, request: AnalysisRequest) -> dict[str, Any]:
        """Get consciousness assessment for the analysis"""
        # Assess what aspects to focus on
        awareness = await self.consciousness_service.assess_awareness(
            {
                "stimulus": request.data,
                "context": {"analysis_type": request.analysis_type},
            }
        )

        # Get decision on analysis approach
        decision = await self.consciousness_service.make_decision(
            {
                "scenario": "analysis_approach",
                "options": ["detailed", "summary", "pattern_focus"],
                "context": {"data_complexity": self._assess_complexity(request.data)},
            }
        )

        return {
            "focus_areas": awareness.get("attention_targets", []),
            "approach": decision.get("selected_option", "detailed"),
            "confidence_modifier": decision.get("confidence", 1.0),
        }

    async def _perform_analysis(
        self, request: AnalysisRequest, consciousness_input: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Perform the actual data analysis"""
        # Simulate analysis based on type
        findings = {
            "analysis_type": request.analysis_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_points": len(request.data),
            "patterns_found": [],
        }

        # Example pattern detection
        if request.analysis_type == "pattern":
            patterns = self._detect_patterns(request.data)
            findings["patterns_found"] = patterns
            findings["pattern_count"] = len(patterns)

        # Apply consciousness input if available
        if consciousness_input:
            findings["approach_used"] = consciousness_input["approach"]
            findings["focus_areas"] = consciousness_input["focus_areas"]
            findings["confidence"] = 0.8 * consciousness_input["confidence_modifier"]
        else:
            findings["confidence"] = 0.8

        # Assess significance
        findings["significance"] = self._assess_significance(findings)

        return findings

    def _detect_patterns(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Detect patterns in data (simplified example)"""
        patterns = []

        # Example: Find repeated values
        values = []
        for value in data.values():
            if isinstance(value, (str, int, float)):
                values.append(value)

        # Count occurrences
        from collections import Counter

        value_counts = Counter(values)

        for value, count in value_counts.items():
            if count > 1:
                patterns.append({"type": "repetition", "value": str(value), "occurrences": count})

        return patterns

    def _assess_complexity(self, data: dict[str, Any]) -> float:
        """Assess data complexity (0.0-1.0)"""
        # Simple heuristic based on structure
        complexity = 0.0

        # Factor in data size
        complexity += min(len(data) / 100, 0.3)

        # Factor in nesting depth
        max_depth = self._get_max_depth(data)
        complexity += min(max_depth / 10, 0.3)

        # Factor in data types diversity
        types = set()
        for value in data.values():
            types.add(type(value).__name__)
        complexity += min(len(types) / 10, 0.4)

        return min(complexity, 1.0)

    def _get_max_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Get maximum nesting depth of object"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def _assess_significance(self, findings: dict[str, Any]) -> float:
        """Assess significance of findings (0.0-1.0)"""
        significance = 0.0

        # Pattern detection increases significance
        if findings.get("pattern_count", 0) > 0:
            significance += min(findings["pattern_count"] * 0.1, 0.5)

        # High confidence increases significance
        significance += findings.get("confidence", 0) * 0.3

        # More data points increase significance
        significance += min(findings.get("data_points", 0) / 1000, 0.2)

        return min(significance, 1.0)

    async def _store_in_memory(self, request: AnalysisRequest, result: AnalysisResult) -> str:
        """Store analysis in memory system"""
        memory_content = {
            "request": {
                "analysis_type": request.analysis_type,
                "priority": request.priority,
                "data_summary": f"Data with {len(request.data)} fields",
            },
            "result": {"findings": result.findings, "confidence": result.confidence},
        }

        metadata = {
            "module": "data_analyzer",
            "significance": result.findings.get("significance", 0.5),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return await self.memory_service.store(
            content=memory_content, memory_type=MemoryType.SEMANTIC, metadata=metadata
        )

    def _update_average_time(self, elapsed_ms: float) -> None:
        """Update average processing time"""
        total_analyses = self.metrics["analyses_completed"]
        if total_analyses == 1:
            self.metrics["average_time_ms"] = elapsed_ms
        else:
            # Running average
            current_avg = self.metrics["average_time_ms"]
            self.metrics["average_time_ms"] = (current_avg * (total_analyses - 1) + elapsed_ms) / total_analyses

    # Required interface methods

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the module (interface requirement)"""
        if not self.operational:
            raise LukhasError("Module not operational")

        # Convert to analysis request
        request = AnalysisRequest(
            data=data,
            analysis_type=data.get("analysis_type", "general"),
            priority=data.get("priority", "normal"),
            ethical_check=data.get("ethical_check", True),
        )

        # Perform analysis
        result = await self.analyze_data(request)

        # Convert result to dict
        return {
            "request_id": result.request_id,
            "findings": result.findings,
            "confidence": result.confidence,
            "memory_id": result.memory_id,
        }

    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token communication (interface requirement)"""
        logger.debug(f"Received GLYPH token: {token.symbol}")

        response_payload = {}

        # Handle different GLYPH symbols
        if token.symbol == GLYPHSymbol.QUERY:
            # Status query
            response_payload = await self.get_status()

        elif token.symbol == GLYPHSymbol.ANALYZE:
            # Analysis request via GLYPH
            if "data" in token.payload:
                try:
                    result = await self.process(token.payload)
                    response_payload = {"success": True, "result": result}
                except Exception as e:
                    response_payload = {"success": False, "error": str(e)}
            else:
                response_payload = {"error": "No data provided"}

        elif token.symbol == GLYPHSymbol.REFLECT:
            # Reflection on past analyses
            recent_analyses = self._analysis_history[-5:]
            response_payload = {
                "recent_analyses": len(recent_analyses),
                "success_rate": self._calculate_success_rate(),
                "average_confidence": self._calculate_average_confidence(),
            }

        else:
            response_payload = {"error": f"Unknown symbol: {token.symbol}"}

        # Create response token
        return GLYPHToken(
            symbol=GLYPHSymbol.ACKNOWLEDGE,
            source="data_analyzer",
            target=token.source,
            payload=response_payload,
        )

    async def get_status(self) -> dict[str, Any]:
        """Get module status (interface requirement)"""
        health_score = self._calculate_health_score()

        return {
            "operational": self.operational,
            "health_score": health_score,
            "last_update": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "analyses_completed": self.metrics["analyses_completed"],
                "analyses_failed": self.metrics["analyses_failed"],
                "success_rate": self._calculate_success_rate(),
                "average_time_ms": self.metrics["average_time_ms"],
                "memory_stores": self.metrics["memory_stores"],
                "ethical_rejections": self.metrics["ethical_rejections"],
            },
            "dependencies": {
                "memory_service": self.memory_service is not None,
                "consciousness_service": self.consciousness_service is not None,
                "guardian_service": self.guardian_service is not None,
            },
        }

    def _calculate_health_score(self) -> float:
        """Calculate module health score (0.0-1.0)"""
        if not self.operational:
            return 0.0

        # Start with perfect health
        health = 1.0

        # Deduct for failures
        total_attempts = self.metrics["analyses_completed"] + self.metrics["analyses_failed"]
        if total_attempts > 0:
            failure_rate = self.metrics["analyses_failed"] / total_attempts
            health -= failure_rate * 0.5

        # Deduct for missing services
        if not self.memory_service:
            health -= 0.1
        if not self.consciousness_service:
            health -= 0.1
        if not self.guardian_service:
            health -= 0.1

        # Deduct for high rejection rate
        if self.metrics["analyses_completed"] > 0:
            rejection_rate = self.metrics["ethical_rejections"] / self.metrics["analyses_completed"]
            if rejection_rate > 0.2:
                health -= 0.2

        return max(health, 0.0)

    def _calculate_success_rate(self) -> float:
        """Calculate analysis success rate"""
        total = self.metrics["analyses_completed"] + self.metrics["analyses_failed"]
        if total == 0:
            return 1.0
        return self.metrics["analyses_completed"] / total

    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence from recent analyses"""
        if not self._analysis_history:
            return 0.0

        total_confidence = sum(r.confidence for r in self._analysis_history)
        return total_confidence / len(self._analysis_history)


# Example usage and testing
async def main():
    """Example usage of the DataAnalyzer module"""

    # Create and initialize module
    analyzer = DataAnalyzer(config={"max_history": 100})

    # In a real system, these services would be already registered
    # For this example, we'll create simple mocks
    from unittest.mock import AsyncMock, Mock

    # Mock services
    mock_memory = Mock()
    mock_memory.get_status = AsyncMock(return_value={"operational": True})
    mock_memory.store = AsyncMock(return_value="mem_12345")

    mock_consciousness = Mock()
    mock_consciousness.assess_awareness = AsyncMock(return_value={"overall_awareness": 0.8})
    mock_consciousness.make_decision = AsyncMock(return_value={"selected_option": "detailed", "confidence": 0.9})

    mock_guardian = Mock()
    mock_guardian.validate_action = AsyncMock(
        return_value={"approved": True, "reasoning": "Action is safe and ethical"}
    )

    # Register mock services
    from core.interfaces.dependency_injection import register_service

    register_service("memory_service", mock_memory)
    register_service("consciousness_service", mock_consciousness)
    register_service("guardian_service", mock_guardian)

    # Initialize analyzer
    await analyzer.initialize()

    # Example 1: Simple analysis
    print("Example 1: Simple Analysis")
    print("-" * 50)

    request = AnalysisRequest(
        data={
            "temperature": 22.5,
            "humidity": 65,
            "pressure": 1013,
            "location": "lab_1",
            "sensor": "env_sensor_01",
        },
        analysis_type="pattern",
        priority="normal",
    )

    result = await analyzer.analyze_data(request)
    print("Analysis Result:")
    print(f"  Request ID: {result.request_id}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Patterns found: {result.findings.get('pattern_count', 0)}")
    print(f"  Memory stored: {result.memory_id is not None}")
    print()

    # Example 2: GLYPH communication
    print("Example 2: GLYPH Communication")
    print("-" * 50)

    # Query status via GLYPH
    query_token = GLYPHToken(
        symbol=GLYPHSymbol.QUERY,
        source="test_client",
        target="data_analyzer",
        payload={},
    )

    response = await analyzer.handle_glyph(query_token)
    print("GLYPH Response:")
    print(f"  Health Score: {response.payload['health_score']}")
    print(f"  Analyses Completed: {response.payload['metrics']['analyses_completed']}")
    print()

    # Example 3: Get module status
    print("Example 3: Module Status")
    print("-" * 50)

    status = await analyzer.get_status()
    print("Module Status:")
    print(f"  Operational: {status['operational']}")
    print(f"  Health Score: {status['health_score']:.2f}")
    print(f"  Success Rate: {status['metrics']['success_rate']:.2%}")
    print(f"  Average Time: {status['metrics']['average_time_ms']:.2f}ms")
    print(f"  Dependencies: {status['dependencies']}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())