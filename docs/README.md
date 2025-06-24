# Chat Bot System Documentation

A comprehensive documentation for the LangGraph-based Chat Bot System with microservices architecture.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Services](#services)
- [Frontend Application](#frontend-application)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development Guide](#development-guide)

## Project Overview

The Chat Bot System is a scalable, microservices-based application built with FastAPI, Vue.js, and LangGraph. It provides a complete chat bot solution with user authentication, real-time messaging, admin management, and AI-powered responses using Large Language Models.

### Key Features

- **Microservices Architecture**: Separate services for authentication, chat, and administration
- **Real-time Chat**: WebSocket-based real-time messaging
- **AI Integration**: LangGraph-powered conversation flows with LLM integration
- **User Management**: Complete authentication and authorization system
- **Admin Panel**: Comprehensive administrative interface
- **Responsive Frontend**: Modern Vue.js application with Tailwind CSS
- **Containerized Deployment**: Docker-based deployment with nginx load balancing

### Technology Stack

#### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **PostgreSQL**: Primary database for data persistence
- **Redis**: Caching and session management
- **Pydantic**: Data validation using Python type annotations

#### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Pinia**: State management for Vue.js
- **Vue Router**: Official router for Vue.js
- **Tailwind CSS**: Utility-first CSS framework
- **Headless UI**: Unstyled, accessible UI components
- **Heroicons**: Beautiful hand-crafted SVG icons

#### Infrastructure
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container Docker applications
- **Nginx**: Web server and reverse proxy
- **PostgreSQL**: Relational database
- **Redis**: In-memory data structure store

## Architecture

The system follows a microservices architecture pattern with the following components:

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Nginx       │
│   (Vue.js)      │◄──►│  Load Balancer  │
│   Port: 3000    │    │   Port: 80      │
└─────────────────┘    └─────────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──────┐ ┌───▼────┐ ┌────▼─────┐
            │ Auth Service │ │ Chat   │ │  Admin   │
            │ Port: 8001   │ │Service │ │ Service  │
            │              │ │Port:   │ │ Port:    │
            │              │ │8002    │ │ 8003     │
            └──────┬───────┘ └───┬────┘ └────┬─────┘
                   │             │           │
                   └─────────────┼───────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     PostgreSQL          │
                    │     Port: 5432          │
                    └─────────────────────────┘
                    ┌─────────────────────────┐
                    │       Redis             │
                    │     Port: 6379          │
                    └─────────────────────────┘
```

### Service Communication

- **Frontend ↔ Nginx**: HTTP/HTTPS requests
- **Nginx ↔ Services**: HTTP reverse proxy
- **Services ↔ Database**: Async PostgreSQL connections
- **Services ↔ Redis**: Caching and session storage
- **Inter-service**: HTTP API calls when needed

## Services

### 1. Authentication Service (Port 8001)

**Responsibilities:**
- User registration and login
- JWT token management
- Password operations
- User profile management
- Role-based access control

**Key Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Get current user profile
- `PUT /auth/profile` - Update user profile

### 2. Chat Service (Port 8002)

**Responsibilities:**
- Chat session management
- Message processing
- LangGraph integration
- Real-time WebSocket connections
- Conversation history

**Key Endpoints:**
- `POST /chat/sessions` - Create chat session
- `GET /chat/sessions` - List user sessions
- `POST /chat/message` - Send message
- `WS /chat/ws/{session_id}` - WebSocket connection

### 3. Admin Service (Port 8003)

**Responsibilities:**
- User management
- Chat session monitoring
- System analytics
- Administrative operations
- System configuration

**Key Endpoints:**
- `GET /admin/users` - List all users
- `PUT /admin/users/{id}` - Update user
- `GET /admin/chats` - Monitor chat sessions
- `GET /admin/analytics` - System analytics

## Frontend Application

The Vue.js frontend provides a modern, responsive user interface with the following key features:

### Components Structure

```
src/
├── components/
│   └── Layout/
│       └── MainLayout.vue     # Main application layout
├── views/
│   ├── Auth/                  # Authentication pages
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   └── ForgotPasswordView.vue
│   ├── Admin/                 # Admin panel pages
│   │   ├── AdminDashboard.vue
│   │   ├── AdminUsers.vue
│   │   ├── AdminChats.vue
│   │   └── AdminSettings.vue
│   ├── ChatView.vue           # Main chat interface
│   ├── DashboardView.vue      # User dashboard
│   └── ProfileView.vue        # User profile management
├── stores/                    # Pinia state management
│   ├── auth.js               # Authentication state
│   ├── chat.js               # Chat state
│   ├── admin.js              # Admin state
│   └── theme.js              # Theme management
├── services/
│   └── api.js                # API service layer
└── router/
    └── index.js              # Vue Router configuration
```

### State Management

The application uses Pinia for state management with the following stores:

- **Auth Store**: Manages user authentication, login state, and user profile
- **Chat Store**: Handles chat sessions, messages, and WebSocket connections
- **Admin Store**: Manages administrative data and operations
- **Theme Store**: Controls dark/light theme preferences

## Database Schema

The system uses PostgreSQL with the following main entities:

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    avatar_url VARCHAR(500),
    bio TEXT,
    phone VARCHAR(20)
);
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    session_id INTEGER REFERENCES chat_sessions(id),
    message_type VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata TEXT, -- JSON string for additional data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Documentation

Detailed API documentation for each service:

- [Authentication API](./api/auth-api.md)
- [Chat API](./api/chat-api.md)
- [Admin API](./api/admin-api.md)

## Deployment

### Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd chat-bot-practice-langchain

# Start development environment
make dev

# Or using docker-compose directly
docker-compose -f docker-compose.dev.yml up
```

### Production Environment

```bash
# Build and start production environment
make prod

# Or using docker-compose directly
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot

# Authentication
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Integration
OPENAI_API_KEY=your-openai-api-key
MODEL_NAME=gpt-3.5-turbo

# Redis
REDIS_URL=redis://localhost:6379
```

## Development Guide

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for backend development)

### Local Development Setup

1. **Backend Development**:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run individual services
   uvicorn app.auth_main:app --reload --port 8001
   uvicorn app.chat_main:app --reload --port 8002
   uvicorn app.admin_main:app --reload --port 8003
   ```

2. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Setup**:
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up postgres redis
   
   # Run database migrations
   alembic upgrade head
   ```

### Testing

```bash
# Run all tests
make test

# Run specific service tests
docker-compose exec auth-service pytest
docker-compose exec chat-service pytest
docker-compose exec admin-service pytest
```

### Monitoring and Logs

```bash
# View all service logs
make logs

# View specific service logs
make logs-auth
make logs-chat
make logs-admin

# Check service health
make health
```

## Additional Documentation

- [Frontend Components Guide](./frontend/components.md)
- [Backend Services Guide](./backend/services.md)
- [Database Design](./database/schema.md)
- [Deployment Guide](./deployment/guide.md)
- [API Reference](./api/reference.md)
- [Contributing Guidelines](./contributing.md)