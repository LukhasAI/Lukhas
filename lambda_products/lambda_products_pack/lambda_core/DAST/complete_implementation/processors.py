"""
🔄 LUCAS DAST Processors

Specialized processors for tasks, tags, attention management, and solution tracking
with AI-powered optimization and real-time processing capabilities.
"""

import time
from datetime import datetime
from typing import Any, Optional


class TaskProcessor:
    """
    📋 AI-powered task processing with intelligent categorization and optimization
    """

    def __init__(self):
        self.processing_patterns: dict[str, Any] = {}
        self.task_templates: dict[str, dict] = self._initialize_templates()
        self.processing_cache: dict[str, Any] = {}

    def _initialize_templates(self) -> dict[str, dict]:
        """Initialize task processing templates"""
        return {
            "bug_fix": {
                "pattern": ["bug", "fix", "error", "issue", "broken"],
                "default_priority": "high",
                "estimated_duration": 60,
                "required_tags": ["bug"],
                "workflow_steps": ["investigate", "fix", "test", "deploy"]
            },
            "feature_development": {
                "pattern": ["feature", "implement", "add", "create", "build"],
                "default_priority": "medium",
                "estimated_duration": 240,
                "required_tags": ["feature"],
                "workflow_steps": ["design", "implement", "test", "review", "deploy"]
            },
            "documentation": {
                "pattern": ["docs", "documentation", "readme", "guide"],
                "default_priority": "low",
                "estimated_duration": 30,
                "required_tags": ["documentation"],
                "workflow_steps": ["research", "write", "review", "publish"]
            },
            "testing": {
                "pattern": ["test", "testing", "qa", "quality", "verify"],
                "default_priority": "medium",
                "estimated_duration": 90,
                "required_tags": ["testing"],
                "workflow_steps": ["plan", "execute", "validate", "report"]
            }
        }

    def process_task(self, task_data: dict) -> dict[str, Any]:
        """Process task with AI-powered enhancements"""
        start_time = time.time()

        processed_task = task_data.copy()

        # Apply template matching
        template = self._match_template(task_data)
        if template:
            processed_task = self._apply_template(processed_task, template)

        # Enhance with AI processing
        ai_enhancements = self._apply_ai_enhancements(processed_task)
        processed_task.update(ai_enhancements)

        # Add processing metadata
        processed_task["processing_metadata"] = {
            "processed_at": datetime.now().isoformat(),
            "processing_time_ms": (time.time() - start_time) * 1000,
            "template_applied": template["name"] if template else None,
            "ai_confidence": ai_enhancements.get("ai_confidence", 0.8)
        }

        return processed_task

    def _match_template(self, task_data: dict) -> Optional[dict]:
        """Match task to appropriate template using AI pattern recognition"""
        description = task_data.get("description", "").lower()
        title = task_data.get("title", "").lower()
        combined_text = f"{title} {description}"

        best_match = None
        highest_score = 0.0

        for template_name, template in self.task_templates.items():
            score = self._calculate_template_match_score(combined_text, template["pattern"])
            if score > highest_score and score > 0.3:  # Minimum threshold
                highest_score = score
                best_match = {
                    "name": template_name,
                    "score": score,
                    **template
                }

        return best_match

    def _calculate_template_match_score(self, text: str, patterns: list[str]) -> float:
        """Calculate how well text matches template patterns"""
        matches = sum(1 for pattern in patterns if pattern in text)
        return matches / len(patterns) if patterns else 0.0

    def _apply_template(self, task_data: dict, template: dict) -> dict:
        """Apply template defaults and enhancements to task"""
        enhanced_task = task_data.copy()

        # Apply default priority if not set
        if not enhanced_task.get("priority"):
            enhanced_task["priority"] = template["default_priority"]

        # Apply estimated duration if not set
        if not enhanced_task.get("estimated_duration"):
            enhanced_task["estimated_duration"] = template["estimated_duration"]

        # Add required tags
        current_tags = set(enhanced_task.get("tags", []))
        required_tags = set(template.get("required_tags", []))
        enhanced_task["tags"] = list(current_tags | required_tags)

        # Add workflow steps
        enhanced_task["suggested_workflow"] = template.get("workflow_steps", [])

        return enhanced_task

    def _apply_ai_enhancements(self, task_data: dict) -> dict[str, Any]:
        """Apply AI-powered task enhancements"""
        enhancements = {}

        # Smart duration estimation
        if not task_data.get("estimated_duration"):
            enhancements["estimated_duration"] = self._ai_estimate_duration(task_data)

        # Intelligent tag suggestions
        suggested_tags = self._ai_suggest_tags(task_data)
        current_tags = set(task_data.get("tags", []))
        enhancements["suggested_additional_tags"] = list(set(suggested_tags) - current_tags)

        # Risk assessment
        enhancements["risk_assessment"] = self._ai_assess_risks(task_data)

        # Success criteria suggestions
        enhancements["suggested_success_criteria"] = self._ai_suggest_success_criteria(task_data)

        # AI confidence score
        enhancements["ai_confidence"] = 0.85  # Would be calculated by actual AI models

        return enhancements

    def _ai_estimate_duration(self, task_data: dict) -> int:
        """AI-powered duration estimation in minutes"""
        description = task_data.get("description", "").lower()

        # Complexity indicators
        if any(word in description for word in ["quick", "simple", "minor"]):
            return 30
        elif any(word in description for word in ["refactor", "redesign", "architecture"]):
            return 480
        elif any(word in description for word in ["complex", "major", "system"]):
            return 360
        elif any(word in description for word in ["implement", "create", "build"]):
            return 180
        else:
            return 120  # Default

    def _ai_suggest_tags(self, task_data: dict) -> list[str]:
        """AI-powered tag suggestions"""
        description = task_data.get("description", "").lower()
        title = task_data.get("title", "").lower()
        combined_text = f"{title} {description}"

        tag_patterns = {
            "frontend": ["ui", "frontend", "react", "vue", "angular", "css", "html"],
            "backend": ["api", "backend", "server", "database", "db"],
            "devops": ["deploy", "deployment", "docker", "kubernetes", "ci/cd"],
            "security": ["security", "auth", "authorization", "vulnerability"],
            "performance": ["performance", "optimize", "speed", "slow", "fast"],
            "mobile": ["mobile", "ios", "android", "react-native"],
            "urgent": ["urgent", "asap", "critical", "emergency"],
            "research": ["research", "investigate", "explore", "spike"]
        }

        suggested_tags = []
        for tag, patterns in tag_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                suggested_tags.append(tag)

        return suggested_tags

    def _ai_assess_risks(self, task_data: dict) -> dict[str, Any]:
        """AI-powered risk assessment"""
        description = task_data.get("description", "").lower()

        risks = {
            "technical_complexity": "low",
            "timeline_risk": "low",
            "dependency_risk": "low",
            "business_impact": "medium"
        }

        # Technical complexity assessment
        if any(word in description for word in ["complex", "architecture", "refactor"]):
            risks["technical_complexity"] = "high"
        elif any(word in description for word in ["integration", "api", "database"]):
            risks["technical_complexity"] = "medium"

        # Timeline risk assessment
        if task_data.get("due_date"):
            due_date = datetime.fromisoformat(task_data["due_date"]) if isinstance(task_data["due_date"], str) else task_data["due_date"]
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 1:
                risks["timeline_risk"] = "high"
            elif days_until_due <= 7:
                risks["timeline_risk"] = "medium"

        # Dependency risk
        if task_data.get("dependencies", []):
            risks["dependency_risk"] = "high" if len(task_data["dependencies"]) > 2 else "medium"

        return risks

    def _ai_suggest_success_criteria(self, task_data: dict) -> list[str]:
        """AI-powered success criteria suggestions"""
        description = task_data.get("description", "").lower()

        criteria = ["Task completed successfully"]

        if "test" in description:
            criteria.append("All tests pass")
        if "deploy" in description:
            criteria.append("Deployment successful with no rollbacks")
        if "performance" in description:
            criteria.append("Performance metrics meet or exceed targets")
        if "bug" in description or "fix" in description:
            criteria.append("Issue resolved and verified in production")
        if "feature" in description:
            criteria.append("Feature works as specified")
            criteria.append("User acceptance criteria met")

        return criteria

class TagProcessor:
    """
    🏷️ Intelligent tag processing and management
    """

    def __init__(self):
        self.tag_hierarchy: dict[str, list[str]] = self._initialize_tag_hierarchy()
        self.tag_analytics: dict[str, dict] = {}

    def _initialize_tag_hierarchy(self) -> dict[str, list[str]]:
        """Initialize hierarchical tag structure"""
        return {
            "technology": ["frontend", "backend", "mobile", "devops", "database"],
            "priority": ["critical", "high", "medium", "low"],
            "type": ["feature", "bug", "task", "research", "documentation"],
            "status": ["new", "in-progress", "review", "testing", "done"],
            "team": ["engineering", "design", "product", "qa", "devops"]
        }

    def process_tags(self, tags: list[str], context: Optional[dict] = None) -> dict[str, Any]:
        """Process and enhance tags with intelligent categorization"""
        processed = {
            "original_tags": tags,
            "normalized_tags": self._normalize_tags(tags),
            "suggested_tags": self._suggest_additional_tags(tags, context or {}),
            "tag_categories": self._categorize_tags(tags),
            "tag_conflicts": self._detect_tag_conflicts(tags),
            "tag_analytics": self._analyze_tag_usage(tags)
        }

        return processed

    def _normalize_tags(self, tags: list[str]) -> list[str]:
        """Normalize tag formatting and handle aliases"""
        normalized = []

        # Tag aliases mapping
        aliases = {
            "fe": "frontend",
            "be": "backend",
            "ui": "frontend",
            "ux": "design",
            "db": "database",
            "api": "backend",
            "infra": "devops"
        }

        for tag in tags:
            # Convert to lowercase and strip whitespace
            clean_tag = tag.lower().strip()

            # Handle aliases
            if clean_tag in aliases:
                clean_tag = aliases[clean_tag]

            # Remove duplicates
            if clean_tag not in normalized:
                normalized.append(clean_tag)

        return normalized

    def _suggest_additional_tags(self, current_tags: list[str], context: dict) -> list[str]:
        """Suggest additional relevant tags"""
        suggestions = []
        current_set = {tag.lower() for tag in current_tags}

        # Context-based suggestions
        if context.get("repo"):
            repo_name = context["repo"].lower()
            if "frontend" in repo_name or "ui" in repo_name:
                if "frontend" not in current_set:
                    suggestions.append("frontend")
            elif "api" in repo_name or "backend" in repo_name:
                if "backend" not in current_set:
                    suggestions.append("backend")

        # Tag combination suggestions
        if "bug" in current_set and "critical" not in current_set and "high" not in current_set:
            suggestions.append("high")
        if "feature" in current_set and "testing" not in current_set:
            suggestions.append("testing")

        return suggestions

    def _categorize_tags(self, tags: list[str]) -> dict[str, list[str]]:
        """Categorize tags by hierarchy"""
        categorized = {}

        for category, category_tags in self.tag_hierarchy.items():
            matching_tags = [tag for tag in tags if tag.lower() in [ct.lower() for ct in category_tags]]
            if matching_tags:
                categorized[category] = matching_tags

        # Handle uncategorized tags
        all_hierarchical_tags = set()
        for category_tags in self.tag_hierarchy.values():
            all_hierarchical_tags.update(tag.lower() for tag in category_tags)

        uncategorized = [tag for tag in tags if tag.lower() not in all_hierarchical_tags]
        if uncategorized:
            categorized["custom"] = uncategorized

        return categorized

    def _detect_tag_conflicts(self, tags: list[str]) -> list[dict[str, Any]]:
        """Detect conflicting tags"""
        conflicts = []
        tags_lower = [tag.lower() for tag in tags]

        # Priority conflicts
        priority_tags = [tag for tag in tags_lower if tag in ["critical", "high", "medium", "low"]]
        if len(priority_tags) > 1:
            conflicts.append({
                "type": "multiple_priorities",
                "conflicting_tags": priority_tags,
                "suggestion": "Use only one priority tag"
            })

        # Status conflicts
        status_tags = [tag for tag in tags_lower if tag in ["new", "in-progress", "review", "testing", "done"]]
        if len(status_tags) > 1:
            conflicts.append({
                "type": "multiple_statuses",
                "conflicting_tags": status_tags,
                "suggestion": "Use only one status tag"
            })

        return conflicts

    def _analyze_tag_usage(self, tags: list[str]) -> dict[str, Any]:
        """Analyze tag usage patterns"""
        return {
            "tag_count": len(tags),
            "unique_categories": len(self._categorize_tags(tags)),
            "completeness_score": self._calculate_tag_completeness(tags),
            "optimization_suggestions": self._suggest_tag_optimizations(tags)
        }

    def _calculate_tag_completeness(self, tags: list[str]) -> float:
        """Calculate how complete the tag set is"""
        categories = self._categorize_tags(tags)
        important_categories = ["technology", "type", "priority"]

        coverage = sum(1 for cat in important_categories if cat in categories)
        return coverage / len(important_categories)

    def _suggest_tag_optimizations(self, tags: list[str]) -> list[str]:
        """Suggest tag optimizations"""
        suggestions = []

        if len(tags) > 8:
            suggestions.append("Consider reducing tag count for better focus")
        elif len(tags) < 3:
            suggestions.append("Consider adding more descriptive tags")

        categories = self._categorize_tags(tags)
        if "priority" not in categories:
            suggestions.append("Add a priority tag (critical/high/medium/low)")
        if "type" not in categories:
            suggestions.append("Add a type tag (feature/bug/task/research)")

        return suggestions

class AttentionProcessor:
    """
    🎯 Intelligent attention management and focus optimization
    """

    def __init__(self):
        self.attention_patterns: dict[str, Any] = {}
        self.focus_sessions: list[dict] = []

    def process_attention_request(self, request: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Process attention/focus requests with AI optimization"""
        attention_analysis = {
            "focus_type": self._classify_focus_type(request),
            "recommended_tasks": [],
            "focus_duration": self._recommend_focus_duration(request),
            "distraction_mitigation": self._suggest_distraction_mitigation(request),
            "attention_score": self._calculate_attention_score(context or {})
        }

        return attention_analysis

    def _classify_focus_type(self, request: str) -> str:
        """Classify the type of focus needed"""
        request_lower = request.lower()

        if any(word in request_lower for word in ["deep", "complex", "thinking", "design"]):
            return "deep_work"
        elif any(word in request_lower for word in ["quick", "small", "minor", "simple"]):
            return "quick_tasks"
        elif any(word in request_lower for word in ["review", "check", "verify"]):
            return "review_mode"
        elif any(word in request_lower for word in ["creative", "brainstorm", "ideate"]):
            return "creative_mode"
        else:
            return "standard_focus"

    def _recommend_focus_duration(self, request: str) -> int:
        """Recommend optimal focus duration in minutes"""
        focus_type = self._classify_focus_type(request)

        duration_map = {
            "deep_work": 90,
            "quick_tasks": 25,
            "review_mode": 45,
            "creative_mode": 60,
            "standard_focus": 50
        }

        return duration_map.get(focus_type, 50)

    def _suggest_distraction_mitigation(self, request: str) -> list[str]:
        """Suggest ways to minimize distractions"""
        suggestions = [
            "Close unnecessary browser tabs",
            "Put phone in do-not-disturb mode",
            "Use noise-cancelling headphones or focus music"
        ]

        focus_type = self._classify_focus_type(request)

        if focus_type == "deep_work":
            suggestions.extend([
                "Block social media and news sites",
                "Clear physical workspace",
                "Schedule longer uninterrupted blocks"
            ])
        elif focus_type == "creative_mode":
            suggestions.extend([
                "Have notebook or whiteboard ready",
                "Ensure good lighting and comfortable seating",
                "Keep inspiration materials accessible"
            ])

        return suggestions

    def _calculate_attention_score(self, context: dict) -> float:
        """Calculate current attention readiness score"""
        base_score = 7.0

        # Time of day factor
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 11 or 14 <= current_hour <= 16:
            base_score += 1.0  # Peak focus hours
        elif current_hour < 8 or current_hour > 18:
            base_score -= 1.0  # Low energy hours

        # Workload factor
        if context.get("current_task_count", 0) > 10:
            base_score -= 1.0  # High workload reduces focus

        # Recent completion factor
        if context.get("recent_completions", 0) > 0:
            base_score += 0.5  # Momentum from recent completions

        return max(1.0, min(10.0, base_score))

class SolutionProcessor:
    """
    💡 Intelligent solution tracking and knowledge management
    """

    def __init__(self):
        self.solution_database: dict[str, Any] = {}
        self.pattern_library: dict[str, list[dict]] = {}

    def process_solution(self, problem: str, solution: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Process and store solution with intelligent categorization"""
        solution_record = {
            "problem": problem,
            "solution": solution,
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "solution_id": self._generate_solution_id(problem, solution),
            "categories": self._categorize_solution(problem, solution),
            "effectiveness_score": 0.0,  # Will be updated based on usage
            "related_solutions": self._find_related_solutions(problem, solution)
        }

        # Store in database
        self.solution_database[solution_record["solution_id"]] = solution_record

        # Update pattern library
        self._update_pattern_library(solution_record)

        return {
            "solution_id": solution_record["solution_id"],
            "categorization": solution_record["categories"],
            "related_count": len(solution_record["related_solutions"]),
            "reusability_score": self._calculate_reusability_score(solution_record)
        }

    def _generate_solution_id(self, problem: str, solution: str) -> str:
        """Generate unique solution ID"""
        import hashlib
        content = f"{problem}{solution}{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _categorize_solution(self, problem: str, solution: str) -> list[str]:
        """Categorize solution for better organization"""
        categories = []
        combined_text = f"{problem} {solution}".lower()

        # Technical categories
        if any(word in combined_text for word in ["bug", "error", "fix"]):
            categories.append("bug_resolution")
        if any(word in combined_text for word in ["performance", "optimize", "speed"]):
            categories.append("performance_optimization")
        if any(word in combined_text for word in ["security", "vulnerability", "auth"]):
            categories.append("security_solution")
        if any(word in combined_text for word in ["api", "integration", "endpoint"]):
            categories.append("integration_solution")
        if any(word in combined_text for word in ["database", "query", "db"]):
            categories.append("database_solution")

        # Complexity categories
        if len(solution.split()) > 50:
            categories.append("complex_solution")
        elif len(solution.split()) < 20:
            categories.append("simple_solution")
        else:
            categories.append("standard_solution")

        return categories if categories else ["general_solution"]

    def _find_related_solutions(self, problem: str, solution: str) -> list[str]:
        """Find related solutions using similarity matching"""
        related = []

        for solution_id, record in self.solution_database.items():
            similarity_score = self._calculate_similarity(
                problem, record["problem"]
            )
            if similarity_score > 0.3:  # Similarity threshold
                related.append(solution_id)

        return related[:5]  # Return top 5 related solutions

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simplified implementation)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _update_pattern_library(self, solution_record: dict):
        """Update pattern library with new solution"""
        for category in solution_record["categories"]:
            if category not in self.pattern_library:
                self.pattern_library[category] = []

            self.pattern_library[category].append({
                "solution_id": solution_record["solution_id"],
                "problem_pattern": self._extract_problem_pattern(solution_record["problem"]),
                "solution_pattern": self._extract_solution_pattern(solution_record["solution"])
            })

    def _extract_problem_pattern(self, problem: str) -> str:
        """Extract generalizable pattern from problem description"""
        # Simplified pattern extraction
        problem_lower = problem.lower()

        if "not working" in problem_lower:
            return "functionality_failure"
        elif "slow" in problem_lower or "performance" in problem_lower:
            return "performance_issue"
        elif "error" in problem_lower or "exception" in problem_lower:
            return "error_occurrence"
        else:
            return "general_problem"

    def _extract_solution_pattern(self, solution: str) -> str:
        """Extract generalizable pattern from solution"""
        solution_lower = solution.lower()

        if "restart" in solution_lower or "reboot" in solution_lower:
            return "restart_resolution"
        elif "update" in solution_lower or "upgrade" in solution_lower:
            return "update_resolution"
        elif "config" in solution_lower or "setting" in solution_lower:
            return "configuration_change"
        else:
            return "custom_solution"

    def _calculate_reusability_score(self, solution_record: dict) -> float:
        """Calculate how reusable this solution is"""
        score = 5.0

        # General solutions are more reusable
        if "general" in solution_record["categories"]:
            score += 2.0

        # Solutions with many related items are more reusable
        related_count = len(solution_record["related_solutions"])
        score += min(3.0, related_count * 0.5)

        # Shorter solutions tend to be more reusable
        solution_length = len(solution_record["solution"].split())
        if solution_length < 30:
            score += 1.0
        elif solution_length > 100:
            score -= 1.0

        return max(1.0, min(10.0, score))
