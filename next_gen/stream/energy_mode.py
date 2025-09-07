#!/usr/bin/env python3
"""
Energy-conscious Mode - Adaptive throttling and resource management
Monitors system load and adjusts operation intensity with moon symbol 🌙
"""
import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class EnergyProfile:
    """Energy consumption profile"""

    profile_name: str
    cpu_threshold: float  # 0.0 to 1.0
    memory_threshold: float  # 0.0 to 1.0
    operation_delay: float  # seconds
    max_concurrent: int
    throttle_factor: float  # 0.1 to 1.0
    symbolic_indicator: str
    description: str


@dataclass
class SystemMetrics:
    """Current system performance metrics"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io: float
    network_io: float
    temperature: Optional[float] = None
    battery_level: Optional[float] = None
    energy_score: float = 0.0  # Calculated composite score


class EnergyManager:
    """
    Manages system energy consumption and adaptive throttling
    Provides different energy profiles for various operation modes
    """

    # Energy profiles from most efficient to most intensive
    ENERGY_PROFILES = {
        "deep_sleep": EnergyProfile(
            profile_name="deep_sleep",
            cpu_threshold=0.05,
            memory_threshold=0.3,
            operation_delay=5.0,
            max_concurrent=1,
            throttle_factor=0.1,
            symbolic_indicator="🌙",
            description="Minimal operations, maximum efficiency",
        ),
        "power_save": EnergyProfile(
            profile_name="power_save",
            cpu_threshold=0.2,
            memory_threshold=0.5,
            operation_delay=2.0,
            max_concurrent=2,
            throttle_factor=0.3,
            symbolic_indicator="🔋",
            description="Conservative resource usage",
        ),
        "balanced": EnergyProfile(
            profile_name="balanced",
            cpu_threshold=0.5,
            memory_threshold=0.7,
            operation_delay=0.5,
            max_concurrent=4,
            throttle_factor=0.6,
            symbolic_indicator="⚖️",
            description="Balanced performance and efficiency",
        ),
        "performance": EnergyProfile(
            profile_name="performance",
            cpu_threshold=0.8,
            memory_threshold=0.9,
            operation_delay=0.1,
            max_concurrent=8,
            throttle_factor=1.0,
            symbolic_indicator="⚡",
            description="Maximum performance",
        ),
    }

    # Automatic switching thresholds
    SWITCH_THRESHOLDS = {
        "cpu_high": 0.8,  # Switch to lower profile
        "cpu_low": 0.3,  # Switch to higher profile
        "memory_high": 0.9,
        "memory_low": 0.4,
        "battery_low": 0.2,  # Force power save mode
        "temperature_high": 80.0,  # Celsius
    }

    def __init__(
        self,
        initial_profile: str = "balanced",
        monitoring_interval: float = 5.0,
        auto_switch: bool = True,
        log_file: str = "energy_management.log",
    ):
        self.current_profile = self.ENERGY_PROFILES[initial_profile]
        self.monitoring_interval = monitoring_interval
        self.auto_switch = auto_switch
        self.log_file = Path(log_file)

        # Monitoring data
        self.metrics_history = deque(maxlen=100)
        self.active_operations = 0
        self.operation_queue = []
        self.throttle_active = False

        # Energy tracking
        self.energy_events: list[dict] = []
        self.profile_switches = 0
        self.monitoring_active = False

        logger.info("🌙 Energy Manager initialized")
        logger.info(f"   Profile: {self.current_profile.profile_name} {self.current_profile.symbolic_indicator}")
        logger.info(f"   Auto-switch: {'enabled' if auto_switch else 'disabled'}")

    async def start_monitoring(self):
        """Start energy monitoring and management"""
        self.monitoring_active = True

        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_system_metrics(),
            self._manage_energy_profiles(),
            self._process_operation_queue(),
        )

    async def _monitor_system_metrics(self):
        """Monitor system performance metrics"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = SystemMetrics(
                    timestamp=datetime.now(timezone.utc),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_io=(sum(psutil.disk_io_counters()[:2]) if psutil.disk_io_counters() else 0),
                    network_io=(sum(psutil.net_io_counters()[:2]) if psutil.net_io_counters() else 0),
                )

                # Get battery info if available
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        metrics.battery_level = battery.percent / 100.0
                except BaseException:
                    pass

                # Get temperature if available
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get CPU temperature
                        cpu_temps = temps.get("cpu-thermal", temps.get("coretemp", []))
                        if cpu_temps:
                            metrics.temperature = cpu_temps[0].current
                except BaseException:
                    pass

                # Calculate energy score (0 = efficient, 1 = intensive)
                cpu_score = metrics.cpu_percent / 100.0
                memory_score = metrics.memory_percent / 100.0
                metrics.energy_score = cpu_score * 0.6 + memory_score * 0.4

                # Store metrics
                self.metrics_history.append(metrics)

                # Log high resource usage
                if metrics.energy_score > 0.8:
                    self._log_energy_event(
                        "high_usage",
                        {
                            "cpu": metrics.cpu_percent,
                            "memory": metrics.memory_percent,
                            "energy_score": metrics.energy_score,
                        },
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error monitoring system metrics: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _manage_energy_profiles(self):
        """Automatically manage energy profiles based on system state"""
        while self.monitoring_active:
            try:
                if not self.auto_switch or not self.metrics_history:
                    await asyncio.sleep(self.monitoring_interval * 2)
                    continue

                current_metrics = self.metrics_history[-1]
                should_switch = False
                target_profile = None

                # Check for forced power save conditions
                if (
                    current_metrics.battery_level
                    and current_metrics.battery_level < self.SWITCH_THRESHOLDS["battery_low"]
                ):
                    target_profile = "power_save"
                    should_switch = True
                elif (
                    current_metrics.temperature
                    and current_metrics.temperature > self.SWITCH_THRESHOLDS["temperature_high"]
                ):
                    target_profile = "deep_sleep"
                    should_switch = True

                # Check CPU thresholds
                elif current_metrics.cpu_percent > self.SWITCH_THRESHOLDS["cpu_high"] * 100:
                    # Switch to more efficient profile
                    profiles = list(self.ENERGY_PROFILES.keys())
                    current_idx = profiles.index(self.current_profile.profile_name)
                    if current_idx > 0:
                        target_profile = profiles[current_idx - 1]
                        should_switch = True

                elif current_metrics.cpu_percent < self.SWITCH_THRESHOLDS["cpu_low"] * 100:
                    # Switch to more performance profile
                    profiles = list(self.ENERGY_PROFILES.keys())
                    current_idx = profiles.index(self.current_profile.profile_name)
                    if current_idx < len(profiles) - 1:
                        target_profile = profiles[current_idx + 1]
                        should_switch = True

                # Perform switch if needed
                if should_switch and target_profile:
                    await self._switch_profile(target_profile, current_metrics)

                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"Error managing energy profiles: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _switch_profile(self, profile_name: str, metrics: SystemMetrics):
        """Switch to a different energy profile"""
        if profile_name == self.current_profile.profile_name:
            return

        old_profile = self.current_profile.profile_name
        self.current_profile = self.ENERGY_PROFILES[profile_name]
        self.profile_switches += 1

        # Log the switch
        self._log_energy_event(
            "profile_switch",
            {
                "from_profile": old_profile,
                "to_profile": profile_name,
                "trigger_cpu": metrics.cpu_percent,
                "trigger_memory": metrics.memory_percent,
                "battery_level": metrics.battery_level,
                "temperature": metrics.temperature,
            },
        )

        logger.info(f"🔄 Energy profile switched: {old_profile} → {profile_name}")
        logger.info(
            f"   New limits: CPU {self.current_profile.cpu_threshold  * 100:.1f}%, "
            f"Memory {self.current_profile.memory_threshold  * 100:.1f}%"
        )
        logger.info(f"   Symbol: {self.current_profile.symbolic_indicator}")

    async def _process_operation_queue(self):
        """Process queued operations with energy-aware throttling"""
        while self.monitoring_active:
            try:
                if not self.operation_queue:
                    await asyncio.sleep(0.1)
                    continue

                # Check if we can process operations
                if self.active_operations >= self.current_profile.max_concurrent:
                    await asyncio.sleep(self.current_profile.operation_delay)
                    continue

                # Check system load
                if self.metrics_history and self._should_throttle():
                    if not self.throttle_active:
                        self.throttle_active = True
                        logger.info("🌙 Throttling activated - high system load")

                    await asyncio.sleep(self.current_profile.operation_delay * 2)
                    continue
                else:
                    if self.throttle_active:
                        self.throttle_active = False
                        logger.info("⚡ Throttling deactivated - normal load")

                # Process next operation
                if self.operation_queue:
                    operation = self.operation_queue.pop(0)
                    asyncio.create_task(self._execute_operation(operation))

                # Energy-aware delay
                delay = self.current_profile.operation_delay * (1.0 / self.current_profile.throttle_factor)
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Error processing operation queue: {e}")
                await asyncio.sleep(self.current_profile.operation_delay)

    def _should_throttle(self) -> bool:
        """Determine if operations should be throttled"""
        if not self.metrics_history:
            return False

        current_metrics = self.metrics_history[-1]

        # Check against current profile thresholds
        return bool(
            current_metrics.cpu_percent / 100.0 > self.current_profile.cpu_threshold
            or current_metrics.memory_percent / 100.0 > self.current_profile.memory_threshold
        )

    async def _execute_operation(self, operation: dict):
        """Execute an operation with energy tracking"""
        self.active_operations += 1
        start_time = time.time()

        try:
            # Simulate operation execution
            operation_type = operation.get("type", "unknown")
            duration = operation.get("duration", 1.0)

            # Apply throttle factor
            adjusted_duration = duration / self.current_profile.throttle_factor
            await asyncio.sleep(adjusted_duration)

            # Log completion
            execution_time = time.time() - start_time
            self._log_energy_event(
                "operation_complete",
                {
                    "type": operation_type,
                    "duration": execution_time,
                    "profile": self.current_profile.profile_name,
                    "throttled": self.throttle_active,
                },
            )

        except Exception as e:
            logger.error(f"Error executing operation: {e}")
        finally:
            self.active_operations -= 1

    def queue_operation(
        self,
        operation_type: str,
        duration: float = 1.0,
        priority: str = "normal",
        metadata: Optional[dict] = None,
    ) -> str:
        """Queue an operation for energy-aware execution"""
        operation_id = f"op_{datetime.now(timezone.utc).timestamp()}_{operation_type}"

        operation = {
            "id": operation_id,
            "type": operation_type,
            "duration": duration,
            "priority": priority,
            "metadata": metadata or {},
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "profile_at_queue": self.current_profile.profile_name,
        }

        # Insert based on priority
        if priority == "high":
            self.operation_queue.insert(0, operation)
        else:
            self.operation_queue.append(operation)

        logger.info(f"📋 Queued operation: {operation_type} (priority: {priority})")
        return operation_id

    def set_profile(self, profile_name: str) -> bool:
        """Manually set energy profile"""
        if profile_name not in self.ENERGY_PROFILES:
            logger.error(f"Unknown profile: {profile_name}")
            return False

        old_profile = self.current_profile.profile_name
        self.current_profile = self.ENERGY_PROFILES[profile_name]

        self._log_energy_event("manual_switch", {"from_profile": old_profile, "to_profile": profile_name})

        logger.info(f"🔧 Manual profile switch: {old_profile} → {profile_name}")
        return True

    def _log_energy_event(self, event_type: str, data: dict):
        """Log energy management events"""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "profile": self.current_profile.profile_name,
            "data": data,
        }

        self.energy_events.append(event)

        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def get_energy_report(self) -> dict[str, Any]:
        """Generate comprehensive energy management report"""
        current_metrics = self.metrics_history[-1] if self.metrics_history else None

        # Calculate average metrics
        if self.metrics_history:
            avg_cpu = sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history)
            avg_memory = sum(m.memory_percent for m in self.metrics_history) / len(self.metrics_history)
            avg_energy = sum(m.energy_score for m in self.metrics_history) / len(self.metrics_history)
        else:
            avg_cpu = avg_memory = avg_energy = 0.0

        # Event distribution
        event_types = {}
        for event in self.energy_events:
            event_type = event["event"]
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "current_profile": {
                "name": self.current_profile.profile_name,
                "symbol": self.current_profile.symbolic_indicator,
                "description": self.current_profile.description,
                "cpu_threshold": self.current_profile.cpu_threshold * 100,
                "memory_threshold": self.current_profile.memory_threshold * 100,
            },
            "current_metrics": {
                "cpu_percent": current_metrics.cpu_percent if current_metrics else 0,
                "memory_percent": (current_metrics.memory_percent if current_metrics else 0),
                "energy_score": current_metrics.energy_score if current_metrics else 0,
                "battery_level": (current_metrics.battery_level if current_metrics else None),
                "temperature": current_metrics.temperature if current_metrics else None,
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "energy_score": avg_energy,
            },
            "operations": {
                "active": self.active_operations,
                "queued": len(self.operation_queue),
                "throttle_active": self.throttle_active,
            },
            "statistics": {
                "profile_switches": self.profile_switches,
                "total_events": len(self.energy_events),
                "event_distribution": event_types,
                "monitoring_time": len(self.metrics_history) * self.monitoring_interval,
            },
        }

    async def stop_monitoring(self):
        """Stop energy monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Energy monitoring stopped")


# Example usage and testing
async def demo_energy_manager():
    """Demonstrate energy management"""
    manager = EnergyManager(initial_profile="balanced", monitoring_interval=2)

    print("🌙 Energy Manager Demo")
    print("=" * 60)
    print(f"Initial profile: {manager.current_profile.profile_name} {manager.current_profile.symbolic_indicator}")

    # Queue some operations
    print("\n📋 Queueing operations...")
    for i in range(5):
        op_type = ["analysis", "processing", "sync", "backup", "cleanup"][i]
        duration = [0.5, 2.0, 1.0, 3.0, 0.8][i]
        priority = "high" if i < 2 else "normal"
        manager.queue_operation(op_type, duration, priority)

    # Start monitoring
    print("\n🔄 Starting energy monitoring...")
    monitoring_task = asyncio.create_task(manager.start_monitoring())

    # Let it run for demo
    await asyncio.sleep(15)

    # Test manual profile switching
    print("\n🔧 Testing manual profile switches...")
    await asyncio.sleep(2)
    manager.set_profile("power_save")
    await asyncio.sleep(3)
    manager.set_profile("performance")
    await asyncio.sleep(3)

    # Generate report
    print("\n📊 Energy Management Report:")
    report = manager.get_energy_report()

    print("\n🎯 Current Profile:")
    profile = report["current_profile"]
    print(f"   {profile['name']} {profile['symbol']} - {profile['description']}")
    print(f"   CPU threshold: {profile['cpu_threshold']:.0f}%")
    print(f"   Memory threshold: {profile['memory_threshold']:.0f}%")

    print("\n📈 Current Metrics:")
    metrics = report["current_metrics"]
    print(f"   CPU: {metrics['cpu_percent']:.1f}%")
    print(f"   Memory: {metrics['memory_percent']:.1f}%")
    print(f"   Energy score: {metrics['energy_score']:.3f}")

    print("\n🔢 Statistics:")
    stats = report["statistics"]
    print(f"   Profile switches: {stats['profile_switches']}")
    print(f"   Total events: {stats['total_events']}")
    print(f"   Monitoring time: {stats['monitoring_time']:.0f}s")

    # Stop monitoring
    await manager.stop_monitoring()
    monitoring_task.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(demo_energy_manager())
