# Chat API Documentation

The Chat Service provides the core conversational AI functionality using LangGraph for intelligent chat interactions.

## Base URL

```
http://localhost:8002/api/v1/chat
```

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the chat service.

#### Response

**Status: 200 OK**

```json
{
  "status": "healthy",
  "service": "chat-service",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Direct Chat

**POST** `/direct`

Send a message directly to the AI without session persistence.

#### Headers

```
Authorization: Bearer <access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "message": "Hello, how can you help me today?",
  "context": {
    "user_preferences": {
      "language": "en",
      "tone": "professional"
    },
    "metadata": {
      "source": "web",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

#### Response

**Status: 200 OK**

```json
{
  "response": "Hello! I'm here to help you with any questions or tasks you might have. I can assist with information, analysis, writing, coding, problem-solving, and much more. What would you like to work on today?",
  "metadata": {
    "model_used": "gpt-4",
    "tokens_used": {
      "input": 25,
      "output": 45,
      "total": 70
    },
    "processing_time_ms": 1250,
    "timestamp": "2024-01-01T12:00:01Z"
  },
  "conversation_id": "temp_conv_123456789"
}
```

### Create Chat Session

**POST** `/sessions`

Create a new chat session for persistent conversation.

#### Headers

```
Authorization: Bearer <access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "title": "Project Planning Discussion",
  "initial_message": "I need help planning a new software project",
  "context": {
    "project_type": "web_application",
    "team_size": 5
  }
}
```

#### Response

**Status: 201 Created**

```json
{
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "title": "Project Planning Discussion",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "message_count": 1,
  "first_message": {
    "id": "msg_123e4567-e89b-12d3-a456-426614174001",
    "content": "I need help planning a new software project",
    "role": "user",
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "ai_response": {
    "id": "msg_123e4567-e89b-12d3-a456-426614174002",
    "content": "I'd be happy to help you plan your new software project! Let's start by understanding your requirements...",
    "role": "assistant",
    "timestamp": "2024-01-01T12:00:01Z",
    "metadata": {
      "model_used": "gpt-4",
      "tokens_used": {
        "input": 35,
        "output": 55,
        "total": 90
      }
    }
  }
}
```

### Get Chat Sessions

**GET** `/sessions`

Retrieve user's chat sessions with pagination.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `search` (optional): Search term for session titles
- `sort` (optional): Sort order (`created_at_desc`, `created_at_asc`, `updated_at_desc`, `updated_at_asc`)

#### Response

**Status: 200 OK**

```json
{
  "sessions": [
    {
      "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
      "title": "Project Planning Discussion",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:30:00Z",
      "message_count": 15,
      "last_message_preview": "That sounds like a great approach for the database design...",
      "last_message_timestamp": "2024-01-01T12:30:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Get Chat Session

**GET** `/sessions/{session_id}`

Retrieve a specific chat session with its messages.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Query Parameters

- `include_messages` (optional): Include messages in response (default: true)
- `message_limit` (optional): Limit number of messages returned (default: 50)
- `message_offset` (optional): Offset for message pagination (default: 0)

#### Response

**Status: 200 OK**

```json
{
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "title": "Project Planning Discussion",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z",
  "message_count": 15,
  "messages": [
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174001",
      "content": "I need help planning a new software project",
      "role": "user",
      "timestamp": "2024-01-01T12:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174002",
      "content": "I'd be happy to help you plan your new software project! Let's start by understanding your requirements...",
      "role": "assistant",
      "timestamp": "2024-01-01T12:00:01Z",
      "metadata": {
        "model_used": "gpt-4",
        "tokens_used": {
          "input": 35,
          "output": 55,
          "total": 90
        },
        "processing_time_ms": 1250
      }
    }
  ]
}
```

### Send Message to Session

**POST** `/sessions/{session_id}/messages`

Send a new message to an existing chat session.

#### Headers

```
Authorization: Bearer <access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "message": "What technologies would you recommend for the backend?",
  "context": {
    "previous_context": "web_application_planning",
    "user_preferences": {
      "experience_level": "intermediate",
      "preferred_languages": ["python", "javascript"]
    }
  }
}
```

#### Response

**Status: 200 OK**

```json
{
  "user_message": {
    "id": "msg_123e4567-e89b-12d3-a456-426614174015",
    "content": "What technologies would you recommend for the backend?",
    "role": "user",
    "timestamp": "2024-01-01T12:30:00Z",
    "metadata": {}
  },
  "ai_response": {
    "id": "msg_123e4567-e89b-12d3-a456-426614174016",
    "content": "Based on your preferences for Python and JavaScript, I'd recommend several excellent backend options...",
    "role": "assistant",
    "timestamp": "2024-01-01T12:30:01Z",
    "metadata": {
      "model_used": "gpt-4",
      "tokens_used": {
        "input": 150,
        "output": 200,
        "total": 350
      },
      "processing_time_ms": 2100,
      "context_used": {
        "previous_messages": 14,
        "context_window_tokens": 3500
      }
    }
  },
  "session_updated": {
    "message_count": 16,
    "updated_at": "2024-01-01T12:30:01Z"
  }
}
```

### Update Session Title

**PUT** `/sessions/{session_id}/title`

Update the title of a chat session.

#### Headers

```
Authorization: Bearer <access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "title": "Backend Technology Selection Discussion"
}
```

#### Response

**Status: 200 OK**

```json
{
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "title": "Backend Technology Selection Discussion",
  "updated_at": "2024-01-01T12:35:00Z"
}
```

### Delete Chat Session

**DELETE** `/sessions/{session_id}`

Delete a chat session and all its messages.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "message": "Chat session deleted successfully",
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "deleted_at": "2024-01-01T12:40:00Z"
}
```

### Get Message History

**GET** `/sessions/{session_id}/messages`

Retrieve messages from a chat session with advanced filtering.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Query Parameters

- `limit` (optional): Number of messages to return (default: 50, max: 200)
- `offset` (optional): Number of messages to skip (default: 0)
- `role` (optional): Filter by message role (`user`, `assistant`)
- `from_date` (optional): Filter messages from this date (ISO format)
- `to_date` (optional): Filter messages to this date (ISO format)
- `search` (optional): Search term in message content

#### Response

**Status: 200 OK**

```json
{
  "messages": [
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174001",
      "content": "I need help planning a new software project",
      "role": "user",
      "timestamp": "2024-01-01T12:00:00Z",
      "metadata": {}
    }
  ],
  "pagination": {
    "total": 16,
    "limit": 50,
    "offset": 0,
    "has_more": false
  },
  "session_info": {
    "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
    "title": "Backend Technology Selection Discussion",
    "total_messages": 16
  }
}
```

## Streaming Endpoints

### Stream Chat Response

**POST** `/sessions/{session_id}/stream`

Send a message and receive a streaming response.

#### Headers

```
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: text/event-stream
```

#### Request Body

```json
{
  "message": "Explain the benefits of microservices architecture",
  "stream_options": {
    "include_metadata": true,
    "chunk_size": "word"
  }
}
```

#### Response

**Status: 200 OK**
**Content-Type: text/event-stream**

```
data: {"type": "start", "message_id": "msg_123456", "timestamp": "2024-01-01T12:00:00Z"}

data: {"type": "chunk", "content": "Microservices", "chunk_index": 0}

data: {"type": "chunk", "content": " architecture", "chunk_index": 1}

data: {"type": "chunk", "content": " offers", "chunk_index": 2}

data: {"type": "metadata", "tokens_used": 45, "processing_time_ms": 1200}

data: {"type": "end", "message_id": "msg_123456", "total_chunks": 50, "timestamp": "2024-01-01T12:00:02Z"}

```

## Data Models

### ChatRequest

```json
{
  "message": "string (required, max 4000 chars)",
  "context": {
    "user_preferences": "object (optional)",
    "metadata": "object (optional)"
  }
}
```

### ChatResponse

```json
{
  "response": "string",
  "metadata": {
    "model_used": "string",
    "tokens_used": {
      "input": "integer",
      "output": "integer",
      "total": "integer"
    },
    "processing_time_ms": "integer",
    "timestamp": "string (ISO datetime)"
  },
  "conversation_id": "string"
}
```

### SessionCreate

```json
{
  "title": "string (optional, max 200 chars)",
  "initial_message": "string (required, max 4000 chars)",
  "context": "object (optional)"
}
```

### SessionResponse

```json
{
  "session_id": "string (UUID)",
  "title": "string",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)",
  "message_count": "integer",
  "messages": "array (optional)"
}
```

### Message

```json
{
  "id": "string (UUID)",
  "content": "string",
  "role": "string (user|assistant)",
  "timestamp": "string (ISO datetime)",
  "metadata": "object"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Message content is required"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 404 Not Found
```json
{
  "detail": "Chat session not found"
}
```

#### 413 Payload Too Large
```json
{
  "detail": "Message content exceeds maximum length of 4000 characters"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please wait before sending another message."
}
```

#### 503 Service Unavailable
```json
{
  "detail": "AI service temporarily unavailable. Please try again later."
}
```

## Rate Limiting

Chat endpoints have the following rate limits:

- Direct chat: 30 requests per minute per user
- Session messages: 60 requests per minute per user
- Session creation: 10 requests per minute per user
- Session management: 100 requests per minute per user

## LangGraph Integration

The chat service uses LangGraph for intelligent conversation flow:

### Graph Nodes

1. **Preprocessing Node**: Analyzes user input, extracts intent, and prepares context
2. **LLM Node**: Generates AI response using configured language model
3. **Postprocessing Node**: Formats response, adds metadata, and handles follow-up actions

### Context Management

- **Session Context**: Maintains conversation history and user preferences
- **Message Context**: Includes immediate context for each message
- **Global Context**: System-wide settings and configurations

### Model Configuration

- **Default Model**: GPT-4 (configurable via environment variables)
- **Fallback Model**: GPT-3.5-turbo
- **Token Limits**: 4096 tokens for input, 2048 tokens for output
- **Temperature**: 0.7 (configurable)

## Performance Considerations

1. **Response Times**: Typical response time is 1-3 seconds
2. **Concurrent Users**: Supports up to 100 concurrent chat sessions
3. **Message History**: Sessions store up to 1000 messages
4. **Token Management**: Automatic context window management
5. **Caching**: Response caching for common queries (optional)

## Security Features

1. **Input Sanitization**: All user inputs are sanitized
2. **Content Filtering**: Inappropriate content detection
3. **Rate Limiting**: Per-user and per-IP rate limiting
4. **Audit Logging**: All chat interactions are logged
5. **Data Encryption**: Messages encrypted at rest and in transit