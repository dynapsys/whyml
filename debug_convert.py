#!/usr/bin/env python3
"""Debug script to trace LoadedManifest conversion error."""

import sys
import traceback
import asyncio
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent))

from whyml_cli.cli import WhyMLCLI

async def debug_convert():
    """Debug the convert command with full stack trace."""
    try:
        cli = WhyMLCLI()
        
        # Test the load_manifest method directly first
        print("Testing load_manifest directly...")
        loaded_manifest = await cli.load_manifest('test-manifest.yaml')
        print(f"Loaded manifest type: {type(loaded_manifest)}")
        print(f"Has content attribute: {hasattr(loaded_manifest, 'content')}")
        
        if hasattr(loaded_manifest, 'content'):
            print(f"Content type: {type(loaded_manifest.content)}")
            print(f"Content has keys: {hasattr(loaded_manifest.content, 'keys')}")
            print(f"Content has get: {hasattr(loaded_manifest.content, 'get')}")
        
        # Extract the manifest content
        manifest = loaded_manifest.content if hasattr(loaded_manifest, 'content') else loaded_manifest
        print(f"Extracted manifest type: {type(manifest)}")
        
        # Test process_manifest
        print("\nTesting process_manifest...")
        processed = await cli.process_manifest(manifest)
        print(f"Processed manifest type: {type(processed)}")
        
        print("\nTesting full convert command...")
        # Simulate the convert command args  
        args = ['convert', '--format', 'html', '--output', 'test-output.html', 'test-manifest.yaml']
        
        result = await cli.run(args)
        print(f"Command completed with exit code: {result}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(asyncio.run(debug_convert()))
