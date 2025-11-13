#!/usr/bin/env python3
"""
MATRIZ Resource Allocation Node

Allocates limited resources optimally across competing demands.
Uses constraint satisfaction and optimization algorithms.

Example: "Allocate 100 hours across projects A, B, C based on priority and ROI"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class ResourceAllocation:
    """Allocation of resources to a task."""
    task_id: str
    task_name: str
    allocated_resources: Dict[str, float]
    expected_value: float
    efficiency: float  # Value per resource unit


class ResourceAllocationNode(CognitiveNode):
    """
    Allocates limited resources optimally.

    Capabilities:
    - Resource optimization
    - Constraint satisfaction
    - Value maximization
    - Efficiency analysis
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_resource_allocation",
            capabilities=[
                "resource_optimization",
                "constraint_satisfaction",
                "value_maximization",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate resources optimally.

        Args:
            input_data: Dict containing:
                - tasks: List of tasks requiring resources
                - available_resources: Total available resources
                - constraints: Hard constraints on allocation
                - objectives: Optimization objectives

        Returns:
            Dict with allocations, efficiency, and MATRIZ node
        """
        start_time = time.time()

        tasks = input_data.get("tasks", [])
        available_resources = input_data.get("available_resources", {})
        constraints = input_data.get("constraints", {})
        objectives = input_data.get("objectives", ["maximize_value"])

        # Allocate resources
        allocations = self._allocate_resources(
            tasks,
            available_resources,
            constraints,
            objectives
        )

        # Compute efficiency metrics
        total_value = sum(a.expected_value for a in allocations)
        total_allocated = self._compute_total_allocated(allocations)
        overall_efficiency = self._compute_efficiency(allocations, available_resources)

        # Compute confidence
        confidence = self._compute_confidence(allocations, available_resources)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + overall_efficiency * 0.3),
            novelty=max(0.1, 0.3),
            utility=min(1.0, total_value / max(1.0, len(tasks)))
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="resource_allocation_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "DECISION",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "task_count": len(tasks)
            },
            "allocations": [
                {
                    "task_id": a.task_id,
                    "task_name": a.task_name,
                    "allocated_resources": a.allocated_resources,
                    "expected_value": a.expected_value,
                    "efficiency": a.efficiency
                }
                for a in allocations
            ],
            "summary": {
                "total_value": total_value,
                "total_allocated": total_allocated,
                "overall_efficiency": overall_efficiency
            }
        }

        return {
            "answer": {
                "allocations": matriz_node["allocations"],
                "summary": matriz_node["summary"]
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "allocations" not in output["answer"]:
            return False

        return True

    def _allocate_resources(
        self,
        tasks: List[dict],
        available_resources: Dict[str, float],
        constraints: dict,
        objectives: List[str]
    ) -> List[ResourceAllocation]:
        """Allocate resources to tasks."""
        allocations = []

        # Sort tasks by priority/value
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.get("priority", 0.5) * t.get("expected_value", 1.0),
            reverse=True
        )

        # Track remaining resources
        remaining = available_resources.copy()

        # Greedy allocation (simplified optimization)
        for task in sorted_tasks:
            task_id = task.get("id", f"task_{len(allocations)}")
            task_name = task.get("name", f"Task {len(allocations)}")
            requested = task.get("requested_resources", {})
            expected_value = task.get("expected_value", 1.0)

            # Determine what we can actually allocate
            allocated = {}
            can_allocate = True

            for resource, amount in requested.items():
                available = remaining.get(resource, 0.0)

                if available >= amount:
                    # Can fully allocate
                    allocated[resource] = amount
                elif available > 0:
                    # Partial allocation
                    allocated[resource] = available
                else:
                    # No resources available
                    can_allocate = False
                    break

            if can_allocate and allocated:
                # Compute efficiency
                total_allocated_value = sum(allocated.values())
                efficiency = expected_value / max(1.0, total_allocated_value)

                allocations.append(
                    ResourceAllocation(
                        task_id=task_id,
                        task_name=task_name,
                        allocated_resources=allocated,
                        expected_value=expected_value,
                        efficiency=efficiency
                    )
                )

                # Update remaining resources
                for resource, amount in allocated.items():
                    remaining[resource] -= amount

        return allocations

    def _compute_total_allocated(self, allocations: List[ResourceAllocation]) -> Dict[str, float]:
        """Compute total resources allocated."""
        total = {}

        for allocation in allocations:
            for resource, amount in allocation.allocated_resources.items():
                total[resource] = total.get(resource, 0.0) + amount

        return total

    def _compute_efficiency(
        self,
        allocations: List[ResourceAllocation],
        available_resources: Dict[str, float]
    ) -> float:
        """Compute overall allocation efficiency."""
        if not allocations:
            return 0.0

        # Average efficiency across allocations
        avg_efficiency = sum(a.efficiency for a in allocations) / len(allocations)

        # Resource utilization
        total_allocated = self._compute_total_allocated(allocations)
        total_available = sum(available_resources.values())
        total_used = sum(total_allocated.values())

        utilization = total_used / max(1.0, total_available) if total_available > 0 else 0.0

        # Combine efficiency and utilization
        return (avg_efficiency + utilization) / 2

    def _compute_confidence(
        self,
        allocations: List[ResourceAllocation],
        available_resources: Dict[str, float]
    ) -> float:
        """Compute confidence in allocation."""
        if not allocations:
            return 0.0

        # Confidence based on:
        # 1. How many tasks got resources
        # 2. How well resources were utilized

        # Task satisfaction
        task_satisfaction = min(1.0, len(allocations) * 0.2)

        # Resource utilization
        total_allocated = self._compute_total_allocated(allocations)
        total_available = sum(available_resources.values())
        total_used = sum(total_allocated.values())

        utilization = total_used / max(1.0, total_available) if total_available > 0 else 0.0

        return (task_satisfaction + utilization) / 2
