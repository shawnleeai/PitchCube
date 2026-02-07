#!/bin/bash

# PitchCube Setup Script
# Run this script to set up the development environment

set -e

echo "🎲 Setting up PitchCube..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version must be 18 or higher. Current: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node -v)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker is not installed. Docker is required for production deployment.${NC}"
else
    echo -e "${GREEN}✅ Docker $(docker --version)${NC}"
fi

# Create .env file
echo ""
echo -e "${BLUE}📝 Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    
    # Generate random keys
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -base64 32)
        MONGO_PASS=$(openssl rand -base64 12)
        
        sed -i.bak "s/change-this-to-a-random_32_char_string/$JWT_SECRET/g" .env
        sed -i.bak "s/secure_password_here/$MONGO_PASS/g" .env
        rm -f .env.bak
        
        echo -e "${GREEN}✅ Generated secure keys${NC}"
    fi
    
    echo -e "${YELLOW}⚠️  Please edit .env file to add your API keys (optional)${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Setup frontend
echo ""
echo -e "${BLUE}📦 Setting up frontend...${NC}"
cd frontend
npm install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
cd ..

# Setup backend
echo ""
echo -e "${BLUE}🐍 Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Created Python virtual environment${NC}"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

cd ..

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p uploads generated logs
echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo -e "${BLUE}  1. Start with Docker (recommended):${NC}"
echo "     ./scripts/start.sh docker"
echo ""
echo -e "${BLUE}  2. Or start in development mode:${NC}"
echo "     ./scripts/start.sh dev"
echo ""
echo -e "${BLUE}  3. Then open:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}  Note: Edit .env file to configure API keys for AI features${NC}"
