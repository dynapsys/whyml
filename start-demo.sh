#!/bin/bash

# WhyML Multi-Technology Stack Demonstration Startup Script
# This script starts all services for visual comparison of technology implementations

set -e

echo "🚀 WhyML Multi-Technology Stack Demonstration"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker and Docker Compose are installed
echo "🔍 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker prerequisites check passed${NC}"
echo ""

# Display service information
echo "📋 Service Configuration:"
echo "========================="
echo -e "${CYAN}🎛️  Dashboard (Summary):${NC}     http://localhost:8010"
echo -e "${RED}📄  HTML Static:${NC}           http://localhost:8011"
echo -e "${YELLOW}🟨  JavaScript/Node.js:${NC}    http://localhost:8012"
echo -e "${PURPLE}🐘  PHP 8.2:${NC}               http://localhost:8013"  
echo -e "${BLUE}⚛️   React:${NC}                 http://localhost:8014"
echo -e "${CYAN}📜  Source (Original):${NC}     http://localhost:8015"
echo -e "${BLUE}📘  TypeScript:${NC}            http://localhost:8016"
echo -e "${GREEN}🍃  Vue.js:${NC}                http://localhost:8017"
echo -e "${CYAN}📸  Screenshot Service:${NC}    http://localhost:8018"
echo ""

# Check if ports are available
echo "🔍 Checking port availability..."
PORTS=(8010 8011 8012 8013 8014 8015 8016 8017 8018)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Warning: Port $port is already in use${NC}"
    fi
done
echo ""

# Build and start services
echo "🏗️  Building and starting services..."
echo "====================================="

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build all services
echo "🔨 Building services..."
if docker-compose build; then
    echo -e "${GREEN}✅ All services built successfully${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Start services
echo "🚀 Starting services..."
if docker-compose up -d; then
    echo -e "${GREEN}✅ All services started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo ""
echo "🏥 Service Health Check:"
echo "======================="

for port in "${PORTS[@]}"; do
    SERVICE_NAME=""
    case $port in
        8010) SERVICE_NAME="Dashboard" ;;
        8011) SERVICE_NAME="HTML Static" ;;
        8012) SERVICE_NAME="JavaScript/Node.js" ;;
        8013) SERVICE_NAME="PHP 8.2" ;;
        8014) SERVICE_NAME="React" ;;
        8015) SERVICE_NAME="Source (Original)" ;;
        8016) SERVICE_NAME="TypeScript" ;;
        8017) SERVICE_NAME="Vue.js" ;;
        8018) SERVICE_NAME="Screenshot Service" ;;
    esac
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port | grep -q "200\|302"; then
        echo -e "${GREEN}✅ $SERVICE_NAME (Port $port): Running${NC}"
    else
        echo -e "${YELLOW}⚠️  $SERVICE_NAME (Port $port): Starting up...${NC}"
    fi
done

echo ""
echo "🎉 WhyML Multi-Technology Stack Demo is ready!"
echo "=============================================="
echo ""
echo -e "${CYAN}🎛️  Access the main dashboard at: ${YELLOW}http://localhost:8010${NC}"
echo ""
echo "📖 Usage Instructions:"
echo "====================="
echo "1. Open http://localhost:8010 in your browser"
echo "2. View the visual comparison of all technology implementations"
echo "3. Click 'Preview' buttons to load iframe previews"
echo "4. Click 'Open' buttons to view individual services in new tabs"
echo "5. Compare how the same HTML content is rendered across different stacks"
echo ""
echo "🛠️  Management Commands:"
echo "======================="
echo "• View logs:           docker-compose logs -f"
echo "• Stop services:       docker-compose down"
echo "• Restart services:    docker-compose restart"
echo "• View service status: docker-compose ps"
echo ""
echo "🔧 Troubleshooting:"
echo "=================="
echo "• If services don't load, wait a few more seconds for initialization"
echo "• Check logs with: docker-compose logs [service-name]"
echo "• Restart specific service: docker-compose restart [service-name]"
echo ""
echo -e "${GREEN}Happy comparing! 🚀${NC}"
