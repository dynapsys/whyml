#!/usr/bin/env python3
"""
Example 1: Complete Webpage Scraping and Regeneration Workflow
This script demonstrates the complete WhyML workflow using Python API
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from whyml import WhyMLProcessor
    from whyml.scrapers import URLScraper
except ImportError as e:
    print(f"❌ Error importing WhyML: {e}")
    print("Please ensure WhyML is installed: pip install -e .")
    sys.exit(1)


async def run_example_1():
    """Run the complete Example 1 workflow"""
    print("🚀 Running Example 1: Complete Webpage Scraping and Regeneration Workflow")
    print("=" * 70)
    
    # Ensure we're in the right directory
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: Please run this script from the WhyML root directory")
        return False
    
    # Create examples/1 directory
    examples_dir = project_root / "examples" / "1"
    examples_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Scrape webpage
        print("📥 Step 1: Scraping https://example.com...")
        
        scraper = URLScraper(
            max_depth=5,
            simplify_structure=True,
            preserve_semantic=True
        )
        
        scraping_result = await scraper.scrape_url("https://example.com")
        manifest_content = scraping_result.to_yaml()
        
        # Save manifest
        manifest_path = examples_dir / "scraped-manifest.yaml"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        print(f"✅ Successfully scraped webpage to {manifest_path}")
        
        # Step 2: Convert to multiple formats
        print("🔄 Step 2: Converting manifest to multiple formats...")
        
        processor = WhyMLProcessor()
        
        # Convert to HTML
        html_result = await processor.convert_to_html(str(manifest_path))
        html_path = examples_dir / "regenerated.html"
        html_result.save_to_file(str(html_path))
        print(f"✅ Successfully converted to HTML: {html_path}")
        
        # Convert to React
        react_result = await processor.convert_to_react(
            str(manifest_path),
            use_typescript=True,
            css_modules=True
        )
        react_path = examples_dir / "Component.tsx"
        react_result.save_to_file(str(react_path))
        print(f"✅ Successfully converted to React: {react_path}")
        
        # Convert to Vue
        vue_result = await processor.convert_to_vue(
            str(manifest_path),
            composition_api=True,
            scoped_styles=True
        )
        vue_path = examples_dir / "Component.vue"
        vue_result.save_to_file(str(vue_path))
        print(f"✅ Successfully converted to Vue: {vue_path}")
        
        # Convert to PHP
        php_result = await processor.convert_to_php(
            str(manifest_path),
            namespace="App\\Components",
            use_type_declarations=True
        )
        php_path = examples_dir / "Component.php"
        php_result.save_to_file(str(php_path))
        print(f"✅ Successfully converted to PHP: {php_path}")
        
        # Display results
        print("\n🎉 Example 1 completed successfully!")
        print(f"📁 Generated files in {examples_dir}:")
        
        for file_path in examples_dir.iterdir():
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  • {file_path.name} ({size} bytes)")
        
        print("\n🔍 To view the results:")
        print(f"  • Original manifest: cat {manifest_path}")
        print(f"  • Generated HTML: open {html_path}")
        print(f"  • React component: cat {react_path}")
        print(f"  • Vue component: cat {vue_path}")
        print(f"  • PHP component: cat {php_path}")
        
        print(f"\n📖 For more details, see: {examples_dir}/README.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during example execution: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = asyncio.run(run_example_1())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
