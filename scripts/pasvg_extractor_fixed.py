#!/usr/bin/env python3
"""
PASVG Extractor - Fixed Version
==============================

Extracts project files from PASVG (Project Artifact SVG) files.
This version properly handles CDATA sections using raw text parsing.
"""

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional


class PASVGExtractor:
    """Extract projects from PASVG files with proper CDATA handling."""
    
    def __init__(self):
        self.namespaces = {
            'pasvg': 'http://whyml.org/pasvg/1.0'
        }
    
    def extract_pasvg(self, pasvg_file: str, output_dir: str) -> str:
        """Extract project from PASVG file."""
        pasvg_path = Path(pasvg_file)
        output_path = Path(output_dir)
        
        if not pasvg_path.exists():
            raise FileNotFoundError(f"PASVG file not found: {pasvg_file}")
        
        # Read raw SVG content for CDATA extraction
        with open(pasvg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Parse SVG for metadata
        tree = ET.parse(pasvg_path)
        root = tree.getroot()
        
        # Extract project metadata
        metadata = self._extract_metadata(root)
        project_name = metadata.get('name', 'extracted-project')
        
        print(f"📋 Extracting project: {project_name}")
        
        # Create project directory
        project_dir = output_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract source files using raw content parsing
        extracted_files = self._extract_files_from_raw_content(svg_content, project_dir)
        
        # Extract build configuration
        build_targets = self._extract_build_targets(svg_content)
        
        # Generate build script
        self._generate_build_script(project_dir, metadata, extracted_files, build_targets)
        
        # Generate README
        self._generate_readme(project_dir, metadata, extracted_files)
        
        print(f"✅ Project extracted to: {project_dir}")
        print(f"   📁 {len(extracted_files)} files extracted")
        print(f"   🏗️  Build targets: {', '.join(build_targets) if build_targets else 'None detected'}")
        
        return str(project_dir)
    
    def _extract_metadata(self, root: ET.Element) -> Dict[str, str]:
        """Extract project metadata from SVG."""
        metadata = {}
        
        # Look for metadata element
        metadata_elem = root.find('.//metadata/project', self.namespaces)
        if metadata_elem is not None:
            for child in metadata_elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                metadata[tag_name.replace('-', '_')] = child.text or ''
        
        return metadata
    
    def _extract_files_from_raw_content(self, svg_content: str, project_dir: Path) -> List[str]:
        """Extract embedded files using raw SVG content parsing."""
        extracted_files = []
        
        # Pattern to match CDATA sections within elements with data-filename attribute
        # This handles foreignObject, pre, and script elements
        pattern = r'<(foreignObject|pre|script)[^>]*data-filename="([^"]+)"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</\1>'
        
        matches = re.findall(pattern, svg_content, re.DOTALL)
        
        for element_type, filename, content in matches:
            # Clean and process the content
            cleaned_content = content.strip()
            if cleaned_content:
                self._write_file(project_dir, filename, cleaned_content)
                extracted_files.append(filename)
        
        return extracted_files
    
    def _extract_build_targets(self, svg_content: str) -> List[str]:
        """Extract build targets from build configuration."""
        # Look for build configuration JSON
        config_pattern = r'<script[^>]*data-filename="pasvg-build\.json"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</script>'
        
        match = re.search(config_pattern, svg_content, re.DOTALL)
        if match:
            try:
                config_data = json.loads(match.group(1).strip())
                return config_data.get('targets', [])
            except json.JSONDecodeError:
                pass
        
        return []
    
    def _write_file(self, project_dir: Path, filename: str, content: str):
        """Write file to project directory, creating subdirectories as needed."""
        file_path = project_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_build_script(self, project_dir: Path, metadata: Dict[str, str], 
                              extracted_files: List[str], build_targets: List[str]):
        """Generate build script for the extracted project."""
        project_name = metadata.get('name', 'project')
        
        build_commands = []
        
        # Add common setup
        build_commands.extend([
            "#!/bin/bash",
            "# Auto-generated build script for PASVG project",
            f"# Project: {project_name}",
            "",
            "set -e",
            "",
            "echo '🚀 Building PASVG project...'",
            ""
        ])
        
        # Add build commands based on detected targets and files
        if any('docker-compose.yml' in f for f in extracted_files):
            build_commands.extend([
                "# Docker Compose build",
                "if [ -f docker-compose.yml ]; then",
                "    echo '🐳 Building with Docker Compose...'",
                "    docker-compose build",
                "    echo '✅ Docker Compose build complete'",
                "fi",
                ""
            ])
        
        if any('Dockerfile' in f for f in extracted_files):
            build_commands.extend([
                "# Docker build",
                "if [ -f Dockerfile ]; then",
                f"    echo '🐳 Building Docker image for {project_name}...'",
                f"    docker build -t {project_name.lower().replace(' ', '-')} .",
                "    echo '✅ Docker image built'",
                "fi",
                ""
            ])
        
        if any('package.json' in f for f in extracted_files):
            build_commands.extend([
                "# Node.js/NPM build",
                "if [ -f package.json ]; then",
                "    echo '📦 Installing npm dependencies...'",
                "    npm install",
                "    if npm run build > /dev/null 2>&1; then",
                "        echo '🔨 Building frontend...'",
                "        npm run build",
                "        echo '✅ Frontend build complete'",
                "    fi",
                "fi",
                ""
            ])
        
        if any('Cargo.toml' in f and 'src-tauri' in f for f in extracted_files):
            build_commands.extend([
                "# Tauri desktop app build",
                "if [ -d src-tauri ]; then",
                "    echo '🖥️  Building Tauri desktop app...'",
                "    npm run tauri:build",
                "    echo '✅ Desktop app built'",
                "fi",
                ""
            ])
        
        build_commands.extend([
            "echo '🎉 Build complete!'",
            "echo 'Available build outputs:'",
            "find . -name '*.html' -o -name 'dist' -o -name 'build' -type d 2>/dev/null || true"
        ])
        
        build_script_content = '\n'.join(build_commands)
        
        build_script_path = project_dir / 'build.sh'
        with open(build_script_path, 'w') as f:
            f.write(build_script_content)
        
        # Make executable
        build_script_path.chmod(0o755)
    
    def _generate_readme(self, project_dir: Path, metadata: Dict[str, str], extracted_files: List[str]):
        """Generate README for the extracted project."""
        project_name = metadata.get('name', 'PASVG Project')
        description = metadata.get('description', 'Project extracted from PASVG artifact')
        technologies = metadata.get('technologies', '')
        platforms = metadata.get('platforms', '')
        
        readme_content = f"""# {project_name}

{description}

## Project Overview

This project was extracted from a PASVG (Project Artifact SVG) file - a revolutionary single-file project container that embeds all source code, configuration, and documentation within an SVG format.

### Technologies
{technologies}

### Target Platforms
{platforms}

## Extracted Files

This project contains {len(extracted_files)} extracted files:

{chr(10).join(f'- `{file}`' for file in sorted(extracted_files))}

## Building

To build this project, run:

```bash
./build.sh
```

## About PASVG

PASVG (Project Artifact SVG) is an innovative approach to project distribution that:
- ✅ **Single-source-of-truth**: Everything in one SVG file
- ✅ **Human-readable**: Visual documentation + embedded code
- ✅ **Machine-parseable**: Automated extraction and builds
- ✅ **Version control friendly**: Text-based format
- ✅ **Cross-platform**: Works everywhere SVG is supported

Generated by WhyML PASVG system.
"""
        
        with open(project_dir / 'README.md', 'w') as f:
            f.write(readme_content)


def main():
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python pasvg_extractor_fixed.py <pasvg_file> <output_directory>")
        print("\nExample:")
        print("  python pasvg_extractor_fixed.py project.pasvg.svg ./extracted/")
        sys.exit(1)
    
    pasvg_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        extractor = PASVGExtractor()
        project_path = extractor.extract_pasvg(pasvg_file, output_dir)
        
        print(f"\n🚀 To build: cd {project_path} && ./build.sh")
        print(f"\n🎉 Success! Project extracted to: {project_path}")
        
    except Exception as e:
        print(f"❌ Error extracting PASVG: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
