#!/usr/bin/env python3
"""
PASVG Extractor - Extract Projects from Project Artifact SVG Files
================================================================

This tool extracts complete projects from PASVG (Project Artifact SVG) files,
recreating the original directory structure and all source files.
"""

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import base64
import sys


class PASVGExtractor:
    """Extracts project files from PASVG SVG format."""
    
    def __init__(self):
        self.namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'pasvg': 'http://whyml.org/pasvg/1.0'
        }
        
    def extract_project(self, pasvg_path: str, output_dir: str) -> str:
        """Extract complete project from PASVG file."""
        
        # Parse SVG
        tree = ET.parse(pasvg_path)
        root = tree.getroot()
        
        # Extract metadata
        metadata = self._extract_metadata(root)
        print(f"📋 Extracting project: {metadata.get('name', 'Unknown')}")
        
        # Create output directory
        project_name = metadata.get('name', 'extracted-project').lower().replace(' ', '-')
        project_dir = Path(output_dir) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract all embedded files
        files_extracted = self._extract_files(root, project_dir)
        
        # Extract build configuration
        build_config = self._extract_build_config(root, project_dir)
        
        # Create build script
        self._create_build_script(build_config, project_dir)
        
        # Create README
        self._create_readme(metadata, build_config, project_dir)
        
        print(f"✅ Project extracted to: {project_dir}")
        print(f"   📁 {len(files_extracted)} files extracted")
        print(f"   🏗️  Build targets: {', '.join(build_config.get('targets', []))}")
        print(f"\n🚀 To build: cd {project_dir} && ./build.sh")
        
        return str(project_dir)
    
    def _extract_metadata(self, root: ET.Element) -> Dict:
        """Extract project metadata from PASVG."""
        metadata = {}
        
        # Check root attributes
        metadata['name'] = root.get('data-project-name', 'Unknown Project')
        
        # Look for metadata element
        metadata_elem = root.find('.//metadata/project', self.namespaces)
        if metadata_elem is not None:
            for child in metadata_elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                metadata[tag_name.replace('-', '_')] = child.text or ''
        
        return metadata
    
    def _extract_files(self, root: ET.Element, project_dir: Path) -> List[str]:
        """Extract all embedded source files using raw SVG parsing."""
        extracted_files = []
        
        # Read the raw SVG content to extract CDATA sections
        svg_content = ""
        if hasattr(self, '_raw_svg_content'):
            svg_content = self._raw_svg_content
        else:
            # If we don't have raw content, try to extract from elements
            return self._fallback_extract_files(root, project_dir)
        
        # Extract CDATA sections using regex from raw SVG content
        # Pattern to match: <element data-filename="..." ...>...<![CDATA[...]]>...</element>
        cdata_pattern = r'<(foreignObject|pre|script)[^>]*data-filename="([^"]+)"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</\1>'
        
        matches = re.findall(cdata_pattern, svg_content, re.DOTALL)
        
        for element_type, filename, content in matches:
            # Clean up the content by removing leading/trailing whitespace
            cleaned_content = content.strip()
            if cleaned_content:
                self._write_file(project_dir, filename, cleaned_content)
                extracted_files.append(filename)
        
        return extracted_files
    
    def _fallback_extract_files(self, root: ET.Element, project_dir: Path) -> List[str]:
        """Fallback extraction method for when raw content is not available."""
        extracted_files = []
        
        # Find all foreignObject elements (YAML manifests)
        for elem in root.findall('.//foreignObject[@data-filename]'):
            filename = elem.get('data-filename')
            content = self._extract_cdata_content(elem)
            if content:
                self._write_file(project_dir, filename, content)
                extracted_files.append(filename)
        
        # Find all pre elements (source code)
        for elem in root.findall('.//pre[@data-filename]'):
            filename = elem.get('data-filename')
            content = self._extract_cdata_content(elem)
            if content:
                self._write_file(project_dir, filename, content)
                extracted_files.append(filename)
        
        # Find all script elements (JSON configs)
        for elem in root.findall('.//script[@data-filename]'):
            filename = elem.get('data-filename')
            content = self._extract_cdata_content(elem)
            if content:
                self._write_file(project_dir, filename, content)
                extracted_files.append(filename)
        
        return extracted_files
    
    def _extract_cdata_content(self, element: ET.Element) -> Optional[str]:
        """Extract CDATA content from XML element."""
        # Try to get direct text content first
        if element.text and element.text.strip():
            return element.text.strip()
        
        # For CDATA sections, we need to parse the raw content
        # ElementTree doesn't preserve CDATA sections, so we need to extract differently
        content_parts = []
        if element.text:
            content_parts.append(element.text)
        
        for child in element:
            if child.tail:
                content_parts.append(child.tail)
        
        if content_parts:
            content = ''.join(content_parts).strip()
            if content:
                return content
        
        return None
    
    def _write_file(self, project_dir: Path, filename: str, content: str):
        """Write file to project directory, creating subdirectories as needed."""
        file_path = project_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make shell scripts executable
        if filename.endswith('.sh'):
            file_path.chmod(0o755)
    
    def _extract_build_config(self, root: ET.Element, project_dir: Path) -> Dict:
        """Extract build configuration."""
        # Look for build config script
        build_script = root.find('.//script[@data-filename="pasvg-build.json"]')
        if build_script is not None:
            try:
                config_text = self._extract_cdata_content(build_script)
                if config_text:
                    return json.loads(config_text)
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract from metadata
        metadata = self._extract_metadata(root)
        return {
            'project': metadata.get('name', 'Unknown'),
            'targets': metadata.get('build_targets', '').split(', ') if metadata.get('build_targets') else [],
            'platforms': metadata.get('platforms', '').split(', ') if metadata.get('platforms') else [],
            'technologies': metadata.get('technologies', '').split(', ') if metadata.get('technologies') else []
        }
    
    def _create_build_script(self, build_config: Dict, project_dir: Path):
        """Create build script based on detected targets."""
        targets = build_config.get('targets', [])
        technologies = build_config.get('technologies', [])
        
        script_lines = [
            '#!/bin/bash',
            'set -e',
            '',
            f'echo "🏗️  Building {build_config.get("project", "project")}..."',
            'echo "Detected targets: ' + ', '.join(targets) + '"',
            ''
        ]
        
        # Docker builds
        if 'Container' in targets or 'Docker' in technologies:
            script_lines.extend([
                '# Docker build',
                'if [ -f "docker-compose.yml" ]; then',
                '    echo "🐳 Building with Docker Compose..."',
                '    docker-compose build',
                '    docker-compose up -d',
                'elif [ -f "Dockerfile" ]; then',
                '    echo "🐳 Building Docker image..."',
                '    docker build -t $(basename $(pwd)) .',
                'fi',
                ''
            ])
        
        # Node.js builds
        if any(tech in technologies for tech in ['React', 'Vue.js', 'PWA']):
            script_lines.extend([
                '# Node.js build',
                'if [ -f "package.json" ]; then',
                '    echo "📦 Installing dependencies..."',
                '    npm install',
                '    echo "🔨 Building application..."',
                '    npm run build',
                'fi',
                ''
            ])
        
        # Android builds
        if 'APK' in targets:
            script_lines.extend([
                '# Android build',
                'if [ -f "build.gradle" ] || [ -d "android" ]; then',
                '    echo "🤖 Building Android APK..."',
                '    ./gradlew assembleRelease',
                'fi',
                ''
            ])
        
        # Tauri builds
        if 'Desktop' in targets and 'Tauri' in technologies:
            script_lines.extend([
                '# Tauri build',
                'if [ -f "src-tauri/Cargo.toml" ]; then',
                '    echo "🦀 Building Tauri desktop app..."',
                '    npm run tauri:build',
                'fi',
                ''
            ])
        
        script_lines.extend([
            'echo "✅ Build completed!"',
            'echo "📦 Check output directories for built artifacts"'
        ])
        
        build_script_path = project_dir / 'build.sh'
        with open(build_script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(script_lines))
        
        build_script_path.chmod(0o755)
    
    def _create_readme(self, metadata: Dict, build_config: Dict, project_dir: Path):
        """Create README file for extracted project."""
        readme_content = f"""# {metadata.get('name', 'Extracted Project')}

{metadata.get('description', 'Project extracted from PASVG (Project Artifact SVG)')}

## Generated from PASVG

This project was extracted from a Project Artifact SVG (PASVG) file - a single-source-of-truth
container that embeds all project files in SVG format.

## Project Information

- **Version**: {metadata.get('version', '1.0.0')}
- **Platforms**: {', '.join(build_config.get('platforms', []))}
- **Technologies**: {', '.join(build_config.get('technologies', []))}
- **Build Targets**: {', '.join(build_config.get('targets', []))}

## Quick Start

```bash
# Build the project
./build.sh

# Or build specific targets manually:
"""

        targets = build_config.get('targets', [])
        
        if 'Container' in targets:
            readme_content += "\n# Docker build\ndocker-compose up --build\n"
        
        if any(target in targets for target in ['SPA', 'Progressive Web App']):
            readme_content += "\n# Web app build\nnpm install && npm run build\n"
        
        if 'APK' in targets:
            readme_content += "\n# Android build\ncd android && ./gradlew assembleRelease\n"
        
        if 'Desktop' in targets:
            readme_content += "\n# Desktop app build\nnpm run tauri:build\n"
        
        readme_content += """```

## Project Structure

This project contains all the source files needed to build and deploy the application.
Check the individual files for specific configuration and implementation details.

## PASVG Technology

This project demonstrates the innovative PASVG (Project Artifact SVG) concept:
- Single SVG file contains entire project
- Human-readable visual documentation + machine-extractable source code
- Version control friendly
- Cross-platform compatible

Learn more about WhyML and PASVG at: https://github.com/dynapsys/whyml
"""

        readme_path = project_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)


def main():
    if len(sys.argv) != 3:
        print("Usage: python pasvg_extractor.py <pasvg_file.svg> <output_directory>")
        print("\nExample:")
        print("  python pasvg_extractor.py tutorial-01.pasvg.svg ./extracted-projects/")
        sys.exit(1)
    
    extractor = PASVGExtractor()
    pasvg_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        project_dir = extractor.extract_project(pasvg_file, output_dir)
        print(f"\n🎉 Success! Project extracted to: {project_dir}")
    except Exception as e:
        print(f"❌ Error extracting PASVG: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
