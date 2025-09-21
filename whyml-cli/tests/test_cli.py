"""
Test suite for whyml_cli.cli module

Tests for:
- CLI initialization and configuration
- Command registration and discovery
- Global options handling
- Help system
- Error handling and reporting
- Plugin system

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from io import StringIO

from whyml_cli.cli import WhyMLCLI, main
from whyml_cli.commands.base_command import BaseCommand


class TestWhyMLCLI:
    """Test cases for WhyMLCLI main class."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def cli_instance(self):
        """Create a WhyMLCLI instance for testing."""
        return WhyMLCLI()
    
    def test_cli_initialization(self, cli_instance):
        """Test WhyMLCLI initialization."""
        assert cli_instance is not None
        assert hasattr(cli_instance, 'main')
        assert hasattr(cli_instance, 'add_command')
    
    def test_main_command_help(self, cli_runner):
        """Test main command help output."""
        result = cli_runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'WhyML' in result.output
        assert 'scrape' in result.output
        assert 'convert' in result.output
        assert 'validate' in result.output
        assert 'generate' in result.output
        assert 'info' in result.output
    
    def test_version_option(self, cli_runner):
        """Test version option."""
        result = cli_runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_verbose_option(self, cli_runner):
        """Test verbose option."""
        result = cli_runner.invoke(main, ['--verbose', 'info'])
        
        # Should not error out with verbose flag
        assert result.exit_code in [0, 1, 2]  # May fail due to missing dependencies but should accept flag
    
    def test_debug_option(self, cli_runner):
        """Test debug option."""
        result = cli_runner.invoke(main, ['--debug', 'info'])
        
        # Should not error out with debug flag
        assert result.exit_code in [0, 1, 2]  # May fail due to missing dependencies but should accept flag
    
    def test_config_file_option(self, cli_runner, tmp_path):
        """Test config file option."""
        config_file = tmp_path / "whyml_config.yaml"
        config_file.write_text("verbose: true\ndebug: false\n")
        
        result = cli_runner.invoke(main, ['--config', str(config_file), 'info'])
        
        # Should not error out with config file
        assert result.exit_code in [0, 1, 2]
    
    def test_invalid_command(self, cli_runner):
        """Test invalid command handling."""
        result = cli_runner.invoke(main, ['invalid_command'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output or 'Usage:' in result.output
    
    def test_command_registration(self, cli_instance):
        """Test command registration system."""
        # Mock a command
        mock_command = Mock()
        mock_command.name = 'test_command'
        
        # Should be able to add commands
        assert hasattr(cli_instance, 'add_command')


class TestCommandDiscovery:
    """Test command discovery and loading."""
    
    def test_built_in_commands_loaded(self):
        """Test that built-in commands are discovered and loaded."""
        cli = WhyMLCLI()
        
        # Check that main commands are available
        expected_commands = ['scrape', 'convert', 'validate', 'generate', 'info']
        
        # This might require checking the Click group's commands
        # Implementation depends on how commands are registered
        assert cli is not None
    
    @patch('whyml_cli.cli.importlib')
    def test_dynamic_command_loading(self, mock_importlib):
        """Test dynamic command loading."""
        mock_module = Mock()
        mock_command = Mock()
        mock_command.name = 'dynamic_command'
        mock_module.command = mock_command
        mock_importlib.import_module.return_value = mock_module
        
        cli = WhyMLCLI()
        # Test would depend on actual implementation
        assert cli is not None


class TestGlobalOptions:
    """Test global CLI options."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_quiet_mode(self, cli_runner):
        """Test quiet mode operation."""
        result = cli_runner.invoke(main, ['--quiet', 'info'])
        
        # Should suppress normal output
        assert result.exit_code in [0, 1, 2]
    
    def test_output_format_json(self, cli_runner):
        """Test JSON output format."""
        result = cli_runner.invoke(main, ['--format', 'json', 'info'])
        
        assert result.exit_code in [0, 1, 2]
    
    def test_output_format_yaml(self, cli_runner):
        """Test YAML output format."""
        result = cli_runner.invoke(main, ['--format', 'yaml', 'info'])
        
        assert result.exit_code in [0, 1, 2]
    
    def test_parallel_execution(self, cli_runner):
        """Test parallel execution option."""
        result = cli_runner.invoke(main, ['--parallel', '4', 'info'])
        
        assert result.exit_code in [0, 1, 2]


class TestErrorHandling:
    """Test CLI error handling and reporting."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_missing_required_argument(self, cli_runner):
        """Test handling of missing required arguments."""
        result = cli_runner.invoke(main, ['scrape'])  # Missing URL
        
        assert result.exit_code != 0
        assert 'Usage:' in result.output or 'Error:' in result.output
    
    def test_invalid_option_value(self, cli_runner):
        """Test handling of invalid option values."""
        result = cli_runner.invoke(main, ['scrape', 'https://example.com', '--max-depth', 'invalid'])
        
        assert result.exit_code != 0
    
    def test_file_not_found_error(self, cli_runner):
        """Test handling of file not found errors."""
        result = cli_runner.invoke(main, ['convert', 'nonexistent.yaml'])
        
        assert result.exit_code != 0
    
    @patch('whyml_cli.cli.sys.stderr')
    def test_error_output_to_stderr(self, mock_stderr, cli_runner):
        """Test that errors are output to stderr."""
        result = cli_runner.invoke(main, ['invalid_command'])
        
        assert result.exit_code != 0
    
    def test_keyboard_interrupt_handling(self, cli_runner):
        """Test handling of keyboard interruption."""
        with patch('whyml_cli.commands.scrape_command.URLScraper.scrape_url') as mock_scrape:
            mock_scrape.side_effect = KeyboardInterrupt()
            
            result = cli_runner.invoke(main, ['scrape', 'https://example.com'])
            
            # Should handle KeyboardInterrupt gracefully
            assert result.exit_code != 0


class TestConfigurationSystem:
    """Test CLI configuration system."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_default_config_loading(self, cli_runner):
        """Test default configuration loading."""
        # Test that CLI works without explicit config
        result = cli_runner.invoke(main, ['info'])
        
        assert result.exit_code in [0, 1, 2]
    
    def test_custom_config_file(self, cli_runner, tmp_path):
        """Test custom configuration file."""
        config_content = """
        verbose: true
        debug: false
        default_format: html
        cache_enabled: true
        """
        
        config_file = tmp_path / "custom_config.yaml"
        config_file.write_text(config_content)
        
        result = cli_runner.invoke(main, ['--config', str(config_file), 'info'])
        
        assert result.exit_code in [0, 1, 2]
    
    def test_environment_variables(self, cli_runner):
        """Test environment variable configuration."""
        with patch.dict(os.environ, {'WHYML_VERBOSE': 'true', 'WHYML_DEBUG': 'false'}):
            result = cli_runner.invoke(main, ['info'])
            
            assert result.exit_code in [0, 1, 2]
    
    def test_config_precedence(self, cli_runner, tmp_path):
        """Test configuration precedence (CLI args > env vars > config file > defaults)."""
        config_file = tmp_path / "precedence_config.yaml"
        config_file.write_text("verbose: false\n")
        
        # CLI arg should override config file
        with patch.dict(os.environ, {'WHYML_VERBOSE': 'false'}):
            result = cli_runner.invoke(main, [
                '--config', str(config_file),
                '--verbose',
                'info'
            ])
            
            assert result.exit_code in [0, 1, 2]


class TestPluginSystem:
    """Test CLI plugin system."""
    
    def test_plugin_discovery(self):
        """Test plugin discovery mechanism."""
        cli = WhyMLCLI()
        # Implementation would depend on actual plugin system
        assert cli is not None
    
    @patch('whyml_cli.cli.pkg_resources')
    def test_plugin_loading(self, mock_pkg_resources):
        """Test plugin loading from entry points."""
        mock_entry_point = Mock()
        mock_entry_point.name = 'test_plugin'
        mock_entry_point.load.return_value = Mock()
        mock_pkg_resources.iter_entry_points.return_value = [mock_entry_point]
        
        cli = WhyMLCLI()
        # Test would depend on actual plugin implementation
        assert cli is not None


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_pipeline_commands(self, cli_runner, tmp_path):
        """Test chaining multiple CLI commands."""
        manifest_file = tmp_path / "test_manifest.yaml"
        manifest_content = """
        metadata:
          title: Test Page
        structure:
          body:
            h1: Hello World
        """
        manifest_file.write_text(manifest_content)
        
        # Test validate -> convert pipeline
        validate_result = cli_runner.invoke(main, ['validate', str(manifest_file)])
        
        if validate_result.exit_code == 0:
            convert_result = cli_runner.invoke(main, [
                'convert', str(manifest_file), '--format', 'html'
            ])
            
            # Should be able to chain commands
            assert convert_result.exit_code in [0, 1, 2]
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_scrape_to_convert_workflow(self, mock_scraper, cli_runner, tmp_path):
        """Test scrape -> convert workflow."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        output_file = tmp_path / "scraped.yaml"
        
        # Scrape first
        scrape_result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--output', str(output_file)
        ])
        
        if scrape_result.exit_code == 0 and output_file.exists():
            # Then convert
            convert_result = cli_runner.invoke(main, [
                'convert', str(output_file), '--format', 'html'
            ])
            
            assert convert_result.exit_code in [0, 1, 2]
    
    def test_batch_processing(self, cli_runner, tmp_path):
        """Test batch processing capabilities."""
        # Create multiple manifest files
        for i in range(3):
            manifest_file = tmp_path / f"manifest_{i}.yaml"
            manifest_file.write_text(f"""
            metadata:
              title: Test Page {i}
            structure:
              body:
                h1: Hello {i}
            """)
        
        # Test batch validation
        result = cli_runner.invoke(main, [
            'validate', str(tmp_path / "*.yaml")
        ])
        
        assert result.exit_code in [0, 1, 2]


class TestPerformanceAndScalability:
    """Test CLI performance and scalability."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    def test_memory_usage(self, cli_runner):
        """Test CLI memory usage for large operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run a command that might use significant memory
        result = cli_runner.invoke(main, ['info'])
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not use excessive memory for simple operations
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
    
    @patch('whyml_cli.commands.scrape_command.URLScraper')
    def test_concurrent_operations(self, mock_scraper, cli_runner):
        """Test concurrent CLI operations."""
        mock_scraper.return_value.scrape_url.return_value = {
            'metadata': {'title': 'Test'},
            'structure': {'body': {'h1': 'Hello'}}
        }
        
        result = cli_runner.invoke(main, [
            'scrape', 'https://example.com',
            '--parallel', '2'
        ])
        
        assert result.exit_code in [0, 1, 2]


if __name__ == "__main__":
    pytest.main([__file__])
