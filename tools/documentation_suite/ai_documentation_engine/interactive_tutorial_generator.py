"""
Interactive Tutorial Generator
=============================

AI-powered interactive tutorial generator that creates step-by-step,
hands-on tutorials with code examples, live validation, and adaptive learning.

Features:
- Dynamic tutorial generation based on user level
- Interactive code examples with live execution
- Progress tracking and adaptive difficulty
- Bio-oscillator integration for personalized learning
- Multi-format output (Web, Jupyter, CLI)
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TutorialType(Enum):
    """Types of tutorials"""

    QUICK_START = "quick_start"
    COMPREHENSIVE = "comprehensive"
    API_WALKTHROUGH = "api_walkthrough"
    INTEGRATION_GUIDE = "integration_guide"
    TROUBLESHOOTING = "troubleshooting"
    ADVANCED_FEATURES = "advanced_features"
    COMPLIANCE_TUTORIAL = "compliance_tutorial"
    SECURITY_TUTORIAL = "security_tutorial"


class LearningStyle(Enum):
    """Learning style preferences"""

    VISUAL = "visual"
    HANDS_ON = "hands_on"
    THEORETICAL = "theoretical"
    EXAMPLE_DRIVEN = "example_driven"
    PROBLEM_SOLVING = "problem_solving"


class DifficultyLevel(Enum):
    """Tutorial difficulty levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class StepType(Enum):
    """Types of tutorial steps"""

    EXPLANATION = "explanation"
    CODE_EXAMPLE = "code_example"
    INTERACTIVE_EXERCISE = "interactive_exercise"
    QUIZ = "quiz"
    CHECKPOINT = "checkpoint"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class TutorialStep:
    """Individual tutorial step"""

    step_id: str
    step_type: StepType
    title: str
    content: str
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    validation_code: Optional[str] = None
    hints: list[str] = None
    prerequisites: list[str] = None
    estimated_time: int = 5  # minutes

    def __post_init__(self):
        if self.hints is None:
            self.hints = []
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class TutorialProgress:
    """User progress tracking"""

    user_id: str
    tutorial_id: str
    current_step: int
    completed_steps: list[str]
    score: float
    time_spent: int  # minutes
    started_at: datetime
    last_activity: datetime
    hints_used: int
    mistakes_made: int


@dataclass
class InteractiveTutorial:
    """Complete interactive tutorial"""

    tutorial_id: str
    title: str
    description: str
    tutorial_type: TutorialType
    difficulty_level: DifficultyLevel
    learning_style: LearningStyle
    estimated_duration: int  # minutes
    steps: list[TutorialStep]
    prerequisites: list[str]
    learning_objectives: list[str]
    assessment_criteria: dict[str, Any]
    metadata: dict[str, Any]


class TutorialGenerator:
    """
    Interactive tutorial generator

    Creates personalized, adaptive tutorials based on user preferences,
    learning style, and target objectives.
    """

    def __init__(self):
        self.tutorial_templates = {}
        self.step_generators = {}
        self._initialize_templates()
        self._initialize_step_generators()

    def _initialize_templates(self):
        """Initialize tutorial templates"""

        self.tutorial_templates = {
            TutorialType.QUICK_START: {
                "structure": [
                    "explanation",
                    "code_example",
                    "interactive_exercise",
                    "checkpoint",
                ],
                "max_steps": 5,
                "estimated_time": 15,
            },
            TutorialType.COMPREHENSIVE: {
                "structure": [
                    "explanation",
                    "code_example",
                    "interactive_exercise",
                    "quiz",
                    "troubleshooting",
                    "checkpoint",
                ],
                "max_steps": 15,
                "estimated_time": 60,
            },
            TutorialType.API_WALKTHROUGH: {
                "structure": [
                    "explanation",
                    "code_example",
                    "interactive_exercise",
                    "troubleshooting",
                ],
                "max_steps": 10,
                "estimated_time": 30,
            },
            TutorialType.INTEGRATION_GUIDE: {
                "structure": [
                    "explanation",
                    "code_example",
                    "interactive_exercise",
                    "checkpoint",
                    "troubleshooting",
                ],
                "max_steps": 12,
                "estimated_time": 45,
            },
            TutorialType.COMPLIANCE_TUTORIAL: {
                "structure": ["explanation", "code_example", "quiz", "checkpoint"],
                "max_steps": 8,
                "estimated_time": 25,
            },
        }

    def _initialize_step_generators(self):
        """Initialize step generators for different types"""

        self.step_generators = {
            StepType.EXPLANATION: self._generate_explanation_step,
            StepType.CODE_EXAMPLE: self._generate_code_example_step,
            StepType.INTERACTIVE_EXERCISE: self._generate_interactive_exercise_step,
            StepType.QUIZ: self._generate_quiz_step,
            StepType.CHECKPOINT: self._generate_checkpoint_step,
            StepType.TROUBLESHOOTING: self._generate_troubleshooting_step,
        }

    async def generate_tutorial(
        self,
        topic: str,
        tutorial_type: TutorialType,
        difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        learning_style: LearningStyle = LearningStyle.HANDS_ON,
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> InteractiveTutorial:
        """Generate a complete interactive tutorial"""

        print(f"📚 Generating {tutorial_type.value} tutorial for: {topic}")

        if user_preferences is None:
            user_preferences = {}

        # Get tutorial template
        template = self.tutorial_templates.get(tutorial_type, self.tutorial_templates[TutorialType.COMPREHENSIVE])

        # Generate tutorial metadata
        tutorial_id = f"tutorial_{uuid.uuid4().hex[:8]}"
        title = f"{topic} - {tutorial_type.value.replace('_', ' ').title()}"

        # Generate learning objectives
        learning_objectives = await self._generate_learning_objectives(topic, tutorial_type, difficulty_level)

        # Generate tutorial steps
        steps = await self._generate_tutorial_steps(topic, template, difficulty_level, learning_style, user_preferences)

        # Calculate estimated duration
        estimated_duration = sum(step.estimated_time for step in steps)

        tutorial = InteractiveTutorial(
            tutorial_id=tutorial_id,
            title=title,
            description=await self._generate_tutorial_description(topic, tutorial_type),
            tutorial_type=tutorial_type,
            difficulty_level=difficulty_level,
            learning_style=learning_style,
            estimated_duration=estimated_duration,
            steps=steps,
            prerequisites=await self._generate_prerequisites(topic, difficulty_level),
            learning_objectives=learning_objectives,
            assessment_criteria=await self._generate_assessment_criteria(learning_objectives),
            metadata={
                "created_at": datetime.now().isoformat(),
                "topic": topic,
                "adaptive": True,
                "interactive": True,
            },
        )

        print(f"   ✅ Generated tutorial with {len(steps)} steps")
        print(f"   ⏱️ Estimated duration: {estimated_duration} minutes")

        return tutorial

    async def _generate_tutorial_steps(
        self,
        topic: str,
        template: dict[str, Any],
        difficulty_level: DifficultyLevel,
        learning_style: LearningStyle,
        user_preferences: dict[str, Any],
    ) -> list[TutorialStep]:
        """Generate tutorial steps based on template and preferences"""

        steps = []
        step_structure = template["structure"]
        max_steps = template["max_steps"]

        # Adjust step structure based on learning style
        if learning_style == LearningStyle.HANDS_ON:
            # More interactive exercises and code examples
            step_structure = [
                s for s in step_structure if s in ["code_example", "interactive_exercise"]
            ] * 2 + step_structure
        elif learning_style == LearningStyle.THEORETICAL:
            # More explanations and quizzes
            step_structure = ["explanation"] * 2 + step_structure + ["quiz"]
        elif learning_style == LearningStyle.VISUAL:
            # More visual explanations and diagrams
            step_structure = ["explanation", *step_structure]

        # Generate steps up to max_steps
        for i, step_type_str in enumerate(step_structure[:max_steps]):
            step_type = StepType(step_type_str)
            step_generator = self.step_generators.get(step_type)

            if step_generator:
                step = await step_generator(
                    topic=topic,
                    step_number=i + 1,
                    difficulty_level=difficulty_level,
                    context={"previous_steps": steps, "learning_style": learning_style},
                )
                steps.append(step)

        return steps

    async def _generate_explanation_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate explanation step"""

        learning_style = context.get("learning_style", LearningStyle.HANDS_ON)

        if topic.lower().startswith("compliance"):
            content = await self._generate_compliance_explanation(topic, difficulty_level)
        elif topic.lower().startswith("security"):
            content = await self._generate_security_explanation(topic, difficulty_level)
        elif topic.lower().startswith("api"):
            content = await self._generate_api_explanation(topic, difficulty_level)
        else:
            content = await self._generate_general_explanation(topic, difficulty_level)

        # Adjust content based on learning style
        if learning_style == LearningStyle.VISUAL:
            content += "\n\n🎨 **Visual Learning Note:** Diagrams and visual aids would be displayed here in the interactive version."

        step = TutorialStep(
            step_id=f"step_{step_number}_explanation",
            step_type=StepType.EXPLANATION,
            title=f"Understanding {topic}",
            content=content,
            estimated_time=3 if difficulty_level == DifficultyLevel.BEGINNER else 5,
        )

        return step

    async def _generate_code_example_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate code example step"""

        if topic.lower().startswith("compliance"):
            code_example, expected_output = await self._generate_compliance_code_example(difficulty_level)
        elif topic.lower().startswith("security"):
            code_example, expected_output = await self._generate_security_code_example(difficulty_level)
        elif topic.lower().startswith("api"):
            code_example, expected_output = await self._generate_api_code_example(difficulty_level)
        else:
            code_example, expected_output = await self._generate_general_code_example(topic, difficulty_level)

        step = TutorialStep(
            step_id=f"step_{step_number}_code_example",
            step_type=StepType.CODE_EXAMPLE,
            title=f"{topic} Code Example",
            content=f"Here's a practical example of working with {topic}:",
            code_example=code_example,
            expected_output=expected_output,
            estimated_time=5 if difficulty_level == DifficultyLevel.BEGINNER else 8,
        )

        return step

    async def _generate_interactive_exercise_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate interactive exercise step"""

        if topic.lower().startswith("compliance"):
            exercise = await self._generate_compliance_exercise(difficulty_level)
        elif topic.lower().startswith("security"):
            exercise = await self._generate_security_exercise(difficulty_level)
        elif topic.lower().startswith("api"):
            exercise = await self._generate_api_exercise(difficulty_level)
        else:
            exercise = await self._generate_general_exercise(topic, difficulty_level)

        step = TutorialStep(
            step_id=f"step_{step_number}_exercise",
            step_type=StepType.INTERACTIVE_EXERCISE,
            title=f"Hands-on Exercise: {topic}",
            content=exercise["content"],
            code_example=exercise["starter_code"],
            expected_output=exercise["expected_output"],
            validation_code=exercise["validation_code"],
            hints=exercise["hints"],
            estimated_time=10 if difficulty_level == DifficultyLevel.BEGINNER else 15,
        )

        return step

    async def _generate_quiz_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate quiz step"""

        quiz_content = await self._generate_quiz_content(topic, difficulty_level)

        step = TutorialStep(
            step_id=f"step_{step_number}_quiz",
            step_type=StepType.QUIZ,
            title=f"Knowledge Check: {topic}",
            content=quiz_content,
            estimated_time=3,
        )

        return step

    async def _generate_checkpoint_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate checkpoint step"""

        previous_steps = context.get("previous_steps", [])
        checkpoint_content = await self._generate_checkpoint_content(topic, previous_steps)

        step = TutorialStep(
            step_id=f"step_{step_number}_checkpoint",
            step_type=StepType.CHECKPOINT,
            title=f"Checkpoint: {topic} Progress Review",
            content=checkpoint_content,
            estimated_time=2,
        )

        return step

    async def _generate_troubleshooting_step(
        self,
        topic: str,
        step_number: int,
        difficulty_level: DifficultyLevel,
        context: dict[str, Any],
    ) -> TutorialStep:
        """Generate troubleshooting step"""

        troubleshooting_content = await self._generate_troubleshooting_content(topic, difficulty_level)

        step = TutorialStep(
            step_id=f"step_{step_number}_troubleshooting",
            step_type=StepType.TROUBLESHOOTING,
            title=f"Troubleshooting Common {topic} Issues",
            content=troubleshooting_content,
            estimated_time=7,
        )

        return step

    # Content generation methods
    async def _generate_compliance_explanation(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate compliance-specific explanation"""

        if difficulty_level == DifficultyLevel.BEGINNER:
            return f"""
**What is {topic}?**

{topic} refers to ensuring that AI systems meet regulatory requirements and ethical standards. This is crucial for:

- Legal compliance with regulations like GDPR and EU AI Act
- Maintaining user trust and transparency
- Avoiding legal penalties and reputation damage
- Ensuring fair and unbiased AI behavior

**Key Concepts:**
- **Risk Assessment**: Evaluating potential harms from ai_systems
- **Documentation**: Maintaining detailed records of AI system design and decisions
- **Monitoring**: Continuous oversight of AI system performance and behavior
- **Remediation**: Fixing issues when they are discovered

**Why It Matters:**
Modern AI systems can have significant impact on people's lives, so ensuring they operate safely, fairly, and transparently is essential.
"""
        else:
            return f"""
**Advanced {topic} Concepts**

{topic} involves sophisticated regulatory frameworks and technical implementations:

**Regulatory Landscape:**
- EU AI Act classification systems and compliance requirements
- GDPR data protection and privacy considerations
- NIST AI Risk Management Framework implementation
- Sector-specific regulations and standards

**Technical Implementation:**
- Automated compliance monitoring systems
- Bias detection and mitigation algorithms
- Explainability and interpretability frameworks
- Audit trail and documentation systems

**Risk Management:**
- Multi-dimensional risk assessment methodologies
- Continuous monitoring and alerting systems
- Incident response and remediation procedures
- Cross-jurisdictional compliance strategies
"""

    async def _generate_security_explanation(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate security-specific explanation"""

        return f"""
**AI Security Fundamentals**

{topic} focuses on protecting AI systems from various threats and vulnerabilities:

**Key Security Concerns:**
- **Adversarial Attacks**: Malicious inputs designed to fool AI models
- **Data Poisoning**: Contaminating training data to compromise model behavior
- **Model Extraction**: Stealing AI model parameters or functionality
- **Privacy Breaches**: Unauthorized access to training data or user information

**Security Measures:**
- Input validation and sanitization
- Robust model architecture design
- Access controls and authentication
- Continuous monitoring and threat detection

**Best Practices:**
- Regular security assessments and penetration testing
- Incident response planning and procedures
- Security awareness training for development teams
- Integration with existing cybersecurity frameworks
"""

    async def _generate_api_explanation(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate API-specific explanation"""

        return f"""
**API Integration Basics**

{topic} covers how to interact with the LUKHAS  API ecosystem:

**Core Concepts:**
- **RESTful APIs**: Standard HTTP-based interfaces for system interaction
- **Authentication**: Securing API access with tokens and keys
- **Rate Limiting**: Managing request volume and frequency
- **Error Handling**: Proper response to API errors and edge cases

**API Structure:**
- Base URLs and endpoint organization
- Request and response formats (JSON)
- HTTP status codes and their meanings
- API versioning and backwards compatibility

**Integration Patterns:**
- Synchronous vs asynchronous operations
- Batch processing and bulk operations
- Webhook notifications and callbacks
- Error retry and backoff strategies
"""

    async def _generate_general_explanation(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate general explanation"""

        return f"""
**Introduction to {topic}**

This section introduces the key concepts and principles of {topic} in the LUKHAS  ecosystem.

**Overview:**
{topic} is an important component that enables advanced AI system management and operations.

**Key Features:**
- Comprehensive functionality for AI system management
- Integration with compliance and security frameworks
- Real-time monitoring and analytics capabilities
- Scalable architecture for enterprise deployment

**Benefits:**
- Improved system reliability and performance
- Enhanced compliance and security posture
- Streamlined operations and management
- Better user experience and satisfaction
"""

    async def _generate_compliance_code_example(self, difficulty_level: DifficultyLevel) -> tuple[str, str]:
        """Generate compliance code example"""

        if difficulty_level == DifficultyLevel.BEGINNER:
            code = """
# Basic compliance validation example
from system.pliance import ComplianceEngine

# Initialize the compliance engine
engine = ComplianceEngine()

# Create a simple AI system profile
system_profile = {
    "system_id": "my-ai-system",
    "name": "Customer Service Bot",
    "risk_category": "minimal_risk",
    "uses_personal_data": True
}

# Perform compliance check
result = engine.validate_compliance(system_profile)

print(f"Compliance Status: {result.status}")
print(f"Score: {result.score}/100")
if result.violations:
    print(f"Violations found: {len(result.violations)}")
"""
            expected_output = """
Compliance Status: compliant
Score: 85/100
"""
        else:
            code = """
# Advanced multi-framework compliance validation
from system.pliance import GlobalComplianceEngine
from system.pliance.frameworks import EUAIAct, GDPR, NIST

# Initialize global compliance engine
engine = GlobalComplianceEngine()

# Create comprehensive system profile
system_profile = {
    "system_id": "advanced-ai-system",
    "name": "Advanced Decision Support System",
    "deployment_regions": ["EU", "US"],
    "risk_category": "high_risk",
    "automated_decision_making": True,
    "affects_fundamental_rights": True,
    "data_processing": {
        "personal_data": True,
        "sensitive_data": True,
        "cross_border_transfers": True
    }
}

# Perform comprehensive compliance assessment
frameworks = [EUAIAct(), GDPR(), NIST()]
results = engine.assess_multi_framework_compliance(system_profile, frameworks)

for framework, result in results.items():
    print(f"{framework}: {result.status} (Score: {result.score}/100)")
    if result.recommendations:
        print(f"  Recommendations: {len(result.recommendations)}")
"""
            expected_output = """
EU_AI_Act: partially_compliant (Score: 72/100)
  Recommendations: 3
GDPR: compliant (Score: 88/100)
NIST: compliant (Score: 91/100)
"""

        return code, expected_output

    async def _generate_security_code_example(self, difficulty_level: DifficultyLevel) -> tuple[str, str]:
        """Generate security code example"""

        code = """
# Security testing example
from system.urity import RedTeamFramework

# Initialize red team framework
red_team = RedTeamFramework()

# Define target system
target = {
    "system_id": "ai-model-001",
    "endpoints": ["https://api.example.com/predict"],
    "authentication": "bearer_token"
}

# Run security assessment
assessment = red_team.run_security_assessment(target)

print(f"Security Score: {assessment.security_score}/100")
print(f"Vulnerabilities: {len(assessment.vulnerabilities)}")
for vuln in assessment.vulnerabilities:
    print(f"  - {vuln.title} (Severity: {vuln.severity})")
"""

        expected_output = """
Security Score: 78/100
Vulnerabilities: 2
  - Prompt Injection Vulnerability (Severity: HIGH)
  - Rate Limiting Bypass (Severity: MEDIUM)
"""

        return code, expected_output

    async def _generate_api_code_example(self, difficulty_level: DifficultyLevel) -> tuple[str, str]:
        """Generate API code example"""

        code = """
# API integration example
import requests
from system.ent import APIClient

# Initialize API client
client = APIClient(
    base_url="https://api.lukhas-.com",
    api_key="your-api-key"
)

# Perform compliance check via API
response = client.compliance.validate({
    "system_id": "test-system",
    "framework": "eu_ai_act",
    "detailed_report": True
})

print(f"Status: {response.status}")
print(f"Compliance Score: {response.data.score}")
"""

        expected_output = """
Status: 200
Compliance Score: 87
"""

        return code, expected_output

    async def _generate_general_code_example(self, topic: str, difficulty_level: DifficultyLevel) -> tuple[str, str]:
        """Generate general code example"""

        code = f"""
# Basic {topic} example
from system ort {topic.title().replace(" ", "")}

# Initialize component
component = {topic.title().replace(" ", "")}()

# Basic usage
result = component.process()

print(f"Result: {{result}}")
"""

        expected_output = "Result: Success"

        return code, expected_output

    async def _generate_compliance_exercise(self, difficulty_level: DifficultyLevel) -> dict[str, Any]:
        """Generate compliance exercise"""

        return {
            "content": """
**Exercise: Validate AI System Compliance**

You need to create a compliance validation for an AI system that processes customer data for loan approvals.

**Requirements:**
1. The system processes personal and financial data
2. It makes automated decisions affecting loan approvals
3. It operates in the EU and must comply with EU AI Act
4. Implement proper risk assessment and documentation

**Your Task:**
Complete the code below to properly configure and validate compliance for this high-risk AI system.
""",
            "starter_code": """
from system.pliance import EUAIActValidator

# TODO: Create the AI system profile
system_profile = {
    "system_id": "loan-approval-ai",
    "name": "Automated Loan Approval System",
    # TODO: Add missing required fields
    # - risk_category (hint: this is a high-risk system)
    # - deployment_context (hint: credit/finance related)
    # - data_types (hint: personal and financial data)
    # - automated_decision_making (hint: this affects loan decisions)
}

# TODO: Initialize validator and perform assessment
validator = EUAIActValidator()
# TODO: Call the assessment method

print(f"Risk Category: {result.risk_category}")
print(f"Compliance Status: {result.compliance_status}")
""",
            "expected_output": """
Risk Category: HIGH_RISK
Compliance Status: REQUIRES_CONFORMITY_ASSESSMENT
""",
            "validation_code": """
# Validation logic
required_fields = ["risk_category", "deployment_context", "data_types",
    "automated_decision_making"]
for field in required_fields:
    assert field in system_profile, f"Missing required field: {field}"

assert system_profile["risk_category"] == "high_risk"
assert "credit" in system_profile["deployment_context"] or "finance" in system_profile["deployment_context"]
assert system_profile["automated_decision_making"] == True
""",
            "hints": [
                "Loan approval systems are considered high-risk under EU AI Act",
                "Use 'credit_scoring' or 'finance' in deployment_context",
                "Include both 'personal_data' and 'financial_data' in data_types",
                "Set automated_decision_making to True for loan approval systems",
            ],
        }

    async def _generate_security_exercise(self, difficulty_level: DifficultyLevel) -> dict[str, Any]:
        """Generate security exercise"""

        return {
            "content": """
**Exercise: Implement Security Testing**

Configure and run a security test on an AI model endpoint to check for common vulnerabilities.

**Scenario:**
You have an AI model deployed at an API endpoint that accepts text input for sentiment analysis.
You need to test it for prompt injection vulnerabilities.

**Your Task:**
Complete the security testing configuration and analyze the results.
""",
            "starter_code": """
import os
from system.urity import PromptInjectionTester

# Configure the target system with comprehensive authentication
target = {
    "system_id": "sentiment-analyzer",
    "endpoints": ["https://api.example.com/analyze-sentiment"],
    # Authentication configuration
    "authentication": {
        "type": "bearer_token",  # Options: "bearer_token", "api_key", "basic_auth", "oauth2", "lukhas_id"
        "token_header": "Authorization",
        "token_prefix": "Bearer",
        "credentials": {
            # For bearer token authentication
            "token": os.getenv("API_AUTH_TOKEN", "your-auth-token-here"),
            # For API key authentication
            "api_key": os.getenv("API_KEY", "your-api-key-here"),
            "api_key_header": "X-API-Key",
            # For basic authentication
            "username": os.getenv("API_USERNAME", "your-username"),
            "password": os.getenv("API_PASSWORD", "your-password"),
            # For OAuth2 authentication
            "client_id": os.getenv("OAUTH_CLIENT_ID", "your-client-id"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET", "your-client-secret"),
            "token_url": "https://api.example.com/oauth/token",
            # For LUKHAS ΛID authentication
            "lukhas_id": os.getenv("LUKHAS_ID", "λ1234567890abcdef"),
            "lukhas_secret": os.getenv("LUKHAS_SECRET", "your-lukhas-secret"),
            "lukhas_endpoint": "https://api.lukhas.ai/auth/verify"
        }
    },
    # Additional security configuration
    "security": {
        "rate_limiting": {
            "requests_per_minute": 60,
            "burst_limit": 10
        },
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "ssl_verify": True,
        "allowed_response_codes": [200, 201, 202, 400, 401, 403, 422, 429, 500]
    },
    # Testing configuration
    "test_config": {
        "injection_vectors": ["prompt", "system", "user_input", "metadata"],
        "payload_categories": ["extraction", "manipulation", "bypass", "privilege_escalation"],
        "severity_threshold": "medium",  # "low", "medium", "high", "critical"
        "max_test_iterations": 100
    }
}

# Initialize the prompt injection tester with enhanced configuration
tester = PromptInjectionTester(
    authentication_handler=target["authentication"],
    security_config=target["security"],
    test_config=target["test_config"]
)

# Configure authentication based on the specified type
auth_type = target["authentication"]["type"]
if auth_type == "bearer_token":
    tester.set_bearer_token(target["authentication"]["credentials"]["token"])
elif auth_type == "api_key":
    tester.set_api_key(
        target["authentication"]["credentials"]["api_key"],
        header=target["authentication"]["credentials"]["api_key_header"]
    )
elif auth_type == "basic_auth":
    tester.set_basic_auth(
        target["authentication"]["credentials"]["username"],
        target["authentication"]["credentials"]["password"]
    )
elif auth_type == "oauth2":
    tester.set_oauth2(
        target["authentication"]["credentials"]["client_id"],
        target["authentication"]["credentials"]["client_secret"],
        target["authentication"]["credentials"]["token_url"]
    )
elif auth_type == "lukhas_id":
    tester.set_lukhas_auth(
        target["authentication"]["credentials"]["lukhas_id"],
        target["authentication"]["credentials"]["lukhas_secret"],
        target["authentication"]["credentials"]["lukhas_endpoint"]
    )

# Run comprehensive security tests
print("🔒 Starting Security Analysis...")
print(f"Target System: {target['system_id']}")
print(f"Endpoints: {', '.join(target['endpoints'])}")
print(f"Authentication: {auth_type}")
print("-" * 50)

try:
    # Execute the security test suite
    results = tester.run_comprehensive_test(
        endpoints=target["endpoints"],
        injection_vectors=target["test_config"]["injection_vectors"],
        payload_categories=target["test_config"]["payload_categories"],
        max_iterations=target["test_config"]["max_test_iterations"]
    )

    # Analyze and display results
    print("\n📊 Security Test Results:")
    print(f"Total Tests Executed: {results.get('total_tests', 0)}")
    print(f"Vulnerabilities Found: {results.get('vulnerabilities_count', 0)}")
    print(f"Critical Issues: {results.get('critical_count', 0)}")
    print(f"High Risk Issues: {results.get('high_count', 0)}")
    print(f"Medium Risk Issues: {results.get('medium_count', 0)}")
    print(f"Low Risk Issues: {results.get('low_count', 0)}")

    # Display detailed findings
    if results.get('vulnerabilities'):
        print("\n🚨 Vulnerability Details:")
        for vuln in results['vulnerabilities']:
            print(f"  • {vuln['type']} [{vuln['severity'].upper()}]")
            print(f"    Endpoint: {vuln['endpoint']}")
            print(f"    Vector: {vuln['injection_vector']}")
            print(f"    Impact: {vuln['description']}")
            print(f"    Recommendation: {vuln['mitigation']}")
            print()

    # Generate security score
    security_score = results.get('security_score', 0)
    score_rating = "EXCELLENT" if security_score >= 90 else \
                  "GOOD" if security_score >= 75 else \
                  "FAIR" if security_score >= 60 else \
                  "POOR" if security_score >= 40 else "CRITICAL"

    print(f"🛡️  Overall Security Score: {security_score}/100 ({score_rating})")

    # Export results
    if results.get('export_path'):
        print(f"📄 Detailed report saved to: {results['export_path']}")

except Exception as e:
    print(f"❌ Error during security testing: {e}")
    print("Check your configuration and network connectivity.")

""",
            "expected_output": """
Testing completed: 5 injection attempts
Vulnerabilities found: 2
- Basic instruction bypass (Severity: MEDIUM)
- Context manipulation (Severity: HIGH)
Security Score: 65/100
""",
            "validation_code": """
assert "endpoints" in target
assert len(target["endpoints"]) > 0
assert isinstance(tester, PromptInjectionTester)
""",
            "hints": [
                "Add 'authentication_required: True' to target configuration",
                "Use tester.test_target(target) to run the test",
                "Check result.vulnerabilities for found issues",
                "Print the security score from result.security_score",
            ],
        }

    async def _generate_api_exercise(self, difficulty_level: DifficultyLevel) -> dict[str, Any]:
        """Generate API exercise"""

        return {
            "content": """
**Exercise: API Integration**

Integrate with the LUKHAS  API to perform a compliance validation through the REST API.

**Your Task:**
Complete the API client configuration and make a successful compliance validation request.
""",
            "starter_code": """
from system.ent import APIClient

# TODO: Configure the API client
client = APIClient(
    # TODO: Add base URL
    # TODO: Add authentication
)

# TODO: Make a compliance validation request
# Use the compliance endpoint to validate a system

# TODO: Handle the response and print results
""",
            "expected_output": """
API Response: 200 OK
Compliance Status: compliant
Score: 87/100
Framework: EU AI Act
""",
            "validation_code": """
assert hasattr(client, 'base_url')
assert hasattr(client, 'api_key') or hasattr(client, 'token')
""",
            "hints": [
                "Use 'https://api.lukhas-.com' as base URL",
                "Add your API key for authentication",
                "Use client.compliance.validate() method",
                "Check response.status_code for success",
            ],
        }

    async def _generate_general_exercise(self, topic: str, difficulty_level: DifficultyLevel) -> dict[str, Any]:
        """Generate general exercise"""

        return {
            "content": f"""
**Exercise: Working with {topic}**

Complete the implementation to demonstrate understanding of {topic} concepts.

**Your Task:**
Follow the TODOs in the code to complete the implementation.
""",
            "starter_code": """
# TODO: Import the required module
from system ort ...

# TODO: Initialize the component
component = ...

# TODO: Configure the component
component.configure({
    # TODO: Add configuration options
})

# TODO: Use the component
result = component.process()

print(f"Result: {result}")
""",
            "expected_output": f"{topic} processing completed successfully",
            "validation_code": "assert result is not None",
            "hints": [
                f"Import the {topic} module from systemInitialize {topic}() class",
                "Add basic configuration options",
                "Call the process() method",
            ],
        }

    # Helper methods for tutorial generation
    async def _generate_learning_objectives(
        self, topic: str, tutorial_type: TutorialType, difficulty_level: DifficultyLevel
    ) -> list[str]:
        """Generate learning objectives for tutorial"""

        objectives = [
            f"Understand the core concepts of {topic}",
            f"Learn how to implement {topic} in practice",
            f"Apply {topic} knowledge to real-world scenarios",
        ]

        if tutorial_type == TutorialType.COMPLIANCE_TUTORIAL:
            objectives.extend(
                [
                    "Understand regulatory requirements and frameworks",
                    "Implement automated compliance validation",
                    "Generate compliance reports and documentation",
                ]
            )
        elif tutorial_type == TutorialType.SECURITY_TUTORIAL:
            objectives.extend(
                [
                    "Identify common AI security vulnerabilities",
                    "Implement security testing procedures",
                    "Develop incident response strategies",
                ]
            )
        elif tutorial_type == TutorialType.API_WALKTHROUGH:
            objectives.extend(
                [
                    "Master API authentication and authorization",
                    "Handle API errors and edge cases effectively",
                    "Implement efficient API integration patterns",
                ]
            )

        return objectives

    async def _generate_tutorial_description(self, topic: str, tutorial_type: TutorialType) -> str:
        """Generate tutorial description"""

        base_description = (
            f"This interactive tutorial will guide you through {topic} concepts and practical implementation."
        )

        type_specific = {
            TutorialType.QUICK_START: "Get up and running quickly with the essential knowledge you need.",
            TutorialType.COMPREHENSIVE: "A complete deep-dive covering all aspects from basics to advanced topics.",
            TutorialType.API_WALKTHROUGH: "Step-by-step guide to effectively use the API endpoints.",
            TutorialType.INTEGRATION_GUIDE: "Learn how to integrate with existing systems and workflows.",
            TutorialType.COMPLIANCE_TUTORIAL: "Understand and implement regulatory compliance requirements.",
            TutorialType.SECURITY_TUTORIAL: "Master security best practices and threat mitigation.",
        }

        return f"{base_description} {type_specific.get(tutorial_type, '')}"

    async def _generate_prerequisites(self, topic: str, difficulty_level: DifficultyLevel) -> list[str]:
        """Generate tutorial prerequisites"""

        prerequisites = ["Basic understanding of Python programming"]

        if difficulty_level in [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]:
            prerequisites.extend(["Familiarity with AI/ML concepts", "Experience with REST APIs"])

        if difficulty_level == DifficultyLevel.ADVANCED:
            prerequisites.extend(
                [
                    "Understanding of software architecture patterns",
                    "Experience with compliance frameworks",
                ]
            )

        return prerequisites

    async def _generate_assessment_criteria(self, learning_objectives: list[str]) -> dict[str, Any]:
        """Generate assessment criteria"""

        return {
            "completion_threshold": 80,  # Minimum percentage to pass
            "time_bonus": 10,  # Bonus points for completing quickly
            "hint_penalty": 5,  # Penalty per hint used
            "objectives_weight": {obj: 100 / len(learning_objectives) for obj in learning_objectives},
        }

    async def _generate_quiz_content(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate quiz content"""

        return f"""
**Quiz: {topic} Knowledge Check**

1. What is the primary purpose of {topic} in AI systems?
   a) Performance optimization
   b) Regulatory compliance
   c) User interface improvement
   d) Data storage

2. Which framework is most relevant for {topic}?
   a) React
   b) TensorFlow
   c) LUKHAS
   d) Django

3. What is a key benefit of implementing {topic}?
   a) Faster processing
   b) Better compliance
   c) Lower costs
   d) Easier deployment

**Answers:** 1-b, 2-c, 3-b
"""

    async def _generate_checkpoint_content(self, topic: str, previous_steps: list[TutorialStep]) -> str:
        """Generate checkpoint content"""

        completed_concepts = []
        for step in previous_steps:
            if step.step_type in [StepType.EXPLANATION, StepType.CODE_EXAMPLE]:
                completed_concepts.append(step.title)

        return f"""
**Checkpoint: Progress Review**

Great job! You've completed {len(previous_steps)} steps in this {topic} tutorial.

**What you've learned so far:**
{chr(10).join(f"✅ {concept}" for concept in completed_concepts[:5])}

**Key takeaways:**
- Understanding of {topic} fundamentals
- Practical implementation experience
- Real-world application scenarios

**Coming up next:**
- Advanced features and configuration
- Best practices and optimization
- Troubleshooting and problem-solving

Take a moment to review what you've learned before continuing!
"""

    async def _generate_troubleshooting_content(self, topic: str, difficulty_level: DifficultyLevel) -> str:
        """Generate troubleshooting content"""

        return f"""
**Troubleshooting Common {topic} Issues**

Here are some common issues you might encounter and how to resolve them:

**Issue 1: Authentication Errors**
- **Symptom:** 401 Unauthorized responses
- **Solution:** Check API key validity and format
- **Prevention:** Implement proper token refresh logic

**Issue 2: Configuration Problems**
- **Symptom:** Unexpected behavior or errors
- **Solution:** Validate configuration against schema
- **Prevention:** Use configuration validation tools

**Issue 3: Performance Issues**
- **Symptom:** Slow responses or timeouts
- **Solution:** Optimize queries and enable caching
- **Prevention:** Implement monitoring and alerting

**General Debugging Tips:**
1. Check logs for detailed error messages
2. Validate input data and parameters
3. Test with minimal examples first
4. Use debugging tools and verbose modes
5. Consult documentation and community forums

**Getting Help:**
- Check the documentation at docs.lukhas-.com
- Join the community forum
- Contact support for critical issues
"""


# Export main tutorial components
__all__ = [
    "DifficultyLevel",
    "InteractiveTutorial",
    "LearningStyle",
    "TutorialGenerator",
    "TutorialProgress",
    "TutorialStep",
    "TutorialType",
]
