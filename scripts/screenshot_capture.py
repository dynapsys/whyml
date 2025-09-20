#!/usr/bin/env python3
"""
Screenshot Capture Helper
========================

Klasa pomocnicza do robienia zrzutów ekranu stron WWW i plików HTML.
Obsługuje różne backendy: playwright, selenium, lub fallback z wkhtmltopdf.
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Union
import subprocess


class ScreenshotCapture:
    """Klasa do robienia zrzutów ekranu stron WWW i plików HTML."""
    
    def __init__(self, backend: str = 'auto'):
        """
        Inicjalizuje klasę screenshot capture.
        
        Args:
            backend: 'playwright', 'selenium', 'wkhtmltopdf', lub 'auto'
        """
        self.backend = backend
        self.logger = logging.getLogger(__name__)
        self.playwright_browser = None
        
        if backend == 'auto':
            self.backend = self._detect_available_backend()
        
        self.logger.info(f"Używany backend dla screenshotów: {self.backend}")
    
    def _detect_available_backend(self) -> str:
        """Automatycznie wykrywa dostępny backend."""
        try:
            import playwright
            return 'playwright'
        except ImportError:
            pass
        
        try:
            import selenium
            return 'selenium'
        except ImportError:
            pass
        
        # Sprawdź czy jest dostępny wkhtmltopdf
        try:
            subprocess.run(['wkhtmltopdf', '--version'], 
                         capture_output=True, check=True)
            return 'wkhtmltopdf'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return 'fallback'
    
    async def setup(self):
        """Konfiguruje backend do robienia screenshotów."""
        if self.backend == 'playwright':
            await self._setup_playwright()
        elif self.backend == 'selenium':
            await self._setup_selenium()
    
    async def _setup_playwright(self):
        """Konfiguruje Playwright."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.playwright_browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.logger.info("Playwright skonfigurowany pomyślnie")
            
        except ImportError:
            self.logger.error("Playwright nie jest zainstalowany")
            self.backend = 'fallback'
        except Exception as e:
            self.logger.error(f"Błąd konfiguracji Playwright: {e}")
            self.backend = 'fallback'
    
    async def _setup_selenium(self):
        """Konfiguruje Selenium."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Selenium skonfigurowany pomyślnie")
            
        except ImportError:
            self.logger.error("Selenium nie jest zainstalowany")
            self.backend = 'fallback'
        except Exception as e:
            self.logger.error(f"Błąd konfiguracji Selenium: {e}")
            self.backend = 'fallback'
    
    async def capture_url(self, url: str, output_path: Path, 
                         width: int = 1920, height: int = 1080) -> bool:
        """
        Robi screenshot strony WWW.
        
        Args:
            url: URL strony do zescreenowania
            output_path: Ścieżka do zapisu PNG
            width: Szerokość viewport
            height: Wysokość viewport
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            if self.backend == 'playwright':
                return await self._capture_url_playwright(url, output_path, width, height)
            elif self.backend == 'selenium':
                return await self._capture_url_selenium(url, output_path, width, height)
            elif self.backend == 'wkhtmltopdf':
                return await self._capture_url_wkhtmltopdf(url, output_path, width, height)
            else:
                return await self._capture_url_fallback(url, output_path)
                
        except Exception as e:
            self.logger.error(f"Błąd podczas screenshotu URL {url}: {e}")
            return False
    
    async def capture_html_file(self, html_file: Path, output_path: Path,
                               width: int = 1920, height: int = 1080) -> bool:
        """
        Robi screenshot lokalnego pliku HTML.
        
        Args:
            html_file: Ścieżka do pliku HTML
            output_path: Ścieżka do zapisu PNG
            width: Szerokość viewport
            height: Wysokość viewport
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            if not html_file.exists():
                self.logger.error(f"Plik HTML nie istnieje: {html_file}")
                return False
            
            file_url = f"file://{html_file.absolute()}"
            return await self.capture_url(file_url, output_path, width, height)
            
        except Exception as e:
            self.logger.error(f"Błąd podczas screenshotu pliku {html_file}: {e}")
            return False
    
    async def _capture_url_playwright(self, url: str, output_path: Path, 
                                     width: int, height: int) -> bool:
        """Screenshot z użyciem Playwright."""
        try:
            if not self.playwright_browser:
                await self._setup_playwright()
            
            page = await self.playwright_browser.new_page()
            await page.set_viewport_size({"width": width, "height": height})
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.screenshot(path=str(output_path), full_page=True)
            await page.close()
            
            self.logger.info(f"Screenshot Playwright: {url} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd Playwright screenshot: {e}")
            return False
    
    async def _capture_url_selenium(self, url: str, output_path: Path,
                                   width: int, height: int) -> bool:
        """Screenshot z użyciem Selenium."""
        try:
            if not hasattr(self, 'selenium_driver'):
                await self._setup_selenium()
            
            self.selenium_driver.set_window_size(width, height)
            self.selenium_driver.get(url)
            
            # Poczekaj na załadowanie strony
            await asyncio.sleep(2)
            
            self.selenium_driver.save_screenshot(str(output_path))
            
            self.logger.info(f"Screenshot Selenium: {url} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd Selenium screenshot: {e}")
            return False
    
    async def _capture_url_wkhtmltopdf(self, url: str, output_path: Path,
                                      width: int, height: int) -> bool:
        """Screenshot z użyciem wkhtmltopdf (via wkhtmltoimage)."""
        try:
            cmd = [
                'wkhtmltoimage',
                '--width', str(width),
                '--height', str(height),
                '--format', 'png',
                '--javascript-delay', '2000',
                url,
                str(output_path)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                self.logger.info(f"Screenshot wkhtmltoimage: {url} -> {output_path}")
                return True
            else:
                self.logger.error(f"wkhtmltoimage error: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Błąd wkhtmltoimage screenshot: {e}")
            return False
    
    async def _capture_url_fallback(self, url: str, output_path: Path) -> bool:
        """Fallback - tworzy placeholder image."""
        try:
            # Utwórz prosty placeholder PNG
            placeholder_content = self._create_placeholder_image(url)
            
            with open(output_path, 'wb') as f:
                f.write(placeholder_content)
            
            self.logger.warning(f"Screenshot fallback (placeholder): {url} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd fallback screenshot: {e}")
            return False
    
    def _create_placeholder_image(self, text: str) -> bytes:
        """Tworzy prosty placeholder PNG z tekstem."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Utwórz obraz 800x600
            img = Image.new('RGB', (800, 600), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Dodaj tekst
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 50), f"Screenshot Placeholder", fill='black', font=font)
            draw.text((50, 100), f"URL: {text}", fill='darkblue', font=font)
            draw.text((50, 550), "Install playwright or selenium for real screenshots", 
                     fill='gray', font=font)
            
            # Zapisz do bytes
            import io
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except ImportError:
            # Jeśli PIL nie jest dostępne, utwórz minimalny PNG
            return self._create_minimal_png()
    
    def _create_minimal_png(self) -> bytes:
        """Tworzy minimalny PNG (1x1 pixel)."""
        # Minimalny PNG 1x1 transparent pixel
        return bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
            0x89, 0x00, 0x00, 0x00, 0x0D, 0x49, 0x44, 0x41,
            0x54, 0x78, 0x9C, 0x63, 0xF8, 0x0F, 0x00, 0x01,
            0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D, 0xB4, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
            0x42, 0x60, 0x82
        ])
    
    async def cleanup(self):
        """Czyści zasoby."""
        try:
            if hasattr(self, 'playwright_browser') and self.playwright_browser:
                await self.playwright_browser.close()
                await self.playwright.stop()
            
            if hasattr(self, 'selenium_driver'):
                self.selenium_driver.quit()
                
        except Exception as e:
            self.logger.error(f"Błąd podczas czyszczenia zasobów: {e}")


# Singleton instance
_screenshot_capture = None

async def get_screenshot_capture() -> ScreenshotCapture:
    """Zwraca singleton instance ScreenshotCapture."""
    global _screenshot_capture
    if _screenshot_capture is None:
        _screenshot_capture = ScreenshotCapture()
        await _screenshot_capture.setup()
    return _screenshot_capture


# Convenience functions
async def capture_url_screenshot(url: str, output_path: Path) -> bool:
    """Convenience function do robienia screenshotu URL."""
    capture = await get_screenshot_capture()
    return await capture.capture_url(url, output_path)


async def capture_html_screenshot(html_file: Path, output_path: Path) -> bool:
    """Convenience function do robienia screenshotu pliku HTML."""
    capture = await get_screenshot_capture()
    return await capture.capture_html_file(html_file, output_path)
