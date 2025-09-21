"""
WhyML CLI - Command Line Interface Package

Unified command-line interface for WhyML ecosystem including scraping,
conversion, validation, and generation workflows.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

__version__ = "0.1.0"
__author__ = "Tom Sapletta"
__email__ = "tom@sapletta.pl"
__description__ = "WhyML CLI - Command Line Interface for WhyML ecosystem"

from .main import main
from .cli import WhyMLCLI

__all__ = [
    "main",
    "WhyMLCLI",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
