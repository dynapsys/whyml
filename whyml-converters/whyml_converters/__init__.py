"""
WhyML Converters Package

Advanced manifest converters for multiple output formats.
Provides intelligent conversion from WhyML manifests to HTML, React, Vue, PHP, 
and other target formats with template support and optimization.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .html_converter import HTMLConverter
from .react_converter import ReactConverter
from .vue_converter import VueConverter
from .php_converter import PHPConverter
from .base_converter import BaseConverter

__version__ = "0.1.0"
__author__ = "Tom Sapletta"
__email__ = "tom@sapletta.pl"

__all__ = [
    'BaseConverter',
    'HTMLConverter',
    'ReactConverter',
    'VueConverter',
    'PHPConverter'
]
