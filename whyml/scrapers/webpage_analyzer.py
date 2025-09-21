"""
Webpage Analyzer - Advanced analysis and structure detection for web pages

Provides intelligent analysis of webpage structure, content patterns,
and automatic categorization for optimal manifest generation.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
try:
    from bs4 import BeautifulSoup, Tag, NavigableString
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    # Fallback classes for when BS4 is not available
    class BeautifulSoup:
        def __init__(self, *args, **kwargs):
            raise ImportError("beautifulsoup4 is required for web scraping. Install with: pip install beautifulsoup4")
    
    class Tag:
        pass
    
    class NavigableString:
        pass
from collections import Counter
import logging

from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class WebpageAnalyzer:
    """
    Analyze webpage structure and content for intelligent manifest generation.
    
    Features:
    - Content type detection
    - Layout pattern recognition  
    - Component identification
    - Accessibility analysis
    - Performance optimization suggestions
    """
    
    def __init__(self, 
                 min_content_length: int = 50,
                 max_nesting_depth: int = 10,
                 analyze_accessibility: bool = True,
                 # Structure simplification parameters
                 max_depth: Optional[int] = None,
                 flatten_containers: bool = False,
                 simplify_structure: bool = False,
                 preserve_semantic_tags: bool = True):
        """
        Initialize webpage analyzer.
        
        Args:
            min_content_length: Minimum content length to consider substantial
            max_nesting_depth: Maximum nesting depth to analyze
            analyze_accessibility: Whether to perform accessibility analysis
            max_depth: Maximum nesting depth for structure simplification
            flatten_containers: Whether container flattening was applied
            simplify_structure: Whether structure simplification was applied
            preserve_semantic_tags: Whether semantic tags are preserved
        """
        self.min_content_length = min_content_length
        self.max_nesting_depth = max_nesting_depth
        self.analyze_accessibility = analyze_accessibility
        
        # Simplification parameters
        self.max_depth = max_depth
        self.flatten_containers = flatten_containers
        self.simplify_structure = simplify_structure
        self.preserve_semantic_tags = preserve_semantic_tags
    
    def analyze_webpage(self, soup: BeautifulSoup, url: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive webpage analysis.
        
        Args:
            soup: BeautifulSoup parsed HTML
            url: Source URL (optional)
            
        Returns:
            Analysis results dictionary
        """
        analysis = {
            'page_type': self._detect_page_type(soup),
            'layout_structure': self._analyze_layout_structure(soup),
            'content_sections': self._identify_content_sections(soup),
            'navigation_elements': self._find_navigation_elements(soup),
            'interactive_elements': self._find_interactive_elements(soup),
            'media_elements': self._analyze_media_elements(soup),
            'semantic_structure': self._analyze_semantic_structure(soup),
            'component_patterns': self._detect_component_patterns(soup),
            'optimization_suggestions': self._generate_optimization_suggestions(soup),
            'structure_complexity': self._analyze_structure_complexity(soup)
        }
        
        if self.analyze_accessibility:
            analysis['accessibility'] = self._analyze_accessibility(soup)
        
        if url:
            analysis['url_analysis'] = self._analyze_url_structure(url)
        
        return analysis
    
    def _detect_page_type(self, soup: BeautifulSoup) -> str:
        """Detect the type of webpage (blog, product, landing, etc.)."""
        # Check for common page type indicators
        indicators = {
            'blog': ['article', '.post', '.blog-post', '.entry', 'time[datetime]'],
            'product': ['.product', '.item', '.price', '.buy-button', '.add-to-cart'],
            'landing': ['.hero', '.cta', '.testimonials', '.features'],
            'portfolio': ['.portfolio', '.gallery', '.project', '.work'],
            'contact': ['form[name*="contact"]', '.contact-form', 'input[type="email"]'],
            'about': ['.about', '.team', '.biography', '.company'],
            'news': ['.news', '.article-list', '.headline', '.breaking'],
            'ecommerce': ['.cart', '.checkout', '.product-list', '.catalog'],
            'documentation': ['.docs', '.api-docs', '.documentation', '.guide'],
            'dashboard': ['.dashboard', '.stats', '.metrics', '.analytics']
        }
        
        scores = {}
        for page_type, selectors in indicators.items():
            score = 0
            for selector in selectors:
                elements = soup.select(selector)
                score += len(elements) * 2  # Weight by number of matching elements
                
                # Check for keywords in text content
                if any(page_type in soup.get_text().lower() for _ in range(1)):
                    score += 1
            
            scores[page_type] = score
        
        # Return the type with highest score, or 'general' if no clear match
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                result_type = best_type[0]
                
                # Map specific types to broader categories where appropriate
                if result_type == 'product':
                    return 'e-commerce'
                elif result_type == 'ecommerce':
                    return 'e-commerce'
                
                return result_type
            else:
                return 'general'
        
        return 'general'
    
    def _analyze_layout_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the overall layout structure."""
        structure = {
            'has_header': bool(soup.find(['header', '[role="banner"]'])),
            'has_footer': bool(soup.find(['footer', '[role="contentinfo"]'])),
            'has_sidebar': bool(soup.find(['aside', '.sidebar', '.side-nav'])),
            'has_navigation': bool(soup.find(['nav', '[role="navigation"]'])),
            'main_content_area': self._find_main_content_selector(soup),
            'layout_type': self._detect_layout_type(soup),
            'grid_structure': self._analyze_grid_structure(soup),
            'responsive_breakpoints': self._detect_responsive_breakpoints(soup)
        }
        
        return structure
    
    def _find_main_content_selector(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the selector for the main content area."""
        main_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#main',
            '#content',
            'article',
            '.post-content',
            '.page-content'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element and self._has_substantial_content(element):
                return selector
        
        return None
    
    def _detect_layout_type(self, soup: BeautifulSoup) -> str:
        """Detect common layout patterns."""
        # Check for common CSS frameworks and layout patterns
        body_classes = list(soup.body.get('class', [])) if soup.body else []
        html_classes = list(soup.html.get('class', [])) if soup.html else []
        all_classes = ' '.join(body_classes + html_classes).lower()
        
        if any(fw in all_classes for fw in ['bootstrap', 'bs-', 'container']):
            return 'bootstrap'
        elif any(fw in all_classes for fw in ['foundation', 'row', 'column']):
            return 'foundation'
        elif any(fw in all_classes for fw in ['bulma', 'columns', 'column']):
            return 'bulma'
        elif any(fw in all_classes for fw in ['tailwind', 'tw-']):
            return 'tailwind'
        
        # Check for common layout patterns
        if soup.find('.grid') or soup.find('[class*="grid"]'):
            return 'css-grid'
        elif soup.find('.flex') or soup.find('[class*="flex"]'):
            return 'flexbox'
        elif soup.find('.float-left') or soup.find('.float-right'):
            return 'float-based'
        
        return 'custom'
    
    def _analyze_grid_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze grid/column structure."""
        grid_info = {
            'has_grid': False,
            'grid_containers': [],
            'column_patterns': [],
            'max_columns': 0
        }
        
        # Look for grid containers
        grid_selectors = [
            '.grid', '.row', '.columns', '.grid-container',
            '[class*="grid"]', '[class*="row"]', '[class*="col"]'
        ]
        
        for selector in grid_selectors:
            elements = soup.select(selector)
            if elements:
                grid_info['has_grid'] = True
                for element in elements[:5]:  # Limit to first 5
                    grid_info['grid_containers'].append({
                        'tag': element.name,
                        'classes': list(element.get('class', [])),
                        'children_count': len(element.find_all(recursive=False))
                    })
        
        # Analyze column patterns
        col_elements = soup.select('[class*="col"], [class*="column"]')
        if col_elements:
            column_classes = []
            for elem in col_elements:
                classes = list(elem.get('class', []))
                column_classes.extend([cls for cls in classes if 'col' in cls.lower()])
            
            # Count column patterns
            col_counter = Counter(column_classes)
            grid_info['column_patterns'] = list(col_counter.most_common(10))
            
            # Try to determine max columns
            col_numbers = []
            for cls in column_classes:
                numbers = re.findall(r'\d+', cls)
                col_numbers.extend([int(n) for n in numbers if int(n) <= 12])
            
            if col_numbers:
                grid_info['max_columns'] = max(col_numbers)
        
        return grid_info
    
    def _detect_responsive_breakpoints(self, soup: BeautifulSoup) -> List[str]:
        """Detect responsive design breakpoints from classes."""
        breakpoint_patterns = [
            r'sm[-:]', r'md[-:]', r'lg[-:]', r'xl[-:]',  # Bootstrap/Tailwind
            r'small[-:]', r'medium[-:]', r'large[-:]',  # Foundation
            r'mobile[-:]', r'tablet[-:]', r'desktop[-:]'  # Custom
        ]
        
        all_classes = []
        for element in soup.find_all(class_=True):
            all_classes.extend(list(element.get('class', [])))
        
        breakpoints = set()
        for class_name in all_classes:
            for pattern in breakpoint_patterns:
                if re.search(pattern, class_name, re.IGNORECASE):
                    # Extract breakpoint name
                    match = re.search(r'(sm|md|lg|xl|small|medium|large|mobile|tablet|desktop)', 
                                    class_name, re.IGNORECASE)
                    if match:
                        breakpoints.add(match.group(1).lower())
        
        return sorted(list(breakpoints))
    
    def _identify_content_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify distinct content sections."""
        sections = []
        
        # Look for semantic sections
        section_elements = soup.find_all(['section', 'article', 'div[class*="section"]'])
        
        for element in section_elements:
            if self._has_substantial_content(element):
                section_info = {
                    'tag': element.name,
                    'classes': list(element.get('class', [])),
                    'id': element.get('id'),
                    'content_type': self._classify_content_type(element),
                    'word_count': len(element.get_text().split()),
                    'has_images': bool(element.find('img')),
                    'has_links': bool(element.find('a')),
                    'has_forms': bool(element.find('form')),
                    'nesting_level': self._get_nesting_level(element)
                }
                sections.append(section_info)
        
        return sections[:20]  # Limit to first 20 sections
    
    def _classify_content_type(self, element: Tag) -> str:
        """Classify the type of content in an element."""
        text = element.get_text().lower()
        classes = ' '.join(list(element.get('class', []))).lower()
        
        # Classification based on content and classes
        if any(keyword in text for keyword in ['subscribe', 'newsletter', 'email']):
            return 'newsletter'
        elif any(keyword in classes for keyword in ['hero', 'banner', 'jumbotron']):
            return 'hero'
        elif any(keyword in classes for keyword in ['testimonial', 'review']):
            return 'testimonial'
        elif any(keyword in classes for keyword in ['feature', 'benefit']):
            return 'features'
        elif any(keyword in classes for keyword in ['team', 'staff', 'member']):
            return 'team'
        elif any(keyword in text for keyword in ['contact', 'reach', 'phone', 'email']):
            return 'contact'
        elif element.find('form'):
            return 'form'
        elif element.find('img') and len(element.find_all('img')) > 3:
            return 'gallery'
        elif any(keyword in classes for keyword in ['card', 'post', 'article']):
            return 'content_card'
        else:
            return 'general'
    
    def _find_navigation_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find and analyze navigation elements."""
        nav_info = {
            'main_nav': None,
            'breadcrumbs': None,
            'pagination': None,
            'secondary_nav': [],
            'mobile_nav': None
        }
        
        # Main navigation
        main_nav = soup.find('nav') or soup.find('[role="navigation"]')
        if main_nav:
            nav_info['main_nav'] = {
                'tag': main_nav.name,
                'classes': list(main_nav.get('class', [])),
                'links_count': len(main_nav.find_all('a')),
                'has_dropdown': bool(main_nav.find('.dropdown, .submenu'))
            }
        
        # Breadcrumbs
        breadcrumb_selectors = ['.breadcrumb', '.breadcrumbs', '[aria-label*="breadcrumb"]']
        for selector in breadcrumb_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                nav_info['breadcrumbs'] = {
                    'selector': selector,
                    'items_count': len(breadcrumb.find_all('a')) + len(breadcrumb.find_all('span'))
                }
                break
        
        # Pagination
        pagination_selectors = ['.pagination', '.pager', '.page-numbers']
        for selector in pagination_selectors:
            pagination = soup.select_one(selector)
            if pagination:
                nav_info['pagination'] = {
                    'selector': selector,
                    'pages_count': len(pagination.find_all('a'))
                }
                break
        
        return nav_info
    
    def _find_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find and analyze interactive elements."""
        interactive = {
            'forms': [],
            'buttons': [],
            'modals': [],
            'tabs': [],
            'accordions': [],
            'sliders': []
        }
        
        # Forms
        forms = soup.find_all('form')
        for form in forms:
            form_info = {
                'action': form.get('action'),
                'method': form.get('method', 'GET'),
                'inputs_count': len(form.find_all(['input', 'textarea', 'select'])),
                'has_validation': bool(form.find('[required], [pattern]'))
            }
            interactive['forms'].append(form_info)
        
        # Buttons
        buttons = soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
        for button in buttons:
            button_info = {
                'type': button.get('type', 'button'),
                'classes': list(button.get('class', [])),
                'has_onclick': bool(button.get('onclick'))
            }
            interactive['buttons'].append(button_info)
        
        # Look for common interactive patterns
        modal_indicators = soup.select('.modal, [data-toggle="modal"], [data-bs-toggle="modal"]')
        interactive['modals'] = [{'classes': list(el.get('class', []))} for el in modal_indicators]
        
        tab_indicators = soup.select('.tabs, .nav-tabs, [role="tablist"]')
        interactive['tabs'] = [{'classes': list(el.get('class', []))} for el in tab_indicators]
        
        return interactive
    
    def _analyze_media_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze media elements (images, videos, etc.)."""
        media = {
            'images': {
                'count': 0,
                'has_alt_text': 0,
                'has_lazy_loading': 0,
                'responsive_images': 0,
                'formats': set()
            },
            'videos': {
                'count': 0,
                'embedded': 0,
                'local': 0
            },
            'audio': {
                'count': 0
            }
        }
        
        # Analyze images
        images = soup.find_all('img')
        media['images']['count'] = len(images)
        
        for img in images:
            if img.get('alt'):
                media['images']['has_alt_text'] += 1
            if img.get('loading') == 'lazy':
                media['images']['has_lazy_loading'] += 1
            if img.get('srcset') or img.get('sizes'):
                media['images']['responsive_images'] += 1
            
            src = img.get('src', '')
            if src:
                # Extract file extension
                ext_match = re.search(r'\.(\w+)(?:\?|$)', src.lower())
                if ext_match:
                    media['images']['formats'].add(ext_match.group(1))
        
        # Convert set to list for JSON serialization
        media['images']['formats'] = list(media['images']['formats'])
        
        # Analyze videos
        videos = soup.find_all(['video', 'iframe[src*="youtube"]', 'iframe[src*="vimeo"]'])
        media['videos']['count'] = len(videos)
        
        for video in videos:
            if video.name == 'iframe':
                media['videos']['embedded'] += 1
            else:
                media['videos']['local'] += 1
        
        # Analyze audio
        audio = soup.find_all('audio')
        media['audio']['count'] = len(audio)
        
        return media
    
    def _analyze_semantic_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze semantic HTML structure."""
        semantic = {
            'heading_structure': self._analyze_heading_structure(soup),
            'landmark_roles': self._find_landmark_roles(soup),
            'semantic_elements': self._count_semantic_elements(soup),
            'structured_data': self._find_structured_data(soup)
        }
        
        return semantic
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading hierarchy."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        structure = {
            'count_by_level': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
            'total_count': len(headings),
            'has_proper_hierarchy': True,
            'outline': []
        }
        
        prev_level = 0
        for heading in headings:
            level = int(heading.name[1])
            structure['count_by_level'][heading.name] += 1
            
            # Check for proper hierarchy (no skipping levels)
            if level > prev_level + 1:
                structure['has_proper_hierarchy'] = False
            
            structure['outline'].append({
                'level': level,
                'text': heading.get_text().strip()[:100],  # Limit length
                'id': heading.get('id')
            })
            
            prev_level = level
        
        return structure
    
    def _find_landmark_roles(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Find ARIA landmark roles."""
        landmarks = {
            'banner': 0, 'navigation': 0, 'main': 0, 'complementary': 0,
            'contentinfo': 0, 'search': 0, 'form': 0, 'region': 0
        }
        
        for role in landmarks.keys():
            elements = soup.find_all(attrs={'role': role})
            landmarks[role] = len(elements)
        
        return landmarks
    
    def _count_semantic_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Count semantic HTML5 elements."""
        semantic_elements = [
            'header', 'nav', 'main', 'section', 'article', 'aside', 
            'footer', 'figure', 'figcaption', 'time', 'mark'
        ]
        
        counts = {}
        for element in semantic_elements:
            counts[element] = len(soup.find_all(element))
        
        return counts
    
    def _find_structured_data(self, soup: BeautifulSoup) -> List[str]:
        """Find structured data formats."""
        structured_data = []
        
        # JSON-LD
        if soup.find('script', type='application/ld+json'):
            structured_data.append('JSON-LD')
        
        # Microdata
        if soup.find(attrs={'itemscope': True}):
            structured_data.append('Microdata')
        
        # RDFa
        if soup.find(attrs={'typeof': True}) or soup.find(attrs={'property': True}):
            structured_data.append('RDFa')
        
        return structured_data
    
    def _detect_component_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detect reusable component patterns."""
        patterns = []
        
        # Look for repeated structures
        class_patterns = self._find_repeated_class_patterns(soup)
        for pattern in class_patterns:
            patterns.append({
                'type': 'repeated_class',
                'pattern': pattern['class'],
                'count': pattern['count'],
                'elements': pattern['sample_elements'][:3]  # Sample elements
            })
        
        return patterns
    
    def _find_repeated_class_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find class patterns that repeat across the page."""
        class_counter = Counter()
        class_elements = {}
        
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            for cls in classes:
                if len(cls) > 3 and not cls.startswith(('col-', 'row-')):  # Skip grid classes
                    class_counter[cls] += 1
                    if cls not in class_elements:
                        class_elements[cls] = []
                    class_elements[cls].append({
                        'tag': element.name,
                        'text_preview': element.get_text()[:50]
                    })
        
        # Return patterns that appear multiple times
        patterns = []
        for cls, count in class_counter.items():
            if count > 2:  # Appears more than twice
                patterns.append({
                    'class': cls,
                    'count': count,
                    'sample_elements': class_elements[cls]
                })
        
        return sorted(patterns, key=lambda x: x['count'], reverse=True)[:10]
    
    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze accessibility features."""
        accessibility = {
            'images_with_alt': 0,
            'images_without_alt': 0,
            'form_labels': 0,
            'form_inputs_without_labels': 0,
            'skip_links': bool(soup.find('a[href="#main"], a[href="#content"]')),
            'aria_labels': len(soup.find_all(attrs={'aria-label': True})),
            'aria_described_by': len(soup.find_all(attrs={'aria-describedby': True})),
            'focus_indicators': self._check_focus_indicators(soup),
            'color_contrast_issues': []  # Would require CSS analysis
        }
        
        # Check images
        images = soup.find_all('img')
        for img in images:
            if img.get('alt') is not None:
                accessibility['images_with_alt'] += 1
            else:
                accessibility['images_without_alt'] += 1
        
        # Check form labels
        inputs = soup.find_all(['input', 'textarea', 'select'])
        for input_elem in inputs:
            input_id = input_elem.get('id')
            if input_id:
                label = soup.find('label', attrs={'for': input_id})
                if label:
                    accessibility['form_labels'] += 1
                else:
                    accessibility['form_inputs_without_labels'] += 1
            else:
                accessibility['form_inputs_without_labels'] += 1
        
        return accessibility
    
    def _check_focus_indicators(self, soup: BeautifulSoup) -> bool:
        """Check for custom focus indicators in CSS."""
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string and ':focus' in style_tag.string:
                return True
        return False
    
    def _generate_optimization_suggestions(self, soup: BeautifulSoup) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        # Check for missing alt texts
        images_without_alt = soup.find_all('img', alt=False)
        if images_without_alt:
            suggestions.append(f"Add alt text to {len(images_without_alt)} images for better accessibility")
        
        # Check for multiple h1 tags
        h1_tags = soup.find_all('h1')
        if len(h1_tags) > 1:
            suggestions.append("Consider using only one h1 tag per page for better SEO")
        elif len(h1_tags) == 0:
            suggestions.append("Add an h1 tag for better SEO and document structure")
        
        # Check for missing meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            suggestions.append("Add a meta description for better SEO")
        
        # Check for large DOM size
        all_elements = soup.find_all()
        if len(all_elements) > 1500:
            suggestions.append("Consider reducing DOM size for better performance")
        
        # Check for inline styles
        inline_styles = soup.find_all(attrs={'style': True})
        if len(inline_styles) > 10:
            suggestions.append("Consider moving inline styles to CSS files")
        
        return suggestions
    
    def _analyze_url_structure(self, url: str) -> Dict[str, Any]:
        """Analyze URL structure for insights."""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        analysis = {
            'domain': parsed.netloc,
            'path_segments': [seg for seg in parsed.path.split('/') if seg],
            'has_query_params': bool(parsed.query),
            'is_secure': parsed.scheme == 'https',
            'subdomain': parsed.netloc.split('.')[0] if '.' in parsed.netloc else None
        }
        
        return analysis
    
    def _has_substantial_content(self, element: Tag) -> bool:
        """Check if element has substantial content."""
        if not isinstance(element, Tag):
            return False
        
        text_content = element.get_text().strip()
        return len(text_content) >= self.min_content_length
    
    def _get_nesting_level(self, element: Tag) -> int:
        """Get the nesting level of an element."""
        level = 0
        parent = element.parent
        while parent and parent.name and level < self.max_nesting_depth:
            level += 1
            parent = parent.parent
        return level
    
    def _analyze_structure_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML structure complexity."""
        def get_max_depth(element, current_depth=0):
            if not hasattr(element, 'children'):
                return current_depth
            
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        body = soup.find('body')
        max_depth = get_max_depth(body) if body else 0
        
        # Determine if any simplification was applied
        simplification_applied = bool(
            self.max_depth or 
            self.flatten_containers or 
            self.simplify_structure
        )
        
        result = {
            'max_nesting_depth': max_depth,
            'total_elements': len(soup.find_all()),
            'div_count': len(soup.find_all('div')),
            'semantic_elements': len(soup.find_all(['article', 'section', 'header', 'footer', 'main', 'nav', 'aside'])),
            'simplification_applied': simplification_applied
        }
        
        # Add simplification details if applied
        if simplification_applied:
            result['simplification_details'] = {
                'max_depth_limit': self.max_depth,
                'flatten_containers': self.flatten_containers,
                'simplify_structure': self.simplify_structure,
                'preserve_semantic_tags': self.preserve_semantic_tags
            }
        
        return result
    
    def _analyze_structure_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze structural complexity of the webpage."""
        all_elements = soup.find_all()
        
        # Count different element types
        element_counts = {}
        for element in all_elements:
            if hasattr(element, 'name') and element.name:
                element_counts[element.name] = element_counts.get(element.name, 0) + 1
        
        # Calculate nesting depth
        def get_max_depth(element, current_depth=0):
            if not hasattr(element, 'children'):
                return current_depth
            
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        max_depth = get_max_depth(soup.body) if soup.body else get_max_depth(soup)
        
        # Count semantic elements
        semantic_elements = ['header', 'main', 'section', 'article', 'aside', 'footer', 'nav']
        semantic_count = sum(len(soup.find_all(tag)) for tag in semantic_elements)
        
        # Basic complexity metrics
        complexity = {
            'total_elements': len(all_elements),
            'max_nesting_depth': max_depth,
            'div_count': element_counts.get('div', 0),
            'semantic_elements': semantic_count,
            'element_types': len(element_counts),
            'complexity_score': self._calculate_complexity_score(len(all_elements), max_depth, element_counts.get('div', 0))
        }
        
        # Add simplification status if applicable
        if hasattr(self, 'max_depth') and (self.max_depth or self.flatten_containers or self.simplify_structure):
            complexity['simplification_applied'] = True
            complexity['simplification_details'] = {
                'max_depth_limit': getattr(self, 'max_depth', None),
                'flatten_containers': getattr(self, 'flatten_containers', False),
                'simplify_structure': getattr(self, 'simplify_structure', False),
                'preserve_semantic_tags': getattr(self, 'preserve_semantic_tags', True)
            }
        
        return complexity
    
    def _calculate_complexity_score(self, total_elements: int, max_depth: int, div_count: int) -> float:
        """Calculate a complexity score for the page structure."""
        # Simple scoring algorithm
        base_score = total_elements * 0.1
        depth_penalty = max_depth * 2
        div_penalty = div_count * 0.5
        
        return round(base_score + depth_penalty + div_penalty, 2)
