# ARCHITECTURE.md

# PitchCube System Architecture

## Overview

PitchCube is an AI-driven presentation platform that helps developers and startups create stunning pitch decks, promotional videos, and marketing materials from GitHub repositories or manual input.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web App    │  │  Mobile App  │  │   API Client │      │
│  │  (Next.js)   │  │   (Future)   │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                      │
│                    (FastAPI Application)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   REST API   │  │   WebSocket  │  │   Swagger    │      │
│  │              │  │              │  │    Docs      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ AI Services  │  │   Product    │  │    Media     │      │
│  │  (Manager)   │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Poster     │  │    Video     │  │    Voice     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Provider Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    OpenAI    │  │   StepFun    │  │    Minimax   │      │
│  │  (GPT-4)     │  │  (Chinese)   │  │  (Chinese)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Stability  │  │   Replicate  │  │    Azure     │      │
│  │  (Images)    │  │  (Video)     │  │  (Speech)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MongoDB    │  │    Redis     │  │  File Store  │      │
│  │  (Primary)   │  │   (Cache)    │  │ (Generated)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks + Context
- **Build Tool**: Next.js built-in

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **ASGI Server**: Uvicorn

### Database & Storage
- **Primary Database**: MongoDB (async via Motor)
- **Cache**: Redis
- **File Storage**: Local filesystem (with cloud storage option)

### AI Services
- **Text Generation**: OpenAI GPT-4, StepFun (Chinese)
- **Image Generation**: Stability AI, OpenAI DALL-E, StepFun
- **Video Generation**: Replicate, Runway ML
- **Voice Synthesis**: StepFun TTS, Minimax TTS, Azure Speech

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Code Quality**: Black, Flake8, Prettier, ESLint

## Module Details

### Frontend Architecture

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Landing page
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
│   ├── generate/          # Generation pages
│   ├── dashboard/         # User dashboard
│   └── api/              # API routes
├── components/            # React components
│   ├── ui/               # UI components
│   ├── forms/            # Form components
│   └── layout/           # Layout components
├── lib/                  # Utility functions
├── hooks/                # Custom React hooks
└── public/               # Static assets
```

**Key Features**:
- Server-side rendering (SSR) for SEO
- Client-side interactivity
- Responsive design
- Dark mode support

### Backend Architecture

```
backend/
├── app/
│   ├── main.py           # Application entry point
│   ├── core/             # Core configuration
│   │   ├── config.py    # Settings
│   │   ├── logging.py   # Logging setup
│   │   └── exceptions.py # Custom exceptions
│   ├── api/             # API layer
│   │   └── v1/         # API version 1
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── posters.py
│   │       ├── videos.py
│   │       └── ...
│   ├── services/        # Business logic
│   │   ├── ai_service_manager.py
│   │   ├── openai_service.py
│   │   ├── stepfun_service.py
│   │   └── ...
│   ├── db/             # Database layer
│   │   ├── mongodb.py
│   │   └── redis.py
│   └── models/         # Data models (if using ORM)
└── tests/              # Test suite
```

**Key Features**:
- Dependency injection
- Async/await throughout
- Automatic API documentation
- CORS enabled
- Request validation via Pydantic

## Data Flow

### 1. Product Creation Flow

```
User Input → Frontend → API → Product Service → MongoDB
                ↓
         GitHub Parsing → AI Enhancement → Storage
```

### 2. Poster Generation Flow

```
Product Data → Poster Service → AI Service Manager
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
              Template +          AI Enhancement
              Product Info              ↓
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                    Poster Generation → Storage → Response
```

### 3. Video Generation Flow

```
Script/Images → Video Service → AI Providers
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
              StepFun LLM      Replicate API      Runway API
                    ↓                 ↓                 ↓
              Voice Synthesis    Video Gen         Video Gen
                    ↓                 ↓                 ↓
                    └─────────────────┴─────────────────┘
                                      ↓
                         Video Composition → Storage
```

## Security Considerations

### Authentication
- JWT-based authentication
- Token expiration and refresh
- Password hashing with bcrypt

### API Security
- Rate limiting (configurable)
- CORS configuration
- Input validation via Pydantic
- No sensitive data in logs

### Data Security
- Environment variables for secrets
- API keys stored securely
- No credentials in code repository

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- External session storage (Redis)
- Database sharding ready (MongoDB)

### Performance
- Redis caching layer
- Async I/O throughout
- CDN for static assets
- Lazy loading for heavy assets

### Resource Management
- Queue system for long-running tasks (future)
- Background job processing
- File cleanup automation

## Deployment Architecture

### Development
```
Local Machine
├── Frontend (localhost:3000)
├── Backend (localhost:8000)
├── MongoDB (localhost:27017)
└── Redis (localhost:6379)
```

### Production (Suggested)
```
Cloud Infrastructure
├── Load Balancer
├── Frontend (CDN/Edge)
├── API Servers (Auto-scaling)
├── MongoDB Cluster
└── Redis Cluster
```

## Future Enhancements

### Short Term
- [ ] Queue system for video generation
- [ ] WebSocket for real-time updates
- [ ] Advanced caching strategies
- [ ] Metrics and monitoring

### Long Term
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Multi-region support
- [ ] Mobile application

## Development Guidelines

### Code Organization
- Follow existing directory structure
- Keep services independent
- Use dependency injection
- Write tests for new features

### API Design
- RESTful principles
- Consistent naming conventions
- Comprehensive error handling
- Version your APIs

### Database
- Use indexes for frequently queried fields
- Implement proper data validation
- Regular backup strategy
- Migration scripts for schema changes

---

Last updated: 2026-02-05
