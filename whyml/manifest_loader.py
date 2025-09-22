"""
WhyML Manifest Loader Module - Backward compatibility alias

This module provides backward compatibility for imports from whyml.manifest_loader
by re-exporting the ManifestLoader class from the whyml-core package.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

# Re-export ManifestLoader from whyml-core
from whyml_core.loading.manifest_loader import ManifestLoader

# Re-export related exceptions
from whyml_core.exceptions import (
    ManifestLoadingError, 
    DependencyResolutionError,
    TemplateInheritanceError,
    NetworkError,
    LoaderError
)

# Make all exports available
__all__ = [
    'ManifestLoader',
    'ManifestLoadingError',
    'DependencyResolutionError', 
    'TemplateInheritanceError',
    'NetworkError',
    'LoaderError'
]
