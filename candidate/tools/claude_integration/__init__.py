"""
🤖 Claude Integration Tools

This module contains utilities for integrating with Claude AI systems,
including context management, memory integration, and task extraction.

Components:
- save_claude_context.py: Context preservation for Claude conversations
- claude_memory_integration.py: Integration with LUKHAS memory systems
- claude_lukhas_integration.py: Journal and workspace integration
- claude_context_extractor.js: JavaScript-based context extraction
- extract_claude6_tasks.py: Task extraction for Claude Agent deployments

Part of the LUKHAS AI Trinity Framework ⚛️🧠🛡️
"""

__version__ = "1.0.0"
__author__ = "LUKHAS AI"

# Claude integration utilities
from .claude_lukhas_integration import *
from .claude_memory_integration import *
from .save_claude_context import *

__all__ = ["claude_lukhas_integration", "claude_memory_integration", "save_claude_context"]
