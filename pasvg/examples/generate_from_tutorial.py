#!/usr/bin/env python3
"""
Script to generate a PASVG file from a tutorial markdown file.
"""
import sys
import os
from pathlib import Path
from pasvg.core.generator import Generator

def main():
    # Set up paths
    tutorial_path = Path(__file__).parent / "tutorial.md"
    output_dir = Path(__file__).parent / "output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Initialize the generator
    generator = Generator()
    
    print(f"Generating PASVG from {tutorial_path}...")
    
    # Generate the PASVG file
    result = generator.generate_from_markdown(
        markdown_file=str(tutorial_path),
        output_dir=str(output_dir)
    )
    
    if result.success:
        print(f"✅ Successfully generated PASVG file in {output_dir}")
        for filename in os.listdir(output_dir):
            if filename.endswith('.pasvg.svg'):
                print(f"   - {filename}")
    else:
        print("❌ Failed to generate PASVG file:")
        for error in result.errors:
            print(f"   - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
