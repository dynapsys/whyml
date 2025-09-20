# Tutorial 2: SVG File Generation with Menu, Metadata, and Media as DataURI with PHP and Docker

## Overview
This tutorial demonstrates how to generate dynamic SVG files with interactive menus, embedded metadata, and media assets converted to Data URIs using WhyML, PHP, and Docker deployment.

## Prerequisites
- WhyML installed (`pip install whyml`)
- Docker and Docker Compose installed
- Basic knowledge of SVG, PHP, and YAML
- Image files for DataURI conversion

## Project Structure
```
svg-dynamic-site/
├── docker-compose.yml
├── Dockerfile
├── manifests/
│   ├── svg-app.yaml        # Main SVG application
│   ├── components/
│   │   ├── svg-menu.yaml   # Interactive SVG menu
│   │   ├── svg-header.yaml # SVG header with logo
│   │   └── svg-footer.yaml # SVG footer
│   └── pages/
│       ├── home-svg.yaml   # Home page as SVG
│       └── gallery-svg.yaml # Gallery with DataURI images
├── assets/
│   ├── logo.png
│   ├── bg-pattern.svg
│   └── gallery/
│       ├── image1.jpg
│       ├── image2.png
│       └── image3.gif
├── src/
│   └── php/
│       ├── svg-generator.php
│       ├── datauri-converter.php
│       └── svg-router.php
└── output/
```

## Step 1: Main SVG Application Manifest

**manifests/svg-app.yaml:**
```yaml
metadata:
  name: "Dynamic SVG Application"
  description: "Interactive SVG app with DataURI media and PHP backend"
  version: "1.0.0"
  format: "svg"

config:
  output_format: "svg+php"
  viewport: "0 0 1200 800"
  namespace: "http://www.w3.org/2000/svg"
  
variables:
  app_title: "SVG Interactive App"
  bg_color: "#f0f9ff"
  primary_color: "#0369a1"
  logo_datauri: "{{DATAURI:assets/logo.png}}"

dependencies:
  - "components/svg-header.yaml"
  - "components/svg-menu.yaml"
  - "components/svg-footer.yaml"

structure:
  - tag: "svg"
    attributes:
      xmlns: "http://www.w3.org/2000/svg"
      viewBox: "{{viewport}}"
      width: "100%"
      height: "100vh"
    children:
      # Background and definitions
      - tag: "defs"
        children:
          - tag: "linearGradient"
            attributes:
              id: "bgGradient"
              x1: "0%"
              y1: "0%"
              x2: "100%"
              y2: "100%"
            children:
              - tag: "stop"
                attributes:
                  offset: "0%"
                  stop-color: "{{bg_color}}"
              - tag: "stop"
                attributes:
                  offset: "100%"
                  stop-color: "#e0f2fe"
      
      # Background rectangle
      - tag: "rect"
        attributes:
          width: "100%"
          height: "100%"
          fill: "url(#bgGradient)"
      
      # Dynamic content area
      - tag: "g"
        attributes:
          id: "app-container"
        children:
          - "{{EXTERNAL:components/svg-header.yaml}}"
          - "{{EXTERNAL:components/svg-menu.yaml}}"
          - tag: "g"
            attributes:
              id: "main-content"
              transform: "translate(0, 120)"
            children:
              - "<?php include $current_page_svg; ?>"
          - "{{EXTERNAL:components/svg-footer.yaml}}"
      
      # Interactive scripts
      - tag: "script"
        attributes:
          type: "text/javascript"
        content: |
          function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('[id$="-page"]').forEach(el => el.style.display = 'none');
            // Show selected page
            document.getElementById(pageId + '-page').style.display = 'block';
            // Update active menu
            document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
          }
```

## Step 2: Interactive SVG Components

### SVG Header Component
**manifests/components/svg-header.yaml:**
```yaml
metadata:
  name: "SVG Header"
  description: "Header with logo and title"

structure:
  - tag: "g"
    attributes:
      id: "header"
      class: "header-group"
    children:
      # Header background
      - tag: "rect"
        attributes:
          x: "0"
          y: "0"
          width: "1200"
          height: "80"
          fill: "{{primary_color}}"
          opacity: "0.9"
      
      # Logo (DataURI image)
      - tag: "image"
        attributes:
          x: "20"
          y: "15"
          width: "50"
          height: "50"
          href: "{{logo_datauri}}"
      
      # App title
      - tag: "text"
        attributes:
          x: "90"
          y: "45"
          fill: "white"
          font-family: "Arial, sans-serif"
          font-size: "24"
          font-weight: "bold"
        content: "{{app_title}}"
      
      # Current time display
      - tag: "text"
        attributes:
          x: "1000"
          y: "30"
          fill: "white"
          font-family: "Arial, sans-serif"
          font-size: "12"
          id: "current-time"
        content: "<?php echo date('Y-m-d H:i:s'); ?>"
      
      # Dynamic status indicator
      - tag: "circle"
        attributes:
          cx: "1150"
          cy: "40"
          r: "8"
          fill: "#10b981"
          id: "status-indicator"
      - tag: "text"
        attributes:
          x: "1100"
          y: "55"
          fill: "white"
          font-family: "Arial, sans-serif"
          font-size: "10"
        content: "Online"
```

### Interactive SVG Menu
**manifests/components/svg-menu.yaml:**
```yaml
metadata:
  name: "SVG Interactive Menu"
  description: "Clickable navigation menu in SVG"

structure:
  - tag: "g"
    attributes:
      id: "navigation-menu"
      transform: "translate(0, 80)"
    children:
      # Menu background
      - tag: "rect"
        attributes:
          x: "0"
          y: "0" 
          width: "1200"
          height: "40"
          fill: "#0c4a6e"
      
      # Home menu item
      - tag: "g"
        attributes:
          class: "menu-item active"
          data-page: "home"
          style: "cursor: pointer"
          onclick: "showPage('home')"
        children:
          - tag: "rect"
            attributes:
              x: "0"
              y: "0"
              width: "120"
              height: "40"
              fill: "rgba(255,255,255,0.1)"
              class: "menu-bg"
          - tag: "text"
            attributes:
              x: "60"
              y: "25"
              text-anchor: "middle"
              fill: "white"
              font-family: "Arial, sans-serif"
              font-size: "14"
            content: "Home"
      
      # Gallery menu item
      - tag: "g"
        attributes:
          class: "menu-item"
          data-page: "gallery"
          style: "cursor: pointer"
          onclick: "showPage('gallery')"
        children:
          - tag: "rect"
            attributes:
              x: "120"
              y: "0"
              width: "120"
              height: "40"
              fill: "transparent"
              class: "menu-bg"
          - tag: "text"
            attributes:
              x: "180"
              y: "25"
              text-anchor: "middle"
              fill: "white"
              font-family: "Arial, sans-serif"
              font-size: "14"
            content: "Gallery"
      
      # About menu item  
      - tag: "g"
        attributes:
          class: "menu-item"
          data-page: "about"
          style: "cursor: pointer"
          onclick: "showPage('about')"
        children:
          - tag: "rect"
            attributes:
              x: "240"
              y: "0"
              width: "120"
              height: "40"
              fill: "transparent"
              class: "menu-bg"
          - tag: "text"
            attributes:
              x: "300"
              y: "25"
              text-anchor: "middle"
              fill: "white"
              font-family: "Arial, sans-serif"
              font-size: "14"
            content: "About"
      
      # Menu hover effects
      - tag: "style"
        content: |
          .menu-item:hover .menu-bg {
            fill: rgba(255,255,255,0.2) !important;
          }
          .menu-item.active .menu-bg {
            fill: rgba(255,255,255,0.3) !important;
          }
```

### SVG Footer Component
**manifests/components/svg-footer.yaml:**
```yaml
metadata:
  name: "SVG Footer"
  description: "Footer with copyright and metadata"

structure:
  - tag: "g"
    attributes:
      id: "footer"
      transform: "translate(0, 750)"
    children:
      # Footer background
      - tag: "rect"
        attributes:
          x: "0"
          y: "0"
          width: "1200"
          height: "50"
          fill: "#374151"
      
      # Copyright text
      - tag: "text"
        attributes:
          x: "20"
          y: "30"
          fill: "white"
          font-family: "Arial, sans-serif"
          font-size: "12"
        content: "© 2025 {{app_title}}. Generated with WhyML."
      
      # Metadata display
      - tag: "text"
        attributes:
          x: "1000"
          y: "20"
          fill: "#9ca3af"
          font-family: "monospace"
          font-size: "10"
        content: "Version: {{version}}"
      - tag: "text"
        attributes:
          x: "1000"
          y: "35"
          fill: "#9ca3af"
          font-family: "monospace"
          font-size: "10"
        content: "Format: {{format}}"
```

## Step 3: SVG Page Content

### Home Page SVG
**manifests/pages/home-svg.yaml:**
```yaml
metadata:
  name: "Home Page SVG"
  description: "Welcome page rendered in SVG"

structure:
  - tag: "g"
    attributes:
      id: "home-page"
      style: "display: block"
    children:
      # Welcome section
      - tag: "rect"
        attributes:
          x: "50"
          y: "50"
          width: "1100"
          height: "200"
          fill: "white"
          stroke: "{{primary_color}}"
          stroke-width: "2"
          rx: "10"
          opacity: "0.9"
      
      # Title
      - tag: "text"
        attributes:
          x: "600"
          y: "100"
          text-anchor: "middle"
          fill: "{{primary_color}}"
          font-family: "Arial, sans-serif"
          font-size: "32"
          font-weight: "bold"
        content: "Welcome to {{app_title}}"
      
      # Subtitle
      - tag: "text"
        attributes:
          x: "600"
          y: "130"
          text-anchor: "middle"
          fill: "#6b7280"
          font-family: "Arial, sans-serif"
          font-size: "16"
        content: "Experience interactive SVG with embedded media and dynamic PHP backend"
      
      # Feature boxes
      - tag: "g"
        attributes:
          id: "features"
          transform: "translate(0, 180)"
        children:
          # Feature 1
          - tag: "rect"
            attributes:
              x: "100"
              y: "100"
              width: "300"
              height: "150"
              fill: "#dbeafe"
              stroke: "{{primary_color}}"
              rx: "8"
          - tag: "text"
            attributes:
              x: "250"
              y: "130"
              text-anchor: "middle"
              fill: "{{primary_color}}"
              font-family: "Arial, sans-serif"
              font-size: "18"
              font-weight: "bold"
            content: "DataURI Media"
          - tag: "text"
            attributes:
              x: "250"
              y: "155"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Images embedded as base64"
          - tag: "text"
            attributes:
              x: "250"
              y: "175"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "No external dependencies"
          
          # Feature 2
          - tag: "rect"
            attributes:
              x: "450"
              y: "100"
              width: "300"
              height: "150"
              fill: "#fef3c7"
              stroke: "#d97706"
              rx: "8"
          - tag: "text"
            attributes:
              x: "600"
              y: "130"
              text-anchor: "middle"
              fill: "#d97706"
              font-family: "Arial, sans-serif"
              font-size: "18"
              font-weight: "bold"
            content: "Interactive Menu"
          - tag: "text"
            attributes:
              x: "600"
              y: "155"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Click navigation items"
          - tag: "text"
            attributes:
              x: "600"
              y: "175"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Dynamic page switching"
          
          # Feature 3
          - tag: "rect"
            attributes:
              x: "800"
              y: "100"
              width: "300"
              height: "150"
              fill: "#ecfdf5"
              stroke: "#10b981"
              rx: "8"
          - tag: "text"
            attributes:
              x: "950"
              y: "130"
              text-anchor: "middle"
              fill: "#10b981"
              font-family: "Arial, sans-serif"
              font-size: "18"
              font-weight: "bold"
            content: "PHP Backend"
          - tag: "text"
            attributes:
              x: "950"
              y: "155"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Dynamic content generation"
          - tag: "text"
            attributes:
              x: "950"
              y: "175"
              text-anchor: "middle"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Server-side processing"
      
      # Animated elements
      - tag: "circle"
        attributes:
          cx: "600"
          cy: "450"
          r: "20"
          fill: "{{primary_color}}"
          opacity: "0.7"
        children:
          - tag: "animate"
            attributes:
              attributeName: "r"
              values: "20;30;20"
              dur: "2s"
              repeatCount: "indefinite"
```

### Gallery Page with DataURI Images
**manifests/pages/gallery-svg.yaml:**
```yaml
metadata:
  name: "Gallery Page SVG"
  description: "Image gallery with DataURI embedded media"

structure:
  - tag: "g"
    attributes:
      id: "gallery-page"
      style: "display: none"
    children:
      # Gallery title
      - tag: "text"
        attributes:
          x: "600"
          y: "40"
          text-anchor: "middle"
          fill: "{{primary_color}}"
          font-family: "Arial, sans-serif"
          font-size: "24"
          font-weight: "bold"
        content: "Media Gallery"
      
      # Gallery grid
      - tag: "g"
        attributes:
          id: "gallery-grid"
          transform: "translate(100, 80)"
        children:
          # Image 1
          - tag: "g"
            attributes:
              class: "gallery-item"
              transform: "translate(0, 0)"
            children:
              - tag: "rect"
                attributes:
                  x: "0"
                  y: "0"
                  width: "200"
                  height: "200"
                  fill: "white"
                  stroke: "#e5e7eb"
                  stroke-width: "2"
                  rx: "8"
              - tag: "image"
                attributes:
                  x: "10"
                  y: "10"
                  width: "180"
                  height: "140"
                  href: "{{DATAURI:assets/gallery/image1.jpg}}"
                  style: "cursor: pointer"
                  onclick: "showImageDetails('image1')"
              - tag: "text"
                attributes:
                  x: "100"
                  y: "175"
                  text-anchor: "middle"
                  fill: "#374151"
                  font-family: "Arial, sans-serif"
                  font-size: "14"
                content: "Mountain View"
          
          # Image 2
          - tag: "g"
            attributes:
              class: "gallery-item"
              transform: "translate(250, 0)"
            children:
              - tag: "rect"
                attributes:
                  x: "0"
                  y: "0"
                  width: "200"
                  height: "200"
                  fill: "white"
                  stroke: "#e5e7eb"
                  stroke-width: "2"
                  rx: "8"
              - tag: "image"
                attributes:
                  x: "10"
                  y: "10"
                  width: "180"
                  height: "140"
                  href: "{{DATAURI:assets/gallery/image2.png}}"
                  style: "cursor: pointer"
                  onclick: "showImageDetails('image2')"
              - tag: "text"
                attributes:
                  x: "100"
                  y: "175"
                  text-anchor: "middle"
                  fill: "#374151"
                  font-family: "Arial, sans-serif"
                  font-size: "14"
                content: "City Skyline"
          
          # Image 3
          - tag: "g"
            attributes:
              class: "gallery-item"
              transform: "translate(500, 0)"
            children:
              - tag: "rect"
                attributes:
                  x: "0"
                  y: "0"
                  width: "200"
                  height: "200"
                  fill: "white"
                  stroke: "#e5e7eb"
                  stroke-width: "2"
                  rx: "8"
              - tag: "image"
                attributes:
                  x: "10"
                  y: "10"
                  width: "180"
                  height: "140"
                  href: "{{DATAURI:assets/gallery/image3.gif}}"
                  style: "cursor: pointer"
                  onclick: "showImageDetails('image3')"
              - tag: "text"
                attributes:
                  x: "100"
                  y: "175"
                  text-anchor: "middle"
                  fill: "#374151"
                  font-family: "Arial, sans-serif"
                  font-size: "14"
                content: "Ocean Waves"
      
      # Gallery stats
      - tag: "g"
        attributes:
          id: "gallery-stats"
          transform: "translate(100, 350)"
        children:
          - tag: "rect"
            attributes:
              x: "0"
              y: "0"
              width: "700"
              height: "100"
              fill: "#f8fafc"
              stroke: "#e5e7eb"
              rx: "8"
          - tag: "text"
            attributes:
              x: "20"
              y: "30"
              fill: "#374151"
              font-family: "Arial, sans-serif"
              font-size: "16"
              font-weight: "bold"
            content: "Gallery Statistics"
          - tag: "text"
            attributes:
              x: "20"
              y: "55"
              fill: "#6b7280"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Total Images: <?php echo count(glob('assets/gallery/*')); ?>"
          - tag: "text"
            attributes:
              x: "20"
              y: "75"
              fill: "#6b7280"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "All media embedded as DataURI for offline viewing"
          - tag: "text"
            attributes:
              x: "400"
              y: "55"
              fill: "#6b7280"
              font-family: "Arial, sans-serif"
              font-size: "12"
            content: "Generated: <?php echo date('Y-m-d H:i:s'); ?>"
```

## Step 4: PHP Backend Components

### DataURI Converter
**src/php/datauri-converter.php:**
```php
<?php
class DataURIConverter {
    public static function convertToDataURI($filePath) {
        if (!file_exists($filePath)) {
            return '';
        }
        
        $fileData = file_get_contents($filePath);
        $mimeType = mime_content_type($filePath);
        $base64 = base64_encode($fileData);
        
        return "data:$mimeType;base64,$base64";
    }
    
    public static function processManifestDataURIs($content) {
        // Find all {{DATAURI:path}} patterns and replace with actual DataURIs
        return preg_replace_callback(
            '/\{\{DATAURI:([^}]+)\}\}/',
            function($matches) {
                $filePath = $matches[1];
                return self::convertToDataURI($filePath);
            },
            $content
        );
    }
}
?>
```

### SVG Generator
**src/php/svg-generator.php:**
```php
<?php
require_once 'datauri-converter.php';

class SVGGenerator {
    private $config;
    
    public function __construct($config = []) {
        $this->config = array_merge([
            'viewport' => '0 0 1200 800',
            'app_title' => 'SVG App',
            'primary_color' => '#0369a1',
            'bg_color' => '#f0f9ff'
        ], $config);
    }
    
    public function generatePage($manifestPath, $variables = []) {
        // Load the manifest
        $manifestContent = file_get_contents($manifestPath);
        
        // Process variables
        foreach (array_merge($this->config, $variables) as $key => $value) {
            $manifestContent = str_replace("{{$key}}", $value, $manifestContent);
        }
        
        // Process DataURIs
        $manifestContent = DataURIConverter::processManifestDataURIs($manifestContent);
        
        // Process PHP variables
        $manifestContent = $this->processPHPVariables($manifestContent, $variables);
        
        return $manifestContent;
    }
    
    private function processPHPVariables($content, $variables) {
        // Extract PHP code blocks and evaluate them
        return preg_replace_callback(
            '/<\?php\s+(.+?)\s+\?>/',
            function($matches) use ($variables) {
                extract($variables);
                ob_start();
                eval($matches[1]);
                return ob_get_clean();
            },
            $content
        );
    }
    
    public function renderSVGPage($page = 'home') {
        $pages = [
            'home' => 'manifests/pages/home-svg.yaml',
            'gallery' => 'manifests/pages/gallery-svg.yaml'
        ];
        
        $manifestPath = $pages[$page] ?? $pages['home'];
        
        $variables = [
            'current_page' => $page,
            'current_time' => date('Y-m-d H:i:s'),
            'version' => '1.0.0'
        ];
        
        return $this->generatePage($manifestPath, $variables);
    }
}
?>
```

### SVG Router
**src/php/svg-router.php:**
```php
<?php
require_once 'svg-generator.php';

class SVGRouter {
    private $generator;
    
    public function __construct() {
        $this->generator = new SVGGenerator();
    }
    
    public function route() {
        $request = $_SERVER['REQUEST_URI'] ?? '/';
        $path = parse_url($request, PHP_URL_PATH);
        
        // Remove leading slash
        $path = ltrim($path, '/');
        
        // Default to home if empty
        if (empty($path)) {
            $path = 'home';
        }
        
        // Set content type
        header('Content-Type: image/svg+xml; charset=utf-8');
        
        // Generate and return SVG
        echo $this->generator->renderSVGPage($path);
    }
}

// Auto-routing
if (basename($_SERVER['PHP_SELF']) === 'svg-router.php') {
    $router = new SVGRouter();
    $router->route();
}
?>
```

## Step 5: Docker Configuration

**Dockerfile:**
```dockerfile
FROM php:8.2-apache

# Install required extensions
RUN docker-php-ext-install fileinfo

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Set working directory
WORKDIR /var/www/html

# Copy files
COPY output/ /var/www/html/
COPY src/ /var/www/html/src/
COPY assets/ /var/www/html/assets/

# Create .htaccess for SVG routing
RUN echo "RewriteEngine On\n\
RewriteCond %{REQUEST_FILENAME} !-f\n\
RewriteCond %{REQUEST_FILENAME} !-d\n\
RewriteRule ^(.*)$ src/php/svg-router.php [QSA,L]\n\
\n\
<Files \"*.svg\">\n\
    Header set Content-Type \"image/svg+xml\"\n\
</Files>" > /var/www/html/.htaccess

# Set permissions
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  svg-app:
    build: .
    ports:
      - "8080:80"
    volumes:
      - ./output:/var/www/html/output
      - ./assets:/var/www/html/assets
      - ./src:/var/www/html/src
    environment:
      - APACHE_DOCUMENT_ROOT=/var/www/html
    restart: unless-stopped
```

## Step 6: Generate and Deploy

```bash
# Generate SVG manifests
whyml convert manifests/svg-app.yaml --output output/

# Build and run Docker container
docker-compose up --build

# Access the SVG app at http://localhost:8080
```

## Features Demonstrated

1. **SVG Generation**: Dynamic SVG creation with embedded content
2. **DataURI Media**: Images converted to base64 for offline viewing
3. **Interactive Elements**: Clickable menus and animations
4. **PHP Integration**: Server-side processing and dynamic content
5. **Modular Components**: Reusable SVG components with YAML
6. **Docker Deployment**: Complete containerized deployment

This tutorial showcases WhyML's ability to generate complex, interactive SVG applications with embedded media and dynamic backends.
