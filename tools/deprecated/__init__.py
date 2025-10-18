"""
LUKHAS Analysis Tools Module
Provides decision auditing and analysis capabilities
"""

# Use absolute imports to avoid relative import issues
try:
    from tools.deprecated.audit_decision_embedding_engine import DecisionAuditDecorator, DecisionAuditEngine

    __all__ = ["DecisionAuditDecorator", "DecisionAuditEngine"]
except ImportError:
    import warnings

    warnings.warn("Could not import deprecated analysis tools", ImportWarning)
    __all__ = []
