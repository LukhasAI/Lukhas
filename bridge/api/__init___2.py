"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


AI Documentation Engine
=====================

Advanced AI-powered documentation generation, analysis, and optimization system
for the LUKHAS PWM ecosystem.

This package provides:
- Comprehensive ecosystem documentation generation
- Specialized API documentation with multiple output formats
- Interactive tutorial creation and management
- Documentation analytics and quality assessment
- Content gap analysis and optimization recommendations
- User behavior pattern detection and insights

Key Components:
- EcosystemDocumentationGenerator: Comprehensive code analysis and documentation
- APIDocumentationGenerator: Specialized API documentation with OpenAPI, Postman support
- TutorialGenerator: Interactive, adaptive tutorial creation
- DocumentationAnalytics: Quality assessment and usage analytics
"""

from .ecosystem_documentation_generator import (
    DocumentationGenerator,
    CodeAnalyzer,
    DocumentationRequest
)

from .api_documentation_generator import (
    APIDocumentationGenerator,
    APIEndpoint,
    APIParameter,
    APIResponse,
    APIExample,
    AuthenticationMethod,
    APIDocumentationConfig,
    OutputFormat
)

from .interactive_tutorial_generator import (
    TutorialGenerator,
    InteractiveTutorial,
    TutorialStep,
    TutorialProgress,
    TutorialType,
    LearningStyle,
    DifficultyLevel,
    StepType
)

from .documentation_analytics import (
    DocumentationAnalytics,
    AnalyticsReport,
    QualityScore,
    UsageMetrics,
    ContentGap,
    UserBehaviorPattern,
    AnalyticsType,
    QualityMetric,
    ContentType
)

__all__ = [
    # Ecosystem Documentation
    'DocumentationGenerator',
    'CodeAnalyzer',
    'DocumentationRequest',
    
    # API Documentation
    'APIDocumentationGenerator',
    'APIEndpoint',
    'APIParameter',
    'APIResponse',
    'APIExample',
    'AuthenticationMethod',
    'APIDocumentationConfig',
    'OutputFormat',
    
    # Interactive Tutorials
    'TutorialGenerator',
    'InteractiveTutorial',
    'TutorialStep',
    'TutorialProgress',
    'TutorialType',
    'LearningStyle',
    'DifficultyLevel',
    'StepType',
    
    # Documentation Analytics
    'DocumentationAnalytics',
    'AnalyticsReport',
    'QualityScore',
    'UsageMetrics',
    'ContentGap',
    'UserBehaviorPattern',
    'AnalyticsType',
    'QualityMetric',
    'ContentType'
]

__version__ = "1.0.0"
__author__ = "LUKHAS PWM Development Team"
__description__ = "AI-powered documentation generation and analytics system"

# Configuration constants
DEFAULT_CONFIG = {
    "ai_documentation_engine": {
        "ecosystem_documentation": {
            "max_file_size": 1024 * 1024,  # 1MB
            "supported_extensions": [".py", ".js", ".ts", ".md", ".yaml", ".json"],
            "analysis_depth": "comprehensive",
            "include_dependencies": True,
            "generate_diagrams": True
        },
        "api_documentation": {
            "auto_detect_frameworks": True,
            "generate_postman_collections": True,
            "include_examples": True,
            "validate_schemas": True,
            "output_formats": ["markdown", "html", "openapi", "postman"]
        },
        "tutorial_generation": {
            "adaptive_difficulty": True,
            "interactive_mode": True,
            "include_live_validation": True,
            "support_multiple_languages": True,
            "track_progress": True
        },
        "analytics": {
            "real_time_monitoring": True,
            "quality_threshold": 75,
            "accessibility_compliance": "WCAG 2.1 AA",
            "performance_budget": {
                "load_time": 3.0,
                "mobile_score": 80,
                "accessibility_score": 90
            }
        }
    }
}

def get_config(section: str = None) -> dict:
    """Get configuration for AI documentation engine
    
    Args:
        section: Specific configuration section to retrieve
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG["ai_documentation_engine"]
    
    if section:
        return config.get(section, {})
    
    return config

def validate_config(config: dict) -> bool:
    """Validate configuration dictionary
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_sections = ["ecosystem_documentation", "api_documentation", 
                        "tutorial_generation", "analytics"]
    
    for section in required_sections:
        if section not in config:
            return False
    
    return True

# Quick access functions for common operations
async def generate_ecosystem_docs(workspace_path: str, 
                                output_path: str = None,
                                format: str = "markdown") -> str:
    """Quick function to generate ecosystem documentation
    
    Args:
        workspace_path: Path to the workspace to document
        output_path: Optional output path (defaults to workspace/docs)
        format: Output format (markdown, html, json)
        
    Returns:
        Path to generated documentation
    """
    generator = DocumentationGenerator()
    
    # Generate comprehensive documentation
    documentation = await generator.generate_comprehensive_documentation(
        workspace_path=workspace_path
    )
    
    # Export documentation
    export_path = await generator.export_documentation(
        documentation=documentation,
        output_path=output_path,
        format=format
    )
    
    return export_path

async def generate_api_docs(api_path: str,
                          output_formats: list = None,
                          include_examples: bool = True) -> dict:
    """Quick function to generate API documentation
    
    Args:
        api_path: Path to API code or configuration
        output_formats: List of output formats
        include_examples: Whether to include examples
        
    Returns:
        Dictionary of generated files by format
    """
    if output_formats is None:
        output_formats = ["markdown", "openapi", "postman"]
    
    generator = APIDocumentationGenerator()
    
    # Discover and analyze APIs
    apis = await generator.discover_apis(api_path)
    
    generated_files = {}
    for api in apis:
        # Generate documentation in all requested formats
        for output_format in output_formats:
            file_path = await generator.generate_documentation(
                api=api,
                output_format=OutputFormat(output_format),
                include_examples=include_examples
            )
            
            generated_files[output_format] = file_path
    
    return generated_files

async def create_tutorial(topic: str,
                        difficulty: str = "intermediate",
                        tutorial_type: str = "comprehensive") -> InteractiveTutorial:
    """Quick function to create an interactive tutorial
    
    Args:
        topic: Tutorial topic
        difficulty: Difficulty level (beginner, intermediate, advanced)
        tutorial_type: Type of tutorial
        
    Returns:
        Generated interactive tutorial
    """
    generator = TutorialGenerator()
    
    tutorial = await generator.generate_tutorial(
        topic=topic,
        tutorial_type=TutorialType(tutorial_type),
        difficulty_level=DifficultyLevel(difficulty)
    )
    
    return tutorial

async def analyze_documentation(content_paths: list = None,
                              analytics_type: str = "quality_analysis") -> AnalyticsReport:
    """Quick function to analyze documentation
    
    Args:
        content_paths: List of content paths to analyze
        analytics_type: Type of analytics to perform
        
    Returns:
        Analytics report
    """
    analytics = DocumentationAnalytics()
    
    report = await analytics.generate_analytics_report(
        analytics_type=AnalyticsType(analytics_type),
        content_paths=content_paths
    )
    
    return report

# Utility functions
def get_supported_formats() -> dict:
    """Get supported formats for different generators
    
    Returns:
        Dictionary of supported formats by component
    """
    return {
        "ecosystem_documentation": ["markdown", "html", "json", "pdf"],
        "api_documentation": ["markdown", "html", "openapi", "postman", "json"],
        "tutorials": ["markdown", "html", "jupyter", "interactive"],
        "analytics": ["json", "html", "csv", "pdf"]
    }

def get_version_info() -> dict:
    """Get version and component information
    
    Returns:
        Version information dictionary
    """
    return {
        "version": __version__,
        "components": {
            "ecosystem_documentation_generator": "1.0.0",
            "api_documentation_generator": "1.0.0", 
            "interactive_tutorial_generator": "1.0.0",
            "documentation_analytics": "1.0.0"
        },
        "features": {
            "ai_powered_analysis": True,
            "multi_format_output": True,
            "interactive_tutorials": True,
            "real_time_analytics": True,
            "accessibility_compliance": True,
            "integration_support": True
        }
    }

# Module initialization
def initialize_ai_documentation_engine(config: dict = None) -> bool:
    """Initialize the AI documentation engine
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        True if initialization successful
    """
    if config is None:
        config = DEFAULT_CONFIG["ai_documentation_engine"]
    
    # Validate configuration
    if not validate_config(config):
        raise ValueError("Invalid configuration provided")
    
    # Initialize components
    print("🤖 Initializing AI Documentation Engine...")
    print(f"   📚 Ecosystem Documentation Generator: Ready")
    print(f"   🔌 API Documentation Generator: Ready")
    print(f"   🎓 Interactive Tutorial Generator: Ready")
    print(f"   📊 Documentation Analytics: Ready")
    print("   ✅ AI Documentation Engine initialized successfully")
    
    return True

# Auto-initialize when imported
try:
    initialize_ai_documentation_engine()
except Exception as e:
    print(f"⚠️ Warning: AI Documentation Engine initialization failed: {e}")

# Module metadata
__package_name__ = "ai_documentation_engine"
__dependencies__ = [
    "asyncio",
    "pathlib", 
    "dataclasses",
    "typing",
    "json",
    "yaml",
    "markdown",
    "jinja2"
]

__optional_dependencies__ = [
    "openai",  # For AI-powered content generation
    "tiktoken",  # For token counting
    "pygments",  # For syntax highlighting
    "plantuml",  # For diagram generation
    "matplotlib",  # For analytics visualizations
    "pandas"  # For data analysis
]
