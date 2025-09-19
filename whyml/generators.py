"""
WhyML Generators - Helper functions for generating various application artifacts

This module contains utility functions for generating PWA, SPA, Docker, Tauri,
and other application artifacts from WhyML manifests.
"""

import json
from typing import Dict, Any


def enhance_for_spa(html_content: str, manifest: Dict[str, Any]) -> str:
    """Enhance HTML content for Single Page Application functionality."""
    
    # Add SPA routing script
    spa_script = """
    <script>
    // Simple SPA Router
    class SPARouter {
        constructor() {
            this.routes = {};
            this.currentRoute = null;
            this.init();
        }
        
        init() {
            window.addEventListener('popstate', () => this.handleRoute());
            document.addEventListener('DOMContentLoaded', () => this.handleRoute());
            
            // Handle link clicks
            document.addEventListener('click', (e) => {
                if (e.target.matches('a[data-route]')) {
                    e.preventDefault();
                    this.navigateTo(e.target.getAttribute('data-route'));
                }
            });
        }
        
        addRoute(path, component) {
            this.routes[path] = component;
        }
        
        navigateTo(path) {
            history.pushState(null, null, path);
            this.handleRoute();
        }
        
        handleRoute() {
            const path = window.location.pathname;
            const route = this.routes[path] || this.routes['/'];
            
            if (route) {
                this.currentRoute = path;
                if (typeof route === 'function') {
                    route();
                } else {
                    this.renderComponent(route);
                }
            }
        }
        
        renderComponent(component) {
            const appContainer = document.getElementById('app') || document.body;
            if (typeof component === 'string') {
                appContainer.innerHTML = component;
            }
        }
    }
    
    // Initialize router
    const router = new SPARouter();
    
    // Add default routes based on manifest
    router.addRoute('/', () => {
        console.log('Home route');
    });
    
    // Add routes from manifest if defined
    const routes = """ + json.dumps(manifest.get('routes', {})) + """;
    Object.keys(routes).forEach(path => {
        router.addRoute(path, () => {
            console.log('Route:', path);
        });
    });
    </script>
    """
    
    # Insert before closing body tag
    if '</body>' in html_content:
        return html_content.replace('</body>', f'{spa_script}\n</body>')
    else:
        return html_content + spa_script


def enhance_for_pwa(html_content: str, manifest: Dict[str, Any]) -> str:
    """Enhance HTML content for Progressive Web Application functionality."""
    
    # Add PWA features
    pwa_head = f"""
    <meta name="theme-color" content="{manifest.get('metadata', {}).get('theme_color', '#000000')}">
    <meta name="background-color" content="{manifest.get('metadata', {}).get('background_color', '#ffffff')}">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192x192.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{manifest.get('metadata', {}).get('title', 'WhyML App')}">
    """
    
    pwa_script = """
    <script>
    // Service Worker Registration
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
    
    // PWA Install Prompt
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        deferredPrompt = e;
        showInstallPromotion();
    });
    
    function showInstallPromotion() {
        const installButton = document.createElement('button');
        installButton.textContent = 'Install App';
        installButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            z-index: 1000;
        `;
        
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User ${outcome} the install prompt`);
                deferredPrompt = null;
                document.body.removeChild(installButton);
            }
        });
        
        document.body.appendChild(installButton);
    }
    </script>
    """
    
    # Insert head content
    if '<head>' in html_content:
        html_content = html_content.replace('<head>', f'<head>\n{pwa_head}')
    
    # Insert script before closing body tag
    if '</body>' in html_content:
        return html_content.replace('</body>', f'{pwa_script}\n</body>')
    else:
        return html_content + pwa_script


def generate_service_worker(manifest: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate service worker for PWA."""
    
    app_name = manifest.get('metadata', {}).get('title', 'WhyML App')
    version = manifest.get('metadata', {}).get('version', '1.0.0')
    
    # Only cache essential files that are guaranteed to exist
    cache_files = [
        '/',
        '/index.html',
        '/manifest.json',
        '/offline.html'
    ]
    
    # Add any additional static assets if specified in config
    additional_assets = config.get('cache_assets', [])
    if additional_assets:
        cache_files.extend(additional_assets)
    
    cache_list = ',\n    '.join(f"'{asset}'" for asset in cache_files)
    
    return f"""
// Service Worker for {app_name} v{version}
const CACHE_NAME = '{app_name.lower().replace(' ', '-')}-v{version}';
const urlsToCache = [
    {cache_list}
];

// Install event
self.addEventListener('install', event => {{
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {{
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            }})
    );
}});

// Fetch event
self.addEventListener('fetch', event => {{
    event.respondWith(
        caches.match(event.request)
            .then(response => {{
                // Return cached version or fetch from network
                if (response) {{
                    return response;
                }}
                
                return fetch(event.request).catch(() => {{
                    // If both cache and network fail, show offline page
                    if (event.request.destination === 'document') {{
                        return caches.match('/offline.html');
                    }}
                }});
            }})
    );
}});

// Activate event
self.addEventListener('activate', event => {{
    event.waitUntil(
        caches.keys().then(cacheNames => {{
            return Promise.all(
                cacheNames.map(cacheName => {{
                    if (cacheName !== CACHE_NAME) {{
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }})
    );
}});
"""


def generate_web_manifest(manifest: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate web app manifest for PWA."""
    
    metadata = manifest.get('metadata', {})
    
    # Get icons from config or use data URLs for default icons
    icons = config.get('icons', [])
    if not icons:
        # Generate default icons using data URLs to avoid 404 errors
        default_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="%23007acc"/><text x="256" y="280" font-family="Arial,sans-serif" font-size="200" fill="white" text-anchor="middle">W</text></svg>"""
        default_icon_data_url = f"data:image/svg+xml;base64,{__import__('base64').b64encode(default_icon_svg.encode()).decode()}"
        
        icons = [
            {
                "src": default_icon_data_url,
                "sizes": "192x192",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            },
            {
                "src": default_icon_data_url,
                "sizes": "512x512", 
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    
    return {
        "name": metadata.get('title', 'WhyML App'),
        "short_name": metadata.get('short_name', metadata.get('title', 'App')[:12]),
        "description": metadata.get('description', 'Generated by WhyML'),
        "start_url": "/",
        "display": "standalone",
        "background_color": metadata.get('background_color', '#ffffff'),
        "theme_color": metadata.get('theme_color', '#007acc'),
        "orientation": "portrait-primary",
        "icons": icons,
        "categories": ["productivity", "utilities"],
        "screenshots": [],
        "related_applications": [],
        "prefer_related_applications": False
    }


def generate_offline_page(manifest: Dict[str, Any]) -> str:
    """Generate offline page for PWA."""
    
    app_name = manifest.get('metadata', {}).get('title', 'WhyML App')
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - {app_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .offline-container {{
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }}
        button {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 1rem 2rem;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
    </style>
</head>
<body>
    <div class="offline-container">
        <h1>📱</h1>
        <h2>You're Offline</h2>
        <p>Sorry, you need an internet connection to access {app_name}.</p>
        <button onclick="window.location.reload()">Try Again</button>
    </div>
</body>
</html>
"""


def generate_spa_enhancements(manifest: Dict[str, Any]) -> str:
    """Generate SPA-specific enhancements and utilities."""
    
    app_name = manifest.get('metadata', {}).get('title', 'WhyML SPA')
    
    return f"""
// SPA Enhancements for {app_name}
class SPAApp {{
    constructor() {{
        this.currentRoute = '/';
        this.routes = {{}};
        this.init();
    }}
    
    init() {{
        window.addEventListener('popstate', () => {{
            this.handleRouteChange();
        }});
        
        // Handle initial route
        this.handleRouteChange();
        
        // Setup navigation links
        this.setupNavigationLinks();
    }}
    
    setupNavigationLinks() {{
        document.addEventListener('click', (e) => {{
            if (e.target.tagName === 'A' && e.target.getAttribute('href')) {{
                const href = e.target.getAttribute('href');
                if (href.startsWith('/') || href.startsWith('#')) {{
                    e.preventDefault();
                    this.navigateTo(href);
                }}
            }}
        }});
    }}
    
    navigateTo(path) {{
        if (path !== this.currentRoute) {{
            history.pushState(null, '', path);
            this.currentRoute = path;
            this.handleRouteChange();
        }}
    }}
    
    handleRouteChange() {{
        const path = window.location.pathname || '/';
        this.currentRoute = path;
        
        // Trigger route change event
        const event = new CustomEvent('spa-route-change', {{
            detail: {{ path, route: this.currentRoute }}
        }});
        document.dispatchEvent(event);
    }}
    
    // Add page transition effects
    transitionTo(newContent) {{
        const main = document.querySelector('main') || document.body;
        main.style.opacity = '0';
        
        setTimeout(() => {{
            main.innerHTML = newContent;
            main.style.opacity = '1';
        }}, 150);
    }}
}}

// Initialize SPA
if (typeof window !== 'undefined') {{
    window.spaApp = new SPAApp();
}}
"""

def generate_pwa_enhancements(manifest: Dict[str, Any]) -> str:
    """Generate PWA-specific enhancements and service worker registration."""
    
    app_name = manifest.get('metadata', {}).get('title', 'WhyML PWA')
    
    return f"""
// PWA Enhancements for {app_name}
class PWAApp {{
    constructor() {{
        this.isOnline = navigator.onLine;
        this.init();
    }}
    
    init() {{
        // Register service worker
        this.registerServiceWorker();
        
        // Setup online/offline detection
        this.setupConnectivityDetection();
        
        // Setup install prompt
        this.setupInstallPrompt();
        
        // Setup update notifications
        this.setupUpdateNotifications();
    }}
    
    async registerServiceWorker() {{
        if ('serviceWorker' in navigator) {{
            try {{
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {{
                    this.handleServiceWorkerUpdate(registration);
                }});
            }} catch (error) {{
                console.error('Service Worker registration failed:', error);
            }}
        }}
    }}
    
    handleServiceWorkerUpdate(registration) {{
        const newWorker = registration.installing;
        if (newWorker) {{
            newWorker.addEventListener('statechange', () => {{
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {{
                    this.showUpdateNotification();
                }}
            }});
        }}
    }}
    
    setupConnectivityDetection() {{
        window.addEventListener('online', () => {{
            this.isOnline = true;
            this.showConnectivityStatus('online');
        }});
        
        window.addEventListener('offline', () => {{
            this.isOnline = false;
            this.showConnectivityStatus('offline');
        }});
    }}
    
    setupInstallPrompt() {{
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton();
        }});
        
        // Handle install button click
        document.addEventListener('click', async (e) => {{
            if (e.target.id === 'pwa-install-btn') {{
                if (deferredPrompt) {{
                    deferredPrompt.prompt();
                    const {{ outcome }} = await deferredPrompt.userChoice;
                    console.log('Install prompt outcome:', outcome);
                    deferredPrompt = null;
                    this.hideInstallButton();
                }}
            }}
        }});
    }}
    
    showInstallButton() {{
        if (!document.getElementById('pwa-install-btn')) {{
            const button = document.createElement('button');
            button.id = 'pwa-install-btn';
            button.textContent = 'Install App';
            button.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #007acc;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                cursor: pointer;
                z-index: 1000;
                font-family: Arial, sans-serif;
            `;
            document.body.appendChild(button);
        }}
    }}
    
    hideInstallButton() {{
        const button = document.getElementById('pwa-install-btn');
        if (button) {{
            button.remove();
        }}
    }}
    
    showConnectivityStatus(status) {{
        const existing = document.getElementById('connectivity-status');
        if (existing) existing.remove();
        
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connectivity-status';
        statusDiv.textContent = status === 'online' ? 'Back online!' : 'You are offline';
        statusDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 10px 20px;
            border-radius: 6px;
            color: white;
            background: ${{status === 'online' ? '#4CAF50' : '#f44336'}};
            z-index: 1000;
            font-family: Arial, sans-serif;
        `;
        
        document.body.appendChild(statusDiv);
        
        setTimeout(() => {{
            if (statusDiv && statusDiv.parentNode) {{
                statusDiv.parentNode.removeChild(statusDiv);
            }}
        }}, 3000);
    }}
    
    showUpdateNotification() {{
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #333;
            color: white;
            padding: 15px;
            border-radius: 6px;
            z-index: 1000;
            font-family: Arial, sans-serif;
        `;
        notification.innerHTML = `
            <div>New version available!</div>
            <button onclick="window.location.reload()" style="
                background: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            ">Refresh</button>
        `;
        
        document.body.appendChild(notification);
    }}
    
    setupUpdateNotifications() {{
        // Check for updates periodically
        setInterval(() => {{
            if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {{
                navigator.serviceWorker.controller.postMessage({{ type: 'CHECK_FOR_UPDATES' }});
            }}
        }}, 60000); // Check every minute
    }}
}}

// Initialize PWA
if (typeof window !== 'undefined') {{
    window.pwaApp = new PWAApp();
}}
"""

def generate_spa_router(manifest: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Generate router configuration for SPA."""
    
    routes = manifest.get('routes', {})
    
    return f"""
// SPA Router Configuration
const routes = {json.dumps(routes, indent=2)};

class Router {{
    constructor() {{
        this.routes = new Map();
        this.currentPath = '/';
        this.init();
    }}
    
    init() {{
        // Load routes from configuration
        Object.entries(routes).forEach(([path, component]) => {{
            this.addRoute(path, component);
        }});
        
        // Handle browser navigation
        window.addEventListener('popstate', () => this.handleRoute());
        
        // Handle initial load
        document.addEventListener('DOMContentLoaded', () => this.handleRoute());
        
        // Handle navigation clicks
        document.addEventListener('click', this.handleClick.bind(this));
    }}
    
    addRoute(path, component) {{
        this.routes.set(path, component);
    }}
    
    handleClick(event) {{
        if (event.target.matches('a[href^="/"]')) {{
            event.preventDefault();
            this.navigateTo(event.target.getAttribute('href'));
        }}
    }}
    
    navigateTo(path, replace = false) {{
        if (replace) {{
            history.replaceState(null, null, path);
        }} else {{
            history.pushState(null, null, path);
        }}
        this.handleRoute();
    }}
    
    handleRoute() {{
        const path = window.location.pathname;
        this.currentPath = path;
        
        const route = this.routes.get(path) || this.routes.get('*') || this.routes.get('/');
        
        if (route) {{
            this.renderRoute(route, path);
        }} else {{
            this.render404();
        }}
    }}
    
    renderRoute(route, path) {{
        const container = document.getElementById('app') || document.body;
        
        if (typeof route === 'string') {{
            container.innerHTML = route;
        }} else if (typeof route === 'function') {{
            route(container, path);
        }} else if (route.template) {{
            container.innerHTML = route.template;
        }}
        
        // Trigger route change event
        window.dispatchEvent(new CustomEvent('routechange', {{
            detail: {{ path, route }}
        }}));
    }}
    
    render404() {{
        const container = document.getElementById('app') || document.body;
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/">Go Home</a>
            </div>
        `;
    }}
}}

// Initialize router
const router = new Router();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = router;
}}
"""


def generate_capacitor_config(manifest: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Capacitor configuration for APK generation."""
    
    metadata = manifest.get('metadata', {})
    
    return {
        "appId": config.get('app_id', f"com.whyml.{metadata.get('title', 'app').lower().replace(' ', '')}"),
        "appName": metadata.get('title', 'WhyML App'),
        "webDir": "www",
        "bundledWebRuntime": False,
        "server": {
            "androidScheme": "https"
        },
        "plugins": {
            "CapacitorHttp": {
                "enabled": True
            },
            "SplashScreen": {
                "launchShowDuration": 3000,
                "launchAutoHide": True,
                "backgroundColor": metadata.get('background_color', '#ffffff'),
                "androidSplashResourceName": "splash",
                "showSpinner": True
            }
        }
    }


def generate_capacitor_package_json(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Generate package.json for Capacitor project."""
    
    metadata = manifest.get('metadata', {})
    
    return {
        "name": metadata.get('title', 'whyml-app').lower().replace(' ', '-'),
        "version": metadata.get('version', '1.0.0'),
        "description": metadata.get('description', 'Generated by WhyML'),
        "main": "index.js",
        "scripts": {
            "build": "echo 'Build completed'",
            "android": "npx cap run android",
            "ios": "npx cap run ios",
            "sync": "npx cap sync",
            "copy": "npx cap copy"
        },
        "dependencies": {
            "@capacitor/android": "^5.0.0",
            "@capacitor/core": "^5.0.0",
            "@capacitor/ios": "^5.0.0"
        },
        "devDependencies": {
            "@capacitor/cli": "^5.0.0"
        }
    }


def generate_dockerfile(manifest: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate Dockerfile for containerization."""
    
    metadata = manifest.get('metadata', {})
    node_version = config.get('node_version', '18-alpine')
    
    return f"""# Dockerfile for {metadata.get('title', 'WhyML App')}
FROM node:{node_version}

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application files
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S whyml -u 1001

# Change ownership of the app directory
RUN chown -R whyml:nodejs /app
USER whyml

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application
CMD ["node", "server.js"]
"""


def generate_docker_compose(manifest: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate docker-compose.yml for development."""
    
    metadata = manifest.get('metadata', {})
    app_name = metadata.get('title', 'whyml-app').lower().replace(' ', '-')
    
    compose_config = {
        'version': '3.8',
        'services': {
            'whyml-app': {
                'build': '.',
                'ports': ['8080:8080'],
                'environment': [
                    'NODE_ENV=production',
                    'WHYML_HOST=0.0.0.0',
                    'WHYML_PORT=8080'
                ],
                'volumes': [
                    './manifests:/app/manifests:ro',
                    './assets:/app/assets:ro'
                ],
                'restart': 'unless-stopped',
                'healthcheck': {
                    'test': ['CMD', 'curl', '-f', 'http://localhost:8080/api/health'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3
                }
            }
        },
        'networks': {
            'whyml-network': {
                'driver': 'bridge'
            }
        }
    }
    
    import yaml
    return yaml.dump(compose_config, default_flow_style=False)


def generate_dockerignore() -> str:
    """Generate .dockerignore file."""
    
    return """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/
.nyc_output/

# Production builds
build/
dist/

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# Documentation
docs/
README.md
"""


def generate_tauri_config(manifest: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Tauri configuration."""
    
    metadata = manifest.get('metadata', {})
    
    return {
        "build": {
            "beforeDevCommand": "npm run dev",
            "beforeBuildCommand": "npm run build",
            "devPath": "http://localhost:3000",
            "distDir": "../dist"
        },
        "package": {
            "productName": metadata.get('title', 'WhyML App'),
            "version": metadata.get('version', '1.0.0')
        },
        "tauri": {
            "allowlist": {
                "all": False,
                "shell": {
                    "all": False,
                    "open": True
                },
                "window": {
                    "all": False,
                    "close": True,
                    "hide": True,
                    "show": True,
                    "maximize": True,
                    "minimize": True,
                    "unmaximize": True,
                    "unminimize": True,
                    "startDragging": True
                }
            },
            "bundle": {
                "active": True,
                "category": "DeveloperTool",
                "copyright": f"© {metadata.get('author', 'WhyML')}",
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
                "identifier": f"com.whyml.{metadata.get('title', 'app').lower().replace(' ', '')}",
                "longDescription": metadata.get('description', 'Generated by WhyML'),
                "macOS": {
                    "entitlements": None,
                    "exceptionDomain": "",
                    "frameworks": [],
                    "providerShortName": None,
                    "signingIdentity": None
                },
                "resources": [],
                "shortDescription": metadata.get('description', 'Generated by WhyML'),
                "targets": "all",
                "windows": {
                    "certificateThumbprint": None,
                    "digestAlgorithm": "sha256",
                    "timestampUrl": ""
                }
            },
            "security": {
                "csp": None
            },
            "updater": {
                "active": False
            },
            "windows": [
                {
                    "fullscreen": False,
                    "height": 600,
                    "resizable": True,
                    "title": metadata.get('title', 'WhyML App'),
                    "width": 800,
                    "center": True
                }
            ]
        }
    }


def generate_cargo_toml(manifest: Dict[str, Any]) -> str:
    """Generate Cargo.toml for Tauri."""
    
    metadata = manifest.get('metadata', {})
    app_name = metadata.get('title', 'whyml-app').lower().replace(' ', '-').replace('_', '-')
    
    return f"""[package]
name = "{app_name}"
version = "{metadata.get('version', '1.0.0')}"
description = "{metadata.get('description', 'Generated by WhyML')}"
authors = ["{metadata.get('author', 'WhyML')}"]
license = "MIT"
repository = ""
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[build-dependencies]
tauri-build = {{ version = "1.0", features = [] }}

[dependencies]
serde_json = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
tauri = {{ version = "1.0", features = ["api-all"] }}

[features]
# by default Tauri runs in production mode
# when `tauri dev` runs it is executed with `cargo run --no-default-features` if `devPath` is an URL
default = ["custom-protocol"]
# this feature is used used for production builds where `devPath` points to the filesystem
# DO NOT remove this
custom-protocol = ["tauri/custom-protocol"]
"""


def generate_tauri_main_rs(manifest: Dict[str, Any]) -> str:
    """Generate main.rs for Tauri."""
    
    return """// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
"""
