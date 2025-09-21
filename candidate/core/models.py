"""
LUKHAS Core Models Module

This module provides the base model definitions used throughout the LUKHAS system.
Re-exports Pydantic BaseModel and provides LUKHAS-specific base classes.

This file was created to resolve import issues in auto-generated consciousness
reasoning modules that expect to import BaseModel from candidate.core.models.
"""

import logging
from typing import Any, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field

logger = logging.getLogger(__name__)


class BaseModel(PydanticBaseModel):
    """
    LUKHAS Base Model extending Pydantic BaseModel with LUKHAS-specific features.
    
    This serves as the foundation for all LUKHAS data models, providing:
    - Constellation Framework awareness
    - Identity integration hooks
    - Consciousness-aware serialization
    """
    
    model_config = ConfigDict(
        # Enable validation on assignment
        validate_assignment=True,
        # Use enum values for serialization
        use_enum_values=True,
        # Preserve field order
        str_strip_whitespace=True,
        # Additional LUKHAS-specific config
        extra='forbid'
    )
    
    # Optional LUKHAS-specific metadata
    lambda_id: Optional[str] = Field(None, description="Lambda ID for identity tracking")
    tier: Optional[int] = Field(None, ge=0, le=5, description="LUKHAS tier (0-5)")
    constellation_aspect: Optional[str] = Field(None, description="Constellation Framework aspect")
    
    def to_lukhas_dict(self) -> dict[str, Any]:
        """Convert to dictionary with LUKHAS-specific formatting."""
        data = self.model_dump()
        
        # Add LUKHAS metadata if available
        if hasattr(self, '_lukhas_metadata'):
            data['_lukhas'] = self._lukhas_metadata
            
        return data
    
    def __init_subclass__(cls, **kwargs):
        """Initialize subclasses with LUKHAS awareness."""
        super().__init_subclass__(**kwargs)
        
        # Log model registration for Constellation Framework
        logger.debug(
            f"ΛTRACE: Registering LUKHAS model class: {cls.__name__}",
            extra={
                'model_class': cls.__name__,
                'module': cls.__module__,
                'constellation_aware': True
            }
        )


# Re-export for compatibility with auto-generated code
__all__ = ['BaseModel', 'PydanticBaseModel']

logger.info("ΛTRACE: LUKHAS Core Models module initialized")
