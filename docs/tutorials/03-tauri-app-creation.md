# Tutorial 3: Tauri Desktop Application from Scraped Webpage

## Overview
This tutorial demonstrates how to scrape a webpage with WhyML, convert it to a YAML manifest, and build a cross-platform desktop application using Tauri with Rust and JavaScript.

## Prerequisites
- WhyML installed (`pip install whyml`)
- Rust and Cargo installed
- Node.js and npm installed
- Tauri CLI (`cargo install tauri-cli`)

## Project Structure
```
webpage-to-tauri-app/
├── src-tauri/
│   ├── src/
│   │   └── main.rs
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── build.rs
├── src/
│   ├── index.html
│   ├── main.js
│   ├── style.css
│   └── manifest.yaml
├── scraped/
│   └── original-site.yaml
├── package.json
└── README.md
```

## Step 1: Scrape Target Website

First, let's scrape a website and analyze its structure:

```bash
# Scrape with comprehensive analysis
whyml scrape https://example-blog.com \
  --section metadata \
  --section analysis \
  --section structure \
  --section styles \
  --output scraped/original-site.yaml \
  --verbose

# Review the scraped content
cat scraped/original-site.yaml
```

## Step 2: Create Tauri Project

Initialize a new Tauri project:

```bash
# Create new Tauri app
npm create tauri-app@latest webpage-to-tauri-app
cd webpage-to-tauri-app

# Choose:
# - Package manager: npm
# - UI template: Vanilla
# - Add @tauri-apps/api: Yes
```

## Step 3: Convert Scraped Content to App Manifest

**src/manifest.yaml:**
```yaml
metadata:
  name: "Scraped Website App"
  description: "Desktop app created from scraped webpage"
  version: "1.0.0"
  author: "WhyML Generator"

config:
  app_type: "desktop"
  framework: "tauri"
  window_title: "{{site_name}} - Desktop App"
  window_width: 1200
  window_height: 800
  resizable: true

variables:
  site_name: "Example Blog"
  primary_color: "#2563eb"
  background_color: "#ffffff"

structure:
  - tag: "div"
    attributes:
      id: "app"
      class: "app-container"
    children:
      - tag: "header"
        attributes:
          class: "app-header"
        children:
          - tag: "h1"
            attributes:
              class: "app-title"
            content: "{{site_name}}"
          - tag: "div"
            attributes:
              class: "app-controls"
            children:
              - tag: "button"
                attributes:
                  id: "refresh-btn"
                  class: "control-btn"
                content: "Refresh"
              - tag: "button"
                attributes:
                  id: "settings-btn"
                  class: "control-btn"
                content: "Settings"
      
      - tag: "main"
        attributes:
          class: "app-content"
        children:
          - tag: "div"
            attributes:
              id: "scraped-content"
              class: "content-area"
            content: "<!-- Scraped content will be loaded here -->"
      
      - tag: "footer"
        attributes:
          class: "app-footer"
        children:
          - tag: "p"
            content: "Powered by WhyML + Tauri"

styles:
  - selector: ".app-container"
    rules:
      display: "flex"
      flex-direction: "column"
      height: "100vh"
      font-family: "'Segoe UI', system-ui, sans-serif"
  
  - selector: ".app-header"
    rules:
      background: "{{primary_color}}"
      color: "white"
      padding: "1rem"
      display: "flex"
      justify-content: "space-between"
      align-items: "center"
  
  - selector: ".app-content"
    rules:
      flex: "1"
      padding: "1rem"
      overflow-y: "auto"
  
  - selector: ".control-btn"
    rules:
      background: "rgba(255,255,255,0.2)"
      border: "none"
      color: "white"
      padding: "0.5rem 1rem"
      margin-left: "0.5rem"
      border-radius: "4px"
      cursor: "pointer"
```

## Step 4: Generate HTML from Manifest

Create a conversion script:

**scripts/generate-app.py:**
```python
#!/usr/bin/env python3
import yaml
import json
from pathlib import Path

def load_manifest(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def generate_html(manifest):
    """Generate HTML from WhyML manifest structure"""
    
    def render_element(element):
        if isinstance(element, str):
            return element
        
        tag = element.get('tag', 'div')
        attrs = element.get('attributes', {})
        content = element.get('content', '')
        children = element.get('children', [])
        
        # Build attributes string
        attr_str = ''
        for key, value in attrs.items():
            attr_str += f' {key}="{value}"'
        
        # Build element
        if children:
            child_html = ''.join(render_element(child) for child in children)
            return f'<{tag}{attr_str}>{child_html}</{tag}>'
        else:
            return f'<{tag}{attr_str}>{content}</{tag}>'
    
    structure = manifest.get('structure', [])
    body_html = ''.join(render_element(elem) for elem in structure)
    
    variables = manifest.get('variables', {})
    title = variables.get('site_name', 'WhyML App')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {body_html}
    <script src="main.js"></script>
</body>
</html>'''
    
    return html

def generate_css(manifest):
    """Generate CSS from manifest styles"""
    styles = manifest.get('styles', [])
    variables = manifest.get('variables', {})
    
    css = '/* Generated by WhyML */\n\n'
    
    # Add CSS reset
    css += '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #ffffff;
}

'''
    
    # Add manifest styles
    for style in styles:
        selector = style.get('selector', '')
        rules = style.get('rules', {})
        
        css += f'{selector} {{\n'
        for prop, value in rules.items():
            # Replace variables
            for var_name, var_value in variables.items():
                value = str(value).replace(f'{{{{{var_name}}}}}', str(var_value))
            css += f'    {prop}: {value};\n'
        css += '}\n\n'
    
    return css

def main():
    manifest = load_manifest('src/manifest.yaml')
    
    # Generate HTML
    html = generate_html(manifest)
    with open('src/index.html', 'w') as f:
        f.write(html)
    
    # Generate CSS
    css = generate_css(manifest)
    with open('src/style.css', 'w') as f:
        f.write(css)
    
    print("Generated HTML and CSS from manifest")

if __name__ == '__main__':
    main()
```

Run the generator:
```bash
python3 scripts/generate-app.py
```

## Step 5: Configure Tauri Application

**src-tauri/tauri.conf.json:**
```json
{
  "$schema": "../node_modules/@tauri-apps/cli/schema.json",
  "build": {
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev",
    "devPath": "../src",
    "distDir": "../src"
  },
  "package": {
    "productName": "Scraped Website App",
    "version": "1.0.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      },
      "window": {
        "all": false,
        "close": true,
        "hide": true,
        "maximize": true,
        "minimize": true,
        "setResizable": true,
        "setTitle": true,
        "show": true,
        "unmaximize": true,
        "unminimize": true
      },
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "scope": ["$APPDATA/*", "$RESOURCE/*"]
      }
    },
    "bundle": {
      "active": true,
      "category": "DeveloperTool",
      "copyright": "Generated by WhyML",
      "deb": {
        "depends": []
      },
      "externalBin": [],
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "identifier": "com.whyml.scraped-app",
      "longDescription": "Desktop application created from scraped webpage using WhyML and Tauri",
      "macOS": {
        "entitlements": null,
        "exceptionDomain": "",
        "frameworks": [],
        "providerShortName": null,
        "signingIdentity": null
      },
      "resources": [],
      "shortDescription": "WhyML Scraped Website App",
      "targets": "all",
      "windows": {
        "certificateThumbprint": null,
        "digestAlgorithm": "sha256",
        "timestampUrl": ""
      }
    },
    "security": {
      "csp": null
    },
    "updater": {
      "active": false
    },
    "windows": [
      {
        "fullscreen": false,
        "height": 800,
        "resizable": true,
        "title": "Scraped Website App",
        "width": 1200,
        "center": true
      }
    ]
  }
}
```

## Step 6: Implement App Functionality

**src/main.js:**
```javascript
const { invoke } = window.__TAURI__.tauri;
const { appWindow } = window.__TAURI__.window;

class ScrapedWebsiteApp {
    constructor() {
        this.initializeApp();
        this.bindEvents();
        this.loadScrapedContent();
    }

    async initializeApp() {
        console.log('Initializing Scraped Website App...');
        
        // Set window title dynamically
        await appWindow.setTitle('Scraped Website App - WhyML Generated');
        
        // Load app settings
        this.loadSettings();
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshContent();
            });
        }

        // Settings button
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.showSettings();
            });
        }

        // Window controls
        this.setupWindowControls();
    }

    async loadScrapedContent() {
        const contentArea = document.getElementById('scraped-content');
        if (!contentArea) return;

        try {
            // In a real app, you'd load the scraped content from the manifest
            // For this demo, we'll create some sample content
            const sampleContent = this.generateSampleContent();
            contentArea.innerHTML = sampleContent;
            
            console.log('Scraped content loaded successfully');
        } catch (error) {
            console.error('Failed to load scraped content:', error);
            contentArea.innerHTML = '<p>Failed to load content. Please try refreshing.</p>';
        }
    }

    generateSampleContent() {
        return `
            <div class="content-section">
                <h2>Welcome to Your Desktop App</h2>
                <p>This application was generated from a scraped webpage using WhyML and converted to a desktop app using Tauri.</p>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>📄 Content Preservation</h3>
                        <p>Original webpage structure and content preserved in YAML format</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>🖥️ Native Desktop</h3>
                        <p>Cross-platform desktop application using Tauri and Rust</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>⚡ High Performance</h3>
                        <p>Fast, lightweight, and resource-efficient application</p>
                    </div>
                </div>
                
                <div class="scraped-info">
                    <h3>Original Site Information</h3>
                    <ul>
                        <li><strong>Source:</strong> Scraped from example-blog.com</li>
                        <li><strong>Generated:</strong> ${new Date().toLocaleDateString()}</li>
                        <li><strong>Technology:</strong> WhyML + Tauri + Rust</li>
                    </ul>
                </div>
            </div>
        `;
    }

    async refreshContent() {
        console.log('Refreshing content...');
        const contentArea = document.getElementById('scraped-content');
        
        if (contentArea) {
            contentArea.innerHTML = '<p>Refreshing content...</p>';
            
            // Simulate refresh delay
            setTimeout(() => {
                this.loadScrapedContent();
            }, 1000);
        }
    }

    showSettings() {
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>App Settings</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="setting-group">
                        <label for="theme-select">Theme:</label>
                        <select id="theme-select">
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label for="font-size">Font Size:</label>
                        <input type="range" id="font-size" min="12" max="20" value="14">
                        <span id="font-size-value">14px</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="save-settings">Save</button>
                    <button class="cancel-settings">Cancel</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Bind modal events
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelector('.cancel-settings').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelector('.save-settings').addEventListener('click', () => {
            this.saveSettings();
            document.body.removeChild(modal);
        });
        
        // Font size slider
        const fontSlider = modal.querySelector('#font-size');
        const fontValue = modal.querySelector('#font-size-value');
        fontSlider.addEventListener('input', (e) => {
            fontValue.textContent = e.target.value + 'px';
        });
    }

    setupWindowControls() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshContent();
                        break;
                    case ',':
                        e.preventDefault();
                        this.showSettings();
                        break;
                }
            }
        });
    }

    loadSettings() {
        // In a real app, you'd load settings from Tauri's filesystem API
        const settings = {
            theme: 'light',
            fontSize: '14px'
        };
        
        document.documentElement.style.setProperty('--font-size', settings.fontSize);
        document.documentElement.className = settings.theme;
    }

    saveSettings() {
        console.log('Settings saved!');
        // In a real app, you'd save settings using Tauri's filesystem API
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScrapedWebsiteApp();
});
```

## Step 7: Enhanced Styling

**src/style.css:**
```css
/* Generated by WhyML */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-color: #2563eb;
    --background-color: #ffffff;
    --text-color: #1f2937;
    --border-color: #e5e7eb;
    --font-size: 14px;
}

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--background-color);
    color: var(--text-color);
    font-size: var(--font-size);
}

.app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

.app-header {
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    -webkit-app-region: drag;
}

.app-title {
    font-size: 1.2rem;
    font-weight: 600;
}

.app-controls {
    -webkit-app-region: no-drag;
}

.control-btn {
    background: rgba(255,255,255,0.2);
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    margin-left: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.control-btn:hover {
    background: rgba(255,255,255,0.3);
}

.app-content {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
}

.content-section h2 {
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 1.8rem;
}

.content-section p {
    margin-bottom: 1.5rem;
    line-height: 1.6;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.feature-card {
    background: #f8fafc;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.feature-card h3 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

.scraped-info {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 2rem;
}

.scraped-info h3 {
    color: #d97706;
    margin-bottom: 1rem;
}

.scraped-info ul {
    list-style: none;
    padding: 0;
}

.scraped-info li {
    margin-bottom: 0.5rem;
    padding-left: 1rem;
    position: relative;
}

.scraped-info li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #d97706;
}

.app-footer {
    background: #f8fafc;
    border-top: 1px solid var(--border-color);
    padding: 0.75rem 1rem;
    text-align: center;
    font-size: 0.875rem;
    color: #6b7280;
}

/* Settings Modal */
.settings-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    overflow: hidden;
}

.modal-header {
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.close-modal {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-body {
    padding: 1.5rem;
}

.setting-group {
    margin-bottom: 1.5rem;
}

.setting-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.setting-group select,
.setting-group input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.modal-footer {
    padding: 1rem;
    background: #f8fafc;
    text-align: right;
}

.modal-footer button {
    margin-left: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.save-settings {
    background: var(--primary-color);
    color: white;
}

.cancel-settings {
    background: #6b7280;
    color: white;
}

/* Dark theme */
.dark {
    --background-color: #1f2937;
    --text-color: #f9fafb;
    --border-color: #374151;
}

.dark .feature-card {
    background: #374151;
}

.dark .modal-content {
    background: #1f2937;
    color: #f9fafb;
}

.dark .modal-footer {
    background: #374151;
}
```

## Step 8: Build and Test

**package.json:**
```json
{
  "name": "scraped-website-app",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "echo 'Development server for Tauri'",
    "build": "echo 'Build process for Tauri'",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "@tauri-apps/api": "^1.5.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^1.5.0"
  }
}
```

Build and run the application:

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri:dev

# Build for distribution
npm run tauri:build
```

## Step 9: Integration with WhyML Workflow

Create an automation script that handles the complete workflow:

**scripts/webpage-to-tauri.sh:**
```bash
#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <website-url> <app-name>"
    exit 1
fi

WEBSITE_URL=$1
APP_NAME=$2

echo "🌐 Scraping website: $WEBSITE_URL"
whyml scrape "$WEBSITE_URL" \
  --section metadata \
  --section analysis \
  --section structure \
  --section styles \
  --output "scraped/${APP_NAME}.yaml" \
  --verbose

echo "📱 Generating Tauri application..."
python3 scripts/generate-app.py "$APP_NAME"

echo "🔧 Building desktop application..."
npm run tauri:build

echo "✅ Desktop application created successfully!"
echo "📦 Find your app in: src-tauri/target/release/bundle/"
```

## Features Demonstrated

1. **Website Scraping**: Complete webpage analysis and structure extraction
2. **YAML Manifest**: Structured data representation of scraped content
3. **Desktop App Generation**: Conversion to cross-platform desktop application
4. **Native Performance**: Rust backend with JavaScript frontend
5. **Modern UI**: Responsive design with settings and controls
6. **Cross-Platform**: Windows, macOS, and Linux support

## Next Steps

- Add offline content caching
- Implement automatic updates
- Add more advanced UI components
- Integrate with system notifications
- Create installer packages
- Add analytics and crash reporting

This tutorial demonstrates the complete workflow from web scraping to desktop application deployment using WhyML and Tauri.
