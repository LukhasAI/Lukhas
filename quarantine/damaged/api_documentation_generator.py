import logging
import streamlit as st
from typing import List
logger = logging.getLogger(__name__)
"""
AI-Powered API Documentation Generator
=====================================

Specialized API documentation generator that automatically creates comprehensive,
interactive API documentation with examples, testing capabilities, and compliance
    information.

Features:
    - Automatic endpoint discovery and analysis
- Interactive API documentation with live testing
    - Request/response examples and schemas
- Authentication and authorization documentation
- Rate limiting and usage guidelines
- Compliance and security information
"""

import ast
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class APIDocumentationType(Enum):
        """Types of API documentation"""

    REST_API = "rest_api"
    GRAPHQL_API = "graphql_api"
    WEBSOCKET_API = "websocket_api"
    GRPC_API = "grpc_api"
    SDK_REFERENCE = "sdk_reference"


class HTTPMethod(Enum):
        """HTTP methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class AuthenticationType(Enum):
        """API authentication types"""

    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


@dataclass
class APIParameter:
        """API parameter definition"""

    name: str
    param_type: str  # query, path, header, body
    data_type: str
    required: bool
    description: str
    example: Any
    constraints: Optional[dict[str, Any]] = None


@dataclass
class APIResponse:
        """API response definition"""

    status_code: int
    description: str
    schema: Optional[dict[str, Any]]
    examples: list[dict[str, Any]]
    headers: Optional[dict[str, str]] = None


@dataclass
class APIEndpoint:
        """API endpoint definition"""

    path: str
    method: HTTPMethod
    summary: str
    description: str
    parameters: list[APIParameter]
    responses: list[APIResponse]
    authentication: AuthenticationType
    tags: list[str]
    deprecated: bool = False
    rate_limits: Optional[dict[str, Any]] = None


@dataclass
class APIDocumentation:
        """Complete API documentation"""

    title: str
    version: str
    description: str
    base_url: str
    endpoints: list[APIEndpoint]
    authentication: dict[str, Any]
    schemas: dict[str, Any]
    examples: dict[str, Any]
    rate_limits: dict[str, Any]
    compliance_info: dict[str, Any]


class APIAnalyzer:
    """
    API code analyzer for documentation generation

    Analyzes API code to extract endpoints, parameters, responses,
    and other documentation elements automatically.
    """

    def __init__(self):
        self.framework_handlers = {
            "fastapi": self._analyze_fastapi,
            "flask": self._analyze_flask,
            "django": self._analyze_django,
            "starlette": self._analyze_starlette,
        }

    async def analyze_api_code(self, file_paths: list[str]) -> list[APIEndpoint]:
        """Analyze API code files to extract endpoint information"""

        endpoints = []

        for file_path in file_paths:
            try:
                # Detect framework
                framework = await self._detect_framework(file_path)

                if framework in self.framework_handlers:
                    file_endpoints = await self.framework_handlers[framework](file_path)
                    endpoints.extend(file_endpoints)
                else:
                    # Generic analysis
                    file_endpoints = await self._analyze_generic_api(file_path)
                    endpoints.extend(file_endpoints)

            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")

        return endpoints

    async def _detect_framework(self, file_path: str) -> Optional[str]:
        """Detect which API framework is being used"""

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check for framework imports
        if "from fastapi import" in content or "import fastapi" in content:
            return "fastapi"
        elif "from flask import" in content or "import flask" in content:
            return "flask"
        elif "from django" in content or "import django" in content:
            return "django"
        elif "from starlette import" in content or "import starlette" in content:
            return "starlette"

        return None

    async def _analyze_fastapi(self, file_path: str) -> list[APIEndpoint]:
        """Analyze FastAPI application"""

        endpoints = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for FastAPI decorators
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            endpoint = await self._parse_fastapi_decorator(node, decorator, content)
                            if endpoint:
                                endpoints.append(endpoint)

        except Exception as e:
            logger.error(f"Failed to parse FastAPI file {file_path}: {e}")

        return endpoints

    async def _parse_fastapi_decorator(
        self, func_node: ast.FunctionDef, decorator: ast.Call, content: str
    ) -> Optional[APIEndpoint]:
        """Parse FastAPI decorator to extract endpoint information"""

        # Extract HTTP method and path
        method = None
        path = None

        if isinstance(decorator.func, ast.Attribute) and hasattr(decorator.func, "attr"):
            method_name = decorator.func.attr.upper()
            if method_name in [m.value for m in HTTPMethod]:
                method = HTTPMethod(method_name)

        # Extract path from decorator arguments
        if decorator.args and isinstance(decorator.args[0], ast.Str):
            path = decorator.args[0].s
        elif decorator.args and isinstance(decorator.args[0], ast.Constant):
            path = decorator.args[0].value

        if not method or not path:
            return None

        # Extract function information
        summary = func_node.name.replace("_", " ").title()
        description = ast.get_docstring(func_node) or f"API endpoint: {method.value} {path}"

        # Extract parameters from function signature
        parameters = await self._extract_fastapi_parameters(func_node)

        # Generate response information
        responses = await self._generate_default_responses(method)

        endpoint = APIEndpoint(
            path=path,
            method=method,
            summary=summary,
            description=description,
            parameters=parameters,
            responses=responses,
            authentication=AuthenticationType.BEARER_TOKEN,  # Default assumption
            tags=[self._extract_tag_from_path(path)],
        )

        return endpoint

    async def _extract_fastapi_parameters(self, func_node: ast.FunctionDef) -> list[APIParameter]:
        """Extract parameters from FastAPI function"""

        parameters = []

        for arg in func_node.args.args:
            if arg.arg == "self":
                continue

            # Determine parameter type and data type
            param_type = "query"  # Default
            data_type = "string"  # Default
            required = True
            description = f"Parameter: {arg.arg}"

            # Check for type annotations
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    data_type = arg.annotation.id.lower()
                elif isinstance(arg.annotation, ast.Subscript):
                    # Handle Optional[Type] or List[Type]
                    if isinstance(arg.annotation.value, ast.Name):
                        if arg.annotation.value.id == "Optional":
                            required = False
                        elif arg.annotation.value.id == "List":
                            data_type = "array"

            # Generate example based on data type
            example = self._generate_parameter_example(data_type)

            parameter = APIParameter(
                name=arg.arg,
                param_type=param_type,
                data_type=data_type,
                required=required,
                description=description,
                example=example,
            )
            parameters.append(parameter)

        return parameters

    async def _analyze_flask(self, file_path: str) -> list[APIEndpoint]:
        """Analyze Flask application"""

        endpoints = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Look for Flask route decorators
        route_pattern = r"@app\.route\([\'\"](.*?)[\'\"](?:,\s*methods\s*=\s*\[(.*?)\])?\)"
        routes = re.findall(route_pattern, content)

        for route_info in routes:
            path = route_info[0]
            methods = route_info[1].replace("'", "").replace('"', "").split(",") if route_info[1] else ["GET"]

            for method_str in methods:
                method_str = method_str.strip().upper()
                if method_str in [m.value for m in HTTPMethod]:
                    method = HTTPMethod(method_str)

                    endpoint = APIEndpoint(
                        path=path,
                        method=method,
                        summary=f"{method.value} {path}",
                        description=f"Flask endpoint: {method.value} {path}",
                        parameters=[],
                        responses=await self._generate_default_responses(method),
                        authentication=AuthenticationType.API_KEY,
                        tags=[self._extract_tag_from_path(path)],
                    )
                    endpoints.append(endpoint)

        return endpoints

    async def _analyze_django(self, file_path: str) -> list[APIEndpoint]:
        """Analyze Django REST framework"""

        # Placeholder for Django analysis
        return []

    async def _analyze_starlette(self, file_path: str) -> list[APIEndpoint]:
        """Analyze Starlette application"""

        # Placeholder for Starlette analysis
        return []

    async def _analyze_generic_api(self, file_path: str) -> list[APIEndpoint]:
        """Generic API analysis when framework is unknown"""

        endpoints = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Look for common API patterns
        # This is a basic implementation - could be enhanced
        http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

        for method in http_methods:
            pattern = rf"def\s+(\w*{method.lower()}\w*)\s*\("
            matches = re.findall(pattern, content, re.IGNORECASE)

            for match in matches:
                endpoint = APIEndpoint(
                    path=f"/{match.replace('_', '/')}",
                    method=HTTPMethod(method),
                    summary=match.replace("_", " ").title(),
                    description=f"Generic API endpoint: {method} /{match}",
                    parameters=[],
                    responses=await self._generate_default_responses(HTTPMethod(method)),
                    authentication=AuthenticationType.BEARER_TOKEN,
                    tags=["generic"],
                )
                endpoints.append(endpoint)

        return endpoints

    async def _generate_default_responses(self, method: HTTPMethod) -> list[APIResponse]:
        """Generate default responses for HTTP method"""

        responses = []

        if method == HTTPMethod.GET:
            responses.extend(
                [
                    APIResponse(
                        200,
                        "Successful response",
                        {},
                        [{"message": "Success"}],
                    ),
                    APIResponse(404, "Resource not found", {}, [{"error": "Not found"}]),
                ]
            )
        elif method == HTTPMethod.POST:
            responses.extend(
                [
                    APIResponse(
                        201,
                        "Resource created",
                        {},
                        [{"id": 1, "message": "Created"}],
                    ),
                    APIResponse(400, "Bad request", {}, [{"error": "Invalid input"}]),
                ]
            )
        elif method == HTTPMethod.PUT:
            responses.extend(
                [
                    APIResponse(200, "Resource updated", {}, [{"message": "Updated"}]),
                    APIResponse(404, "Resource not found", {}, [{"error": "Not found"}]),
                ]
            )
        elif method == HTTPMethod.DELETE:
            responses.extend(
                [
                    APIResponse(204, "Resource deleted", {}, []),
                    APIResponse(404, "Resource not found", {}, [{"error": "Not found"}]),
                ]
            )

        # Common responses for all methods
        responses.extend(
            [
                APIResponse(
                    401,
                    "Unauthorized",
                    {},
                    [{"error": "Authentication required"}],
                ),
                APIResponse(
                    500,
                    "Internal server error",
                    {},
                    [{"error": "Server error"}],
                ),
            ]
        )

        return responses

    def _extract_tag_from_path(self, path: str) -> str:
        """Extract API tag from path"""

        parts = path.strip("/").split("/")
        if parts and parts[0]:
            return parts[0].replace("_", " ").title()
        return "General"

    def _generate_parameter_example(self, data_type: str) -> Any:
        """Generate example value for parameter type"""

        examples = {
            "string": "example_value",
            "int": 123,
            "integer": 123,
            "float": 123.45,
            "bool": True,
            "boolean": True,
            "array": ["item1", "item2"],
            "object": {"key": "value"},
        }

        return examples.get(data_type.lower(), "example_value")


class APIDocumentationGenerator:
    """
    API documentation generator

    Generates comprehensive, interactive API documentation
    in multiple formats with examples and testing capabilities.
    """

    def __init__(self):
        self.analyzer = APIAnalyzer()

    async def generate_api_documentation(
        self, api_files: list[str], output_format: str = "openapi"
    ) -> APIDocumentation:
        """Generate comprehensive API documentation"""

        print(f"📡 Generating API documentation from {len(api_files)} files...")

        # Analyze API files
        endpoints = await self.analyzer.analyze_api_code(api_files)

        # Create API documentation
        documentation = APIDocumentation(
            title="LUKHAS  API",
            version="1.0.0",
            description="Comprehensive API for LUKHAS  AI platform",
            base_url="https://api.lukhas-.com",
            endpoints=endpoints,
            authentication=await self._generate_auth_documentation(),
            schemas=await self._generate_schemas(endpoints),
            examples=await self._generate_examples(endpoints),
            rate_limits=await self._generate_rate_limits(),
            compliance_info=await self._generate_compliance_info(),
        )

        print(f"   ✅ Generated documentation for {len(endpoints)} endpoints")

        # Generate output files
        await self._generate_output_files(documentation, output_format)

        return documentation

    async def _generate_auth_documentation(self) -> dict[str, Any]:
        """Generate authentication documentation"""

        return {
            "bearer_token": {
                "type": "http",
                "scheme": "bearer",
                "description": "JWT token authentication",
            },
            "api_key": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication",
            },
            "oauth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://auth.lukhas-.com/oauth/authorize",
                        "tokenUrl": "https://auth.lukhas-.com/oauth/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access",
                            "admin": "Administrative access",
                        },
                    }
                },
            },
        }

    async def _generate_schemas(self, endpoints: list[APIEndpoint]) -> dict[str, Any]:
        """Generate API schemas"""

        schemas = {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message",
                    },
                    "code": {"type": "integer", "description": "Error code"},
                    "details": {
                        "type": "object",
                        "description": "Additional error details",
                    },
                },
                "required": ["error"],
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Success message",
                    },
                    "data": {"type": "object", "description": "Response data"},
                },
                "required": ["message"],
            },
            "ComplianceReport": {
                "type": "object",
                "properties": {
                    "compliance_status": {
                        "type": "string",
                        "enum": ["compliant", "non_compliant", "pending"],
                    },
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "violations": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["compliance_status", "score"],
            },
        }

        return schemas

    async def _generate_examples(self, endpoints: list[APIEndpoint]) -> dict[str, Any]:
        """Generate API examples"""

        examples = {
            "basic_request": {
                "summary": "Basic API request",
                "value": {
                    "headers": {
                        "Authorization": "Bearer your-token-here",
                        "Content-Type": "application/json",
                    }
                },
            },
            "compliance_check": {
                "summary": "Compliance validation request",
                "value": {
                    "system_id": "ai-system-001",
                    "framework": "eu_ai_act",
                    "detailed_report": True,
                },
            },
            "security_test": {
                "summary": "Security test request",
                "value": {
                    "target_system": "ai-model-001",
                    "test_types": ["prompt_injection", "model_extraction"],
                    "severity_threshold": "medium",
                },
            },
        }

        return examples

    async def _generate_rate_limits(self) -> dict[str, Any]:
        """Generate rate limiting documentation"""

        return {
            "default": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
            },
            "authenticated": {
                "requests_per_minute": 500,
                "requests_per_hour": 5000,
                "requests_per_day": 50000,
            },
            "premium": {
                "requests_per_minute": 1000,
                "requests_per_hour": 10000,
                "requests_per_day": 100000,
            },
        }

    async def _generate_compliance_info(self) -> dict[str, Any]:
        """Generate compliance information"""

        return {
            "gdpr_compliant": True,
            "eu_ai_act_compliant": True,
            "data_retention": "User data retained according to GDPR requirements",
            "data_processing": "All data processing activities logged and auditable",
            "security_standards": ["ISO 27001", "SOC 2 Type II"],
            "certifications": ["EU AI Act Compliance", "GDPR Certification"],
        }

    async def _generate_output_files(self, documentation: APIDocumentation, output_format: str):
        """Generate output files in specified format"""

        output_dir = Path("docs/generated/api")
        output_dir.mkdir(parents=True, exist_ok=True)

        if output_format == "openapi":
            await self._generate_openapi_spec(documentation, output_dir)
        elif output_format == "postman":
            await self._generate_postman_collection(documentation, output_dir)
        elif output_format == "markdown":
            await self._generate_markdown_docs(documentation, output_dir)
        elif output_format == "html":
            await self._generate_html_docs(documentation, output_dir)

    async def _generate_openapi_spec(self, documentation: APIDocumentation, output_dir: Path):
        """Generate OpenAPI 3.0 specification"""

        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": documentation.title,
                "version": documentation.version,
                "description": documentation.description,
            },
            "servers": [
                {
                    "url": documentation.base_url,
                    "description": "Production server",
                }
            ],
            "components": {
                "securitySchemes": documentation.authentication,
                "schemas": documentation.schemas,
            },
            "paths": {},
        }

        # Add endpoints
        for endpoint in documentation.endpoints:
            if endpoint.path not in openapi_spec["paths"]:
                openapi_spec["paths"][endpoint.path] = {}

            operation = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": [
                    {
                        "name": param.name,
                        "in": param.param_type,
                        "required": param.required,
                        "schema": {"type": param.data_type},
                        "description": param.description,
                        "example": param.example,
                    }
                    for param in endpoint.parameters
                ],
                "responses": {
                    str(response.status_code): {
                        "description": response.description,
                        "content": (
                            {
                                "application/json": {
                                    "examples": {
                                        f"example_{i}": {"value": ex} for i, ex in enumerate(response.examples)
                                    }
                                }
                            }
                            if response.examples
                            else {}
                        ),
                    }
                    for response in endpoint.responses
                },
            }

            if endpoint.authentication != AuthenticationType.NONE:
                operation["security"] = [{"bearer_token": []}]

            openapi_spec["paths"][endpoint.path][endpoint.method.value.lower()] = operation

        # Write OpenAPI spec
        spec_file = output_dir / "openapi.json"
        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

        print(f"   📄 Generated OpenAPI spec: {spec_file}")

    async def _generate_postman_collection(self, documentation: APIDocumentation, output_dir: Path):
        """Generate Postman collection"""

        collection = {
            "info": {
                "name": documentation.title,
                "description": documentation.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "variable": [{"key": "base_url", "value": documentation.base_url}],
            "item": [],
        }

        # Group endpoints by tag
        tagged_endpoints = {}
        for endpoint in documentation.endpoints:
            tag = endpoint.tags[0] if endpoint.tags else "General"
            if tag not in tagged_endpoints:
                tagged_endpoints[tag] = []
            tagged_endpoints[tag].append(endpoint)

        # Create collection items
        for tag, endpoints in tagged_endpoints.items():
            folder = {"name": tag, "item": []}

            for endpoint in endpoints:
                request_item = {
                    "name": endpoint.summary,
                    "request": {
                        "method": endpoint.method.value,
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json",
                            }
                        ],
                        "url": {
                            "raw": f"{{{{base_url}{endpoint.path}}}}",
                            "host": ["{{base_url}"],
                            "path": endpoint.path.strip("/").split("/"),
                        },
                    },
                }

                if endpoint.authentication != AuthenticationType.NONE:
                    request_item["request"]["header"].append(
                        {
                            "key": "Authorization",
                            "value": "Bearer {{access_token}",
                        }
                    )

                folder["item"].append(request_item)

            collection["item"].append(folder)

        # Write Postman collection
        collection_file = output_dir / "postman_collection.json"
        with open(collection_file, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

        print(f"   📮 Generated Postman collection: {collection_file}")

    async def _generate_markdown_docs(self, documentation: APIDocumentation, output_dir: Path):
        """Generate Markdown API documentation"""

        content = f"""# {documentation.title}

{documentation.description}

**Version:** {documentation.version}
**Base URL:** {documentation.base_url}

## Authentication

"""

        for auth_type, auth_config in documentation.authentication.items():
            content += f"## {auth_type.replace('_', ' ').title()}\n\n"
            content += f"{auth_config.get('description', 'Authentication method')}\n\n"

        content += "## Rate Limits\n\n"
        for tier, limits in documentation.rate_limits.items():
            content += f"### {tier.title()}\n"
            content += f"- Requests per minute: {limits['requests_per_minute']}\n"
            content += f"- Requests per hour: {limits['requests_per_hour']}\n"
            content += f"- Requests per day: {limits['requests_per_day']}\n\n"

        content += "## Endpoints\n\n"

        # Group endpoints by tag
        tagged_endpoints = {}
        for endpoint in documentation.endpoints:
            tag = endpoint.tags[0] if endpoint.tags else "General"
            if tag not in tagged_endpoints:
                tagged_endpoints[tag] = []
            tagged_endpoints[tag].append(endpoint)

        for tag, endpoints in tagged_endpoints.items():
            content += f"## {tag}\n\n"

            for endpoint in endpoints:
                content += f"### `{endpoint.method.value}` {endpoint.path}\n\n"
                content += f"{endpoint.description}\n\n"

                if endpoint.parameters:
                    content += "**Parameters:**\n\n"
                    content += "| Name | Type | Location | Required | Description |\n"
                    content += "|------|------|----------|----------|--------------|\n"

                    for param in endpoint.parameters:
                        required = "Yes" if param.required else "No"
                        content += f"| {param.name} | {param.data_type} | {param.param_type} | {required} | {param.description} |\n"
                    content += "\n"

                content += "**Responses:**\n\n"
                for response in endpoint.responses:
                    content += f"- **{response.status_code}**: {response.description}\n"
                content += "\n"

        # Write Markdown documentation
        markdown_file = output_dir / "api_documentation.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"   📝 Generated Markdown docs: {markdown_file}")

    async def _generate_html_docs(self, documentation: APIDocumentation, output_dir: Path):
        """Generate HTML API documentation"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{documentation.title}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1, h2, h3 {{ color: #333; }
        .endpoint {{ border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }
        .method {{ display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
        .get {{ background-color: #61affe; }
        .post {{ background-color: #49cc90; }
        .put {{ background-color: #fca130; }
        .delete {{ background-color: #f93e3e; }
        table {{ border-collapse: collapse; width: 100%; }
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }
        th {{ background-color: #f2f2f2; }
        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>{documentation.title}</h1>
    <p>{documentation.description}</p>
    <p><strong>Version:</strong> {documentation.version}</p>
    <p><strong>Base URL:</strong> <code>{documentation.base_url}</code></p>

    <h2>Endpoints</h2>
"""

        for endpoint in documentation.endpoints:
            method_class = endpoint.method.value.lower()
            html_content += f"""
    <div class="endpoint">
        <h3><span class="method {method_class}">{endpoint.method.value}</span> {endpoint.path}</h3>
        <p>{endpoint.description}</p>
"""

            if endpoint.parameters:
                html_content += """
        <h4>Parameters</h4>
        <table>
            <tr><th>Name</th><th>Type</th><th>Location</th><th>Required</th><th>Description</th></tr>
"""
                for param in endpoint.parameters:
                    required = "Yes" if param.required else "No"
                    html_content += f"""
            <tr>
                <td><code>{param.name}</code></td>
                <td>{param.data_type}</td>
                <td>{param.param_type}</td>
                <td>{required}</td>
                <td>{param.description}</td>
            </tr>
"""
                html_content += "        </table>\n"

            html_content += """
        <h4>Responses</h4>
        <ul>
"""
            for response in endpoint.responses:
                html_content += (
                    f"            <li><strong>{response.status_code}:</strong> {response.description}</li>\n"
                )

            html_content += "        </ul>\n    </div>\n"

        html_content += "</body></html>"

        # Write HTML documentation
        html_file = output_dir / "api_documentation.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"   🌐 Generated HTML docs: {html_file}")


# Export main API documentation components
__all__ = [
    "APIAnalyzer",
    "APIDocumentation",
    "APIDocumentationGenerator",
    "APIEndpoint",
    "APIParameter",
    "APIResponse",
]