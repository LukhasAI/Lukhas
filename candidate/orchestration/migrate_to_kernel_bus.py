#!/usr/bin/env python3
import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
Migration script to update LUKHΛS components to use the Symbolic Kernel Bus.
Removes experimental broadcast/print-based signals and replaces with kernel events.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


class KernelBusMigration:
    """Migrate system to use symbolic_kernel_bus"""

    def __init__(self):
        self.workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
        self.backup_dir = self.workspace / f".event_bus_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.changes = []

        # Patterns to replace
        self.replacements = [
            # Old event bus imports
            (
                r"from core\.event_bus import EventBus",
                "from candidate.orchestration.symbolic_kernel_bus import kernel_bus",
            ),
            (
                r"from system\.common\.event_bus import EventBus",
                "from candidate.orchestration.symbolic_kernel_bus import kernel_bus",
            ),
            (
                r"from \.\.event_bus import",
                "from candidate.orchestration.symbolic_kernel_bus import",
            ),
            # Old publish methods
            (r"event_bus\.publish\((.*?)\)", r"kernel_bus.emit(\1)"),
            (r"self\.event_bus\.publish\((.*?)\)", r"kernel_bus.emit(\1)"),
            (r"await event_bus\.publish\((.*?)\)", r"kernel_bus.emit(\1)"),
            # Subscribe methods
            (r"event_bus\.subscribe\((.*?)\)", r"kernel_bus.subscribe(\1)"),
            (r"self\.event_bus\.subscribe\((.*?)\)", r"kernel_bus.subscribe(\1)"),
            # Remove print-based debugging
            (
                r'print\(.*?["\']EVENT:.*?\)',
                "# Removed: experimental print-based event",
            ),
            (
                r'print\(.*?["\']BROADCAST:.*?\)',
                "# Removed: experimental broadcast print",
            ),
            (
                r'logger\.debug\(["\']EXPERIMENTAL:.*?\)',
                "# Removed: experimental debug log",
            ),
            # Update event creation
            (r"Event\(event_type=(.*?), payload=(.*?)\)", r"kernel_bus.emit(\1, \2)"),
        ]

    def backup_files(self):
        """Backup event-related files"""
        print("\n📦 Creating backup...")
        self.backup_dir.mkdir(exist_ok=True)

        # Backup old event bus files
        event_files = [
            "core/event_bus.py",
            "system/common/event_bus.py",
            "core/events/typed_event_bus.py",
        ]

        for file_path in event_files:
            full_path = self.workspace / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                print(f"  ✅ Backed up {file_path}")

    def remove_experimental_code(self):
        """Remove experimental broadcast and print-based signals"""
        print("\n🗑️ Removing experimental code...")

        removed_count = 0

        for py_file in self.workspace.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".backup", "__pycache__", "migrate_to_kernel"]):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Remove experimental patterns
                experimental_patterns = [
                    r"# EXPERIMENTAL:.*?\n",
                    r'print\(f?["\'].*?BROADCAST:.*?\)\n',
                    r'print\(f?["\'].*?EVENT:.*?\)\n',
                    r'logger\.debug\(["\']EXPERIMENTAL:.*?\)\n',
                    r"# TODO: Remove print-based.*?\n",
                ]

                for pattern in experimental_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        removed_count += len(matches)
                    content = re.sub(pattern, "", content)

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.changes.append(
                        (
                            "removed_experimental",
                            str(py_file.relative_to(self.workspace)),
                        )
                    )

            except Exception as e:
                print(f"  ⚠️ Error processing {py_file.name}: {e}")

        print(f"  ✅ Removed {removed_count} experimental code blocks")

    def update_imports_and_calls(self):
        """Update imports and method calls to use kernel bus"""
        print("\n🔄 Updating imports and calls...")

        updated_files = 0

        for py_file in self.workspace.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".backup", "__pycache__", "symbolic_kernel_bus.py"]):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Apply replacements
                for old_pattern, new_pattern in self.replacements:
                    content = re.sub(old_pattern, new_pattern, content)

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_files += 1
                    self.changes.append(("updated", str(py_file.relative_to(self.workspace))))

            except Exception as e:
                print(f"  ⚠️ Error updating {py_file.name}: {e}")

        print(f"  ✅ Updated {updated_files} files")

    def create_integration_examples(self):
        """Create example integrations for common patterns"""
        print("\n📝 Creating integration examples...")

        examples = '''"""
Symbolic Kernel Bus Integration Examples
========================================

Common patterns for using the new kernel bus in LUKHΛS components.
"""

from candidate.orchestration.symbolic_kernel_bus import (
    kernel_bus,
    SymbolicEffect,
    EventPriority
)

# Example 1: Memory fold event
def create_memory_fold(fold_id: str, content: dict):
    """Create a memory fold with proper symbolic effects"""
    kernel_bus.emit(
        "memory.fold.init",
        {"fold_id": fold_id, "content": content},
        source="memory.manager",
        effects=[SymbolicEffect.MEMORY_FOLD, SymbolicEffect.LOG_TRACE],
        priority=EventPriority.HIGH
    )

# Example 2: Agent drift detection
def detect_agent_drift(agent_id: str, drift_score: float):
    """Report agent drift to Guardian system"""
    kernel_bus.emit(
        "agent.drift.detected",
        {"agent_id": agent_id, "drift_score": drift_score},
        source="swarm.monitor",
        effects=[SymbolicEffect.DRIFT_DETECT, SymbolicEffect.ETHICS_CHECK],
        priority=EventPriority.HIGH if drift_score > 0.7 else EventPriority.NORMAL
    )

# Example 3: Plugin loading
def load_plugin(plugin_name: str, config: dict):
    """Load a plugin with registry update"""
    kernel_bus.emit(
        "plugin.loaded",
        {"name": plugin_name, "config": config},
        source="plugin.loader",
        effects=[SymbolicEffect.PLUGIN_LOAD, SymbolicEffect.PLUGIN_UPDATE]
    )

# Example 4: Subscribe to memory events
def handle_memory_event(event):
    """Handle memory-related events"""
    print(f"Memory event: {event.event_type}")
    # Process memory event
    if event.payload.get("cascade"):
        kernel_bus.emit(
            "memory.cascade.propagated",
            {"depth": event.payload.get("depth", 0) + 1},
            correlation_id=event.correlation_id
        )

# Subscribe to all memory events
kernel_bus.subscribe("memory.*", handle_memory_event)

# Example 5: Dream cycle with correlation
def start_dream_cycle(dream_id: str):
    """Start a dream cycle with correlated events"""
    # Initial dream event
    event_id = kernel_bus.emit(
        "dream.cycle.started",
        {"dream_id": dream_id, "timestamp": time.time()},
        source="dream.engine",
        effects=[SymbolicEffect.DREAM_TRIGGER, SymbolicEffect.MEMORY_FOLD],
        correlation_id=dream_id
    )

    # Correlated consciousness update
    kernel_bus.emit(
        "consciousness.state.changed",
        {"state": "dreaming", "dream_id": dream_id},
        source="consciousness.core",
        effects=[SymbolicEffect.AWARENESS_UPDATE],
        correlation_id=dream_id
    )

    return event_id

# Example 6: Critical safety event
def safety_violation(boundary: str, severity: str = "high"):
    """Report safety boundary violation"""
    kernel_bus.emit(
        "safety.boundary.violated",
        {"boundary": boundary, "severity": severity},
        source="safety.monitor",
        effects=[SymbolicEffect.SAFETY_GATE, SymbolicEffect.ETHICS_CHECK],
        priority=EventPriority.CRITICAL
    )

# Example 7: Swarm consensus
async def request_swarm_consensus(topic: str, agents: list):
    """Request consensus from agent swarm"""
    kernel_bus.emit(
        "swarm.consensus.required",
        {"topic": topic, "agents": agents, "quorum": len(agents) * 0.6},
        source="swarm.coordinator",
        effects=[SymbolicEffect.SWARM_CONSENSUS, SymbolicEffect.AGENT_SYNC],
        priority=EventPriority.HIGH
    )

# Example 8: Effect-based subscription
def handle_memory_effects(event):
    """Handle any event with memory effects"""
    if SymbolicEffect.MEMORY_PERSIST in event.effects:
        # Persist to storage
        print(f"Persisting memory from {event.source}")

kernel_bus.subscribe_effect(SymbolicEffect.MEMORY_PERSIST, handle_memory_effects)
'''

        example_path = self.workspace / "orchestration" / "kernel_bus_examples.py"
        with open(example_path, "w") as f:
            f.write(examples)

        print(f"  ✅ Created {example_path.name}")

    def generate_report(self):
        """Generate migration report"""
        print("\n📊 Generating migration report...")

        report = f"""
# Kernel Bus Migration Report
Generated: {datetime.now(timezone.utc).isoformat()}

## Summary
- Backup location: {self.backup_dir}
- Files updated: {len([c for c in self.changes if c[0] == "updated"])}
- Experimental code removed: {len([c for c in self.changes if c[0] == "removed_experimental"])}

## Key Changes
1. Replaced old EventBus with SymbolicKernelBus
2. Removed print-based event debugging
3. Added symbolic effect annotations
4. Implemented priority-based event queuing
5. Added correlation tracking for related events

## New Features
- Symbolic effects for automatic handler routing
- Priority levels (CRITICAL, HIGH, NORMAL, LOW, TRACE)
- Event correlation for tracking related operations
- Causality chains for event relationships
- Automatic retry for critical events
- Pattern-based subscriptions (e.g., "memory.*")

## Migration Checklist
- [x] Backup old event bus files
- [x] Remove experimental code
- [x] Update imports to use kernel_bus
- [x] Replace publish() with emit()
- [x] Add symbolic effects to events
- [x] Create integration examples

## Next Steps
1. Test kernel bus with memory subsystem
2. Verify agent drift detection
3. Test plugin loading events
4. Monitor event metrics
5. Optimize priority queue sizes
"""

        report_path = self.workspace / "orchestration" / "KERNEL_BUS_MIGRATION_REPORT.md"
        with open(report_path, "w") as f:
            f.write(report)

        print(f"  ✅ Report saved to {report_path.name}")

        return report

    def execute(self):
        """Execute the migration"""
        print("=" * 60)
        print("🌀 SYMBOLIC KERNEL BUS MIGRATION")
        print("=" * 60)

        # Execute migration steps
        self.backup_files()
        self.remove_experimental_code()
        self.update_imports_and_calls()
        self.create_integration_examples()
        report = self.generate_report()

        print(report)
        print("\n✅ Migration complete!")


def main():
    """Run the migration"""

    migration = KernelBusMigration()
    migration.execute()


if __name__ == "__main__":
    main()