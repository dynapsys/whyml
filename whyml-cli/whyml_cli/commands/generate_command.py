"""
WhyML CLI Generate Command

Code generation command for creating new projects and components
from templates using the WhyML ecosystem.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

from whyml_core.exceptions import ProcessingError
from .base_command import BaseCommand


class GenerateCommand(BaseCommand):
    """Command for generating new projects and components."""
    
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register generate command parser."""
        parser = subparsers.add_parser(
            'generate',
            help='Generate new projects and components',
            description='Create new WhyML projects, components, and code from templates',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli generate --template basic-page --name HomePage --output src/
  whyml-cli generate --format react --name UserProfile --typescript --output components/
  whyml-cli generate --template blog-post --name "My Article" --output content/
  whyml-cli generate --format vue --name ProductCard --composition-api --output src/components/
            """
        )
        
        # Generation type
        generation_group = parser.add_mutually_exclusive_group(required=True)
        generation_group.add_argument(
            '--template',
            type=str,
            help='Generate from template (basic-page, blog-post, landing-page, etc.)'
        )
        
        generation_group.add_argument(
            '--format',
            type=self.validate_format,
            help='Generate component in specific format (html, react, vue, php)'
        )
        
        # Basic options
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name for the generated component/project'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=str,
            required=True,
            help='Output directory path'
        )
        
        parser.add_argument(
            '--description',
            type=str,
            help='Description for the generated component/project'
        )
        
        # Template options
        parser.add_argument(
            '--template-vars',
            nargs='+',
            metavar='KEY=VALUE',
            help='Template variables in KEY=VALUE format'
        )
        
        # Format-specific options (same as convert command)
        parser.add_argument(
            '--typescript',
            action='store_true',
            help='Generate TypeScript code (React/Vue)'
        )
        
        parser.add_argument(
            '--component-type',
            choices=['functional', 'class'],
            default='functional',
            help='React component type (default: functional)'
        )
        
        parser.add_argument(
            '--composition-api',
            action='store_true',
            default=True,
            help='Use Vue Composition API (default: true)'
        )
        
        parser.add_argument(
            '--namespace',
            type=str,
            help='PHP namespace'
        )
        
        # Project structure options
        parser.add_argument(
            '--create-structure',
            action='store_true',
            default=True,
            help='Create directory structure (default: true)'
        )
        
        parser.add_argument(
            '--include-styles',
            action='store_true',
            default=True,
            help='Include CSS/style files (default: true)'
        )
        
        parser.add_argument(
            '--include-tests',
            action='store_true',
            help='Generate test files'
        )
        
        parser.add_argument(
            '--include-docs',
            action='store_true',
            help='Generate documentation files'
        )
        
        return parser
    
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute generate command."""
        try:
            output_path = Path(args.output)
            
            # Ensure output directory exists
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Parse template variables
            template_vars = self._parse_template_vars(args.template_vars or [])
            template_vars['name'] = args.name
            if args.description:
                template_vars['description'] = args.description
            
            # Generate based on type
            if args.template:
                return await self._generate_from_template(args, output_path, template_vars)
            elif args.format:
                return await self._generate_component(args, output_path, template_vars)
            
            return 0
            
        except ProcessingError as e:
            self.print_error(str(e))
            return 1
        except Exception as e:
            self.print_error(f"Generation failed: {e}")
            return 1
    
    async def _generate_from_template(self, 
                                    args: argparse.Namespace, 
                                    output_path: Path,
                                    template_vars: Dict[str, Any]) -> int:
        """Generate from predefined template."""
        template_name = args.template
        
        # Get template manifest
        template_manifest = await self._get_template_manifest(template_name, template_vars)
        
        if not template_manifest:
            available_templates = await self._get_available_templates()
            self.print_error(
                f"Template '{template_name}' not found.\n"
                f"Available templates: {', '.join(available_templates)}"
            )
            return 1
        
        self.print_info(f"Generating from template: {template_name}")
        
        # Process and generate files
        generated_files = await self._generate_template_files(
            template_manifest, 
            output_path, 
            args
        )
        
        # Report results
        self.print_success(f"Generated {len(generated_files)} files in {output_path}")
        for file_path in generated_files:
            self.print_info(f"  Created: {file_path}")
        
        return 0
    
    async def _generate_component(self, 
                                args: argparse.Namespace, 
                                output_path: Path,
                                template_vars: Dict[str, Any]) -> int:
        """Generate component in specific format."""
        format_name = args.format
        
        self.print_info(f"Generating {format_name.upper()} component: {args.name}")
        
        # Create component manifest
        component_manifest = await self._create_component_manifest(
            args.name, 
            format_name, 
            template_vars
        )
        
        # Prepare conversion options
        conversion_options = self._prepare_component_options(args, format_name)
        
        # Generate component code
        converter = self.cli.converters[format_name]
        component_code = await converter.convert_manifest(
            component_manifest,
            **conversion_options
        )
        
        # Determine file extension and name
        extensions = {
            'html': '.html',
            'react': '.tsx' if args.typescript else '.jsx',
            'vue': '.vue',
            'php': '.php'
        }
        
        component_filename = self._sanitize_filename(args.name) + extensions[format_name]
        component_path = output_path / component_filename
        
        # Save component
        component_path.write_text(component_code, encoding='utf-8')
        
        generated_files = [component_path]
        
        # Generate additional files if requested
        if args.include_styles and format_name in ['html', 'react']:
            style_files = await self._generate_style_files(
                args.name, 
                output_path, 
                format_name,
                args.typescript
            )
            generated_files.extend(style_files)
        
        if args.include_tests:
            test_files = await self._generate_test_files(
                args.name, 
                output_path, 
                format_name,
                args.typescript
            )
            generated_files.extend(test_files)
        
        if args.include_docs:
            doc_files = await self._generate_doc_files(
                args.name, 
                output_path, 
                format_name
            )
            generated_files.extend(doc_files)
        
        # Report results
        self.print_success(f"Generated {format_name.upper()} component: {component_filename}")
        for file_path in generated_files:
            self.print_info(f"  Created: {file_path.relative_to(output_path)}")
        
        return 0
    
    def _parse_template_vars(self, var_args: List[str]) -> Dict[str, Any]:
        """Parse template variables from KEY=VALUE format."""
        template_vars = {}
        
        for var_arg in var_args:
            if '=' not in var_arg:
                self.print_warning(f"Invalid template variable format: {var_arg}")
                continue
            
            key, value = var_arg.split('=', 1)
            template_vars[key.strip()] = value.strip()
        
        return template_vars
    
    async def _get_template_manifest(self, 
                                   template_name: str, 
                                   template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Get template manifest by name."""
        # Built-in templates
        templates = {
            'basic-page': {
                'metadata': {
                    'title': template_vars.get('name', 'Basic Page'),
                    'description': template_vars.get('description', 'A basic web page'),
                    'version': '1.0.0'
                },
                'structure': {
                    'tag': 'div',
                    'attributes': {'class': 'page-container'},
                    'children': [
                        {
                            'tag': 'header',
                            'children': [
                                {
                                    'tag': 'h1',
                                    'content': template_vars.get('name', 'Basic Page')
                                }
                            ]
                        },
                        {
                            'tag': 'main',
                            'children': [
                                {
                                    'tag': 'p',
                                    'content': template_vars.get('description', 'Welcome to your new page!')
                                }
                            ]
                        }
                    ]
                }
            },
            'blog-post': {
                'metadata': {
                    'title': template_vars.get('name', 'Blog Post'),
                    'description': template_vars.get('description', 'A blog post'),
                    'author': template_vars.get('author', 'Anonymous'),
                    'date': template_vars.get('date', '2025-01-01')
                },
                'structure': {
                    'tag': 'article',
                    'attributes': {'class': 'blog-post'},
                    'children': [
                        {
                            'tag': 'header',
                            'children': [
                                {
                                    'tag': 'h1',
                                    'content': template_vars.get('name', 'Blog Post')
                                },
                                {
                                    'tag': 'p',
                                    'attributes': {'class': 'meta'},
                                    'content': f"By {template_vars.get('author', 'Anonymous')} on {template_vars.get('date', '2025-01-01')}"
                                }
                            ]
                        },
                        {
                            'tag': 'div',
                            'attributes': {'class': 'content'},
                            'children': [
                                {
                                    'tag': 'p',
                                    'content': template_vars.get('description', 'Your blog post content goes here.')
                                }
                            ]
                        }
                    ]
                }
            },
            'landing-page': {
                'metadata': {
                    'title': template_vars.get('name', 'Landing Page'),
                    'description': template_vars.get('description', 'An effective landing page')
                },
                'structure': {
                    'tag': 'div',
                    'attributes': {'class': 'landing-page'},
                    'children': [
                        {
                            'tag': 'section',
                            'attributes': {'class': 'hero'},
                            'children': [
                                {
                                    'tag': 'h1',
                                    'content': template_vars.get('name', 'Landing Page')
                                },
                                {
                                    'tag': 'p',
                                    'attributes': {'class': 'subtitle'},
                                    'content': template_vars.get('description', 'Convert visitors into customers')
                                },
                                {
                                    'tag': 'button',
                                    'attributes': {'class': 'cta-button'},
                                    'content': template_vars.get('cta_text', 'Get Started')
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        return templates.get(template_name)
    
    async def _get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return ['basic-page', 'blog-post', 'landing-page']
    
    async def _generate_template_files(self, 
                                     template_manifest: Dict[str, Any],
                                     output_path: Path,
                                     args: argparse.Namespace) -> List[Path]:
        """Generate files from template manifest."""
        generated_files = []
        
        # Generate main HTML file
        if 'html' in self.cli.converters:
            html_converter = self.cli.converters['html']
            html_content = await html_converter.convert_manifest(template_manifest)
            
            html_path = output_path / 'index.html'
            html_path.write_text(html_content, encoding='utf-8')
            generated_files.append(html_path)
        
        # Generate manifest file
        manifest_path = output_path / 'manifest.yaml'
        await self.cli._save_manifest(template_manifest, manifest_path)
        generated_files.append(manifest_path)
        
        # Generate additional formats if requested
        for format_name in ['react', 'vue', 'php']:
            if format_name in self.cli.converters:
                converter = self.cli.converters[format_name]
                
                extensions = {
                    'react': '.jsx',
                    'vue': '.vue', 
                    'php': '.php'
                }
                
                format_content = await converter.convert_manifest(template_manifest)
                format_path = output_path / f"index{extensions[format_name]}"
                format_path.write_text(format_content, encoding='utf-8')
                generated_files.append(format_path)
        
        return generated_files
    
    async def _create_component_manifest(self, 
                                       name: str, 
                                       format_name: str, 
                                       template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic component manifest."""
        return {
            'metadata': {
                'title': name,
                'description': template_vars.get('description', f'A {format_name} component'),
                'version': '1.0.0',
                'type': 'component'
            },
            'structure': {
                'tag': 'div',
                'attributes': {'class': self._kebab_case(name)},
                'children': [
                    {
                        'tag': 'h2',
                        'content': name
                    },
                    {
                        'tag': 'p',
                        'content': template_vars.get('description', f'{name} component content')
                    }
                ]
            }
        }
    
    def _prepare_component_options(self, args: argparse.Namespace, format_name: str) -> Dict[str, Any]:
        """Prepare format-specific component options."""
        options = {}
        
        if format_name == 'react':
            options.update({
                'typescript': args.typescript,
                'component_type': args.component_type,
                'component_name': self._pascal_case(args.name)
            })
        elif format_name == 'vue':
            options.update({
                'typescript': args.typescript,
                'composition_api': args.composition_api,
                'component_name': self._pascal_case(args.name)
            })
        elif format_name == 'php':
            options.update({
                'class_name': self._pascal_case(args.name),
                'use_classes': True
            })
            if args.namespace:
                options['namespace'] = args.namespace
        
        return options
    
    async def _generate_style_files(self, 
                                  name: str, 
                                  output_path: Path, 
                                  format_name: str,
                                  typescript: bool) -> List[Path]:
        """Generate style files for component."""
        generated_files = []
        
        # Basic CSS content
        css_content = f"""/* {name} Component Styles */
.{self._kebab_case(name)} {{
  /* Add your styles here */
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}}

.{self._kebab_case(name)} h2 {{
  margin: 0 0 0.5rem 0;
  color: #333;
}}

.{self._kebab_case(name)} p {{
  margin: 0;
  color: #666;
}}
"""
        
        if format_name == 'react':
            # Generate CSS module or styled-components
            if typescript:
                style_path = output_path / f"{self._pascal_case(name)}.module.css"
            else:
                style_path = output_path / f"{self._kebab_case(name)}.css"
            
            style_path.write_text(css_content, encoding='utf-8')
            generated_files.append(style_path)
        
        elif format_name == 'html':
            style_path = output_path / f"{self._kebab_case(name)}.css"
            style_path.write_text(css_content, encoding='utf-8')
            generated_files.append(style_path)
        
        return generated_files
    
    async def _generate_test_files(self, 
                                 name: str, 
                                 output_path: Path, 
                                 format_name: str,
                                 typescript: bool) -> List[Path]:
        """Generate test files for component."""
        generated_files = []
        
        if format_name == 'react':
            test_ext = '.test.tsx' if typescript else '.test.jsx'
            test_content = f"""import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {self._pascal_case(name)} from './{self._pascal_case(name)}';

describe('{self._pascal_case(name)}', () => {{
  test('renders without crashing', () => {{
    render(<{self._pascal_case(name)} />);
  }});
  
  test('displays component name', () => {{
    render(<{self._pascal_case(name)} />);
    expect(screen.getByText('{name}')).toBeInTheDocument();
  }});
}});
"""
            
            test_path = output_path / f"{self._pascal_case(name)}{test_ext}"
            test_path.write_text(test_content, encoding='utf-8')
            generated_files.append(test_path)
        
        elif format_name == 'vue':
            test_content = f"""import {{ mount }} from '@vue/test-utils';
import {self._pascal_case(name)} from './{self._pascal_case(name)}.vue';

describe('{self._pascal_case(name)}', () => {{
  test('renders without crashing', () => {{
    const wrapper = mount({self._pascal_case(name)});
    expect(wrapper.exists()).toBe(true);
  }});
  
  test('displays component name', () => {{
    const wrapper = mount({self._pascal_case(name)});
    expect(wrapper.text()).toContain('{name}');
  }});
}});
"""
            
            test_path = output_path / f"{self._pascal_case(name)}.test.js"
            test_path.write_text(test_content, encoding='utf-8')
            generated_files.append(test_path)
        
        return generated_files
    
    async def _generate_doc_files(self, 
                                name: str, 
                                output_path: Path, 
                                format_name: str) -> List[Path]:
        """Generate documentation files for component."""
        generated_files = []
        
        # README file
        readme_content = f"""# {name}

A {format_name} component generated by WhyML CLI.

## Usage

```{format_name}
<!-- Add usage examples here -->
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| | | | |

## Styling

The component uses CSS classes with the `{self._kebab_case(name)}` prefix.

## Development

Generated on {self._get_current_date()} using WhyML CLI.
"""
        
        readme_path = output_path / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        generated_files.append(readme_path)
        
        return generated_files
    
    # Utility methods
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize name for use as filename."""
        import re
        return re.sub(r'[^\w\-_.]', '', name.replace(' ', '_'))
    
    def _pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        return ''.join(word.capitalize() for word in text.replace('-', ' ').replace('_', ' ').split())
    
    def _kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        import re
        text = re.sub(r'([A-Z])', r'-\1', text).lower()
        return re.sub(r'[\s_]+', '-', text).strip('-')
    
    def _get_current_date(self) -> str:
        """Get current date as string."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
