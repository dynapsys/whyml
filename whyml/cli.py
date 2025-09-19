#!/usr/bin/env python3
"""
WhyML Command Line Interface

Provides command-line tools for WhyML manifest processing, conversion,
and development server functionality.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import json
import yaml
from dotenv import load_dotenv

from . import __version__, show_logo
from .processor import WhyMLProcessor
from .exceptions import WhyMLError
from .server import WhyMLServer
from .caddy import CaddyConfig


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='whyml',
        description='WhyML - Advanced YAML Manifest System',
        epilog='For more information, visit: https://github.com/dynapsys/whyml'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'WhyML {__version__}'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # whyml run command
    run_parser = subparsers.add_parser(
        'run',
        help='Start development server with manifest'
    )
    run_parser.add_argument(
        '-f', '--file',
        default='manifest.yaml',
        help='Manifest file to serve (default: manifest.yaml)'
    )
    run_parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Port to run server on (default: 8080)'
    )
    run_parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind server to (default: localhost)'
    )
    run_parser.add_argument(
        '--tls-provider',
        choices=['letsencrypt', 'internal', 'custom'],
        help='TLS certificate provider for production'
    )
    run_parser.add_argument(
        '--caddy-config',
        help='Generate Caddy configuration file'
    )
    run_parser.add_argument(
        '--watch',
        action='store_true',
        help='Enable file watching and auto-reload'
    )
    run_parser.add_argument(
        '--api-debug',
        action='store_true',
        help='Enable API debug endpoints and enhanced logging'
    )
    
    # Natural language conversion syntax
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert manifest using natural language syntax'
    )
    convert_parser.add_argument(
        '--from',
        dest='source',
        required=True,
        help='Source manifest file'
    )
    convert_parser.add_argument(
        '--to',
        dest='target',
        required=True,
        help='Target output file'
    )
    convert_parser.add_argument(
        '-as', '--as',
        dest='format',
        choices=['html', 'react', 'vue', 'php', 'spa', 'pwa', 'docker', 'tauri'],
        default='html',
        help='Output format'
    )
    convert_parser.add_argument(
        '--config',
        help='Configuration file (JSON or YAML)'
    )
    convert_parser.add_argument(
        '--env-file',
        help='Environment file (.env) for variable substitution'
    )
    
    # Generate command for various app types
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate application artifacts'
    )
    generate_parser.add_argument(
        'type',
        choices=['pwa', 'spa', 'apk', 'docker', 'tauri', 'caddy'],
        help='Type of artifact to generate'
    )
    generate_parser.add_argument(
        '-f', '--file',
        default='manifest.yaml',
        help='Source manifest file'
    )
    generate_parser.add_argument(
        '-o', '--output',
        help='Output directory or file'
    )
    generate_parser.add_argument(
        '--config',
        help='Configuration file for the generator'
    )
    
    # Serve command (alias for run)
    serve_parser = subparsers.add_parser(
        'serve',
        help='Start development server (alias for run)'
    )
    serve_parser.add_argument(
        '-f', '--file',
        default='manifest.yaml',
        help='Manifest file to serve (default: manifest.yaml)'
    )
    serve_parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Port to run server on (default: 8080)'
    )
    serve_parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind server to (default: localhost)'
    )
    serve_parser.add_argument(
        '--watch',
        action='store_true',
        help='Enable file watching and auto-reload'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate manifest file'
    )
    validate_parser.add_argument(
        'file',
        help='Manifest file to validate'
    )
    
    # Scrape command
    scrape_parser = subparsers.add_parser(
        'scrape',
        help='Scrape website to generate manifest'
    )
    scrape_parser.add_argument(
        'url',
        help='URL to scrape'
    )
    scrape_parser.add_argument(
        '-o', '--output',
        default='scraped-manifest.yaml',
        help='Output manifest file'
    )
    
    return parser


async def run_command(args) -> int:
    """Handle the run/serve command."""
    try:
        # Load environment variables if specified
        if hasattr(args, 'env_file') and args.env_file:
            load_dotenv(args.env_file)
        
        # Check if manifest file exists
        if not Path(args.file).exists():
            print(f"Error: Manifest file '{args.file}' not found")
            return 1
        
        # Generate Caddy configuration if requested
        if hasattr(args, 'caddy_config') and args.caddy_config:
            caddy_config = CaddyConfig()
            config = await caddy_config.generate_config(
                manifest_file=args.file,
                host=args.host,
                port=args.port,
                tls_provider=getattr(args, 'tls_provider', None)
            )
            
            with open(args.caddy_config, 'w') as f:
                f.write(config)
            
            print(f"Caddy configuration written to {args.caddy_config}")
        
        # Start the development server
        server = WhyMLServer(
            manifest_file=args.file,
            host=args.host,
            port=args.port,
            watch=getattr(args, 'watch', False),
            api_debug=getattr(args, 'api_debug', False)
        )
        
        print(f"Starting WhyML server on http://{args.host}:{args.port}")
        print(f"Serving manifest: {args.file}")
        
        await server.start()
        
    except WhyMLError as e:
        print(f"WhyML Error: {e}")
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        return 1
    
    return 0


async def convert_command(args) -> int:
    """Handle the convert command with natural language syntax."""
    try:
        # Load environment variables
        if args.env_file:
            load_dotenv(args.env_file)
        
        # Load configuration
        config = {}
        if args.config:
            with open(args.config) as f:
                if args.config.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
        
        # Initialize processor
        processor = WhyMLProcessor(config=config)
        
        # Determine output format and perform conversion
        format_mapping = {
            'html': 'convert_to_html',
            'react': 'convert_to_react', 
            'vue': 'convert_to_vue',
            'php': 'convert_to_php',
            'spa': 'convert_to_spa',
            'pwa': 'convert_to_pwa',
            'docker': 'generate_docker',
            'tauri': 'generate_tauri'
        }
        
        converter_method = format_mapping.get(args.format)
        if not converter_method:
            print(f"Unsupported format: {args.format}")
            return 1
        
        # Perform conversion
        method = getattr(processor, converter_method)
        result = await method(args.source)
        
        # Save result
        result.save_to_file(args.target)
        
        print(f"Successfully converted {args.source} to {args.target} as {args.format}")
        
    except WhyMLError as e:
        print(f"WhyML Error: {e}")
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        return 1
    
    return 0


async def generate_command(args) -> int:
    """Handle the generate command for various artifacts."""
    try:
        processor = WhyMLProcessor()
        
        generators = {
            'pwa': processor.generate_pwa,
            'spa': processor.generate_spa,
            'apk': processor.generate_apk,
            'docker': processor.generate_docker,
            'tauri': processor.generate_tauri,
            'caddy': processor.generate_caddy_config
        }
        
        generator = generators.get(args.type)
        if not generator:
            print(f"Unsupported generator type: {args.type}")
            return 1
        
        # Load configuration if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                if args.config.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
        
        # Generate artifact
        result = await generator(args.file, output=args.output, config=config)
        
        if args.output:
            output_path = args.output
        else:
            output_path = f"{Path(args.file).stem}-{args.type}"
        
        print(f"Generated {args.type} artifact: {output_path}")
        
    except WhyMLError as e:
        print(f"WhyML Error: {e}")
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        return 1
    
    return 0


async def validate_command(args) -> int:
    """Handle the validate command."""
    try:
        processor = WhyMLProcessor()
        is_valid, errors = await processor.validate_manifest(args.file)
        
        if is_valid:
            print(f"✓ Manifest {args.file} is valid")
            return 0
        else:
            print(f"✗ Manifest {args.file} has errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
            
    except Exception as e:
        print(f"Error validating manifest: {e}")
        return 1


async def scrape_command(args) -> int:
    """Handle the scrape command."""
    try:
        processor = WhyMLProcessor()
        manifest = await processor.scrape_url_to_manifest(args.url)
        
        # Save manifest
        with open(args.output, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        
        print(f"Successfully scraped {args.url} to {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return 1


async def main_async() -> int:
    """Main async entry point."""
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        show_logo()
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command in ['run', 'serve']:
        return await run_command(args)
    elif args.command == 'convert':
        return await convert_command(args)
    elif args.command == 'generate':
        return await generate_command(args)
    elif args.command == 'validate':
        return await validate_command(args)
    elif args.command == 'scrape':
        return await scrape_command(args)
    else:
        parser.print_help()
        return 1


def main():
    """Main entry point for CLI."""
    try:
        exit_code = asyncio.run(main_async())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
