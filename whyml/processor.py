"""
WhyML Main Processor - High-level interface for WhyML functionality

Provides a unified interface for loading, processing, and converting
YAML manifests to various output formats.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .manifest_loader import ManifestLoader
from .manifest_processor import ManifestProcessor
from .converters import (
    HTMLConverter, ReactConverter, VueConverter, PHPConverter,
    ConversionResult
)
from .scrapers import URLScraper, WebpageAnalyzer
from .exceptions import WhyMLError, ConversionError


class WhyMLProcessor:
    """
    Main processor class for WhyML operations.
    
    Provides a high-level interface for:
    - Loading and processing YAML manifests
    - Converting to multiple output formats
    - Web scraping and analysis
    - Batch processing operations
    """
    
    def __init__(self,
                 cache_size: int = 1000,
                 cache_ttl: int = 3600,
                 enable_validation: bool = True,
                 optimize_output: bool = True):
        """
        Initialize WhyML processor.
        
        Args:
            cache_size: Size of manifest cache
            cache_ttl: Cache time-to-live in seconds
            enable_validation: Enable manifest validation
            optimize_output: Enable output optimization
        """
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.enable_validation = enable_validation
        self.optimize_output = optimize_output
        
        # Initialize core components
        self.loader = ManifestLoader(
            cache_size=cache_size,
            cache_ttl=cache_ttl
        )
        
        self.processor = ManifestProcessor(
            enable_validation=enable_validation
        )
        
        # Initialize converters
        self.html_converter = HTMLConverter(optimize_output=optimize_output)
        self.react_converter = ReactConverter(optimize_output=optimize_output)
        self.vue_converter = VueConverter(optimize_output=optimize_output)
        self.php_converter = PHPConverter(optimize_output=optimize_output)
        
        # Initialize scrapers
        self.url_scraper = URLScraper()
        self.webpage_analyzer = WebpageAnalyzer()
    
    async def load_manifest(self, 
                           source: Union[str, Path],
                           options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load and process a manifest from file or URL.
        
        Args:
            source: Path to manifest file or URL
            options: Loading options
            
        Returns:
            Processed manifest dictionary
        """
        async with self.loader:
            raw_manifest = await self.loader.load_manifest(str(source), options or {})
            processed_manifest = self.processor.process_manifest(raw_manifest)
            return processed_manifest
    
    async def convert_to_html(self,
                             source: Union[str, Path, Dict[str, Any]],
                             **kwargs) -> ConversionResult:
        """
        Convert manifest to HTML.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with HTML content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        return self.html_converter.convert(manifest, **kwargs)
    
    async def convert_to_react(self,
                              source: Union[str, Path, Dict[str, Any]],
                              **kwargs) -> ConversionResult:
        """
        Convert manifest to React component.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with React content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        return self.react_converter.convert(manifest, **kwargs)
    
    async def convert_to_vue(self,
                            source: Union[str, Path, Dict[str, Any]],
                            **kwargs) -> ConversionResult:
        """
        Convert manifest to Vue component.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with Vue content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        return self.vue_converter.convert(manifest, **kwargs)
    
    async def convert_to_php(self,
                            source: Union[str, Path, Dict[str, Any]],
                            **kwargs) -> ConversionResult:
        """
        Convert manifest to PHP class.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with PHP content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        return self.php_converter.convert(manifest, **kwargs)
    
    async def convert_to_all_formats(self,
                                    source: Union[str, Path, Dict[str, Any]],
                                    output_dir: Optional[Union[str, Path]] = None,
                                    **kwargs) -> Dict[str, ConversionResult]:
        """
        Convert manifest to all supported formats.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            output_dir: Directory to save all outputs
            **kwargs: Additional conversion options
            
        Returns:
            Dictionary mapping format names to ConversionResults
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        # Convert to all formats
        results = {}
        
        try:
            results['html'] = self.html_converter.convert(manifest, **kwargs)
        except Exception as e:
            results['html'] = ConversionError(f"HTML conversion failed: {e}")
        
        try:
            results['react'] = self.react_converter.convert(manifest, **kwargs)
        except Exception as e:
            results['react'] = ConversionError(f"React conversion failed: {e}")
        
        try:
            results['vue'] = self.vue_converter.convert(manifest, **kwargs)
        except Exception as e:
            results['vue'] = ConversionError(f"Vue conversion failed: {e}")
        
        try:
            results['php'] = self.php_converter.convert(manifest, **kwargs)
        except Exception as e:
            results['php'] = ConversionError(f"PHP conversion failed: {e}")
        
        # Save to output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for format_name, result in results.items():
                if isinstance(result, ConversionResult):
                    output_file = output_path / result.filename
                    result.save_to_file(str(output_file))
        
        return results
    
    async def scrape_url_to_manifest(self,
                                    url: str,
                                    analyze: bool = True,
                                    **kwargs) -> Dict[str, Any]:
        """
        Scrape a URL and convert to YAML manifest.
        
        Args:
            url: URL to scrape
            analyze: Whether to perform webpage analysis
            **kwargs: Additional scraping options
            
        Returns:
            Generated manifest dictionary
        """
        async with self.url_scraper:
            # Scrape the URL
            manifest = await self.url_scraper.scrape_url(url)
            
            # Clean and optimize
            cleaned_manifest = self.url_scraper.clean_manifest(manifest)
            
            # Process the manifest
            processed_manifest = self.processor.process_manifest(cleaned_manifest)
            
            # Add analysis if requested
            if analyze:
                from bs4 import BeautifulSoup
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        analysis = self.webpage_analyzer.analyze_webpage(soup, url)
                        processed_manifest['analysis'] = analysis
            
            return processed_manifest
    
    async def batch_convert(self,
                           sources: List[Union[str, Path]],
                           output_format: str = 'html',
                           output_dir: Optional[Union[str, Path]] = None,
                           **kwargs) -> List[ConversionResult]:
        """
        Batch convert multiple manifests.
        
        Args:
            sources: List of manifest sources
            output_format: Target format ('html', 'react', 'vue', 'php')
            output_dir: Directory to save outputs
            **kwargs: Additional conversion options
            
        Returns:
            List of ConversionResults
        """
        converter_map = {
            'html': self.convert_to_html,
            'react': self.convert_to_react,
            'vue': self.convert_to_vue,
            'php': self.convert_to_php
        }
        
        if output_format not in converter_map:
            raise ConversionError(f"Unsupported output format: {output_format}")
        
        converter_func = converter_map[output_format]
        
        # Process all sources concurrently
        tasks = [converter_func(source, **kwargs) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for i, result in enumerate(results):
                if isinstance(result, ConversionResult):
                    output_file = output_path / f"{i:03d}_{result.filename}"
                    result.save_to_file(str(output_file))
                elif isinstance(result, Exception):
                    # Log error but continue processing
                    print(f"Error processing {sources[i]}: {result}")
        
        return [r for r in results if isinstance(r, ConversionResult)]
    
    async def validate_manifest(self,
                               source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a manifest and return validation results.
        
        Args:
            source: Manifest source
            
        Returns:
            Validation results dictionary
        """
        try:
            if isinstance(source, dict):
                manifest = source
            else:
                manifest = await self.load_manifest(source)
            
            # Perform validation
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'metadata': manifest.get('metadata', {}),
                'structure_complexity': self._analyze_structure_complexity(manifest),
                'style_count': len(manifest.get('styles', {})),
                'dependency_count': len(manifest.get('dependencies', []))
            }
            
            return validation_results
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': [],
                'error_type': type(e).__name__
            }
    
    def _analyze_structure_complexity(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the complexity of the manifest structure."""
        structure = manifest.get('structure', {})
        
        def count_elements(obj, depth=0):
            if isinstance(obj, dict):
                count = 1
                max_depth = depth
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        element_count, element_depth = count_elements(value, depth + 1)
                        count += element_count
                        max_depth = max(max_depth, element_depth)
                return count, max_depth
            elif isinstance(obj, list):
                count = 0
                max_depth = depth
                for item in obj:
                    if isinstance(item, (dict, list)):
                        element_count, element_depth = count_elements(item, depth)
                        count += element_count
                        max_depth = max(max_depth, element_depth)
                return count, max_depth
            return 0, depth
        
        element_count, max_depth = count_elements(structure)
        
        return {
            'element_count': element_count,
            'max_nesting_depth': max_depth,
            'complexity_score': element_count * (max_depth + 1)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Clean up resources if needed
        pass


# Convenience functions for common operations
async def convert_manifest(source: Union[str, Path, Dict[str, Any]],
                          output_format: str = 'html',
                          **kwargs) -> ConversionResult:
    """
    Convenience function to convert a manifest to specified format.
    
    Args:
        source: Manifest source
        output_format: Target format
        **kwargs: Additional options
        
    Returns:
        ConversionResult
    """
    async with WhyMLProcessor() as processor:
        if output_format == 'html':
            return await processor.convert_to_html(source, **kwargs)
        elif output_format == 'react':
            return await processor.convert_to_react(source, **kwargs)
        elif output_format == 'vue':
            return await processor.convert_to_vue(source, **kwargs)
        elif output_format == 'php':
            return await processor.convert_to_php(source, **kwargs)
        else:
            raise ConversionError(f"Unsupported format: {output_format}")


async def scrape_and_convert(url: str,
                            output_format: str = 'html',
                            **kwargs) -> ConversionResult:
    """
    Convenience function to scrape URL and convert to specified format.
    
    Args:
        url: URL to scrape
        output_format: Target format
        **kwargs: Additional options
        
    Returns:
        ConversionResult
    """
    async with WhyMLProcessor() as processor:
        manifest = await processor.scrape_url_to_manifest(url)
        return await convert_manifest(manifest, output_format, **kwargs)
