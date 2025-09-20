"""
Scrapers Package - URL processing and website-to-manifest conversion

Provides tools for scraping websites and converting them to YAML manifests
with intelligent content extraction and structure analysis.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .url_scraper import URLScraper
from .webpage_analyzer import WebpageAnalyzer

__all__ = [
    'URLScraper',
    'WebpageAnalyzer',
]
