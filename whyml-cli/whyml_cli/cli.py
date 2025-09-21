"""
WhyML CLI - Core CLI Class

Main CLI controller class that coordinates all WhyML ecosystem functionality
including scraping, conversion, validation, and generation workflows.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import argparse
import json
import yaml

from whyml_core.exceptions import WhyMLError, ValidationError, ProcessingError
from whyml_core.loading import ManifestLoader
from whyml_core.processing import TemplateProcessor, InheritanceResolver, VariableSubstitution
from whyml_core.validation import ManifestValidator
from whyml_core.utils import PathUtils, StringUtils, YAMLUtils

try:
    from whyml_scrapers import URLScraper, WebpageAnalyzer
except ImportError:
    URLScraper = None
    WebpageAnalyzer = None

try:
    from whyml_converters import HTMLConverter, ReactConverter, VueConverter, PHPConverter
except ImportError:
    HTMLConverter = None
    ReactConverter = None
    VueConverter = None
    PHPConverter = None

from .commands import (
    ScrapeCommand,
    ConvertCommand, 
    ValidateCommand,
    GenerateCommand,
    InfoCommand
)


class WhyMLCLI:
    """Main CLI controller for WhyML ecosystem."""
    
    def __init__(self):
        """Initialize CLI controller."""
        self.loader = ManifestLoader()
        self.validator = ManifestValidator()
        self.template_processor = TemplateProcessor()
        self.inheritance_resolver = InheritanceResolver()
        self.variable_substitution = VariableSubstitution()
        
        # Initialize converters if available
        self.converters = {}
        if HTMLConverter:
            self.converters['html'] = HTMLConverter()
        if ReactConverter:
            self.converters['react'] = ReactConverter()
        if VueConverter:
            self.converters['vue'] = VueConverter()
        if PHPConverter:
            self.converters['php'] = PHPConverter()
        
        # Initialize scraper if available
        self.scraper = URLScraper() if URLScraper else None
        
        # Command handlers
        self.commands = {
            'scrape': ScrapeCommand(self),
            'convert': ConvertCommand(self),
            'validate': ValidateCommand(self),
            'generate': GenerateCommand(self),
            'info': InfoCommand(self)
        }
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create main argument parser."""
        parser = argparse.ArgumentParser(
            prog='whyml-cli',
            description='WhyML CLI - Unified interface for WhyML ecosystem',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli scrape https://example.com --output manifest.yaml
  whyml-cli convert manifest.yaml --format html --output index.html
  whyml-cli validate manifest.yaml
  whyml-cli generate --format react --name MyComponent --output src/
  whyml-cli info --formats

For more help on a specific command:
  whyml-cli <command> --help
            """
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version=f'whyml-cli {self._get_version()}'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Configuration file path'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='command'
        )
        
        # Register command parsers
        for name, command in self.commands.items():
            command.register_parser(subparsers)
        
        return parser
    
    async def run(self, args: List[str] = None) -> int:
        """Run CLI with arguments.
        
        Args:
            args: Command line arguments (default: sys.argv[1:])
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        if args is None:
            args = sys.argv[1:]
        
        parser = self.create_parser()
        
        # Parse arguments
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit as e:
            return e.code or 0
        
        # Configure logging/output
        self._configure_output(parsed_args)
        
        # Load configuration if specified
        if parsed_args.config:
            await self._load_config(parsed_args.config)
        
        # Handle command
        if not parsed_args.command:
            parser.print_help()
            return 0
        
        try:
            command = self.commands[parsed_args.command]
            return await command.execute(parsed_args)
            
        except WhyMLError as e:
            self._print_error(f"WhyML Error: {e}")
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 1
            
        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    async def load_manifest(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load and validate manifest from path.
        
        Args:
            path: Path to manifest file or URL
            
        Returns:
            Loaded and validated manifest
            
        Raises:
            ValidationError: If manifest is invalid
            ProcessingError: If loading fails
        """
        manifest = await self.loader.load_manifest(str(path))
        
        # Validate manifest
        validation_result = await self.validator.validate_manifest(manifest)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Manifest validation failed: {validation_result.errors}"
            )
        
        return manifest
    
    async def process_manifest(self, manifest: Dict[str, Any], **options) -> Dict[str, Any]:
        """Process manifest with full pipeline.
        
        Args:
            manifest: Raw manifest data
            **options: Processing options
            
        Returns:
            Processed manifest
        """
        # Resolve inheritance
        if options.get('resolve_inheritance', True):
            manifest = await self.inheritance_resolver.resolve_inheritance(manifest)
        
        # Process templates
        if options.get('process_templates', True):
            manifest = await self.template_processor.process_templates(manifest)
        
        # Substitute variables
        if options.get('substitute_variables', True):
            manifest = await self.variable_substitution.substitute_variables(manifest)
        
        return manifest
    
    async def convert_manifest(self, 
                             manifest: Dict[str, Any], 
                             format: str, 
                             output_path: Optional[Union[str, Path]] = None,
                             **options) -> str:
        """Convert manifest to target format.
        
        Args:
            manifest: Processed manifest
            format: Target format (html, react, vue, php)
            output_path: Optional output file path
            **options: Format-specific options
            
        Returns:
            Generated content
            
        Raises:
            ProcessingError: If conversion fails
        """
        if format not in self.converters:
            available = ', '.join(self.converters.keys())
            raise ProcessingError(
                f"Format '{format}' not available. Available formats: {available}"
            )
        
        converter = self.converters[format]
        
        if output_path:
            await converter.save_to_file(manifest, output_path, **options)
            return f"Saved to {output_path}"
        else:
            return await converter.convert_manifest(manifest, **options)
    
    async def scrape_url(self, 
                        url: str, 
                        output_path: Optional[Union[str, Path]] = None,
                        **options) -> Dict[str, Any]:
        """Scrape URL to WhyML manifest.
        
        Args:
            url: URL to scrape
            output_path: Optional output file path
            **options: Scraping options
            
        Returns:
            Generated manifest
            
        Raises:
            ProcessingError: If scraping not available or fails
        """
        if not self.scraper:
            raise ProcessingError(
                "Web scraping not available. Install whyml-scrapers package."
            )
        
        manifest = await self.scraper.scrape_to_manifest(url, **options)
        
        if output_path:
            await self._save_manifest(manifest, output_path)
        
        return manifest
    
    async def _save_manifest(self, manifest: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save manifest to file."""
        path = Path(path)
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format by extension
        if path.suffix.lower() in ['.yaml', '.yml']:
            content = yaml.dump(manifest, default_flow_style=False, sort_keys=False)
        elif path.suffix.lower() == '.json':
            content = json.dumps(manifest, indent=2, ensure_ascii=False)
        else:
            # Default to YAML
            content = yaml.dump(manifest, default_flow_style=False, sort_keys=False)
        
        # Write file
        path.write_text(content, encoding='utf-8')
    
    async def _load_config(self, config_path: str) -> None:
        """Load CLI configuration from file."""
        try:
            config_path = Path(config_path)
            if config_path.exists():
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config = YAMLUtils.load_yaml(config_path)
                elif config_path.suffix.lower() == '.json':
                    config = json.loads(config_path.read_text(encoding='utf-8'))
                else:
                    raise ProcessingError(f"Unsupported config format: {config_path.suffix}")
                
                # Apply configuration to components
                await self._apply_config(config)
                
        except Exception as e:
            raise ProcessingError(f"Failed to load configuration: {e}")
    
    async def _apply_config(self, config: Dict[str, Any]) -> None:
        """Apply configuration to CLI components."""
        # Configure core components
        if 'core' in config:
            core_config = config['core']
            if 'validation' in core_config and hasattr(self.validator, 'configure'):
                await self.validator.configure(core_config['validation'])
            if 'loading' in core_config and hasattr(self.loader, 'configure'):
                await self.loader.configure(core_config['loading'])
        
        # Configure converters
        if 'converters' in config:
            for format_name, format_config in config['converters'].items():
                if format_name in self.converters:
                    converter = self.converters[format_name]
                    if hasattr(converter, 'configure'):
                        await converter.configure(format_config)
        
        # Configure scraper
        if 'scraper' in config and self.scraper:
            if hasattr(self.scraper, 'configure'):
                await self.scraper.configure(config['scraper'])
    
    def _configure_output(self, args: argparse.Namespace) -> None:
        """Configure output verbosity and formatting."""
        import logging
        
        if args.debug:
            level = logging.DEBUG
        elif args.verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _print_error(self, message: str) -> None:
        """Print error message to stderr."""
        print(f"Error: {message}", file=sys.stderr)
    
    def _print_info(self, message: str) -> None:
        """Print info message to stdout."""
        print(message)
    
    def _print_success(self, message: str) -> None:
        """Print success message to stdout."""
        print(f"✓ {message}")
    
    def _get_version(self) -> str:
        """Get CLI version."""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def get_available_formats(self) -> List[str]:
        """Get list of available output formats."""
        return list(self.converters.keys())
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return list(self.commands.keys())
    
    def is_scraping_available(self) -> bool:
        """Check if web scraping functionality is available."""
        return self.scraper is not None
    
    def get_ecosystem_info(self) -> Dict[str, Any]:
        """Get information about WhyML ecosystem availability."""
        return {
            'whyml_core': True,  # Always available
            'whyml_scrapers': self.scraper is not None,
            'whyml_converters': len(self.converters) > 0,
            'available_formats': self.get_available_formats(),
            'available_commands': self.get_available_commands(),
            'version': self._get_version()
        }
