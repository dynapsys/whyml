#!/usr/bin/env python3
"""
WhyML Batch Processing Script
============================

Skrypt do przetwarzania wsadowego stron WWW z wykorzystaniem WhyML.
Pobiera listę URL z pliku, generuje manifesty YAML i konwertuje do wszystkich formatów.

Struktura wyjściowa:
- project/[domain]/source/index.html
- project/[domain]/source/index.png  
- project/[domain]/manifest.yaml
- project/[domain]/html/index.html
- project/[domain]/html/index.png
- project/[domain]/php/index.php
- project/[domain]/vue/index.vue
- project/[domain]/js/index.js
- project/[domain]/ts/index.ts
- project/[domain]/react/index.tsx

Usage:
    python scripts/batch_process.py
    python scripts/batch_process.py --url-list custom_urls.txt
    python scripts/batch_process.py --output-dir custom_output
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import argparse

# Add WhyML to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML nie jest zainstalowany. Instaluj: pip install PyYAML")
    sys.exit(1)

from whyml.processor import WhyMLProcessor
from whyml.scrapers.url_scraper import URLScraper
from whyml.converters.html_converter import HTMLConverter
from whyml.converters.php_converter import PHPConverter
from whyml.converters.vue_converter import VueConverter
from whyml.converters.react_converter import ReactConverter
from scripts.screenshot_capture import ScreenshotCapture
from scripts.simple_manifest_generator import SimpleManifestGenerator


class BatchProcessor:
    """Główna klasa do przetwarzania wsadowego stron WWW."""
    
    def __init__(self, output_dir: Path = None, url_list_file: Path = None):
        self.output_dir = output_dir or Path("project")
        self.url_list_file = url_list_file or Path("project/url.list.txt")
        self.processor = WhyMLProcessor()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize converters
        self.converters = {
            'html': HTMLConverter(),
            'php': PHPConverter(), 
            'vue': VueConverter(vue_version='3'),
            'react': ReactConverter(react_version='18')
        }
        
        # Initialize screenshot capture
        self.screenshot_capture = None
        
        # Statistics
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def setup_logging(self):
        """Konfiguruje system logowania."""
        log_dir = self.output_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"batch_process_{int(time.time())}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_urls(self) -> List[str]:
        """Ładuje listę URL z pliku."""
        try:
            if not self.url_list_file.exists():
                self.logger.error(f"Plik z URL nie istnieje: {self.url_list_file}")
                return []
            
            with open(self.url_list_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.logger.info(f"Załadowano {len(urls)} URL z pliku {self.url_list_file}")
            return urls
        
        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania URL: {e}")
            return []
    
    def get_domain_name(self, url: str) -> str:
        """Wyciąga nazwę domeny z URL do użycia jako nazwa folderu."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Usuwamy www. i zamieniamy znaki specjalne
            domain = domain.replace('www.', '')
            domain = domain.replace('.', '_')
            domain = domain.replace(':', '_')
            return domain
        except Exception:
            return "unknown_domain"
    
    def create_directory_structure(self, domain: str) -> Dict[str, Path]:
        """Tworzy strukturę katalogów dla domeny."""
        base_dir = self.output_dir / domain
        
        dirs = {
            'base': base_dir,
            'source': base_dir / 'source',
            'html': base_dir / 'html',
            'php': base_dir / 'php',
            'vue': base_dir / 'vue',
            'js': base_dir / 'js',
            'ts': base_dir / 'ts',
            'react': base_dir / 'react'
        }
        
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    async def scrape_url_to_manifest(self, url: str) -> Optional[Dict]:
        """Scrapuje URL i generuje manifest YAML."""
        try:
            self.logger.info(f"Scrapowanie URL: {url}")
            
            # Try WhyML processor first
            try:
                manifest = await self.processor.scrape_url_to_manifest(
                    url=url,
                    sections=['metadata', 'structure', 'styles'],
                    simplify_structure=True,
                    max_depth=5
                )
                
                if manifest:
                    self.logger.info(f"Pomyślnie wygenerowano manifest przez WhyML processor dla {url}")
                    return manifest
                    
            except Exception as whyml_error:
                self.logger.warning(f"WhyML processor failed for {url}: {whyml_error}")
                self.logger.info(f"Próbując fallback SimpleManifestGenerator...")
                
                # Fallback to SimpleManifestGenerator
                try:
                    # Get HTML content first
                    html_content = None
                    
                    # Try URLScraper for HTML content
                    try:
                        async with URLScraper() as scraper:
                            html_content = await scraper._fetch_url(url)
                    except Exception:
                        # Final fallback to requests
                        import requests
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        html_content = response.text
                    
                    if html_content:
                        # Use SimpleManifestGenerator
                        simple_generator = SimpleManifestGenerator()
                        manifest = simple_generator.generate_manifest_from_html(html_content, url)
                        
                        self.logger.info(f"Pomyślnie wygenerowano manifest przez SimpleManifestGenerator dla {url}")
                        return manifest
                        
                except Exception as fallback_error:
                    self.logger.error(f"SimpleManifestGenerator failed for {url}: {fallback_error}")
            
            self.logger.warning(f"Nie udało się wygenerować manifestu dla {url}")
            return None
                
        except Exception as e:
            self.logger.error(f"Błąd podczas scrapowania {url}: {e}")
            return None
    
    async def save_source_files(self, url: str, dirs: Dict[str, Path]) -> bool:
        """Zapisuje pliki źródłowe (HTML i screenshot)."""
        try:
            # Zapisz źródłowy HTML - try URLScraper first, fallback to requests
            html_content = None
            
            try:
                async with URLScraper() as scraper:
                    html_content = await scraper._fetch_url(url)
            except Exception as scraper_error:
                self.logger.warning(f"URLScraper failed for {url}: {scraper_error}, trying fallback...")
                
                # Fallback to basic requests if URLScraper fails
                try:
                    import requests
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    html_content = response.text
                    self.logger.info(f"Pobrano HTML przez fallback requests dla {url}")
                except Exception as fallback_error:
                    self.logger.error(f"Fallback scraping failed for {url}: {fallback_error}")
                    return False
                
            if html_content:
                source_html = dirs['source'] / 'index.html'
                with open(source_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"Zapisano źródłowy HTML: {source_html}")
            
            # Zrób screenshot źródłowej strony (jeśli dostępne narzędzia)
            await self.capture_screenshot(url, dirs['source'] / 'index.png')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania plików źródłowych dla {url}: {e}")
            return False
    
    async def convert_to_all_formats(self, manifest: Dict, dirs: Dict[str, Path]) -> Dict[str, bool]:
        """Konwertuje manifest do wszystkich formatów."""
        results = {}
        
        # HTML conversion
        try:
            html_result = self.converters['html'].convert(manifest)
            html_file = dirs['html'] / 'index.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_result.content)
            results['html'] = True
            self.logger.info(f"Wygenerowano HTML: {html_file}")
        except Exception as e:
            self.logger.error(f"Błąd konwersji HTML: {e}")
            results['html'] = False
        
        # PHP conversion  
        try:
            php_result = self.converters['php'].convert(manifest)
            php_file = dirs['php'] / 'index.php'
            with open(php_file, 'w', encoding='utf-8') as f:
                f.write(php_result.content)
            results['php'] = True
            self.logger.info(f"Wygenerowano PHP: {php_file}")
        except Exception as e:
            self.logger.error(f"Błąd konwersji PHP: {e}")
            results['php'] = False
        
        # Vue conversion
        try:
            vue_result = self.converters['vue'].convert(manifest)
            vue_file = dirs['vue'] / 'index.vue'
            with open(vue_file, 'w', encoding='utf-8') as f:
                f.write(vue_result.content)
            results['vue'] = True
            self.logger.info(f"Wygenerowano Vue: {vue_file}")
        except Exception as e:
            self.logger.error(f"Błąd konwersji Vue: {e}")
            results['vue'] = False
        
        # React conversion
        try:
            react_result = self.converters['react'].convert(manifest)
            react_file = dirs['react'] / 'index.tsx'
            with open(react_file, 'w', encoding='utf-8') as f:
                f.write(react_result.content)
            results['react'] = True
            self.logger.info(f"Wygenerowano React: {react_file}")
        except Exception as e:
            self.logger.error(f"Błąd konwersji React: {e}")
            results['react'] = False
        
        # Generate vanilla JS and TypeScript versions
        try:
            js_content = self.generate_vanilla_js(manifest)
            js_file = dirs['js'] / 'index.js'
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            results['js'] = True
            self.logger.info(f"Wygenerowano JS: {js_file}")
        except Exception as e:
            self.logger.error(f"Błąd generowania JS: {e}")
            results['js'] = False
        
        try:
            ts_content = self.generate_typescript(manifest)
            ts_file = dirs['ts'] / 'index.ts'
            with open(ts_file, 'w', encoding='utf-8') as f:
                f.write(ts_content)
            results['ts'] = True
            self.logger.info(f"Wygenerowano TS: {ts_file}")
        except Exception as e:
            self.logger.error(f"Błąd generowania TS: {e}")
            results['ts'] = False
        
        return results
    
    def generate_vanilla_js(self, manifest: Dict) -> str:
        """Generuje vanilla JavaScript z manifestu."""
        metadata = manifest.get('metadata', {})
        title = metadata.get('title', 'Generated Page')
        
        js_content = f'''// Generated by WhyML - {title}
// Vanilla JavaScript implementation

class PageController {{
    constructor() {{
        this.init();
    }}
    
    init() {{
        document.addEventListener('DOMContentLoaded', () => {{
            this.setupInteractions();
            this.loadContent();
        }});
    }}
    
    setupInteractions() {{
        // Add event listeners for interactive elements
        const buttons = document.querySelectorAll('button[data-action]');
        buttons.forEach(button => {{
            button.addEventListener('click', (e) => {{
                const action = e.target.dataset.action;
                this.handleAction(action, e);
            }});
        }});
    }}
    
    handleAction(action, event) {{
        console.log(`Action triggered: ${{action}}`);
        // TODO: Implement specific action handlers
    }}
    
    loadContent() {{
        // TODO: Load dynamic content if needed
        console.log('Page loaded and ready');
    }}
}}

// Initialize page controller
new PageController();
'''
        return js_content
    
    def generate_typescript(self, manifest: Dict) -> str:
        """Generuje TypeScript z manifestu."""
        metadata = manifest.get('metadata', {})
        title = metadata.get('title', 'Generated Page')
        
        ts_content = f'''// Generated by WhyML - {title}
// TypeScript implementation

interface PageMetadata {{
    title: string;
    description?: string;
    author?: string;
}}

interface ActionEvent extends Event {{
    target: HTMLElement & {{ dataset: {{ action: string }} }};
}}

class PageController {{
    private metadata: PageMetadata;
    
    constructor(metadata: PageMetadata) {{
        this.metadata = metadata;
        this.init();
    }}
    
    private init(): void {{
        document.addEventListener('DOMContentLoaded', () => {{
            this.setupInteractions();
            this.loadContent();
        }});
    }}
    
    private setupInteractions(): void {{
        const buttons = document.querySelectorAll<HTMLButtonElement>('button[data-action]');
        buttons.forEach(button => {{
            button.addEventListener('click', (e: ActionEvent) => {{
                const action = e.target.dataset.action;
                this.handleAction(action, e);
            }});
        }});
    }}
    
    private handleAction(action: string, event: ActionEvent): void {{
        console.log(`Action triggered: ${{action}}`);
        // TODO: Implement specific action handlers
    }}
    
    private loadContent(): void {{
        // TODO: Load dynamic content if needed
        console.log('Page loaded and ready');
    }}
}}

// Initialize page controller
const pageMetadata: PageMetadata = {{
    title: "{title}",
    description: "{metadata.get('description', '')}",
    author: "{metadata.get('author', '')}"
}};

new PageController(pageMetadata);
'''
        return ts_content
    
    async def capture_screenshot(self, url_or_file: str, output_path: Path) -> bool:
        """Robi screenshot strony lub pliku HTML."""
        try:
            if not self.screenshot_capture:
                self.screenshot_capture = ScreenshotCapture()
                await self.screenshot_capture.setup()
            
            # Sprawdź czy to URL czy plik
            if url_or_file.startswith('http'):
                success = await self.screenshot_capture.capture_url(url_or_file, output_path)
            else:
                # To jest ścieżka do pliku
                file_path = Path(url_or_file)
                success = await self.screenshot_capture.capture_html_file(file_path, output_path)
            
            if success:
                self.logger.info(f"Screenshot: {url_or_file} -> {output_path}")
            else:
                self.logger.warning(f"Screenshot failed: {url_or_file}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Błąd podczas robienia screenshotu: {e}")
            return False
    
    async def process_single_url(self, url: str) -> bool:
        """Przetwarza pojedynczy URL."""
        try:
            self.logger.info(f"\\n=== Przetwarzanie URL: {url} ===")
            
            # Uzyskaj nazwę domeny
            domain = self.get_domain_name(url)
            self.logger.info(f"Domena: {domain}")
            
            # Utwórz strukturę katalogów
            dirs = self.create_directory_structure(domain)
            
            # Zapisz pliki źródłowe
            await self.save_source_files(url, dirs)
            
            # Scrapuj i wygeneruj manifest
            manifest = await self.scrape_url_to_manifest(url)
            if not manifest:
                self.logger.error(f"Nie udało się wygenerować manifestu dla {url}")
                return False
            
            # Zapisz manifest YAML
            manifest_file = dirs['base'] / 'manifest.yaml'
            with open(manifest_file, 'w', encoding='utf-8') as f:
                yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, indent=2)
            self.logger.info(f"Zapisano manifest: {manifest_file}")
            
            # Konwertuj do wszystkich formatów
            conversion_results = await self.convert_to_all_formats(manifest, dirs)
            
            # Zrób screenshoty wygenerowanych plików
            for format_name, success in conversion_results.items():
                if success:
                    if format_name == 'html':
                        html_file = dirs[format_name] / 'index.html' 
                        screenshot_file = dirs[format_name] / 'index.png'
                        await self.capture_screenshot(str(html_file), screenshot_file)
            
            successful_conversions = sum(1 for success in conversion_results.values() if success)
            self.logger.info(f"Ukończono przetwarzanie {url}: {successful_conversions}/{len(conversion_results)} formatów")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania {url}: {e}")
            return False
    
    async def generate_documentation(self, processed_urls: List[Tuple[str, bool]]) -> None:
        """Generuje dokumentację HTML z podsumowaniem."""
        try:
            doc_file = self.output_dir / 'index.html'
            
            html_content = f'''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhyML Batch Processing Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-box {{ background: #e9ecef; padding: 15px; border-radius: 8px; text-align: center; }}
        .url-section {{ margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .success {{ border-left: 5px solid #28a745; }}
        .failed {{ border-left: 5px solid #dc3545; }}
        .formats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px; }}
        .format-link {{ display: block; padding: 8px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; text-align: center; }}
        .format-link:hover {{ background: #0056b3; }}
        .screenshot {{ max-width: 200px; border: 1px solid #ddd; margin: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 WhyML Batch Processing Results</h1>
        <p>Automatyczne przetwarzanie stron WWW do różnych formatów</p>
        <p><strong>Data generowania:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>{self.stats['processed']}</h3>
            <p>Przetworzone URL</p>
        </div>
        <div class="stat-box">
            <h3>{self.stats['successful']}</h3>
            <p>Udane konwersje</p>
        </div>
        <div class="stat-box">
            <h3>{self.stats['failed']}</h3>
            <p>Nieudane konwersje</p>
        </div>
        <div class="stat-box">
            <h3>{self.stats.get('duration', 0):.1f}s</h3>
            <p>Czas przetwarzania</p>
        </div>
    </div>
'''
            
            for url, success in processed_urls:
                domain = self.get_domain_name(url)
                status_class = 'success' if success else 'failed'
                status_text = '✅ Sukces' if success else '❌ Błąd'
                
                html_content += f'''
    <div class="url-section {status_class}">
        <h2>{url}</h2>
        <p><strong>Status:</strong> {status_text}</p>
        <p><strong>Domena:</strong> {domain}</p>
        
        <h3>Dostępne formaty:</h3>
        <div class="formats">
            <a href="{domain}/source/index.html" class="format-link">📄 Źródło HTML</a>
            <a href="{domain}/manifest.yaml" class="format-link">📋 Manifest YAML</a>
            <a href="{domain}/html/index.html" class="format-link">🌐 HTML</a>
            <a href="{domain}/php/index.php" class="format-link">🐘 PHP</a>
            <a href="{domain}/vue/index.vue" class="format-link">💚 Vue</a>
            <a href="{domain}/react/index.tsx" class="format-link">⚛️ React</a>
            <a href="{domain}/js/index.js" class="format-link">📜 JavaScript</a>
            <a href="{domain}/ts/index.ts" class="format-link">📘 TypeScript</a>
        </div>
        
        <h3>Screenshoty:</h3>
        <div>
            <img src="{domain}/source/index.png" alt="Źródło" class="screenshot" title="Oryginalna strona">
            <img src="{domain}/html/index.png" alt="HTML" class="screenshot" title="Wygenerowany HTML">
        </div>
    </div>
'''
            
            html_content += '''
</body>
</html>'''
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Wygenerowano dokumentację: {doc_file}")
            
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania dokumentacji: {e}")
    
    async def run(self) -> None:
        """Główna funkcja uruchamiająca przetwarzanie wsadowe."""
        self.stats['start_time'] = time.time()
        self.logger.info("🚀 Rozpoczynanie przetwarzania wsadowego WhyML")
        
        # Załaduj listę URL
        urls = self.load_urls()
        if not urls:
            self.logger.error("Brak URL do przetworzenia")
            return
        
        processed_urls = []
        
        # Przetwórz każdy URL
        for i, url in enumerate(urls, 1):
            self.logger.info(f"\\n[{i}/{len(urls)}] Przetwarzanie: {url}")
            self.stats['processed'] += 1
            
            success = await self.process_single_url(url)
            processed_urls.append((url, success))
            
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
        
        self.stats['end_time'] = time.time()
        self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
        
        # Wygeneruj dokumentację
        await self.generate_documentation(processed_urls)
        
        # Wyczyść zasoby screenshot capture
        if self.screenshot_capture:
            await self.screenshot_capture.cleanup()
        
        # Podsumowanie
        self.logger.info(f"\\n=== PODSUMOWANIE ===")
        self.logger.info(f"Przetworzone URL: {self.stats['processed']}")
        self.logger.info(f"Udane konwersje: {self.stats['successful']}")
        self.logger.info(f"Nieudane konwersje: {self.stats['failed']}")
        self.logger.info(f"Czas przetwarzania: {self.stats['duration']:.1f}s")
        self.logger.info(f"Dokumentacja: {self.output_dir}/index.html")


async def main():
    """Główna funkcja programu."""
    parser = argparse.ArgumentParser(description='WhyML Batch Processing Script')
    parser.add_argument('--url-list', type=Path, help='Ścieżka do pliku z listą URL')
    parser.add_argument('--output-dir', type=Path, help='Katalog wyjściowy')
    parser.add_argument('--verbose', '-v', action='store_true', help='Szczegółowe logowanie')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    processor = BatchProcessor(
        output_dir=args.output_dir,
        url_list_file=args.url_list
    )
    
    await processor.run()


if __name__ == "__main__":
    asyncio.run(main())
