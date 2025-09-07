"""
🧠 LUCAS DAST Intelligence Modules

AI-powered intelligence components for advanced task management, priority optimization,
context tracking, symbolic reasoning, and workflow analysis.
"""
import streamlit as st

import time
from datetime import datetime
from typing import Any


class TaskIntelligence:
    """
    🧠 AI-powered task intelligence for smart categorization and analysis
    """

    def __init__(self):
        self.learning_patterns: dict[str, Any] = {}
        self.task_embeddings: dict[str, list[float]] = {}

    def analyze_task_complexity(self, task_description: str, context: dict) -> dict[str, Any]:
        """Analyze task complexity using AI patterns"""
        complexity_indicators = {
            "simple": ["fix", "update", "change", "quick"],
            "moderate": ["implement", "create", "build", "develop"],
            "complex": ["design", "architect", "refactor", "integrate"],
            "very_complex": ["system", "platform", "infrastructure", "migration"],
        }

        description_lower = task_description.lower()
        complexity_score = 1.0

        for level, indicators in complexity_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                complexity_scores = {
                    "simple": 1.0,
                    "moderate": 3.0,
                    "complex": 6.0,
                    "very_complex": 10.0,
                }
                complexity_score = complexity_scores[level]
                break

        return {
            "complexity_score": complexity_score,
            "estimated_effort_hours": complexity_score * 2,
            "recommended_approach": self._recommend_approach(complexity_score),
            "risk_factors": self._identify_risk_factors(task_description, context),
        }

    def _recommend_approach(self, complexity_score: float) -> str:
        """Recommend approach based on complexity"""
        if complexity_score <= 2:
            return "Direct implementation - single focused session"
        elif complexity_score <= 5:
            return "Break into 2-3 subtasks, plan dependencies"
        elif complexity_score <= 8:
            return "Create detailed specification, multiple sprints"
        else:
            return "Full design phase required, team collaboration needed"

    def _identify_risk_factors(self, description: str, context: dict) -> list[str]:
        """Identify potential risk factors"""
        risks = []
        description_lower = description.lower()

        if any(word in description_lower for word in ["database", "migration", "schema"]):
            risks.append("Data integrity risk")
        if any(word in description_lower for word in ["api", "breaking", "change"]):
            risks.append("Backward compatibility risk")
        if "production" in description_lower:
            risks.append("Production deployment risk")
        if context.get("dependencies", []):
            risks.append("Dependency coordination risk")

        return risks


class PriorityOptimizer:
    """
    🎯 AI-powered priority optimization with learning capabilities
    """

    def __init__(self):
        self.historical_priorities: list[dict] = []
        self.optimization_patterns: dict[str, float] = {}

    def optimize_priorities(self, tasks: list[dict]) -> list[dict]:
        """Optimize task priorities using AI-powered analysis"""
        optimized_tasks = []

        for task in tasks:
            optimized_priority = self._calculate_dynamic_priority(task)
            task_copy = task.copy()
            task_copy["optimized_priority"] = optimized_priority
            task_copy["optimization_reasoning"] = self._explain_priority_decision(task, optimized_priority)
            optimized_tasks.append(task_copy)

        # Sort by optimized priority
        return sorted(optimized_tasks, key=lambda x: x["optimized_priority"], reverse=True)

    def _calculate_dynamic_priority(self, task: dict) -> float:
        """Calculate dynamic priority score"""
        base_score = 5.0

        # Time pressure factor
        if task.get("due_date"):
            due_date = (
                datetime.fromisoformat(task["due_date"]) if isinstance(task["due_date"], str) else task["due_date"]
            )
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 0:
                base_score += 5.0  # Overdue
            elif days_until_due <= 1:
                base_score += 3.0  # Due soon
            elif days_until_due <= 7:
                base_score += 1.0  # Due this week

        # Business impact factor
        impact_keywords = ["revenue", "customer", "security", "critical", "production"]
        if any(keyword in task.get("description", "").lower() for keyword in impact_keywords):
            base_score += 2.0

        # Effort vs impact ratio
        complexity = task.get("complexity_score", 5.0)
        if complexity > 0:
            efficiency_bonus = min(2.0, 10.0 / complexity)  # Favor high-impact, low-effort tasks
            base_score += efficiency_bonus

        # Dependencies factor
        if task.get("dependencies", []):
            base_score += 1.0  # Prioritize tasks that unlock others

        return min(10.0, base_score)

    def _explain_priority_decision(self, task: dict, priority_score: float) -> str:
        """Provide human-readable explanation for priority decision"""
        explanations = []

        if task.get("due_date"):
            due_date = (
                datetime.fromisoformat(task["due_date"]) if isinstance(task["due_date"], str) else task["due_date"]
            )
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 0:
                explanations.append("OVERDUE - immediate attention required")
            elif days_until_due <= 1:
                explanations.append("Due within 24 hours")

        impact_keywords = ["revenue", "customer", "security", "critical"]
        if any(keyword in task.get("description", "").lower() for keyword in impact_keywords):
            explanations.append("High business impact")

        if task.get("dependencies", []):
            explanations.append("Unlocks other tasks")

        if priority_score >= 8.0:
            explanations.append("TOP PRIORITY")
        elif priority_score >= 6.0:
            explanations.append("High priority")
        elif priority_score >= 4.0:
            explanations.append("Medium priority")
        else:
            explanations.append("Lower priority")

        return " • ".join(explanations) if explanations else "Standard priority"


class ContextTracker:
    """
    📋 Intelligent context tracking and prediction
    """

    def __init__(self):
        self.context_history: list[dict] = []
        self.pattern_cache: dict[str, Any] = {}

    def track_context(self, task_id: str, context: dict) -> dict[str, Any]:
        """Track and analyze task context patterns"""
        context_entry = {
            "task_id": task_id,
            "context": context,
            "timestamp": time.time(),
            "patterns_detected": self._detect_context_patterns(context),
        }

        self.context_history.append(context_entry)

        # Keep only recent history
        if len(self.context_history) > 1000:
            self.context_history = self.context_history[-1000:]

        return {
            "context_insights": self._analyze_context_insights(context),
            "predicted_needs": self._predict_context_needs(context),
            "related_contexts": self._find_related_contexts(context),
        }

    def _detect_context_patterns(self, context: dict) -> list[str]:
        """Detect patterns in task context"""
        patterns = []

        if context.get("repo"):
            patterns.append(f"repository_work:{context['repo']}")
        if context.get("project"):
            patterns.append(f"project_work:{context['project']}")
        if context.get("urgency"):
            patterns.append(f"urgency_level:{context['urgency']}")

        return patterns

    def _analyze_context_insights(self, context: dict) -> dict[str, Any]:
        """Analyze context for actionable insights"""
        insights = {"context_type": "standard", "recommendations": [], "resource_needs": []}

        if context.get("repo"):
            insights["context_type"] = "development"
            insights["recommendations"].append("Ensure development environment is ready")
            insights["resource_needs"].append("Code editor, terminal access")

        if context.get("urgency") == "high":
            insights["recommendations"].append("Clear calendar for focused work")
            insights["recommendations"].append("Notify stakeholders of priority status")

        return insights

    def _predict_context_needs(self, context: dict) -> list[str]:
        """Predict likely future context needs"""
        predictions = []

        if context.get("repo"):
            predictions.append("Likely to need testing environment")
            predictions.append("May require code review")

        if any(keyword in str(context).lower() for keyword in ["api", "endpoint"]):
            predictions.append("API documentation may be needed")
            predictions.append("Postman/testing tools might be required")

        return predictions

    def _find_related_contexts(self, context: dict) -> list[dict]:
        """Find related contexts from history"""
        related = []

        for historical_context in self.context_history[-50:]:  # Check recent 50
            similarity_score = self._calculate_context_similarity(context, historical_context["context"])
            if similarity_score > 0.5:
                related.append(
                    {
                        "task_id": historical_context["task_id"],
                        "similarity_score": similarity_score,
                        "context": historical_context["context"],
                    }
                )

        return sorted(related, key=lambda x: x["similarity_score"], reverse=True)[:5]

    def _calculate_context_similarity(self, context1: dict, context2: dict) -> float:
        """Calculate similarity between two contexts"""
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0

        matches = sum(1 for key in common_keys if context1[key] == context2[key])
        total_keys = len(set(context1.keys()) | set(context2.keys()))

        return matches / total_keys if total_keys > 0 else 0.0


class SymbolicReasoner:
    """
    🔮 Symbolic reasoning engine for complex task relationships
    """

    def __init__(self):
        self.reasoning_rules: dict[str, Any] = self._initialize_reasoning_rules()
        self.inference_cache: dict[str, Any] = {}

    def _initialize_reasoning_rules(self) -> dict[str, Any]:
        """Initialize symbolic reasoning rules"""
        return {
            "dependency_rules": {
                "testing_depends_on_implementation": {
                    "if_pattern": ["implement", "build", "create"],
                    "then_suggest": "Add testing task",
                    "reasoning": "Implementation tasks typically require testing",
                },
                "deployment_depends_on_testing": {
                    "if_pattern": ["test", "qa", "verify"],
                    "then_suggest": "Consider deployment task",
                    "reasoning": "Tested features are ready for deployment",
                },
            },
            "priority_rules": {
                "security_high_priority": {
                    "if_pattern": ["security", "vulnerability", "exploit"],
                    "then_action": "elevate_priority",
                    "reasoning": "Security issues require immediate attention",
                },
                "documentation_lower_priority": {
                    "if_pattern": ["docs", "documentation", "readme"],
                    "unless_pattern": ["critical", "urgent"],
                    "then_action": "standard_priority",
                    "reasoning": "Documentation is important but rarely urgent",
                },
            },
        }

    def apply_reasoning(self, task: dict, context: dict) -> dict[str, Any]:
        """Apply symbolic reasoning to task and context"""
        reasoning_result = {
            "inferences": [],
            "suggested_actions": [],
            "logical_connections": [],
            "confidence_score": 0.0,
        }

        # Apply dependency reasoning
        dependency_inferences = self._apply_dependency_reasoning(task, context)
        reasoning_result["inferences"].extend(dependency_inferences)

        # Apply priority reasoning
        priority_inferences = self._apply_priority_reasoning(task, context)
        reasoning_result["inferences"].extend(priority_inferences)

        # Calculate confidence based on number of matching patterns
        reasoning_result["confidence_score"] = min(1.0, len(reasoning_result["inferences"]) * 0.3)

        return reasoning_result

    def _apply_dependency_reasoning(self, task: dict, context: dict) -> list[dict]:
        """Apply dependency reasoning rules"""
        inferences = []
        task_description = task.get("description", "").lower()

        for rule_name, rule in self.reasoning_rules["dependency_rules"].items():
            if any(pattern in task_description for pattern in rule["if_pattern"]):
                inferences.append(
                    {
                        "type": "dependency_inference",
                        "rule": rule_name,
                        "suggestion": rule["then_suggest"],
                        "reasoning": rule["reasoning"],
                        "confidence": 0.8,
                    }
                )

        return inferences

    def _apply_priority_reasoning(self, task: dict, context: dict) -> list[dict]:
        """Apply priority reasoning rules"""
        inferences = []
        task_description = task.get("description", "").lower()

        for rule_name, rule in self.reasoning_rules["priority_rules"].items():
            if any(pattern in task_description for pattern in rule["if_pattern"]):
                # Check unless conditions
                unless_patterns = rule.get("unless_pattern", [])
                if not any(pattern in task_description for pattern in unless_patterns):
                    inferences.append(
                        {
                            "type": "priority_inference",
                            "rule": rule_name,
                            "action": rule["then_action"],
                            "reasoning": rule["reasoning"],
                            "confidence": 0.9,
                        }
                    )

        return inferences


class WorkflowAnalyzer:
    """
    📊 Intelligent workflow analysis and optimization
    """

    def __init__(self):
        self.workflow_patterns: dict[str, Any] = {}
        self.performance_metrics: dict[str, list[float]] = {}

    def analyze_workflow(self, tasks: list[dict], timeframe_days: int = 7) -> dict[str, Any]:
        """Analyze workflow patterns and performance"""
        analysis = {
            "efficiency_score": 0.0,
            "bottlenecks": [],
            "optimization_suggestions": [],
            "workflow_insights": {},
            "performance_trends": {},
        }

        # Calculate efficiency metrics
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        total_tasks = len(tasks)

        if total_tasks > 0:
            completion_rate = len(completed_tasks) / total_tasks
            analysis["efficiency_score"] = completion_rate

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(tasks)
        analysis["bottlenecks"] = bottlenecks

        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(tasks, bottlenecks)
        analysis["optimization_suggestions"] = suggestions

        # Workflow insights
        insights = self._extract_workflow_insights(tasks)
        analysis["workflow_insights"] = insights

        return analysis

    def _identify_bottlenecks(self, tasks: list[dict]) -> list[dict]:
        """Identify workflow bottlenecks"""
        bottlenecks = []

        # Tasks stuck in progress
        stuck_tasks = [t for t in tasks if t.get("status") == "in_progress" and self._task_age_days(t) > 3]
        if stuck_tasks:
            bottlenecks.append(
                {
                    "type": "stuck_in_progress",
                    "count": len(stuck_tasks),
                    "description": "Tasks stuck in progress for >3 days",
                    "impact": "high",
                }
            )

        # Blocked tasks
        blocked_tasks = [t for t in tasks if t.get("status") == "blocked"]
        if blocked_tasks:
            bottlenecks.append(
                {
                    "type": "blocked_tasks",
                    "count": len(blocked_tasks),
                    "description": "Tasks waiting on external dependencies",
                    "impact": "medium",
                }
            )

        # High-priority backlog
        high_priority_pending = [
            t for t in tasks if t.get("priority") in ["critical", "high"] and t.get("status") == "pending"
        ]
        if len(high_priority_pending) > 5:
            bottlenecks.append(
                {
                    "type": "priority_backlog",
                    "count": len(high_priority_pending),
                    "description": "Large backlog of high-priority tasks",
                    "impact": "high",
                }
            )

        return bottlenecks

    def _generate_optimization_suggestions(self, tasks: list[dict], bottlenecks: list[dict]) -> list[str]:
        """Generate workflow optimization suggestions"""
        suggestions = []

        for bottleneck in bottlenecks:
            if bottleneck["type"] == "stuck_in_progress":
                suggestions.append("Schedule daily check-ins for in-progress tasks")
                suggestions.append("Consider breaking down complex tasks")

            elif bottleneck["type"] == "blocked_tasks":
                suggestions.append("Create unblocking tasks with clear owners")
                suggestions.append("Set up automated notifications for blockers")

            elif bottleneck["type"] == "priority_backlog":
                suggestions.append("Review and reassess task priorities")
                suggestions.append("Consider adding team capacity or scope reduction")

        # General suggestions
        if len(tasks) > 20:
            suggestions.append("Consider using task batching for similar work")

        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        if len(completed_tasks) > 0:
            avg_completion_time = sum(self._task_age_days(t) for t in completed_tasks) / len(completed_tasks)
            if avg_completion_time > 5:
                suggestions.append("Focus on reducing task cycle time")

        return list(set(suggestions))  # Remove duplicates

    def _extract_workflow_insights(self, tasks: list[dict]) -> dict[str, Any]:
        """Extract actionable workflow insights"""
        insights = {}

        # Task distribution by status
        status_distribution = {}
        for task in tasks:
            status = task.get("status", "unknown")
            status_distribution[status] = status_distribution.get(status, 0) + 1
        insights["status_distribution"] = status_distribution

        # Priority distribution
        priority_distribution = {}
        for task in tasks:
            priority = task.get("priority", "unknown")
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        insights["priority_distribution"] = priority_distribution

        # Average task age by status
        avg_age_by_status = {}
        for status in status_distribution:
            status_tasks = [t for t in tasks if t.get("status") == status]
            if status_tasks:
                avg_age = sum(self._task_age_days(t) for t in status_tasks) / len(status_tasks)
                avg_age_by_status[status] = round(avg_age, 1)
        insights["avg_age_by_status"] = avg_age_by_status

        return insights

    def _task_age_days(self, task: dict) -> float:
        """Calculate task age in days"""
        created_at = task.get("created_at")
        if not created_at:
            return 0.0

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            return 0.0

        age = datetime.now() - created_at
        return age.total_seconds() / (24 * 3600)  # Convert to days
