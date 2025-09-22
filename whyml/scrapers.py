"""
WhyML Scrapers Module - Backward compatibility alias

This module provides backward compatibility for imports from whyml.scrapers
by re-exporting all scraper classes from the whyml-scrapers package.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

# Re-export all scrapers from whyml-scrapers
from whyml_scrapers import URLScraper, WebpageAnalyzer

# Re-export exceptions that scrapers might use
from whyml_core.exceptions import NetworkError, ConversionError

# Make all exports available
__all__ = [
    'URLScraper',
    'WebpageAnalyzer',
    'NetworkError',
    'ConversionError'
]
