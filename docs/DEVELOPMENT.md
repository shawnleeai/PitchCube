# DEVELOPMENT.md

# PitchCube Development Guide

## Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **MongoDB** 5.0+ (database)
- **Redis** 6.0+ (cache)
- **Git** (version control)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pitchcube.git
cd pitchcube/pitchcube-new
```

#### 2. Setup Environment Files

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

Edit the `.env` files and add your configuration (API keys, etc.)

#### 3. Install Dependencies

Using Make (recommended):
```bash
make install
```

Or manually:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### 4. Start Development Servers

Using Make:
```bash
make dev
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Your application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Workflow

### Branch Strategy

We follow the **Git Flow** branching model:

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   make test
   make lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Code Style

### Python (Backend)

We use:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting

Format your code:
```bash
cd backend
black app/ --line-length=100
isort app/ --profile=black --line-length=100
flake8 app/ --max-line-length=100
```

Or use Make:
```bash
make format
```

#### Python Style Guidelines

- Maximum line length: 100 characters
- Use type hints for function parameters and returns
- Write docstrings for all public functions
- Use async/await for I/O operations
- Handle exceptions appropriately

Example:
```python
async def create_product(
    name: str,
    description: str,
    github_url: Optional[str] = None
) -> Product:
    """Create a new product.
    
    Args:
        name: Product name
        description: Product description
        github_url: Optional GitHub repository URL
        
    Returns:
        Created product object
        
    Raises:
        ValueError: If product name is empty
    """
    if not name:
        raise ValueError("Product name cannot be empty")
    
    product = Product(name=name, description=description)
    # ... save to database
    return product
```

### TypeScript/JavaScript (Frontend)

We use:
- **ESLint** for linting
- **Prettier** for formatting
- **TypeScript** for type safety

Format your code:
```bash
cd frontend
npm run lint
npm run format
```

#### Frontend Style Guidelines

- Use functional components with hooks
- Use TypeScript for type safety
- Follow React best practices
- Use Tailwind CSS for styling
- Keep components small and focused

Example:
```typescript
interface ProductCardProps {
  product: Product;
  onSelect: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onSelect,
}) => {
  return (
    <div
      className="p-4 bg-white rounded-lg shadow-md cursor-pointer"
      onClick={() => onSelect(product)}
    >
      <h3 className="text-lg font-bold">{product.name}</h3>
      <p className="text-gray-600">{product.description}</p>
    </div>
  );
};
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run with coverage
make test-coverage

# Run frontend tests
make test-frontend
```

### Writing Tests

#### Backend Tests

We use **pytest** for testing.

```python
# tests/integration/test_api/test_auth.py
import pytest

@pytest.mark.asyncio
async def test_login_success(client):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Frontend Tests

We use **Jest** and **React Testing Library**.

```typescript
// components/__tests__/ProductCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '../ProductCard';

describe('ProductCard', () => {
  it('renders product information', () => {
    const product = { name: 'Test Product', description: 'A test' };
    render(<ProductCard product={product} onSelect={jest.fn()} />);
    
    expect(screen.getByText('Test Product')).toBeInTheDocument();
  });
});
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality.

### Setup

```bash
pip install pre-commit
pre-commit install
```

### Run manually

```bash
pre-commit run --all-files
```

## Docker Development

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Individual Services

```bash
# Backend only
docker-compose up -d backend

# Frontend only
docker-compose up -d frontend

# Database only
docker-compose up -d mongo redis
```

## API Development

### Adding a New Endpoint

1. Create or update the router file in `backend/app/api/v1/`
2. Define request/response models using Pydantic
3. Implement the endpoint function
4. Add the router to `backend/app/api/v1/__init__.py`
5. Write tests for the endpoint
6. Update API documentation

Example:
```python
# backend/app/api/v1/products.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: str

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    """Create a new product."""
    # Implementation
    pass
```

## Database

### MongoDB

We use Motor for async MongoDB operations.

```python
from app.db.mongodb import db

# Insert
await db.products.insert_one(product_data)

# Find
product = await db.products.find_one({"_id": product_id})

# Update
await db.products.update_one(
    {"_id": product_id},
    {"$set": {"name": new_name}}
)
```

### Redis

We use Redis for caching and session storage.

```python
from app.db.redis import redis_client

# Set cache
await redis_client.setex(
    f"product:{product_id}",
    3600,  # TTL in seconds
    json.dumps(product_data)
)

# Get cache
cached = await redis_client.get(f"product:{product_id}")
```

## Debugging

### Backend Debugging

Using VS Code:
1. Add breakpoints in your code
2. Run the "Python: FastAPI" debug configuration
3. Use the Debug Console to inspect variables

Using print statements (not recommended for production):
```python
from app.core.logging import logger

logger.debug("Debug message: %s", variable)
logger.info("Information message")
logger.error("Error message")
```

### Frontend Debugging

- Use Chrome DevTools or Firefox Developer Tools
- React DevTools extension
- Redux DevTools (if using Redux)
- Console logging: `console.log()`, `console.error()`

## Troubleshooting

### Common Issues

#### Backend won't start

1. Check if ports are available:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

2. Verify MongoDB and Redis are running:
   ```bash
   docker-compose ps
   ```

3. Check environment variables:
   ```bash
   cat backend/.env
   ```

#### Frontend build fails

1. Clear node_modules:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   ```

2. Check Node.js version:
   ```bash
   node --version  # Should be 18+
   ```

#### Tests fail

1. Check if test database is configured
2. Verify test fixtures are loaded
3. Run with verbose output:
   ```bash
   pytest tests/ -v --tb=long
   ```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)

## Getting Help

- Check existing [Issues](https://github.com/yourusername/pitchcube/issues)
- Join our [Discord/Slack] community
- Email: support@pitchcube.ai

---

Happy coding! 🚀
