"""
PASVG Command Line Interface
"""

import click
import sys
from pathlib import Path
from typing import Optional

from pasvg.core.generator import Generator
from pasvg.core.extractor import Extractor
from pasvg.core.validator import Validator
from pasvg.core.builder import Builder


@click.group()
@click.version_option(version="1.0.0", prog_name="pasvg")
def main():
    """PASVG - Project Artifact SVG system for revolutionary project distribution."""
    pass


@main.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--type', 'source_type', 
              type=click.Choice(['markdown', 'directory', 'config']),
              default='markdown',
              help='Type of source to generate from')
@click.option('--width', default=1200, help='SVG width in pixels')
@click.option('--height', default=800, help='SVG height in pixels')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate(source: str, output_dir: str, source_type: str, 
             width: int, height: int, verbose: bool):
    """Generate PASVG file from source."""
    if verbose:
        click.echo(f"🚀 Generating PASVG from {source_type}: {source}")
    
    try:
        generator = Generator(svg_width=width, svg_height=height)
        
        if source_type == 'markdown':
            result = generator.generate_from_markdown(source, output_dir)
        elif source_type == 'directory':
            result = generator.generate_from_directory(source, output_dir)
        elif source_type == 'config':
            result = generator.generate_from_config(source, output_dir)
        else:
            click.echo(f"❌ Unsupported source type: {source_type}", err=True)
            sys.exit(1)
        
        if result.success:
            click.echo(f"✅ Generated PASVG: {result.pasvg_file}")
            if verbose:
                click.echo(f"   📁 {result.file_count} files embedded")
                click.echo(f"   📊 Total size: {result.total_size} bytes")
        else:
            click.echo("❌ Generation failed:", err=True)
            for error in result.errors:
                click.echo(f"   {error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pasvg_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def extract(pasvg_file: str, output_dir: str, verbose: bool):
    """Extract project from PASVG file."""
    if verbose:
        click.echo(f"📂 Extracting project from: {pasvg_file}")
    
    try:
        extractor = Extractor()
        result = extractor.extract(pasvg_file, output_dir)
        
        if result.success:
            click.echo(f"✅ Project extracted to: {result.project_dir}")
            if verbose:
                click.echo(f"   📁 {len(result.extracted_files)} files extracted")
                click.echo(f"   🏗️  Build targets: {', '.join(result.build_targets)}")
                click.echo(f"\n🚀 To build: cd {result.project_dir} && ./build.sh")
        else:
            click.echo("❌ Extraction failed:", err=True)
            for error in result.errors:
                click.echo(f"   {error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pasvg_file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--strict', is_flag=True, help='Strict validation mode')
def validate(pasvg_file: str, verbose: bool, strict: bool):
    """Validate PASVG file structure and content."""
    if verbose:
        click.echo(f"🔍 Validating PASVG file: {pasvg_file}")
    
    try:
        validator = Validator()
        result = validator.validate(pasvg_file)
        
        if result.is_valid:
            click.echo(f"✅ PASVG file is valid")
            if verbose:
                click.echo(f"   📁 {result.file_count} files found")
                click.echo(f"   📊 Total size: {result.total_size} bytes")
                if result.metadata:
                    click.echo(f"   📋 Project: {result.metadata.name}")
        else:
            click.echo("❌ PASVG file validation failed:", err=True)
            for error in result.errors:
                click.echo(f"   Error: {error}", err=True)
            
            if not strict and result.warnings:
                click.echo("⚠️  Warnings:", err=True)
                for warning in result.warnings:
                    click.echo(f"   Warning: {warning}", err=True)
            
            sys.exit(1)
        
        # Show warnings even for valid files
        if result.warnings and verbose:
            click.echo("⚠️  Warnings:")
            for warning in result.warnings:
                click.echo(f"   {warning}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pasvg_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--target', multiple=True, 
              help='Specific build targets to build (can be used multiple times)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--clean', is_flag=True, help='Clean build artifacts before building')
def build(pasvg_file: str, output_dir: str, target: tuple, verbose: bool, clean: bool):
    """Build project from PASVG file."""
    if verbose:
        click.echo(f"🔨 Building project from: {pasvg_file}")
    
    try:
        builder = Builder()
        
        # Extract first
        extractor = Extractor()
        extract_result = extractor.extract(pasvg_file, output_dir)
        
        if not extract_result.success:
            click.echo("❌ Failed to extract project for building", err=True)
            sys.exit(1)
        
        # Build
        build_targets = list(target) if target else extract_result.build_targets
        result = builder.build_project(extract_result.project_dir, build_targets, clean)
        
        if result.success:
            click.echo(f"✅ Build completed successfully")
            if verbose:
                click.echo(f"   🏗️  Targets built: {', '.join(result.built_targets)}")
                click.echo(f"   📁 Output directory: {extract_result.project_dir}")
        else:
            click.echo("❌ Build failed:", err=True)
            for error in result.errors:
                click.echo(f"   {error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for the list')
@click.option('--format', 'output_format', 
              type=click.Choice(['table', 'json', 'csv']),
              default='table',
              help='Output format')
def list_files(directory: str, output: Optional[str], output_format: str):
    """List PASVG files in directory."""
    try:
        pasvg_files = list(Path(directory).glob("**/*.pasvg.svg"))
        
        if not pasvg_files:
            click.echo("No PASVG files found.")
            return
        
        if output_format == 'table':
            click.echo(f"Found {len(pasvg_files)} PASVG files:")
            click.echo("-" * 60)
            for pasvg_file in pasvg_files:
                size = pasvg_file.stat().st_size
                click.echo(f"{pasvg_file.name:<40} {size:>10} bytes")
        
        elif output_format == 'json':
            import json
            file_data = []
            for pasvg_file in pasvg_files:
                file_data.append({
                    'name': pasvg_file.name,
                    'path': str(pasvg_file),
                    'size': pasvg_file.stat().st_size
                })
            
            json_output = json.dumps(file_data, indent=2)
            if output:
                Path(output).write_text(json_output)
                click.echo(f"JSON output written to: {output}")
            else:
                click.echo(json_output)
        
        elif output_format == 'csv':
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            writer.writerow(['name', 'path', 'size'])
            
            for pasvg_file in pasvg_files:
                writer.writerow([
                    pasvg_file.name,
                    str(pasvg_file),
                    pasvg_file.stat().st_size
                ])
            
            csv_output = output_buffer.getvalue()
            if output:
                Path(output).write_text(csv_output)
                click.echo(f"CSV output written to: {output}")
            else:
                click.echo(csv_output)
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pasvg_file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def info(pasvg_file: str, verbose: bool):
    """Show information about PASVG file."""
    try:
        validator = Validator()
        result = validator.validate(pasvg_file)
        
        click.echo(f"📋 PASVG File Information: {Path(pasvg_file).name}")
        click.echo("=" * 50)
        
        if result.metadata:
            click.echo(f"Name:         {result.metadata.name}")
            click.echo(f"Description:  {result.metadata.description}")
            click.echo(f"Version:      {result.metadata.version}")
            if result.metadata.author:
                click.echo(f"Author:       {result.metadata.author}")
            if result.metadata.technologies:
                click.echo(f"Technologies: {', '.join(result.metadata.technologies)}")
            if result.metadata.platforms:
                click.echo(f"Platforms:    {', '.join(result.metadata.platforms)}")
            if result.metadata.build_targets:
                click.echo(f"Build Targets: {', '.join(result.metadata.build_targets)}")
        
        click.echo(f"Files:        {result.file_count}")
        click.echo(f"Total Size:   {result.total_size:,} bytes")
        click.echo(f"Valid:        {'✅' if result.is_valid else '❌'}")
        
        if result.errors:
            click.echo("\n❌ Errors:")
            for error in result.errors:
                click.echo(f"  - {error}")
        
        if result.warnings and verbose:
            click.echo("\n⚠️  Warnings:")
            for warning in result.warnings:
                click.echo(f"  - {warning}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
