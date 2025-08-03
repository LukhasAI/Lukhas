"""
⚠️ Common Exceptions
===================
Standardized exceptions for LUKHAS modules.
"""

from typing import Optional, Dict, Any


class LukhasError(Exception):
    """Base exception for all LUKHAS errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details
        }


class GuardianRejectionError(LukhasError):
    """Raised when Guardian system rejects an operation"""
    
    def __init__(
        self,
        message: str,
        ethics_violation: Optional[str] = None,
        suggestion: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if ethics_violation:
            details['ethics_violation'] = ethics_violation
        if suggestion:
            details['suggestion'] = suggestion
            
        super().__init__(
            message=message,
            error_code='GUARDIAN_REJECTION',
            details=details
        )


class MemoryDriftError(LukhasError):
    """Raised when memory drift exceeds acceptable threshold"""
    
    def __init__(
        self,
        message: str,
        memory_id: str,
        drift_level: float,
        threshold: float,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'memory_id': memory_id,
            'drift_level': drift_level,
            'threshold': threshold,
            'exceeded_by': drift_level - threshold
        })
        
        super().__init__(
            message=message,
            error_code='MEMORY_DRIFT_EXCESSIVE',
            details=details
        )


class ModuleTimeoutError(LukhasError):
    """Raised when a module operation times out"""
    
    def __init__(
        self,
        message: str,
        module_name: Optional[str] = None,
        operation: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if module_name:
            details['module'] = module_name
        if operation:
            details['operation'] = operation
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
            
        super().__init__(
            message=message,
            error_code='MODULE_TIMEOUT',
            details=details
        )


class ModuleNotFoundError(LukhasError):
    """Raised when a required module is not available"""
    
    def __init__(self, module_name: str, **kwargs):
        super().__init__(
            message=f"Module '{module_name}' not found or not initialized",
            error_code='MODULE_NOT_FOUND',
            details={'module_name': module_name, **kwargs.get('details', {})}
        )


class ConfigurationError(LukhasError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        if config_file:
            details['config_file'] = config_file
            
        super().__init__(
            message=message,
            error_code='CONFIGURATION_ERROR',
            details=details
        )


class AuthenticationError(LukhasError):
    """Raised when authentication fails"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        auth_method: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if auth_method:
            details['auth_method'] = auth_method
            
        super().__init__(
            message=message,
            error_code='AUTHENTICATION_ERROR',
            details=details
        )


class AuthorizationError(LukhasError):
    """Raised when authorization fails"""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_tier: Optional[int] = None,
        current_tier: Optional[int] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if required_tier is not None:
            details['required_tier'] = required_tier
        if current_tier is not None:
            details['current_tier'] = current_tier
        if required_permission:
            details['required_permission'] = required_permission
            
        super().__init__(
            message=message,
            error_code='AUTHORIZATION_ERROR',
            details=details
        )


class ValidationError(LukhasError):
    """Raised when input validation fails"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        constraint: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        if constraint:
            details['constraint'] = constraint
            
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details
        )


class GLYPHError(LukhasError):
    """Raised when GLYPH token operations fail"""
    
    def __init__(
        self,
        message: str,
        glyph_id: Optional[str] = None,
        glyph_symbol: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if glyph_id:
            details['glyph_id'] = glyph_id
        if glyph_symbol:
            details['glyph_symbol'] = glyph_symbol
            
        super().__init__(
            message=message,
            error_code='GLYPH_ERROR',
            details=details
        )


class CircuitBreakerError(LukhasError):
    """Raised when circuit breaker is open"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        failure_count: int,
        threshold: int,
        reset_timeout: float,
        **kwargs
    ):
        details = {
            'service_name': service_name,
            'failure_count': failure_count,
            'threshold': threshold,
            'reset_timeout_seconds': reset_timeout,
            **kwargs.get('details', {})
        }
        
        super().__init__(
            message=message,
            error_code='CIRCUIT_BREAKER_OPEN',
            details=details
        )


class ResourceExhaustedError(LukhasError):
    """Raised when system resources are exhausted"""
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        current_usage: Optional[float] = None,
        limit: Optional[float] = None,
        **kwargs
    ):
        details = {
            'resource_type': resource_type,
            **kwargs.get('details', {})
        }
        
        if current_usage is not None:
            details['current_usage'] = current_usage
        if limit is not None:
            details['limit'] = limit
            details['usage_percentage'] = (current_usage / limit * 100) if limit > 0 else 100
            
        super().__init__(
            message=message,
            error_code='RESOURCE_EXHAUSTED',
            details=details
        )


# Convenience functions for raising common errors
def raise_guardian_rejection(
    message: str,
    ethics_violation: Optional[str] = None,
    suggestion: Optional[str] = None
) -> None:
    """Raise a Guardian rejection error"""
    raise GuardianRejectionError(
        message=message,
        ethics_violation=ethics_violation,
        suggestion=suggestion
    )


def raise_if_drift_excessive(
    memory_id: str,
    drift_level: float,
    threshold: float = 0.3
) -> None:
    """Raise error if memory drift exceeds threshold"""
    if drift_level > threshold:
        raise MemoryDriftError(
            message=f"Memory drift {drift_level:.3f} exceeds threshold {threshold}",
            memory_id=memory_id,
            drift_level=drift_level,
            threshold=threshold
        )