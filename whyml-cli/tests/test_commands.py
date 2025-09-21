"""
Test suite for whyml_cli commands module

Tests for all CLI commands:
- ScrapeCommand
- ConvertCommand 
- ValidateCommand
- GenerateCommand
- InfoCommand

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from pathlib import Path

from whyml_cli.cli import main
from whyml_cli.commands.scrape_command import ScrapeCommand
from whyml_cli.commands.convert_command import ConvertCommand
from whyml_cli.commands.validate_command import ValidateCommand
from whyml_cli.commands.generate_command import GenerateCommand
from whyml_cli.commands.info_command import InfoCommand


class TestScrapeCommand:
    """Test cases for ScrapeCommand."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_scrape_command_help(self, cli_runner):
        """Test scrape command help."""
        result = cli_runner.invoke(main, ['scrape', '--help'])
        
        assert result.exit_code == 0
        assert 'URL' in result.output
        assert 'scrape' in result.output.lower()
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_basic_scrape(self, mock_scraper, cli_runner):
        """Test basic URL scraping."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {
                'title': 'Test Page',
                'description': 'Test Description'
            },
            'structure': {
                'body': {
                    'h1': 'Hello World',
                    'p': 'Test content'
                }
            }
        }
        
        result = cli_runner.invoke(main, ['scrape', 'https://example.com'])
        
        assert result.exit_code == 0
        assert 'metadata:' in result.output
        assert 'structure:' in result.output
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_scrape_with_output_file(self, mock_scraper, cli_runner, tmp_path):
        """Test scraping with output file."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        output_file = tmp_path / "scraped.yaml"
        
        result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--output', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_scrape_with_sections(self, mock_scraper, cli_runner):
        """Test scraping with specific sections."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--section', 'metadata',
            '--section', 'structure'
        ])
        
        assert result.exit_code == 0
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_scrape_with_simplification(self, mock_scraper, cli_runner):
        """Test scraping with structure simplification."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--simplify-structure',
            '--max-depth', '5',
            '--flatten-containers'
        ])
        
        assert result.exit_code == 0
    
    def test_scrape_invalid_url(self, cli_runner):
        """Test scraping with invalid URL."""
        result = cli_runner.invoke(main, ['scrape', 'invalid-url'])
        
        assert result.exit_code != 0
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_scrape_network_error(self, mock_scraper, cli_runner):
        """Test scraping with network error."""
        mock_scraper.return_value.scrape_url.side_effect = Exception("Network error")
        
        result = cli_runner.invoke(main, ['scrape', 'https://example.com'])
        
        assert result.exit_code != 0
        assert 'error' in result.output.lower()


class TestConvertCommand:
    """Test cases for ConvertCommand."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def test_manifest(self, tmp_path):
        """Create a test manifest file."""
        manifest_content = """
metadata:
  title: Test Page
  description: A test page
structure:
  body:
    h1: Hello World
    p: This is test content
"""
        manifest_file = tmp_path / "test.yaml"
        manifest_file.write_text(manifest_content)
        return manifest_file
    
    def test_convert_command_help(self, cli_runner):
        """Test convert command help."""
        result = cli_runner.invoke(main, ['convert', '--help'])
        
        assert result.exit_code == 0
        assert 'manifest' in result.output.lower()
        assert 'format' in result.output.lower()
    
    @patch('whyml_cli.commands.convert_command.HTMLConverter')
    def test_convert_to_html(self, mock_converter, cli_runner, test_manifest):
        """Test converting manifest to HTML."""
        mock_converter.return_value.convert.return_value = Mock(
            content="<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>",
            filename="test.html"
        )
        
        result = cli_runner.invoke(main, [
            'convert', str(test_manifest),
            '--format', 'html'
        ])
        
        assert result.exit_code == 0
        assert '<html>' in result.output
    
    @patch('whyml_cli.commands.convert_command.ReactConverter')
    def test_convert_to_react(self, mock_converter, cli_runner, test_manifest):
        """Test converting manifest to React."""
        mock_converter.return_value.convert.return_value = Mock(
            content="import React from 'react';\n\nfunction TestPage() {\n  return <h1>Hello</h1>;\n}",
            filename="TestPage.jsx"
        )
        
        result = cli_runner.invoke(main, [
            'convert', str(test_manifest),
            '--format', 'react'
        ])
        
        assert result.exit_code == 0
        assert 'React' in result.output
    
    @patch('whyml_cli.commands.convert_command.VueConverter')
    def test_convert_to_vue(self, mock_converter, cli_runner, test_manifest):
        """Test converting manifest to Vue."""
        mock_converter.return_value.convert.return_value = Mock(
            content="<template><h1>Hello</h1></template>\n<script>export default {name: 'TestPage'}</script>",
            filename="TestPage.vue"
        )
        
        result = cli_runner.invoke(main, [
            'convert', str(test_manifest),
            '--format', 'vue'
        ])
        
        assert result.exit_code == 0
        assert '<template>' in result.output
    
    @patch('whyml_cli.commands.convert_command.PHPConverter')
    def test_convert_to_php(self, mock_converter, cli_runner, test_manifest):
        """Test converting manifest to PHP."""
        mock_converter.return_value.convert.return_value = Mock(
            content="<?php\n$title = 'Test';\n?>\n<h1><?= $title ?></h1>",
            filename="test.php"
        )
        
        result = cli_runner.invoke(main, [
            'convert', str(test_manifest),
            '--format', 'php'
        ])
        
        assert result.exit_code == 0
        assert '<?php' in result.output
    
    def test_convert_with_output_file(self, cli_runner, test_manifest, tmp_path):
        """Test converting with output file."""
        output_file = tmp_path / "output.html"
        
        with patch('whyml_cli.commands.convert_command.HTMLConverter') as mock_converter:
            mock_converter.return_value.convert.return_value = Mock(
                content="<html><h1>Test</h1></html>",
                filename="test.html"
            )
            
            result = cli_runner.invoke(main, [
                'convert', str(test_manifest),
                '--format', 'html',
                '--output', str(output_file)
            ])
            
            assert result.exit_code == 0
    
    def test_convert_nonexistent_file(self, cli_runner):
        """Test converting nonexistent file."""
        result = cli_runner.invoke(main, [
            'convert', 'nonexistent.yaml',
            '--format', 'html'
        ])
        
        assert result.exit_code != 0
    
    def test_convert_invalid_format(self, cli_runner, test_manifest):
        """Test converting with invalid format."""
        result = cli_runner.invoke(main, [
            'convert', str(test_manifest),
            '--format', 'invalid'
        ])
        
        assert result.exit_code != 0


class TestValidateCommand:
    """Test cases for ValidateCommand."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def valid_manifest(self, tmp_path):
        """Create a valid test manifest file."""
        manifest_content = """
metadata:
  title: Valid Page
  description: A valid test page
structure:
  body:
    h1: Hello World
    p: Valid content
"""
        manifest_file = tmp_path / "valid.yaml"
        manifest_file.write_text(manifest_content)
        return manifest_file
    
    @pytest.fixture
    def invalid_manifest(self, tmp_path):
        """Create an invalid test manifest file."""
        manifest_content = """
metadata:
  # Missing required title
structure:
  invalid_structure: true
"""
        manifest_file = tmp_path / "invalid.yaml"
        manifest_file.write_text(manifest_content)
        return manifest_file
    
    def test_validate_command_help(self, cli_runner):
        """Test validate command help."""
        result = cli_runner.invoke(main, ['validate', '--help'])
        
        assert result.exit_code == 0
        assert 'validate' in result.output.lower()
        assert 'manifest' in result.output.lower()
    
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    def test_validate_valid_manifest(self, mock_validator, cli_runner, valid_manifest):
        """Test validating a valid manifest."""
        mock_validator.return_value.validate.return_value = True
        mock_validator.return_value.get_errors.return_value = []
        
        result = cli_runner.invoke(main, ['validate', str(valid_manifest)])
        
        assert result.exit_code == 0
        assert 'valid' in result.output.lower()
    
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    def test_validate_invalid_manifest(self, mock_validator, cli_runner, invalid_manifest):
        """Test validating an invalid manifest."""
        mock_validator.return_value.validate.return_value = False
        mock_validator.return_value.get_errors.return_value = [
            "Missing required field: title",
            "Invalid structure format"
        ]
        
        result = cli_runner.invoke(main, ['validate', str(invalid_manifest)])
        
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_validate_nonexistent_file(self, cli_runner):
        """Test validating nonexistent file."""
        result = cli_runner.invoke(main, ['validate', 'nonexistent.yaml'])
        
        assert result.exit_code != 0
    
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    def test_validate_with_schema(self, mock_validator, cli_runner, valid_manifest, tmp_path):
        """Test validation with custom schema."""
        schema_file = tmp_path / "schema.json"
        schema_file.write_text('{"type": "object"}')
        
        mock_validator.return_value.validate.return_value = True
        mock_validator.return_value.get_errors.return_value = []
        
        result = cli_runner.invoke(main, [
            'validate', str(valid_manifest),
            '--schema', str(schema_file)
        ])
        
        assert result.exit_code == 0
    
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    def test_validate_strict_mode(self, mock_validator, cli_runner, valid_manifest):
        """Test validation in strict mode."""
        mock_validator.return_value.validate.return_value = True
        mock_validator.return_value.get_errors.return_value = []
        
        result = cli_runner.invoke(main, [
            'validate', str(valid_manifest),
            '--strict'
        ])
        
        assert result.exit_code == 0


class TestGenerateCommand:
    """Test cases for GenerateCommand."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_generate_command_help(self, cli_runner):
        """Test generate command help."""
        result = cli_runner.invoke(main, ['generate', '--help'])
        
        assert result.exit_code == 0
        assert 'generate' in result.output.lower()
    
    @patch('whyml_cli.commands.generate_command.WhyMLProcessor')
    def test_generate_pwa(self, mock_processor, cli_runner, tmp_path):
        """Test PWA generation."""
        mock_processor.return_value.generate_pwa.return_value = "PWA files generated"
        
        manifest_file = tmp_path / "test.yaml"
        manifest_file.write_text("metadata:\n  title: Test PWA")
        
        result = cli_runner.invoke(main, [
            'generate', 'pwa',
            '--manifest', str(manifest_file),
            '--output', str(tmp_path)
        ])
        
        assert result.exit_code == 0
    
    @patch('whyml_cli.commands.generate_command.WhyMLProcessor')
    def test_generate_spa(self, mock_processor, cli_runner, tmp_path):
        """Test SPA generation."""
        mock_processor.return_value.generate_spa.return_value = "SPA files generated"
        
        manifest_file = tmp_path / "test.yaml"
        manifest_file.write_text("metadata:\n  title: Test SPA")
        
        result = cli_runner.invoke(main, [
            'generate', 'spa',
            '--manifest', str(manifest_file),
            '--framework', 'react'
        ])
        
        assert result.exit_code == 0
    
    @patch('whyml_cli.commands.generate_command.WhyMLProcessor')
    def test_generate_docker_config(self, mock_processor, cli_runner, tmp_path):
        """Test Docker configuration generation."""
        mock_processor.return_value.generate_docker_config.return_value = "Dockerfile generated"
        
        manifest_file = tmp_path / "test.yaml"
        manifest_file.write_text("metadata:\n  title: Test App")
        
        result = cli_runner.invoke(main, [
            'generate', 'docker',
            '--manifest', str(manifest_file)
        ])
        
        assert result.exit_code == 0
    
    def test_generate_invalid_type(self, cli_runner):
        """Test generation with invalid type."""
        result = cli_runner.invoke(main, [
            'generate', 'invalid_type'
        ])
        
        assert result.exit_code != 0


class TestInfoCommand:
    """Test cases for InfoCommand."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_info_command_help(self, cli_runner):
        """Test info command help."""
        result = cli_runner.invoke(main, ['info', '--help'])
        
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
    
    def test_info_basic(self, cli_runner):
        """Test basic info command."""
        result = cli_runner.invoke(main, ['info'])
        
        assert result.exit_code == 0
        assert 'WhyML' in result.output
    
    def test_info_version(self, cli_runner):
        """Test info version display."""
        result = cli_runner.invoke(main, ['info', '--version'])
        
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_info_dependencies(self, cli_runner):
        """Test info dependencies display."""
        result = cli_runner.invoke(main, ['info', '--dependencies'])
        
        assert result.exit_code == 0
    
    def test_info_system(self, cli_runner):
        """Test info system information."""
        result = cli_runner.invoke(main, ['info', '--system'])
        
        assert result.exit_code == 0
    
    @patch('whyml_cli.commands.info_command.WhyMLProcessor')
    def test_info_formats(self, mock_processor, cli_runner):
        """Test supported formats information."""
        mock_processor.return_value.get_supported_formats.return_value = ['html', 'react', 'vue', 'php']
        
        result = cli_runner.invoke(main, ['info', '--formats'])
        
        assert result.exit_code == 0
        assert 'html' in result.output.lower()


class TestCommandIntegration:
    """Test command integration scenarios."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    @patch('whyml_cli.commands.validate_command.ManifestValidator')
    @patch('whyml_cli.commands.convert_command.HTMLConverter')
    def test_scrape_validate_convert_workflow(self, mock_converter, mock_validator, mock_scraper, cli_runner, tmp_path):
        """Test complete scrape -> validate -> convert workflow."""
        # Setup mocks
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        mock_validator.return_value.validate.return_value = True
        mock_validator.return_value.get_errors.return_value = []
        mock_converter.return_value.convert.return_value = Mock(
            content="<html><h1>Hello</h1></html>",
            filename="test.html"
        )
        
        scraped_file = tmp_path / "scraped.yaml"
        
        # Step 1: Scrape
        scrape_result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--output', str(scraped_file)
        ])
        assert scrape_result.exit_code == 0
        
        # Create the scraped file for validation/conversion
        scraped_file.write_text("metadata:\n  title: Test\nstructure:\n  body:\n    h1: Hello")
        
        # Step 2: Validate
        validate_result = cli_runner.invoke(main, [
            'validate', str(scraped_file)
        ])
        assert validate_result.exit_code == 0
        
        # Step 3: Convert
        convert_result = cli_runner.invoke(main, [
            'convert', str(scraped_file),
            '--format', 'html'
        ])
        assert convert_result.exit_code == 0
    
    def test_error_propagation(self, cli_runner):
        """Test error propagation through command chain."""
        # Test that errors in one command don't affect others
        result1 = cli_runner.invoke(main, ['validate', 'nonexistent.yaml'])
        assert result1.exit_code != 0
        
        # Next command should still work
        result2 = cli_runner.invoke(main, ['info'])
        assert result2.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__])
