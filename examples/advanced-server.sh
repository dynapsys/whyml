#!/bin/bash
# WhyML Advanced Server Examples
# Demonstrates the whyml run command with various configurations

echo "🚀 WhyML Advanced Server Examples"
echo "================================="

# Create an advanced manifest for server examples
echo "1. Creating advanced manifest with API routes..."
cat > advanced-manifest.yaml << EOF
metadata:
  title: "Advanced WhyML App"
  description: "Advanced WhyML application with API routes and real-time features"
  version: "2.0.0"
  author: "WhyML Developer"
  theme_color: "#6366f1"
  background_color: "#ffffff"

template_vars:
  api_base_url: "https://api.example.com"
  brand_name: "WhyML Advanced"
  primary_color: "#6366f1"
  secondary_color: "#ec4899"

api:
  routes:
    /users:
      method: "GET"
      description: "Get all users"
    /users/{id}:
      method: "GET" 
      description: "Get user by ID"
    /dashboard:
      method: "GET"
      description: "Dashboard data"

routes:
  "/": "Home page"
  "/about": "About page"
  "/dashboard": "Dashboard"
  "/profile": "User profile"
  "*": "404 Not Found"

styles:
  app:
    font-family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    margin: "0"
    padding: "0"
    background: "{{ background_color }}"
  
  navbar:
    background: "{{ primary_color }}"
    padding: "1rem"
    color: "white"
    display: "flex"
    justify-content: "space-between"
    align-items: "center"
  
  main:
    padding: "2rem"
    max-width: "1200px"
    margin: "0 auto"

interactions:
  handleNavigation: "router.navigateTo"
  handleApiCall: "api.fetch"
  handleWebSocket: "ws.connect"

structure:
  div:
    class: "app"
    children:
      - nav:
          class: "navbar"
          children:
            - div:
                class: "brand"
                text: "{{ brand_name }}"
            - div:
                class: "nav-links"
                children:
                  - a:
                      href: "/"
                      text: "Home"
                      data-route: "/"
                  - a:
                      href: "/about"
                      text: "About"
                      data-route: "/about"
                  - a:
                      href: "/dashboard"
                      text: "Dashboard"
                      data-route: "/dashboard"
      - main:
          id: "app"
          class: "main"
          children:
            - div:
                id: "loading"
                text: "Loading..."
EOF

echo "✅ Advanced manifest created: advanced-manifest.yaml"
echo ""

# Basic server startup
echo "2. Basic development server:"
echo "whyml run -f advanced-manifest.yaml"
echo ""

# Server with custom host and port
echo "3. Custom host and port:"
echo "whyml run -f advanced-manifest.yaml -p 3000 -h 0.0.0.0"
echo ""

# Server with file watching
echo "4. Development server with file watching:"
echo "whyml run -f advanced-manifest.yaml --port 8080 --watch"
echo ""

# Generate Caddy configuration for production
echo "5. Generating Caddy configuration for production deployment:"
whyml run -f advanced-manifest.yaml --port 80 --host web.local --tls-provider letsencrypt --caddy-config Caddyfile.json

if [ -f "Caddyfile.json" ]; then
    echo "✅ Caddy configuration generated: Caddyfile.json"
    echo "Preview of generated config:"
    head -20 Caddyfile.json
else
    echo "ℹ️  Caddy configuration would be generated with this command"
fi
echo ""

# Using serve command (alias for run)
echo "6. Using serve command (alias for run):"
echo "whyml serve -f advanced-manifest.yaml --port 8080 --watch"
echo ""

# Environment file integration
echo "7. Creating .env file for configuration:"
cat > .env.example << EOF
# WhyML Environment Configuration
WHYML_HOST=localhost
WHYML_PORT=8080
WHYML_WATCH=true

# Application Configuration
API_BASE_URL=https://api.example.com
BRAND_NAME="My WhyML App"
PRIMARY_COLOR=#6366f1
SECONDARY_COLOR=#ec4899

# Database (if needed)
DATABASE_URL=sqlite:///app.db

# External Services
SENTRY_DSN=your_sentry_dsn_here
ANALYTICS_ID=your_analytics_id
EOF

echo "✅ Environment file example created: .env.example"
echo ""

# Convert with environment variables
echo "8. Converting with environment file:"
echo "whyml convert --from advanced-manifest.yaml --to advanced-app.html -as pwa --env-file .env.example"
echo ""

# Production deployment examples
echo "9. Production Deployment Examples:"
echo ""

echo "   Docker deployment:"
echo "   whyml generate docker -f advanced-manifest.yaml -o ./production"
echo ""

echo "   Caddy + Docker deployment:"
cat > docker-compose.production.yml << EOF
version: '3.8'
services:
  whyml-app:
    build: .
    environment:
      - NODE_ENV=production
      - WHYML_HOST=0.0.0.0
      - WHYML_PORT=8080
    networks:
      - whyml-network
    
  caddy:
    image: caddy:2.7-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    networks:
      - whyml-network
    depends_on:
      - whyml-app

networks:
  whyml-network:
    driver: bridge

volumes:
  caddy-data:
  caddy-config:
EOF

echo "✅ Production Docker Compose created: docker-compose.production.yml"
echo ""

echo "   To deploy in production:"
echo "   1. Copy your manifest and assets to the server"
echo "   2. Generate Caddy config: whyml run --caddy-config Caddyfile.json --host yourdomain.com --tls-provider letsencrypt"
echo "   3. Start with: docker-compose -f docker-compose.production.yml up -d"
echo ""

# Real-time features
echo "10. Real-time Features (WebSocket support):"
echo "    The WhyML server automatically supports WebSocket connections for:"
echo "    - Live reload during development"
echo "    - Real-time manifest updates"
echo "    - Custom WebSocket endpoints"
echo ""
echo "    WebSocket endpoint: ws://localhost:8080/ws"
echo ""

# API Integration
echo "11. API Integration Examples:"
echo "    The server provides these API endpoints:"
echo "    - GET /api/health - Health check"
echo "    - GET /api/info - Server information"
echo "    - GET /manifest - Get current manifest"
echo "    - POST /manifest - Update manifest"
echo "    - GET /convert/{format} - Convert current manifest"
echo "    - POST /convert/{format} - Convert provided manifest"
echo "    - POST /api/validate - Validate manifest"
echo ""

echo "🎉 Advanced server examples completed!"
echo ""
echo "Quick Start Commands:"
echo "====================="
echo "# Development server with watching:"
echo "whyml run -f advanced-manifest.yaml --watch"
echo ""
echo "# Production-ready server:"
echo "whyml run -f advanced-manifest.yaml --port 80 --host yourdomain.com --tls-provider letsencrypt"
echo ""
echo "# Generate production deployment:"
echo "whyml generate docker -f advanced-manifest.yaml"
echo "whyml generate caddy -f advanced-manifest.yaml"
