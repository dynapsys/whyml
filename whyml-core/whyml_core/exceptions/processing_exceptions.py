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
                 status_code: Optional[int] = None):
        """Initialize network error.
        
        Args:
            message: Human-readable error message
            url: URL that caused the error
            status_code: HTTP status code if available
        """
        details = {}
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        
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
