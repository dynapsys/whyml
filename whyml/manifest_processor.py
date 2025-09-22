"""
WhyML Manifest Processor Module - Backward compatibility alias

This module provides backward compatibility for imports from whyml.manifest_processor
by re-exporting the ManifestProcessor class from the whyml-core package.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

# Re-export ManifestProcessor from whyml-core
from whyml_core.processing.manifest_processor import ManifestProcessor

# Re-export related exceptions
from whyml_core.exceptions import (
    ManifestProcessingError,
    TemplateInheritanceError,
    ValidationError,
    ConfigurationError,
    ProcessingError
)

# Make all exports available
__all__ = [
    'ManifestProcessor',
    'ManifestProcessingError',
    'TemplateInheritanceError',
    'ValidationError',
    'ConfigurationError',
    'ProcessingError'
]
