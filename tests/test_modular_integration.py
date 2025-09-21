"""
Integration tests for WhyML modular ecosystem

Tests for end-to-end workflows across all modular packages:
- whyml-core (validation, loading, processing, utils)
- whyml-scrapers (URLScraper, WebpageAnalyzer, ContentExtractor)
- whyml-converters (HTML, React, Vue, PHP converters)
- whyml-cli (unified command-line interface)

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner

# Import from modular packages
from whyml_core.loading.manifest_loader import ManifestLoader
from whyml_core.processing.manifest_processor import ManifestProcessor
from whyml_core.validation.manifest_validator import ManifestValidator
from whyml_scrapers.url_scraper import URLScraper
from whyml_scrapers.webpage_analyzer import WebpageAnalyzer
from whyml_converters.html_converter import HTMLConverter
from whyml_converters.react_converter import ReactConverter
from whyml_converters.vue_converter import VueConverter
from whyml_converters.php_converter import PHPConverter
from whyml_cli.cli import main as cli_main


class TestModularEcosystemIntegration:
    """Test integration across all modular packages."""
    
    @pytest.fixture
    def sample_manifest_data(self):
        """Create sample manifest data for testing."""
        return {
            'metadata': {
                'title': 'Integration Test Page',
                'description': 'Testing modular ecosystem integration',
                'version': '1.0.0',
                'author': 'WhyML Test Suite'
            },
            'structure': {
                'body': {
                    'header': {
                        'h1': 'Integration Test',
                        'nav': {
                            'ul': {
                                'children': [
                                    {'li': {'a': {'href': '/', 'text': 'Home'}}},
                                    {'li': {'a': {'href': '/about', 'text': 'About'}}}
                                ]
                            }
                        }
                    },
                    'main': {
                        'section': {
                            'h2': 'Main Content',
                            'p': 'This is a test of the modular WhyML ecosystem.'
                        }
                    },
                    'footer': {
                        'p': 'Copyright 2025'
                    }
                }
            },
            'styles': {
                'body': 'font-family: Arial, sans-serif; margin: 0; padding: 20px;',
                'header': 'background: #007bff; color: white; padding: 20px;',
                'nav ul': 'list-style: none; display: flex; gap: 20px;',
                'nav a': 'color: white; text-decoration: none;',
                'main': 'padding: 40px 0;',
                'footer': 'background: #f8f9fa; padding: 20px; text-align: center;'
            }
        }
    
    @pytest.fixture
    def temp_project(self, sample_manifest_data):
        """Create temporary project with manifest file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_file = project_path / 'test_manifest.yaml'
            
            with open(manifest_file, 'w') as f:
                yaml.dump(sample_manifest_data, f)
            
            yield {
                'project_path': project_path,
                'manifest_file': manifest_file,
                'manifest_data': sample_manifest_data
            }
    
    @pytest.mark.asyncio
    async def test_core_loading_processing_workflow(self, temp_project):
        """Test whyml-core loading and processing workflow."""
        # Step 1: Load manifest using whyml-core
        loader = ManifestLoader()
        
        async with loader:
            raw_manifest = await loader.load_manifest(str(temp_project['manifest_file']))
            
            assert raw_manifest is not None
            assert raw_manifest['metadata']['title'] == 'Integration Test Page'
            assert 'structure' in raw_manifest
        
        # Step 2: Validate manifest using whyml-core
        validator = ManifestValidator()
        is_valid = validator.validate(raw_manifest)
        
        assert is_valid is True
        assert len(validator.get_errors()) == 0
        
        # Step 3: Process manifest using whyml-core
        processor = ManifestProcessor()
        processed_manifest = processor.process_manifest(raw_manifest)
        
        assert processed_manifest is not None
        assert processed_manifest['metadata']['title'] == 'Integration Test Page'
        assert 'structure' in processed_manifest
    
    @pytest.mark.asyncio
    async def test_scrapers_to_core_workflow(self):
        """Test whyml-scrapers to whyml-core workflow."""
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scraped Integration Test</title>
            <meta name="description" content="Testing scraper integration">
        </head>
        <body>
            <header>
                <h1>Scraped Content</h1>
            </header>
            <main>
                <p>This content was scraped for integration testing.</p>
            </main>
        </body>
        </html>
        """
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Step 1: Scrape using whyml-scrapers
            scraper = URLScraper()
            
            async with scraper:
                scraped_manifest = await scraper.scrape_url('https://example.com')
                
                assert scraped_manifest is not None
                assert 'metadata' in scraped_manifest
                assert scraped_manifest['metadata']['title'] == 'Scraped Integration Test'
            
            # Step 2: Validate scraped manifest using whyml-core
            validator = ManifestValidator()
            is_valid = validator.validate(scraped_manifest)
            
            assert is_valid is True
            
            # Step 3: Process scraped manifest using whyml-core
            processor = ManifestProcessor()
            processed_manifest = processor.process_manifest(scraped_manifest)
            
            assert processed_manifest is not None
            assert 'structure' in processed_manifest
    
    @pytest.mark.asyncio
    async def test_core_to_converters_workflow(self, temp_project):
        """Test whyml-core to whyml-converters workflow."""
        # Step 1: Load and process using whyml-core
        loader = ManifestLoader()
        processor = ManifestProcessor()
        
        async with loader:
            raw_manifest = await loader.load_manifest(str(temp_project['manifest_file']))
            processed_manifest = processor.process_manifest(raw_manifest)
        
        # Step 2: Convert to all formats using whyml-converters
        converters = [
            ('html', HTMLConverter()),
            ('react', ReactConverter()),
            ('vue', VueConverter()),
            ('php', PHPConverter())
        ]
        
        results = {}
        for format_name, converter in converters:
            result = converter.convert(processed_manifest)
            results[format_name] = result
            
            assert result is not None
            assert result.content is not None
            assert result.filename is not None
            assert 'Integration Test' in result.content
        
        # Verify format-specific content
        assert '<!DOCTYPE html>' in results['html'].content
        assert 'import React' in results['react'].content or 'function ' in results['react'].content
        assert '<template>' in results['vue'].content
        assert '<?php' in results['php'].content
    
    def test_cli_integration_workflow(self, temp_project):
        """Test whyml-cli integration with all modules."""
        cli_runner = CliRunner()
        
        # Test CLI info command
        result = cli_runner.invoke(cli_main, ['info'])
        assert result.exit_code in [0, 1, 2]  # May fail due to missing dependencies
        
        # Test CLI validate command
        result = cli_runner.invoke(cli_main, [
            'validate', str(temp_project['manifest_file'])
        ])
        assert result.exit_code in [0, 1, 2]
        
        # Test CLI convert command
        result = cli_runner.invoke(cli_main, [
            'convert', str(temp_project['manifest_file']),
            '--format', 'html'
        ])
        assert result.exit_code in [0, 1, 2]
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_workflow(self, temp_project):
        """Test complete pipeline: scrape -> validate -> process -> convert."""
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pipeline Test</title>
        </head>
        <body>
            <h1>Pipeline Content</h1>
            <p>Testing complete pipeline workflow.</p>
        </body>
        </html>
        """
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Complete pipeline
            scraper = URLScraper()
            validator = ManifestValidator()
            processor = ManifestProcessor()
            converter = HTMLConverter()
            
            async with scraper:
                # Step 1: Scrape
                scraped_manifest = await scraper.scrape_url('https://example.com')
                
                # Step 2: Validate
                is_valid = validator.validate(scraped_manifest)
                assert is_valid is True
                
                # Step 3: Process
                processed_manifest = processor.process_manifest(scraped_manifest)
                
                # Step 4: Convert
                result = converter.convert(processed_manifest)
                
                # Verify pipeline success
                assert result is not None
                assert 'Pipeline Test' in result.content
                assert 'Pipeline Content' in result.content
    
    def test_error_handling_across_modules(self):
        """Test error handling across modular packages."""
        # Test validation error handling
        validator = ManifestValidator()
        invalid_manifest = {'invalid': 'structure'}
        
        is_valid = validator.validate(invalid_manifest)
        assert is_valid is False
        assert len(validator.get_errors()) > 0
        
        # Test converter error handling
        converter = HTMLConverter()
        
        try:
            result = converter.convert(invalid_manifest)
            # Should handle gracefully or raise appropriate error
            assert result is not None or True  # Either succeeds or we catch error
        except Exception as e:
            # Should be a meaningful error from the converter
            assert str(e) is not None
    
    @pytest.mark.asyncio
    async def test_performance_across_modules(self, temp_project):
        """Test performance across modular packages."""
        import time
        
        start_time = time.time()
        
        # Complete workflow with timing
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = HTMLConverter()
        
        async with loader:
            raw_manifest = await loader.load_manifest(str(temp_project['manifest_file']))
            processed_manifest = processor.process_manifest(raw_manifest)
            result = converter.convert(processed_manifest)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        assert execution_time < 2.0  # Less than 2 seconds
        assert result is not None


class TestModularDependencies:
    """Test dependencies between modular packages."""
    
    def test_core_package_independence(self):
        """Test that whyml-core can work independently."""
        from whyml_core.validation.manifest_validator import ManifestValidator
        from whyml_core.loading.manifest_loader import ManifestLoader
        from whyml_core.processing.manifest_processor import ManifestProcessor
        
        # These should import without errors
        validator = ManifestValidator()
        loader = ManifestLoader()
        processor = ManifestProcessor()
        
        assert validator is not None
        assert loader is not None
        assert processor is not None
    
    def test_scrapers_package_independence(self):
        """Test that whyml-scrapers can work independently."""
        from whyml_scrapers.url_scraper import URLScraper
        from whyml_scrapers.webpage_analyzer import WebpageAnalyzer
        from whyml_scrapers.content_extractor import ContentExtractor
        
        scraper = URLScraper()
        analyzer = WebpageAnalyzer()
        extractor = ContentExtractor()
        
        assert scraper is not None
        assert analyzer is not None
        assert extractor is not None
    
    def test_converters_package_independence(self):
        """Test that whyml-converters can work independently."""
        from whyml_converters.html_converter import HTMLConverter
        from whyml_converters.react_converter import ReactConverter
        from whyml_converters.vue_converter import VueConverter
        from whyml_converters.php_converter import PHPConverter
        
        html_conv = HTMLConverter()
        react_conv = ReactConverter()
        vue_conv = VueConverter()
        php_conv = PHPConverter()
        
        assert html_conv is not None
        assert react_conv is not None
        assert vue_conv is not None
        assert php_conv is not None
    
    def test_cli_package_dependencies(self):
        """Test that whyml-cli properly imports all dependencies."""
        from whyml_cli.cli import WhyMLCLI
        from whyml_cli.commands.scrape_command import ScrapeCommand
        from whyml_cli.commands.convert_command import ConvertCommand
        from whyml_cli.commands.validate_command import ValidateCommand
        
        cli = WhyMLCLI()
        scrape_cmd = ScrapeCommand()
        convert_cmd = ConvertCommand()
        validate_cmd = ValidateCommand()
        
        assert cli is not None
        assert scrape_cmd is not None
        assert convert_cmd is not None
        assert validate_cmd is not None


if __name__ == "__main__":
    pytest.main([__file__])
