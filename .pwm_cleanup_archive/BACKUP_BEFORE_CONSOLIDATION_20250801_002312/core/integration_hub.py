"""
Unified Integration Module for Core Systems
Provides unified integration capabilities for various system components.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class IntegrationConfig:
    """Configuration for unified integration."""

    max_concurrent_operations: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    integration_logging: bool = True
    async_processing: bool = True
    component_isolation: bool = True

    def __post_init__(self):
        """Validate configuration."""
        self.max_concurrent_operations = max(
            1, min(100, self.max_concurrent_operations)
        )
        self.timeout_seconds = max(1, min(300, self.timeout_seconds))
        self.retry_attempts = max(0, min(10, self.retry_attempts))


@dataclass
class IntegrationResult:
    """Result of an integration operation."""

    success: bool
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: float = 0.0
    component_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class UnifiedIntegration:
    """
    Unified integration system for coordinating multiple components.

    This class provides a centralized integration layer that can coordinate
    various system components, handle async operations, and manage data flow.
    """

    def __init__(self, config: Optional[IntegrationConfig] = None):
        """
        Initialize the unified integration system.

        Args:
            config: Configuration for integration behavior
        """
        self.config = config or IntegrationConfig()
        self.components = {}
        self.integration_handlers = {}
        self.operation_queue = []
        self.active_operations = {}
        self.integration_history = []
        self.logger = self._setup_logger()
        self.lock = threading.Lock()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the integration system."""
        logger = logging.getLogger("UnifiedIntegration")
        if self.config.integration_logging:
            logger.setLevel(logging.INFO)

            # Create console handler if not already exists
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
        else:
            logger.setLevel(logging.CRITICAL)

        return logger

    def register_component(
        self,
        component_id: str,
        component: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntegrationResult:
        """
        Register a component with the integration system.

        Args:
            component_id: Unique identifier for the component
            component: The component instance
            metadata: Optional metadata about the component

        Returns:
            Integration result
        """
        try:
            with self.lock:
                if component_id in self.components:
                    return IntegrationResult(
                        success=False,
                        error_message=f"Component {component_id} already registered",
                    )

                self.components[component_id] = {
                    "instance": component,
                    "metadata": metadata or {},
                    "registered_at": datetime.now().isoformat(),
                    "active": True,
                }

                self.logger.info(f"Registered component: {component_id}")

                return IntegrationResult(
                    success=True,
                    result_data={"component_id": component_id, "registered": True},
                    component_id=component_id,
                )

        except Exception as e:
            return IntegrationResult(
                success=False,
                error_message=f"Failed to register component {component_id}: {str(e)}",
                component_id=component_id,
            )

    def unregister_component(self, component_id: str) -> IntegrationResult:
        """
        Unregister a component from the integration system.

        Args:
            component_id: Component identifier to unregister

        Returns:
            Integration result
        """
        try:
            with self.lock:
                if component_id not in self.components:
                    return IntegrationResult(
                        success=False,
                        error_message=f"Component {component_id} not found",
                    )

                del self.components[component_id]

                self.logger.info(f"Unregistered component: {component_id}")

                return IntegrationResult(
                    success=True,
                    result_data={"component_id": component_id, "unregistered": True},
                    component_id=component_id,
                )

        except Exception as e:
            return IntegrationResult(
                success=False,
                error_message=f"Failed to unregister component {component_id}: {str(e)}",
                component_id=component_id,
            )

    def invoke_component(
        self,
        component_id: str,
        method_name: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> IntegrationResult:
        """
        Invoke a method on a registered component.

        Args:
            component_id: Component identifier
            method_name: Name of the method to invoke
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method

        Returns:
            Integration result
        """
        start_time = datetime.now()

        try:
            if component_id not in self.components:
                return IntegrationResult(
                    success=False,
                    error_message=f"Component {component_id} not found",
                    component_id=component_id,
                )

            component_info = self.components[component_id]
            component_instance = component_info["instance"]

            # Check if method exists
            if not hasattr(component_instance, method_name):
                return IntegrationResult(
                    success=False,
                    error_message=f"Method {method_name} not found on component {component_id}",
                    component_id=component_id,
                )

            # Get the method
            method = getattr(component_instance, method_name)

            # Invoke the method
            args = args or []
            kwargs = kwargs or {}

            result = method(*args, **kwargs)

            execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Successfully invoked {component_id}.{method_name}")

            return IntegrationResult(
                success=True,
                result_data={"method_result": result, "method_name": method_name},
                execution_time=execution_time,
                component_id=component_id,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.error(
                f"Failed to invoke {component_id}.{method_name}: {str(e)}"
            )

            return IntegrationResult(
                success=False,
                error_message=f"Failed to invoke {component_id}.{method_name}: {str(e)}",
                execution_time=execution_time,
                component_id=component_id,
            )

    def batch_invoke(self, operations: List[Dict[str, Any]]) -> List[IntegrationResult]:
        """
        Perform batch invocation of multiple operations.

        Args:
            operations: List of operation dictionaries with component_id, method_name, args, kwargs

        Returns:
            List of integration results
        """
        results = []

        for operation in operations:
            component_id = operation.get("component_id")
            method_name = operation.get("method_name")
            args = operation.get("args", [])
            kwargs = operation.get("kwargs", {})

            result = self.invoke_component(component_id, method_name, args, kwargs)
            results.append(result)

            # Add operation tracking
            self.integration_history.append(
                {
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return results

    def create_data_pipeline(
        self, pipeline_config: Dict[str, Any]
    ) -> IntegrationResult:
        """
        Create a data processing pipeline.

        Args:
            pipeline_config: Configuration for the pipeline

        Returns:
            Integration result
        """
        try:
            pipeline_id = pipeline_config.get(
                "id", f"pipeline_{len(self.integration_handlers)}"
            )
            steps = pipeline_config.get("steps", [])

            if not steps:
                return IntegrationResult(
                    success=False, error_message="Pipeline must have at least one step"
                )

            pipeline = {
                "id": pipeline_id,
                "steps": steps,
                "created_at": datetime.now().isoformat(),
                "active": True,
            }

            self.integration_handlers[pipeline_id] = pipeline

            self.logger.info(f"Created data pipeline: {pipeline_id}")

            return IntegrationResult(
                success=True,
                result_data={"pipeline_id": pipeline_id, "steps": len(steps)},
                component_id=pipeline_id,
            )

        except Exception as e:
            return IntegrationResult(
                success=False, error_message=f"Failed to create pipeline: {str(e)}"
            )

    def execute_pipeline(self, pipeline_id: str, input_data: Any) -> IntegrationResult:
        """
        Execute a data processing pipeline.

        Args:
            pipeline_id: Pipeline identifier
            input_data: Input data for the pipeline

        Returns:
            Integration result
        """
        start_time = datetime.now()

        try:
            if pipeline_id not in self.integration_handlers:
                return IntegrationResult(
                    success=False, error_message=f"Pipeline {pipeline_id} not found"
                )

            pipeline = self.integration_handlers[pipeline_id]
            steps = pipeline["steps"]

            current_data = input_data
            step_results = []

            for i, step in enumerate(steps):
                step_component_id = step.get("component_id")
                step_method = step.get("method_name")
                step_args = step.get("args", [])
                step_kwargs = step.get("kwargs", {})

                # Add current data as first argument
                step_args = [current_data] + step_args

                # Execute step
                step_result = self.invoke_component(
                    step_component_id, step_method, step_args, step_kwargs
                )
                step_results.append(step_result)

                if not step_result.success:
                    return IntegrationResult(
                        success=False,
                        error_message=f"Pipeline step {i} failed: {step_result.error_message}",
                        result_data={"step_results": step_results, "failed_step": i},
                    )

                # Update current data for next step
                current_data = step_result.result_data.get(
                    "method_result", current_data
                )

            execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Successfully executed pipeline: {pipeline_id}")

            return IntegrationResult(
                success=True,
                result_data={
                    "pipeline_result": current_data,
                    "step_results": step_results,
                    "steps_executed": len(steps),
                },
                execution_time=execution_time,
                component_id=pipeline_id,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            return IntegrationResult(
                success=False,
                error_message=f"Failed to execute pipeline {pipeline_id}: {str(e)}",
                execution_time=execution_time,
                component_id=pipeline_id,
            )

    def get_component_status(
        self, component_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get status information for components.

        Args:
            component_id: Optional specific component ID, None for all components

        Returns:
            Status information
        """
        if component_id:
            if component_id not in self.components:
                return {"error": f"Component {component_id} not found"}

            component_info = self.components[component_id]
            return {
                "component_id": component_id,
                "active": component_info["active"],
                "registered_at": component_info["registered_at"],
                "metadata": component_info["metadata"],
                "instance_type": type(component_info["instance"]).__name__,
            }
        else:
            return {
                "total_components": len(self.components),
                "active_components": sum(
                    1 for c in self.components.values() if c["active"]
                ),
                "components": {
                    cid: {
                        "active": info["active"],
                        "registered_at": info["registered_at"],
                        "instance_type": type(info["instance"]).__name__,
                    }
                    for cid, info in self.components.items()
                },
            }

    def get_integration_metrics(self) -> Dict[str, Any]:
        """
        Get integration system metrics.

        Returns:
            Metrics dictionary
        """
        total_operations = len(self.integration_history)
        successful_operations = sum(
            1 for h in self.integration_history if h["result"].success
        )

        return {
            "total_components": len(self.components),
            "active_components": sum(
                1 for c in self.components.values() if c["active"]
            ),
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": (
                successful_operations / total_operations
                if total_operations > 0
                else 0.0
            ),
            "active_pipelines": len(self.integration_handlers),
            "config": {
                "max_concurrent_operations": self.config.max_concurrent_operations,
                "timeout_seconds": self.config.timeout_seconds,
                "retry_attempts": self.config.retry_attempts,
            },
        }

    def cleanup(self):
        """Clean up resources and reset the integration system."""
        with self.lock:
            self.components.clear()
            self.integration_handlers.clear()
            self.operation_queue.clear()
            self.active_operations.clear()
            self.integration_history.clear()

        self.logger.info("Integration system cleaned up")

    def export_configuration(self) -> Dict[str, Any]:
        """
        Export current configuration and component setup.

        Returns:
            Configuration dictionary
        """
        return {
            "components": {
                cid: {
                    "metadata": info["metadata"],
                    "registered_at": info["registered_at"],
                    "active": info["active"],
                    "instance_type": type(info["instance"]).__name__,
                }
                for cid, info in self.components.items()
            },
            "pipelines": {
                pid: {
                    "steps": pipeline["steps"],
                    "created_at": pipeline["created_at"],
                    "active": pipeline["active"],
                }
                for pid, pipeline in self.integration_handlers.items()
            },
            "config": {
                "max_concurrent_operations": self.config.max_concurrent_operations,
                "timeout_seconds": self.config.timeout_seconds,
                "retry_attempts": self.config.retry_attempts,
                "integration_logging": self.config.integration_logging,
                "async_processing": self.config.async_processing,
                "component_isolation": self.config.component_isolation,
            },
            "export_timestamp": datetime.now().isoformat(),
        }

    def import_configuration(self, config_data: Dict[str, Any]) -> IntegrationResult:
        """
        Import configuration and recreate pipelines.

        Args:
            config_data: Configuration data to import

        Returns:
            Integration result
        """
        try:
            # Import pipelines
            pipelines = config_data.get("pipelines", {})
            imported_pipelines = 0

            for pipeline_id, pipeline_data in pipelines.items():
                pipeline_config = {"id": pipeline_id, "steps": pipeline_data["steps"]}

                result = self.create_data_pipeline(pipeline_config)
                if result.success:
                    imported_pipelines += 1

            self.logger.info(f"Imported {imported_pipelines} pipelines")

            return IntegrationResult(
                success=True,
                result_data={
                    "imported_pipelines": imported_pipelines,
                    "total_pipelines": len(pipelines),
                },
            )

        except Exception as e:
            return IntegrationResult(
                success=False, error_message=f"Failed to import configuration: {str(e)}"
            )
