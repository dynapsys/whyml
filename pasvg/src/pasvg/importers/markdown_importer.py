"""
Markdown Importer - Imports projects from markdown tutorial files.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from pasvg.core.models import (
    PASVGMetadata, SourceFile, ProjectConfig, BuildConfig, FileType
)


class MarkdownImporter:
    """Imports project configuration from markdown tutorial files."""
    
    def __init__(self):
        self.file_type_mapping = {
            'yaml': FileType.MANIFEST,
            'yml': FileType.MANIFEST,
            'json': FileType.CONFIGURATION,
            'dockerfile': FileType.CONTAINER,
            'docker-compose.yml': FileType.CONTAINER,
            'css': FileType.STYLESHEET,
            'js': FileType.SOURCE_CODE,
            'ts': FileType.SOURCE_CODE,
            'php': FileType.SOURCE_CODE,
            'py': FileType.SOURCE_CODE,
            'html': FileType.WEB,
            'md': FileType.DOCUMENTATION,
            'sh': FileType.BUILD,
            'toml': FileType.CONFIGURATION,
        }
    
    def import_from_markdown(self, markdown_file: str) -> Optional[ProjectConfig]:
        """Import project from markdown tutorial file."""
        md_path = Path(markdown_file)
        if not md_path.exists():
            return None
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from markdown
        metadata = self._extract_metadata(content, md_path.stem)
        
        # Extract source files from code blocks
        source_files = self._extract_source_files(content)
        
        # Create build configuration
        build_config = self._create_build_config(source_files)
        
        return ProjectConfig(
            metadata=metadata,
            source_files=source_files,
            build_config=build_config
        )
    
    def _extract_metadata(self, content: str, filename: str) -> PASVGMetadata:
        """Extract project metadata from markdown content."""
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else filename.replace('-', ' ').title()
        
        # Extract description (first paragraph after title)
        desc_pattern = r'^#\s+.+?\n\n(.+?)(?:\n\n|\n#|\Z)'
        desc_match = re.search(desc_pattern, content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract technologies from content
        technologies = self._extract_technologies(content)
        
        # Extract platforms/targets
        platforms = self._extract_platforms(content)
        build_targets = self._extract_build_targets(content, technologies)
        
        return PASVGMetadata(
            name=title,
            description=description,
            version="1.0.0",
            technologies=technologies,
            platforms=platforms,
            build_targets=build_targets,
            created_at=datetime.now().isoformat()
        )
    
    def _extract_source_files(self, content: str) -> List[SourceFile]:
        """Extract source files from markdown code blocks."""
        source_files = []
        
        # Pattern to match code blocks with filenames
        # Matches: ```language filename or ```language\nfilename: content
        patterns = [
            # Pattern 1: ```yaml manifests/site.yaml
            r'```(\w+)\s+([^\n]+?)\n(.*?)```',
            # Pattern 2: filename.ext:\n```language
            r'([^\n]+?\.\w+):\s*\n```(\w+)\n(.*?)```',
            # Pattern 3: **filename.ext**\n```language  
            r'\*\*([^\n]+?\.\w+)\*\*\s*\n```(\w+)\n(.*?)```',
            # Pattern 4: ### filename.ext followed by code block
            r'###\s+([^\n]+?\.\w+)\s*\n```(\w+)\n(.*?)```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if len(match) == 3:
                    if pattern.endswith('([^\n]+?)\n(.*?)```'):  # Pattern 1
                        language, filename, file_content = match
                    else:  # Other patterns
                        filename, language, file_content = match
                    
                    # Clean up content
                    file_content = file_content.strip()
                    filename = filename.strip()
                    language = language.strip().lower()
                    
                    if filename and file_content:
                        # Determine file type
                        file_type = self._determine_file_type(filename, language)
                        
                        # Extract section context
                        section = self._extract_section_context(content, filename)
                        
                        source_file = SourceFile(
                            filename=filename,
                            content=file_content,
                            file_type=file_type,
                            language=language,
                            section=section
                        )
                        source_files.append(source_file)
        
        # Remove duplicates (same filename)
        unique_files = {}
        for file in source_files:
            if file.filename not in unique_files:
                unique_files[file.filename] = file
        
        return list(unique_files.values())
    
    def _extract_technologies(self, content: str) -> List[str]:
        """Extract technologies mentioned in markdown."""
        tech_keywords = {
            'docker': ['docker', 'dockerfile', 'docker-compose'],
            'php': ['php'],
            'python': ['python', 'py'],
            'javascript': ['javascript', 'js', 'node'],
            'react': ['react'],
            'vue': ['vue'],
            'tauri': ['tauri'],
            'rust': ['rust', 'cargo'],
            'yaml': ['yaml', 'yml'],
            'css': ['css'],
            'html': ['html'],
            'nginx': ['nginx'],
            'apache': ['apache'],
            'mysql': ['mysql'],
            'postgresql': ['postgresql', 'postgres'],
        }
        
        content_lower = content.lower()
        technologies = []
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                technologies.append(tech.title())
        
        return technologies
    
    def _extract_platforms(self, content: str) -> List[str]:
        """Extract target platforms from content."""
        platform_keywords = {
            'web': ['web', 'browser', 'html'],
            'desktop': ['desktop', 'tauri'],
            'mobile': ['mobile', 'android', 'ios'],
            'container': ['docker', 'container'],
        }
        
        content_lower = content.lower()
        platforms = []
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                platforms.append(platform.title())
        
        return platforms
    
    def _extract_build_targets(self, content: str, technologies: List[str]) -> List[str]:
        """Extract build targets based on content and technologies."""
        targets = []
        content_lower = content.lower()
        
        # Container targets
        if any(tech.lower() in ['docker'] for tech in technologies):
            targets.append("Container")
        
        # Web targets
        if any(tech.lower() in ['html', 'css', 'javascript', 'php'] for tech in technologies):
            targets.append("Web Application")
        
        # Desktop targets
        if any(tech.lower() in ['tauri'] for tech in technologies):
            targets.append("Desktop")
        
        # SPA targets
        if any(tech.lower() in ['react', 'vue'] for tech in technologies):
            targets.append("SPA")
        
        # PWA targets
        if 'pwa' in content_lower or 'progressive web app' in content_lower:
            targets.append("Progressive Web App")
        
        # Mobile targets
        if 'android' in content_lower:
            targets.append("APK")
        
        return targets
    
    def _determine_file_type(self, filename: str, language: str) -> FileType:
        """Determine file type based on filename and language."""
        filename_lower = filename.lower()
        
        # Check specific filenames first
        if filename_lower in self.file_type_mapping:
            return self.file_type_mapping[filename_lower]
        
        # Check file extension
        ext = Path(filename).suffix.lower().lstrip('.')
        if ext in self.file_type_mapping:
            return self.file_type_mapping[ext]
        
        # Check language
        if language in self.file_type_mapping:
            return self.file_type_mapping[language]
        
        # Default to source code
        return FileType.SOURCE_CODE
    
    def _extract_section_context(self, content: str, filename: str) -> str:
        """Extract the section context where the file is defined."""
        lines = content.split('\n')
        current_section = ""
        
        for i, line in enumerate(lines):
            # Track current section (headers)
            if line.startswith('#'):
                current_section = line.strip('#').strip()
            
            # Check if this line contains our filename
            if filename in line:
                return current_section
        
        return ""
    
    def _create_build_config(self, source_files: List[SourceFile]) -> BuildConfig:
        """Create build configuration based on source files."""
        build_config = BuildConfig()
        
        # Detect build targets
        targets = set()
        commands = {}
        dependencies = {}
        
        for file in source_files:
            filename = file.filename.lower()
            
            # Docker
            if 'docker' in filename:
                targets.add("Container")
                if filename == 'docker-compose.yml':
                    commands['container'] = ['docker-compose build', 'docker-compose up -d']
                elif filename == 'dockerfile':
                    commands['container'] = ['docker build -t project .', 'docker run -p 8080:80 project']
            
            # Web/PHP
            if filename.endswith(('.php', '.html', '.css')):
                targets.add("Web Application")
                dependencies['web'] = ['php', 'apache']
            
            # Node.js
            if filename == 'package.json':
                targets.add("SPA")
                commands['spa'] = ['npm install', 'npm run build']
                dependencies['spa'] = ['node', 'npm']
            
            # Tauri
            if 'tauri' in file.content.lower():
                targets.add("Desktop")
                commands['desktop'] = ['npm install', 'npm run tauri:build']
                dependencies['desktop'] = ['rust', 'node', 'tauri']
        
        build_config.targets = list(targets)
        build_config.commands = commands
        build_config.dependencies = dependencies
        
        return build_config


class MarkdownParseError(Exception):
    """Custom exception for markdown parsing errors."""
    pass
