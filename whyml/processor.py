"""
WhyML Main Processor - High-level interface for WhyML functionality

Provides a unified interface for loading, processing, and converting
YAML manifests to various output formats.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import json
import yaml
import os
import tempfile
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

from .manifest_loader import ManifestLoader
from .manifest_processor import ManifestProcessor
from .converters import (
    HTMLConverter, ReactConverter, VueConverter, PHPConverter,
    ConversionResult
)
from .scrapers import URLScraper, WebpageAnalyzer
from .exceptions import WhyMLError, ConversionError
from .caddy import CaddyConfig
from .generators import (
    enhance_for_spa, enhance_for_pwa, generate_service_worker,
    generate_web_manifest, generate_offline_page, generate_spa_router,
    generate_capacitor_config, generate_capacitor_package_json,
    generate_dockerfile, generate_docker_compose, generate_dockerignore,
    generate_tauri_config, generate_cargo_toml, generate_tauri_main_rs
)


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
                 optimize_output: bool = True,
                 config: Optional[Dict[str, Any]] = None):
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
        self.config = config or {}
        
        # Initialize core components
        self.loader = ManifestLoader(
            cache_size=cache_size,
            cache_ttl=cache_ttl
        )
        
        self.processor = ManifestProcessor(
            strict_validation=enable_validation
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
                                    max_depth: Optional[int] = None,
                                    flatten_containers: bool = False,
                                    simplify_structure: bool = False,
                                    preserve_semantic_tags: bool = True,
                                    sections: Optional[List[str]] = None,
                                    extract_styles: bool = True,
                                    extract_scripts: bool = False,
                                    **kwargs) -> Dict[str, Any]:
        """
        Scrape a URL and convert to YAML manifest with advanced simplification options.
        
        Args:
            url: URL to scrape  
            analyze: Whether to perform webpage analysis
            max_depth: Maximum nesting depth for structure (None = unlimited)
            flatten_containers: Merge wrapper/container divs with minimal content
            simplify_structure: Apply general structure simplification rules
            preserve_semantic_tags: Keep semantic HTML5 tags (article, section, etc.)
            sections: Only extract specific sections (None = all sections)
            extract_styles: Whether to extract CSS styles
            extract_scripts: Whether to extract JavaScript
            **kwargs: Additional scraping options
            
        Returns:
            Generated manifest dictionary
        """
        # Create URLScraper with advanced parameters
        scraper = URLScraper(
            extract_styles=extract_styles,
            extract_scripts=extract_scripts,
            max_depth=max_depth,
            flatten_containers=flatten_containers,
            simplify_structure=simplify_structure,
            preserve_semantic_tags=preserve_semantic_tags,
            sections=sections
        )
        
        async with scraper:
            # Scrape the URL
            manifest = await scraper.scrape_url(url)
            
            # Clean and optimize
            cleaned_manifest = scraper.clean_manifest(manifest)
            
            # Process the manifest with selective validation if sections specified
            if sections:
                # Create a new processor with selective validation for the requested sections
                selective_processor = ManifestProcessor(
                    strict_validation=self.enable_validation,
                    requested_sections=sections
                )
                processed_manifest = selective_processor.process_manifest(cleaned_manifest)
            else:
                # Use default processor for full manifest processing
                processed_manifest = self.processor.process_manifest(cleaned_manifest)
            
            # Add analysis if requested
            if analyze:
                from bs4 import BeautifulSoup
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Create WebpageAnalyzer with simplification parameters
                        analyzer = WebpageAnalyzer(
                            max_depth=max_depth,
                            flatten_containers=flatten_containers,
                            simplify_structure=simplify_structure,
                            preserve_semantic_tags=preserve_semantic_tags
                        )
                        analysis = analyzer.analyze_webpage(soup, url)
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
    
    async def convert_to_spa(self,
                            source: Union[str, Path, Dict[str, Any]],
                            **kwargs) -> ConversionResult:
        """
        Convert manifest to Single Page Application.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with SPA content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        # Generate HTML with SPA routing
        html_result = self.html_converter.convert(manifest, spa_mode=True, **kwargs)
        
        # Add SPA-specific enhancements
        spa_content = self._enhance_for_spa(html_result.content, manifest)
        
        return ConversionResult(
            content=spa_content,
            filename=f"{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}.html",
            format_type='spa',
            metadata=html_result.metadata
        )
    
    async def convert_to_pwa(self,
                            source: Union[str, Path, Dict[str, Any]],
                            **kwargs) -> ConversionResult:
        """
        Convert manifest to Progressive Web Application.
        
        Args:
            source: Manifest source (file path, URL, or dict)
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with PWA content
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        # Generate SPA first
        spa_result = await self.convert_to_spa(source, **kwargs)
        
        # Add PWA-specific features
        pwa_content = self._enhance_for_pwa(spa_result.content, manifest)
        
        return ConversionResult(
            content=pwa_content,
            filename=f"pwa-{spa_result.filename}",
            format_type='pwa',
            metadata={**spa_result.metadata, 'pwa_enabled': True}
        )
    
    async def generate_pwa(self,
                          source: Union[str, Path, Dict[str, Any]],
                          output: Optional[str] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate complete PWA artifact with all necessary files.
        
        Args:
            source: Manifest source
            output: Output directory path
            config: PWA configuration
            
        Returns:
            Path to generated PWA directory
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        output_dir = Path(output) if output else Path(f"pwa-{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main PWA files
        pwa_result = await self.convert_to_pwa(source)
        
        # Write main HTML file
        (output_dir / "index.html").write_text(pwa_result.content)
        
        # Generate service worker
        from .generators import generate_service_worker
        sw_content = generate_service_worker(manifest, config or {})
        (output_dir / "sw.js").write_text(sw_content)
        
        # Generate web manifest
        from .generators import generate_web_manifest
        web_manifest = generate_web_manifest(manifest, config or {})
        (output_dir / "manifest.json").write_text(json.dumps(web_manifest, indent=2))
        
        # Generate offline page
        from .generators import generate_offline_page
        offline_content = generate_offline_page(manifest)
        (output_dir / "offline.html").write_text(offline_content)
        
        return str(output_dir)
    
    async def generate_spa(self,
                          source: Union[str, Path, Dict[str, Any]],
                          output: Optional[str] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate complete SPA artifact.
        
        Args:
            source: Manifest source
            output: Output directory path
            config: SPA configuration
            
        Returns:
            Path to generated SPA directory
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        output_dir = Path(output) if output else Path(f"spa-{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate SPA
        spa_result = await self.convert_to_spa(source)
        
        # Write main HTML file
        (output_dir / "index.html").write_text(spa_result.content)
        
        # Generate router configuration
        from .generators import generate_spa_router
        router_content = generate_spa_router(manifest, config or {})
        (output_dir / "router.js").write_text(router_content)
        
        return str(output_dir)
    
    async def generate_apk(self,
                          source: Union[str, Path, Dict[str, Any]],
                          output: Optional[str] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate APK build configuration using Capacitor.
        
        Args:
            source: Manifest source
            output: Output directory path
            config: APK configuration
            
        Returns:
            Path to generated APK project directory
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        output_dir = Path(output) if output else Path(f"apk-{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PWA first
        pwa_dir = await self.generate_pwa(source, str(output_dir / "www"))
        
        # Generate Capacitor configuration
        from .generators import generate_capacitor_config
        capacitor_config = generate_capacitor_config(manifest, config or {})
        (output_dir / "capacitor.config.json").write_text(json.dumps(capacitor_config, indent=2))
        
        # Generate package.json for Capacitor
        from .generators import generate_capacitor_package_json
        package_json = generate_capacitor_package_json(manifest)
        (output_dir / "package.json").write_text(json.dumps(package_json, indent=2))
        
        return str(output_dir)
    
    async def generate_docker(self,
                             source: Union[str, Path, Dict[str, Any]],
                             output: Optional[str] = None,
                             config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Docker configuration for the application.
        
        Args:
            source: Manifest source
            output: Output directory path
            config: Docker configuration
            
        Returns:
            Path to generated Docker configuration
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        output_dir = Path(output) if output else Path(f"docker-{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Dockerfile
        from .generators import generate_dockerfile
        dockerfile_content = generate_dockerfile(manifest, config or {})
        (output_dir / "Dockerfile").write_text(dockerfile_content)
        
        # Generate docker-compose.yml
        from .generators import generate_docker_compose
        compose_content = generate_docker_compose(manifest, config or {})
        (output_dir / "docker-compose.yml").write_text(compose_content)
        
        # Generate .dockerignore
        from .generators import generate_dockerignore
        dockerignore_content = generate_dockerignore()
        (output_dir / ".dockerignore").write_text(dockerignore_content)
        
        return str(output_dir)
    
    async def generate_tauri(self,
                            source: Union[str, Path, Dict[str, Any]],
                            output: Optional[str] = None,
                            config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Tauri application configuration.
        
        Args:
            source: Manifest source
            output: Output directory path
            config: Tauri configuration
            
        Returns:
            Path to generated Tauri project directory
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        output_dir = Path(output) if output else Path(f"tauri-{manifest.get('metadata', {}).get('title', 'app').lower().replace(' ', '-')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate frontend (SPA)
        spa_dir = await self.generate_spa(source, str(output_dir / "dist"))
        
        # Create Tauri project structure
        (output_dir / "src-tauri").mkdir(exist_ok=True)
        
        # Generate Tauri configuration
        from .generators import generate_tauri_config
        tauri_config = generate_tauri_config(manifest, config or {})
        (output_dir / "src-tauri" / "tauri.conf.json").write_text(json.dumps(tauri_config, indent=2))
        
        # Generate Cargo.toml
        from .generators import generate_cargo_toml
        cargo_toml = generate_cargo_toml(manifest)
        (output_dir / "src-tauri" / "Cargo.toml").write_text(cargo_toml)
        
        # Generate main.rs
        from .generators import generate_tauri_main_rs
        main_rs = generate_tauri_main_rs(manifest)
        (output_dir / "src-tauri" / "src").mkdir(exist_ok=True)
        (output_dir / "src-tauri" / "src" / "main.rs").write_text(main_rs)
        
        return str(output_dir)
    
    async def generate_caddy_config(self,
                                   source: Union[str, Path, Dict[str, Any]],
                                   output: Optional[str] = None,
                                   config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Caddy configuration for the application.
        
        Args:
            source: Manifest source
            output: Output file path
            config: Caddy configuration options
            
        Returns:
            Path to generated Caddy configuration file
        """
        if isinstance(source, dict):
            manifest = source
        else:
            manifest = await self.load_manifest(source)
        
        caddy_config = CaddyConfig()
        
        # Extract configuration options
        caddy_opts = config or {}
        domain = caddy_opts.get('domain', 'localhost')
        host = caddy_opts.get('host', 'localhost')
        port = caddy_opts.get('port', 8080)
        tls_provider = caddy_opts.get('tls_provider')
        
        # Generate configuration
        config_content = await caddy_config.generate_config(
            manifest_file=str(source) if not isinstance(source, dict) else 'manifest.yaml',
            host=host,
            port=port,
            domain=domain,
            tls_provider=tls_provider
        )
        
        # Write to file
        output_file = Path(output) if output else Path("Caddyfile.json")
        output_file.write_text(config_content)
        
        return str(output_file)
    
    async def validate_manifest(self,
                               source: Union[str, Path, Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a manifest and return validation results.
        
        Args:
            source: Manifest source
            
        Returns:
            Tuple of (is_valid, error_list)
        """
        try:
            if isinstance(source, dict):
                manifest = source
            else:
                manifest = await self.load_manifest(source)
            
            # Perform basic validation
            errors = []
            
            # Check required fields
            if 'metadata' not in manifest:
                errors.append("Missing required 'metadata' section")
            
            if 'structure' not in manifest:
                errors.append("Missing required 'structure' section")
            
            # Validate metadata
            metadata = manifest.get('metadata', {})
            if not metadata.get('title'):
                errors.append("Missing 'title' in metadata")
            
            # Validate structure
            structure = manifest.get('structure', {})
            if not structure:
                errors.append("Empty structure section")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [str(e)]
    
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
    
    def _enhance_for_spa(self, html_content: str, manifest: Dict[str, Any]) -> str:
        """Enhance HTML content for SPA functionality."""
        from .generators import generate_spa_router, generate_spa_enhancements
        
        # Add SPA router and enhancements with config
        config = self.config or {}
        spa_router = generate_spa_router(manifest, config)
        spa_enhancements = generate_spa_enhancements(manifest)
        
        # Insert SPA functionality before closing </body> tag
        spa_scripts = f"""
        <script>
        {spa_router}
        {spa_enhancements}
        </script>
        """
        
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{spa_scripts}\n</body>')
        else:
            html_content += spa_scripts
            
        return html_content
    
    def _enhance_for_pwa(self, html_content: str, manifest: Dict[str, Any]) -> str:
        """Enhance HTML content for PWA functionality."""
        from .generators import generate_pwa_enhancements, generate_service_worker, generate_web_manifest
        
        # Generate PWA components with empty config if not provided
        config = self.config or {}
        pwa_enhancements = generate_pwa_enhancements(manifest)
        service_worker = generate_service_worker(manifest, config)
        web_manifest = generate_web_manifest(manifest, config)
        
        # Add PWA meta tags and service worker registration
        pwa_head = f"""
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="{manifest.get('styles', {}).get('primary', '#000000')}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="{manifest.get('metadata', {}).get('title', 'PWA')}">
        """
        
        pwa_scripts = f"""
        <script>
        {pwa_enhancements}
        </script>
        """
        
        # Insert PWA head content
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{pwa_head}\n</head>')
        
        # Insert PWA scripts before closing </body> tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{pwa_scripts}\n</body>')
        else:
            html_content += pwa_scripts
            
        return html_content
    
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
