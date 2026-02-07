#!/bin/bash

# PitchCube Startup Script
# This script helps start the PitchCube application

set -e

echo "🎲 Starting PitchCube..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please edit it with your configuration.${NC}"
    echo -e "${YELLOW}   Then run this script again.${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to check if services are healthy
check_health() {
    echo -e "${BLUE}🔍 Checking service health...${NC}"
    
    # Wait for services to be ready
    sleep 5
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${RED}❌ Backend is not responding${NC}"
        return 1
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${RED}❌ Frontend is not responding${NC}"
        return 1
    fi
    
    return 0
}

# Parse arguments
MODE=${1:-"docker"}

if [ "$MODE" = "docker" ]; then
    echo -e "${BLUE}🐳 Starting with Docker Compose...${NC}"
    
    # Build and start services
    docker-compose up --build -d
    
    # Check health
    if check_health; then
        echo ""
        echo -e "${GREEN}🎉 PitchCube is now running!${NC}"
        echo ""
        echo -e "${BLUE}   Frontend:${NC} http://localhost:3000"
        echo -e "${BLUE}   Backend API:${NC} http://localhost:8000"
        echo -e "${BLUE}   API Docs:${NC} http://localhost:8000/docs"
        echo ""
        echo -e "${YELLOW}   To stop:${NC} docker-compose down"
        echo -e "${YELLOW}   To view logs:${NC} docker-compose logs -f"
    else
        echo -e "${RED}❌ Some services failed to start. Check logs with: docker-compose logs${NC}"
        exit 1
    fi

elif [ "$MODE" = "dev" ]; then
    echo -e "${BLUE}🚀 Starting development mode...${NC}"
    
    # Start infrastructure services
    echo -e "${BLUE}📦 Starting infrastructure services...${NC}"
    docker-compose up -d mongodb redis
    
    # Wait for databases
    echo -e "${BLUE}⏳ Waiting for databases to be ready...${NC}"
    sleep 5
    
    # Install backend dependencies
    echo -e "${BLUE}🐍 Installing backend dependencies...${NC}"
    cd backend
    pip install -r requirements.txt
    
    # Start backend
    echo -e "${BLUE}▶️  Starting backend server...${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Install frontend dependencies
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    
    # Start frontend
    echo -e "${BLUE}▶️  Starting frontend dev server...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo -e "${GREEN}🎉 Development servers started!${NC}"
    echo ""
    echo -e "${BLUE}   Frontend:${NC} http://localhost:3000"
    echo -e "${BLUE}   Backend API:${NC} http://localhost:8000"
    echo -e "${BLUE}   API Docs:${NC} http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}   Press Ctrl+C to stop all servers${NC}"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait

elif [ "$MODE" = "stop" ]; then
    echo -e "${BLUE}🛑 Stopping PitchCube...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Stopped${NC}"

else
    echo -e "${RED}❌ Unknown mode: $MODE${NC}"
    echo "Usage: ./start.sh [docker|dev|stop]"
    echo ""
    echo "  docker  - Start with Docker Compose (default)"
    echo "  dev     - Start in development mode"
    echo "  stop    - Stop all services"
    exit 1
fi
