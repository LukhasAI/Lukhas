"""
🔤 Common GLYPH Utilities
========================
Centralized GLYPH token handling for all modules.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from .exceptions import GLYPHError, ValidationError


class GLYPHSymbol(Enum):
    """Standard GLYPH symbols used across LUKHAS"""

    # Core actions
    TRUST = "TRUST"
    LEARN = "LEARN"
    ADAPT = "ADAPT"
    CREATE = "CREATE"
    PROTECT = "PROTECT"
    REMEMBER = "REMEMBER"
    FORGET = "FORGET"
    REFLECT = "REFLECT"
    CONNECT = "CONNECT"
    DREAM = "DREAM"

    # Emotional
    JOY = "JOY"
    FEAR = "FEAR"
    ANGER = "ANGER"
    SADNESS = "SADNESS"
    SURPRISE = "SURPRISE"
    DISGUST = "DISGUST"

    # System
    INIT = "INIT"
    SYNC = "SYNC"
    ERROR = "ERROR"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    QUERY = "QUERY"
    ACKNOWLEDGE = "ACKNOWLEDGE"

    # Guardian
    VALIDATE = "VALIDATE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    AUDIT = "AUDIT"

    # Memory
    STORE = "STORE"
    RECALL = "RECALL"
    DRIFT = "DRIFT"
    REPAIR = "REPAIR"


class GLYPHPriority(Enum):
    """GLYPH message priorities"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class GLYPHContext:
    """Context information for GLYPH tokens"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    interaction_id: Optional[str] = None
    module_trace: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GLYPHContext":
        """Create from dictionary"""
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class GLYPHToken:
    """
    Standard GLYPH token for inter-module communication.

    Attributes:
        glyph_id: Unique identifier
        symbol: GLYPH symbol (action/state)
        source: Source module
        target: Target module
        payload: Data payload
        context: Context information
        priority: Message priority
        metadata: Additional metadata
    """

    glyph_id: str = field(default_factory=lambda: f"glyph_{uuid.uuid4().hex}")
    symbol: Union[str, GLYPHSymbol] = GLYPHSymbol.SYNC
    source: str = "unknown"
    target: str = "unknown"
    payload: dict[str, Any] = field(default_factory=dict)
    context: GLYPHContext = field(default_factory=GLYPHContext)
    priority: Union[str, GLYPHPriority] = GLYPHPriority.NORMAL
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize token"""
        # Convert string symbols to enum if possible
        if isinstance(self.symbol, str):
            from contextlib import suppress

            with suppress(ValueError):
                self.symbol = GLYPHSymbol(self.symbol)

        # Convert string priority to enum
        if isinstance(self.priority, str):
            from contextlib import suppress

            with suppress(ValueError):
                self.priority = GLYPHPriority(self.priority)
            if isinstance(self.priority, str):
                self.priority = GLYPHPriority.NORMAL

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "glyph_id": self.glyph_id,
            "symbol": (self.symbol.value if isinstance(self.symbol, GLYPHSymbol) else self.symbol),
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "context": self.context.to_dict(),
            "priority": (
                self.priority.value if isinstance(self.priority, GLYPHPriority) else self.priority
            ),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GLYPHToken":
        """Create from dictionary"""
        # Handle context
        if "context" in data and isinstance(data["context"], dict):
            data["context"] = GLYPHContext.from_dict(data["context"])
        else:
            data["context"] = GLYPHContext()

        return cls(**data)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "GLYPHToken":
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_to_trace(self, module: str) -> None:
        """Add module to processing trace"""
        self.context.module_trace.append(module)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)


# Convenience functions


def create_glyph(
    symbol: Union[str, GLYPHSymbol],
    source: str,
    target: str,
    payload: Optional[dict[str, Any]] = None,
    context: Optional[Union[dict[str, Any], GLYPHContext]] = None,
    priority: Union[str, GLYPHPriority] = GLYPHPriority.NORMAL,
    **metadata,
) -> GLYPHToken:
    """
    Create a new GLYPH token.

    Args:
        symbol: GLYPH symbol
        source: Source module name
        target: Target module name
        payload: Data payload
        context: Context information
        priority: Message priority
        **metadata: Additional metadata

    Returns:
        New GLYPH token
    """
    # Handle context
    if context is None:
        ctx = GLYPHContext()
    elif isinstance(context, dict):
        ctx = GLYPHContext.from_dict(context)
    else:
        ctx = context

    return GLYPHToken(
        symbol=symbol,
        source=source,
        target=target,
        payload=payload or {},
        context=ctx,
        priority=priority,
        metadata=metadata,
    )


def parse_glyph(data: Union[str, dict[str, Any]]) -> GLYPHToken:
    """
    Parse GLYPH token from json_string or dictionary.

    Args:
        data: JSON string or dictionary

    Returns:
        Parsed GLYPH token

    Raises:
        GLYPHError: If parsing fails
    """
    try:
        if isinstance(data, str):
            return GLYPHToken.from_json(data)
        elif isinstance(data, dict):
            return GLYPHToken.from_dict(data)
        else:
            raise ValueError(f"Invalid data type: {type(data)}")
    except Exception as e:
        raise GLYPHError(
            message=f"Failed to parse GLYPH token: {e!s}",
            details={"data_type": type(data).__name__},
        ) from e


def validate_glyph(token: GLYPHToken) -> bool:
    """
    Validate GLYPH token structure and content.

    Args:
        token: GLYPH token to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Check required fields
    if not token.glyph_id:
        raise ValidationError("GLYPH token missing ID", field="glyph_id")

    if not token.source:
        raise ValidationError("GLYPH token missing source", field="source")

    if not token.target:
        raise ValidationError("GLYPH token missing target", field="target")

    # Validate symbol
    if not token.symbol:
        raise ValidationError("GLYPH token missing symbol", field="symbol")

    # Validate context
    if not isinstance(token.context, GLYPHContext):
        raise ValidationError(
            "Invalid context type",
            field="context",
            value=type(token.context).__name__,
        )

    return True


def create_response_glyph(
    request: GLYPHToken,
    symbol: Union[str, GLYPHSymbol],
    payload: Optional[dict[str, Any]] = None,
    **metadata,
) -> GLYPHToken:
    """
    Create a response GLYPH token from a request.

    Args:
        request: Original request token
        symbol: Response symbol
        payload: Response payload
        **metadata: Additional metadata

    Returns:
        Response GLYPH token
    """
    # Swap source and target
    response = create_glyph(
        symbol=symbol,
        source=request.target,
        target=request.source,
        payload=payload,
        context=request.context,
        priority=request.priority,
        **metadata,
    )

    # Link to original request
    response.set_metadata("request_id", request.glyph_id)

    # Copy trace
    response.context.module_trace = request.context.module_trace.copy()
    response.add_to_trace(request.target)

    return response


def create_error_glyph(
    request: GLYPHToken,
    error_message: str,
    error_code: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> GLYPHToken:
    """
    Create an error GLYPH token.

    Args:
        request: Original request token
        error_message: Error message
        error_code: Error code
        details: Error details

    Returns:
        Error GLYPH token
    """
    return create_response_glyph(
        request=request,
        symbol=GLYPHSymbol.ERROR,
        payload={
            "error": error_code or "UNKNOWN_ERROR",
            "message": error_message,
            "details": details or {},
        },
        error=True,
    )


# GLYPH routing utilities


class GLYPHRouter:
    """Simple GLYPH token router"""

    def __init__(self):
        self.routes: dict[str, list[str]] = {}
        self.handlers: dict[str, Any] = {}

    def register_route(self, source: str, targets: list[str]) -> None:
        """Register routing rule"""
        self.routes[source] = targets

    def register_handler(self, module: str, handler: Any) -> None:
        """Register module handler"""
        self.handlers[module] = handler

    async def route(self, token: GLYPHToken) -> list[Any]:
        """Route token to appropriate handlers"""
        results = []

        # Get targets
        targets = self.routes.get(token.source, [token.target])

        # Send to each target
        for target in targets:
            if target in self.handlers:
                handler = self.handlers[target]
                if hasattr(handler, "handle_glyph"):
                    result = await handler.handle_glyph(token)
                    results.append(result)

        return results
