"""
WhyML CLI Convert Command

Manifest conversion command for generating code from WhyML manifests
using the whyml-converters package functionality.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
from pathlib import Path
from typing import Dict, Any

from whyml_core.exceptions import ProcessingError, ValidationError
from .base_command import BaseCommand


class ConvertCommand(BaseCommand):
    """Command for converting WhyML manifests to code."""
    
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register convert command parser."""
        parser = subparsers.add_parser(
            'convert',
            help='Convert WhyML manifests to code',
            description='Generate code from WhyML manifest files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli convert manifest.yaml --format html --output index.html
  whyml-cli convert manifest.yaml --format react --typescript --output App.tsx
  whyml-cli convert manifest.yaml --format vue --composition-api --output App.vue
  whyml-cli convert manifest.yaml --format php --namespace "App\\Pages" --output Page.php
            """
        )
        
        # Required arguments
        parser.add_argument(
            'manifest',
            type=lambda x: self.validate_file_path(x, must_exist=True),
            help='WhyML manifest file to convert'
        )
        
        # Format and output
        parser.add_argument(
            '--format', '-f',
            type=self.validate_format,
            required=True,
            help='Output format (html, react, vue, php)'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file path (default: stdout)'
        )
        
        # Processing options
        parser.add_argument(
            '--no-inheritance',
            action='store_true',
            help='Skip inheritance resolution'
        )
        
        parser.add_argument(
            '--no-templates',
            action='store_true',
            help='Skip template processing'
        )
        
        parser.add_argument(
            '--no-variables',
            action='store_true',
            help='Skip variable substitution'
        )
        
        # HTML-specific options
        html_group = parser.add_argument_group('HTML Options')
        html_group.add_argument(
            '--html-version',
            choices=['5', 'html5', '4.01'],
            default='5',
            help='HTML version (default: 5)'
        )
        
        html_group.add_argument(
            '--semantic-structure',
            action='store_true',
            default=True,
            help='Use semantic HTML5 elements (default: true)'
        )
        
        html_group.add_argument(
            '--no-semantic-structure',
            dest='semantic_structure',
            action='store_false',
            help='Disable semantic structure'
        )
        
        html_group.add_argument(
            '--css-framework',
            choices=['bootstrap', 'tailwind', 'bulma', 'none'],
            help='CSS framework integration'
        )
        
        html_group.add_argument(
            '--minify',
            action='store_true',
            help='Minify HTML output'
        )
        
        # React-specific options
        react_group = parser.add_argument_group('React Options')
        react_group.add_argument(
            '--typescript',
            action='store_true',
            help='Generate TypeScript code'
        )
        
        react_group.add_argument(
            '--component-type',
            choices=['functional', 'class'],
            default='functional',
            help='Component type (default: functional)'
        )
        
        react_group.add_argument(
            '--use-hooks',
            action='store_true',
            default=True,
            help='Use React Hooks (default: true)'
        )
        
        react_group.add_argument(
            '--css-in-js',
            action='store_true',
            help='Use CSS-in-JS styling'
        )
        
        react_group.add_argument(
            '--component-name',
            type=str,
            help='Custom component name'
        )
        
        # Vue-specific options
        vue_group = parser.add_argument_group('Vue Options')
        vue_group.add_argument(
            '--composition-api',
            action='store_true',
            default=True,
            help='Use Composition API (default: true)'
        )
        
        vue_group.add_argument(
            '--options-api',
            dest='composition_api',
            action='store_false',
            help='Use Options API instead of Composition API'
        )
        
        vue_group.add_argument(
            '--scoped-css',
            action='store_true',
            default=True,
            help='Use scoped CSS (default: true)'
        )
        
        vue_group.add_argument(
            '--css-preprocessor',
            choices=['scss', 'sass', 'less', 'stylus'],
            help='CSS preprocessor'
        )
        
        # PHP-specific options
        php_group = parser.add_argument_group('PHP Options')
        php_group.add_argument(
            '--namespace',
            type=str,
            help='PHP namespace'
        )
        
        php_group.add_argument(
            '--class-name',
            type=str,
            help='Custom class name'
        )
        
        php_group.add_argument(
            '--procedural',
            action='store_true',
            help='Use procedural style instead of classes'
        )
        
        php_group.add_argument(
            '--php-version',
            choices=['7.4', '8.0', '8.1', '8.2', '8.3'],
            default='8.1',
            help='Target PHP version (default: 8.1)'
        )
        
        php_group.add_argument(
            '--strict-types',
            action='store_true',
            default=True,
            help='Use strict type declarations (default: true)'
        )
        
        return parser
    
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute convert command."""
        try:
            # Load and validate manifest
            self.print_info(f"Loading manifest: {args.manifest}")
            manifest = await self.cli.load_manifest(args.manifest)
            
            # Process manifest
            processing_options = {
                'resolve_inheritance': not args.no_inheritance,
                'process_templates': not args.no_templates,
                'substitute_variables': not args.no_variables
            }
            
            self.print_info("Processing manifest...")
            manifest = await self.cli.process_manifest(manifest, **processing_options)
            
            # Prepare conversion options
            conversion_options = self._prepare_conversion_options(args)
            
            # Determine output path
            output_path = self._determine_output_path(args)
            
            # Convert manifest
            self.print_info(f"Converting to {args.format.upper()} format...")
            result = await self.cli.convert_manifest(
                manifest,
                args.format,
                output_path=output_path,
                **conversion_options
            )
            
            # Output result
            if output_path:
                self.print_success(f"Generated {args.format.upper()} code saved to {output_path}")
            else:
                # Print to stdout
                print(result)
            
            return 0
            
        except ValidationError as e:
            self.print_error(f"Manifest validation failed: {e}")
            return 1
        except ProcessingError as e:
            self.print_error(f"Conversion failed: {e}")
            return 1
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return 1
    
    def _prepare_conversion_options(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Prepare format-specific conversion options."""
        options = {}
        
        if args.format == 'html':
            options.update({
                'html_version': args.html_version,
                'semantic_structure': args.semantic_structure,
                'minify': args.minify
            })
            
            if args.css_framework:
                options['css_framework'] = args.css_framework
        
        elif args.format == 'react':
            options.update({
                'typescript': args.typescript,
                'component_type': args.component_type,
                'use_hooks': args.use_hooks,
                'css_in_js': args.css_in_js
            })
            
            if args.component_name:
                options['component_name'] = args.component_name
        
        elif args.format == 'vue':
            options.update({
                'typescript': args.typescript,
                'composition_api': args.composition_api,
                'scoped': args.scoped_css
            })
            
            if args.css_preprocessor:
                options['css_preprocessor'] = args.css_preprocessor
            
            if args.component_name:
                options['component_name'] = args.component_name
        
        elif args.format == 'php':
            options.update({
                'use_classes': not args.procedural,
                'php_version': args.php_version,
                'strict_types': args.strict_types
            })
            
            if args.namespace:
                options['namespace'] = args.namespace
            
            if args.class_name:
                options['class_name'] = args.class_name
        
        return options
    
    def _determine_output_path(self, args: argparse.Namespace) -> Path:
        """Determine output path from arguments."""
        if not args.output:
            return None
        
        # Format-specific extensions
        extensions = {
            'html': '.html',
            'react': '.tsx' if args.typescript else '.jsx',
            'vue': '.vue',
            'php': '.php'
        }
        
        # Get default filename
        manifest_name = args.manifest.stem
        default_name = f"{manifest_name}_converted"
        
        return self.create_output_path(
            args.output,
            default_name,
            extensions.get(args.format, '.txt')
        )
