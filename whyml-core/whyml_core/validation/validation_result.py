"""
ValidationResult class for WhyML Core validation results.

Provides a standardized structure for validation results including
validation status, errors, and warnings.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Represents the result of a validation operation.
    
    Attributes:
        is_valid (bool): Whether the validation passed
        errors (List[str]): List of validation errors
        warnings (List[str]): List of validation warnings
        context (Optional[dict]): Additional context information
    """
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    context: Optional[dict] = None
    
    def __post_init__(self):
        """Ensure errors and warnings are lists."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if not isinstance(self.errors, list):
            self.errors = [str(self.errors)]
        if not isinstance(self.warnings, list):
            self.warnings = [str(self.warnings)]
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0
    
    @property
    def error_count(self) -> int:
        """Get the number of validation errors."""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Get the number of validation warnings."""
        return len(self.warnings)
    
    def add_error(self, error: str) -> None:
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """
        Merge this validation result with another.
        
        Args:
            other: Another ValidationResult to merge
            
        Returns:
            A new ValidationResult with combined errors and warnings
        """
        merged_errors = self.errors + other.errors
        merged_warnings = self.warnings + other.warnings
        
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=merged_errors,
            warnings=merged_warnings,
            context={**(self.context or {}), **(other.context or {})}
        )
    
    def to_dict(self) -> dict:
        """Convert the validation result to a dictionary."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'context': self.context
        }
    
    def __str__(self) -> str:
        """String representation of the validation result."""
        if self.is_valid:
            status = "✅ VALID"
        else:
            status = "❌ INVALID"
            
        parts = [f"ValidationResult: {status}"]
        
        if self.has_errors:
            parts.append(f"Errors ({self.error_count}): {', '.join(self.errors)}")
            
        if self.has_warnings:
            parts.append(f"Warnings ({self.warning_count}): {', '.join(self.warnings)}")
            
        return " | ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed representation of the validation result."""
        return (f"ValidationResult(is_valid={self.is_valid}, "
                f"errors={self.errors}, warnings={self.warnings}, "
                f"context={self.context})")
