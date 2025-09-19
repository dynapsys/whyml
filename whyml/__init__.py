"""
WhyML: Advanced YAML-based webpage generator with modular architecture

A comprehensive Python package for processing YAML manifests and converting them
to various web formats including HTML, React, Vue, and PHP.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

__version__ = "1.0.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"
__license__ = "Apache-2.0"

# Core imports
from .manifest_loader import ManifestLoader
from .manifest_processor import ManifestProcessor
from .exceptions import (
    WhyMLError,
    ManifestError,
    ValidationError,
    ConversionError,
    LoaderError
)

# Converter imports
from .converters import (
    HTMLConverter,
    ReactConverter,
    VueConverter,
    PHPConverter,
    BaseConverter
)

# Scraper imports
from .scrapers import URLScraper, WebpageAnalyzer

# Main API
__all__ = [
    # Core classes
    'ManifestLoader',
    'ManifestProcessor',
    
    # Converters
    'HTMLConverter',
    'ReactConverter', 
    'VueConverter',
    'PHPConverter',
    'BaseConverter',
    
    # Scrapers
    'URLScraper',
    'WebpageAnalyzer',
    
    # Exceptions
    'WhyMLError',
    'ManifestError',
    'ValidationError',
    'ConversionError',
    'LoaderError',
    
    # Metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
]

# ASCII Logo
LOGO = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  🎯 WhyML - Advanced YAML Manifest System               ║
║  Modern Web Development Framework                         ║
║                                                           ║
║  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  ║
║  │    YAML     │───▶│  MANIFEST   │───▶│   OUTPUT    │  ║
║  │  MANIFESTS  │    │  PROCESSOR  │    │   FORMATS   │  ║
║  └─────────────┘    └─────────────┘    └─────────────┘  ║
║       │                     │                   │       ║
║  ┌────▼────┐           ┌────▼────┐         ┌────▼────┐  ║
║  │Templates│           │Modules  │         │HTML/CSS │  ║
║  │& Styles │           │& Imports│         │React/Vue│  ║
║  │Inherit. │           │Python   │         │PHP/JSON │  ║
║  └─────────┘           └─────────┘         └─────────┘  ║
╚═══════════════════════════════════════════════════════════╝
"""

def get_version():
    """Get the current version of WhyML."""
    return __version__

def show_logo():
    """Display the WhyML ASCII logo."""
    print(LOGO)
