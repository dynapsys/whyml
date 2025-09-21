"""
Test suite for whyml_scrapers.content_extractor module

Tests for:
- ContentExtractor functionality
- Text extraction
- Media extraction
- Link extraction
- Metadata extraction

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from whyml_scrapers.content_extractor import ContentExtractor


class TestContentExtractor:
    """Test cases for ContentExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create a ContentExtractor instance for testing."""
        return ContentExtractor()
    
    @pytest.fixture
    def rich_content_html(self):
        """Create HTML with rich content for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Rich Content Page</title>
            <meta name="description" content="Page with various content types">
            <meta name="author" content="John Doe">
        </head>
        <body>
            <header>
                <h1>Main Title</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                    <a href="/contact">Contact</a>
                </nav>
            </header>
            
            <main>
                <article>
                    <h2>Article Title</h2>
                    <p>This is the first paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
                    <p>Second paragraph with a <a href="https://example.com">external link</a>.</p>
                    
                    <img src="/images/article-image.jpg" alt="Article illustration" width="600" height="400">
                    
                    <ul>
                        <li>List item 1</li>
                        <li>List item 2</li>
                        <li>List item 3</li>
                    </ul>
                    
                    <blockquote>
                        "This is an important quote from the article."
                    </blockquote>
                </article>
                
                <aside>
                    <h3>Related Links</h3>
                    <ul>
                        <li><a href="/related-1">Related Article 1</a></li>
                        <li><a href="/related-2">Related Article 2</a></li>
                    </ul>
                </aside>
            </main>
            
            <footer>
                <p>&copy; 2025 Test Site</p>
                <div class="social-links">
                    <a href="https://twitter.com/testsite">Twitter</a>
                    <a href="https://facebook.com/testsite">Facebook</a>
                </div>
            </footer>
        </body>
        </html>
        """
    
    def test_extractor_initialization(self, extractor):
        """Test ContentExtractor initialization."""
        assert extractor is not None
        assert hasattr(extractor, 'extract_content')
        assert hasattr(extractor, 'extract_text')
        assert hasattr(extractor, 'extract_links')
        assert hasattr(extractor, 'extract_images')
    
    def test_extract_text_content(self, extractor, rich_content_html):
        """Test text content extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        text_content = extractor.extract_text(soup)
        
        assert isinstance(text_content, dict)
        assert 'headings' in text_content
        assert 'paragraphs' in text_content
        assert 'lists' in text_content
        
        # Should extract headings
        assert len(text_content['headings']) >= 3  # h1, h2, h3
        
        # Should extract paragraphs
        assert len(text_content['paragraphs']) >= 2
        
        # Should contain expected content
        assert any('Main Title' in heading for heading in text_content['headings'])
        assert any('first paragraph' in para for para in text_content['paragraphs'])
    
    def test_extract_links(self, extractor, rich_content_html):
        """Test link extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        links = extractor.extract_links(soup)
        
        assert isinstance(links, list)
        assert len(links) > 0
        
        # Should extract various types of links
        external_links = [link for link in links if link.get('href', '').startswith('http')]
        internal_links = [link for link in links if link.get('href', '').startswith('/')]
        
        assert len(external_links) > 0  # https://example.com, social links
        assert len(internal_links) > 0  # navigation and related links
        
        # Check link structure
        for link in links:
            assert 'href' in link
            assert 'text' in link
            assert 'type' in link  # internal, external, etc.
    
    def test_extract_images(self, extractor, rich_content_html):
        """Test image extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        images = extractor.extract_images(soup)
        
        assert isinstance(images, list)
        assert len(images) >= 1
        
        # Check image structure
        for image in images:
            assert 'src' in image
            if 'alt' in image:
                assert isinstance(image['alt'], str)
            if 'width' in image:
                assert isinstance(image['width'], (str, int))
    
    def test_extract_metadata(self, extractor, rich_content_html):
        """Test metadata extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        metadata = extractor.extract_metadata(soup)
        
        assert isinstance(metadata, dict)
        assert 'title' in metadata
        assert 'description' in metadata
        
        assert metadata['title'] == 'Rich Content Page'
        assert metadata['description'] == 'Page with various content types'
        
        # Should extract author meta tag
        if 'author' in metadata:
            assert metadata['author'] == 'John Doe'
    
    def test_extract_all_content(self, extractor, rich_content_html):
        """Test comprehensive content extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        content = extractor.extract_content(soup)
        
        assert isinstance(content, dict)
        assert 'text' in content
        assert 'links' in content
        assert 'images' in content
        assert 'metadata' in content
        
        # Should have extracted all content types
        assert len(content['text']['headings']) > 0
        assert len(content['links']) > 0
        assert len(content['images']) > 0
    
    def test_extract_social_media_links(self, extractor, rich_content_html):
        """Test social media link extraction."""
        soup = BeautifulSoup(rich_content_html, 'html.parser')
        links = extractor.extract_links(soup)
        
        social_links = [
            link for link in links 
            if any(social in link.get('href', '') for social in ['twitter', 'facebook', 'instagram', 'linkedin'])
        ]
        
        assert len(social_links) >= 2  # Twitter and Facebook
        
        for social_link in social_links:
            assert social_link['type'] == 'external'
    
    def test_extract_structured_data(self, extractor):
        """Test structured data extraction."""
        structured_html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article",
                "author": "John Doe",
                "datePublished": "2025-01-01"
            }
            </script>
        </head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>Article content</p>
            </article>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(structured_html, 'html.parser')
        
        # Test structured data extraction if method exists
        if hasattr(extractor, 'extract_structured_data'):
            structured_data = extractor.extract_structured_data(soup)
            assert isinstance(structured_data, (dict, list))
        
        # Alternative: test in general content extraction
        content = extractor.extract_content(soup)
        assert isinstance(content, dict)
    
    def test_extract_tables(self, extractor):
        """Test table extraction."""
        table_html = """
        <html>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>City</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>John</td>
                        <td>25</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>30</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(table_html, 'html.parser')
        
        # Test table extraction if method exists
        if hasattr(extractor, 'extract_tables'):
            tables = extractor.extract_tables(soup)
            assert isinstance(tables, list)
            if tables:
                assert 'headers' in tables[0]
                assert 'rows' in tables[0]
        
        # Alternative: test in general content extraction
        content = extractor.extract_content(soup)
        assert isinstance(content, dict)
    
    def test_extract_forms(self, extractor):
        """Test form extraction."""
        form_html = """
        <html>
        <body>
            <form action="/submit" method="POST">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                
                <label for="message">Message:</label>
                <textarea id="message" name="message"></textarea>
                
                <button type="submit">Send</button>
            </form>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(form_html, 'html.parser')
        
        # Test form extraction if method exists
        if hasattr(extractor, 'extract_forms'):
            forms = extractor.extract_forms(soup)
            assert isinstance(forms, list)
            if forms:
                assert 'action' in forms[0]
                assert 'method' in forms[0]
                assert 'fields' in forms[0]
        
        # Alternative: test in general content extraction
        content = extractor.extract_content(soup)
        assert isinstance(content, dict)
    
    def test_empty_page_extraction(self, extractor):
        """Test extraction from empty page."""
        empty_html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(empty_html, 'html.parser')
        
        content = extractor.extract_content(soup)
        
        assert isinstance(content, dict)
        assert content['text']['headings'] == []
        assert content['links'] == []
        assert content['images'] == []
    
    def test_malformed_html_extraction(self, extractor):
        """Test extraction from malformed HTML."""
        malformed_html = """
        <html>
        <head>
            <title>Malformed Page
        <body>
            <h1>Title without closing
            <p>Content without closing
            <a href="/link">Link without closing
        """
        
        soup = BeautifulSoup(malformed_html, 'html.parser')
        content = extractor.extract_content(soup)
        
        # Should handle malformed HTML gracefully
        assert isinstance(content, dict)
        assert 'text' in content
        assert 'links' in content


class TestContentExtractorFiltering:
    """Test cases for ContentExtractor filtering and options."""
    
    @pytest.fixture
    def filtering_extractor(self):
        """Create ContentExtractor with filtering options."""
        return ContentExtractor(
            include_external_links=True,
            include_images=True,
            min_text_length=10,
            exclude_tags=['script', 'style']
        )
    
    def test_filtered_extraction(self, filtering_extractor):
        """Test content extraction with filters."""
        html_with_noise = """
        <html>
        <head>
            <style>body { color: red; }</style>
            <script>console.log('test');</script>
        </head>
        <body>
            <h1>Important Title</h1>
            <p>This is important content that should be extracted.</p>
            <p>Short</p>
            <script>alert('noise');</script>
            <div style="display:none;">Hidden content</div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_noise, 'html.parser')
        content = filtering_extractor.extract_content(soup)
        
        assert isinstance(content, dict)
        
        # Should filter out script and style content
        text_content = ' '.join(content['text']['paragraphs'])
        assert 'console.log' not in text_content
        assert 'color: red' not in text_content
        
        # Should include content meeting minimum length
        long_paragraphs = [p for p in content['text']['paragraphs'] if len(p) >= 10]
        assert len(long_paragraphs) > 0


if __name__ == "__main__":
    pytest.main([__file__])
