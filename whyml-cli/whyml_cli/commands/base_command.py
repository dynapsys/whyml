"""
WhyML CLI Base Command

Abstract base class for all CLI commands providing common functionality
and interface for command implementation.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path


class BaseCommand(ABC):
    """Abstract base class for CLI commands."""
    
    def __init__(self, cli_instance):
        """Initialize command with CLI instance.
        
        Args:
            cli_instance: Main CLI controller instance
        """
        self.cli = cli_instance
    
    @abstractmethod
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register command parser with subparsers.
        
        Args:
            subparsers: Subparsers object from main parser
            
        Returns:
            Command-specific parser
        """
        pass
    
    @abstractmethod
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute command with parsed arguments.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        pass
    
    def validate_file_path(self, path: str, must_exist: bool = True) -> Path:
        """Validate file path argument.
        
        Args:
            path: File path string
            must_exist: Whether file must exist
            
        Returns:
            Validated Path object
            
        Raises:
            argparse.ArgumentTypeError: If path is invalid
        """
        try:
            file_path = Path(path).resolve()
            
            if must_exist and not file_path.exists():
                raise argparse.ArgumentTypeError(f"File does not exist: {path}")
            
            if must_exist and not file_path.is_file():
                raise argparse.ArgumentTypeError(f"Path is not a file: {path}")
            
            return file_path
            
        except Exception as e:
            raise argparse.ArgumentTypeError(f"Invalid file path '{path}': {e}")
    
    def validate_url(self, url: str) -> str:
        """Validate URL argument.
        
        Args:
            url: URL string
            
        Returns:
            Validated URL string
            
        Raises:
            argparse.ArgumentTypeError: If URL is invalid
        """
        import re
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise argparse.ArgumentTypeError(f"Invalid URL: {url}")
        
        return url
    
    def validate_format(self, format_name: str) -> str:
        """Validate output format argument.
        
        Args:
            format_name: Format name string
            
        Returns:
            Validated format name
            
        Raises:
            argparse.ArgumentTypeError: If format is not supported
        """
        available_formats = self.cli.get_available_formats()
        
        if format_name not in available_formats:
            available_str = ', '.join(available_formats)
            raise argparse.ArgumentTypeError(
                f"Unsupported format '{format_name}'. Available: {available_str}"
            )
        
        return format_name
    
    def create_output_path(self, output_arg: Optional[str], 
                          default_name: str, 
                          format_ext: str = None) -> Path:
        """Create output path from argument.
        
        Args:
            output_arg: Output argument from CLI
            default_name: Default filename
            format_ext: Format-specific extension
            
        Returns:
            Output file path
        """
        if output_arg:
            output_path = Path(output_arg)
            
            # If directory provided, use default name
            if output_path.is_dir() or output_arg.endswith('/'):
                output_path = output_path / default_name
                
        else:
            output_path = Path(default_name)
        
        # Add extension if format specified and no extension present
        if format_ext and not output_path.suffix:
            output_path = output_path.with_suffix(format_ext)
        
        return output_path
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"✓ {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message."""
        print(message)
    
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"⚠ {message}")
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"✗ {message}")
    
    def format_list(self, items: list, title: str = None) -> str:
        """Format list for display.
        
        Args:
            items: List of items to format
            title: Optional title for the list
            
        Returns:
            Formatted string
        """
        lines = []
        
        if title:
            lines.append(f"{title}:")
        
        for item in items:
            lines.append(f"  • {item}")
        
        return '\n'.join(lines)
    
    def format_dict(self, data: dict, title: str = None, indent: int = 0) -> str:
        """Format dictionary for display.
        
        Args:
            data: Dictionary to format
            title: Optional title
            indent: Indentation level
            
        Returns:
            Formatted string
        """
        lines = []
        prefix = "  " * indent
        
        if title:
            lines.append(f"{prefix}{title}:")
            prefix += "  "
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self.format_dict(value, indent=indent+1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: [{', '.join(str(v) for v in value)}]")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return '\n'.join(lines)
