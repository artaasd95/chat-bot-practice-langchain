# Backend Services Documentation

This document provides comprehensive documentation for the backend services in the Chat Bot System.

## Table of Contents

1. [Overview](#overview)
2. [LLM Service](#llm-service)
3. [Webhook Service](#webhook-service)
4. [Request Tracking Service](#request-tracking-service)
5. [Service Integration](#service-integration)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Overview

The backend services layer provides core business logic and external integrations for the Chat Bot System. This layer is responsible for:

- **LLM Integration**: Managing language model interactions
- **API Tools Service**: Handling REST API tool calling functionality
- **History Service**: Managing conversation history and context
- **Webhook Processing**: Handling asynchronous notifications
- **Request Tracking**: Monitoring and tracking request lifecycle
- **External API Integration**: Connecting with third-party services

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │   API Layer     │    │   API Layer     │    │   API Layer     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Service   │    │ API Tools       │    │ History Service │    │ Webhook Service │
└─────────────────┘    │ Service         │    └─────────────────┘    └─────────────────┘
         │              └─────────────────┘             │                       │
         ▼                       │                       ▼                       ▼
┌─────────────────┐              ▼              ┌─────────────────┐    ┌─────────────────┐
│   OpenAI API    │    ┌─────────────────┐    │   PostgreSQL    │    │ External APIs   │
└─────────────────┘    │ External APIs   │    │   Database      │    └─────────────────┘
                        └─────────────────┘    └─────────────────┘
```

## API Tools Service

### Overview

The API Tools Service (`app/services/api_tools.py`) provides REST API tool calling functionality, enabling the LLM to make external API calls and integrate the results into conversations.

### Key Features

- **API Request Parsing**: Extracts API call requests from LLM responses
- **HTTP Client**: Asynchronous HTTP requests using aiohttp
- **Response Integration**: Incorporates API results back into conversation flow
- **Error Handling**: Graceful handling of API failures and timeouts
- **Request Validation**: Validates API requests before execution

### Service Implementation

#### API Request Models

```python
class APIRequest(BaseModel):
    """Model for API request data."""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30

class APIResponse(BaseModel):
    """Model for API response data."""
    status_code: int
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
```

#### API Tools Service Class

```python
class APIToolsService:
    """Service for making API calls from LLM responses."""
    
    def __init__(self):
        self.session = None
    
    async def make_api_call(self, request: APIRequest) -> APIResponse:
        """Make an API call and return the response."""
        start_time = time.time()
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                json=request.data,
                timeout=aiohttp.ClientTimeout(total=request.timeout)
            ) as response:
                execution_time = time.time() - start_time
                
                if response.content_type == 'application/json':
                    data = await response.json()
                    return APIResponse(
                        status_code=response.status,
                        data=data,
                        execution_time=execution_time
                    )
                else:
                    text = await response.text()
                    return APIResponse(
                        status_code=response.status,
                        text=text,
                        execution_time=execution_time
                    )
        except Exception as e:
            execution_time = time.time() - start_time
            return APIResponse(
                status_code=0,
                error=str(e),
                execution_time=execution_time
            )
```

#### Utility Functions

```python
def parse_api_request_from_text(text: str) -> Optional[APIRequest]:
    """Parse API request from LLM response text."""
    # Implementation for parsing API calls from text
    
def should_make_api_call(text: str) -> bool:
    """Check if the text contains an API call request."""
    # Implementation for detecting API calls
```

## History Service

### Overview

The History Service (`app/services/history.py`) manages conversation history, providing persistent storage and intelligent context loading for enhanced chat experiences.

### Key Features

- **Conversation Persistence**: Automatic saving of all chat messages
- **Context Loading**: Intelligent retrieval of relevant conversation history
- **Session Management**: Maintains conversation continuity across sessions
- **History Summarization**: Efficient context management for long conversations
- **Database Integration**: Seamless integration with PostgreSQL database

### Service Implementation

#### Core Functions

```python
async def load_conversation_history(
    session_id: str, 
    db: Session, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Load conversation history for a session."""
    
async def save_human_message(
    session_id: str, 
    message: str, 
    db: Session, 
    user_id: Optional[str] = None
) -> ChatMessage:
    """Save a human message to the conversation history."""
    
async def save_ai_message(
    session_id: str, 
    message: str, 
    db: Session, 
    metadata: Optional[Dict[str, Any]] = None
) -> ChatMessage:
    """Save an AI message to the conversation history."""
    
async def save_system_message(
    session_id: str, 
    message: str, 
    db: Session
) -> ChatMessage:
    """Save a system message to the conversation history."""
    
async def summarize_conversation(
    session_id: str, 
    db: Session
) -> Optional[str]:
    """Summarize a conversation for context management."""
    
def format_history_for_llm(
    history: List[Dict[str, Any]]
) -> List[BaseMessage]:
    """Format conversation history for LLM context."""
```

#### Database Models Integration

The History Service integrates with the following database models:

- **ChatSession**: Represents a conversation session
- **ChatMessage**: Individual messages within a session
- **User**: User information for message attribution

## LLM Service

### Overview

The LLM Service (`app/services/llm.py`) manages all interactions with language models, providing a unified interface for AI response generation.

### Key Features

- **Model Abstraction**: Unified interface for different LLM providers
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Handling**: Comprehensive error management
- **Configuration Management**: Centralized model configuration
- **Performance Monitoring**: Response time and token usage tracking

### Service Implementation

#### LLM Initialization

```python
def get_llm() -> BaseLLM:
    """Get the language model instance.
    
    Returns:
        BaseLLM: The language model instance.
    """
    logger.info(f"Initializing LLM with model {settings.LLM_MODEL}")
    
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )
    
    return llm
```

**Configuration Parameters**:
- `LLM_MODEL`: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
- `LLM_TEMPERATURE`: Response creativity (0.0 - 2.0)
- `OPENAI_API_KEY`: Authentication key for OpenAI API

#### Response Generation

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_llm_response(
    llm: BaseLLM,
    messages: List[BaseMessage],
    **kwargs
) -> Dict[str, Any]:
    """Generate a response from the LLM with retry logic.
    
    Args:
        llm: The language model to use.
        messages: The messages to generate a response for.
        **kwargs: Additional arguments to pass to the LLM.
        
    Returns:
        Dict containing the response and any additional metadata.
    """
    logger.info(f"Generating LLM response for {len(messages)} messages")
    
    try:
        # Generate response
        response = await llm.agenerate([messages], **kwargs)
        response_text = response.generations[0][0].text
        
        # Extract metadata
        metadata = {}
        if hasattr(response, "llm_output") and response.llm_output:
            metadata = response.llm_output
        
        logger.info(f"LLM response generated successfully")
        
        return {
            "response": response_text,
            "metadata": metadata,
        }
    except Exception as e:
        logger.error(f"Error generating LLM response: {str(e)}")
        raise
```

### Retry Strategy

**Configuration**:
- **Max Attempts**: 3 retries
- **Wait Strategy**: Exponential backoff (2s, 4s, 8s)
- **Max Wait**: 10 seconds

**Retry Triggers**:
- Network timeouts
- Rate limiting errors
- Temporary API unavailability
- Connection errors

### Error Handling

**Common Error Types**:

1. **Authentication Errors**
   - Invalid API key
   - Expired credentials
   - Insufficient permissions

2. **Rate Limiting**
   - Request quota exceeded
   - Token limit reached
   - Concurrent request limits

3. **Model Errors**
   - Invalid model name
   - Model unavailable
   - Content policy violations

4. **Network Errors**
   - Connection timeouts
   - DNS resolution failures
   - SSL/TLS errors

**Error Response Format**:
```python
{
    "error": "LLM_GENERATION_FAILED",
    "message": "Failed to generate response",
    "details": {
        "error_type": "RateLimitError",
        "retry_after": 60,
        "request_id": "req_123"
    }
}
```

### Performance Monitoring

**Metrics Tracked**:
- Response generation time
- Token usage (input/output)
- Success/failure rates
- Retry attempts
- API quota usage

**Logging Examples**:
```
INFO: Initializing LLM with model gpt-3.5-turbo
INFO: Generating LLM response for 3 messages
INFO: LLM response generated successfully
DEBUG: Response time: 1.2s, Tokens used: 150
```

## Webhook Service

### Overview

The Webhook Service (`app/services/webhook.py`) handles asynchronous communication with external systems through HTTP callbacks.

### Key Features

- **Asynchronous Delivery**: Non-blocking webhook sending
- **Retry Logic**: Automatic retry with exponential backoff
- **Timeout Management**: Configurable request timeouts
- **Error Handling**: Comprehensive error tracking
- **Security**: Optional webhook signature verification

### Service Implementation

#### Webhook Delivery

```python
@retry(
    stop=stop_after_attempt(settings.WEBHOOK_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=settings.WEBHOOK_RETRY_DELAY, max=10)
)
async def send_webhook_response(callback_url: str, data: Dict[str, Any]) -> bool:
    """Send a webhook response to the callback URL with retry logic.
    
    Args:
        callback_url: The URL to send the response to.
        data: The data to send.
        
    Returns:
        True if the response was sent successfully, False otherwise.
    """
    try:
        logger.info(f"Sending webhook response to {callback_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                callback_url,
                json=data,
                timeout=settings.WEBHOOK_TIMEOUT
            ) as response:
                if response.status < 400:
                    response_text = await response.text()
                    logger.info(f"Webhook response sent successfully to {callback_url}")
                    logger.debug(f"Webhook response: {response_text}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send webhook response to {callback_url}: {response.status} - {error_text}")
                    return False
    except aiohttp.ClientError as e:
        logger.error(f"Client error sending webhook response to {callback_url}: {str(e)}")
        raise
    except asyncio.TimeoutError:
        logger.error(f"Timeout sending webhook response to {callback_url}")
        raise
    except Exception as e:
        logger.error(f"Error sending webhook response to {callback_url}: {str(e)}")
        raise
```

### Configuration

**Webhook Settings**:
```python
# Webhook Settings
WEBHOOK_SECRET: Optional[str] = None
WEBHOOK_TIMEOUT: int = 30
WEBHOOK_RETRY_ATTEMPTS: int = 3
WEBHOOK_RETRY_DELAY: int = 2
```

### Webhook Payload Format

**Standard Payload**:
```json
{
  "event": "chat.response.generated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "track_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "sess_123",
    "user_id": 456,
    "response": "Generated AI response",
    "metadata": {
      "tokens_used": 150,
      "processing_time": 1.2
    }
  }
}
```

**Error Payload**:
```json
{
  "event": "chat.response.failed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "track_id": "550e8400-e29b-41d4-a716-446655440000",
    "error": {
      "code": "LLM_GENERATION_FAILED",
      "message": "Failed to generate response",
      "details": {}
    }
  }
}
```

### Security Considerations

**Webhook Signature Verification**:
```python
import hmac
import hashlib

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

**Best Practices**:
- Use HTTPS for webhook URLs
- Implement signature verification
- Validate webhook URLs
- Rate limit webhook sending
- Log all webhook attempts

## Request Tracking Service

### Overview

The Request Tracking Service (`app/utils/tracking.py`) provides request lifecycle management and status tracking for asynchronous operations.

### Key Features

- **Request Lifecycle Tracking**: Monitor request from start to completion
- **Status Management**: Track processing status and updates
- **Thread-Safe Operations**: Concurrent request handling
- **Memory-Based Storage**: Fast in-memory tracking (production should use Redis)
- **Cleanup Management**: Automatic cleanup of old requests

### Service Implementation

#### RequestTracker Class

```python
class RequestTracker:
    """Utility class for tracking webhook requests.
    
    This is a simple in-memory implementation. In a production environment,
    this would be replaced with a persistent store like Redis or a database.
    """
    
    def __init__(self):
        self._requests: Dict[str, WebhookStatusResponse] = {}
        self._lock = asyncio.Lock()
    
    async def add_request(self, track_id: UUID, status: str = "processing") -> None:
        """Add a new request to the tracker.
        
        Args:
            track_id: The tracking ID for the request.
            status: The initial status of the request.
        """
        async with self._lock:
            self._requests[str(track_id)] = WebhookStatusResponse(
                track_id=track_id,
                status=status,
                timestamp=datetime.utcnow()
            )
            logger.debug(f"Added request with track_id: {track_id}")
    
    async def update_request(self, track_id: UUID, **kwargs) -> None:
        """Update an existing request.
        
        Args:
            track_id: The tracking ID for the request.
            **kwargs: The fields to update.
        """
        track_id_str = str(track_id)
        async with self._lock:
            if track_id_str not in self._requests:
                logger.warning(f"Attempted to update non-existent request: {track_id}")
                return
            
            current = self._requests[track_id_str].dict()
            current.update(kwargs)
            current['timestamp'] = datetime.utcnow()
            
            self._requests[track_id_str] = WebhookStatusResponse(**current)
            logger.debug(f"Updated request {track_id} with: {kwargs}")
```

### Status Management

**Request Statuses**:
- `processing`: Request is being processed
- `completed`: Request completed successfully
- `failed`: Request failed with error
- `timeout`: Request timed out
- `cancelled`: Request was cancelled

**Status Transitions**:
```
processing → completed
processing → failed
processing → timeout
processing → cancelled
```

### WebhookStatusResponse Model

```python
class WebhookStatusResponse(BaseModel):
    track_id: UUID
    status: str
    timestamp: datetime
    response: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Usage Examples

#### Adding a Request
```python
tracker = RequestTracker()
track_id = uuid4()

# Add new request
await tracker.add_request(track_id, "processing")

# Update with response
await tracker.update_request(
    track_id,
    status="completed",
    response="AI response generated",
    metadata={"tokens_used": 150}
)
```

#### Checking Request Status
```python
status = await tracker.get_request(track_id)
if status:
    print(f"Status: {status.status}")
    print(f"Response: {status.response}")
else:
    print("Request not found")
```

### Production Considerations

**Redis Implementation**:
```python
import redis.asyncio as redis

class RedisRequestTracker:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def add_request(self, track_id: UUID, status: str = "processing") -> None:
        data = {
            "track_id": str(track_id),
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.redis.setex(
            f"request:{track_id}",
            3600,  # 1 hour TTL
            json.dumps(data)
        )
```

## Service Integration

### Service Dependencies

```python
# Dependency injection pattern
from app.services.llm import get_llm
from app.services.webhook import send_webhook_response
from app.utils.tracking import RequestTracker

class ChatService:
    def __init__(self):
        self.llm = get_llm()
        self.tracker = RequestTracker()
    
    async def process_chat_request(
        self,
        messages: List[BaseMessage],
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        track_id = uuid4()
        
        # Track request
        await self.tracker.add_request(track_id, "processing")
        
        try:
            # Generate response
            result = await generate_llm_response(self.llm, messages)
            
            # Update tracking
            await self.tracker.update_request(
                track_id,
                status="completed",
                response=result["response"]
            )
            
            # Send webhook if provided
            if callback_url:
                webhook_data = {
                    "track_id": str(track_id),
                    "response": result["response"],
                    "metadata": result["metadata"]
                }
                await send_webhook_response(callback_url, webhook_data)
            
            return result
            
        except Exception as e:
            # Update tracking with error
            await self.tracker.update_request(
                track_id,
                status="failed",
                error=str(e)
            )
            raise
```

### Service Lifecycle

1. **Initialization**: Services are initialized with configuration
2. **Request Processing**: Services handle incoming requests
3. **Error Handling**: Services manage errors and retries
4. **Cleanup**: Services clean up resources and connections

## Configuration

### Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7

# Webhook Configuration
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=2

# Tracking Configuration
REDIS_URL=redis://localhost:6379/0
TRACKING_TTL=3600
```

### Configuration Validation

```python
from pydantic import BaseSettings, validator

class ServiceSettings(BaseSettings):
    # LLM Settings
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    
    # Webhook Settings
    webhook_timeout: int = 30
    webhook_retry_attempts: int = 3
    
    @validator('llm_temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if v and not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v
```

## Error Handling

### Error Categories

1. **Service Errors**: Internal service failures
2. **External API Errors**: Third-party API failures
3. **Configuration Errors**: Invalid configuration
4. **Network Errors**: Connectivity issues
5. **Validation Errors**: Invalid input data

### Error Response Format

```python
class ServiceError(Exception):
    def __init__(self, message: str, error_code: str, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class LLMServiceError(ServiceError):
    pass

class WebhookServiceError(ServiceError):
    pass

class TrackingServiceError(ServiceError):
    pass
```

### Error Handling Patterns

```python
try:
    result = await generate_llm_response(llm, messages)
except RateLimitError as e:
    raise LLMServiceError(
        "Rate limit exceeded",
        "RATE_LIMIT_EXCEEDED",
        {"retry_after": e.retry_after}
    )
except AuthenticationError as e:
    raise LLMServiceError(
        "Authentication failed",
        "AUTHENTICATION_FAILED",
        {"api_key_valid": False}
    )
except Exception as e:
    logger.error(f"Unexpected LLM error: {str(e)}")
    raise LLMServiceError(
        "Internal service error",
        "INTERNAL_ERROR",
        {"original_error": str(e)}
    )
```

## Performance Optimization

### Connection Pooling

```python
import aiohttp
from aiohttp import TCPConnector

class OptimizedWebhookService:
    def __init__(self):
        connector = TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        self.session = aiohttp.ClientSession(connector=connector)
    
    async def close(self):
        await self.session.close()
```

### Caching Strategies

```python
from functools import lru_cache
import asyncio

class CachedLLMService:
    def __init__(self):
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def generate_cached_response(
        self,
        messages: List[BaseMessage]
    ) -> Dict[str, Any]:
        # Create cache key from messages
        cache_key = self._create_cache_key(messages)
        
        # Check cache
        if cache_key in self.response_cache:
            cached_response, timestamp = self.response_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info("Returning cached response")
                return cached_response
        
        # Generate new response
        response = await generate_llm_response(self.llm, messages)
        
        # Cache response
        self.response_cache[cache_key] = (response, time.time())
        
        return response
```

### Async Optimization

```python
import asyncio
from typing import List, Coroutine

async def batch_process_requests(
    requests: List[Coroutine],
    max_concurrent: int = 10
) -> List[Any]:
    """Process multiple requests concurrently with limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_request(coro):
        async with semaphore:
            return await coro
    
    tasks = [limited_request(req) for req in requests]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm import generate_llm_response

@pytest.mark.asyncio
async def test_generate_llm_response_success():
    # Mock LLM
    mock_llm = AsyncMock()
    mock_response = AsyncMock()
    mock_response.generations = [[AsyncMock(text="Test response")]]
    mock_response.llm_output = {"tokens_used": 10}
    mock_llm.agenerate.return_value = mock_response
    
    # Test
    messages = [HumanMessage(content="Hello")]
    result = await generate_llm_response(mock_llm, messages)
    
    # Assertions
    assert result["response"] == "Test response"
    assert result["metadata"]["tokens_used"] == 10
    mock_llm.agenerate.assert_called_once_with([messages])

@pytest.mark.asyncio
async def test_generate_llm_response_retry():
    # Mock LLM with failure then success
    mock_llm = AsyncMock()
    mock_llm.agenerate.side_effect = [
        Exception("Temporary failure"),
        AsyncMock(generations=[[AsyncMock(text="Success")]])
    ]
    
    # Test
    messages = [HumanMessage(content="Hello")]
    result = await generate_llm_response(mock_llm, messages)
    
    # Assertions
    assert result["response"] == "Success"
    assert mock_llm.agenerate.call_count == 2
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_webhook_service_integration():
    # Start test server
    async with aiohttp.test_server(create_test_app()) as server:
        callback_url = f"http://{server.host}:{server.port}/webhook"
        
        # Test webhook sending
        data = {"message": "test"}
        result = await send_webhook_response(callback_url, data)
        
        assert result is True
```

### Load Testing

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def load_test_llm_service(num_requests: int = 100):
    """Load test the LLM service."""
    llm = get_llm()
    messages = [HumanMessage(content="Hello")]
    
    start_time = time.time()
    
    # Create tasks
    tasks = [
        generate_llm_response(llm, messages)
        for _ in range(num_requests)
    ]
    
    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    # Analyze results
    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = len(results) - successful
    
    print(f"Processed {num_requests} requests in {end_time - start_time:.2f}s")
    print(f"Success rate: {successful/len(results)*100:.1f}%")
    print(f"Requests per second: {num_requests/(end_time - start_time):.1f}")
```

## Troubleshooting

### Common Issues

#### LLM Service Issues

**Issue**: "Authentication failed"
**Solution**: 
- Verify OPENAI_API_KEY is set correctly
- Check API key permissions
- Ensure API key is not expired

**Issue**: "Rate limit exceeded"
**Solution**:
- Implement request queuing
- Add delays between requests
- Upgrade API plan if needed

**Issue**: "Model not found"
**Solution**:
- Verify model name in configuration
- Check model availability
- Update to supported model

#### Webhook Service Issues

**Issue**: "Webhook delivery failed"
**Solution**:
- Verify callback URL is accessible
- Check network connectivity
- Validate webhook endpoint

**Issue**: "Webhook timeout"
**Solution**:
- Increase timeout configuration
- Optimize webhook endpoint
- Implement async processing

#### Tracking Service Issues

**Issue**: "Request not found"
**Solution**:
- Check request ID format
- Verify tracking service is running
- Check TTL configuration

**Issue**: "Memory usage high"
**Solution**:
- Implement cleanup routines
- Use Redis for persistence
- Set appropriate TTL values

### Debugging Tools

#### Service Health Checks

```python
async def health_check_llm_service() -> Dict[str, Any]:
    """Check LLM service health."""
    try:
        llm = get_llm()
        test_messages = [HumanMessage(content="Health check")]
        
        start_time = time.time()
        result = await generate_llm_response(llm, test_messages)
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time": response_time,
            "model": settings.LLM_MODEL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

#### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    return wrapper

@monitor_performance
async def generate_llm_response(llm, messages, **kwargs):
    # Implementation here
    pass
```

This documentation provides comprehensive coverage of the backend services in the Chat Bot System. For additional support or questions, refer to the development team or the individual service documentation.