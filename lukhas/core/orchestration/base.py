"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - BASE ORCHESTRATOR PATTERN
║ Foundation for all orchestrators in the LUKHAS system
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: base.py
║ Path: lukhas/orchestration/base.py
║ Version: 1.0.0 | Created: 2025-07-26
║ Authors: LUKHAS AI Architecture Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module provides the foundational BaseOrchestrator abstract class that all
║ orchestrators in the LUKHAS system must inherit from. It enforces consistent
║ patterns for initialization, lifecycle management, error handling, and monitoring.
║
║ HIERARCHY:
║ BaseOrchestrator (Abstract)
║  ├── ModuleOrchestrator - Orchestrates within a single module
║  ├── SystemOrchestrator - Orchestrates across multiple modules
║  └── MasterOrchestrator - Top-level system coordination
║
║ KEY PATTERNS:
║ - Async-first design for concurrent operations
║ - Standardized lifecycle (initialize → start → process → stop)
║ - Built-in health monitoring and metrics
║ - Consistent error handling and recovery
║ - Configuration management
║ - Component registration and discovery
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import contextlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class OrchestratorState(Enum):
    """Standardized orchestrator states"""

    UNINITIALIZED = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


class ComponentStatus(Enum):
    """Status of managed components"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class OrchestratorConfig:
    """Base configuration for all orchestrators"""

    name: str
    description: str = ""
    max_concurrent_operations: int = 10
    health_check_interval: int = 30  # seconds
    enable_metrics: bool = True
    enable_detailed_logging: bool = False
    retry_attempts: int = 3
    timeout_seconds: int = 30
    config_path: Optional[Path] = None
    custom_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentInfo:
    """Information about a managed component"""

    name: str
    type: str
    status: ComponentStatus = ComponentStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorMetrics:
    """Standard metrics for orchestrators"""

    start_time: datetime = field(default_factory=datetime.now)
    operations_completed: int = 0
    operations_failed: int = 0
    average_operation_time: float = 0.0
    current_load: float = 0.0
    component_health: dict[str, ComponentStatus] = field(default_factory=dict)


class BaseOrchestrator(ABC):
    """
    Abstract base class for all LUKHAS orchestrators.

    Provides standardized patterns for:
    - Component lifecycle management
    - Health monitoring
    - Error handling and recovery
    - Metrics collection
    - Configuration management
    """

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.state = OrchestratorState.UNINITIALIZED
        self.components: dict[str, ComponentInfo] = {}
        self.metrics = OrchestratorMetrics()
        self._health_check_task: Optional[asyncio.Task] = None
        self._operation_semaphore = asyncio.Semaphore(config.max_concurrent_operations)

        # Load additional configuration if path provided
        if config.config_path:
            self._load_additional_config(config.config_path)

        self.logger.info(f"Initialized {self.__class__.__name__}: {config.name}")

    def _setup_logging(self) -> logging.Logger:
        """Setup standardized logging for the orchestrator"""
        logger_name = f"LUKHAS.{self.__class__.__name__}.{self.config.name}"
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(
                logging.DEBUG if self.config.enable_detailed_logging else logging.INFO
            )

        return logger

    def _load_additional_config(self, config_path: Path) -> None:
        """Load additional configuration from file"""
        try:
            with open(config_path) as f:
                additional_config = json.load(f)
                self.config.custom_config.update(additional_config)
                self.logger.info(f"Loaded additional config from {config_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load config from {config_path}: {e}")

    # === Lifecycle Management ===

    async def initialize(self) -> bool:
        """Initialize the orchestrator and its components"""
        if self.state != OrchestratorState.UNINITIALIZED:
            self.logger.warning(f"Cannot initialize from state {self.state}")
            return False

        self.state = OrchestratorState.INITIALIZING
        self.logger.info("Starting initialization")

        try:
            # Initialize components
            success = await self._initialize_components()
            if not success:
                raise Exception("Component initialization failed")

            # Perform custom initialization
            await self._custom_initialize()

            self.state = OrchestratorState.INITIALIZED
            self.logger.info("Initialization complete")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.state = OrchestratorState.ERROR
            return False

    @abstractmethod
    async def _initialize_components(self) -> bool:
        """Initialize managed components. Must be implemented by subclasses."""

    async def _custom_initialize(self) -> None:
        """Optional custom initialization. Override in subclasses if needed."""

    async def start(self) -> bool:
        """Start the orchestrator"""
        if self.state != OrchestratorState.INITIALIZED:
            self.logger.warning(f"Cannot start from state {self.state}")
            return False

        self.state = OrchestratorState.STARTING
        self.logger.info("Starting orchestrator")

        try:
            # Start health monitoring
            if self.config.enable_metrics:
                self._health_check_task = asyncio.create_task(self._health_monitor())

            # Start components
            await self._start_components()

            # Custom startup logic
            await self._custom_start()

            self.state = OrchestratorState.RUNNING
            self.metrics.start_time = datetime.now()
            self.logger.info("Orchestrator started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Start failed: {e}")
            self.state = OrchestratorState.ERROR
            return False

    @abstractmethod
    async def _start_components(self) -> None:
        """Start managed components. Must be implemented by subclasses."""

    async def _custom_start(self) -> None:
        """Optional custom startup logic. Override in subclasses if needed."""

    async def stop(self) -> bool:
        """Stop the orchestrator"""
        if self.state != OrchestratorState.RUNNING:
            self.logger.warning(f"Cannot stop from state {self.state}")
            return False

        self.state = OrchestratorState.STOPPING
        self.logger.info("Stopping orchestrator")

        try:
            # Stop health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._health_check_task

            # Stop components
            await self._stop_components()

            # Custom shutdown logic
            await self._custom_stop()

            self.state = OrchestratorState.STOPPED
            self.logger.info("Orchestrator stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stop failed: {e}")
            self.state = OrchestratorState.ERROR
            return False

    @abstractmethod
    async def _stop_components(self) -> None:
        """Stop managed components. Must be implemented by subclasses."""

    async def _custom_stop(self) -> None:
        """Optional custom shutdown logic. Override in subclasses if needed."""

    # === Component Management ===

    def register_component(
        self,
        name: str,
        component_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a component for management"""
        self.components[name] = ComponentInfo(
            name=name, type=component_type, metadata=metadata or {}
        )
        self.logger.debug(f"Registered component: {name} ({component_type})")

    def unregister_component(self, name: str) -> None:
        """Unregister a component"""
        if name in self.components:
            del self.components[name]
            self.logger.debug(f"Unregistered component: {name}")

    async def check_component_health(self, name: str) -> ComponentStatus:
        """Check health of a specific component"""
        if name not in self.components:
            return ComponentStatus.UNKNOWN

        try:
            status = await self._check_component_health(name)
            self.components[name].status = status
            self.components[name].last_health_check = datetime.now()
            return status
        except Exception as e:
            self.logger.error(f"Health check failed for {name}: {e}")
            return ComponentStatus.UNHEALTHY

    @abstractmethod
    async def _check_component_health(self, name: str) -> ComponentStatus:
        """Implementation-specific health check. Must be implemented by subclasses."""

    # === Operation Processing ===

    async def process(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Process an operation with proper error handling and metrics"""
        if self.state != OrchestratorState.RUNNING:
            return {
                "success": False,
                "error": f"Orchestrator not running (state: {self.state})",
            }

        async with self._operation_semaphore:
            start_time = time.time()

            try:
                result = await self._process_operation(operation)

                # Update metrics
                self.metrics.operations_completed += 1
                operation_time = time.time() - start_time
                self._update_average_operation_time(operation_time)

                return result

            except Exception as e:
                self.logger.error(f"Operation failed: {e}")
                self.metrics.operations_failed += 1

                # Attempt recovery
                if await self._handle_operation_error(operation, e):
                    # Retry if recovery successful
                    return await self.process(operation)

                return {"success": False, "error": str(e)}

    @abstractmethod
    async def _process_operation(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Process a specific operation. Must be implemented by subclasses."""

    async def _handle_operation_error(
        self, operation: dict[str, Any], error: Exception
    ) -> bool:
        """Handle operation errors. Override for custom error handling."""
        return False  # Default: no recovery

    # === Health Monitoring ===

    async def _health_monitor(self) -> None:
        """Background task for health monitoring"""
        while self.state == OrchestratorState.RUNNING:
            try:
                # Check all components
                for name in self.components:
                    status = await self.check_component_health(name)
                    self.metrics.component_health[name] = status

                # Calculate overall health
                await self._update_orchestrator_health()

                # Wait for next check
                await asyncio.sleep(self.config.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")

    async def _update_orchestrator_health(self) -> None:
        """Update overall orchestrator health metrics"""
        # Calculate current load
        active_operations = (
            self.config.max_concurrent_operations - self._operation_semaphore._value
        )
        self.metrics.current_load = (
            active_operations / self.config.max_concurrent_operations
        )

    def _update_average_operation_time(self, operation_time: float) -> None:
        """Update rolling average of operation time"""
        total_ops = self.metrics.operations_completed
        if total_ops == 1:
            self.metrics.average_operation_time = operation_time
        else:
            # Rolling average
            self.metrics.average_operation_time = (
                self.metrics.average_operation_time * (total_ops - 1) + operation_time
            ) / total_ops

    # === Utility Methods ===

    def get_status(self) -> dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "name": self.config.name,
            "type": self.__class__.__name__,
            "state": self.state.name,
            "uptime": str(datetime.now() - self.metrics.start_time),
            "metrics": {
                "operations_completed": self.metrics.operations_completed,
                "operations_failed": self.metrics.operations_failed,
                "average_operation_time": f"{self.metrics.average_operation_time:.3f}s",
                "current_load": f"{self.metrics.current_load:.1%}",
            },
            "components": {
                name: info.status.value for name, info in self.components.items()
            },
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.config.name}', state={self.state.name})"
