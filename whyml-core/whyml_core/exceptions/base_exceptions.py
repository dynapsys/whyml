"""
WhyML Core Base Exceptions - Base exception classes for WhyML ecosystem

Defines the fundamental exception hierarchy used across all WhyML packages.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""


class WhyMLError(Exception):
    """Base exception for all WhyML-related errors.
    
    This is the root exception that all other WhyML exceptions inherit from.
    It provides a consistent error handling interface across the entire ecosystem.
    """
    
    def __init__(self, message: str, details: dict = None, cause: Exception = None):
        """Initialize WhyML error.
        
        Args:
            message: Human-readable error message
            details: Additional error context and information
            cause: Underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        result = self.message
        if self.details:
            result += f" - Details: {self.details}"
        if self.cause:
            result += f" - Caused by: {self.cause}"
        return result
    
    def to_dict(self) -> dict:
        """Convert error to dictionary representation.
        
        Returns:
            Dictionary containing error information
        """
        return {
            'type': self.__class__.__name__,
            'message': self.message,
            'details': self.details,
            'cause': str(self.cause) if self.cause else None
        }
