# WhyML Scrapers

[![PyPI version](https://badge.fury.io/py/whyml-scrapers.svg)](https://badge.fury.io/py/whyml-scrapers)
[![Python Support](https://img.shields.io/pypi/pyversions/whyml-scrapers.svg)](https://pypi.org/project/whyml-scrapers/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![WhyML Ecosystem](https://img.shields.io/badge/ecosystem-WhyML-blue.svg)](https://github.com/dynapsys/whyml)

**🕷️ Advanced web scraping and webpage analysis for the WhyML ecosystem**

Comprehensive web scraping and analysis toolkit that converts websites into structured WhyML manifests. Features intelligent content extraction, structure simplification, and advanced webpage analysis with SEO and accessibility auditing.

## 🔧 Recent Scraper Updates (2025)

**✅ ENHANCED URL SCRAPER**: Added `scrape_url()` method as compatibility wrapper for `scrape_to_manifest()` to ensure test compatibility and direct usage patterns.

**✅ SIMILARITY CALCULATION**: Added `_calculate_similarity()` method to URLScraper for manifest comparison and testing workflows, enabling content similarity analysis.

**✅ WEBPAGE ANALYZER**: Enhanced constructor with `max_nesting_depth` parameter (in addition to existing `max_depth`) and `min_content_length` for improved analysis control.

**✅ STRUCTURE ANALYSIS**: Added `simplification_applied` and `max_nesting_depth` fields to structure complexity analysis results for comprehensive testing compatibility.

**✅ ASYNC COMPATIBILITY**: All scraping operations maintain full async support while providing synchronous compatibility methods for testing environments.

## 🌟 Features

### 🚀 Core Components

- **📥 URLScraper**: High-performance async web scraping with intelligent structure analysis
- **🔍 WebpageAnalyzer**: Advanced webpage content, layout, and accessibility analysis  
- **📝 ContentExtractor**: Smart content extraction with semantic understanding
- **🏗️ StructureAnalyzer**: HTML structure analysis, simplification, and optimization

### 🎯 Key Capabilities

- **⚡ Async Processing**: High-performance asynchronous HTTP requests and parsing
- **🧹 Structure Simplification**: Reduce HTML nesting depth and flatten unnecessary containers
- **🎯 Selective Extraction**: Extract specific sections (metadata, content, styles, scripts)
- **📊 Page Analysis**: Automatic detection of page types, layouts, and optimization opportunities
- **♿ Accessibility Analysis**: Comprehensive accessibility metrics and recommendations
- **🔍 SEO Analysis**: Complete SEO audit with actionable recommendations
- **📱 Responsive Detection**: Identify responsive design patterns and breakpoints
- **🎨 Style Extraction**: Intelligent CSS analysis and framework detection

## 📦 Installation

### Standard Installation
```bash
pip install whyml-scrapers
```

### With Core Dependencies
```bash
pip install whyml-core whyml-scrapers
```

### Development Installation
```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml/whyml-scrapers
pip install -e .
```

## 🚀 Quick Start

### Basic URL Scraping
```python
import asyncio
from whyml_scrapers import URLScraper

async def scrape_website():
    scraper = URLScraper()
    async with scraper:
        # Scrape to WhyML manifest
        manifest = await scraper.scrape_to_manifest("https://example.com")
        
        # Save manifest
        with open("scraped-manifest.yaml", "w") as f:
            f.write(manifest.to_yaml())
        
        print("✓ Website scraped successfully!")

asyncio.run(scrape_website())
```

### Advanced Scraping with Options
```python
from whyml_scrapers import URLScraper

scraper = URLScraper(
    timeout=30.0,
    max_retries=3,
    extract_styles=True,
    extract_scripts=False,
    simplify_structure=True,
    max_depth=5,
    flatten_containers=True,
    preserve_semantic_tags=True
)

async with scraper:
    manifest = await scraper.scrape_to_manifest(
        url="https://example.com",
        sections=["metadata", "structure", "styles"],
        analyze_page=True
    )
```

### Webpage Analysis
```python
from whyml_scrapers import WebpageAnalyzer
import requests
from bs4 import BeautifulSoup

# Get webpage content
response = requests.get("https://example.com")
soup = BeautifulSoup(response.content, 'html.parser')

# Analyze webpage
analyzer = WebpageAnalyzer(
    min_content_length=50,
    detect_framework=True,
    analyze_accessibility=True
)

analysis = analyzer.analyze_webpage(soup, "https://example.com")

print(f"Page Type: {analysis['page_type']}")
print(f"Layout: {analysis['layout_type']}")
print(f"SEO Score: {analysis['seo_score']}")
print(f"Accessibility Score: {analysis['accessibility_score']}")
```

## 🔧 Advanced Features

### Structure Simplification

Automatically reduce HTML complexity while preserving semantic meaning:

```python
# Limit nesting depth
scraper = URLScraper(max_depth=3)

# Flatten unnecessary containers
scraper = URLScraper(
    flatten_containers=True,
    container_threshold=2  # Remove containers with < 2 meaningful children
)

# Preserve important semantic elements
scraper = URLScraper(
    preserve_semantic_tags=True,
    semantic_tags=['article', 'section', 'nav', 'header', 'footer', 'main']
)
```

### Selective Content Extraction

Extract only what you need:

```python
# Extract specific sections
manifest = await scraper.scrape_to_manifest(
    url="https://example.com",
    sections=["metadata", "structure"],  # Skip styles and scripts
    include_analytics=False
)

# Custom content filters
manifest = await scraper.scrape_to_manifest(
    url="https://example.com",
    content_filters={
        'min_text_length': 20,
        'exclude_empty_divs': True,
        'preserve_data_attributes': True
    }
)
```

### Page Analysis and Detection

Comprehensive webpage analysis:

```python
from whyml_scrapers import WebpageAnalyzer

analyzer = WebpageAnalyzer()

# Detect page type (blog, ecommerce, landing, etc.)
page_info = analyzer.detect_page_type(soup)

# Analyze layout structure  
layout_info = analyzer.analyze_layout_structure(soup)

# SEO analysis
seo_analysis = analyzer.analyze_seo(soup, url)

# Accessibility audit
accessibility = analyzer.analyze_accessibility(soup)

# Performance suggestions
optimization = analyzer.generate_optimization_suggestions(soup)
```

### Framework and Technology Detection

Automatically identify technologies used:

```python
# Detect CSS frameworks
frameworks = analyzer.detect_css_frameworks(soup)
# Returns: ['bootstrap', 'tailwind', 'foundation', etc.]

# Detect JavaScript libraries
libraries = analyzer.detect_js_libraries(soup)
# Returns: ['react', 'vue', 'angular', 'jquery', etc.]

# Detect CMS/platform
platform = analyzer.detect_platform(soup, response_headers)
# Returns: 'wordpress', 'shopify', 'drupal', etc.
```

## 🎯 Use Cases

### Website Migration and Refactoring
```python
# Scrape existing site
manifest = await scraper.scrape_to_manifest("https://old-site.com")

# Analyze for optimization opportunities
analysis = analyzer.analyze_webpage(soup, url)

# Generate modernized version using WhyML converters
from whyml_converters import HTMLConverter, ReactConverter

html_converter = HTMLConverter(css_framework='tailwind')
react_converter = ReactConverter(use_typescript=True)

modern_html = html_converter.convert(manifest)
react_component = react_converter.convert(manifest)
```

### Competitive Analysis
```python
competitors = [
    "https://competitor1.com",
    "https://competitor2.com", 
    "https://competitor3.com"
]

analyses = []
async with URLScraper() as scraper:
    for url in competitors:
        manifest = await scraper.scrape_to_manifest(url, analyze_page=True)
        analysis = manifest.metadata.get('analysis', {})
        analyses.append({
            'url': url,
            'seo_score': analysis.get('seo_score'),
            'accessibility_score': analysis.get('accessibility_score'),
            'page_type': analysis.get('page_type'),
            'technologies': analysis.get('detected_technologies', [])
        })

# Compare results
for analysis in analyses:
    print(f"{analysis['url']}: SEO {analysis['seo_score']}, A11y {analysis['accessibility_score']}")
```

### Content Audit and Optimization
```python
# Audit large sites
urls_to_audit = ["https://site.com/page1", "https://site.com/page2"]

audit_results = []
async with URLScraper() as scraper:
    for url in urls_to_audit:
        manifest = await scraper.scrape_to_manifest(url, analyze_page=True)
        
        audit_results.append({
            'url': url,
            'issues': manifest.metadata.get('analysis', {}).get('issues', []),
            'suggestions': manifest.metadata.get('analysis', {}).get('optimization_suggestions', []),
            'structure_complexity': manifest.metadata.get('analysis', {}).get('structure_depth')
        })

# Generate audit report
print("=== Content Audit Report ===")
for result in audit_results:
    print(f"\n{result['url']}:")
    print(f"  Issues: {len(result['issues'])}")
    print(f"  Suggestions: {len(result['suggestions'])}")
    print(f"  Structure Depth: {result['structure_complexity']}")
```

## 🧪 Testing and Validation

### Scrape-to-HTML Testing Workflow
```python
from whyml_scrapers import URLScraper
from whyml_converters import HTMLConverter

async def test_scraping_accuracy():
    scraper = URLScraper()
    converter = HTMLConverter()
    
    async with scraper:
        # Scrape original page
        original_url = "https://example.com"
        manifest = await scraper.scrape_to_manifest(original_url)
        
        # Convert back to HTML
        regenerated_html = converter.convert(manifest)
        
        # Compare with original
        similarity_score = await scraper.calculate_similarity(
            original_url, 
            regenerated_html.content
        )
        
        print(f"Regeneration Accuracy: {similarity_score:.2%}")
        
        if similarity_score > 0.85:
            print("✓ High fidelity regeneration achieved")
        else:
            print("⚠ Consider adjusting scraping parameters")

asyncio.run(test_scraping_accuracy())
```

## ⚙️ Configuration

### URLScraper Configuration
```python
scraper = URLScraper(
    # Network settings
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    user_agent="WhyML-Scraper/1.0",
    
    # Extraction settings
    extract_styles=True,
    extract_scripts=False,
    extract_meta_tags=True,
    extract_data_attributes=True,
    
    # Structure settings
    simplify_structure=True,
    max_depth=5,
    flatten_containers=True,
    preserve_semantic_tags=True,
    
    # Analysis settings
    analyze_page=True,
    detect_frameworks=True,
    calculate_metrics=True,
    
    # Performance settings
    enable_compression=True,
    follow_redirects=True,
    max_redirects=5
)
```

### WebpageAnalyzer Configuration
```python
analyzer = WebpageAnalyzer(
    # Content analysis
    min_content_length=50,
    ignore_hidden_elements=True,
    
    # Detection settings
    detect_framework=True,
    detect_cms=True,
    detect_ecommerce=True,
    
    # Analysis depth
    analyze_accessibility=True,
    analyze_seo=True,
    analyze_performance=True,
    generate_suggestions=True,
    
    # Scoring weights
    seo_weights={
        'title': 0.2,
        'meta_description': 0.15,
        'headings': 0.2,
        'images_alt': 0.15,
        'internal_links': 0.1,
        'page_speed': 0.2
    }
)
```

## 🔌 Integration with WhyML Ecosystem

### With WhyML Core
```python
from whyml_core.loading import ManifestLoader
from whyml_core.processing import ManifestProcessor
from whyml_scrapers import URLScraper

# Scrape and process
async with URLScraper() as scraper:
    manifest = await scraper.scrape_to_manifest("https://example.com")

# Load with core
loader = ManifestLoader()
loaded_manifest = await loader.load_from_dict(manifest.to_dict())

# Process with core
processor = ManifestProcessor()
processed_manifest = processor.process_manifest(loaded_manifest)
```

### With WhyML Converters
```python
from whyml_scrapers import URLScraper
from whyml_converters import HTMLConverter, ReactConverter, VueConverter

async with URLScraper() as scraper:
    manifest = await scraper.scrape_to_manifest("https://example.com")

# Convert to multiple formats
html_converter = HTMLConverter(css_framework='bootstrap')
react_converter = ReactConverter(use_typescript=True)
vue_converter = VueConverter(vue_version='3')

html_output = html_converter.convert(manifest)
react_output = react_converter.convert(manifest)
vue_output = vue_converter.convert(manifest)
```

## 🚨 Error Handling

```python
from whyml_scrapers import URLScraper
from whyml_core.exceptions import NetworkError, ProcessingError

async def robust_scraping():
    scraper = URLScraper()
    
    try:
        async with scraper:
            manifest = await scraper.scrape_to_manifest("https://example.com")
            return manifest
            
    except NetworkError as e:
        print(f"Network error: {e}")
        # Implement retry logic or fallback
        
    except ProcessingError as e:
        print(f"Processing error: {e}")
        # Handle parsing/processing issues
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle other errors gracefully
```

## 📊 Performance Optimization

### Concurrent Scraping
```python
import asyncio
from whyml_scrapers import URLScraper

async def scrape_multiple_urls(urls):
    scraper = URLScraper()
    
    async def scrape_single(url):
        async with scraper:
            return await scraper.scrape_to_manifest(url)
    
    # Scrape up to 5 URLs concurrently
    semaphore = asyncio.Semaphore(5)
    
    async def bounded_scrape(url):
        async with semaphore:
            return await scrape_single(url)
    
    results = await asyncio.gather(*[
        bounded_scrape(url) for url in urls
    ])
    
    return results
```

### Memory Optimization
```python
# For large sites, use streaming approach
scraper = URLScraper(
    stream_large_content=True,
    max_content_size="10MB",
    cleanup_dom=True  # Remove DOM references after processing
)
```

## 🔗 API Reference

### URLScraper

#### Methods
- `scrape_to_manifest(url, **options)` - Scrape URL to WhyML manifest
- `scrape_url(url, **options)` - Raw URL scraping (returns BeautifulSoup)
- `calculate_similarity(url1, content2)` - Compare original vs regenerated content
- `get_page_info(url)` - Get basic page information without full scraping

#### Properties
- `session` - Current aiohttp session
- `stats` - Scraping statistics and performance metrics
- `last_response` - Most recent HTTP response details

### WebpageAnalyzer

#### Methods
- `analyze_webpage(soup, url)` - Complete webpage analysis
- `detect_page_type(soup)` - Detect page type (blog, ecommerce, etc.)
- `analyze_seo(soup, url)` - SEO analysis and recommendations
- `analyze_accessibility(soup)` - Accessibility audit
- `detect_technologies(soup, headers)` - Technology stack detection

## 📋 System Requirements

- **Python**: 3.8+ (3.9+ recommended)
- **Memory**: 256MB+ available RAM for basic scraping
- **Network**: Internet connection for URL scraping
- **Optional**: Selenium/Playwright for JavaScript-heavy sites

## 🛠️ Dependencies

### Core Dependencies
```
aiohttp>=3.8.0          # Async HTTP client
beautifulsoup4>=4.11.0  # HTML parsing
lxml>=4.9.0             # Fast XML/HTML parser
whyml-core>=0.1.0       # WhyML core functionality
```

### Optional Dependencies
```
selenium>=4.0.0         # JavaScript rendering (optional)
playwright>=1.20.0      # Alternative browser automation (optional)
Pillow>=9.0.0          # Image analysis (optional)
```

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](../CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml/whyml-scrapers
pip install -e ".[dev]"
pytest tests/
```

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[whyml-core](../whyml-core/)** - Core WhyML functionality
- **[whyml-converters](../whyml-converters/)** - Multi-format conversion
- **[whyml-cli](../whyml-cli/)** - Command-line interface
- **[whyml](../)** - Main WhyML package

---

**🏠 [Back to WhyML Main Documentation](../README.md)**
