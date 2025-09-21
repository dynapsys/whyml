"""
WhyML Core Validation Exceptions - Validation-specific exception classes

Defines exceptions related to manifest validation, schema errors, and field validation.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import logging
from typing import List, Dict, Any, Optional
from .base_exceptions import WhyMLError

logger = logging.getLogger(__name__)


class ValidationError(WhyMLError):
    """Raised when manifest validation fails.
    
    This exception is raised when a manifest doesn't conform to the expected
    schema or contains invalid field values.
    """
    
    def __init__(self, message: str, errors: List[str] = None, warnings: List[str] = None):
        """Initialize validation error.
        
        Args:
            message: Human-readable error message
            errors: List of specific validation errors
            warnings: List of validation warnings
        """
        self.errors = errors or []
        self.warnings = warnings or []
        details = {
            'errors': self.errors,
            'warnings': self.warnings
        }
        super().__init__(message, details)


class SchemaError(WhyMLError):
    """Raised when schema loading or processing fails.
    
    This exception is raised when there are issues with the validation schema
    itself, such as malformed schema files or missing schema definitions.
    """
    
    def __init__(self, message: str, schema_path: Optional[str] = None):
        """Initialize schema error.
        
        Args:
            message: Human-readable error message
            schema_path: Path to the problematic schema file
        """
        details = {'schema_path': schema_path} if schema_path else {}
        super().__init__(message, details)


def handle_validation_errors(func):
    """Decorator for handling validation errors consistently.
    
    This decorator catches common validation exceptions and converts them
    to WhyML ValidationError instances with proper context.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, (ValidationError, SchemaError)):
                raise
            
            logger.error(f"Validation error in {func.__name__}: {e}")
            raise ValidationError(
                f"Validation failed in {func.__name__}: {str(e)}",
                errors=[str(e)]
            )
    
    return wrapper
