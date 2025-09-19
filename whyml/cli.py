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
    run_parser.add_argument(
        '--rss',
        action='store_true',
        help='Enable RSS feed for file changes at /rss/changes.xml'
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
        help='Scrape website to generate manifest with advanced simplification options'
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
    
    # Structure simplification options
    scrape_parser.add_argument(
        '--max-depth',
        type=int,
        help='Maximum nesting depth for structure (reduces deep HTML nesting)'
    )
    scrape_parser.add_argument(
        '--flatten-containers',
        action='store_true',
        help='Merge wrapper/container divs with minimal semantic value'
    )
    scrape_parser.add_argument(
        '--simplify-structure',
        action='store_true',
        help='Apply general structure simplification rules'
    )
    scrape_parser.add_argument(
        '--no-preserve-semantic',
        action='store_true',
        help='Do not preserve semantic HTML5 tags during simplification'
    )
    
    # Selective section generation
    scrape_parser.add_argument(
        '--section',
        action='append',
        choices=['metadata', 'styles', 'structure', 'imports', 'analysis'],
        help='Only generate specific sections (can be used multiple times)'
    )
    scrape_parser.add_argument(
        '--no-styles',
        action='store_true',
        help='Skip CSS style extraction'
    )
    scrape_parser.add_argument(
        '--extract-scripts',
        action='store_true',
        help='Include JavaScript files in imports'
    )
    
    # Testing and comparison options
    scrape_parser.add_argument(
        '--test-conversion',
        action='store_true',
        help='Test conversion workflow: scrape → YAML → HTML and compare with original'
    )
    scrape_parser.add_argument(
        '--output-html',
        help='Output file for regenerated HTML (for testing conversion accuracy)'
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
            api_debug=getattr(args, 'api_debug', False),
            rss_enabled=getattr(args, 'rss', False)
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
    """Handle the scrape command with advanced simplification options."""
    try:
        processor = WhyMLProcessor()
        
        # Prepare parameters for advanced scraping
        scrape_params = {
            'extract_styles': not args.no_styles,
            'extract_scripts': args.extract_scripts,
            'max_depth': args.max_depth,
            'flatten_containers': args.flatten_containers,
            'simplify_structure': args.simplify_structure,
            'preserve_semantic_tags': not args.no_preserve_semantic,
            'sections': args.section  # CLI collects multiple --section flags into a list
        }
        
        # Scrape with advanced parameters
        manifest = await processor.scrape_url_to_manifest(args.url, **scrape_params)
        
        # Save manifest
        with open(args.output, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(f"Successfully scraped {args.url} to {args.output}")
        
        # Print simplification report
        if any([args.max_depth, args.flatten_containers, args.simplify_structure]):
            print("\n📊 Structure Simplification Applied:")
            if args.max_depth:
                print(f"   • Maximum depth limited to: {args.max_depth}")
            if args.flatten_containers:
                print("   • Container divs flattened")
            if args.simplify_structure:
                print("   • General structure simplification applied")
        
        # Print section filtering report
        if args.section:
            print(f"\n🎯 Sections Generated: {', '.join(args.section)}")
        
        # Run conversion testing workflow if requested
        if args.test_conversion:
            return await _test_conversion_workflow(args.url, args.output, args.output_html, manifest)
        
        return 0
        
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return 1


async def _test_conversion_workflow(url: str, manifest_file: str, output_html: Optional[str], manifest: Dict[str, Any]) -> int:
    """
    Test conversion workflow: scrape → YAML → HTML and compare with original.
    
    This tests the round-trip accuracy of the scraping and conversion process.
    """
    try:
        import requests
        from difflib import unified_diff
        import tempfile
        
        print("\n🧪 Testing Conversion Workflow:")
        print("=" * 50)
        
        # Step 1: Fetch original HTML
        print("📥 1. Fetching original HTML...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        original_html = response.text
        
        # Step 2: Convert manifest back to HTML
        print("🔄 2. Converting manifest back to HTML...")
        processor = WhyMLProcessor()
        
        # Load the saved manifest
        with open(manifest_file, 'r') as f:
            loaded_manifest = yaml.safe_load(f)
        
        # Convert to HTML
        conversion_result = await processor.convert_manifest(loaded_manifest, 'html')
        regenerated_html = conversion_result.content
        
        # Step 3: Save regenerated HTML if output file specified
        if output_html:
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(regenerated_html)
            print(f"💾 3. Saved regenerated HTML to: {output_html}")
        else:
            # Create temporary file for comparison
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(regenerated_html)
                output_html = f.name
                print(f"💾 3. Created temporary HTML file: {output_html}")
        
        # Step 4: Analyze differences
        print("📊 4. Analyzing conversion accuracy...")
        
        # Basic content comparison
        original_text = _extract_text_content(original_html)
        regenerated_text = _extract_text_content(regenerated_html)
        
        text_similarity = _calculate_text_similarity(original_text, regenerated_text)
        
        # Structure comparison
        original_structure = _analyze_html_structure(original_html)
        regenerated_structure = _analyze_html_structure(regenerated_html)
        
        # Report results
        print("\n📈 CONVERSION TEST RESULTS:")
        print("=" * 40)
        print(f"Text Content Similarity: {text_similarity:.1%}")
        print(f"Original HTML Size: {len(original_html):,} chars")
        print(f"Regenerated HTML Size: {len(regenerated_html):,} chars")
        print(f"Size Difference: {((len(regenerated_html) - len(original_html)) / len(original_html) * 100):+.1f}%")
        
        print(f"\nStructure Comparison:")
        print(f"  Original Elements: {original_structure['total_elements']}")
        print(f"  Regenerated Elements: {regenerated_structure['total_elements']}")
        print(f"  Original Max Depth: {original_structure['max_depth']}")
        print(f"  Regenerated Max Depth: {regenerated_structure['max_depth']}")
        
        # Show content preservation
        print(f"\nContent Preservation:")
        print(f"  Original Word Count: {len(original_text.split())}")
        print(f"  Regenerated Word Count: {len(regenerated_text.split())}")
        print(f"  Word Count Difference: {((len(regenerated_text.split()) - len(original_text.split())) / len(original_text.split()) * 100):+.1f}%")
        
        # Generate diff sample if significant differences
        if text_similarity < 0.8:
            print(f"\n⚠️  Text similarity is low ({text_similarity:.1%}). Showing content diff sample:")
            _show_text_diff_sample(original_text, regenerated_text)
        
        # Success criteria
        if text_similarity > 0.7 and abs(len(regenerated_text.split()) - len(original_text.split())) / len(original_text.split()) < 0.5:
            print(f"\n✅ CONVERSION TEST PASSED: Good content preservation achieved!")
            success_code = 0
        elif text_similarity > 0.5:
            print(f"\n⚠️  CONVERSION TEST PARTIAL: Reasonable content preservation, but room for improvement.")
            success_code = 0
        else:
            print(f"\n❌ CONVERSION TEST FAILED: Significant content loss detected.")
            success_code = 1
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if regenerated_structure['max_depth'] < original_structure['max_depth'] / 2:
            print("  • Consider reducing --max-depth for better structure preservation")
        if text_similarity < 0.8:
            print("  • Some content may be lost in wrapper div flattening")
            print("  • Try --no-preserve-semantic to preserve more structural elements")
        if regenerated_structure['total_elements'] < original_structure['total_elements'] / 3:
            print("  • Aggressive simplification detected - consider reducing simplification settings")
        
        return success_code
        
    except Exception as e:
        print(f"❌ Error in conversion testing workflow: {e}")
        return 1


def _extract_text_content(html: str) -> str:
    """Extract clean text content from HTML."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text()
    
    # Clean up text
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 1.0
    
    return len(intersection) / len(union)


def _analyze_html_structure(html: str) -> Dict[str, int]:
    """Analyze HTML structure complexity."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    def get_max_depth(element, current_depth=0):
        if not hasattr(element, 'children'):
            return current_depth
        
        max_child_depth = current_depth
        for child in element.children:
            if hasattr(child, 'name') and child.name:
                child_depth = get_max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    body = soup.find('body')
    max_depth = get_max_depth(body) if body else 0
    
    return {
        'total_elements': len(soup.find_all()),
        'max_depth': max_depth,
        'div_count': len(soup.find_all('div')),
        'semantic_elements': len(soup.find_all(['article', 'section', 'header', 'footer', 'main', 'nav', 'aside']))
    }


def _show_text_diff_sample(original: str, regenerated: str, max_lines: int = 10):
    """Show a sample of text differences."""
    original_lines = original.split('\n')[:max_lines]
    regenerated_lines = regenerated.split('\n')[:max_lines]
    
    diff = list(unified_diff(
        original_lines,
        regenerated_lines,
        fromfile='original',
        tofile='regenerated',
        lineterm=''
    ))
    
    if diff:
        print("   Sample differences (first 10 lines):")
        for line in diff[:20]:  # Show first 20 diff lines
            print(f"   {line}")


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
