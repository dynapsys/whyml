"""
WhyML Core - Podstawowy pakiet ekosystemu WhyML

Zawiera fundamentalne funkcjonalności:
- Walidację manifestów
- Ładowanie i zarządzanie zależnościami  
- Przetwarzanie szablonów
- Wyjątki i obsługę błędów

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .exceptions import (
    WhyMLError,
    ValidationError, 
    TemplateError,
    TemplateInheritanceError,
    ManifestError,
    SchemaError,
    NetworkError,
    ConversionError,
    handle_validation_errors
)

from .validation import ManifestValidator, SchemaLoader, FieldValidators
from .loading import ManifestLoader, CacheManager, DependencyResolver, LoadedManifest
from .processing import TemplateProcessor, InheritanceResolver, VariableSubstitution
from .utils import yaml_utils, async_utils

__version__ = "1.0.0"
__author__ = "Tom Sapletta"
__license__ = "Apache 2.0"

__all__ = [
    # Exceptions
    'WhyMLError', 'ValidationError', 'TemplateError', 'TemplateInheritanceError',
    'ManifestError', 'SchemaError', 'NetworkError', 'ConversionError',
    'handle_validation_errors',
    
    # Validation
    'ManifestValidator', 'SchemaLoader', 'FieldValidators',
    
    # Loading
    'ManifestLoader', 'CacheManager', 'DependencyResolver', 'LoadedManifest',
    
    # Processing
    'TemplateProcessor', 'InheritanceResolver', 'VariableSubstitution',
    
    # Utils
    'yaml_utils', 'async_utils'
]
