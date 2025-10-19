#!/usr/bin/env python3
"""
Module: validate_directory_indexes.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
LUKHAS Directory Index Validator
Validates directory indexes and integrates with context sync system
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import jsonschema


class DirectoryIndexValidator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.schema_path = self.root_path / "schemas" / "directory_index.schema.json"

    def load_schema(self) -> Dict:
        """Load the directory index schema"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load schema: {e}"}

    def validate_index(self, index_path: Path) -> Tuple[bool, List[str]]:
        """Validate a single directory index"""
        schema = self.load_schema()
        if "error" in schema:
            return False, [schema["error"]]

        try:
            with open(index_path, 'r') as f:
                index = json.load(f)

            jsonschema.validate(index, schema)
            return True, []

        except jsonschema.ValidationError as e:
            return False, [f"Validation error: {e.message}"]
        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    def find_all_indexes(self) -> List[Path]:
        """Find all directory_index.json files"""
        return list(self.root_path.rglob("directory_index.json"))

    def check_index_consistency(self, index_path: Path) -> Dict:
        """Check consistency between directory index and actual directory contents"""
        try:
            with open(index_path, 'r') as f:
                index = json.load(f)

            directory = index_path.parent
            issues = []

            # Check Python files
            listed_files = {f["filename"] for f in index["component_inventory"]["python_files"]}
            actual_files = {f.name for f in directory.glob("*.py") if f.name != "__init__.py"}

            missing_files = actual_files - listed_files
            extra_files = listed_files - actual_files

            if missing_files:
                issues.append(f"Missing Python files in index: {missing_files}")
            if extra_files:
                issues.append(f"Extra Python files in index: {extra_files}")

            # Check subdirectories
            listed_subdirs = {d["name"] for d in index["component_inventory"]["subdirectories"]}
            actual_subdirs = {d.name for d in directory.iterdir() if d.is_dir() and not d.name.startswith('.')}

            missing_subdirs = actual_subdirs - listed_subdirs
            extra_subdirs = listed_subdirs - actual_subdirs

            if missing_subdirs:
                issues.append(f"Missing subdirectories in index: {missing_subdirs}")
            if extra_subdirs:
                issues.append(f"Extra subdirectories in index: {extra_subdirs}")

            # Check documentation files
            listed_docs = {d["filename"] for d in index["component_inventory"]["documentation"]}
            actual_docs = {f.name for f in directory.iterdir()
                          if f.is_file() and f.suffix in ['.md', '.me']}

            missing_docs = actual_docs - listed_docs
            if missing_docs:
                issues.append(f"Missing documentation files in index: {missing_docs}")

            return {
                "consistent": len(issues) == 0,
                "issues": issues,
                "path": str(directory)
            }

        except Exception as e:
            return {
                "consistent": False,
                "issues": [f"Error checking consistency: {e}"],
                "path": str(index_path.parent)
            }

    def check_context_sync_integration(self, index_path: Path) -> Dict:
        """Check integration with context sync system"""
        try:
            with open(index_path, 'r') as f:
                index = json.load(f)

            directory = index_path.parent
            integration_issues = []

            # Check for context files
            has_claude_me = (directory / "claude.me").exists()
            has_lukhas_context = (directory / "lukhas_context.md").exists()

            documented_files = [d["filename"] for d in index["component_inventory"]["documentation"]]

            if has_claude_me and "claude.me" not in documented_files:
                integration_issues.append("claude.me exists but not documented in index")

            if has_lukhas_context and "lukhas_context.md" not in documented_files:
                integration_issues.append("lukhas_context.md exists but not documented in index")

            # Check sync headers
            sync_header_files = [d for d in index["component_inventory"]["documentation"]
                               if d.get("has_sync_header", False)]

            if not sync_header_files and (has_claude_me or has_lukhas_context):
                integration_issues.append("Context files present but no sync headers detected")

            # Check lane consistency
            lane = index["directory_metadata"]["lane"]
            path = index["directory_metadata"]["path"]

            expected_lane = "production" if "/lukhas/" in path and "/candidate/" not in path else \
                           "integration" if "/candidate/core/" in path else "development"

            if lane != expected_lane:
                integration_issues.append(f"Lane mismatch: expected {expected_lane}, got {lane}")

            return {
                "integrated": len(integration_issues) == 0,
                "issues": integration_issues,
                "sync_headers": len(sync_header_files),
                "context_files": len([f for f in documented_files if f in ["claude.me", "lukhas_context.md"]])
            }

        except Exception as e:
            return {
                "integrated": False,
                "issues": [f"Error checking integration: {e}"],
                "sync_headers": 0,
                "context_files": 0
            }

    def validate_all_indexes(self) -> Dict:
        """Validate all directory indexes"""
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_indexes": 0,
            "valid_indexes": 0,
            "consistent_indexes": 0,
            "integrated_indexes": 0,
            "validation_errors": {},
            "consistency_issues": {},
            "integration_issues": {},
            "summary": {},
            "recommendations": []
        }

        indexes = self.find_all_indexes()
        results["total_indexes"] = len(indexes)

        validation_stats = {"valid": 0, "invalid": 0}
        consistency_stats = {"consistent": 0, "inconsistent": 0}
        integration_stats = {"integrated": 0, "not_integrated": 0}

        for index_path in indexes:
            # Validate schema
            is_valid, errors = self.validate_index(index_path)
            if is_valid:
                validation_stats["valid"] += 1
                results["valid_indexes"] += 1
            else:
                validation_stats["invalid"] += 1
                results["validation_errors"][str(index_path)] = errors

            # Check consistency
            consistency = self.check_index_consistency(index_path)
            if consistency["consistent"]:
                consistency_stats["consistent"] += 1
                results["consistent_indexes"] += 1
            else:
                consistency_stats["inconsistent"] += 1
                results["consistency_issues"][str(index_path)] = consistency["issues"]

            # Check integration
            integration = self.check_context_sync_integration(index_path)
            if integration["integrated"]:
                integration_stats["integrated"] += 1
                results["integrated_indexes"] += 1
            else:
                integration_stats["not_integrated"] += 1
                results["integration_issues"][str(index_path)] = integration["issues"]

        # Generate summary
        results["summary"] = {
            "validation_rate": results["valid_indexes"] / results["total_indexes"] if results["total_indexes"] > 0 else 0,
            "consistency_rate": results["consistent_indexes"] / results["total_indexes"] if results["total_indexes"] > 0 else 0,
            "integration_rate": results["integrated_indexes"] / results["total_indexes"] if results["total_indexes"] > 0 else 0,
            "validation_stats": validation_stats,
            "consistency_stats": consistency_stats,
            "integration_stats": integration_stats
        }

        # Generate recommendations
        if results["valid_indexes"] < results["total_indexes"]:
            results["recommendations"].append(f"Fix {results['total_indexes'] - results['valid_indexes']} invalid directory indexes")

        if results["consistent_indexes"] < results["total_indexes"]:
            results["recommendations"].append(f"Update {results['total_indexes'] - results['consistent_indexes']} inconsistent directory indexes")

        if results["integrated_indexes"] < results["total_indexes"]:
            results["recommendations"].append(f"Improve context sync integration for {results['total_indexes'] - results['integrated_indexes']} directories")

        if results["summary"]["validation_rate"] == 1.0 and results["summary"]["consistency_rate"] > 0.9:
            results["recommendations"].append("Directory index system is operating well - consider automation")

        return results


def main():
    validator = DirectoryIndexValidator(".")
    results = validator.validate_all_indexes()

    print("LUKHAS Directory Index Validation Results:")
    print("=" * 50)
    print(f"Total indexes: {results['total_indexes']}")
    print(f"Valid indexes: {results['valid_indexes']}")
    print(f"Consistent indexes: {results['consistent_indexes']}")
    print(f"Integrated indexes: {results['integrated_indexes']}")

    print(f"\nValidation rate: {results['summary']['validation_rate']:.1%}")
    print(f"Consistency rate: {results['summary']['consistency_rate']:.1%}")
    print(f"Integration rate: {results['summary']['integration_rate']:.1%}")

    if results["validation_errors"]:
        print(f"\nValidation Errors ({len(results['validation_errors'])}):")
        for path, errors in list(results["validation_errors"].items())[:3]:
            print(f"  {path}:")
            for error in errors:
                print(f"    - {error}")

    if results["consistency_issues"]:
        print(f"\nConsistency Issues ({len(results['consistency_issues'])}):")
        for path, issues in list(results["consistency_issues"].items())[:3]:
            print(f"  {path}:")
            for issue in issues:
                print(f"    - {issue}")

    if results["integration_issues"]:
        print(f"\nIntegration Issues ({len(results['integration_issues'])}):")
        for path, issues in list(results["integration_issues"].items())[:3]:
            print(f"  {path}:")
            for issue in issues:
                print(f"    - {issue}")

    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"  - {rec}")

    # Save full results
    with open("temp_directory_index_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nFull validation report saved to: temp_directory_index_validation_report.json")


if __name__ == "__main__":
    main()
