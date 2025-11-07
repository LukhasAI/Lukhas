#!/usr/bin/env python3
"""
T4-Compliant Batch Locker

Locks batch files to prevent duplicate task assignment:
- Validates batch integrity
- Locks TaskIDs to prevent conflicts
- Creates allocation registry
- Enforces T4 constraints
"""

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set


class BatchLocker:
    def __init__(self):
        self.locked_tasks: set[str] = set()
        self.batch_registry: dict[str, dict[str, Any]] = {}
        self.conflicts: list[dict[str, Any]] = []

    def lock_batches(self, batch_dir: str) -> dict[str, Any]:
        """Lock all batch files and create allocation registry"""
        batch_path = Path(batch_dir)
        if not batch_path.exists():
            raise FileNotFoundError(f"Batch directory not found: {batch_dir}")

        batch_files = list(batch_path.glob("BATCH-*.json"))
        if not batch_files:
            print("No batch files found to lock")
            return {"status": "no_batches", "locked": 0}

        print(f"Locking {len(batch_files)} batch files...")

        seen_batches = set()
        for batch_file in batch_files:
            self._process_batch_file(batch_file)
            batch_id = self.batch_registry.get(Path(batch_file).stem, {}).get("batch_id")
            if batch_id:
                if batch_id in seen_batches:
                    self.conflicts.append(
                        {
                            "task_id": "BATCH_DUPLICATE",
                            "reason": f"Duplicate batch identifier detected: {batch_id}",
                            "current_batch": batch_id,
                            "file": str(batch_file),
                        }
                    )
                seen_batches.add(batch_id)

        # Create registry
        registry = self._create_registry(batch_dir)

        # Write lock file
        lock_file = batch_path / "batches.lock"
        with open(lock_file, "w") as f:
            json.dump(registry, f, indent=2)

        # Report results
        total_locked = len(self.locked_tasks)
        total_conflicts = len(self.conflicts)

        print("Locking complete:")
        print(f"  Locked tasks: {total_locked}")
        print(f"  Conflicts detected: {total_conflicts}")

        if self.conflicts:
            print("  Conflicts:")
            for conflict in self.conflicts:
                print(f"    {conflict['task_id']}: {conflict['reason']}")

        return {"status": "locked", "locked_tasks": total_locked, "conflicts": total_conflicts, "registry": registry}

    def _process_batch_file(self, batch_file: Path):
        """Process and validate a single batch file"""
        try:
            with open(batch_file) as f:
                batch_data = json.load(f)

            batch_id = batch_data["batch_id"]
            agent = batch_data["agent"]
            tasks = batch_data["tasks"]

            print(f"Processing {batch_id} ({len(tasks)} tasks)")

            # Validate batch structure
            validation_result = self._validate_batch(batch_data)
            if not validation_result["valid"]:
                print(f"  WARNING: {validation_result['errors']}")

            # Lock tasks
            locked_count = 0
            for task in tasks:
                task_id = task["task_id"]
                if task_id in self.locked_tasks:
                    # Conflict detected
                    self.conflicts.append(
                        {
                            "task_id": task_id,
                            "reason": "Already assigned to another batch",
                            "current_batch": batch_id,
                            "file": str(batch_file),
                        }
                    )
                else:
                    self.locked_tasks.add(task_id)
                    locked_count += 1

            # Register batch
            self.batch_registry[batch_id] = {
                "agent": agent,
                "file": batch_file.name,
                "tasks": len(tasks),
                "locked_tasks": locked_count,
                "conflicts": len(tasks) - locked_count,
                "created_at": batch_data.get("created_at"),
                "expires_at": batch_data.get("expires_at"),
                "branch_name": batch_data.get("branch_name"),
                "status": "locked",
                "checksum": self._calculate_checksum(batch_data),
            }

            print(f"  Locked: {locked_count}/{len(tasks)} tasks")

        except Exception as e:
            print(f"Error processing {batch_file}: {e}")
            self.conflicts.append(
                {
                    "task_id": "FILE_ERROR",
                    "reason": f"Could not process batch file: {e}",
                    "current_batch": str(batch_file),
                    "file": str(batch_file),
                }
            )

    def _validate_batch(self, batch_data: dict[str, Any]) -> dict[str, Any]:
        """Validate batch structure and constraints"""
        errors = []

        # Required fields
        required_fields = ["batch_id", "agent", "tasks", "created_at", "branch_name"]
        for field in required_fields:
            if field not in batch_data:
                errors.append(f"Missing required field: {field}")

        # Task validation
        tasks = batch_data.get("tasks", [])
        if not tasks:
            errors.append("No tasks in batch")

        # Batch size validation
        agent = batch_data.get("agent", "")
        max_batch_size = self._get_max_batch_size(agent)
        if len(tasks) > max_batch_size:
            errors.append(f"Batch size {len(tasks)} exceeds limit {max_batch_size} for agent {agent}")

        # Task structure validation
        for i, task in enumerate(tasks):
            task_errors = self._validate_task(task, i)
            errors.extend(task_errors)

        # Branch name format
        branch_name = batch_data.get("branch_name", "")
        if not self._validate_branch_name(branch_name):
            errors.append(f"Invalid branch name format: {branch_name}")

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_task(self, task: dict[str, Any], index: int) -> list[str]:
        """Validate individual task structure"""
        errors = []

        # Required task fields
        required_fields = ["task_id", "priority", "title", "file", "status"]
        for field in required_fields:
            if field not in task:
                errors.append(f"Task {index}: Missing field {field}")

        # TaskID format validation
        task_id = task.get("task_id", "")
        if not self._validate_task_id(task_id):
            errors.append(f"Task {index}: Invalid TaskID format: {task_id}")

        # Status validation
        valid_statuses = ["open", "completed", "blocked", "wip"]
        status = task.get("status", "")
        if status not in valid_statuses:
            errors.append(f"Task {index}: Invalid status: {status}")

        return errors

    def _validate_task_id(self, task_id: str) -> bool:
        """Validate TaskID format: TODO-{PRIORITY}-{MODULE}-{HASH8}"""
        if not task_id.startswith("TODO-"):
            return False

        parts = task_id.split("-")
        if len(parts) != 4:
            return False

        priority = parts[1]
        valid_priorities = ["CRIT", "HIGH", "MED", "LOW"]
        if priority not in valid_priorities:
            return False

        module = parts[2]
        if not re.fullmatch(r"[A-Z0-9-]+", module):
            return False

        hash_part = parts[3]
        return not (len(hash_part) != 8 or not re.fullmatch(r"[0-9a-fA-F]{8}", hash_part))

    def _validate_branch_name(self, branch_name: str) -> bool:
        """Validate branch name format"""
        if not branch_name:
            return False

        # Expected format: feat/jules03/module-batch01 or fix/codex07/area-batch01
        parts = branch_name.split("/")
        if len(parts) != 3:
            return False

        branch_type = parts[0]
        if branch_type not in ["feat", "fix", "refactor"]:
            return False

        agent_part = parts[1]
        return agent_part.startswith("jules") or agent_part.startswith("codex")

    def _get_max_batch_size(self, agent: str) -> int:
        """Get maximum batch size for agent type"""
        if agent.startswith("jules"):
            if agent in ["jules04", "jules05", "jules06", "jules07", "jules08"]:
                return 25  # Lower for complex/experimental work
            return 30
        elif agent.startswith("codex"):
            if agent in ["codex01", "codex02", "codex03", "codex04", "codex05", "codex06"]:
                return 40  # Higher for mechanical work
            return 30
        return 25  # Default

    def _calculate_checksum(self, batch_data: dict[str, Any]) -> str:
        """Calculate checksum for batch integrity verification"""
        # Use task IDs and batch ID for checksum
        task_ids = [task["task_id"] for task in batch_data.get("tasks", [])]
        task_ids.sort()  # Ensure consistent ordering

        checksum_input = f"{batch_data.get('batch_id', '')}:{':'.join(task_ids)}"
        return hashlib.md5(checksum_input.encode()).hexdigest()[:16]

    def _create_registry(self, batch_dir: str) -> dict[str, Any]:
        """Create allocation registry"""
        registry = {
            "created_at": datetime.now().isoformat() + "Z",
            "batch_dir": batch_dir,
            "total_batches": len(self.batch_registry),
            "total_locked_tasks": len(self.locked_tasks),
            "total_conflicts": len(self.conflicts),
            "batches": self.batch_registry,
            "conflicts": self.conflicts,
            "locked_task_ids": sorted(self.locked_tasks),
            "integrity": {
                "checksum": self._calculate_registry_checksum(),
                "verified_at": datetime.now().isoformat() + "Z",
            },
        }

        return registry

    def _calculate_registry_checksum(self) -> str:
        """Calculate registry integrity checksum"""
        # Sort for consistent checksum
        sorted_tasks = sorted(self.locked_tasks)
        sorted_batches = sorted(self.batch_registry.keys())

        checksum_input = f"tasks:{':'.join(sorted_tasks)}:batches:{':'.join(sorted_batches)}"
        return hashlib.md5(checksum_input.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Lock batch files to prevent conflicts")
    parser.add_argument("--dir", required=True, help="Directory containing batch files")
    parser.add_argument("--force", action="store_true", help="Force locking even with conflicts")

    args = parser.parse_args()

    locker = BatchLocker()
    result = locker.lock_batches(args.dir)

    if result["status"] == "locked":
        if result["conflicts"] > 0 and not args.force:
            print("\nERROR: Conflicts detected. Use --force to lock anyway.")
            exit(1)
        else:
            print(f"\nSUCCESS: Locked {result['locked_tasks']} tasks in {args.dir}")
            print("Batch allocation ready for execution.")
    else:
        print("No batches to lock.")


if __name__ == "__main__":
    main()
