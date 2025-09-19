
// SPA Router Configuration
const routes = {};

class Router {
    constructor() {
        this.routes = new Map();
        this.currentPath = '/';
        this.init();
    }
    
    init() {
        // Load routes from configuration
        Object.entries(routes).forEach(([path, component]) => {
            this.addRoute(path, component);
        });
        
        // Handle browser navigation
        window.addEventListener('popstate', () => this.handleRoute());
        
        // Handle initial load
        document.addEventListener('DOMContentLoaded', () => this.handleRoute());
        
        // Handle navigation clicks
        document.addEventListener('click', this.handleClick.bind(this));
    }
    
    addRoute(path, component) {
        this.routes.set(path, component);
    }
    
    handleClick(event) {
        if (event.target.matches('a[href^="/"]')) {
            event.preventDefault();
            this.navigateTo(event.target.getAttribute('href'));
        }
    }
    
    navigateTo(path, replace = false) {
        if (replace) {
            history.replaceState(null, null, path);
        } else {
            history.pushState(null, null, path);
        }
        this.handleRoute();
    }
    
    handleRoute() {
        const path = window.location.pathname;
        this.currentPath = path;
        
        const route = this.routes.get(path) || this.routes.get('*') || this.routes.get('/');
        
        if (route) {
            this.renderRoute(route, path);
        } else {
            this.render404();
        }
    }
    
    renderRoute(route, path) {
        const container = document.getElementById('app') || document.body;
        
        if (typeof route === 'string') {
            container.innerHTML = route;
        } else if (typeof route === 'function') {
            route(container, path);
        } else if (route.template) {
            container.innerHTML = route.template;
        }
        
        // Trigger route change event
        window.dispatchEvent(new CustomEvent('routechange', {
            detail: { path, route }
        }));
    }
    
    render404() {
        const container = document.getElementById('app') || document.body;
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/">Go Home</a>
            </div>
        `;
    }
}

// Initialize router
const router = new Router();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = router;
}
