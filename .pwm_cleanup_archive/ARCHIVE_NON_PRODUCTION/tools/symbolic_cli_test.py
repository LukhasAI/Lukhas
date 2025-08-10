#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Symbolic CLI Test Suite

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This tool tests symbolic command functionality like `lukhas describe dream.recursion`.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymbolicResolver:
    """Resolves symbolic paths to actual modules and descriptions."""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.symbol_map = self.load_symbol_map()

    def load_symbol_map(self) -> Dict:
        """Load symbol map from generated JSON."""
        symbol_map_path = self.root_path.parent / "symbol_map.json"

        try:
            with open(symbol_map_path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Symbol map not found at {symbol_map_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading symbol map: {e}")
            return {}

    def resolve_symbolic_path(self, symbolic_path: str) -> Dict[str, Any]:
        """Resolve a symbolic path like 'dream.recursion' to module info."""

        result = {
            "symbolic_path": symbolic_path,
            "resolved": False,
            "matches": [],
            "suggestions": [],
        }

        # Split symbolic path
        parts = symbolic_path.split(".")

        if not self.symbol_map:
            result["error"] = "Symbol map not loaded"
            return result

        # Search for matches in symbol map
        modules = self.symbol_map.get("modules", {})

        for module_path, module_info in modules.items():
            # Check if module path contains symbolic parts
            module_lower = module_path.lower()

            matches_all = True
            for part in parts:
                if part.lower() not in module_lower:
                    matches_all = False
                    break

            if matches_all:
                result["matches"].append(
                    {
                        "module": module_path,
                        "tags": module_info.get("tags", []),
                        "subsystem": module_info.get("subsystem", "unknown"),
                        "level": module_info.get("level", "unknown"),
                    }
                )

        # Find suggestions based on partial matches
        if not result["matches"]:
            for module_path, module_info in modules.items():
                module_lower = module_path.lower()

                # Check if any part matches
                for part in parts:
                    if part.lower() in module_lower:
                        result["suggestions"].append(
                            {
                                "module": module_path,
                                "subsystem": module_info.get("subsystem", "unknown"),
                                "match_reason": f"Contains '{part}'",
                            }
                        )
                        break

        result["resolved"] = len(result["matches"]) > 0
        return result

    def describe_module(self, module_path: str) -> Dict[str, Any]:
        """Get detailed description of a module."""

        # Try to read the actual file for docstring
        file_path = self.root_path / (module_path.replace(".", "/") + ".py")

        description = {
            "module": module_path,
            "file_path": str(file_path),
            "exists": file_path.exists(),
            "docstring": None,
            "imports": [],
            "classes": [],
            "functions": [],
        }

        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract docstring (simple approach)
                lines = content.split("\n")
                in_docstring = False
                docstring_lines = []

                for line in lines:
                    if '"""' in line and not in_docstring:
                        in_docstring = True
                        if line.strip().count('"""') == 2:
                            # Single line docstring
                            docstring_lines.append(line.strip().replace('"""', ""))
                            break
                        else:
                            # Multi-line docstring start
                            docstring_lines.append(line.strip().replace('"""', ""))
                    elif '"""' in line and in_docstring:
                        in_docstring = False
                        docstring_lines.append(line.strip().replace('"""', ""))
                        break
                    elif in_docstring:
                        docstring_lines.append(line.strip())

                description["docstring"] = "\n".join(docstring_lines).strip()

            except Exception as e:
                description["error"] = str(e)

        return description


class SymbolicCLI:
    """Command-line interface for symbolic operations."""

    def __init__(self, root_path: str):
        self.resolver = SymbolicResolver(Path(root_path))

    def describe(self, symbolic_path: str) -> str:
        """Main describe command implementation."""

        resolution = self.resolver.resolve_symbolic_path(symbolic_path)

        output = []
        output.append(f"🔍 Symbolic Path: {symbolic_path}")
        output.append("=" * 50)

        if resolution["resolved"]:
            output.append(f"✅ Resolved to {len(resolution['matches'])} module(s):")
            output.append("")

            for i, match in enumerate(resolution["matches"][:5], 1):  # Limit to 5
                output.append(f"{i}. **{match['module']}**")
                output.append(f"   - Subsystem: {match['subsystem']}")
                output.append(f"   - Level: {match['level']}")
                output.append(
                    f"   - Tags: {', '.join(match['tags'][:3])}"
                )  # Show first 3 tags

                # Get detailed description
                desc = self.resolver.describe_module(match["module"])
                if desc["docstring"]:
                    output.append(f"   - Description: {desc['docstring'][:100]}...")

                output.append("")

        else:
            output.append("❌ No exact matches found")

            if resolution["suggestions"]:
                output.append("")
                output.append("💡 Suggestions:")
                for suggestion in resolution["suggestions"][:5]:
                    output.append(
                        f"   - {suggestion['module']} ({suggestion['match_reason']})"
                    )
            else:
                output.append("   No similar modules found")

        return "\n".join(output)

    def test_symbolic_commands(self) -> Dict[str, Any]:
        """Test various symbolic command patterns."""

        test_cases = [
            "dream.recursion",
            "memory.fold",
            "ethics.governance",
            "quantum.bio",
            "consciousness.awareness",
            "emotion.loop",
            "reasoning.symbolic",
            "narrative.weaver",
        ]

        results = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "results": {},
        }

        for test_case in test_cases:
            try:
                description = self.describe(test_case)
                resolution = self.resolver.resolve_symbolic_path(test_case)

                test_result = {
                    "symbolic_path": test_case,
                    "resolved": resolution["resolved"],
                    "matches_count": len(resolution["matches"]),
                    "description_length": len(description),
                    "status": "PASS" if resolution["resolved"] else "FAIL",
                }

                if resolution["resolved"]:
                    results["passed_tests"] += 1
                else:
                    results["failed_tests"] += 1

                results["results"][test_case] = test_result

            except Exception as e:
                results["results"][test_case] = {
                    "symbolic_path": test_case,
                    "status": "ERROR",
                    "error": str(e),
                }
                results["failed_tests"] += 1

        return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test LUKHAS symbolic CLI functionality"
    )
    parser.add_argument(
        "--root", default="lukhas", help="Root directory of LUKHAS modules"
    )
    parser.add_argument(
        "--describe", help="Describe a symbolic path (e.g., dream.recursion)"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run symbolic CLI test suite"
    )
    parser.add_argument("--output", help="Output test results to file")

    args = parser.parse_args()

    cli = SymbolicCLI(args.root)

    if args.describe:
        result = cli.describe(args.describe)
        print(result)

    elif args.test:
        results = cli.test_symbolic_commands()

        # Print summary
        print("🧪 Symbolic CLI Test Results")
        print("=" * 40)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']} ✅")
        print(f"Failed: {results['failed_tests']} ❌")
        print(
            f"Success Rate: {results['passed_tests']/results['total_tests']*100:.1f}%"
        )
        print("")

        # Print detailed results
        for test_path, result in results["results"].items():
            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_emoji} {test_path}: {result['status']}")
            if result["status"] == "PASS":
                print(f"   Matches: {result['matches_count']}")

        # Save results if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
