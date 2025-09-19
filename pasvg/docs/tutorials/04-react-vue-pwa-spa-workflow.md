# Tutorial 4: React/Vue/PWA/SPA Creation from HTTP to YAML to Final Application

## Overview
This tutorial demonstrates the complete workflow from scraping a website with WhyML to creating modern React, Vue, PWA, and SPA applications with full deployment.

## Prerequisites
- WhyML installed (`pip install whyml`)
- Node.js 18+ and npm installed
- Docker and Docker Compose
- Basic knowledge of React/Vue, PWA concepts

## Project Structure
```
modern-web-apps/
├── scraped/
│   └── source-site.yaml
├── manifests/
│   ├── app-base.yaml
│   ├── react-app.yaml
│   ├── vue-app.yaml
│   ├── pwa-config.yaml
│   └── spa-router.yaml
├── apps/
│   ├── react-app/
│   ├── vue-app/
│   ├── pwa-app/
│   └── spa-app/
├── docker/
│   ├── react.dockerfile
│   ├── vue.dockerfile
│   └── nginx.conf
├── scripts/
│   ├── generate-react.js
│   ├── generate-vue.js
│   └── build-all.sh
└── docker-compose.yml
```

## Step 1: Scrape and Analyze Source Website

```bash
# Scrape with comprehensive analysis
whyml scrape https://example-modern-site.com \
  --section metadata \
  --section analysis \
  --section structure \
  --section styles \
  --section imports \
  --output scraped/source-site.yaml \
  --verbose

# Analyze for modern frameworks
whyml scrape https://example-modern-site.com \
  --section analysis \
  --test-conversion \
  --output scraped/analysis.yaml
```

## Step 2: Create Base Application Manifest

**manifests/app-base.yaml:**
```yaml
metadata:
  name: "Modern Web Application"
  description: "Multi-framework app generated from scraped content"
  version: "1.0.0"
  author: "WhyML Generator"

config:
  base_url: "/"
  api_endpoint: "/api"
  build_target: "modern"
  
variables:
  app_name: "ModernApp"
  primary_color: "#3b82f6"
  secondary_color: "#1e40af"
  background_color: "#ffffff"
  text_color: "#1f2937"

components:
  header:
    type: "navigation"
    props:
      brand: "{{app_name}}"
      links:
        - { path: "/", label: "Home", icon: "home" }
        - { path: "/about", label: "About", icon: "info" }
        - { path: "/contact", label: "Contact", icon: "mail" }
  
  footer:
    type: "content"
    props:
      copyright: "© 2024 {{app_name}}"
      links:
        - { href: "/privacy", label: "Privacy" }
        - { href: "/terms", label: "Terms" }

pages:
  home:
    title: "Welcome to {{app_name}}"
    components: ["header", "hero", "features", "footer"]
  about:
    title: "About {{app_name}}"
    components: ["header", "content", "footer"]
  contact:
    title: "Contact Us"
    components: ["header", "form", "footer"]

styles:
  theme:
    colors:
      primary: "{{primary_color}}"
      secondary: "{{secondary_color}}"
      background: "{{background_color}}"
      text: "{{text_color}}"
    fonts:
      primary: "'Inter', system-ui, sans-serif"
      mono: "'JetBrains Mono', monospace"
    spacing:
      xs: "0.25rem"
      sm: "0.5rem"
      md: "1rem"
      lg: "1.5rem"
      xl: "2rem"
```

## Step 3: React Application Generation

**manifests/react-app.yaml:**
```yaml
metadata:
  name: "React Application"
  framework: "react"
  version: "18.0.0"

config:
  build_tool: "vite"
  typescript: true
  routing: "react-router"
  state_management: "context"

structure:
  app_component: |
    import React from 'react';
    import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
    import { ThemeProvider } from './contexts/ThemeContext';
    import Header from './components/Header';
    import Footer from './components/Footer';
    import Home from './pages/Home';
    import About from './pages/About';
    import Contact from './pages/Contact';
    import './App.css';

    function App() {
      return (
        <ThemeProvider>
          <Router>
            <div className="app">
              <Header />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/about" element={<About />} />
                  <Route path="/contact" element={<Contact />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </Router>
        </ThemeProvider>
      );
    }

    export default App;

  header_component: |
    import React from 'react';
    import { Link, useLocation } from 'react-router-dom';
    import './Header.css';

    const Header = () => {
      const location = useLocation();
      
      const navItems = [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/about', label: 'About', icon: 'ℹ️' },
        { path: '/contact', label: 'Contact', icon: '📧' }
      ];

      return (
        <header className="header">
          <div className="container">
            <Link to="/" className="brand">
              {{app_name}}
            </Link>
            <nav className="nav">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
      );
    };

    export default Header;

  home_page: |
    import React, { useState, useEffect } from 'react';
    import './Home.css';

    const Home = () => {
      const [features, setFeatures] = useState([]);

      useEffect(() => {
        // Simulate loading scraped content
        setFeatures([
          {
            id: 1,
            title: 'Modern Framework',
            description: 'Built with React 18 and modern hooks',
            icon: '⚛️'
          },
          {
            id: 2,
            title: 'Responsive Design',
            description: 'Works perfectly on all devices',
            icon: '📱'
          },
          {
            id: 3,
            title: 'Fast Performance',
            description: 'Optimized for speed and efficiency',
            icon: '⚡'
          }
        ]);
      }, []);

      return (
        <div className="home">
          <section className="hero">
            <div className="container">
              <h1>Welcome to {{app_name}}</h1>
              <p>A modern web application generated from scraped content using WhyML</p>
              <button className="cta-button">Get Started</button>
            </div>
          </section>
          
          <section className="features">
            <div className="container">
              <h2>Features</h2>
              <div className="features-grid">
                {features.map((feature) => (
                  <div key={feature.id} className="feature-card">
                    <div className="feature-icon">{feature.icon}</div>
                    <h3>{feature.title}</h3>
                    <p>{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      );
    };

    export default Home;

dependencies:
  - "react@^18.0.0"
  - "react-dom@^18.0.0"
  - "react-router-dom@^6.0.0"
  - "vite@^4.0.0"
  - "@vitejs/plugin-react@^4.0.0"
```

## Step 4: Vue Application Generation

**manifests/vue-app.yaml:**
```yaml
metadata:
  name: "Vue Application"
  framework: "vue"
  version: "3.0.0"

config:
  build_tool: "vite"
  typescript: true
  routing: "vue-router"
  state_management: "pinia"

structure:
  app_component: |
    <template>
      <div id="app">
        <AppHeader />
        <main class="main-content">
          <router-view />
        </main>
        <AppFooter />
      </div>
    </template>

    <script setup lang="ts">
    import { onMounted } from 'vue'
    import AppHeader from './components/AppHeader.vue'
    import AppFooter from './components/AppFooter.vue'
    import { useThemeStore } from './stores/theme'

    const themeStore = useThemeStore()

    onMounted(() => {
      themeStore.initializeTheme()
    })
    </script>

    <style>
    #app {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .main-content {
      flex: 1;
    }
    </style>

  header_component: |
    <template>
      <header class="header">
        <div class="container">
          <router-link to="/" class="brand">
            {{app_name}}
          </router-link>
          <nav class="nav">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link"
              :class="{ active: $route.path === item.path }"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              {{ item.label }}
            </router-link>
          </nav>
        </div>
      </header>
    </template>

    <script setup lang="ts">
    import { ref } from 'vue'

    const navItems = ref([
      { path: '/', label: 'Home', icon: '🏠' },
      { path: '/about', label: 'About', icon: 'ℹ️' },
      { path: '/contact', label: 'Contact', icon: '📧' }
    ])
    </script>

  home_page: |
    <template>
      <div class="home">
        <section class="hero">
          <div class="container">
            <h1>Welcome to {{app_name}}</h1>
            <p>A modern Vue.js application generated from scraped content</p>
            <button class="cta-button" @click="handleGetStarted">
              Get Started
            </button>
          </div>
        </section>
        
        <section class="features">
          <div class="container">
            <h2>Features</h2>
            <div class="features-grid">
              <div
                v-for="feature in features"
                :key="feature.id"
                class="feature-card"
              >
                <div class="feature-icon">{{ feature.icon }}</div>
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>

    <script setup lang="ts">
    import { ref, onMounted } from 'vue'

    const features = ref([])

    const handleGetStarted = () => {
      console.log('Getting started...')
    }

    onMounted(() => {
      features.value = [
        {
          id: 1,
          title: 'Vue 3 Composition API',
          description: 'Built with the latest Vue.js features',
          icon: '💚'
        },
        {
          id: 2,
          title: 'TypeScript Support',
          description: 'Full type safety and better development experience',
          icon: '🔷'
        },
        {
          id: 3,
          title: 'Reactive Data',
          description: 'Efficient reactivity system for optimal performance',
          icon: '⚡'
        }
      ]
    })
    </script>

dependencies:
  - "vue@^3.3.0"
  - "vue-router@^4.2.0"
  - "pinia@^2.1.0"
  - "vite@^4.0.0"
  - "@vitejs/plugin-vue@^4.0.0"
```

## Step 5: PWA Configuration

**manifests/pwa-config.yaml:**
```yaml
metadata:
  name: "Progressive Web App"
  type: "pwa"

config:
  manifest:
    name: "{{app_name}} PWA"
    short_name: "{{app_name}}"
    description: "Progressive Web App generated from scraped content"
    start_url: "/"
    display: "standalone"
    theme_color: "{{primary_color}}"
    background_color: "{{background_color}}"
    icons:
      - src: "/icons/icon-192.png"
        sizes: "192x192"
        type: "image/png"
      - src: "/icons/icon-512.png"
        sizes: "512x512"
        type: "image/png"

  service_worker: |
    const CACHE_NAME = 'whyml-pwa-v1';
    const urlsToCache = [
      '/',
      '/static/css/main.css',
      '/static/js/main.js',
      '/manifest.json'
    ];

    self.addEventListener('install', (event) => {
      event.waitUntil(
        caches.open(CACHE_NAME)
          .then((cache) => cache.addAll(urlsToCache))
      );
    });

    self.addEventListener('fetch', (event) => {
      event.respondWith(
        caches.match(event.request)
          .then((response) => {
            if (response) {
              return response;
            }
            return fetch(event.request);
          }
        );
      );
    });

  features:
    - offline_support: true
    - push_notifications: true
    - background_sync: true
    - install_prompt: true
```

## Step 6: Generation Scripts

**scripts/generate-react.js:**
```javascript
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class ReactGenerator {
  constructor(manifestPath) {
    this.manifest = yaml.load(fs.readFileSync(manifestPath, 'utf8'));
    this.outputDir = 'apps/react-app';
  }

  generate() {
    this.createDirectoryStructure();
    this.generatePackageJson();
    this.generateViteConfig();
    this.generateComponents();
    this.generatePages();
    this.generateStyles();
    console.log('React app generated successfully!');
  }

  createDirectoryStructure() {
    const dirs = [
      'src/components',
      'src/pages',
      'src/contexts',
      'src/hooks',
      'src/utils',
      'public'
    ];

    dirs.forEach(dir => {
      fs.mkdirSync(path.join(this.outputDir, dir), { recursive: true });
    });
  }

  generatePackageJson() {
    const packageJson = {
      name: this.manifest.metadata.name.toLowerCase().replace(/\s+/g, '-'),
      version: this.manifest.metadata.version,
      type: 'module',
      scripts: {
        dev: 'vite',
        build: 'vite build',
        preview: 'vite preview'
      },
      dependencies: Object.fromEntries(
        this.manifest.dependencies.map(dep => {
          const [name, version] = dep.split('@');
          return [name, version || 'latest'];
        })
      ),
      devDependencies: {
        '@types/react': '^18.0.0',
        '@types/react-dom': '^18.0.0',
        'typescript': '^5.0.0'
      }
    };

    fs.writeFileSync(
      path.join(this.outputDir, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );
  }

  generateComponents() {
    const components = this.manifest.structure;
    
    Object.entries(components).forEach(([key, content]) => {
      if (key.includes('component')) {
        const componentName = this.toPascalCase(key.replace('_component', ''));
        const filePath = path.join(this.outputDir, 'src/components', `${componentName}.jsx`);
        
        // Process template variables
        const processedContent = this.processTemplate(content);
        fs.writeFileSync(filePath, processedContent);
      }
    });
  }

  generatePages() {
    const pages = this.manifest.structure;
    
    Object.entries(pages).forEach(([key, content]) => {
      if (key.includes('page')) {
        const pageName = this.toPascalCase(key.replace('_page', ''));
        const filePath = path.join(this.outputDir, 'src/pages', `${pageName}.jsx`);
        
        const processedContent = this.processTemplate(content);
        fs.writeFileSync(filePath, processedContent);
      }
    });
  }

  processTemplate(content) {
    const variables = this.manifest.variables || {};
    let processed = content;
    
    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      processed = processed.replace(regex, value);
    });
    
    return processed;
  }

  toPascalCase(str) {
    return str.replace(/(^\w|_\w)/g, match => 
      match.replace('_', '').toUpperCase()
    );
  }
}

// Usage
const generator = new ReactGenerator('manifests/react-app.yaml');
generator.generate();
```

## Step 7: Docker Configuration

**docker/react.dockerfile:**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY apps/react-app/package*.json ./
RUN npm ci --only=production

COPY apps/react-app/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  react-app:
    build:
      context: .
      dockerfile: docker/react.dockerfile
    ports:
      - "3001:80"
    environment:
      - NODE_ENV=production

  vue-app:
    build:
      context: .
      dockerfile: docker/vue.dockerfile
    ports:
      - "3002:80"
    environment:
      - NODE_ENV=production

  pwa-app:
    build:
      context: .
      dockerfile: docker/pwa.dockerfile
    ports:
      - "3003:80"
    environment:
      - NODE_ENV=production
    volumes:
      - ./pwa-assets:/usr/share/nginx/html/assets

networks:
  default:
    name: whyml-apps
```

## Step 8: Build and Deploy

**scripts/build-all.sh:**
```bash
#!/bin/bash

echo "🌐 Scraping source website..."
whyml scrape https://example-modern-site.com \
  --section metadata \
  --section analysis \
  --section structure \
  --section styles \
  --output scraped/source-site.yaml

echo "⚛️ Generating React application..."
node scripts/generate-react.js

echo "💚 Generating Vue application..."
node scripts/generate-vue.js

echo "📱 Generating PWA..."
node scripts/generate-pwa.js

echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting all applications..."
docker-compose up -d

echo "✅ All applications deployed successfully!"
echo "React App: http://localhost:3001"
echo "Vue App: http://localhost:3002"
echo "PWA: http://localhost:3003"
```

## Features Demonstrated

1. **Multi-Framework Support**: React, Vue, PWA generation from single manifest
2. **Modern Build Tools**: Vite, TypeScript, modern JavaScript features
3. **Component Architecture**: Reusable components and pages
4. **Routing**: Client-side routing with React Router and Vue Router
5. **State Management**: Context API (React) and Pinia (Vue)
6. **PWA Features**: Service workers, offline support, installable apps
7. **Docker Deployment**: Containerized applications with Nginx
8. **Template Processing**: Variable substitution and dynamic content

## Usage Examples

```bash
# Generate React app
whyml convert manifests/react-app.yaml --framework react --output apps/react-app/

# Generate Vue app  
whyml convert manifests/vue-app.yaml --framework vue --output apps/vue-app/

# Generate PWA
whyml convert manifests/pwa-config.yaml --type pwa --output apps/pwa-app/

# Build all apps
./scripts/build-all.sh
```

This tutorial demonstrates the complete workflow from website scraping to modern web application deployment across multiple frameworks and deployment targets.
