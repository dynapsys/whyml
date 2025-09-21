"""
WhyML Core Exceptions - Centralized exception handling for WhyML ecosystem

Provides base exceptions and error handling utilities used across all WhyML packages.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .base_exceptions import WhyMLError
from .validation_exceptions import ValidationError, SchemaError, handle_validation_errors
from .processing_exceptions import (
    TemplateError, 
    TemplateInheritanceError, 
    ManifestError, 
    NetworkError,
    ConversionError
)

__all__ = [
    'WhyMLError',
    'ValidationError', 
    'SchemaError',
    'handle_validation_errors',
    'TemplateError',
    'TemplateInheritanceError', 
    'ManifestError',
    'NetworkError',
    'ConversionError'
]
