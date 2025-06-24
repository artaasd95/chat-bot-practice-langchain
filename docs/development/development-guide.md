# Development Guide

This guide provides comprehensive instructions for developers working on the LangGraph Chat Bot System.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Contributing](#contributing)
8. [Best Practices](#best-practices)

## Development Environment Setup

### Prerequisites

- **Python 3.11+**: Latest stable version recommended
- **Node.js 18+**: For frontend development
- **Docker & Docker Compose**: For containerized development
- **Git**: Version control
- **IDE**: VS Code, PyCharm, or similar with Python support

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd chat-bot-practice-langchain
```

#### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
# or
yarn install
```

#### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY
# - OPENAI_API_KEY
```

#### 5. Database Setup

```bash
# Start database services
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# (Optional) Seed database with test data
python scripts/seed_database.py
```

#### 6. Start Development Services

```bash
# Terminal 1: Auth Service
uvicorn app.auth_main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Chat Service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3: Admin Service
uvicorn app.admin_main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 4: Frontend
cd frontend
npm run dev
```

### Docker Development Setup

```bash
# Start all services with Docker Compose
make dev-up
# or
docker-compose -f docker-compose.dev.yml up -d

# View logs
make dev-logs
# or
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
make dev-down
# or
docker-compose -f docker-compose.dev.yml down
```

### IDE Configuration

#### VS Code Settings

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true,
    "**/.pytest_cache": true
  }
}
```

#### VS Code Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "vue.volar",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode-remote.remote-containers",
    "redhat.vscode-yaml",
    "ms-kubernetes-tools.vscode-kubernetes-tools"
  ]
}
```

## Project Structure

### Backend Structure

```
app/
├── main.py                    # Chat service entry point
├── auth_main.py              # Auth service entry point
├── admin_main.py             # Admin service entry point
├── config.py                 # Configuration management
├── database/                 # Database layer
│   ├── __init__.py
│   ├── connection.py         # Database connection
│   ├── models.py            # SQLAlchemy models
│   └── migrations/          # Alembic migrations
├── auth/                    # Authentication module
│   ├── __init__.py
│   ├── routes.py           # Auth API routes
│   ├── models.py           # Auth Pydantic models
│   ├── services.py         # Auth business logic
│   └── utils.py            # Auth utilities
├── api/                     # Chat API module
│   ├── __init__.py
│   ├── routes.py           # Chat API routes
│   ├── models.py           # API Pydantic models
│   └── dependencies.py     # FastAPI dependencies
├── admin/                   # Admin module
│   ├── __init__.py
│   ├── routes.py           # Admin API routes
│   ├── services.py         # Admin business logic
│   └── analytics.py        # Analytics functions
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── llm.py              # LLM integration
│   ├── chat.py             # Chat service logic
│   ├── user.py             # User management
│   └── cache.py            # Redis caching
├── graph/                   # LangGraph implementation
│   ├── __init__.py
│   ├── builder.py          # Graph construction
│   ├── nodes.py            # Graph nodes
│   ├── edges.py            # Graph edges
│   └── state.py            # Graph state
├── core/                    # Core utilities
│   ├── __init__.py
│   ├── security.py         # Security utilities
│   ├── exceptions.py       # Custom exceptions
│   ├── middleware.py       # Custom middleware
│   └── logging.py          # Logging configuration
└── utils/                   # General utilities
    ├── __init__.py
    ├── helpers.py          # Helper functions
    └── validators.py       # Custom validators
```

### Frontend Structure

```
frontend/
├── public/                  # Static assets
├── src/
│   ├── components/         # Vue components
│   │   ├── layout/        # Layout components
│   │   ├── chat/          # Chat components
│   │   ├── auth/          # Authentication components
│   │   ├── admin/         # Admin components
│   │   └── common/        # Shared components
│   ├── views/             # Page components
│   │   ├── Auth/          # Authentication pages
│   │   ├── Admin/         # Admin pages
│   │   └── Chat/          # Chat pages
│   ├── router/            # Vue Router configuration
│   ├── stores/            # Pinia stores
│   ├── services/          # API services
│   ├── types/             # TypeScript types
│   ├── utils/             # Utility functions
│   ├── styles/            # Global styles
│   ├── App.vue            # Root component
│   └── main.ts            # Application entry point
├── package.json           # Dependencies
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## Development Workflow

### Git Workflow

#### Branch Naming Convention

- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes
- `refactor/component-name`: Code refactoring
- `docs/documentation-update`: Documentation updates

#### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add password reset functionality
fix(chat): resolve message ordering issue
docs(api): update authentication endpoints
refactor(database): optimize query performance
```

#### Pull Request Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes and Commit**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Push Branch**:
   ```bash
   git push origin feature/new-feature
   ```

4. **Create Pull Request**:
   - Use the PR template
   - Add appropriate labels
   - Request reviews from team members
   - Ensure CI/CD checks pass

5. **Code Review**:
   - Address review comments
   - Update documentation if needed
   - Ensure tests pass

6. **Merge**:
   - Use "Squash and merge" for feature branches
   - Delete branch after merge

### Development Tasks

#### Adding New API Endpoints

1. **Define Pydantic Models**:
   ```python
   # app/api/models.py
   from pydantic import BaseModel
   from typing import Optional
   
   class NewFeatureRequest(BaseModel):
       name: str
       description: Optional[str] = None
   
   class NewFeatureResponse(BaseModel):
       id: int
       name: str
       description: Optional[str]
       created_at: datetime
   ```

2. **Create Database Model** (if needed):
   ```python
   # app/database/models.py
   from sqlalchemy import Column, Integer, String, DateTime, Text
   from sqlalchemy.sql import func
   from .connection import Base
   
   class NewFeature(Base):
       __tablename__ = "new_features"
       
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String(255), nullable=False)
       description = Column(Text)
       created_at = Column(DateTime(timezone=True), server_default=func.now())
       updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   ```

3. **Create Migration**:
   ```bash
   alembic revision --autogenerate -m "Add new_features table"
   alembic upgrade head
   ```

4. **Implement Service Logic**:
   ```python
   # app/services/new_feature.py
   from sqlalchemy.orm import Session
   from app.database.models import NewFeature
   from app.api.models import NewFeatureRequest
   
   class NewFeatureService:
       def create_feature(self, db: Session, feature_data: NewFeatureRequest) -> NewFeature:
           feature = NewFeature(
               name=feature_data.name,
               description=feature_data.description
           )
           db.add(feature)
           db.commit()
           db.refresh(feature)
           return feature
   ```

5. **Add API Routes**:
   ```python
   # app/api/routes.py
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from app.database.connection import get_db
   from app.api.models import NewFeatureRequest, NewFeatureResponse
   from app.services.new_feature import NewFeatureService
   
   router = APIRouter()
   service = NewFeatureService()
   
   @router.post("/features", response_model=NewFeatureResponse)
   async def create_feature(
       feature_data: NewFeatureRequest,
       db: Session = Depends(get_db)
   ):
       feature = service.create_feature(db, feature_data)
       return feature
   ```

6. **Add Tests**:
   ```python
   # tests/test_new_feature.py
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   
   client = TestClient(app)
   
   def test_create_feature():
       response = client.post(
           "/api/v1/features",
           json={"name": "Test Feature", "description": "Test Description"}
       )
       assert response.status_code == 200
       assert response.json()["name"] == "Test Feature"
   ```

#### Adding Frontend Components

1. **Create Component**:
   ```vue
   <!-- src/components/NewFeature.vue -->
   <template>
     <div class="new-feature">
       <h2>{{ title }}</h2>
       <form @submit.prevent="submitForm">
         <input v-model="form.name" placeholder="Feature Name" required />
         <textarea v-model="form.description" placeholder="Description"></textarea>
         <button type="submit" :disabled="loading">Create Feature</button>
       </form>
     </div>
   </template>
   
   <script setup lang="ts">
   import { ref, reactive } from 'vue'
   import { useNewFeatureStore } from '@/stores/newFeature'
   
   interface Props {
     title?: string
   }
   
   const props = withDefaults(defineProps<Props>(), {
     title: 'New Feature'
   })
   
   const store = useNewFeatureStore()
   const loading = ref(false)
   
   const form = reactive({
     name: '',
     description: ''
   })
   
   const submitForm = async () => {
     loading.value = true
     try {
       await store.createFeature(form)
       // Reset form
       form.name = ''
       form.description = ''
     } catch (error) {
       console.error('Error creating feature:', error)
     } finally {
       loading.value = false
     }
   }
   </script>
   
   <style scoped>
   .new-feature {
     @apply p-4 border rounded-lg;
   }
   </style>
   ```

2. **Create Store**:
   ```typescript
   // src/stores/newFeature.ts
   import { defineStore } from 'pinia'
   import { ref } from 'vue'
   import { newFeatureApi } from '@/services/api'
   
   export interface NewFeature {
     id: number
     name: string
     description?: string
     created_at: string
   }
   
   export const useNewFeatureStore = defineStore('newFeature', () => {
     const features = ref<NewFeature[]>([])
     const loading = ref(false)
     const error = ref<string | null>(null)
   
     const createFeature = async (featureData: { name: string; description?: string }) => {
       loading.value = true
       error.value = null
       try {
         const feature = await newFeatureApi.create(featureData)
         features.value.push(feature)
         return feature
       } catch (err) {
         error.value = err instanceof Error ? err.message : 'Unknown error'
         throw err
       } finally {
         loading.value = false
       }
     }
   
     const fetchFeatures = async () => {
       loading.value = true
       try {
         const data = await newFeatureApi.getAll()
         features.value = data
       } catch (err) {
         error.value = err instanceof Error ? err.message : 'Unknown error'
       } finally {
         loading.value = false
       }
     }
   
     return {
       features,
       loading,
       error,
       createFeature,
       fetchFeatures
     }
   })
   ```

3. **Create API Service**:
   ```typescript
   // src/services/newFeatureApi.ts
   import { apiClient } from './apiClient'
   import type { NewFeature } from '@/stores/newFeature'
   
   export const newFeatureApi = {
     async create(data: { name: string; description?: string }): Promise<NewFeature> {
       const response = await apiClient.post('/features', data)
       return response.data
     },
   
     async getAll(): Promise<NewFeature[]> {
       const response = await apiClient.get('/features')
       return response.data
     },
   
     async getById(id: number): Promise<NewFeature> {
       const response = await apiClient.get(`/features/${id}`)
       return response.data
     },
   
     async update(id: number, data: Partial<NewFeature>): Promise<NewFeature> {
       const response = await apiClient.put(`/features/${id}`, data)
       return response.data
     },
   
     async delete(id: number): Promise<void> {
       await apiClient.delete(`/features/${id}`)
     }
   }
   ```

## Code Standards

### Python Code Standards

#### Formatting and Linting

- **Black**: Code formatting (line length: 88)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

#### Configuration Files

```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    migrations

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
no_implicit_optional = True
show_error_codes = True

[mypy-tests.*]
disallow_untyped_defs = False

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
(
  /(
      \.eggs
    | \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
    | migrations
  )/
)
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["migrations/*"]
```

#### Code Style Guidelines

1. **Function and Variable Names**: Use snake_case
2. **Class Names**: Use PascalCase
3. **Constants**: Use UPPER_SNAKE_CASE
4. **Type Hints**: Always use type hints for function parameters and return values
5. **Docstrings**: Use Google-style docstrings

```python
def calculate_user_score(
    user_id: int, 
    messages: List[ChatMessage], 
    weight_factor: float = 1.0
) -> float:
    """Calculate user engagement score based on chat messages.
    
    Args:
        user_id: The ID of the user
        messages: List of chat messages to analyze
        weight_factor: Multiplier for score calculation
        
    Returns:
        The calculated engagement score
        
    Raises:
        ValueError: If user_id is invalid or messages is empty
    """
    if user_id <= 0:
        raise ValueError("User ID must be positive")
    
    if not messages:
        raise ValueError("Messages list cannot be empty")
    
    # Implementation here
    return score
```

### TypeScript/Vue Code Standards

#### ESLint Configuration

```json
// .eslintrc.json
{
  "extends": [
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "vue/component-name-in-template-casing": ["error", "PascalCase"],
    "vue/component-definition-name-casing": ["error", "PascalCase"],
    "vue/multi-word-component-names": "error",
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

#### Prettier Configuration

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "endOfLine": "lf"
}
```

#### Vue Component Guidelines

1. **Component Naming**: Use PascalCase for component names
2. **Props**: Define with TypeScript interfaces
3. **Emits**: Explicitly define emitted events
4. **Composition API**: Prefer Composition API over Options API
5. **Script Setup**: Use `<script setup>` syntax

```vue
<template>
  <div class="user-profile">
    <h2>{{ user.name }}</h2>
    <button @click="handleUpdate">Update Profile</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { User } from '@/types/user'

interface Props {
  user: User
  editable?: boolean
}

interface Emits {
  update: [user: User]
  delete: [userId: number]
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

const isEditing = ref(false)

const displayName = computed(() => {
  return props.user.firstName + ' ' + props.user.lastName
})

const handleUpdate = (): void => {
  emit('update', props.user)
}
</script>

<style scoped>
.user-profile {
  @apply p-4 border rounded-lg shadow-sm;
}
</style>
```

## Testing

### Backend Testing

#### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_auth.py
│   ├── test_chat.py
│   └── test_services.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   └── test_database.py
├── e2e/                     # End-to-end tests
│   └── test_user_flows.py
└── fixtures/                # Test data fixtures
    ├── users.json
    └── messages.json
```

#### Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import get_db, Base
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    from app.database.models import User
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

#### Unit Test Examples

```python
# tests/unit/test_auth.py
import pytest
from app.auth.services import AuthService
from app.auth.models import UserCreate

class TestAuthService:
    def test_create_user_success(self, db_session):
        auth_service = AuthService()
        user_data = UserCreate(
            email="newuser@example.com",
            username="newuser",
            password="securepassword"
        )
        
        user = auth_service.create_user(db_session, user_data)
        
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.hashed_password != "securepassword"  # Should be hashed
    
    def test_create_user_duplicate_email(self, db_session, test_user):
        auth_service = AuthService()
        user_data = UserCreate(
            email=test_user.email,  # Duplicate email
            username="anotheruser",
            password="securepassword"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.create_user(db_session, user_data)
    
    def test_authenticate_user_success(self, db_session, test_user):
        auth_service = AuthService()
        
        # Mock password verification
        auth_service.verify_password = lambda plain, hashed: True
        
        user = auth_service.authenticate_user(
            db_session, test_user.email, "correct_password"
        )
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_authenticate_user_wrong_password(self, db_session, test_user):
        auth_service = AuthService()
        
        # Mock password verification
        auth_service.verify_password = lambda plain, hashed: False
        
        user = auth_service.authenticate_user(
            db_session, test_user.email, "wrong_password"
        )
        
        assert user is None
```

#### Integration Test Examples

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient

class TestAuthEndpoints:
    def test_register_user(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
    
    def test_login_user(self, client: TestClient, test_user):
        # First, set a known password for the test user
        from app.core.security import get_password_hash
        test_user.hashed_password = get_password_hash("testpassword")
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user(self, client: TestClient, test_user):
        # Create access token
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

class TestChatEndpoints:
    def test_direct_chat(self, client: TestClient, test_user):
        # Create access token
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/v1/chat/direct",
            json={
                "message": "Hello, how are you?",
                "context": {}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "metadata" in data
    
    def test_create_session(self, client: TestClient, test_user):
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/v1/chat/sessions",
            json={
                "title": "Test Chat Session",
                "context": {"topic": "general"}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat Session"
        assert "session_id" in data
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run tests with specific marker
pytest -m unit
pytest -m integration

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Frontend Testing

#### Test Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts']
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
```

```typescript
// src/test/setup.ts
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'

// Global test configuration
config.global.plugins = [createPinia()]

// Mock API calls
vi.mock('@/services/api', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn()
  },
  chatApi: {
    sendMessage: vi.fn(),
    createSession: vi.fn(),
    getSessions: vi.fn()
  }
}))
```

#### Component Tests

```typescript
// src/components/__tests__/LoginForm.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import LoginForm from '../LoginForm.vue'
import { useAuthStore } from '@/stores/auth'

describe('LoginForm', () => {
  it('renders login form correctly', () => {
    const wrapper = mount(LoginForm, {
      global: {
        plugins: [createPinia()]
      }
    })
    
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })
  
  it('validates required fields', async () => {
    const wrapper = mount(LoginForm, {
      global: {
        plugins: [createPinia()]
      }
    })
    
    // Try to submit without filling fields
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
  
  it('calls login function on form submission', async () => {
    const pinia = createPinia()
    const wrapper = mount(LoginForm, {
      global: {
        plugins: [pinia]
      }
    })
    
    const authStore = useAuthStore()
    const loginSpy = vi.spyOn(authStore, 'login')
    
    // Fill form
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(loginSpy).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    })
  })
})
```

#### Store Tests

```typescript
// src/stores/__tests__/auth.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { authApi } from '@/services/api'

vi.mock('@/services/api')

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('initializes with correct default state', () => {
    const store = useAuthStore()
    
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.loading).toBe(false)
  })
  
  it('handles successful login', async () => {
    const store = useAuthStore()
    const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' }
    const mockToken = 'mock-jwt-token'
    
    vi.mocked(authApi.login).mockResolvedValue({
      user: mockUser,
      access_token: mockToken,
      token_type: 'bearer'
    })
    
    await store.login({ email: 'test@example.com', password: 'password123' })
    
    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe(mockToken)
    expect(store.isAuthenticated).toBe(true)
    expect(store.loading).toBe(false)
  })
  
  it('handles login failure', async () => {
    const store = useAuthStore()
    
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'))
    
    await expect(store.login({ 
      email: 'test@example.com', 
      password: 'wrongpassword' 
    })).rejects.toThrow('Invalid credentials')
    
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.loading).toBe(false)
  })
})
```

#### Running Frontend Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test LoginForm.test.ts

# Run tests in UI mode
npm run test:ui
```

## Debugging

### Backend Debugging

#### VS Code Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Chat Service",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/venv/bin/uvicorn",
      "args": [
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8002",
        "--reload"
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug Auth Service",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/venv/bin/uvicorn",
      "args": [
        "app.auth_main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${workspaceFolder}/tests",
        "-v"
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

#### Logging Configuration

```python
# app/core/logging.py
import logging
import sys
from typing import Any, Dict
from app.config import settings

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging() -> None:
    """Set up logging configuration."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    if settings.DEBUG:
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

# Create logger instance
logger = logging.getLogger(__name__)
```

#### Debug Utilities

```python
# app/utils/debug.py
import functools
import time
from typing import Any, Callable, TypeVar
from app.core.logging import logger

F = TypeVar('F', bound=Callable[..., Any])

def debug_time(func: F) -> F:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(
            f"{func.__name__} executed in {end_time - start_time:.4f} seconds"
        )
        return result
    return wrapper

def debug_params(func: F) -> F:
    """Decorator to log function parameters."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"{func.__name__} called with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned: {result}")
        return result
    return wrapper

class DebugContext:
    """Context manager for debugging code blocks."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Entering {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        
        if exc_type:
            logger.debug(f"Exiting {self.name} with exception: {exc_val} (duration: {duration:.4f}s)")
        else:
            logger.debug(f"Exiting {self.name} (duration: {duration:.4f}s)")
```

### Frontend Debugging

#### Vue DevTools

1. Install Vue DevTools browser extension
2. Enable in development mode
3. Use for inspecting component state, props, and events

#### Debug Configuration

```typescript
// src/utils/debug.ts
export const DEBUG = import.meta.env.DEV

export const debugLog = (message: string, data?: any): void => {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data)
  }
}

export const debugError = (message: string, error?: any): void => {
  if (DEBUG) {
    console.error(`[ERROR] ${message}`, error)
  }
}

export const debugTime = <T extends (...args: any[]) => any>(fn: T, name?: string): T => {
  return ((...args: any[]) => {
    if (!DEBUG) return fn(...args)
    
    const label = name || fn.name || 'Anonymous function'
    console.time(label)
    const result = fn(...args)
    console.timeEnd(label)
    return result
  }) as T
}
```

## Contributing

### Getting Started

1. **Fork the Repository**
2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/yourusername/chat-bot-practice-langchain.git
   cd chat-bot-practice-langchain
   ```

3. **Set Up Development Environment** (see setup instructions above)

4. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Pull Request Guidelines

1. **Code Quality**:
   - Follow code standards
   - Add tests for new features
   - Ensure all tests pass
   - Update documentation

2. **Commit Messages**:
   - Use conventional commit format
   - Be descriptive and clear
   - Reference issues when applicable

3. **PR Description**:
   - Describe what the PR does
   - List any breaking changes
   - Include screenshots for UI changes
   - Reference related issues

### Code Review Process

1. **Automated Checks**:
   - CI/CD pipeline must pass
   - Code coverage requirements
   - Linting and formatting checks

2. **Manual Review**:
   - At least one approval required
   - Address all review comments
   - Ensure documentation is updated

3. **Merge Requirements**:
   - All checks passing
   - Approved by maintainer
   - Up to date with main branch

## Best Practices

### Security

1. **Never commit secrets**:
   - Use environment variables
   - Add sensitive files to .gitignore
   - Use secret management tools

2. **Input validation**:
   - Validate all user inputs
   - Use Pydantic models for API validation
   - Sanitize data before database operations

3. **Authentication**:
   - Use strong password policies
   - Implement proper session management
   - Use HTTPS in production

### Performance

1. **Database**:
   - Use appropriate indexes
   - Implement connection pooling
   - Monitor query performance

2. **API**:
   - Implement caching strategies
   - Use pagination for large datasets
   - Optimize response payloads

3. **Frontend**:
   - Implement lazy loading
   - Use virtual scrolling for large lists
   - Optimize bundle size

### Monitoring

1. **Logging**:
   - Use structured logging
   - Include correlation IDs
   - Log important business events

2. **Metrics**:
   - Monitor API response times
   - Track error rates
   - Monitor resource usage

3. **Alerting**:
   - Set up alerts for critical issues
   - Monitor service health
   - Track business metrics

This development guide provides a comprehensive foundation for working on the Chat Bot System. Follow these guidelines to ensure consistent, high-quality code and smooth collaboration.