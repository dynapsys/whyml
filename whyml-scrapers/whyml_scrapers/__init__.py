"""
WhyML Scrapers Package

Advanced web scraping functionality for WhyML ecosystem.
Provides intelligent web scraping with structure analysis, content extraction,
and manifest generation capabilities.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .url_scraper import URLScraper
from .webpage_analyzer import WebpageAnalyzer
from .content_extractor import ContentExtractor
from .structure_analyzer import StructureAnalyzer

__version__ = "0.1.0"
__author__ = "Tom Sapletta"
__email__ = "tom@sapletta.pl"

__all__ = [
    'URLScraper',
    'WebpageAnalyzer', 
    'ContentExtractor',
    'StructureAnalyzer'
]
