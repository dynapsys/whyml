"""
WhyML Exception Classes

Custom exceptions for the WhyML package providing detailed error information
for different types of failures in manifest processing and conversion.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, List, Optional, Union


class WhyMLError(Exception):
    """Base exception class for all WhyML-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ManifestError(WhyMLError):
    """Exception raised for manifest-related errors."""
    
    def __init__(self, message: str, manifest_path: Optional[str] = None, 
                 line_number: Optional[int] = None, **kwargs):
        details = kwargs
        if manifest_path:
            details['manifest_path'] = manifest_path
        if line_number:
            details['line_number'] = line_number
        super().__init__(message, details)


class ValidationError(WhyMLError):
    """Exception raised when manifest validation fails."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None, 
                 warnings: Optional[List[str]] = None, **kwargs):
        details = kwargs
        if errors:
            details['errors'] = errors
        if warnings:
            details['warnings'] = warnings
        super().__init__(message, details)


class ConversionError(WhyMLError):
    """Exception raised during format conversion operations."""
    
    def __init__(self, message: str, source_format: Optional[str] = None,
                 target_format: Optional[str] = None, **kwargs):
        details = kwargs
        if source_format:
            details['source_format'] = source_format
        if target_format:
            details['target_format'] = target_format
        super().__init__(message, details)


class LoaderError(WhyMLError):
    """Exception raised during manifest loading operations."""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 dependency_chain: Optional[List[str]] = None, **kwargs):
        details = kwargs
        if url:
            details['url'] = url
        if dependency_chain:
            details['dependency_chain'] = dependency_chain
        super().__init__(message, details)


class TemplateError(WhyMLError):
    """Exception raised during template processing operations."""
    
    def __init__(self, message: str, template_name: Optional[str] = None,
                 template_path: Optional[str] = None, **kwargs):
        details = kwargs
        if template_name:
            details['template_name'] = template_name
        if template_path:
            details['template_path'] = template_path
        super().__init__(message, details)


class DependencyError(WhyMLError):
    """Exception raised during dependency resolution."""
    
    def __init__(self, message: str, missing_dependencies: Optional[List[str]] = None,
                 circular_dependencies: Optional[List[str]] = None, **kwargs):
        details = kwargs
        if missing_dependencies:
            details['missing_dependencies'] = missing_dependencies
        if circular_dependencies:
            details['circular_dependencies'] = circular_dependencies
        super().__init__(message, details)


class SchemaError(WhyMLError):
    """Exception raised when manifest schema validation fails."""
    
    def __init__(self, message: str, schema_violations: Optional[List[str]] = None,
                 schema_path: Optional[str] = None, **kwargs):
        details = kwargs
        if schema_violations:
            details['schema_violations'] = schema_violations
        if schema_path:
            details['schema_path'] = schema_path
        super().__init__(message, details)


class CacheError(WhyMLError):
    """Exception raised during caching operations."""
    
    def __init__(self, message: str, cache_key: Optional[str] = None,
                 cache_operation: Optional[str] = None, **kwargs):
        details = kwargs
        if cache_key:
            details['cache_key'] = cache_key
        if cache_operation:
            details['cache_operation'] = cache_operation
        super().__init__(message, details)


class NetworkError(WhyMLError):
    """Exception raised during network operations (URL scraping, etc.)."""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 status_code: Optional[int] = None, **kwargs):
        details = kwargs
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        super().__init__(message, details)


class ConfigurationError(WhyMLError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, **kwargs):
        details = kwargs
        if config_key:
            details['config_key'] = config_key
        if config_file:
            details['config_file'] = config_file
        super().__init__(message, details)


# Exception utilities
def handle_yaml_error(yaml_error: Exception, manifest_path: str) -> ManifestError:
    """Convert PyYAML errors to ManifestError with better context."""
    if hasattr(yaml_error, 'problem_mark'):
        line_number = yaml_error.problem_mark.line + 1
        return ManifestError(
            f"YAML parsing error: {str(yaml_error)}",
            manifest_path=manifest_path,
            line_number=line_number
        )
    return ManifestError(
        f"YAML parsing error: {str(yaml_error)}",
        manifest_path=manifest_path
    )


def handle_validation_errors(errors: List[str], warnings: List[str] = None) -> ValidationError:
    """Create a comprehensive validation error from multiple issues."""
    error_count = len(errors)
    warning_count = len(warnings or [])
    
    if error_count == 1:
        message = f"Validation failed: {errors[0]}"
    else:
        message = f"Validation failed with {error_count} errors"
    
    if warning_count:
        message += f" and {warning_count} warnings"
    
    return ValidationError(message, errors=errors, warnings=warnings)


def format_error_details(error: WhyMLError) -> str:
    """Format error details for user-friendly display."""
    lines = [f"Error: {error.message}"]
    
    if hasattr(error, 'details') and error.details:
        lines.append("Details:")
        for key, value in error.details.items():
            if isinstance(value, list):
                lines.append(f"  {key}:")
                for item in value:
                    lines.append(f"    - {item}")
            else:
                lines.append(f"  {key}: {value}")
    
    return "\n".join(lines)


# Aliases for backward compatibility and test imports
ManifestError = LoaderError  # Alias for test compatibility
ManifestLoadingError = LoaderError  # Alias for test compatibility
ManifestProcessingError = WhyMLError  # Alias for test compatibility
TemplateInheritanceError = TemplateError  # Alias for test compatibility
DependencyResolutionError = DependencyError  # Alias for test compatibility
