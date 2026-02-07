.PHONY: help install dev test lint format clean build docker-up docker-down

help:
	@echo "PitchCube Development Commands"
	@echo "=============================="
	@echo "  make install       Install all dependencies"
	@echo "  make dev           Start development servers"
	@echo "  make dev-backend   Start backend development server"
	@echo "  make dev-frontend  Start frontend development server"
	@echo "  make test          Run all tests"
	@echo "  make test-backend  Run backend tests"
	@echo "  make test-frontend Run frontend tests"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code"
	@echo "  make clean         Clean generated files"
	@echo "  make build         Build for production"
	@echo "  make docker-up     Start Docker containers"
	@echo "  make docker-down   Stop Docker containers"
	@echo ""

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	make dev-backend & make dev-frontend

dev-backend:
	@echo "Starting backend server on http://localhost:8000"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend server on http://localhost:3000"
	cd frontend && npm run dev

test:
	make test-backend

test-backend:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v --tb=short

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

test-coverage:
	cd backend && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:
	@echo "Linting backend..."
	cd backend && flake8 app --count --statistics --max-line-length=100
	@echo "Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend code..."
	cd backend && black app/ --line-length=100
	cd backend && isort app/ --profile=black --line-length=100
	@echo "Formatting frontend code..."
	cd frontend && npm run format

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	rm -rf backend/generated/* 2>/dev/null || true
	@echo "Cleanup complete!"

build:
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build complete!"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-build:
	@echo "Building Docker images..."
	docker-compose build

setup:
	@echo "Setting up development environment..."
	cp backend/.env.example backend/.env
	cp frontend/.env.local.example frontend/.env.local 2>/dev/null || true
	make install
	@echo "Setup complete! Please configure your .env files."
