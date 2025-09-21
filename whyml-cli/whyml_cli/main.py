"""
WhyML CLI Main Entry Point

Main entry point for the WhyML CLI application providing
unified access to the entire WhyML ecosystem.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import sys
from typing import List, Optional

from .cli import WhyMLCLI


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for WhyML CLI.
    
    Args:
        args: Command line arguments (default: sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Create CLI instance
        cli = WhyMLCLI()
        
        # Run CLI with asyncio
        return asyncio.run(cli.run(args))
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


def cli_main() -> None:
    """Entry point for console script."""
    sys.exit(main())


if __name__ == "__main__":
    cli_main()
