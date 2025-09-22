"""
WhyML Core Processing Exceptions - Processing-specific exception classes

Defines exceptions related to template processing, manifest loading, and conversions.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Optional
from .base_exceptions import WhyMLError


class TemplateError(WhyMLError):
    """Raised when template processing fails.
    
    This exception is raised when there are issues with Jinja2 template
    rendering, variable substitution, or template syntax errors.
    """
    
    def __init__(self, message: str, template_name: Optional[str] = None, 
                 line_number: Optional[int] = None):
        """Initialize template error.
        
        Args:
            message: Human-readable error message
            template_name: Name of the problematic template
            line_number: Line number where error occurred
        """
        details = {}
        if template_name:
            details['template_name'] = template_name
        if line_number:
            details['line_number'] = line_number
        
        super().__init__(message, details)


class TemplateInheritanceError(WhyMLError):
    """Raised when template inheritance processing fails.
    
    This exception is raised for issues with template inheritance,
    circular dependencies, or missing parent templates.
    """
    
    def __init__(self, message: str, template_chain: Optional[list] = None):
        """Initialize template inheritance error.
        
        Args:
            message: Human-readable error message
            template_chain: Chain of template inheritance that caused the error
        """
        details = {'template_chain': template_chain} if template_chain else {}
        super().__init__(message, details)


class ManifestError(WhyMLError):
    """Raised when manifest loading or processing fails.
    
    This exception is raised for issues with manifest files,
    YAML parsing, or manifest structure problems.
    """
    
    def __init__(self, message: str, manifest_path: Optional[str] = None):
        """Initialize manifest error.
        
        Args:
            message: Human-readable error message
            manifest_path: Path to the problematic manifest file
        """
        details = {'manifest_path': manifest_path} if manifest_path else {}
        super().__init__(message, details)


class NetworkError(WhyMLError):
    """Raised when network operations fail.
    
    This exception is raised for HTTP request failures, timeouts,
    connection errors, or other network-related issues.
    """
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 status_code: Optional[int] = None, details: Optional[dict] = None):
        """Initialize network error.
        
        Args:
            message: Human-readable error message
            url: URL that caused the error
            status_code: HTTP status code if available
            details: Additional error details
        """
        error_details = details or {}
        if url:
            error_details['url'] = url
        if status_code:
            error_details['status_code'] = status_code
        
        super().__init__(message, error_details)


class ProcessingError(WhyMLError):
    """Raised when general processing operations fail.
    
    This exception is raised for issues with data processing, YAML operations,
    or other general processing tasks.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize processing error.
        
        Args:
            message: Human-readable error message
            details: Additional error details
        """
        super().__init__(message, details or {})


class LoaderError(WhyMLError):
    """Raised when loading operations fail.
    
    This exception is raised for issues with loading manifests, files,
    or other loading-related operations.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        """Initialize loader error.
        
        Args:
            message: Human-readable error message
            file_path: Path to the file that failed to load
        """
        details = {'file_path': file_path} if file_path else {}
        super().__init__(message, details)


class ConversionError(WhyMLError):
    """Raised when format conversion fails.
    
    This exception is raised when converting manifests to output formats
    like HTML, React, Vue, or PHP fails.
    """
    
    def __init__(self, message: str, source_format: Optional[str] = None,
                 target_format: Optional[str] = None):
        """Initialize conversion error.
        
        Args:
            message: Human-readable error message
            source_format: Source format being converted from
            target_format: Target format being converted to
        """
        details = {}
        if source_format:
            details['source_format'] = source_format
        if target_format:
            details['target_format'] = target_format
        
        super().__init__(message, details)


class ManifestLoadingError(LoaderError):
    """Raised when manifest loading specifically fails.
    
    This is an alias for LoaderError with specific context for manifest loading.
    """
    pass


class ManifestProcessingError(ProcessingError):
    """Raised when manifest processing specifically fails.
    
    This is an alias for ProcessingError with specific context for manifest processing.
    """
    pass


class DependencyResolutionError(WhyMLError):
    """Raised when dependency resolution fails.
    
    This exception is raised when there are issues resolving manifest dependencies,
    circular dependencies, or missing dependencies.
    """
    
    def __init__(self, message: str, dependency_path: Optional[str] = None,
                 dependency_chain: Optional[list] = None):
        """Initialize dependency resolution error.
        
        Args:
            message: Human-readable error message
            dependency_path: Path to the problematic dependency
            dependency_chain: Chain of dependencies that caused the error
        """
        details = {}
        if dependency_path:
            details['dependency_path'] = dependency_path
        if dependency_chain:
            details['dependency_chain'] = dependency_chain
        
        super().__init__(message, details)


class ConfigurationError(WhyMLError):
    """Raised when configuration-related errors occur.
    
    This exception is raised for issues with configuration files,
    invalid configuration values, or missing configuration.
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[str] = None):
        """Initialize configuration error.
        
        Args:
            message: Human-readable error message
            config_key: Configuration key that caused the error
            config_value: Configuration value that caused the error
        """
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_value:
            details['config_value'] = config_value
        
        super().__init__(message, details)
