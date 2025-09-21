"""
WhyML Core String Utilities - Advanced string processing and manipulation

Provides comprehensive string manipulation functions including text processing,
formatting, validation, and conversion utilities for WhyML operations.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import html
import unicodedata
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import quote, unquote
from ..exceptions import ValidationError


class StringUtils:
    """Utility functions for advanced string operations."""
    
    @staticmethod
    def normalize_whitespace(text: str, 
                           preserve_paragraphs: bool = True) -> str:
        """Normalize whitespace in text.
        
        Args:
            text: Text to normalize
            preserve_paragraphs: Whether to preserve paragraph breaks
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        if preserve_paragraphs:
            # Split by double newlines (paragraphs)
            paragraphs = re.split(r'\n\s*\n', text)
            normalized_paragraphs = []
            
            for paragraph in paragraphs:
                # Normalize whitespace within paragraph
                normalized = re.sub(r'\s+', ' ', paragraph.strip())
                if normalized:
                    normalized_paragraphs.append(normalized)
            
            return '\n\n'.join(normalized_paragraphs)
        else:
            # Simple whitespace normalization
            return re.sub(r'\s+', ' ', text.strip())
    
    @staticmethod
    def truncate_text(text: str, 
                     max_length: int,
                     suffix: str = "...",
                     word_boundary: bool = True) -> str:
        """Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length including suffix
            suffix: Suffix to add when truncating
            word_boundary: Whether to respect word boundaries
            
        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text
        
        if len(suffix) >= max_length:
            return text[:max_length]
        
        target_length = max_length - len(suffix)
        
        if not word_boundary:
            return text[:target_length] + suffix
        
        # Find last word boundary
        truncated = text[:target_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return text[:last_space] + suffix
        else:
            return text[:target_length] + suffix
    
    @staticmethod
    def extract_words(text: str, 
                     min_length: int = 2,
                     exclude_numbers: bool = True) -> List[str]:
        """Extract words from text.
        
        Args:
            text: Text to extract words from
            min_length: Minimum word length
            exclude_numbers: Whether to exclude numeric strings
            
        Returns:
            List of extracted words
        """
        if not text:
            return []
        
        # Extract word-like sequences
        word_pattern = r'\b[a-zA-Z]+\b' if exclude_numbers else r'\b\w+\b'
        words = re.findall(word_pattern, text, re.UNICODE)
        
        # Filter by length and clean
        filtered_words = []
        for word in words:
            word = word.lower().strip()
            if len(word) >= min_length:
                filtered_words.append(word)
        
        return filtered_words
    
    @staticmethod
    def count_words(text: str, unique_only: bool = False) -> int:
        """Count words in text.
        
        Args:
            text: Text to count words in
            unique_only: Whether to count only unique words
            
        Returns:
            Word count
        """
        words = StringUtils.extract_words(text, min_length=1, exclude_numbers=False)
        
        if unique_only:
            return len(set(words))
        else:
            return len(words)
    
    @staticmethod
    def calculate_reading_time(text: str, 
                             words_per_minute: int = 200) -> int:
        """Calculate estimated reading time in minutes.
        
        Args:
            text: Text to analyze
            words_per_minute: Average reading speed
            
        Returns:
            Reading time in minutes
        """
        word_count = StringUtils.count_words(text)
        reading_time = max(1, round(word_count / words_per_minute))
        return reading_time
    
    @staticmethod
    def slugify(text: str, 
               max_length: int = 50,
               separator: str = "-") -> str:
        """Convert text to URL-friendly slug.
        
        Args:
            text: Text to slugify
            max_length: Maximum slug length
            separator: Word separator character
            
        Returns:
            URL-friendly slug
        """
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to ASCII, removing non-ASCII characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace spaces and special chars with separator
        text = re.sub(r'[^a-z0-9]+', separator, text)
        
        # Remove leading/trailing separators
        text = text.strip(separator)
        
        # Collapse multiple separators
        text = re.sub(f'{re.escape(separator)}+', separator, text)
        
        # Truncate if necessary
        if len(text) > max_length:
            text = text[:max_length].rstrip(separator)
        
        return text
    
    @staticmethod
    def escape_html(text: str, quote: bool = True) -> str:
        """Escape HTML entities in text.
        
        Args:
            text: Text to escape
            quote: Whether to escape quotes
            
        Returns:
            HTML-escaped text
        """
        if not text:
            return ""
        
        return html.escape(text, quote=quote)
    
    @staticmethod
    def unescape_html(text: str) -> str:
        """Unescape HTML entities in text.
        
        Args:
            text: Text to unescape
            
        Returns:
            Unescaped text
        """
        if not text:
            return ""
        
        return html.unescape(text)
    
    @staticmethod
    def strip_html_tags(text: str, 
                       preserve_entities: bool = False) -> str:
        """Remove HTML tags from text.
        
        Args:
            text: Text containing HTML
            preserve_entities: Whether to preserve HTML entities
            
        Returns:
            Text with HTML tags removed
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Optionally unescape HTML entities
        if not preserve_entities:
            text = StringUtils.unescape_html(text)
        
        return StringUtils.normalize_whitespace(text)
    
    @staticmethod
    def extract_urls(text: str, 
                    schemes: Optional[List[str]] = None) -> List[str]:
        """Extract URLs from text.
        
        Args:
            text: Text to extract URLs from
            schemes: Optional list of URL schemes to match
            
        Returns:
            List of found URLs
        """
        if not text:
            return []
        
        if schemes:
            scheme_pattern = '|'.join(re.escape(scheme) for scheme in schemes)
            url_pattern = rf'\b(?:{scheme_pattern})://[^\s<>"{{}}|\\^`\[\]]*'
        else:
            url_pattern = r'\bhttps?://[^\s<>"{}|\\^`\[\]]*'
        
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return urls
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text.
        
        Args:
            text: Text to extract emails from
            
        Returns:
            List of found email addresses
        """
        if not text:
            return []
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails
    
    @staticmethod
    def mask_sensitive_data(text: str, 
                           patterns: Optional[Dict[str, str]] = None,
                           mask_char: str = "*") -> str:
        """Mask sensitive data in text.
        
        Args:
            text: Text to mask
            patterns: Custom patterns to mask (name -> regex)
            mask_char: Character to use for masking
            
        Returns:
            Text with sensitive data masked
        """
        if not text:
            return text
        
        result = text
        
        # Default patterns
        default_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        }
        
        # Merge with custom patterns
        all_patterns = default_patterns.copy()
        if patterns:
            all_patterns.update(patterns)
        
        # Apply masking
        for pattern_name, pattern in all_patterns.items():
            def mask_match(match):
                matched_text = match.group(0)
                return mask_char * len(matched_text)
            
            result = re.sub(pattern, mask_match, result, flags=re.IGNORECASE)
        
        return result
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid
        """
        if not email or len(email) > 254:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_url(url: str, 
                    schemes: Optional[List[str]] = None) -> bool:
        """Validate URL format.
        
        Args:
            url: URL to validate
            schemes: Optional list of allowed schemes
            
        Returns:
            True if URL is valid
        """
        if not url:
            return False
        
        schemes = schemes or ['http', 'https']
        
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return (result.scheme in schemes and 
                   bool(result.netloc) and 
                   bool(result.scheme))
        except Exception:
            return False
    
    @staticmethod
    def format_bytes(bytes_count: int, 
                    decimal_places: int = 2) -> str:
        """Format byte count as human-readable string.
        
        Args:
            bytes_count: Number of bytes
            decimal_places: Number of decimal places
            
        Returns:
            Formatted byte string (e.g., "1.5 MB")
        """
        if bytes_count == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        
        for unit in units:
            if bytes_count < 1024:
                if unit == 'B':
                    return f"{bytes_count} {unit}"
                else:
                    return f"{bytes_count:.{decimal_places}f} {unit}"
            bytes_count /= 1024
        
        return f"{bytes_count:.{decimal_places}f} {units[-1]}"
    
    @staticmethod
    def generate_excerpt(text: str, 
                        max_length: int = 150,
                        sentence_boundary: bool = True) -> str:
        """Generate excerpt from text.
        
        Args:
            text: Source text
            max_length: Maximum excerpt length
            sentence_boundary: Whether to respect sentence boundaries
            
        Returns:
            Text excerpt
        """
        if not text or len(text) <= max_length:
            return text
        
        if sentence_boundary:
            # Try to find sentence boundary
            sentences = re.split(r'[.!?]+', text)
            excerpt = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                test_excerpt = f"{excerpt} {sentence}".strip()
                if len(test_excerpt) <= max_length:
                    excerpt = test_excerpt
                else:
                    break
            
            if excerpt and len(excerpt) > 20:  # Minimum viable excerpt
                return excerpt + "."
        
        # Fallback to word boundary truncation
        return StringUtils.truncate_text(text, max_length, word_boundary=True)
    
    @staticmethod
    def clean_text(text: str, 
                  remove_extra_whitespace: bool = True,
                  remove_html: bool = False,
                  normalize_unicode: bool = False) -> str:
        """Clean and normalize text.
        
        Args:
            text: Text to clean
            remove_extra_whitespace: Whether to normalize whitespace
            remove_html: Whether to strip HTML tags
            normalize_unicode: Whether to normalize Unicode
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        result = text
        
        # Remove HTML if requested
        if remove_html:
            result = StringUtils.strip_html_tags(result)
        
        # Normalize unicode if requested
        if normalize_unicode:
            result = unicodedata.normalize('NFKC', result)
        
        # Remove extra whitespace if requested
        if remove_extra_whitespace:
            result = StringUtils.normalize_whitespace(result)
        
        return result
    
    @staticmethod
    def smart_title_case(text: str, 
                        small_words: Optional[List[str]] = None) -> str:
        """Convert text to smart title case.
        
        Args:
            text: Text to convert
            small_words: List of words to keep lowercase (unless first/last)
            
        Returns:
            Title-cased text
        """
        if not text:
            return ""
        
        # Default small words
        default_small_words = [
            'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 
            'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet'
        ]
        
        small_words = small_words or default_small_words
        small_words_lower = [word.lower() for word in small_words]
        
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                result.append(word.capitalize())
            # Keep small words lowercase
            elif word.lower() in small_words_lower:
                result.append(word.lower())
            # Capitalize other words
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
