#Introduction:
You are a very professional code reviewer and document generator agent
Your task is to completely analyze a code base and generate docs as defined below:

#Step 1:
You have to completely analyze the whole codebase, files, folders, and structure.

#Step 2:
You have to analyze the logic of the code and the relations between codes
IMPORTANT: if documents exist you might need to improve them or update them based on the recent changes of the code.

#Step 3:
After analysis you have to generate docs
the docs should be put in the folder docs if this folder is not exist, please make it
then you have to generate docs for the whole codebase
Each service, each section, each structure, each pipeline and every details of the code should be documented.
all of the pipelines should be able to track and read via this documents, which means if one wants to understand the code this document should be enough.
The models should be explained and the fields of the models and their usages should be also explained.

#Considerations: 
The documents should be in different files and folders if required.
The default of document generation should be in markdown format, but if any other structure like latex or formal documentation as language standards is requested, 
you have to fulfill the request and generate requested documents.
The documented should be well-formatted with the best practices of the GitHub.
if any section analysis is missing, please again analyze the code and complete and improve documents.
The documents you generate should be completely understandable, readable and standard.
Do not generate lots of readme files generate one readme file in the root of project as the standard,
for other parts of project you have to generate docs and put only one readme file for the sections required like each subfolder

Note: Documentation might be in different levels and use cases:
Development, Explanation the logic, usage
Development is the consideration in the docs that if the system wanted to be extended, what considerations should be applied.
Explanation is the docs that focus on explanation of the logic of the code, pipelines and structures of data flow and other logic flow.
Usage is the docs that mostly applied on README files that introduce the system and explain how the system should be used.
The focus is explanation in the docs and the usage must be written in the docs, development guide is not the major focus but if the user wanted it should be
explicitly focused on.
Also in writing the explanatory docs, the development type should not be completely forgotten.

IMPORTANT: Your task is to generate documents only not any other codes.# Backend Architecture Documentation

This document describes the backend architecture of the LangGraph Chat Bot System, built with FastAPI, LangGraph, and a microservices architecture.

## Overview

The backend consists of three main microservices:

- **Authentication Service** (Port 8001): User management and authentication
- **Chat Service** (Port 8002): Core chat functionality with LangGraph integration
- **Admin Service** (Port 8003): Administrative operations and analytics

All services are built with:

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **PostgreSQL**: Primary database for persistent data
- **Redis**: Caching and session management
- **LangGraph**: Orchestrating complex AI workflows
- **Pydantic**: Data validation and serialization

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Nginx       │    │   Load Balancer │
│   (Vue.js)      │◄──►│   Reverse Proxy │◄──►│   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (Nginx)                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Auth Service  │   Chat Service  │      Admin Service          │
│   (Port 8001)   │   (Port 8002)   │      (Port 8003)           │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │    │   LLM Service   │
│   Database      │    │     Cache       │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
app/
├── main.py                    # Chat service main application
├── auth_main.py              # Auth service main application
├── admin_main.py             # Admin service main application
├── config.py                 # Configuration settings
├── database/                 # Database layer
│   ├── __init__.py
│   ├── connection.py         # Database connection setup
│   ├── models.py            # SQLAlchemy models
│   └── migrations/          # Alembic migrations
├── auth/                    # Authentication service
│   ├── __init__.py
│   ├── routes.py           # Auth API routes
│   ├── models.py           # Auth-specific models
│   ├── services.py         # Auth business logic
│   └── utils.py            # Auth utilities
├── api/                     # Chat service API
│   ├── __init__.py
│   ├── routes.py           # Chat API routes
│   ├── models.py           # API request/response models
│   └── dependencies.py     # FastAPI dependencies
├── admin/                   # Admin service
│   ├── __init__.py
│   ├── routes.py           # Admin API routes
│   ├── services.py         # Admin business logic
│   └── analytics.py        # Analytics and reporting
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
│   └── state.py            # Graph state management
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

## Service Architecture

### Authentication Service

#### Main Application

```python
# app/auth_main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db
from app.auth.routes import router as auth_router
from app.core.middleware import LoggingMiddleware, SecurityMiddleware

app = FastAPI(
    title="Chat Bot Auth Service",
    description="Authentication and user management service",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }
```

#### Authentication Routes

```python
# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.auth.services import AuthService
from app.auth.models import UserCreate, UserResponse, Token
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user account."""
    try:
        user = await auth_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access tokens."""
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    
    # Update last login
    await auth_service.update_last_login(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    updated_user = await auth_service.update_user_profile(
        db, current_user.id, profile_data
    )
    return updated_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user and invalidate tokens."""
    # In a production system, you would invalidate the token
    # by adding it to a blacklist in Redis
    return {"message": "Successfully logged out"}

# Admin endpoints
@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of all users (admin only)."""
    users = await auth_service.get_users(
        db, page=page, size=size, search=search, is_active=is_active
    )
    return users

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)."""
    user = await auth_service.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### Chat Service

#### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db
from app.api.routes import router as api_router
from app.graph.builder import build_chat_graph
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware

app = FastAPI(
    title="Chat Bot Service",
    description="LangGraph-powered chat service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Global state for the chat graph
chat_graph = None

@app.on_event("startup")
async def startup_event():
    global chat_graph
    
    # Initialize database
    await init_db()
    
    # Build the chat graph
    chat_graph = build_chat_graph()
    
    print("Chat service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    print("Chat service shutting down")

# Include routers
app.include_router(api_router, prefix="/api/v1/chat", tags=["chat"])

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chat-service",
        "version": "1.0.0",
        "graph_ready": chat_graph is not None
    }

# Get the chat graph instance
def get_chat_graph():
    return chat_graph
```

#### Chat Routes

```python
# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.models import ChatRequest, ChatResponse, SessionCreate, SessionResponse
from app.services.chat import ChatService
from app.core.security import get_current_user
from app.main import get_chat_graph

router = APIRouter()
chat_service = ChatService()

@router.post("/direct", response_model=ChatResponse)
async def direct_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    graph = Depends(get_chat_graph)
):
    """Send a direct message to the AI without session persistence."""
    try:
        response = await chat_service.process_direct_message(
            graph, request.message, request.context, current_user
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    graph = Depends(get_chat_graph)
):
    """Create a new chat session."""
    try:
        session = await chat_service.create_session(
            db, graph, current_user.id, session_data
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/sessions")
async def get_sessions(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions."""
    sessions = await chat_service.get_user_sessions(
        db, current_user.id, page=page, size=size, search=search
    )
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    include_messages: bool = True,
    message_limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session."""
    session = await chat_service.get_session(
        db, session_id, current_user.id, include_messages, message_limit
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    graph = Depends(get_chat_graph)
):
    """Send a message to a chat session."""
    try:
        response = await chat_service.send_message(
            db, graph, session_id, current_user.id, request
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    success = await chat_service.delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session deleted successfully"}
```

## LangGraph Integration

### Graph Builder

```python
# app/graph/builder.py
from langgraph import StateGraph, END
from app.graph.state import ChatState
from app.graph.nodes import (
    preprocess_node,
    llm_node,
    postprocess_node,
    error_handler_node
)
from app.graph.edges import should_continue, route_to_llm

def build_chat_graph():
    """Build and compile the chat processing graph."""
    
    # Create the state graph
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("postprocess", postprocess_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Set entry point
    workflow.set_entry_point("preprocess")
    
    # Add edges
    workflow.add_conditional_edges(
        "preprocess",
        should_continue,
        {
            "continue": "llm",
            "error": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "llm",
        route_to_llm,
        {
            "success": "postprocess",
            "retry": "llm",
            "error": "error_handler"
        }
    )
    
    workflow.add_edge("postprocess", END)
    workflow.add_edge("error_handler", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    return graph
```

### Graph State

```python
# app/graph/state.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from langgraph import BaseState

class ChatState(BaseState):
    """State object for the chat processing graph."""
    
    # Input data
    user_message: str
    user_id: int
    session_id: Optional[str] = None
    context: Dict[str, Any] = {}
    
    # Processing data
    processed_message: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    system_prompt: Optional[str] = None
    
    # LLM data
    llm_response: Optional[str] = None
    tokens_used: Dict[str, int] = {}
    model_used: Optional[str] = None
    processing_time_ms: int = 0
    
    # Output data
    final_response: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    # Error handling
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Status tracking
    status: str = "initialized"
    timestamp: Optional[str] = None
```

### Graph Nodes

```python
# app/graph/nodes.py
import time
from datetime import datetime
from typing import Dict, Any
from app.graph.state import ChatState
from app.services.llm import LLMService
from app.services.chat import ChatService
from app.core.logging import logger

llm_service = LLMService()
chat_service = ChatService()

async def preprocess_node(state: ChatState) -> Dict[str, Any]:
    """Preprocess the user message and prepare context."""
    try:
        logger.info(f"Preprocessing message for user {state.user_id}")
        
        # Clean and validate the message
        processed_message = state.user_message.strip()
        if not processed_message:
            return {
                "error": "Empty message",
                "status": "error"
            }
        
        # Load conversation history if session exists
        conversation_history = []
        if state.session_id:
            # This would typically load from database
            conversation_history = await chat_service.get_conversation_history(
                state.session_id, limit=10
            )
        
        # Prepare system prompt based on context
        system_prompt = await chat_service.prepare_system_prompt(
            state.context, conversation_history
        )
        
        return {
            "processed_message": processed_message,
            "conversation_history": conversation_history,
            "system_prompt": system_prompt,
            "status": "preprocessed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Preprocessing error: {str(e)}")
        return {
            "error": f"Preprocessing failed: {str(e)}",
            "status": "error"
        }

async def llm_node(state: ChatState) -> Dict[str, Any]:
    """Generate response using the LLM."""
    try:
        start_time = time.time()
        
        logger.info(f"Generating LLM response for user {state.user_id}")
        
        # Prepare the prompt
        messages = []
        if state.system_prompt:
            messages.append({"role": "system", "content": state.system_prompt})
        
        # Add conversation history
        for msg in state.conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": state.processed_message})
        
        # Generate response
        response = await llm_service.generate_response(
            messages=messages,
            user_id=state.user_id,
            session_id=state.session_id
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "llm_response": response.content,
            "tokens_used": {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            },
            "model_used": response.model,
            "processing_time_ms": processing_time,
            "status": "llm_completed"
        }
        
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        
        # Check if we should retry
        if state.retry_count < state.max_retries:
            return {
                "retry_count": state.retry_count + 1,
                "status": "retry"
            }
        else:
            return {
                "error": f"LLM generation failed: {str(e)}",
                "status": "error"
            }

async def postprocess_node(state: ChatState) -> Dict[str, Any]:
    """Postprocess the LLM response and prepare final output."""
    try:
        logger.info(f"Postprocessing response for user {state.user_id}")
        
        # Clean up the response
        final_response = state.llm_response.strip()
        
        # Prepare metadata
        metadata = {
            "model_used": state.model_used,
            "tokens_used": state.tokens_used,
            "processing_time_ms": state.processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add any additional context
        if state.context:
            metadata["context"] = state.context
        
        return {
            "final_response": final_response,
            "metadata": metadata,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Postprocessing error: {str(e)}")
        return {
            "error": f"Postprocessing failed: {str(e)}",
            "status": "error"
        }

async def error_handler_node(state: ChatState) -> Dict[str, Any]:
    """Handle errors and provide fallback responses."""
    logger.error(f"Error handler activated: {state.error}")
    
    # Provide a fallback response
    fallback_response = (
        "I apologize, but I'm experiencing some technical difficulties. "
        "Please try again in a moment."
    )
    
    return {
        "final_response": fallback_response,
        "metadata": {
            "error": state.error,
            "fallback": True,
            "timestamp": datetime.utcnow().isoformat()
        },
        "status": "error_handled"
    }
```

### Graph Edges

```python
# app/graph/edges.py
from app.graph.state import ChatState

def should_continue(state: ChatState) -> str:
    """Determine if processing should continue after preprocessing."""
    if state.error:
        return "error"
    if state.status == "preprocessed":
        return "continue"
    return "error"

def route_to_llm(state: ChatState) -> str:
    """Route after LLM processing based on status."""
    if state.error:
        return "error"
    if state.status == "retry":
        return "retry"
    if state.status == "llm_completed":
        return "success"
    return "error"
```

## Service Layer

### LLM Service

```python
# app/services/llm.py
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.core.logging import logger
from app.services.cache import CacheService

class LLMService:
    """Service for interacting with Language Learning Models."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache_service = CacheService()
        self.default_model = settings.LLM_MODEL
        self.fallback_model = settings.LLM_FALLBACK_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        user_id: int,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Generate a response using the LLM."""
        
        model = model or self.default_model
        
        # Check cache first
        cache_key = self._generate_cache_key(messages, model)
        cached_response = await self.cache_service.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for user {user_id}")
            return cached_response
        
        try:
            # Make the API call
            response = await self._make_api_call(messages, model, **kwargs)
            
            # Cache the response
            await self.cache_service.set(
                cache_key, response, expire=settings.LLM_CACHE_TTL
            )
            
            logger.info(
                f"LLM response generated for user {user_id}, "
                f"tokens: {response.usage.total_tokens}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            
            # Try fallback model if primary fails
            if model != self.fallback_model:
                logger.info(f"Trying fallback model: {self.fallback_model}")
                return await self.generate_response(
                    messages, user_id, session_id, self.fallback_model, **kwargs
                )
            
            raise e
    
    async def _make_api_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Any:
        """Make the actual API call to the LLM."""
        
        params = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": kwargs.get("stream", False)
        }
        
        # Add any additional parameters
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            params["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            params["presence_penalty"] = kwargs["presence_penalty"]
        
        response = await self.client.chat.completions.create(**params)
        return response
    
    def _generate_cache_key(self, messages: List[Dict[str, str]], model: str) -> str:
        """Generate a cache key for the request."""
        import hashlib
        import json
        
        # Create a hash of the messages and model
        content = json.dumps({
            "messages": messages,
            "model": model
        }, sort_keys=True)
        
        return f"llm_response:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        user_id: int,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """Generate a streaming response from the LLM."""
        
        model = model or self.default_model
        kwargs["stream"] = True
        
        try:
            response_stream = await self._make_api_call(messages, model, **kwargs)
            
            async for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    yield {
                        "type": "chunk",
                        "content": chunk.choices[0].delta.content,
                        "model": model
                    }
            
            yield {"type": "end", "model": model}
            
        except Exception as e:
            logger.error(f"Streaming LLM error: {str(e)}")
            yield {"type": "error", "error": str(e)}
```

### Chat Service

```python
# app/services/chat.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import ChatSession, ChatMessage, User
from app.api.models import SessionCreate, ChatRequest
from app.graph.state import ChatState
from app.core.logging import logger
from datetime import datetime
import uuid

class ChatService:
    """Service for managing chat sessions and messages."""
    
    async def create_session(
        self,
        db: Session,
        graph: Any,
        user_id: int,
        session_data: SessionCreate
    ) -> Dict[str, Any]:
        """Create a new chat session."""
        
        # Create the session record
        session = ChatSession(
            uuid=str(uuid.uuid4()),
            user_id=user_id,
            title=session_data.title or "New Chat",
            metadata=session_data.context or {}
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # If there's an initial message, process it
        if session_data.initial_message:
            response = await self._process_message(
                db, graph, session.uuid, user_id, session_data.initial_message
            )
            
            return {
                "session_id": session.uuid,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": 2,  # User message + AI response
                "first_message": response["user_message"],
                "ai_response": response["ai_response"]
            }
        
        return {
            "session_id": session.uuid,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": 0
        }
    
    async def send_message(
        self,
        db: Session,
        graph: Any,
        session_id: str,
        user_id: int,
        request: ChatRequest
    ) -> Dict[str, Any]:
        """Send a message to a chat session."""
        
        # Verify session exists and belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.uuid == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_active == True
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        return await self._process_message(
            db, graph, session_id, user_id, request.message, request.context
        )
    
    async def _process_message(
        self,
        db: Session,
        graph: Any,
        session_id: str,
        user_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message through the LangGraph."""
        
        # Create user message record
        user_message = ChatMessage(
            uuid=str(uuid.uuid4()),
            session_id=db.query(ChatSession).filter(
                ChatSession.uuid == session_id
            ).first().id,
            content=message,
            role="user",
            metadata=context or {}
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        try:
            # Create initial state
            state = ChatState(
                user_message=message,
                user_id=user_id,
                session_id=session_id,
                context=context or {}
            )
            
            # Process through the graph
            result = await graph.ainvoke(state)
            
            # Create AI response message
            ai_message = ChatMessage(
                uuid=str(uuid.uuid4()),
                session_id=user_message.session_id,
                content=result["final_response"],
                role="assistant",
                metadata=result["metadata"],
                tokens_used=result["metadata"].get("tokens_used", {}).get("total", 0),
                processing_time_ms=result["metadata"].get("processing_time_ms", 0)
            )
            
            db.add(ai_message)
            
            # Update session
            session = db.query(ChatSession).filter(
                ChatSession.uuid == session_id
            ).first()
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(ai_message)
            
            # Get updated message count
            message_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).count()
            
            return {
                "user_message": {
                    "id": user_message.uuid,
                    "content": user_message.content,
                    "role": user_message.role,
                    "timestamp": user_message.created_at.isoformat(),
                    "metadata": user_message.metadata
                },
                "ai_response": {
                    "id": ai_message.uuid,
                    "content": ai_message.content,
                    "role": ai_message.role,
                    "timestamp": ai_message.created_at.isoformat(),
                    "metadata": ai_message.metadata
                },
                "session_updated": {
                    "message_count": message_count,
                    "updated_at": session.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")
            
            # Create error response
            error_message = ChatMessage(
                uuid=str(uuid.uuid4()),
                session_id=user_message.session_id,
                content="I apologize, but I encountered an error processing your message. Please try again.",
                role="assistant",
                metadata={"error": str(e), "fallback": True}
            )
            
            db.add(error_message)
            db.commit()
            
            raise e
    
    async def get_user_sessions(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's chat sessions with pagination."""
        
        query = db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.is_active == True
        )
        
        if search:
            query = query.filter(
                ChatSession.title.ilike(f"%{search}%")
            )
        
        total = query.count()
        sessions = query.order_by(
            ChatSession.updated_at.desc()
        ).offset((page - 1) * size).limit(size).all()
        
        session_list = []
        for session in sessions:
            # Get last message preview
            last_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            message_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).count()
            
            session_data = {
                "session_id": session.uuid,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": message_count
            }
            
            if last_message:
                session_data["last_message_preview"] = last_message.content[:100] + "..." if len(last_message.content) > 100 else last_message.content
                session_data["last_message_timestamp"] = last_message.created_at.isoformat()
            
            session_list.append(session_data)
        
        return {
            "sessions": session_list,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
                "has_next": page * size < total,
                "has_prev": page > 1
            }
        }
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation history for context."""
        # This would typically query the database
        # For now, return empty list
        return []
    
    async def prepare_system_prompt(
        self,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Prepare system prompt based on context."""
        base_prompt = (
            "You are a helpful AI assistant. Provide accurate, helpful, and "
            "engaging responses to user questions. Be concise but thorough."
        )
        
        # Add context-specific instructions
        if context.get("tone") == "professional":
            base_prompt += " Maintain a professional tone in your responses."
        elif context.get("tone") == "casual":
            base_prompt += " Use a casual, friendly tone in your responses."
        
        return base_prompt
```

## Configuration Management

```python
# app/config.py
from pydantic import BaseSettings, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat Bot System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database Settings
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Authentication Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # LLM Settings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4"
    LLM_FALLBACK_MODEL: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.7
    LLM_CACHE_TTL: int = 3600  # 1 hour
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Webhook Settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Deployment Configuration

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chatbot_db
      POSTGRES_USER: chatbot_user
      POSTGRES_PASSWORD: chatbot_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chatbot_user -d chatbot_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  auth-service:
    build: .
    command: uvicorn app.auth_main:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://chatbot_user:chatbot_password@postgres:5432/chatbot_db
      - REDIS_URL=redis://redis:6379
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

  chat-service:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://chatbot_user:chatbot_password@postgres:5432/chatbot_db
      - REDIS_URL=redis://redis:6379
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

  admin-service:
    build: .
    command: uvicorn app.admin_main:app --host 0.0.0.0 --port 8003
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://chatbot_user:chatbot_password@postgres:5432/chatbot_db
      - REDIS_URL=redis://redis:6379
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

volumes:
  postgres_data:

networks:
  default:
    name: chatbot_network
```

This backend architecture provides a robust, scalable foundation for the Chat Bot System with clear separation of concerns, comprehensive error handling, and efficient LangGraph integration.