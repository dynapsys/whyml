"""
WhyML Converters Module - Backward compatibility alias

This module provides backward compatibility for imports from whyml.converters
by re-exporting all converter classes from the whyml-converters package.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

# Re-export all converters from whyml-converters
from whyml_converters import (
    HTMLConverter,
    ReactConverter,
    VueConverter,
    PHPConverter,
    BaseConverter,
    ConversionResult
)

# Re-export exceptions that converters might use
from whyml_core.exceptions import ConversionError, ValidationError

# Make all exports available
__all__ = [
    'HTMLConverter',
    'ReactConverter', 
    'VueConverter',
    'PHPConverter',
    'BaseConverter',
    'ConversionResult',
    'ConversionError',
    'ValidationError'
]
