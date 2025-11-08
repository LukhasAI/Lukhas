#!/usr/bin/env python3
"""
Test sharding tool for LUKHAS CI performance optimization.
Distributes tests across parallel workers for faster execution.
"""

import argparse
import json
import pathlib
import sys
from typing import Any


class TestSharding:
    def __init__(self):
        self.root_path = pathlib.Path(".")

    def discover_test_files(self, pattern: str = "**/test_*.py") -> list[pathlib.Path]:
        """Discover all test files matching the pattern."""
        test_files = []

        # Find test files in module directories
        for test_file in self.root_path.glob(pattern):
            if test_file.is_file() and not str(test_file).startswith('.'):
                test_files.append(test_file)

        # Also look for tests in tests/ directories
        for test_file in self.root_path.glob("*/tests/test_*.py"):
            if test_file.is_file():
                test_files.append(test_file)

        return sorted(test_files)

    def estimate_test_duration(self, test_file: pathlib.Path) -> float:
        """Estimate test duration based on file size and complexity."""
        try:
            file_size = test_file.stat().st_size

            # Read file to check for complexity indicators
            with open(test_file) as f:
                content = f.read()

            # Base duration from file size (rough heuristic)
            base_duration = file_size / 1000  # 1 second per KB

            # Adjust based on content patterns
            if 'asyncio' in content or 'async def' in content:
                base_duration *= 1.5  # Async tests often take longer

            if 'integration' in str(test_file).lower():
                base_duration *= 2.0  # Integration tests are slower

            if 'consciousness' in content.lower():
                base_duration *= 1.3  # Consciousness tests can be complex

            # Count test functions
            test_func_count = content.count('def test_')
            if test_func_count > 10:
                base_duration *= 1.2  # Many tests = longer file

            return max(base_duration, 1.0)  # Minimum 1 second

        except Exception:
            return 5.0  # Default fallback

    def create_balanced_shards(self, test_files: list[pathlib.Path],
                              num_shards: int) -> list[list[pathlib.Path]]:
        """Create balanced test shards using a greedy algorithm."""
        if not test_files:
            return [[] for _ in range(num_shards)]

        # Estimate durations for all test files
        test_durations = [(f, self.estimate_test_duration(f)) for f in test_files]

        # Sort by duration (largest first) for better balancing
        test_durations.sort(key=lambda x: x[1], reverse=True)

        # Initialize shards with their total durations
        shards = [[] for _ in range(num_shards)]
        shard_durations = [0.0] * num_shards

        # Greedy assignment: add each test to the shard with minimum duration
        for test_file, duration in test_durations:
            min_shard_idx = shard_durations.index(min(shard_durations))
            shards[min_shard_idx].append(test_file)
            shard_durations[min_shard_idx] += duration

        return shards

    def create_module_based_shards(self, test_files: list[pathlib.Path],
                                  num_shards: int) -> list[list[pathlib.Path]]:
        """Create shards based on module groupings."""
        # Group tests by module
        module_groups: dict[str, list[pathlib.Path]] = {}

        for test_file in test_files:
            # Extract module name from path
            parts = test_file.parts
            if len(parts) >= 2:
                module_name = parts[0]  # First directory is module
            else:
                module_name = "root"

            if module_name not in module_groups:
                module_groups[module_name] = []
            module_groups[module_name].append(test_file)

        # Calculate total duration per module
        module_durations = []
        for module, files in module_groups.items():
            total_duration = sum(self.estimate_test_duration(f) for f in files)
            module_durations.append((module, files, total_duration))

        # Sort by duration (largest first)
        module_durations.sort(key=lambda x: x[2], reverse=True)

        # Distribute modules across shards
        shards = [[] for _ in range(num_shards)]
        shard_durations = [0.0] * num_shards

        for module, files, duration in module_durations:
            min_shard_idx = shard_durations.index(min(shard_durations))
            shards[min_shard_idx].extend(files)
            shard_durations[min_shard_idx] += duration

        return shards

    def generate_ci_config(self, shards: list[list[pathlib.Path]],
                          output_format: str = "github") -> str:
        """Generate CI configuration for test sharding."""
        if output_format == "github":
            return self._generate_github_actions_config(shards)
        elif output_format == "pytest":
            return self._generate_pytest_config(shards)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_github_actions_config(self, shards: list[list[pathlib.Path]]) -> str:
        """Generate GitHub Actions matrix strategy."""
        config = {
            "strategy": {
                "matrix": {
                    "shard": list(range(len(shards))),
                    "include": []
                }
            }
        }

        for i, shard in enumerate(shards):
            shard_paths = [str(f) for f in shard]
            config["strategy"]["matrix"]["include"].append({
                "shard": i,
                "test_files": " ".join(shard_paths) if shard_paths else "# No tests"
            })

        return json.dumps(config, indent=2)

    def _generate_pytest_config(self, shards: list[list[pathlib.Path]]) -> str:
        """Generate pytest commands for each shard."""
        commands = []
        for i, shard in enumerate(shards):
            if shard:
                test_paths = " ".join(str(f) for f in shard)
                commands.append(f"# Shard {i}")
                commands.append(f"pytest {test_paths} -v --tb=short")
            else:
                commands.append(f"# Shard {i} - No tests")
                commands.append("echo 'No tests in this shard'")
            commands.append("")

        return "\n".join(commands)

    def analyze_test_distribution(self, test_files: list[pathlib.Path]) -> dict[str, Any]:
        """Analyze current test distribution across modules."""
        module_stats = {}
        total_tests = len(test_files)
        total_estimated_time = 0.0

        for test_file in test_files:
            # Extract module name
            parts = test_file.parts
            module_name = parts[0] if len(parts) >= 2 else "root"

            duration = self.estimate_test_duration(test_file)
            total_estimated_time += duration

            if module_name not in module_stats:
                module_stats[module_name] = {
                    "test_count": 0,
                    "estimated_duration": 0.0,
                    "files": []
                }

            module_stats[module_name]["test_count"] += 1
            module_stats[module_name]["estimated_duration"] += duration
            module_stats[module_name]["files"].append(str(test_file))

        return {
            "total_tests": total_tests,
            "total_estimated_time": total_estimated_time,
            "module_count": len(module_stats),
            "modules": module_stats,
            "average_time_per_test": total_estimated_time / total_tests if total_tests > 0 else 0
        }

def main():
    """Main function for test sharding."""
    parser = argparse.ArgumentParser(description="Test sharding for CI optimization")
    parser.add_argument("--shards", "-s", type=int, default=4,
                       help="Number of shards to create")
    parser.add_argument("--strategy", choices=["balanced", "module"], default="balanced",
                       help="Sharding strategy")
    parser.add_argument("--output", "-o", choices=["github", "pytest"], default="pytest",
                       help="Output format")
    parser.add_argument("--analyze", action="store_true",
                       help="Analyze current test distribution")
    parser.add_argument("--pattern", default="**/test_*.py",
                       help="Test file pattern")

    args = parser.parse_args()

    sharding = TestSharding()
    test_files = sharding.discover_test_files(args.pattern)

    if not test_files:
        print("No test files found")
        return 1

    if args.analyze:
        print("📊 Test Distribution Analysis")
        print("=" * 50)
        analysis = sharding.analyze_test_distribution(test_files)

        print(f"Total test files: {analysis['total_tests']}")
        print(f"Estimated total time: {analysis['total_estimated_time']:.1f}s")
        print(f"Average time per test: {analysis['average_time_per_test']:.1f}s")
        print(f"Modules with tests: {analysis['module_count']}")
        print()

        print("Top 10 modules by test count:")
        modules_by_count = sorted(analysis['modules'].items(),
                                key=lambda x: x[1]['test_count'], reverse=True)
        for module, stats in modules_by_count[:10]:
            print(f"  {module}: {stats['test_count']} tests ({stats['estimated_duration']:.1f}s)")

        return 0

    # Create shards
    if args.strategy == "balanced":
        shards = sharding.create_balanced_shards(test_files, args.shards)
    else:
        shards = sharding.create_module_based_shards(test_files, args.shards)

    # Print shard distribution
    print(f"🧪 Created {len(shards)} test shards using {args.strategy} strategy")
    total_duration = 0.0
    for i, shard in enumerate(shards):
        shard_duration = sum(sharding.estimate_test_duration(f) for f in shard)
        total_duration += shard_duration
        print(f"  Shard {i}: {len(shard)} tests (~{shard_duration:.1f}s)")

    print(f"\nTotal estimated time: {total_duration:.1f}s")
    if len(shards) > 1:
        parallel_time = max(sum(sharding.estimate_test_duration(f) for f in shard) for shard in shards)
        speedup = total_duration / parallel_time
        print(f"Parallel time: ~{parallel_time:.1f}s")
        print(f"Estimated speedup: {speedup:.1f}x")

    # Generate configuration
    print(f"\n🔧 {args.output.upper()} Configuration:")
    print("=" * 50)
    config = sharding.generate_ci_config(shards, args.output)
    print(config)

    return 0

if __name__ == "__main__":
    sys.exit(main())
