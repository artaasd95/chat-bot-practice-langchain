# Configuration Documentation

This document provides comprehensive information about configuring the LangGraph Chat Bot System.

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Configuration Files](#configuration-files)
4. [Service Configuration](#service-configuration)
5. [Database Configuration](#database-configuration)
6. [Security Configuration](#security-configuration)
7. [LLM Configuration](#llm-configuration)
8. [Frontend Configuration](#frontend-configuration)
9. [Docker Configuration](#docker-configuration)
10. [Environment-Specific Settings](#environment-specific-settings)
11. [Configuration Validation](#configuration-validation)
12. [Troubleshooting](#troubleshooting)

## Overview

The Chat Bot System uses a hierarchical configuration approach that supports:

- **Environment Variables**: Primary configuration method
- **Configuration Files**: Structured settings management
- **Default Values**: Fallback configuration
- **Environment-Specific Overrides**: Development, staging, production settings
- **Runtime Configuration**: Dynamic configuration updates

### Configuration Priority

1. **Environment Variables** (Highest priority)
2. **Configuration Files** (.env files)
3. **Default Values** (Lowest priority)

### Configuration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Environment     │    │ Configuration   │    │ Default         │
│ Variables       │───▶│ Merger          │◀───│ Values          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │ Application     │
                    │ Configuration   │
                    └─────────────────┘
```

## Environment Variables

### Core Application Settings

```bash
# API Configuration
API_V1_STR="/api/v1"
PROJECT_NAME="Chat Bot API"
VERSION="1.0.0"
DESCRIPTION="A chat bot API using LangChain and LangGraph"

# Server Configuration
HOST="0.0.0.0"
PORT=8000
WORKERS=1
RELOAD=false

# CORS Configuration
BACKEND_CORS_ORIGINS='["http://localhost:3000", "http://localhost:8080"]'
```

### Database Configuration

```bash
# Database Settings
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/chatbot"
DATABASE_ECHO=false
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD=""
REDIS_DB=0
REDIS_MAX_CONNECTIONS=20
```

### Authentication Configuration

```bash
# JWT Settings
SECRET_KEY="your-super-secret-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Settings
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true

# Admin Settings
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin123"
ADMIN_FIRST_NAME="Admin"
ADMIN_LAST_NAME="User"
```

### LLM Configuration

```bash
# OpenAI Configuration
OPENAI_API_KEY="sk-your-openai-api-key"
OPENAI_ORG_ID="org-your-organization-id"
LLM_MODEL="gpt-3.5-turbo"
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TOP_P=1.0
LLM_FREQUENCY_PENALTY=0.0
LLM_PRESENCE_PENALTY=0.0

# Alternative LLM Providers
ANTHROPIC_API_KEY="your-anthropic-api-key"
COHERE_API_KEY="your-cohere-api-key"
HUGGINGFACE_API_KEY="your-huggingface-api-key"

# LLM Behavior
LLM_TIMEOUT=30
LLM_RETRY_ATTEMPTS=3
LLM_RETRY_DELAY=2
LLM_MAX_CONCURRENT_REQUESTS=10
```

### Webhook Configuration

```bash
# Webhook Settings
WEBHOOK_SECRET="your-webhook-secret"
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=2
WEBHOOK_MAX_CONCURRENT=5

# Webhook Security
WEBHOOK_VERIFY_SSL=true
WEBHOOK_ALLOWED_HOSTS='["example.com", "api.example.com"]'
```

### Logging Configuration

```bash
# Logging Settings
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="logs/app.log"
LOG_MAX_SIZE="10MB"
LOG_BACKUP_COUNT=5
LOG_ROTATION="daily"

# Debug Settings
DEBUG=false
DEBUG_SQL=false
DEBUG_REQUESTS=false
```

### Monitoring Configuration

```bash
# Metrics Settings
METRICS_ENABLED=true
METRICS_PORT=9090
METRICS_PATH="/metrics"

# Health Check Settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PATH="/health"
HEALTH_CHECK_INTERVAL=30

# Tracing Settings
TRACING_ENABLED=true
TRACING_ENDPOINT="http://jaeger:14268/api/traces"
TRACING_SERVICE_NAME="chat-bot-api"

# LangSmith Settings
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=chatbot-microservices
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

#### LangSmith Configuration
LangSmith provides comprehensive tracing, monitoring, and evaluation for LangChain and LangGraph components:

- **LANGCHAIN_TRACING_V2**: Enable LangSmith tracing (true/false)
- **LANGCHAIN_API_KEY**: Your LangSmith API key (obtain from [LangSmith](https://smith.langchain.com))
- **LANGCHAIN_PROJECT**: Project name in LangSmith for organizing traces
- **LANGCHAIN_ENDPOINT**: LangSmith API endpoint (defaults to https://api.smith.langchain.com)

##### Benefits of LangSmith Integration

- **Tracing**: Visualize and debug LangGraph execution paths with detailed node-by-node analysis
- **Monitoring**: Track token usage, costs, and performance metrics across all LLM interactions
- **Debugging**: Identify bottlenecks, errors, and optimization opportunities in LLM interactions
- **Evaluation**: Compare different models, prompts, and graph configurations for quality and efficiency
- **Cost Analysis**: Monitor token usage and associated costs to optimize spending
- **A/B Testing**: Test different LLM configurations and graph structures side by side

LangSmith integration enables:
- **Detailed Visualization**: See the exact flow of data through your LangGraph nodes
- **Token Usage Tracking**: Monitor prompt and completion tokens for each LLM call
- **Performance Metrics**: Measure latency and throughput of each component
- **Error Analysis**: Quickly identify and debug failures in your LLM applications
- **Quality Assessment**: Evaluate LLM responses against ground truth or custom criteria
- **Historical Data**: Maintain a searchable history of all LLM interactions for analysis
- **Collaborative Development**: Share traces and evaluations with team members

## Configuration Files

### Main Configuration Class

```python
# app/config.py
from pydantic import BaseSettings, validator
from typing import List, Optional, Union
import json

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat Bot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A chat bot API using LangChain and LangGraph"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    @validator('BACKEND_CORS_ORIGINS', pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 20
    
    # Authentication Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    # Password Settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Admin Settings
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_FIRST_NAME: str = "Admin"
    ADMIN_LAST_NAME: str = "User"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    LLM_TOP_P: float = 1.0
    LLM_FREQUENCY_PENALTY: float = 0.0
    LLM_PRESENCE_PENALTY: float = 0.0
    LLM_TIMEOUT: int = 30
    LLM_RETRY_ATTEMPTS: int = 3
    LLM_RETRY_DELAY: int = 2
    LLM_MAX_CONCURRENT_REQUESTS: int = 10
    
    @validator('LLM_TEMPERATURE')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('LLM_TEMPERATURE must be between 0.0 and 2.0')
        return v
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v):
        if v and not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v
    
    # Webhook Settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_RETRY_DELAY: int = 2
    WEBHOOK_MAX_CONCURRENT: int = 5
    WEBHOOK_VERIFY_SSL: bool = True
    WEBHOOK_ALLOWED_HOSTS: Union[str, List[str]] = []
    
    @validator('WEBHOOK_ALLOWED_HOSTS', pre=True)
    def assemble_webhook_hosts(cls, v):
        if isinstance(v, str) and v:
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v or []
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    LOG_MAX_SIZE: str = "10MB"
    LOG_BACKUP_COUNT: int = 5
    LOG_ROTATION: str = "daily"
    DEBUG: bool = False
    DEBUG_SQL: bool = False
    DEBUG_REQUESTS: bool = False
    
    # Monitoring Settings
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_PATH: str = "/health"
    HEALTH_CHECK_INTERVAL: int = 30
    TRACING_ENABLED: bool = False
    TRACING_ENDPOINT: Optional[str] = None
    TRACING_SERVICE_NAME: str = "chat-bot-api"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

# Global settings instance
settings = Settings()
```

### Environment Files

#### Development Environment (.env.dev)

```bash
# Development Configuration
DEBUG=true
LOG_LEVEL="DEBUG"
RELOAD=true

# Database
DATABASE_URL="sqlite+aiosqlite:///./dev_chatbot.db"
DATABASE_ECHO=true

# Redis
REDIS_URL="redis://localhost:6379/1"

# LLM
LLM_MODEL="gpt-3.5-turbo"
LLM_TEMPERATURE=0.8

# CORS - Allow all origins in development
BACKEND_CORS_ORIGINS='["*"]'

# Webhooks - Disabled in development
WEBHOOK_VERIFY_SSL=false
```

#### Staging Environment (.env.staging)

```bash
# Staging Configuration
DEBUG=false
LOG_LEVEL="INFO"
RELOAD=false

# Database
DATABASE_URL="postgresql+asyncpg://user:password@staging-db:5432/chatbot_staging"
DATABASE_ECHO=false

# Redis
REDIS_URL="redis://staging-redis:6379/0"

# LLM
LLM_MODEL="gpt-3.5-turbo"
LLM_TEMPERATURE=0.7

# CORS - Specific origins
BACKEND_CORS_ORIGINS='["https://staging.example.com"]'

# Monitoring
METRICS_ENABLED=true
TRACING_ENABLED=true
```

#### Production Environment (.env.prod)

```bash
# Production Configuration
DEBUG=false
LOG_LEVEL="WARNING"
RELOAD=false
WORKERS=4

# Database
DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/chatbot_prod"
DATABASE_ECHO=false
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100

# Redis
REDIS_URL="redis://prod-redis:6379/0"
REDIS_MAX_CONNECTIONS=50

# LLM
LLM_MODEL="gpt-4"
LLM_TEMPERATURE=0.5
LLM_MAX_CONCURRENT_REQUESTS=20

# CORS - Production domains only
BACKEND_CORS_ORIGINS='["https://app.example.com", "https://api.example.com"]'

# Security
WEBHOOK_VERIFY_SSL=true
WEBHOOK_ALLOWED_HOSTS='["trusted-partner.com"]'

# Monitoring
METRICS_ENABLED=true
TRACING_ENABLED=true
TRACING_ENDPOINT="https://jaeger.example.com/api/traces"
```

## Service Configuration

### Auth Service Configuration

```python
# app/auth/config.py
from app.config import settings

class AuthConfig:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # Password policy
    PASSWORD_MIN_LENGTH = settings.PASSWORD_MIN_LENGTH
    PASSWORD_REQUIRE_UPPERCASE = settings.PASSWORD_REQUIRE_UPPERCASE
    PASSWORD_REQUIRE_LOWERCASE = settings.PASSWORD_REQUIRE_LOWERCASE
    PASSWORD_REQUIRE_NUMBERS = settings.PASSWORD_REQUIRE_NUMBERS
    PASSWORD_REQUIRE_SPECIAL = settings.PASSWORD_REQUIRE_SPECIAL
    
    # Rate limiting
    LOGIN_RATE_LIMIT = "5/minute"
    REGISTER_RATE_LIMIT = "3/minute"
    PASSWORD_RESET_RATE_LIMIT = "2/hour"
```

### Chat Service Configuration

```python
# app/chat/config.py
from app.config import settings

class ChatConfig:
    # LLM Settings
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    LLM_MODEL = settings.LLM_MODEL
    LLM_TEMPERATURE = settings.LLM_TEMPERATURE
    LLM_MAX_TOKENS = settings.LLM_MAX_TOKENS
    LLM_TIMEOUT = settings.LLM_TIMEOUT
    LLM_RETRY_ATTEMPTS = settings.LLM_RETRY_ATTEMPTS
    
    # Chat Settings
    MAX_MESSAGE_LENGTH = 4000
    MAX_CONVERSATION_LENGTH = 50
    CONVERSATION_TIMEOUT = 3600  # 1 hour
    
    # Rate limiting
    CHAT_RATE_LIMIT = "10/minute"
    STREAMING_RATE_LIMIT = "5/minute"
```

### Admin Service Configuration

```python
# app/admin/config.py
from app.config import settings

class AdminConfig:
    # Admin user settings
    ADMIN_EMAIL = settings.ADMIN_EMAIL
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    ADMIN_FIRST_NAME = settings.ADMIN_FIRST_NAME
    ADMIN_LAST_NAME = settings.ADMIN_LAST_NAME
    
    # Admin permissions
    ADMIN_PERMISSIONS = [
        "users:read",
        "users:write",
        "users:delete",
        "chats:read",
        "chats:delete",
        "analytics:read",
        "system:read",
        "system:write"
    ]
    
    # Rate limiting
    ADMIN_RATE_LIMIT = "100/minute"
```

## Database Configuration

### SQLAlchemy Configuration

```python
# app/database/config.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Engine configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,  # Validate connections
    connect_args={
        "server_settings": {
            "application_name": settings.PROJECT_NAME,
        }
    } if "postgresql" in settings.DATABASE_URL else {}
)

# Session configuration
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Redis Configuration

```python
# app/cache/config.py
import redis.asyncio as redis
from app.config import settings

# Redis connection
redis_client = redis.from_url(
    settings.REDIS_URL,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    retry_on_timeout=True,
    health_check_interval=30
)

# Cache configuration
class CacheConfig:
    DEFAULT_TTL = 3600  # 1 hour
    SESSION_TTL = 86400  # 24 hours
    USER_TTL = 1800  # 30 minutes
    CHAT_TTL = 7200  # 2 hours
    
    # Key prefixes
    SESSION_PREFIX = "session:"
    USER_PREFIX = "user:"
    CHAT_PREFIX = "chat:"
    RATE_LIMIT_PREFIX = "rate_limit:"
```

## Security Configuration

### JWT Configuration

```python
# app/auth/jwt_config.py
from datetime import timedelta
from app.config import settings

class JWTConfig:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # Token settings
    ISSUER = settings.PROJECT_NAME
    AUDIENCE = "chat-bot-users"
    
    # Security settings
    REQUIRE_HTTPS = not settings.DEBUG
    SECURE_COOKIES = not settings.DEBUG
    SAME_SITE = "strict" if not settings.DEBUG else "lax"
```

### CORS Configuration

```python
# app/middleware/cors_config.py
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

def configure_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-Request-ID"
        ],
        expose_headers=["X-Request-ID"],
        max_age=86400  # 24 hours
    )
```

### Rate Limiting Configuration

```python
# app/middleware/rate_limit_config.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiter configuration
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["1000/hour"],
    headers_enabled=True
)

# Rate limit rules
RATE_LIMITS = {
    "auth": {
        "login": "5/minute",
        "register": "3/minute",
        "password_reset": "2/hour"
    },
    "chat": {
        "message": "10/minute",
        "streaming": "5/minute"
    },
    "admin": {
        "general": "100/minute"
    }
}
```

## LLM Configuration

### OpenAI Configuration

```python
# app/llm/openai_config.py
from langchain_openai import ChatOpenAI
from app.config import settings

def create_openai_llm():
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        top_p=settings.LLM_TOP_P,
        frequency_penalty=settings.LLM_FREQUENCY_PENALTY,
        presence_penalty=settings.LLM_PRESENCE_PENALTY,
        api_key=settings.OPENAI_API_KEY,
        organization=settings.OPENAI_ORG_ID,
        timeout=settings.LLM_TIMEOUT,
        max_retries=settings.LLM_RETRY_ATTEMPTS
    )
```

### Model Configuration

```python
# app/llm/model_config.py
from typing import Dict, Any
from app.config import settings

MODEL_CONFIGS = {
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "context_window": 4096,
        "cost_per_1k_tokens": 0.002,
        "supports_functions": True,
        "supports_streaming": True
    },
    "gpt-4": {
        "max_tokens": 8192,
        "context_window": 8192,
        "cost_per_1k_tokens": 0.03,
        "supports_functions": True,
        "supports_streaming": True
    },
    "gpt-4-turbo": {
        "max_tokens": 4096,
        "context_window": 128000,
        "cost_per_1k_tokens": 0.01,
        "supports_functions": True,
        "supports_streaming": True
    }
}

def get_model_config(model_name: str) -> Dict[str, Any]:
    return MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["gpt-3.5-turbo"])
```

## Frontend Configuration

### Vite Configuration

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: process.env.NODE_ENV === 'production',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['@headlessui/vue', '@heroicons/vue']
        }
      }
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  }
})
```

### Environment Configuration

```bash
# frontend/.env.development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_TITLE="Chat Bot - Development"
VITE_DEBUG=true
VITE_LOG_LEVEL=debug

# frontend/.env.production
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
VITE_APP_TITLE="Chat Bot"
VITE_DEBUG=false
VITE_LOG_LEVEL=error
```

### TypeScript Configuration

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## Docker Configuration

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-chatbot}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Auth Service
  auth-service:
    build:
      context: .
      dockerfile: auth.Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/chatbot
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Chat Service
  chat-service:
    build:
      context: .
      dockerfile: chat.Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/chatbot
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    ports:
      - "8002:8002"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Admin Service
  admin-service:
    build:
      context: .
      dockerfile: admin.Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/chatbot
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    ports:
      - "8003:8003"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=http://localhost:8080
    ports:
      - "3000:3000"
    depends_on:
      - auth-service
      - chat-service
      - admin-service

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "8080:80"
    depends_on:
      - auth-service
      - chat-service
      - admin-service
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### Environment-Specific Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  auth-service:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    volumes:
      - ./app:/app/app:ro

  chat-service:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    volumes:
      - ./app:/app/app:ro

  admin-service:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    volumes:
      - ./app:/app/app:ro

  frontend:
    command: npm run dev
    volumes:
      - ./frontend/src:/app/src:ro
      - ./frontend/public:/app/public:ro
```

## Environment-Specific Settings

### Development Settings

```python
# config/development.py
from app.config import Settings

class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    RELOAD: bool = True
    
    # Database
    DATABASE_ECHO: bool = True
    
    # CORS - Allow all origins
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Security - Relaxed for development
    WEBHOOK_VERIFY_SSL: bool = False
    
    # LLM - More creative responses
    LLM_TEMPERATURE: float = 0.8
    
    class Config:
        env_file = ".env.dev"
```

### Production Settings

```python
# config/production.py
from app.config import Settings

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    RELOAD: bool = False
    WORKERS: int = 4
    
    # Database - Optimized for production
    DATABASE_POOL_SIZE: int = 50
    DATABASE_MAX_OVERFLOW: int = 100
    
    # Security - Strict settings
    WEBHOOK_VERIFY_SSL: bool = True
    
    # LLM - Conservative settings
    LLM_TEMPERATURE: float = 0.5
    LLM_MAX_CONCURRENT_REQUESTS: int = 20
    
    class Config:
        env_file = ".env.prod"
```

## Configuration Validation

### Validation Functions

```python
# app/config/validation.py
from typing import List, Dict, Any
from app.config import settings
import re

def validate_configuration() -> List[Dict[str, Any]]:
    """Validate configuration settings."""
    errors = []
    
    # Validate required settings
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        errors.append({
            "field": "SECRET_KEY",
            "error": "SECRET_KEY must be at least 32 characters long"
        })
    
    if not settings.OPENAI_API_KEY:
        errors.append({
            "field": "OPENAI_API_KEY",
            "error": "OPENAI_API_KEY is required"
        })
    
    # Validate database URL
    if not settings.DATABASE_URL:
        errors.append({
            "field": "DATABASE_URL",
            "error": "DATABASE_URL is required"
        })
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, settings.ADMIN_EMAIL):
        errors.append({
            "field": "ADMIN_EMAIL",
            "error": "Invalid email format"
        })
    
    # Validate LLM settings
    if not 0.0 <= settings.LLM_TEMPERATURE <= 2.0:
        errors.append({
            "field": "LLM_TEMPERATURE",
            "error": "LLM_TEMPERATURE must be between 0.0 and 2.0"
        })
    
    return errors

def validate_environment() -> bool:
    """Validate environment configuration."""
    errors = validate_configuration()
    
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  {error['field']}: {error['error']}")
        return False
    
    print("Configuration validation passed")
    return True
```

### Startup Validation

```python
# app/main.py
from app.config.validation import validate_environment

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not validate_environment():
        raise RuntimeError("Configuration validation failed")
    
    yield
    
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)
```

## Troubleshooting

### Common Configuration Issues

#### Issue: "Configuration validation failed"

**Symptoms**: Application fails to start with validation errors

**Solutions**:
1. Check environment variables are set correctly
2. Verify .env file exists and is readable
3. Ensure required fields have valid values
4. Check file permissions on configuration files

#### Issue: "Database connection failed"

**Symptoms**: Cannot connect to database

**Solutions**:
1. Verify DATABASE_URL format
2. Check database server is running
3. Verify credentials and permissions
4. Test network connectivity

#### Issue: "OpenAI API authentication failed"

**Symptoms**: LLM requests fail with authentication errors

**Solutions**:
1. Verify OPENAI_API_KEY is correct
2. Check API key permissions
3. Ensure API key is not expired
4. Verify organization ID if using

#### Issue: "CORS errors in frontend"

**Symptoms**: Frontend cannot access API

**Solutions**:
1. Check BACKEND_CORS_ORIGINS setting
2. Verify frontend URL is included
3. Check for typos in origins list
4. Ensure proper JSON format for list

### Configuration Debugging

```python
# app/config/debug.py
from app.config import settings
import json

def print_configuration():
    """Print current configuration (excluding secrets)."""
    config_dict = settings.dict()
    
    # Mask sensitive values
    sensitive_keys = [
        'SECRET_KEY', 'OPENAI_API_KEY', 'ADMIN_PASSWORD',
        'DATABASE_URL', 'WEBHOOK_SECRET'
    ]
    
    for key in sensitive_keys:
        if key in config_dict and config_dict[key]:
            config_dict[key] = "***MASKED***"
    
    print("Current Configuration:")
    print(json.dumps(config_dict, indent=2, default=str))

def check_environment_variables():
    """Check which environment variables are set."""
    import os
    
    required_vars = [
        'SECRET_KEY', 'OPENAI_API_KEY', 'DATABASE_URL',
        'ADMIN_EMAIL', 'ADMIN_PASSWORD'
    ]
    
    print("Environment Variables Status:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✓ SET" if value else "✗ NOT SET"
        print(f"  {var}: {status}")
```

### Health Check Configuration

```python
# app/health/config.py
from fastapi import APIRouter
from app.config import settings
from app.config.validation import validate_configuration

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    errors = validate_configuration()
    
    return {
        "status": "healthy" if not errors else "unhealthy",
        "version": settings.VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "configuration_errors": errors
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with configuration status."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "configuration": {
            "database_configured": bool(settings.DATABASE_URL),
            "redis_configured": bool(settings.REDIS_URL),
            "llm_configured": bool(settings.OPENAI_API_KEY),
            "admin_configured": bool(settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD)
        },
        "features": {
            "webhooks_enabled": bool(settings.WEBHOOK_SECRET),
            "metrics_enabled": settings.METRICS_ENABLED,
            "tracing_enabled": settings.TRACING_ENABLED
        }
    }
```

This configuration documentation provides comprehensive guidance for setting up and managing the Chat Bot System across different environments. For additional support, refer to the deployment documentation or contact the development team.