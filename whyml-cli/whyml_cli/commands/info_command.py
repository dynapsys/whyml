"""
WhyML CLI Info Command

Information command for displaying system info, available formats,
templates, and WhyML ecosystem status.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
import sys
import platform
from pathlib import Path
from typing import Dict, Any

from .base_command import BaseCommand


class InfoCommand(BaseCommand):
    """Command for displaying system and ecosystem information."""
    
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register info command parser."""
        parser = subparsers.add_parser(
            'info',
            help='Display system and ecosystem information',
            description='Show information about WhyML CLI, available formats, and system status',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli info
  whyml-cli info --formats
  whyml-cli info --system
  whyml-cli info --packages
  whyml-cli info --all
            """
        )
        
        # Information categories
        parser.add_argument(
            '--formats',
            action='store_true',
            help='Show available output formats'
        )
        
        parser.add_argument(
            '--commands',
            action='store_true',
            help='Show available CLI commands'
        )
        
        parser.add_argument(
            '--templates',
            action='store_true',
            help='Show available generation templates'
        )
        
        parser.add_argument(
            '--packages',
            action='store_true',
            help='Show WhyML package availability and versions'
        )
        
        parser.add_argument(
            '--system',
            action='store_true',
            help='Show system information'
        )
        
        parser.add_argument(
            '--config',
            action='store_true',
            help='Show configuration information'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all available information'
        )
        
        # Output format
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output information in JSON format'
        )
        
        return parser
    
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute info command."""
        try:
            # Gather information
            info_data = await self._gather_information(args)
            
            # Output information
            if args.json:
                await self._output_json(info_data)
            else:
                await self._output_formatted(info_data, args)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Failed to gather information: {e}")
            return 1
    
    async def _gather_information(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Gather all requested information."""
        info_data = {}
        
        # Always include basic CLI info
        info_data['cli'] = await self._get_cli_info()
        
        # Add requested categories
        if args.all or args.formats:
            info_data['formats'] = await self._get_formats_info()
        
        if args.all or args.commands:
            info_data['commands'] = await self._get_commands_info()
        
        if args.all or args.templates:
            info_data['templates'] = await self._get_templates_info()
        
        if args.all or args.packages:
            info_data['packages'] = await self._get_packages_info()
        
        if args.all or args.system:
            info_data['system'] = await self._get_system_info()
        
        if args.all or args.config:
            info_data['config'] = await self._get_config_info()
        
        return info_data
    
    async def _get_cli_info(self) -> Dict[str, Any]:
        """Get CLI basic information."""
        return {
            'name': 'whyml-cli',
            'version': self.cli._get_version(),
            'description': 'WhyML CLI - Unified interface for WhyML ecosystem',
            'ecosystem_status': self.cli.get_ecosystem_info()
        }
    
    async def _get_formats_info(self) -> Dict[str, Any]:
        """Get information about available output formats."""
        formats_info = {
            'available_formats': self.cli.get_available_formats(),
            'total_count': len(self.cli.get_available_formats()),
            'details': {}
        }
        
        # Add details for each format
        for format_name in self.cli.get_available_formats():
            converter = self.cli.converters.get(format_name)
            if converter:
                formats_info['details'][format_name] = {
                    'name': format_name.upper(),
                    'description': self._get_format_description(format_name),
                    'supports_components': converter._supports_components(),
                    'template_extension': converter._get_template_extension(),
                    'features': self._get_format_features(format_name)
                }
        
        return formats_info
    
    async def _get_commands_info(self) -> Dict[str, Any]:
        """Get information about available CLI commands."""
        commands_info = {
            'available_commands': self.cli.get_available_commands(),
            'total_count': len(self.cli.get_available_commands()),
            'details': {}
        }
        
        # Command descriptions
        command_descriptions = {
            'scrape': 'Convert websites to WhyML manifests',
            'convert': 'Generate code from WhyML manifests',
            'validate': 'Validate WhyML manifest files',
            'generate': 'Create new projects and components from templates',
            'info': 'Display system and ecosystem information'
        }
        
        for command_name in self.cli.get_available_commands():
            commands_info['details'][command_name] = {
                'name': command_name,
                'description': command_descriptions.get(command_name, 'No description available'),
                'available': True
            }
        
        return commands_info
    
    async def _get_templates_info(self) -> Dict[str, Any]:
        """Get information about available generation templates."""
        # This would be expanded with actual template discovery
        templates = {
            'basic-page': {
                'name': 'Basic Page',
                'description': 'Simple web page with header and content',
                'variables': ['name', 'description']
            },
            'blog-post': {
                'name': 'Blog Post',
                'description': 'Blog article with metadata and content',
                'variables': ['name', 'description', 'author', 'date']
            },
            'landing-page': {
                'name': 'Landing Page',
                'description': 'Marketing landing page with CTA',
                'variables': ['name', 'description', 'cta_text']
            }
        }
        
        return {
            'available_templates': list(templates.keys()),
            'total_count': len(templates),
            'details': templates
        }
    
    async def _get_packages_info(self) -> Dict[str, Any]:
        """Get information about WhyML package availability and versions."""
        packages_info = {
            'core_packages': {},
            'optional_packages': {}
        }
        
        # Core packages
        core_packages = ['whyml-core']
        for package_name in core_packages:
            try:
                version = await self._get_package_version(package_name)
                packages_info['core_packages'][package_name] = {
                    'installed': version is not None,
                    'version': version or 'unknown',
                    'status': 'available' if version else 'missing'
                }
            except Exception:
                packages_info['core_packages'][package_name] = {
                    'installed': False,
                    'version': 'unknown',
                    'status': 'error'
                }
        
        # Optional packages
        optional_packages = ['whyml-scrapers', 'whyml-converters']
        for package_name in optional_packages:
            try:
                version = await self._get_package_version(package_name)
                packages_info['optional_packages'][package_name] = {
                    'installed': version is not None,
                    'version': version or 'unknown',
                    'status': 'available' if version else 'missing',
                    'functionality': self._get_package_functionality(package_name)
                }
            except Exception:
                packages_info['optional_packages'][package_name] = {
                    'installed': False,
                    'version': 'unknown', 
                    'status': 'error',
                    'functionality': self._get_package_functionality(package_name)
                }
        
        return packages_info
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'executable': sys.executable
            },
            'environment': {
                'cwd': str(Path.cwd()),
                'home': str(Path.home()),
                'python_path': sys.path[:3]  # First 3 entries
            }
        }
    
    async def _get_config_info(self) -> Dict[str, Any]:
        """Get configuration information."""
        return {
            'config_locations': [
                str(Path.home() / '.whyml' / 'config.yaml'),
                str(Path.cwd() / 'whyml.config.yaml'),
                str(Path.cwd() / '.whyml.yaml')
            ],
            'environment_variables': {
                'WHYML_CONFIG': self._get_env_var('WHYML_CONFIG'),
                'WHYML_DEBUG': self._get_env_var('WHYML_DEBUG'),
                'WHYML_CACHE_DIR': self._get_env_var('WHYML_CACHE_DIR')
            },
            'default_settings': {
                'output_format': 'yaml',
                'validation_mode': 'standard',
                'template_engine': 'jinja2',
                'cache_enabled': True
            }
        }
    
    async def _output_json(self, info_data: Dict[str, Any]) -> None:
        """Output information in JSON format."""
        import json
        print(json.dumps(info_data, indent=2, ensure_ascii=False))
    
    async def _output_formatted(self, info_data: Dict[str, Any], args: argparse.Namespace) -> None:
        """Output information in formatted text."""
        # CLI header
        if not any([args.formats, args.commands, args.templates, args.packages, args.system, args.config]):
            await self._display_cli_header(info_data['cli'])
        
        # Display requested sections
        if 'formats' in info_data:
            await self._display_formats(info_data['formats'])
        
        if 'commands' in info_data:
            await self._display_commands(info_data['commands'])
        
        if 'templates' in info_data:
            await self._display_templates(info_data['templates'])
        
        if 'packages' in info_data:
            await self._display_packages(info_data['packages'])
        
        if 'system' in info_data:
            await self._display_system(info_data['system'])
        
        if 'config' in info_data:
            await self._display_config(info_data['config'])
    
    async def _display_cli_header(self, cli_info: Dict[str, Any]) -> None:
        """Display CLI header information."""
        print("🚀 WhyML CLI")
        print("=" * 50)
        print(f"Version: {cli_info['version']}")
        print(f"Description: {cli_info['description']}")
        print()
        
        ecosystem = cli_info['ecosystem_status']
        print("📦 Ecosystem Status:")
        print(f"  Core: {'✓' if ecosystem['whyml_core'] else '✗'}")
        print(f"  Scrapers: {'✓' if ecosystem['whyml_scrapers'] else '✗'}")
        print(f"  Converters: {'✓' if ecosystem['whyml_converters'] else '✗'}")
        print(f"  Available Formats: {len(ecosystem['available_formats'])}")
        print()
    
    async def _display_formats(self, formats_info: Dict[str, Any]) -> None:
        """Display available formats information."""
        print("🎨 Available Output Formats")
        print("=" * 50)
        print(f"Total Formats: {formats_info['total_count']}")
        print()
        
        for format_name, details in formats_info['details'].items():
            print(f"📄 {details['name']}")
            print(f"   Description: {details['description']}")
            print(f"   Extension: {details['template_extension']}")
            print(f"   Components: {'Yes' if details['supports_components'] else 'No'}")
            if details['features']:
                print(f"   Features: {', '.join(details['features'])}")
            print()
    
    async def _display_commands(self, commands_info: Dict[str, Any]) -> None:
        """Display available commands information."""
        print("⌨️ Available CLI Commands")
        print("=" * 50)
        print(f"Total Commands: {commands_info['total_count']}")
        print()
        
        for command_name, details in commands_info['details'].items():
            status = "✓" if details['available'] else "✗"
            print(f"{status} {details['name']}")
            print(f"   {details['description']}")
            print()
    
    async def _display_templates(self, templates_info: Dict[str, Any]) -> None:
        """Display available templates information."""
        print("📋 Available Generation Templates")
        print("=" * 50)
        print(f"Total Templates: {templates_info['total_count']}")
        print()
        
        for template_name, details in templates_info['details'].items():
            print(f"📝 {template_name}")
            print(f"   Name: {details['name']}")
            print(f"   Description: {details['description']}")
            if details['variables']:
                print(f"   Variables: {', '.join(details['variables'])}")
            print()
    
    async def _display_packages(self, packages_info: Dict[str, Any]) -> None:
        """Display package information."""
        print("📦 WhyML Package Status")
        print("=" * 50)
        
        print("Core Packages:")
        for package_name, details in packages_info['core_packages'].items():
            status = "✓" if details['installed'] else "✗"
            print(f"  {status} {package_name} ({details['version']})")
        
        print("\nOptional Packages:")
        for package_name, details in packages_info['optional_packages'].items():
            status = "✓" if details['installed'] else "✗"
            print(f"  {status} {package_name} ({details['version']})")
            if 'functionality' in details:
                print(f"     Functionality: {details['functionality']}")
        print()
    
    async def _display_system(self, system_info: Dict[str, Any]) -> None:
        """Display system information."""
        print("💻 System Information")
        print("=" * 50)
        
        platform_info = system_info['platform']
        print(f"Platform: {platform_info['system']} {platform_info['release']}")
        print(f"Machine: {platform_info['machine']}")
        
        python_info = system_info['python']
        print(f"Python: {python_info['version']} ({python_info['implementation']})")
        print(f"Executable: {python_info['executable']}")
        
        env_info = system_info['environment']
        print(f"Working Directory: {env_info['cwd']}")
        print()
    
    async def _display_config(self, config_info: Dict[str, Any]) -> None:
        """Display configuration information."""
        print("⚙️ Configuration Information")
        print("=" * 50)
        
        print("Config File Locations:")
        for location in config_info['config_locations']:
            exists = Path(location).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {location}")
        
        print("\nEnvironment Variables:")
        for var, value in config_info['environment_variables'].items():
            print(f"  {var}: {value or 'not set'}")
        
        print("\nDefault Settings:")
        for key, value in config_info['default_settings'].items():
            print(f"  {key}: {value}")
        print()
    
    # Helper methods
    
    def _get_format_description(self, format_name: str) -> str:
        """Get description for output format."""
        descriptions = {
            'html': 'Semantic HTML5 with modern standards',
            'react': 'React JSX components with hooks and TypeScript support',
            'vue': 'Vue.js Single File Components with Composition API',
            'php': 'Modern PHP classes with security best practices'
        }
        return descriptions.get(format_name, 'No description available')
    
    def _get_format_features(self, format_name: str) -> list:
        """Get features list for output format."""
        features = {
            'html': ['semantic-structure', 'accessibility', 'responsive', 'seo-optimized'],
            'react': ['typescript', 'hooks', 'css-in-js', 'component-props'],
            'vue': ['composition-api', 'scoped-css', 'typescript', 'sfc'],
            'php': ['classes', 'namespaces', 'strict-types', 'security']
        }
        return features.get(format_name, [])
    
    async def _get_package_version(self, package_name: str) -> str:
        """Get version of installed package."""
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name.replace('-', '_'))
        except Exception:
            return None
    
    def _get_package_functionality(self, package_name: str) -> str:
        """Get functionality description for package."""
        functionality = {
            'whyml-scrapers': 'Web scraping and manifest generation',
            'whyml-converters': 'Multi-format code generation'
        }
        return functionality.get(package_name, 'Unknown functionality')
    
    def _get_env_var(self, var_name: str) -> str:
        """Get environment variable value."""
        import os
        return os.getenv(var_name)
