#!/usr/bin/env python3
"""
LUKHAS Schema Validation Tool
Validates all LUKHAS schemas and generates comprehensive reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import jsonschema


class LUKHASSchemaValidator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.schemas_dir = self.root_path / "schemas"
        self.docs_dir = self.root_path / "docs"
        self.validation_results = {}

    def load_schema(self, schema_path: Path) -> Dict:
        """Load a JSON schema file"""
        try:
            with open(schema_path) as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load schema: {e}"}

    def load_document(self, doc_path: Path) -> Dict:
        """Load a JSON document to validate"""
        try:
            with open(doc_path) as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load document: {e}"}

    def validate_document(self, document: Dict, schema: Dict) -> tuple[bool, list[str]]:
        """Validate a document against a schema"""
        try:
            jsonschema.validate(document, schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [f"Validation error: {e.message}"]
        except jsonschema.SchemaError as e:
            return False, [f"Schema error: {e.message}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    def find_documents_for_schema(self, schema_name: str) -> list[Path]:
        """Find documents that should be validated against a schema"""
        document_map = {
            "architecture_master.schema.json": [
                "docs/LUKHAS_ARCHITECTURE_MASTER.json"
            ],
            "dependency_matrix.schema.json": [
                "docs/architecture/DEPENDENCY_MATRIX.json"
            ],
            "matriz_graph.schema.json": [
                "MATRIZ/demo_export.json"
            ]
        }

        docs = []
        for doc_path in document_map.get(schema_name, []):
            full_path = self.root_path / doc_path
            if full_path.exists():
                docs.append(full_path)
        return docs

    def validate_all_schemas(self) -> Dict:
        """Validate all schemas and their associated documents"""
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_schemas": 0,
            "total_documents": 0,
            "validation_summary": {
                "schemas_valid": 0,
                "documents_valid": 0,
                "total_errors": 0
            },
            "schema_results": {},
            "recommendations": []
        }

        if not self.schemas_dir.exists():
            results["error"] = "Schemas directory not found"
            return results

        schema_files = list(self.schemas_dir.glob("*.json"))
        results["total_schemas"] = len(schema_files)

        for schema_file in schema_files:
            schema_name = schema_file.name
            schema_result = {
                "schema_path": str(schema_file),
                "schema_valid": False,
                "schema_errors": [],
                "documents": {},
                "document_count": 0,
                "documents_valid_count": 0
            }

            # Load and validate schema itself
            schema = self.load_schema(schema_file)
            if "error" in schema:
                schema_result["schema_errors"].append(schema["error"])
            else:
                try:
                    # Validate that schema is a valid JSON Schema
                    jsonschema.Draft7Validator.check_schema(schema)
                    schema_result["schema_valid"] = True
                    results["validation_summary"]["schemas_valid"] += 1
                except Exception as e:
                    schema_result["schema_errors"].append(f"Invalid JSON Schema: {e}")

                # Find and validate documents
                documents = self.find_documents_for_schema(schema_name)
                schema_result["document_count"] = len(documents)
                results["total_documents"] += len(documents)

                for doc_path in documents:
                    doc_name = doc_path.name
                    document = self.load_document(doc_path)

                    if "error" in document:
                        schema_result["documents"][doc_name] = {
                            "valid": False,
                            "errors": [document["error"]]
                        }
                    else:
                        is_valid, errors = self.validate_document(document, schema)
                        schema_result["documents"][doc_name] = {
                            "valid": is_valid,
                            "errors": errors,
                            "path": str(doc_path)
                        }

                        if is_valid:
                            schema_result["documents_valid_count"] += 1
                            results["validation_summary"]["documents_valid"] += 1
                        else:
                            results["validation_summary"]["total_errors"] += len(errors)

            results["schema_results"][schema_name] = schema_result

        # Generate recommendations
        results["recommendations"] = self.generate_recommendations(results)

        return results

    def generate_recommendations(self, results: Dict) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Check schema quality
        for schema_name, schema_result in results["schema_results"].items():
            if not schema_result["schema_valid"]:
                recommendations.append(f"Fix schema {schema_name}: {', '.join(schema_result['schema_errors'])}")

            if schema_result["document_count"] == 0:
                recommendations.append(f"Schema {schema_name} has no associated documents to validate")

            invalid_docs = [doc for doc, info in schema_result["documents"].items() if not info["valid"]]
            if invalid_docs:
                recommendations.append(f"Fix validation errors in documents: {', '.join(invalid_docs)}")

        # Overall system recommendations
        if results["validation_summary"]["total_errors"] > 0:
            recommendations.append("Address all validation errors before production deployment")

        if results["validation_summary"]["schemas_valid"] < results["total_schemas"]:
            recommendations.append("Update all schemas to be valid JSON Schema Draft 7")

        return recommendations

    def generate_report(self) -> str:
        """Generate a human-readable validation report"""
        results = self.validate_all_schemas()

        report = [
            "# LUKHAS Schema Validation Report",
            f"Generated: {results['validation_timestamp']}",
            "",
            "## Summary",
            f"- Total Schemas: {results['total_schemas']}",
            f"- Total Documents: {results['total_documents']}",
            f"- Valid Schemas: {results['validation_summary']['schemas_valid']}",
            f"- Valid Documents: {results['validation_summary']['documents_valid']}",
            f"- Total Errors: {results['validation_summary']['total_errors']}",
            ""
        ]

        # Add details for each schema
        for schema_name, schema_result in results["schema_results"].items():
            report.append(f"## Schema: {schema_name}")
            report.append(f"- Status: {'✅ Valid' if schema_result['schema_valid'] else '❌ Invalid'}")

            if schema_result["schema_errors"]:
                report.append("- Errors:")
                for error in schema_result["schema_errors"]:
                    report.append(f"  - {error}")

            if schema_result["documents"]:
                report.append("- Documents:")
                for doc_name, doc_info in schema_result["documents"].items():
                    status = "✅" if doc_info["valid"] else "❌"
                    report.append(f"  - {status} {doc_name}")
                    if doc_info["errors"]:
                        for error in doc_info["errors"]:
                            report.append(f"    - {error}")
            report.append("")

        # Add recommendations
        if results["recommendations"]:
            report.append("## Recommendations")
            for rec in results["recommendations"]:
                report.append(f"- {rec}")

        return "\\n".join(report)


if __name__ == "__main__":
    validator = LUKHASSchemaValidator("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    # Generate JSON results
    results = validator.validate_all_schemas()
    print("JSON Results:")
    print(json.dumps(results, indent=2))

    print("\\n" + "="*50 + "\\n")

    # Generate readable report
    report = validator.generate_report()
    print("Validation Report:")
    print(report)
