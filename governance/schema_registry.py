"""Forwarding module for schema_registry."""
from lukhas_website.lukhas.governance.schema_registry import SchemaRegistry, register_schema, validate_schema

__all__ = ["SchemaRegistry", "register_schema", "validate_schema"]
