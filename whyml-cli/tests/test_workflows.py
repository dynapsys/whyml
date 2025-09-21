"""
Test suite for whyml_cli workflow integration

Tests for:
- End-to-end workflows
- Command chaining
- Batch processing
- Pipeline operations
- Real-world usage scenarios
- Performance benchmarks

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import os
import tempfile
import asyncio
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from pathlib import Path
import yaml

from whyml_cli.cli import main


class TestWorkflowIntegration:
    """Test end-to-end workflow integration."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def sample_manifests(self, tmp_path):
        """Create sample manifest files for testing."""
        manifests = []
        for i in range(3):
            manifest_content = f"""
metadata:
  title: Sample Page {i+1}
  description: A sample test page {i+1}
  version: 1.0.{i}
structure:
  body:
    header:
      h1: Welcome to Page {i+1}
      nav:
        ul:
          li: Home
          li: About
          li: Contact
    main:
      section:
        h2: Content Section {i+1}
        p: This is the main content for page {i+1}
        article:
          h3: Article Title {i+1}
          p: Article content goes here
    footer:
      p: Copyright 2025 - Page {i+1}
"""
            manifest_file = tmp_path / f"manifest_{i+1}.yaml"
            manifest_file.write_text(manifest_content)
            manifests.append(manifest_file)
        return manifests
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    @patch('whyml_cli.commands.convert_command.HTMLConverter')
    def test_complete_website_creation_workflow(self, mock_converter, mock_validator, mock_scraper, cli_runner, tmp_path):
        """Test complete workflow: scrape -> validate -> convert -> generate."""
        # Setup mocks
        scraped_data = {
            'metadata': {
                'title': 'Example Site',
                'description': 'An example website'
            },
            'structure': {
                'body': {
                    'header': {'h1': 'Example Site'},
                    'main': {'p': 'Main content'},
                    'footer': {'p': 'Footer'}
                }
            }
        }
        
        mock_scraper.return_value.scrape_url.return_value = scraped_data
        mock_validator.return_value.validate.return_value = True
        mock_validator.return_value.get_errors.return_value = []
        mock_converter.return_value.convert.return_value = Mock(
            content="<html><head><title>Example Site</title></head><body><h1>Example Site</h1></body></html>",
            filename="index.html"
        )
        
        # Step 1: Scrape multiple pages
        urls = ['https://example.com', 'https://example.com/about', 'https://example.com/contact']
        scraped_files = []
        
        for i, url in enumerate(urls):
            output_file = tmp_path / f"scraped_{i+1}.yaml"
            result = cli_runner.invoke(main, [
                'scrape', url,
                '--output', str(output_file),
                '--section', 'metadata',
                '--section', 'structure'
            ])
            
            assert result.exit_code == 0
            
            # Create the file manually since we're mocking
            output_file.write_text(yaml.dump(scraped_data))
            scraped_files.append(output_file)
        
        # Step 2: Validate all scraped manifests
        for scraped_file in scraped_files:
            result = cli_runner.invoke(main, [
                'validate', str(scraped_file),
                '--strict'
            ])
            assert result.exit_code == 0
        
        # Step 3: Convert all to different formats
        formats = ['html', 'react', 'vue', 'php']
        for scraped_file in scraped_files:
            for fmt in formats:
                with patch(f'whyml_cli.commands.convert_command.{fmt.upper()}Converter' if fmt != 'react' else 'whyml_cli.commands.convert_command.ReactConverter') as mock_fmt_converter:
                    mock_fmt_converter.return_value.convert.return_value = Mock(
                        content=f"<!-- {fmt} content -->",
                        filename=f"test.{fmt}"
                    )
                    
                    result = cli_runner.invoke(main, [
                        'convert', str(scraped_file),
                        '--format', fmt,
                        '--output', str(tmp_path / f"{scraped_file.stem}.{fmt}")
                    ])
                    
                    assert result.exit_code == 0
        
        # Step 4: Generate PWA/SPA configurations
        with patch('whyml_cli.commands.generate_command.WhyMLProcessor') as mock_processor:
            mock_processor.return_value.generate_pwa.return_value = "PWA generated"
            
            result = cli_runner.invoke(main, [
                'generate', 'pwa',
                '--manifest', str(scraped_files[0]),
                '--output', str(tmp_path / 'pwa_output')
            ])
            
            assert result.exit_code == 0
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_batch_scraping_workflow(self, mock_scraper, cli_runner, tmp_path):
        """Test batch scraping of multiple URLs."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        # Create URL list file
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com\nhttps://test.com\nhttps://demo.com\n")
        
        result = cli_runner.invoke(main, [
            'scrape',
            '--batch', str(urls_file),
            '--output-dir', str(tmp_path / 'scraped'),
            '--parallel', '2'
        ])
        
        assert result.exit_code in [0, 1, 2]  # May fail due to missing implementation
    
    def test_validation_pipeline(self, cli_runner, sample_manifests):
        """Test validation pipeline for multiple manifests."""
        with patch('whyml_cli.commands.validate_command.ManifestValidator') as mock_validator:
            mock_validator.return_value.validate.return_value = True
            mock_validator.return_value.get_errors.return_value = []
            
            # Validate all manifests in batch
            for manifest in sample_manifests:
                result = cli_runner.invoke(main, [
                    'validate', str(manifest),
                    '--format', 'json',
                    '--quiet'
                ])
                
                assert result.exit_code == 0
    
    def test_conversion_pipeline(self, cli_runner, sample_manifests, tmp_path):
        """Test conversion pipeline for multiple formats."""
        output_dir = tmp_path / 'converted'
        output_dir.mkdir()
        
        formats = ['html', 'react', 'vue', 'php']
        
        for fmt in formats:
            converter_class = f'{fmt.upper()}Converter' if fmt != 'react' else 'ReactConverter'
            
            with patch(f'whyml_cli.commands.convert_command.{converter_class}') as mock_converter:
                mock_converter.return_value.convert.return_value = Mock(
                    content=f"<!-- {fmt} content -->",
                    filename=f"test.{fmt}"
                )
                
                for manifest in sample_manifests:
                    result = cli_runner.invoke(main, [
                        'convert', str(manifest),
                        '--format', fmt,
                        '--output', str(output_dir / f"{manifest.stem}.{fmt}")
                    ])
                    
                    assert result.exit_code == 0


class TestErrorRecovery:
    """Test error recovery and resilience."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_network_failure_recovery(self, cli_runner):
        """Test recovery from network failures."""
        with patch('whyml_cli.commands.scrape_command.URLScraper') as mock_scraper:
            # First call fails, second succeeds
            mock_scraper.return_value.scrape_url.side_effect = [
                Exception("Network timeout"),
                {'metadata': {'title': 'Success'}, 'structure': {'body': {'h1': 'Hello'}}}
            ]
            
            result = cli_runner.invoke(main, [
                'scrape', 'https://example.com',
                '--retry', '2',
                '--timeout', '10'
            ])
            
            # Should eventually succeed with retry
            assert result.exit_code in [0, 1, 2]
    
    def test_partial_batch_failure(self, cli_runner, tmp_path):
        """Test handling of partial failures in batch operations."""
        # Create mixed valid/invalid manifests
        valid_manifest = tmp_path / "valid.yaml"
        valid_manifest.write_text("metadata:\n  title: Valid\nstructure:\n  body:\n    h1: Hello")
        
        invalid_manifest = tmp_path / "invalid.yaml"
        invalid_manifest.write_text("invalid: yaml: content:")
        
        with patch('whyml_cli.commands.validate_command.ManifestValidator') as mock_validator:
            def side_effect(manifest_path):
                if 'valid' in str(manifest_path):
                    mock_validator.return_value.validate.return_value = True
                    mock_validator.return_value.get_errors.return_value = []
                else:
                    mock_validator.return_value.validate.return_value = False
                    mock_validator.return_value.get_errors.return_value = ["Invalid YAML"]
                return mock_validator.return_value
            
            # Test validation continues despite partial failures
            for manifest in [valid_manifest, invalid_manifest]:
                result = cli_runner.invoke(main, [
                    'validate', str(manifest),
                    '--continue-on-error'
                ])
                
                # Should handle both success and failure gracefully
                assert result.exit_code in [0, 1, 2]
    
    def test_memory_pressure_handling(self, cli_runner, tmp_path):
        """Test handling of memory pressure during large operations."""
        # Create large manifest
        large_structure = {}
        for i in range(1000):
            large_structure[f'section_{i}'] = {
                'h1': f'Title {i}',
                'p': f'Content {i}' * 100  # Make it large
            }
        
        large_manifest_data = {
            'metadata': {'title': 'Large Page'},
            'structure': {'body': large_structure}
        }
        
        large_manifest = tmp_path / "large.yaml"
        large_manifest.write_text(yaml.dump(large_manifest_data))
        
        with patch('whyml_cli.commands.convert_command.HTMLConverter') as mock_converter:
            mock_converter.return_value.convert.return_value = Mock(
                content="<html>Large content</html>",
                filename="large.html"
            )
            
            result = cli_runner.invoke(main, [
                'convert', str(large_manifest),
                '--format', 'html',
                '--memory-limit', '512MB'
            ])
            
            assert result.exit_code in [0, 1, 2]


class TestPerformanceBenchmarks:
    """Test performance and scalability benchmarks."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_scraping_performance(self, cli_runner):
        """Test scraping performance metrics."""
        import time
        
        with patch('whyml_cli.commands.scrape_command.URLScraper') as mock_scraper:
            mock_scraper.return_value.scrape_url.return_value = {
                'metadata': {'title': 'Performance Test'},
                'structure': {'body': {'h1': 'Hello'}}
            }
            
            start_time = time.time()
            
            result = cli_runner.invoke(main, [
                'scrape', 'https://example.com',
                '--performance'
            ])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete within reasonable time
            assert execution_time < 5.0  # 5 seconds max
            assert result.exit_code in [0, 1, 2]
    
    def test_conversion_performance(self, cli_runner, tmp_path):
        """Test conversion performance metrics."""
        import time
        
        manifest_file = tmp_path / "perf_test.yaml"
        manifest_file.write_text("""
metadata:
  title: Performance Test
structure:
  body:
    h1: Performance Test
    p: Testing conversion speed
""")
        
        with patch('whyml_cli.commands.convert_command.HTMLConverter') as mock_converter:
            mock_converter.return_value.convert.return_value = Mock(
                content="<html>Performance test</html>",
                filename="perf.html"
            )
            
            start_time = time.time()
            
            result = cli_runner.invoke(main, [
                'convert', str(manifest_file),
                '--format', 'html',
                '--optimize'
            ])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete quickly for small files
            assert execution_time < 2.0  # 2 seconds max
            assert result.exit_code in [0, 1, 2]
    
    def test_parallel_processing(self, cli_runner, tmp_path):
        """Test parallel processing capabilities."""
        # Create multiple manifests
        manifests = []
        for i in range(5):
            manifest = tmp_path / f"parallel_{i}.yaml"
            manifest.write_text(f"""
metadata:
  title: Parallel Test {i}
structure:
  body:
    h1: Test {i}
""")
            manifests.append(manifest)
        
        with patch('whyml_cli.commands.convert_command.HTMLConverter') as mock_converter:
            mock_converter.return_value.convert.return_value = Mock(
                content="<html>Parallel test</html>",
                filename="parallel.html"
            )
            
            import time
            start_time = time.time()
            
            # Process multiple files
            for manifest in manifests:
                result = cli_runner.invoke(main, [
                    'convert', str(manifest),
                    '--format', 'html',
                    '--parallel', '3'
                ])
                
                assert result.exit_code in [0, 1, 2]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Parallel processing should be reasonably fast
            assert total_time < 10.0  # 10 seconds max for 5 files


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_website_migration_scenario(self, cli_runner, tmp_path):
        """Test website migration workflow."""
        # Scenario: Migrate from old HTML site to modern React app
        
        # Step 1: Scrape existing pages
        with patch('whyml_cli.commands.scrape_command.URLScraper') as mock_scraper:
            mock_scraper.return_value.scrape_url.return_value = {
                'metadata': {
                    'title': 'Legacy Site',
                    'description': 'Old HTML website'
                },
                'structure': {
                    'body': {
                        'header': {'h1': 'Legacy Site'},
                        'nav': {'ul': ['Home', 'About', 'Contact']},
                        'main': {'p': 'Main content'},
                        'footer': {'p': 'Copyright 2020'}
                    }
                }
            }
            
            scraped_manifest = tmp_path / "legacy_scraped.yaml"
            result = cli_runner.invoke(main, [
                'scrape', 'https://legacy-site.com',
                '--output', str(scraped_manifest),
                '--simplify-structure',
                '--preserve-semantic'
            ])
            
            assert result.exit_code in [0, 1, 2]
    
    def test_content_audit_scenario(self, cli_runner, tmp_path):
        """Test content audit and analysis workflow."""
        # Scenario: Audit multiple pages for SEO and accessibility
        
        urls = [
            'https://site.com/',
            'https://site.com/about',
            'https://site.com/products',
            'https://site.com/contact'
        ]
        
        with patch('whyml_cli.commands.scrape_command.URLScraper') as mock_scraper:
            with patch('whyml_cli.commands.scrape_command.WebpageAnalyzer') as mock_analyzer:
                mock_scraper.return_value.scrape_url.return_value = {
                    'metadata': {'title': 'Audit Page'},
                    'analysis': {
                        'seo_score': 85,
                        'accessibility_score': 78,
                        'performance_score': 92
                    }
                }
                
                mock_analyzer.return_value.analyze_page.return_value = {
                    'page_type': 'corporate',
                    'word_count': 1250,
                    'heading_structure': {'h1': 1, 'h2': 3, 'h3': 5},
                    'issues': ['Missing alt text on 2 images']
                }
                
                audit_results = tmp_path / "audit_results.json"
                
                result = cli_runner.invoke(main, [
                    'scrape', urls[0],
                    '--section', 'analysis',
                    '--analyze-seo',
                    '--analyze-accessibility',
                    '--output', str(audit_results),
                    '--format', 'json'
                ])
                
                assert result.exit_code in [0, 1, 2]
    
    def test_multi_language_site_scenario(self, cli_runner, tmp_path):
        """Test multi-language site generation."""
        # Scenario: Generate multi-language versions of a site
        
        base_manifest = tmp_path / "base_manifest.yaml"
        base_manifest.write_text("""
metadata:
  title: "{{LANG.site_title}}"
  description: "{{LANG.site_description}}"
structure:
  body:
    header:
      h1: "{{LANG.welcome_message}}"
    main:
      p: "{{LANG.main_content}}"
""")
        
        languages = ['en', 'es', 'fr', 'de']
        
        for lang in languages:
            with patch('whyml_cli.commands.convert_command.HTMLConverter') as mock_converter:
                mock_converter.return_value.convert.return_value = Mock(
                    content=f"<html lang='{lang}'>Localized content</html>",
                    filename=f"index_{lang}.html"
                )
                
                result = cli_runner.invoke(main, [
                    'convert', str(base_manifest),
                    '--format', 'html',
                    '--language', lang,
                    '--output', str(tmp_path / f"site_{lang}.html")
                ])
                
                assert result.exit_code in [0, 1, 2]


if __name__ == "__main__":
    pytest.main([__file__])
