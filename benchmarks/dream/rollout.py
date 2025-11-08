from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class RolloutStrategy(Enum):
    """Rollout strategy types."""
    IMMEDIATE = "immediate"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    A_B_TEST = "a_b_test"
    GRADUAL = "gradual"

class RolloutStatus(Enum):
    """Rollout status states."""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class SafetyThresholds:
    """Safety thresholds for rollout monitoring."""
    min_accuracy: float = 0.8
    max_latency_p95: float = 0.1
    max_error_rate: float = 0.05
    min_coverage: float = 0.7
    max_drift_increase: float = 0.2

@dataclass
class RolloutConfig:
    """Configuration for a rollout."""
    strategy: RolloutStrategy
    target_config: dict[str, Any]
    safety_thresholds: SafetyThresholds
    canary_percentage: float = 5.0  # For canary/A-B testing
    gradual_steps: list[float] = None  # For gradual rollout [10, 25, 50, 100]
    rollback_threshold_violations: int = 3  # Violations before auto-rollback
    monitoring_duration_minutes: int = 30

@dataclass
class RolloutEvent:
    """Single rollout event/measurement."""
    timestamp: float
    percentage: float
    metrics: dict[str, float]
    threshold_violations: list[str]
    status: RolloutStatus

@dataclass
class RolloutPlan:
    """Complete rollout plan with monitoring."""
    plan_id: str
    config: RolloutConfig
    baseline_metrics: dict[str, float]
    events: list[RolloutEvent]
    current_status: RolloutStatus
    created_at: float
    completed_at: float | None = None

class RolloutManager:
    """Manages safe rollout of dream system configurations."""

    def __init__(self, state_file: str = "benchmarks/dream/rollout_state.json"):
        self.state_file = state_file
        self.plans: dict[str, RolloutPlan] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load rollout state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    state_data = json.load(f)

                for plan_id, plan_data in state_data.items():
                    # Reconstruct objects from JSON
                    config_data = plan_data['config']
                    config = RolloutConfig(
                        strategy=RolloutStrategy(config_data['strategy']),
                        target_config=config_data['target_config'],
                        safety_thresholds=SafetyThresholds(**config_data['safety_thresholds']),
                        canary_percentage=config_data.get('canary_percentage', 5.0),
                        gradual_steps=config_data.get('gradual_steps'),
                        rollback_threshold_violations=config_data.get('rollback_threshold_violations', 3),
                        monitoring_duration_minutes=config_data.get('monitoring_duration_minutes', 30)
                    )

                    events = []
                    for event_data in plan_data['events']:
                        event = RolloutEvent(
                            timestamp=event_data['timestamp'],
                            percentage=event_data['percentage'],
                            metrics=event_data['metrics'],
                            threshold_violations=event_data['threshold_violations'],
                            status=RolloutStatus(event_data['status'])
                        )
                        events.append(event)

                    plan = RolloutPlan(
                        plan_id=plan_id,
                        config=config,
                        baseline_metrics=plan_data['baseline_metrics'],
                        events=events,
                        current_status=RolloutStatus(plan_data['current_status']),
                        created_at=plan_data['created_at'],
                        completed_at=plan_data.get('completed_at')
                    )

                    self.plans[plan_id] = plan

            except Exception as e:
                print(f"Warning: Failed to load rollout state: {e}")

    def _save_state(self) -> None:
        """Save rollout state to disk."""
        try:
            state_data = {}
            for plan_id, plan in self.plans.items():
                # Convert to JSON-serializable format
                config_dict = {
                    'strategy': plan.config.strategy.value,
                    'target_config': plan.config.target_config,
                    'safety_thresholds': asdict(plan.config.safety_thresholds),
                    'canary_percentage': plan.config.canary_percentage,
                    'gradual_steps': plan.config.gradual_steps,
                    'rollback_threshold_violations': plan.config.rollback_threshold_violations,
                    'monitoring_duration_minutes': plan.config.monitoring_duration_minutes
                }

                events_data = []
                for event in plan.events:
                    events_data.append({
                        'timestamp': event.timestamp,
                        'percentage': event.percentage,
                        'metrics': event.metrics,
                        'threshold_violations': event.threshold_violations,
                        'status': event.status.value
                    })

                state_data[plan_id] = {
                    'config': config_dict,
                    'baseline_metrics': plan.baseline_metrics,
                    'events': events_data,
                    'current_status': plan.current_status.value,
                    'created_at': plan.created_at,
                    'completed_at': plan.completed_at
                }

            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save rollout state: {e}")

    def create_rollout_plan(self, target_config: dict[str, Any],
                           strategy: RolloutStrategy = RolloutStrategy.CANARY,
                           safety_thresholds: SafetyThresholds = None) -> str:
        """Create a new rollout plan."""
        if safety_thresholds is None:
            safety_thresholds = SafetyThresholds()

        # Generate plan ID
        config_hash = hashlib.md5(json.dumps(target_config, sort_keys=True).encode()).hexdigest()[:8]
        plan_id = f"rollout_{int(time.time())}_{config_hash}"

        # Set up gradual steps based on strategy
        gradual_steps = None
        if strategy == RolloutStrategy.GRADUAL:
            gradual_steps = [10.0, 25.0, 50.0, 100.0]
        elif strategy == RolloutStrategy.CANARY:
            gradual_steps = [5.0, 100.0]
        elif strategy == RolloutStrategy.A_B_TEST:
            gradual_steps = [50.0]  # 50/50 split

        config = RolloutConfig(
            strategy=strategy,
            target_config=target_config,
            safety_thresholds=safety_thresholds,
            gradual_steps=gradual_steps
        )

        # Get baseline metrics (would typically come from current production)
        baseline_metrics = self._get_baseline_metrics()

        plan = RolloutPlan(
            plan_id=plan_id,
            config=config,
            baseline_metrics=baseline_metrics,
            events=[],
            current_status=RolloutStatus.PLANNED,
            created_at=time.time()
        )

        self.plans[plan_id] = plan
        self._save_state()

        return plan_id

    def _get_baseline_metrics(self) -> dict[str, float]:
        """Get baseline metrics from current system (simulated)."""
        # In real implementation, this would query production metrics
        return {
            'accuracy': 0.85,
            'coverage>=0.5': 0.9,
            'p95_ms': 0.05,
            'error_rate': 0.02,
            'stability': 1.0
        }

    def _simulate_metrics(self, config: dict[str, Any], percentage: float) -> dict[str, float]:
        """Simulate metrics for given config and rollout percentage."""
        # Simulate realistic metrics with some noise
        base_accuracy = 0.82 + random.gauss(0, 0.02)
        base_latency = 0.03 + random.gauss(0, 0.01)
        base_coverage = 0.88 + random.gauss(0, 0.03)

        # Configuration impact (simplified)
        if config.get('strategy') == 'blend':
            base_accuracy += 0.03
            base_latency += 0.01

        if config.get('use_objective') == '1':
            base_accuracy += 0.02
            base_latency += 0.005

        # Rollout percentage impact (higher percentage = more realistic load)
        load_factor = percentage / 100.0
        base_latency *= (1.0 + load_factor * 0.1)

        return {
            'accuracy': max(0.0, min(1.0, base_accuracy)),
            'coverage>=0.5': max(0.0, min(1.0, base_coverage)),
            'p95_ms': max(0.01, base_latency),
            'error_rate': max(0.0, min(1.0, 1.0 - base_accuracy * 0.9)),
            'stability': 1.0
        }

    def check_safety_thresholds(self, metrics: dict[str, float],
                               thresholds: SafetyThresholds) -> list[str]:
        """Check if metrics violate safety thresholds."""
        violations = []

        if metrics.get('accuracy', 0.0) < thresholds.min_accuracy:
            violations.append(f"accuracy {metrics['accuracy']:.3f} < {thresholds.min_accuracy:.3f}")

        if metrics.get('p95_ms', float('inf')) > thresholds.max_latency_p95:
            violations.append(f"latency {metrics['p95_ms']:.3f} > {thresholds.max_latency_p95:.3f}")

        if metrics.get('error_rate', 1.0) > thresholds.max_error_rate:
            violations.append(f"error_rate {metrics['error_rate']:.3f} > {thresholds.max_error_rate:.3f}")

        if metrics.get('coverage>=0.5', 0.0) < thresholds.min_coverage:
            violations.append(f"coverage {metrics['coverage>=0.5']:.3f} < {thresholds.min_coverage:.3f}")

        return violations

    def execute_rollout_step(self, plan_id: str, percentage: float) -> bool:
        """Execute a single rollout step."""
        if plan_id not in self.plans:
            raise ValueError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]

        if plan.current_status not in [RolloutStatus.PLANNED, RolloutStatus.ACTIVE]:
            raise ValueError(f"Cannot execute step for plan in status: {plan.current_status}")

        # Simulate getting metrics for this percentage
        metrics = self._simulate_metrics(plan.config.target_config, percentage)

        # Check safety thresholds
        violations = self.check_safety_thresholds(metrics, plan.config.safety_thresholds)

        # Determine status
        if violations:
            violation_count = sum(1 for event in plan.events if event.threshold_violations)
            if violation_count >= plan.config.rollback_threshold_violations:
                status = RolloutStatus.FAILED
                plan.current_status = RolloutStatus.FAILED
            else:
                status = RolloutStatus.ACTIVE
        else:
            status = RolloutStatus.ACTIVE
            if percentage >= 100.0:
                status = RolloutStatus.COMPLETED
                plan.current_status = RolloutStatus.COMPLETED
                plan.completed_at = time.time()

        # Record event
        event = RolloutEvent(
            timestamp=time.time(),
            percentage=percentage,
            metrics=metrics,
            threshold_violations=violations,
            status=status
        )

        plan.events.append(event)
        self._save_state()

        return len(violations) == 0

    def execute_full_rollout(self, plan_id: str) -> dict[str, Any]:
        """Execute complete rollout according to plan."""
        if plan_id not in self.plans:
            raise ValueError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]

        if plan.current_status != RolloutStatus.PLANNED:
            raise ValueError(f"Plan {plan_id} is not in planned status")

        plan.current_status = RolloutStatus.ACTIVE

        result = {
            'plan_id': plan_id,
            'success': False,
            'final_status': None,
            'steps_completed': 0,
            'violations_encountered': 0,
            'rollback_triggered': False
        }

        try:
            if plan.config.strategy == RolloutStrategy.IMMEDIATE:
                success = self.execute_rollout_step(plan_id, 100.0)
                result['steps_completed'] = 1
                result['success'] = success

            elif plan.config.gradual_steps:
                for i, percentage in enumerate(plan.config.gradual_steps):
                    success = self.execute_rollout_step(plan_id, percentage)
                    result['steps_completed'] = i + 1

                    if not success:
                        result['violations_encountered'] += 1

                    # Check if we should stop
                    if plan.current_status == RolloutStatus.FAILED:
                        result['rollback_triggered'] = True
                        break

                    # Wait between steps (simulated)
                    time.sleep(0.1)

                result['success'] = plan.current_status == RolloutStatus.COMPLETED

        except Exception as e:
            plan.current_status = RolloutStatus.FAILED
            result['error'] = str(e)

        result['final_status'] = plan.current_status.value
        self._save_state()

        return result

    def rollback_plan(self, plan_id: str) -> bool:
        """Rollback a rollout plan."""
        if plan_id not in self.plans:
            raise ValueError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]

        if plan.current_status not in [RolloutStatus.ACTIVE, RolloutStatus.FAILED]:
            return False

        plan.current_status = RolloutStatus.ROLLED_BACK

        # Record rollback event
        event = RolloutEvent(
            timestamp=time.time(),
            percentage=0.0,
            metrics={},
            threshold_violations=["Manual rollback"],
            status=RolloutStatus.ROLLED_BACK
        )

        plan.events.append(event)
        self._save_state()

        return True

    def get_rollout_status(self, plan_id: str) -> dict[str, Any]:
        """Get current status of a rollout plan."""
        if plan_id not in self.plans:
            raise ValueError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]

        latest_event = plan.events[-1] if plan.events else None

        return {
            'plan_id': plan_id,
            'status': plan.current_status.value,
            'strategy': plan.config.strategy.value,
            'created_at': plan.created_at,
            'completed_at': plan.completed_at,
            'total_events': len(plan.events),
            'current_percentage': latest_event.percentage if latest_event else 0.0,
            'latest_metrics': latest_event.metrics if latest_event else {},
            'violations_count': sum(1 for e in plan.events if e.threshold_violations),
            'target_config': plan.config.target_config
        }

    def list_plans(self) -> list[dict[str, Any]]:
        """List all rollout plans."""
        return [self.get_rollout_status(plan_id) for plan_id in self.plans]

def create_and_execute_rollout(config: dict[str, Any], strategy: str = "canary") -> dict[str, Any]:
    """Create and execute a rollout plan."""
    manager = RolloutManager()

    try:
        strategy_enum = RolloutStrategy(strategy.lower())
    except ValueError:
        return {"error": f"Invalid strategy: {strategy}"}

    plan_id = manager.create_rollout_plan(config, strategy_enum)
    result = manager.execute_full_rollout(plan_id)

    return {
        'plan_id': plan_id,
        'execution_result': result,
        'final_status': manager.get_rollout_status(plan_id)
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m benchmarks.dream.rollout create <config.json> [strategy]")
        print("  python -m benchmarks.dream.rollout execute <plan_id>")
        print("  python -m benchmarks.dream.rollout status <plan_id>")
        print("  python -m benchmarks.dream.rollout list")
        print("  python -m benchmarks.dream.rollout rollback <plan_id>")
        sys.exit(1)

    command = sys.argv[1]
    manager = RolloutManager()

    try:
        if command == "create":
            if len(sys.argv) < 3:
                print("Error: config file required")
                sys.exit(1)

            with open(sys.argv[2]) as f:
                config = json.load(f)

            strategy = sys.argv[3] if len(sys.argv) > 3 else "canary"
            plan_id = manager.create_rollout_plan(config, RolloutStrategy(strategy))
            print(f"Created rollout plan: {plan_id}")

        elif command == "execute":
            if len(sys.argv) < 3:
                print("Error: plan_id required")
                sys.exit(1)

            plan_id = sys.argv[2]
            result = manager.execute_full_rollout(plan_id)
            print(json.dumps(result, indent=2))

        elif command == "status":
            if len(sys.argv) < 3:
                print("Error: plan_id required")
                sys.exit(1)

            plan_id = sys.argv[2]
            status = manager.get_rollout_status(plan_id)
            print(json.dumps(status, indent=2))

        elif command == "list":
            plans = manager.list_plans()
            for plan in plans:
                print(f"{plan['plan_id']}: {plan['status']} ({plan['strategy']})")

        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Error: plan_id required")
                sys.exit(1)

            plan_id = sys.argv[2]
            success = manager.rollback_plan(plan_id)
            print(f"Rollback {'successful' if success else 'failed'}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
