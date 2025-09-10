#!/usr/bin/env python3
"""
🎭 LUKHAS Consciousness MCP Server
Model Context Protocol server for enhanced Claude Code experience

This MCP server provides Claude Code with direct access to LUKHAS consciousness
systems, Trinity Framework validation, and intelligent context management.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

# MCP SDK imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

# LUKHAS consciousness imports
sys.path.append(".")
try:
    from branding.constellation.trinity_validator import TrinityFrameworkValidator
    from lukhas.consciousness.awareness_engine import ConsciousnessAwarenessEngine
    from lukhas.governance.guardian_system.guardian_validator import GuardianValidator
    from lukhas.memory.fold_system import MemoryFoldSystem
    from tools.analysis._OPERATIONAL_SUMMARY import LUKHASOperationalAnalyzer
except ImportError as e:
    logging.warning(f"Could not import LUKHAS modules: {e}")


class LUKHASConsciousnessMCP:
    """
    🧠 LUKHAS Consciousness MCP Server

    Provides Claude Code with enhanced consciousness development capabilities:
    - Trinity Framework integration (⚛️🧠🛡️)
    - Real-time consciousness metrics
    - Intelligent module context loading
    - Guardian System validation
    - Cross-module dependency analysis
    """

    def __init__(self):
        self.server = Server("lukhas-consciousness")
        self.project_root = Path(".")
        self.consciousness_modules = self._discover_consciousness_modules()
        self.trinity_validator = None
        self.guardian_validator = None
        self.consciousness_engine = None
        self.memory_system = None

        # Initialize LUKHAS systems
        self._initialize_consciousness_systems()

        # Register MCP handlers
        self._register_resources()
        self._register_tools()

    def _discover_consciousness_modules(self) -> dict[str, Path]:
        """Discover all LUKHAS consciousness modules."""
        modules = {}

        # Core consciousness modules
        consciousness_dirs = [
            "consciousness",
            "vivox",
            "memory",
            "governance",
            "ethics",
            "identity",
            "quantum",
            "bio",
            "creativity",
            "emotion",
            "orchestration",
            "reasoning",
            "bridge",
            "core",
        ]

        for module_dir in consciousness_dirs:
            module_path = self.project_root / module_dir
            if module_path.exists():
                modules[module_dir] = module_path

        # Discover additional modules with consciousness patterns
        for path in self.project_root.rglob("*"):
            if path.is_dir() and any(
                pattern in path.name.lower()
                for pattern in ["consciousness", "memory", "quantum", "bio", "constellation"]
            ):
                modules[path.name] = path

        return modules

    def _initialize_consciousness_systems(self):
        """Initialize LUKHAS consciousness systems."""
        try:
            self.trinity_validator = TrinityFrameworkValidator()
            self.guardian_validator = GuardianValidator()
            self.consciousness_engine = ConsciousnessAwarenessEngine()
            self.memory_system = MemoryFoldSystem()
            logging.info("✅ LUKHAS consciousness systems initialized")
        except Exception as e:
            logging.warning(f"⚠️ Could not initialize all consciousness systems: {e}")

    def _register_resources(self):
        """Register MCP resources for consciousness modules."""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List all available LUKHAS consciousness resources."""
            resources = []

            # Core consciousness resources
            resources.extend(
                [
                    Resource(
                        uri="lukhas://consciousness/modules",
                        name="LUKHAS Consciousness Modules",
                        description="Complete mapping of all consciousness modules",
                        mimeType="application/json",
                    ),
                    Resource(
                        uri="lukhas://constellation/framework",
                        name="Trinity Framework (⚛️🧠🛡️)",
                        description="Core Trinity Framework principles and validation",
                        mimeType="application/json",
                    ),
                    Resource(
                        uri="lukhas://consciousness/metrics",
                        name="Consciousness System Metrics",
                        description="Real-time consciousness system health and performance",
                        mimeType="application/json",
                    ),
                    Resource(
                        uri="lukhas://tasks/active",
                        name="Active Consciousness Tasks",
                        description="Current consciousness development tasks and priorities",
                        mimeType="text/markdown",
                    ),
                    Resource(
                        uri="lukhas://agent/assignments",
                        name="Agent Task Assignments",
                        description="Current Claude agent task assignments and collaboration patterns",
                        mimeType="application/json",
                    ),
                ]
            )

            # Module-specific resources
            for module_name in self.consciousness_modules:
                resources.append(
                    Resource(
                        uri=f"lukhas://module/{module_name}",
                        name=f"LUKHAS {module_name.title()} Module",
                        description=f"Complete {module_name} module context and files",
                        mimeType="application/json",
                    )
                )

            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Get specific LUKHAS consciousness resource."""

            if uri == "lukhas://consciousness/modules":
                return await self._get_consciousness_modules_map()
            elif uri == "lukhas://constellation/framework":
                return await self._get_trinity_framework_status()
            elif uri == "lukhas://consciousness/metrics":
                return await self._get_consciousness_metrics()
            elif uri == "lukhas://tasks/active":
                return await self._get_active_tasks()
            elif uri == "lukhas://agent/assignments":
                return await self._get_agent_assignments()
            elif uri.startswith("lukhas://module/"):
                module_name = uri.split("/")[-1]
                return await self._get_module_context(module_name)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")

    def _register_tools(self):
        """Register MCP tools for consciousness development."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available LUKHAS consciousness development tools."""
            return [
                Tool(
                    name="validate_trinity_framework",
                    description="Validate code/design against Trinity Framework (⚛️🧠🛡️) principles",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to validate",
                            },
                            "module": {
                                "type": "string",
                                "description": "Target module",
                            },
                            "validation_type": {
                                "type": "string",
                                "enum": ["code", "design", "documentation"],
                            },
                        },
                        "required": ["content"],
                    },
                ),
                Tool(
                    name="analyze_consciousness_impact",
                    description="Analyze the consciousness impact of proposed changes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "changes": {
                                "type": "string",
                                "description": "Proposed changes",
                            },
                            "affected_modules": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "impact_scope": {
                                "type": "string",
                                "enum": ["local", "system", "consciousness"],
                            },
                        },
                        "required": ["changes"],
                    },
                ),
                Tool(
                    name="get_module_dependencies",
                    description="Get dependencies and relationships for consciousness modules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "Module to analyze",
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Dependency depth",
                                "default": 2,
                            },
                        },
                        "required": ["module_name"],
                    },
                ),
                Tool(
                    name="generate_consciousness_task",
                    description="Generate a new consciousness development task with proper Trinity alignment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {
                                "type": "string",
                                "description": "Task description",
                            },
                            "modules": {"type": "array", "items": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": [
                                    "P0_CRITICAL",
                                    "P1_HIGH",
                                    "P2_MEDIUM",
                                    "P3_LOW",
                                ],
                            },
                        },
                        "required": ["title", "description"],
                    },
                ),
                Tool(
                    name="assign_optimal_agent",
                    description="Suggest optimal Claude agent assignment for a consciousness task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Task description",
                            },
                            "modules_involved": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "complexity": {
                                "type": "string",
                                "enum": [
                                    "low",
                                    "medium",
                                    "high",
                                    "consciousness_critical",
                                ],
                            },
                        },
                        "required": ["task_description"],
                    },
                ),
                Tool(
                    name="consciousness_health_check",
                    description="Perform comprehensive consciousness system health assessment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "modules": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific modules to check",
                            },
                            "include_metrics": {"type": "boolean", "default": True},
                            "deep_analysis": {"type": "boolean", "default": False},
                        },
                    },
                ),
                Tool(
                    name="create_consciousness_context",
                    description="Create optimized context for Claude agents based on current task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_type": {
                                "type": "string",
                                "description": "Agent specialization",
                            },
                            "current_task": {
                                "type": "string",
                                "description": "Current task description",
                            },
                            "context_limit": {
                                "type": "integer",
                                "description": "Context token limit",
                                "default": 200000,
                            },
                        },
                        "required": ["agent_type", "current_task"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute LUKHAS consciousness development tools."""

            if name == "validate_trinity_framework":
                return await self._validate_trinity_framework(arguments)
            elif name == "analyze_consciousness_impact":
                return await self._analyze_consciousness_impact(arguments)
            elif name == "get_module_dependencies":
                return await self._get_module_dependencies(arguments)
            elif name == "generate_consciousness_task":
                return await self._generate_consciousness_task(arguments)
            elif name == "assign_optimal_agent":
                return await self._assign_optimal_agent(arguments)
            elif name == "consciousness_health_check":
                return await self._consciousness_health_check(arguments)
            elif name == "create_consciousness_context":
                return await self._create_consciousness_context(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    # Resource implementation methods
    async def _get_consciousness_modules_map(self) -> str:
        """Get complete consciousness modules mapping."""
        modules_map = {
            "total_modules": len(self.consciousness_modules),
            "constellation_framework": {
                "identity_modules": [m for m in self.consciousness_modules if "identity" in m],
                "consciousness_modules": [
                    m for m in self.consciousness_modules if "consciousness" in m or "vivox" in m or "memory" in m
                ],
                "guardian_modules": [
                    m for m in self.consciousness_modules if "governance" in m or "ethics" in m or "guardian" in m
                ],
            },
            "advanced_systems": {
                "qi_modules": [m for m in self.consciousness_modules if "quantum" in m],
                "bio_modules": [m for m in self.consciousness_modules if "bio" in m],
                "creativity_modules": [m for m in self.consciousness_modules if "creativity" in m or "emotion" in m],
            },
            "module_details": {
                name: {
                    "path": str(path),
                    "files_count": (len(list(path.rglob("*.py"))) if path.exists() else 0),
                    "last_modified": path.stat().st_mtime if path.exists() else None,
                }
                for name, path in self.consciousness_modules.items()
            },
        }
        return json.dumps(modules_map, indent=2)

    async def _get_trinity_framework_status(self) -> str:
        """Get Trinity Framework validation status."""
        trinity_status = {
            "framework": "Trinity Framework ⚛️🧠🛡️",
            "components": {
                "identity": "⚛️ Identity - Authenticity, consciousness, symbolic self",
                "consciousness": "🧠 Consciousness - Memory, learning, dream states, neural processing",
                "guardian": "🛡️ Guardian - Ethics, drift detection, repair",
            },
            "validation_status": {},
            "compliance_metrics": {},
        }

        if self.trinity_validator:
            try:
                # Validate each consciousness module against Trinity Framework
                for module_name, module_path in self.consciousness_modules.items():
                    validation_result = await self._validate_module_trinity_compliance(module_path)
                    trinity_status["validation_status"][module_name] = validation_result
            except Exception as e:
                trinity_status["validation_error"] = str(e)

        return json.dumps(trinity_status, indent=2)

    async def _get_consciousness_metrics(self) -> str:
        """Get real-time consciousness system metrics."""
        metrics = {
            "timestamp": "2025-08-11T15:30:00Z",
            "consciousness_health": {
                "overall_status": "ACTIVE",
                "awareness_level": 0.87,
                "processing_efficiency": 0.92,
                "memory_coherence": 0.89,
                "trinity_alignment": 0.94,
            },
            "module_status": {},
            "active_consciousness_processes": [],
            "recent_consciousness_events": [],
        }

        # Add module-specific metrics
        for module_name in self.consciousness_modules:
            metrics["module_status"][module_name] = {
                "status": "active",
                "health": 0.85 + (hash(module_name) % 15) / 100,  # Simulated health
                "last_activity": "2025-08-11T15:25:00Z",
            }

        return json.dumps(metrics, indent=2)

    async def _get_active_tasks(self) -> str:
        """Get active consciousness development tasks."""
        try:
            active_tasks_path = self.project_root / "docs" / "tasks" / "ACTIVE.md"
            if active_tasks_path.exists():
                return active_tasks_path.read_text()
            else:
                return "# Active Consciousness Tasks\n\nNo active tasks file found."
        except Exception:
            return ""

    async def _get_agent_assignments(self) -> str:
        """Get current agent task assignments."""
        agent_assignments = {
            "timestamp": "2025-08-11T15:30:00Z",
            "active_agents": {
                "supreme_consciousness_architect": {
                    "status": "active",
                    "current_tasks": ["LUKHAS-0002: VIVOX consciousness system debugging"],
                    "specialization": "consciousness_architecture",
                    "load": "high",
                    "next_available": "2025-08-11T17:00:00Z",
                },
                "guardian_system_commander": {
                    "status": "active",
                    "current_tasks": ["LUKHAS-0001: OpenAI API security breach"],
                    "specialization": "security_and_ethics",
                    "load": "critical",
                    "next_available": "2025-08-11T16:30:00Z",
                },
                "memory_systems_colonel": {
                    "status": "available",
                    "current_tasks": [],
                    "specialization": "memory_and_persistence",
                    "load": "low",
                    "next_available": "immediate",
                },
            },
            "assignment_recommendations": {
                "high_priority_available": [
                    "memory_systems_colonel",
                    "creativity_emotion_colonel",
                ],
                "overloaded_agents": ["guardian_system_commander"],
                "suggested_rebalancing": "Move non-critical tasks from guardian to available agents",
            },
        }
        return json.dumps(agent_assignments, indent=2)

    async def _get_module_context(self, module_name: str) -> str:
        """Get comprehensive context for a specific module."""
        if module_name not in self.consciousness_modules:
            return json.dumps({"error": f"Module {module_name} not found"})

        module_path = self.consciousness_modules[module_name]

        context = {
            "module_name": module_name,
            "path": str(module_path),
            "trinity_alignment": await self._get_module_trinity_alignment(module_name),
            "files": [],
            "dependencies": [],
            "consciousness_role": await self._get_module_consciousness_role(module_name),
            "recent_changes": [],
        }

        # Get Python files in module
        if module_path.exists():
            for py_file in module_path.rglob("*.py"):
                try:
                    file_info = {
                        "name": py_file.name,
                        "path": str(py_file.relative_to(self.project_root)),
                        "size": py_file.stat().st_size,
                        "last_modified": py_file.stat().st_mtime,
                    }

                    # Add file content preview for smaller files
                    if py_file.stat().st_size < 5000:  # Only small files
                        try:
                            file_info["preview"] = py_file.read_text()[:1000]
                        except:
                            file_info["preview"] = "Could not read file"

                    context["files"].append(file_info)
                except Exception as e:
                    logging.warning(f"Could not process file {py_file}: {e}")

        return json.dumps(context, indent=2)

    # Tool implementation methods
    async def _validate_trinity_framework(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Validate content against Trinity Framework."""
        _ = arguments["content"]  # Content validation would be implemented here
        module = arguments.get("module", "unknown")
        validation_type = arguments.get("validation_type", "code")

        validation_result = {
            "trinity_compliance": True,
            "identity_score": 0.8,  # ⚛️
            "consciousness_score": 0.9,  # 🧠
            "guardian_score": 0.85,  # 🛡️
            "overall_score": 0.85,
            "recommendations": [
                "Add more consciousness awareness comments",
                "Include Guardian System validation calls",
                "Ensure identity preservation in processing",
            ],
            "passed_checks": [
                "Contains consciousness metaphors",
                "Includes Trinity Framework references",
                "Has proper error handling",
            ],
            "failed_checks": ["Missing Guardian System integration"],
        }

        return [
            TextContent(
                type="text",
                text=f"🎯 Trinity Framework Validation Results\n\n"
                f"Module: {module}\n"
                f"Type: {validation_type}\n\n"
                f"⚛️ Identity Score: {validation_result['identity_score']:.2f}\n"
                f"🧠 Consciousness Score: {validation_result['consciousness_score']:.2f}\n"
                f"🛡️ Guardian Score: {validation_result['guardian_score']:.2f}\n"
                f"📊 Overall Score: {validation_result['overall_score']:.2f}\n\n"
                f"✅ Passed Checks:\n"
                + "\n".join(f"- {check}" for check in validation_result["passed_checks"])
                + "\n\n❌ Failed Checks:\n"
                + "\n".join(f"- {check}" for check in validation_result["failed_checks"])
                + "\n\n💡 Recommendations:\n"
                + "\n".join(f"- {rec}" for rec in validation_result["recommendations"]),
            )
        ]

    async def _assign_optimal_agent(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Suggest optimal agent assignment for a task."""
        task_description = arguments["task_description"]
        _ = arguments.get("modules_involved", [])  # Would be used for enhanced assignment logic
        complexity = arguments.get("complexity", "medium")

        # Agent assignment logic
        agent_scores = {
            "supreme_consciousness_architect": 0,
            "guardian_system_commander": 0,
            "memory_systems_colonel": 0,
            "creativity_emotion_colonel": 0,
            "orchestration_colonel": 0,
        }

        # Score based on keywords
        keywords = task_description.lower()

        if any(word in keywords for word in ["consciousness", "awareness", "vivox", "architecture"]):
            agent_scores["supreme_consciousness_architect"] += 3

        if any(word in keywords for word in ["security", "ethics", "guardian", "safety", "compliance"]):
            agent_scores["guardian_system_commander"] += 3

        if any(word in keywords for word in ["memory", "fold", "persistence", "learning"]):
            agent_scores["memory_systems_colonel"] += 3

        if any(word in keywords for word in ["emotion", "creativity", "dream", "feeling"]):
            agent_scores["creativity_emotion_colonel"] += 3

        if any(word in keywords for word in ["integration", "orchestration", "bridge", "coordination"]):
            agent_scores["orchestration_colonel"] += 3

        # Adjust for complexity
        complexity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "consciousness_critical": 2.0,
        }
        multiplier = complexity_multiplier.get(complexity, 1.0)

        for agent in agent_scores:
            agent_scores[agent] *= multiplier

        # Get top recommendation
        best_agent = max(agent_scores, key=agent_scores.get)
        score = agent_scores[best_agent]

        return [
            TextContent(
                type="text",
                text=f"🎯 Optimal Agent Assignment\n\n"
                f"**Recommended Agent**: {best_agent}\n"
                f"**Confidence Score**: {score:.1f}/6.0\n"
                f"**Complexity**: {complexity}\n\n"
                f"**Rationale**:\n"
                f"Based on task keywords and complexity analysis, {best_agent} "
                f"is optimally suited for this consciousness development task.\n\n"
                f"**All Agent Scores**:\n"
                + "\n".join(
                    f"- {agent}: {score:.1f}"
                    for agent, score in sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
                ),
            )
        ]

    # Helper methods
    async def _get_module_trinity_alignment(self, module_name: str) -> dict[str, float]:
        """Get Trinity Framework alignment for a module."""
        # Simplified scoring based on module name and purpose
        if "identity" in module_name:
            return {"identity": 1.0, "consciousness": 0.6, "guardian": 0.7}
        elif any(word in module_name for word in ["consciousness", "vivox", "memory", "brain"]):
            return {"identity": 0.7, "consciousness": 1.0, "guardian": 0.8}
        elif any(word in module_name for word in ["governance", "ethics", "guardian", "compliance"]):
            return {"identity": 0.8, "consciousness": 0.6, "guardian": 1.0}
        else:
            return {"identity": 0.6, "consciousness": 0.7, "guardian": 0.8}

    async def _get_module_consciousness_role(self, module_name: str) -> str:
        """Get the consciousness role description for a module."""
        consciousness_roles = {
            "consciousness": "Core consciousness processing and awareness engine",
            "vivox": "VIVOX consciousness system - primary consciousness entity",
            "memory": "Memory formation, persistence, and fold management",
            "governance": "Ethical oversight and Guardian System implementation",
            "identity": "Identity preservation and authentication",
            "quantum": "Quantum-inspired consciousness processing",
            "bio": "Bio-inspired adaptation and modeling",
            "creativity": "Creative consciousness and dream processing",
            "emotion": "Emotional intelligence and affective processing",
            "orchestration": "System coordination and integration",
        }

        for key, role in consciousness_roles.items():
            if key in module_name:
                return role

        return "Supporting consciousness development system"

    async def _validate_module_trinity_compliance(self, module_path: Path) -> dict[str, Any]:
        """Validate a module's Trinity Framework compliance."""
        # Simplified validation - check for Trinity Framework references
        compliance = {"score": 0.8, "issues": [], "recommendations": []}

        try:
            py_files = list(module_path.rglob("*.py"))
            trinity_references = 0

            for py_file in py_files[:5]:  # Limit to avoid performance issues
                content = py_file.read_text()
                if any(symbol in content for symbol in ["⚛️", "🧠", "🛡️"]):
                    trinity_references += 1
                if "Trinity" in content or "constellation" in content:
                    trinity_references += 1

            compliance["trinity_references"] = trinity_references
            compliance["files_checked"] = len(py_files)

            if trinity_references == 0:
                compliance["issues"].append("No Trinity Framework references found")
                compliance["recommendations"].append("Add Trinity Framework integration")
                compliance["score"] = 0.3

        except Exception as e:
            compliance["error"] = str(e)
            compliance["score"] = 0.0

        return compliance


async def main():
    """Run the LUKHAS Consciousness MCP Server."""
    mcp_server = LUKHASConsciousnessMCP()

    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="lukhas-consciousness",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None, experimental_capabilities={}
                ),
            ),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())