# Tutorial 1: Multi-Page HTML Site with Menu Using YAML Dependencies, PHP Integration, and Docker

## Overview
This tutorial demonstrates how to create a complete multi-page HTML website with navigation menus using WhyML's YAML dependency system, PHP integration for dynamic content, and Docker for deployment.

## Prerequisites
- WhyML installed (`pip install whyml`)
- Docker and Docker Compose installed
- Basic knowledge of HTML, PHP, and YAML

## Project Structure
```
my-multipage-site/
├── docker-compose.yml
├── Dockerfile
├── manifests/
│   ├── site.yaml          # Main site manifest with dependencies
│   ├── pages/
│   │   ├── home.yaml      # Home page manifest
│   │   ├── about.yaml     # About page manifest  
│   │   └── contact.yaml   # Contact page manifest
│   └── components/
│       ├── header.yaml    # Shared header with navigation
│       ├── footer.yaml    # Shared footer
│       └── menu.yaml      # Navigation menu component
├── src/
│   ├── styles/
│   │   └── main.css
│   └── images/
└── output/                # Generated files will go here
```

## Step 1: Create the Main Site Manifest

First, let's create the main site manifest that defines the overall structure and dependencies:

**manifests/site.yaml:**
```yaml
metadata:
  name: "My Multi-Page Website"
  description: "A complete multi-page site built with WhyML"
  version: "1.0.0"
  author: "Your Name"
  language: "en"

config:
  output_format: "php"
  base_url: "http://localhost:8080"
  theme_color: "#2563eb"
  
variables:
  site_name: "My Awesome Site"
  copyright_year: "2024"
  contact_email: "hello@example.com"

dependencies:
  - "components/header.yaml"
  - "components/footer.yaml" 
  - "components/menu.yaml"
  - "pages/home.yaml"
  - "pages/about.yaml"
  - "pages/contact.yaml"

structure:
  - tag: "html"
    attributes:
      lang: "<?= $language ?>"
    children:
      - tag: "head"
        children:
          - tag: "meta"
            attributes:
              charset: "utf-8"
          - tag: "meta"
            attributes:
              name: "viewport"
              content: "width=device-width, initial-scale=1"
          - tag: "title"
            content: "<?= $site_name ?> - <?= $page_title ?>"
          - tag: "link"
            attributes:
              rel: "stylesheet"
              href: "styles/main.css"
      - tag: "body"
        children:
          - "{{EXTERNAL:components/header.yaml}}"
          - tag: "main"
            attributes:
              id: "content"
            children:
              - "<?php include $current_page; ?>"
          - "{{EXTERNAL:components/footer.yaml}}"

routes:
  - path: "/"
    page: "home"
    title: "Welcome"
  - path: "/about"
    page: "about" 
    title: "About Us"
  - path: "/contact"
    page: "contact"
    title: "Contact"
```

## Step 2: Create Shared Components

### Navigation Menu Component
**manifests/components/menu.yaml:**
```yaml
metadata:
  name: "Navigation Menu"
  description: "Site navigation with active page highlighting"

structure:
  - tag: "nav"
    attributes:
      class: "main-nav"
      role: "navigation"
    children:
      - tag: "ul"
        attributes:
          class: "nav-list"
        children:
          - tag: "li"
            attributes:
              class: "nav-item"
            children:
              - tag: "a"
                attributes:
                  href: "/"
                  class: "nav-link <?= $current_page == 'home' ? 'active' : '' ?>"
                content: "Home"
          - tag: "li"
            attributes:
              class: "nav-item"
            children:
              - tag: "a"
                attributes:
                  href: "/about"
                  class: "nav-link <?= $current_page == 'about' ? 'active' : '' ?>"
                content: "About"
          - tag: "li"
            attributes:
              class: "nav-item"
            children:
              - tag: "a"
                attributes:
                  href: "/contact"
                  class: "nav-link <?= $current_page == 'contact' ? 'active' : '' ?>"
                content: "Contact"
```

### Header Component
**manifests/components/header.yaml:**
```yaml
metadata:
  name: "Site Header"
  description: "Main site header with logo and navigation"

structure:
  - tag: "header"
    attributes:
      class: "site-header"
      role: "banner"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "div"
            attributes:
              class: "header-content"
            children:
              - tag: "h1"
                attributes:
                  class: "site-title"
                children:
                  - tag: "a"
                    attributes:
                      href: "/"
                    content: "{{site_name}}"
              - "{{EXTERNAL:components/menu.yaml}}"
```

### Footer Component
**manifests/components/footer.yaml:**
```yaml
metadata:
  name: "Site Footer"
  description: "Site footer with copyright and links"

structure:
  - tag: "footer"
    attributes:
      class: "site-footer"
      role: "contentinfo"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "div"
            attributes:
              class: "footer-content"
            children:
              - tag: "p"
                attributes:
                  class: "copyright"
                content: "© {{copyright_year}} {{site_name}}. All rights reserved."
              - tag: "p"
                attributes:
                  class: "contact"
                children:
                  - tag: "a"
                    attributes:
                      href: "mailto:{{contact_email}}"
                    content: "{{contact_email}}"
```

## Step 3: Create Individual Page Manifests

### Home Page
**manifests/pages/home.yaml:**
```yaml
metadata:
  name: "Home Page"
  description: "Welcome page for the website"

variables:
  page_title: "Welcome"
  current_page: "home"

structure:
  - tag: "section"
    attributes:
      class: "hero"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "h2"
            content: "Welcome to {{site_name}}"
          - tag: "p"
            attributes:
              class: "hero-text"
            content: "Your one-stop destination for amazing content and services."
          - tag: "a"
            attributes:
              href: "/about"
              class: "btn btn-primary"
            content: "Learn More"
  
  - tag: "section"
    attributes:
      class: "features"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "h3"
            content: "Our Features"
          - tag: "div"
            attributes:
              class: "feature-grid"
            children:
              - tag: "div"
                attributes:
                  class: "feature"
                children:
                  - tag: "h4"
                    content: "Fast & Reliable"
                  - tag: "p"
                    content: "Built with modern technologies for optimal performance."
              - tag: "div"
                attributes:
                  class: "feature"
                children:
                  - tag: "h4"
                    content: "Easy to Use"
                  - tag: "p"
                    content: "Intuitive interface designed for the best user experience."
              - tag: "div"
                attributes:
                  class: "feature"
                children:
                  - tag: "h4"
                    content: "Fully Responsive"
                  - tag: "p"
                    content: "Works perfectly on all devices and screen sizes."
```

### About Page
**manifests/pages/about.yaml:**
```yaml
metadata:
  name: "About Page"
  description: "Information about the company"

variables:
  page_title: "About Us"
  current_page: "about"

structure:
  - tag: "section"
    attributes:
      class: "page-header"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "h2"
            content: "About {{site_name}}"
          - tag: "p"
            attributes:
              class: "page-subtitle"
            content: "Learn more about our mission and values"
  
  - tag: "section"
    attributes:
      class: "content"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "div"
            attributes:
              class: "content-grid"
            children:
              - tag: "div"
                attributes:
                  class: "content-main"
                children:
                  - tag: "h3"
                    content: "Our Story"
                  - tag: "p"
                    content: "Founded in {{copyright_year}}, we've been dedicated to providing exceptional services to our customers. Our team combines expertise with innovation to deliver results that exceed expectations."
                  - tag: "p"
                    content: "We believe in the power of technology to transform businesses and improve lives. That's why we're committed to staying at the forefront of industry developments and best practices."
                  - tag: "h3"
                    content: "Our Mission"
                  - tag: "p"
                    content: "To empower businesses and individuals through innovative web solutions that are both beautiful and functional."
              - tag: "aside"
                attributes:
                  class: "content-sidebar"
                children:
                  - tag: "h4"
                    content: "Quick Facts"
                  - tag: "ul"
                    children:
                      - tag: "li"
                        content: "Founded: {{copyright_year}}"
                      - tag: "li"
                        content: "Team Size: 50+ professionals"
                      - tag: "li"
                        content: "Projects: 500+ completed"
                      - tag: "li"
                        content: "Satisfaction: 99% client satisfaction"
```

### Contact Page
**manifests/pages/contact.yaml:**
```yaml
metadata:
  name: "Contact Page"
  description: "Contact form and information"

variables:
  page_title: "Contact Us"
  current_page: "contact"

structure:
  - tag: "section"
    attributes:
      class: "page-header"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "h2"
            content: "Contact Us"
          - tag: "p"
            attributes:
              class: "page-subtitle"
            content: "Get in touch with our team"
  
  - tag: "section"
    attributes:
      class: "contact-section"
    children:
      - tag: "div"
        attributes:
          class: "container"
        children:
          - tag: "div"
            attributes:
              class: "contact-grid"
            children:
              - tag: "div"
                attributes:
                  class: "contact-form"
                children:
                  - tag: "h3"
                    content: "Send us a Message"
                  - tag: "form"
                    attributes:
                      action: "/contact.php"
                      method: "post"
                    children:
                      - tag: "div"
                        attributes:
                          class: "form-group"
                        children:
                          - tag: "label"
                            attributes:
                              for: "name"
                            content: "Name"
                          - tag: "input"
                            attributes:
                              type: "text"
                              id: "name"
                              name: "name"
                              required: "required"
                      - tag: "div"
                        attributes:
                          class: "form-group"
                        children:
                          - tag: "label"
                            attributes:
                              for: "email"
                            content: "Email"
                          - tag: "input"
                            attributes:
                              type: "email"
                              id: "email"
                              name: "email"
                              required: "required"
                      - tag: "div"
                        attributes:
                          class: "form-group"
                        children:
                          - tag: "label"
                            attributes:
                              for: "message"
                            content: "Message"
                          - tag: "textarea"
                            attributes:
                              id: "message"
                              name: "message"
                              rows: "5"
                              required: "required"
                      - tag: "button"
                        attributes:
                          type: "submit"
                          class: "btn btn-primary"
                        content: "Send Message"
              - tag: "div"
                attributes:
                  class: "contact-info"
                children:
                  - tag: "h3"
                    content: "Get in Touch"
                  - tag: "div"
                    attributes:
                      class: "contact-item"
                    children:
                      - tag: "h4"
                        content: "Email"
                      - tag: "a"
                        attributes:
                          href: "mailto:{{contact_email}}"
                        content: "{{contact_email}}"
                  - tag: "div"
                    attributes:
                      class: "contact-item"
                    children:
                      - tag: "h4"
                        content: "Phone"
                      - tag: "p"
                        content: "+1 (555) 123-4567"
                  - tag: "div"
                    attributes:
                      class: "contact-item"
                    children:
                      - tag: "h4"
                        content: "Address"
                      - tag: "p"
                        content: "123 Main Street<br>City, State 12345"
```

## Step 4: Create CSS Styles

**src/styles/main.css:**
```css
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header Styles */
.site-header {
    background: #2563eb;
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.site-title a {
    color: white;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: bold;
}

/* Navigation Styles */
.main-nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.nav-link:hover,
.nav-link.active {
    background-color: rgba(255,255,255,0.2);
}

/* Main Content Styles */
main {
    min-height: calc(100vh - 140px);
    padding: 2rem 0;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4rem 0;
    text-align: center;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.hero-text {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

/* Button Styles */
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 500;
    transition: all 0.3s;
    border: none;
    cursor: pointer;
}

.btn-primary {
    background: #2563eb;
    color: white;
}

.btn-primary:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

/* Features Grid */
.features {
    padding: 4rem 0;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.feature {
    padding: 2rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    text-align: center;
    transition: transform 0.3s;
}

.feature:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

/* Page Header */
.page-header {
    background: #f8fafc;
    padding: 3rem 0;
    text-align: center;
    border-bottom: 1px solid #e5e7eb;
}

.page-header h2 {
    font-size: 2.2rem;
    color: #1f2937;
    margin-bottom: 0.5rem;
}

.page-subtitle {
    font-size: 1.1rem;
    color: #6b7280;
}

/* Content Grid */
.content-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3rem;
    margin-top: 2rem;
}

.content-main h3 {
    color: #1f2937;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.content-main p {
    margin-bottom: 1.5rem;
    color: #4b5563;
}

.content-sidebar {
    background: #f8fafc;
    padding: 2rem;
    border-radius: 8px;
    height: fit-content;
}

.content-sidebar h4 {
    color: #1f2937;
    margin-bottom: 1rem;
}

.content-sidebar ul {
    list-style: none;
}

.content-sidebar li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e5e7eb;
}

/* Contact Form */
.contact-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin-top: 2rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.contact-item {
    margin-bottom: 2rem;
}

.contact-item h4 {
    color: #1f2937;
    margin-bottom: 0.5rem;
}

.contact-item a {
    color: #2563eb;
    text-decoration: none;
}

/* Footer Styles */
.site-footer {
    background: #1f2937;
    color: white;
    padding: 2rem 0;
    margin-top: 2rem;
}

.footer-content {
    text-align: center;
}

.footer-content a {
    color: #60a5fa;
    text-decoration: none;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .main-nav ul {
        gap: 1rem;
    }
    
    .hero h2 {
        font-size: 2rem;
    }
    
    .content-grid,
    .contact-grid {
        grid-template-columns: 1fr;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
```

## Step 5: Docker Configuration

**Dockerfile:**
```dockerfile
FROM php:8.2-apache

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY output/ /var/www/html/
COPY src/ /var/www/html/

# Create .htaccess for clean URLs
RUN echo "RewriteEngine On\n\
RewriteCond %{REQUEST_FILENAME} !-f\n\
RewriteCond %{REQUEST_FILENAME} !-d\n\
RewriteRule ^(.*)$ index.php [QSA,L]" > /var/www/html/.htaccess

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Expose port 80
EXPOSE 80
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:80"
    volumes:
      - ./output:/var/www/html
      - ./src:/var/www/html/src
    environment:
      - APACHE_DOCUMENT_ROOT=/var/www/html
    restart: unless-stopped
```

## Step 6: Generate the Site

Now let's generate our multi-page site using WhyML:

```bash
# Generate the main site structure
whyml convert manifests/site.yaml --output output/

# Generate individual pages
whyml convert manifests/pages/home.yaml --output output/pages/
whyml convert manifests/pages/about.yaml --output output/pages/
whyml convert manifests/pages/contact.yaml --output output/pages/

# Create PHP routing
cat > output/index.php << 'EOF'
<?php
// Simple PHP router for multi-page site

$request = $_SERVER['REQUEST_URI'];
$path = parse_url($request, PHP_URL_PATH);

// Site configuration
$site_name = "My Awesome Site";
$copyright_year = "2024";
$contact_email = "hello@example.com";
$language = "en";

// Routing configuration
$routes = [
    '/' => ['page' => 'home', 'title' => 'Welcome'],
    '/about' => ['page' => 'about', 'title' => 'About Us'],
    '/contact' => ['page' => 'contact', 'title' => 'Contact']
];

// Find matching route
$current_route = $routes[$path] ?? $routes['/'];
$current_page = $current_route['page'];
$page_title = $current_route['title'];

// Include the generated page structure
include 'site.php';
?>
EOF

# Create contact form handler
cat > output/contact.php << 'EOF'
<?php
if ($_POST) {
    $name = htmlspecialchars($_POST['name'] ?? '');
    $email = htmlspecialchars($_POST['email'] ?? '');
    $message = htmlspecialchars($_POST['message'] ?? '');
    
    // In a real application, you would send an email or save to database
    // For this demo, we'll just redirect with a success message
    
    header('Location: /contact?success=1');
    exit;
}

header('Location: /contact');
?>
EOF
```

## Step 7: Build and Run with Docker

```bash
# Build and start the Docker container
docker-compose up --build

# The site will be available at http://localhost:8080
```

## Step 8: Testing the Site

Once the Docker container is running, you can test your multi-page site:

1. **Home Page**: Navigate to `http://localhost:8080/`
2. **About Page**: Click "About" in the menu or go to `http://localhost:8080/about`
3. **Contact Page**: Click "Contact" in the menu or go to `http://localhost:8080/contact`

## Features Demonstrated

This tutorial showcases several powerful WhyML features:

1. **YAML Dependencies**: Using `{{EXTERNAL:filename}}` syntax to include reusable components
2. **Variable Substitution**: Using `{{variable_name}}` and `<?= $variable ?>` syntax
3. **PHP Integration**: Generating PHP files with dynamic content and routing
4. **Modular Architecture**: Separating components, pages, and configuration
5. **Docker Deployment**: Complete containerized deployment setup
6. **Responsive Design**: Mobile-friendly CSS with modern styling

## Next Steps

- Add more pages by creating additional YAML manifests
- Implement a database for the contact form
- Add user authentication and admin panels
- Integrate with a CMS for content management
- Add SEO optimization and analytics
- Deploy to production using Docker Swarm or Kubernetes

This tutorial provides a solid foundation for building complex multi-page websites using WhyML's powerful manifest system combined with PHP and Docker for robust deployment.
