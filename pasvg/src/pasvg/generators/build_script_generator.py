"""
Build Script Generator - Creates build scripts for extracted projects.
"""

from pathlib import Path
from typing import List, Dict, Optional
import os

from pasvg.core.models import PASVGMetadata


class BuildScriptGenerator:
    """Generates build scripts for extracted PASVG projects."""
    
    def __init__(self):
        self.script_templates = {
            'bash': self._generate_bash_script,
            'batch': self._generate_batch_script,
            'powershell': self._generate_powershell_script
        }
    
    def generate_build_script(self, project_dir: Path, metadata: Optional[PASVGMetadata],
                            extracted_files: List[str], build_targets: List[str],
                            script_type: str = 'bash'):
        """Generate build script for the extracted project."""
        generator = self.script_templates.get(script_type, self._generate_bash_script)
        generator(project_dir, metadata, extracted_files, build_targets)
    
    def _generate_bash_script(self, project_dir: Path, metadata: Optional[PASVGMetadata],
                             extracted_files: List[str], build_targets: List[str]):
        """Generate bash build script."""
        project_name = metadata.name if metadata else 'project'
        
        commands = self._generate_build_commands(extracted_files, build_targets, project_name)
        
        script_content = f"""#!/bin/bash
# Auto-generated build script for PASVG project
# Project: {project_name}

set -e

echo '🚀 Building PASVG project: {project_name}'
echo '=================================='

{chr(10).join(commands)}

echo ''
echo '🎉 Build complete!'
echo 'Available build outputs:'
find . -name '*.html' -o -name 'dist' -o -name 'build' -type d 2>/dev/null || true
"""
        
        script_path = project_dir / 'build.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable
        script_path.chmod(0o755)
    
    def _generate_batch_script(self, project_dir: Path, metadata: Optional[PASVGMetadata],
                              extracted_files: List[str], build_targets: List[str]):
        """Generate Windows batch build script."""
        project_name = metadata.name if metadata else 'project'
        
        commands = self._generate_build_commands(extracted_files, build_targets, project_name, 'batch')
        
        script_content = f"""@echo off
REM Auto-generated build script for PASVG project
REM Project: {project_name}

echo 🚀 Building PASVG project: {project_name}
echo ==================================

{chr(10).join(commands)}

echo.
echo 🎉 Build complete!
echo Available build outputs:
dir /b /s *.html dist build 2>nul
"""
        
        script_path = project_dir / 'build.bat'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
    
    def _generate_powershell_script(self, project_dir: Path, metadata: Optional[PASVGMetadata],
                                   extracted_files: List[str], build_targets: List[str]):
        """Generate PowerShell build script."""
        project_name = metadata.name if metadata else 'project'
        
        commands = self._generate_build_commands(extracted_files, build_targets, project_name, 'powershell')
        
        script_content = f"""# Auto-generated build script for PASVG project
# Project: {project_name}

$ErrorActionPreference = "Stop"

Write-Host "🚀 Building PASVG project: {project_name}" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

{chr(10).join(commands)}

Write-Host ""
Write-Host "🎉 Build complete!" -ForegroundColor Green
Write-Host "Available build outputs:"
Get-ChildItem -Path . -Include "*.html", "dist", "build" -Recurse -ErrorAction SilentlyContinue
"""
        
        script_path = project_dir / 'build.ps1'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
    
    def _generate_build_commands(self, extracted_files: List[str], build_targets: List[str],
                                project_name: str, script_type: str = 'bash') -> List[str]:
        """Generate build commands based on detected files and targets."""
        commands = []
        
        # Docker commands
        if any('docker-compose.yml' in f for f in extracted_files):
            commands.extend(self._get_docker_compose_commands(script_type))
        elif any('dockerfile' in f.lower() for f in extracted_files):
            commands.extend(self._get_docker_commands(project_name, script_type))
        
        # Node.js commands
        if any('package.json' in f for f in extracted_files):
            commands.extend(self._get_nodejs_commands(script_type))
        
        # Python commands
        if any('requirements.txt' in f for f in extracted_files) or \
           any('pyproject.toml' in f for f in extracted_files):
            commands.extend(self._get_python_commands(script_type))
        
        # Rust/Tauri commands
        if any('cargo.toml' in f.lower() for f in extracted_files):
            commands.extend(self._get_rust_commands(script_type))
        
        # PHP commands
        if any(f.endswith('.php') for f in extracted_files):
            commands.extend(self._get_php_commands(script_type))
        
        # Static site commands
        if any(f.endswith('.html') for f in extracted_files):
            commands.extend(self._get_static_commands(script_type))
        
        return commands
    
    def _get_docker_compose_commands(self, script_type: str) -> List[str]:
        """Get Docker Compose build commands."""
        if script_type == 'bash':
            return [
                "",
                "# Docker Compose build",
                "if [ -f docker-compose.yml ]; then",
                "    echo '🐳 Building with Docker Compose...'",
                "    docker-compose build",
                "    echo '✅ Docker Compose build complete'",
                "    echo 'To start: docker-compose up -d'",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Docker Compose build",
                "if exist docker-compose.yml (",
                "    echo 🐳 Building with Docker Compose...",
                "    docker-compose build",
                "    echo ✅ Docker Compose build complete",
                "    echo To start: docker-compose up -d",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Docker Compose build",
                "if (Test-Path 'docker-compose.yml') {",
                "    Write-Host '🐳 Building with Docker Compose...' -ForegroundColor Blue",
                "    docker-compose build",
                "    Write-Host '✅ Docker Compose build complete' -ForegroundColor Green",
                "    Write-Host 'To start: docker-compose up -d'",
                "}"
            ]
    
    def _get_docker_commands(self, project_name: str, script_type: str) -> List[str]:
        """Get Docker build commands."""
        image_name = project_name.lower().replace(' ', '-')
        
        if script_type == 'bash':
            return [
                "",
                "# Docker build",
                "if [ -f Dockerfile ]; then",
                f"    echo '🐳 Building Docker image: {image_name}...'",
                f"    docker build -t {image_name} .",
                "    echo '✅ Docker image built'",
                f"    echo 'To run: docker run -p 8080:80 {image_name}'",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Docker build",
                "if exist Dockerfile (",
                f"    echo 🐳 Building Docker image: {image_name}...",
                f"    docker build -t {image_name} .",
                "    echo ✅ Docker image built",
                f"    echo To run: docker run -p 8080:80 {image_name}",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Docker build",
                "if (Test-Path 'Dockerfile') {",
                f"    Write-Host '🐳 Building Docker image: {image_name}...' -ForegroundColor Blue",
                f"    docker build -t {image_name} .",
                "    Write-Host '✅ Docker image built' -ForegroundColor Green",
                f"    Write-Host 'To run: docker run -p 8080:80 {image_name}'",
                "}"
            ]
    
    def _get_nodejs_commands(self, script_type: str) -> List[str]:
        """Get Node.js build commands."""
        if script_type == 'bash':
            return [
                "",
                "# Node.js build",
                "if [ -f package.json ]; then",
                "    echo '📦 Installing npm dependencies...'",
                "    npm install",
                "    if npm run build > /dev/null 2>&1; then",
                "        echo '🔨 Building frontend...'",
                "        npm run build",
                "        echo '✅ Frontend build complete'",
                "    else",
                "        echo 'ℹ️  No build script found in package.json'",
                "    fi",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Node.js build",
                "if exist package.json (",
                "    echo 📦 Installing npm dependencies...",
                "    npm install",
                "    npm run build >nul 2>&1",
                "    if %errorlevel% equ 0 (",
                "        echo 🔨 Building frontend...",
                "        npm run build",
                "        echo ✅ Frontend build complete",
                "    ) else (",
                "        echo ℹ️  No build script found in package.json",
                "    )",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Node.js build",
                "if (Test-Path 'package.json') {",
                "    Write-Host '📦 Installing npm dependencies...' -ForegroundColor Blue",
                "    npm install",
                "    try {",
                "        npm run build *>$null",
                "        Write-Host '🔨 Building frontend...' -ForegroundColor Blue",
                "        npm run build",
                "        Write-Host '✅ Frontend build complete' -ForegroundColor Green",
                "    } catch {",
                "        Write-Host 'ℹ️ No build script found in package.json' -ForegroundColor Yellow",
                "    }",
                "}"
            ]
    
    def _get_python_commands(self, script_type: str) -> List[str]:
        """Get Python build commands."""
        if script_type == 'bash':
            return [
                "",
                "# Python build",
                "if [ -f requirements.txt ] || [ -f pyproject.toml ]; then",
                "    echo '🐍 Setting up Python environment...'",
                "    python -m venv venv || python3 -m venv venv",
                "    source venv/bin/activate",
                "    if [ -f requirements.txt ]; then",
                "        pip install -r requirements.txt",
                "    elif [ -f pyproject.toml ]; then",
                "        pip install -e .",
                "    fi",
                "    echo '✅ Python environment ready'",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Python build",
                "if exist requirements.txt if exist pyproject.toml (",
                "    echo 🐍 Setting up Python environment...",
                "    python -m venv venv",
                "    call venv\\Scripts\\activate.bat",
                "    if exist requirements.txt (",
                "        pip install -r requirements.txt",
                "    ) else if exist pyproject.toml (",
                "        pip install -e .",
                "    )",
                "    echo ✅ Python environment ready",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Python build",
                "if ((Test-Path 'requirements.txt') -or (Test-Path 'pyproject.toml')) {",
                "    Write-Host '🐍 Setting up Python environment...' -ForegroundColor Blue",
                "    python -m venv venv",
                "    .\\venv\\Scripts\\Activate.ps1",
                "    if (Test-Path 'requirements.txt') {",
                "        pip install -r requirements.txt",
                "    } elseif (Test-Path 'pyproject.toml') {",
                "        pip install -e .",
                "    }",
                "    Write-Host '✅ Python environment ready' -ForegroundColor Green",
                "}"
            ]
    
    def _get_rust_commands(self, script_type: str) -> List[str]:
        """Get Rust/Tauri build commands."""
        if script_type == 'bash':
            return [
                "",
                "# Rust/Tauri build",
                "if [ -f Cargo.toml ]; then",
                "    echo '🦀 Building Rust project...'",
                "    if [ -d src-tauri ]; then",
                "        echo '🖥️ Building Tauri desktop app...'",
                "        npm install",
                "        npm run tauri:build",
                "        echo '✅ Desktop app built'",
                "    else",
                "        cargo build --release",
                "        echo '✅ Rust build complete'",
                "    fi",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Rust/Tauri build",
                "if exist Cargo.toml (",
                "    echo 🦀 Building Rust project...",
                "    if exist src-tauri (",
                "        echo 🖥️ Building Tauri desktop app...",
                "        npm install",
                "        npm run tauri:build",
                "        echo ✅ Desktop app built",
                "    ) else (",
                "        cargo build --release",
                "        echo ✅ Rust build complete",
                "    )",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Rust/Tauri build",
                "if (Test-Path 'Cargo.toml') {",
                "    Write-Host '🦀 Building Rust project...' -ForegroundColor Blue",
                "    if (Test-Path 'src-tauri') {",
                "        Write-Host '🖥️ Building Tauri desktop app...' -ForegroundColor Blue",
                "        npm install",
                "        npm run tauri:build",
                "        Write-Host '✅ Desktop app built' -ForegroundColor Green",
                "    } else {",
                "        cargo build --release",
                "        Write-Host '✅ Rust build complete' -ForegroundColor Green",
                "    }",
                "}"
            ]
    
    def _get_php_commands(self, script_type: str) -> List[str]:
        """Get PHP build commands."""
        if script_type == 'bash':
            return [
                "",
                "# PHP build",
                "if ls *.php 1> /dev/null 2>&1; then",
                "    echo '🐘 PHP project detected'",
                "    if [ -f composer.json ]; then",
                "        echo '📦 Installing Composer dependencies...'",
                "        composer install",
                "        echo '✅ Composer dependencies installed'",
                "    fi",
                "    echo 'ℹ️ Start local server: php -S localhost:8000'",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM PHP build",
                "dir *.php >nul 2>&1",
                "if %errorlevel% equ 0 (",
                "    echo 🐘 PHP project detected",
                "    if exist composer.json (",
                "        echo 📦 Installing Composer dependencies...",
                "        composer install",
                "        echo ✅ Composer dependencies installed",
                "    )",
                "    echo ℹ️ Start local server: php -S localhost:8000",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# PHP build",
                "if (Get-ChildItem -Filter '*.php' -ErrorAction SilentlyContinue) {",
                "    Write-Host '🐘 PHP project detected' -ForegroundColor Blue",
                "    if (Test-Path 'composer.json') {",
                "        Write-Host '📦 Installing Composer dependencies...' -ForegroundColor Blue",
                "        composer install",
                "        Write-Host '✅ Composer dependencies installed' -ForegroundColor Green",
                "    }",
                "    Write-Host 'ℹ️ Start local server: php -S localhost:8000' -ForegroundColor Yellow",
                "}"
            ]
    
    def _get_static_commands(self, script_type: str) -> List[str]:
        """Get static site commands."""
        if script_type == 'bash':
            return [
                "",
                "# Static site",
                "if ls *.html 1> /dev/null 2>&1; then",
                "    echo '📄 Static HTML files detected'",
                "    echo 'ℹ️ Open index.html in browser or start local server:'",
                "    echo 'ℹ️ python -m http.server 8000'",
                "fi"
            ]
        elif script_type == 'batch':
            return [
                "",
                "REM Static site",
                "dir *.html >nul 2>&1",
                "if %errorlevel% equ 0 (",
                "    echo 📄 Static HTML files detected",
                "    echo ℹ️ Open index.html in browser or start local server:",
                "    echo ℹ️ python -m http.server 8000",
                ")"
            ]
        else:  # powershell
            return [
                "",
                "# Static site",
                "if (Get-ChildItem -Filter '*.html' -ErrorAction SilentlyContinue) {",
                "    Write-Host '📄 Static HTML files detected' -ForegroundColor Blue",
                "    Write-Host 'ℹ️ Open index.html in browser or start local server:' -ForegroundColor Yellow",
                "    Write-Host 'ℹ️ python -m http.server 8000' -ForegroundColor Yellow",
                "}"
            ]


class BuildScriptError(Exception):
    """Custom exception for build script generation errors."""
    pass
