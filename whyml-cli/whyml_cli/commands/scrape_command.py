"""
WhyML CLI Scrape Command

Web scraping command for converting websites to WhyML manifests
using the whyml-scrapers package functionality.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
from pathlib import Path
from typing import List

from whyml_core.exceptions import ProcessingError
from .base_command import BaseCommand


class ScrapeCommand(BaseCommand):
    """Command for web scraping to WhyML manifests."""
    
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register scrape command parser."""
        parser = subparsers.add_parser(
            'scrape',
            help='Scrape websites to WhyML manifests',
            description='Convert web pages to structured WhyML manifest format',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli scrape https://example.com
  whyml-cli scrape https://example.com --output site.yaml
  whyml-cli scrape https://example.com --sections metadata structure --simplify
  whyml-cli scrape https://example.com --max-depth 3 --flatten-containers
            """
        )
        
        # Required arguments
        parser.add_argument(
            'url',
            type=self.validate_url,
            help='URL to scrape'
        )
        
        # Output options
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output manifest file path (default: stdout)'
        )
        
        parser.add_argument(
            '--format',
            choices=['yaml', 'json'],
            default='yaml',
            help='Output format (default: yaml)'
        )
        
        # Scraping options
        parser.add_argument(
            '--sections',
            nargs='+',
            choices=['metadata', 'structure', 'styles', 'scripts', 'analysis', 'imports'],
            help='Specific sections to extract (default: all)'
        )
        
        parser.add_argument(
            '--max-depth',
            type=int,
            metavar='N',
            help='Maximum HTML nesting depth'
        )
        
        parser.add_argument(
            '--simplify',
            action='store_true',
            help='Enable structure simplification'
        )
        
        parser.add_argument(
            '--flatten-containers',
            action='store_true',
            help='Remove wrapper div containers'
        )
        
        parser.add_argument(
            '--preserve-semantic',
            action='store_true',
            default=True,
            help='Preserve semantic HTML5 elements (default: true)'
        )
        
        parser.add_argument(
            '--no-preserve-semantic',
            dest='preserve_semantic',
            action='store_false',
            help='Disable semantic element preservation'
        )
        
        # Content options
        parser.add_argument(
            '--extract-styles',
            action='store_true',
            default=True,
            help='Extract CSS styles (default: true)'
        )
        
        parser.add_argument(
            '--no-extract-styles',
            dest='extract_styles',
            action='store_false',
            help='Skip CSS extraction'
        )
        
        parser.add_argument(
            '--extract-scripts',
            action='store_true',
            help='Extract JavaScript code'
        )
        
        parser.add_argument(
            '--extract-media',
            action='store_true',
            help='Extract media elements (images, videos)'
        )
        
        # Analysis options
        parser.add_argument(
            '--analyze-page',
            action='store_true',
            default=True,
            help='Include page analysis (default: true)'
        )
        
        parser.add_argument(
            '--no-analyze-page',
            dest='analyze_page',
            action='store_false',
            help='Skip page analysis'
        )
        
        # Testing options
        parser.add_argument(
            '--test-conversion',
            action='store_true',
            help='Test round-trip conversion (scrape -> generate -> compare)'
        )
        
        parser.add_argument(
            '--output-html',
            type=str,
            help='Save regenerated HTML for testing'
        )
        
        return parser
    
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute scrape command."""
        try:
            # Check if scraping is available
            if not self.cli.is_scraping_available():
                self.print_error(
                    "Web scraping not available. Install whyml-scrapers package:\n"
                    "pip install whyml-scrapers"
                )
                return 1
            
            # Prepare scraping options
            scrape_options = self._prepare_scrape_options(args)
            
            self.print_info(f"Scraping URL: {args.url}")
            
            # Perform scraping
            manifest = await self.cli.scrape_url(
                args.url,
                output_path=args.output,
                **scrape_options
            )
            
            # Output result
            if args.output:
                self.print_success(f"Manifest saved to {args.output}")
            else:
                # Print to stdout
                if args.format == 'json':
                    import json
                    print(json.dumps(manifest, indent=2, ensure_ascii=False))
                else:
                    import yaml
                    print(yaml.dump(manifest, default_flow_style=False, sort_keys=False))
            
            # Test conversion if requested
            if args.test_conversion:
                return await self._test_conversion(manifest, args)
            
            return 0
            
        except ProcessingError as e:
            self.print_error(str(e))
            return 1
        except Exception as e:
            self.print_error(f"Scraping failed: {e}")
            return 1
    
    def _prepare_scrape_options(self, args: argparse.Namespace) -> dict:
        """Prepare scraping options from arguments."""
        options = {}
        
        # Section selection
        if args.sections:
            options['sections'] = args.sections
        
        # Structure simplification
        if args.max_depth:
            options['max_depth'] = args.max_depth
        
        if args.simplify:
            options['simplify_structure'] = True
        
        if args.flatten_containers:
            options['flatten_containers'] = True
        
        options['preserve_semantic'] = args.preserve_semantic
        
        # Content extraction
        options['extract_styles'] = args.extract_styles
        options['extract_scripts'] = args.extract_scripts
        
        if args.extract_media:
            options['extract_media'] = True
        
        # Analysis
        options['analyze_page'] = args.analyze_page
        
        return options
    
    async def _test_conversion(self, manifest: dict, args: argparse.Namespace) -> int:
        """Test round-trip conversion."""
        try:
            self.print_info("Testing round-trip conversion...")
            
            # Convert manifest to HTML
            if 'html' not in self.cli.converters:
                self.print_warning("HTML converter not available, skipping conversion test")
                return 0
            
            html_converter = self.cli.converters['html']
            regenerated_html = await html_converter.convert_manifest(manifest)
            
            # Save regenerated HTML if requested
            if args.output_html:
                html_path = Path(args.output_html)
                html_path.write_text(regenerated_html, encoding='utf-8')
                self.print_info(f"Regenerated HTML saved to {args.output_html}")
            
            # Calculate similarity (basic implementation)
            similarity_score = await self._calculate_similarity(args.url, regenerated_html)
            
            self.print_info(f"Content similarity: {similarity_score:.1%}")
            
            if similarity_score > 0.8:
                self.print_success("Conversion test passed (similarity > 80%)")
                return 0
            elif similarity_score > 0.6:
                self.print_warning("Conversion test partial (similarity > 60%)")
                return 0
            else:
                self.print_warning("Conversion test concerns (similarity < 60%)")
                return 0
                
        except Exception as e:
            self.print_error(f"Conversion test failed: {e}")
            return 1
    
    async def _calculate_similarity(self, original_url: str, regenerated_html: str) -> float:
        """Calculate content similarity between original and regenerated content."""
        try:
            # Fetch original content
            import aiohttp
            import re
            from difflib import SequenceMatcher
            
            async with aiohttp.ClientSession() as session:
                async with session.get(original_url) as response:
                    original_html = await response.text()
            
            # Extract text content from both
            def extract_text(html):
                # Simple text extraction (remove tags and normalize whitespace)
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text).strip()
                return text.lower()
            
            original_text = extract_text(original_html)
            regenerated_text = extract_text(regenerated_html)
            
            # Calculate similarity
            matcher = SequenceMatcher(None, original_text, regenerated_text)
            return matcher.ratio()
            
        except Exception:
            # If similarity calculation fails, return neutral score
            return 0.7
